"""Self-checks for Assignment 5."""

from __future__ import annotations

import numpy as np

from advanced_ai.trees.decision_tree import DecisionTreeClassifier


def check_gini() -> None:
    model = DecisionTreeClassifier(max_depth=1)
    model.classes_ = np.array([0, 1])
    assert abs(model._gini(np.array([0, 0, 0])) - 0.0) < 1e-12
    assert abs(model._gini(np.array([0, 0, 1, 1])) - 0.5) < 1e-12


def check_best_split() -> None:
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0, 0, 1, 1])
    model = DecisionTreeClassifier(max_depth=1, min_samples_leaf=1)
    model.classes_ = np.array([0, 1])
    feature, threshold, gain = model._best_split(X, y)
    assert feature == 0
    assert abs(float(threshold) - 1.5) < 1e-12
    assert gain > 0.0


def check_fit_predict() -> None:
    X = np.array(
        [
            [0.0, 0.0],
            [0.2, 0.1],
            [1.0, 1.0],
            [1.2, 1.1],
            [3.0, 0.0],
            [3.2, 0.2],
        ]
    )
    y = np.array([0, 0, 1, 1, 2, 2])
    model = DecisionTreeClassifier(max_depth=2, min_samples_leaf=1)
    pred = model.fit(X, y).predict(X)
    assert pred.shape == y.shape
    assert np.mean(pred == y) >= 0.8
    assert model.n_leaves() >= 2


def run_all_checks() -> None:
    check_gini()
    check_best_split()
    check_fit_predict()
    print("All decision tree self-checks passed.")


if __name__ == "__main__":
    run_all_checks()
