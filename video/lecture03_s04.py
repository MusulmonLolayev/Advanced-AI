"""Lecture 3, section 4 — variance.

The coffee shop's pastries: E[X^2] = 0.6, Var = 0.6 - 0.4^2 = 0.44, sigma = 0.66. Then two raffles with the
same expectation (-$1.20) and very different spreads (sigma $17.87 against $2.40). Every number is N's.
"""
from lecture03_kit import *

A, B = N["raffle_A"], N["raffle_B"]
MU, E2, VAR, SD = N["pastry_mean"], N["pastry_e2"], N["pastry_var"], N["pastry_sd"]


def money(v, places=2):
    """-1.2 -> −$1.20, 6 -> $6, as the screen shows a dollar amount."""
    s = f"{abs(v):,.{places}f}"
    if places and float(s.replace(",", "")) == int(abs(v)):
        s = f"{abs(v):,.0f}"
    return ("-" if v < 0 else "") + "\\$" + s


def mtex(s, size=40, color=WHITE):
    return MathTex(s.replace(",", "{,}"), font_size=size, color=color)


def pmf_of(r):
    """{net gain: probability} of a raffle, from N's [numerator, denominator] pairs."""
    return {int(k): f[0] / f[1] for k, f in r["pmf"].items()}


def frac_str(f):
    return rf"\tfrac{{{f[0]}}}{{{f[1]}}}"


def pastry_panel(cx=-3.4, step=1.4):
    """The pastry bars with the mean as a dashed line; x_of(v) is where value v sits on screen."""
    bars, probs, vals, floor = pmf_bars(PASTRY, base=-2.3, height=3.2, step=step, width=0.9)
    xs = sorted(PASTRY)

    def x_of(v):
        return cx + (v - xs[0] - (len(xs) - 1) / 2) * step
    VGroup(bars, probs, vals, floor).shift(RIGHT * cx)
    mean = DashedLine([x_of(MU), -2.3, 0], [x_of(MU), 1.5, 0], color=RLRED, stroke_width=4)
    mu = MathTex(r"\mu", "=", dec(MU), font_size=36, color=RLRED).next_to(mean, UP, buff=0.4)
    return VGroup(bars, probs, vals, floor, mean, mu), x_of


class S04Pastry(LectureScene):
    def construct(self):
        self.section_card(4)
        g, x_of = pastry_panel()
        bars, probs, vals, floor, mean, mu = g
        cap = txt(label("pastries"), size=24, color=GREY_B).next_to(vals, DOWN, buff=0.2)
        # the distance of each value from the mean, the thing variance squares
        # from the mean out to each value: above the tall bar for 0, clear of the short bars' labels for 1 and 2
        ys = [probs[0].get_top()[1] + 0.25, probs[1].get_top()[1] + 0.4, probs[1].get_top()[1] + 0.8]
        dists = VGroup(*[Arrow([x_of(MU), y, 0], [x_of(v), y, 0], buff=0, color=HILITE, stroke_width=4,
                               max_tip_length_to_length_ratio=0.25) for v, y in zip(sorted(PASTRY), ys)])
        f1 = MathTex(r"\mathrm{Var}(X)", "=", r"E\!\left[(X-\mu)^2\right]", font_size=48).move_to([3.3, 2.0, 0])
        with self.say("4.1") as (tr, t):
            self.play(FadeIn(floor), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2),
                      FadeIn(probs), FadeIn(vals), FadeIn(cap), run_time=1.2)
            self.play(Create(mean), FadeIn(mu), run_time=0.6)
            self.cue(tr, t, {"en": "the variance is", "uz": "dispersiya —"})
            self.play(LaggedStart(*[GrowArrow(a) for a in dists], lag_ratio=0.3), Write(f1), run_time=1.4)

        f2 = MathTex("=", r"E[X^2]", "-", r"\mu^2", font_size=48).next_to(f1, DOWN, buff=0.35).align_to(f1[1], LEFT)
        box = SurroundingRectangle(f2[1:], color=HILITE, buff=0.12)
        with self.say("4.2"):
            self.play(FadeOut(dists), Write(f2), run_time=1.2)
            self.play(Create(box), run_time=0.6)

        xs = sorted(PASTRY)
        e2 = mtex(r"E[X^2] = " + " + ".join(f"{x}^2({dec(PASTRY[x])})" for x in xs) + f" = {dec(E2)}", 38)
        var = mtex(r"\mathrm{Var}(X) = " + f"{dec(E2)} - {dec(MU)}^2 = {dec(VAR)}", 40, HILITE)
        sd = mtex(r"\sigma = \sqrt{" + dec(VAR) + r"} \approx " + dec(SD), 40, RLGREEN)
        calc = VGroup(e2, var, sd).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([3.0, -0.8, 0])
        if calc.width > 7.0:
            calc.scale_to_fit_width(7.0)
        band = DoubleArrow([x_of(MU - SD), 2.3, 0], [x_of(MU + SD), 2.3, 0], buff=0, color=RLGREEN,
                           stroke_width=4, max_tip_length_to_length_ratio=0.12)
        with self.say("4.3") as (tr, t):
            self.play(Write(e2), run_time=1.2)
            self.cue(tr, t, {"en": "We subtract", "uz": "Undan nol"})
            self.play(Write(var), run_time=1.0)
            self.cue(tr, t, {"en": "The standard deviation", "uz": "Standart chetlanish"})
            self.play(Write(sd), GrowFromCenter(band), run_time=1.0)
        self.clear_all()


