"""Lecture 1, section 8 — quartiles and box plots.

The nine salaries and their quartiles, IQR and fences come from capture_l01.py; the
three branches are the figure script's own simulated waiting times (regenerated there
with its seed and checked against its printed quartiles), so each box, whisker and
outlier dot is the real summary of 200 customers.
"""
from lecture01_kit import *

NINE = L["nine"]
Q1, Q2, Q3, IQR = L["q1"], L["q2"], L["q3"], L["iqr"]
F_LO, F_HI = L["fence_lo"], L["fence_hi"]
assert NINE == sorted(NINE) and len(NINE) == 9
assert (Q1, Q2, Q3, IQR, F_LO, F_HI) == (40, 47, 56.5, 16.5, 15.25, 81.25)
assert L["outliers"] == [88]
W_HI = max(v for v in NINE if v <= F_HI)          # upper whisker: largest value inside the fence
assert (min(NINE), W_HI) == (31, 61)
BR = L["branches"]
BRANCH = {"A": label("branch_a"), "B": label("branch_b"), "C": label("branch_c")}
assert [b["median"] for b in BR] == [11.8, 17.7, 29.5] and round(BR[2]["iqrx"], 1) == 19.9
assert [len(b["fliers"]) for b in BR] == [2, 3, 3]


def num(v):
    return f"{v:g}"


# ─── a horizontal axis for the nine salaries (thousands of dollars) ────────
P0, P1, PX0, PX1 = 10, 95, -5.6, 5.6


def px(v):
    return PX0 + (PX1 - PX0) * (v - P0) / (P1 - P0)


def nine_axis(y):
    axis = Line([PX0, y, 0], [PX1, y, 0], color=GREY_B, stroke_width=2)
    marks = VGroup()
    for v in range(20, 100, 10):
        t = Line(UP * 0.08, DOWN * 0.08, color=GREY_B, stroke_width=2).move_to([px(v), y, 0])
        marks.add(t, txt(str(v), size=20, color=GREY_B).next_to(t, DOWN, buff=0.12))
    unit = txt(label("thousand"), size=20, color=GREY_B).next_to(axis, DOWN, buff=0.55).set_x(PX1 - 0.6)
    return VGroup(axis, marks, unit)


def nine_box(y, h=1.2):
    """Box Q1..Q3, median line, whiskers to 31 and 61, the 88 as a separate dot."""
    box_ = Rectangle(width=px(Q3) - px(Q1), height=h, stroke_color=RLBLUE, stroke_width=4,
                     fill_color=RLBLUE, fill_opacity=0.35).move_to([(px(Q1) + px(Q3)) / 2, y, 0])
    med = Line([px(Q2), y - h / 2, 0], [px(Q2), y + h / 2, 0], color=RLGREEN, stroke_width=6)
    wl = VGroup(Line([px(min(NINE)), y, 0], [px(Q1), y, 0], color=WHITE, stroke_width=3),
                Line([px(min(NINE)), y - h / 4, 0], [px(min(NINE)), y + h / 4, 0], color=WHITE, stroke_width=3))
    wh = VGroup(Line([px(Q3), y, 0], [px(W_HI), y, 0], color=WHITE, stroke_width=3),
                Line([px(W_HI), y - h / 4, 0], [px(W_HI), y + h / 4, 0], color=WHITE, stroke_width=3))
    out = Dot([px(88), y, 0], radius=0.11, color=RLRED)
    return VGroup(box_, med, wl, wh, out)


