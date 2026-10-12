"""Lecture 1, section 7 — variance is risk.

The two machines are the figure script's own simulated bottles (ARR["fills_A"],
ARR["fills_B"], regenerated in capture_l01.py with its seed and checked against its
stdout): every bar of the bells and every cell of the 1000-bottle grid is one of them.
"""
from lecture01_kit import *

FA, FB = np.array(ARR["fills_A"]), np.array(ARR["fills_B"])
TARGET, TOL, SD, N_BOTTLES = L["bottle_target"], L["bottle_tol"], L["bottle_sd"], L["bottles"]
LO_ML, HI_ML = TARGET - TOL, TARGET + TOL
REJ_A, REJ_B = L["bottle_A_rejected"], L["bottle_B_rejected"]
SHIFT = {int(k): v for k, v in L["bottle_B_shift"].items()}
NINE = V1["nine"]
assert (REJ_A, REJ_B, L["bottle_ratio"]) == (11, 210, 19)
assert int(((FA < LO_ML) | (FA > HI_ML)).sum()) == REJ_A and int(((FB < LO_ML) | (FB > HI_ML)).sum()) == REJ_B
assert (L["bottle_A_limits_sd"], L["bottle_B_limits_sd"]) == (2.5, 1.25)
assert round(L["bottle_A_mean"]) == round(L["bottle_B_mean"]) == 500
assert SHIFT[0] == REJ_B and all(SHIFT[d] > SHIFT[0] for d in SHIFT if d)
assert (L["nine_var"], round(L["eight_var"], 1)) == (271.5, 82.3) and NINE[-1] == 88

# ─── the fill axis: 486..514 ml on the left of the frame ──────────────────
M0, M1, X0, X1 = 486.0, 514.0, -6.2, 2.2
BASE, HK = -2.5, 3.6 / 200          # bar height per bottle (machine A peaks just under 200)
EDGES = np.arange(486.0, 515.0, 1.0)


def mx(v):
    return X0 + (X1 - X0) * (v - M0) / (M1 - M0)


def fill_axis():
    axis = Line([X0, BASE, 0], [X1, BASE, 0], color=GREY_B, stroke_width=2)
    marks = VGroup()
    for v in (490, 495, 500, 505, 510):
        t = Line(UP * 0.08, DOWN * 0.08, color=GREY_B, stroke_width=2).move_to([mx(v), BASE, 0])
        marks.add(t, txt(str(v), size=20, color=GREY_B).next_to(t, DOWN, buff=0.12))
    unit = txt("ml", size=20, color=GREY_B).next_to(axis, RIGHT, buff=0.15).shift(DOWN * 0.2)
    band = Rectangle(width=mx(HI_ML) - mx(LO_ML), height=3.9, stroke_width=0, fill_color=RLGREEN,
                     fill_opacity=0.16).move_to([mx(500), BASE + 1.95, 0])
    lims = VGroup(*[DashedLine([mx(v), BASE, 0], [mx(v), BASE + 3.9, 0], color=RLRED, stroke_width=3)
                    for v in (LO_ML, HI_ML)])
    return VGroup(band, lims, axis, marks, unit)


def hist(fills, color, shift=0):
    counts, _ = np.histogram(fills, bins=EDGES)
    g = VGroup()
    for a, c in zip(EDGES[:-1], counts):
        if c == 0:
            continue
        out = a + shift < LO_ML or a + 1 + shift > HI_ML
        r = Rectangle(width=(X1 - X0) / (M1 - M0) * 0.94, height=c * HK, stroke_width=0,
                      fill_color=RLRED if out else color, fill_opacity=0.9)
        g.add(r.move_to([mx(a + 0.5), BASE + c * HK / 2, 0]))
    return g


def recolor(g, fills, color, shift):
    """Bars that land outside the limits after moving the mean by `shift` ml turn red."""
    counts, _ = np.histogram(fills, bins=EDGES)
    starts = [a for a, c in zip(EDGES[:-1], counts) if c]
    return [r.animate.set_fill(RLRED if (a + shift < LO_ML or a + 1 + shift > HI_ML) else color)
            for r, a in zip(g, starts)]


# ─── 1000 bottles, one cell each ──────────────────────────────────────────
GRID_C, CELL = (4.75, -0.35, 0), 0.088


