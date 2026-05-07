"""DBSCAN starter implementation for Assignment 4."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class DBSCANClustering:
    eps: float = 0.5
    min_pts: int = 5

    def __post_init__(self) -> None:
        if self.eps <= 0:
            raise ValueError("eps must be positive.")
        if self.min_pts <= 0:
            raise ValueError("min_pts must be positive.")
        self.labels_: np.ndarray | None = None
        self.core_sample_indices_: np.ndarray | None = None

    def _epsilon_neighborhood(self, X: np.ndarray, index: int) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        point = X[index]
        distances = np.linalg.norm(X - point, axis=1)
        return np.flatnonzero(distances <= self.eps)

    def _region_query(self, X: np.ndarray, index: int) -> np.ndarray:
        return self._epsilon_neighborhood(X, index)

    def _expand_cluster(
        self,
        X: np.ndarray,
        labels: np.ndarray,
        visited: np.ndarray,
        cluster_id: int,
        point_index: int,
        neighbors: np.ndarray,
    ) -> None:
        raise NotImplementedError("TODO D1: implement cluster expansion.")

    def fit(self, X: np.ndarray) -> "DBSCANClustering":
        X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2:
            raise ValueError("X must be a 2D array.")

        raise NotImplementedError("TODO D2: implement fit.")

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        if self.labels_ is None:
            raise RuntimeError("fit did not set labels_.")
        return self.labels_.copy()
