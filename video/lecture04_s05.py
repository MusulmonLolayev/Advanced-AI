"""Lecture 4, section 5 — the Beta: a density over one share, closing Part 0.

3 pastries in 10 orders → Beta(4, 8), mean 0.33 ± 0.13; 30 in 100 → Beta(31, 71), 0.30 ± 0.05; one more
pastry → Beta(5, 8), mean 5/13 ≈ 0.38 (the pause). Every curve is N's (capture_l04.py); beta_pdf here only
finds the height of the Beta(5, 8) curve at its mean, to end the dashed mean line on it.
Every number shown comes from N.
"""
from math import exp, lgamma, log

from lecture04_kit import *

FIRST, MORE, NEXT = N["beta"]["first"], N["beta"]["more"], N["beta_next"]
CLICKS = N["clicks"]
FIRST_C, MORE_C, NEXT_C = LBLUE, HILITE, RLGREEN


def beta_pdf(x, a, b):
    if x <= 0 or x >= 1:
        return 0.0
    return exp(lgamma(a + b) - lgamma(a) - lgamma(b) + (a - 1) * log(x) + (b - 1) * log(1 - x))


def beta_axes(y_max, y_step, x_len=8.6, y_len=3.6, numbers=True):
    return Axes(x_range=[0, 1, 0.1], y_range=[0, y_max, y_step], x_length=x_len, y_length=y_len, tips=False,
                axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 22},
                x_axis_config={"include_numbers": True, "numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1]},
                y_axis_config={"include_numbers": numbers})


def curve_from(ax, pts, color, width=5):
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly([ax.c2p(x, y) for x, y in pts])


def stats(name, b, color, size=34):
    return MathTex(rf"\mathrm{{Beta}}({b['a']}, {b['b']})", r":\ \ ", rf"{b['mean']:.2f} \pm {b['sd']:.2f}",
                   font_size=size, color=color)


class S05Question(LectureScene):
    def construct(self):
        self.section_card(5)
        # the Dirichlet held many shares; the Beta holds one
        many = VGroup(txt(label("dist_dirichlet"), size=34, weight=BOLD, color=GREY_B),
                      txt(label("many_shares"), size=24, color=GREY_B)).arrange(DOWN, buff=0.2)
        one = VGroup(txt(label("dist_beta"), size=34, weight=BOLD, color=HILITE),
                     txt(label("one_share"), size=24, color=HILITE)).arrange(DOWN, buff=0.2)
        VGroup(many, one).arrange(RIGHT, buff=3.0).move_to(UP * 0.4)
        arrow = Arrow(many.get_right(), one.get_left(), buff=0.4, color=GREY_B)
        with self.say("5.1") as (tr, t):
            self.play(FadeIn(many), run_time=0.7)
            self.cue(tr, t, {"en": "The two-answer case", "uz": "Ikki javobli holat"})
            self.play(GrowArrow(arrow), FadeIn(one, shift=LEFT * 0.3), run_time=0.8)
        self.clear_all()

        s, n = FIRST["successes"], FIRST["n"]
        # which of the ten held a pastry is a picture; only the count, 3, is data
        lit = {1, 4, 8}
        assert len(lit) == s
        orders = VGroup(*[RoundedRectangle(corner_radius=0.08, width=0.62, height=0.62, stroke_width=2.5,
                                           stroke_color=HILITE if i in lit else GREY_B,
                                           fill_color=HILITE if i in lit else BLACK, fill_opacity=0.8 if i in lit else 0)
                          for i in range(n)]).arrange(RIGHT, buff=0.25).move_to(UP * 2.0)
        lit_l = tagged(f"{s}/{n}", label("pastries_short"), size=26, color=HILITE).next_to(orders, DOWN, buff=0.3)
        p_lit = MathTex(rf"p = \tfrac{{{s}}}{{{n}}} = {dec(s / n)}", font_size=44, color=HILITE)
        line = NumberLine(x_range=[0, 1, 0.1], length=10, include_numbers=False, color=GREY_B).move_to(DOWN * 1.4)
        ends = VGroup(MathTex("0", font_size=28, color=GREY_B).next_to(line.n2p(0), DOWN, buff=0.2),
                      MathTex("1", font_size=28, color=GREY_B).next_to(line.n2p(1), DOWN, buff=0.2))
        p_lit.next_to(line.n2p(s / n), UP, buff=0.35)
        mark = Dot(line.n2p(s / n), radius=0.1, color=HILITE)
        others = N["beta_plausible"]
        alts = VGroup(*[VGroup(Dot(line.n2p(v), radius=0.08, color=GREY_B),
                               MathTex(rf"{dec(v)}\,?", font_size=30, color=GREY_B).next_to(line.n2p(v), DOWN, buff=0.25))
                        for v in others])
        with self.say("5.2") as (tr, t):
            self.cue(tr, t, {"en": "Three of the first ten", "uz": "Dastlabki oʻnta"})
            self.play(LaggedStart(*[FadeIn(o, scale=0.6) for o in orders], lag_ratio=0.06), FadeIn(lit_l), run_time=1.0)
            self.cue(tr, t, {"en": "Read literally", "uz": "Toʻgʻridan-toʻgʻri"})
            self.play(Create(line), FadeIn(ends), FadeIn(mark), Write(p_lit), run_time=0.9)
            self.cue(tr, t, {"en": "But on ten orders", "uz": "Lekin oʻnta buyurtmada"})
            self.play(LaggedStart(*[FadeIn(a, scale=0.7) for a in alts], lag_ratio=0.3), run_time=0.8)

        span = BraceBetweenPoints(line.n2p(0), line.n2p(1), UP, color=LBLUE, buff=0.9)
        sp_l = txt(label("the_share_p_unknown"), size=26, color=LBLUE).next_to(span, UP, buff=0.15)
        name = txt(label("dist_beta"), size=40, weight=BOLD, color=HILITE).next_to(line, DOWN, buff=1.1)
        with self.say("5.3") as (tr, t):
            self.play(FadeOut(orders), FadeOut(lit_l), FadeOut(p_lit), run_time=0.4)
            self.play(GrowFromCenter(span), FadeIn(sp_l), run_time=0.8)
            self.cue(tr, t, {"en": "That is the Beta", "uz": "Bu Beta taqsimoti"})
            self.play(FadeIn(name, scale=1.2), run_time=0.6)
        self.clear_all()


