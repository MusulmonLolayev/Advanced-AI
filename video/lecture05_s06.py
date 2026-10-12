"""Lecture 5, section 6 — the likelihood function, opening Part 1.

66 pastry orders in 200 → L(p) = p⁶⁶ (1 − p)¹³⁴; read as a curve over p it peaks at p̂ = 0.33. Which of
the 200 cards are lit is a picture (marked); the counts 66 and 134 are N's. The likelihood curve is N's
(capture_l05.py). Every number shown comes from N.
"""
from lecture05_kit import *

K, NN, NK, P_HAT = N["k"], N["n"], N["n_minus_k"], N["p_hat"]
LIK = N["lik_curve"]                       # likelihood rescaled to peak 1, over p
P_FLUKE = min(float(p) for p in N["relative"])   # 0.25, the candidate the narration doubts
LIT_C, OFF_C = HILITE, GREY_D


def order_grid(n=NN, k=K, cols=20, side=0.3, gap=0.08):
    """n order cards in rows of cols; k of them lit. Which are lit is a picture: i*37 mod n < k picks
    exactly k cards (37 and 200 are coprime), spread over the grid."""
    lit = [(i * 37) % n < k for i in range(n)]
    assert sum(lit) == k
    g = VGroup(*[RoundedRectangle(corner_radius=0.04, width=side, height=side, stroke_width=1.5,
                                  stroke_color=LIT_C if on else GREY_B, fill_color=LIT_C if on else BLACK,
                                  fill_opacity=0.85 if on else 0) for on in lit])
    g.arrange_in_grid(rows=n // cols, cols=cols, buff=gap)
    return g, lit


def lik_axes(x_len=6.2, y_len=2.8):
    ax = Axes(x_range=[0.15, 0.55, 0.1], y_range=[0, 1.1, 0.5], x_length=x_len, y_length=y_len, tips=False,
              axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 22},
              x_axis_config={"include_numbers": True, "numbers_to_include": [0.2, 0.3, 0.4, 0.5],
                             "decimal_number_config": {"num_decimal_places": 1}},
              y_axis_config={"include_numbers": False})
    return ax


def curve_on(ax, pts, color, width=5):
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly([ax.c2p(x, y) for x, y in pts])


