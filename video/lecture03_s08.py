"""Lecture 3, section 8 — the binomial distribution: how many of the next ten buy a pastry.

Every number on screen comes from N (capture_l03.py, unit-tested by test_l03.py):
bin_n, bin_p, bin_pmf, bin_mode, bin_comb3, bin_p3_parts, bin_mean, bin_var, bin_sd, bin_ge6, bin_p0,
test_n, test_acc, test_mean, test_sd, test_band, test_pmf (the AI panel's Binomial(100, 0.9) bars).
"""

from lecture03_kit import *
from lecture03_s07 import person

BN, BP, PMF = N["bin_n"], N["bin_p"], N["bin_pmf"]
YES_C, LIT, RUSH_C = HILITE, HILITE, RLRED


def bin_bars(pmf, ks, base=-2.4, height=3.6, step=0.78, width=0.56, vmax=None, color=RLBLUE, size=26):
    """Probabilities as bars over their counts k (only the k under each bar is printed)."""
    vmax = vmax or max(pmf)
    sc = height / vmax
    xs = [(i - (len(ks) - 1) / 2) * step for i in range(len(ks))]
    bars = VGroup(*[Rectangle(width=width, height=max(pmf[i] * sc, 1e-3), stroke_width=0, fill_color=color,
                              fill_opacity=1).move_to([x, base + pmf[i] * sc / 2, 0]) for i, x in zip(range(len(ks)), xs)])
    kl = VGroup(*[MathTex(str(k), font_size=size, color=GREY_B).next_to([x, base, 0], DOWN, buff=0.15)
                  for k, x in zip(ks, xs)])
    floor = Line([xs[0] - width, base, 0], [xs[-1] + width, base, 0], color=GREY_B, stroke_width=2)
    return VGroup(bars, kl, floor), sc


