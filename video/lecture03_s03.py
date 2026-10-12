"""Lecture 3, section 3 — the sample mean heads for the expectation: three runs of die rolls.

Every number on screen comes from N (capture_l03.py, unit-tested by test_l03.py):
runs (the figure script's three running means, same seed), die_mean, run1_gap, raffle_A, raffle_B.
"""
import textwrap

import numpy as np
from lecture03_kit import *

RUNS = N["runs"]
MU = N["die_mean"]
RUN_C = (LBLUE, RLGREEN, RLORANGE)
NMAX = len(RUNS[0]["curve"])
TICKS = [1, 10, 100, 1000]               # axis ticks on the log scale


SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def wrapped(text, width=24, **kw):
    """A long label as centred lines of at most `width` characters."""
    return VGroup(*[txt(l, **kw) for l in textwrap.wrap(text, width)]).arrange(DOWN, buff=0.12)


def run_axes():
    ax = Axes(x_range=[0, np.log10(NMAX), 1], y_range=[1, 6, 1], x_length=9.0, y_length=4.4, tips=False,
              axis_config={"color": GREY_B, "stroke_width": 2},
              x_axis_config={"include_ticks": False}, y_axis_config={"include_numbers": True, "font_size": 26})
    ax.move_to(DOWN * 0.3 + LEFT * 0.6)
    ticks = VGroup()
    for n in TICKS + [NMAX]:
        p = ax.c2p(np.log10(n), 1)
        ticks.add(Line(p + DOWN * 0.08, p + UP * 0.08, color=GREY_B, stroke_width=2),
                  MathTex(f"{n:,}".replace(",", "{,}"), font_size=26, color=GREY_B).next_to(p, DOWN, buff=0.18))
    xl = txt(label("rolls_so_far"), size=24, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.6)
    yl = MathTex(r"\bar{x}", font_size=40, color=GREY_B).next_to(ax.y_axis, UP, buff=0.15)
    return ax, VGroup(ticks, xl, yl)


def run_curve(ax, i):
    pts = [ax.c2p(np.log10(n), m) for n, m in enumerate(RUNS[i]["curve"], 1)]
    return VMobject(stroke_color=RUN_C[i], stroke_width=3).set_points_as_corners(pts)


def mu_line(ax):
    line = DashedLine(ax.c2p(0, MU), ax.c2p(np.log10(NMAX), MU), color=RLRED, stroke_width=3)
    tag = MathTex(rf"E[X] = {dec(MU)}", font_size=34, color=RLRED).next_to(line, RIGHT, buff=0.15)
    tag.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.05)
    return line, tag


def readings(ax, n, key, places, side=RIGHT):
    """Dots on the three curves at n rolls, with their values beside them."""
    dots, tags = VGroup(), VGroup()
    for i, r in enumerate(RUNS):
        p = ax.c2p(np.log10(n), r["curve"][n - 1])
        dots.add(Dot(p, radius=0.08, color=RUN_C[i]))
        t = MathTex(dec(r[key], places), font_size=30, color=RUN_C[i])
        t.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.04)
        tags.add(t)
    tags.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    return dots, tags


