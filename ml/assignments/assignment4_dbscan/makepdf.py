"""Convert the DBSCAN notebook to PDF."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: makepdf.py NOTEBOOK.ipynb")
    notebook = Path(sys.argv[1]).resolve()
    if not notebook.exists():
        raise SystemExit(f"Notebook not found: {notebook}")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "pdf",
            str(notebook),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
