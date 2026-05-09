"""Run a decision tree on the prepared toy dataset."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import RESULTS_DIR, TOY_DATA_PATH
from advanced_ai.data_utils import load_toy_bundle
from advanced_ai.metrics import accuracy, class_counts
from advanced_ai.task_utils import print_section, require_file
from advanced_ai.trees.decision_tree import DecisionTreeClassifier


def _plot_boundary(model: DecisionTreeClassifier, X: np.ndarray, y: np.ndarray, filename: str) -> None:
    x_min, x_max = X[:, 0].min() - 0.4, X[:, 0].max() + 0.4
    y_min, y_max = X[:, 1].min() - 0.4, X[:, 1].max() + 0.4
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 240), np.linspace(y_min, y_max, 180))
    grid = np.column_stack([xx.ravel(), yy.ravel()])
    zz = model.predict(grid).reshape(xx.shape)

    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.contourf(xx, yy, zz, levels=np.arange(-0.5, 2.5, 1), alpha=0.18, cmap="tab10")
    scatter = ax.scatter(X[:, 0], X[:, 1], c=y, cmap="tab10", s=45, edgecolor="white", linewidth=0.8)
    ax.set_title("Toy decision tree regions")
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$x_2$")
    ax.grid(True, alpha=0.3)
    fig.colorbar(scatter, ax=ax, shrink=0.82)
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / filename)
    plt.close(fig)


def main() -> None:
    bundle = load_toy_bundle(require_file(TOY_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y = bundle["y"].astype(np.int64)

    print_section("Toy Decision Tree")
    model = DecisionTreeClassifier(max_depth=2, min_samples_leaf=1)
    model.fit(X, y)
    pred = model.predict(X)
    print(f"class counts = {class_counts(y)}")
    print(f"training accuracy = {accuracy(y, pred):.4f}")
    print(f"tree depth = {model.depth()}")
    print(f"number of leaves = {model.n_leaves()}")
    if model.root_ is not None and model.root_.feature_index is not None and model.root_.threshold is not None:
        print(f"first split = x[{model.root_.feature_index}] <= {model.root_.threshold:.6g}")
    print("example path:")
    for step in model.explain_one_path(X[0]):
        print(f"  {step}")
    _plot_boundary(model, X, y, "toy_tree_regions.pdf")


if __name__ == "__main__":
    main()
