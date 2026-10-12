"""Lecture 5, section 7 — why we take the logarithm.

L(p̂) ≈ 8 × 10⁻⁵⁶, the chance of one exact sequence; × C(200, 66) gives 0.06 and leaves the peak where it
is. The rescaled likelihood and the log-likelihood, both N's curves, peak at p̂ = 0.33, where
ℓ = −126.84. Relative likelihoods 0.66 (p = 0.30), 0.12 (0.40) and, in the pause, 0.04 (0.25).
Every number shown comes from N.
"""
from math import floor

from lecture05_kit import *

K, NN, P_HAT = N["k"], N["n"], N["p_hat"]
LIK, LOGLIK = N["lik_curve"], N["loglik_curve"]
REL = {float(p): r for p, r in N["relative"].items()}     # {0.25: 0.04, 0.30: 0.66, 0.40: 0.12}
P_TASK = min(REL)                                         # 0.25, the pause
SHOWN = sorted(p for p in REL if p != P_TASK)             # 0.30, 0.40, read off in 7.6
LL_LO = floor(min(y for _, y in LOGLIK) / 10) * 10


def axes(y_range, y_len, numbers, x_len=7.2):
    return Axes(x_range=[0.15, 0.55, 0.1], y_range=y_range, x_length=x_len, y_length=y_len, tips=False,
                axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 20},
                x_axis_config={"include_numbers": True, "numbers_to_include": [0.2, 0.3, 0.4, 0.5],
                               "decimal_number_config": {"num_decimal_places": 1}},
                y_axis_config={"include_numbers": numbers, "decimal_number_config": {"num_decimal_places": 0}})


def curve_on(ax, pts, color, width=5):
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly([ax.c2p(x, y) for x, y in pts])


def lik_at(p):
    """The rescaled likelihood at p, read off N's curve (nearest grid point)."""
    return min(LIK, key=lambda t: abs(t[0] - p))[1]


class S07Tiny(LectureScene):
    def construct(self):
        self.section_card(7)
        val = MathTex(r"L(\hat p)", r"\approx", rf"{round(N['lik_hat_mantissa'])} \times 10^{{{N['lik_hat_exp']}}}",
                      font_size=64).move_to(UP * 1.6)
        seq = VGroup(txt(label("one_exact_sequence"), size=28, color=GREY_B),
                     tagged(NN, label("orders_word"), size=28, color=GREY_B)).arrange(RIGHT, buff=0.25)
        seq.next_to(val, DOWN, buff=0.4)
        with self.say("7.1"):
            self.play(Write(val), run_time=1.0)
            self.play(FadeIn(seq), run_time=0.6)

        ways = MathTex(r"\binom{" + str(NN) + "}{" + str(K) + r"}", r"\times", r"L(\hat p)", r"\approx",
                       dec(N["p_some_66"]), font_size=56).move_to(DOWN * 0.6)
        ways[4].set_color(HILITE)
        ways_l = txt(label("the_number_of_ways"), size=24, color=GREY_B).next_to(ways[0], DOWN, buff=0.3)
        stays = txt(label("no_p_the_peak_stays"), size=28, color=LBLUE).next_to(ways, DOWN, buff=0.9)
        with self.say("7.2") as (tr, t):
            self.play(Write(ways), FadeIn(ways_l), run_time=1.0)
            self.cue(tr, t, {"en": "That factor has no p", "uz": "Bu koʻpaytuvchida pi yoʻq"})
            self.play(Indicate(ways[0], color=LBLUE, scale_factor=1.1), FadeIn(stays), run_time=0.9)
        self.clear_all()


