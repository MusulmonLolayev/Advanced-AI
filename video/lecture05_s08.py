"""Lecture 5, section 8 — the Bernoulli and Gaussian maximum likelihood estimates.

p-hat = k/n with the lecture's 66 of 200, the log-likelihood curve and its peak (l05_numbers.json);
the Gaussian derivation over the figure script's 40 espresso shots. The class-share bars in the AI
line are an illustration, marked so.
"""
import numpy as np
from lecture05_kit import *

K, NN, P_HAT = N["k"], N["n"], N["p_hat"]
SHOTS = np.array(N["shots"])
XBAR = N["xbar"]


def loglik_panel(width=4.6, height=2.2):
    """The Bernoulli log-likelihood of 66 in 200 (captured curve), with its peak marked."""
    pts = N["loglik_curve"]
    ys = [y for _, y in pts]
    lo, hi = min(ys), max(ys)
    # the values are all negative: plot them above the curve's own minimum so the p axis sits at the bottom
    ax = Axes(x_range=[0.15, 0.55, 0.1], y_range=[0, hi - lo + 2, 10], x_length=width, y_length=height, tips=False,
              axis_config={"color": GREY_B, "stroke_width": 2},
              x_axis_config={"include_numbers": True, "font_size": 20, "decimal_number_config": {"num_decimal_places": 1}},
              y_axis_config={"include_ticks": False})
    c = VMobject(stroke_color=LBLUE, stroke_width=4).set_points_smoothly([ax.c2p(x, y - lo) for x, y in pts])
    peak = Dot(ax.c2p(P_HAT, N["loglik_hat"] - lo), radius=0.08, color=HILITE)
    drop = DashedLine(ax.c2p(P_HAT, N["loglik_hat"] - lo), ax.c2p(P_HAT, 0), color=HILITE, stroke_width=2)
    name = txt(label("mle_log_likelihood"), size=20, color=GREY_B).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
    tag = txt(label("mle_the_peak"), size=20, color=HILITE).next_to(peak, UP, buff=0.12)
    return VGroup(ax, c, drop, peak, name, tag)