class S05Beta(LectureScene):
    def construct(self):
        peak = max(y for _, y in MORE["curve"])
        ax = beta_axes(round(peak) + 1, 3).move_to(DOWN * 0.8 + RIGHT * 0.3)
        xl = txt(label("the_share_p"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.5)
        c1 = curve_from(ax, FIRST["curve"], FIRST_C)
        c2 = curve_from(ax, MORE["curve"], MORE_C)
        s1 = VGroup(tagged(f"{FIRST['successes']}/{FIRST['n']}", label("pastries_short"), size=24, color=FIRST_C),
                    stats("first", FIRST, FIRST_C)).arrange(RIGHT, buff=0.5)
        s2 = VGroup(tagged(f"{MORE['successes']}/{MORE['n']}", label("pastries_short"), size=24, color=MORE_C),
                    stats("more", MORE, MORE_C)).arrange(RIGHT, buff=0.5)
        VGroup(s1, s2).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_edge(UP, buff=SAFE + 0.3)
        ab = VGroup(MathTex(r"\alpha", font_size=40, color=HILITE), txt(label("successes"), size=24, color=GREY_B),
                    MathTex(r"\beta", font_size=40, color=LBLUE), txt(label("failures"), size=24, color=GREY_B))
        ab = VGroup(VGroup(ab[0], ab[1]).arrange(RIGHT, buff=0.2), VGroup(ab[2], ab[3]).arrange(RIGHT, buff=0.2))
        ab.arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(ax.c2p(0.78, peak * 0.7))
        with self.say("5.4") as (tr, t):
            self.play(Create(ax), FadeIn(xl), FadeIn(ab), run_time=0.9)
            self.cue(tr, t, {"en": "Three of ten gives", "uz": "Oʻntadan uchta"})
            self.play(Create(c1), FadeIn(s1), run_time=1.0)
        with self.say("5.5") as (tr, t):
            self.cue(tr, t, {"en": "Thirty of a hundred", "uz": "Yuztadan oʻttizta"})
            self.play(Create(c2), FadeIn(s2), run_time=1.0)
            self.cue(tr, t, {"en": "The more data", "uz": "Berilganlar koʻpaygan sari"})
            self.play(Indicate(c2, color=WHITE, scale_factor=1.03), run_time=0.8)

        rule = VGroup(txt(label("one_more_pastry"), size=26, color=GREY_B),
                      MathTex(r"\alpha \;\to\; \alpha + 1", font_size=44, color=HILITE)).arrange(RIGHT, buff=0.4)
        upd = txt(label("updating_is_counting"), size=30, weight=BOLD, color=HILITE)
        VGroup(upd, rule).arrange(DOWN, buff=0.2).move_to(ax.c2p(0.72, peak * 0.42))
        ab_box = BackgroundRectangle(VGroup(upd, rule), color=BLACK, fill_opacity=0.9, buff=0.12)
        with self.say("5.6"):
            self.play(FadeOut(ab), FadeIn(ab_box), FadeIn(upd), FadeIn(rule), run_time=0.8)
        self.clear_all()


class S05AI(LectureScene):
    def construct(self):
        head = txt(label("click_rate_or_accuracy"), size=34, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        panels = VGroup()
        for c, color in zip(CLICKS, (FIRST_C, MORE_C)):
            pts = c["curve"]
            top = max(y for _, y in pts)
            ax = beta_axes(top * 1.1, top, x_len=5.4, y_len=2.8, numbers=False)
            curve = curve_from(ax, pts, color)
            tag = tagged(f"{c['correct']}/{c['n']}", label("correct_answers"), size=26, color=color)
            tag.next_to(ax, UP, buff=0.25)
            panels.add(VGroup(ax, curve, tag))
        panels.arrange(RIGHT, buff=1.0).move_to(DOWN * 0.4)
        later = txt(f"{label('lecture_6')}: {label('beta_prior_for_a_bernoulli')}", size=26, color=GREY_B)
        later.next_to(panels, DOWN, buff=0.7)
        with self.say("5.7") as (tr, t):
            self.play(FadeIn(head), run_time=0.5)
            self.cue(tr, t, {"en": "twelve correct", "uz": "oʻn beshtadan"})
            self.play(Create(panels[0][0]), Create(panels[0][1]), FadeIn(panels[0][2]), run_time=0.9)
            self.play(Create(panels[1][0]), Create(panels[1][1]), FadeIn(panels[1][2]), run_time=0.9)
            self.cue(tr, t, {"en": "In Lecture 6", "uz": "Oltinchi maʼruzada"})
            self.play(FadeIn(later), run_time=0.6)
        self.clear_all()


class S05HandsOn(LectureScene):
    def construct(self):
        card = pause_card([rf"Beta({FIRST['a']}, {FIRST['b']})", label("the_next_order_has_a_pastry"),
                           label("new_distribution_and_its_mean_q")])
        card.to_edge(UP, buff=SAFE + 0.3)
        with self.say("5.8"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        a, b = NEXT["a"], NEXT["b"]
        pts = NEXT["curve"]
        top = max(max(y for _, y in pts), max(y for _, y in FIRST["curve"]))
        ax = beta_axes(round(top) + 1, 1).move_to(DOWN * 0.9)
        xl = txt(label("the_share_p"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.5)
        old = curve_from(ax, FIRST["curve"], GREY_B, width=3)
        new = curve_from(ax, pts, NEXT_C)
        mean = DashedLine(ax.c2p(NEXT["mean"], 0), ax.c2p(NEXT["mean"], beta_pdf(NEXT["mean"], a, b)),
                          color=NEXT_C, stroke_width=3)
        res = MathTex(rf"\mathrm{{Beta}}({a}, {b}):\ \ \tfrac{{{a}}}{{{a + b}}} \approx {NEXT['mean']:.2f}",
                      font_size=44, color=NEXT_C).to_edge(UP, buff=SAFE + 0.4)
        with self.say("5.9") as (tr, t):
            self.play(Create(ax), FadeIn(xl), Create(old), run_time=0.8)
            self.play(TransformFromCopy(old, new), Write(res), run_time=1.0)
            self.cue(tr, t, {"en": "The mean is", "uz": "Oʻrtacha"})
            self.play(Create(mean), run_time=0.6)
        self.clear_all()

        # Part 0 closes on the shape Part 1 is about
        mu, sigma = N["mu"], N["sigma"]
        pts = [[(x - mu) / sigma * 1.1, y * sigma * 7.0, 0] for x, y in N["normal_curve"]]
        bell = VMobject(stroke_color=HILITE, stroke_width=5).set_points_smoothly(pts).move_to(DOWN * 0.6)
        b_lab = txt(label("the_bell_curve"), size=30, color=HILITE).next_to(bell, DOWN, buff=0.35)
        nxt = txt(PARTS[1], size=34, weight=BOLD).to_edge(UP, buff=SAFE + 0.6)
        with self.say("5.10") as (tr, t):
            self.cue(tr, t, {"en": "One shape", "uz": "Bitta shakl"})
            self.play(Create(bell), FadeIn(b_lab), run_time=1.2)
            self.cue(tr, t, {"en": "In part one", "uz": "Birinchi qismda"})
            self.play(FadeIn(nxt, shift=DOWN * 0.2), run_time=0.7)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S05Question", "S05Beta", "S05AI", "S05HandsOn"]
