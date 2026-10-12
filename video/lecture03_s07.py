"""Lecture 3, section 7 — the Bernoulli distribution: one yes-or-no question.

Every number on screen comes from N (capture_l03.py, unit-tested by test_l03.py):
pastry_pmf, bern_p, bern_var, bern_max_var, bern_girl, bern_girl_var, bin_n.
"""
from lecture03_kit import *

COIN = N["bern_coin"]                   # a fair coin
P, VAR, VMAX = N["bern_p"], N["bern_var"], N["bern_max_var"]
GIRL, GIRL_VAR = N["bern_girl"], N["bern_girl_var"]
YES_C, NO_C = HILITE, GREY_D


def person(color=GREY_B, h=0.55):
    """A customer: a head over rounded shoulders."""
    head = Circle(radius=h * 0.2, stroke_width=0, fill_color=color, fill_opacity=1)
    body = RoundedRectangle(corner_radius=h * 0.18, width=h * 0.62, height=h * 0.42, stroke_width=0,
                            fill_color=color, fill_opacity=1)
    head.next_to(body, UP, buff=h * 0.05)
    return VGroup(body, head)


def yes_no_bars(p, x0=0.0, base=-2.0, height=3.2, width=1.1, step=1.6, size=34):
    """The Bernoulli distribution as two bars: 0 (no) and 1 (yes), with their probabilities."""
    q = 1 - p
    bars = VGroup(*[Rectangle(width=width, height=max(v * height, 1e-3), stroke_width=0, fill_color=c,
                              fill_opacity=1).move_to([x0 + i * step, base + v * height / 2, 0])
                    for i, (v, c) in enumerate(((q, NO_C), (p, YES_C)))])
    probs = VGroup(*[MathTex(dec(v), font_size=size).next_to(b, UP, buff=0.12) for v, b in zip((q, p), bars)])
    vals = VGroup(MathTex("0", font_size=size, color=GREY_B), MathTex("1", font_size=size, color=GREY_B))
    for v, b in zip(vals, bars):
        v.next_to([b.get_x(), base, 0], DOWN, buff=0.2)
    words = VGroup(txt(label("no_answer"), size=22, color=GREY_B), txt(label("yes_answer"), size=22, color=GREY_B))
    for w_, v in zip(words, vals):
        w_.next_to(v, DOWN, buff=0.1)
    floor = Line([x0 - width, base, 0], [x0 + step + width, base, 0], color=GREY_B, stroke_width=2)
    return VGroup(bars, probs, vals, words, floor)


