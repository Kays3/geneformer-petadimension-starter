# Lesson 4. Install Python and Geneformer

This lesson installs everything lessons 5 to 8 need. Do it on the computer
where you will run them: your laptop, or a remote Linux machine
(lesson 3). The steps are the same, except where marked.

Allow about 30 minutes and 3 GB of disk. Most of the time goes on downloads.

## What you are installing

- **Python** runs the analysis scripts.
- **conda** keeps a separate copy of Python and its add-ons for each project,
  called an **environment**, so projects cannot break each other. We use
  Miniforge, a small free distribution of conda.
- **Git** downloads code; **Git LFS** ("large file storage") downloads the
  large model files that Git alone skips.
- **Geneformer** itself, plus one trained model (about 420 MB).

## Step 1. Install Miniforge

This downloads the installer for your system and runs it without questions
(`-b`), then sets up your terminal to find conda:

```bash
cd ~
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash "Miniforge3-$(uname)-$(uname -m).sh" -b
~/miniforge3/bin/conda init "$(basename "$SHELL")"
```

**Close the terminal and open a new one.** You should see `(base)` at the
start of the prompt:

```text
(base) yourname@laptop ~ %
```

## Step 2. Create the tutorial environment

This makes an environment called `geneformer` with Python 3.11, Git and Git
LFS, and switches to it:

```bash
conda create -n geneformer -c conda-forge python=3.11 git git-lfs -y
conda activate geneformer
python --version
```

You should see:

```text
Python 3.11.x
```

and the prompt now starts with `(geneformer)`. Run
`conda activate geneformer` every time you open a new terminal for this
tutorial.

## Step 3. Linux without a GPU only: install the small PyTorch

**PyTorch** is the library Geneformer uses to do its calculations. On Linux,
the default download includes GPU support and is several gigabytes. On a
Linux machine without a GPU, install the
CPU-only version first. Skip this step on macOS.

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

For a machine with an NVIDIA GPU, see [lesson 9](09-next-steps.md).

## Step 4. Download Geneformer and one model

The Geneformer download holds several models, several gigabytes in all. These
commands fetch the code, the V2 gene lists, and only the 104M model:

```bash
cd ~/geneformer-tutorial
git lfs install
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/ctheodoris/Geneformer
cd Geneformer
git lfs pull --include="geneformer/*.pkl,Geneformer-V2-104M/*"
pip install .
pip install "pandas<3" "transformers<5"
cd ..
```

Line by line: turn on Git LFS; download the code but not the large files;
fetch only the files we need; install Geneformer and the libraries it uses
(this takes a few minutes); keep pandas at version 2 and transformers at
version 4, because Geneformer does not yet work with pandas 3 or transformers
5. Without the transformers pin, step 5 fails with
`cannot import name 'SpecialTokensMixin' from 'transformers'` (found when this
lesson was tested on a GPU machine, October 2026).

## Step 5. Check that it works

Create the file with `nano`:

```bash
cd ~/geneformer-tutorial
nano check_install.py
```

Paste the script below, press `Ctrl` + `O` and `Return` to save, then
`Ctrl` + `X` to leave. The later lessons save their scripts the same way.

```python
from pathlib import Path

import pandas
import torch
from geneformer import TranscriptomeTokenizer

model = Path("Geneformer/Geneformer-V2-104M/model.safetensors")
print("pandas", pandas.__version__)
print("torch", torch.__version__, "| GPU available:", torch.cuda.is_available())
print("Geneformer tokenizer:", TranscriptomeTokenizer.__name__)
print("model file MB:", round(model.stat().st_size / 1e6))
```

```bash
python check_install.py
```

You should see something like:

```text
pandas 2.x.x
torch 2.x.x | GPU available: False
Geneformer tokenizer: TranscriptomeTokenizer
model file MB: 418
```

`GPU available: False` is expected on a laptop; on a machine with a working NVIDIA GPU it
reads `True` (lesson 9). If the model size is under 1 MB, the model was not
downloaded (see Troubleshooting).

Your folder now looks like this:

```text
~/geneformer-tutorial/
├── check_install.py
└── Geneformer/
    ├── geneformer/            # the code, with the gene lists (.pkl files)
    └── Geneformer-V2-104M/    # the model
```

By the end of lesson 8 the folder will also hold the scripts you save and a
`pbmc/` folder of results:

```text
~/geneformer-tutorial/
├── Geneformer/
├── check_install.py, prepare_pbmc.py, tokenize_pbmc.py, ...
└── pbmc/
    ├── data/       # downloaded example data (lesson 5)
    ├── input/      # prepared .h5ad for the tokenizer (lesson 5)
    ├── tokens/     # tokenized dataset (lesson 6)
    ├── results/    # embeddings, UMAP picture (lessons 7 and 8)
    └── finetune/   # fine-tuning run (lesson 8, GPU only)
```

## You should now see

`python check_install.py` prints four lines with no error, and the model file
is about 418 MB.

## Troubleshooting

| You see | What it means | What to do |
| --- | --- | --- |
| `can't open file ... check_install.py` or `FileNotFoundError` | You are in a different folder | `cd ~/geneformer-tutorial` and run again |
| `conda: command not found` | The terminal was not reopened after step 1 | Close and reopen it; if it persists, run `~/miniforge3/bin/conda init "$(basename "$SHELL")"` again |
| `model file MB: 0`, or errors mentioning `.pkl` or `safetensors` header | Git LFS left small placeholder files instead of the real ones | `cd Geneformer`, rerun the `git lfs pull ...` line, then `cd ..` |

Previous: [3. A remote Linux machine](03-remote-machines.md) ·
Next: [5. Prepare data](05-prepare-data.md)
