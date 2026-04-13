"""Nearest-neighbor utility used by the PCA comparison tasks.

This helper is intentionally small and NumPy-only so the PCA assignment can
compare representations without introducing an external nearest-neighbor
dependency.
"""

from __future__ import annotations

import numpy as np


class KNearestNeighbor:
    """Simple k-NN classifier for downstream comparison experiments."""

    def __init__(self) -> None:
        self.X_train: np.ndarray | None = None
        self.y_train: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "KNearestNeighbor":
        self.X_train = np.asarray(X, dtype=np.float64)
        self.y_train = np.asarray(y)
        return self

    def predict(self, X: np.ndarray, k: int = 1) -> np.ndarray:
        if self.X_train is None or self.y_train is None:
            raise ValueError("Call fit before predict.")
        if k < 1:
            raise ValueError("k must be at least 1.")
        if k > self.X_train.shape[0]:
            raise ValueError("k cannot exceed the number of training examples.")

        X = np.asarray(X, dtype=np.float64)
        train_sq = np.sum(self.X_train ** 2, axis=1)
        test_sq = np.sum(X ** 2, axis=1)[:, None]
        distances = test_sq + train_sq[None, :] - 2.0 * (X @ self.X_train.T)
        nearest = np.argpartition(distances, kth=k - 1, axis=1)[:, :k]
        neighbor_labels = self.y_train[nearest].astype(int)

        predictions = np.empty(X.shape[0], dtype=self.y_train.dtype)
        for i, labels in enumerate(neighbor_labels):
            counts = np.bincount(labels)
            predictions[i] = counts.argmax()
        return predictions
