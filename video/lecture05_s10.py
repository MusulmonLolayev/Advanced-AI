"""Lecture 5, section 10 — the default losses are negative log-likelihoods, then the lecture close.

The regression points and the outlier are an illustration, marked so. The hands-on loss and every
summary icon come from l05_numbers.json (the -log p curve is the formula itself).
"""
import numpy as np
from lecture05_kit import *


def underbrace_label(mob, text, color=GREY_B, size=22):
    b = Brace(mob, DOWN, buff=0.08, color=color)
    t = txt(text, size=size, color=color).next_to(b, DOWN, buff=0.1)
    return VGroup(b, t)


class S10CrossEntropy(LectureScene):
    def construct(self):
        self.section_card(10)
        box = RoundedRectangle(corner_radius=0.12, width=2.8, height=0.9, color=LBLUE, stroke_width=3)
        cls = VGroup(box, txt(label("classifier"), size=26, color=LBLUE).move_to(box))
        out = MathTex(r"p_i", font_size=48, color=HILITE)
        arrow = Arrow(LEFT * 0.6, RIGHT * 0.6, buff=0, color=GREY_B, stroke_width=3)
        row = VGroup(cls, arrow, out).arrange(RIGHT, buff=0.3).move_to([-3.2, 2.0, 0])
        chance = txt(label("mle_predicted_chance"), size=22, color=GREY_B).next_to(out, DOWN, buff=0.15)
        ys = VGroup(MathTex(r"y_i \in \{0, 1\}", font_size=40),
                    txt(label("mle_labels"), size=22, color=GREY_B),
                    txt(label("dist_bernoulli"), size=26, weight=BOLD, color=HILITE)).arrange(DOWN, buff=0.12)
        ys.move_to([3.4, 2.0, 0])
        lik = MathTex(r"L = \prod_{i=1}^{n} p_i^{\,y_i}(1-p_i)^{1-y_i}", font_size=40).move_to(UP * 0.35)
        nll = MathTex(r"-\ell", "=", r"-\sum_{i=1}^{n}\Big[y_i \log p_i + (1-y_i)\log(1-p_i)\Big]", font_size=42)
        nll.next_to(lik, DOWN, buff=0.45)
        with self.say("10.1") as (tr, t):
            self.play(FadeIn(row), FadeIn(chance), run_time=0.8)
            self.play(FadeIn(ys), run_time=0.6)
            self.cue(tr, t, {"en": "We write down", "uz": "Haqiqatga oʻxshashlikning minus"})
            self.play(Write(lik), run_time=0.7)
            self.play(Write(nll), run_time=0.8)

        bce = underbrace_label(nll[2], label("mle_binary_cross_entropy"), color=HILITE, size=26)
        frame = txt(label("mle_in_every_framework"), size=22, color=GREY_B).next_to(bce, DOWN, buff=0.2)
        exact = txt(label("mle_not_approximately"), size=24, weight=BOLD, color=HILITE).next_to(frame, DOWN, buff=0.15)
        with self.say("10.2") as (tr, t):
            self.play(FadeIn(bce), FadeIn(frame), run_time=0.9)
            self.cue(tr, t, {"en": "Not approximately", "uz": "Taxminan emas"})
            self.play(FadeIn(exact, shift=UP * 0.2), run_time=0.5)

        cat = MathTex(r"-\ell = -\sum_{i=1}^{n}\sum_{c=1}^{k} y_{ic}\log p_{ic}", font_size=42).move_to(nll)
        cat_l = VGroup(txt(label("dist_categorical"), size=26, weight=BOLD, color=HILITE),
                       txt(label("mle_categorical_cross_entropy"), size=24, color=HILITE)).arrange(DOWN, buff=0.12)
        cat_l.next_to(cat, DOWN, buff=0.4)
        with self.say("10.3"):
            self.play(FadeOut(VGroup(bce, frame, exact)), ReplacementTransform(nll, cat), run_time=0.9)
            self.play(Transform(ys[2], txt(label("dist_categorical"), size=26, weight=BOLD, color=HILITE).move_to(ys[2])),
                      FadeIn(cat_l), run_time=0.7)
        self.clear_all()


