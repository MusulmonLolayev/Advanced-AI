"""k-NN starter scaffold used by the assignment task runners.

Students should fill in the TODO blocks in this file while keeping the
NumPy-only constraints in mind.
"""

from __future__ import annotations

import numpy as np


class KNearestNeighbor:
    """A k-NN model that supports classification, regression, and scoring."""

    EPS = 1e-12

    def __init__(self) -> None:
        self.X_train: np.ndarray | None = None
        self.y_train: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray | None = None) -> None:
        """Store training features and optional labels."""
        self.X_train = np.asarray(X, dtype=np.float64)
        self.y_train = None if y is None else np.asarray(y)

    def compute_distances_two_loops(self, X: np.ndarray, metric: str = "l2") -> np.ndarray:
        """TODO I1: compute pairwise distances using a very explicit double loop."""
        # TODO: Fill in the reference distance computation here.
        # Hint: this version is intentionally the clearest, not the fastest.
        raise NotImplementedError("TODO I1: implement compute_distances_two_loops.")

    def compute_distances_one_loop(self, X: np.ndarray, metric: str = "l2") -> np.ndarray:
        """TODO I1: compute pairwise distances using a single loop over test points."""
        # TODO: Reuse vectorized row-wise operations for each test sample.
        raise NotImplementedError("TODO I1: implement compute_distances_one_loop.")

    def compute_distances_no_loops(self, X: np.ndarray, metric: str = "l2") -> np.ndarray:
        """TODO I1: compute pairwise distances using fully vectorized NumPy."""
        # TODO: Use broadcasting / matrix multiplication here instead of loops.
        raise NotImplementedError("TODO I1: implement compute_distances_no_loops.")

    def kneighbors(
        self,
        X: np.ndarray,
        k: int = 1,
        metric: str = "l2",
        num_loops: int = 0,
    ) -> tuple[np.ndarray, np.ndarray]:
        """TODO I1: return distances and indices of the nearest neighbors."""
        # TODO: Call one of the distance routines, sort the distances, and keep top-k.
        raise NotImplementedError("TODO I1: implement kneighbors.")

    def predict(
        self,
        X: np.ndarray,
        k: int = 1,
        metric: str = "l2",
        task: str = "classification",
        weighting: str = "uniform",
        num_loops: int = 0,
    ) -> np.ndarray:
        """TODO I2/I3: dispatch to classification or regression prediction."""
        # TODO: Use kneighbors() and then route to classification or regression.
        raise NotImplementedError("TODO I2/I3: implement predict.")

    def predict_labels(
        self,
        neighbor_dists: np.ndarray,
        neighbor_idx: np.ndarray,
        weighting: str = "uniform",
    ) -> np.ndarray:
        """TODO I2: predict class labels from nearest neighbors."""
        # TODO: Implement uniform and distance-weighted voting.
        raise NotImplementedError("TODO I2: implement predict_labels.")

    def predict_values(
        self,
        neighbor_dists: np.ndarray,
        neighbor_idx: np.ndarray,
        weighting: str = "uniform",
    ) -> np.ndarray:
        """TODO I3: predict continuous targets from nearest neighbors."""
        # TODO: Implement uniform averaging and distance-weighted averaging.
        raise NotImplementedError("TODO I3: implement predict_values.")

    def anomaly_scores(
        self,
        X: np.ndarray,
        k: int = 5,
        metric: str = "l2",
        num_loops: int = 0,
    ) -> np.ndarray:
        """TODO I4B: use distance to the k-th nearest neighbor as anomaly score."""
        # TODO: The k-th distance is the anomaly score.
        raise NotImplementedError("TODO I4B: implement anomaly_scores.")

    def _compute_distances(self, X: np.ndarray, metric: str, num_loops: int) -> np.ndarray:
        # TODO: dispatch to the requested distance implementation.
        raise NotImplementedError("TODO I1: implement _compute_distances.")

    def _check_is_fitted(self) -> None:
        if self.X_train is None:
            raise ValueError("Call fit before using the model.")

    def _check_has_labels(self) -> None:
        self._check_is_fitted()
        if self.y_train is None:
            raise ValueError("This operation requires training labels.")

    @staticmethod
    def _normalize_metric(metric: str) -> str:
        metric = metric.lower()
        if metric not in {"l1", "l2", "cosine"}:
            raise ValueError(f"Unsupported metric: {metric}")
        return metric

    @staticmethod
    def _normalize_weighting(weighting: str) -> str:
        weighting = weighting.lower()
        if weighting not in {"uniform", "distance"}:
            raise ValueError(f"Unsupported weighting: {weighting}")
        return weighting
