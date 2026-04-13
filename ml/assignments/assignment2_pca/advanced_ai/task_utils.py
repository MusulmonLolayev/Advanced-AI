"""Shared helpers for the thin PCA task-driver scripts."""

from __future__ import annotations

from pathlib import Path


def require_file(path: str | Path) -> Path:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")
    return path


def print_section(title: str) -> None:
    normalized_title = title.lstrip("\n")
    if title.startswith("\n"):
        print()
    print(normalized_title)
    print("-" * len(normalized_title))


def print_kv(name: str, value: object) -> None:
    print(f"{name} = {value}")
