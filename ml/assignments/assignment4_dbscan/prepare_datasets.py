#!/usr/bin/env python3
"""Prepare instructor-provided dataset bundles for Assignment 4: DBSCAN."""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

import numpy as np


ROOT = Path(__file__).resolve().parent
DATASETS_DIR = ROOT / "datasets"
RANDOM_SEED = 231
IRIS_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
IRIS_FEATURE_NAMES = np.asarray(
    ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"], dtype=object
)
IRIS_TARGET_NAMES = np.asarray(["setosa", "versicolor", "virginica"], dtype=object)
TOY_FEATURE_NAMES = np.asarray(["x_1", "x_2"], dtype=object)
TOY_TARGET_NAMES = np.asarray(["cluster_0", "cluster_1", "cluster_2", "noise"], dtype=object)


def _standardize(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std = np.where(std < 1e-12, 1.0, std)
    return (X - mean) / std


def _load_iris_from_uci() -> tuple[np.ndarray, np.ndarray]:
    rows: list[list[float]] = []
    labels: list[int] = []
    label_to_index = {name: idx for idx, name in enumerate(IRIS_TARGET_NAMES.tolist())}
    with urlopen(IRIS_URL, timeout=30) as response:
        for raw_line in response.read().decode("utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split(",")]
            if len(parts) != 5:
                continue
            rows.append([float(value) for value in parts[:4]])
            labels.append(label_to_index[parts[4].replace("Iris-", "")])
    return np.asarray(rows, dtype=np.float64), np.asarray(labels, dtype=np.int64)


def _save_iris_bundle() -> None:
    X, y = _load_iris_from_uci()
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        DATASETS_DIR / "iris_dbscan.npz",
        X=X,
        y=y,
        feature_names=IRIS_FEATURE_NAMES,
        target_names=IRIS_TARGET_NAMES,
    )


def _make_toy_bundle() -> None:
    rng = np.random.default_rng(RANDOM_SEED)
    cluster0 = rng.normal(loc=(-2.2, -1.6), scale=(0.18, 0.16), size=(28, 2))
    cluster1 = rng.normal(loc=(0.0, 2.2), scale=(0.17, 0.16), size=(30, 2))
    cluster2 = rng.normal(loc=(2.7, -0.5), scale=(0.20, 0.18), size=(26, 2))
    noise = np.array([[-4.2, 3.5], [4.4, 3.1], [4.8, -3.3], [-3.8, -3.0], [0.0, -4.1]], dtype=np.float64)
    X = np.vstack([cluster0, cluster1, cluster2, noise])
    y = np.concatenate(
        [
            np.zeros(cluster0.shape[0], dtype=np.int64),
            np.ones(cluster1.shape[0], dtype=np.int64),
            np.full(cluster2.shape[0], 2, dtype=np.int64),
            np.full(noise.shape[0], -1, dtype=np.int64),
        ]
    )
    np.savez_compressed(
        DATASETS_DIR / "toy_dbscan.npz",
        X=X,
        y=y,
        feature_names=TOY_FEATURE_NAMES,
        target_names=TOY_TARGET_NAMES,
    )


def _make_scaling_bundle() -> None:
    rng = np.random.default_rng(RANDOM_SEED + 7)
    cluster_a = np.column_stack(
        [
            rng.normal(-1.2, 0.18, size=36),
            rng.normal(70.0, 4.0, size=36),
        ]
    )
    cluster_b = np.column_stack(
        [
            rng.normal(1.3, 0.22, size=36),
            rng.normal(110.0, 4.5, size=36),
        ]
    )
    cluster_c = np.column_stack(
        [
            rng.normal(3.1, 0.20, size=36),
            rng.normal(150.0, 5.0, size=36),
        ]
    )
    X = np.vstack([cluster_a, cluster_b, cluster_c])
    y = np.concatenate(
        [
            np.zeros(cluster_a.shape[0], dtype=np.int64),
            np.ones(cluster_b.shape[0], dtype=np.int64),
            np.full(cluster_c.shape[0], 2, dtype=np.int64),
        ]
    )
    np.savez_compressed(DATASETS_DIR / "scaling_study.npz", X=X, y=y)


def _make_outlier_bundle() -> None:
    rng = np.random.default_rng(RANDOM_SEED + 13)
    dense_a = rng.normal(loc=(-2.0, -1.2), scale=(0.17, 0.15), size=(30, 2))
    dense_b = rng.normal(loc=(2.1, 1.9), scale=(0.18, 0.16), size=(30, 2))
    sparse_bridge = np.array([[0.0, 0.0], [0.7, 0.4], [1.0, -0.8]], dtype=np.float64)
    noise = np.array([[-4.5, 3.6], [4.6, 3.2], [5.0, -3.4], [-3.7, -3.3]], dtype=np.float64)
    X = np.vstack([dense_a, dense_b, sparse_bridge, noise])
    y = np.concatenate(
        [
            np.zeros(dense_a.shape[0], dtype=np.int64),
            np.ones(dense_b.shape[0], dtype=np.int64),
            np.full(sparse_bridge.shape[0], -1, dtype=np.int64),
            np.full(noise.shape[0], -1, dtype=np.int64),
        ]
    )
    np.savez_compressed(DATASETS_DIR / "outlier_study.npz", X=X, y=y)


def main() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    _save_iris_bundle()
    _make_toy_bundle()
    _make_scaling_bundle()
    _make_outlier_bundle()
    print(f"Prepared datasets in {DATASETS_DIR}")


if __name__ == "__main__":
    main()
