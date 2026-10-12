"""Lecture 1, section 2 — population and sample.

The 600 dots are the 600 real salaries (statistics/raw/v01_salaries.txt); the cloud
around them is a drawing of the population, which by definition we never see. The five
salaries and their sums come from capture_l01.py (l01_numbers.json).
"""
from lecture01_kit import *
from lecture01_s04 import hist_axis, hist_dots

FIVE = L["five"]
assert FIVE == [31, 45, 47, 52, 88] and L["five_sum"] == 263
assert (L["x2"], L["x1_plus_x5"]) == (45, 119)
assert len(SAL) == 600


def cloud(center, width, height, n, seed=3, radius=0.022, opacity=0.35):
    """Faint grey dots filling an ellipse: the population we cannot measure."""
    rng = np.random.default_rng(seed)
    r = np.sqrt(rng.uniform(0, 1, n))
    th = rng.uniform(0, 2 * np.pi, n)
    pts = np.c_[r * np.cos(th) * width / 2, r * np.sin(th) * height / 2, np.zeros(n)] + np.array(center)
    return VGroup(*[Dot(p, radius=radius, color=GREY_B, fill_opacity=opacity) for p in pts])


def five_cards(y=0.9, step=2.2, size=48):
    cards = VGroup()
    for i, v in enumerate(FIVE):
        rect = RoundedRectangle(corner_radius=0.14, width=1.6, height=1.3, stroke_color=RLBLUE,
                                stroke_width=3, fill_color=BLACK, fill_opacity=0.6)
        num = txt(str(v), size=size, weight=BOLD).move_to(rect)
        cards.add(VGroup(rect, num).move_to([(i - 2) * step, y, 0]))
    return cards


def sub_labels(cards):
    return VGroup(*[MathTex(f"x_{i + 1}", font_size=46, color=RLGREEN).next_to(c, DOWN, buff=0.25)
                    for i, c in enumerate(cards)])


