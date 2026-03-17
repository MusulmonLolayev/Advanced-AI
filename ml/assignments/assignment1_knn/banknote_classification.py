"""Run the required banknote classification task."""

from __future__ import annotations

from advanced_ai.classifiers.k_nearest_neighbor import KNearestNeighbor
from advanced_ai.config import BANKNOTE_DATA_PATH, CORE_METRICS, CORE_WEIGHTINGS, K_CHOICES, RANDOM_SEED
from advanced_ai.data_utils import load_tabular_dataset, make_labeled_split
from advanced_ai.solver import KNNSolver
from advanced_ai.task_utils import print_classification_history, print_section, require_file


def main() -> None:
    X, y = load_tabular_dataset(require_file(BANKNOTE_DATA_PATH))
    data, _ = make_labeled_split(
        X,
        y,
        train_ratio=0.7,
        val_ratio=0.15,
        seed=RANDOM_SEED,
        shuffle=True,
        standardize=True,
    )

    solver = KNNSolver(KNearestNeighbor(), data)
    history, best = solver.sweep_classification(K_CHOICES, CORE_METRICS, CORE_WEIGHTINGS)

    print_section("Validation sweep")
    print_classification_history(history)

    print_section("\nBest validation config")
    print(best)

    report = solver.final_classification_report(best)
    print_section("\nTest report")
    print(f"accuracy  = {report['accuracy']:.4f}")
    print(f"precision = {report['precision']:.4f}")
    print(f"recall    = {report['recall']:.4f}")
    print(f"f1        = {report['f1']:.4f}")
    print("confusion_matrix =")
    print(report["confusion_matrix"])


if __name__ == "__main__":
    main()
