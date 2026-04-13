"""Experiment helpers for repeated PCA evaluation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PCAComponentSweepResult:
    n_components: int
    method: str
    val_reconstruction_error: float
    val_explained_variance: float


class PCASolver:
    """Run repeated PCA experiments without rewriting the evaluation loop."""

    def __init__(self, model, data: dict[str, np.ndarray]) -> None:
        self.model = model
        self.data = data

    def fit(self, method: str = "svd") -> None:
        self.model.fit(self.data["X_train"], method=method)

    def sweep_components(
        self,
        component_choices: list[int],
        methods: list[str] | tuple[str, ...] = ("svd", "covariance"),
    ) -> tuple[list[PCAComponentSweepResult], PCAComponentSweepResult]:
        if not component_choices:
            raise ValueError("component_choices must not be empty.")

        self.fit(method=methods[0])
        history: list[PCAComponentSweepResult] = []
        best: PCAComponentSweepResult | None = None

        for method in methods:
            self.fit(method=method)
            for n_components in component_choices:
                val_error = self.model.reconstruction_error(self.data["X_val"], n_components=n_components)
                result = PCAComponentSweepResult(
                    n_components=n_components,
                    method=method,
                    val_reconstruction_error=float(np.mean(val_error)),
                    val_explained_variance=float(self.model.cumulative_explained_variance(n_components)),
                )
                history.append(result)
                if best is None or result.val_reconstruction_error < best.val_reconstruction_error:
                    best = result

        assert best is not None
        return history, best

    def final_reconstruction_report(self, config: PCAComponentSweepResult) -> dict[str, float | PCAComponentSweepResult]:
        self.fit(method=config.method)
        test_error = self.model.reconstruction_error(self.data["X_test"], n_components=config.n_components)
        return {
            "config": config,
            "mean_reconstruction_error": float(np.mean(test_error)),
        }