def ticket_grid(n_prize, color, cols=25, side=0.13, gap=0.04):
    """All the tickets as a grid; the prize tickets lit, spread evenly through it."""
    n = N["raffle_tickets"]
    every = n // n_prize
    g = VGroup(*[Square(side, stroke_width=0, fill_color=color if i % every == every // 2 and i // every < n_prize
                        else GREY_D, fill_opacity=1) for i in range(n)])
    g.arrange_in_grid(cols=cols, buff=gap)
    return g


def raffle_panel(r, prize_color, title, prizes_math):
    """A raffle's net gain as bars on a shared dollar axis, so a far prize sits far away."""
    pmf = pmf_of(r)
    ax = NumberLine(x_range=[-50, 400, 50], length=5.6, include_numbers=True, font_size=20, color=GREY_B,
                    numbers_to_exclude=[-50])
    hk = 2.0
    bars = VGroup()
    probs = VGroup()
    for v, p in sorted(pmf.items()):
        h = max(p * hk, 0.05)
        b = Rectangle(width=0.16, height=h, stroke_width=0, fill_color=RLRED if v < 0 else prize_color,
                      fill_opacity=1).move_to(ax.n2p(v) + UP * h / 2)
        bars.add(b)
        f = next(fr for k, fr in r["pmf"].items() if int(k) == v)
        probs.add(MathTex(frac_str(f), font_size=30, color=GREY_A).next_to(b, UP, buff=0.1))
    title = VGroup(txt(title, size=28, weight=BOLD, color=prize_color), prizes_math).arrange(RIGHT, buff=0.3)
    title.next_to(ax, UP, buff=2.6)
    return VGroup(ax, bars, probs, title)


