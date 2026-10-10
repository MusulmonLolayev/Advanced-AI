"""Lecture 1, section 5 — the median and the mode.

The five salaries, the nine salaries and the bus times are the slides' worked examples,
recomputed and asserted by statistics/capture_l01.py; the histogram is the 600 real
salaries of section 4. The narration is the approved section 5 of narration/lecture01.md.
"""
from lecture01_kit import *
from lecture01_s04 import (AFTER_MEAN, BILLIONAIRE, DRINKERS, hist_axis, hist_dots, hx, xpos,
                           HBASE, LEFT_X, RIGHT_X)

FIVE, FOUR = L["five"], L["four"]
FIVE_MEAN, FIVE_MED, FOUR_MED = L["five_mean"], L["five_median"], L["four_median"]
TYPO, TYPO_MEAN, TYPO_MED = L["five_typo"], L["five_typo_mean"], L["five_typo_median"]
NINE, NINE_MEAN = V1["nine"], V1["nine_mean"]
BUS, CAR = L["bus"], L["car"]

# the narration speaks these
assert FIVE == [31, 45, 47, 52, 88] and FIVE_MED == 47 and FOUR_MED == 46 and FIVE_MEAN == 52.6
assert sum(v < FIVE_MEAN for v in FIVE) == 4
assert (TYPO_MEAN, TYPO_MED) == (146.2, 47)
assert sorted(NINE)[4] == 47 and round(NINE_MEAN, 3) == 50.333
assert BUS.count(30) == 3 and max(set(BUS), key=BUS.count) == 30
assert L["bus_mean"] == L["car_mean"] == 30
assert (round(L["sal_median"]), round(L["sal_mean"])) == (47697, 51613)

BASE, HMAX = -2.6, 4.0          # floor and tallest-bar height for the five-salary rows
K5 = HMAX / max(FIVE)
STEP = 1.55


def five_bar(v, x, color=RLBLUE):
    return Rectangle(width=1.05, height=v * K5, stroke_width=0, fill_color=color,
                     fill_opacity=1).move_to([x, BASE + v * K5 / 2, 0])


def slots(n):
    return [(i - (n - 1) / 2) * STEP for i in range(n)]


def hline(v, color, dashed=False, x0=-4.1, x1=3.85):
    y = BASE + v * K5
    cls = DashedLine if dashed else Line
    return cls([x0, y, 0], [x1, y, 0], color=color, stroke_width=5)


def floor_line():
    return Line([-4.1, BASE, 0], [4.1, BASE, 0], color=GREY_B, stroke_width=2)


class S05Callback(LectureScene):
    """Callback: one billionaire pulled the mean into empty space."""
    def construct(self):
        self.section_card(5)
        y = -1.2
        axis = Line([LEFT_X, y, 0], [RIGHT_X, y, 0], stroke_width=2, color=GREY_B)
        ticks = VGroup()
        for val, lab in ((1e5, "$100k"), (1e7, "$10M"), (1e9, "$1B"), (1e11, "$100B")):
            tk = Line(UP * 0.1, DOWN * 0.1, stroke_width=2, color=GREY_B).move_to([xpos(val), y, 0])
            ticks.add(tk, txt(lab, size=20, color=GREY_B).next_to(tk, DOWN, buff=0.18))
        rng = np.random.default_rng(1)
        dots = VGroup(*[Dot([xpos(s), y + 0.55 + rng.uniform(-0.3, 0.3), 0], radius=0.055, color=RLBLUE)
                        for s in DRINKERS])
        bill = Dot([xpos(BILLIONAIRE), y + 0.55, 0], radius=0.11, color=HILITE)
        bill_lab = txt(w("billionaire", "milliarder"), size=22, color=HILITE).next_to(bill, UP, buff=0.2)
        mline = Line([xpos(AFTER_MEAN), y - 0.25, 0], [xpos(AFTER_MEAN), y + 2.2, 0], color=RLRED, stroke_width=5)
        mlab = txt(f"{w('mean', 'oʻrtacha')}: {money(AFTER_MEAN)}", size=24, color=RLRED).next_to(mline, UP, buff=0.15)
        q = txt(w("A number that holds its ground?", "Joyidan qimirlamaydigan son?"), size=36, weight=BOLD,
                color=RLGREEN).to_edge(UP, buff=SAFE + 0.4)
        t = line("5.1")
        with self.voiceover(t) as tr:
            self.play(Create(axis), FadeIn(ticks), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.02),
                      run_time=1.2)
            self.play(FadeIn(bill, shift=LEFT * 0.6), FadeIn(bill_lab), run_time=0.7)
            self.play(Create(mline), FadeIn(mlab), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.8)
        self.clear_all()


