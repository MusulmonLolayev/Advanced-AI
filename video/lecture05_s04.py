"""Lecture 5, section 4 — when the CLT is slow: one office run of forty coffees.

Every number on screen comes from N (capture_l05.py, unit-tested by test_l05.py): office (counts out of
every 20 orders, ordinary = 27/19, mu, var), runs (0-3 office runs among 30 orders: totals and averages;
3 is the pause), run_step, n_customers, office30 (the exact distribution of the average of 30 orders) and
sampling["30"] (pastries). The curves over the two n = 30 panels are N(mu, var/30), drawn from mu and
var only. The gradient trace in the AI beat is an illustration.
"""
import numpy as np

from lecture05_kit import *
from lecture05_s03 import mean_axes, sampling_panel

O = N["office"]
COUNTS = {int(c): k for c, k in O["counts"].items()}         # coffees per order -> how many of every 20
PER = O["per"]
RUNS = N["runs"]
STEP = N["run_step"]
N30 = N["n_customers"]
RUN_C, ORD_C = RLRED, LBLUE


def avg(x):
    return f"{x:.1f}"


def order_bars(unit=0.072, gap=0.56, width=0.34):
    """The 20 orders as bars of height coffees × unit, with the count above each."""
    vals = [c for c in sorted(COUNTS) for _ in range(COUNTS[c])]
    assert len(vals) == PER
    g = VGroup()
    for i, c in enumerate(vals):
        h = max(c * unit, 0.05)
        bar = Rectangle(width=width, height=h, stroke_width=0, fill_color=RUN_C if c == max(COUNTS) else ORD_C,
                        fill_opacity=1).move_to([i * gap, h / 2, 0])
        num = MathTex(str(c), font_size=26, color=RUN_C if c == max(COUNTS) else GREY_B).next_to(bar, UP, buff=0.08)
        g.add(VGroup(bar, num))
    floor = Line(g.get_corner(DL) + LEFT * 0.2, g.get_corner(DR) + RIGHT * 0.2, color=GREY_B, stroke_width=2)
    floor.set_y(g[0][0].get_bottom()[1])
    return VGroup(g, floor), vals


def island_line(n_dots, length=10.0):
    """A number line of averages with the island centres (0, 1, 2 … office runs) as dots."""
    line = NumberLine(x_range=[0, 6, 1], length=length, color=GREY_B, include_numbers=True, font_size=24,
                      decimal_number_config={"num_decimal_places": 0})
    dots = VGroup(*[Dot(line.n2p(RUNS[r]["mean"]), radius=0.12, color=HILITE) for r in range(n_dots)])
    vals = VGroup(*[MathTex(avg(RUNS[r]["mean"]), font_size=32, color=HILITE).next_to(dots[r], UP, buff=0.18)
                    for r in range(n_dots)])
    return line, dots, vals


def step_arc(vals, i):
    """The +1.3 hop from island i to island i + 1, drawn over the value labels."""
    a = vals[i].get_top() + UP * 0.12
    b = vals[i + 1].get_top() + UP * 0.12
    arc = CurvedArrow(a, b, angle=-PI / 2.6, color=RUN_C, stroke_width=3, tip_length=0.18)
    return arc, MathTex(rf"+{avg(STEP)}", font_size=30, color=RUN_C).next_to(arc, UP, buff=0.06)


def office_panel(x_length=5.6, y_length=2.6, xr=(0, 8, 1)):
    """The exact distribution of the average of 30 coffee orders (islands), with N(mu, var/30) over it."""
    s = N["office30"]
    k = N30
    dens = [p * k for p in s["probs"]]
    sd = np.sqrt(O["var"] / k)
    top = max(max(dens), 1 / (sd * np.sqrt(2 * np.pi)))
    ax = mean_axes(top * 1.1, x_length, y_length, True, xr, decimals=0)
    w = max((ax.c2p(1 / k, 0)[0] - ax.c2p(0, 0)[0]) * 0.85, 0.02)
    bars = VGroup(*[Rectangle(width=w, height=max(ax.c2p(0, d)[1] - ax.c2p(0, 0)[1], 1e-3), stroke_width=0,
                              fill_color=ORD_C, fill_opacity=0.9).move_to(ax.c2p(m, d / 2))
                    for m, d in zip(s["means"], dens) if xr[0] <= m <= xr[1] and d > top * 0.004])
    xs = np.linspace(xr[0], xr[1], 300)
    curve = VMobject(stroke_color=HILITE, stroke_width=3).set_points_smoothly(
        [ax.c2p(x, np.exp(-(x - O["mu"]) ** 2 / (2 * sd * sd)) / (sd * np.sqrt(2 * np.pi))) for x in xs])
    return ax, bars, curve