class S10Squared(LectureScene):
    def construct(self):
        rng = np.random.default_rng(5)                          # an illustration: made-up regression points
        xs = np.linspace(-4.6, -0.6, 14)
        line_y = lambda x: 0.45 * x + 1.4
        pts = [(x, line_y(x) + rng.normal(0, 0.28)) for x in xs]
        fit = Line([-4.9, line_y(-4.9), 0], [-0.3, line_y(-0.3), 0], color=LBLUE, stroke_width=3)
        dots = VGroup(*[Dot([x, y, 0], radius=0.06, color=GREY_A) for x, y in pts])
        res = VGroup(*[Line([x, line_y(x), 0], [x, y, 0], stroke_width=2, color=RLRED) for x, y in pts])
        model = txt(label("mle_regression_model"), size=26, weight=BOLD, color=LBLUE).move_to([-2.6, 2.6, 0])
        bs = np.linspace(-3, 3, 61)
        bell = VMobject(stroke_color=HILITE, stroke_width=3).set_points_smoothly(
            [[0.35 * np.exp(-b * b / 2) * 1.2, b * 0.2, 0] for b in bs]).move_to([-0.15, line_y(-0.6), 0])
        normal = txt(label("mle_residuals_normal"), size=22, color=HILITE).next_to(VGroup(dots, fit), DOWN, buff=0.3)
        note = info(label("illustration"))
        nll = MathTex(r"-\ell", "=", r"\frac{n}{2}\log(2\pi\sigma^2)", "+",
                      r"\frac{1}{2\sigma^2}\sum_{i=1}^{n}\big(y_i - f(x_i)\big)^2", font_size=36)
        if nll.width > 5.6:
            nll.scale_to_fit_width(5.6)
        nll.move_to([3.6, 1.0, 0])                               # clear of the residuals' bell on the left
        c1 = underbrace_label(nll[2], label("mle_a_constant"), size=22)
        c2 = underbrace_label(nll[4], label("mle_multiple_of_mse"), color=HILITE, size=22)
        for c, w in ((c1, 3.0), (c2, 4.6)):
            if c[1].width > w:
                c[1].scale_to_fit_width(w)
                c[1].next_to(c[0], DOWN, buff=0.1)
        c2[1].next_to(c2[0], DOWN, buff=0.5)                      # a row below the constant's caption
        if c2[1].get_right()[0] > 6.4:
            c2[1].shift(LEFT * (c2[1].get_right()[0] - 6.4))
        with self.say("10.4") as (tr, t):
            self.play(FadeIn(model), Create(fit), FadeIn(dots), FadeIn(note), run_time=0.9)
            self.play(LaggedStart(*[Create(r) for r in res], lag_ratio=0.05), Create(bell), FadeIn(normal), run_time=0.9)
            self.cue(tr, t, {"en": "Minus the log-likelihood", "uz": "Minus logarifmik"})
            self.play(Write(nll), run_time=0.9)
            self.play(FadeIn(c1), FadeIn(c2), run_time=0.6)
        self.clear_all()

        head = VGroup(txt(label("mle_two_losses_one_idea"), size=34, weight=BOLD, color=LBLUE),
                      txt(label("mle_minus_log_likelihood_assumed"), size=24, color=GREY_B)).arrange(DOWN, buff=0.15)
        head.to_edge(UP, buff=SAFE + 0.3)
        if head.width > 12.4:
            head.scale_to_fit_width(12.4)

        def pairing(dist, loss, color):
            a = txt(dist, size=26, weight=BOLD, color=color)
            b = txt(loss, size=26, color=color)
            return VGroup(a, MathTex(r"\to", font_size=40, color=GREY_B), b).arrange(RIGHT, buff=0.3)

        pairs = VGroup(pairing(f"{label('dist_bernoulli')} · {label('dist_categorical')}", label("mle_cross_entropy"), HILITE),
                       pairing(label("mle_normal"), label("mle_squared_error"), RLGREEN)).arrange(DOWN, buff=0.4)
        pairs.next_to(head, DOWN, buff=0.5)
        # an outlier pulls the squared error: its square dwarfs the others
        base = Line([-3.0, -2.4, 0], [3.0, -2.4, 0], color=LBLUE, stroke_width=3)
        small = VGroup(*[Square(0.18 + 0.06 * k, stroke_width=0, fill_color=GREY_B, fill_opacity=0.6)
                         .move_to([-2.4 + 0.7 * k, -2.4 + (0.09 + 0.03 * k), 0]) for k in range(4)])
        big = Square(1.6, stroke_width=0, fill_color=RLRED, fill_opacity=0.7).move_to([1.8, -2.4 + 0.8, 0])
        out = Dot(big.get_corner(UR), radius=0.08, color=RLRED)
        chase = txt(label("mle_chases_outliers"), size=24, color=RLRED).next_to(big, LEFT, buff=0.3).shift(UP * 0.3)
        note2 = info(label("illustration"))
        with self.say("10.5") as (tr, t):
            self.play(FadeIn(head), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in pairs], lag_ratio=0.3), run_time=1.0)
            self.cue(tr, t, {"en": "Squared error assumes", "uz": "Kvadratik xato normal"})
            self.play(Create(base), FadeIn(small), FadeIn(note2), run_time=0.6)
            self.play(GrowFromPoint(big, big.get_corner(DL)), FadeIn(out), FadeIn(chase), run_time=0.8)
        self.clear_all()