class S02Population(LectureScene):
    def construct(self):
        self.section_card(2)
        dots, axis = hist_dots(), hist_axis()
        fog = cloud([0, -0.1, 0], 12.4, 6.6, 2600)
        rim = Ellipse(width=12.6, height=6.8, color=GREY_B, stroke_width=2).move_to([0, -0.1, 0])
        rim.set_stroke(opacity=0.5)

        with self.say("2.1") as (tr, t):
            self.play(FadeIn(axis), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.002), run_time=1.6)
            self.cue(tr, t, 1)
            self.play(FadeOut(axis), dots.animate.scale(0.26).move_to([1.4, -1.0, 0]), run_time=1.6)
            self.play(FadeIn(fog, lag_ratio=0.0005), run_time=1.6)

        pop = txt(label("population"), size=40, weight=BOLD, color=GREY_A)
        pop.move_to([-3.0, 1.9, 0])
        with self.say("2.2") as (tr, t):
            self.cue(tr, t, 1)
            self.play(Create(rim), FadeIn(pop, shift=UP * 0.2), run_time=1.2)

        ring = Ellipse(width=dots.width + 0.5, height=dots.height + 0.5, color=RLBLUE, stroke_width=4)
        ring.move_to(dots)
        smp = txt(label("sample"), size=36, weight=BOLD, color=RLBLUE)
        smp.next_to(ring, RIGHT, buff=0.4)
        n_lab = tagged(len(SAL), label("salaries"), size=24, color=GREY_B).next_to(smp, DOWN, buff=0.15)
        with self.say("2.3") as (tr, t):
            self.play(Create(ring), FadeIn(smp, shift=LEFT * 0.2), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(FadeIn(n_lab), Indicate(dots, color=HILITE, scale_factor=1.15), run_time=1.2)
        self.clear_all()


class S02Notation(LectureScene):
    def construct(self):
        cards = five_cards()
        unit = txt(label("salaries_thousand"), size=26, color=GREY_B)
        unit.next_to(cards, UP, buff=0.5)
        with self.say("2.4") as (tr, t):
            self.play(LaggedStart(*[FadeIn(c[0], scale=0.8) for c in cards], lag_ratio=0.15), run_time=1.2)
            self.cue(tr, t, 1)
            self.play(FadeIn(unit), run_time=0.6)
            self.cue(tr, t, 2)
            self.play(LaggedStart(*[FadeIn(c[1], shift=DOWN * 0.2) for c in cards], lag_ratio=0.35), run_time=2.2)

        subs = sub_labels(cards)
        n_eq = MathTex("n", "=", str(len(FIVE)), font_size=60).move_to([0, -1.6, 0])
        n_eq[0].set_color(HILITE)
        with self.say("2.5") as (tr, t):
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[Write(s) for s in subs], lag_ratio=0.3), run_time=2.0)
            self.cue(tr, t, 2)
            self.play(FadeIn(n_eq, shift=UP * 0.2), run_time=0.8)

        x3 = MathTex("x_3", "=", str(FIVE[2]), font_size=52).move_to([-2.2, -2.6, 0])
        x5 = MathTex("x_5", "=", str(FIVE[4]), font_size=52).move_to([2.2, -2.6, 0])
        with self.say("2.6") as (tr, t):
            self.play(cards[2][0].animate.set_stroke(HILITE, width=6), subs[2].animate.set_color(HILITE),
                      FadeIn(x3), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(cards[4][0].animate.set_stroke(HILITE, width=6), subs[4].animate.set_color(HILITE),
                      FadeIn(x5), run_time=0.8)

        long = MathTex("x_1", "+", "x_2", "+", "x_3", "+", "x_4", "+", "x_5", font_size=60).move_to([0, -1.9, 0])
        sigma = MathTex(r"\sum_{i=1}^{n} x_i", font_size=66).move_to([-1.2, -1.9, 0])
        with self.say("2.7") as (tr, t):
            self.play(FadeOut(n_eq), FadeOut(x3), FadeOut(x5),
                      cards[2][0].animate.set_stroke(RLBLUE, width=3), cards[4][0].animate.set_stroke(RLBLUE, width=3),
                      subs[2].animate.set_color(RLGREEN), subs[4].animate.set_color(RLGREEN), run_time=0.6)
            self.play(TransformFromCopy(subs, VGroup(*[long[i] for i in range(0, 9, 2)])),
                      FadeIn(VGroup(*[long[i] for i in range(1, 9, 2)])), run_time=1.4)
            self.cue(tr, t, 1)
            self.play(ReplacementTransform(long, sigma), run_time=1.4)

        total = MathTex("=", "+".join(map(str, FIVE)), "=", str(L["five_sum"]), font_size=56)
        total.next_to(sigma, RIGHT, buff=0.3)
        VGroup(sigma, total).set_x(0)          # sigma lands where the whole line will be centred
        total[3].set_color(HILITE)
        with self.say("2.8"):
            self.play(FadeIn(total[:2]), run_time=0.8)
            self.play(FadeIn(total[2:], scale=1.2), run_time=0.8)
        self.clear_all()


class S02Symbols(LectureScene):
    def construct(self):
        fog = cloud([-3.6, 0.1, 0], 6.0, 4.4, 900, seed=5, radius=0.02)
        rim = Ellipse(width=6.2, height=4.6, color=GREY_B, stroke_width=2).move_to([-3.6, 0.1, 0]).set_stroke(opacity=0.5)
        dots = hist_dots().scale(0.15).move_to([-3.0, -0.6, 0])
        ring = Ellipse(width=dots.width + 0.35, height=dots.height + 0.35, color=RLBLUE, stroke_width=3).move_to(dots)
        pop = txt(label("population"), size=30, weight=BOLD, color=GREY_A).next_to(rim, UP, buff=0.2)
        smp = txt(label("sample"), size=28, weight=BOLD, color=RLBLUE).next_to(ring, DOWN, buff=0.25)

        cx_s, cx_p, y0 = 2.5, 4.9, 1.7
        div = Line([3.4, y0 + 0.3, 0], [3.4, -2.0, 0], color=GREY_D, stroke_width=2)
        h_s = txt(label("sample"), size=32, color=RLBLUE).move_to([cx_s, y0, 0])
        h_p = txt(label("population"), size=32, color=GREY_A).move_to([cx_p, y0, 0])
        latin = VGroup(MathTex(r"\bar{x}", font_size=96), MathTex("s", font_size=96)).arrange(DOWN, buff=0.7)
        greek = VGroup(MathTex(r"\mu", font_size=96), MathTex(r"\sigma", font_size=96)).arrange(DOWN, buff=0.7)
        # headers hug the divider, so a long label never crosses it
        h_s.next_to(div, LEFT, buff=0.3).set_y(y0)
        h_p.next_to(div, RIGHT, buff=0.3).set_y(y0)
        latin.set_color(RLBLUE).move_to([h_s.get_x(), -0.2, 0])
        greek.set_color(HILITE).move_to([h_p.get_x(), -0.2, 0])

        with self.say("2.9") as (tr, t):
            self.play(FadeIn(fog), Create(rim), FadeIn(dots), Create(ring), FadeIn(pop), FadeIn(smp), run_time=1.2)
            self.cue(tr, t, 1)
            self.play(FadeIn(h_s), Create(div), FadeIn(h_p), run_time=0.6)
            self.cue(tr, t, 2)
            self.play(FadeIn(latin, shift=UP * 0.2), Indicate(ring, color=RLBLUE), run_time=1.0)
            self.cue(tr, t, 4)
            self.play(FadeIn(greek, shift=UP * 0.2), Indicate(rim, color=HILITE, scale_factor=1.0), run_time=1.0)

        smp2 = txt(label("training_set"), size=28, weight=BOLD, color=RLBLUE).move_to(smp)
        pop2 = txt(label("the_whole_world"), size=30, weight=BOLD, color=GREY_A).move_to(pop)
        tag_s = txt(f"= {label("sample")}", size=22, color=RLBLUE).next_to(smp2, DOWN, buff=0.1)
        tag_p = txt(f"= {label("population")}", size=22, color=GREY_A).next_to(pop2, RIGHT, buff=0.2)
        gap = DoubleArrow(ring.get_left() + LEFT * 0.05, rim.get_left() + RIGHT * 0.25, buff=0.05,
                          color=RLRED, stroke_width=4, tip_length=0.2)
        with self.say("2.10") as (tr, t):
            self.play(FadeTransform(smp, smp2), FadeIn(tag_s), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeTransform(pop, pop2), FadeIn(tag_p), run_time=0.8)
            self.cue(tr, t, {"en": 3, "uz": 2})
            self.play(GrowArrow(gap), run_time=0.8)
        self.clear_all()


class S02HandsOn(LectureScene):
    def construct(self):
        cards = five_cards(y=-1.2, step=1.9, size=40).scale(0.85)
        subs = sub_labels(cards)
        card_ = pause_card([label("x_q"), label("x_x_q")]).to_edge(UP, buff=SAFE + 0.3)
        with self.say("2.11"):
            self.play(FadeIn(card_), FadeIn(cards), FadeIn(subs), run_time=1.0)
        self.hands_on()

        a1 = MathTex("x_2", "=", str(L["x2"]), font_size=56)
        a2 = MathTex("x_1", "+", "x_5", "=", str(FIVE[0]), "+", str(FIVE[4]), "=", str(L["x1_plus_x5"]), font_size=56)
        VGroup(a1, a2).arrange(DOWN, buff=0.5).move_to([0, 1.6, 0])
        a1[2].set_color(HILITE)
        a2[8].set_color(HILITE)
        with self.say("2.12") as (tr, t):
            self.play(FadeOut(card_), run_time=0.5)
            self.play(cards[1][0].animate.set_stroke(HILITE, width=6), FadeIn(a1), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(cards[1][0].animate.set_stroke(RLBLUE, width=3),
                      cards[0][0].animate.set_stroke(HILITE, width=6), cards[4][0].animate.set_stroke(HILITE, width=6),
                      FadeIn(a2[:8]), run_time=1.0)
            self.play(FadeIn(a2[8], scale=1.3), run_time=0.6)
        self.clear_all()

        dots, axis = hist_dots(), hist_axis()
        q = txt("?", size=96, weight=BOLD, color=HILITE).move_to([0, 1.6, 0])
        with self.say("2.13") as (tr, t):
            self.play(FadeIn(axis), FadeIn(dots, lag_ratio=0.002), run_time=1.4)
            self.cue(tr, t, 1)
            self.play(FadeIn(q, scale=0.5), run_time=0.8)
        self.clear_all()


SCENES = ["S02Population", "S02Notation", "S02Symbols", "S02HandsOn"]
