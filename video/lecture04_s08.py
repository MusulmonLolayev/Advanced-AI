"""Lecture 4, section 8 — z-scores: which bake went further wrong, and standardizing.

Every number on screen comes from N (capture_l04.py, unit-tested by test_l04.py):
mu, sigma, normal_curve, light, z_light, p_light, loaf_mu, loaf_sigma, loaf, z_loaf, p_loaf, heavy,
z_heavy, days, day_mean, day_sd. The loaf curve and the standard curve are the captured croissant curve rescaled
(lecture04_s06.bell_points), not recomputed.
"""
import numpy as np

from lecture04_s06 import CURVE, MU, SIGMA, area_on, bell_points, curve_on, g, gram_axes
from lecture04_kit import *

LIGHT, Z_LIGHT, P_LIGHT = N["light"], N["z_light"], N["p_light"]
LOAF_MU, LOAF_SIGMA, LOAF = N["loaf_mu"], N["loaf_sigma"], N["loaf"]
Z_LOAF, P_LOAF = N["z_loaf"], N["p_loaf"]
HEAVY, Z_HEAVY = N["heavy"], N["z_heavy"]
CRO_C, LOAF_C = HILITE, RLORANGE
LOAF_PTS = bell_points(LOAF_MU, LOAF_SIGMA)
Z_PTS = bell_points(0.0, 1.0)                    # the standard curve: z from −4 to 4


def zd(z, places=2):
    """−1.5, −1.33, +1.5 with a real minus sign and an explicit plus."""
    # the kit's dec() strips zeros from a whole number with places=0 ("20" -> "2"), so round here
    s = str(round(abs(z))) if places == 0 else dec(abs(z), places)
    return ("+" if z > 0 else "-" if z < 0 else "") + s


