# Lesson 5. Prepare data

Before you start, open a terminal and run:

```bash
cd ~/geneformer-tutorial
conda activate geneformer
```

This lesson builds Geneformer's input from the 10x Genomics
**3k PBMCs from a healthy donor** dataset: about 2,700 peripheral blood
mononuclear cells from one healthy donor. It is a good first dataset: it is
small (about 6 MB) and public, and its cell types are well known. Scanpy
downloads it for you.

## What Geneformer needs from your data

Single-cell data in Python usually lives in an **AnnData** object (saved as an
`.h5ad` file): a table of counts, `X`, with one row per cell and one column per
gene, plus side tables describing the cells (`obs`) and the genes (`var`).
Geneformer needs four things from it:

| Requirement | Where | Why |
| --- | --- | --- |
| Raw integer counts | `adata.X` | The tokenizer does its own normalization; already-normalized or log values give wrong ranks |
| Ensembl gene IDs | `adata.var["ensembl_id"]` | The vocabulary is keyed by Ensembl ID (`ENSG...`), not by gene symbol |
| Total counts per cell | `adata.obs["n_counts"]` | Used to scale each cell to 10,000 counts |
| Optional QC flag | `adata.obs["filter_pass"]` | Cells with `1` are tokenized; others are skipped |

Any other `obs` column you want to carry through (labels, donor, split) must be
named explicitly when you tokenize.

## Build the input file

Save this as `prepare_pbmc.py` in `~/geneformer-tutorial` (with `nano`, as in
lesson 1). Read the comments (lines starting with `#`): they say what each part
does.

```python
from pathlib import Path

import numpy as np
import scanpy as sc
from sklearn.model_selection import train_test_split

Path("pbmc/data").mkdir(parents=True, exist_ok=True)  # scanpy will not create it
sc.settings.datasetdir = "pbmc/data"

# Raw UMI counts: 2,700 cells x 32,738 genes. var["gene_ids"] holds Ensembl IDs.
raw = sc.datasets.pbmc3k()
# The scanpy tutorial's processed copy: 2,638 cells that passed QC, with
# cluster-based cell-type names in obs["louvain"]. We borrow only the labels.
labelled = sc.datasets.pbmc3k_processed()

adata = raw[labelled.obs_names].copy()
adata.obs["cell_type"] = labelled.obs["louvain"].astype(str).to_numpy()
adata.obs["cell_id"] = adata.obs_names.astype(str)
adata.obs["n_counts"] = np.asarray(adata.X.sum(axis=1)).ravel().astype(float)
adata.obs["filter_pass"] = 1
adata.var["ensembl_id"] = adata.var["gene_ids"].astype(str).str.split(".").str[0]
adata.var = adata.var[["ensembl_id"]]

# Fixed, stratified split: 70% train, 10% eval, 20% test.
train_ids, test_ids = train_test_split(
    adata.obs_names, test_size=0.2, stratify=adata.obs["cell_type"], random_state=42
)
train_ids, eval_ids = train_test_split(
    train_ids,
    test_size=0.125,
    stratify=adata.obs.loc[train_ids, "cell_type"],
    random_state=42,
)
adata.obs["split"] = "train"
adata.obs.loc[eval_ids, "split"] = "eval"
adata.obs.loc[test_ids, "split"] = "test"

sample = adata.X[:200].toarray()
assert np.allclose(sample, np.rint(sample)), "Expected raw integer counts."

out_dir = Path("pbmc/input")
out_dir.mkdir(parents=True, exist_ok=True)
adata.write_h5ad(out_dir / "pbmc3k.h5ad")

print(adata)
print(adata.obs["cell_type"].value_counts())
print(adata.obs["split"].value_counts())
```

Run it. The first run downloads about 30 MB:

```bash
python prepare_pbmc.py
```

You should see, among some download progress bars:

```text
AnnData object with n_obs × n_vars = 2638 × 32738
CD4 T cells          1144
CD14+ Monocytes       480
B cells               342
CD8 T cells           316
NK cells              154
FCGR3A+ Monocytes     150
Dendritic cells        37
Megakaryocytes         15
train    1846
test      528
eval      264
```

## Three things to know about this dataset

**How many genes reach the model.** Of the 32,738 genes in the file, 19,301
map to Geneformer V2's vocabulary of 20,271 genes (a few of them collapse onto
the same token, leaving 19,050 distinct tokens). A typical cell has roughly
800 vocabulary genes with at least one count (median 797, range 206 to 2,363
across the 2,638 cells), well under the 4,096-token input size, so no cell is
truncated. These figures come from the V2 dictionaries on Hugging Face as of
October 2026.

**Where the labels come from.** The `louvain` names were assigned by
clustering these same cells and annotating the clusters with marker genes.
They are reasonable, but they are derived from the expression data the model
will see. A classifier that recovers them is reproducing a clustering; the labels
were not measured independently of that data. Treat accuracy on this dataset
as a check that the pipeline works, not as evidence of biological performance.

**One donor.** All cells come from one person, so the train/test split is
between cells, not between people. Real studies should hold out whole donors;
the [lung allograft example](../examples/lung-allograft/README.md) shows a
donor-held-out design.

## Your own data

- If your genes are symbols only, convert them to Ensembl IDs first (for
  example with Ensembl BioMart). Do not guess.
- Strip version suffixes: `ENSG00000141510.18` becomes `ENSG00000141510`
  (the `.str.split(".")` line above does this).
- If your `.h5ad` stores normalized values in `X`, use the raw counts in
  `adata.raw` or a counts layer instead.
- Mouse or other non-human data need a one-to-one orthology mapping to human
  Ensembl IDs. Report how many genes were lost in that mapping.

## You should now see

A new file, `pbmc/input/pbmc3k.h5ad` (about 20 MB), and the cell-type counts
above. Check with `ls -lh pbmc/input`.

## Troubleshooting

| You see | What it means | What to do |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'scanpy'` | The `geneformer` environment is not active, or lesson 4 did not finish | `conda activate geneformer`; if it persists, repeat lesson 4, step 4 |
| `URLError` or `HTTP Error` while downloading | No internet, or the download server is busy | Check your connection and run the script again; finished downloads are kept in `pbmc/data` |
| `AssertionError: Expected raw integer counts.` | `X` holds normalized values (only happens with your own data) | Use the raw counts, as described under "Your own data" |

Previous: [4. Install Python and Geneformer](04-install.md) · Next: [6. Tokenize](06-tokenize.md)
