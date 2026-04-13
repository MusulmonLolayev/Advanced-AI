"""Prepare synthetic text embedding data for PCA visualization."""

from __future__ import annotations

from pathlib import Path

from common import DATASETS_DIR, make_text_embeddings_bundle, save_bundle


def prepare_pca_text_embeddings(overwrite: bool = False) -> Path:
    path = DATASETS_DIR / "pca_text_embeddings.npz"
    if path.exists() and not overwrite:
        return path
    return save_bundle(path, **make_text_embeddings_bundle())


def main() -> None:
    print(prepare_pca_text_embeddings(overwrite=True))


if __name__ == "__main__":
    main()