class S03Running(LectureScene):
    def construct(self):
        self.section_card(3)
        xbar = MathTex(r"\bar{x}", font_size=96, color=LBLUE)
        rolled = VGroup(*[die_face(k, 0.55) for k in (4, 1, 6, 3)]).arrange(RIGHT, buff=0.15)
        left = VGroup(xbar, rolled, wrapped(label("from_the_data_we_have"), size=28, color=GREY_B)).arrange(DOWN, buff=0.35)
        ex = MathTex(rf"E[X] = {dec(MU)}", font_size=72, color=HILITE)
        right = VGroup(ex, die_face(6, 0.8, color=GREY_B),
                       wrapped(label("fixed_before_any_data_exists"), size=28, color=GREY_B)).arrange(DOWN, buff=0.35)
        VGroup(left, right).arrange(RIGHT, buff=2.4).move_to(UP * 0.1)
        with self.say("3.1") as (tr, t):
            self.play(FadeIn(left, shift=RIGHT * 0.2), run_time=0.9)
            self.cue(tr, t, {"en": "The expectation is", "uz": "Kutilma esa"})
            self.play(FadeIn(right, shift=LEFT * 0.2), run_time=0.9)
        self.clear_all()

        ax, deco = run_axes()
        line, tag = mu_line(ax)
        curves = [run_curve(ax, i) for i in range(3)]
        with self.say("3.2") as (tr, t):
            self.play(Create(ax), FadeIn(deco), run_time=0.9)
            self.play(Create(line), FadeIn(tag), run_time=0.6)
            self.cue(tr, t, {"en": "We do this three times", "uz": "Buni uch marta"})
            self.play(*[Create(c, rate_func=linear) for c in curves], run_time=3.0)

        d10, t10 = readings(ax, 10, "after_10", 2)
        t10.next_to(d10, UP, buff=0.4).shift(RIGHT * 0.3)
        mark10 = DashedLine(ax.c2p(1, 1), ax.c2p(1, 6), color=GREY_D, stroke_width=2)
        with self.say("3.3") as (tr, t):
            self.play(Create(mark10), FadeIn(d10, scale=1.5), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(x) for x in t10], lag_ratio=0.3), run_time=1.2)
            self.cue(tr, t, {"en": "They disagree", "uz": "Ular bir-biridan"})
            self.play(Indicate(VGroup(*[x[1:] for x in t10]), scale_factor=1.1, color=WHITE), run_time=0.8)

        d2k, t2k = readings(ax, NMAX, "after_2000", 2)
        t2k.next_to(d2k, UP, buff=0.55).shift(LEFT * 0.5)
        with self.say("3.4") as (tr, t):
            self.play(FadeIn(d2k, scale=1.5), LaggedStart(*[FadeIn(x) for x in t2k], lag_ratio=0.3), run_time=1.4)
            self.cue(tr, t, {"en": "All three have", "uz": "Uchalasi ham"})
            self.play(Indicate(line, color=RLRED), Indicate(tag[1:], color=RLRED), run_time=0.9)

        nxt = txt(label("how_fast_lecture_5"), size=28, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.25)
        with self.say("3.5") as (tr, t):
            self.play(Indicate(VGroup(*curves), color=WHITE, scale_factor=1.0), run_time=0.9)
            self.cue(tr, t, {"en": "How fast", "uz": "Bu qanchalik tez"})
            self.play(FadeIn(nxt, shift=DOWN * 0.2), run_time=0.7)
        self.clear_all()

        # AI: a batch's average loss estimates the expected loss; a bigger batch, a tighter estimate
        rng = np.random.default_rng(8)

        def batch(n, w, h):
            box = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=GREY_B, stroke_width=2)
            pts = rng.uniform([-w / 2 + 0.15, -h / 2 + 0.15], [w / 2 - 0.15, h / 2 - 0.15], size=(n, 2))
            return VGroup(box, *[Dot([x, y, 0], radius=0.05, color=GREY_B) for x, y in pts])

        def spread(half, color):
            nl = Line(LEFT * 2.2, RIGHT * 2.2, color=GREY_D, stroke_width=2)
            truth = Line(UP * 0.35, DOWN * 0.35, color=RLRED, stroke_width=4)
            band = Rectangle(width=2 * half, height=0.3, stroke_width=0, fill_color=color, fill_opacity=0.55)
            return VGroup(nl, band, truth)

        small, big = batch(6, 1.4, 1.2), batch(60, 3.0, 1.8)
        cols = VGroup(VGroup(small, txt(label("small_batch"), size=26), spread(1.7, RLORANGE)).arrange(DOWN, buff=0.35),
                      VGroup(big, txt(label("big_batch"), size=26), spread(0.45, RLGREEN)).arrange(DOWN, buff=0.35))
        cols.arrange(RIGHT, buff=1.6).scale(1.25).move_to(DOWN * 0.2)
        head = txt(f"{label('batch_average')}  ≈  E[{label('error')}]", size=32, weight=BOLD, color=HILITE)
        head.to_edge(UP, buff=SAFE + 0.35)
        note = info(label("illustration"))
        with self.say("3.6") as (tr, t):
            self.play(FadeIn(head), FadeIn(note), run_time=0.7)
            self.play(FadeIn(cols[0]), run_time=0.8)
            self.cue(tr, t, {"en": "The bigger the batch", "uz": "Toʻplam qanchalik"})
            self.play(FadeIn(cols[1]), run_time=0.8)
        self.clear_all()


