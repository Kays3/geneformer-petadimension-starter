# Lesson 0. Start here

This tutorial is for people new to Geneformer and to working in a terminal. It assumes you have never used a
terminal, Python, or a remote computer. By the end you will have run
Geneformer, a model trained on single-cell gene expression data, on a small
public dataset, and you will know how to use a remote Linux machine for larger jobs.

Technical terms are explained in the [glossary](GLOSSARY.md).

## What you need

- A laptop. The instructions are written for macOS; notes for Linux and
  Windows appear where the steps differ.
- About 5 GB of free disk space on a laptop (our estimate). A GPU machine
  needs more: the GPU test run used about 11 GB, most of it the GPU
  build of PyTorch.
- An internet connection.
- Optional, for [lesson 3](03-remote-machines.md): an account on a remote Linux
  machine, ideally one with an NVIDIA GPU. Your institution provides this.

## How to read the lessons

You type commands in a **terminal** (lesson 1 shows you how to open one). They are
shown in grey boxes like this:

```bash
echo "hello"
```

Copy the whole box (on GitHub, use the copy button at the top right of the
box), paste it into the terminal, and press Return. If any line prints an
error, stop there and check the Troubleshooting table before going on. Lines
that start with `#` are comments for you to read; the terminal ignores them.

What the terminal should print back is shown in a separate box labelled
*You should see*:

```text
hello
```

Your output will not always match character for character (dates, version
numbers, and folder names differ), but it should look the same in shape. If
you see something very different, check the Troubleshooting table at the
end of the lesson.

## The lessons

| Lesson | What you do | About |
| --- | --- | --- |
| [1. The terminal](01-terminal.md) | Open a terminal and move between folders | 15 min |
| [2. Geneformer in plain words](02-geneformer-in-plain-words.md) | Learn what the model does, without code | 15 min |
| [3. A remote Linux machine](03-remote-machines.md) | Log in over SSH, check resources, keep jobs running | 20 min, once you have an account |
| [4. Install Python and Geneformer](04-install.md) | Set up everything the later lessons need | 30 min |
| [5. Prepare data](05-prepare-data.md) | Download a small public dataset and get it ready | 10 min |
| [6. Tokenize](06-tokenize.md) | Turn each cell into the model's input | 5 min |
| [7. Embeddings](07-embeddings.md) | Get one vector per cell and draw a map of the cells | 20 min or more on a CPU; 1 min on a GPU |
| [8. Classify](08-classify.md) | Predict cell types from the vectors | 10 min |
| [9. Next steps](09-next-steps.md) | Fine-tuning on a GPU, in silico perturbation | reading |

Lessons 5 to 8 run on a laptop. You can also run them on a remote machine after
lesson 3; the commands are the same.

## You should now see

A folder of lessons and a plan. Next: [1. The terminal](01-terminal.md).
