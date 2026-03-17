"""End-to-end anomaly dataset download and feature preparation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import DATASETS_DIR, RAW_DIR, ensure_dir


def _split_object_columns(X: np.ndarray) -> tuple[list[int], list[int]]:
    categorical_idx: list[int] = []
    numeric_idx: list[int] = []
    for col_idx in range(X.shape[1]):
        value = X[0, col_idx]
        if isinstance(value, (bytes, str)):
            categorical_idx.append(col_idx)
        else:
            numeric_idx.append(col_idx)
    return numeric_idx, categorical_idx


def prepare_network_anomaly_dataset(overwrite: bool = False) -> Path:
    from sklearn.compose import ColumnTransformer
    from sklearn.datasets import fetch_kddcup99
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    ensure_dir(DATASETS_DIR)
    out_path = DATASETS_DIR / "network_anomaly.npz"
    if out_path.exists() and not overwrite:
        return out_path

    bunch = fetch_kddcup99(
        data_home=str(RAW_DIR),
        subset="SA",
        percent10=True,
        shuffle=True,
        random_state=231,
    )
    X = bunch.data
    y = (bunch.target != b"normal.").astype(np.int32)

    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=231,
        stratify=y,
    )
    X_train_pool, X_val, y_train_pool, y_val = train_test_split(
        X_train_full,
        y_train_full,
        test_size=0.2,
        random_state=231,
        stratify=y_train_full,
    )

    normal_mask = y_train_pool == 0
    X_train = X_train_pool[normal_mask]

    numeric_idx, categorical_idx = _split_object_columns(X_train)
    numeric_transformer = Pipeline([("scaler", StandardScaler())])
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_idx),
            ("cat", categorical_transformer, categorical_idx),
        ]
    )

    X_train_processed = preprocessor.fit_transform(X_train)
    X_val_processed = preprocessor.transform(X_val)
    X_test_processed = preprocessor.transform(X_test)

    np.savez_compressed(
        out_path,
        X_train=np.asarray(X_train_processed, dtype=np.float32),
        X_val=np.asarray(X_val_processed, dtype=np.float32),
        y_val=np.asarray(y_val, dtype=np.int32),
        X_test=np.asarray(X_test_processed, dtype=np.float32),
        y_test=np.asarray(y_test, dtype=np.int32),
        dataset_name=np.asarray("kddcup99_sa"),
    )
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    out_path = prepare_network_anomaly_dataset(overwrite=args.overwrite)
    print(f"Saved anomaly dataset to: {out_path}")


if __name__ == "__main__":
    main()
