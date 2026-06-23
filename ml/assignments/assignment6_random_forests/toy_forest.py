"""Compare a single decision tree with a random forest on the toy dataset."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import RANDOM_SEED, RESULTS_DIR, TOY_DATA_PATH
from advanced_ai.data_utils import load_toy_bundle
from advanced_ai.forest.random_forest import RandomForestClassifier
from advanced_ai.metrics import accuracy, class_counts
from advanced_ai.task_utils import print_section, require_file
from advanced_ai.trees.decision_tree import DecisionTreeClassifier

FOREST_B = 50


def _plot_side_by_side(
    tree: DecisionTreeClassifier,
    forest: RandomForestClassifier,
    X: np.ndarray,
    y: np.ndarray,
    filename: str,
) -> None:
    x_min, x_max = X[:, 0].min() - 0.4, X[:, 0].max() + 0.4
    y_min, y_max = X[:, 1].min() - 0.4, X[:, 1].max() + 0.4
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 240), np.linspace(y_min, y_max, 180))
    grid = np.column_stack([xx.ravel(), yy.ravel()])

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6), sharex=True, sharey=True)

    zz_tree = tree.predict(grid).reshape(xx.shape)
    axes[0].contourf(xx, yy, zz_tree, levels=np.arange(-0.5, 2.5, 1), alpha=0.18, cmap="tab10")
    axes[0].scatter(X[:, 0], X[:, 1], c=y, cmap="tab10", s=35, edgecolor="white", linewidth=0.6)
    axes[0].set_title("Single decision tree")
    axes[0].set_xlabel(r"$x_1$")
    axes[0].set_ylabel(r"$x_2$")
    axes[0].grid(True, alpha=0.3)

    zz_forest = forest.predict(grid).reshape(xx.shape)
    axes[1].contourf(xx, yy, zz_forest, levels=np.arange(-0.5, 2.5, 1), alpha=0.18, cmap="tab10")
    axes[1].scatter(X[:, 0], X[:, 1], c=y, cmap="tab10", s=35, edgecolor="white", linewidth=0.6)
    axes[1].set_title(f"Random forest (B={FOREST_B})")
    axes[1].set_xlabel(r"$x_1$")
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / filename)
    plt.close(fig)


def main() -> None:
    bundle = load_toy_bundle(require_file(TOY_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y = bundle["y"].astype(np.int64)

    print_section("Toy: single tree versus random forest")
    print(f"class counts = {class_counts(y)}")

    tree = DecisionTreeClassifier(max_depth=None, min_samples_leaf=1)
    tree.fit(X, y)
    tree_pred = tree.predict(X)
    print(f"single tree depth = {tree.depth()}")
    print(f"single tree leaves = {tree.n_leaves()}")
    print(f"single tree training accuracy = {accuracy(y, tree_pred):.4f}")

    forest = RandomForestClassifier(
        n_estimators=FOREST_B, max_depth=None, min_samples_leaf=1, random_state=RANDOM_SEED
    )
    forest.fit(X, y)
    forest_pred = forest.predict(X)
    print(f"forest (B={FOREST_B}) training accuracy = {accuracy(y, forest_pred):.4f}")

    _plot_side_by_side(tree, forest, X, y, "toy_forest_regions.pdf")


if __name__ == "__main__":
    main()
