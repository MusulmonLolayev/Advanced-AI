#!/usr/bin/env python3
"""Prepare instructor-provided dataset bundles for Assignment 5: Decision Trees."""

from __future__ import annotations

from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
DATASETS_DIR = ROOT / "datasets"
RANDOM_SEED = 231

FEATURE_NAMES_2D = np.asarray(["x_1", "x_2"], dtype=object)
BINARY_TARGET_NAMES = np.asarray(["class_0", "class_1"], dtype=object)
IRIS_FEATURE_NAMES = np.asarray(
    ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"], dtype=object
)
IRIS_TARGET_NAMES = np.asarray(["setosa", "versicolor", "virginica"], dtype=object)


def _make_toy_bundle() -> None:
    X = np.array(
        [
            [0.8, 1.1],
            [1.2, 1.7],
            [1.5, 0.8],
            [2.1, 1.3],
            [2.7, 2.2],
            [3.0, 1.0],
            [3.4, 2.8],
            [3.8, 1.7],
            [4.2, 3.1],
            [4.6, 2.3],
            [5.1, 3.4],
            [5.4, 2.6],
        ],
        dtype=np.float64,
    )
    y = np.asarray([0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1], dtype=np.int64)
    np.savez_compressed(
        DATASETS_DIR / "toy_tree.npz",
        X=X,
        y=y,
        feature_names=FEATURE_NAMES_2D,
        target_names=BINARY_TARGET_NAMES,
    )


def _load_local_iris() -> tuple[np.ndarray, np.ndarray] | None:
    candidates = [
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


def _save_iris_bundle() -> None:
    loaded = _load_local_iris()
    if loaded is None:
        X, y = _make_iris_like_fallback()
    else:
        X, y = loaded
    np.savez_compressed(
        DATASETS_DIR / "iris_tree.npz",
        X=X,
        y=y,
        feature_names=IRIS_FEATURE_NAMES,
        target_names=IRIS_TARGET_NAMES,
    )


def _make_depth_study_bundle() -> None:
    rng = np.random.default_rng(RANDOM_SEED + 31)
    n = 180
    theta0 = rng.uniform(0.0, np.pi, size=n // 2)
    theta1 = rng.uniform(0.0, np.pi, size=n // 2)

    outer = np.column_stack([np.cos(theta0), np.sin(theta0)])
    inner = np.column_stack([1.0 - np.cos(theta1), 0.45 - np.sin(theta1)])
    X = np.vstack([outer, inner])
    X += rng.normal(0.0, 0.08, size=X.shape)
    y = np.concatenate([np.zeros(n // 2, dtype=np.int64), np.ones(n // 2, dtype=np.int64)])

    outliers = np.array([[-1.2, -0.2], [2.1, 0.85], [0.3, 1.35], [1.4, -0.85]], dtype=np.float64)
    outlier_labels = np.asarray([1, 0, 1, 0], dtype=np.int64)
    X = np.vstack([X, outliers])
    y = np.concatenate([y, outlier_labels])

    np.savez_compressed(
        DATASETS_DIR / "depth_study.npz",
        X=X,
        y=y,
        feature_names=FEATURE_NAMES_2D,
        target_names=BINARY_TARGET_NAMES,
    )


def main() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    _make_toy_bundle()
    _save_iris_bundle()
    _make_depth_study_bundle()
    print(f"Prepared datasets in {DATASETS_DIR}")


if __name__ == "__main__":
    main()
