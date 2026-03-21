"""k-NN implementation used by assignment task runners."""

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
        """Compute pairwise distances using a very explicit double loop."""
        self._check_is_fitted()
        X = np.asarray(X, dtype=np.float64)
        num_test = X.shape[0]
        num_train = self.X_train.shape[0]
        dists = np.zeros((num_test, num_train), dtype=np.float64)

        metric = self._normalize_metric(metric)
        for i in range(num_test):
            for j in range(num_train):
                dists[i, j] = self._pair_distance(X[i], self.X_train[j], metric)

        return dists

    def compute_distances_one_loop(self, X: np.ndarray, metric: str = "l2") -> np.ndarray:
        """Compute pairwise distances using a single loop over test points."""
        self._check_is_fitted()
        X = np.asarray(X, dtype=np.float64)
        num_test = X.shape[0]
        num_train = self.X_train.shape[0]
        dists = np.zeros((num_test, num_train), dtype=np.float64)

        metric = self._normalize_metric(metric)
        train_norms = None
        if metric == "cosine":
            train_norms = np.linalg.norm(self.X_train, axis=1)

        for i in range(num_test):
            diff = self.X_train - X[i]
            if metric == "l2":
                dists[i] = np.sqrt(np.sum(diff * diff, axis=1))
            elif metric == "l1":
                dists[i] = np.sum(np.abs(diff), axis=1)
            else:
                test_norm = np.linalg.norm(X[i])
                denom = np.maximum(train_norms * test_norm, self.EPS)
                cosine_similarity = (self.X_train @ X[i]) / denom
                cosine_similarity = np.clip(cosine_similarity, -1.0, 1.0)
                dists[i] = 1.0 - cosine_similarity

        return dists

    def compute_distances_no_loops(self, X: np.ndarray, metric: str = "l2") -> np.ndarray:
        """Compute pairwise distances using fully vectorized NumPy."""
        self._check_is_fitted()
        X = np.asarray(X, dtype=np.float64)
        dists = np.zeros((X.shape[0], self.X_train.shape[0]), dtype=np.float64)

        metric = self._normalize_metric(metric)
        if metric == "l2":
            x_sq = np.sum(X * X, axis=1, keepdims=True)
            train_sq = np.sum(self.X_train * self.X_train, axis=1)[None, :]
            sq_dists = np.maximum(x_sq + train_sq - 2.0 * (X @ self.X_train.T), 0.0)
            dists = np.sqrt(sq_dists)
        elif metric == "l1":
            dists = np.sum(np.abs(X[:, None, :] - self.X_train[None, :, :]), axis=2)
        else:
            numerator = X @ self.X_train.T
            x_norms = np.linalg.norm(X, axis=1, keepdims=True)
            train_norms = np.linalg.norm(self.X_train, axis=1, keepdims=True).T
            denom = np.maximum(x_norms * train_norms, self.EPS)
            cosine_similarity = numerator / denom
            cosine_similarity = np.clip(cosine_similarity, -1.0, 1.0)
            dists = 1.0 - cosine_similarity

        return dists

    def kneighbors(
        self,
        X: np.ndarray,
        k: int = 1,
        metric: str = "l2",
        num_loops: int = 0,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return distances and indices of the nearest neighbors."""
        dists = self._compute_distances(X, metric=metric, num_loops=num_loops)
        num_train = dists.shape[1]
        if k < 1:
            raise ValueError(f"k must be >= 1, got {k}")
        if k > num_train:
            raise ValueError(f"k must be <= number of training samples ({num_train}), got {k}")

        neighbor_idx = np.argpartition(dists, kth=k - 1, axis=1)[:, :k]
        neighbor_dists = np.take_along_axis(dists, neighbor_idx, axis=1)
        sort_order = np.argsort(neighbor_dists, axis=1)
        neighbor_idx = np.take_along_axis(neighbor_idx, sort_order, axis=1)
        neighbor_dists = np.take_along_axis(neighbor_dists, sort_order, axis=1)
        return neighbor_dists, neighbor_idx

    def predict(
        self,
        X: np.ndarray,
        k: int = 1,
        metric: str = "l2",
        task: str = "classification",
        weighting: str = "uniform",
        num_loops: int = 0,
    ) -> np.ndarray:
        """Dispatch to classification or regression prediction."""
        neighbor_dists, neighbor_idx = self.kneighbors(X, k=k, metric=metric, num_loops=num_loops)
        if task == "classification":
            return self.predict_labels(neighbor_dists, neighbor_idx, weighting=weighting)
        if task == "regression":
            return self.predict_values(neighbor_dists, neighbor_idx, weighting=weighting)
        raise ValueError(f"Unsupported task: {task}")

    def predict_labels(
        self,
        neighbor_dists: np.ndarray,
        neighbor_idx: np.ndarray,
        weighting: str = "uniform",
    ) -> np.ndarray:
        """Predict class labels from nearest neighbors."""
        self._check_has_labels()
        y_pred = np.zeros(neighbor_idx.shape[0], dtype=self.y_train.dtype)

        weighting = self._normalize_weighting(weighting)
        neighbor_labels = self.y_train[neighbor_idx]
        unique_labels = np.unique(self.y_train)

        if weighting == "uniform":
            weights = np.ones_like(neighbor_dists, dtype=np.float64)
        else:
            weights = 1.0 / (neighbor_dists + self.EPS)

        for i in range(neighbor_idx.shape[0]):
            label_scores = np.zeros(unique_labels.shape[0], dtype=np.float64)
            for label_pos, label in enumerate(unique_labels):
                label_scores[label_pos] = np.sum(weights[i][neighbor_labels[i] == label])
            y_pred[i] = unique_labels[int(np.argmax(label_scores))]

        return y_pred

    def predict_values(
        self,
        neighbor_dists: np.ndarray,
        neighbor_idx: np.ndarray,
        weighting: str = "uniform",
    ) -> np.ndarray:
        """Predict continuous targets from nearest neighbors."""
        self._check_has_labels()
        y_pred = np.zeros(neighbor_idx.shape[0], dtype=np.float64)

        weighting = self._normalize_weighting(weighting)
        neighbor_values = np.asarray(self.y_train[neighbor_idx], dtype=np.float64)

        if weighting == "uniform":
            y_pred = np.mean(neighbor_values, axis=1)
        else:
            weights = 1.0 / (neighbor_dists + self.EPS)
            weighted_sum = np.sum(weights * neighbor_values, axis=1)
            y_pred = weighted_sum / np.sum(weights, axis=1)

        return y_pred

    def anomaly_scores(
        self,
        X: np.ndarray,
        k: int = 5,
        metric: str = "l2",
        num_loops: int = 0,
    ) -> np.ndarray:
        """Use distance to the k-th nearest neighbor as anomaly score."""
        neighbor_dists, _ = self.kneighbors(X, k=k, metric=metric, num_loops=num_loops)
        return neighbor_dists[:, -1]

    def _compute_distances(self, X: np.ndarray, metric: str, num_loops: int) -> np.ndarray:
        if num_loops == 2:
            return self.compute_distances_two_loops(X, metric=metric)
        if num_loops == 1:
            return self.compute_distances_one_loop(X, metric=metric)
        if num_loops == 0:
            return self.compute_distances_no_loops(X, metric=metric)
        raise ValueError(f"Unsupported num_loops: {num_loops}")

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

    @staticmethod
    def _pair_distance(x: np.ndarray, y: np.ndarray, metric: str) -> float:
        if metric == "l2":
            return float(np.sqrt(np.sum((x - y) ** 2)))
        if metric == "l1":
            return float(np.sum(np.abs(x - y)))
        denom = max(float(np.linalg.norm(x) * np.linalg.norm(y)), KNearestNeighbor.EPS)
        cosine_similarity = float(np.dot(x, y) / denom)
        cosine_similarity = float(np.clip(cosine_similarity, -1.0, 1.0))
        return 1.0 - cosine_similarity