class S05Middle(LectureScene):
    """Sort, take the middle; even n; mean against median on the five."""
    def construct(self):
        shuffled = [52, 31, 88, 45, 47]
        assert sorted(shuffled) == FIVE
        xs = slots(5)
        bars = [five_bar(v, x) for v, x in zip(shuffled, xs)]
        by_value = {v: b for v, b in zip(shuffled, bars)}
        floor = floor_line()
        head = self.heading(w("Median", "Mediana"), color=RLGREEN)

        t = line("5.2")
        with self.voiceover(t) as tr:
            self.play(Create(floor), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.15),
                      run_time=1.2)
            self.cue(tr, t, 1)
            self.play(*[by_value[v].animate.set_x(x) for v, x in zip(FIVE, xs)], run_time=1.6)
            self.cue(tr, t, 2)
            mid = by_value[FIVE[2]]
            self.play(mid.animate.set_fill(RLGREEN), FadeIn(head), run_time=0.8)

        bars = VGroup(*[by_value[v] for v in FIVE])
        nums = VGroup(*[txt(str(v), size=30, weight=BOLD).next_to(b, UP, buff=0.12) for v, b in zip(FIVE, bars)])
        subs = VGroup(*[MathTex(f"x_{{({i})}}", font_size=40, color=GREY_B).next_to(b, DOWN, buff=0.15)
                        for i, b in enumerate(bars, 1)])
        n_lab = MathTex("n = 5", font_size=40).to_corner(UR, buff=SAFE + 0.4)
        t = line("5.3")
        with self.voiceover(t) as tr:
            self.play(bars[2].animate.set_fill(RLBLUE), run_time=0.3)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(n) for n in nums], lag_ratio=0.2), FadeIn(subs), run_time=1.4)
            self.cue(tr, t, 2)
            self.play(FadeIn(n_lab), run_time=0.6)
            self.cue(tr, t, 3)
            self.play(*[m.animate.set_opacity(0.25) for i in (0, 1, 3, 4) for m in (bars[i], nums[i])],
                      bars[2].animate.set_fill(RLGREEN), run_time=0.9)
            self.play(Indicate(nums[2], color=RLGREEN, scale_factor=1.3), run_time=0.8)

        # even n: the 88 leaves, four remain, the middle is a pair
        four_x = slots(4)
        n4 = MathTex("n = 4", font_size=40).move_to(n_lab)
        t = line("5.4")
        with self.voiceover(t) as tr:
            self.play(*[m.animate.set_opacity(1) for i in (0, 1, 3, 4) for m in (bars[i], nums[i])],
                      bars[2].animate.set_fill(RLBLUE), run_time=0.6)
            self.cue(tr, t, 1)
            gone = VGroup(bars[4], nums[4], subs[4])
            self.play(gone.animate.shift(RIGHT * 3 + UP * 2).set_opacity(0), TransformMatchingTex(n_lab, n4),
                      run_time=1.0)
            self.remove(gone)
            self.cue(tr, t, 2)
            self.play(*[VGroup(bars[i], nums[i], subs[i]).animate.set_x(four_x[i]) for i in range(4)], run_time=0.9)
            self.play(bars[1].animate.set_fill(RLGREEN), bars[2].animate.set_fill(RLGREEN), run_time=0.6)

        mline = hline(FOUR_MED, RLGREEN, dashed=True)
        calc = MathTex(rf"\frac{{{FOUR[1]} + {FOUR[2]}}}{{2}} = {FOUR_MED:g}", font_size=46, color=RLGREEN)
        calc.to_edge(UP, buff=SAFE + 1.2)
        t = line("5.5")
        with self.voiceover(t) as tr:
            self.play(FadeOut(head), run_time=0.3)
            self.cue(tr, t, 1)
            self.play(FadeIn(calc), run_time=0.8)
            self.play(Create(mline), run_time=0.8)

        # back to five: the mean sits above four of them
        back = VGroup(bars[4], nums[4], subs[4]).set_opacity(1).shift(-(RIGHT * 3 + UP * 2))
        n5 = MathTex("n = 5", font_size=40).move_to(n4)
        mean_l = hline(FIVE_MEAN, RLRED)
        med_l = hline(FIVE_MED, RLGREEN, dashed=True)
        mean_t = txt(f"{w('mean', 'oʻrtacha')} = {FIVE_MEAN:g}", size=26, color=RLRED).next_to(mean_l, RIGHT, buff=0.2)
        mean_t.shift(UP * 0.2)
        med_t = txt(f"{w('median', 'mediana')} = {FIVE_MED}", size=26, color=RLGREEN)
        t = line("5.6")
        with self.voiceover(t) as tr:
            self.play(FadeOut(calc), FadeOut(mline), TransformMatchingTex(n4, n5),
                      *[VGroup(bars[i], nums[i], subs[i]).animate.set_x(xs[i]) for i in range(4)], run_time=0.9)
            self.play(FadeIn(back, shift=DOWN * 0.5), *[bars[i].animate.set_fill(RLBLUE) for i in (1, 2)],
                      run_time=0.7)
            self.cue(tr, t, 1)
            self.play(Create(mean_l), FadeIn(mean_t), run_time=0.9)
            self.cue(tr, t, 2)
            self.play(*[bars[i].animate.set_fill(HILITE) for i in range(4)], run_time=0.7)
            self.cue(tr, t, {"en": "A single", "uz": "Bitta sakson"})
            self.play(*[bars[i].animate.set_fill(RLBLUE) for i in range(4)],
                      Indicate(bars[4], color=RLRED, scale_factor=1.08), run_time=1.0)
            self.cue(tr, t, {"en": "while the median", "uz": "Mediana esa"})
            med_t.next_to(med_l, RIGHT, buff=0.2).shift(DOWN * 0.2)
            self.play(bars[2].animate.set_fill(RLGREEN), Create(med_l), FadeIn(med_t), run_time=0.9)

        typ = txt(w("median → a typical member", "mediana → odatiy odam"), size=30, color=RLGREEN)
        share = txt(w("mean → each person's equal share", "oʻrtacha → teng ulush"), size=30, color=RLRED)
        VGroup(typ, share).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(UP, buff=SAFE + 0.3).set_x(-1.2)
        t = line("5.7")
        with self.voiceover(t) as tr:
            self.play(FadeOut(n5), FadeIn(typ, shift=RIGHT * 0.3), Indicate(med_l, color=RLGREEN), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(FadeIn(share, shift=RIGHT * 0.3), Indicate(mean_l, color=RLRED), run_time=1.0)
        self.clear_all()


class S05Histogram(LectureScene):
    """The 600 salaries: skewed, so the median and the mean part ways."""
    def construct(self):
        dots, axis = hist_dots(), hist_axis()
        top = HBASE + 4.6
        med = DashedLine([hx(L["sal_median"]), HBASE, 0], [hx(L["sal_median"]), top, 0], color=RLGREEN, stroke_width=5)
        mean = Line([hx(L["sal_mean"]), HBASE, 0], [hx(L["sal_mean"]), top, 0], color=RLRED, stroke_width=5)
        med_t = txt(f"{w('median', 'mediana')}  {money(L['sal_median'])}", size=26, color=RLGREEN)
        med_t.next_to(med, LEFT, buff=0.15).set_y(top - 0.2)
        mean_t = txt(f"{w('mean', 'oʻrtacha')}  {money(L['sal_mean'])}", size=26, color=RLRED)
        mean_t.next_to(mean, RIGHT, buff=0.15).set_y(top - 0.2)
        reports = VGroup(
            txt(w("household income → median", "oilalar daromadi → mediana"), size=26),
            txt(w("house prices → median", "uy narxlari → mediana"), size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([3.4, 0.3, 0])
        t = line("5.8")
        with self.voiceover(t) as tr:
            self.play(FadeIn(axis), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.002), run_time=1.6)
            self.play(Create(med), FadeIn(med_t), Create(mean), FadeIn(mean_t), run_time=1.0)
            self.play(FadeIn(reports[0], shift=LEFT * 0.3), run_time=0.7)
            self.cue(tr, t, {"en": "and house prices", "uz": "Uy narxlari"})
            self.play(FadeIn(reports[1], shift=LEFT * 0.3), run_time=0.7)
            tail = [d for d in dots if d.get_center()[0] > hx(100_000)]
            self.cue(tr, t, {"en": "A handful", "uz": "Bir nechta"})
            self.play(*[d.animate.set_color(HILITE) for d in tail], Indicate(mean, color=RLRED), run_time=1.2)
        self.clear_all()


class S05Mode(LectureScene):
    """The mode: the most frequent value, the only centre for categories."""
    def construct(self):
        x0, x1, y = -4.5, 4.5, -1.6
        lo, hi = 28, 32
        def mx(v):
            return x0 + (x1 - x0) * (v - lo) / (hi - lo)
        axis = Line([x0 - 0.3, y, 0], [x1 + 0.3, y, 0], color=GREY_B, stroke_width=2)
        ticks = VGroup()
        for v in range(lo, hi + 1):
            tk = Line(UP * 0.08, DOWN * 0.08, color=GREY_B, stroke_width=2).move_to([mx(v), y, 0])
            ticks.add(tk, txt(str(v), size=24, color=GREY_B).next_to(tk, DOWN, buff=0.15))
        unit = txt(w("bus, minutes", "avtobus, daqiqa"), size=24, color=GREY_B).next_to(axis, DOWN, buff=0.75)
        seen, dots = {}, VGroup()
        for v in BUS:
            k = seen.get(v, 0)
            seen[v] = k + 1
            dots.add(Dot([mx(v), y + 0.35 + 0.55 * k, 0], radius=0.2, color=RLBLUE))
        head = self.heading(w("Mode", "Moda"), color=HILITE)
        mode_t = txt(f"{w('mode', 'moda')} = 30  (×3)", size=34, weight=BOLD, color=HILITE)
        mode_t.next_to(dots, UP, buff=0.35)
        cat = VGroup(txt(w("categorical data:", "kategorial berilganlar:"), size=26, color=GREY_B),
                     txt(w("blood type, shoe size → mode", "qon guruhi, oyoq kiyim oʻlchami → moda"), size=26))
        cat.arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(UP, buff=SAFE + 1.3)
        t = line("5.9")
        with self.voiceover(t) as tr:
            self.play(FadeIn(head), Create(axis), FadeIn(ticks), FadeIn(unit), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.4) for d in dots], lag_ratio=0.2), run_time=1.2)
            self.cue(tr, t, 1)
            three = [d for d, v in zip(dots, BUS) if v == 30]
            self.play(*[d.animate.set_color(HILITE) for d in three], FadeIn(mode_t), run_time=0.9)
            self.cue(tr, t, 2)
            self.play(FadeIn(cat, shift=DOWN * 0.2), run_time=0.8)
        self.clear_all(run_time=0.5)

        cards = VGroup(
            card(w("mean", "oʻrtacha qiymat"), w("symmetric, totals", "simmetrik, jami"), color=RLRED,
                 width=4.0, height=2.3, size=30),
            card(w("median", "mediana"), w("skewed, extremes", "qiyshiq, chetdagi qiymatlar"), color=RLGREEN,
                 width=4.0, height=2.3, size=30),
            card(w("mode", "moda"), w("categorical", "kategorial"), color=HILITE, width=4.0, height=2.3, size=30),
        ).arrange(RIGHT, buff=0.35).move_to(DOWN * 0.2)
        for c in cards:                    # long Uzbek values must stay inside their card
            if c[2].width > c[0].width - 0.3:
                c[2].scale_to_fit_width(c[0].width - 0.3)
        icons = VGroup(
            # symmetric hump, skewed hump, category bars: drawn, not typed
            FunctionGraph(lambda x: 0.55 * np.exp(-x * x * 3), x_range=[-0.9, 0.9], color=RLRED),
            FunctionGraph(lambda x: 0.75 * (x + 0.9) * np.exp(-3.2 * (x + 0.9)) * 3.2, x_range=[-0.9, 0.9],
                          color=RLGREEN),
            VGroup(*[Rectangle(width=0.32, height=h, fill_color=HILITE, fill_opacity=1, stroke_width=0)
                     .move_to([(i - 1) * 0.45, h / 2, 0]) for i, h in enumerate((0.3, 0.6, 0.4))]),
        )
        for ic, c in zip(icons, cards):
            ic.next_to(c, UP, buff=0.3)
        head = self.heading(w("Rule of thumb", "Qoidamiz"))
        t = line("5.10")
        with self.voiceover(t) as tr:
            self.play(FadeIn(head), run_time=0.5)
            for i in range(3):
                self.cue(tr, t, i + 1)
                self.play(FadeIn(cards[i], shift=UP * 0.3), Create(icons[i]), run_time=0.8)
        self.clear_all()


