#!/usr/bin/env python3
"""Prepare instructor-provided dataset bundles for Assignment 7: Forest Variants."""

from __future__ import annotations

from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
DATASETS_DIR = ROOT / "datasets"
RANDOM_SEED = 231

ISOLATION_FEATURE_NAMES = np.asarray(["x_1", "x_2"], dtype=object)
IRIS_FEATURE_NAMES = np.asarray(
    ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"], dtype=object
)
IRIS_TARGET_NAMES = np.asarray(["setosa", "versicolor", "virginica"], dtype=object)
QUANTILE_FEATURE_NAMES = np.asarray(["x_1"], dtype=object)


def _make_isolation_bundle() -> None:
    rng = np.random.default_rng(RANDOM_SEED + 5)
    n_normal = 200
    cluster_a = rng.normal(loc=[0.0, 0.0], scale=0.6, size=(n_normal // 2, 2))
    cluster_b = rng.normal(loc=[4.0, 3.0], scale=0.6, size=(n_normal // 2, 2))
    normal = np.vstack([cluster_a, cluster_b])

    outliers = np.array(
        [
            [-6.0, 6.0],
            [9.0, -5.0],
            [-7.0, -6.0],
            [10.0, 9.0],
            [-5.0, 9.5],
            [8.5, -7.0],
            [11.0, 2.0],
            [-8.0, 1.0],
            [2.0, -8.0],
            [6.0, 10.0],
        ],
        dtype=np.float64,
    )

    X = np.vstack([normal, outliers])
    y_outlier = np.concatenate(
        [np.zeros(normal.shape[0], dtype=np.int64), np.ones(outliers.shape[0], dtype=np.int64)]
    )

    order = rng.permutation(X.shape[0])
    X = X[order]
    y_outlier = y_outlier[order]

    np.savez_compressed(
        DATASETS_DIR / "isolation_toy.npz",
        X=X,
        y_outlier=y_outlier,
        feature_names=ISOLATION_FEATURE_NAMES,
    )


def _load_local_iris() -> tuple[np.ndarray, np.ndarray] | None:
    candidates = [
        ROOT.parent / "assignment6_random_forests" / "datasets" / "iris_forest.npz",
        ROOT.parent / "assignment5_decision_trees" / "datasets" / "iris_tree.npz",
        ROOT.parent / "assignment4_dbscan" / "datasets" / "iris_dbscan.npz",
        ROOT.parent / "assignment3_kmeans" / "datasets" / "iris_clustering.npz",
    ]
    for path in candidates:
        if not path.exists():
            continue
        with np.load(path, allow_pickle=True) as bundle:
            if "X" in bundle and "y" in bundle:
                return np.asarray(bundle["X"], dtype=np.float64), np.asarray(bundle["y"], dtype=np.int64)
    return None


def _make_iris_like_fallback() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(RANDOM_SEED + 17)
    means = np.array(
        [
            [5.0, 3.4, 1.5, 0.2],
            [5.9, 2.8, 4.2, 1.3],
            [6.6, 3.0, 5.5, 2.0],
        ],
        dtype=np.float64,
    )
    scales = np.array(
        [
            [0.28, 0.25, 0.18, 0.08],
            [0.36, 0.25, 0.35, 0.16],
            [0.42, 0.30, 0.40, 0.20],
        ],
        dtype=np.float64,
    )
    X_parts = [rng.normal(loc=means[c], scale=scales[c], size=(50, 4)) for c in range(3)]
    X = np.vstack(X_parts)
    y = np.repeat(np.arange(3, dtype=np.int64), 50)
    return X, y


def _make_extra_trees_bundle() -> None:
    loaded = _load_local_iris()
    if loaded is None:
        X, y = _make_iris_like_fallback()
    else:
        X, y = loaded
    np.savez_compressed(
        DATASETS_DIR / "extra_trees_iris.npz",
        X=X,
        y=y,
        feature_names=IRIS_FEATURE_NAMES,
        target_names=IRIS_TARGET_NAMES,
    )


def _make_quantile_bundle() -> None:
    rng = np.random.default_rng(RANDOM_SEED + 41)
    n = 300
    X = np.sort(rng.uniform(0.0, 10.0, size=n))
    noise_scale = 0.3 + 0.15 * X
    y = 3.0 * np.sin(X) + rng.normal(0.0, 1.0, size=n) * noise_scale

    indices = rng.permutation(n)
    n_test = int(round(0.2 * n))
    test_idx = np.sort(indices[:n_test])
    train_idx = np.sort(indices[n_test:])

    np.savez_compressed(
        DATASETS_DIR / "quantile_regression.npz",
        X_train=X[train_idx].reshape(-1, 1),
        y_train=y[train_idx],
        X_test=X[test_idx].reshape(-1, 1),
        y_test=y[test_idx],
        feature_names=QUANTILE_FEATURE_NAMES,
    )


def main() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    _make_isolation_bundle()
    _make_extra_trees_bundle()
    _make_quantile_bundle()
    print(f"Prepared datasets in {DATASETS_DIR}")


if __name__ == "__main__":
    main()
