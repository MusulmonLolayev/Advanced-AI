"""Lecture 1, section 4 — the mean (was video 1, v01_mean.py, folded into the lecture).

Every number shown here comes from statistics/raw/, which statistics/capture_v01.py
produces (and asserts against the slide figures). Every picture is drawn from the
same files: the 600 dots are the 600 real salaries, the bars are the same people.
The narration is the approved section 4 of narration/lecture01.md.
"""
import json

import numpy as np
from lecture01_kit import *

RAW = Path(__file__).parent / "statistics" / "raw"
D = json.loads((RAW / "v01_numbers.json").read_text())
SAL = np.sort(np.loadtxt(RAW / "v01_salaries.txt"))
DRINKERS = np.sort(np.loadtxt(RAW / "v01_drinkers.txt"))

N_EMP = D["n_emp"]
N_DRINKERS = D["n_drinkers"]
PAYROLL_MEAN = D["payroll_mean"]
PAYROLL_MEDIAN = D["payroll_median"]
PAYROLL_TOTAL = D["payroll_total"]
EXCESS = D["excess"]
MEDIAN_TOTAL, MEDIAN_SHORT = D["median_total"], D["median_short"]
DRINK_MEAN, DRINK_MED = D["drink_mean"], D["drink_median"]
AFTER_MEAN, AFTER_MED = D["after_mean"], D["after_median"]
BILLIONAIRE = D["billionaire"]
NINE, NINE_SUM, NINE_MEAN, NINE_BELOW = D["nine"], D["nine_sum"], D["nine_mean"], D["nine_below"]

