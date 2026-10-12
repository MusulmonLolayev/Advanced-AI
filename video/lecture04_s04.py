"""Lecture 4, section 4 — where random numbers come from: a uniform u run backwards through the CDF.

x = -ln(1 - u) / λ: u = 0.5 gives 1.73 minutes, and 50.5 % of the figure script's 20,000 simulated gaps
are shorter; u = 0.9 gives 5.76 (the pause). The histogram is the same 20,000 gaps (N["hist"]). The u
dots that map onto the axis are a picture of the mapping, not data. Every number shown comes from N.
"""
from math import exp, log

from lecture04_kit import *

RATE = N["rate"]
U_HALF, X_HALF = N["u_half"], N["x_half"]
U_TASK, X_TASK = N["u_task"], N["x_task"]
HIST = N["hist"]["0.25"]
X_MAX = round(N["pdf_curve"][-1][0])
EXP_C, U_C = LBLUE, HILITE


def F(x):
    return 1 - exp(-RATE * x)


def inv(u):
    return -log(1 - u) / RATE


def cdf_panel(center=ORIGIN, x_len=8.0, y_len=3.8):
    """Axes placed first, then the CDF on them (plotting before moving leaves the curve behind)."""
    ax = Axes(x_range=[0, X_MAX, 2], y_range=[0, 1, 0.25], x_length=x_len, y_length=y_len, tips=False,
              axis_config={"color": GREY_B, "stroke_width": 2, "include_numbers": True, "font_size": 22})
    ax.move_to(center)
    curve = ax.plot(F, x_range=[0, X_MAX], color=EXP_C, stroke_width=5)
    fl = MathTex("F(x)", font_size=34, color=EXP_C).next_to(ax.c2p(X_MAX, F(X_MAX)), UP, buff=0.2)
    return ax, curve, fl


def backwards(ax, u, color=U_C):
    """u on the vertical axis → across to the curve → down to x."""
    x = inv(u)
    dot_u = Dot(ax.c2p(0, u), radius=0.09, color=color)
    across = DashedLine(ax.c2p(0, u), ax.c2p(x, u), color=color, stroke_width=3)
    down = Arrow(ax.c2p(x, u), ax.c2p(x, 0), buff=0, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.12)
    dot_x = Dot(ax.c2p(x, 0), radius=0.09, color=color)
    return dot_u, across, down, dot_x