class S08Count(LectureScene):
    def construct(self):
        self.section_card(8)
        row = VGroup(*[person(GREY_B, 0.8) for _ in range(BN)]).arrange(RIGHT, buff=0.3).move_to(UP * 0.4)
        # one possible morning: as many buyers as the most likely count
        buyers = [1, 4, 8][:N["bin_mode"]]
        marks = VGroup(*[MathTex("1" if i in buyers else "0", font_size=36, color=YES_C if i in buyers else GREY_D)
                         .next_to(p_, DOWN, buff=0.25) for i, p_ in enumerate(row)])
        count = MathTex(f"X = {N['bin_mode']}", font_size=56, color=YES_C).next_to(marks, DOWN, buff=0.6)
        name = txt(label("dist_binomial"), size=34, weight=BOLD, color=HILITE).next_to(count, DOWN, buff=0.4)
        params = MathTex(rf"n = {BN},\; p = {dec(BP)}", font_size=40, color=GREY_B).next_to(row, UP, buff=0.4)
        with self.say("8.1") as (tr, t):
            self.play(LaggedStart(*[FadeIn(p_, shift=UP * 0.2) for p_ in row], lag_ratio=0.06), FadeIn(params),
                      run_time=1.0)
            self.play(LaggedStart(*[FadeIn(m) for m in marks], lag_ratio=0.08),
                      *[row[i].animate.set_color(YES_C) for i in buyers], run_time=1.2)
            self.play(Write(count), run_time=0.6)
            self.cue(tr, t, 1)
            self.play(FadeIn(name, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        conds = VGroup(txt(label("same_p_every_time"), size=32), txt(label("no_trial_affects_another"), size=32))
        conds.arrange(DOWN, aligned_edge=LEFT, buff=0.6).move_to(UP * 1.1 + RIGHT * 0.4)
        ticks = VGroup(*[MathTex(r"\checkmark", font_size=48, color=RLGREEN).next_to(c, LEFT, buff=0.35) for c in conds])
        socks = VGroup(txt(label("lecture_2_socks"), size=28, color=GREY_B),
                       txt(label("without_replacement"), size=28, color=RLRED)).arrange(RIGHT, buff=0.3)
        socks.move_to(DOWN * 1.6)
        cross = MathTex(r"\times", font_size=56, color=RLRED).next_to(socks, LEFT, buff=0.35)
        link = Arrow(socks.get_top(), conds[1].get_bottom(), buff=0.2, color=RLRED, stroke_width=3)
        with self.say("8.2") as (tr, t):
            self.cue(tr, t, {"en": "the same p", "uz": "har safar pi"})
            self.play(FadeIn(ticks[0]), FadeIn(conds[0], shift=RIGHT * 0.2), run_time=0.6)
            self.cue(tr, t, {"en": "no trial affecting", "uz": "hech bir tajriba"})
            self.play(FadeIn(ticks[1]), FadeIn(conds[1], shift=RIGHT * 0.2), run_time=0.6)
            self.cue(tr, t, {"en": "When we drew socks", "uz": "Ikkinchi maʼruzada"})
            self.play(FadeIn(socks), FadeIn(cross), GrowArrow(link), run_time=0.8)
        self.clear_all()

        f = MathTex(r"P(X = k) =", r"\binom{n}{k}", r"p^k (1 - p)^{n - k}", font_size=64)
        f[2].shift(RIGHT * 0.35)                                # room between the two boxes
        f.move_to(UP * 0.6)
        b1 = SurroundingRectangle(f[1], buff=0.1, color=LBLUE, stroke_width=4)
        b2 = SurroundingRectangle(f[2], buff=0.1, color=HILITE, stroke_width=4)
        # one label under each box, the first ending left of where the second begins
        l1 = txt(label("number_of_orders"), size=26, color=LBLUE).next_to(b1, DOWN, buff=0.35).align_to(b1, RIGHT)
        l2 = txt(label("probability_of_one_order"), size=26, color=HILITE).next_to(b2, DOWN, buff=0.35)
        l2.align_to(b2, LEFT).shift(RIGHT * 0.2).set_y(l1.get_y())
        with self.say("8.3") as (tr, t):
            self.play(Write(f), run_time=1.2)
            self.cue(tr, t, {"en": "the number of orders", "uz": "tartibda kelishi"})
            self.play(Create(b1), FadeIn(l1), run_time=0.7)
            self.cue(tr, t, {"en": "and the probability", "uz": "va bitta shunday"})
            self.play(Create(b2), FadeIn(l2), run_time=0.7)
        self.clear_all()


class S08Pastries(LectureScene):
    def construct(self):
        ks = list(range(BN + 1))
        chart, sc = bin_bars(PMF, ks, base=-2.6, height=3.4)
        bars = chart[0]
        chart.shift(DOWN * 0.1)
        head = MathTex(rf"X \sim \mathrm{{Binomial}}({BN},\ {dec(BP)})", font_size=44).to_edge(UP, buff=SAFE + 0.35)
        m = N["bin_mode"]
        p3 = PMF[m]
        calc = MathTex(rf"{N['bin_comb3']} \times {dec(N['bin_p3_parts'][0], 3)} \times {dec(N['bin_p3_parts'][1], 4)}"
                       rf" \approx {dec(p3, 3)}", font_size=40, color=HILITE)
        calc.next_to(head, DOWN, buff=0.3)
        v3 = MathTex(dec(p3, 3), font_size=32, color=HILITE).next_to(bars[m], UP, buff=0.1)
        with self.say("8.4") as (tr, t):
            self.play(FadeIn(head), Create(chart[2]), FadeIn(chart[1]), run_time=0.7)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06), run_time=1.2)
            self.cue(tr, t, {"en": "The chance that exactly three", "uz": "Aynan uchtasi"})
            self.play(bars[m].animate.set_fill(LIT), FadeIn(v3), Write(calc), run_time=1.0)
            self.cue(tr, t, {"en": "It is the most likely", "uz": "Bu eng ehtimolli"})
            self.play(Indicate(bars[m], color=LIT, scale_factor=1.08), run_time=0.7)

        x_of = lambda k: bars[0].get_x() + k * (bars[1].get_x() - bars[0].get_x())
        base = chart[2].get_y()
        mean_ln = DashedLine([x_of(N["bin_mean"]), base, 0], [x_of(N["bin_mean"]), base + 3.6, 0], color=WHITE,
                             stroke_width=3)
        sd_w = N["bin_sd"] * (bars[1].get_x() - bars[0].get_x())
        sd_ar = DoubleArrow([x_of(N["bin_mean"]) - sd_w, base + 3.75, 0], [x_of(N["bin_mean"]) + sd_w, base + 3.75, 0],
                            buff=0, color=LBLUE, stroke_width=4, tip_length=0.2)
        moments = MathTex(rf"E[X] = np = {dec(N['bin_mean'])}", r"\quad",
                          rf"\mathrm{{Var}}(X) = {dec(N['bin_var'])}", r"\quad",
                          rf"\sigma \approx {dec(N['bin_sd'])}", font_size=38)
        moments.move_to(calc)
        with self.say("8.5") as (tr, t):
            self.play(FadeOut(calc), FadeOut(v3), bars[m].animate.set_fill(RLBLUE), run_time=0.4)
            self.play(Write(moments[0]), Create(mean_ln), run_time=0.8)
            self.cue(tr, t, {"en": "The variance is", "uz": "Dispersiya —"})
            self.play(Write(moments[2]), run_time=0.6)
            self.play(Write(moments[4]), GrowFromCenter(sd_ar), run_time=0.7)

        rush = [k for k in ks if k >= N["bin_tail_from"]]
        tail = MathTex(rf"P(X \ge {rush[0]}) \approx {dec(N['bin_ge6'], 3)}", font_size=44, color=RUSH_C)
        tail.next_to(bars[rush[0]], UP, buff=1.2).shift(RIGHT * 1.0)
        tail.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.08)
        with self.say("8.6") as (tr, t):
            self.play(Indicate(bars[m], color=WHITE, scale_factor=1.05), run_time=0.7)
            self.cue(tr, t, {"en": "Six or more", "uz": "Olti yoki"})
            self.play(*[bars[k].animate.set_fill(RUSH_C) for k in rush], FadeIn(tail), run_time=0.9)
        self.clear_all()


