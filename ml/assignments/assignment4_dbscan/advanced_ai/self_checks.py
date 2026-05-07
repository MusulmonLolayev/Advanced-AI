"""Self-checks for Assignment 4."""

from __future__ import annotations

import numpy as np

from advanced_ai.clustering.dbscan import DBSCANClustering


def check_region_query() -> None:
    X = np.array([[0.0, 0.0], [0.1, 0.0], [0.8, 0.0], [2.0, 2.0]])
    model = DBSCANClustering(eps=0.25, min_pts=2)
    neighbors = model._epsilon_neighborhood(X, 0)
    assert neighbors.tolist() == [0, 1], neighbors


def check_fit_basic() -> None:
    X = np.array(
        [
            [0.0, 0.0],
            [0.1, 0.0],
            [0.0, 0.1],
            [2.0, 2.0],
            [2.1, 2.0],
            [2.0, 2.1],
            [5.0, 5.0],
        ]
    )
    model = DBSCANClustering(eps=0.25, min_pts=3)
    labels = model.fit_predict(X)
    assert labels.shape == (7,)
    assert -1 in labels


def run_all_checks() -> None:
    check_region_query()
    check_fit_basic()
    print("All DBSCAN self-checks passed.")


if __name__ == "__main__":
    run_all_checks()
