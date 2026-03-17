"""Run the required California housing regression task."""

from __future__ import annotations

from advanced_ai.classifiers.k_nearest_neighbor import KNearestNeighbor
from advanced_ai.config import CALIFORNIA_DATA_PATH, CORE_METRICS, CORE_WEIGHTINGS, K_CHOICES, RANDOM_SEED
from advanced_ai.data_utils import load_tabular_dataset, make_labeled_split, standardized_split
from advanced_ai.solver import KNNSolver
from advanced_ai.task_utils import print_regression_history, print_section, require_file


def main() -> None:
    X, y = load_tabular_dataset(require_file(CALIFORNIA_DATA_PATH))
    raw_data, _ = make_labeled_split(
        X,
        y,
        train_ratio=0.7,
        val_ratio=0.15,
        seed=RANDOM_SEED,
        shuffle=True,
        standardize=False,
    )
    standardized_data, _ = standardized_split(raw_data)

    print_section("Unscaled experiment")
    unscaled_solver = KNNSolver(
        KNearestNeighbor(),
        raw_data,
    )
    unscaled_history, unscaled_best = unscaled_solver.sweep_regression(K_CHOICES, CORE_METRICS, CORE_WEIGHTINGS)
    print_regression_history(unscaled_history)
    print("best_unscaled =", unscaled_best)

    print_section("\nStandardized experiment")
    standardized_solver = KNNSolver(
        KNearestNeighbor(),
        standardized_data,
    )
    standardized_history, standardized_best = standardized_solver.sweep_regression(
        K_CHOICES,
        CORE_METRICS,
        CORE_WEIGHTINGS,
    )
    print_regression_history(standardized_history)
    print("best_standardized =", standardized_best)

    report = standardized_solver.final_regression_report(standardized_best)
    print_section("\nFinal standardized test report")
    print(f"mae  = {report['mae']:.4f}")
    print(f"rmse = {report['rmse']:.4f}")


if __name__ == "__main__":
    main()
