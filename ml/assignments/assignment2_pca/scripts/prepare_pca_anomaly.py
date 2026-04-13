"""Prepare synthetic anomaly-detection data for PCA."""

from __future__ import annotations

from pathlib import Path

from common import DATASETS_DIR, make_anomaly_bundle, save_bundle


def prepare_pca_anomaly_dataset(overwrite: bool = False) -> Path:
    path = DATASETS_DIR / "pca_anomaly.npz"
    if path.exists() and not overwrite:
        return path
    return save_bundle(path, **make_anomaly_bundle())


def main() -> None:
    print(prepare_pca_anomaly_dataset(overwrite=True))


if __name__ == "__main__":
    main()
