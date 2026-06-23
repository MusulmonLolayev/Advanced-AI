"""Self-checks for Assignment 7."""

from __future__ import annotations

import numpy as np

from advanced_ai.forest.extra_trees import ExtraTreeClassifier
from advanced_ai.forest.isolation_forest import IsolationForest, IsolationTree
from advanced_ai.forest.quantile_forest import QuantileRegressionForest


def check_isolation_tree_single_point() -> None:
    X = np.array([[1.0, 2.0]])
    tree = IsolationTree(height_limit=8, random_state=0)
    tree.fit(X)
    assert tree.root_ is not None
    assert tree.root_.is_leaf
    assert tree.path_length(np.array([1.0, 2.0])) == 0


def check_isolation_tree_grows() -> None:
    rng = np.random.default_rng(0)
    X = rng.normal(size=(50, 3))
    height_limit = int(np.ceil(np.log2(50)))
    tree = IsolationTree(height_limit=height_limit, random_state=1)
    tree.fit(X)
    assert tree.root_ is not None
    assert not tree.root_.is_leaf


def check_path_length_bounds() -> None:
    rng = np.random.default_rng(1)
    X = rng.normal(size=(64, 2))
    height_limit = int(np.ceil(np.log2(64)))
    tree = IsolationTree(height_limit=height_limit, random_state=2)
    tree.fit(X)
    for row in X[:5]:
        h = tree.path_length(row)
        assert isinstance(h, int) or float(h).is_integer()
        assert 0 <= h <= height_limit


def check_avg_path_length() -> None:
    forest = IsolationForest(n_estimators=1, subsample_size=16, random_state=0)
    expected = 2.0 * (np.log(15) + 0.5772) - 2.0 * 15 / 16
    assert abs(forest._avg_path_length(16) - expected) < 1e-9
    assert forest._avg_path_length(1) == 0.0


def check_anomaly_score_separates_outlier() -> None:
    rng = np.random.default_rng(0)
    inliers = rng.normal(loc=0.0, scale=0.5, size=(200, 2))
    outlier = np.array([20.0, 20.0])
    X = np.vstack([inliers, outlier[None, :]])
    forest = IsolationForest(n_estimators=80, subsample_size=64, random_state=0).fit(X)
    inlier_score = forest.anomaly_score(inliers[0])
    outlier_score = forest.anomaly_score(outlier)
    assert outlier_score > inlier_score
    assert outlier_score > 0.5
    assert inlier_score < 0.6


def check_random_threshold_split() -> None:
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0, 0, 1, 1])
    model = ExtraTreeClassifier(max_depth=1, min_samples_leaf=1, random_state=0)
    model.classes_ = np.array([0, 1])
    feature, threshold, gain = model._random_threshold_split(X, y)
    assert feature == 0
    assert 0.0 < threshold < 3.0
    assert gain > 0.0


def check_extra_tree_fit_predict() -> None:
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
    model = ExtraTreeClassifier(max_depth=3, min_samples_leaf=1, random_state=0)
    pred = model.fit(X, y).predict(X)
    assert pred.shape == y.shape
    assert np.mean(pred == y) >= 0.8


class _StubLeaf:
    def __init__(self, y_values: list[float]) -> None:
        self.y_values = np.asarray(y_values, dtype=np.float64)


class _StubTree:
    def __init__(self, y_values: list[float]) -> None:
        self._leaf = _StubLeaf(y_values)

    def apply_leaf(self, x: np.ndarray) -> _StubLeaf:
        return self._leaf


def _make_stub_qrf() -> QuantileRegressionForest:
    model = QuantileRegressionForest(n_estimators=2)
    model.trees_ = [
        _StubTree([10.0, 12.0, 14.0, 16.0, 18.0]),
        _StubTree([11.0, 13.0, 15.0, 17.0, 19.0]),
    ]
    model.feature_subsets_ = [np.array([0]), np.array([0])]
    return model


def check_collect_leaf_values() -> None:
    model = _make_stub_qrf()
    leaves = model._collect_leaf_values(np.array([0.0]))
    assert len(leaves) == 2
    assert np.allclose(sorted(leaves[0]), [10.0, 12.0, 14.0, 16.0, 18.0])
    assert np.allclose(sorted(leaves[1]), [11.0, 13.0, 15.0, 17.0, 19.0])


def check_predict_quantile() -> None:
    model = _make_stub_qrf()
    X = np.array([[0.0]])
    median = model.predict_quantile(X, tau=0.5)[0]
    low = model.predict_quantile(X, tau=0.1)[0]
    high = model.predict_quantile(X, tau=0.9)[0]
    assert abs(median - 14.0) < 1e-9
    assert abs(low - 10.0) < 1e-9
    assert abs(high - 18.0) < 1e-9


def run_all_checks() -> None:
    check_isolation_tree_single_point()
    check_isolation_tree_grows()
    check_path_length_bounds()
    check_avg_path_length()
    check_anomaly_score_separates_outlier()
    check_random_threshold_split()
    check_extra_tree_fit_predict()
    check_collect_leaf_values()
    check_predict_quantile()
    print("All forest variants self-checks passed.")


if __name__ == "__main__":
    run_all_checks()
