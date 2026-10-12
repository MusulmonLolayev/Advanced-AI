"""Lecture 5's kit: its approved narration, its numbers (statistics/raw/l05_numbers.json, written
by capture_l05.py and unit-tested by test_l05.py) and the shared lecture pieces bound to them.
"""
import json

from lecture_kit import *
from lecture_kit import LectureScene as _BaseScene

N = json.loads((RAW / "l05_numbers.json").read_text())

NARRATION, HEADS = narration(5)
assert len(HEADS) == 10 and "0.0" in NARRATION and "5.8" in NARRATION and "10.11" in NARRATION

PARTS = {0: label("part_0_the_central_limit_theorem"), 1: label("part_1_maximum_likelihood_estimation")}

LectureScene, line = bind(_BaseScene, (NARRATION, HEADS), PARTS, {1: 0, 6: 1})

LBLUE = "#8C88F0"                  # course blue is dim on black; use this for blue text


def dec(x, places=2):
    """0.55, 0.314, 2.5 — a value as the screen shows it, trailing zeros dropped."""
    s = f"{x:.{places}f}"
    if "." in s:                   # only zeros after a decimal point go: dec(-20, 0) stays "-20"
        s = s.rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def pct(x, places=1):
    """0.1353 → 13.5% (trailing zeros dropped)."""
    return dec(100 * x, places) + "%"
