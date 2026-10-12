"""Lecture 4, section 6 — the normal distribution: the croissants' bell curve and the 68-95-99.7 rule.

Every number on screen comes from N (capture_l04.py, unit-tested by test_l04.py):
mu, sigma, normal_curve, rule, rule_ranges, label_min. The bell is drawn from the captured density
points; a curve for another sigma or another bake is that same curve rescaled (see bell_points).
"""
import numpy as np

from lecture04_kit import *

MU, SIGMA = N["mu"], N["sigma"]
CURVE = N["normal_curve"]                          # croissant density, 52 … 68 g
RULE = N["rule"]                                   # {"1": 0.6827, "2": 0.9545, "3": 0.9973}
RANGES = N["rule_ranges"]                          # {"1": [58, 62], …}
BAND_C = {"1": LBLUE, "2": RLGREEN, "3": GREY_B}
X0, X1 = CURVE[0][0], CURVE[-1][0]


def bell_points(mu=MU, sigma=SIGMA):
    """The captured croissant curve moved to (mu, sigma): x → mu + sigma·z, height × SIGMA/sigma.
    Every normal curve is this one shape, so nothing is recomputed."""
    return [[mu + sigma * (x - MU) / SIGMA, y * SIGMA / sigma] for x, y in CURVE]


def gram_axes(x_range=(X0, X1, 2), x_length=10.0, y_max=0.22, y_length=3.6, numbers=True):
    ax = Axes(x_range=list(x_range), y_range=[0, y_max, y_max], x_length=x_length, y_length=y_length, tips=False,
              axis_config={"color": GREY_B, "stroke_width": 2},
              x_axis_config={"include_numbers": numbers, "font_size": 24, "decimal_number_config": {"num_decimal_places": 0}},
              y_axis_config={"include_ticks": False, "stroke_opacity": 0})
    return ax


def curve_on(ax, pts, color=HILITE, width=4):
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly([ax.c2p(x, y) for x, y in pts])


def area_on(ax, pts, a, b, color, opacity=0.55):
    """The area under the curve between a and b, built from the captured points."""
    sel = [(x, y) for x, y in pts if a - 1e-9 <= x <= b + 1e-9]
    poly = [ax.c2p(sel[0][0], 0)] + [ax.c2p(x, y) for x, y in sel] + [ax.c2p(sel[-1][0], 0)]
    return Polygon(*poly, stroke_width=0, fill_color=color, fill_opacity=opacity)


def g(v):
    """60 → '60 g' as math."""
    return rf"{v:g}\,\mathrm{{g}}"