class S08ZScore(LectureScene):
    def construct(self):
        self.section_card(8)
        formula = MathTex("z", "=", r"\frac{x - \mu}{\sigma}", font_size=64)
        z_w = txt(label("z_score"), size=30, weight=BOLD, color=HILITE)
        no_units = txt(label("no_units"), size=24, color=GREY_B)
        head = VGroup(z_w, formula, no_units).arrange(DOWN, buff=0.3).move_to(UP * 0.4)
        units = VGroup(MathTex(r"\mathrm{g}", font_size=40, color=CRO_C), MathTex(r"\mathrm{min}", font_size=40, color=LBLUE))
        units.arrange(RIGHT, buff=1.0).next_to(no_units, DOWN, buff=0.45)
        arrow = MathTex(r"\to\; z", font_size=40, color=HILITE).next_to(units, RIGHT, buff=0.5)
        with self.say("8.1") as (tr, t):
            self.play(FadeIn(z_w), Write(formula), run_time=0.9)
            self.cue(tr, t, {"en": "It has no units", "uz": "Uning birligi"})
            self.play(FadeIn(no_units), FadeIn(units), run_time=0.6)
            self.play(Write(arrow), run_time=0.5)
        self.play(FadeOut(VGroup(units, arrow, no_units)), VGroup(z_w, formula).animate.scale(0.7)
                  .to_corner(UL, buff=SAFE + 0.25), run_time=0.6)

        # the light croissant and the light loaf, each on its own axis, each worked out to its right
        ax_c = gram_axes(x_length=6.4, y_length=2.1).move_to(LEFT * 1.6 + UP * 0.75)
        bell_c = curve_on(ax_c, CURVE, color=CRO_C)
        mark_c = DashedLine(ax_c.c2p(LIGHT, 0), ax_c.c2p(LIGHT, 0.17), color=CRO_C, stroke_width=3)
        cro_w = txt(label("croissant"), size=26, color=CRO_C).next_to(ax_c, LEFT, buff=0.3)
        calc_c = MathTex(rf"z = \frac{{{LIGHT:g} - {MU:g}}}{{{SIGMA:g}}} = {zd(Z_LIGHT)}", font_size=36, color=CRO_C)
        calc_c.next_to(ax_c, RIGHT, buff=0.45).shift(UP * 0.35)
        with self.say("8.2") as (tr, t):
            self.play(FadeIn(ax_c), Create(bell_c), FadeIn(cro_w), run_time=0.8)
            self.play(Create(mark_c), run_time=0.4)
            self.cue(tr, t, {"en": "minus three divided", "uz": "minus uchni"})
            self.play(Write(calc_c), run_time=0.8)

        # the loaf: 480 g, loaves N(500, 15²)
        lo, hi = LOAF_MU - 4 * LOAF_SIGMA, LOAF_MU + 4 * LOAF_SIGMA
        ax_l = gram_axes(x_range=(lo, hi, 20), x_length=6.4, y_max=0.22 * SIGMA / LOAF_SIGMA, y_length=2.1)
        ax_l.move_to(LEFT * 1.6 + DOWN * 2.15)
        bell_l = curve_on(ax_l, LOAF_PTS, color=LOAF_C)
        mark_l = DashedLine(ax_l.c2p(LOAF, 0), ax_l.c2p(LOAF, 0.17 * SIGMA / LOAF_SIGMA), color=LOAF_C, stroke_width=3)
        loaf_w = txt(label("loaf"), size=26, color=LOAF_C).next_to(ax_l, LEFT, buff=0.3).align_to(cro_w, RIGHT)
        params = MathTex(rf"\mu = {g(LOAF_MU)},\;\; \sigma = {g(LOAF_SIGMA)}", font_size=30, color=LOAF_C)
        params.next_to(ax_l, RIGHT, buff=0.45).shift(UP * 0.75)
        calc_l = MathTex(rf"z = \frac{{{LOAF:g} - {LOAF_MU:g}}}{{{LOAF_SIGMA:g}}} = {zd(Z_LOAF)}", font_size=36, color=LOAF_C)
        calc_l.next_to(params, DOWN, buff=0.3).align_to(params, LEFT)
        calc_c.align_to(params, LEFT)
        raw_c = MathTex(rf"{zd(LIGHT - MU, 0)}\,\mathrm{{g}}", font_size=32, color=CRO_C).next_to(calc_c, DOWN, buff=0.3).align_to(calc_c, LEFT)
        raw_l = MathTex(rf"{zd(LOAF - LOAF_MU, 0)}\,\mathrm{{g}}", font_size=32, color=LOAF_C).next_to(calc_l, DOWN, buff=0.3).align_to(calc_l, LEFT)
        with self.say("8.3") as (tr, t):
            self.cue(tr, t, {"en": "a loaf at", "uz": "non esa"})
            self.play(FadeIn(ax_l), Create(bell_l), FadeIn(loaf_w), Create(mark_l), run_time=0.9)
            self.cue(tr, t, {"en": "Loaves average", "uz": "Nonlar oʻrtacha"})
            self.play(FadeIn(params), run_time=0.6)

        with self.say("8.4") as (tr, t):
            self.play(FadeIn(raw_l), FadeIn(raw_c), run_time=0.6)
            self.cue(tr, t, {"en": "Yet the loaf", "uz": "Lekin nonning"})
            self.play(Write(calc_l), run_time=0.6)
            self.cue(tr, t, {"en": "and the croissant's", "uz": "kruassanniki"})
            self.play(Indicate(calc_c, color=WHITE, scale_factor=1.08), run_time=0.6)
        self.clear_all()

        # one z axis: the two curves become the same curve, with two marks on it
        ax_z = gram_axes(x_range=(-4, 4, 1), x_length=10.0, y_max=0.45, y_length=3.6).move_to(DOWN * 0.5)
        bell_z = curve_on(ax_z, Z_PTS, color=WHITE)
        z_lab = MathTex("z", font_size=36, color=GREY_B).next_to(ax_z.x_axis, RIGHT, buff=0.2)
        tail_c = area_on(ax_z, Z_PTS, -4, Z_LIGHT, CRO_C, 0.75)
        tail_l = area_on(ax_z, Z_PTS, Z_LIGHT, Z_LOAF, LOAF_C, 0.6)
        mk_c = DashedLine(ax_z.c2p(Z_LIGHT, 0), ax_z.c2p(Z_LIGHT, 0.34), color=CRO_C, stroke_width=3)
        mk_l = DashedLine(ax_z.c2p(Z_LOAF, 0), ax_z.c2p(Z_LOAF, 0.22), color=LOAF_C, stroke_width=3)
        t_c = VGroup(txt(label("croissant"), size=24, color=CRO_C),
                     MathTex(rf"{zd(Z_LIGHT)} \;\to\; {dec(100 * P_LIGHT, 1)}\%", font_size=32, color=CRO_C)
                     ).arrange(DOWN, buff=0.06)
        t_c.next_to(ax_z.c2p(Z_LIGHT, 0.34), LEFT, buff=0.25)
        t_l = VGroup(txt(label("loaf"), size=24, color=LOAF_C),
                     MathTex(rf"{zd(Z_LOAF)} \;\to\; {dec(100 * P_LOAF, 1)}\%", font_size=32, color=LOAF_C)
                     ).arrange(DOWN, buff=0.06)
        t_l.next_to(ax_z.c2p(Z_LIGHT, 0.2), LEFT, buff=0.25)
        lead = Line(t_l.get_right() + RIGHT * 0.05, ax_z.c2p(Z_LOAF, 0.2), color=LOAF_C, stroke_width=2)
        for m in (t_c, t_l):
            m.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.06)
        verdict = VGroup(txt(label("raw_difference"), size=26, color=GREY_B), MathTex(r"\neq", font_size=40),
                         txt(label("how_unusual"), size=26, color=HILITE)).arrange(RIGHT, buff=0.3)
        verdict.to_edge(UP, buff=SAFE + 0.35)
        with self.say("8.5") as (tr, t):
            self.play(FadeIn(ax_z), Create(bell_z), FadeIn(z_lab), run_time=0.8)
            self.play(Create(mk_c), Create(mk_l), run_time=0.5)
            self.cue(tr, t, {"en": "six point seven percent", "uz": "olti butun oʻndan yetti"})
            self.play(FadeIn(tail_c), FadeIn(t_c), run_time=0.6)
            self.cue(tr, t, {"en": "nine point one percent", "uz": "toʻqqiz butun oʻndan bir"})
            self.play(FadeIn(tail_l), FadeIn(t_l), Create(lead), run_time=0.6)
            self.cue(tr, t, {"en": "Raw differences mislead", "uz": "Xom farq"})
            self.play(FadeIn(verdict, shift=DOWN * 0.2), run_time=0.6)
        self.clear_all()


