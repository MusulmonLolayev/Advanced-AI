"""Quantile Regression Forest starter implementation for Assignment 7."""

from __future__ import annotations

import numpy as np

from advanced_ai.forest.regression_forest import RandomForestRegressor


class QuantileRegressionForest(RandomForestRegressor):
    """Regression forest that also reports leaf-distribution quantiles.

    Reuses RandomForestRegressor's bootstrap sampler, feature subsampler,
    bagging loop, and point prediction unchanged. The new work is reading
    each tree's leaf distribution for a query point and turning the B
    pooled leaf distributions into a weighted quantile prediction.
    """

    def _collect_leaf_values(self, x: np.ndarray) -> list[np.ndarray]:
        # TODO T5: for every tree in self.trees_, route x (restricted to
        # that tree's feature subset in self.feature_subsets_) down to its
        # leaf with tree.apply_leaf(...), and collect that leaf's stored
        # y_values array. Return the list of B arrays (one per tree).
        raise NotImplementedError("TODO T5: implement leaf distribution collection.")

    def predict_quantile(self, X: np.ndarray, tau: float) -> np.ndarray:
        # TODO T6: for each row x of X:
        #   1. Get the B leaf-value arrays from self._collect_leaf_values(x).
        #   2. Build the implied weights: every value in leaf b carries
        #      weight 1 / (B * |leaf_b|), matching
        #      w_i(x) = (1/B) sum_b 1{x_i in L_b(x)} / |L_b(x)|.
        #   3. Pool all (value, weight) pairs across the B leaves, sort by
        #      value, and form the weighted empirical CDF
        #      F_hat(y | x) = sum_i w_i(x) * 1{y_i <= y} via a cumulative
        #      sum of the sorted weights.
        #   4. Return Q_hat_tau(x) = inf{y : F_hat(y | x) >= tau}, i.e. the
        #      smallest pooled value whose cumulative weight reaches tau.
        #      Compare against (tau - 1e-9) rather than tau, since summing
        #      many floating-point weights can land just below the exact
        #      target even when the true cumulative weight equals tau.
        # Return one prediction per row of X as a 1D array.
        raise NotImplementedError("TODO T6: implement the weighted quantile prediction.")

    def predict_interval(self, X: np.ndarray, tau_low: float, tau_high: float) -> tuple[np.ndarray, np.ndarray]:
        return self.predict_quantile(X, tau_low), self.predict_quantile(X, tau_high)
