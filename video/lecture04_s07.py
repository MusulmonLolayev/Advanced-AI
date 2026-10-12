"""Lecture 4, section 7 — the label's promise: 55 g or more, and why spread decides the failure rate.

Every number on screen comes from N (capture_l04.py, unit-tested by test_l04.py):
mu, sigma, normal_curve, label_min, label_z, label_short, label_per_1000, sigma_tight, tight_z,
tight_short, tight_per_10000, three_sigma_outside. The sigma = 1.5 g curve is the captured croissant
curve rescaled (lecture04_s06.bell_points), not recomputed.
"""
import numpy as np

from lecture04_s06 import CURVE, MU, SIGMA, area_on, bell_points, curve_on, g, gram_axes
from lecture04_kit import *

LIM = N["label_min"]
SHORT, PER_1000 = N["label_short"], N["label_per_1000"]
TIGHT, TIGHT_Z, TIGHT_PER_10000 = N["sigma_tight"], N["tight_z"], N["tight_per_10000"]
TIGHT_PTS = bell_points(MU, TIGHT)
LIGHT_C = RLRED


def croissant_grid(n=1000, cols=40, r=0.035, gap=0.105):
    """n croissants as small dots, cols to a row."""
    return VGroup(*[Dot([(i % cols) * gap, -(i // cols) * gap, 0], radius=r, color=GREY_D) for i in range(n)])


def lit_indices(k, n=1000):
    """k positions spread evenly through the grid (where they sit carries no meaning)."""
    return [round((i + 0.5) * n / k) for i in range(k)] if k else []


class S07Tail(LectureScene):
    def construct(self):
        self.section_card(7)
        ax = gram_axes(x_length=7.6, y_max=0.3, y_length=3.8).move_to(LEFT * 2.6 + DOWN * 0.5)
        bell = curve_on(ax, CURVE)
        mu_ln = DashedLine(ax.c2p(MU, 0), ax.c2p(MU, 0.21), color=WHITE, stroke_width=2.5)
        lim_ln = DashedLine(ax.c2p(LIM, 0), ax.c2p(LIM, 0.21), color=LIGHT_C, stroke_width=3)
        tag = VGroup(txt(f"{label('bottle_label')}:", size=26, weight=BOLD, color=HILITE),
                     MathTex(rf"\ge {g(LIM)}", font_size=38, color=HILITE)).arrange(RIGHT, buff=0.2)
        tag.next_to(lim_ln, UP, buff=0.15).shift(LEFT * 0.4)
        y_a = 0.17
        dist = DoubleArrow(ax.c2p(LIM, y_a), ax.c2p(MU, y_a), buff=0, color=LIGHT_C, stroke_width=3,
                           max_tip_length_to_length_ratio=0.12)
        dist_t = MathTex(rf"{dec(-N['label_z'], 1)}\,\sigma", font_size=34, color=LIGHT_C).next_to(dist, UP, buff=0.1)
        dist_t.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.05)
        with self.say("7.1") as (tr, t):
            self.play(FadeIn(ax), Create(bell), Create(mu_ln), run_time=0.9)
            self.play(Create(lim_ln), FadeIn(tag), run_time=0.6)
            self.cue(tr, t, {"en": "two point five sigma", "uz": "ikki butun oʻndan besh"})
            self.play(GrowFromCenter(dist), FadeIn(dist_t), run_time=0.6)

        # the tail: 0.62 %, about 6 in every 1000
        tail = area_on(ax, CURVE, CURVE[0][0], LIM, LIGHT_C, 0.9)
        zoom = Arrow(ax.c2p(LIM - 1.2, 0.07), ax.c2p(LIM - 0.6, 0.004), buff=0.05, color=LIGHT_C, stroke_width=3,
                     max_tip_length_to_length_ratio=0.25)
        pct_t = MathTex(rf"{dec(100 * SHORT, 2)}\%", font_size=36, color=LIGHT_C).next_to(zoom.get_start(), UP, buff=0.1)
        grid = croissant_grid().scale(0.92).move_to(RIGHT * 4.3 + DOWN * 0.2)
        g_cap = tagged(1000, label("croissants"), size=24, color=GREY_B).next_to(grid, UP, buff=0.15)
        k = round(PER_1000)
        lit = VGroup(*[grid[i] for i in lit_indices(k)])
        count = VGroup(MathTex(rf"\approx {k} \,/\, 1000", font_size=36, color=LIGHT_C),
                       txt(label("lighter_than_promised"), size=22, color=LIGHT_C)).arrange(DOWN, buff=0.08)
        count.next_to(grid, DOWN, buff=0.2)
        with self.say("7.2") as (tr, t):
            self.play(FadeIn(tail), GrowArrow(zoom), FadeIn(pct_t), run_time=0.8)
            self.cue(tr, t, {"en": "about six croissants", "uz": "har ming"})
            self.play(FadeIn(grid, lag_ratio=0.001), FadeIn(g_cap), run_time=0.9)
            self.play(*[d.animate.set_color(LIGHT_C).scale(1.8) for d in lit], FadeIn(count), run_time=0.7)

        # a more precise process: sigma 2 g → 1.5 g, the mean unchanged
        tight = curve_on(ax, TIGHT_PTS)
        sig_t = MathTex(rf"\sigma:\; {g(SIGMA)} \;\to\; {g(TIGHT)}", font_size=36, color=LBLUE)
        prec = txt(label("a_more_precise_process"), size=24, color=LBLUE)
        same = txt(label("mean_unchanged"), size=22, color=GREY_B)
        sig_box = VGroup(sig_t, prec, same).arrange(DOWN, buff=0.12).to_corner(UL, buff=SAFE + 0.3)
        with self.say("7.3") as (tr, t):
            self.play(FadeOut(VGroup(zoom, pct_t)), FadeIn(sig_box[1]), run_time=0.5)
            self.cue(tr, t, {"en": "sigma becomes", "uz": "sigma bir butun"})
            self.play(Write(sig_t), FadeIn(same), run_time=0.7)

        dist2_t = MathTex(rf"{dec(-TIGHT_Z, 1)}\,\sigma", font_size=34, color=LIGHT_C).move_to(dist_t)
        dist2_t.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.05)
        tail2 = area_on(ax, TIGHT_PTS, TIGHT_PTS[0][0], LIM, LIGHT_C, 0.9)
        k2 = round(1000 * N["tight_short"])
        count2 = MathTex(rf"\approx {dec(1000 * N['tight_short'], 1)} \,/\, 1000", font_size=36, color=LIGHT_C).move_to(count[0])
        with self.say("7.4") as (tr, t):
            self.play(Transform(bell, tight), Transform(tail, tail2), run_time=1.2)
            self.cue(tr, t, {"en": "three point three sigma", "uz": "uch butun oʻndan uch"})
            self.play(Transform(dist_t, dist2_t), run_time=0.5)
            self.cue(tr, t, {"en": "falls sharply", "uz": "keskin kamayadi"})
            self.play(*[d.animate.set_color(GREY_D).scale(1 / 1.8) for d in lit[k2:]],
                      Transform(count[0], count2), run_time=0.8)

        lesson = txt(label("spread_not_the_average_decides_the_failure_rate"), size=30, weight=BOLD, color=HILITE)
        back = txt(label("lecture_1_the_bottling_line"), size=24, color=GREY_B)
        les = VGroup(lesson, back).arrange(DOWN, buff=0.2)
        if les.width > 12.4:
            les.scale_to_fit_width(12.4)
        les.to_edge(UP, buff=SAFE + 0.25)
        bg = BackgroundRectangle(les, color=BLACK, fill_opacity=0.92, buff=0.15)
        with self.say("7.5") as (tr, t):
            self.play(FadeOut(sig_box), FadeOut(tag), FadeIn(bg), FadeIn(lesson, shift=DOWN * 0.2), run_time=0.8)
            self.cue(tr, t, {"en": "bottling line", "uz": "shisha toʻldirish"})
            self.play(FadeIn(back), run_time=0.5)
        self.clear_all()


class S07Alert(LectureScene):
    """AI: a value more than three sigma away raises an alert. The readings are an illustration."""
    def construct(self):
        rng = np.random.default_rng(7)
        n = 60
        vals = rng.normal(0, 1, n)
        vals[41] = 3.6                                   # the one reading far out
        x0, dx, ys = -5.6, 0.18, 0.55
        base_y = -0.4
        pts = [[x0 + i * dx, base_y + v * ys, 0] for i, v in enumerate(vals)]
        line = VMobject(stroke_color=GREY_B, stroke_width=2).set_points_as_corners(pts)
        dots = VGroup(*[Dot(p, radius=0.045, color=GREY_B) for p in pts])
        x1 = x0 + (n - 1) * dx
        bands = VGroup(*[DashedLine([x0, base_y + s * 3 * ys, 0], [x1, base_y + s * 3 * ys, 0], color=HILITE,
                                    stroke_width=2.5) for s in (1, -1)])
        b_t = VGroup(MathTex(r"+3\sigma", font_size=30, color=HILITE).next_to(bands[0], RIGHT, buff=0.15),
                     MathTex(r"-3\sigma", font_size=30, color=HILITE).next_to(bands[1], RIGHT, buff=0.15))
        cap = txt(label("readings"), size=24, color=GREY_B).next_to(VGroup(line, bands), DOWN, buff=0.35)
        out = dots[41]
        ring = Circle(radius=0.22, color=RLRED, stroke_width=4).move_to(out)
        alert = txt(label("alert"), size=26, weight=BOLD, color=RLRED).next_to(ring, UP, buff=0.15)
        rate = VGroup(MathTex(rf"\approx {round(1000 * N['three_sigma_outside'])} \,/\, 1000", font_size=44, color=HILITE),
                      txt(label("normal_readings_beyond_three_sigma"), size=22, color=GREY_B)).arrange(DOWN, buff=0.12)
        rate.to_corner(UR, buff=SAFE + 0.4)
        note = info(label("illustration"))
        with self.say("7.6") as (tr, t):
            self.play(Create(line), FadeIn(dots), FadeIn(cap), FadeIn(note), run_time=1.2)
            self.cue(tr, t, {"en": "more than three sigma", "uz": "uch sigmadan"})
            self.play(Create(bands), FadeIn(b_t), run_time=0.6)
            self.play(out.animate.set_color(RLRED).scale(1.6), Create(ring), FadeIn(alert), run_time=0.6)
            self.cue(tr, t, {"en": "three readings in a thousand", "uz": "mingtadan"})
            self.play(FadeIn(rate, shift=LEFT * 0.2), run_time=0.6)
        self.clear_all()


def croissant_icon(color=HILITE, s=0.9):
    """A crescent."""
    outer = Arc(radius=s, start_angle=PI * 0.15, angle=PI * 0.7)
    inner = Arc(radius=s * 0.62, start_angle=PI * 0.85, angle=-PI * 0.7).shift(UP * s * 0.12)
    shape = VMobject(fill_color=color, fill_opacity=0.9, stroke_color=color, stroke_width=2)
    shape.set_points(np.concatenate([outer.points, inner.points]))
    return shape


def loaf_icon(color=RLORANGE, s=0.9):
    body = RoundedRectangle(corner_radius=s * 0.35, width=s * 2.2, height=s * 0.95, fill_color=color,
                            fill_opacity=0.9, stroke_width=0)
    cuts = VGroup(*[Line(UP * s * 0.25, DOWN * s * 0.15, color=BLACK, stroke_width=3).rotate(-0.4)
                    .move_to(body.get_center() + RIGHT * dx * s) for dx in (-0.5, 0, 0.5)])
    return VGroup(body, cuts)


class S07HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"σ = {TIGHT:g} g", f"P(X < {LIM:g} g) × 10 000 = ?"])
        card.move_to(UP * 0.6)
        with self.say("7.7"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        before = round(10_000 * SHORT)
        after = round(TIGHT_PER_10000)
        rows = VGroup()
        top = max(before, after)
        for sig, v, c in ((SIGMA, before, GREY_B), (TIGHT, after, LIGHT_C)):
            bar = Rectangle(width=max(7.0 * v / top, 0.06), height=0.55, stroke_width=0, fill_color=c, fill_opacity=1)
            lab_ = MathTex(rf"\sigma = {g(sig)}", font_size=36, color=c)
            val = MathTex(rf"{'' if v == before else r'\approx '}{v} \,/\, 10\,000", font_size=36, color=c)
            rows.add(VGroup(lab_, bar, val))
        for r in rows:
            r[0].move_to([-4.6, 0, 0])
            r[1].next_to([-3.4, 0, 0], RIGHT, buff=0)
            r[2].next_to(r[1], RIGHT, buff=0.3)
        rows[0].shift(UP * 0.6)
        rows[1].shift(DOWN * 0.6)
        head = MathTex(rf"P(X < {g(LIM)})", font_size=40).to_edge(UP, buff=SAFE + 0.6)
        with self.say("7.8") as (tr, t):
            self.play(FadeIn(head), FadeIn(rows[1][0]), GrowFromEdge(rows[1][1], LEFT), FadeIn(rows[1][2]), run_time=0.9)
            self.cue(tr, t, {"en": "Before, it was", "uz": "Ilgari"})
            self.play(FadeIn(rows[0][0]), GrowFromEdge(rows[0][1], LEFT), FadeIn(rows[0][2]), run_time=0.8)
        self.clear_all()

        cro = VGroup(croissant_icon(), txt(label("croissant"), size=28, color=HILITE)).arrange(DOWN, buff=0.3)
        loaf = VGroup(loaf_icon(), txt(label("loaf"), size=28, color=RLORANGE)).arrange(DOWN, buff=0.3)
        pair = VGroup(cro, txt("?", size=64, weight=BOLD, color=WHITE), loaf).arrange(RIGHT, buff=1.2)
        grams = VGroup(MathTex(r"\mathrm{g}", font_size=40, color=HILITE).next_to(cro, DOWN, buff=0.25),
                       MathTex(r"\mathrm{g}", font_size=40, color=RLORANGE).next_to(loaf, DOWN, buff=0.25))
        with self.say("7.9") as (tr, t):
            self.play(FadeIn(cro, shift=RIGHT * 0.2), FadeIn(loaf, shift=LEFT * 0.2), run_time=0.7)
            self.play(FadeIn(pair[1], scale=0.6), run_time=0.4)
            self.cue(tr, t, {"en": "their grams", "uz": "grammlari"})
            self.play(FadeIn(grams), run_time=0.5)
        self.clear_all(run_time=0.3)      # the next section opens on a silent card


SCENES = ["S07Tail", "S07Alert", "S07HandsOn"]
