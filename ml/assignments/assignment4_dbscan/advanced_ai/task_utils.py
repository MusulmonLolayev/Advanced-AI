"""Helper utilities for Assignment 4 tasks."""

from __future__ import annotations

from pathlib import Path


def print_section(title: str) -> None:
    line = "-" * len(title)
    print(title)
    print(line)


def require_file(path: str | Path) -> Path:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path
