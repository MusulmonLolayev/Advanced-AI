"""Lecture 3, section 6 — shifting and scaling; the end of Part 0.

Pastry revenue R = 2X: E and sigma double ($0.80, $1.33). The bill T = 2X + 3: E = $3.80, the variance stays 1.76.
The rule E[aX + b] = aE[X] + b, Var(aX + b) = a^2 Var(X), and standardizing Z = (X - mu)/sigma. Every number is N's.
"""
from lecture03_kit import *

MU, SD, VAR = N["pastry_mean"], N["pastry_sd"], N["pastry_var"]
PRICE, COFFEE = N["price"], N["coffee"]
XS = sorted(PASTRY)
BASE, HK = -1.6, 3.0             # bar floor and the height of probability 1 (bars are 0.7 tall at most)


def mtex(s, size=40, color=WHITE):
    return MathTex(s.replace(",", "{,}"), font_size=size, color=color)


def usd(v):
    return "\\$" + (f"{v:.0f}" if v == int(v) else f"{v:.2f}")


def line_axis(lo, hi, length=11.0, y=BASE):
    ax = NumberLine(x_range=[lo, hi, 1], length=length, include_numbers=True, font_size=24, color=GREY_B)
    ax.shift(UP * (y - ax.n2p(0)[1]))
    return ax


def bars_on(ax, a=1.0, b=0.0, color=RLBLUE):
    """The pastry distribution of aX + b on the axis: one bar per value, the probability above it."""
    g = VGroup()
    for x in XS:
        h = PASTRY[x] * HK
        r = Rectangle(width=0.55, height=h, stroke_width=0, fill_color=color, fill_opacity=1)
        r.move_to(ax.n2p(a * x + b) + UP * h / 2)
        g.add(VGroup(r, MathTex(dec(PASTRY[x]), font_size=28).next_to(r, UP, buff=0.1)))
    return g


def mean_mark(ax, m, s):
    """The mean as a dashed line, one standard deviation either side as a double arrow."""
    top = BASE + PASTRY[XS[0]] * HK + 0.5
    mean = DashedLine(ax.n2p(m), ax.n2p(m) + UP * (top - BASE), color=RLRED, stroke_width=4)
    spread = DoubleArrow(ax.n2p(m - s) + UP * (top - BASE + 0.25), ax.n2p(m + s) + UP * (top - BASE + 0.25), buff=0,
                         color=RLGREEN, stroke_width=4, max_tip_length_to_length_ratio=0.1)
    return VGroup(mean, spread)


class S06Scale(LectureScene):
    def construct(self):
        self.section_card(6)
        ax = line_axis(0, PRICE * XS[-1] + COFFEE + 1)
        dl = txt(label("dollars"), size=24, color=GREY_B).next_to(ax, DOWN, buff=0.55)
        x_bars = bars_on(ax)
        x_head = mtex("X", 54).to_edge(UP, buff=SAFE + 0.4)
        r_head = mtex(rf"R = {PRICE}X", 54, HILITE).move_to(x_head)
        r_bars = bars_on(ax, PRICE)
        cap = txt(label("pastries"), size=24, color=GREY_B).next_to(x_head, DOWN, buff=0.15)
        with self.say("6.1") as (tr, t):
            self.play(Create(ax), FadeIn(x_head), FadeIn(cap), LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in x_bars],
                                                                      lag_ratio=0.2), run_time=1.2)
            self.cue(tr, t, {"en": "So the pastry revenue", "uz": "Demak"})
            self.play(Transform(x_bars, r_bars), Transform(x_head, r_head), FadeOut(cap), FadeIn(dl), run_time=1.2)

        mark = mean_mark(ax, N["revenue_mean"], N["revenue_sd"])
        e_r = mtex(rf"E[R] = {PRICE} \times {dec(MU)} = {usd(N['revenue_mean'])}", 40, RLRED)
        s_r = mtex(rf"\sigma_R = {PRICE} \times {dec(SD)} = {usd(N['revenue_sd'])}", 40, RLGREEN)
        stats = VGroup(e_r, s_r).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_corner(UR, buff=SAFE + 0.3)
        with self.say("6.2") as (tr, t):
            self.play(Create(mark[0]), Write(e_r), run_time=1.0)
            self.cue(tr, t, {"en": "So does the standard deviation", "uz": "Standart chetlanish ham"})
            self.play(GrowFromCenter(mark[1]), Write(s_r), run_time=1.0)

        t_head = mtex(rf"T = {PRICE}X + {COFFEE}", 54, HILITE).move_to(x_head)
        t_bars = bars_on(ax, PRICE, COFFEE)
        t_mark = mean_mark(ax, N["bill_mean"], N["revenue_sd"])
        e_t = mtex(rf"E[T] = {usd(N['revenue_mean'])} + {usd(COFFEE)} = {usd(N['bill_mean'])}", 40, RLRED)
        e_t.move_to(e_r, aligned_edge=LEFT)
        with self.say("6.3") as (tr, t):
            self.cue(tr, t, {"en": "Then the bill", "uz": "Unda hisob"})
            self.play(Transform(x_head, t_head), run_time=0.6)
            self.play(Transform(x_bars, t_bars), Transform(mark, t_mark), run_time=1.4)
            self.play(Transform(e_r, e_t), run_time=0.8)

        v = mtex(rf"\mathrm{{Var}}(T) = \mathrm{{Var}}(R) = {dec(N['bill_var'])}", 40, RLGREEN).move_to(s_r, aligned_edge=LEFT)
        with self.say("6.4") as (tr, t):
            self.play(Transform(s_r, v), run_time=0.9)
            self.cue(tr, t, {"en": "A fixed three dollars", "uz": "Doimiy uch"})
            self.play(Indicate(mark[1], color=RLGREEN, scale_factor=1.15), run_time=1.0)
        self.clear_all()


