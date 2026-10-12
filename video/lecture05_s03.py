"""Lecture 5, section 3 — the central limit theorem: three spikes become a bell.

Every number on screen comes from N (capture_l05.py, unit-tested by test_l05.py): mu, var, the exact
sampling distributions sampling["1" | "2" | "5" | "30"] (means, probs, se, within_1se, within_2se),
gauss_1se, gauss_2se. The bars are exact (convolutions), not a simulation; the curve over each panel is
N(mu, var/n), drawn from mu and var only.
"""
import numpy as np

from lecture05_kit import *

MU, VAR = N["mu"], N["var"]
NS = ("1", "2", "5", "30")
S = N["sampling"]
BAR_C, CURVE_C = LBLUE, HILITE
X_LO, X_HI = -0.25, 2.25                   # the same mean axis for every panel, so the bell visibly narrows


def normal_pdf(x, n):
    sd = np.sqrt(VAR / n)
    return np.exp(-(x - MU) ** 2 / (2 * sd * sd)) / (sd * np.sqrt(2 * np.pi))


def mean_axes(y_max, x_length=5.2, y_length=2.1, numbers=True, xr=(X_LO, X_HI, 0.5), decimals=1):
    ticks = [round(v, 2) for v in np.arange(0, xr[1] + 1e-9, xr[2]) if v >= xr[0]]
    return Axes(x_range=list(xr), y_range=[0, y_max, y_max], x_length=x_length, y_length=y_length,
                tips=False, axis_config={"color": GREY_B, "stroke_width": 2},
                x_axis_config={"include_numbers": numbers, "font_size": 20,
                               "decimal_number_config": {"num_decimal_places": decimals},
                               "numbers_to_include": ticks},
                y_axis_config={"include_ticks": False, "stroke_opacity": 0})


def sampling_panel(n, x_length=5.2, y_length=2.1, numbers=True, xr=(X_LO, X_HI, 0.5)):
    """The exact distribution of the mean of n orders as density bars (probability ÷ spacing 1/n),
    with the curve N(mu, var/n) over it. Returns (axes, bars, curve)."""
    s = S[n]
    k = int(n)
    dens = [p * k for p in s["probs"]]
    top = max(max(dens), normal_pdf(MU, k))
    ax = mean_axes(top * 1.12, x_length, y_length, numbers, xr)
    w = (ax.c2p(1 / k, 0)[0] - ax.c2p(0, 0)[0]) * 0.8
    w = min(w, 0.32)
    bars = VGroup(*[Rectangle(width=w, height=max(ax.c2p(0, d)[1] - ax.c2p(0, 0)[1], 1e-3), stroke_width=0,
                              fill_color=BAR_C, fill_opacity=0.9).move_to(ax.c2p(m, d / 2))
                    for m, d in zip(s["means"], dens) if xr[0] <= m <= xr[1] and d > top * 0.004])
    xs = np.linspace(xr[0], xr[1], 300)
    curve = VMobject(stroke_color=CURVE_C, stroke_width=3).set_points_smoothly(
        [ax.c2p(x, normal_pdf(x, k)) for x in xs])
    return ax, bars, curve


def shape_icon(kind, w=1.5, h=0.9, color=GREY_B):
    """A tiny picture of a distribution's shape (no numbers): coin, die, waiting time, pastries."""
    base = Line(LEFT * w / 2, RIGHT * w / 2, color=GREY_D, stroke_width=2)
    if kind == "waiting":
        xs = np.linspace(0, 1, 40)
        curve = VMobject(stroke_color=color, stroke_width=3).set_points_smoothly(
            [[-w / 2 + x * w, h * np.exp(-3.2 * x), 0] for x in xs])
        return VGroup(base, curve)
    heights = {"coin": [0.5, 0.5], "die": [1 / 6] * 6, "pastries": N["pastry"]}[kind]
    m = max(heights)
    nb = len(heights)
    bw = w / nb * 0.7
    bars = VGroup(*[Rectangle(width=bw, height=h * v / m, stroke_width=0, fill_color=color, fill_opacity=0.9)
                    .move_to([-w / 2 + (i + 0.5) * w / nb, h * v / m / 2, 0]) for i, v in enumerate(heights)])
    return VGroup(base, bars)


def small_bell(w=1.3, h=0.8, color=HILITE):
    xs = np.linspace(-3, 3, 60)
    return VMobject(stroke_color=color, stroke_width=3).set_points_smoothly(
        [[x * w / 6, h * np.exp(-x * x / 2), 0] for x in xs])