class S08TestSet(LectureScene):
    def construct(self):
        n, acc = N["test_n"], N["test_acc"]
        ks = list(range(round(N["test_mean"] - 4 * N["test_sd"]), n + 1))
        pmf = [N["test_pmf"][k] for k in ks]
        chart, sc = bin_bars(pmf, ks, base=-2.5, height=3.3, step=0.42, width=0.32, size=20)
        bars, kl, floor = chart
        for i, k in enumerate(ks):                      # every second count, so the axis stays readable
            if k % 2:
                kl[i].set_opacity(0)
        head = VGroup(txt(label("correct_answers"), size=30, weight=BOLD),
                      MathTex(rf"\sim \mathrm{{Binomial}}({n},\ {dec(acc)})", font_size=40)).arrange(RIGHT, buff=0.25)
        head.to_edge(UP, buff=SAFE + 0.35)
        mom = MathTex(rf"E = {dec(N['test_mean'])},\qquad \sigma = {dec(N['test_sd'])}", font_size=40, color=LBLUE)
        mom.next_to(head, DOWN, buff=0.3)
        i_of = {k: i for i, k in enumerate(ks)}
        lo, hi = (round(x) for x in N["test_band"])
        band = VGroup(*[bars[i_of[k]] for k in range(lo, hi + 1)])
        marks = VGroup(*[MathTex(str(k), font_size=34, color=HILITE).next_to(bars[i_of[k]], UP, buff=0.12)
                         for k in (lo, hi)])
        with self.say("8.7") as (tr, t):
            self.play(FadeIn(head), Create(floor), FadeIn(kl), run_time=0.7)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.02), run_time=1.2)
            self.cue(tr, t, {"en": "expectation ninety", "uz": "kutilma toʻqson"})
            self.play(Write(mom), run_time=0.8)
            self.cue(tr, t, {"en": "So on another", "uz": "Demak, boshqa"})
            self.play(*[b.animate.set_fill(HILITE) for b in band], FadeIn(marks), run_time=0.9)
        self.clear_all()


def cup(h, color=GREY_B):
    """A coffee cup of height h: a tapered body and a handle."""
    w = h * 0.8
    body = Polygon([-w / 2, h / 2, 0], [w / 2, h / 2, 0], [w * 0.36, -h / 2, 0], [-w * 0.36, -h / 2, 0],
                   stroke_color=color, stroke_width=4, fill_color=color, fill_opacity=0.15)
    handle = Arc(radius=h * 0.2, start_angle=-PI / 2, angle=PI, color=color, stroke_width=4)
    handle.move_to(body.get_right() + LEFT * h * 0.03)
    return VGroup(body, handle)


CUP_KEYS = ("small", "medium", "large")                    # keys into N["cups"]


def cup_names():
    """The three cup sizes' names, in CUP_KEYS order."""
    return [label("small"), label("medium"), label("large")]


def cups_row(scale=1.0):
    """Small, medium and large cups, standing on one line, with their names under them."""
    cs = VGroup(*[cup(h * scale) for h in (0.8, 1.15, 1.5)]).arrange(RIGHT, buff=1.2, aligned_edge=DOWN)
    names = VGroup(*[txt(nm, size=26, color=GREY_B) for nm in cup_names()])
    for c, n_ in zip(cs, names):
        n_.next_to(c, DOWN, buff=0.2)
    return VGroup(cs, names)


class S08HandsOn(LectureScene):
    def construct(self):
        card = pause_card([rf"n = {BN},   p = {dec(BP)}", f"P(X = 0) = ?   ({label('nobody_buys')})"])
        card.to_edge(UP, buff=SAFE + 0.4)
        with self.say("8.8"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        ks = list(range(BN + 1))
        chart, sc = bin_bars(PMF, ks, base=-2.6, height=3.0)
        bars = chart[0]
        calc = MathTex(rf"{dec(1 - BP)}^{{{BN}}} \approx {dec(N['bin_p0'], 3)}", font_size=60, color=HILITE)
        calc.to_edge(UP, buff=SAFE + 0.5)
        v0 = MathTex(dec(N["bin_p0"], 3), font_size=30, color=HILITE).next_to(bars[0], UP, buff=0.12)
        with self.say("8.9") as (tr, t):
            self.play(FadeIn(chart), run_time=0.7)
            self.cue(tr, t, {"en": "We multiply", "uz": "Buni oʻn marta"})
            self.play(Write(calc), bars[0].animate.set_fill(HILITE), FadeIn(v0), run_time=1.0)
        self.clear_all()

        row = cups_row(1.5).move_to(DOWN * 0.3)
        qs = VGroup(*[txt("?", size=44, weight=BOLD, color=HILITE).next_to(c, UP, buff=0.25) for c in row[0]])
        with self.say("8.10") as (tr, t):
            self.cue(tr, t, {"en": "like small", "uz": "Masalan"})
            self.play(LaggedStart(*[FadeIn(VGroup(c, n_), shift=UP * 0.2) for c, n_ in zip(*row)], lag_ratio=0.25),
                      run_time=1.0)
            self.play(FadeIn(qs), run_time=0.5)
        self.clear_all()


SCENES = ["S08Count", "S08Pastries", "S08TestSet", "S08HandsOn"]