class S04Office(LectureScene):
    def construct(self):
        self.section_card(4)
        (bars, floor), vals = order_bars()
        grp = VGroup(bars, floor).move_to(DOWN * 0.4)
        cap = tagged(PER, label("orders_word"), size=26, color=GREY_B).next_to(floor, DOWN, buff=0.3)
        run = bars[-1]
        run_lab = txt(label("office_run"), size=28, weight=BOLD, color=RUN_C).next_to(run, LEFT, buff=0.3).shift(UP * 0.6)
        with self.say("4.1") as (tr, t):
            self.play(Create(floor), FadeIn(cap), run_time=0.5)
            self.cue(tr, t, {"en": "twelve are one coffee", "uz": "oʻn ikkitasi"})
            self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in bars[:COUNTS[min(COUNTS)]]], lag_ratio=0.08), run_time=0.9)
            self.cue(tr, t, {"en": "six are two", "uz": "oltitasi"})
            self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in bars[COUNTS[1]:PER - 1]], lag_ratio=0.1), run_time=0.7)
            self.cue(tr, t, {"en": "office run of forty", "uz": "butun ofis"})
            self.play(GrowFromEdge(run[0], DOWN), FadeIn(run[1]), FadeIn(run_lab), run_time=0.9)

        ordinary = [c for c in COUNTS if c != max(COUNTS)]
        num = " + ".join(rf"{COUNTS[c]}\cdot{c}" for c in ordinary)
        den = sum(COUNTS[c] for c in ordinary)
        frac_ = MathTex(rf"\frac{{{num}}}{{{den}}} = \frac{{{O['ordinary_frac'][0]}}}{{{O['ordinary_frac'][1]}}} \approx {avg(O['ordinary'])}",
                        font_size=40, color=ORD_C)
        o_lab = txt(label("ordinary_order"), size=28, color=ORD_C)
        box = VGroup(o_lab, frac_).arrange(DOWN, buff=0.25).to_edge(UP, buff=SAFE + 0.3)
        with self.say("4.2") as (tr, t):
            self.play(run.animate.set_opacity(0.35), FadeIn(o_lab), run_time=0.5)
            self.play(Write(frac_), run_time=1.0)
        self.clear_all()