def bottle_grid():
    g = VGroup(*[Square(CELL * 0.8, stroke_width=0, fill_color=GREY_D, fill_opacity=1) for _ in range(1000)])
    g.arrange_in_grid(rows=40, cols=25, buff=CELL * 0.2).move_to(GRID_C)
    return g


def bad_cells(grid, fills):
    return [grid[i] for i in np.flatnonzero((fills < LO_ML) | (fills > HI_ML))]


def bell(mean, sd, color, height):
    """The normal curve with the machine's own measured mean and spread."""
    xs = np.linspace(M0, M1, 200)
    ys = np.exp(-0.5 * ((xs - mean) / sd) ** 2)
    pts = [[mx(x), BASE + height * y, 0] for x, y in zip(xs, ys)]
    return VMobject(stroke_color=color, stroke_width=5).set_points_smoothly(pts)


# ─── the way from the mean to the upper limit, marked off in standard deviations ───
RULER_Y = BASE - 0.68


def sd_ruler(sd, color):
    """A white line from 500 ml to the upper limit, and on it one segment per standard deviation
    (the last one cut short where the limit falls), each full segment marked s."""
    base_ = VGroup(Line([mx(TARGET), RULER_Y, 0], [mx(HI_ML), RULER_Y, 0], color=WHITE, stroke_width=2),
                   *[Line([mx(v), RULER_Y - 0.12, 0], [mx(v), RULER_Y + 0.12, 0], color=WHITE, stroke_width=3)
                     for v in (TARGET, HI_ML)])
    dist = txt(f"{TOL:g} ml", size=22).next_to(base_[1], LEFT, buff=0.2)
    segs = VGroup()
    a, j = TARGET, 0
    while a < HI_ML - 1e-9:
        b = min(a + sd, HI_ML)
        shade = color if j % 2 == 0 else interpolate_color(ManimColor(color), BLACK, 0.45)
        seg = Line([mx(a), RULER_Y, 0], [mx(b), RULER_Y, 0], color=shade, stroke_width=10)
        mark = VGroup(seg)
        if b - a >= sd - 1e-9:
            mark.add(MathTex("s", font_size=30, color=color).next_to(seg, DOWN, buff=0.1))
        segs.add(mark)
        a, j = b, j + 1
    return VGroup(VGroup(base_, dist), segs)


def limits_sum(sd, k, color):
    assert TOL / sd == k
    return MathTex(rf"{TOL:g} \div {sd:g} = {k:g}", font_size=34, color=color).move_to([mx(HI_ML) + 1.45, RULER_Y, 0])