class S08Bernoulli(LectureScene):
    def construct(self):
        self.section_card(8)
        given = VGroup(tagged("k", label("mle_k_successes"), size=30, color=LBLUE),
                       txt("·", size=30, color=GREY_B),
                       tagged("n", label("mle_trials"), size=30, color=LBLUE)).arrange(RIGHT, buff=0.3)
        given.to_edge(UP, buff=SAFE + 0.35)
        ell = MathTex(r"\ell(p) = k \log p + (n-k)\log(1-p)", font_size=44).next_to(given, DOWN, buff=0.45)
        deriv = MathTex(r"\frac{d\ell}{dp} = \frac{k}{p} - \frac{n-k}{1-p} = 0", font_size=44).next_to(ell, DOWN, buff=0.35)
        with self.say("8.1") as (tr, t):
            self.play(FadeIn(given), run_time=0.6)
            self.cue(tr, t, {"en": "We take the log", "uz": "Logarifm olamiz"})
            self.play(Write(ell), run_time=0.9)
            self.cue(tr, t, {"en": "and set it to zero", "uz": "nolga tenglaymiz"})
            self.play(Write(deriv), run_time=0.9)

        res = MathTex(r"\hat{p} = \frac{k}{n}", "=", rf"\frac{{{K}}}{{{NN}}}", "=", dec(P_HAT), font_size=52)
        res.move_to([-2.9, -1.3, 0])
        box = SurroundingRectangle(res[0], buff=0.12, color=HILITE, stroke_width=3)
        res[4].set_color(HILITE)
        share = txt(label("mle_observed_share"), size=26, color=GREY_B).next_to(res, DOWN, buff=0.3)
        panel = loglik_panel().move_to([3.6, -1.5, 0])
        derived = txt(label("mle_derived_not_assumed"), size=26, color=HILITE).next_to(share, DOWN, buff=0.25)
        with self.say("8.2") as (tr, t):
            self.play(FadeIn(res[0]), Create(box), run_time=0.8)
            self.cue(tr, t, {"en": "It is simply", "uz": "Bu shunchaki"})
            self.play(FadeIn(res[1:]), FadeIn(share), run_time=0.9)
            self.play(FadeIn(panel), run_time=0.8)
            self.cue(tr, t, {"en": "The answer everyone", "uz": "Hamma taxmin"})
            self.play(FadeIn(derived, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S08Gaussian(LectureScene):
    def construct(self):
        lik = MathTex(r"L(\mu, \sigma^2) = \prod_{i=1}^{n} \frac{1}{\sqrt{2\pi\sigma^2}}\,"
                      r"e^{-\frac{(x_i-\mu)^2}{2\sigma^2}}", font_size=40).to_edge(UP, buff=SAFE + 0.3)
        ell = MathTex(r"\ell(\mu, \sigma^2) = -\frac{n}{2}\log(2\pi\sigma^2)", r"-\frac{1}{2\sigma^2}\sum_{i=1}^{n}(x_i-\mu)^2",
                      font_size=40).move_to(lik)
        with self.say("8.3") as (tr, t):
            self.play(Write(lik), run_time=1.0)
            self.cue(tr, t, {"en": "the log turns", "uz": "logarifm koʻpaytmani"})
            self.play(ReplacementTransform(lik, ell), run_time=1.0)

        # the 40 espresso shots on a line, each with its deviation from the average
        line = NumberLine(x_range=[26, 34, 1], length=9.0, color=GREY_B, include_numbers=True, font_size=22)
        line.move_to(DOWN * 2.2)
        unit = txt(label("espresso_ml"), size=20, color=GREY_B).next_to(line, DOWN, buff=0.4)
        order = np.argsort(SHOTS)
        dots, devs = VGroup(), VGroup()
        for j, i in enumerate(order):
            y = -1.45 + 0.13 * (j % 6)
            p = [line.n2p(SHOTS[i])[0], y, 0]
            dots.add(Dot(p, radius=0.05, color=LBLUE))
            devs.add(Line([line.n2p(XBAR)[0], y, 0], p, stroke_width=2,
                          color=RLGREEN if SHOTS[i] > XBAR else RLRED))
        mean_ln = DashedLine(line.n2p(XBAR) + UP * 0.05, line.n2p(XBAR) + UP * 1.55, color=HILITE, stroke_width=3)
        dmu = MathTex(r"\frac{\partial \ell}{\partial \mu} = \frac{1}{\sigma^2}\sum_{i=1}^{n}(x_i-\mu) = 0", r"\;\Rightarrow\;",
                      r"\hat{\mu} = \bar{x}", font_size=38).next_to(ell, DOWN, buff=0.45)
        box_mu = SurroundingRectangle(dmu[2], buff=0.1, color=HILITE, stroke_width=3)
        sm = txt(label("mle_sample_mean"), size=22, color=HILITE).next_to(mean_ln, UP, buff=0.08)
        sm.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.05)
        cancel = txt(label("mle_deviations_cancel"), size=24, color=GREY_B)
        if cancel.width > 4.0:
            cancel.scale_to_fit_width(4.0)
        cancel.move_to([3.9, sm.get_y(), 0])                  # beside the mean's tag, clear of the dots
        with self.say("8.4") as (tr, t):
            self.play(FadeIn(line), FadeIn(unit), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.02), run_time=1.0)
            self.play(Write(dmu[0]), run_time=0.9)
            self.cue(tr, t, {"en": "and that happens exactly", "uz": "va bu aynan oʻrtachada"})
            self.play(Create(mean_ln), LaggedStart(*[Create(d) for d in devs], lag_ratio=0.02), FadeIn(cancel), run_time=1.0)
            self.play(FadeIn(dmu[1:]), Create(box_mu), FadeIn(sm), run_time=0.8)

        dvar = MathTex(r"\hat{\sigma}^2 = \frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^2", font_size=44).move_to(dmu)
        box_v = SurroundingRectangle(dvar, buff=0.12, color=HILITE, stroke_width=3)
        with self.say("8.5"):
            self.play(FadeOut(dmu), FadeOut(box_mu), FadeOut(cancel), run_time=0.4)
            self.play(Write(dvar), Create(box_v), run_time=1.0)
        self.clear_all()

        ml = VGroup(MathTex(r"\frac{1}{n}", font_size=72, color=HILITE),
                    txt(label("mle_max_likelihood"), size=26, color=HILITE)).arrange(DOWN, buff=0.3)
        l1 = VGroup(MathTex(r"\frac{1}{n-1}", font_size=72, color=LBLUE),
                    txt(label("lecture_1"), size=26, color=LBLUE)).arrange(DOWN, buff=0.3)
        pair = VGroup(l1, ml).arrange(RIGHT, buff=2.4).move_to(UP * 0.6)
        small = txt(label("mle_slightly_small"), size=30, weight=BOLD, color=HILITE).next_to(ml, DOWN, buff=0.45)
        why = txt(label("mle_fitted_to_the_same_data"), size=24, color=GREY_B).next_to(pair, DOWN, buff=1.5)
        if why.width > 12.4:
            why.scale_to_fit_width(12.4)
        with self.say("8.6") as (tr, t):
            self.play(FadeIn(l1), run_time=0.6)
            self.cue(tr, t, {"en": "Maximum likelihood runs", "uz": "Maksimal haqiqatga"})
            self.play(FadeIn(ml), FadeIn(small, shift=UP * 0.2), run_time=0.8)
            self.cue(tr, t, {"en": "because the spread", "uz": "chunki tarqoqlik"})
            self.play(FadeIn(why), run_time=0.6)
        self.clear_all()


