"""Lecture 1, section 14 — classical vs empirical probability, and the lecture's close.

The histogram is the 600 real salaries (L["hist_edges"], L["hist_counts"]); the empirical
probability is L["p_40_60k"]. The weather grid is an illustration and says so on screen.
"""
from lecture01_kit import *

EDGES, COUNTS = L["hist_edges"], L["hist_counts"]
N_EMP = sum(COUNTS)
SPAM = L["spam_train"]
assert SPAM["emails"] - SPAM["spam"] == 1
SPAM_SHARE = f"{round(100 * SPAM['spam'] / SPAM['emails'])}%"
P4060 = L["p_40_60k"]
# the narration speaks these
assert N_EMP == 600 and COUNTS[1] == 311 and EDGES[1:3] == [40_000, 60_000]
assert abs(P4060 - COUNTS[1] / N_EMP) < 1e-12 and round(P4060 * 100) == 52
LBLUE = "#8C88F0"   # RLBLUE is too dark for text on black


def cloud_icon(scale=1.0, color=GREY_B):
    c = VGroup(*[Circle(radius=r, stroke_width=0).set_fill(color, 0.95).move_to(p)
                 for r, p in ((0.5, (-0.55, 0, 0)), (0.7, (0.1, 0.22, 0)), (0.5, (0.78, 0, 0)))])
    base = Rectangle(width=1.9, height=0.5, stroke_width=0).set_fill(color, 0.95).move_to([0.1, -0.2, 0])
    return VGroup(c, base).scale(scale)


def drop_icon(size=0.22, color=RLBLUE):
    d = VGroup(Triangle(stroke_width=0).set_fill(color, 1).scale(size * 0.55).stretch(1.3, 1),
               Circle(radius=size * 0.5, stroke_width=0).set_fill(color, 1))
    d[0].next_to(d[1], UP, buff=-size * 0.35)
    return d


def sun_icon(size=0.22, color=RLORANGE):
    core = Circle(radius=size * 0.42, stroke_width=0).set_fill(color, 1)
    rays = VGroup(*[Line(ORIGIN, RIGHT * size * 0.22, color=color, stroke_width=2)
                    .shift(RIGHT * size * 0.55).rotate(a, about_point=ORIGIN) for a in np.arange(0, TAU, TAU / 8)])
    return VGroup(core, rays)


def text_frac(num, den, size=30, color=WHITE):
    n, d = txt(num, size=size, color=color), txt(den, size=size, color=color)
    bar = Line(LEFT, RIGHT, color=color, stroke_width=3).set_width(max(n.width, d.width) + 0.2)
    return VGroup(n, bar, d).arrange(DOWN, buff=0.15)


def histogram(x0=-5.6, x1=1.4, base=-2.6, height=4.2):
    """The 600 salaries, seven classes, touching bars (section 3's histogram)."""
    k = height / max(COUNTS)
    wbar = (x1 - x0) / len(COUNTS)
    bars = VGroup(*[Rectangle(width=wbar, height=c * k, stroke_color=BLACK, stroke_width=1.5,
                              fill_color=RLBLUE, fill_opacity=1).move_to([x0 + (i + 0.5) * wbar, base + c * k / 2, 0])
                    for i, c in enumerate(COUNTS)])
    axis = Line([x0 - 0.1, base, 0], [x1 + 0.1, base, 0], color=GREY_B, stroke_width=2)
    ticks = VGroup(*[txt(f"{e // 1000}k", size=18, color=GREY_B).move_to([x0 + i * wbar, base - 0.25, 0])
                     for i, e in enumerate(EDGES)])
    nums = VGroup(*[txt(str(c), size=20, color=GREY_B).next_to(b, UP, buff=0.08) for c, b in zip(COUNTS, bars)])
    return bars, VGroup(axis, ticks), nums