class S07Bottles(LectureScene):
    def construct(self):
        self.section_card(7)
        ax = fill_axis()
        target = tagged(f"{TARGET:g} ml", f"{label('bottle_label')}:", after=False, size=30, weight=BOLD)
        target.to_edge(UP, buff=SAFE + 0.3)
        target.set_x(mx(500))
        allowed = txt(f"{LO_ML:g}–{HI_ML:g} ml", size=24, color=RLGREEN).next_to(ax[0], UP, buff=0.12)
        with self.say("7.1") as (tr, t):
            self.play(Create(ax[2]), FadeIn(ax[3]), FadeIn(ax[4]), FadeIn(target), run_time=1.0)
            self.cue(tr, t, {"en": "and the law", "uz": "Qonun"})
            self.play(FadeIn(ax[0]), Create(ax[1]), FadeIn(allowed), run_time=1.0)

        mean_ln = DashedLine([mx(TARGET), BASE, 0], [mx(TARGET), BASE + 3.9, 0], color=WHITE, stroke_width=3)
        grid = bottle_grid()
        g_lab = tagged(N_BOTTLES, label("bottles"), size=22, color=GREY_B).next_to(grid, UP, buff=0.15)
        m_lab = tagged(f"{TARGET:g} ml", f"{label('a_and_b')}: {label('mean', 1)}", after=False, size=24).next_to(target, DOWN, buff=0.2)
        with self.say("7.2") as (tr, t):
            self.play(Create(mean_ln), FadeIn(m_lab), FadeOut(allowed), run_time=0.9)
            self.play(FadeIn(grid, lag_ratio=0.001), FadeIn(g_lab), run_time=1.2)

        ha = hist(FA, RLGREEN)
        name_a = tagged(f"s = {SD['A']:g} ml", f"{label('machine_a')}: ", after=False, size=26, color=RLGREEN)
        name_a.next_to(m_lab, DOWN, buff=0.2).set_x(mx(500))
        sd_a = tagged(f"± {L['bottle_A_limits_sd']:g} s", f"{label('limits')}:", after=False, size=22, color=GREY_B)
        sd_a.move_to([mx(509.5), BASE + 2.6, 0])
        ctr_a = tagged(f"{REJ_A} / {N_BOTTLES}", label("rejected"), after=False, size=24, color=RLRED)
        ctr_a.next_to(grid, DOWN, buff=0.15)
        with self.say("7.3") as (tr, t):
            self.play(FadeOut(m_lab), FadeIn(name_a), LaggedStart(*[GrowFromEdge(r, DOWN) for r in ha],
                                                                 lag_ratio=0.05), run_time=1.6)
            self.cue(tr, t, 1)
            self.play(FadeIn(sd_a), run_time=0.6)
            self.cue(tr, t, {"en": "eleven", "uz": "Shuning uchun"})
            self.play(*[c.animate.set_fill(RLRED) for c in bad_cells(grid, FA)], FadeIn(ctr_a), run_time=0.9)

        ruler_a, sum_a = sd_ruler(SD["A"], RLGREEN), limits_sum(SD["A"], L["bottle_A_limits_sd"], RLGREEN)
        with self.say("7.3a") as (tr, t):
            self.play(Indicate(sd_a, color=RLGREEN, scale_factor=1.06), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(Create(ruler_a[0][0]), FadeIn(ruler_a[0][1]), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(m) for m in ruler_a[1]], lag_ratio=0.35), run_time=1.0)
            self.cue(tr, t, 2)
            self.play(FadeIn(sum_a, shift=UP * 0.1), run_time=0.7)
            self.cue(tr, t, 3)
            self.play(Indicate(ctr_a, color=RLRED), run_time=0.9)

        hb = hist(FB, RLORANGE)
        name_b = tagged(f"s = {SD['B']:g} ml", f"{label('machine_b')}: ", after=False, size=26,
                        color=RLORANGE).move_to(name_a)
        sd_b = tagged(f"± {L['bottle_B_limits_sd']:g} s", f"{label('limits')}:", after=False, size=22,
                      color=GREY_B).move_to(sd_a)
        ctr_b = tagged(f"{REJ_B} / {N_BOTTLES}", label("rejected"), after=False, size=24, color=RLRED).move_to(ctr_a)
        with self.say("7.4") as (tr, t):
            self.play(ha.animate.set_opacity(0.18), FadeOut(name_a), FadeIn(name_b), *[c.animate.set_fill(GREY_D) for c
                      in bad_cells(grid, FA)], FadeOut(ctr_a), FadeOut(ruler_a), FadeOut(sum_a), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(r, DOWN) for r in hb], lag_ratio=0.04), run_time=1.6)
            self.cue(tr, t, 1)
            self.play(FadeOut(sd_a), FadeIn(sd_b), run_time=0.6)
            self.cue(tr, t, 2)
            self.play(*[c.animate.set_fill(RLRED) for c in bad_cells(grid, FB)], FadeIn(ctr_b), run_time=1.2)

        ruler_b, sum_b = sd_ruler(SD["B"], RLORANGE), limits_sum(SD["B"], L["bottle_B_limits_sd"], RLORANGE)
        with self.say("7.4a") as (tr, t):
            self.play(Create(ruler_b[0][0]), FadeIn(ruler_b[0][1]), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(m) for m in ruler_b[1]], lag_ratio=0.35), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeIn(sum_b, shift=UP * 0.1), run_time=0.7)
            self.cue(tr, t, 2)
            self.play(Indicate(ruler_b[1][-1], color=RLRED, scale_factor=1.3), Indicate(ctr_b, color=RLRED), run_time=1.0)

        ratio = VGroup(tagged(f"×{L['bottle_spread_ratio']:g}", label("spread"), after=False, size=34, weight=BOLD,
                              color=RLORANGE),
                       txt("→", size=34), tagged(f"×{L['bottle_ratio']}", label("waste"), after=False, size=34,
                                                 weight=BOLD, color=RLRED)).arrange(RIGHT, buff=0.3)
        ratio.move_to(target)
        still = txt(f"{label('mean', 1)}: {TARGET:g} ml, {label('unchanged')}", size=24).next_to(mean_ln, UP, buff=0.1)
        with self.say("7.5") as (tr, t):
            self.play(FadeOut(target), FadeOut(name_b), FadeOut(ruler_b), FadeOut(sum_b), FadeIn(ratio, shift=UP * 0.2),
                      run_time=0.9)
            self.cue(tr, t, 1)
            self.play(Indicate(mean_ln, color=WHITE), FadeIn(still), run_time=1.2)
        self.clear_all()


