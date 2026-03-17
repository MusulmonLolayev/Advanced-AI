"""Download and prepare the required core datasets."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import DATASETS_DIR, RAW_DIR, download_file, ensure_dir


BANKNOTE_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00267/"
    "data_banknote_authentication.txt"
)


def prepare_banknote_dataset(overwrite: bool = False) -> Path:
    ensure_dir(DATASETS_DIR)
    raw_path = download_file(BANKNOTE_URL, RAW_DIR / "banknote_authentication.txt", overwrite=overwrite)
    data = np.loadtxt(raw_path, delimiter=",", dtype=np.float64)
    out_path = DATASETS_DIR / "banknote_authentication.csv"
    np.savetxt(out_path, data, delimiter=",", fmt="%.10g")
    return out_path


def prepare_california_dataset(overwrite: bool = False) -> Path:
    from sklearn.datasets import fetch_california_housing

    ensure_dir(DATASETS_DIR)
    out_path = DATASETS_DIR / "california_housing.npz"
    if out_path.exists() and not overwrite:
        return out_path

    X, y = fetch_california_housing(data_home=str(RAW_DIR), return_X_y=True, as_frame=False)
    np.savez_compressed(out_path, X=np.asarray(X, dtype=np.float64), y=np.asarray(y, dtype=np.float64))
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    banknote_path = prepare_banknote_dataset(overwrite=args.overwrite)
    california_path = prepare_california_dataset(overwrite=args.overwrite)

    print(f"Saved banknote dataset to: {banknote_path}")
    print(f"Saved California dataset to: {california_path}")


if __name__ == "__main__":
    main()
