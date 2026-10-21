"""What every lecture video shares: the approved-narration parser, the lecture scene with its
cards, and small drawings. Each lecture's own kit (lecture01_kit.py, lecture02_kit.py …) loads
its narration and numbers and binds them with `bind()`.

The narration is read from narration/lectureNN.md, the draft the instructor approved, so the
voice says exactly the approved words and nothing is retyped in Python.
"""
import os
import re
import sys
from contextlib import contextmanager

from common import *
import builds
import drafts
import yaml

HERE = Path(__file__).parent
RAW = HERE / "statistics" / "raw"


# ─── the approved narration ───────────────────────────────────────────────
def parse(md, single=None):
    """{'N.k': {'uz', 'en'}} for every narrated line, and {N: {'uz', 'en'}} section headings.

    single="en": a narration written in one language only (the agent course): headings
    "### Section N — Title", and each bold line is that language's text, with a "▸" visual under it
    instead of a second-language line. Other languages are added beside it later."""
    if single:
        return _parse_single(md, single)
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
        m = re.match(r"\s*(\d+[a-z]?)\.\s+(?:⏸\s*)?\*\*(.+)\*\*\s*$", row)   # "3a": a line added after 3
        if m and sec is not None:
            en = rows[i + 1].strip()
            assert en.startswith("*") and en.endswith("*"), (sec, m[1], en)
            lines[f"{sec}.{m[1]}"] = {"uz": m[2], "en": en[1:-1]}
            continue
        m = re.match(r"- (?:\*\*)?(s\d\w*)[^*]*(?:\*\*)?\s*\*\*([^*]+)\*\* · \*([^*]+)\*", row)
        if m and sec is not None:
            lines[f"{sec}.{m[1]}"] = {"uz": m[2], "en": m[3]}
    return lines, heads


def _parse_single(md, lang):
    """A one-language narration: "### Section N — Title" (whatever word the language puts before N, see languages.yaml),
    "N. **text**" lines and "- sNx **text**" depth lines. A line with no text yet (a skeleton's) is left out."""
    lines, heads, sec = {}, {}, None
    for row in md.splitlines():
        if row.startswith(("## Lecture opening", "## 강의 시작")):
            sec = 0
            continue
        m = re.match(r"### [^\d\n]*(\d+)[^\d\n—–-]*[—–-]\s*(.*?)\s*$", row)
        if m:
            sec = int(m[1])
            heads[sec] = {lang: f"{languages.section(lang, sec)} · {m[2]}"}
            continue
        m = re.match(r"\s*(\d+[a-z]?)\.\s+(?:⏸\s*)?\*\*(.+)\*\*\s*$", row) or \
            re.match(r"- (s\d\w*)\s+\*\*(.+?)\*\*(?:\s+▸.*)?\s*$", row)
        if m and sec is not None:
            key = f"{sec}.{m[1]}"
            assert key not in lines, f"line {key} twice"
            lines[key] = {lang: m[2]}
    return lines, heads


def narration_dir():
    """narration/, or $NARRATION_DIR: the editor renders a draft version of a scene from a changed copy of the file."""
    return Path(os.environ.get("NARRATION_DIR", HERE / "narration"))


def narration(n):
    return parse((narration_dir() / f"lecture{n:02d}.md").read_text())


def primary_language(stem):
    """The language a lecture was written in (the cue reference): Uzbek for Module 0, English for the agent module."""
    try:
        return "uz" if builds.parse_stem(stem)[0] == 0 else "en"
    except ValueError:                 # not a numbered lecture (the agent course): English
        return "en"


def add_language(lines, heads, stem, lang):
    """Put the lecture's narration in `lang` (narration/<stem>_<lang>.md, one language, the primary language's line ids)
    into lines / heads, in place. A line the file lacks or has empty is left out: saying it fails with a clear message
    (check_lang.py lists them first). A line the lecture has no id for is an error. Returns whether the file was there."""
    path = narration_dir() / f"{stem}_{lang}.md"
    if not path.exists():
        return False
    new, new_heads = _parse_single(path.read_text(), lang)
    unknown = sorted(set(new) - set(lines))
    assert not unknown, f"{path.name}: lines {unknown[:5]} are not in the lecture"
    for k, v in new.items():
        lines[k][lang] = v[lang]
    for n, v in new_heads.items():
        heads.setdefault(n, {}).update(v)
    return True