class S06Question(LectureScene):
    def construct(self):
        self.section_card(6)
        # the parameters arrived filled in; nobody said where they came from
        params = VGroup(*[MathTex(s, font_size=60, color=c) for s, c in
                          ((r"p", HILITE), (r"\lambda", LBLUE), (r"\mu", RLGREEN), (r"\sigma", RLGREEN))])
        params.arrange(RIGHT, buff=1.4).move_to(UP * 0.6)
        qs = VGroup(*[MathTex("?", font_size=54, color=RLRED).next_to(p, UR, buff=0.05) for p in params])
        where = txt(label("where_do_these_come_from_q"), size=32, color=GREY_B).next_to(params, DOWN, buff=0.9)
        with self.say("6.1") as (tr, t):
            self.play(LaggedStart(*[FadeIn(p, scale=0.7) for p in params], lag_ratio=0.25), run_time=1.2)
            self.cue(tr, t, {"en": "Nobody ever said", "uz": "Bu sonlar qayerdan"})
            self.play(LaggedStart(*[FadeIn(q, scale=1.4) for q in qs], lag_ratio=0.15), FadeIn(where), run_time=0.9)
        head = txt(label("least_surprising_parameter_q"), size=34, weight=BOLD, color=LBLUE)
        head.to_edge(UP, buff=SAFE + 0.3)
        if head.width > 12:
            head.scale_to_fit_width(12)
        with self.say("6.2"):
            self.play(FadeOut(VGroup(params, qs, where)), FadeIn(head, shift=DOWN * 0.2), run_time=0.8)

        grid, lit = order_grid()
        grid.move_to(UP * 0.85)
        count = tagged(f"{K}/{NN}", label("pastries_short"), size=28, color=LIT_C).next_to(grid, DOWN, buff=0.25)
        note = info(label("illustration"))
        line = NumberLine(x_range=[0, 1, 0.1], length=10, include_numbers=False, color=GREY_B).move_to(DOWN * 1.75)
        ends = VGroup(MathTex("0", font_size=28, color=GREY_B).next_to(line.n2p(0), DOWN, buff=0.2),
                      MathTex("1", font_size=28, color=GREY_B).next_to(line.n2p(1), DOWN, buff=0.2))
        pq = MathTex("p", font_size=34, color=GREY_B).next_to(line, LEFT, buff=0.3)
        fl = VGroup(Dot(line.n2p(P_FLUKE), radius=0.09, color=GREY_B),
                    MathTex(rf"{dec(P_FLUKE)}\,?", font_size=30, color=GREY_B))
        fl[1].next_to(fl[0], DOWN, buff=0.22)
        fl_l = txt(label("a_bit_of_a_fluke"), size=22, color=GREY_B).next_to(fl[1], DOWN, buff=0.15)
        fl_l.align_to(fl[1], RIGHT)
        best = VGroup(Dot(line.n2p(P_HAT), radius=0.11, color=LIT_C),
                      MathTex(dec(P_HAT), font_size=32, color=LIT_C))
        best[1].next_to(best[0], DOWN, buff=0.22)
        best_l = txt(label("the_most_ordinary"), size=22, color=LIT_C).next_to(best[1], DOWN, buff=0.15)
        best_l.align_to(best[1], LEFT)
        with self.say("6.3") as (tr, t):
            self.play(LaggedStart(*[FadeIn(c) for c in grid], lag_ratio=0.003), FadeIn(note), run_time=1.2)
            self.play(FadeIn(count), run_time=0.5)
            self.play(Create(line), FadeIn(ends), FadeIn(pq), run_time=0.6)
            self.cue(tr, t, {"en": "Was p zero point two five", "uz": "Pi nol butun yuzdan yigirma besh"})
            self.play(FadeIn(fl), FadeIn(fl_l), run_time=0.6)
            self.cue(tr, t, {"en": "A p of zero point three three", "uz": "Pi nol butun yuzdan oʻttiz uch"})
            self.play(FadeIn(best, scale=1.3), FadeIn(best_l), run_time=0.6)
        self.clear_all()