class S03HandsOn(LectureScene):
    def construct(self):
        ax, deco = run_axes()
        VGroup(ax, deco).scale(0.62).move_to([3.4, -0.6, 0])
        line, tag = mu_line(ax)
        tag.scale(0.75).next_to(line, UP, buff=0.08).align_to(line, RIGHT)
        c1 = run_curve(ax, 0)
        r = RUNS[0]
        dots = VGroup(*[Dot(ax.c2p(np.log10(n), r["curve"][n - 1]), radius=0.08, color=HILITE) for n in (10, NMAX)])
        s10, s2k = "10".translate(SUB), str(NMAX).translate(SUB)
        card = pause_card([f"x̄{s10} = {dec(r['after_10'])},   E[X] = {dec(MU)}",
                           f"|x̄{s10} − E[X]| = ?",
                           f"|x̄{s2k} − E[X]| = ?"]).move_to([-3.3, 0.6, 0])
        with self.say("3.7") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(card, shift=UP * 0.2), FadeIn(ax), FadeIn(deco), Create(line), FadeIn(tag),
                      Create(c1), FadeIn(dots), run_time=1.2)
        self.hands_on()

        g = N["run1_gap"]
        a10 = MathTex(rf"|{dec(r['after_10'])} - {dec(MU)}| = {dec(g['after_10'])}", font_size=46)
        a2k = MathTex(rf"|{dec(r['after_2000'], 3)} - {dec(MU)}| = {dec(g['after_2000'], 3)}", font_size=46, color=HILITE)
        ans = VGroup(a10, a2k).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to([-3.3, -0.2, 0])
        with self.say("3.8") as (tr, t):
            self.play(FadeOut(card), run_time=0.4)
            self.play(Write(a10), Indicate(dots[0], color=WHITE, scale_factor=1.8), run_time=1.0)
            self.cue(tr, t, {"en": "After two thousand, only", "uz": "Ikki ming tashlashdan keyin bor-yoʻgʻi"})
            self.play(Write(a2k), Indicate(dots[1], color=WHITE, scale_factor=1.8), run_time=1.0)
        self.clear_all()

        # same expectation, different spread: the two raffles of the next section
        lo, hi = -40, 420
        rows = VGroup()
        for key, name in (("raffle_A", label("raffle_a")), ("raffle_B", label("raffle_b"))):
            pmf = {int(k): v[0] / v[1] for k, v in N[key]["pmf"].items()}
            nl = NumberLine(x_range=[lo, hi, 100], length=9, color=GREY_B, include_numbers=False)
            dots = VGroup(*[Dot(nl.n2p(x), radius=0.07 + 0.3 * np.sqrt(p), color=LBLUE, fill_opacity=0.85)
                            for x, p in pmf.items()])
            xs = sorted(pmf)
            # values closer than a dot's width on this scale: the larger one is labelled above its dot
            vals = VGroup(*[MathTex(str(x), font_size=28, color=GREY_B)
                            .next_to(nl.n2p(x), UP if i and x - xs[i - 1] < 40 else DOWN, buff=0.4)
                            for i, x in enumerate(xs)])
            mean = Triangle(color=HILITE, fill_opacity=1).scale(0.12).rotate(PI).next_to(nl.n2p(N[key]["mean"]), UP, buff=0.85)
            rows.add(VGroup(txt(name, size=28, weight=BOLD).next_to(nl, LEFT, buff=0.4), nl, dots, vals, mean))
        rows.arrange(DOWN, buff=1.2).move_to(DOWN * 0.3)
        same = txt(f"{label('same_mean')}:  E[X] = {N['raffle_A']['mean']:.2f}".replace("-", "−"), size=30, color=HILITE)
        same.to_edge(UP, buff=SAFE + 0.4)
        q = txt("?", size=60, weight=BOLD, color=HILITE).next_to(same, RIGHT, buff=0.4)
        with self.say("3.9") as (tr, t):
            self.play(FadeIn(rows[0]), FadeIn(rows[1]), run_time=1.0)
            self.play(FadeIn(same), run_time=0.6)
            self.cue(tr, t, {"en": "We measure that", "uz": "Buni keyingi"})
            self.play(FadeIn(q, scale=1.4), run_time=0.6)
        self.clear_all()


SCENES = ["S03Running", "S03HandsOn"]
