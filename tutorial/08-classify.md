# Lesson 8. Classify

Before you start, open a terminal and run:

```bash
cd ~/geneformer-tutorial
conda activate geneformer
```

A **classifier** is a model that learns to name a cell's type from data. You
can turn Geneformer into a cell classifier in two ways:

1. **Frozen embeddings plus a simple classifier (a "probe").** Keep the model
   fixed, take the embeddings from [lesson 7](07-embeddings.md), and fit a
   logistic regression. This runs on CPU in seconds.
2. **Fine-tuning.** Add a classification head to the transformer and train it,
   usually with the lower layers frozen. This needs a GPU.

Start with the probe. It is fast and easy to inspect, and often good enough.

## Frozen embeddings plus logistic regression

Save as `probe_pbmc.py`:

```python
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

table = pd.read_csv("pbmc/results/pbmc3k_cls_embeddings.csv", index_col=0)
labels = ["cell_type", "split", "cell_id"]
features = [c for c in table.columns if c not in labels]

train = table[table["split"].isin(["train", "eval"])]
test = table[table["split"] == "test"]

probe = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
)
probe.fit(train[features], train["cell_type"])
predicted = probe.predict(test[features])

print("test cells:", len(test))
print("accuracy:", round(accuracy_score(test["cell_type"], predicted), 4))
print("macro F1:", round(f1_score(test["cell_type"], predicted, average="macro"), 4))
print(classification_report(test["cell_type"], predicted, zero_division=0))
```

Run it:

```bash
python probe_pbmc.py
```

It takes a few seconds. You should see (from the test run on a GPU machine):

```text
test cells: 528
accuracy: 0.9299
macro F1: 0.9251
                   precision    recall  f1-score   support

          B cells       0.99      1.00      0.99        69
  CD14+ Monocytes       0.97      0.95      0.96        96
      CD4 T cells       0.95      0.94      0.95       229
      CD8 T cells       0.78      0.79      0.79        63
  Dendritic cells       1.00      0.86      0.92         7
FCGR3A+ Monocytes       0.85      0.93      0.89        30
   Megakaryocytes       1.00      1.00      1.00         3
         NK cells       0.90      0.90      0.90        31

         accuracy                           0.93       528
        macro avg       0.93      0.92      0.93       528
     weighted avg       0.93      0.93      0.93       528
```

Your numbers may differ in the last digit or two. The `support` column is the
number of test cells of each type. The weakest class is CD8 T cells, which
the classifier partly confuses with CD4 T cells, as the UMAP in lesson 7
suggested.

**Accuracy** is the share of test cells named correctly. **F1** combines two
questions for each cell type: of the cells called type X, how many really are
X (precision), and of the real type-X cells, how many were found (recall).

`class_weight="balanced"` stops the large CD4 T-cell class from dominating.
Report **macro F1** (the unweighted mean of per-class F1) next to accuracy:
with 1,144 CD4 T cells and 15 megakaryocytes, accuracy alone hides how the
small classes fare.

Even with all cells embedded, the test split holds only 7 dendritic cells and
3 megakaryocytes. Per-class scores on so few cells are not informative; always
report the support column (the number of test cells per class) with them. If
you embedded a subset in lesson 7, rare classes may be missing from the test
set entirely.

## Fine-tuning on a GPU

Geneformer's `Classifier` prepares labelled data, fine-tunes, and evaluates.
Run it on a machine with an NVIDIA GPU after the GPU setup in
[lesson 9](09-next-steps.md). This example uses the `split` column from
[lesson 5](05-prepare-data.md) so
that the test cells are the same ones the probe was scored on. Save as
`finetune_pbmc.py`:

```python
from pathlib import Path

from geneformer import Classifier

RUN_DIR = Path("pbmc/finetune")
RUN_DIR.mkdir(parents=True, exist_ok=True)
PREFIX = "pbmc3k"

classifier = Classifier(
    classifier="cell",
    cell_state_dict={"state_key": "cell_type", "states": "all"},
    training_args={
        "num_train_epochs": 1,
        "learning_rate": 5e-5,
        "per_device_train_batch_size": 8,
        "per_device_eval_batch_size": 16,
        "seed": 42,
        "report_to": "none",
    },
    freeze_layers=6,  # train only the top 6 of 12 transformer layers
    num_crossval_splits=1,
    forward_batch_size=16,
    nproc=4,
    model_version="V2",
)

# Writes {PREFIX}_labeled_train.dataset, {PREFIX}_labeled_test.dataset and
# {PREFIX}_id_class_dict.pkl into RUN_DIR.
classifier.prepare_data(
    input_data_file="pbmc/tokens/pbmc3k.dataset",
    output_directory=str(RUN_DIR),
    output_prefix=PREFIX,
    split_id_dict={"attr_key": "split", "train": ["train", "eval"], "test": ["test"]},
)

# Trains on "train" cells and monitors on "eval" cells.
classifier.validate(
    model_directory="Geneformer/Geneformer-V2-104M",
    prepared_input_data_file=str(RUN_DIR / f"{PREFIX}_labeled_train.dataset"),
    id_class_dict_file=str(RUN_DIR / f"{PREFIX}_id_class_dict.pkl"),
    output_directory=str(RUN_DIR),
    output_prefix=PREFIX,
    split_id_dict={"attr_key": "split", "train": ["train"], "eval": ["eval"]},
    n_hyperopt_trials=0,
)

# The trained model is saved in a dated folder ending in .../ksplit1.
model_dir = sorted(RUN_DIR.glob(f"*geneformer_cellClassifier_{PREFIX}/ksplit1"))[-1]
metrics = classifier.evaluate_saved_model(
    model_directory=str(model_dir),
    id_class_dict_file=str(RUN_DIR / f"{PREFIX}_id_class_dict.pkl"),
    test_data_file=str(RUN_DIR / f"{PREFIX}_labeled_test.dataset"),
    output_directory=str(RUN_DIR),
    output_prefix=f"{PREFIX}_test",
)
print(metrics)
```

