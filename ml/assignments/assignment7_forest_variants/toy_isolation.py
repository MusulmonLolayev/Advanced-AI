"""Run an Isolation Forest on the toy dataset with injected outliers."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import ISOLATION_DATA_PATH, RANDOM_SEED, RESULTS_DIR
from advanced_ai.data_utils import load_isolation_bundle
from advanced_ai.forest.isolation_forest import IsolationForest
from advanced_ai.task_utils import print_section, require_file

ANOMALY_THRESHOLD = 0.6


def main() -> None:
    bundle = load_isolation_bundle(require_file(ISOLATION_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y_outlier = bundle["y_outlier"].astype(np.int64)

    print_section("Toy Isolation Forest")
    forest = IsolationForest(n_estimators=100, subsample_size=64, random_state=RANDOM_SEED)
    forest.fit(X)

    outlier_idx = int(np.flatnonzero(y_outlier == 1)[0])
    normal_idx = int(np.flatnonzero(y_outlier == 0)[0])

    outlier_path = float(np.mean([tree.path_length(X[outlier_idx]) for tree in forest.trees_]))
    normal_path = float(np.mean([tree.path_length(X[normal_idx]) for tree in forest.trees_]))
    outlier_score = forest.anomaly_score(X[outlier_idx])
    normal_score = forest.anomaly_score(X[normal_idx])

    print(f"injected outlier: avg path length = {outlier_path:.4f}, anomaly score = {outlier_score:.4f}")
    print(f"normal point:     avg path length = {normal_path:.4f}, anomaly score = {normal_score:.4f}")

    scores = forest.score_samples(X)
    avg_paths = np.asarray(
        [float(np.mean([tree.path_length(row) for tree in forest.trees_])) for row in X]
    )
    flagged = scores > ANOMALY_THRESHOLD
    print(f"anomaly threshold = {ANOMALY_THRESHOLD}")
    print(f"flagged points = {int(np.sum(flagged))} / {X.shape[0]}")

    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    normalized_path = avg_paths / forest.height_limit_
    ax.scatter(normalized_path[y_outlier == 0], scores[y_outlier == 0], s=24, label="normal", alpha=0.7)
    ax.scatter(normalized_path[y_outlier == 1], scores[y_outlier == 1], s=36, marker="x", label="injected outlier")
    ax.axhline(ANOMALY_THRESHOLD, color="gray", linestyle="--", linewidth=1.0, label="threshold")
    ax.set_title("Anomaly score versus normalized path length")
    ax.set_xlabel("average path length / height limit")
    ax.set_ylabel(r"$s(x,\psi)$")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / "isolation_anomaly_scores.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