class S07Risk(LectureScene):
    def construct(self):
        ax = fill_axis()
        sa, sb = L["bottle_A_std"], L["bottle_B_std"]
        ba = bell(L["bottle_A_mean"], sa, RLGREEN, 3.4)
        bb = bell(L["bottle_B_mean"], sb, RLORANGE, 1.7)
        head = self.heading(label("six_sigma_control_the_spread"),
                            color=HILITE)
        ticks = VGroup()
        for k in (-2, -1, 1, 2):
            x = mx(L["bottle_A_mean"] + k * sa)
            ticks.add(Line([x, BASE - (0.55 if abs(k) == 1 else 0.95), 0], [x, BASE + 0.25, 0], color=RLGREEN, stroke_width=4),
                      MathTex(rf"{k:+d}\sigma", font_size=30, color=RLGREEN).move_to([x, BASE - (0.85 if abs(k) == 1 else 1.25), 0]))
        with self.say("7.6") as (tr, t):
            self.play(FadeIn(ax), Create(ba), Create(bb), run_time=1.4)
            self.cue(tr, t, 1)
            self.play(FadeIn(head), FadeIn(ticks), run_time=1.0)

        # everyday versions of the same two bells, drawn as small icons on the right
        def bus():
            body = RoundedRectangle(corner_radius=0.08, width=0.9, height=0.45, stroke_color=WHITE, stroke_width=3)
            wheels = VGroup(*[Circle(0.08, color=WHITE, stroke_width=3).move_to(body.get_bottom() + [dx, 0, 0])
                              for dx in (-0.25, 0.25)])
            return VGroup(body, wheels)

        def clinic():
            sq = RoundedRectangle(corner_radius=0.08, width=0.6, height=0.6, stroke_color=WHITE, stroke_width=3)
            return VGroup(sq, Rectangle(width=0.12, height=0.38, stroke_width=0, fill_color=RLRED, fill_opacity=1),
                          Rectangle(width=0.38, height=0.12, stroke_width=0, fill_color=RLRED, fill_opacity=1))

        def oven():
            box_ = RoundedRectangle(corner_radius=0.06, width=0.8, height=0.6, stroke_color=WHITE, stroke_width=3)
            door = Rectangle(width=0.5, height=0.3, stroke_color=WHITE, stroke_width=2).shift(DOWN * 0.08)
            return VGroup(box_, door, Dot(box_.get_top() + DOWN * 0.1, radius=0.04))

        items = VGroup()
        for icon, lab in ((bus(), label("bus_timetable")),
                          (clinic(), label("clinic_waiting_time")),
                          (oven(), label("oven_temperature"))):
            items.add(VGroup(icon, txt(lab, size=22)).arrange(RIGHT, buff=0.25))
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to([4.7, 0.2, 0])
        often = txt(label("the_mean_never_says_how_often"), size=24, color=GREY_B)
        often.next_to(head, DOWN, buff=0.25)
        with self.say("7.7") as (tr, t):
            self.play(FadeOut(ticks), run_time=0.5)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(i, shift=LEFT * 0.3) for i in items], lag_ratio=0.35), run_time=1.6)
            self.cue(tr, t, 2)
            self.play(FadeIn(often), run_time=0.8)

        head2 = self.heading(label("ai_a_prediction_and_its_uncertainty"),
                             color=HILITE)
        trust = txt(label("small_spread_we_can_trust_it"), size=24, color=RLGREEN)
        careful = txt(label("large_spread_we_are_careful"), size=24, color=RLORANGE)
        trust.move_to([4.3, 0.9, 0])
        careful.move_to([4.3, -1.2, 0])
        a_trust = Arrow(trust.get_left(), [mx(501.6), BASE + 2.6, 0], buff=0.1, color=RLGREEN, stroke_width=4)
        a_care = Arrow(careful.get_left(), [mx(504.5), BASE + 0.8, 0], buff=0.1, color=RLORANGE, stroke_width=4)
        with self.say("7.8") as (tr, t):
            self.play(FadeOut(items), FadeOut(often), FadeOut(head), FadeIn(head2), FadeOut(ax[0]), FadeOut(ax[1]),
                      run_time=0.9)
            self.play(FadeIn(trust), GrowArrow(a_trust), Indicate(ba, color=RLGREEN, scale_factor=1.04), run_time=1.0)
            self.play(FadeIn(careful), GrowArrow(a_care), Indicate(bb, color=RLORANGE, scale_factor=1.04), run_time=1.0)
        self.clear_all()


