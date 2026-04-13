"""PCA starter scaffold used by the assignment task runners.

Students should fill in the TODO blocks in this file while keeping the
NumPy-only constraints in mind.
"""

from __future__ import annotations

import numpy as np


class PrincipalComponentAnalysis:
    """PCA model supporting covariance and SVD-based fitting."""

    EPS = 1e-12

    def __init__(self) -> None:
        self.mean_: np.ndarray | None = None
        self.components_: np.ndarray | None = None
        self.singular_values_: np.ndarray | None = None
        self.eigenvalues_: np.ndarray | None = None
        self.explained_variance_ratio_: np.ndarray | None = None

    def fit(self, X: np.ndarray, method: str = "covariance") -> "PrincipalComponentAnalysis":
        """TODO P1: fit PCA using either covariance eigendecomposition or SVD."""
        # TODO: dispatch to fit_covariance or fit_svd based on the requested method.
        raise NotImplementedError("TODO P1: implement fit.")

    def fit_covariance(self, X: np.ndarray) -> "PrincipalComponentAnalysis":
        """TODO P1: fit PCA from the covariance matrix."""
        # TODO: center X, compute the covariance matrix, and eigendecompose it.
        raise NotImplementedError("TODO P1: implement fit_covariance.")

    def fit_svd(self, X: np.ndarray) -> "PrincipalComponentAnalysis":
        """TODO P1: fit PCA directly from the centered data matrix via SVD."""
        # TODO: center X, compute its SVD, and map singular values to variances.
        raise NotImplementedError("TODO P1: implement fit_svd.")

    def transform(self, X: np.ndarray, n_components: int | None = None) -> np.ndarray:
        """TODO P1: project centered examples into the PCA subspace."""
        # TODO: subtract the mean and multiply by the top principal directions.
        raise NotImplementedError("TODO P1: implement transform.")

    def inverse_transform(self, Z: np.ndarray, n_components: int | None = None) -> np.ndarray:
        """TODO P1: reconstruct examples from PCA coordinates."""
        # TODO: map low-dimensional coordinates back to the original feature space.
        raise NotImplementedError("TODO P1: implement inverse_transform.")

    def reconstruction_error(self, X: np.ndarray, n_components: int) -> np.ndarray:
        """TODO P3: compute per-example reconstruction error."""
        # TODO: reconstruct X and return squared L2 error for each example.
        raise NotImplementedError("TODO P3: implement reconstruction_error.")

    def explained_variance_ratio(self) -> np.ndarray:
        """TODO P1: return the explained variance ratio for all components."""
        # TODO: compute lambda_j / sum(lambda) using the stored eigenvalues.
        raise NotImplementedError("TODO P1: implement explained_variance_ratio.")

    def cumulative_explained_variance(self, n_components: int) -> float:
        """TODO P1: compute cumulative explained variance up to n_components."""
        # TODO: sum the leading explained variance ratios.
        raise NotImplementedError("TODO P1: implement cumulative_explained_variance.")

    def fit_transform(self, X: np.ndarray, n_components: int | None = None, method: str = "covariance") -> np.ndarray:
        """Fit PCA and return projected coordinates."""
        self.fit(X, method=method)
        return self.transform(X, n_components=n_components)

    def _check_is_fitted(self) -> None:
        if self.mean_ is None or self.components_ is None:
            raise ValueError("Call fit before using the PCA model.")

    def _center(self, X: np.ndarray) -> np.ndarray:
        self._check_is_fitted()
        return np.asarray(X, dtype=np.float64) - self.mean_

    def _top_components(self, n_components: int | None = None) -> np.ndarray:
        self._check_is_fitted()
        if n_components is None:
            return self.components_
        return self.components_[:n_components]