class S03Theorem(LectureScene):
    def construct(self):
        self.section_card(3)
        head = txt(label("central_limit_theorem"), size=36, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        cond = txt(label("independent_draws_any_distribution_finite_variance"), size=26, color=GREY_B)
        cond.next_to(head, DOWN, buff=0.35)
        f1 = MathTex(r"\bar{x} \;\approx\; \mathcal{N}\!\left(\mu,\; \frac{\sigma^2}{n}\right)", font_size=60, color=HILITE)
        f2 = MathTex(r"\frac{\bar{x} - \mu}{\sigma / \sqrt{n}} \;\approx\; \mathcal{N}(0, 1)", font_size=44)
        fs = VGroup(f1, f2).arrange(DOWN, buff=0.5).move_to(DOWN * 0.6)
        with self.say("3.1") as (tr, t):
            self.play(FadeIn(head), run_time=0.6)
            self.play(FadeIn(cond), run_time=0.6)
            self.cue(tr, t, {"en": "As n grows", "uz": "En oshgan sari"})
            self.play(Write(f1), run_time=1.0)
            self.play(FadeIn(f2), run_time=0.7)
        self.play(FadeOut(VGroup(cond, fs)), run_time=0.4)

        # any shape in, a bell out (the shapes are pictures, no numbers)
        names = {"coin": label("coin"), "die": label("die"), "waiting": label("waiting_time"),
                 "pastries": label("pastries_short")}
        rows = VGroup()
        for kind in ("coin", "die", "waiting", "pastries"):
            icon = shape_icon(kind)
            cap = txt(names[kind], size=22, color=GREY_B).next_to(icon, DOWN, buff=0.15)
            arrow = Arrow(LEFT * 0.4, RIGHT * 0.4, buff=0, color=GREY_B, stroke_width=3)
            bell = small_bell()
            row = VGroup(VGroup(icon, cap), arrow, bell).arrange(RIGHT, buff=0.35)
            rows.add(row)
        rows.arrange_in_grid(rows=2, cols=2, buff=(1.2, 0.6)).move_to(DOWN * 0.5)
        note = info(label("illustration"))
        with self.say("3.2") as (tr, t):
            self.play(FadeIn(note), run_time=0.3)
            for r, cue in zip(rows, [{"en": "Coins", "uz": "Tanga"}, {"en": "dice", "uz": "kubik"},
                                     {"en": "waiting times", "uz": "kutish vaqti"}, {"en": "pastries", "uz": "pishiriqlar"}]):
                self.cue(tr, t, cue)
                self.play(FadeIn(r[0]), GrowArrow(r[1]), run_time=0.4)
            self.play(*[Create(r[2]) for r in rows], run_time=0.8)
        self.play(FadeOut(VGroup(rows, note)), run_time=0.4)

        # law of large numbers: where it lands; CLT: the whole distribution
        line = NumberLine(x_range=[0, 1, 0.1], length=8, color=GREY_B, include_numbers=False).move_to(DOWN * 1.6)
        mu_tick = MathTex(r"\mu", font_size=36, color=HILITE).next_to(line.n2p(MU), DOWN, buff=0.2)
        dot = Dot(line.n2p(MU), radius=0.11, color=HILITE)
        lln = txt(label("law_of_large_numbers_where"), size=26, color=GREY_B).next_to(mu_tick, DOWN, buff=0.3)
        clt = txt(label("clt_the_whole_distribution"), size=26, color=HILITE).move_to(UP * 0.9)
        xs = np.linspace(0, 1, 200)
        sd = np.sqrt(VAR / 30)
        bell = VMobject(stroke_color=HILITE, stroke_width=4).set_points_smoothly(
            [line.n2p(x) + UP * 2.0 * np.exp(-(x - MU) ** 2 / (2 * sd * sd)) for x in xs])
        with self.say("3.3") as (tr, t):
            self.play(Create(line), FadeIn(mu_tick), FadeIn(lln), run_time=0.7)
            self.play(FadeIn(dot, scale=1.6), run_time=0.4)
            self.cue(tr, t, {"en": "The central limit theorem", "uz": "Markaziy limit teoremasi"})
            self.play(FadeIn(clt), Create(bell), run_time=1.0)
        self.clear_all()


class S03Bell(LectureScene):
    def construct(self):
        panels = VGroup()
        tags = VGroup()
        for n in NS:
            ax, bars, curve = sampling_panel(n, y_length=1.85)
            title = MathTex(rf"n = {n}", font_size=34, color=WHITE).next_to(ax, UP, buff=0.12).align_to(ax, LEFT)
            panels.add(VGroup(ax, bars, curve, title))
        panels.arrange_in_grid(rows=2, cols=2, buff=(0.9, 0.7)).move_to(UP * 0.35)
        for p, n in zip(panels, NS):
            tg = MathTex(rf"{S[n]['within_1se']:.2f}", font_size=32, color=HILITE)
            tg.next_to(p[0], UP, buff=0.12).align_to(p[0], RIGHT)
            tags.add(tg)
        exact = txt(label("exact_not_simulated"), size=26, color=LBLUE).to_edge(DOWN, buff=SAFE + 0.2)
        exact.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06)
        with self.say("3.4") as (tr, t):
            for p, cue in zip(panels, [{"en": "For pastries", "uz": "Pishiriqlarda"}, {"en": "At two", "uz": "En ikki"},
                                       {"en": "By five", "uz": "En besh"}, {"en": "at thirty", "uz": "en oʻttizda"}]):
                self.cue(tr, t, cue)
                self.play(FadeIn(p[0]), FadeIn(p[3]), LaggedStart(*[GrowFromEdge(b, DOWN) for b in p[1]],
                                                                   lag_ratio=0.02), run_time=0.7)
                self.play(Create(p[2]), run_time=0.4)
        with self.say("3.5") as (tr, t):
            self.play(FadeIn(exact, shift=DOWN * 0.2), run_time=0.6)

        within = txt(label("within_one_standard_error"), size=24, color=HILITE)
        gauss = VGroup(txt(label("normal_distribution_says"), size=24, color=GREY_B),
                       MathTex(rf"{N['gauss_1se']:.2f}", font_size=34, color=HILITE)).arrange(RIGHT, buff=0.2)
        foot = VGroup(within, gauss).arrange(RIGHT, buff=0.8).to_edge(DOWN, buff=SAFE + 0.2)
        foot.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.08)
        with self.say("3.6") as (tr, t):
            self.play(FadeOut(exact), run_time=0.3)
            self.play(FadeIn(foot[0], foot[1]), run_time=0.3)
            for tg, cue in zip(tags, [{"en": "zero point nine zero", "uz": "toʻqson"}, {"en": "seven seven", "uz": "yetmish yetti"},
                                      {"en": "six seven", "uz": "oltmish yetti"}, {"en": "and six six", "uz": "oltmish olti"}]):
                self.cue(tr, t, cue)
                self.play(FadeIn(tg, scale=1.3), run_time=0.4)
            self.cue(tr, t, {"en": "says six eight", "uz": "oltmish sakkiz"})
            self.play(FadeIn(foot[2]), run_time=0.5)
        self.clear_all()