class S05Typo(LectureScene):
    """Data cleaning: one extra zero wrecks the mean and leaves the median."""
    def construct(self):
        k = 2.3 / max(FIVE)            # flatter scale, so the new mean still fits on screen
        def bar(v, x, color=RLBLUE):
            return Rectangle(width=1.05, height=v * k, stroke_width=0, fill_color=color,
                             fill_opacity=1).move_to([x, BASE + v * k / 2, 0])
        def lvl(v, color, dashed=False):
            return (DashedLine if dashed else Line)([-4.1, BASE + v * k, 0], [4.1, BASE + v * k, 0],
                                                    color=color, stroke_width=5)
        xs = slots(5)
        bars = VGroup(*[bar(v, x) for v, x in zip(FIVE, xs)])
        nums = VGroup(*[txt(str(v), size=28, weight=BOLD).next_to(b, UP, buff=0.12) for v, b in zip(FIVE, bars)])
        floor = floor_line()
        mean_l, med_l = lvl(FIVE_MEAN, RLRED), lvl(FIVE_MED, RLGREEN, dashed=True)
        i_bad = TYPO.index(520)
        assert FIVE[i_bad] == 52
        head = self.heading(w("One typo: 52 → 520", "Bitta xato: 52 → 520"), color=HILITE)
        top = 2.55
        assert BASE + TYPO_MEAN * k < top - 0.9
        bad = Rectangle(width=1.05, height=top - BASE, stroke_width=0, fill_color=HILITE, fill_opacity=1)
        bad.move_to([xs[i_bad], (top + BASE) / 2, 0])
        cut = VGroup(*[Line(LEFT * 0.62 + DOWN * 0.08, RIGHT * 0.62 + UP * 0.08, color=BLACK, stroke_width=6)
                       .move_to(bad.get_top() + DOWN * (0.45 + 0.16 * j)) for j in range(2)])
        bad_n = txt("520", size=30, weight=BOLD, color=BLACK).move_to(bad).set_y(BASE + 0.5)
        mean_new = lvl(TYPO_MEAN, RLRED)
        legend = VGroup(
            txt(f"{w('mean', 'oʻrtacha')}:  {FIVE_MEAN:g} → {TYPO_MEAN:g}", size=30, color=RLRED),
            txt(f"{w('median', 'mediana')}:  {FIVE_MED} → {TYPO_MED}", size=30, color=RLGREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        legend.move_to([0, 0.15, 0], aligned_edge=LEFT).set_x(-6.4, LEFT)
        t = line("5.11")
        with self.voiceover(t) as tr:
            self.play(Create(floor), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1),
                      FadeIn(nums), Create(mean_l), Create(med_l), run_time=1.4)
            self.cue(tr, t, 1)
            self.play(FadeIn(head), run_time=0.5)
            self.play(Transform(bars[i_bad], bad), FadeTransform(nums[i_bad], bad_n), run_time=1.2)
            self.add(cut)
            self.play(Transform(mean_l, mean_new), FadeIn(legend), run_time=1.2)
            self.play(Indicate(med_l, color=RLGREEN), run_time=0.8)
            self.cue(tr, t, 2)
            self.play(Indicate(legend[1], color=RLGREEN), run_time=0.9)
        self.clear_all()


class S05HandsOn(LectureScene):
    def construct(self):
        bars, nums, floor, k, xs = bars_row(NINE, base=-2.6, height=2.4)
        unit = txt(w("salaries, in thousands of dollars", "maoshlar, ming dollarda"), size=22, color=GREY_B)
        unit.next_to(floor, DOWN, buff=0.15)
        pc = pause_card([w("We find the median of these nine.", "Shu toʻqqiztasining medianasini topamiz.")])
        pc.to_edge(UP, buff=SAFE + 0.3)
        with self.say("5.12"):
            self.play(FadeIn(pc), Create(floor), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1), FadeIn(nums),
                      FadeIn(unit), run_time=1.4)
        self.hands_on()

        assert NINE == sorted(NINE)
        ym = -2.6 + NINE_MEAN * k
        mean_l = Line([xs[0] - 0.6, ym, 0], [xs[-1] + 0.6, ym, 0], color=RLRED, stroke_width=4)
        mean_t = txt(f"{w('mean', 'oʻrtacha')} = {NINE_MEAN:.3f}", size=28, color=RLRED)
        order = VGroup(*[txt(str(i), size=22, color=GREY_B).next_to(b, DOWN, buff=0.45) for i, b in enumerate(bars, 1)])
        ans = txt(f"{w('median', 'mediana')} = {sorted(NINE)[4]}", size=40, weight=BOLD, color=RLGREEN)
        ans.to_edge(UP, buff=SAFE + 0.5)
        mean_t.next_to(ans, DOWN, buff=0.25)
        t = line("5.13")
        with self.voiceover(t) as tr:
            self.play(FadeOut(pc), FadeOut(unit), LaggedStart(*[FadeIn(o) for o in order], lag_ratio=0.08),
                      run_time=1.0)
            self.play(*[bars[i].animate.set_opacity(0.3) for i in range(9) if i != 4],
                      bars[4].animate.set_fill(RLGREEN), FadeIn(ans), run_time=0.9)
            self.cue(tr, t, {"en": "The mean was", "uz": "Oʻrtacha qiymat esa"})
            self.play(Create(mean_l), FadeIn(mean_t), run_time=0.9)
        self.clear_all()


