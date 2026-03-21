"""Experiment helpers for repeated k-NN evaluation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from advanced_ai.metrics import (
    accuracy_score,
    confusion_matrix_binary,
    mae,
    precision_recall_f1,
    rmse,
)


@dataclass
class ClassificationSweepResult:
    k: int
    metric: str
    weighting: str
    val_accuracy: float


@dataclass
class RegressionSweepResult:
    k: int
    metric: str
    weighting: str
    val_mae: float
    val_rmse: float


class KNNSolver:
    """Run repeated k-NN experiments without rewriting the evaluation loop."""

    def __init__(self, model, data: dict[str, np.ndarray]) -> None:
        self.model = model
        self.data = data

    def fit(self) -> None:
        self.model.fit(self.data["X_train"], self.data.get("y_train"))

    @staticmethod
    def _iter_configs(
        k_choices: list[int],
        metric_choices: list[str],
        weighting_choices: list[str],
    ):
        for metric in metric_choices:
            for weighting in weighting_choices:
                for k in k_choices:
                    yield k, metric, weighting

    @staticmethod
    def _validate_sweep_inputs(
        k_choices: list[int],
        metric_choices: list[str],
        weighting_choices: list[str],
    ) -> None:
        if not k_choices:
            raise ValueError("k_choices must not be empty.")
        if not metric_choices:
            raise ValueError("metric_choices must not be empty.")
        if not weighting_choices:
            raise ValueError("weighting_choices must not be empty.")
        if any(k < 1 for k in k_choices):
            raise ValueError(f"k choices must be >= 1, got {k_choices}")

    def sweep_classification(
        self,
        k_choices: list[int],
        metric_choices: list[str],
        weighting_choices: list[str],
        num_loops: int = 0,
    ) -> tuple[list[ClassificationSweepResult], ClassificationSweepResult]:
        self._validate_sweep_inputs(k_choices, metric_choices, weighting_choices)
        self.fit()
        history: list[ClassificationSweepResult] = []
        best: ClassificationSweepResult | None = None

        for k, metric, weighting in self._iter_configs(k_choices, metric_choices, weighting_choices):
            y_val_pred = self.model.predict(
                self.data["X_val"],
                k=k,
                metric=metric,
                task="classification",
                weighting=weighting,
                num_loops=num_loops,
            )
            result = ClassificationSweepResult(
                k=k,
                metric=metric,
                weighting=weighting,
                val_accuracy=accuracy_score(self.data["y_val"], y_val_pred),
            )
            history.append(result)
            if best is None or result.val_accuracy > best.val_accuracy:
                best = result

        return history, best

    def final_classification_report(
        self,
        config: ClassificationSweepResult,
        num_loops: int = 0,
    ) -> dict[str, object]:
        self.fit()
        y_test_pred = self.model.predict(
            self.data["X_test"],
            k=config.k,
            metric=config.metric,
            task="classification",
            weighting=config.weighting,
            num_loops=num_loops,
        )
        prf = precision_recall_f1(self.data["y_test"], y_test_pred)
        return {
            "config": config,
            "accuracy": accuracy_score(self.data["y_test"], y_test_pred),
            "precision": prf["precision"],
            "recall": prf["recall"],
            "f1": prf["f1"],
            "confusion_matrix": confusion_matrix_binary(self.data["y_test"], y_test_pred),
        }

    def sweep_regression(
        self,
        k_choices: list[int],
        metric_choices: list[str],
        weighting_choices: list[str],
        num_loops: int = 0,
    ) -> tuple[list[RegressionSweepResult], RegressionSweepResult]:
        self._validate_sweep_inputs(k_choices, metric_choices, weighting_choices)
        self.fit()
        history: list[RegressionSweepResult] = []
        best: RegressionSweepResult | None = None

        for k, metric, weighting in self._iter_configs(k_choices, metric_choices, weighting_choices):
            y_val_pred = self.model.predict(
                self.data["X_val"],
                k=k,
                metric=metric,
                task="regression",
                weighting=weighting,
                num_loops=num_loops,
            )
            result = RegressionSweepResult(
                k=k,
                metric=metric,
                weighting=weighting,
                val_mae=mae(self.data["y_val"], y_val_pred),
                val_rmse=rmse(self.data["y_val"], y_val_pred),
            )
            history.append(result)
            if best is None or result.val_rmse < best.val_rmse:
                best = result

        return history, best

    def final_regression_report(
        self,
        config: RegressionSweepResult,
        num_loops: int = 0,
    ) -> dict[str, object]:
        self.fit()
        y_test_pred = self.model.predict(
            self.data["X_test"],
            k=config.k,
            metric=config.metric,
            task="regression",
            weighting=config.weighting,
            num_loops=num_loops,
        )
        return {
            "config": config,
            "mae": mae(self.data["y_test"], y_test_pred),
            "rmse": rmse(self.data["y_test"], y_test_pred),
        }
