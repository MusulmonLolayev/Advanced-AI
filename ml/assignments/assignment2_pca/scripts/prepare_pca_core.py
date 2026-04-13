"""Prepare core PCA datasets used throughout the assignment."""

from __future__ import annotations

from pathlib import Path

from common import DATASETS_DIR, make_knn_comparison_bundle, make_pca_core_dataset, save_bundle


def prepare_pca_core_dataset(overwrite: bool = False) -> Path:
    path = DATASETS_DIR / "pca_core_toy.npz"
    if path.exists() and not overwrite:
        return path
    return save_bundle(path, **make_pca_core_dataset())


def prepare_pca_knn_comparison_dataset(overwrite: bool = False) -> Path:
    path = DATASETS_DIR / "pca_knn_comparison.npz"
    if path.exists() and not overwrite:
        return path
    return save_bundle(path, **make_knn_comparison_bundle())


def main() -> None:
    print(prepare_pca_core_dataset(overwrite=True))
    print(prepare_pca_knn_comparison_dataset(overwrite=True))


if __name__ == "__main__":
    main()
