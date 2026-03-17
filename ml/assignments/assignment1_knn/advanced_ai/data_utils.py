"""Starter data utilities for Assignment 1."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_tabular_dataset(path: str | Path, target_col: int = -1, skiprows: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Load a CSV or NPZ feature-label dataset."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    if path.suffix == ".npz":
        bundle = np.load(path, allow_pickle=True)
        if "X" not in bundle or "y" not in bundle:
            raise KeyError("Expected keys 'X' and 'y' in NPZ dataset.")
        return np.asarray(bundle["X"], dtype=np.float64), np.asarray(bundle["y"])

    data = np.loadtxt(path, delimiter=",", skiprows=skiprows)
    X = np.asarray(np.delete(data, target_col, axis=1), dtype=np.float64)
    y = np.asarray(data[:, target_col])
    return X, y


def _load_required_npz(path: str | Path, required_keys: list[str]) -> dict[str, np.ndarray]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    bundle = np.load(path, allow_pickle=True)
    for key in required_keys:
        if key not in bundle:
            raise KeyError(f"Missing key '{key}' in dataset bundle.")
    return {key: bundle[key] for key in required_keys}


def train_val_test_split(
    X: np.ndarray,
    y: np.ndarray,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    seed: int = 231,
    shuffle: bool = True,
) -> dict[str, np.ndarray]:
    """Split a labeled dataset into train/val/test partitions."""
    X = np.asarray(X)
    y = np.asarray(y)
    n = X.shape[0]

    idx = np.arange(n)
    if shuffle:
        rng = np.random.default_rng(seed)
        rng.shuffle(idx)

    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    train_idx = idx[:n_train]
    val_idx = idx[n_train : n_train + n_val]
    test_idx = idx[n_train + n_val :]

    return {
        "X_train": X[train_idx],
        "y_train": y[train_idx],
        "X_val": X[val_idx],
        "y_val": y[val_idx],
        "X_test": X[test_idx],
        "y_test": y[test_idx],
    }


def make_labeled_split(
    X: np.ndarray,
    y: np.ndarray,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    seed: int = 231,
    shuffle: bool = True,
    standardize: bool = False,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray] | None]:
    """Create one labeled split and optionally standardize it."""
    data = train_val_test_split(
        X,
        y,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        seed=seed,
        shuffle=shuffle,
    )
    if not standardize:
        return data, None

    standardized_data, stats = standardized_split(data)
    return standardized_data, stats


def standardize_from_train(
    X_train: np.ndarray,
    X_val: np.ndarray,
    X_test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    """Standardize using training-set statistics only."""
    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std = np.where(std < 1e-12, 1.0, std)

    return (
        (X_train - mean) / std,
        (X_val - mean) / std,
        (X_test - mean) / std,
        {"mean": mean, "std": std},
    )


def standardized_split(data: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Return a copy of a labeled split with standardized features."""
    X_train, X_val, X_test, stats = standardize_from_train(
        data["X_train"], data["X_val"], data["X_test"]
    )
    standardized = dict(data)
    standardized["X_train"] = X_train
    standardized["X_val"] = X_val
    standardized["X_test"] = X_test
    return standardized, stats


def load_retrieval_bundle(path: str | Path) -> dict[str, np.ndarray]:
    """Load instructor-prepared retrieval embeddings and metadata."""
    required = [
        "query_embeddings",
        "doc_embeddings",
        "relevance",
        "query_lengths",
        "doc_lengths",
    ]
    return _load_required_npz(path, required)


def load_anomaly_bundle(path: str | Path) -> dict[str, np.ndarray]:
    """Load an anomaly-detection bundle prepared by the instructor."""
    required = ["X_train", "X_val", "y_val", "X_test", "y_test"]
    return _load_required_npz(path, required)
