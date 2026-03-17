"""Shared helpers for the thin task-driver scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


def require_file(path: str | Path) -> Path:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")
    return path


def print_section(title: str) -> None:
    print(title)
    print("-" * len(title))


def print_classification_history(history: Iterable[object]) -> None:
    for row in history:
        print(
            f"k={row.k:>2d} metric={row.metric:<6s} weighting={row.weighting:<8s} "
            f"val_accuracy={row.val_accuracy:.4f}"
        )


def print_regression_history(history: Iterable[object]) -> None:
    for row in history:
        print(
            f"k={row.k:>2d} metric={row.metric:<6s} weighting={row.weighting:<8s} "
            f"val_mae={row.val_mae:.4f} val_rmse={row.val_rmse:.4f}"
        )
