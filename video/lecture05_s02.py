"""Lecture 5, section 2 — the standard error: how far an average typically sits from the truth.

SE = σ/√n for the coffee shop's σ = 0.663 (N["sigma"]); the curve and its read-offs at n = 10, 40, 160,
30 and 640 are N["se_curve"] and N["se"]. The one-customer bars are the pastry distribution and the
average-of-30 bars are its exact sampling distribution (N["sampling"]["30"]). Every number shown comes from N.
"""
from math import sqrt

from lecture05_kit import *

SIGMA, MU = N["sigma"], N["mu"]
SE = N["se"]
PASTRY = N["pastry"]
S30 = N["sampling"]["30"]
N30 = N["n_customers"]
CURVE = N["se_curve"]                        # [[n, SE]], n = 1 … 200
LO, MID, HI = N["n_se"]                      # 10, 40, 160
TASK = N["n_se_task"]                        # 640
SE_C, ONE_C = HILITE, LBLUE


def se3(x):
    """An SE as the narration reads it, three decimals kept: 0.210, 0.105, 0.052."""
    return f"{x:.3f}"


def pmf_panel(means, probs, x0, x1, width, color, base=-2.2, height=2.6, vmax=None):
    """Bars at their values on a value axis from x0 to x1 (screen units), with the mean marked."""
    vmax = vmax or max(probs)
    lo, hi = 0.0, 2.0                           # pastries per order, and their averages, live in [0, 2]
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    bars = VGroup(*[Rectangle(width=width, height=max(p / vmax * height, 1e-3), stroke_width=0, fill_color=color,
                              fill_opacity=1).move_to([sx(m), base + p / vmax * height / 2, 0])
                    for m, p in zip(means, probs) if p > 1e-5])
    floor = Line([x0 - 0.2, base, 0], [x1 + 0.2, base, 0], color=GREY_B, stroke_width=2)
    ticks = VGroup(*[MathTex(str(v), font_size=26, color=GREY_B).next_to([sx(v), base, 0], DOWN, buff=0.15)
                     for v in (0, 1, 2)])
    return VGroup(bars, floor, ticks), sx


def se_axes(x_len=8.6, y_len=4.2):
    return Axes(x_range=[0, 200, 40], y_range=[0, 0.7, 0.1], x_length=x_len, y_length=y_len, tips=False,
                axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 24, "include_numbers": True},
                y_axis_config={"decimal_number_config": {"num_decimal_places": 1}})


def se_curve(ax, color=SE_C):
    return ax.plot_line_graph([n for n, _ in CURVE], [s for _, s in CURVE], add_vertex_dots=False,
                              line_color=color, stroke_width=4)["line_graph"]


def read_off(ax, n, color=SE_C, side=UR):
    y = SE[str(n)]
    d = Dot(ax.c2p(n, y), radius=0.08, color=color)
    guide = DashedLine(ax.c2p(n, 0), ax.c2p(n, y), color=GREY_C, stroke_width=2)
    t = MathTex(rf"n = {n}:\ {se3(y)}", font_size=30, color=color).next_to(d, side, buff=0.12)
    t.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.05)
    return VGroup(guide, d, t)


