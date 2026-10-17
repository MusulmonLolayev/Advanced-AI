"""Module 7, Lecture 1's kit: its narration (narration/m7_lecture01.md), its numbers (m7/raw/l01_numbers.json,
tested by m7/test_l01.py), the class agent's recorded runs (agents/class_agent/traces/, facts tested by
test_class_agent.py) and the real Labor Code articles they read. Nothing shown here is typed by hand.
"""
import json
import re
import sys
import textwrap

from lecture_kit import *
from lecture_kit import LectureScene as _BaseScene

M7 = HERE / "m7"
N = json.loads((M7 / "raw" / "l01_numbers.json").read_text())
_spec = __import__("importlib.util").util.spec_from_file_location("capture_l01_m7", M7 / "capture_l01.py")
C = __import__("importlib.util").util.module_from_spec(_spec)
_spec.loader.exec_module(C)                     # the capture script's inputs (P_GOOD, K_LONG …) for the curves
assert C.compute() == N, "m7/raw/l01_numbers.json is stale: rerun m7/capture_l01.py"
AGENT = REPO / "agents" / "class_agent"
sys.path.insert(0, str(AGENT))
import agent as class_agent                     # noqa: E402  the real loop's act(): failure replies, search lists
from corpus import ARTICLES                     # noqa: E402

NARRATION, HEADS = parse((HERE / "narration" / "m7_lecture01.md").read_text())
assert len(HEADS) == 10 and "0.0" in NARRATION and "10.86" in NARRATION

LectureScene, line = bind(_BaseScene, (NARRATION, HEADS), {}, {})

MONO = "DejaVu Sans Mono"
THINK = "#8fb8de"
KIND_COLOR = {"thought": THINK, "action": GOOD, "observation": GREY_B, "answer": HILITE}


def trace(name):
    return json.loads((AGENT / "traces" / f"{name}.json").read_text())


def turns(name):
    """[(thought, action, observation or None)] of a recorded run, split from the model's own text."""
    out = []
    for s in trace(name)["trace"]:
        th = re.search(r"Thought:\s*(.*?)\s*(?=\nAction:|$)", s["model"], re.S)
        ac = re.search(r"Action:\s*(.*)", s["model"], re.S)
        out.append((th.group(1).strip() if th else "", ac.group(1).strip() if ac else "", s["observation"]))
    return out


def mono(text, size=20, color=WHITE, width=None):
    """Monospace text, wrapped to `width` characters."""
    if width:
        text = "\n".join(textwrap.fill(p, width) for p in text.split("\n"))
    return Text(text, font=MONO, font_size=size, color=color, disable_ligatures=True)


def short(text, n):
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def trace_line(kind, text, size=19, width=70):
    """One line of a ReAct trace: the coloured kind ('Fikr') and the recorded text beside it."""
    head = txt(label({"thought": "m7_thought", "action": "m7_action", "observation": "m7_observation",
                      "answer": "m7_final"}[kind]), size=size + 3, weight=BOLD, color=KIND_COLOR[kind])
    body = mono(text, size=size, color=WHITE if kind != "observation" else GREY_A, width=width)
    g = VGroup(head, body)
    body.next_to(head, RIGHT, buff=0.25, aligned_edge=UP)
    return g


def stack(rows, buff=0.18, left=-6.5, top=2.7):
    """Rows left-aligned under each other, from the top left of the frame."""
    g = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    g.move_to([left, top, 0], aligned_edge=UL)
    return g


