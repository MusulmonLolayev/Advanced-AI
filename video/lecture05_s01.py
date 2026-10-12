"""Lecture 5, section 1 — the sampling distribution: an average is a random variable.

Pastries per order (Lecture 3): 0, 1 or 2 with probabilities N["pastry"]. With two customers the
average takes five values; their exact probabilities are N["two"] (a convolution in capture_l05.py),
so E = 0.4 and Var = 0.22 = 0.44 / 2 are read off real arithmetic. Every number shown comes from N.
"""
from lecture05_kit import *

PASTRY = N["pastry"]                         # [0.7, 0.2, 0.1] for 0, 1, 2 pastries
VALS = list(range(len(PASTRY)))
TWO = N["two"]                               # {"means": [...], "probs": [...]}
MU, VAR = N["mu"], N["var"]
BAR_C, MEAN_C = LBLUE, HILITE


def num(x, places=2):
    """A probability or mean as shown: 0.49, 1.5, 0."""
    return dec(x, places)


def bar_chart(values, probs, base=-2.4, height=3.4, step=1.6, width=1.0, color=BAR_C, size=30, vmax=None):
    """Bars on a floor: the probability above, the value below. Returns (bars, tops, ticks, floor)."""
    vmax = vmax or max(probs)
    k = height / vmax
    xs = [(i - (len(values) - 1) / 2) * step for i in range(len(values))]
    bars = VGroup(*[Rectangle(width=width, height=max(p * k, 1e-3), stroke_width=0, fill_color=color,
                              fill_opacity=1).move_to([x, base + p * k / 2, 0]) for x, p in zip(xs, probs)])
    tops = VGroup(*[MathTex(num(p), font_size=size).next_to(b, UP, buff=0.12) for b, p in zip(bars, probs)])
    ticks = VGroup(*[MathTex(num(v), font_size=size, color=GREY_B).next_to([x, base, 0], DOWN, buff=0.2)
                     for x, v in zip(xs, values)])
    floor = Line([xs[0] - width, base, 0], [xs[-1] + width, base, 0], color=GREY_B, stroke_width=2)
    return bars, tops, ticks, floor


def mu_marker(bars, base, step, words=False):
    """A dashed line at the mean, kept below the bar labels it would cross; mu and a pointer sit under the
    value ticks, where no bar or label is."""
    x = bars[0].get_center()[0] + (MU - TWO["means"][0]) / (TWO["means"][1] - TWO["means"][0]) * step
    top = bars[1].get_top()[1] - 0.05
    ln = DashedLine([x, base, 0], [x, top, 0], color=MEAN_C, stroke_width=4)
    tag = MathTex(r"\mu", font_size=36, color=MEAN_C)
    if words:
        tag = VGroup(tag, txt(label("the_truth"), size=22, color=MEAN_C)).arrange(RIGHT, buff=0.12)
    tip = Triangle(color=MEAN_C, fill_opacity=1, stroke_width=0).scale(0.1).move_to([x, base - 0.62, 0])
    tag.next_to(tip, DOWN, buff=0.08)
    return ln, VGroup(tip, tag)


def order_card(pastries, color=GREY_B):
    """One order: a cup outline holding its pastries as dots."""
    box = RoundedRectangle(corner_radius=0.12, width=1.1, height=1.1, stroke_color=color, stroke_width=3)
    dots = VGroup(*[Dot(radius=0.13, color=HILITE) for _ in range(pastries)]).arrange(RIGHT, buff=0.16)
    if pastries:
        dots.move_to(box)
    n = MathTex(str(pastries), font_size=30, color=GREY_B).next_to(box, DOWN, buff=0.15)
    return VGroup(box, dots, n)