class S10Training(LectureScene):
    def construct(self):
        layers = [3, 4, 2]
        nodes = VGroup(*[VGroup(*[Circle(radius=0.14, color=GREY_B, stroke_width=2) for _ in range(k)])
                         .arrange(DOWN, buff=0.3) for k in layers]).arrange(RIGHT, buff=1.0).move_to([-4.2, 1.2, 0])
        edges = VGroup(*[Line(a.get_right(), b.get_left(), stroke_width=1, color=GREY_D)
                         for l1, l2 in zip(nodes, nodes[1:]) for a in l1 for b in l2])
        nof = txt(label("mle_no_formula"), size=24, color=RLRED).next_to(nodes, DOWN, buff=0.3)
        ell = MathTex(r"\ell(\theta) = \sum_{i} \log p(x_i \mid \theta)", font_size=42).move_to([2.6, 2.2, 0])
        sum_l = txt(label("mle_sum_over_examples"), size=22, color=GREY_B).next_to(ell, DOWN, buff=0.15)
        step = MathTex(r"\theta \;\leftarrow\; \theta + \eta\, \nabla_\theta\, \ell", font_size=42, color=HILITE)
        step.next_to(sum_l, DOWN, buff=0.4)
        se = MathTex(r"\mathrm{SE} = \frac{\sigma_g}{\sqrt{B}}", font_size=42, color=LBLUE).next_to(step, DOWN, buff=0.4)
        mb = txt(label("mle_mini_batch"), size=22, color=LBLUE).next_to(se, LEFT, buff=0.3)
        what = txt(label("mle_what_to_optimise"), size=24, weight=BOLD, color=HILITE)
        why = txt(label("mle_why_a_few_examples"), size=24, weight=BOLD, color=LBLUE)
        tags = VGroup(what, why).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([0, -2.6, 0])
        if tags.width > 12.4:
            tags.scale_to_fit_width(12.4)
        with self.say("10.6") as (tr, t):
            self.play(Create(edges), FadeIn(nodes), FadeIn(nof), run_time=0.8)
            self.play(Write(ell), FadeIn(sum_l), run_time=0.8)
            self.cue(tr, t, {"en": "So we step along", "uz": "Shuning uchun gradient"})
            self.play(FadeIn(step), run_time=0.6)
            self.play(FadeIn(se), FadeIn(mb), run_time=0.6)
            self.cue(tr, t, {"en": "maximum likelihood says", "uz": "maksimal haqiqatga oʻxshashlik nimani"})
            self.play(FadeIn(what, shift=UP * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": "and the central limit theorem", "uz": "markaziy limit teoremasi esa"})
            self.play(FadeIn(why, shift=UP * 0.2), run_time=0.5)
        self.clear_all()


class S10HandsOn(LectureScene):
    def construct(self):
        y, p = N["ce_y"], N["ce_p"]
        card = pause_card([f"y = {y},   p = {dec(p, 1)}", "−[ y log p + (1 − y) log(1 − p) ] = ?"])
        with self.say("10.7"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 3, 1], x_length=6.0, y_length=3.2, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 22, "include_numbers": True},
                  x_axis_config={"decimal_number_config": {"num_decimal_places": 2}}).move_to([-2.4, -0.6, 0])
        curve = ax.plot(lambda q: -np.log(q), x_range=[0.05, 1.0], color=LBLUE, stroke_width=4)
        xl = MathTex("p", font_size=34, color=GREY_B).next_to(ax.x_axis, RIGHT, buff=0.2)
        yl = MathTex(r"-\log p", font_size=34, color=GREY_B).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        dot = Dot(ax.c2p(p, N["ce_loss"]), radius=0.1, color=HILITE)
        ans = MathTex(rf"-\log {dec(p, 1)} \approx {dec(N['ce_loss'], 3)}", font_size=56, color=HILITE).move_to([3.6, 1.2, 0])
        good = txt(label("mle_confident_and_right"), size=26, color=GREY_B).next_to(ans, DOWN, buff=0.35)
        if good.width > 5.6:
            good.scale_to_fit_width(5.6)
        with self.say("10.8") as (tr, t):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), Create(curve), run_time=0.9)
            self.play(FadeIn(dot, scale=1.5), Write(ans), run_time=0.8)
            self.cue(tr, t, {"en": "The model is confident", "uz": "Model ishonchli"})
            self.play(FadeIn(good, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S10Summary(LectureScene):
    def construct(self):
        head = self.heading(label("lecture_5_summary"), color=LBLUE)

        def poly(points, sx, sy, color=LBLUE):
            return VMobject(stroke_color=color, stroke_width=3).set_points_smoothly([[x * sx, y * sy, 0] for x, y in points])

        def icon_se():
            return poly(N["se_curve"][:120], 0.006, 1.0)

        def icon_clt():
            s = N["sampling"]["30"]
            k = 0.5 / max(s["probs"])
            return VGroup(*[Rectangle(width=0.02, height=max(p * k, 1e-3), stroke_width=0, fill_color=HILITE,
                                      fill_opacity=1).move_to([m * 0.9, p * k / 2, 0])
                            for m, p in zip(s["means"], s["probs"]) if p > 1e-3])

        def icon_likelihood():
            return poly(N["lik_curve"], 1.6, 0.4, HILITE)

        def icon_estimates():
            f = N["fits"]["mle"]
            xs = np.linspace(f["mu"] - 4 * f["sigma"], f["mu"] + 4 * f["sigma"], 61)
            return poly([[x, np.exp(-(x - f["mu"]) ** 2 / (2 * f["sigma"] ** 2))] for x in xs], 0.1, 0.45)

        def icon_losses():
            return poly([[q, -np.log(q)] for q in np.linspace(0.06, 1.0, 40)], 0.7, 0.18, RLGREEN)

        def rows_of(items):
            rows = VGroup()
            for icon, text in items:
                ic = icon()
                if ic.height > 0.5:
                    ic.scale_to_fit_height(0.5)
                if ic.width > 0.7:
                    ic.scale_to_fit_width(0.7)
                slot = VGroup(Square(0.75, stroke_width=0), ic)
                ic.move_to(slot[0])
                # a long row breaks after its "; ", so the text keeps its size
                words = VGroup(*[txt(part, size=26) for part in text.split("; ")]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
                rows.add(VGroup(slot, words).arrange(RIGHT, buff=0.35))
            rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT).next_to(head, DOWN, buff=0.6)
            if rows.width > 12.4:
                rows.scale_to_fit_width(12.4)
            return rows.set_x(0)

        part0 = rows_of([(icon_se, label("l05_summary_sample_mean")), (icon_clt, label("l05_summary_clt"))])
        with self.say("10.9") as (tr, t):
            self.play(FadeIn(head), run_time=0.6)
            self.play(FadeIn(part0[0], shift=RIGHT * 0.3), run_time=0.6)
            self.cue(tr, t, {"en": "The central limit theorem:", "uz": "Markaziy limit teoremasi:"})
            self.play(FadeIn(part0[1], shift=RIGHT * 0.3), run_time=0.6)
        self.play(FadeOut(part0), run_time=0.4)

        part1 = rows_of([(icon_likelihood, label("l05_summary_likelihood")),
                         (icon_estimates, label("l05_summary_estimates")),
                         (icon_losses, label("l05_summary_losses"))])
        with self.say("10.10") as (tr, t):
            self.play(FadeIn(part1[0], shift=RIGHT * 0.3), run_time=0.6)
            self.cue(tr, t, {"en": "For a Bernoulli", "uz": "Bernulli uchun"})
            self.play(FadeIn(part1[1], shift=RIGHT * 0.3), run_time=0.6)
            self.cue(tr, t, {"en": "Cross-entropy and squared error", "uz": "Kross-entropiya va kvadratik"})
            self.play(FadeIn(part1[2], shift=RIGHT * 0.3), run_time=0.6)
        self.clear_all()

        end = VGroup(txt(label("lecture_5"), size=56, weight=BOLD, color=RLBLUE),
                     txt(label("the_end"), size=34, color=GREY_B)).arrange(DOWN, buff=0.3).move_to(UP * 0.4)
        title6 = txt(label("lecture_6_bayesian_inference"), size=40, weight=BOLD, color=LBLUE)
        if title6.width > 12.4:
            title6.scale_to_fit_width(12.4)
        nxt = VGroup(txt(label("next"), size=28, color=GREY_B), title6,
                     MathTex(r"p(\theta \mid x) \;\propto\; p(x \mid \theta)\, p(\theta)", font_size=60,
                             color=HILITE)).arrange(DOWN, buff=0.4)
        with self.say("10.11") as (tr, t):
            self.play(FadeIn(end, shift=UP * 0.3), run_time=0.9)
            self.cue(tr, t, {"en": "In the next lecture", "uz": "Keyingi maʼruzada"})
            self.play(FadeOut(end), FadeIn(nxt, shift=UP * 0.3), run_time=1.0)
        self.play(FadeOut(nxt), run_time=0.6)
        self.play(FadeIn(brand_outro()), run_time=1.0)
        self.wait(2.0)
        self.clear_all(run_time=0.6)


SCENES = ["S10CrossEntropy", "S10Squared", "S10Training", "S10HandsOn", "S10Summary"]
