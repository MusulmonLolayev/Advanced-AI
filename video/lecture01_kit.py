"""Shared pieces for the Lecture 1 video (lecture01.py and its lecture01_sNN.py sections).

The narration is read from narration/lecture01.md, the draft the instructor approved,
so the voice says exactly the approved words and nothing is retyped here. Every number
on screen comes from statistics/raw/ (capture_v01.py, capture_l01.py).
"""
import json
import re
from contextlib import contextmanager

import numpy as np
from common import *

HERE = Path(__file__).parent
RAW = HERE / "statistics" / "raw"
L = json.loads((RAW / "l01_numbers.json").read_text())
ARR = json.loads((RAW / "l01_arrays.json").read_text())
V1 = json.loads((RAW / "v01_numbers.json").read_text())
SAL = np.sort(np.loadtxt(RAW / "v01_salaries.txt"))


# ─── the approved narration ───────────────────────────────────────────────
def _parse(md):
    lines, heads, sec = {}, {}, None
    rows = md.splitlines()
    for i, row in enumerate(rows):
        if row.startswith("## Lecture opening"):
            sec = 0
        m = re.match(r"### (\d+)-boʻlim · Section \d+ — (.+?) · (.+?)(?:\s+\*\(.*)?$", row)
        if m:
            sec = int(m[1])
            heads[sec] = {"uz": f"{sec}-boʻlim · {m[2]}", "en": f"Section {sec} · {m[3]}"}
            continue
        m = re.match(r"\s*(\d+)\.\s+(?:⏸\s*)?\*\*(.+)\*\*\s*$", row)
        if m and sec is not None:
            en = rows[i + 1].strip()
            assert en.startswith("*") and en.endswith("*"), (sec, m[1], en)
            lines[f"{sec}.{m[1]}"] = {"uz": m[2], "en": en[1:-1]}
            continue
        m = re.match(r"- (?:\*\*)?(s\d\w*)[^*]*(?:\*\*)?\s*\*\*([^*]+)\*\* · \*([^*]+)\*", row)
        if m and sec is not None:
            lines[f"{sec}.{m[1]}"] = {"uz": m[2], "en": m[3]}
    return lines, heads


NARRATION, HEADS = _parse((HERE / "narration" / "lecture01.md").read_text())
assert len(HEADS) == 14 and "0.0" in NARRATION and "4.s3d" in NARRATION and "14.11" in NARRATION


def line(key):
    return NARRATION[key][LANG]


def w(en, uz):
    """An on-screen label in the current language."""
    return uz if LANG == "uz" else en


def money(v, cents=False):
    return f"${v:,.2f}" if cents else f"${v:,.0f}"


PARTS = {0: w("Part 0 · Data and descriptive statistics", "0-qism · Berilganlar va tavsiflovchi statistika"),
         1: w("Part 1 · Probability", "1-qism · Ehtimollik")}


