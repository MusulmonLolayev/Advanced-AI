"""Random forest starter implementation for Assignment 6."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from advanced_ai.trees.decision_tree import DecisionTreeClassifier


@dataclass
class RandomForestClassifier:
    n_estimators: int = 50
    max_depth: int | None = None
    min_samples_leaf: int = 1
    max_features: int | None = None
    random_state: int | None = None

    def __post_init__(self) -> None:
        if self.n_estimators < 1:
            raise ValueError("n_estimators must be at least 1.")
        if self.min_samples_leaf < 1:
            raise ValueError("min_samples_leaf must be at least 1.")
        self._rng = np.random.default_rng(self.random_state)
        self.trees_: list[DecisionTreeClassifier] = []
        self.feature_subsets_: list[np.ndarray] = []
        self.oob_masks_: list[np.ndarray] = []
        self.classes_: np.ndarray | None = None

    def _bootstrap_sample(self, n: int) -> np.ndarray:
        # TODO T1: draw n indices from {0, ..., n-1} uniformly with replacement
        # using self._rng, and return them as an array of shape (n,).
        raise NotImplementedError("TODO T1: implement the bootstrap sampler.")

    def _feature_subset(self, d: int) -> np.ndarray:
        # TODO T2: select m = floor(sqrt(d)) feature indices uniformly at
        # random without replacement from {0, ..., d-1} (use self.max_features
        # instead of floor(sqrt(d)) when it is set). Return the selected indices.
        raise NotImplementedError("TODO T2: implement the feature subsampler.")

    def _new_tree(self) -> DecisionTreeClassifier:
        return DecisionTreeClassifier(max_depth=self.max_depth, min_samples_leaf=self.min_samples_leaf)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestClassifier":
        # TODO T3: for each of self.n_estimators rounds, draw a bootstrap
        # sample with _bootstrap_sample, draw a feature subset with
        # _feature_subset, train a new tree (via _new_tree) on the
        # bootstrapped rows restricted to the sampled feature columns, and
        # store the fitted tree, the feature subset, and the OOB mask (the
        # rows not drawn by the bootstrap sample) in self.trees_,
        # self.feature_subsets_, and self.oob_masks_ respectively. Also set
        # self.classes_ from the unique labels in y.
        raise NotImplementedError("TODO T3: implement the bagging training loop.")

    def predict(self, X: np.ndarray) -> np.ndarray:
        # TODO T4: for every fitted tree, predict on X restricted to that
        # tree's feature subset, tally the votes per class across all trees,
        # and return the majority class for each row of X.
        raise NotImplementedError("TODO T4: implement majority-vote prediction.")

    def oob_error(self, X: np.ndarray, y: np.ndarray) -> float:
        # TODO T5: for each training example, aggregate votes only from the
        # trees for which that example was out-of-bag (see self.oob_masks_),
        # take the majority vote among those trees, and return the fraction
        # of examples (that had at least one OOB tree) whose OOB prediction
        # disagrees with the true label.
        raise NotImplementedError("TODO T5: implement out-of-bag error.")

    def feature_importances(self, n_features: int) -> np.ndarray:
        # TODO T6: walk every internal node of every fitted tree, and for the
        # feature used at that node accumulate (n_m / n) * delta_I, where n_m
        # is the node's sample count, n is the tree's root sample count, and
        # delta_I is the impurity decrease at that node (use the node's stored
        # impurity together with its children's impurity and sample counts).
        # Remember to map each tree's local feature index back to the
        # original feature index using that tree's feature subset. Average
        # the accumulated values over the number of trees and normalize the
        # result so it sums to 1.
        raise NotImplementedError("TODO T6: implement feature importances.")