class S03Conditions(LectureScene):
    def construct(self):
        keys = (label("independent_draws"), label("same_distribution"), label("finite_variance"))
        chips = VGroup()
        for k in keys:
            t_ = txt(k, size=30)
            box = RoundedRectangle(corner_radius=0.14, width=t_.width + 0.6, height=t_.height + 0.5,
                                   stroke_color=LBLUE, stroke_width=3)
            chips.add(VGroup(box, t_.move_to(box)))
        chips.arrange(RIGHT, buff=0.5).move_to(UP * 1.4)
        if chips.width > 12.6:
            chips.scale_to_fit_width(12.6)
        head = txt(label("three_conditions"), size=34, weight=BOLD, color=HILITE).next_to(chips, UP, buff=0.5)
        with self.say("3.7") as (tr, t):
            self.play(FadeIn(head), run_time=0.5)
            for c, cue in zip(chips, [{"en": "independent", "uz": "mustaqil"}, {"en": "same distribution", "uz": "bitta taqsimotdan"},
                                      {"en": "finite variance", "uz": "dispersiyasi chekli"}]):
                self.cue(tr, t, cue)
                self.play(FadeIn(c, shift=UP * 0.2), run_time=0.45)

        # AI: the interval around a reported accuracy (an illustration: no numbers)
        bar_y = -1.4
        axis = NumberLine(x_range=[0, 1, 0.25], length=7.5, color=GREY_B, include_numbers=False).move_to([0, bar_y, 0])
        centre = 0.62
        dot = Dot(axis.n2p(centre), radius=0.12, color=HILITE)
        lo, hi = axis.n2p(centre - 0.12), axis.n2p(centre + 0.12)
        lo, hi = lo + DOWN * 0.45, hi + DOWN * 0.45
        bracket = VGroup(Line(lo, hi, color=HILITE, stroke_width=5),
                         Line(lo + UP * 0.15, lo + DOWN * 0.15, color=HILITE, stroke_width=5),
                         Line(hi + UP * 0.15, hi + DOWN * 0.15, color=HILITE, stroke_width=5))
        xs = np.linspace(centre - 0.3, centre + 0.3, 120)
        bell = VMobject(stroke_color=LBLUE, stroke_width=3).set_points_smoothly(
            [axis.n2p(x) + UP * 1.4 * np.exp(-(x - centre) ** 2 / (2 * 0.06 ** 2)) for x in xs])
        acc = txt(label("accuracy_on_a_test_set"), size=26, color=GREY_B).next_to(axis, UP, buff=0.25).align_to(axis, LEFT)
        ci = txt(label("confidence_interval"), size=26, color=HILITE).next_to(bracket, DOWN, buff=0.2)
        note = info(label("illustration"))
        with self.say("3.8") as (tr, t):
            self.play(Create(axis), FadeIn(acc), FadeIn(note), run_time=0.6)
            self.play(FadeIn(dot, scale=1.5), Create(bell), run_time=0.8)
            self.cue(tr, t, {"en": "close to normal", "uz": "normal taqsimotga yaqin"})
            self.play(Create(bracket), FadeIn(ci), run_time=0.6)
        self.clear_all()


