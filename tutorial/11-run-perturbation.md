# Lesson 11. Run a first in silico perturbation

You will remove one gene token from a small set of PBMCs, run the pretrained
model again, and summarize the change in its cell representations. This is a
**technical pilot**, not a biological discovery: PBMC 3k has one donor and no
resting/stimulated conditions. The pilot measures similarity between original
and edited embeddings, not movement toward a healthy or resting state.

This lesson is based on the [official perturber API](https://geneformer.readthedocs.io/en/latest/geneformer.in_silico_perturber.html)
and [statistics API](https://geneformer.readthedocs.io/en/latest/geneformer.in_silico_perturber_stats.html).
The code below has been checked against documented parameters but **has not
been run end to end on a GPU**. Package versions can differ: if an output or
API differs, inspect the installed version before interpreting it.

## Before you start

- Finish [lesson 6](06-tokenize.md) using the conda tutorial route, producing
  `pbmc/tokens/pbmc3k.dataset`, and use the V2-104M checkpoint installed in
  [lesson 4](04-install.md), at `Geneformer/Geneformer-V2-104M` relative to
  `~/geneformer-tutorial`.
- Use a GPU machine configured as in [lesson 9](09-next-steps.md). An NVIDIA
  GPU with sufficient free memory is needed for the authors' perturber.
- The quickstart's `uv` folder and the conda lessons use different paths. The
  commands here assume the conda lesson layout; do not mix their environments.
- Save the code below as `pilot_isp.py` in `~/geneformer-tutorial`. Run it on
  the GPU machine inside `tmux` if the connection may drop. Install packages
  only as described in the earlier lessons.

## 1. Understand the edit

An example list `A, B, C` becomes `A, C` when B is deleted. We run the same
model on the original and edited sequence. The perturbation does not physically
knock out B, change expression counts in a real cell, or update model weights.
For V2 we compare the `<cls>` cell embedding from the penultimate layer
(`emb_mode="cls"`, `emb_layer=-1`).

The script picks a frequently detected Ensembl gene **without using disease
or outcome information**, selects up to 20 CD4 T cells containing it, and
perturbs that single gene. The automatic selection is only to make the tutorial
reproducible; it is not a recommendation to study that gene. Since filtering
for detection precedes the test, results apply to these eligible cells only.

## 2. Save and run the pilot

```python
from collections import Counter
from pathlib import Path
import json
import pickle

import torch
from datasets import load_from_disk
from geneformer import (
    InSilicoPerturber,
    InSilicoPerturberStats,
    TOKEN_DICTIONARY_FILE,
)

MODEL = Path("Geneformer/Geneformer-V2-104M")
INPUT = Path("pbmc/tokens/pbmc3k.dataset")
OUT = Path("pbmc/isp_pilot")
CELL_TYPE = "CD4 T cells"
N_CELLS = 20
SEED = 42

if not torch.cuda.is_available():
    raise RuntimeError("An available NVIDIA GPU is required; see lesson 9.")
if not MODEL.is_dir() or not INPUT.is_dir():
    raise FileNotFoundError("Finish lessons 4 and 6 and run from ~/geneformer-tutorial.")
if OUT.exists():
    raise FileExistsError("pbmc/isp_pilot already exists; choose a new OUT path to keep the old run.")

with open(TOKEN_DICTIONARY_FILE, "rb") as handle:
    gene_to_token = pickle.load(handle)
token_to_gene = {token: gene for gene, token in gene_to_token.items()
                 if isinstance(gene, str) and gene.startswith("ENSG")}

cells = load_from_disk(str(INPUT))
if "cell_type" not in cells.column_names:
    raise ValueError("The tokenized dataset needs the cell_type column from lesson 6.")
cells = cells.filter(lambda row: row["cell_type"] == CELL_TYPE)
if len(cells) == 0:
    raise ValueError("No matching cells; check the cell_type labels from lesson 6.")
counts = Counter(token for row in cells for token in set(row["input_ids"])
                 if token in token_to_gene)
if not counts:
    raise ValueError("No Ensembl tokens found; check V2 token dictionary compatibility.")
token, n_detected = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
gene = token_to_gene[token]
eligible = cells.filter(lambda row: token in row["input_ids"])
eligible = eligible.shuffle(seed=SEED).select(range(min(N_CELLS, len(eligible))))

OUT.mkdir(parents=True)
(OUT / "raw").mkdir()
(OUT / "stats").mkdir()
eligible.save_to_disk(str(OUT / "pilot.dataset"))
manifest = {"gene_ensembl": gene, "token": token, "cell_type": CELL_TYPE,
            "detected_in_cell_type": n_detected, "pilot_cells": len(eligible),
            "seed": SEED, "model": str(MODEL), "edit": "delete",
            "embedding": "cls", "emb_layer": -1, "model_version": "V2"}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("Pilot:", manifest, flush=True)

perturber = InSilicoPerturber(
    perturb_type="delete", genes_to_perturb=[gene], combos=0,
    model_type="Pretrained", num_classes=0, emb_mode="cls", emb_layer=-1,
    max_ncells=None, forward_batch_size=4, nproc=1, model_version="V2",
)
perturber.perturb_data(str(MODEL), str(OUT / "pilot.dataset"),
                       str(OUT / "raw"), "pilot")

stats = InSilicoPerturberStats(mode="aggregate_data", genes_perturbed=[gene],
                               combos=0, model_version="V2")
stats.get_stats(str(OUT / "raw"), None, str(OUT / "stats"), "pilot_summary")
print("Finished. See", OUT / "stats", "and", OUT / "manifest.json")
```

```bash
cd ~/geneformer-tutorial
conda activate geneformer
python pilot_isp.py
```

A progress bar and GPU activity should appear. The selected gene, eligible
cell counts, and settings are printed and saved in `pbmc/isp_pilot/manifest.json`.
The pilot should save raw perturbation dictionaries in `raw/` and a summary
CSV in `stats/`. Filenames and table columns are version-dependent. Raw pickle
files should be opened only if they come from a trusted source.

If a run fails after creating `pbmc/isp_pilot`, edit `OUT` to a **new** path
before restarting; this protects the incomplete run for troubleshooting.
Record the installed Geneformer commit, package versions, CUDA and GPU name
alongside the manifest; the manifest is a minimal teaching record.

## 3. Read the summary

For the documented `aggregate_data` mode, `Perturbed` identifies the edit,
`Affected` indicates a gene or the whole-cell embedding, and
`Cosine_sim_mean` is the mean cosine similarity of original versus edited
embeddings across eligible cells. `Cosine_sim_stdev` describes their spread.
Inspect the actual output header before relying on these fields. A cosine
closer to 1 indicates more similar directions; a lower value means a larger
angular change. It does **not** indicate whether the edit moves toward a
desirable biological state. You cannot rank a single tested gene against a
proper control distribution from this pilot.

For interpreting goal-directed analyses and sample tables, continue to
[lesson 12](12-interpret-perturbation.md). The [PBMC lesson](perturbation-peripheral-blood.md)
and [cardiomyocyte lesson](perturbation-cardiomyocytes.md) explain how to design
larger studies with suitable multi-donor data.

## You should now see

A manifest naming one selected gene, a saved subset of up to 20 cells, raw
perturbation results, and a summary CSV. Your values depend on the data and
software version; no numbers are promised here.

## Troubleshooting

| You see | What to check |
| --- | --- |
| `An available NVIDIA GPU is required` | Check `nvidia-smi`, the CUDA-enabled PyTorch environment, and lesson 9 |
| No CD4 T cells or no Ensembl tokens | Verify lesson 6 dataset columns, labels and V2 dictionary |
| CUDA out of memory | Check other GPU jobs and reduce `forward_batch_size` or `N_CELLS`; use a new output directory |
| No CSV or unexpected output columns | Inspect the raw directory, full log and installed Geneformer API; preserve the run and ask for help |

Previous: [10. Lessons from real runs](10-lessons-from-real-runs.md) · Next: [12. Interpret perturbations](12-interpret-perturbation.md)