class S04Uniform(LectureScene):
    def construct(self):
        self.section_card(4)
        title = txt(label("a_uniform_number"), size=34, weight=BOLD, color=U_C).to_edge(UP, buff=SAFE + 0.4)
        line = NumberLine(x_range=[0, 1, 0.25], length=10, include_numbers=True, font_size=26, color=GREY_B)
        line.move_to(DOWN * 0.2)
        sym = MathTex(r"u \in [0, 1]", font_size=48, color=U_C).next_to(title, DOWN, buff=0.4)
        # where the draws land: an evenly scattered picture, not real draws
        us = [(k * 0.6180339887) % 1 for k in range(1, 25)]
        drops = VGroup(*[Dot(line.n2p(u) + UP * 0.25, radius=0.08, color=U_C) for u in us])
        rest = txt(label("everything_else_is_built_from_it"), size=28, color=GREY_B).next_to(line, DOWN, buff=0.9)
        note = info(label("illustration"))
        with self.say("4.1") as (tr, t):
            self.play(FadeIn(title), Create(line), run_time=0.8)
            self.play(Write(sym), LaggedStart(*[FadeIn(d, shift=DOWN * 0.5) for d in drops], lag_ratio=0.05),
                      FadeIn(note), run_time=1.3)
            self.cue(tr, t, {"en": "Everything else", "uz": "Qolgan hamma narsa"})
            self.play(FadeIn(rest, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S04Inverse(LectureScene):
    def construct(self):
        ax, curve, fl = cdf_panel(DOWN * 0.6 + LEFT * 1.8, x_len=7.4)
        xl = txt(label("minutes_to_next_customer"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.5)
        head = txt(label("run_the_cdf_backwards"), size=34, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        dot_u, across, down, dot_x = backwards(ax, U_HALF)
        u_lab = MathTex("u", font_size=36, color=U_C).next_to(dot_u, UR, buff=0.08)
        x_lab = MathTex("x", font_size=36, color=U_C).next_to(dot_x, DOWN, buff=0.45)
        with self.say("4.2") as (tr, t):
            self.play(FadeIn(head), Create(ax), Create(curve), FadeIn(fl), FadeIn(xl), run_time=1.0)
            self.cue(tr, t, {"en": "We take a uniform number u", "uz": "Tekis son yu ni olamiz"})
            self.play(FadeIn(dot_u, scale=1.6), FadeIn(u_lab), run_time=0.5)
            self.cue(tr, t, {"en": "find the x", "uz": "eks ni topamiz"})
            self.play(Create(across), run_time=0.6)
            self.play(GrowArrow(down), FadeIn(dot_x), FadeIn(x_lab), run_time=0.6)

        side = RIGHT * 4.75
        formula = MathTex(r"x = -\frac{\ln(1 - u)}{\lambda}", font_size=46).move_to(side + UP * 0.9)
        with self.say("4.3"):
            self.play(Write(formula), run_time=1.0)

        plug = MathTex(rf"u = {dec(U_HALF)},\ \ \lambda = {dec(RATE)}", font_size=36).next_to(formula, DOWN, buff=0.4)
        res = MathTex(rf"x \approx {dec(X_HALF)}", font_size=44, color=U_C).next_to(plug, DOWN, buff=0.3)
        half = MathTex(rf"P(X < {dec(X_HALF)}) \approx {pct(N['median_gap_check'])}".replace("%", r"\%"),
                       font_size=34, color=EXP_C).next_to(res, DOWN, buff=0.45)
        sims = tagged(f"{N['n_gaps']:,}", label("simulated_gaps"), size=22, color=GREY_B).next_to(half, DOWN, buff=0.15)
        if sims.width > 3.6:                       # the Uzbek words are longer
            sims.scale_to_fit_width(3.6).next_to(half, DOWN, buff=0.15)
        sims.shift(LEFT * max(0, sims.get_right()[0] - (config.frame_width / 2 - SAFE - 0.2)))
        x_val = MathTex(dec(X_HALF), font_size=30, color=U_C).move_to(x_lab)
        with self.say("4.4") as (tr, t):
            self.play(Write(plug), run_time=0.7)
            self.play(Write(res), Transform(x_lab, x_val), run_time=0.8)
            self.cue(tr, t, {"en": "And indeed", "uz": "Haqiqatan ham"})
            self.play(FadeIn(half), FadeIn(sims), run_time=0.8)
        self.clear_all()


class S04Histogram(LectureScene):
    def construct(self):
        # many uniform u's pushed through the formula pile up as the exponential
        ax = Axes(x_range=[0, X_MAX, 2], y_range=[0, 0.45, 0.1], x_length=8.6, y_length=3.4, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2, "include_numbers": True, "font_size": 22})
        ax.move_to(DOWN * 1.0 + RIGHT * 0.8)
        ucol = NumberLine(x_range=[0, 1, 0.5], length=3.4, rotation=PI / 2, include_numbers=True, font_size=22,
                          color=U_C, label_direction=LEFT).move_to(ax.get_left() + LEFT * 1.3)
        ucol.align_to(ax, DOWN)
        u_name = MathTex("u", font_size=36, color=U_C).next_to(ucol, UP, buff=0.2)
        us = [(k * 0.6180339887) % 1 for k in range(1, 31)]
        us = [u for u in us if inv(u) < X_MAX]
        src = VGroup(*[Dot(ucol.n2p(u), radius=0.06, color=U_C) for u in us])
        dst = VGroup(*[Dot(ax.c2p(inv(u), 0), radius=0.06, color=U_C) for u in us])
        w = HIST["width"]
        bars = VGroup(*[Rectangle(width=ax.x_axis.unit_size * w * 0.92, height=max(h * ax.y_axis.unit_size, 1e-3),
                                  stroke_width=0, fill_color=EXP_C, fill_opacity=0.55)
                        .move_to(ax.c2p(e + w / 2, h / 2)) for e, h in zip(HIST["edges"], HIST["heights"])])
        curve = ax.plot(lambda x: RATE * exp(-RATE * x), x_range=[0, X_MAX], color=EXP_C, stroke_width=5)
        sims = tagged(f"{N['n_gaps']:,}", label("simulated_gaps"), size=22, color=GREY_B)
        sims.next_to(ax, UP, buff=0.15).align_to(ax, RIGHT)
        formula = MathTex(r"x = -\frac{\ln(1 - u)}{\lambda}", font_size=40).to_edge(UP, buff=SAFE + 0.35)
        note = info(label("illustration"))
        with self.say("4.5") as (tr, t):
            self.play(FadeIn(formula), Create(ax), Create(ucol), FadeIn(u_name), FadeIn(src), FadeIn(note),
                      run_time=1.0)
            self.play(LaggedStart(*[Transform(s, d) for s, d in zip(src, dst)], lag_ratio=0.04), run_time=1.6)
            self.cue(tr, t, {"en": "their histogram", "uz": "ularning gistogrammasi"})
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.01), FadeIn(sims), run_time=1.0)
            self.play(Create(curve), run_time=0.8)
        self.clear_all()

        # where AI draws its randomness
        u = VGroup(Circle(radius=0.55, color=U_C, stroke_width=4), MathTex("u", font_size=48, color=U_C))
        u.move_to(LEFT * 4.2)
        uses = VGroup(*[txt(k, size=28) for k in (label("dropout_masks"), label("shuffled_mini_batches"),
                                                  label("data_augmentation"), label("diffusion_noise"))])
        uses.arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to(RIGHT * 2.0)
        arrows = VGroup(*[Arrow(u.get_right(), m.get_left(), buff=0.2, color=GREY_B, stroke_width=3) for m in uses])
        head = txt(label("sampling"), size=34, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        with self.say("4.6") as (tr, t):
            self.play(FadeIn(head), FadeIn(u), run_time=0.6)
            self.cue(tr, t, {"en": "dropout masks", "uz": "dropout niqoblari"})
            self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(m)) for a, m in zip(arrows, uses)],
                                  lag_ratio=0.35), run_time=1.8)
        self.clear_all()


