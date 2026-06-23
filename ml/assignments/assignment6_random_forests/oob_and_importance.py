"""Report OOB error and feature importances on the forest study dataset."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import FOREST_STUDY_DATA_PATH, RANDOM_SEED, RESULTS_DIR
from advanced_ai.data_utils import load_forest_study_bundle, train_val_split
from advanced_ai.forest.random_forest import RandomForestClassifier
from advanced_ai.metrics import accuracy
from advanced_ai.task_utils import print_section, require_file

N_ESTIMATORS = 100


def main() -> None:
    bundle = load_forest_study_bundle(require_file(FOREST_STUDY_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y = bundle["y"].astype(np.int64)
    feature_names = [str(name) for name in bundle["feature_names"]]
    X_train, X_test, y_train, y_test = train_val_split(X, y, val_fraction=0.25, seed=RANDOM_SEED)

    print_section("Forest study: OOB error and feature importance")
    forest = RandomForestClassifier(
        n_estimators=N_ESTIMATORS, max_depth=None, min_samples_leaf=2, random_state=RANDOM_SEED
    )
    forest.fit(X_train, y_train)

    oob_err = forest.oob_error(X_train, y_train)
    test_acc = accuracy(y_test, forest.predict(X_test))
    print(f"OOB error = {oob_err:.4f}")
    print(f"test accuracy = {test_acc:.4f} (test error = {1.0 - test_acc:.4f})")

    importances = forest.feature_importances(X.shape[1])
    order = np.argsort(importances)[::-1]
    print("feature importance ranking:")
    for rank in order:
        print(f"  {feature_names[rank]}: {importances[rank]:.4f}")
    print("top-3 features:")
    for rank in order[:3]:
        print(f"  {feature_names[rank]}: {importances[rank]:.4f}")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.bar(np.arange(len(feature_names)), importances[order], color="tab:blue")
    ax.set_xticks(np.arange(len(feature_names)))
    ax.set_xticklabels([feature_names[i] for i in order], rotation=35, ha="right")
    ax.set_title(f"Feature importances (B={N_ESTIMATORS})")
    ax.set_ylabel("importance")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / "feature_importances.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
