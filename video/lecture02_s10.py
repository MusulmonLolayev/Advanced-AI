"""Lecture 2, section 10 — base rates; where Bayes goes next; the lecture's summary and close."""
import numpy as np
from lecture02_kit import *

S1, S1000 = N["screen"], N["screen_1in1000"]
MARKS = N["base_marks"]                       # base rate → P(ill | positive)
ACC = N["acc_always_healthy"]
ILL_C, WELL_C = RLRED, "#2F5557"


def pct(x, nd=0):
    return f"{100 * x:.{nd}f}%"


def cells_image(total, ill, cols, height, ill_c=ILL_C, well_c=WELL_C):
    """total people as one bitmap, one cell each, the ill first."""
    rows = total // cols
    hexrgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
    colours = np.empty((total, 3), dtype=np.uint8)
    colours[:] = hexrgb(well_c)
    colours[:ill] = hexrgb(ill_c)
    k, gap = 24, 4                     # fine enough to scale smoothly without moiré
    img = np.zeros((rows * k, cols * k, 3), dtype=np.uint8)
    grid = colours.reshape(rows, cols, 3)
    for dy in range(k - gap):
        for dx in range(k - gap):
            img[dy::k, dx::k] = grid
    m = ImageMobject(img)
    m.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
    m.set_height(height)
    return m


def one_in(s):
    return s["tested"] // s["ill"]


class S10Curve(LectureScene):
    def construct(self):
        self.section_card(10)
        ill, pos = label("ill"), label("positive")
        f = MathTex(rf"P(\text{{{ill}}} \mid \text{{{pos}}})", "=", rf"P(\text{{{pos}}} \mid \text{{{ill}}})",
                    r"\cdot", rf"P(\text{{{ill}}})", "/", rf"P(\text{{{pos}}})", font_size=46)
        f.move_to(UP * 1.0)
        prior_box = SurroundingRectangle(f[4], color=HILITE, buff=0.12)
        prior_l = txt(label("base_rate_the_prior"), size=30, color=HILITE)
        prior_l.next_to(prior_box, DOWN, buff=0.5)
        with self.say("10.1") as (tr, t):
            self.play(Write(f), run_time=1.2)
            self.play(Create(prior_box), run_time=0.5)
            self.cue(tr, t, {"en": "It is the prior", "uz": "Bu Bayes"})
            self.play(FadeIn(prior_l, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        # the same test at every base rate
        ax = Axes(x_range=[0, 20, 5], y_range=[0, 100, 25], x_length=8.0, y_length=4.6, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2, "include_numbers": True, "font_size": 24})
        ax.move_to(DOWN * 0.35 + RIGHT * 0.3)
        xl = txt(label("how_common_the_disease_is_percent"), size=24, color=GREY_B)
        xl.next_to(ax.x_axis, DOWN, buff=0.45)
        yl = txt(label("p_ill_positive_percent"), size=24, color=GREY_B)
        yl.next_to(ax, UP, buff=0.2).align_to(ax, LEFT).shift(LEFT * 0.4)
        xs = [100 * p for p, _ in N["base_curve"]]
        ys = [100 * y for _, y in N["base_curve"]]
        curve = ax.plot_line_graph(xs, ys, add_vertex_dots=False, line_color=LBLUE, stroke_width=4)["line_graph"]
        fixed = txt(label("same_test_throughout"), size=26, color=LBLUE).move_to(ax.c2p(14, 30))
        with self.say("10.2") as (tr, t):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.play(Create(curve), FadeIn(fixed), run_time=1.8)

        # three base rates, read off the curve
        marks = VGroup()
        offs = {"0.001": RIGHT * 2.4 + UP * 0.45, "0.01": RIGHT * 2.2 + UP * 0.75, "0.1": RIGHT * 1.0 + DOWN * 0.9}
        for k, v in MARKS.items():
            p = ax.c2p(100 * float(k), 100 * v)
            d = Dot(p, radius=0.09, color=HILITE)
            lab = VGroup(txt(label("1_in_n", n=round(1 / float(k))), size=22, color=GREY_B),
                         txt(pct(v), size=30, weight=BOLD, color=HILITE)).arrange(DOWN, buff=0.08).move_to(p + offs[k])
            lab.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06)   # the curve must not cross the text
            marks.add(VGroup(d, lab, Line(d.get_center(), lab.get_center(), color=GREY_D, stroke_width=1.5)
                             .scale(0.55)))
        with self.say("10.3") as (tr, t):
            for i, (k, cue) in enumerate(zip(MARKS, [{"en": "At one in a thousand", "uz": "Ming kishidan"},
                                                    {"en": "At one in a hundred", "uz": "Yuzdan bittada"},
                                                    {"en": "At one in ten", "uz": "Oʻndan bittada"}])):
                self.cue(tr, t, cue)
                self.play(FadeIn(marks[i][0], scale=1.6), FadeIn(marks[i][1]), Create(marks[i][2]), run_time=0.6)

        # screening a healthy population: almost everyone is well, so most positives are false
        band = Rectangle(width=ax.c2p(1, 0)[0] - ax.c2p(0, 0)[0], height=ax.y_length, stroke_width=0,
                         fill_color=RLRED, fill_opacity=0.18)
        band.move_to([(ax.c2p(0, 0)[0] + ax.c2p(1, 0)[0]) / 2, ax.c2p(0, 50)[1], 0])
        band_l = txt(label("almost_everyone_is_well"), size=22, color=RLRED)
        band_l.next_to(band, RIGHT, buff=0.15).align_to(band, UP).shift(DOWN * 0.15)
        second = node(label("positive_a_second_different_test"), color=HILITE, size=24)
        second.move_to(ax.c2p(13.5, 30))
        with self.say("10.4") as (tr, t):
            self.play(FadeOut(fixed), FadeIn(band), FadeIn(band_l), run_time=0.8)
            self.cue(tr, t, {"en": "So a positive", "uz": "Shuning uchun musbat"})
            self.play(FadeIn(second, shift=UP * 0.2), run_time=0.7)
        self.clear_all()