class S04Islands(LectureScene):
    def construct(self):
        head = txt(label("office_runs_among_thirty_orders"), size=30, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        hdr = VGroup(txt(label("office_runs"), size=24, color=GREY_B), txt(label("total_coffees"), size=24, color=GREY_B),
                     txt(label("average_word"), size=24, color=GREY_B))
        rows = VGroup()
        for r in RUNS[:3]:
            rows.add(VGroup(MathTex(str(r["runs"]), font_size=36, color=RUN_C), MathTex(str(round(r["total"])), font_size=36),
                            MathTex(avg(r["mean"]), font_size=36, color=HILITE)))
        xs = [-3.2, 0, 3.2]
        for j, h in enumerate(hdr):
            h.move_to([xs[j], 1.6, 0])
        for i, row in enumerate(rows):
            for j, c in enumerate(row):
                c.move_to([xs[j], 0.9 - 0.65 * i, 0])
        rule = Line([-4.6, 1.25, 0], [4.6, 1.25, 0], color=GREY_D, stroke_width=2)
        with self.say("4.3") as (tr, t):
            self.play(FadeIn(head), FadeIn(hdr), Create(rule), run_time=0.7)
            for row, cue in zip(rows, [{"en": "With none", "uz": "Birorta ham"}, {"en": "With one", "uz": "Bitta boʻlsa"},
                                       {"en": "With two", "uz": "Ikkita boʻlsa"}]):
                self.cue(tr, t, cue)
                self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.play(FadeOut(VGroup(hdr, rows, rule)), run_time=0.4)

        line, dots, vals = island_line(3)
        line.move_to(DOWN * 0.4)
        for d, v, r in zip(dots, vals, RUNS):
            d.move_to(line.n2p(r["mean"]))
            v.next_to(d, UP, buff=0.18)
        hops = [step_arc(vals, i) for i in range(2)]
        arcs = VGroup(*[h[0] for h in hops])
        steps = VGroup(*[h[1] for h in hops])
        gap = Rectangle(width=line.n2p(RUNS[1]["mean"])[0] - line.n2p(RUNS[0]["mean"])[0] - 0.4, height=0.5,
                        stroke_width=0, fill_color=RUN_C, fill_opacity=0.18)
        gap.move_to([(line.n2p(RUNS[0]["mean"])[0] + line.n2p(RUNS[1]["mean"])[0]) / 2, line.get_y(), 0])
        none = txt(label("no_average_here"), size=24, color=RUN_C).next_to(gap, DOWN, buff=0.55)
        with self.say("4.4") as (tr, t):
            self.play(Create(line), FadeIn(dots), FadeIn(vals), run_time=0.8)
            self.play(Create(arcs), FadeIn(steps), run_time=0.8)
            self.cue(tr, t, {"en": "So no average", "uz": "Shuning uchun"})
            self.play(FadeIn(gap), FadeIn(none), run_time=0.6)
        self.clear_all()

        # n = 30: pastries already a bell, coffees still islands
        pa, pb, pc = sampling_panel("30", x_length=5.0, y_length=2.6, xr=(0, 0.9, 0.3))
        oa, ob, oc = office_panel()
        left = VGroup(pa, pb, pc)
        right = VGroup(oa, ob, oc)
        VGroup(left, right).arrange(RIGHT, buff=1.0).move_to(DOWN * 0.3)
        lt = txt(label("pastries_short"), size=28, weight=BOLD, color=LBLUE).next_to(pa, UP, buff=0.35)
        rt = txt(label("coffees"), size=28, weight=BOLD, color=LBLUE).next_to(oa, UP, buff=0.35)
        rt.set_y(max(rt.get_y(), lt.get_y()))
        lt.set_y(rt.get_y())
        nn = MathTex(rf"n = {N30}", font_size=40).to_edge(UP, buff=SAFE + 0.3)
        isl = VGroup()
        for r in RUNS[:3]:
            m = r["mean"]
            col = [b for b in ob if abs(oa.p2c(b.get_center())[0] - m) < 0.5]
            top_y = max(b.get_top()[1] for b in col) if col else oa.c2p(m, 0)[1]
            isl.add(MathTex(str(r["runs"]), font_size=26, color=RUN_C).move_to([oa.c2p(m, 0)[0], top_y + 0.22, 0]))
        cap = txt(label("office_runs_inside"), size=22, color=RUN_C).next_to(oa, DOWN, buff=0.55)
        with self.say("4.5") as (tr, t):
            self.play(FadeIn(nn), FadeIn(rt), FadeIn(oa), FadeIn(ob), run_time=0.9)
            self.play(Create(oc), run_time=0.6)
            self.cue(tr, t, {"en": "one for each", "uz": "har biri ichidagi"})
            self.play(FadeIn(isl), FadeIn(cap), run_time=0.6)
            self.cue(tr, t, {"en": "For pastries", "uz": "Pishiriqlarda"})
            self.play(FadeIn(lt), FadeIn(pa), FadeIn(pb), run_time=0.7)
            self.play(Create(pc), run_time=0.5)
        self.clear_all()


class S04Rule(LectureScene):
    def construct(self):
        rule = MathTex(rf"n \ge {N30}", font_size=72, color=HILITE)
        not_t = txt(label("a_rule_of_thumb_not_a_theorem"), size=32, color=GREY_B).next_to(rule, DOWN, buff=0.45)
        breaks = txt(label("a_rare_huge_value_breaks_it"), size=30, color=RUN_C).next_to(not_t, DOWN, buff=0.35)
        VGroup(rule, not_t, breaks).move_to(UP * 0.2)
        with self.say("4.6") as (tr, t):
            self.play(Write(rule), run_time=0.7)
            self.play(FadeIn(not_t), run_time=0.5)
            self.cue(tr, t, {"en": "A rare huge value", "uz": "Kam uchraydigan"})
            self.play(FadeIn(breaks), run_time=0.5)
        self.clear_all()

        # AI: a rare huge gradient makes the average jump; clipping caps it (an illustration)
        rng = np.random.default_rng(3)
        n = 48
        vals = np.abs(rng.normal(1.0, 0.25, n))
        vals[31] = 6.0
        x0, dx, base = -5.4, 0.22, -2.4
        k = 0.55
        bars = VGroup(*[Rectangle(width=0.14, height=v * k, stroke_width=0, fill_color=RUN_C if i == 31 else LBLUE,
                                  fill_opacity=0.9).move_to([x0 + i * dx, base + v * k / 2, 0]) for i, v in enumerate(vals)])
        floor = Line([x0 - 0.2, base, 0], [x0 + n * dx, base, 0], color=GREY_B, stroke_width=2)
        cap_y = base + 1.8 * k
        clip = DashedLine([x0 - 0.2, cap_y, 0], [x0 + n * dx, cap_y, 0], color=HILITE, stroke_width=3)
        clip_t = txt(label("gradient_clipping"), size=26, color=HILITE).next_to(clip, UP, buff=0.12).align_to(clip, LEFT)
        clip_t.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.05)
        g_t = txt(label("gradient_size"), size=24, color=GREY_B).next_to(floor, DOWN, buff=0.25)
        clipped = Rectangle(width=0.14, height=1.8 * k, stroke_width=0, fill_color=HILITE, fill_opacity=0.9)
        clipped.move_to([bars[31].get_x(), base + 0.9 * k, 0])
        note = info(label("illustration"))
        with self.say("4.7") as (tr, t):
            self.play(Create(floor), FadeIn(g_t), FadeIn(note), run_time=0.5)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.03), run_time=1.2)
            self.cue(tr, t, {"en": "clipped", "uz": "kesish"})
            self.play(Create(clip), FadeIn(clip_t), run_time=0.6)
            self.play(Transform(bars[31], clipped), run_time=0.6)
        self.clear_all()


