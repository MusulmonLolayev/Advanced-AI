"""Extra-Trees (extremely randomized trees) starter implementation for Assignment 7."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from advanced_ai.forest.random_forest import RandomForestClassifier
from advanced_ai.trees.decision_tree import DecisionTreeClassifier


@dataclass
class ExtraTreeClassifier(DecisionTreeClassifier):
    random_state: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self._rng = np.random.default_rng(self.random_state)

    def _random_threshold_split(self, X: np.ndarray, y: np.ndarray) -> tuple[int | None, float | None, float]:
        # TODO T4: for each feature, draw ONE threshold uniformly at random
        # between that feature's min and max at this node (use
        # self._rng.uniform), instead of searching every candidate
        # threshold. Score each random threshold with self._split_gain
        # (reused unchanged from the decision tree). Keep the feature
        # whose random threshold gives the largest gain. Skip features
        # that are constant at this node (min == max).
        raise NotImplementedError("TODO T4: implement the random-threshold split rule.")

    def _best_split(self, X: np.ndarray, y: np.ndarray) -> tuple[int | None, float | None, float]:
        return self._random_threshold_split(X, y)


class ExtraTreesClassifier(RandomForestClassifier):
    """Bagging ensemble of ExtraTreeClassifier.

    Reuses RandomForestClassifier's bootstrap sampler, feature subsampler,
    bagging loop, prediction, and OOB error unchanged. Only the per-tree
    estimator changes, via _new_tree.
    """

    def _new_tree(self) -> ExtraTreeClassifier:
        seed = int(self._rng.integers(0, 2**31 - 1))
        return ExtraTreeClassifier(
            max_depth=self.max_depth,
            min_samples_leaf=self.min_samples_leaf,
            random_state=seed,
        )
