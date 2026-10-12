"""Lecture 3's kit: its approved narration, its numbers (statistics/raw/l03_numbers.json, written
by capture_l03.py and unit-tested by test_l03.py), the shared lecture pieces bound to them, and the
coffee shop's pastry distribution, which runs through every section.
"""
import json

from lecture_kit import *
from lecture_kit import LectureScene as _BaseScene

N = json.loads((RAW / "l03_numbers.json").read_text())

NARRATION, HEADS = narration(3)
assert len(HEADS) == 11 and "0.0" in NARRATION and "6.9" in NARRATION and "11.12" in NARRATION

PARTS = {0: label("part_0_random_variables"), 1: label("part_1_key_distributions")}

LectureScene, line = bind(_BaseScene, (NARRATION, HEADS), PARTS, {1: 0, 7: 1})

LBLUE = "#8C88F0"                  # course blue is dim on black; use this for blue text


def dec(x, places=2):
    """0.4, 0.44, 0.267 — a value as the screen shows it, trailing zeros dropped."""
    s = f"{x:.{places}f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def pmf_bars(pmf, base=-2.3, height=3.6, step=1.4, width=0.9, vmax=None, color=RLBLUE, size=30,
             fmt=dec, x_labels=None):
    """{value: probability} as bars on a floor: the probability above each bar, the value under it.
    Returns (bars, probs, values, floor)."""
    xs = sorted(pmf)
    vmax = vmax or max(pmf.values())
    k = height / vmax
    pos = [(i - (len(xs) - 1) / 2) * step for i in range(len(xs))]
    bars = VGroup(*[Rectangle(width=width, height=max(pmf[x] * k, 1e-3), stroke_width=0, fill_color=color,
                              fill_opacity=1).move_to([px, base + pmf[x] * k / 2, 0]) for x, px in zip(xs, pos)])
    probs = VGroup(*[MathTex(fmt(pmf[x]), font_size=size).next_to(b, UP, buff=0.12) for x, b in zip(xs, bars)])
    vals = VGroup(*[MathTex(str(x) if x_labels is None else x_labels[i], font_size=size, color=GREY_B)
                    .next_to([px, base, 0], DOWN, buff=0.2) for i, (x, px) in enumerate(zip(xs, pos))])
    floor = Line([pos[0] - width, base, 0], [pos[-1] + width, base, 0], color=GREY_B, stroke_width=2)
    return bars, probs, vals, floor


# the cups by their key in l03_numbers.json, as labels
CUP_NAME = {"small": label("small"), "medium": label("medium"), "large": label("large")}
assert list(CUP_NAME) == list(N["cups"])

PASTRY = {int(k): v for k, v in N["pastry_pmf"].items()}       # {0: 0.7, 1: 0.2, 2: 0.1}