class S07Questions(LectureScene):
    def construct(self):
        self.section_card(7)
        rows = [(label("q_did_this_customer_buy"), None, label("dist_bernoulli")),
                (label("q_how_many_of_the_next"), f"n = {N['bin_n']}", label("dist_binomial")),
                (label("q_which_cup_size"), None, label("dist_categorical")),
                (label("q_how_many_walk_in"), None, label("dist_poisson"))]
        qs, names = VGroup(), VGroup()
        for i, (q, chip, name) in enumerate(rows):
            t = txt(q, size=28)
            if chip:
                t = VGroup(t, MathTex(r"\;(" + chip + ")", font_size=34, color=GREY_B)).arrange(RIGHT, buff=0.15)
            qs.add(t)
            names.add(txt(name, size=30, weight=BOLD, color=(LBLUE, HILITE, RLGREEN, RLORANGE)[i]))
        qs.arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to(LEFT * 1.6 + UP * 0.2)
        for n_, q in zip(names, qs):
            n_.move_to([4.6, q.get_y(), 0])
        arrows = VGroup(*[Arrow([q.get_right()[0] + 0.15, q.get_y(), 0], [n_.get_left()[0] - 0.15, q.get_y(), 0],
                                buff=0, color=GREY_D, stroke_width=3, max_tip_length_to_length_ratio=0.15)
                          for q, n_ in zip(qs, names)])
        grp = VGroup(qs, names, arrows)
        if grp.width > 12.6:
            grp.scale_to_fit_width(12.6)
        with self.say("7.1") as (tr, t):
            cues = [{"en": "Did this customer", "uz": "Bu mijoz pishiriq"},
                    {"en": "How many of the next ten", "uz": "Keyingi oʻnta"},
                    {"en": "Which cup size", "uz": "Bu mijoz qaysi"},
                    {"en": "How many customers walk in", "uz": "Keyingi oʻn daqiqada"}]
            for q, c in zip(qs, cues):
                self.cue(tr, t, c)
                self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": "Four questions", "uz": "Toʻrt savol"})
            self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(n_)) for a, n_ in zip(arrows, names)],
                                  lag_ratio=0.25), run_time=1.2)
        self.play(FadeOut(VGroup(qs[1:], names[1:], arrows[1:])), VGroup(qs[0], arrows[0], names[0])
                  .animate.to_edge(UP, buff=SAFE + 0.35), run_time=0.6)
        self.first = VGroup(qs[0], arrows[0], names[0])

        # one yes-or-no question, with p
        cust = person(GREY_B, 1.1).move_to(LEFT * 4.2 + DOWN * 0.3)
        qm = txt("?", size=56, weight=BOLD, color=HILITE).next_to(cust, UP, buff=0.2)
        y_def = MathTex(r"Y = \begin{cases} 1 \\ 0 \end{cases}", font_size=60).move_to(LEFT * 0.9 + DOWN * 0.3)
        y_words = VGroup(txt(label("yes_answer"), size=26, color=YES_C), txt(label("no_answer"), size=26, color=GREY_B))
        y_words.arrange(DOWN, buff=0.35).next_to(y_def, RIGHT, buff=0.3)
        p_txt = MathTex(r"P(Y = 1) = p", font_size=52, color=HILITE).move_to(RIGHT * 3.6 + DOWN * 0.3)
        with self.say("7.2") as (tr, t):
            self.play(FadeIn(cust), FadeIn(qm, scale=0.6), run_time=0.6)
            self.cue(tr, t, {"en": "The answer is one", "uz": "Javob «ha»"})
            self.play(Write(y_def), FadeIn(y_words), run_time=0.9)
            self.cue(tr, t, {"en": "We call the probability", "uz": "«Ha» ehtimolini"})
            self.play(Write(p_txt), run_time=0.7)
            self.cue(tr, t, {"en": "This is the Bernoulli", "uz": "Bu Bernulli"})
            self.play(Indicate(self.first[2], color=WHITE, scale_factor=1.1), run_time=0.7)
        self.clear_all()

        # a coin and a newborn: two values of p
        coin = yes_no_bars(COIN, x0=-5.0, base=-1.4, height=3.6)
        girl = yes_no_bars(GIRL, x0=2.2, base=-1.4, height=3.6)
        c_lab = txt(label("coin"), size=30, weight=BOLD, color=LBLUE).next_to(coin, UP, buff=0.35)
        g_lab = txt(label("newborn_girl"), size=30, weight=BOLD, color=LBLUE).next_to(girl, UP, buff=0.35)
        c_p = MathTex(f"p = {dec(COIN)}", font_size=40, color=HILITE).next_to(c_lab, UP, buff=0.2)
        g_p = MathTex(rf"p \approx {dec(GIRL)}", font_size=40, color=HILITE).next_to(g_lab, UP, buff=0.2)
        with self.say("7.3") as (tr, t):
            self.play(FadeIn(c_lab), FadeIn(c_p), FadeIn(coin), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeIn(g_lab), FadeIn(g_p), FadeIn(girl), run_time=0.8)
        self.clear_all()

        rule = MathTex(r"E[Y] = p", r"\qquad", r"\mathrm{Var}(Y) = p\,(1 - p)", font_size=60).move_to(UP * 0.4)
        with self.say("7.4") as (tr, t):
            self.play(Write(rule[0]), run_time=0.8)
            self.cue(tr, t, {"en": "and the variance", "uz": "dispersiya esa"})
            self.play(Write(rule[2]), run_time=0.9)
        self.play(rule.animate.scale(0.7).to_edge(UP, buff=SAFE + 0.35), run_time=0.5)

        # the coffee shop: any pastry at all is one yes-or-no question
        bars, probs, vals, floor = pmf_bars(PASTRY, base=-2.4, height=3.0, step=1.5)
        shop = VGroup(bars, probs, vals, floor).move_to(LEFT * 3.0 + DOWN * 0.5)
        cap = txt(label("pastries"), size=24, color=GREY_B).next_to(floor, DOWN, buff=0.7)
        anyp = yes_no_bars(P, x0=2.4, base=-2.4, height=3.0)
        anyp_lab = txt(label("at_least_one_pastry"), size=26, color=YES_C).next_to(anyp, UP, buff=0.3)
        sum_ = MathTex(f"{dec(PASTRY[1])} + {dec(PASTRY[2])} = {dec(P)}", font_size=40, color=YES_C)
        sum_.next_to(anyp_lab, UP, buff=0.25)
        var = MathTex(rf"\mathrm{{Var}} = {dec(P)} \times {dec(1 - P)} = {dec(VAR)}", font_size=40)
        var.next_to(rule, DOWN, buff=0.35)
        with self.say("7.5") as (tr, t):
            self.play(FadeIn(shop), FadeIn(cap), run_time=0.8)
            self.play(bars[1].animate.set_fill(YES_C), bars[2].animate.set_fill(YES_C), run_time=0.6)
            self.play(Write(sum_), FadeIn(anyp_lab), FadeIn(anyp), run_time=1.0)
            self.cue(tr, t, {"en": "The variance is", "uz": "Dispersiya —"})
            self.play(Write(var), run_time=0.9)
        self.clear_all()

        # the spread is largest at p = 0.5
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 0.3, 0.05], x_length=8.0, y_length=4.2, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2, "include_numbers": True, "font_size": 24,
                               "decimal_number_config": {"num_decimal_places": 2}})
        ax.move_to(DOWN * 0.4)
        xl = MathTex("p", font_size=40, color=GREY_B).next_to(ax.x_axis, RIGHT, buff=0.25)
        yl = MathTex(r"p\,(1 - p)", font_size=36, color=GREY_B).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        curve = ax.plot(lambda x: x * (1 - x), x_range=[0, 1], color=LBLUE, stroke_width=4)
        top = Dot(ax.c2p(0.5, VMAX), radius=0.09, color=HILITE)
        top_l = MathTex(dec(VMAX), font_size=36, color=HILITE).next_to(top, UP, buff=0.15)
        top_l.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06)
        ends = VGroup(Dot(ax.c2p(0, 0), radius=0.09, color=RLRED), Dot(ax.c2p(1, 0), radius=0.09, color=RLRED))
        shop_d = Dot(ax.c2p(P, VAR), radius=0.08, color=YES_C)
        shop_l = MathTex(dec(VAR), font_size=30, color=YES_C).next_to(shop_d, LEFT, buff=0.15)
        shop_l.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.05)
        known = txt(label("answer_already_known"), size=24, color=RLRED)
        known.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06)
        known.move_to(ax.c2p(0.86, 0.285))                    # top right, clear of the curve
        # arcs out to the right, so it never runs along the curve into the dot
        known_ar = CurvedArrow(known.get_corner(DR) + LEFT * 0.3 + DOWN * 0.05, ax.c2p(1, 0) + RIGHT * 0.12 + UP * 0.08,
                               angle=PI / 3, color=RLRED, stroke_width=3, tip_length=0.2)
        with self.say("7.6") as (tr, t):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.play(Create(curve), FadeIn(shop_d), FadeIn(shop_l), run_time=1.0)
            self.play(FadeIn(top, scale=1.6), FadeIn(top_l), run_time=0.5)
            self.cue(tr, t, {"en": "and zero at", "uz": "pi nol yoki"})
            self.play(*[FadeIn(d, scale=1.6) for d in ends], run_time=0.5)
            self.cue(tr, t, {"en": "a question whose answer", "uz": "javobi oldindan"})
            self.play(FadeIn(known), Create(known_ar), run_time=0.6)
        self.clear_all()