def cue_overrides(stem, lang):
    """{line key: {reference phrase: phrase in lang}} from narration/<stem>_<lang>.cues.yaml, or {}."""
    path = narration_dir() / f"{stem}_{lang}.cues.yaml"
    return {str(k): v for k, v in (yaml.safe_load(path.read_text()) or {}).items()} if path.exists() else {}


def money(v, cents=False):
    return f"${v:,.2f}" if cents else f"${v:,.0f}"


class LectureScene(CourseScene):
    """CourseScene plus the lecture's narration keys and cards. A lecture's kit subclasses it
    with NARRATION, HEADS, PARTS ({part: 'name · title'}) and PART_AT ({first section: part})."""
    NARRATION, HEADS, PARTS, PART_AT = {}, {}, {}, {}
    BRAND = True                       # the corner mark; a video presented elsewhere sets it False
    PRIMARY, OVERRIDES = "uz", {}      # the language the lecture was written in; the build language's cue overrides
    STEM, DRAFT_TAG = "", True         # the lecture; whether an unapproved build in a new language carries the corner tag
    CARD_HOLD, CLEAR_TIME = 0.35, 0.5  # section card's still time; the fade between scenes (seconds)

    def setup(self):
        super().setup()
        self.brand = brand_mark() if self.BRAND else VGroup()
        if self.DRAFT_TAG and LANG not in ("uz", "en") and drafts.tagged(self.STEM, LANG):
            # a build in a new language is a draft until every line and label is approved (drafts.py); uz and en
            # keep what they always did (the Module 7 scenes tag themselves, with their own label)
            self.brand.add(txt(languages.draft_word(LANG), size=16, color=RLRED).to_corner(DL, buff=SAFE))
        self.add(self.brand)

    def line(self, key):
        if LANG not in self.NARRATION[key]:
            raise NoForm(f"no {LANG} narration for line {key} (empty or missing in narration/*_{LANG}.md); "
                         f"check_lang.py lists the lines")
        return self.NARRATION[key][LANG]

    @contextmanager
    def say(self, key):
        t = self.line(key)
        self._key = key                # the cue mapping reads this line's text in the other languages
        with self.voiceover(t) as tr:
            yield tr, t

    def cue_ref(self, text):
        """The CueRef of the line being voiced: its key (from say, else the line with this text) and its texts."""
        key = getattr(self, "_key", None)
        if key is None or self.NARRATION.get(key, {}).get(LANG) != text:
            key = next((k for k, v in self.NARRATION.items() if v.get(LANG) == text), None)
        if key is None:
            return None
        return CueRef(key, self.NARRATION[key], self.PRIMARY, self.OVERRIDES.get(key, {}))

    def wait_for_voiceover(self):
        # a shorter breath than CourseScene's 0.3 s: the clips carry their own tail silence
        had = getattr(self, "current_tracker", None) is not None
        VoiceoverScene.wait_for_voiceover(self)
        if had:
            self.wait(0.15)

    def clear_all(self, run_time=None):
        # short: the voice clips already carry their own lead-in and tail silence,
        # and a transition must stay under the 2 s silence limit
        rest = [m for m in self.mobjects if m is not self.brand]
        if rest:
            self.play(*[FadeOut(m) for m in rest], run_time=run_time or self.CLEAR_TIME)

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
        self.wait(self.CARD_HOLD if part is None else self.CARD_HOLD + 0.15)
        self.play(FadeOut(g), run_time=0.25)

    def heading(self, text, color=WHITE, size=34):
        return txt(text, size=size, weight=BOLD, color=color).to_edge(UP, buff=SAFE + 0.3)


def bind(scene_cls, narration_and_heads, parts, part_at, merge=True):
    """A lecture's LectureScene, and its line(key) for module-level use. The build language's narration file is
    merged into the lines first (add_language), unless the kit does that itself (merge=False)."""
    lines, heads = narration_and_heads
    stem = sys._getframe(1).f_globals["__name__"].removesuffix("_kit")      # the kit that calls: lecture01_kit
    if merge:
        add_language(lines, heads, stem, LANG)

    class Bound(scene_cls):
        NARRATION, HEADS, PARTS, PART_AT = lines, heads, parts, part_at
        PRIMARY, OVERRIDES, STEM = primary_language(stem), cue_overrides(stem, LANG), stem

    Bound.__name__ = Bound.__qualname__ = "LectureScene"

    def line(key):
        if LANG not in lines[key]:
            raise NoForm(f"no {LANG} narration for line {key} (empty or missing in narration/{stem}_{LANG}.md)")
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