class S14Classical(LectureScene):
    def construct(self):
        self.section_card(14)
        cloud = cloud_icon(1.1).move_to([-2.2, 0.6, 0])
        drops = VGroup(*[drop_icon(0.28).move_to([-2.9 + 0.55 * i, -0.65 - 0.15 * (i % 2), 0]) for i in range(4)])
        fc = VGroup(txt(label("tomorrow_rain"), size=34),
                    txt("70%", size=80, weight=BOLD, color=LBLUE)).arrange(DOWN, buff=0.25).move_to([2.2, 0.2, 0])
        frame = SurroundingRectangle(VGroup(cloud, drops, fc), buff=0.45, color=GREY_B, corner_radius=0.2)
        q = txt("?", size=96, weight=BOLD, color=HILITE).next_to(frame, RIGHT, buff=0.3)
        t = line("14.1")
        with self.voiceover(t) as tr:
            self.play(Create(frame), FadeIn(cloud, shift=DOWN * 0.2), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.3) for d in drops], lag_ratio=0.15),
                      FadeIn(fc), run_time=1.0)
            self.cue(tr, t, 2)
            self.play(FadeIn(q, scale=0.6), run_time=0.5)
        forecast = VGroup(frame, cloud, drops, fc, q)

        faces = VGroup(*[die_face(n, 0.7) for n in range(1, 7)]).arrange(RIGHT, buff=0.3).move_to([-2.6, 0.9, 0])
        omega = SurroundingRectangle(faces, buff=0.25, color=GREY_B, corner_radius=0.15)
        om_l = MathTex(r"\Omega", font_size=40, color=GREY_B).next_to(omega, LEFT, buff=0.2)
        ring = VGroup(*[SurroundingRectangle(faces[i], buff=0.08, color=LBLUE, corner_radius=0.1) for i in (1, 3, 5)])
        a_l = MathTex("A", font_size=44, color=LBLUE).next_to(omega, UP, buff=0.2)
        fml = MathTex(r"P(A)=\frac{|A|}{|\Omega|}", "=", r"\frac{3}{6}", font_size=56).move_to([-2.6, -1.4, 0])
        cls = txt(label("classical"), size=32, weight=BOLD, color=LBLUE).next_to(fml, DOWN, buff=0.4)
        eq = txt(label("all_outcomes_equally_likely"), size=24, color=GREY_B)
        eq.next_to(omega, DOWN, buff=0.25)
        t = line("14.2")
        with self.voiceover(t) as tr:
            self.play(forecast.animate.scale(0.5).move_to([3.7, 1.6, 0]), run_time=0.8)
            self.play(FadeIn(faces, lag_ratio=0.1), Create(omega), FadeIn(om_l), FadeIn(cls), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(FadeIn(eq), run_time=0.5)
            self.play(Create(ring), FadeIn(a_l), FadeIn(fml[0]), run_time=0.9)
            self.play(FadeIn(fml[1:]), run_time=0.6)

        no_om = MathTex(r"\Omega = \;?", font_size=80).next_to(forecast, DOWN, buff=0.7)
        cross = Cross(no_om, stroke_color=RLRED, stroke_width=6)
        no_eq = txt(label("no_equally_likely_outcomes"), size=24, color=RLRED)
        no_eq.next_to(no_om, DOWN, buff=0.35)
        t = line("14.3")
        with self.voiceover(t) as tr:
            self.play(Indicate(forecast, color=HILITE, scale_factor=1.05), FadeIn(no_eq), run_time=0.9)
            self.cue(tr, t, {"en": 1, "uz": "sanaydigan"})
            self.play(FadeIn(no_om), run_time=0.5)
            self.play(Create(cross), run_time=0.5)
        self.clear_all()


class S14Empirical(LectureScene):
    def construct(self):
        # past days like today: an illustration of the idea, not a weather record
        rng = np.random.default_rng(3)
        rainy = set(rng.permutation(100)[:70].tolist())
        icons = VGroup(*[(drop_icon(0.24) if i in rainy else sun_icon(0.26)) for i in range(100)])
        slots = VGroup(*[Square(0.42, stroke_color=GREY_D, stroke_width=1) for _ in range(100)])
        slots.arrange_in_grid(rows=10, cols=10, buff=0.05).move_to([-3.9, -0.35, 0])
        for ic, sl in zip(icons, slots):
            ic.move_to(sl)
        ill = txt(label("illustration", 2), size=20, color=GREY_B).next_to(slots, DOWN, buff=0.15)
        head = txt(label("past_days_like_today"), size=26, color=GREY_B)
        head.next_to(slots, UP, buff=0.2)
        count = VGroup(drop_icon(0.3), txt("70 / 100", size=44, weight=BOLD, color=LBLUE)).arrange(RIGHT, buff=0.3)
        count.move_to([2.8, 2.2, 0])
        emp = txt(label("empirical_probability"), size=32, weight=BOLD, color=HILITE)
        emp.next_to(count, DOWN, buff=0.5)
        t = line("14.4")
        with self.voiceover(t) as tr:
            self.play(FadeIn(slots), FadeIn(head), FadeIn(ill), run_time=0.7)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(ic, scale=0.4) for ic in icons], lag_ratio=0.02), run_time=2.2)
            self.play(*[icons[i].animate.scale(1.15) for i in rainy], FadeIn(count), run_time=0.7)
            self.cue(tr, t, 2)
            self.play(FadeIn(emp, shift=UP * 0.2), run_time=0.6)

        f = VGroup(MathTex(r"P(A)\approx", font_size=50),
                   text_frac(label("times_the_event_was_observed"),
                             label("total_observations"), size=30))
        f.arrange(DOWN, buff=0.3).next_to(emp, DOWN, buff=0.6)
        t = line("14.5")
        with self.voiceover(t) as tr:
            self.cue(tr, t, 1)
            self.play(FadeIn(f, shift=UP * 0.2), run_time=0.9)
            self.play(Indicate(count[1], color=RLBLUE), run_time=0.8)
        self.clear_all()

        # 14.5a: the share of rainy days wobbles, then settles (an illustration from a fixed seed)
        R = L["rain_share"]
        days, share = R["days"], R["share"]
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 1, 0.25], x_length=9.4, y_length=4.2,
                  axis_config={"color": GREY_B, "stroke_width": 2, "include_tip": False},
                  y_axis_config={"numbers_to_include": [0, 0.25, 0.5, 0.75, 1], "font_size": 22,
                                 "decimal_number_config": {"num_decimal_places": 2}}).move_to([0.3, -0.2, 0])
        xt = VGroup(*[txt(f"{10 ** k:,}".replace(",", " "), size=20, color=GREY_B).next_to(ax.c2p(k, 0), DOWN, buff=0.15)
                      for k in range(5)])
        xl = txt(label("number_of_days"), size=22, color=GREY_B).next_to(xt, DOWN, buff=0.2)
        yl = txt(label("share_of_rainy_days"), size=22, color=GREY_B).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.6)
        truth = DashedLine(ax.c2p(0, R["p"]), ax.c2p(4, R["p"]), color=GREY_B, stroke_width=2)
        tl = txt(f"{R['p']}", size=22, color=GREY_B).next_to(ax.c2p(4, R["p"]), UR, buff=0.1)
        pts = [ax.c2p(np.log10(d), v) for d, v in zip(days, share)]
        path = VMobject(color=LBLUE, stroke_width=4).set_points_as_corners(pts)
        i10, iend = days.index(10), len(days) - 1
        m10 = Dot(pts[i10], radius=0.09, color=RLRED)
        mend = Dot(pts[iend], radius=0.09, color=RLGREEN)
        ill = txt(label("illustration", 2), size=20, color=GREY_B).next_to(ax, UP, buff=0.1).align_to(ax, RIGHT)
        t = line("14.5a")
        with self.voiceover(t) as tr:
            self.play(Create(ax), FadeIn(xt), FadeIn(xl), FadeIn(yl), FadeIn(ill), Create(truth), FadeIn(tl),
                      run_time=0.9)
            self.play(Create(path), run_time=2.4, rate_func=linear)
            self.cue(tr, t, 1)
            self.play(FadeIn(m10, scale=0.5), Flash(m10, color=RLRED), run_time=0.7)
            self.play(FadeIn(mend, scale=0.5), Flash(mend, color=RLGREEN), run_time=0.7)
        self.clear_all()

        bars, axis, nums = histogram()
        lab = tagged(N_EMP, label("salaries"), size=24, color=GREY_B).next_to(axis, DOWN, buff=0.5)
        res = VGroup(MathTex(rf"\frac{{{COUNTS[1]}}}{{{N_EMP}}}", "=", f"{P4060:.3f}", font_size=60),
                     txt(f"≈ {round(P4060 * 100)}%", size=48, weight=BOLD, color=HILITE)).arrange(DOWN, buff=0.4)
        res.move_to([4.4, 0.4, 0])
        cls = txt("$40k – $60k", size=28, color=HILITE).next_to(res, UP, buff=0.5)
        t = line("14.6")
        with self.voiceover(t) as tr:
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1), FadeIn(axis),
                      FadeIn(lab), run_time=1.2)
            self.play(FadeIn(nums), run_time=0.5)
            self.play(bars[1].animate.set_fill(HILITE).shift(UP * 0.35), nums[1].animate.set_color(HILITE)
                      .shift(UP * 0.35), FadeIn(cls), run_time=0.8)
            self.play(FadeIn(res[0]), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeIn(res[1], scale=0.8), run_time=0.6)

        uses = [label("class_shares_in_a_training_set"),
                label("word_frequencies_in_a_corpus"),
                label("click_through_rates_in_logs")]
        rows = VGroup(*[VGroup(MathTex(r"\frac{\#}{n}", font_size=36, color=HILITE), txt(u, size=26))
                        .arrange(RIGHT, buff=0.3) for u in uses]).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        ai = txt(label("ai_counts_then_divides"), size=30, weight=BOLD,
                 color=LBLUE)
        g = VGroup(ai, rows).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to([3.0, 0.2, 0])
        if g.get_right()[0] > 6.2:
            g.shift(LEFT * (g.get_right()[0] - 6.2))
        t = line("14.7")
        with self.voiceover(t) as tr:
            self.play(FadeOut(res), FadeOut(cls), VGroup(bars, axis, nums, lab).animate.scale(0.62)
                      .move_to([-4.3, -0.4, 0]), run_time=0.9)
            self.play(FadeIn(ai), run_time=0.5)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.4), run_time=1.6)
        self.clear_all()


