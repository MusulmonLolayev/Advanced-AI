#!/usr/bin/env python3
"""Prepare instructor-provided dataset bundles for Assignment 6: Random Forests."""

from __future__ import annotations

from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
DATASETS_DIR = ROOT / "datasets"
RANDOM_SEED = 231

TOY_FEATURE_NAMES = np.asarray(["x_1", "x_2"], dtype=object)
TOY_TARGET_NAMES = np.asarray(["class_0", "class_1"], dtype=object)
IRIS_FEATURE_NAMES = np.asarray(
    ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"], dtype=object
)
IRIS_TARGET_NAMES = np.asarray(["setosa", "versicolor", "virginica"], dtype=object)
FOREST_STUDY_FEATURE_NAMES = np.asarray(
    ["income_k", "age_years", "tenure_months", "support_calls", "noise_1", "noise_2"], dtype=object
)
FOREST_STUDY_TARGET_NAMES = np.asarray(["retained", "churned"], dtype=object)


def _make_toy_bundle() -> None:
    rng = np.random.default_rng(RANDOM_SEED + 11)
    n_per_class = 40
    class_0 = rng.normal(loc=[1.4, 1.6], scale=[0.9, 0.8], size=(n_per_class, 2))
    class_1 = rng.normal(loc=[3.0, 2.6], scale=[0.9, 0.8], size=(n_per_class, 2))

    X = np.vstack([class_0, class_1])
    y = np.concatenate(
        [np.zeros(n_per_class, dtype=np.int64), np.ones(n_per_class, dtype=np.int64)]
    )

    order = rng.permutation(X.shape[0])
    X = X[order]
    y = y[order]

    np.savez_compressed(
        DATASETS_DIR / "toy_forest.npz",
        X=X,
        y=y,
        feature_names=TOY_FEATURE_NAMES,
        target_names=TOY_TARGET_NAMES,
    )


def _load_local_iris() -> tuple[np.ndarray, np.ndarray] | None:
    candidates = [
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


def _make_iris_bundle() -> None:
    loaded = _load_local_iris()
    if loaded is None:
        X, y = _make_iris_like_fallback()
    else:
        X, y = loaded
    np.savez_compressed(
        DATASETS_DIR / "iris_forest.npz",
        X=X,
        y=y,
        feature_names=IRIS_FEATURE_NAMES,
        target_names=IRIS_TARGET_NAMES,
    )


def _make_forest_study_bundle() -> None:
    rng = np.random.default_rng(RANDOM_SEED + 29)
    n_per_class = 150

    retained_mean = np.array([85.0, 42.0, 36.0, 1.0])
    churned_mean = np.array([45.0, 27.0, 6.0, 4.5])
    scale = np.array([18.0, 9.0, 10.0, 1.6])

    retained = rng.normal(loc=retained_mean, scale=scale, size=(n_per_class, 4))
    churned = rng.normal(loc=churned_mean, scale=scale, size=(n_per_class, 4))
    informative = np.vstack([retained, churned])

    noise = rng.normal(loc=0.0, scale=1.0, size=(2 * n_per_class, 2))
    X = np.hstack([informative, noise])
    y = np.concatenate(
        [np.zeros(n_per_class, dtype=np.int64), np.ones(n_per_class, dtype=np.int64)]
    )

    order = rng.permutation(X.shape[0])
    X = X[order]
    y = y[order]

    np.savez_compressed(
        DATASETS_DIR / "forest_study.npz",
        X=X,
        y=y,
        feature_names=FOREST_STUDY_FEATURE_NAMES,
        target_names=FOREST_STUDY_TARGET_NAMES,
    )


def main() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    _make_toy_bundle()
    _make_iris_bundle()
    _make_forest_study_bundle()
    print(f"Prepared datasets in {DATASETS_DIR}")


if __name__ == "__main__":
    main()