class S08Standardize(LectureScene):
    def construct(self):
        # standardizing every column of a table: the captured trading days, first rows
        days = N["days"][:5]
        cols = [[d[0] for d in days], [d[1] for d in days]]
        mus, sds = N["day_mean"], N["day_sd"]
        heads = [label("record_temperature"), label("record_iced_coffees")]

        def table(values, fmt, color):
            g_ = VGroup()
            for j, (h, col) in enumerate(zip(heads, values)):
                c = VGroup(txt(h, size=22, color=GREY_B, weight=BOLD),
                           *[MathTex(fmt(v), font_size=30, color=color) for v in col]).arrange(DOWN, buff=0.22)
                g_.add(c)
            return g_.arrange(RIGHT, buff=0.8)

        raw = table(cols, lambda v: dec(v, 1), WHITE).move_to(LEFT * 3.6 + DOWN * 0.2)
        zs = [[(v - m) / s for v in col] for col, m, s in zip(cols, mus, sds)]
        std = table(zs, lambda v: zd(v, 2), HILITE).move_to(RIGHT * 3.6 + DOWN * 0.2)
        arrow = MathTex(r"\xrightarrow{\;(x - \mu)\,/\,\sigma\;}", font_size=40, color=HILITE).move_to(DOWN * 0.2)
        title = txt(label("standardizing"), size=32, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.35)
        with self.say("8.6") as (tr, t):
            self.play(FadeIn(raw), run_time=0.5)
            self.cue(tr, t, {"en": "every column", "uz": "har bir ustuniga"})
            self.play(Write(arrow), TransformFromCopy(raw, std), run_time=1.0)
            self.cue(tr, t, {"en": "standardizing", "uz": "standartlashtirish"})
            self.play(FadeIn(title), run_time=0.4)
        self.clear_all()

        # AI: k nearest neighbours in grams vs kilograms; batch normalization (an illustration)
        rng = np.random.default_rng(8)
        pts = rng.normal(0, 1, (12, 2))
        knn_w = txt(label("k_nearest_neighbours"), size=28, weight=BOLD, color=LBLUE).to_corner(UL, buff=SAFE + 0.3)
        ax_a = Axes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], x_length=4.6, y_length=2.4, tips=False,
                    axis_config={"color": GREY_B, "stroke_width": 2, "include_ticks": False}).move_to(LEFT * 3.4 + DOWN * 0.3)
        ax_b = Axes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], x_length=4.6, y_length=2.4, tips=False,
                    axis_config={"color": GREY_B, "stroke_width": 2, "include_ticks": False}).move_to(RIGHT * 3.4 + DOWN * 0.3)
        # before: one column in grams spreads a thousand times wider, so only it counts
        squash = VGroup(*[Dot(ax_a.c2p(x * 1.0, y * 0.003), radius=0.07, color=WHITE) for x, y in pts])
        even = VGroup(*[Dot(ax_b.c2p(x, y), radius=0.07, color=HILITE) for x, y in pts])
        ga = VGroup(txt(label("grams"), size=22, color=GREY_B).next_to(ax_a.x_axis, DOWN, buff=0.15)
                    .align_to(ax_a.x_axis, RIGHT),
                    txt(label("kilograms"), size=22, color=GREY_B).next_to(ax_a.y_axis, UP, buff=0.1))
        gb = VGroup(MathTex("z_1", font_size=30, color=GREY_B).next_to(ax_b.x_axis, DOWN, buff=0.15)
                    .align_to(ax_b.x_axis, RIGHT),
                    MathTex("z_2", font_size=30, color=GREY_B).next_to(ax_b.y_axis, UP, buff=0.1))
        mid = MathTex(r"\to", font_size=56, color=HILITE).move_to(DOWN * 0.3)
        bn = VGroup(txt(label("batch_normalization"), size=26, weight=BOLD, color=LBLUE),
                    MathTex(r"\frac{a - \mu_{\text{batch}}}{\sigma_{\text{batch}}}", font_size=40)).arrange(RIGHT, buff=0.4)
        bn.to_edge(DOWN, buff=SAFE + 0.75)
        note = info(label("illustration"))
        with self.say("8.7") as (tr, t):
            self.play(FadeIn(knn_w), FadeIn(ax_a), FadeIn(ga), FadeIn(squash), FadeIn(note), run_time=0.8)
            self.cue(tr, t, {"en": "Standardize first", "uz": "Standartlashtirsak"})
            self.play(FadeIn(mid), FadeIn(ax_b), FadeIn(gb), TransformFromCopy(squash, even), run_time=1.0)
            self.cue(tr, t, {"en": "batch normalization", "uz": "paketli normallashtirish"})
            self.play(FadeIn(bn, shift=UP * 0.2), run_time=0.7)
        self.clear_all()


