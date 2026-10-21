# Lesson 9. Next steps

This lesson is mostly reading. It covers setting up a GPU machine,
fine-tuning, and in silico perturbation.

## Set up a GPU machine

Fine-tuning ([lesson 8](08-classify.md)), the GPU route for embeddings
([lesson 7](07-embeddings.md)), and in silico perturbation need an NVIDIA
**GPU**, a processor built for the large calculations these models do.
The test machine had an NVIDIA GB10. It uses an ARM processor (`aarch64`),
which matters for one step below.

Log in (lesson 3) and check the GPU, and whether someone else is using it:

```bash
ssh gpu-box
nvidia-smi
```

You should see a table naming your GPU (the test machine showed `NVIDIA GB10`). The lower part lists running
processes; if another person's job is using most of the memory, coordinate
before starting a large run.

Then repeat [lesson 4](04-install.md) on that machine with one change: in
step 3, install the GPU build of PyTorch for CUDA 13.0 instead of the CPU
build, before step 4:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu130
```

This route was tested on a GB10 machine in October 2026 (PyTorch
2.14.1+cu130). The whole tutorial, lessons 4 to 8, ran there in about 37
minutes, of which about 5 minutes used the GPU. Check it:

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

You should see `True` and the name of your GPU, for example:

```text
True NVIDIA GB10
```

Run long jobs inside `tmux` (lesson 3, step 4). Keep large outputs, such as
fine-tuned models (about 400 MB each), in your home folder or a project folder
on shared storage, not in Git. On the test machine the conda folder grew to about 8 GB with
the GPU build of PyTorch, and pip kept a further 1 GB of downloads in
`~/.cache/pip` (`pip cache purge` removes them).

## In silico perturbation (advanced)

In silico perturbation asks a model-based question: if this gene were absent
from the cell, or ranked at the top, how far would the cell's embedding move,
and in which direction? Geneformer provides two tools for it:

- `InSilicoPerturber` edits the ranked gene list of each cell
  (`perturb_type` is `"delete"`, `"overexpress"`, `"inhibit"` or
  `"activate"`) and records the change in the cell or gene embeddings.
- `InSilicoPerturberStats` summarises those changes across cells and can
  compare them with a null distribution, for example perturbations of
  randomly chosen genes.

With `cell_states_to_model`, you name a start state and a goal state (for
example, a disease state and a healthy state). The tool then reports whether
each perturbation moves cells *toward* or *away from* the goal, measured by
cosine similarity to the average embedding of each state. Those state
averages come from `EmbExtractor.get_state_embs`.

"Overexpress" here means moving a gene to the top of the ranked list. It is not
a dose; the model never sees counts. "Delete" removes the gene from the list.
Both are edits to the input of a model, so the output is a prediction about
the model's representation of a cell. Use it to rank candidate genes for
follow-up. It needs experimental support before it is a finding.

Before you start:

- Use a GPU. Each perturbed gene needs a forward pass for every cell, so cost
  grows with genes times cells.
- Fine-tune on the states you care about first, or check that the pretrained
  embeddings already separate them. If the start and goal states overlap in
  embedding space, the shift toward the goal has little meaning.
- Compare against random genes of similar expression. A small shift is common
  and not informative on its own.

Worked example from the Geneformer authors:
[`examples/in_silico_perturbation.ipynb`](https://huggingface.co/ctheodoris/Geneformer/blob/main/examples/in_silico_perturbation.ipynb).
The method and its validation are described in Theodoris et al. (2023).

## Other official examples

The Geneformer repository on Hugging Face has notebooks for each task in this
tutorial, at full scale:

- [`tokenizing_scRNAseq_data.ipynb`](https://huggingface.co/ctheodoris/Geneformer/blob/main/examples/tokenizing_scRNAseq_data.ipynb)
- [`extract_and_plot_cell_embeddings.ipynb`](https://huggingface.co/ctheodoris/Geneformer/blob/main/examples/extract_and_plot_cell_embeddings.ipynb)
- [`cell_classification.ipynb`](https://huggingface.co/ctheodoris/Geneformer/blob/main/examples/cell_classification.ipynb)
- [`gene_classification.ipynb`](https://huggingface.co/ctheodoris/Geneformer/blob/main/examples/gene_classification.ipynb)
- [`multitask_cell_classification.ipynb`](https://huggingface.co/ctheodoris/Geneformer/blob/main/examples/multitask_cell_classification.ipynb)

## Moving to your own project

| Step | Small example (this tutorial) | Real study |
| --- | --- | --- |
| Data | 2,638 cells, one donor | Many donors; record the source and checksum |
| Labels | Cluster-derived | Independent where possible (sorting, genotype, clinical) |
| Split | Random, by cell | By donor, fixed before any model is fit |
| Model | V2-104M, frozen | Start frozen; fine-tune only if the probe falls short |
| Hardware | Laptop CPU | A GPU machine for embedding at scale, fine-tuning and perturbation |

The [lung allograft example](../examples/lung-allograft/README.md) shows the
right-hand column in practice: a public CELLxGENE dataset, a recorded
checksum, donor-disjoint training, model-selection and test sets, and a
frozen-versus-fine-tuned comparison with its limitations stated.

## You should now see

How to set up GPU work, and what in silico perturbation can and
cannot tell you. For terms, see the [glossary](GLOSSARY.md).

## Troubleshooting

| You see | What it means | What to do |
| --- | --- | --- |
| `False` from the GPU check | The CPU build of PyTorch was installed (often because step 4 ran before the CUDA build was installed) | `pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu130` |
| `CUDA out of memory` | The batch is too large, or another job is using the GPU | Check `nvidia-smi`; lower `forward_batch_size` or `per_device_train_batch_size` |
| Your job stopped when the laptop slept | It was not running inside `tmux` | Start it again inside `tmux new -s gf` |

Previous: [8. Classify](08-classify.md) · Back to the [README](../README.md)