class S06Likelihood(LectureScene):
    def construct(self):
        defn = MathTex(r"L(\theta)", "=", r"\prod_{i=1}^{n} p(x_i \mid \theta)", font_size=56)
        defn.move_to(UP * 2.2)
        name = txt(label("likelihood"), size=30, color=LBLUE).next_to(defn, DOWN, buff=0.3)
        with self.say("6.4"):
            self.play(Write(defn), run_time=1.0)
            self.play(FadeIn(name), run_time=0.5)

        # the first orders of the grid, each with the probability it contributes
        _, lit = order_grid()
        first = lit[:10]
        cards = VGroup(*[RoundedRectangle(corner_radius=0.06, width=0.6, height=0.6, stroke_width=2.5,
                                          stroke_color=LIT_C if on else GREY_B, fill_color=LIT_C if on else BLACK,
                                          fill_opacity=0.85 if on else 0) for on in first])
        cards.arrange(RIGHT, buff=0.6).move_to(UP * 0.35)
        facs = VGroup(*[MathTex("p" if on else "(1-p)", font_size=24, color=LIT_C if on else GREY_B)
                        .next_to(c, DOWN, buff=0.2) for c, on in zip(cards, first)])
        dots = MathTex(r"\cdots", font_size=40, color=GREY_B).next_to(cards, RIGHT, buff=0.3)
        one = MathTex(r"p(y_i \mid p)", "=", r"p^{\,y_i}(1-p)^{\,1-y_i}", font_size=40).move_to(DOWN * 1.3)
        mult = txt(label("independent_orders_multiply"), size=24, color=GREY_B)
        powers = txt(label("powers_add"), size=24, color=GREY_B)
        VGroup(mult, powers).arrange(DOWN, buff=0.15).next_to(one, DOWN, buff=0.35)
        with self.say("6.5") as (tr, t):
            self.play(LaggedStart(*[FadeIn(c) for c in cards], lag_ratio=0.08), FadeIn(dots), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in facs], lag_ratio=0.08), run_time=0.8)
            self.play(Write(one), run_time=0.8)
            self.cue(tr, t, {"en": "The orders are independent", "uz": "Buyurtmalar mustaqil"})
            self.play(FadeIn(mult), run_time=0.5)
            self.cue(tr, t, {"en": "powers of the same base", "uz": "bir xil asosning darajalari"})
            self.play(FadeIn(powers), run_time=0.5)

        res = MathTex(r"L(p)", "=", "p^{" + str(K) + "}", "(1-p)^{" + str(NK) + "}", font_size=72)
        res.move_to(DOWN * 0.2)
        box = SurroundingRectangle(res, buff=0.25, color=HILITE, stroke_width=4)
        with self.say("6.6"):
            self.play(FadeOut(VGroup(cards, facs, dots, one, mult, powers)), run_time=0.5)
            self.play(Write(res), run_time=1.0)
            self.play(Create(box), run_time=0.5)

        survived = txt(label("only_the_counts_survived"), size=30, color=GREY_B).next_to(box, DOWN, buff=0.5)
        ev_k = tagged(K, label("pastries_short"), size=30, color=LIT_C)
        ev_nk = tagged(NK, label("without_pastry"), size=30, color=GREY_B)
        ev = VGroup(ev_k, ev_nk).arrange(RIGHT, buff=0.9).next_to(survived, DOWN, buff=0.35)
        ev_l = txt(label("evidence"), size=26, color=HILITE).next_to(ev, DOWN, buff=0.25)
        with self.say("6.7") as (tr, t):
            self.play(FadeIn(survived), run_time=0.6)
            self.cue(tr, t, {"en": "All the evidence", "uz": "Pi haqidagi butun dalil"})
            self.play(Indicate(res[2], color=LIT_C, scale_factor=1.15), Indicate(res[3], color=WHITE, scale_factor=1.1),
                      FadeIn(ev), FadeIn(ev_l), run_time=1.0)
        self.clear_all()

        # two readings of the same formula
        top = VGroup(res.copy().scale(0.55)).to_edge(UP, buff=SAFE + 0.35)
        left_h = txt(label("parameter_fixed"), size=28, weight=BOLD, color=GREY_B)
        left_b = txt(label("a_distribution_over_data"), size=24, color=GREY_B)
        left_m = MathTex(r"p(x \mid \theta)", font_size=44, color=GREY_B)
        left = VGroup(left_h, left_m, left_b).arrange(DOWN, buff=0.35).move_to([-4.0, 0.0, 0])
        ax = lik_axes().move_to([2.4, -0.4, 0])
        curve = curve_on(ax, LIK, LBLUE)
        right_h = txt(label("data_fixed"), size=28, weight=BOLD, color=LBLUE).next_to(ax, UP, buff=0.6)
        right_b = txt(label("a_curve_over_the_parameter"), size=22, color=LBLUE).next_to(right_h, DOWN, buff=0.12)
        pl = MathTex("p", font_size=30, color=GREY_B).next_to(ax.x_axis, RIGHT, buff=0.2)
        peak = Dot(ax.c2p(P_HAT, 1.0), radius=0.1, color=HILITE)
        drop = DashedLine(ax.c2p(P_HAT, 1.0), ax.c2p(P_HAT, 0), color=HILITE, stroke_width=3)
        ph = MathTex(rf"\hat p = {dec(P_HAT)}", font_size=34, color=HILITE).next_to(peak, RIGHT, buff=0.25)
        ph.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.05)
        mle = txt(label("maximum_likelihood_estimate"), size=24, color=HILITE).next_to(ax, DOWN, buff=0.6)
        with self.say("6.8") as (tr, t):
            self.play(FadeIn(top), FadeIn(left), run_time=0.8)
            self.cue(tr, t, {"en": "With the data fixed", "uz": "Berilganlar belgilangan"})
            self.play(Create(ax), FadeIn(pl), FadeIn(right_h), FadeIn(right_b), run_time=0.8)
            self.play(Create(curve), run_time=1.0)
            self.cue(tr, t, {"en": "Its peak", "uz": "Egri chiziqning choʻqqisi"})
            self.play(FadeIn(peak, scale=1.5), Create(drop), FadeIn(ph), FadeIn(mle), run_time=0.8)
        self.clear_all()

        # AI: training searches for the parameters that make the training data least surprising
        theta = VGroup(txt(label("model_parameters"), size=30, color=LBLUE), MathTex(r"\theta", font_size=56, color=LBLUE))
        theta.arrange(DOWN, buff=0.25).move_to(LEFT * 3.6)
        data = VGroup(txt(label("training_data"), size=30, color=HILITE),
                      MathTex(r"x_1, \dots, x_n", font_size=44, color=HILITE)).arrange(DOWN, buff=0.25).move_to(RIGHT * 3.6)
        arrow = Arrow(theta.get_right(), data.get_left(), buff=0.4, color=GREY_B)
        goal = MathTex(r"\max_\theta L(\theta)", font_size=44).next_to(arrow, UP, buff=0.25)
        least = txt(label("least_surprising"), size=26, color=GREY_B).next_to(arrow, DOWN, buff=0.25)
        with self.say("6.9"):
            self.play(FadeIn(theta), FadeIn(data), run_time=0.7)
            self.play(GrowArrow(arrow), Write(goal), FadeIn(least), run_time=1.0)
        self.clear_all()