class S06Rule(LectureScene):
    def construct(self):
        r1 = MathTex(r"E[aX + b]", "=", r"a\,E[X] + b", font_size=60)
        r2 = MathTex(r"\mathrm{Var}(aX + b)", "=", r"a^2", r"\,\mathrm{Var}(X)", font_size=60)
        rules = VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.6).move_to(UP * 0.3 + LEFT * 1.2)
        sq = SurroundingRectangle(r2[2], color=HILITE, buff=0.1)
        no_b = txt(label("no_b"), size=28, color=GREY_B).next_to(r2, RIGHT, buff=0.5)
        with self.say("6.5") as (tr, t):
            self.play(Write(r1), run_time=1.2)
            self.cue(tr, t, {"en": "Its variance is", "uz": "Dispersiyasi esa"})
            self.play(Write(r2), FadeIn(no_b), run_time=1.2)
            self.cue(tr, t, {"en": "The square appears", "uz": "Kvadrat chiqadi"})
            self.play(Create(sq), r2[2].animate.set_color(HILITE), run_time=0.7)
        self.play(FadeOut(VGroup(sq, no_b)), rules.animate.scale(0.6).to_corner(UR, buff=SAFE + 0.2), run_time=0.6)

        # standardizing: Z = (X - mu) / sigma moves the bars to mean 0 and spread 1
        ax = line_axis(-2, 3, length=10.0)
        zs = [(x - MU) / SD for x in XS]
        z_bars = VGroup()
        for x, z in zip(XS, zs):
            h = PASTRY[x] * HK
            r = Rectangle(width=0.55, height=h, stroke_width=0, fill_color=RLBLUE, fill_opacity=1)
            r.move_to(ax.n2p(x) + UP * h / 2)
            z_bars.add(r)
        targets = VGroup(*[b.copy().move_to(ax.n2p(z) + UP * b.height / 2) for b, z in zip(z_bars, zs)])
        z = mtex(rf"Z = \frac{{X - {dec(MU)}}}{{{dec(SD)}}}", 52, HILITE).to_corner(UL, buff=SAFE + 0.3)
        head = txt(label("standardizing_a_feature"), size=30, weight=BOLD, color=LBLUE).next_to(z, DOWN, buff=0.3, aligned_edge=LEFT)
        zero = DashedLine(ax.n2p(0), ax.n2p(0) + UP * 2.4, color=RLRED, stroke_width=4)
        one = DoubleArrow(ax.n2p(-1) + UP * 2.6, ax.n2p(1) + UP * 2.6, buff=0, color=RLGREEN, stroke_width=4,
                          max_tip_length_to_length_ratio=0.08)
        res = VGroup(mtex(rf"E[Z] = {dec(N['z_mean'])}", 40, RLRED), mtex(rf"\mathrm{{Var}}(Z) = {dec(N['z_var'])}", 40, RLGREEN))
        res.arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(rules, DOWN, buff=0.4).align_to(rules, LEFT)
        with self.say("6.6") as (tr, t):
            self.play(Create(ax), LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in z_bars], lag_ratio=0.2), run_time=1.0)
            self.play(Write(z), FadeIn(head), run_time=1.0)
            self.play(*[Transform(b, tg) for b, tg in zip(z_bars, targets)], run_time=1.4)
            self.cue(tr, t, {"en": "The expectation becomes zero", "uz": "Natijada kutilma nol"})
            self.play(Create(zero), GrowFromCenter(one), Write(res), run_time=1.2)
        self.clear_all()