class S07HandsOn(LectureScene):
    def construct(self):
        ax = fill_axis()
        hb = hist(FB, RLORANGE)
        card_ = pause_card([label("we_cannot_shrink_machine_b_s"),
                            label("where_do_we_set_its_mean_q")])
        card_.scale(0.85).to_edge(UP, buff=SAFE + 0.15)
        with self.say("7.9"):
            self.play(FadeIn(ax), FadeIn(hb), run_time=1.0)
            self.play(FadeIn(card_), run_time=0.8)
        self.hands_on()

        mean_ln = DashedLine([mx(TARGET), BASE, 0], [mx(TARGET), BASE + 3.9, 0], color=WHITE, stroke_width=3)
        cnt_lab = txt(label("rejected"), size=30)
        num = txt(str(SHIFT[0]), size=40, weight=BOLD, color=RLRED)
        counter = VGroup(cnt_lab, num).arrange(RIGHT, buff=0.25).move_to([4.6, 1.0, 0])
        shift_lab = tagged(f"{TARGET:g} ml", label("mean", 1), after=False, size=26).next_to(counter, DOWN, buff=0.35)
        moving = VGroup(hb, mean_ln)

        def step(d, rt=0.55):
            new = txt(str(SHIFT[d]), size=40, weight=BOLD, color=RLRED).move_to(num, aligned_edge=LEFT)
            new_s = tagged(f"{TARGET + d:g} ml", label("mean", 1), after=False, size=26).move_to(shift_lab)
            self.play(moving.animate.set_x(mx(500 + d) - mx(500) + cx), *recolor(hb, FB, RLORANGE, d),
                      Transform(num, new), Transform(shift_lab, new_s), run_time=rt)

        with self.say("7.10") as (tr, t):
            self.play(FadeOut(card_), Create(mean_ln), FadeIn(counter), FadeIn(shift_lab), run_time=0.8)
            cx = moving.get_x()
            self.cue(tr, t, 1)
            for d in (-1, -2, -3, -2, -1, 0, 1, 2, 3, 2, 1, 0):
                step(d, 0.4)
            self.play(Indicate(num, color=RLRED), run_time=0.8)
        self.clear_all()


class S07Teaser(LectureScene):
    def construct(self):
        bars, nums, floor, k, xs = bars_row(NINE, base=-2.4, height=3.0)
        unit = txt(label("salaries_in_thousands_of_dollars"), size=22, color=GREY_B)
        unit.next_to(floor, DOWN, buff=0.2)
        with_ = MathTex(r"s^2 = " + f"{L['nine_var']:g}", font_size=44, color=RLRED)
        without = MathTex(r"s^2 = " + f"{L['eight_var']:.1f}", font_size=44, color=RLGREEN)
        lab_w = tagged(NINE[-1], f"{label('included')}:", size=28)
        lab_wo = tagged(NINE[-1], f"{label('left_out')}:", size=28)
        rows = VGroup(VGroup(lab_wo, without).arrange(RIGHT, buff=0.3),
                      VGroup(lab_w, with_).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        rows.to_edge(UP, buff=SAFE + 0.3)
        q = txt("?", size=60, weight=BOLD, color=HILITE).move_to([5.6, 1.6, 0])
        with self.say("7.11") as (tr, t):
            self.play(Create(floor), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars[:-1]], lag_ratio=0.1),
                      FadeIn(nums[:-1]), FadeIn(unit), FadeIn(rows[0]), run_time=1.4)
            self.play(GrowFromEdge(bars[-1], DOWN), FadeIn(nums[-1]), bars[-1].animate.set_fill(RLRED),
                      FadeIn(rows[1]), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(FadeIn(q, scale=0.6), run_time=0.6)
        self.clear_all()


SCENES = ["S07Bottles", "S07Risk", "S07HandsOn", "S07Teaser"]