class S06HandsOn(LectureScene):
    def construct(self):
        card = pause_card([label("three_orders_pastry_none_pastry"), "L(p) = ?"])
        card.to_edge(UP, buff=SAFE + 0.3)
        seq = (True, False, True)
        cards = VGroup(*[RoundedRectangle(corner_radius=0.08, width=0.9, height=0.9, stroke_width=3,
                                          stroke_color=LIT_C if on else GREY_B, fill_color=LIT_C if on else BLACK,
                                          fill_opacity=0.85 if on else 0) for on in seq]).arrange(RIGHT, buff=1.0)
        cards.move_to(DOWN * 0.6)
        names = VGroup(*[txt(label("with_pastry") if on else label("no_pastry"), size=22, color=LIT_C if on else GREY_B)
                         .next_to(c, UP, buff=0.15) for c, on in zip(cards, seq)])
        with self.say("6.10") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(card), FadeIn(cards), FadeIn(names), run_time=0.8)
        self.hands_on()

        facs = VGroup(*[MathTex("p" if on else "(1-p)", font_size=40, color=LIT_C if on else GREY_B)
                        .next_to(c, DOWN, buff=0.25) for c, on in zip(cards, seq)])
        ans = MathTex(r"L(p)", "=", r"p \cdot (1-p) \cdot p", "=", r"p^{2}(1-p)", font_size=52)
        ans.next_to(facs, DOWN, buff=0.6)
        ans[4].set_color(HILITE)
        with self.say("6.11"):
            self.play(FadeOut(card), LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in facs], lag_ratio=0.2), run_time=0.8)
            self.play(Write(ans), run_time=1.0)
        self.clear_all()

        prod = MathTex(r"\prod_{i=1}^{" + str(NN) + r"} p(y_i \mid p)", font_size=56).move_to(UP * 0.5)
        q = txt(label("a_tiny_number_q"), size=30, color=LBLUE).next_to(prod, DOWN, buff=0.6)
        with self.say("6.12"):
            self.play(Write(prod), run_time=0.8)
            self.play(prod.animate.scale(0.6), FadeIn(q), run_time=0.8)
        self.clear_all(run_time=0.3)


SCENES = ["S06Question", "S06Likelihood", "S06HandsOn"]
