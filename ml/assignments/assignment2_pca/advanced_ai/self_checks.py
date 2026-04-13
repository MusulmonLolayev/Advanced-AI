"""Text-based self checks for the PCA implementation."""

from __future__ import annotations

import numpy as np

from advanced_ai.pca import PrincipalComponentAnalysis


def _print_result(name: str, passed: bool, detail: str) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")


def _check_close(name: str, actual: np.ndarray, expected: np.ndarray, atol: float = 1e-8) -> None:
    passed = np.allclose(actual, expected, atol=atol)
    detail = f"max abs diff = {np.max(np.abs(actual - expected)):.3e}"
    _print_result(name, passed, detail)


def _check_orthonormal(name: str, components: np.ndarray, atol: float = 1e-8) -> None:
    gram = components @ components.T
    expected = np.eye(components.shape[0], dtype=components.dtype)
    passed = np.allclose(gram, expected, atol=atol)
    detail = f"max abs diff = {np.max(np.abs(gram - expected)):.3e}"
    _print_result(name, passed, detail)


def run_fit_checks(model: PrincipalComponentAnalysis) -> None:
    X = np.array(
        [
            [2.0, 0.0],
            [0.0, 2.0],
            [1.0, 1.0],
            [3.0, 1.0],
        ]
    )

    for method in ["covariance", "svd"]:
        try:
            model.fit(X, method=method)
            _print_result(f"{method} fit", True, "fit completed")
        except NotImplementedError as exc:
            _print_result(f"{method} fit", False, str(exc))
            continue

        _check_close(f"{method} mean", model.mean_, np.array([1.5, 1.0]))
        _check_orthonormal(f"{method} components", model.components_[:2])
        try:
            ratios = model.explained_variance_ratio()
            _print_result(
                f"{method} explained variance shape",
                ratios.shape == (2,),
                f"shape = {ratios.shape}",
            )
            _print_result(
                f"{method} explained variance sum",
                np.isclose(float(np.sum(ratios)), 1.0, atol=1e-8),
                f"sum = {float(np.sum(ratios)):.6f}",
            )
        except NotImplementedError as exc:
            _print_result(f"{method} explained variance", False, str(exc))

    try:
        cov_model = PrincipalComponentAnalysis().fit(X, method="covariance")
        svd_model = PrincipalComponentAnalysis().fit(X, method="svd")
        alignment = abs(float(np.dot(cov_model.components_[0], svd_model.components_[0])))
        _print_result(
            "covariance vs svd direction",
            np.isclose(alignment, 1.0, atol=1e-6),
            f"|dot| = {alignment:.6f}",
        )
    except NotImplementedError as exc:
        _print_result("covariance vs svd direction", False, str(exc))


def run_projection_checks(model: PrincipalComponentAnalysis) -> None:
    X = np.array(
        [
            [2.0, 0.0],
            [0.0, 2.0],
            [1.0, 1.0],
            [3.0, 1.0],
        ]
    )

    try:
        model.fit(X, method="covariance")
        Z = model.transform(X, n_components=1)
        _print_result("projection shape", Z.shape == (4, 1), f"shape = {Z.shape}")
        X_hat = model.inverse_transform(Z, n_components=1)
        _print_result("reconstruction shape", X_hat.shape == X.shape, f"shape = {X_hat.shape}")
        centered = X - model.mean_
        _check_close("centered mean", centered.mean(axis=0), np.zeros(2))
    except NotImplementedError as exc:
        _print_result("projection/reconstruction", False, str(exc))

    try:
        err = model.reconstruction_error(X, n_components=1)
        _print_result("reconstruction error shape", err.shape == (4,), f"shape = {err.shape}")
        err_full = model.reconstruction_error(X, n_components=2)
        _print_result(
            "reconstruction error monotonicity",
            float(np.mean(err_full)) <= float(np.mean(err)) + 1e-10,
            f"mean(k=1) = {float(np.mean(err)):.6f}, mean(k=2) = {float(np.mean(err_full)):.6f}",
        )
    except NotImplementedError as exc:
        _print_result("reconstruction error", False, str(exc))


def main() -> None:
    print("Advanced AI Assignment 2 self-checks")
    print("------------------------------------")
    model = PrincipalComponentAnalysis()
    run_fit_checks(model)
    run_projection_checks(model)


if __name__ == "__main__":
    main()