class S08HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"μ = {MU:g} g,   σ = {SIGMA:g} g", f"x = {HEAVY:g} g:   z = ?"])
        card.move_to(UP * 0.6)
        with self.say("8.8"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        ax = gram_axes(x_length=9.0, y_length=3.0).move_to(DOWN * 0.6)
        bell = curve_on(ax, CURVE, color=CRO_C)
        mk = DashedLine(ax.c2p(HEAVY, 0), ax.c2p(HEAVY, 0.17), color=HILITE, stroke_width=3)
        calc = MathTex(rf"z = \frac{{{HEAVY:g} - {MU:g}}}{{{SIGMA:g}}} = {zd(Z_HEAVY)}", font_size=44, color=HILITE)
        calc.next_to(mk, UP, buff=0.15)
        calc.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.05)
        heavy_w = txt(label("heavy"), size=26, color=HILITE).next_to(calc, RIGHT, buff=0.3)
        with self.say("8.9") as (tr, t):
            self.play(FadeIn(ax), Create(bell), Create(mk), run_time=0.8)
            self.play(Write(calc), run_time=0.8)
            self.cue(tr, t, {"en": "heavy", "uz": "ogʻir"})
            self.play(FadeIn(heavy_w), run_time=0.4)
        self.clear_all()

        # teaser: a record is a bundle of numbers (the first captured trading day)
        d = N["days"][0]
        rec = VGroup(VGroup(txt(label("record_temperature"), size=26, color=GREY_B), MathTex(dec(d[0], 1), font_size=40)),
                     VGroup(txt(label("record_iced_coffees"), size=26, color=GREY_B), MathTex(dec(d[1], 1), font_size=40)))
        for r in rec:
            r.arrange(RIGHT, buff=0.4)
        rec.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        box = SurroundingRectangle(rec, color=LBLUE, buff=0.3, corner_radius=0.15)
        bundle = VGroup(box, rec).move_to(ORIGIN)
        with self.say("8.10") as (tr, t):
            self.play(Create(box), FadeIn(rec[0]), run_time=0.7)
            self.cue(tr, t, {"en": "in bundles", "uz": "toʻda"})
            self.play(FadeIn(rec[1], shift=UP * 0.2), run_time=0.5)
        self.clear_all(run_time=0.3)      # the next section opens on a silent card


SCENES = ["S08ZScore", "S08Standardize", "S08HandsOn"]