class S01Samples(LectureScene):
    def construct(self):
        self.section_card(1)
        # one sample gives one average; another sample gives another (a picture, not data)
        rng = np.random.default_rng(5)
        cloud = VGroup(*[Dot([x, y, 0], radius=0.05, color=GREY_B, fill_opacity=0.7)
                         for x, y in zip(rng.uniform(-6.0, -1.0, 140), rng.uniform(-2.2, 1.8, 140))])
        pop_l = txt(label("population"), size=24, color=GREY_B).next_to(cloud, UP, buff=0.2)
        picks = [(-4.6, 0.6, RLGREEN), (-2.4, -1.0, HILITE)]
        rings = VGroup(*[Circle(radius=0.75, color=c, stroke_width=4).move_to([x, y, 0]) for x, y, c in picks])
        means = VGroup(*[MathTex(r"\bar{x}", font_size=56, color=c) for _, _, c in picks])
        means[0].move_to([3.0, 1.0, 0])
        means[1].move_to([3.0, -1.2, 0])
        names = VGroup(txt(label("one_sample"), size=26, color=RLGREEN).next_to(means[0], RIGHT, buff=0.35),
                       txt(label("another_sample"), size=26, color=HILITE).next_to(means[1], RIGHT, buff=0.35))
        arrows = VGroup(*[Arrow(r.get_right(), m.get_left(), buff=0.15, color=c, stroke_width=4)
                          for r, m, (_, _, c) in zip(rings, means, picks)])
        neq = MathTex(r"\neq", font_size=60).move_to((means[0].get_center() + means[1].get_center()) / 2)
        change = txt(label("the_average_changes"), size=28, color=GREY_A).to_edge(UP, buff=SAFE + 0.4)
        note = info(label("illustration"))
        with self.say("1.1") as (tr, t):
            self.play(FadeIn(cloud, lag_ratio=0.01), FadeIn(pop_l), FadeIn(note), run_time=1.0)
            self.play(Create(rings[0]), GrowArrow(arrows[0]), FadeIn(means[0]), FadeIn(names[0]), run_time=0.9)
            self.cue(tr, t, {"en": "Take a different sample", "uz": "Boshqa tanlanma olsak"})
            self.play(Create(rings[1]), GrowArrow(arrows[1]), FadeIn(means[1]), FadeIn(names[1]), run_time=0.9)
            self.play(FadeIn(neq), FadeIn(change), run_time=0.5)
        self.clear_all()

        # pastries per order, from Lecture 3
        bars, tops, ticks, floor = bar_chart(VALS, PASTRY, step=1.8, width=1.1)
        chart = VGroup(bars, tops, ticks, floor).shift(LEFT * 2.6)
        xl = txt(label("pastries"), size=24, color=GREY_B).next_to(floor, DOWN, buff=0.75)
        stats = VGroup(MathTex(rf"\mu = {num(MU)}", font_size=50, color=MEAN_C),
                       MathTex(rf"\sigma^2 = {num(VAR)}", font_size=50, color=GREY_A)).arrange(DOWN, buff=0.45)
        stats.move_to(RIGHT * 3.8 + UP * 0.4)
        with self.say("1.2") as (tr, t):
            self.play(Create(floor), FadeIn(ticks), FadeIn(xl), run_time=0.6)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.25), FadeIn(tops), run_time=1.1)
            self.cue(tr, t, {"en": "The mean is", "uz": "Oʻrtacha nol"})
            self.play(Write(stats[0]), run_time=0.6)
            self.cue(tr, t, {"en": "the variance", "uz": "dispersiya"})
            self.play(Write(stats[1]), run_time=0.6)
        self.clear_all()

        # two customers: same shop, same day, different averages
        lo_pair, hi_pair = (VALS[0], VALS[0]), (VALS[1], VALS[2])
        head = txt(label("two_customers"), size=32, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.4)

        def pair_row(pair, color):
            cards = VGroup(*[order_card(p, color) for p in pair]).arrange(RIGHT, buff=0.5)
            m = sum(pair) / len(pair)
            eq = MathTex(rf"\bar{{x}} = \tfrac{{{pair[0]} + {pair[1]}}}{{{len(pair)}}} = {num(m)}", font_size=46, color=color)
            return VGroup(cards, eq.next_to(cards, RIGHT, buff=0.7))

        row1, row2 = pair_row(lo_pair, RLGREEN), pair_row(hi_pair, HILITE)
        rows = VGroup(row1, row2).arrange(DOWN, buff=0.7, aligned_edge=LEFT).move_to(DOWN * 0.2)
        assert num(sum(hi_pair) / 2) == num(TWO["means"][3]) and num(sum(lo_pair) / 2) == num(TWO["means"][0])
        same = txt(label("same_shop_different_answer"), size=26, color=GREY_A).to_edge(DOWN, buff=SAFE + 0.5)
        with self.say("1.3") as (tr, t):
            self.play(FadeIn(head), run_time=0.4)
            self.cue(tr, t, {"en": "We might see zero", "uz": "Nol va nol"})
            self.play(FadeIn(row1[0], shift=UP * 0.2), Write(row1[1]), run_time=0.9)
            self.cue(tr, t, {"en": "Or one and two", "uz": "Bir va ikki"})
            self.play(FadeIn(row2[0], shift=UP * 0.2), Write(row2[1]), run_time=0.9)
            self.cue(tr, t, {"en": "Same shop", "uz": "Qahvaxona oʻsha"})
            self.play(FadeIn(same), run_time=0.5)
        self.clear_all()

        # repeat the sampling: the averages pile up into a distribution of their own
        bars2, tops2, ticks2, floor2 = bar_chart(TWO["means"], TWO["probs"], step=1.7, width=1.0, height=3.2)
        chart2 = VGroup(bars2, tops2, ticks2, floor2).shift(DOWN * 0.2)
        rv = txt(label("sample_mean_is_a_random_variable"), size=30, color=LBLUE).to_edge(UP, buff=SAFE + 0.35)
        sd_l = txt(label("sampling_distribution_of_the_mean"), size=30, weight=BOLD, color=HILITE)
        sd_l.next_to(rv, DOWN, buff=0.3)
        xl2 = txt(label("average_of_two_orders"), size=22, color=GREY_B).next_to(floor2, DOWN, buff=0.7)
        with self.say("1.4") as (tr, t):
            self.play(FadeIn(rv), run_time=0.6)
            self.cue(tr, t, {"en": "Repeat the sampling", "uz": "Tanlashni qayta-qayta"})
            self.play(Create(floor2), FadeIn(ticks2), FadeIn(xl2), run_time=0.6)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars2], lag_ratio=0.2), run_time=1.4)
            self.cue(tr, t, {"en": "We call it", "uz": "Buni tanlanma"})
            self.play(FadeIn(sd_l, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S01TwoOrders(LectureScene):
    def construct(self):
        # the table of the five averages and their exact probabilities
        cols = len(TWO["means"])
        cw, ch = 1.45, 0.8
        head_w = 2.9
        row_l = VGroup(MathTex(r"\bar{x}", font_size=40), txt(label("probability_word"), size=26))
        cells = VGroup()
        for r, vals in enumerate((TWO["means"], TWO["probs"])):
            for c, v in enumerate(vals):
                cells.add(MathTex(num(v), font_size=38, color=WHITE if r == 0 else HILITE)
                          .move_to([-((cols * cw + head_w) / 2) + head_w + (c + 0.5) * cw, 0.4 - r * ch, 0]))
        for r, m in enumerate(row_l):
            m.move_to([-((cols * cw + head_w) / 2) + head_w / 2, 0.4 - r * ch, 0])
        x0 = -((cols * cw + head_w) / 2) + head_w
        rule = VGroup(Line([x0 - head_w, 0.4 - ch / 2, 0], [x0 + cols * cw, 0.4 - ch / 2, 0], color=GREY_D, stroke_width=2),
                      Line([x0, 0.4 + ch / 2, 0], [x0, 0.4 - 1.5 * ch, 0], color=GREY_D, stroke_width=2))
        table = VGroup(row_l, cells, rule).move_to(UP * 2.0)
        bars, tops, ticks, floor = bar_chart(TWO["means"], TWO["probs"], base=-2.7, height=2.4, step=1.6, width=0.95,
                                             size=26)
        chart = VGroup(bars, tops, ticks, floor).shift(LEFT * 1.6)
        with self.say("1.5") as (tr, t):
            self.play(FadeIn(row_l), Create(rule), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(c) for c in cells[:cols]], lag_ratio=0.15), run_time=1.0)
            self.cue(tr, t, {"en": "Their probabilities", "uz": "Ehtimollari"})
            self.play(LaggedStart(*[FadeIn(c) for c in cells[cols:]], lag_ratio=0.15), run_time=1.0)
            self.play(Create(floor), FadeIn(ticks), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.15),
                      FadeIn(tops), run_time=1.0)

        # the expectation: centred on the truth
        ex = MathTex(rf"E[\bar{{x}}] = {num(N['two_mean'])} = \mu", font_size=44, color=MEAN_C)
        ex.move_to(RIGHT * 4.3 + DOWN * 0.6)
        mu_line, mu_t = mu_marker(bars, -2.7, 1.6)
        unb = txt(label("unbiased_estimate"), size=28, weight=BOLD, color=MEAN_C).next_to(ex, DOWN, buff=0.35)
        with self.say("1.6") as (tr, t):
            self.play(Create(mu_line), FadeIn(mu_t), run_time=0.7)
            self.play(Write(ex), run_time=0.8)
            self.cue(tr, t, {"en": "The sample mean is centred", "uz": "Tanlanma oʻrtachasi haqiqatga"})
            self.play(FadeIn(unb, shift=UP * 0.2), run_time=0.6)

        # the variance: half of 0.44 — sigma squared over n
        var = VGroup(MathTex(rf"\mathrm{{Var}}(\bar{{x}}) = {num(N['two_e2'])} - {num(N['two_mean'])}^2 = {num(N['two_var'])}",
                             font_size=40),
                     MathTex(rf"\tfrac{{{num(VAR)}}}{{2}} = {num(N['two_formula'])}", font_size=44, color=HILITE))
        var.arrange(DOWN, buff=0.3).move_to(RIGHT * 4.0 + DOWN * 0.9)
        rule2 = MathTex(r"E[\bar{x}] = \mu,\qquad \mathrm{Var}(\bar{x}) = \frac{\sigma^2}{n}", font_size=48, color=LBLUE)
        rule2.move_to(table)
        if var.get_right()[0] > 6.0:
            var.shift(LEFT * (var.get_right()[0] - 6.0))
        with self.say("1.7") as (tr, t):
            self.play(FadeOut(ex), FadeOut(unb), run_time=0.4)
            self.play(Write(var[0]), run_time=0.9)
            self.cue(tr, t, {"en": "half of zero point four four", "uz": "qirq toʻrtning yarmi"})
            self.play(Write(var[1]), run_time=0.7)
            self.cue(tr, t, {"en": "The general rule", "uz": "Umumiy qoida"})
            self.play(FadeOut(table), FadeIn(rule2, shift=UP * 0.2), run_time=0.8)
        self.clear_all()

        # AI: an accuracy measured on a test set is a sample mean too (a picture, not data)
        rng = np.random.default_rng(8)
        rows = VGroup()
        for name in (label("test_set"), label("another_test_set")):
            marks = VGroup(*[Square(0.34, stroke_width=0, fill_color=RLGREEN if ok else RLRED, fill_opacity=0.9)
                             for ok in rng.random(14) < 0.8]).arrange(RIGHT, buff=0.08)
            rows.add(VGroup(txt(name, size=24, color=GREY_B), marks).arrange(DOWN, buff=0.15, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to(LEFT * 2.2)
        accs = VGroup(*[MathTex(r"\bar{x}_" + str(i + 1), font_size=46, color=c).next_to(r[1], RIGHT, buff=0.9)
                        for i, (r, c) in enumerate(zip(rows, (RLGREEN, HILITE)))])
        diff = txt(label("a_different_accuracy"), size=28, color=HILITE).next_to(VGroup(rows, accs), DOWN, buff=0.6)
        head = txt(label("accuracy"), size=32, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.4)
        note = info(label("illustration"))
        with self.say("1.8") as (tr, t):
            self.play(FadeIn(head), FadeIn(rows[0]), FadeIn(note), run_time=0.8)
            self.play(FadeIn(accs[0]), run_time=0.4)
            self.cue(tr, t, {"en": "a different test set", "uz": "boshqa test toʻplami"})
            self.play(FadeIn(rows[1]), FadeIn(accs[1]), run_time=0.8)
            self.play(FadeIn(diff), run_time=0.5)
        self.clear_all()


class S01HandsOn(LectureScene):
    def construct(self):
        card = pause_card([label("neither_of_two_buys_q"), r"P(x̄ = 0) = ?"])
        with self.say("1.9"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        # the answer: both orders empty, 0.7 x 0.7, the table's first entry
        p0 = PASTRY[0]
        calc = MathTex(rf"{num(p0)} \times {num(p0)} = {num(N['two_both_none'])}", font_size=60, color=HILITE)
        calc.to_edge(UP, buff=SAFE + 0.6)
        cards = VGroup(order_card(VALS[0], RLGREEN), order_card(VALS[0], RLGREEN)).arrange(RIGHT, buff=0.5)
        cards.next_to(calc, DOWN, buff=0.4)
        bars, tops, ticks, floor = bar_chart(TWO["means"], TWO["probs"], base=-3.0, height=2.0, step=1.5, width=0.9,
                                             size=26)
        chart = VGroup(bars, tops, ticks, floor)
        first = txt(label("first_number_in_the_table"), size=26, color=HILITE).next_to(tops[0], RIGHT, buff=0.4)
        with self.say("1.10") as (tr, t):
            self.play(FadeIn(cards), Write(calc), run_time=1.0)
            self.play(FadeIn(chart), run_time=0.6)
            self.cue(tr, t, {"en": "The first number", "uz": "Jadvaldagi birinchi"})
            self.play(Indicate(VGroup(bars[0], tops[0]), color=HILITE, scale_factor=1.1), FadeIn(first), run_time=0.9)
        self.clear_all()

        # the next question: how far does an average usually sit from the truth?
        bars, tops, ticks, floor = bar_chart(TWO["means"], TWO["probs"], base=-2.4, height=3.0, step=1.6, width=0.95)
        chart = VGroup(bars, tops, ticks, floor)
        mu_line, mu_t = mu_marker(bars, -2.4, 1.6, words=True)
        x_mu = mu_line.get_start()[0]
        spread = DoubleArrow([x_mu - 1.3, 1.4, 0], [x_mu + 1.3, 1.4, 0], buff=0, color=LBLUE, stroke_width=4)
        q = txt(label("how_far_from_the_truth_q"), size=34, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.4)
        with self.say("1.11") as (tr, t):
            self.play(FadeIn(chart), Create(mu_line), FadeIn(mu_t), run_time=0.8)
            self.play(GrowFromCenter(spread), FadeIn(q), run_time=0.8)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S01Samples", "S01TwoOrders", "S01HandsOn"]
