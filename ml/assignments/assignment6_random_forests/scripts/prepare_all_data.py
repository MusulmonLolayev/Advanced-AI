#!/usr/bin/env python3
"""Wrapper that prepares the Random Forests datasets for Assignment 6."""

from __future__ import annotations

from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    runpy.run_path(str(ROOT / "prepare_datasets.py"), run_name="__main__")


if __name__ == "__main__":
    main()
