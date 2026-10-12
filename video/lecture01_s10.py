"""Lecture 1, section 10 — sample space, event, probability (opens Part 1).

Probabilities come from statistics/raw/l01_numbers.json (capture_l01.py).
"""
from fractions import Fraction

from lecture01_kit import *

assert (L["p_even"], L["p_gt4"]) == ("1/2", "1/3")
EVEN, GT4 = [2, 4, 6], [5, 6]
LB = interpolate_color(ManimColor(RLBLUE), WHITE, 0.4)   # course blue, lifted for text on black
assert str(Fraction(len(EVEN), 6)) == L["p_even"] and str(Fraction(len(GT4), 6)) == L["p_gt4"]


def omega_set(width=8.4, height=1.7, y=0.6):
    """Ω: the six die faces inside one rounded box."""
    faces = VGroup(*[die_face(n, size=0.9) for n in range(1, 7)]).arrange(RIGHT, buff=0.35)
    rect = RoundedRectangle(corner_radius=0.3, width=width, height=height, stroke_color=RLBLUE, stroke_width=4)
    rect.move_to([0, y, 0])
    faces.move_to(rect)
    lab = MathTex(r"\Omega", font_size=60, color=LB).next_to(rect, LEFT, buff=0.3)
    return rect, faces, lab


def small_set(title, items, color=RLBLUE):
    words = VGroup(*[txt(s, size=30) for s in items]).arrange(RIGHT, buff=0.6)
    rect = SurroundingRectangle(words, buff=0.3, corner_radius=0.2, color=color, stroke_width=3)
    head = txt(title, size=28, color=GREY_B).next_to(rect, UP, buff=0.15)
    return VGroup(head, rect, words)


def prob_scale(y=-2.3):
    ln = NumberLine(x_range=[0, 1, 0.5], length=9, include_numbers=False, color=GREY_B).move_to([0, y, 0])
    nums = VGroup(*[txt(s, size=26).next_to(ln.n2p(v), DOWN, buff=0.2) for v, s in ((0, "0"), (0.5, "½"), (1, "1"))])
    words = VGroup(txt(label("impossible"), size=22, color=GREY_B).next_to(nums[0], DOWN, buff=0.12),
                   txt(label("certain"), size=22, color=GREY_B).next_to(nums[2], DOWN, buff=0.12))
    return ln, nums, words


def venn_icon(kind):
    a = Circle(radius=0.38, color=WHITE, stroke_width=2).shift(LEFT * 0.22)
    b = Circle(radius=0.38, color=WHITE, stroke_width=2).shift(RIGHT * 0.22)
    frame = Rectangle(width=1.5, height=1.05, color=GREY_B, stroke_width=2)
    style = dict(fill_color=HILITE, fill_opacity=0.85, stroke_width=0)
    if kind == "or":
        shade = Union(a, b, **style)
    elif kind == "and":
        shade = Intersection(a, b, **style)
    else:
        shade = Difference(frame, a, **style)
    return VGroup(shade, frame, a, b) if kind == "not" else VGroup(frame, shade, a, b)


class S10Omega(LectureScene):
    def construct(self):
        self.section_card(10)
        q1 = box(label("rain_tomorrow_q"), color=RLBLUE, width=4.4, height=1.1, size=30)
        q2 = VGroup(die_face(6, size=0.9), txt("?", size=44, weight=BOLD, color=HILITE)).arrange(RIGHT, buff=0.25)
        q2 = VGroup(RoundedRectangle(corner_radius=0.12, width=4.4, height=1.1, stroke_color=RLBLUE, stroke_width=3),
                    q2)
        q1.move_to([-3, 1.6, 0])
        q2.move_to([3, 1.6, 0])
        q2[1].move_to(q2[0])
        ln = NumberLine(x_range=[0, 1, 0.5], length=9, include_numbers=False, color=GREY_B).move_to([0, -1.4, 0])
        ends = VGroup(txt("0", size=28).next_to(ln.n2p(0), DOWN, buff=0.2),
                      txt("1", size=28).next_to(ln.n2p(1), DOWN, buff=0.2))
        marks = VGroup(*[txt("?", size=40, weight=BOLD, color=HILITE).move_to(q.get_bottom() + DOWN * 0.5)
                         for q in (q1, q2)])
        with self.say("10.1") as (tr, t):
            self.cue(tr, t, 1)
            self.play(FadeIn(q1, shift=DOWN * 0.2), run_time=0.7)
            self.cue(tr, t, 2)
            self.play(FadeIn(q2, shift=DOWN * 0.2), run_time=0.7)
            self.cue(tr, t, 3)
            self.play(Create(ln), FadeIn(ends), FadeIn(marks), run_time=0.8)
            self.play(marks[0].animate.move_to(ln.n2p(0.4) + UP * 0.45),
                      marks[1].animate.move_to(ln.n2p(1 / 6) + UP * 0.45), run_time=1.2)
        self.clear_all(run_time=0.5)

        rect, faces, lab = omega_set()
        name = txt(label("sample_space"), size=30, color=LB).next_to(rect, UP, buff=0.2)
        with self.say("10.2") as (tr, t):
            self.play(Create(rect), run_time=0.8)
            self.cue(tr, t, {"en": "For a die", "uz": "Kubikda"})
            self.play(LaggedStart(*[FadeIn(f, shift=DOWN * 1.2) for f in faces], lag_ratio=0.22), run_time=2.0)
            self.cue(tr, t, {"en": "We call", "uz": "Buni"})
            self.play(FadeIn(name), Write(lab), run_time=0.9)

        coin = small_set(label("coin"), [label("heads"), label("tails")]).move_to([-3.4, -1.9, 0])
        rain = small_set(label("tomorrow"), [label("rain"), label("no_rain")])
        rain.move_to([3.2, -1.9, 0])
        with self.say("10.3") as (tr, t):
            self.play(FadeIn(coin, shift=UP * 0.2), run_time=0.8)
            self.cue(tr, t, 2)
            self.play(FadeIn(rain, shift=UP * 0.2), run_time=0.8)
        self.clear_all()


