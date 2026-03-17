"""Shared helpers for instructor-side data preparation."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import requests


ASSIGNMENT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ASSIGNMENT_ROOT / "datasets"
RAW_DIR = DATASETS_DIR / "_raw"


def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def download_file(url: str, destination: str | Path, overwrite: bool = False) -> Path:
    destination = Path(destination)
    ensure_dir(destination.parent)
    if destination.exists() and not overwrite:
        return destination

    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    return destination


def unzip_file(archive_path: str | Path, output_dir: str | Path, overwrite: bool = False) -> Path:
    archive_path = Path(archive_path)
    output_dir = Path(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        return output_dir

    if output_dir.exists() and overwrite:
        shutil.rmtree(output_dir)

    ensure_dir(output_dir)
    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(output_dir)
    return output_dir


def simple_token_length(text: str) -> int:
    return len(text.split())