class S05Teaser(LectureScene):
    """Same centre, different behaviour: the commute times of section 6."""
    def construct(self):
        x0, x1 = -3.6, 5.4
        def mx(v):
            return x0 + (x1 - x0) * (v - 15) / 30
        rows = VGroup()
        for yy, vals, name in ((1.1, BUS, w("bus", "avtobus")), (-1.5, CAR, w("car", "mashina"))):
            ax = Line([x0, yy, 0], [x1, yy, 0], color=GREY_B, stroke_width=2)
            seen, ds = {}, VGroup()
            for v in vals:
                kk = seen.get(v, 0)
                seen[v] = kk + 1
                ds.add(Dot([mx(v), yy + 0.25 + 0.3 * kk, 0], radius=0.13, color=RLBLUE))
            ml = Line([mx(30), yy - 0.3, 0], [mx(30), yy + 1.2, 0], color=RLRED, stroke_width=4)
            lab = txt(name, size=28).move_to([-5.3, yy + 0.3, 0])
            for v in range(15, 46, 5):
                tk = Line(UP * 0.07, DOWN * 0.07, color=GREY_B, stroke_width=2).move_to([mx(v), yy, 0])
                ax = VGroup(ax, tk, txt(str(v), size=20, color=GREY_B).next_to(tk, DOWN, buff=0.12))
            mt = txt(f"{w('mean', 'oʻrtacha')} = 30", size=24, color=RLRED).next_to(ml, UP, buff=0.1)
            rows.add(VGroup(ax, ds, ml, lab, mt))
        t = line("5.14")
        with self.voiceover(t) as tr:
            self.cue(tr, t, 1)
            self.play(FadeIn(rows[0][0], rows[0][3], rows[1][0], rows[1][3]),
                      LaggedStart(*[FadeIn(d) for r in rows for d in r[1]], lag_ratio=0.08), run_time=1.4)
            self.play(*[Create(r[2]) for r in rows], *[FadeIn(r[4]) for r in rows], run_time=0.9)
            self.cue(tr, t, 2)
            self.play(Indicate(rows[1][1], color=HILITE), run_time=1.0)
        self.clear_all()


SCENES = ["S05Callback", "S05Middle", "S05Histogram", "S05Mode", "S05Typo", "S05HandsOn", "S05Teaser"]