class S04Raffles(LectureScene):
    def construct(self):
        ga = ticket_grid(1, HILITE)
        gb = ticket_grid(N["raffle_B_count"], RLGREEN)
        VGroup(ga, gb).arrange(RIGHT, buff=1.2).move_to(DOWN * 0.3)
        ta = VGroup(txt(label("raffle_a"), size=28, weight=BOLD, color=HILITE),
                    mtex(rf"1 \times {money(N['raffle_A_prize'], 0)}", 34, HILITE)).arrange(RIGHT, buff=0.3)
        tb = VGroup(txt(label("raffle_b"), size=28, weight=BOLD, color=RLGREEN),
                    mtex(rf"{N['raffle_B_count']} \times {money(N['raffle_B_prize'], 0)}", 34, RLGREEN)).arrange(RIGHT, buff=0.3)
        ta.next_to(ga, UP, buff=0.3)
        tb.next_to(gb, UP, buff=0.3)
        price = tagged(f"{N['raffle_tickets']} × ${N['raffle_price']}", f"{label('tickets')}:", after=False, size=28,
                       color=GREY_B).to_edge(UP, buff=SAFE + 0.35)
        with self.say("4.4") as (tr, t):
            self.play(FadeIn(ga), FadeIn(ta), FadeIn(price), run_time=0.9)
            self.cue(tr, t, {"en": "But this time", "uz": "Lekin bu safar"})
            self.play(FadeIn(gb), FadeIn(tb), run_time=1.0)
        self.play(FadeOut(VGroup(ga, gb, price)), run_time=0.4)

        pa = raffle_panel(A, HILITE, label("raffle_a"), mtex(rf"1 \times {money(N['raffle_A_prize'], 0)}", 30, HILITE))
        pb = raffle_panel(B, RLGREEN, label("raffle_b"), mtex(rf"{N['raffle_B_count']} \times {money(N['raffle_B_prize'], 0)}", 30, RLGREEN))
        VGroup(pa, pb).arrange(RIGHT, buff=0.9)
        for p in (pa, pb):
            p[3].next_to(p[0], UP, buff=2.6)
        # the axes sit high enough for E, sigma and the verdict to fit underneath
        VGroup(pa, pb).shift(UP * (0.55 - pa[0].get_center()[1]))
        ea = mtex(rf"E[X] = {money(A['mean'])}", 34).next_to(pa[0], DOWN, buff=0.55)
        eb = mtex(rf"E[X] = {money(B['mean'])}", 34).next_to(pb[0], DOWN, buff=0.55)
        same = txt("=", size=40, color=HILITE).move_to((ea.get_center() + eb.get_center()) / 2)
        with self.say("4.5") as (tr, t):
            self.play(ReplacementTransform(ta, pa[3]), ReplacementTransform(tb, pb[3]),
                      FadeIn(pa[0]), FadeIn(pb[0]), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in (*pa[1], *pb[1])], lag_ratio=0.2),
                      FadeIn(pa[2]), FadeIn(pb[2]), run_time=1.2)
            self.cue(tr, t, {"en": "The expectation is again", "uz": "Kutilma yana"})
            self.play(Write(ea), Write(eb), run_time=0.9)
            self.play(FadeIn(same, scale=1.4), run_time=0.4)

        sa = mtex(rf"\sigma = {money(A['sd'])}", 40, HILITE).next_to(ea, DOWN, buff=0.35)
        sb = mtex(rf"\sigma = {money(B['sd'])}", 40, RLGREEN).next_to(eb, DOWN, buff=0.35)
        with self.say("4.6") as (tr, t):
            self.play(Write(sa), Indicate(pa[1][-1], color=HILITE, scale_factor=1.6), run_time=1.0)
            self.cue(tr, t, {"en": "and only two dollars forty", "uz": "ikkinchisida"})
            self.play(Write(sb), run_time=0.8)

        la = txt(label("a_lottery"), size=28, weight=BOLD, color=HILITE).next_to(sa, DOWN, buff=0.3)
        lb = txt(label("a_mild_discount"), size=28, weight=BOLD, color=RLGREEN).next_to(sb, DOWN, buff=0.3)
        with self.say("4.7") as (tr, t):
            self.play(Indicate(VGroup(ea, eb, same), color=WHITE, scale_factor=1.05), run_time=0.8)
            self.cue(tr, t, {"en": "The variance says", "uz": "Dispersiya esa"})
            self.play(Indicate(VGroup(sa, sb), color=WHITE, scale_factor=1.08), run_time=0.8)
            self.cue(tr, t, {"en": "The first is a lottery", "uz": "Birinchisi"})
            self.play(FadeIn(la, shift=UP * 0.2), run_time=0.6)
            self.play(FadeIn(lb, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        # AI: two models with the same average error; the narrower one is the one to trust (shapes only)
        ax = NumberLine(x_range=[-4, 4, 1], length=10, include_numbers=False, color=GREY_B).move_to(DOWN * 2.2)
        mid = ax.n2p(0)

        unit = ax.length / 8

        def bell(s, color):
            """An error distribution of spread s, centred on the axis' zero (a shape, no data)."""
            return FunctionGraph(lambda u: mid[1] + 2.4 * (0.8 / s) * np.exp(-(((u - mid[0]) / unit) / s) ** 2 / 2),
                                 x_range=[mid[0] - 4 * unit, mid[0] + 4 * unit, 0.02], color=color, stroke_width=5)
        wide, narrow = bell(1.8, HILITE), bell(0.8, RLGREEN)
        zero = DashedLine(mid, mid + UP * 3.2, color=GREY_B, stroke_width=3)
        avg = txt(label("same_average_error"), size=26, color=GREY_B).next_to(zero, UP, buff=0.15)
        xl = txt(label("error"), size=24, color=GREY_B).next_to(ax, DOWN, buff=0.2)
        na = txt(label("model_a"), size=28, weight=BOLD, color=HILITE).move_to(ax.n2p(-3.0) + UP * 1.3)
        nb = txt(label("model_b"), size=28, weight=BOLD, color=RLGREEN).move_to(ax.n2p(1.9) + UP * 2.2)
        ok = txt("✓", size=40, color=RLGREEN).next_to(nb, RIGHT, buff=0.2)
        note = info(label("illustration"))
        with self.say("4.8") as (tr, t):
            self.play(Create(ax), FadeIn(xl), Create(zero), FadeIn(avg), FadeIn(note), run_time=0.8)
            self.play(Create(wide), FadeIn(na), run_time=0.8)
            self.play(Create(narrow), FadeIn(nb), run_time=0.8)
            self.cue(tr, t, {"en": "the one with the smaller variance", "uz": "dispersiyasi kichigi"})
            self.play(FadeIn(ok, scale=1.5), Indicate(narrow, color=RLGREEN, scale_factor=1.03), run_time=0.8)
        self.clear_all()


class S04HandsOn(LectureScene):
    def construct(self):
        pmf = pmf_of(B)
        card = pause_card([label("variance_of_raffle_b_q")])
        dist = mtex(", \\quad ".join(rf"p({v}) = {frac_str(B['pmf'][str(v)])}" for v in sorted(pmf, reverse=True)), 40)
        ev = mtex(rf"E[X] = {money(B['mean'])}", 36, GREY_B)
        VGroup(card, dist, ev).arrange(DOWN, buff=0.6).move_to(UP * 0.3)
        with self.say("4.9") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(card), FadeIn(dist), FadeIn(ev), run_time=0.8)
        self.hands_on()

        vs = sorted(pmf, reverse=True)
        terms = " + ".join(f"{v * v}({dec(pmf[v])})" for v in vs)
        e2 = mtex(rf"E[X^2] = {terms} = {dec(B['e2'])}", 42)
        var = mtex(rf"\mathrm{{Var}}(X) = {dec(B['e2'])} - {dec(B['mean'] ** 2)} = {dec(B['var'])}", 46, HILITE)
        VGroup(e2, var).arrange(DOWN, buff=0.5).move_to(DOWN * 1.2)
        with self.say("4.10") as (tr, t):
            self.play(FadeOut(card), VGroup(dist, ev).animate.to_edge(UP, buff=SAFE + 0.4), run_time=0.6)
            self.play(Write(e2), run_time=1.2)
            self.cue(tr, t, {"en": "We subtract", "uz": "Undan bir"})
            self.play(Write(var), run_time=1.0)
        self.clear_all()

        # the question for the next section: a negative expectation, played over and over
        neg = mtex(r"E[X] < 0", 64, RLRED)
        more = mtex(r"n \to \infty \;\; ?", 54, HILITE)
        VGroup(neg, more).arrange(RIGHT, buff=1.0).move_to(UP * 0.3)
        arrow = Arrow(neg.get_right(), more.get_left(), buff=0.25, color=GREY_B)
        with self.say("4.11") as (tr, t):
            self.play(Write(neg), run_time=0.7)
            self.cue(tr, t, {"en": "We see it", "uz": "Buni ruletkada"})
            self.play(GrowArrow(arrow), FadeIn(more), run_time=0.8)
        self.clear_all(run_time=0.3)   # the next section opens on a silent card


SCENES = ["S04Pastry", "S04Raffles", "S04HandsOn"]
