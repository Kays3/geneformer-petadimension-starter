"""Geneformer quickstart: public PBMC data -> tokens -> embeddings -> checks -> picture.

Run from this folder after setup.sh:
    uv run python run_quickstart.py              # 300 cells, a few minutes on a CPU
    uv run python run_quickstart.py --cells 0    # all 2,638 cells

Outputs go to ./results/. Nothing is written outside this folder.
"""

from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc
import torch
from datasets import load_from_disk
from geneformer import TranscriptomeTokenizer
from transformers import BertModel

HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE / "Geneformer" / "Geneformer-V2-104M"
WORK = HERE / "results"


def prepare(work: Path) -> None:
    """Download PBMC 3k (10x Genomics, public) and write the file the tokenizer reads."""
    data_dir, input_dir = work / "data", work / "input"
    data_dir.mkdir(parents=True, exist_ok=True)
    input_dir.mkdir(parents=True, exist_ok=True)
    sc.settings.datasetdir = str(data_dir)
    raw = sc.datasets.pbmc3k()  # raw UMI counts; var["gene_ids"] holds Ensembl IDs
    labelled = sc.datasets.pbmc3k_processed()  # QC-passed cells with cluster names
    adata = raw[labelled.obs_names].copy()
    adata.obs["cell_type"] = labelled.obs["louvain"].astype(str).to_numpy()
    adata.obs["cell_id"] = adata.obs_names.astype(str)
    adata.obs["n_counts"] = np.asarray(adata.X.sum(axis=1)).ravel().astype(float)
    adata.var["ensembl_id"] = adata.var["gene_ids"].astype(str).str.split(".").str[0]
    adata.var = adata.var[["ensembl_id"]]
    adata.write_h5ad(input_dir / "pbmc3k.h5ad")


def tokenize(work: Path) -> None:
    tokenizer = TranscriptomeTokenizer(
        custom_attr_name_dict={"cell_id": "cell_id", "cell_type": "cell_type"},
        nproc=2,
        model_version="V2",
    )
    tokenizer.tokenize_data(
        data_directory=str(work / "input"),
        output_directory=str(work / "tokens"),
        output_prefix="pbmc3k",
        file_format="h5ad",
    )


def embed(work: Path, n_cells: int, device: str) -> pd.DataFrame:
    tokens = load_from_disk(str(work / "tokens" / "pbmc3k.dataset"))
    if n_cells:
        tokens = tokens.shuffle(seed=42).select(range(n_cells))
    model = BertModel.from_pretrained(MODEL_DIR).to(device).eval()
    vectors = []
    with torch.no_grad():
        for i, input_ids in enumerate(tokens["input_ids"]):
            ids = torch.tensor([input_ids], device=device)
            out = model(input_ids=ids, output_hidden_states=True)
            vectors.append(out.hidden_states[-2][0][0].float().cpu().numpy())  # <cls> token
            if (i + 1) % 100 == 0:
                print(f"  {i + 1} / {len(tokens)} cells", flush=True)
    table = pd.DataFrame(np.vstack(vectors), index=tokens["cell_id"])
    table["cell_type"] = tokens["cell_type"]
    return table


def check_output(table: pd.DataFrame) -> None:
    """Fail loudly on the silent failures seen in real runs: NaN, all-zero output."""
    values = table.drop(columns=["cell_type"]).to_numpy(dtype="float64")
    nan = int(np.isnan(values).sum())
    zeros = int((values == 0).sum())
    zero_rows = int((np.abs(values).sum(axis=1) == 0).sum())
    spread = float(values.std(axis=0).mean())
    print(f"  values {values.size}, NaN {nan}, exact zeros {zeros}, all-zero cells {zero_rows}, mean per-dimension spread {spread:.3f}")
    assert nan == 0, "NaN in the embeddings"
    assert zero_rows == 0, "Some cells have an all-zero embedding"
    assert spread > 1e-3, "Embeddings are nearly constant across cells; something is wrong"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cells", type=int, default=300, help="cells to embed; 0 means all (default 300)")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    args = parser.parse_args()
    device = ("cuda" if torch.cuda.is_available() else "cpu") if args.device == "auto" else args.device

    if not MODEL_DIR.joinpath("model.safetensors").exists():
        raise SystemExit("Model not found. Run ./setup.sh first.")
    free_gb = shutil.disk_usage(HERE).free / 1e9
    print(f"device: {device}, free disk: {free_gb:.0f} GB")
    WORK.mkdir(exist_ok=True)

    t0 = time.time()
    print("1/4 download and prepare PBMC 3k"); prepare(WORK)
    print("2/4 tokenize"); tokenize(WORK)
    print(f"3/4 embed ({args.cells or 'all'} cells)"); table = embed(WORK, args.cells, device)
    print("4/4 check output and draw"); check_output(table)
    table.to_csv(WORK / "embeddings.csv")

    import anndata as ad
    emb = ad.AnnData(table.drop(columns=["cell_type"]).to_numpy(dtype="float32"),
                     obs=table[["cell_type"]].astype(str))
    sc.pp.neighbors(emb, use_rep="X", random_state=0)
    sc.tl.umap(emb, random_state=0)
    sc.settings.figdir = str(WORK)
    sc.pl.umap(emb, color="cell_type", save="_pbmc3k.png", show=False)
    print(f"done in {time.time() - t0:.0f} s. Picture: {WORK / 'umap_pbmc3k.png'}")


if __name__ == "__main__":
    main()