class S02StandardError(LectureScene):
    def construct(self):
        self.section_card(2)
        se_def = MathTex(r"\mathrm{SE} = \frac{\sigma}{\sqrt{n}}", font_size=72, color=SE_C)
        name = txt(label("standard_error"), size=34, weight=BOLD, color=SE_C).next_to(se_def, UP, buff=0.4)
        VGroup(name, se_def).move_to(UP * 0.3)
        with self.say("2.1") as (tr, t):
            self.play(FadeIn(name), run_time=0.5)
            self.cue(tr, t, {"en": "sigma divided by", "uz": "sigmani en ning"})
            self.play(Write(se_def), run_time=1.0)
        self.play(VGroup(name, se_def).animate.scale(0.6).to_edge(UP, buff=SAFE + 0.25), run_time=0.5)

        # one customer against an average of thirty: the same shop, very different spreads
        vals = list(range(len(PASTRY)))
        left, sx_l = pmf_panel(vals, PASTRY, -6.0, -1.4, 0.55, ONE_C)
        right, sx_r = pmf_panel(S30["means"], S30["probs"], 1.2, 5.8, 0.06, SE_C)
        l_name = txt(label("one_customer"), size=26, color=ONE_C).next_to(left, UP, buff=0.35)
        r_name = VGroup(txt(label("average_of_the_orders"), size=26, color=SE_C),
                        MathTex(rf"n = {N30}", font_size=30, color=SE_C)).arrange(RIGHT, buff=0.2)
        r_name.next_to(right, UP, buff=0.35)
        sig_arrow = DoubleArrow([sx_l(MU - SIGMA), -2.55, 0], [sx_l(MU + SIGMA), -2.55, 0], buff=0, color=ONE_C,
                                stroke_width=4).shift(DOWN * 0.5)
        sig_t = MathTex(rf"\sigma = {se3(SIGMA)}", font_size=32, color=ONE_C).next_to(sig_arrow, DOWN, buff=0.1)
        se_arrow = DoubleArrow([sx_r(MU - SE[str(N30)]), -2.55, 0], [sx_r(MU + SE[str(N30)]), -2.55, 0], buff=0,
                               color=SE_C, stroke_width=4).shift(DOWN * 0.5)
        se_t = MathTex(rf"\mathrm{{SE}} = \tfrac{{{se3(SIGMA)}}}{{\sqrt{{{N30}}}}} = {se3(SE[str(N30)])}", font_size=32,
                       color=SE_C).next_to(se_arrow, DOWN, buff=0.1)
        with self.say("2.2") as (tr, t):
            self.play(FadeIn(left), FadeIn(l_name), run_time=0.8)
            self.cue(tr, t, {"en": "the standard error says", "uz": "standart xato esa"})
            self.play(FadeIn(right), FadeIn(r_name), run_time=0.8)

        steadier = tagged(f"{round(N['steadier'])}×", label("steadier"), size=32, weight=BOLD, color=SE_C)
        steadier.move_to([3.6, 3.1, 0])
        with self.say("2.3") as (tr, t):
            self.play(GrowFromCenter(sig_arrow), FadeIn(sig_t), run_time=0.8)
            self.cue(tr, t, {"en": "but the average of thirty", "uz": "lekin oʻttizta"})
            self.play(GrowFromCenter(se_arrow), Write(se_t), run_time=0.9)
            self.cue(tr, t, {"en": "five times steadier", "uz": "besh marta"})
            self.play(FadeIn(steadier, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S02Curve(LectureScene):
    def construct(self):
        ax = se_axes().move_to(DOWN * 0.2 + RIGHT * 0.4)
        xl = txt(label("orders_axis"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = MathTex(r"\mathrm{SE}", font_size=32, color=GREY_B).next_to(ax.y_axis, UP, buff=0.15)
        curve = se_curve(ax)
        marks = [read_off(ax, LO, side=UR), read_off(ax, MID, side=UR), read_off(ax, HI, side=UP)]
        with self.say("2.4") as (tr, t):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.play(Create(curve), run_time=1.0)
            self.cue(tr, t, {"en": "At ten orders", "uz": "Oʻnta buyurtmada"})
            self.play(FadeIn(marks[0]), run_time=0.5)
            self.cue(tr, t, {"en": "at forty", "uz": "qirqtada"})
            self.play(FadeIn(marks[1]), run_time=0.5)
            self.cue(tr, t, {"en": "at one hundred", "uz": "bir yuz oltmishtada"})
            self.play(FadeIn(marks[2]), run_time=0.5)

        # each step: four times the data, half the error
        steps = VGroup()
        for a, b in ((LO, MID), (MID, HI)):
            # high above the dots, clear of their read-off labels
            arc = CurvedArrow(ax.c2p(a, SE[str(a)]) + UP * 1.45, ax.c2p(b, SE[str(b)]) + UP * 1.45, angle=-PI / 5,
                              color=LBLUE, stroke_width=3)
            steps.add(arc)
        rule = VGroup(MathTex(r"n \times 4", font_size=40, color=LBLUE), txt(label("four_times_the_data"), size=24, color=LBLUE),
                      MathTex(rf"\mathrm{{SE}} \times {dec(SE[str(MID)] / SE[str(LO)])}", font_size=40, color=SE_C),
                      txt(label("half_the_error"), size=24, color=SE_C)).arrange_in_grid(2, 2, buff=(0.3, 0.2),
                                                                                      col_alignments="rl")
        rule.to_corner(UR, buff=SAFE + 0.4)
        never = txt(label("never_steep_again"), size=26, color=GREY_A).next_to(rule, DOWN, buff=0.35)
        with self.say("2.5") as (tr, t):
            self.play(LaggedStart(*[Create(s) for s in steps], lag_ratio=0.4), FadeIn(rule), run_time=1.2)
            self.cue(tr, t, {"en": "There is no sample size", "uz": "Egri chiziq hech"})
            self.play(FadeIn(never), run_time=0.6)

        # accuracy at quadratic cost: a tenth of the error needs a hundred times the data
        cost = N["tenfold_error_cost"]
        quad = VGroup(txt(label("accuracy_at_quadratic_cost"), size=28, weight=BOLD, color=HILITE),
                      MathTex(rf"\mathrm{{SE}} \div {round(sqrt(cost))} \;\Longrightarrow\; n \times {cost}", font_size=46,
                              color=HILITE)).arrange(DOWN, buff=0.25)
        if quad.width > 6.4:
            quad.scale_to_fit_width(6.4)
        quad.next_to(never, DOWN, buff=0.45).to_edge(RIGHT, buff=SAFE + 0.3)
        quad.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.12)
        with self.say("2.6") as (tr, t):
            self.play(FadeIn(quad, shift=UP * 0.2), run_time=0.8)
        self.clear_all()

        # AI: halving the error around a reported accuracy takes four times the test set (a picture)
        head = txt(label("reported_accuracy"), size=32, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.4)
        half = SE[str(MID)] / SE[str(LO)]
        sizes = (1, 4)
        rows = VGroup()
        for k, n_mult in enumerate(sizes):
            cells = VGroup(*[Square(0.22, stroke_width=0, fill_color=GREY_B, fill_opacity=0.8)
                             for _ in range(12 * n_mult)]).arrange_in_grid(n_mult, 12, buff=0.05)
            err = 1.6 * (half if k else 1.0)
            bar = VGroup(Line(LEFT * err, RIGHT * err, color=SE_C, stroke_width=5),
                         Line(UP * 0.18, DOWN * 0.18, color=SE_C, stroke_width=5).shift(LEFT * err),
                         Line(UP * 0.18, DOWN * 0.18, color=SE_C, stroke_width=5).shift(RIGHT * err),
                         Dot(radius=0.09, color=WHITE))
            rows.add(VGroup(VGroup(txt(label("test_set"), size=22, color=GREY_B), cells).arrange(DOWN, buff=0.12),
                            bar).arrange(RIGHT, buff=1.0))
        rows.arrange(DOWN, buff=0.7, aligned_edge=LEFT).move_to(DOWN * 0.3)
        mult = MathTex(r"\times 4", font_size=40, color=LBLUE).next_to(rows[1][0], LEFT, buff=0.3)
        err_l = txt(label("the_error_around_it"), size=22, color=SE_C).next_to(rows[0][1], UP, buff=0.2)
        note = info(label("illustration"))
        with self.say("2.7") as (tr, t):
            self.play(FadeIn(head), FadeIn(rows[0]), FadeIn(err_l), FadeIn(note), run_time=0.9)
            self.cue(tr, t, {"en": "halving the error", "uz": "xatoni ikki baravar"})
            self.play(FadeIn(rows[1]), FadeIn(mult), run_time=0.9)
        self.clear_all()


class S02HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"n = {TASK}", label("standard_error_q")])
        with self.say("2.8"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        # the answer: one more quadrupling halves the error once more
        ax = se_axes().move_to(DOWN * 0.4 + LEFT * 1.6).scale(0.85)
        curve = se_curve(ax)
        mark = read_off(ax, HI, side=UP)
        calc = VGroup(MathTex(rf"{TASK} = {HI} \times {TASK // HI}", font_size=42),
                      MathTex(rf"\mathrm{{SE}} = \tfrac{{{se3(SE[str(HI)])}}}{{2}} \approx {se3(SE[str(TASK)])}",
                              font_size=46, color=SE_C)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        calc.to_edge(RIGHT, buff=SAFE + 0.4).shift(UP * 0.6)
        assert TASK // HI == 4 and abs(SE[str(TASK)] - SE[str(HI)] / 2) < 1e-12
        with self.say("2.9") as (tr, t):
            self.play(FadeIn(ax), Create(curve), FadeIn(mark), run_time=0.9)
            self.play(Write(calc[0]), run_time=0.7)
            self.cue(tr, t, {"en": "half the error", "uz": "xato ikki baravar"})
            self.play(Write(calc[1]), run_time=0.8)
        self.clear_all()

        # the next question: we know the spread of the average — what shape does it have?
        bars, sx = pmf_panel(S30["means"], S30["probs"], -3.6, 3.6, 0.09, SE_C, base=-2.3, height=3.4)
        q = txt(label("its_shape_q"), size=40, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.6)
        n_t = MathTex(rf"n = {N30}", font_size=34, color=GREY_B).next_to(q, DOWN, buff=0.3)
        with self.say("2.10") as (tr, t):
            self.play(FadeIn(bars[1]), FadeIn(bars[2]), run_time=0.5)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars[0]], lag_ratio=0.03), FadeIn(n_t), run_time=1.2)
            self.play(FadeIn(q, shift=UP * 0.2), run_time=0.6)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S02StandardError", "S02Curve", "S02HandsOn"]