class S14HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"{label('training_data')}:  P({label('spam')}) = {SPAM_SHARE}",
                           label("is_that_spam_probability_right_for_q")])
        card.to_edge(UP, buff=SAFE + 0.3)
        mails = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.8, height=0.55, stroke_width=2,
                                          stroke_color=RLRED if i < SPAM["spam"] else RLGREEN,
                                          fill_color=RLRED if i < SPAM["spam"] else RLGREEN, fill_opacity=0.25)
                         for i in range(SPAM["emails"])]).arrange(RIGHT, buff=0.18).move_to(DOWN * 1.9)
        for m in mails:
            m.add(VMobject(stroke_width=2, stroke_color=m.get_stroke_color()).set_points_as_corners(
                [m.get_corner(UL), m.get_center() + DOWN * 0.05, m.get_corner(UR)]))
        nine = tagged(f"{SPAM['spam']}/{SPAM['emails']}:", label("spam"), size=24, color=RLRED).next_to(mails, DOWN, buff=0.25)
        with self.voiceover(line("14.8")):
            self.play(FadeIn(card), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.2) for m in mails], lag_ratio=0.08), FadeIn(nine),
                      run_time=1.2)
        self.hands_on()

        # the sample (training set) does not look like the population (real mail)
        rng = np.random.default_rng(14)
        cloud = Ellipse(width=11.0, height=5.0, color=GREY_B, stroke_width=2).move_to([0, -0.6, 0])
        pop = VGroup()
        while len(pop) < 420:
            x, y = rng.uniform(-5.3, 5.3), rng.uniform(-2.9, 1.7)
            if (x / 5.5) ** 2 + ((y + 0.6) / 2.5) ** 2 < 0.92 and not (abs(x - 2.6) < 1.9 and -1.7 < y < 0.95):
                pop.add(Dot([x, y, 0], radius=0.045, color=RLRED if rng.random() < 0.15 else RLGREEN,
                            fill_opacity=0.75))
        samp_box = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.8, color=WHITE, stroke_width=3)
        samp_box.move_to([2.6, -0.6, 0])
        samp = VGroup(*[Dot([2.6 + (i % 5 - 2) * 0.4, -0.6 + (i // 5 - 0.5) * 0.5, 0], radius=0.08,
                            color=RLRED if i != 7 else RLGREEN) for i in range(SPAM["emails"])])   # one not spam
        pop_l = txt(label("real_email_population"), size=26, color=GREY_B)
        pop_l.next_to(cloud, UP, buff=0.15).set_x(-2.0)
        samp_l = txt(f"{label('training_set')}:  P({label('spam')}) = {SPAM_SHARE}", size=24, color=RLRED)
        samp_l.next_to(samp_box, UP, buff=0.15)
        samp_l.add_background_rectangle(opacity=0.85, buff=0.05)
        neq = txt(label("sample_population"), size=34, weight=BOLD, color=HILITE)
        neq.next_to(cloud, DOWN, buff=0.2)
        ill = txt(label("illustration", 2), size=18, color=GREY_B).next_to(cloud.get_corner(DL), UR, buff=0.0)
        ill.shift(LEFT * 0.0 + UP * 0.1)
        t = line("14.9")
        with self.voiceover(t) as tr:
            self.play(FadeOut(card), FadeOut(nine), run_time=0.5)
            self.play(ReplacementTransform(mails, samp), Create(samp_box), FadeIn(samp_l), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(Create(cloud), FadeIn(pop, lag_ratio=0.003), FadeIn(pop_l), FadeIn(ill), run_time=1.4)
            self.cue(tr, t, 2)
            self.play(FadeIn(neq, shift=UP * 0.2), Indicate(samp_box, color=HILITE), run_time=0.9)
        self.clear_all()


class S14Summary(LectureScene):
    def construct(self):
        head = self.heading(label("lecture_1_summary"), color=RLBLUE)

        def mini_types():
            return VGroup(RoundedRectangle(corner_radius=0.05, width=0.32, height=0.4, color=RLBLUE),
                          RoundedRectangle(corner_radius=0.05, width=0.32, height=0.4, color=HILITE)).arrange(RIGHT, buff=0.08)

        def mini_centre():
            hs = [0.2, 0.45, 0.35, 0.25, 0.12]
            b = VGroup(*[Rectangle(width=0.12, height=h, stroke_width=0, fill_color=RLBLUE, fill_opacity=1)
                         for h in hs]).arrange(RIGHT, buff=0.02, aligned_edge=DOWN)
            return VGroup(b, Line(UP * 0.28, DOWN * 0.28, color=RLGREEN).move_to(b).shift(LEFT * 0.08),
                          Line(UP * 0.28, DOWN * 0.28, color=RLRED).move_to(b).shift(RIGHT * 0.1))

        def mini_box():
            return VGroup(Line(LEFT * 0.35, RIGHT * 0.35, color=GREY_B),
                          Rectangle(width=0.3, height=0.25, color=RLGREEN).shift(LEFT * 0.03),
                          Dot(RIGHT * 0.45, radius=0.04, color=RLRED))

        def mini_scatter():
            pts = [(-0.25, -0.15), (-0.1, 0.0), (0.05, 0.05), (0.2, 0.2), (0.3, -0.2)]
            return VGroup(*[Dot([x, y, 0], radius=0.04, color=RLBLUE) for x, y in pts],
                          Line([-0.32, -0.2, 0], [0.35, 0.22, 0], color=RLRED, stroke_width=2))

        def mini_venn():
            return VGroup(Circle(radius=0.2, color=RLBLUE).shift(LEFT * 0.1),
                          Circle(radius=0.2, color=HILITE).shift(RIGHT * 0.1))

        items = [(mini_types, label("the_data_type_decides_the_calculation")),
                 (mini_centre, label("mean_keeps_the_total_median_survives")),
                 (mini_box, label("variance_and_iqr_measure_risk")),
                 (mini_scatter, label("always_plot_the_data")),
                 (mini_venn, label("probability_rules_complex_from_simple"))]
        rows = VGroup()
        for icon, text in items:
            ic = icon()
            if ic.height > 0.55:
                ic.scale_to_fit_height(0.55)
            slot = VGroup(Square(0.75, stroke_width=0), ic)
            ic.move_to(slot[0])
            rows.add(VGroup(slot, txt(text, size=30)).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, buff=0.38, aligned_edge=LEFT).next_to(head, DOWN, buff=0.55)
        if rows.width > 12.4:
            rows.scale_to_fit_width(12.4)
        rows.set_x(0)
        t = line("14.10")
        with self.voiceover(t) as tr:
            self.play(FadeIn(head), run_time=0.6)
            for k, r in enumerate(rows, 1):
                self.cue(tr, t, k)
                self.play(FadeIn(r, shift=RIGHT * 0.3), run_time=0.6)
        self.clear_all()

        end = VGroup(txt(label("lecture_1"), size=56, weight=BOLD, color=RLBLUE),
                     txt(label("the_end"), size=34, color=GREY_B)).arrange(DOWN, buff=0.3).move_to(UP * 0.4)
        nxt = VGroup(txt(label("next"), size=28, color=GREY_B),
                     txt(label("lecture_2_conditional_probability_and_bayes"), size=40, weight=BOLD, color=RLBLUE),
                     MathTex(r"P(A\mid B)", font_size=64, color=HILITE)).arrange(DOWN, buff=0.4)
        if nxt.width > 12.4:
            nxt.scale_to_fit_width(12.4)
        t = line("14.11")
        with self.voiceover(t) as tr:
            self.play(FadeIn(end, shift=UP * 0.3), run_time=0.9)
            self.cue(tr, t, 1)
            self.play(FadeOut(end), FadeIn(nxt, shift=UP * 0.3), run_time=1.0)
        self.play(FadeOut(nxt), run_time=0.6)
        self.play(FadeIn(brand_outro()), run_time=1.0)
        self.wait(2.0)
        self.clear_all(run_time=0.6)


SCENES = ["S14Classical", "S14Empirical", "S14HandsOn", "S14Summary"]