# The narration speaks these figures in words, so fail loudly if the script's
# output ever moves away from what the voice says.
assert (N_EMP, N_DRINKERS, NINE_SUM, NINE_BELOW) == (600, 50, 453, 6)
assert len(SAL) == N_EMP and len(DRINKERS) == N_DRINKERS
assert np.allclose(DRINKERS, SAL[::N_EMP // N_DRINKERS][:N_DRINKERS])
assert (round(PAYROLL_MEAN), round(PAYROLL_TOTAL)) == (51613, 30968030)
assert (round(DRINK_MEAN), round(DRINK_MED)) == (50627, 47323)
assert (round(AFTER_MEAN), round(AFTER_MED)) == (2941226105, 47761)
assert round(NINE_MEAN, 3) == 50.333

# ─── words ────────────────────────────────────────────────────────────────
T = {
    # on screen
    "employees": {"en": "{n} employees", "uz": "{n} xodim"},
    "question": {"en": "What do people earn here?", "uz": "Bu yerda odamlar qancha maosh oladi?"},
    "salary": {"en": "salary", "uz": "maosh"},
    "one": {"en": "one number?", "uz": "bitta son?"},
    "mean": {"en": "mean", "uz": "oʻrtacha"},
    "the_mean": {"en": "the mean", "uz": "oʻrtacha qiymat"},
    "median": {"en": "median", "uz": "mediana"},
    "fills": {"en": "{v} above the line  =  {v} missing below it",
              "uz": "chiziq ustidagi {v}  =  ostida yetishmagan {v}"},
    "remembers": {"en": "The mean remembers the total", "uz": "Oʻrtacha qiymat umumiy summani eslab qoladi"},
    "people": {"en": "{n} people", "uz": "{n} kishi"},
    "each": {"en": "{v} each", "uz": "har biriga {v}"},
    "missing": {"en": "{v} missing", "uz": "{v} yetishmaydi"},
    "no_other": {"en": "No other summary does that.",
                 "uz": "Boshqa hech bir koʻrsatkich buni qilolmaydi."},
    "billionaire": {"en": "a billionaire", "uz": "milliarder"},
    "nobody": {"en": "describes nobody here", "uz": "hech kimni tasvirlamaydi"},
    "log": {"en": "each tick is ten times the one before", "uz": "har bir belgi oldingisidan 10 marta katta"},
    "not_moved": {"en": "The line that did not move", "uz": "Siljimagan chiziq"},
    "before": {"en": "before", "uz": "avval"},
    "after": {"en": "after", "uz": "keyin"},
    "is_median": {"en": "That line is the median.", "uz": "Bu chiziq — mediana."},
    "task1": {"en": "We work out the mean of these nine.",
              "uz": "Oʻrtacha qiymatini hisoblaymiz."},
    "task2": {"en": "We count how many of the nine earn less than it.",
              "uz": "Nechtasi undan kam olishini sanaymiz."},
    "unit": {"en": "salaries, in thousands of dollars", "uz": "maoshlar, ming dollarda"},
    "total": {"en": "total", "uz": "yigʻindi"},
    "below": {"en": "{k} of the {n} earn less than that", "uz": "{n} kishidan {k} nafari undan kam oladi"},
    "loss_cap": {"en": "training = making this number smaller", "uz": "oʻqitish = shu sonni kichraytirish"},
}


def say(key, **kw):
    """Narration from the approved draft (section 4), or a screen label from T."""
    if f"4.{key}" in NARRATION:
        return line(f"4.{key}")
    return T[key][LANG].format(**kw)


# ─── the 600 salaries as a dot histogram (one dot per person) ─────────────
H0, H1, HX0, HX1 = 25_000, 155_000, -5.8, 5.8
BIN, PER_ROW, DS, HBASE = 5_000, 4, 0.085, -2.2


def hx(s):
    return HX0 + (HX1 - HX0) * (s - H0) / (H1 - H0)


def hist_positions():
    pos, filled = [], {}
    for s in SAL:
        b = int((s - H0) // BIN)
        k = filled.get(b, 0)
        filled[b] = k + 1
        x = hx(H0 + (b + 0.5) * BIN) + (k % PER_ROW - (PER_ROW - 1) / 2) * DS
        pos.append([x, HBASE + 0.08 + (k // PER_ROW) * DS, 0])
    return pos


def hist_axis():
    axis = Line([HX0, HBASE, 0], [HX1, HBASE, 0], stroke_width=2, color=GREY_B)
    marks = VGroup()
    for v in range(40_000, 160_000, 20_000):
        t = Line(UP * 0.08, DOWN * 0.08, stroke_width=2, color=GREY_B).move_to([hx(v), HBASE, 0])
        marks.add(t, txt(f"${v // 1000}k", size=20, color=GREY_B).next_to(t, DOWN, buff=0.15))
    lab = txt(say("salary"), size=22, color=GREY_B).next_to(axis, DOWN, buff=0.6)
    return VGroup(axis, marks, lab)


def hist_dots():
    return VGroup(*[Dot(p, radius=0.034, color=RLBLUE, fill_opacity=0.9) for p in hist_positions()])


# ─── the 600 salaries as sorted bars (scenes 2-3) ─────────────────────────
BX0, BX1, BBASE, BSCALE = -5.5, 5.5, -2.4, 4.0 / SAL.max()
BW = (BX1 - BX0) / N_EMP
HM = PAYROLL_MEAN * BSCALE


def bar(i, h, color=RLBLUE, opacity=1.0, y0=BBASE):
    r = Rectangle(width=BW, height=max(h, 1e-3), stroke_width=0, fill_color=color, fill_opacity=opacity)
    return r.move_to([BX0 + (i + 0.5) * BW, y0 + max(h, 1e-3) / 2, 0])


def salary_bars():
    return VGroup(*[bar(i, s * BSCALE) for i, s in enumerate(SAL)])


def level_bars(color=RLBLUE):
    return VGroup(*[bar(i, HM, color) for i in range(N_EMP)])


def mean_line(y):
    return Line([BX0 - 0.2, y, 0], [BX1 + 0.2, y, 0], color=RLRED, stroke_width=4)


class S04Problem(LectureScene):
    def construct(self):
        self.section_card(4)
        head = txt(say("employees", n=N_EMP), size=34, color=GREY_B).to_edge(UP, buff=SAFE + 0.3)
        rng = np.random.default_rng(7)
        order = rng.permutation(N_EMP)
        grid = VGroup(*[Dot(radius=0.045) for _ in range(N_EMP)])
        grid.arrange_in_grid(rows=20, cols=30, buff=0.17).move_to(DOWN * 0.25)
        dots = VGroup(*[Dot(grid[order[i]].get_center(), radius=0.045, color=RLBLUE, fill_opacity=0.9)
                        for i in range(N_EMP)])
        target = hist_positions()
        axis = hist_axis()

        t = say("s1a")
        with self.voiceover(t) as tr:
            self.play(FadeIn(head), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.004, run_time=3.0))
            self.until(tr, t, 1)
            self.play(FadeIn(axis), run_time=0.6)
            self.play(LaggedStart(*[d.animate.move_to(p).scale(0.034 / 0.045)
                                    for d, p in zip(dots, target)], lag_ratio=0.002, run_time=3.0))
            self.until(tr, t, 2)
            q = txt(say("question"), size=40, weight=BOLD, color=HILITE).move_to(head)
            self.play(FadeOut(head, shift=UP * 0.3), FadeIn(q, shift=UP * 0.3), run_time=1.0)

        # a flicker of real salaries: far too many to read out
        pool = SAL[rng.permutation(N_EMP)]
        def column(j):
            c = VGroup(*[txt(money(v), size=26, color=WHITE) for v in pool[j:j + 7]])
            return c.arrange(DOWN, aligned_edge=RIGHT, buff=0.16).move_to([4.6, 0.8, 0])
        panel = RoundedRectangle(corner_radius=0.15, width=2.9, height=3.4, stroke_color=GREY_D,
                                 fill_color=BLACK, fill_opacity=0.85).move_to([4.6, 0.8, 0])
        t = say("s1b")
        with self.voiceover(t) as tr:
            col = column(0)
            self.play(FadeIn(panel), FadeIn(col), run_time=0.4)
            for j in range(1, 22):
                col.become(column(j))
                self.wait(0.1)
            self.until(tr, t, 1)
            one = box(say("one"), color=HILITE, width=2.6, height=1.0, size=28).move_to(panel)
            self.play(FadeOut(col), ReplacementTransform(panel, one[0]), FadeIn(one[1]), run_time=0.8)
            self.until(tr, t, 2)
            probe = DashedLine([0, HBASE, 0], [0, 1.0, 0], color=HILITE, stroke_width=4)
            mark = txt("?", size=40, weight=BOLD, color=HILITE).next_to(probe, UP, buff=0.1)
            ptr = VGroup(probe, mark).move_to([hx(35_000), probe.get_center()[1] + 0.25, 0])
            self.play(FadeIn(ptr), run_time=0.3)
            for v in (110_000, 45_000, 70_000):
                self.play(ptr.animate.set_x(hx(v)), run_time=0.55)
        self.clear_all()


class S04Mean(LectureScene):
    def construct(self):
        dots, axis = hist_dots(), hist_axis()
        self.add(dots, axis)
        bars, level = salary_bars(), level_bars()
        formula = MathTex(r"\bar{x} \;=\; \frac{1}{n}\sum_{i=1}^{n} x_i", font_size=50)
        formula.to_edge(UP, buff=SAFE + 0.35)

        t = say("s2a")
        with self.voiceover(t) as tr:
            self.until(tr, t, 1)
            self.play(FadeOut(axis), *[ReplacementTransform(d, b) for d, b in zip(dots, bars)], run_time=1.6)
            self.play(Transform(bars, level), run_time=1.8)

        line = mean_line(BBASE + HM)
        value = txt(money(PAYROLL_MEAN), size=60, weight=BOLD, color=WHITE).move_to([0, 0.35, 0])
        label = txt(say("the_mean"), size=30, color=RLRED).next_to(value, DOWN, buff=0.2)
        t = say("s2b")
        with self.voiceover(t) as tr:
            self.play(Create(line), FadeIn(value, shift=UP * 0.3), run_time=1.0)
            self.until(tr, t, 1)
            self.play(FadeIn(label), FadeIn(formula), run_time=0.8)

        # The same people again: what sits above the line is exactly what is missing below it.
        base = VGroup(*[bar(i, min(s * BSCALE, HM)) for i, s in enumerate(SAL)])
        tops = VGroup(*[bar(i, s * BSCALE - HM, HILITE, y0=BBASE + HM) for i, s in enumerate(SAL) if s * BSCALE > HM])
        gaps = VGroup(*[bar(i, HM - s * BSCALE, HILITE, 0.0, y0=BBASE + s * BSCALE)
                        for i, s in enumerate(SAL) if s * BSCALE < HM])
        for g in gaps:
            g.set_stroke(HILITE, width=0.6, opacity=0.8)
        fills = txt(say("fills", v=money(EXCESS)), size=26, color=HILITE).next_to(line, UP, buff=0.25)
        t = say("s2c")
        with self.voiceover(t) as tr:
            self.play(FadeOut(value), FadeOut(label), run_time=0.5)
            self.remove(bars)
            self.add(base)
            self.play(LaggedStart(*[GrowFromEdge(r, DOWN) for r in tops], lag_ratio=0.002, run_time=1.4),
                      FadeIn(gaps), run_time=1.4)
            self.add(line)
            self.until(tr, t, 1)
            self.play(*[r.animate.stretch_to_fit_height(1e-3, about_edge=DOWN) for r in tops],
                      *[g.animate.set_fill(HILITE, opacity=1).set_stroke(width=0) for g in gaps],
                      run_time=2.2)
            self.play(FadeIn(fills, shift=UP * 0.2), run_time=0.7)
            self.wait(1.0)
        self.clear_all()


class S04Totals(LectureScene):
    def construct(self):
        bars, line = level_bars(), mean_line(BBASE + HM)
        self.add(bars, line)
        k = 2.2   # zoom: same rectangle, taller, so the strips below are visible
        rect = Rectangle(width=BX1 - BX0, height=HM, stroke_width=0, fill_color=RLBLUE, fill_opacity=1)
        rect.move_to([0, BBASE + HM / 2, 0])
        big = rect.copy().stretch(k, 1).move_to([0, -2.6 + HM * k / 2, 0])
        head = txt(say("remembers"), size=36, weight=BOLD).to_edge(UP, buff=SAFE + 0.35)

        t = say("s3a")
        with self.voiceover(t):
            self.play(FadeIn(head), run_time=0.7)
            self.remove(bars)
            self.add(rect)
            self.play(FadeOut(line), Transform(rect, big), run_time=1.4)

        b_n = Brace(rect, DOWN, buff=0.12, color=GREY_B)
        l_n = txt(say("people", n=N_EMP), size=26, color=GREY_B).next_to(b_n, DOWN, buff=0.12)
        b_m = Brace(rect, LEFT, buff=0.12, color=GREY_B)
        l_m = txt(say("each", v=money(PAYROLL_MEAN, cents=True)), size=24, color=GREY_B)
        l_m.rotate(PI / 2).next_to(b_m, LEFT, buff=0.12)
        eq = MathTex(rf"\${PAYROLL_MEAN:,.2f}".replace(",", "{,}"), r"\times", str(N_EMP), "=",
                     rf"\${PAYROLL_TOTAL:,.0f}".replace(",", "{,}"), font_size=46)
        eq.next_to(head, DOWN, buff=0.45)
        eq[4].set_color(HILITE)
        total = txt(money(PAYROLL_TOTAL), size=52, weight=BOLD, color=BLACK).move_to(rect)
        t = say("s3b")
        with self.voiceover(t) as tr:
            self.play(GrowFromCenter(b_n), FadeIn(l_n), GrowFromCenter(b_m), FadeIn(l_m), run_time=1.0)
            self.play(FadeIn(eq[:3]), run_time=0.6)
            self.until(tr, t, 1)
            self.play(rect.animate.set_fill(HILITE), FadeIn(eq[3:]), FadeIn(total, scale=0.8), run_time=1.2)

        # the median does not give the payroll back
        hmed = PAYROLL_MEDIAN * BSCALE * k
        y_med = rect.get_bottom()[1] + hmed
        strip = Rectangle(width=rect.width, height=rect.get_top()[1] - y_med, stroke_width=0,
                          fill_color=RLRED, fill_opacity=0.9)
        strip.move_to([0, (rect.get_top()[1] + y_med) / 2, 0])
        med = DashedLine([BX0, y_med, 0], [BX1, y_med, 0], color=RLGREEN, stroke_width=4)
        med_txt = MathTex(r"\text{" + say("median") + r"}\times" + str(N_EMP) + "=" +
                          rf"\${MEDIAN_TOTAL:,.0f}".replace(",", "{,}"), font_size=40, color=RLGREEN)
        med_txt.move_to(eq)
        miss = txt(say("missing", v=money(MEDIAN_SHORT)), size=26, color=RLRED)
        miss.next_to(strip, UP, buff=0.12).set_x(3.4)
        no = txt(say("no_other"), size=30, color=GREY_B).move_to(eq)
        t = say("s3c")
        with self.voiceover(t) as tr:
            self.play(FadeOut(eq), FadeIn(med_txt), Create(med), FadeIn(strip), FadeIn(miss), run_time=1.2)
            self.until(tr, t, 1)
            self.play(FadeOut(med_txt), FadeOut(med), FadeOut(strip), FadeOut(miss), FadeIn(eq), run_time=0.9)
            self.play(Indicate(eq[4], color=HILITE, scale_factor=1.12), run_time=1.2)
        self.clear_all()

        # the same average, used by every model we train later in the course
        mean_f = MathTex(r"\bar{x}", "=", r"\frac{1}{n}\sum_{i=1}^{n}", "x_i", font_size=64)
        loss_f = MathTex("L", "=", r"\frac{1}{n}\sum_{i=1}^{n}", r"\text{" + w("error", "xato") + r"}_i",
                         font_size=64)
        mean_f.move_to(UP * 0.9)
        loss_f.move_to(UP * 0.9)
        loss_f[0].set_color(RLRED)
        loss_f[3].set_color(RLRED)
        cap = txt(say("loss_cap"), size=30, color=GREY_B).next_to(loss_f, DOWN, buff=0.7)
        arrow = Arrow(UP * 0.5, DOWN * 0.5, color=RLRED, stroke_width=6).next_to(cap, DOWN, buff=0.3)
        t = say("s3d")
        with self.voiceover(t) as tr:
            self.play(FadeIn(mean_f), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(TransformMatchingTex(mean_f, loss_f), run_time=1.2)
            self.cue(tr, t, {"en": "training", "uz": "oʻqitish"})
            self.play(FadeIn(cap), GrowArrow(arrow), run_time=0.9)
            self.play(loss_f[0].animate.scale(0.7), run_time=0.8)
        self.clear_all()


# ─── log axis shared by scene 4 ───────────────────────────────────────────
LO, HI, LEFT_X, RIGHT_X = np.log10(2e4), np.log10(3e11), -5.6, 5.6


def xpos(s):
    return LEFT_X + (RIGHT_X - LEFT_X) * (np.log10(s) - LO) / (HI - LO)


class S04Failure(LectureScene):
    def construct(self):
        dots, haxis = hist_dots(), hist_axis()
        self.add(dots, haxis)
        picked = [dots[i] for i in range(0, N_EMP, N_EMP // N_DRINKERS)][:N_DRINKERS]
        others = [d for i, d in enumerate(dots) if d not in picked]

        axis = Line(LEFT_X * RIGHT, RIGHT_X * RIGHT, stroke_width=2, color=GREY_B).shift(DOWN * 1.6)
        ticks = VGroup()
        for val, lab in ((1e5, "$100k"), (1e6, "$1M"), (1e7, "$10M"),
                         (1e8, "$100M"), (1e9, "$1B"), (1e10, "$10B"), (1e11, "$100B")):
            tk = Line(UP * 0.1, DOWN * 0.1, stroke_width=2, color=GREY_B).move_to([xpos(val), axis.get_y(), 0])
            ticks.add(tk, txt(lab, size=20, color=GREY_B).next_to(tk, DOWN, buff=0.18))
        log_note = info(say("log"), size=20)
        rng = np.random.default_rng(1)
        strip = [[xpos(s), axis.get_y() + 0.55 + rng.uniform(-0.3, 0.3), 0] for s in DRINKERS]

        t = say("s4a")
        with self.voiceover(t) as tr:
            self.until(tr, t, 1)
            self.play(*[d.animate.set_color(HILITE).scale(1.6) for d in picked],
                      *[d.animate.set_opacity(0.25) for d in others], run_time=0.9)
            self.play(*[FadeOut(d) for d in others], FadeOut(haxis),
                      *[d.animate.move_to(p).set_color(RLBLUE).scale(0.055 / (0.034 * 1.6))
                        for d, p in zip(picked, strip)],
                      Create(axis), FadeIn(ticks), FadeIn(log_note), run_time=1.8)

        mline = Line(DOWN * 0.25, UP * 2.2, color=RLRED, stroke_width=5)
        mline.move_to([xpos(DRINK_MEAN), axis.get_y() + 1.0, 0])
        dline = DashedLine(DOWN * 0.25, UP * 2.2, color=RLGREEN, stroke_width=5)
        dline.move_to([xpos(DRINK_MED), axis.get_y() + 1.0, 0])
        names = VGroup(txt(say("mean"), size=26, color=GREY_B), txt(say("median"), size=26, color=GREY_B))
        names.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        swatches = VGroup(Line(ORIGIN, RIGHT * 0.45, color=RLRED, stroke_width=5),
                          DashedLine(ORIGIN, RIGHT * 0.45, color=RLGREEN, stroke_width=5))
        for s, n in zip(swatches, names):
            s.next_to(n, LEFT, buff=0.25)
        col_x = names.get_right()[0] + 0.3     # one value column, whatever the label widths
        def val(v, row):
            return txt(money(v), size=28).next_to(names[row], RIGHT, buff=0).set_x(col_x, LEFT)
        m_val, d_val = val(DRINK_MEAN, 0), val(DRINK_MED, 1)
        legend = VGroup(swatches, names, m_val, d_val)
        shift = np.array([-7.1 + SAFE + 0.25, 4.0 - SAFE - 0.25, 0]) - legend.get_corner(UL)
        legend.shift(shift)

        with self.voiceover(say("s4b")):
            self.play(Create(mline), Create(dline), run_time=1.0)
            self.play(FadeIn(legend), run_time=0.8)
            self.wait(1.2)

        bill = Dot(radius=0.11, color=HILITE).move_to([xpos(BILLIONAIRE), axis.get_y() + 0.55, 0])
        bill_lab = txt(say("billionaire"), size=24, color=HILITE).next_to(bill, UP, buff=0.25)
        with self.voiceover(say("s4c")):
            self.play(FadeIn(bill, shift=LEFT * 0.8, scale=0.3), FadeIn(bill_lab), run_time=1.0)
            self.wait(1.2)

        new_m = txt(money(AFTER_MEAN), size=28).move_to(m_val, aligned_edge=LEFT)
        new_d = txt(money(AFTER_MED), size=28).move_to(d_val, aligned_edge=LEFT)
        with self.voiceover(say("s4d")):
            self.play(mline.animate.set_x(xpos(AFTER_MEAN)), FadeTransform(m_val, new_m),
                      dline.animate.set_x(xpos(AFTER_MED)), FadeTransform(d_val, new_d), run_time=2.4)
            self.wait(0.8)

        arrow = Arrow(mline.get_top() + UP * 1.0 + LEFT * 1.6, mline.get_top() + UP * 0.1,
                      buff=0.05, color=RLRED, stroke_width=4)
        nobody = txt(say("nobody"), size=28, color=RLRED).next_to(arrow.get_start(), LEFT, buff=0.15)
        gap = Line([xpos(DRINKERS.max()) + 0.15, axis.get_y() + 0.55, 0],
                   [xpos(BILLIONAIRE) - 0.2, axis.get_y() + 0.55, 0], color=RLRED, stroke_width=2)
        gap.set_opacity(0.6)
        with self.voiceover(say("s4e")):
            self.play(Indicate(mline, color=RLRED), run_time=1.0)
            self.play(Create(gap), run_time=0.8)
            self.play(GrowArrow(arrow), FadeIn(nobody), run_time=1.2)
            self.wait(1.2)
        self.clear_all()


class S04Median(LectureScene):
    def construct(self):
        head = txt(say("not_moved"), size=36, weight=BOLD, color=RLGREEN).to_edge(UP, buff=SAFE + 0.35)
        n1 = N_DRINKERS + 1
        x0, x1, base = -5.5, 5.5, -2.5
        slot = (x1 - x0) / n1
        k = 2.9 / DRINKERS.max()
        def sx(i):
            return x0 + (i + 0.5) * slot
        bars = VGroup(*[Rectangle(width=slot * 0.72, height=s * k, stroke_width=0, fill_color=RLBLUE,
                                  fill_opacity=1).move_to([sx(i), base + s * k / 2, 0])
                        for i, s in enumerate(DRINKERS)])
        h = N_DRINKERS // 2   # 25 people on each side of the middle

        def level(v):
            y = base + v * k
            ln = DashedLine([x0 - 0.15, y, 0], [x1 + 0.15, y, 0], color=RLGREEN, stroke_width=4)
            lab = txt(money(v), size=34, weight=BOLD).move_to([-4.0, y + 0.42, 0])
            return ln, lab

        def braces(left, right):
            bl = Brace(VGroup(*left), DOWN, buff=0.12, color=GREY_B)
            br = Brace(VGroup(*right), DOWN, buff=0.12, color=GREY_B)
            return VGroup(bl, br, txt(say("people", n=len(left)), size=22, color=GREY_B).next_to(bl, DOWN, buff=0.1),
                          txt(say("people", n=len(right)), size=22, color=GREY_B).next_to(br, DOWN, buff=0.1))

        ln, lab = level(DRINK_MED)
        tag = txt(say("before"), size=24, color=GREY_B).next_to(lab, LEFT, buff=0.25)
        br = braces(bars[:h], bars[h:])
        t = say("s5a")
        with self.voiceover(t):
            self.play(FadeIn(head), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.02),
                      run_time=1.6)
            self.play(bars[h - 1].animate.set_fill(RLGREEN), bars[h].animate.set_fill(RLGREEN),
                      FadeIn(br), run_time=0.7)
            self.play(Create(ln), FadeIn(lab), FadeIn(tag), run_time=0.8)

        # the billionaire joins the end of the row: the middle moves by half a person
        top = 2.35
        bb = Rectangle(width=slot * 0.72, height=top - base, stroke_width=0, fill_color=HILITE, fill_opacity=1)
        bb.move_to([sx(N_DRINKERS), (top + base) / 2, 0])
        cut = VGroup(*[Line(LEFT * 0.16 + DOWN * 0.05, RIGHT * 0.16 + UP * 0.05, color=BLACK, stroke_width=5)
                       .move_to(bb.get_top() + DOWN * (0.45 + 0.14 * j)) for j in range(2)])
        b_lab = txt(money(BILLIONAIRE), size=24, color=HILITE).next_to(bb, LEFT, buff=0.2).set_y(1.5)
        all_bars = VGroup(*bars, bb)
        ln2, lab2 = level(AFTER_MED)
        tag2 = txt(say("after"), size=24, color=GREY_B).next_to(lab2, LEFT, buff=0.25)
        br2 = braces(all_bars[:h], all_bars[h + 1:])
        moved = txt(f"+{money(AFTER_MED - DRINK_MED)}", size=28, color=RLGREEN).next_to(lab2, RIGHT, buff=0.35)
        mean_note = txt(f"{say('mean')}:  {money(DRINK_MEAN)}  →  {money(AFTER_MEAN)}", size=24, color=RLRED)
        mean_note.next_to(head, DOWN, buff=0.3)
        with self.voiceover(say("s5b")):
            self.play(GrowFromEdge(bb, DOWN), run_time=1.0)
            self.play(FadeIn(cut), FadeIn(b_lab), FadeIn(mean_note), run_time=0.6)
            self.play(bars[h - 1].animate.set_fill(RLBLUE), Transform(br, br2),
                      Transform(ln, ln2), FadeTransform(lab, lab2), FadeTransform(tag, tag2), run_time=1.2)
            self.play(FadeIn(moved, shift=UP * 0.2), run_time=0.6)

        name = txt(say("is_median"), size=34, weight=BOLD, color=HILITE).move_to(mean_note)
        with self.voiceover(say("s5c")):
            self.play(FadeOut(mean_note), FadeIn(name), Indicate(ln, color=RLGREEN), run_time=1.2)
            self.wait(1.0)
        self.clear_all()


class S04HandsOn(LectureScene):
    def construct(self):
        base, k, step = -2.4, 2.7 / max(NINE), 1.05
        xs = [(i - (len(NINE) - 1) / 2) * step for i in range(len(NINE))]
        bars = VGroup(*[Rectangle(width=0.72, height=v * k, stroke_width=0, fill_color=RLBLUE, fill_opacity=1)
                        .move_to([x, base + v * k / 2, 0]) for x, v in zip(xs, NINE)])
        nums = VGroup(*[txt(str(v), size=30, weight=BOLD).next_to(b, UP, buff=0.12) for v, b in zip(NINE, bars)])
        floor = Line([xs[0] - 0.6, base, 0], [xs[-1] + 0.6, base, 0], color=GREY_B, stroke_width=2)
        unit = txt(say("unit"), size=22, color=GREY_B).next_to(floor, DOWN, buff=0.2)
        card = pause_card([say("task1"), say("task2")]).to_edge(UP, buff=SAFE + 0.3)

        with self.voiceover(say("s6a")):
            self.play(FadeIn(card), Create(floor), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.12), run_time=1.4)
            self.play(LaggedStart(*[FadeIn(n) for n in nums], lag_ratio=0.1), FadeIn(unit), run_time=1.0)
        self.hands_on()

        ym = base + NINE_MEAN * k
        line = Line([xs[0] - 0.6, ym, 0], [xs[-1] + 0.6, ym, 0], color=RLRED, stroke_width=4)
        sums = VGroup(
            txt(f"{say('total')}  =  {' + '.join(map(str, NINE))}  =  {NINE_SUM}", size=30),
            txt(f"{say('mean')}  =  {NINE_SUM} ÷ {len(NINE)}  =  {NINE_MEAN:.3f}", size=34, color=RLRED),
        ).arrange(DOWN, buff=0.3).to_edge(UP, buff=SAFE + 0.4)
        flat = VGroup(*[Rectangle(width=0.72, height=NINE_MEAN * k, stroke_width=0, fill_color=RLBLUE,
                                  fill_opacity=1).move_to([x, base + NINE_MEAN * k / 2, 0]) for x in xs])
        t = say("s6b")
        with self.voiceover(t):
            self.play(FadeOut(card), run_time=0.5)
            self.play(FadeIn(sums[0]), run_time=0.6)
            saved = bars.copy()
            self.play(Transform(bars, flat), FadeOut(nums), run_time=1.2)
            self.play(Create(line), FadeIn(sums[1]), run_time=0.8)

        lows = [i for i, v in enumerate(NINE) if v < NINE_MEAN]
        assert len(lows) == NINE_BELOW
        counts = VGroup(*[txt(str(j + 1), size=28, weight=BOLD, color=HILITE).next_to(saved[i], UP, buff=0.12)
                          for j, i in enumerate(lows)])
        sting = txt(say("below", k=NINE_BELOW, n=len(NINE)), size=34, weight=BOLD, color=HILITE)
        sting.move_to([0, 0.95, 0])
        with self.voiceover(say("s6c")):
            self.play(Transform(bars, saved), run_time=1.0)
            self.play(*[bars[i].animate.set_fill(HILITE) for i in lows], run_time=0.6)
            self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in counts], lag_ratio=0.25), run_time=1.4)
            self.play(FadeIn(sting), run_time=0.7)
            self.wait(1.0)
        self.clear_all()


class S04ToMedian(LectureScene):
    def construct(self):
        ln = DashedLine(LEFT * 3, RIGHT * 3, color=RLGREEN, stroke_width=6)
        name = txt(say("median"), size=56, weight=BOLD, color=RLGREEN).next_to(ln, UP, buff=0.4)
        with self.voiceover(say("s7")):
            self.play(Create(ln), FadeIn(name, shift=UP * 0.3), run_time=1.0)
            self.wait(0.6)
        self.clear_all()


SCENES = ["S04Problem", "S04Mean", "S04Totals", "S04Failure", "S04Median", "S04HandsOn", "S04ToMedian"]
