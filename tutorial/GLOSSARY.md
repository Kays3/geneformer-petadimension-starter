# Glossary

The terms used in the lessons, in alphabetical order.

**AnnData, `.h5ad`.** The standard Python format for single-cell data: a
count table (`X`, cells by genes) with side tables describing cells (`obs`)
and genes (`var`). Saved as an `.h5ad` file.

**Checkpoint.** A saved, trained model: a folder of files holding its learned
numbers. `Geneformer-V2-104M` is a checkpoint.

**Classifier.** A model that assigns a label, such as a cell type, to each
item. In lesson 8 a simple classifier (logistic regression) learns cell types
from embeddings.

**conda, environment.** conda installs Python and its add-ons into separate
**environments**, so that one project's versions do not break another's. You
switch with `conda activate <name>`.

**CPU, GPU.** The CPU is a computer's general-purpose processor. A GPU is a
processor built for many calculations at once; it makes model training and
large-scale embedding far faster.

**Embedding.** A fixed-length list of numbers that represents an item. Here,
768 numbers per cell, read from Geneformer. Cells the model sees as similar
get similar embeddings.

**Ensembl ID.** A stable identifier for a gene, such as `ENSG00000198851`
(the human gene `CD3E`). Geneformer uses Ensembl IDs, not gene names.

**Fine-tuning.** Continuing to train a pretrained model on a smaller labelled
dataset so that it gets better at one task. It changes the model's numbers and
needs a GPU.

**Gene expression.** How strongly a gene is switched on in a cell, measured by
counting its RNA molecules.

**Git, Git LFS.** Git downloads and tracks versions of code. Git LFS ("large
file storage") handles big files, such as model weights, that Git stores
separately.

**Home folder.** Your own folder on a computer, written `~`. On macOS it is
`/Users/yourname`; on Linux machines, `/home/yourname`.

**In silico perturbation.** Changing a cell's input on the computer, for
example removing one gene from its ranked list, and measuring how the model's
view of the cell changes. It produces hypotheses, not measurements.

**Path.** The address of a file or folder, such as
`~/geneformer-tutorial/pbmc/input`. Folders are separated by `/`.

**Pretrained model.** A model already trained on a large general dataset (for
Geneformer, about 104 million human cells) and reused for new tasks.

**Probe.** A simple classifier trained on frozen embeddings, used to test what
information the embeddings already contain.

**Prompt.** The text at the start of a terminal line (ending in `%`, `$` or
similar) that shows the terminal is waiting for a command.

**scRNA-seq.** Single-cell RNA sequencing: measuring gene expression in
thousands of individual cells at once.

**SSH.** "Secure shell": a way to open a terminal on another computer over the
network. `ssh gpu-box` logs you in to the machine called `gpu-box`.

**SSH key.** A pair of files that proves who you are to another computer
without a password. The private half stays on your laptop and is never shared;
your administrator needs only the public half.

**Terminal.** A window where you type commands. See lesson 1.

**tmux.** A program that keeps a terminal session running on a remote machine
after you disconnect.

**Token, tokenization.** A token is one unit of model input. For Geneformer,
each gene is a token, and **tokenization** turns a cell into its ranked list
of gene tokens.

**Transformer.** The type of neural network behind Geneformer and modern
language models. It reads a sequence (words, or genes) and learns how the
items relate to one another.

**UMAP.** A method that draws high-dimensional data, such as 768-number
embeddings, as a 2-D picture, keeping near neighbours near. Distances between
far-apart groups in the picture are not meaningful.

Back to [Lesson 0. Start here](00-start-here.md)