class S08Quartiles(LectureScene):
    def construct(self):
        self.section_card(8)
        bars, nums, floor, k, xs = bars_row(NINE, base=-2.5, height=3.3, step=1.1)

        def y(v):
            return -2.5 + v * k
        unit = txt(label("salaries_in_thousands_of_dollars"), size=20, color=GREY_B)
        unit.next_to(floor, DOWN, buff=0.15)
        with self.say("8.1") as (tr, t):
            self.play(Create(floor), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1),
                      FadeIn(nums), FadeIn(unit), run_time=1.6)

        div = DashedLine([xs[4], -2.6, 0], [xs[4], 1.6, 0], color=RLGREEN, stroke_width=3)
        b_lo = Brace(bars[:4], DOWN, buff=0.5, color=GREY_B)
        b_hi = Brace(bars[5:], DOWN, buff=0.5, color=GREY_B)
        l_lo = txt(label("lower_half"), size=22, color=GREY_B).next_to(b_lo, DOWN, buff=0.08)
        l_hi = txt(label("upper_half"), size=22, color=GREY_B).next_to(b_hi, DOWN, buff=0.08)
        with self.say("8.2") as (tr, t):
            self.cue(tr, t, 1)
            self.play(bars[4].animate.set_fill(RLGREEN), Indicate(nums[4], color=RLGREEN), run_time=0.9)
            self.cue(tr, t, 2)
            self.play(FadeOut(unit), Create(div), GrowFromCenter(b_lo), GrowFromCenter(b_hi), FadeIn(l_lo),
                      FadeIn(l_hi), run_time=1.0)

        q1_ln = DashedLine([xs[0] - 0.55, y(Q1), 0], [xs[3] + 0.55, y(Q1), 0], color=HILITE, stroke_width=4)
        q1_lab = MathTex(r"Q_1 = " + num(Q1), font_size=38, color=HILITE).next_to(q1_ln, LEFT, buff=0.15)
        q1_sum = MathTex(r"\tfrac{38 + 42}{2} = " + num(Q1), font_size=36).move_to([xs[1] - 0.5, 1.7, 0])
        assert (NINE[1] + NINE[2]) / 2 == Q1
        with self.say("8.3") as (tr, t):
            self.play(*[bars[i].animate.set_fill(RLBLUE).set_opacity(0.35) for i in range(5, 9)],
                      Indicate(b_lo, color=WHITE), run_time=0.9)
            self.cue(tr, t, 2)
            self.play(bars[1].animate.set_fill(HILITE), bars[2].animate.set_fill(HILITE), FadeIn(q1_sum), run_time=0.8)
            self.play(Create(q1_ln), FadeIn(q1_lab), run_time=0.8)

        q3_ln = DashedLine([xs[5] - 0.55, y(Q3), 0], [xs[8] + 0.55, y(Q3), 0], color=HILITE, stroke_width=4)
        q3_lab = MathTex(r"Q_3 = " + num(Q3), font_size=38, color=HILITE).next_to(q3_ln, RIGHT, buff=0.15)
        q3_sum = MathTex(r"\tfrac{52 + 61}{2} = " + num(Q3), font_size=36).move_to([xs[6] + 0.5, 1.7, 0])
        assert (NINE[6] + NINE[7]) / 2 == Q3
        with self.say("8.4") as (tr, t):
            self.play(*[bars[i].animate.set_opacity(1) for i in range(5, 9)],
                      *[bars[i].animate.set_opacity(0.35) for i in range(0, 4)], FadeOut(q1_sum),
                      Indicate(b_hi, color=WHITE), run_time=0.9)
            self.cue(tr, t, 2)
            self.play(bars[6].animate.set_fill(HILITE), bars[7].animate.set_fill(HILITE), FadeIn(q3_sum), run_time=0.8)
            self.play(Create(q3_ln), FadeIn(q3_lab), run_time=0.8)

        names = [label("minimum"), "Q1", label("median", 1), "Q3", label("max")]
        vals = [min(NINE), Q1, Q2, Q3, max(NINE)]
        row = VGroup(*[VGroup(txt(n, size=22, color=GREY_B), txt(num(v), size=34, weight=BOLD))
                       .arrange(DOWN, buff=0.1) for n, v in zip(names, vals)]).arrange(RIGHT, buff=0.75)
        row.to_edge(UP, buff=SAFE + 0.2)
        with self.say("8.5") as (tr, t):
            self.play(FadeOut(q3_sum), FadeOut(div),
                      *[b.animate.set_fill(RLGREEN if i == 4 else RLBLUE, opacity=1) for i, b in enumerate(bars)],
                      run_time=0.8)
            self.cue(tr, t, 2)
            self.play(LaggedStart(*[FadeIn(r, shift=DOWN * 0.2) for r in row], lag_ratio=0.3), run_time=1.8)

        band = Rectangle(width=xs[8] - xs[0] + 1.1, height=y(Q3) - y(Q1), stroke_width=0, fill_color=HILITE,
                         fill_opacity=0.18).move_to([0, (y(Q1) + y(Q3)) / 2, 0])
        iqr_t = MathTex(r"\mathrm{IQR} = Q_3 - Q_1 = " + num(Q3) + " - " + num(Q1) + " = " + num(IQR),
                        font_size=38, color=HILITE).move_to([-1.2, 1.9, 0])
        with self.say("8.6") as (tr, t):
            self.play(FadeIn(band), run_time=0.8)
            self.play(FadeIn(iqr_t), run_time=0.8)
            self.cue(tr, t, 3)
            self.play(Indicate(band, color=HILITE, scale_factor=1.03), run_time=1.0)

        fence = DashedLine([xs[0] - 0.55, y(F_HI), 0], [xs[8] + 0.55, y(F_HI), 0], color=RLRED, stroke_width=4)
        fence_lab = txt(num(F_HI), size=28, weight=BOLD, color=RLRED).next_to(fence, RIGHT, buff=0.15)
        fence_t = MathTex(num(Q3) + r" + 1.5 \times " + num(IQR) + " = " + num(F_HI), font_size=38, color=RLRED)
        fence_t.move_to([-1.2, 1.25, 0])
        assert Q3 + 1.5 * IQR == F_HI
        with self.say("8.7") as (tr, t):
            self.cue(tr, t, 1)
            self.play(FadeIn(fence_t), run_time=0.8)
            self.play(Create(fence), FadeIn(fence_lab), run_time=0.9)

        tag = txt(label("outlier"), size=26, weight=BOLD, color=RLRED)
        tag.next_to(nums[8], LEFT, buff=0.25)
        with self.say("8.8") as (tr, t):
            self.play(bars[8].animate.set_fill(RLRED), Indicate(nums[8], color=RLRED), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(FadeIn(tag), run_time=0.7)

        # the bars fall onto a number line as nine dots, and the box is drawn over them
        ax = nine_axis(-1.6)
        dots = VGroup(*[Dot([px(v), -1.6 + 0.0, 0], radius=0.09, color=RLRED if v > F_HI else RLBLUE) for v in NINE])
        box = nine_box(0.0)
        labs = VGroup(MathTex("Q_1", font_size=32).next_to(box[0], UP, buff=0.12).set_x(px(Q1)),
                      txt(label("median", 1), size=22, color=RLGREEN).next_to(box[0], UP, buff=0.12).set_x(px(Q2)),
                      MathTex("Q_3", font_size=32).next_to(box[0], UP, buff=0.12).set_x(px(Q3)))
        name = txt(label("box_plot"), size=34, weight=BOLD, color=RLBLUE).move_to([0, 1.6, 0])
        with self.say("8.9") as (tr, t):
            self.play(FadeOut(VGroup(band, iqr_t, fence, fence_lab, fence_t, tag, q1_ln, q1_lab, q3_ln, q3_lab,
                                     b_lo, b_hi, l_lo, l_hi, nums, floor)), run_time=0.6)
            self.play(FadeIn(ax), *[ReplacementTransform(b, d) for b, d in zip(bars, dots)], run_time=1.4)
            self.cue(tr, t, 1)
            self.play(DrawBorderThenFill(box[0]), run_time=0.8)
            self.play(Create(box[1]), FadeIn(labs), run_time=0.6)
            self.play(Create(box[2]), Create(box[3]), FadeIn(box[4], scale=0.5), run_time=0.9)
            self.cue(tr, t, 2)
            self.play(FadeIn(name, shift=UP * 0.2), run_time=0.7)
        self.wait(1.0)
        self.clear_all()


# ─── three branches, vertical box plots on a minutes axis ─────────────────
MB, MK = -2.7, 5.2 / 80


def my(m):
    return MB + m * MK


class S08Branches(LectureScene):
    def construct(self):
        axis = Line([-6.0, MB, 0], [-6.0, my(80), 0], color=GREY_B, stroke_width=2)
        floor = Line([-6.0, MB, 0], [5.4, MB, 0], color=GREY_B, stroke_width=2)
        ticks = VGroup()
        for m in range(0, 81, 20):
            tk = Line(LEFT * 0.08, RIGHT * 0.08, color=GREY_B, stroke_width=2).move_to([-6.0, my(m), 0])
            ticks.add(tk, txt(str(m), size=20, color=GREY_B).next_to(tk, LEFT, buff=0.1))
        unit = txt(label("minutes", 1), size=20, color=GREY_B).next_to(axis, UP, buff=0.12)
        cols = [RLBLUE, RLGREEN, RLORANGE]
        plots, meds, fliers = VGroup(), VGroup(), VGroup()
        for i, (b, c) in enumerate(zip(BR, cols)):
            x = -3.6 + i * 3.2
            bx = Rectangle(width=1.4, height=my(b["q3x"]) - my(b["q1x"]), stroke_color=c, stroke_width=4,
                           fill_color=c, fill_opacity=0.35).move_to([x, (my(b["q1x"]) + my(b["q3x"])) / 2, 0])
            md = Line([x - 0.7, my(b["medx"]), 0], [x + 0.7, my(b["medx"]), 0], color=WHITE, stroke_width=5)
            wk = VGroup(Line([x, my(b["wlo"]), 0], [x, my(b["q1x"]), 0], stroke_width=3),
                        Line([x, my(b["q3x"]), 0], [x, my(b["whi"]), 0], stroke_width=3),
                        Line([x - 0.3, my(b["wlo"]), 0], [x + 0.3, my(b["wlo"]), 0], stroke_width=3),
                        Line([x - 0.3, my(b["whi"]), 0], [x + 0.3, my(b["whi"]), 0], stroke_width=3))
            fl = VGroup(*[Dot([x, my(v), 0], radius=0.08, color=RLRED) for v in b["fliers"]])
            name = txt(BRANCH[b['name']], size=24).next_to([x, MB, 0], DOWN, buff=0.2)
            plots.add(VGroup(wk, bx, md, fl, name))
            meds.add(txt(num(b["median"]), size=26, weight=BOLD, color=c).next_to(bx, LEFT, buff=0.15).set_y(my(b["medx"])))
            fliers.add(fl)
        head = self.heading(label("waiting_time_at_three_branches"))
        with self.say("8.10") as (tr, t):
            self.play(FadeIn(head), Create(axis), Create(floor), FadeIn(ticks), FadeIn(unit), run_time=0.9)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.3) for p in plots], lag_ratio=0.3), run_time=1.6)
            self.cue(tr, t, 2)
            for m in meds:
                self.play(FadeIn(m), run_time=0.5)

        c_box = plots[2][1]
        br = Brace(c_box, RIGHT, buff=0.15, color=RLORANGE)
        br_t = txt(f"IQR ≈ {BR[2]['iqrx']:.1f} {label('minutes')}", size=24,
                   color=RLORANGE).next_to(br, RIGHT, buff=0.1)
        with self.say("8.11") as (tr, t):
            self.play(Indicate(c_box, color=RLORANGE, scale_factor=1.05), run_time=0.9)
            self.cue(tr, t, 1)
            self.play(GrowFromCenter(br), FadeIn(br_t), run_time=0.8)

        head2 = self.heading(label("ai_catch_strange_values_before_training"), color=HILITE)
        if head2.width > 12.4:
            head2.scale_to_fit_width(12.4)
        with self.say("8.12") as (tr, t):
            self.play(FadeOut(head), FadeIn(head2), FadeOut(br), FadeOut(br_t), run_time=0.7)
            self.play(*[d.animate.scale(1.8) for f in fliers for d in f], run_time=0.6)
            self.play(*[Indicate(d, color=RLRED, scale_factor=1.6) for f in fliers for d in f], run_time=1.0)
            self.play(*[Indicate(d, color=RLRED, scale_factor=1.6) for f in fliers for d in f], run_time=1.0)
        self.clear_all()


