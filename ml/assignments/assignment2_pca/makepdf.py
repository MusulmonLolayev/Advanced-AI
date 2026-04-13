#!/usr/bin/env python3
"""Minimal notebook export helper for the PCA worksheet.

This is intentionally lightweight. If `jupyter nbconvert` is available,
students can export the main worksheet notebook to HTML or PDF themselves.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", nargs="?", default="pca.ipynb")
    parser.add_argument("--to", default="html", choices=["html", "pdf"])
    args = parser.parse_args()

    if shutil.which("jupyter") is None:
        print("jupyter is not installed; cannot export notebook.")
        return 1

    cmd = ["jupyter", "nbconvert", "--to", args.to, args.notebook]
    subprocess.run(cmd, check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
