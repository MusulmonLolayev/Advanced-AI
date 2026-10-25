"""Paths, the step budget and the model settings, in one place.

Replay (the default for every check) needs none of the model settings; they matter only for a live run.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "sample_articles.jsonl"
TRACES = ROOT / "traces"


def load_env(path=ROOT / ".env"):
    """Put the KEY=value lines of .env into the environment (a variable already set wins)."""
    for line in path.read_text().splitlines() if path.exists() else []:
        key, sep, value = line.partition("=")
        if sep and not key.startswith("#") and value.strip():
            os.environ.setdefault(key.strip(), value.strip())


load_env()

MAX_STEPS = 8                      # the step budget: a loop that never answers must stop
SEED = 0                           # for any random choice in later labs; this lab samples nothing
TEMPERATURE = 0                    # a recorded run only replays if the live run was deterministic
MODEL = os.environ.get("LLM_MODEL", "deepseek-flash")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
