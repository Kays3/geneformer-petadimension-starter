# Quickstart

Three commands from a clean folder to Geneformer embeddings of public blood
cells, with automatic checks on the output. The [main README](../README.md)
has the picture of what happens, the measured times, the prerequisites and a
troubleshooting table.

```bash
./setup.sh
uv run python run_quickstart.py            # 300 cells
uv run python run_quickstart.py --cells 0  # all 2,638 cells
```

## Files

| File | What it is |
| --- | --- |
| `setup.sh` | Fetches Geneformer at a pinned commit, downloads the 104M model and gene dictionaries over HTTPS and verifies their checksums (no `git-lfs` needed), then builds the environment with `uv sync` |
| `pyproject.toml`, `uv.lock` | The pinned Python environment. `transformers<5` and `pandas<3` are required by Geneformer |
| `remote_run.sh` | Runs the quickstart on a GPU machine over ssh (Tailscale name or `~/.ssh/config` entry) inside tmux: `check`, `start`, `status`, `fetch`. See [lesson 3](../tutorial/03-remote-machines.md) |
| `run_quickstart.py` | Prepare, tokenize, embed, check, draw. Writes only to `results/` |
| `img/` | The picture used in the README |

## The output checks

`run_quickstart.py` stops with an error if the embeddings contain NaN, if any
cell has an all-zero embedding, or if the values are nearly constant across
cells. These are failures that do not raise an exception by themselves. See
[lesson 10](../tutorial/10-lessons-from-real-runs.md) for why.

## Changing the pins

Geneformer's commit is set in `setup.sh` (`GENEFORMER_COMMIT`) and the
Python packages in `pyproject.toml`. After changing either, delete `.venv`,
run `uv lock` and `./setup.sh`, rerun the quickstart from a clean folder, and
update the numbers in the main README.