class S04HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"u = {dec(U_TASK)},   λ = {dec(RATE)}", "x = −ln(1 − u) / λ = ?"])
        card.to_edge(UP, buff=SAFE + 0.3)
        with self.say("4.7"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        ax, curve, fl = cdf_panel(DOWN * 0.6 + LEFT * 1.8, x_len=7.4)
        xl = txt(label("minutes_to_next_customer"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.5)
        dot_u, across, down, dot_x = backwards(ax, U_TASK)
        calc = MathTex(rf"x = -\frac{{\ln {dec(1 - U_TASK)}}}{{{dec(RATE)}}} \approx {dec(X_TASK)}", font_size=44,
                       color=U_C).move_to(RIGHT * 4.75 + UP * 0.9)
        big = txt(label("a_large_u_a_long_gap"), size=26, color=GREY_B).next_to(calc, DOWN, buff=0.45)
        with self.say("4.8") as (tr, t):
            self.play(Create(ax), Create(curve), FadeIn(fl), FadeIn(xl), run_time=0.8)
            self.play(FadeIn(dot_u), Create(across), GrowArrow(down), FadeIn(dot_x), run_time=1.0)
            self.play(Write(calc), run_time=0.8)
            self.cue(tr, t, {"en": "A large u", "uz": "Katta yu"})
            self.play(FadeIn(big), run_time=0.5)
        self.clear_all()

        s, n = N["beta"]["first"]["successes"], N["beta"]["first"]["n"]
        p = VGroup(txt(label("pastries_short"), size=32, color=GREY_B),
                   MathTex(rf"p = {dec(s / n)}", font_size=56, color=HILITE),
                   txt("?", size=64, weight=BOLD, color=HILITE)).arrange(RIGHT, buff=0.4)
        with self.say("4.9") as (tr, t):
            self.play(FadeIn(p[0]), Write(p[1]), run_time=0.8)
            self.cue(tr, t, {"en": "Where did that number", "uz": "Bu son qayerdan"})
            self.play(FadeIn(p[2], scale=1.4), run_time=0.5)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S04Uniform", "S04Inverse", "S04Histogram", "S04HandsOn"]