def article_card(aid, phrase=None, chars=260, width=10.5, size=20):
    """A real article: its number and title, then the start of its text with `phrase` lit."""
    a = ARTICLES[str(aid)]
    body = a["text"].replace("\n", " ")
    if phrase and phrase in body:
        i = body.index(phrase)
        start = max(0, i - 80)
        body = ("…" if start else "") + body[start:]
    body = short(body, chars)
    head = txt(f"{a['article_display']}. {a['title']}", size=size + 4, weight=BOLD, color=HILITE)
    if head.width > width:
        head.scale_to_fit_width(width)
    lines = textwrap.fill(body, 64)
    t2c = {phrase: HILITE} if phrase and phrase in lines else {}
    text = Text(lines, font_size=size, color=GREY_A, t2c=t2c, disable_ligatures=True)
    if text.width > width:
        text.scale_to_fit_width(width)
    g = VGroup(head, text).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
    frame = SurroundingRectangle(g, buff=0.3, corner_radius=0.12, color=RLBLUE, stroke_width=3)
    frame.set_fill(BLACK, opacity=0.85)
    return VGroup(frame, g)


def node(text_, color=RLBLUE, width=2.4, height=0.9, size=26):
    """A labelled box at one text size (box() scales every word to its width, so short words came out huge)."""
    t = txt(text_, size=size)
    if t.width > width - 0.35:
        t.scale_to_fit_width(width - 0.35)
    rect = RoundedRectangle(corner_radius=0.12, width=width, height=height, stroke_color=color, stroke_width=3)
    return VGroup(rect, t.move_to(rect))


def loop_diagram(scale=1.0):
    """Thought → Action → Observation → back to Thought, with an exit to the Answer."""
    th = node(label("m7_thought"), color=THINK)
    ac = node(label("m7_action"), color=GOOD)
    ob = node(label("m7_observation"), color=GREY_B)
    an = node(label("m7_final"), color=HILITE)
    th.move_to(LEFT * 4.2)
    ac.move_to(ORIGIN)
    ob.move_to(RIGHT * 4.2)
    an.move_to(LEFT * 4.2 + UP * 2.0)
    a1 = Arrow(th.get_right(), ac.get_left(), buff=0.1, color=WHITE)
    a2 = Arrow(ac.get_right(), ob.get_left(), buff=0.1, color=WHITE)
    a3 = CurvedArrow(ob.get_bottom() + DOWN * 0.05, th.get_bottom() + DOWN * 0.05, angle=-TAU / 5, color=WHITE)
    a4 = Arrow(th.get_top(), an.get_bottom(), buff=0.1, color=HILITE)
    g = VGroup(th, ac, ob, an, a1, a2, a3, a4).scale(scale)
    return g


def fit(m, width=12.4):
    """Shrink m to `width` if it is wider: nothing may reach the frame edge (check_edges.py)."""
    if m.width > width:
        m.scale_to_fit_width(width)
    return m


def pause(steps):
    return fit(pause_card(steps))


def draft_tag():
    """The corner tag every frame of the draft carries."""
    return txt(label("m7_draft"), size=16, color=RLRED).to_corner(DL, buff=SAFE)


# What stays on screen after an animation must fit here: inside the frame, and above the bottom strip that holds the
# brand mark and the draft tag (check_edges.py only sees the outer 4 px, so a card covering the tag at 7:15 passed it).
LIMIT_X, LIMIT_TOP, LIMIT_BOTTOM = 6.95, 3.85, -3.28


class Scene7(LectureScene):
    """The lecture scene with the draft tag on every frame (removed once the narration is approved), and a check
    after every animation that nothing left on screen runs off the frame or into the bottom strip."""
    DRAFT = True

    def setup(self):
        super().setup()
        if self.DRAFT:
            self.brand.add(draft_tag())        # clear_all() keeps the brand group, so the tag stays too

    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        for m in self.mobjects:
            if m is self.brand or m.width == 0:
                continue
            l, r = m.get_left()[0], m.get_right()[0]
            b, t = m.get_bottom()[1], m.get_top()[1]
            if l < -LIMIT_X or r > LIMIT_X or t > LIMIT_TOP or b < LIMIT_BOTTOM:
                raise RuntimeError(f"{type(self).__name__} at {self.renderer.time:.1f}s: {type(m).__name__} spans "
                                   f"x {l:.2f}..{r:.2f}, y {b:.2f}..{t:.2f} -- outside the safe area")
