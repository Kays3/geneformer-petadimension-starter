# Lesson 2. Geneformer in plain words

No code in this lesson. It explains what Geneformer does, so the later
commands make sense.

## The biology in three sentences

Every cell in your body carries the same genes, but each cell type switches on
a different set of them. **Gene expression** is how strongly each gene is
switched on, measured by counting its RNA molecules. **Single-cell RNA
sequencing (scRNA-seq)** does that count for thousands of individual cells at
once, giving a table with one row per cell and one column per gene.

## What Geneformer is

Geneformer is a **transformer**, the same kind of model behind modern
language tools. The current version (V2) was trained on gene expression from
about 104 million human cells; the original version described by Theodoris et
al. (2023) used about 30 million. A language model reads a sentence as a
list of words. Geneformer reads a cell as a list of genes.

## How a cell becomes a list of genes

Geneformer does not use the raw counts directly. For each cell it:

1. scales the counts so that every cell has the same total (10,000);
2. divides each gene by how much that gene is usually expressed across the
   ~104 million training cells; and
3. sorts the genes from highest to lowest, and keeps up to the first 4,094.

This sorted list is the cell's input. Each gene in it is a **token**, and the
process is **tokenization** (lesson 6).

Dividing by the usual level reorders the list. A gene that is high in every cell, such
as the housekeeping gene `ACTB`, says little about what makes this cell
special, so it drops down the list. A gene that is normally low but is high here, such as
a T-cell marker in a T cell, moves up. An invented example:

| Gene | Count in this cell | Usual level | Ratio | Position |
| --- | ---: | ---: | ---: | ---: |
| `ACTB` (in every cell) | 120 | 100 | 1.2 | 3rd |
| `CD3E` (T cells) | 15 | 3 | 5.0 | 1st |
| `GZMB` (killer cells) | 8 | 2 | 4.0 | 2nd |

The cell becomes `CD3E, GZMB, ACTB`. The real "usual levels" come with
Geneformer; these numbers only illustrate the idea.

This has two effects. Only the order is kept, so Geneformer cannot tell you
how much a gene went up. And genes that are not in its list of about 20,000 human
genes are dropped, which is why your data must use the right gene IDs
(lesson 5).

## How it learned

During training, about 15% of the genes in each cell's list were hidden, and
the model learned to guess them from the rest. It was never told which cells
were T cells or which were diseased. It learned which genes tend to appear
together, and in which order.

## What you can do with it

| Task | In plain words | Lesson |
| --- | --- | --- |
| Embedding | Turn each cell into a list of 768 numbers; similar cells get similar numbers | 7 |
| Classification | Teach a small extra model to name cell types from those numbers | 8 |
| Fine-tuning | Adjust part of Geneformer itself for one task; needs a GPU | 8, 9 |
| In silico perturbation | Remove or promote one gene in a cell's list and see how far the cell's numbers move | 9 |

## What it cannot tell you

Geneformer makes predictions about its own picture of a cell. It does not
measure anything. A cell "moving toward the healthy state" after a gene is removed
on the computer is a hypothesis to test at the bench, not a finding. It was
trained on human cells; other species need their genes matched to human
genes first, and some are lost on the way.

## Which model this tutorial uses

`Geneformer-V2-104M`: the second version, with 104 million adjustable numbers
("parameters"). It is small enough to run on a laptop for a few thousand
cells. There is a larger V2 model (316M) and an older V1 model (10M); V1 and V2
use different gene lists and must not be mixed.

## You should now see

How a table of counts becomes a ranked list of genes, and what the model can
and cannot be used for. Key words are in the [glossary](GLOSSARY.md).

## Troubleshooting

| Question | Short answer |
| --- | --- |
| Does it need my data to be normalized first? | No. Give it raw counts; it does its own scaling |
| Can I use gene names like `CD3E`? | No. It needs Ensembl IDs such as `ENSG00000198851` (lesson 5) |
| Is a big "shift" in lesson 9 a discovery? | Not by itself. It is a lead for an experiment |

## Source

Theodoris CV et al. Transfer learning enables predictions in network biology.
*Nature* 618, 616–624 (2023).
[doi:10.1038/s41586-023-06139-9](https://doi.org/10.1038/s41586-023-06139-9).
Model card: [huggingface.co/ctheodoris/Geneformer](https://huggingface.co/ctheodoris/Geneformer).

Previous: [1. The terminal](01-terminal.md) ·
Next: [3. A remote Linux machine](03-remote-machines.md)