class S03HandsOn(LectureScene):
    def construct(self):
        card = pause_card(["n = 30", f"P(|x̄ − μ| ≤ 2·SE) = ?   ({label('normal_distribution')})"])
        card.to_edge(UP, buff=SAFE + 0.3)
        with self.say("3.9"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        n = "30"
        ax, bars, curve = sampling_panel(n, x_length=9.0, y_length=3.4, xr=(0, 0.9, 0.1))
        grp = VGroup(ax, bars, curve).move_to(DOWN * 0.7)
        se = S[n]["se"]
        inside = VGroup(*[b for b in bars if abs(ax.p2c(b.get_center())[0] - MU) <= 2 * se + 1e-9])
        band = Rectangle(width=ax.c2p(MU + 2 * se, 0)[0] - ax.c2p(MU - 2 * se, 0)[0], height=ax.y_length,
                         stroke_width=0, fill_color=HILITE, fill_opacity=0.12)
        band.move_to([ax.c2p(MU, 0)[0], ax.c2p(0, 0)[1] + ax.y_length / 2, 0])
        two = MathTex(r"\mu \pm 2\,\mathrm{SE}", font_size=32, color=HILITE).next_to(band, UP, buff=0.1)
        rule = VGroup(txt(label("normal_distribution_says"), size=28, color=GREY_B),
                      MathTex(rf"\approx {round(100 * N['gauss_2se'])}\%", font_size=44, color=HILITE)).arrange(RIGHT, buff=0.25)
        exact = VGroup(txt(label("exact_count"), size=28, color=GREY_B),
                       MathTex(rf"{round(100 * S[n]['within_2se'])}\%", font_size=44, color=LBLUE)).arrange(RIGHT, buff=0.25)
        res = VGroup(rule, exact).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_edge(UP, buff=SAFE + 0.35)
        with self.say("3.10") as (tr, t):
            self.play(FadeIn(ax), FadeIn(bars), Create(curve), run_time=0.8)
            self.play(FadeIn(band), FadeIn(two), *[b.animate.set_fill(HILITE) for b in inside], run_time=0.7)
            self.cue(tr, t, {"en": "By the rule", "uz": "Toʻrtinchi maʼruzadagi"})
            self.play(FadeIn(rule), run_time=0.5)
            self.cue(tr, t, {"en": "The exact count", "uz": "Aniq hisob"})
            self.play(FadeIn(exact), run_time=0.5)
        self.clear_all()

        q = txt(label("is_thirty_always_enough_q"), size=36, weight=BOLD, color=HILITE)
        with self.say("3.11"):
            self.play(FadeIn(q, shift=UP * 0.2), run_time=0.8)
        self.clear_all(run_time=0.3)


SCENES = ["S03Theorem", "S03Bell", "S03Conditions", "S03HandsOn"]