class S10Event(LectureScene):
    def construct(self):
        rect, faces, lab = omega_set(y=1.6)
        self.add(rect, faces, lab)
        q = txt(label("even_number_q"), size=32, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.15)
        ring = Ellipse(width=4.4, height=1.6, color=HILITE, stroke_width=4).move_to([0, -0.7, 0])
        evens = VGroup(*[faces[n - 1].copy() for n in EVEN])      # A is a subset: Ω keeps its six
        a_lab = MathTex("A", font_size=52, color=HILITE).next_to(ring, LEFT, buff=0.3)
        ev_word = txt(label("event"), size=26, color=HILITE).next_to(ring, RIGHT, buff=0.3)
        with self.say("10.4") as (tr, t):
            self.cue(tr, t, {"en": "Will the die", "uz": "Kubik juft"})
            self.play(FadeIn(q), run_time=0.6)
            self.cue(tr, t, {"en": "We collect", "uz": "Javobi"})
            self.play(Create(ring), run_time=0.6)
            self.play(*[faces[n - 1].animate.set_color(HILITE) for n in EVEN], run_time=0.4)
            self.play(*[f.animate.move_to(ring.get_center() + RIGHT * (k - 1) * 1.25).set_color(HILITE)
                        for k, f in enumerate(evens)], run_time=1.4)
            self.cue(tr, t, {"en": "That set", "uz": "Mana shu"})
            self.play(Write(a_lab), FadeIn(ev_word), run_time=0.7)

        ln, nums, words = prob_scale(y=-2.6)
        p_om = MathTex(r"P(\Omega) = 1", font_size=40, color=LB).next_to(ln.n2p(1), UP, buff=0.35)
        with self.say("10.5") as (tr, t):
            self.play(Create(ln), FadeIn(nums), run_time=0.9)
            self.cue(tr, t, {"en": "Zero means", "uz": "Nol"})
            self.play(FadeIn(words[0]), Indicate(nums[0]), run_time=0.7)
            self.play(FadeIn(words[1]), Indicate(nums[2]), run_time=0.7)
            self.cue(tr, t, {"en": "The probability of omega", "uz": "Omeganing"})
            self.play(FadeIn(p_om, shift=DOWN * 0.2), Indicate(rect, color=RLBLUE, scale_factor=1.03), run_time=0.9)

        a, b = L["p_even"].split("/")
        p_a = MathTex(r"P(A) = \tfrac{3}{6} = \tfrac{" + a + "}{" + b + "}", font_size=38, color=HILITE)
        pin = Triangle(color=HILITE, fill_opacity=1).scale(0.14).rotate(PI).next_to(ln.n2p(0.5), UP, buff=0.05)
        p_a.next_to(pin, UP, buff=0.15)
        with self.say("10.6") as (tr, t):
            self.play(FadeIn(pin, shift=DOWN * 0.3), run_time=0.6)
            self.play(FadeIn(p_a), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(Indicate(p_a[0][-3:], color=HILITE), run_time=0.9)
        self.clear_all()


class S10Sets(LectureScene):
    def construct(self):
        rows = VGroup()
        for kind, word, sym in (("or", label("or"), r"A \cup B"), ("and", label("and"), r"A \cap B"),
                                ("not", label("not"), r"A^{c}")):
            r = VGroup(txt(f"«{word}»", size=32, weight=BOLD), MathTex(r"\rightarrow", font_size=44),
                       MathTex(sym, font_size=48, color=HILITE), venn_icon(kind))
            r.arrange(RIGHT, buff=0.55)
            rows.add(r)
        rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT).move_to([0, 0.1, 0])
        # line the columns up
        for col in range(4):
            x = max(r[col].get_center()[0] for r in rows)
            for r in rows:
                r[col].set_x(x)
        q = txt(label("why_sets_q"), size=34, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        with self.say("10.7") as (tr, t):
            self.play(FadeIn(q), run_time=0.6)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows], lag_ratio=0.45), run_time=2.6)
            self.cue(tr, t, 2)
            self.play(Indicate(VGroup(*[r[2] for r in rows]), color=HILITE), run_time=1.0)
        self.clear_all(run_time=0.5)

        classes = [label("cat"), label("dog"), label("bird")]
        probs = [0.7, 0.2, 0.1]                     # an illustration, not a model's real output
        assert abs(sum(probs) - 1) < 1e-12
        base, hk, xs = -2.2, 4.0, [-2.6, 0, 2.6]
        bars = VGroup(*[Rectangle(width=1.4, height=p * hk, stroke_width=0, fill_color=RLBLUE, fill_opacity=1)
                        .move_to([x, base + p * hk / 2, 0]) for x, p in zip(xs, probs)])
        names = VGroup(*[txt(c, size=28).next_to([x, base, 0], DOWN, buff=0.25) for x, c in zip(xs, classes)])
        vals = VGroup(*[txt(f"{p:.1f}", size=30, weight=BOLD).next_to(b, UP, buff=0.12) for b, p in zip(bars, probs)])
        floor = Line([-3.8, base, 0], [3.8, base, 0], color=GREY_B, stroke_width=2)
        head = txt(label("classifier_output"), size=32, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        tag = txt(label("illustration", 1), size=22, color=GREY_B).next_to(head, DOWN, buff=0.15)
        total = MathTex(r"0.7 + 0.2 + 0.1 = 1", font_size=40, color=HILITE).move_to([4.6, 1.4, 0])
        with self.say("10.8") as (tr, t):
            self.play(FadeIn(head), FadeIn(tag), Create(floor), FadeIn(names), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2), run_time=1.2)
            self.play(FadeIn(vals), run_time=0.5)
            self.play(Write(total), run_time=0.9)
        self.clear_all()


