"""Evaluate decision trees on the prepared Iris dataset."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import DEPTH_CHOICES, IRIS_DATA_PATH, RANDOM_SEED, RESULTS_DIR
from advanced_ai.data_utils import load_iris_bundle, standardize_from_train, train_val_split
from advanced_ai.metrics import accuracy, confusion_table
from advanced_ai.task_utils import print_section, require_file
from advanced_ai.trees.decision_tree import DecisionTreeClassifier


def _run_depth_sweep(X_train: np.ndarray, X_val: np.ndarray, y_train: np.ndarray, y_val: np.ndarray, tag: str) -> None:
    rows = []
    lines = [f"Iris decision tree summary ({tag})", ""]
    for depth in DEPTH_CHOICES:
        model = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=2)
        model.fit(X_train, y_train)
        train_acc = accuracy(y_train, model.predict(X_train))
        val_acc = accuracy(y_val, model.predict(X_val))
        rows.append((depth, train_acc, val_acc, model.n_leaves()))
        line = f"max_depth={depth} train_accuracy={train_acc:.6f} val_accuracy={val_acc:.6f} leaves={model.n_leaves()}"
        print(line)
        lines.append(line)

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot([r[0] for r in rows], [r[1] for r in rows], marker="o", label="train")
    ax.plot([r[0] for r in rows], [r[2] for r in rows], marker="o", label="validation")
    ax.set_title(f"Iris accuracy versus tree depth ({tag})")
    ax.set_xlabel("maximum depth")
    ax.set_ylabel("accuracy")
    ax.set_ylim(0.0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / f"iris_tree_depth_{tag}.pdf")
    (RESULTS_DIR / f"iris_tree_summary_{tag}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    plt.close(fig)


def main() -> None:
    bundle = load_iris_bundle(require_file(IRIS_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y = bundle["y"].astype(np.int64)
    X_train, X_val, y_train, y_val = train_val_split(X, y, val_fraction=0.25, seed=RANDOM_SEED)

    print_section("Iris decision tree on raw features")
    _run_depth_sweep(X_train, X_val, y_train, y_val, tag="raw")

    print_section("\nIris decision tree on standardized features")
    X_train_std, X_val_std, _ = standardize_from_train(X_train, X_val)
    _run_depth_sweep(X_train_std, X_val_std, y_train, y_val, tag="standardized")

    model = DecisionTreeClassifier(max_depth=3, min_samples_leaf=2)
    model.fit(X_train, y_train)
    pred = model.predict(X_val)
    print("validation confusion table:")
    print(confusion_table(y_val, pred))


if __name__ == "__main__":
    main()