class S06Bell(LectureScene):
    def construct(self):
        self.section_card(6)
        # three measurements, one shape (the shape is the croissant curve; the other two are illustrations)
        names = [label("croissant_weight"), label("height"), label("thermometer_reading")]
        cols = VGroup()
        for n_ in names:
            ax = gram_axes(x_length=3.6, y_length=2.2, numbers=False)
            cols.add(VGroup(ax, curve_on(ax, CURVE, color=LBLUE, width=3), txt(n_, size=24, color=GREY_B)
                            .next_to(ax, DOWN, buff=0.25)))
        cols.arrange(RIGHT, buff=0.8).move_to(UP * 0.3)
        note = info(label("illustration"))
        with self.say("6.1") as (tr, t):
            for c, cue in zip(cols, [{"en": "Weigh croissants", "uz": "Kruassanlarni tortamiz"},
                                     {"en": "measure people", "uz": "odamlarning boʻyini"},
                                     {"en": "read a thermometer", "uz": "termometrni"}]):
                self.cue(tr, t, cue)
                self.play(FadeIn(c[2]), Create(c[1]), FadeIn(c[0]), run_time=0.6)
            self.play(FadeIn(note), run_time=0.3)
        self.clear_all()

        # a croissant's weight is a sum of many small wobbles
        parts = [label("dough_portion"), label("flour_moisture"), label("place_in_the_oven"), label("rise_time"),
                 label("a_dozen_others")]
        chips = VGroup()
        for i, p_ in enumerate(parts):
            t_ = txt(p_, size=24)
            box = RoundedRectangle(corner_radius=0.12, width=t_.width + 0.4, height=t_.height + 0.35,
                                   stroke_color=GREY_B, stroke_width=2)
            chips.add(VGroup(box, t_.move_to(box)))
        row = VGroup()
        for i, c in enumerate(chips):
            if i:
                row.add(MathTex("+", font_size=40, color=GREY_B))
            row.add(c)
        row.arrange(RIGHT, buff=0.18)
        if row.width > 12.6:
            row.scale_to_fit_width(12.6)
        head = txt(label("croissant_weight"), size=32, weight=BOLD, color=HILITE)
        eq = MathTex("=", font_size=44)
        VGroup(head, eq).arrange(RIGHT, buff=0.3).next_to(row, UP, buff=0.6)
        VGroup(head, eq, row).move_to(UP * 1.2)
        ax = gram_axes(x_length=6.0, y_length=2.2, numbers=False).move_to(DOWN * 1.9)
        bell = curve_on(ax, CURVE)
        with self.say("6.2") as (tr, t):
            self.play(FadeIn(head), FadeIn(eq), run_time=0.5)
            self.cue(tr, t, {"en": "A croissant's weight", "uz": "Kruassanning vazni"})
            self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.15) for m in row], lag_ratio=0.15), run_time=1.6)
            self.play(FadeIn(ax), Create(bell), run_time=1.0)

        clt = txt(label("central_limit_theorem_lecture_5"), size=28, color=LBLUE).next_to(ax, RIGHT, buff=0.5)
        if clt.get_right()[0] > 6.6:
            clt.next_to(ax, UP, buff=0.2)
        with self.say("6.3") as (tr, t):
            self.play(FadeIn(clt, shift=LEFT * 0.2), run_time=0.7)
            self.cue(tr, t, {"en": "sums and averages", "uz": "yigʻindi va oʻrtachalar"})
            self.play(Indicate(bell, color=WHITE, scale_factor=1.04), run_time=0.9)
        self.clear_all()

        # mu slides, sigma stretches: the croissants, 60 g and 2 g
        ax = gram_axes().move_to(DOWN * 0.6)
        bell = curve_on(ax, CURVE)
        mu_ln = DashedLine(ax.c2p(MU, 0), ax.c2p(MU, CURVE[len(CURVE) // 2][1]), color=WHITE, stroke_width=3)
        mu_t = MathTex(rf"\mu = {g(MU)}", font_size=40).next_to(mu_ln, UP, buff=0.15)
        y_s = CURVE[len(CURVE) // 2][1] * 0.6
        sig = DoubleArrow(ax.c2p(MU, y_s), ax.c2p(MU + SIGMA, y_s), buff=0, color=LBLUE, stroke_width=4,
                          max_tip_length_to_length_ratio=0.2)
        sig_t = MathTex(rf"\sigma = {g(SIGMA)}", font_size=36, color=LBLUE).next_to(sig, RIGHT, buff=0.2)
        mu_w = txt(label("mu_moves_it_sideways"), size=24, color=GREY_B)
        sg_w = txt(label("sigma_stretches_it"), size=24, color=LBLUE)
        words = VGroup(mu_w, sg_w).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UL, buff=SAFE + 0.3)
        with self.say("6.4") as (tr, t):
            self.play(FadeIn(ax), Create(bell), run_time=1.0)
            self.cue(tr, t, {"en": "mu slides", "uz": "mu egri"})
            self.play(FadeIn(mu_w), bell.animate.shift(RIGHT * 0.8), run_time=0.6)
            self.play(bell.animate.shift(LEFT * 0.8), run_time=0.5)
            self.cue(tr, t, {"en": "sigma stretches", "uz": "sigma uni"})
            self.play(FadeIn(sg_w), bell.animate.stretch(1.3, 0), run_time=0.6)
            self.play(bell.animate.stretch(1 / 1.3, 0), run_time=0.5)
            self.cue(tr, t, {"en": "For the bakery", "uz": "Novvoyxonadagi"})
            self.play(Create(mu_ln), Write(mu_t), run_time=0.7)
            self.play(GrowFromCenter(sig), Write(sig_t), run_time=0.7)

        formula = MathTex(r"f(x) = \frac{1}{\sigma\sqrt{2\pi}}\, e^{-\frac{(x-\mu)^2}{2\sigma^2}}", font_size=40)
        formula.to_corner(UR, buff=SAFE + 0.3)
        no_int = txt(label("no_simple_integral"), size=24, color=RLRED).next_to(formula, DOWN, buff=0.2)
        with self.say("6.5") as (tr, t):
            self.play(Write(formula), run_time=0.9)
            self.cue(tr, t, {"en": "it has no simple", "uz": "uning oddiy"})
            self.play(FadeIn(no_int), formula.animate.set_opacity(0.35), run_time=0.6)
        self.play(FadeOut(VGroup(formula, no_int, mu_w, sg_w, sig, sig_t)), run_time=0.4)
        self.ax, self.bell, self.mu_ln, self.mu_t = ax, bell, mu_ln, mu_t
        self.rule_part()

    def rule_part(self):
        ax, bell = self.ax, self.bell
        # rings that do not overlap: ±1σ, then the two strips out to ±2σ, then out to ±3σ
        def ring(k):
            a, b = RANGES[k]
            if k == "1":
                return area_on(ax, CURVE, a, b, BAND_C[k], 0.6)
            ia, ib = RANGES[str(int(k) - 1)]
            return VGroup(area_on(ax, CURVE, a, ia, BAND_C[k], 0.55), area_on(ax, CURVE, ib, b, BAND_C[k], 0.55))
        bands = {k: ring(k) for k in ("1", "2", "3")}
        pcts = {k: MathTex(rf"{dec(100 * RULE[k], 2)}\%", font_size=34, color=WHITE) for k in ("1", "2", "3")}
        y_lab = {"1": 0.105, "2": 0.035, "3": 0.012}
        pcts["1"].move_to(ax.c2p(MU, y_lab["1"]))
        pcts["2"].move_to(ax.c2p(MU - 3.0 * SIGMA / 2, y_lab["2"]))
        pcts["3"].move_to(ax.c2p(MU + 2.55 * SIGMA, 0.05))
        for k in ("1", "2", "3"):
            pcts[k].add_background_rectangle(color=BLACK, opacity=0.75, buff=0.05)
        sig_rng = {k: MathTex(rf"\mu \pm {k if k != '1' else ''}\sigma", font_size=30, color=GREY_B) for k in "123"}
        head = MathTex(rf"{round(100 * RULE['1'])} \;-\; {round(100 * RULE['2'])} \;-\; {dec(100 * RULE['3'], 1)}",
                       font_size=48, color=HILITE).to_edge(UP, buff=SAFE + 0.3)
        with self.say("6.6") as (tr, t):
            self.play(Write(head), self.mu_t.animate.set_opacity(0), run_time=0.8)
            for k, cue in zip(("1", "2", "3"), [{"en": "about sixty-eight percent", "uz": "taxminan oltmish sakkiz"},
                                                {"en": "ninety-five percent within two", "uz": "toʻqson besh foizi ikki"},
                                                {"en": "ninety-nine point seven percent within", "uz": "toʻqson toʻqqiz butun oʻndan yetti foizi uch"}]):
                self.cue(tr, t, cue)
                sig_rng[k].next_to(head, DOWN, buff=0.25)
                self.play(FadeIn(bands[k]), FadeIn(pcts[k]), FadeIn(sig_rng[k]) if k == "1" else
                          Transform(sig_rng["1"], sig_rng[k]), run_time=0.7)
            self.bring_to_front(bell, self.mu_ln)

        # the same three ranges in grams
        brackets = VGroup()
        for i, k in enumerate(("1", "2", "3")):
            a, b = RANGES[k]
            off = DOWN * (0.8 + 0.42 * i)
            ln = Line(ax.c2p(a, 0) + off, ax.c2p(b, 0) + off,
                      color=BAND_C[k], stroke_width=4)
            ends = VGroup(*[Line(UP * 0.1, DOWN * 0.1, color=ln.get_color(), stroke_width=3).move_to(p)
                            for p in (ln.get_start(), ln.get_end())])
            tx = MathTex(rf"{g(a)} \;-\; {g(b)}", font_size=26, color=ln.get_color()).next_to(ln, RIGHT, buff=0.25)
            brackets.add(VGroup(ln, ends, tx))
        grp = VGroup(ax, bell, self.mu_ln, *bands.values(), *pcts.values())
        with self.say("6.7") as (tr, t):
            self.play(grp.animate.shift(UP * 0.6), run_time=0.5)
            for b_ in brackets:
                b_.shift(UP * 0.6)
            for k, b_, cue in zip("123", brackets, [{"en": "fifty-eight", "uz": "ellik sakkiz"},
                                                     {"en": "fifty-six", "uz": "ellik olti"},
                                                     {"en": "fifty-four", "uz": "ellik toʻrt"}]):
                self.cue(tr, t, cue)
                self.play(Create(b_[0]), FadeIn(b_[1]), FadeIn(b_[2]), run_time=0.6)

        two = VGroup(MathTex(r"\mu", font_size=56, color=WHITE), MathTex(",", font_size=56),
                     MathTex(r"\sigma", font_size=56, color=LBLUE)).arrange(RIGHT, buff=0.15)
        two_w = txt(label("a_centre_and_a_spread"), size=26, color=GREY_B)
        batch_w = txt(label("the_whole_batch"), size=26, color=HILITE)
        box = VGroup(two, two_w, batch_w).arrange(DOWN, buff=0.2)
        box.to_corner(UR, buff=SAFE + 0.35).shift(DOWN * 0.9)
        bg = BackgroundRectangle(box, color=BLACK, fill_opacity=0.9, buff=0.15)
        with self.say("6.8") as (tr, t):
            self.play(FadeIn(bg), Write(two), FadeIn(two_w), run_time=0.8)
            self.cue(tr, t, {"en": "answer almost", "uz": "butun partiya"})
            self.play(FadeIn(batch_w), Indicate(VGroup(*bands.values()), color=WHITE, scale_factor=1.02), run_time=0.8)
        self.clear_all()


class S06Errors(LectureScene):
    """AI: a model's errors assumed normal; squared error follows (Lecture 5). Points are an illustration."""
    def construct(self):
        rng = np.random.default_rng(6)
        xs = np.linspace(-4.6, 0.6, 14)
        ys = 0.45 * xs + 0.2 + rng.normal(0, 0.45, len(xs))
        line = Line([-5.2, 0.45 * -5.2 + 0.2, 0], [1.2, 0.45 * 1.2 + 0.2, 0], color=LBLUE, stroke_width=4)
        dots = VGroup(*[Dot([x, y, 0], radius=0.07, color=WHITE) for x, y in zip(xs, ys)])
        errs = VGroup(*[Line([x, 0.45 * x + 0.2, 0], [x, y, 0], color=RLRED, stroke_width=2.5) for x, y in zip(xs, ys)])
        VGroup(line, dots, errs).shift(DOWN * 0.4)
        e_w = txt(label("model_errors"), size=26, color=RLRED).next_to(VGroup(line, dots), UP, buff=0.4)
        # the error distribution: the captured bell, on its side
        ax = gram_axes(x_length=3.4, y_length=1.6, numbers=False)
        bell = VGroup(ax, curve_on(ax, CURVE, color=RLRED, width=3)).rotate(PI / 2).move_to([4.1, -0.3, 0])
        sq = txt(label("squared_error_lecture_5"), size=26, color=HILITE).next_to(bell, DOWN, buff=0.35)
        if sq.get_right()[0] > 6.8:
            sq.shift(LEFT * (sq.get_right()[0] - 6.6))
        note = info(label("illustration"))
        with self.say("6.9") as (tr, t):
            self.play(Create(line), LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.05),
                      FadeIn(note), run_time=1.0)
            self.play(LaggedStart(*[Create(e) for e in errs], lag_ratio=0.05), FadeIn(e_w), run_time=0.9)
            self.cue(tr, t, {"en": "The squared error", "uz": "kvadrat xato"})
            self.play(FadeIn(bell[0]), Create(bell[1]), run_time=0.8)
            self.play(FadeIn(sq, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S06HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"μ = {MU:g} g,   σ = {SIGMA:g} g",
                           f"{round(100 * RULE['2'])}%:   ? g  –  ? g"])
        card.move_to(UP * 0.8)
        with self.say("6.10"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        ax = gram_axes().move_to(DOWN * 0.3)
        bell = curve_on(ax, CURVE)
        a, b = RANGES["2"]
        band = area_on(ax, CURVE, a, b, LBLUE, 0.55)
        y = CURVE[len(CURVE) // 2][1] * 0.42
        arr_l = DoubleArrow(ax.c2p(a, y), ax.c2p(MU, y), buff=0, color=WHITE, stroke_width=3,
                            max_tip_length_to_length_ratio=0.12)
        arr_r = DoubleArrow(ax.c2p(MU, y), ax.c2p(b, y), buff=0, color=WHITE, stroke_width=3,
                            max_tip_length_to_length_ratio=0.12)
        two_s = VGroup(*[MathTex(rf"2\sigma = {g(2 * SIGMA)}", font_size=28).next_to(ar, DOWN, buff=0.15)
                         for ar in (arr_l, arr_r)])
        for m in two_s:
            m.add_background_rectangle(color=BLACK, opacity=0.8, buff=0.05)
        ans = MathTex(rf"{g(a)} \;-\; {g(b)}", font_size=56, color=LBLUE).to_edge(UP, buff=SAFE + 0.5)
        with self.say("6.11") as (tr, t):
            self.play(FadeIn(ax), Create(bell), run_time=0.8)
            self.play(FadeIn(band), GrowFromCenter(arr_l), GrowFromCenter(arr_r), FadeIn(two_s), run_time=0.8)
            self.cue(tr, t, {"en": "fifty-six and", "uz": "ellik olti va"})
            self.play(Write(ans), run_time=0.7)

        # teaser: the label's promise
        lim = N["label_min"]
        tag = VGroup(txt(f"{label('bottle_label')}:", size=30, weight=BOLD, color=HILITE),
                     MathTex(rf"\ge {g(lim)}", font_size=44, color=HILITE)).arrange(RIGHT, buff=0.25)
        frame_ = SurroundingRectangle(tag, color=HILITE, buff=0.2, corner_radius=0.12)
        promise = VGroup(frame_, tag).move_to(ans)
        lim_ln = DashedLine(ax.c2p(lim, 0), ax.c2p(lim, 0.16), color=HILITE, stroke_width=3)
        q = txt("?", size=48, weight=BOLD, color=HILITE).next_to(lim_ln, UP, buff=0.1)
        with self.say("6.12") as (tr, t):
            self.play(FadeOut(VGroup(band, arr_l, arr_r, two_s, ans)), run_time=0.5)
            self.play(FadeIn(promise, shift=DOWN * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": "How often", "uz": "Bu vaʼda"})
            self.play(Create(lim_ln), FadeIn(q), run_time=0.6)
        self.clear_all()


SCENES = ["S06Bell", "S06Errors", "S06HandsOn"]
