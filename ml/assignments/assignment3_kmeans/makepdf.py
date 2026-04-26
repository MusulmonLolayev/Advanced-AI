#!/usr/bin/env python3
"""Minimal notebook export helper for the k-means worksheet."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", nargs="?", default="kmeans.ipynb")
    parser.add_argument("--to", default="html", choices=["html", "pdf"])
    args = parser.parse_args()

    if shutil.which("jupyter") is None:
        print("jupyter is not installed; cannot export notebook.")
        return 1

    subprocess.run(["jupyter", "nbconvert", "--to", args.to, args.notebook], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
