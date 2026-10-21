#!/usr/bin/env bash
# Set up the quickstart: fetch Geneformer at a pinned commit, then build the
# pinned Python environment with uv. Safe to run again. Needs git, git-lfs, uv.
set -euo pipefail
cd "$(dirname "$0")"

# Geneformer commit the quickstart was tested with (Hugging Face repository).
GENEFORMER_COMMIT="1f7fbae4e469a5f4f1af8c111a529cfe1b3829f5"

for tool in git git-lfs uv; do
  command -v "$tool" >/dev/null || { echo "Missing tool: $tool (see README.md)" >&2; exit 1; }
done

# Download the code without the large files, then fetch only what is needed:
# the gene dictionaries and the 104M-parameter V2 model (about 420 MB).
if [ ! -d Geneformer ]; then
  GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/ctheodoris/Geneformer
fi
git -C Geneformer checkout --quiet "$GENEFORMER_COMMIT"
git -C Geneformer lfs pull --include="geneformer/*.pkl,Geneformer-V2-104M/*"

# Refuse to continue if Git LFS left small placeholder files behind.
size=$(wc -c < Geneformer/Geneformer-V2-104M/model.safetensors)
if [ "$size" -lt 100000000 ]; then
  echo "The model file is only $size bytes: Git LFS did not download it." >&2
  exit 1
fi

uv sync
echo "Setup finished. Next: uv run python run_quickstart.py"