class S08Classes(LectureScene):
    def construct(self):
        head = self.heading(label("mle_starting_probabilities"), color=LBLUE)
        heights = [2.6, 1.5, 0.9]                       # an illustration: no numbers shown
        bars = VGroup(*[Rectangle(width=1.2, height=h, stroke_width=0, fill_color=c, fill_opacity=1)
                        for h, c in zip(heights, (LBLUE, RLGREEN, HILITE))]).arrange(RIGHT, buff=0.6, aligned_edge=DOWN)
        bars.move_to([-2.6, -0.8, 0])
        names = VGroup(*[tagged(str(i), label("mle_class"), after=False, size=24, color=GREY_B)
                         .next_to(b, DOWN, buff=0.2) for i, b in enumerate(bars, 1)])
        f = MathTex(r"\hat{p}_c = \frac{n_c}{n}", font_size=60, color=HILITE).move_to([2.9, -0.2, 0])
        share = txt(label("mle_class_share"), size=24, color=GREY_B)
        if share.width > 5.2:
            share.scale_to_fit_width(5.2)
        share.next_to(f, DOWN, buff=0.4)
        note = info(label("illustration"))
        with self.say("8.7") as (tr, t):
            self.play(FadeIn(head), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2),
                      FadeIn(names), FadeIn(note), run_time=1.2)
            self.cue(tr, t, {"en": "each class's share", "uz": "har bir sinfning"})
            self.play(Write(f), FadeIn(share), run_time=0.9)
        self.clear_all()


class S08HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"{N['k_task']} / {N['n_task']}:  {label('mle_orders_with_a_pastry')}", "p̂ = ?"])
        with self.say("8.8"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        ans = MathTex(r"\hat{p}", "=", rf"\frac{{{N['k_task']}}}{{{N['n_task']}}}", "=", dec(N["p_hat_task"]),
                      font_size=72).move_to(UP * 0.3)
        ans[4].set_color(HILITE)
        with self.say("8.9"):
            self.play(Write(ans), run_time=1.0)
        self.play(FadeOut(ans), run_time=0.4)

        # three candidate bells: which one is best? (shapes only)
        xs = np.linspace(-4, 4, 121)
        bells = VGroup(*[VMobject(stroke_color=c, stroke_width=4).set_points_smoothly(
            [[(x * s + m) * 0.8, np.exp(-x * x / 2) * 2.0 - 1.4, 0] for x in xs])
            for m, s, c in ((-1.2, 0.8, LBLUE), (0.0, 1.0, HILITE), (1.4, 1.5, RLGREEN))])
        q = txt(label("mle_best_curve_q"), size=38, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.5)
        with self.say("8.10"):
            self.play(LaggedStart(*[Create(b) for b in bells], lag_ratio=0.25), FadeIn(q), run_time=1.2)
        self.clear_all()


SCENES = ["S08Bernoulli", "S08Gaussian", "S08Classes", "S08HandsOn"]
