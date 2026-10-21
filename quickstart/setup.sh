#!/usr/bin/env bash
# Set up the quickstart: fetch Geneformer at a pinned commit, download the
# large files it needs, then build the pinned Python environment with uv.
# Safe to run again. Needs git, curl, sha256sum (or shasum) and uv. It does not
# need git-lfs: the large files are fetched over HTTPS and checked against the
# checksums recorded in Git.
set -euo pipefail
cd "$(dirname "$0")"

# Geneformer commit the quickstart was tested with (Hugging Face repository).
GENEFORMER_COMMIT="1f7fbae4e469a5f4f1af8c111a529cfe1b3829f5"
REPO_URL="https://huggingface.co/ctheodoris/Geneformer"

for tool in git curl uv; do
  command -v "$tool" >/dev/null || { echo "Missing tool: $tool (see README.md)" >&2; exit 1; }
done
if command -v sha256sum >/dev/null; then sha() { sha256sum "$1" | cut -d' ' -f1; }
elif command -v shasum >/dev/null; then sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
else echo "Missing tool: sha256sum or shasum" >&2; exit 1; fi

# Code only: large files arrive as small pointer files that name their checksum.
if [ ! -d Geneformer ]; then
  GIT_LFS_SKIP_SMUDGE=1 git clone --quiet "$REPO_URL" Geneformer
fi
git -C Geneformer checkout --quiet "$GENEFORMER_COMMIT"

# Replace the pointers we need (gene dictionaries and the 104M V2 model, about
# 420 MB in all) with the real files, and verify each one.
cd Geneformer
git ls-files 'geneformer/*.pkl' 'Geneformer-V2-104M/*' | while read -r file; do
  if head -c 64 "$file" | grep -q '^version https://git-lfs'; then
    want_oid=$(sed -n 's/^oid sha256://p' "$file")
    want_size=$(sed -n 's/^size //p' "$file")
    echo "downloading $file ($((want_size / 1000000)) MB)"
    curl --fail --location --silent --show-error --retry 3 \
      -o "$file.part" "$REPO_URL/resolve/$GENEFORMER_COMMIT/$file"
    [ "$(sha "$file.part")" = "$want_oid" ] || { echo "Checksum mismatch for $file" >&2; rm -f "$file.part"; exit 1; }
    mv "$file.part" "$file"
  fi
done
cd ..

# Refuse to continue if the model is still a placeholder.
size=$(wc -c < Geneformer/Geneformer-V2-104M/model.safetensors)
if [ "$size" -lt 100000000 ]; then
  echo "The model file is only $size bytes: the download did not complete." >&2
  exit 1
fi

uv sync
echo "Setup finished. Next: uv run python run_quickstart.py"