class S07Log(LectureScene):
    def construct(self):
        top = axes([0, 1.1, 0.5], 2.2, False).move_to([-1.3, 1.55, 0])
        span = -120 - LL_LO
        bot = axes([0, span, 10], 2.4, False).move_to([-1.3, -1.75, 0])
        yt = VGroup(*[MathTex(str(LL_LO + v), font_size=20, color=GREY_B).next_to(bot.c2p(0.15, v), LEFT, buff=0.12)
                      for v in range(0, span + 1, 10)])
        c_top = curve_on(top, LIK, LBLUE)
        c_bot = curve_on(bot, [(x, y - LL_LO) for x, y in LOGLIK], HILITE)
        t_l = txt(label("rescaled_likelihood"), size=22, color=LBLUE).next_to(top, UP, buff=0.3).align_to(top, LEFT)
        b_l = txt(label("log_likelihood"), size=22, color=HILITE).next_to(bot, UP, buff=0.1).align_to(bot, LEFT)
        ll_peak = max(y for _, y in LOGLIK)
        drops = VGroup(DashedLine(top.c2p(P_HAT, 1.0), top.c2p(P_HAT, 0), color=WHITE, stroke_width=2.5),
                       DashedLine(bot.c2p(P_HAT, ll_peak - LL_LO), bot.c2p(P_HAT, 0), color=WHITE, stroke_width=2.5))
        ph = MathTex(rf"\hat p = {dec(P_HAT)}", font_size=30).next_to(top.c2p(P_HAT, 1.0), RIGHT, buff=0.3)
        ph.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.05)
        inc = txt(label("log_is_increasing"), size=26, color=GREY_B)
        if inc.width > 3.9:
            inc.scale_to_fit_width(3.9)
        inc.move_to([4.55, 1.6, 0])
        with self.say("7.3") as (tr, t):
            self.play(Create(top), FadeIn(t_l), Create(c_top), run_time=1.2)
            self.cue(tr, t, {"en": "First, it does not move", "uz": "Birinchidan"})
            self.play(Create(bot), FadeIn(yt), FadeIn(b_l), Create(c_bot), run_time=1.2)
            self.play(Create(drops), FadeIn(ph), FadeIn(inc), run_time=0.7)

        comp = VGroup(txt(label("in_the_computer"), size=22, color=GREY_B),
                      MathTex(r"\prod p(y_i \mid p) \to 0", font_size=34, color=RLRED)).arrange(DOWN, buff=0.15)
        comp.move_to([4.6, 0.3, 0])
        cross = Cross(comp[1], stroke_color=RLRED, stroke_width=4).scale(0.9)
        llv = MathTex(rf"\ell(\hat p) = {N['loglik_hat']:.2f}", font_size=36, color=HILITE)
        llv.move_to([4.6, -0.9, 0])
        with self.say("7.4") as (tr, t):
            self.play(FadeOut(inc), FadeIn(comp), run_time=0.7)
            self.play(Create(cross), run_time=0.5)
            self.cue(tr, t, {"en": "The log of the same number", "uz": "Oʻsha sonning logarifmi"})
            self.play(Write(llv), Indicate(c_bot, color=HILITE, scale_factor=1.0), run_time=0.9)

        sumrule = MathTex(r"\log \prod_i p_i = \sum_i \log p_i", font_size=34).move_to([4.6, -2.2, 0])
        sum_l = txt(label("product_into_sum"), size=22, color=GREY_B)
        if sum_l.width > 3.6:
            sum_l.scale_to_fit_width(3.6)
        sum_l.next_to(sumrule, DOWN, buff=0.2)
        with self.say("7.5"):
            self.play(Write(sumrule), FadeIn(sum_l), run_time=1.0)
        self.clear_all()


