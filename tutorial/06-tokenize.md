# Lesson 6. Tokenize

Before you start, open a terminal and run:

```bash
cd ~/geneformer-tutorial
conda activate geneformer
```

Tokenization turns each cell into the ranked list of genes described in
[lesson 2](02-geneformer-in-plain-words.md), with each gene replaced by its
number in Geneformer's vocabulary. The result is saved as a folder that the
later lessons read. It took about 20 seconds in our test run.

Save as `tokenize_pbmc.py`:

```python
from datasets import load_from_disk
from geneformer import TranscriptomeTokenizer

tokenizer = TranscriptomeTokenizer(
    # obs columns to carry into the tokenized dataset: {input name: output name}
    custom_attr_name_dict={"cell_id": "cell_id", "cell_type": "cell_type", "split": "split"},
    nproc=4,
    model_version="V2",  # must match the checkpoint you will use
)
tokenizer.tokenize_data(
    data_directory="pbmc/input",   # every .h5ad in this folder is tokenized
    output_directory="pbmc/tokens",
    output_prefix="pbmc3k",
    file_format="h5ad",
)

tokens = load_from_disk("pbmc/tokens/pbmc3k.dataset")
print(tokens)
first = tokens[0]
print("cell:", first["cell_id"], "|", first["cell_type"], "| length:", first["length"])
print("first ten token ids:", first["input_ids"][:10])
```

Run it:

```bash
python tokenize_pbmc.py
```

You should see a progress bar, some `FutureWarning` lines from inside
Geneformer (harmless), and then:

```text
Dataset({
    features: ['input_ids', 'cell_id', 'cell_type', 'split', 'length'],
    num_rows: 2638
})
cell: AAACATACAACCAC-1 | CD4 T cells | length: 761
first ten token ids: [2, 17941, 13923, 17531, 10389, 15363, 8385, 11659, 19067, 9177]
```

`2` is the number of the `<cls>` token, which starts every cell. The first
cell's length of 761 is 759 genes plus the start and end tokens. This output
comes from the test run on a Linux GPU machine (October 2026, Geneformer commit
`1f7fbae`).

## What you get

Each row of the dataset is one cell with these columns:

| Column | Content |
| --- | --- |
| `input_ids` | Token IDs: `<cls>`, then genes from highest to lowest rank, then `<eos>` |
| `length` | Number of tokens, including the two special tokens |
| `cell_id`, `cell_type`, `split` | Copied from `obs` because you named them |

`model_version="V2"` sets the V2 defaults: the V2 gene dictionaries, an input
size of 4,096 tokens, and the `<cls>`/`<eos>` special tokens. For a V1
checkpoint, use `model_version="V1"`; V1 has no special tokens and an input
size of 2,048.

To read a cell's ranked genes as Ensembl IDs, invert the token dictionary:

```python
import pickle

from datasets import load_from_disk
from geneformer import TOKEN_DICTIONARY_FILE

with open(TOKEN_DICTIONARY_FILE, "rb") as handle:
    token_to_gene = {token: gene for gene, token in pickle.load(handle).items()}

tokens = load_from_disk("pbmc/tokens/pbmc3k.dataset")
print([token_to_gene[t] for t in tokens[0]["input_ids"][:6]])
```

The first entry is `<cls>`. After it come the genes this cell ranks
highest.

## You should now see

A folder `pbmc/tokens/pbmc3k.dataset` with 2,638 rows, one per cell. Check
with `ls pbmc/tokens`.

## Troubleshooting

| You see | What it means | What to do |
| --- | --- | --- |
| `KeyError: 'ensembl_id_collapsed'` | pandas 3 is installed | `pip install "pandas<3"`, then run again |
| `'ensembl_id' column missing from data.var` or `'n_counts' column missing from data.obs` | The input file was not made by lesson 5 (or your own data lacks these) | Rerun `python prepare_pbmc.py`; for your own data see lesson 5 |
| `num_rows` is 0, or every `length` is very short | Gene IDs did not match the vocabulary: version suffixes such as `.12`, gene names instead of Ensembl IDs, or non-human genes | Fix the IDs as described in lesson 5, "Your own data" |

Previous: [5. Prepare data](05-prepare-data.md) ·
Next: [7. Embeddings](07-embeddings.md)