class S07Classifier(LectureScene):
    def construct(self):
        mail = RoundedRectangle(corner_radius=0.08, width=1.6, height=1.1, stroke_color=GREY_B, stroke_width=3)
        flap = VMobject(stroke_color=GREY_B, stroke_width=3).set_points_as_corners(
            [mail.get_corner(UL), mail.get_center() + DOWN * 0.1, mail.get_corner(UR)])
        mail = VGroup(mail, flap).move_to(LEFT * 4.8 + UP * 0.3)
        box = RoundedRectangle(corner_radius=0.15, width=3.0, height=1.4, stroke_color=LBLUE, stroke_width=4)
        box_t = txt(label("classifier"), size=28, color=LBLUE).move_to(box)
        clf = VGroup(box, box_t).move_to(LEFT * 0.9 + UP * 0.3)
        a1 = Arrow(mail.get_right(), clf.get_left(), buff=0.2, color=GREY_B)
        out = txt(f"p = P({label('spam')})", size=40, color=HILITE).move_to(RIGHT * 3.7 + UP * 0.3)
        a2 = Arrow(clf.get_right(), out.get_left(), buff=0.2, color=GREY_B)
        bern = txt(label("dist_bernoulli"), size=30, weight=BOLD, color=HILITE).next_to(out, DOWN, buff=0.4)
        nxt = txt(label("lecture_5_its_loss_function"), size=26, color=GREY_B).move_to(DOWN * 2.3)
        with self.say("7.7") as (tr, t):
            self.play(FadeIn(mail), run_time=0.5)
            self.play(GrowArrow(a1), FadeIn(clf), run_time=0.7)
            self.cue(tr, t, {"en": "outputs exactly", "uz": "aynan Bernulli"})
            self.play(GrowArrow(a2), Write(out), FadeIn(bern), run_time=1.0)
            self.cue(tr, t, {"en": "In Lecture 5", "uz": "Beshinchi maʼruzada"})
            self.play(FadeIn(nxt, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S07HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"P({label('newborn_girl')}) = {dec(GIRL)}", r"Var(Y) = ?"])
        card.to_edge(UP, buff=SAFE + 0.4)
        with self.say("7.8"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        calc = MathTex(rf"{dec(GIRL)} \times {dec(1 - GIRL)} \approx {dec(GIRL_VAR)}", font_size=56, color=HILITE)
        calc.to_edge(UP, buff=SAFE + 0.5)
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 0.3, 0.05], x_length=7.0, y_length=3.6, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2, "include_numbers": True, "font_size": 22,
                               "decimal_number_config": {"num_decimal_places": 2}})
        ax.move_to(DOWN * 1.0)
        xl = MathTex("p", font_size=36, color=GREY_B).next_to(ax.x_axis, RIGHT, buff=0.25)
        curve = ax.plot(lambda x: x * (1 - x), x_range=[0, 1], color=LBLUE, stroke_width=4)
        d = Dot(ax.c2p(GIRL, GIRL_VAR), radius=0.1, color=HILITE)
        top = DashedLine(ax.c2p(0, VMAX), ax.c2p(1, VMAX), color=GREY_D, stroke_width=2)
        top_l = MathTex(dec(VMAX), font_size=30, color=GREY_B).next_to(top, RIGHT, buff=0.15)
        with self.say("7.9") as (tr, t):
            self.play(Write(calc), run_time=1.0)
            self.play(Create(ax), FadeIn(xl), Create(curve), run_time=1.0)
            self.cue(tr, t, {"en": "That is almost", "uz": "Bu deyarli"})
            self.play(Create(top), FadeIn(top_l), FadeIn(d, scale=1.8), run_time=0.8)
        self.clear_all()

        one = person(HILITE, 1.0).move_to(LEFT * 4.5)
        many = VGroup(*[person(GREY_B, 0.7) for _ in range(N["bin_n"])]).arrange(RIGHT, buff=0.18)
        many.move_to(RIGHT * 1.6)
        arrow = Arrow(one.get_right(), many.get_left(), buff=0.3, color=GREY_B)
        nlab = MathTex(f"n = {N['bin_n']}", font_size=40, color=GREY_B).next_to(many, DOWN, buff=0.35)
        with self.say("7.10") as (tr, t):
            self.play(FadeIn(one), run_time=0.4)
            self.play(GrowArrow(arrow), LaggedStart(*[FadeIn(p_, shift=UP * 0.2) for p_ in many], lag_ratio=0.08),
                      FadeIn(nlab), run_time=1.2)
        self.clear_all()


SCENES = ["S07Questions", "S07Classifier", "S07HandsOn"]