class S06HandsOn(LectureScene):
    def construct(self):
        p = N["hands_on_price"]
        card = pause_card([tagged_text(label("pastry_price"), f"${p}"),
                           f"E[{p}X] = ?     Var({p}X) = ?"])
        given = VGroup(mtex(rf"E[X] = {dec(MU)}", 40, GREY_B), mtex(rf"\mathrm{{Var}}(X) = {dec(VAR)}", 40, GREY_B))
        given.arrange(RIGHT, buff=0.8)
        VGroup(card, given).arrange(DOWN, buff=0.6).move_to(UP * 0.2)
        with self.say("6.7") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(card), FadeIn(given), run_time=0.8)
        self.hands_on()

        e = mtex(rf"E[{p}X] = {p} \times {dec(MU)} = {usd(N['hands_on_mean'])}", 50, RLRED)
        v = mtex(rf"\mathrm{{Var}}({p}X) = {p * p} \times {dec(VAR)} = {dec(N['hands_on_var'])}", 50, RLGREEN)
        ans = VGroup(e, v).arrange(DOWN, buff=0.5).move_to(DOWN * 0.6)
        with self.say("6.8") as (tr, t):
            self.play(FadeOut(card), given.animate.to_edge(UP, buff=SAFE + 0.5), run_time=0.5)
            self.play(Write(e), run_time=1.0)
            self.cue(tr, t, {"en": "The variance is", "uz": "Dispersiya"})
            self.play(Write(v), run_time=1.0)
        self.clear_all()

        # the end of Part 0: the shapes Part 1 names, drawn from their own numbers (no values shown)
        shapes = [{0: 1 - N["bern_p"], 1: N["bern_p"]},
                  dict(enumerate(N["bin_pmf"])),
                  dict(enumerate(N["cups"].values())),
                  dict(enumerate(N["pois_pmf"]))]
        icons = VGroup()
        for s, c in zip(shapes, (RLBLUE, HILITE, RLGREEN, RLRED)):
            vmax = max(s.values())
            n = len(s)
            w = 2.2 / n
            g = VGroup(*[Rectangle(width=w * 0.8, height=max(2.0 * v / vmax, 0.02), stroke_width=0, fill_color=c,
                                   fill_opacity=1).move_to([i * w, max(2.0 * v / vmax, 0.02) / 2, 0])
                         for i, v in sorted(s.items())])
            icons.add(VGroup(g, Line(g.get_corner(DL) + LEFT * 0.1, g.get_corner(DR) + RIGHT * 0.1, color=GREY_B,
                                     stroke_width=2)))
        icons.arrange(RIGHT, buff=0.8, aligned_edge=DOWN).move_to(DOWN * 0.4)
        nxt = txt(PARTS[1], size=32, weight=BOLD, color=HILITE).next_to(icons, UP, buff=0.8)
        with self.say("6.9") as (tr, t):
            self.cue(tr, t, {"en": "A few shapes", "uz": "Bir necha shakl"})
            self.play(LaggedStart(*[FadeIn(i, shift=UP * 0.3) for i in icons], lag_ratio=0.3), run_time=1.6)
            self.cue(tr, t, {"en": "In part one", "uz": "Birinchi qismda"})
            self.play(FadeIn(nxt, shift=UP * 0.2), run_time=0.7)
        self.clear_all(run_time=0.3)   # Part 1 opens on its card


def tagged_text(words, value):
    """'pastry price: $3' as one pause-card line: the label's words, then the value from the data."""
    return f"{words}: {value}"


SCENES = ["S06Scale", "S06Rule", "S06HandsOn"]