In the test run on an NVIDIA GB10 GPU machine, this took 3 minutes 43
seconds, of which training was 2 minutes 47 seconds. It prints a warning that
some weights are "newly initialized" (expected: the classification head is
new), a loss line every few steps, and finally a dictionary of test results.
The last line looked like this:

```text
{'conf_matrix': ..., 'macro_f1': 0.898984758182372, 'acc': 0.9356060606060606, 'all_roc_metrics': None}
```

Fine-tuning trains on the 1,846 `train` cells and uses the 264 `eval` cells
to monitor training; the probe above trained on both sets together (2,110
cells). Both are scored on the same 528 `test` cells. At a batch size of 8,
one epoch is about 231 training steps.

## Is fine-tuning worth it?

On PBMC, in the test run, scored on the same 528 test cells:

| Method | Accuracy | Macro F1 | Time |
| --- | ---: | ---: | --- |
| Frozen embeddings + logistic regression | 0.930 | 0.925 | seconds (after lesson 7) |
| Fine-tuned, one epoch, 6 of 12 layers frozen | 0.936 | 0.899 | about 4 minutes on a GPU |

Fine-tuning got three more cells right overall (494 against 491) but did
worse on the two smallest classes: it found 2 of 3 megakaryocytes and 5 of 7
dendritic cells, where the probe found all 3 and 6 of 7. With so few cells
these differences are not meaningful in either direction, and both numbers
come from one run with one random seed. Overall, the two methods performed
about the same here.

In the one comparison we have, it added little. In the
[lung allograft example](../examples/lung-allograft/README.md), a public
dataset classified into five broad compartments with two donors held out
entirely, the frozen-embedding probe reached 0.9976 accuracy and the
fine-tuned model 0.9983 on 2,874 test cells: seven errors against five. All
of those errors came from one of the two test donors (`LTx_pt_08`; the other
was classified perfectly by both), and no interval was computed, so a
two-cell difference is not evidence that fine-tuning helps. That run also
used `emb_mode="cell"` (the average of the gene vectors) rather than the
`<cls>` vector used in this tutorial, so its numbers are a reference point,
not a like-for-like comparison.

For broad, well-separated cell types, the pretrained representation already
carries most of the signal. Fine-tuning is more likely to help with subtle
cell states, and it brings more ways to overfit, so compare it against the
probe on the same held-out cells before relying on it.

## Before trusting a score

- **Hold out donors, not just cells.** Cells from one person share genotype,
  sample handling and batch. A cell-level split, as in this PBMC example,
  tends to overstate performance on new people.
- **Know where the labels came from.** The PBMC labels came from clustering
  the same data (see [lesson 5](05-prepare-data.md)), so high accuracy here
  shows the pipeline works, not that Geneformer outperforms a clustering.
- **Report uncertainty.** With few test donors, a single accuracy figure says
  little about variation between donors. Report per-donor results where you
  can.

## You should now see

Accuracy and macro F1 for 528 held-out cells, and a per-cell-type table. The
small classes (dendritic cells, megakaryocytes) will score less reliably than
the large ones.

## Troubleshooting

| You see | What it means | What to do |
| --- | --- | --- |
| `FileNotFoundError: ... pbmc3k_cls_embeddings.csv` | Lesson 7 did not finish | Run `python embed_pbmc_cpu.py` first |
| `test cells:` far below 528, and some cell types missing from the table | The embeddings were made with `N_CELLS` set to a small number | Set `N_CELLS = None` in lesson 7 and run it again |
| `ConvergenceWarning` | The classifier needed more steps | Harmless here; you may raise `max_iter` to 5000 |

Previous: [7. Embeddings](07-embeddings.md) · Next: [9. Next steps](09-next-steps.md)
