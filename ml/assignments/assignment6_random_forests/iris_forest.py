"""Sweep the number of trees B and track OOB error versus test accuracy on Iris."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import B_CHOICES, IRIS_DATA_PATH, RANDOM_SEED, RESULTS_DIR
from advanced_ai.data_utils import load_iris_bundle, train_val_split
from advanced_ai.forest.random_forest import RandomForestClassifier
from advanced_ai.metrics import accuracy
from advanced_ai.task_utils import print_section, require_file


def main() -> None:
    bundle = load_iris_bundle(require_file(IRIS_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y = bundle["y"].astype(np.int64)
    X_train, X_test, y_train, y_test = train_val_split(X, y, val_fraction=0.25, seed=RANDOM_SEED)

    print_section("Iris: random forest B sweep")
    rows = []
    for B in B_CHOICES:
        forest = RandomForestClassifier(n_estimators=B, max_depth=None, min_samples_leaf=2, random_state=RANDOM_SEED)
        forest.fit(X_train, y_train)
        train_acc = accuracy(y_train, forest.predict(X_train))
        oob_err = forest.oob_error(X_train, y_train)
        test_acc = accuracy(y_test, forest.predict(X_test))
        rows.append((B, train_acc, oob_err, test_acc))
        print(f"B={B} train_accuracy={train_acc:.4f} oob_error={oob_err:.4f} test_accuracy={test_acc:.4f}")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot([r[0] for r in rows], [r[2] for r in rows], marker="o", label="OOB error")
    ax.plot([r[0] for r in rows], [r[3] for r in rows], marker="o", label="test accuracy")
    ax.set_xscale("log")
    ax.set_title("Iris: OOB error and test accuracy versus B")
    ax.set_xlabel("number of trees (B)")
    ax.set_ylabel("rate")
    ax.set_ylim(0.0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / "iris_forest_oob_vs_B.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
