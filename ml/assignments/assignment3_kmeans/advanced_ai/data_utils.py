"""Starter data utilities for Assignment 3: k-means."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def _load_required_npz(path: str | Path, required_keys: list[str]) -> dict[str, np.ndarray]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    with np.load(path, allow_pickle=True) as bundle:
        for key in required_keys:
            if key not in bundle:
                raise KeyError(f"Missing key '{key}' in dataset bundle.")
        return {key: np.asarray(bundle[key]) for key in required_keys}


def load_npz_bundle(path: str | Path, required_keys: list[str]) -> dict[str, np.ndarray]:
    return _load_required_npz(path, required_keys)


def standardize_features(X: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    X = np.asarray(X, dtype=np.float64)
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std = np.where(std < 1e-12, 1.0, std)
    return (X - mean) / std, {"mean": mean, "std": std}


def load_iris_bundle(path: str | Path) -> dict[str, np.ndarray]:
    return _load_required_npz(path, ["X", "y", "feature_names", "target_names"])


def load_projection_bundle(path: str | Path) -> dict[str, np.ndarray]:
    return _load_required_npz(path, ["X", "X_pca2", "y", "target_names"])


def load_init_study_bundle(path: str | Path) -> dict[str, np.ndarray]:
    return _load_required_npz(path, ["X"])


def load_image_bundle(path: str | Path) -> dict[str, np.ndarray]:
    return _load_required_npz(path, ["image"])