class LectureScene(CourseScene):
    """CourseScene plus the lecture's narration keys and cards."""

    def setup(self):
        super().setup()
        self.brand = brand_mark()
        self.add(self.brand)

    @contextmanager
    def say(self, key):
        t = line(key)
        with self.voiceover(t) as tr:
            yield tr, t

    def wait_for_voiceover(self):
        # a shorter breath than CourseScene's 0.3 s: the clips carry their own tail silence
        had = getattr(self, "current_tracker", None) is not None
        VoiceoverScene.wait_for_voiceover(self)
        if had:
            self.wait(0.15)

    def clear_all(self, run_time=0.5):
        # short: the voice clips already carry their own lead-in and tail silence,
        # and a transition must stay under the 2 s silence limit
        rest = [m for m in self.mobjects if m is not self.brand]
        if rest:
            self.play(*[FadeOut(m) for m in rest], run_time=run_time)

    def cue(self, tr, t, k):
        self.until(tr, t, k)

    def hands_on(self):
        """The silent gap after a pause card: room to stop the video."""
        self.wait(3)

    def section_card(self, n):
        """The section's title card. The first section of a part carries the part's name
        on the same card: two silent cards back to back would exceed the 2 s silence limit."""
        num, rest = HEADS[n][LANG].split(" · ", 1)
        g = VGroup(txt(num, size=30, color=GREY_B), txt(rest, size=48, weight=BOLD, color=RLBLUE))
        g.arrange(DOWN, buff=0.3)
        part = {1: 0, 10: 1}.get(n)
        if part is not None:
            pn, pt = PARTS[part].split(" · ", 1)
            ph = VGroup(txt(pn, size=34, weight=BOLD, color=HILITE), txt(pt, size=34, weight=BOLD))
            ph.arrange(DOWN, buff=0.2)
            bar = Line(LEFT * 3, RIGHT * 3, color=RLBLUE, stroke_width=4)
            g = VGroup(ph, bar, g).arrange(DOWN, buff=0.45)
        if g.width > 12:
            g.scale_to_fit_width(12)
        self.play(FadeIn(g, shift=UP * 0.3), run_time=0.4)
        self.wait(0.35 if part is None else 0.5)
        self.play(FadeOut(g), run_time=0.25)

    def heading(self, text, color=WHITE, size=34):
        return txt(text, size=size, weight=BOLD, color=color).to_edge(UP, buff=SAFE + 0.3)


# ─── shared drawings ──────────────────────────────────────────────────────
def card(label, value=None, color=RLBLUE, width=2.9, height=1.5, size=26):
    """A data card: the variable's name, and one example value under it."""
    rect = RoundedRectangle(corner_radius=0.14, width=width, height=height, stroke_color=color,
                            stroke_width=3, fill_color=BLACK, fill_opacity=0.6)
    head = txt(label, size=size, color=WHITE)
    if head.width > width - 0.3:
        head.scale_to_fit_width(width - 0.3)
    g = VGroup(rect, head)
    if value is None:
        head.move_to(rect)
    else:
        val = txt(value, size=size - 2, color=HILITE)
        VGroup(head, val).arrange(DOWN, buff=0.18).move_to(rect)
        g.add(val)
    return g


def frac(a, b, size=44, color=WHITE):
    return MathTex(rf"\tfrac{{{a}}}{{{b}}}", font_size=size, color=color)


def die_face(n, size=0.8, color=WHITE):
    sq = RoundedRectangle(corner_radius=0.12, width=size, height=size, stroke_color=color, stroke_width=3)
    spots = {1: [(0, 0)], 2: [(-1, 1), (1, -1)], 3: [(-1, 1), (0, 0), (1, -1)],
             4: [(-1, 1), (1, 1), (-1, -1), (1, -1)], 5: [(-1, 1), (1, 1), (0, 0), (-1, -1), (1, -1)],
             6: [(-1, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)]}[n]
    d = size * 0.27
    pips = VGroup(*[Dot([x * d, y * d, 0], radius=size * 0.08, color=color) for x, y in spots])
    return VGroup(sq, pips)


def bars_row(values, base=-2.4, height=2.7, step=1.05, width=0.72, vmax=None, color=RLBLUE, labels=True, size=28):
    """Values as a row of bars on a floor, with the number above each bar."""
    vmax = vmax or max(values)
    k = height / vmax
    xs = [(i - (len(values) - 1) / 2) * step for i in range(len(values))]
    bars = VGroup(*[Rectangle(width=width, height=max(v * k, 1e-3), stroke_width=0, fill_color=color,
                              fill_opacity=1).move_to([x, base + v * k / 2, 0]) for x, v in zip(xs, values)])
    nums = VGroup(*[txt(f"{v:g}", size=size, weight=BOLD).next_to(b, UP, buff=0.12)
                    for v, b in zip(values, bars)])
    floor = Line([xs[0] - width, base, 0], [xs[-1] + width, base, 0], color=GREY_B, stroke_width=2)
    return bars, nums, floor, k, xs