class S10Accuracy(LectureScene):
    def construct(self):
        # 100 people, 1 ill; a "model" that always says healthy
        n100 = one_in(S1)
        img = cells_image(n100, 1, 10, 4.0).move_to(LEFT * 3.5 + DOWN * 0.2)
        model = node(label("model_always_healthy"), color=LBLUE, size=26)
        model.move_to(RIGHT * 2.6 + UP * 1.7)
        acc = VGroup(txt(label("accuracy"), size=30, color=GREY_B),
                     txt(pct(ACC["0.01"]), size=60, weight=BOLD, color=RLGREEN)).arrange(RIGHT, buff=0.4)
        found = VGroup(txt(label("ill_people_found"), size=30, color=GREY_B),
                       txt("0", size=60, weight=BOLD, color=RLRED)).arrange(RIGHT, buff=0.4)
        VGroup(acc, found).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(RIGHT * 2.6 + DOWN * 0.6)
        with self.say("10.5") as (tr, t):
            self.play(FadeIn(img), run_time=0.8)
            self.cue(tr, t, {"en": "Here, a model", "uz": "Bu yerda doim"})
            self.play(FadeIn(model, shift=DOWN * 0.2), run_time=0.6)
            self.play(FadeIn(acc), run_time=0.6)
            self.cue(tr, t, {"en": "and would never", "uz": "lekin birorta"})
            self.play(FadeIn(found), run_time=0.6)
        self.clear_all()

        n = one_in(S1000)
        card = pause_card([label("1_person_in_n_is_ill", n=n),
                           label("the_model_always_answers_healthy"),
                           label("accuracy_q")])
        with self.say("10.6"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        img = cells_image(n, 1, 40, 3.0).move_to(LEFT * 3.6 + DOWN * 0.1)
        frac_ = MathTex(rf"\frac{{{n - 1}}}{{{n}}}".replace(",", "{,}"), "=", rf"{100 * ACC['0.001']:.1f}\%",
                        font_size=60, color=RLGREEN).move_to(RIGHT * 2.8 + UP * 0.6)
        useless = txt(label("rarer_disease_a_useless_model_looks"),
                      size=26, color=GREY_B).move_to(RIGHT * 2.7 + DOWN * 1.4)
        if useless.width > 5.6:
            useless.scale_to_fit_width(5.6)
        with self.say("10.7") as (tr, t):
            self.play(FadeIn(img), Write(frac_), run_time=1.0)
            self.cue(tr, t, {"en": "The rarer", "uz": "Kasallik qanchalik"})
            self.play(FadeIn(useless, shift=UP * 0.2), run_time=0.7)
        self.clear_all()


class S10Next(LectureScene):
    def construct(self):
        head = self.heading(label("where_bayes_theorem_comes_back"), color=LBLUE)
        items = [(label("lecture_6"), label("bayesian_inference"),
                  {"en": "in Lecture 6", "uz": "oltinchi maʼruzada"}),
                 (label("module_3"), label("naive_bayes"),
                  {"en": "in Module 3", "uz": "uchinchi modulda"}),
                 (label("module_1"), label("classification_metrics"),
                  {"en": "in Module 1", "uz": "birinchi modulda"})]
        cards = VGroup(*[card(b, a, color=c, width=3.8, height=2.2, size=30)
                         for (a, b, _), c in zip(items, (RLBLUE, RLGREEN, HILITE))]).arrange(RIGHT, buff=0.4)
        cards.move_to(DOWN * 0.3)
        formula = MathTex(r"P(A\mid B) = \frac{P(B\mid A)\,P(A)}{P(B)}", font_size=40, color=GREY_B)
        formula.next_to(head, DOWN, buff=0.4)
        with self.say("10.8") as (tr, t):
            self.play(FadeIn(head), FadeIn(formula), run_time=0.7)
            for c, (_, _, cue) in zip(cards, items):
                self.cue(tr, t, cue)
                self.play(FadeIn(c, shift=UP * 0.3), run_time=0.6)
        self.clear_all()


class S10Summary(LectureScene):
    def construct(self):
        head = self.heading(label("lecture_2_summary"), color=LBLUE)

        def mini_grid():
            sq = VGroup(*[Square(0.11, stroke_width=0, fill_color=BUS_C if i in (0, 1, 2, 7) else NOBUS_C,
                                 fill_opacity=1) for i in range(16)]).arrange_in_grid(4, 4, buff=0.03)
            return VGroup(sq, SurroundingRectangle(VGroup(*sq[:8]), color=LBLUE, buff=0.03, stroke_width=2))

        def mini_tree():
            r = Dot(LEFT * 0.35, radius=0.04, color=WHITE)
            ends = [UP * 0.25 + RIGHT * 0.05, DOWN * 0.25 + RIGHT * 0.05]
            g = VGroup(r)
            for e in ends:
                g.add(Line(r.get_center(), e, color=GREY_B, stroke_width=2))
                for e2 in (e + UP * 0.12 + RIGHT * 0.3, e + DOWN * 0.12 + RIGHT * 0.3):
                    g.add(Line(e, e2, color=HILITE, stroke_width=2))
            return g

        def mini_bars():
            hs = [0.25, 0.45, 0.75]
            return VGroup(*[Rectangle(width=0.14, height=h * 0.6, stroke_width=0,
                                      fill_color=(BUS_C, LBLUE, BUS_C)[i], fill_opacity=1)
                            for i, h in enumerate(hs)]).arrange(RIGHT, buff=0.05, aligned_edge=DOWN)

        def mini_flip():
            return VGroup(Arrow(LEFT * 0.35, RIGHT * 0.35, buff=0, color=LBLUE, stroke_width=3,
                                max_tip_length_to_length_ratio=0.3).shift(UP * 0.1),
                          Arrow(RIGHT * 0.35, LEFT * 0.35, buff=0, color=HILITE, stroke_width=3,
                                max_tip_length_to_length_ratio=0.3).shift(DOWN * 0.1))

        items = [(mini_grid, label("a_condition_shrinks_the_sample_space")),
                 (mini_tree, label("tree_multiply_along_branches_table_choose")),
                 (mini_bars, label("independence_conditional_plain_pooling_can_reverse")),
                 (mini_flip, label("total_probability_a_weighted_average_bayes"))]
        rows = VGroup()
        for icon, text in items:
            ic = icon()
            if ic.height > 0.55:
                ic.scale_to_fit_height(0.55)
            slot = VGroup(Square(0.75, stroke_width=0), ic)
            ic.move_to(slot[0])
            rows.add(VGroup(slot, txt(text, size=28)).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT).next_to(head, DOWN, buff=0.6)
        if rows.width > 12.4:
            rows.scale_to_fit_width(12.4)
        rows.set_x(0)
        with self.say("10.9") as (tr, t):
            self.play(FadeIn(head), run_time=0.6)
            for k, r in enumerate(rows, 1):
                self.cue(tr, t, k)
                self.play(FadeIn(r, shift=RIGHT * 0.3), run_time=0.6)
        self.clear_all()

        end = VGroup(txt(label("lecture_n", n=2), size=56, weight=BOLD, color=RLBLUE),
                     txt(label("the_end"), size=34, color=GREY_B)).arrange(DOWN, buff=0.3).move_to(UP * 0.4)
        nxt = VGroup(txt(label("next"), size=28, color=GREY_B),
                     txt(label("lecture_3_discrete_random_variables_and"), size=40, weight=BOLD,
                         color=RLBLUE),
                     MathTex(r"P(X = k)", font_size=64, color=HILITE)).arrange(DOWN, buff=0.4)
        if nxt.width > 12.4:
            nxt.scale_to_fit_width(12.4)
        with self.say("10.10") as (tr, t):
            self.play(FadeIn(end, shift=UP * 0.3), run_time=0.9)
            self.cue(tr, t, {"en": "In the next lecture", "uz": "Keyingi maʼruzada"})
            self.play(FadeOut(end), FadeIn(nxt, shift=UP * 0.3), run_time=1.0)
        self.play(FadeOut(nxt), run_time=0.6)
        self.play(FadeIn(brand_outro()), run_time=1.0)
        self.wait(2.0)
        self.clear_all(run_time=0.6)


SCENES = ["S10Curve", "S10Accuracy", "S10Next", "S10Summary"]