class S10HandsOn(LectureScene):
    def construct(self):
        rect, faces, lab = omega_set(y=0.2)
        task = pause_card([label("write_the_event_more_than_four")])
        task.scale(0.85).to_edge(UP, buff=SAFE + 0.15)
        with self.say("10.9") as (tr, t):
            self.play(FadeIn(rect), FadeIn(faces), FadeIn(lab), run_time=0.7)
            self.cue(tr, t, 1)
            self.play(FadeIn(task), run_time=0.7)
        self.hands_on()

        ring = Ellipse(width=3.2, height=1.5, color=HILITE, stroke_width=4).move_to([0, -1.9, 0])
        b_lab = MathTex("B", font_size=50, color=HILITE).next_to(ring, LEFT, buff=0.3)
        a, b = L["p_gt4"].split("/")
        p_b = MathTex(r"P(B) = \tfrac{2}{6} = \tfrac{" + a + "}{" + b + "}", font_size=42, color=HILITE)
        p_b.next_to(ring, RIGHT, buff=0.5)
        picked = VGroup(*[faces[n - 1].copy() for n in GT4])
        with self.say("10.10") as (tr, t):
            self.play(FadeOut(task), Create(ring), FadeIn(b_lab), run_time=0.7)
            self.play(*[faces[n - 1].animate.set_color(HILITE) for n in GT4], run_time=0.4)
            self.play(*[f.animate.move_to(ring.get_center() + RIGHT * (k - 0.5) * 1.25).set_color(HILITE)
                        for k, f in enumerate(picked)], run_time=1.2)
            self.cue(tr, t, 1)
            self.play(Write(p_b), run_time=1.0)
        self.clear_all(run_time=0.5)

        slots = VGroup(*[RoundedRectangle(corner_radius=0.15, width=3.2, height=1.4, stroke_color=RLBLUE,
                                          stroke_width=3) for _ in range(3)]).arrange(RIGHT, buff=0.5)
        nums = VGroup(*[txt(str(k), size=48, weight=BOLD, color=LB).move_to(s) for k, s in enumerate(slots, 1)])
        head = txt(label("3_rules"), size=40, weight=BOLD).next_to(slots, UP, buff=0.6)
        with self.say("10.11"):
            self.play(FadeIn(head), LaggedStart(*[Create(s) for s in slots], lag_ratio=0.25), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(n, scale=0.6) for n in nums], lag_ratio=0.25), run_time=0.9)
        self.clear_all()


SCENES = ["S10Omega", "S10Event", "S10Sets", "S10HandsOn"]