class S08HandsOn(LectureScene):
    def construct(self):
        card_ = pause_card([label("lower_fence_q1_1_5_iqr"),
                            label("is_any_salary_below_it_q")])
        card_.scale(0.85).to_edge(UP, buff=SAFE + 0.15)
        ax = nine_axis(-2.2)
        box = nine_box(-1.0)
        with self.say("8.13"):
            self.play(FadeIn(ax), FadeIn(box), run_time=1.0)
            self.play(FadeIn(card_), run_time=0.8)
        self.hands_on()

        calc = MathTex(num(Q1) + r" - 1.5 \times " + num(IQR) + " = " + num(Q1) + " - " + num(1.5 * IQR)
                       + " = " + num(F_LO), font_size=44, color=RLRED).move_to([0, 1.6, 0])
        assert Q1 - 1.5 * IQR == F_LO
        fence = DashedLine([px(F_LO), -2.2, 0], [px(F_LO), 0.2, 0], color=RLRED, stroke_width=4)
        f_lab = txt(num(F_LO), size=26, weight=BOLD, color=RLRED).next_to(fence, UP, buff=0.1)
        gap = DoubleArrow([px(F_LO), -1.0, 0], [px(min(NINE)), -1.0, 0], buff=0, color=RLGREEN, stroke_width=4)
        none = txt(f"{min(NINE)} > {num(F_LO)}:  {label('no_outlier_at_the_bottom')}",
                   size=28, color=RLGREEN).move_to([0, 0.75, 0])
        with self.say("8.14") as (tr, t):
            self.play(FadeOut(card_), FadeIn(calc), run_time=0.8)
            self.play(Create(fence), FadeIn(f_lab), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(Indicate(box[2], color=RLGREEN), GrowFromCenter(gap), run_time=0.9)
            self.play(FadeIn(none), run_time=0.7)
        self.clear_all()

        tables = VGroup()
        for name, d in L["anscombe"].items():
            rows = VGroup(*[VGroup(txt(f"{x:g}", size=18), txt(f"{yv:.2f}", size=18)).arrange(RIGHT, buff=0.45)
                            for x, yv in zip(d["x"], d["y"])])
            for r in rows:
                r[0].set_x(-0.45, RIGHT)
                r[1].set_x(0.25, LEFT)
            rows.arrange(DOWN, buff=0.1)
            hdr = VGroup(txt("x", size=20, color=GREY_B), txt("y", size=20, color=GREY_B))
            hdr[0].move_to([rows[0][0].get_center()[0], 0, 0])
            hdr[1].move_to([rows[0][1].get_center()[0], 0, 0])
            hdr.next_to(rows, UP, buff=0.15)
            title = txt(name, size=28, weight=BOLD, color=RLBLUE).next_to(hdr, UP, buff=0.15)
            frame = SurroundingRectangle(VGroup(title, hdr, rows), buff=0.18, color=GREY_D, stroke_width=2)
            tables.add(VGroup(frame, title, hdr, rows))
        tables.arrange(RIGHT, buff=0.45).scale_to_fit_height(5.6).move_to(DOWN * 0.35)
        q = txt("?", size=56, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.2)
        with self.say("8.15") as (tr, t):
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(tb, shift=UP * 0.3) for tb in tables], lag_ratio=0.25), run_time=1.6)
            self.play(FadeIn(q), run_time=0.5)
        self.clear_all()


SCENES = ["S08Quartiles", "S08Branches", "S08HandsOn"]
