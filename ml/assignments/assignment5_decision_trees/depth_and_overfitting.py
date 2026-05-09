"""Study maximum depth and overfitting for decision trees."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import DEPTH_DATA_PATH, DEPTH_CHOICES, RANDOM_SEED, RESULTS_DIR
from advanced_ai.data_utils import load_depth_bundle, train_val_split
from advanced_ai.metrics import accuracy
from advanced_ai.task_utils import print_section, require_file
from advanced_ai.trees.decision_tree import DecisionTreeClassifier


def _plot_boundary(model: DecisionTreeClassifier, X: np.ndarray, y: np.ndarray, filename: str, title: str) -> None:
    x_min, x_max = X[:, 0].min() - 0.25, X[:, 0].max() + 0.25
    y_min, y_max = X[:, 1].min() - 0.25, X[:, 1].max() + 0.25
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 260), np.linspace(y_min, y_max, 200))
    grid = np.column_stack([xx.ravel(), yy.ravel()])
    zz = model.predict(grid).reshape(xx.shape)

    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.contourf(xx, yy, zz, levels=np.arange(-0.5, 2.5, 1), alpha=0.18, cmap="tab10")
    scatter = ax.scatter(X[:, 0], X[:, 1], c=y, cmap="tab10", s=24, edgecolor="white", linewidth=0.5)
    ax.set_title(title)
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$x_2$")
    ax.grid(True, alpha=0.3)
    fig.colorbar(scatter, ax=ax, shrink=0.82)
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / filename)
    plt.close(fig)


def main() -> None:
    bundle = load_depth_bundle(require_file(DEPTH_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y = bundle["y"].astype(np.int64)
    X_train, X_val, y_train, y_val = train_val_split(X, y, val_fraction=0.30, seed=RANDOM_SEED)

    print_section("Depth and overfitting study")
    rows = []
    for depth in DEPTH_CHOICES:
        model = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=1)
        model.fit(X_train, y_train)
        train_acc = accuracy(y_train, model.predict(X_train))
        val_acc = accuracy(y_val, model.predict(X_val))
        rows.append((depth, train_acc, val_acc, model.n_leaves()))
        print(f"max_depth={depth} train_accuracy={train_acc:.4f} val_accuracy={val_acc:.4f} leaves={model.n_leaves()}")

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot([r[0] for r in rows], [r[1] for r in rows], marker="o", label="train")
    ax.plot([r[0] for r in rows], [r[2] for r in rows], marker="o", label="validation")
    ax.set_title("Depth study")
    ax.set_xlabel("maximum depth")
    ax.set_ylabel("accuracy")
    ax.set_ylim(0.0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / "depth_accuracy.pdf")
    plt.close(fig)

    shallow = DecisionTreeClassifier(max_depth=2, min_samples_leaf=3).fit(X_train, y_train)
    deep = DecisionTreeClassifier(max_depth=6, min_samples_leaf=1).fit(X_train, y_train)
    _plot_boundary(shallow, X, y, "depth_shallow_regions.pdf", "Controlled-depth tree")
    _plot_boundary(deep, X, y, "depth_deep_regions.pdf", "Deep tree")


if __name__ == "__main__":
    main()