class S07Sharp(LectureScene):
    def construct(self):
        ax = axes([0, 1.1, 0.5], 4.0, False, x_len=6.4).move_to([-2.4, -0.3, 0])
        curve = curve_on(ax, LIK, LBLUE)
        pl = MathTex("p", font_size=30, color=GREY_B).next_to(ax.x_axis, RIGHT, buff=0.2)
        peak = Dot(ax.c2p(P_HAT, 1.0), radius=0.1, color=HILITE)
        ph = MathTex(rf"\hat p = {dec(P_HAT)}", font_size=30, color=HILITE).next_to(peak, UP, buff=0.15)
        rel_l = txt(label("relative_to_the_peak"), size=24, color=GREY_B).to_edge(UP, buff=SAFE + 0.3)

        def mark(p, color):
            y = lik_at(p)
            d = Dot(ax.c2p(p, y), radius=0.09, color=color)
            stem = DashedLine(ax.c2p(p, 0), ax.c2p(p, y), color=color, stroke_width=2.5)
            v = MathTex(dec(REL[p]), font_size=34, color=color)
            side = LEFT if p < P_HAT else RIGHT
            v.next_to(d, side + UP * 0.3, buff=0.15)
            v.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.05)
            return VGroup(stem, d, v)

        m30, m40 = mark(SHOWN[0], RLGREEN), mark(SHOWN[1], RLORANGE)
        with self.say("7.6") as (tr, t):
            self.play(Create(ax), FadeIn(pl), Create(curve), FadeIn(peak), FadeIn(ph), FadeIn(rel_l), run_time=1.2)
            self.cue(tr, t, {"en": "a p of zero point three is", "uz": "pi nol butun oʻndan uch nol"})
            self.play(FadeIn(m30), run_time=0.6)
            self.cue(tr, t, {"en": "and zero point four only", "uz": "pi nol butun oʻndan toʻrt esa"})
            self.play(FadeIn(m40), run_time=0.6)

        grades = txt(label("it_grades_them"), size=27, color=LBLUE)
        if grades.width > 5.2:
            grades.scale_to_fit_width(5.2)
        grades.move_to([3.9, 1.4, 0])
        nxt = VGroup(txt(label("lecture_6"), size=24, color=GREY_B), MathTex(r"\to", font_size=30, color=GREY_B),
                     txt(label("posterior", 1), size=24, color=HILITE)).arrange(RIGHT, buff=0.2)
        nxt.next_to(grades, DOWN, buff=0.35)
        with self.say("7.7") as (tr, t):
            self.play(FadeIn(grades), run_time=0.6)
            self.cue(tr, t, {"en": "In Lecture 6", "uz": "Oltinchi maʼruzada"})
            self.play(FadeIn(nxt), run_time=0.6)
        self.clear_all()

        fw = txt(label("frameworks"), size=32, weight=BOLD, color=LBLUE).move_to(UP * 1.6)
        bad = MathTex(r"\prod_i p_i", font_size=60, color=GREY_B).move_to(LEFT * 2.6 + DOWN * 0.3)
        good = MathTex(r"\sum_i \log p_i", font_size=60, color=HILITE).move_to(RIGHT * 2.6 + DOWN * 0.3)
        cross = Cross(bad, stroke_color=RLRED, stroke_width=6)
        arrow = Arrow(bad.get_right(), good.get_left(), buff=0.4, color=GREY_B)
        with self.say("7.8"):
            self.play(FadeIn(fw), FadeIn(bad), run_time=0.7)
            self.play(Create(cross), GrowArrow(arrow), FadeIn(good, shift=LEFT * 0.2), run_time=0.9)
        self.clear_all()


class S07HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"L({dec(P_TASK)}) / L(p̂) = ?"])
        card.to_edge(UP, buff=SAFE + 0.3)
        ax = axes([0, 1.1, 0.5], 3.4, False).move_to(DOWN * 1.1)
        curve = curve_on(ax, LIK, LBLUE)
        pl = MathTex("p", font_size=30, color=GREY_B).next_to(ax.x_axis, RIGHT, buff=0.2)
        peak = Dot(ax.c2p(P_HAT, 1.0), radius=0.1, color=HILITE)
        with self.say("7.9") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(card), Create(ax), FadeIn(pl), Create(curve), FadeIn(peak), run_time=0.9)
        self.hands_on()

        y = lik_at(P_TASK)
        d = Dot(ax.c2p(P_TASK, y), radius=0.1, color=RLRED)
        stem = DashedLine(ax.c2p(P_TASK, 0), ax.c2p(P_TASK, max(y, 0.02)), color=RLRED, stroke_width=3)
        v = MathTex(dec(REL[P_TASK]), font_size=40, color=RLRED)
        fluke = txt(label("a_bit_of_a_fluke"), size=26, color=RLRED)
        tag = VGroup(fluke, v).arrange(DOWN, buff=0.12)
        tag.next_to(ax.c2p(0.15, 0.85), RIGHT, buff=0.3)
        point = Arrow(tag.get_bottom(), d.get_center(), buff=0.12, color=RLRED, stroke_width=3,
                      max_tip_length_to_length_ratio=0.15)
        with self.say("7.10") as (tr, t):
            self.play(FadeOut(card), Create(stem), FadeIn(d, scale=1.4), run_time=0.7)
            self.play(Write(v), FadeIn(fluke), GrowArrow(point), run_time=0.7)

        q = txt(label("a_formula_for_the_peak_q"), size=32, color=LBLUE).to_edge(UP, buff=SAFE + 0.5)
        with self.say("7.11"):
            self.play(FadeIn(q), Indicate(peak, color=HILITE, scale_factor=1.6), run_time=0.9)
        self.clear_all(run_time=0.3)


SCENES = ["S07Tiny", "S07Log", "S07Sharp", "S07HandsOn"]
