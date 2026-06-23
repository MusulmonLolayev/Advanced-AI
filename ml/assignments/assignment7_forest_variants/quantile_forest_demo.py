"""Run a Quantile Regression Forest on the 1D regression dataset."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import QUANTILE_DATA_PATH, RANDOM_SEED, RESULTS_DIR, TAU_HIGH, TAU_LOW, TAU_MEDIAN
from advanced_ai.data_utils import load_quantile_bundle
from advanced_ai.forest.quantile_forest import QuantileRegressionForest
from advanced_ai.metrics import coverage_fraction, mean_interval_width
from advanced_ai.task_utils import print_section, require_file


def main() -> None:
    bundle = load_quantile_bundle(require_file(QUANTILE_DATA_PATH))
    X_train = bundle["X_train"].astype(np.float64)
    y_train = bundle["y_train"].astype(np.float64)
    X_test = bundle["X_test"].astype(np.float64)
    y_test = bundle["y_test"].astype(np.float64)

    print_section("Quantile Regression Forest")
    model = QuantileRegressionForest(n_estimators=100, min_samples_leaf=5, random_state=RANDOM_SEED)
    model.fit(X_train, y_train)

    sample_idx = [0, X_test.shape[0] // 2, X_test.shape[0] - 1]
    for idx in sample_idx:
        x = X_test[idx : idx + 1]
        median = model.predict_quantile(x, TAU_MEDIAN)[0]
        low = model.predict_quantile(x, TAU_LOW)[0]
        high = model.predict_quantile(x, TAU_HIGH)[0]
        print(
            f"x={X_test[idx, 0]:.4f} median={median:.4f} "
            f"80% interval=[{low:.4f}, {high:.4f}] true_y={y_test[idx]:.4f}"
        )

    median_all = model.predict_quantile(X_test, TAU_MEDIAN)
    low_all = model.predict_quantile(X_test, TAU_LOW)
    high_all = model.predict_quantile(X_test, TAU_HIGH)
    coverage = coverage_fraction(y_test, low_all, high_all)
    width = mean_interval_width(low_all, high_all)
    print(f"empirical 80% coverage on held-out test points = {coverage:.4f}")
    print(f"mean interval width = {width:.4f}")

    order = np.argsort(X_test[:, 0])
    x_sorted = X_test[order, 0]
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.scatter(X_train[:, 0], y_train, s=10, alpha=0.3, color="gray", label="train")
    ax.scatter(x_sorted, y_test[order], s=18, alpha=0.6, label="test")
    ax.plot(x_sorted, median_all[order], color="C1", label=r"$\hat{Q}_{0.5}(x)$")
    ax.fill_between(x_sorted, low_all[order], high_all[order], color="C1", alpha=0.2, label="80% interval")
    ax.set_title("Quantile regression forest: median and 80% interval")
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$y$")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / "quantile_forest_band.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
