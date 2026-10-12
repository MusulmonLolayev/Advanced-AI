"""What every lecture video shares: the approved-narration parser, the lecture scene with its
cards, and small drawings. Each lecture's own kit (lecture01_kit.py, lecture02_kit.py …) loads
its narration and numbers and binds them with `bind()`.

The narration is read from narration/lectureNN.md, the draft the instructor approved, so the
voice says exactly the approved words and nothing is retyped in Python.
"""
import re
from contextlib import contextmanager

from common import *

HERE = Path(__file__).parent
RAW = HERE / "statistics" / "raw"


# ─── the approved narration ───────────────────────────────────────────────
def parse(md):
    """{'N.k': {'uz', 'en'}} for every narrated line, and {N: {'uz', 'en'}} section headings."""
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


def narration(n):
    return parse((HERE / "narration" / f"lecture{n:02d}.md").read_text())


def money(v, cents=False):
    return f"${v:,.2f}" if cents else f"${v:,.0f}"


class LectureScene(CourseScene):
    """CourseScene plus the lecture's narration keys and cards. A lecture's kit subclasses it
    with NARRATION, HEADS, PARTS ({part: 'name · title'}) and PART_AT ({first section: part})."""
    NARRATION, HEADS, PARTS, PART_AT = {}, {}, {}, {}

    def setup(self):
        super().setup()
        self.brand = brand_mark()
        self.add(self.brand)

    def line(self, key):
        return self.NARRATION[key][LANG]

    @contextmanager
    def say(self, key):
        t = self.line(key)
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
        num, rest = self.HEADS[n][LANG].split(" · ", 1)
        g = VGroup(txt(num, size=30, color=GREY_B), txt(rest, size=48, weight=BOLD, color=RLBLUE))
        g.arrange(DOWN, buff=0.3)
        part = self.PART_AT.get(n)
        if part is not None:
            pn, pt = self.PARTS[part].split(" · ", 1)
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


def bind(scene_cls, narration_and_heads, parts, part_at):
    """A lecture's LectureScene, and its line(key) for module-level use."""
    lines, heads = narration_and_heads

    class Bound(scene_cls):
        NARRATION, HEADS, PARTS, PART_AT = lines, heads, parts, part_at

    Bound.__name__ = Bound.__qualname__ = "LectureScene"

    def line(key):
        return lines[key][LANG]

    return Bound, line


# ─── shared drawings ──────────────────────────────────────────────────────
def card(label, value=None, color=RLBLUE, width=2.9, height=1.5, size=26):
    """A data card: the variable's name, and one example value under it."""
    rect = RoundedRectangle(corner_radius=0.14, width=width, height=height, stroke_color=color,
                            stroke_width=3, fill_color=BLACK, fill_opacity=0.6)
    # a long label breaks at "\n" into centred lines, at the same font size as the other cards
    head = VGroup(*[txt(t, size=size, color=WHITE) for t in label.split("\n")]).arrange(DOWN, buff=0.08)
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
