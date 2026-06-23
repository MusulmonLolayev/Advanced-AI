"""Dataset helpers for Assignment 6."""

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


def load_toy_bundle(path: str | Path) -> dict[str, np.ndarray]:
    return _load_required_npz(path, ["X", "y", "feature_names", "target_names"])


def load_iris_bundle(path: str | Path) -> dict[str, np.ndarray]:
    return _load_required_npz(path, ["X", "y", "feature_names", "target_names"])


def load_forest_study_bundle(path: str | Path) -> dict[str, np.ndarray]:
    return _load_required_npz(path, ["X", "y", "feature_names", "target_names"])


def train_val_split(
    X: np.ndarray,
    y: np.ndarray,
    val_fraction: float = 0.25,
    seed: int = 231,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    if X.shape[0] != y.shape[0]:
        raise ValueError("X and y must contain the same number of examples.")
    if not 0.0 < val_fraction < 1.0:
        raise ValueError("val_fraction must be between 0 and 1.")

    rng = np.random.default_rng(seed)
    indices = rng.permutation(X.shape[0])
    n_val = max(1, int(round(val_fraction * X.shape[0])))
    val_idx = indices[:n_val]
    train_idx = indices[n_val:]
    return X[train_idx], X[val_idx], y[train_idx], y[val_idx]
