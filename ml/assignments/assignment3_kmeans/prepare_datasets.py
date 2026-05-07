#!/usr/bin/env python3
"""Prepare instructor-provided dataset bundles for Assignment 3: k-means."""

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


def _pca_2d(X: np.ndarray) -> np.ndarray:
    X_std = _standardize(X)
    _, _, vt = np.linalg.svd(X_std, full_matrices=False)
    return X_std @ vt[:2].T


def _save_iris_bundles() -> None:
    X, y = _load_iris_from_uci()

    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        DATASETS_DIR / "iris_clustering.npz",
        X=X,
        y=y,
        feature_names=IRIS_FEATURE_NAMES,
        target_names=IRIS_TARGET_NAMES,
    )

    X_pca2 = _pca_2d(X)
    np.savez_compressed(
        DATASETS_DIR / "pca_projection_clustering.npz",
        X=X,
        X_pca2=X_pca2,
        y=y,
        target_names=IRIS_TARGET_NAMES,
    )


def _make_init_study_dataset() -> np.ndarray:
    rng = np.random.default_rng(RANDOM_SEED)
    centers = np.array(
        [
            [-2.2, -1.6],
            [-1.0, -0.2],
            [2.4, 2.1],
            [3.3, -1.2],
        ],
        dtype=np.float64,
    )
    spreads = np.array([0.22, 0.24, 0.28, 0.20], dtype=np.float64)
    counts = np.array([54, 48, 56, 32], dtype=int)

    clouds = []
    for center, spread, count in zip(centers, spreads, counts, strict=True):
        cloud = rng.normal(loc=center, scale=spread, size=(count, 2))
        clouds.append(cloud)

    # Add a thin bridge between the two left clusters so different initializations
    # can converge to different local minima.
    bridge_t = np.linspace(0.0, 1.0, 18, endpoint=True)
    bridge = np.column_stack(
        [
            -2.2 + 1.2 * bridge_t,
            -1.6 + 1.4 * bridge_t + 0.12 * np.sin(4.0 * np.pi * bridge_t),
        ]
    )
    bridge += rng.normal(scale=0.05, size=bridge.shape)
    clouds.append(bridge)

    X = np.vstack(clouds)
    return X.astype(np.float64)


def _make_image_quantization_dataset() -> np.ndarray:
    h, w = 96, 96
    yy, xx = np.mgrid[0:h, 0:w]
    x = xx / (w - 1)
    y = yy / (h - 1)

    image = np.zeros((h, w, 3), dtype=np.float64)

    top = y < 0.5
    left = x < 0.5

    image[top & left, 0] = 220 - 70 * x[top & left]
    image[top & left, 1] = 70 + 120 * y[top & left]
    image[top & left, 2] = 40 + 30 * (1.0 - x[top & left])

    image[top & ~left, 0] = 40 + 30 * x[top & ~left]
    image[top & ~left, 1] = 120 + 90 * (1.0 - x[top & ~left])
    image[top & ~left, 2] = 200 - 40 * y[top & ~left]

    image[~top & left, 0] = 70 + 80 * y[~top & left]
    image[~top & left, 1] = 180 - 70 * x[~top & left]
    image[~top & left, 2] = 60 + 40 * y[~top & left]

    image[~top & ~left, 0] = 150 + 70 * x[~top & ~left]
    image[~top & ~left, 1] = 60 + 50 * y[~top & ~left]
    image[~top & ~left, 2] = 170 - 60 * x[~top & ~left]

    cx = 0.53
    cy = 0.48
    radius = 0.18
    mask = (x - cx) ** 2 + (y - cy) ** 2 <= radius**2
    image[mask, 0] = 245
    image[mask, 1] = 235
    image[mask, 2] = 80

    return np.clip(image, 0.0, 255.0)


def main() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    _save_iris_bundles()

    X_init = _make_init_study_dataset()
    np.savez_compressed(DATASETS_DIR / "initialization_study.npz", X=X_init)

    image = _make_image_quantization_dataset()
    np.savez_compressed(DATASETS_DIR / "image_quantization.npz", image=image)

    print(f"Prepared datasets in {DATASETS_DIR}")


if __name__ == "__main__":
    main()
