"""Compare Extra-Trees against the Lab 6 random forest on Iris-like data."""

from __future__ import annotations

import time

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import B_CHOICES, EXTRA_TREES_DATA_PATH, N_REPEATS, RANDOM_SEED, RESULTS_DIR
from advanced_ai.data_utils import load_extra_trees_bundle, train_val_split
from advanced_ai.forest.extra_trees import ExtraTreesClassifier
from advanced_ai.forest.random_forest import RandomForestClassifier
from advanced_ai.metrics import accuracy
from advanced_ai.task_utils import print_section, require_file


def _sweep(model_cls, X_train, y_train, X_test, y_test) -> dict[int, dict[str, float]]:
    summary: dict[int, dict[str, float]] = {}
    for B in B_CHOICES:
        train_accs, test_accs, fit_times = [], [], []
        for repeat in range(N_REPEATS):
            model = model_cls(n_estimators=B, random_state=RANDOM_SEED + repeat)
            start = time.perf_counter()
            model.fit(X_train, y_train)
            fit_times.append(time.perf_counter() - start)
            train_accs.append(accuracy(y_train, model.predict(X_train)))
            test_accs.append(accuracy(y_test, model.predict(X_test)))
        summary[B] = {
            "fit_time_mean": float(np.mean(fit_times)),
            "train_acc_mean": float(np.mean(train_accs)),
            "test_acc_mean": float(np.mean(test_accs)),
            "test_acc_std": float(np.std(test_accs)),
        }
    return summary


def main() -> None:
    bundle = load_extra_trees_bundle(require_file(EXTRA_TREES_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y = bundle["y"].astype(np.int64)
    X_train, X_test, y_train, y_test = train_val_split(X, y, val_fraction=0.25, seed=RANDOM_SEED)

    print_section("Random Forest sweep")
    rf_summary = _sweep(RandomForestClassifier, X_train, y_train, X_test, y_test)
    for B, row in rf_summary.items():
        print(f"B={B} fit_time={row['fit_time_mean']:.4f}s train_acc={row['train_acc_mean']:.4f} "
              f"test_acc={row['test_acc_mean']:.4f} test_acc_std={row['test_acc_std']:.4f}")

    print_section("\nExtra-Trees sweep")
    et_summary = _sweep(ExtraTreesClassifier, X_train, y_train, X_test, y_test)
    for B, row in et_summary.items():
        print(f"B={B} fit_time={row['fit_time_mean']:.4f}s train_acc={row['train_acc_mean']:.4f} "
              f"test_acc={row['test_acc_mean']:.4f} test_acc_std={row['test_acc_std']:.4f}")

    lines = ["B,rf_fit_time,rf_test_acc,rf_test_acc_std,et_fit_time,et_test_acc,et_test_acc_std"]
    for B in B_CHOICES:
        rf, et = rf_summary[B], et_summary[B]
        lines.append(
            f"{B},{rf['fit_time_mean']:.6f},{rf['test_acc_mean']:.6f},{rf['test_acc_std']:.6f},"
            f"{et['fit_time_mean']:.6f},{et['test_acc_mean']:.6f},{et['test_acc_std']:.6f}"
        )
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "extra_trees_iris_summary.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
    ax1.plot(B_CHOICES, [rf_summary[B]["fit_time_mean"] for B in B_CHOICES], marker="o", label="random forest")
    ax1.plot(B_CHOICES, [et_summary[B]["fit_time_mean"] for B in B_CHOICES], marker="o", label="extra-trees")
    ax1.set_xlabel("B")
    ax1.set_ylabel("training time (s)")
    ax1.set_title("Training time versus B")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.plot(B_CHOICES, [rf_summary[B]["test_acc_mean"] for B in B_CHOICES], marker="o", label="random forest")
    ax2.plot(B_CHOICES, [et_summary[B]["test_acc_mean"] for B in B_CHOICES], marker="o", label="extra-trees")
    ax2.set_xlabel("B")
    ax2.set_ylabel("test accuracy")
    ax2.set_title("Test accuracy versus B")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "extra_trees_vs_forest.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
