"""Self-checks for Assignment 6: Random Forests."""

from __future__ import annotations

import numpy as np

from advanced_ai.forest.random_forest import RandomForestClassifier


def check_bootstrap_sample() -> None:
    forest = RandomForestClassifier(random_state=0)
    idx = forest._bootstrap_sample(10)
    assert idx.shape == (10,)
    assert idx.min() >= 0 and idx.max() < 10


def check_feature_subset() -> None:
    forest = RandomForestClassifier(random_state=0)
    idx = forest._feature_subset(9)
    assert idx.shape[0] == 3
    assert np.unique(idx).size == idx.size
    assert idx.min() >= 0 and idx.max() < 9


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
    forest = RandomForestClassifier(n_estimators=20, max_depth=3, min_samples_leaf=1, max_features=2, random_state=0)
    forest.fit(X, y)
    pred = forest.predict(X)
    assert pred.shape == y.shape
    assert np.mean(pred == y) >= 0.8
    assert len(forest.trees_) == 20


def check_oob_error_bounds() -> None:
    rng = np.random.default_rng(0)
    X = rng.normal(size=(60, 4))
    y = (X[:, 0] + X[:, 1] > 0).astype(np.int64)
    forest = RandomForestClassifier(n_estimators=30, max_depth=4, min_samples_leaf=1, random_state=1)
    forest.fit(X, y)
    err = forest.oob_error(X, y)
    assert 0.0 <= err <= 1.0


def check_feature_importances_sum_to_one() -> None:
    rng = np.random.default_rng(2)
    X = rng.normal(size=(80, 5))
    y = (X[:, 2] > 0).astype(np.int64)
    forest = RandomForestClassifier(n_estimators=25, max_depth=3, min_samples_leaf=2, max_features=5, random_state=3)
    forest.fit(X, y)
    importances = forest.feature_importances(5)
    assert importances.shape == (5,)
    assert importances.min() >= 0.0
    assert abs(importances.sum() - 1.0) < 1e-9
    assert int(np.argmax(importances)) == 2


def run_all_checks() -> None:
    check_bootstrap_sample()
    check_feature_subset()
    check_fit_predict()
    check_oob_error_bounds()
    check_feature_importances_sum_to_one()
    print("All random forest self-checks passed.")


if __name__ == "__main__":
    run_all_checks()