class S04HandsOn(LectureScene):
    def construct(self):
        r3 = RUNS[3]
        card = pause_card([f"{N30} {label('orders_word')}",
                           f"{r3['runs']} {label('office_runs')}",
                           "x̄ = ?"])
        card.to_edge(UP, buff=SAFE + 0.3)
        with self.say("4.8"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        line, dots, vals = island_line(4)
        line.move_to(DOWN * 0.6)
        for d, v, r in zip(dots, vals, RUNS):
            d.move_to(line.n2p(r["mean"]))
            v.next_to(d, UP, buff=0.18)
        new = VGroup(dots[3], vals[3])
        arc, step = step_arc(vals, 2)
        runs_t = VGroup(*[MathTex(str(r["runs"]), font_size=24, color=RUN_C).next_to(dots[i], DOWN, buff=0.75)
                          for i, r in enumerate(RUNS)])
        runs_cap = txt(label("office_runs"), size=22, color=RUN_C).next_to(runs_t, DOWN, buff=0.2)
        with self.say("4.9") as (tr, t):
            self.play(Create(line), FadeIn(VGroup(dots[:3], vals[:3])), FadeIn(runs_t[:3]), FadeIn(runs_cap), run_time=0.8)
            self.play(Create(arc), FadeIn(step), run_time=0.6)
            self.play(FadeIn(new, scale=1.4), FadeIn(runs_t[3]), run_time=0.6)
        self.clear_all()

        q = txt(label("where_does_it_matter_most_in_ai_q"), size=34, weight=BOLD, color=HILITE)
        with self.say("4.10"):
            self.play(FadeIn(q, shift=UP * 0.2), run_time=0.8)
        self.clear_all(run_time=0.3)


SCENES = ["S04Office", "S04Islands", "S04Rule", "S04HandsOn"]
