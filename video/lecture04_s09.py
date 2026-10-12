"""Lecture 4, section 9 — the multivariate Gaussian: hot days and iced coffee.

The 300 dots are the figure script's own simulated trading days (same generator and seed, captured
in l04_numbers.json); the mean vector, covariance matrix, ellipses and the odd day's numbers are the
sample's, as the slide quotes them.
"""
import numpy as np
from lecture04_kit import *

DAYS = np.array(N["days"])
MU = N["day_mean"]
COV = N["day_cov"]
SD = N["day_sd"]
CORR = N["day_corr"]
VALS = N["day_axes"]["vals"]
VECS = N["day_axes"]["vecs"]
ODD = N["odd_day"]
ODD_Z = N["odd_z"]
MAHAL = N["odd_mahalanobis"]


def day_axes(x_length=7.2, y_length=4.2):
    """Temperature against cups, sized for the 300 days."""
    ax = Axes(x_range=[0, 40, 10], y_range=[0, 80, 20], x_length=x_length, y_length=y_length, tips=False,
              axis_config={"color": GREY_B, "stroke_width": 2, "include_numbers": True, "font_size": 22})
    xl = txt(label("temperature_c"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.45)
    yl = txt(label("iced_coffees_sold"), size=22, color=GREY_B).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
    return ax, VGroup(xl, yl)


def day_dots(ax, opacity=0.75, radius=0.045):
    return VGroup(*[Dot(ax.c2p(t, c), radius=radius, color=RLGREEN, fill_opacity=opacity) for t, c in DAYS])


def ellipse(ax, k, color=HILITE, width=3):
    """The k-sigma contour: the mean plus k·sqrt(eigenvalue) along each eigenvector of the covariance."""
    a, b = k * np.sqrt(VALS[0]), k * np.sqrt(VALS[1])
    pts = []
    for th in np.linspace(0, 2 * np.pi, 121):
        x = MU[0] + a * np.cos(th) * VECS[0][0] + b * np.sin(th) * VECS[1][0]
        y = MU[1] + a * np.cos(th) * VECS[0][1] + b * np.sin(th) * VECS[1][1]
        pts.append(ax.c2p(x, y))
    return VMobject(stroke_color=color, stroke_width=width).set_points_as_corners(pts)


def odd_star(ax):
    return Star(n=5, outer_radius=0.2, inner_radius=0.09, color=HILITE, fill_opacity=1, stroke_width=0).move_to(
        ax.c2p(*ODD))


def scatter_scene(self_, ax_pos=LEFT * 2.2 + UP * 0.25):
    ax, labs = day_axes()
    VGroup(ax, labs).move_to(ax_pos)
    return ax, labs, day_dots(ax)


def matrix_tex(rows, color=WHITE):
    """A matrix from formatted entries, entries addressable through get_entries()."""
    return Matrix(rows, element_to_mobject=lambda s: MathTex(s, font_size=40, color=color),
                  h_buff=1.5, v_buff=0.8, bracket_h_buff=0.15)


class S09Scatter(LectureScene):
    def construct(self):
        self.section_card(9)
        ax, labs, dots = scatter_scene(self)
        note = info(f"{N['n_days']} {label('simulated_days')}")
        with self.say("9.1") as (tr, t):
            self.play(Create(ax), FadeIn(labs), FadeIn(note), run_time=0.9)
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.006), run_time=1.6)
            self.cue(tr, t, 1)
            warm = VGroup(*[d for d, (tc, c) in zip(dots, DAYS) if tc > MU[0] + SD[0]])
            self.play(Indicate(warm, color=HILITE, scale_factor=1.3), run_time=0.9)

        # one column at a time: the dots squashed onto each axis lose the link between them
        x0, y0 = ax.c2p(0, 0)[0], ax.c2p(0, 0)[1]
        rug_x = VGroup(*[Line(UP * 0.12, DOWN * 0.12, color=RLGREEN, stroke_width=1.5, stroke_opacity=0.6)
                         .move_to([ax.c2p(tc, 0)[0], y0 + 0.2, 0]) for tc, _ in DAYS])
        rug_y = VGroup(*[Line(LEFT * 0.12, RIGHT * 0.12, color=RLGREEN, stroke_width=1.5, stroke_opacity=0.6)
                         .move_to([x0 + 0.2, ax.c2p(0, c)[1], 0]) for _, c in DAYS])
        cov_word = txt(label("covariance"), size=40, weight=BOLD, color=HILITE)
        cov_sub = txt(label("moving_together"), size=26, color=GREY_B)
        cov = VGroup(cov_word, cov_sub).arrange(DOWN, buff=0.2).move_to([4.4, 0.6, 0])
        with self.say("9.2") as (tr, t):
            self.play(ReplacementTransform(dots.copy(), rug_x), ReplacementTransform(dots.copy(), rug_y),
                      dots.animate.set_opacity(0.15), run_time=1.2)
            self.cue(tr, t, {"en": "That number is the covariance", "uz": "Bu kovariatsiya"})
            self.play(FadeOut(rug_x), FadeOut(rug_y), dots.animate.set_opacity(0.75), FadeIn(cov, shift=UP * 0.2),
                      run_time=0.9)
        self.clear_all()


class S09Matrix(LectureScene):
    def construct(self):
        mu_m = matrix_tex([[dec(MU[0], 1)], [dec(MU[1], 1)]])
        mu_l = MathTex(r"\boldsymbol{\mu} =", font_size=48)
        mu_g = VGroup(mu_l, mu_m).arrange(RIGHT, buff=0.2)
        sig_m = matrix_tex([[dec(COV[0][0], 1), dec(COV[0][1], 1)], [dec(COV[1][0], 1), dec(COV[1][1], 1)]])
        sig_l = MathTex(r"\Sigma =", font_size=48)
        sig_g = VGroup(sig_l, sig_m).arrange(RIGHT, buff=0.2)
        top = VGroup(mu_g, sig_g).arrange(RIGHT, buff=2.2).move_to(UP * 1.3 + LEFT * 1.3)   # room for Σ₁₂ > 0
        mu_cap = txt(label("mean_vector"), size=26, color=LBLUE).next_to(mu_g, DOWN, buff=0.35)
        sig_cap = txt(label("covariance_matrix"), size=26, color=LBLUE).next_to(sig_g, DOWN, buff=0.35)
        e = sig_m.get_entries()
        diag_box = VGroup(*[SurroundingRectangle(e[i], buff=0.1, color=RLGREEN, stroke_width=3) for i in (0, 3)])
        off_box = VGroup(*[SurroundingRectangle(e[i], buff=0.1, color=HILITE, stroke_width=3) for i in (1, 2)])
        diag_l = txt(label("variance"), size=24, color=RLGREEN)
        off_l = txt(label("covariance"), size=24, color=HILITE)
        VGroup(diag_l, off_l).arrange(RIGHT, buff=0.8).next_to(sig_cap, DOWN, buff=0.3)
        with self.say("9.3") as (tr, t):
            self.play(Write(mu_g), FadeIn(mu_cap), run_time=0.9)
            self.play(Write(sig_g), FadeIn(sig_cap), run_time=0.9)
            self.cue(tr, t, 1)
            self.play(Create(diag_box), FadeIn(diag_l), run_time=0.7)
            self.cue(tr, t, {"en": "off the diagonal", "uz": "diagonaldan tashqarida"})
            self.play(Create(off_box), FadeIn(off_l), run_time=0.7)

        # the means, each in its own unit
        me = mu_m.get_entries()
        # units outside the bracket, level with their entries
        units = VGroup(MathTex(r"^\circ\mathrm{C}", font_size=34, color=GREY_B), txt(label("cups_unit"), size=24, color=GREY_B))
        for u, en in zip(units, me):
            u.next_to(mu_m, RIGHT, buff=0.15).set_y(en.get_y())
        with self.say("9.4") as (tr, t):
            self.play(FadeOut(diag_box), FadeOut(off_box), FadeOut(diag_l), FadeOut(off_l), run_time=0.4)
            self.play(Indicate(me[0], color=LBLUE, scale_factor=1.3), FadeIn(units[0]), run_time=0.8)
            self.cue(tr, t, {"en": "and mean sales", "uz": "oʻrtacha savdo"})
            self.play(Indicate(me[1], color=LBLUE, scale_factor=1.3), FadeIn(units[1]), run_time=0.8)

        # spreads, the covariance's sign, and the correlation
        rows = VGroup(
            VGroup(txt(f"{label('temperature')}:", size=26, color=GREY_B),
                   MathTex(rf"\sqrt{{{dec(COV[0][0], 1)}}} = {dec(SD[0], 2)}", font_size=40)),
            VGroup(txt(f"{label('sales')}:", size=26, color=GREY_B),
                   MathTex(rf"\sqrt{{{dec(COV[1][1], 1)}}} = {dec(SD[1], 2)}", font_size=40)),
            VGroup(txt(f"{label('correlation')}:", size=26, color=GREY_B),
                   MathTex(rf"\frac{{{dec(COV[0][1], 1)}}}{{{dec(SD[0], 2)} \times {dec(SD[1], 2)}}} = {dec(CORR, 2)}",
                           font_size=40, color=HILITE)),
        )
        for r in rows:
            r.arrange(RIGHT, buff=0.3)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(VGroup(mu_cap, sig_cap), DOWN, buff=0.5)
        pos = MathTex(rf"\Sigma_{{12}} = {dec(COV[0][1], 1)} > 0", font_size=36, color=HILITE).next_to(sig_m, RIGHT, buff=0.3)
        with self.say("9.5") as (tr, t):
            self.play(FadeIn(rows[0]), Indicate(e[0], color=RLGREEN, scale_factor=1.2), run_time=0.8)
            self.play(FadeIn(rows[1]), Indicate(e[3], color=RLGREEN, scale_factor=1.2), run_time=0.8)
            self.cue(tr, t, {"en": "The covariance", "uz": "Kovariatsiya"})
            self.play(Indicate(VGroup(e[1], e[2]), color=HILITE, scale_factor=1.2), FadeIn(pos), run_time=0.9)
            self.cue(tr, t, {"en": "Dividing out both spreads", "uz": "Ikki tarqoqlikka"})
            self.play(FadeIn(rows[2], shift=UP * 0.2), run_time=0.9)
        self.clear_all()


class S09Ellipse(LectureScene):
    def construct(self):
        ax, labs, dots = scatter_scene(self)
        note = info(f"{N['n_days']} {label('simulated_days')}")
        e1, e2 = ellipse(ax, 1, HILITE, 3.5), ellipse(ax, 2, LBLUE, 3)
        t1 = MathTex(r"1\sigma", font_size=30, color=HILITE)
        t2 = MathTex(r"2\sigma", font_size=30, color=LBLUE)
        # tags at the upper-right end of each ellipse's long axis
        for tg, k in ((t1, 1), (t2, 2)):
            end = ax.c2p(MU[0] + k * np.sqrt(VALS[0]) * VECS[0][0], MU[1] + k * np.sqrt(VALS[0]) * VECS[0][1])
            tg.next_to(end, UR, buff=0.08)
            tg.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.04)
        self.add(ax, labs, dots, note)
        with self.say("9.6") as (tr, t):
            self.play(Create(e1), FadeIn(t1), run_time=1.0)
            self.play(Create(e2), FadeIn(t2), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(Indicate(VGroup(e1, e2), color=WHITE, scale_factor=1.04), run_time=0.9)

        # the odd day: ordinary in each column, strange as a pair
        star = odd_star(ax)
        p = ax.c2p(*ODD)
        to_x = DashedLine(p, [p[0], ax.c2p(0, 0)[1], 0], color=GREY_B, stroke_width=2)
        to_y = DashedLine(p, [ax.c2p(0, 0)[0], p[1], 0], color=GREY_B, stroke_width=2)
        zx = MathTex(rf"+{dec(ODD_Z[0], 1)}\sigma", font_size=32, color=HILITE)
        zx.next_to([p[0], ax.c2p(0, 0)[1], 0], UP, buff=0.12).shift(RIGHT * 0.45)
        zy = MathTex(rf"{dec(ODD_Z[1], 1)}\sigma", font_size=32, color=HILITE)
        zy.next_to([ax.c2p(0, 0)[0], p[1], 0], RIGHT, buff=0.15).shift(UP * 0.25)
        for z in (zx, zy):
            z.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.04)
        day = VGroup(MathTex(rf"{dec(ODD[0], 0)}^\circ\mathrm{{C}}", font_size=34),
                     tagged(dec(ODD[1], 0), label("cups_unit"), size=26)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        day.move_to([2.9, 1.6, 0], aligned_edge=LEFT)
        with self.say("9.7") as (tr, t):
            self.play(dots.animate.set_opacity(0.35), FadeIn(star, scale=1.8), FadeIn(day), run_time=0.9)
            self.cue(tr, t, {"en": "The temperature is only", "uz": "Harorat atigi"})
            self.play(Create(to_x), FadeIn(zx), run_time=0.7)
            self.play(Create(to_y), FadeIn(zy), run_time=0.7)

        pair = VGroup(txt(f"{label('as_a_pair')}:", size=28, weight=BOLD, color=HILITE),
                      MathTex(rf"{dec(MAHAL, 1)}\sigma", font_size=52, color=HILITE)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        pair.next_to(day, DOWN, buff=0.6).align_to(day, LEFT)
        ring = Circle(radius=0.35, color=RLRED, stroke_width=4).move_to(star)
        with self.say("9.8") as (tr, t):
            self.play(FadeIn(pair, shift=UP * 0.2), Indicate(e2, color=LBLUE, scale_factor=1.04), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(FadeOut(to_x), FadeOut(to_y), FadeOut(zx), FadeOut(zy), run_time=0.6)

        flag = txt(label("unusual"), size=28, weight=BOLD, color=RLRED)
        flag.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.05)
        flag.next_to(ring, DOWN, buff=0.12)
        with self.say("9.9") as (tr, t):
            self.play(Create(ring), FadeIn(flag), run_time=0.9)
            self.play(Indicate(e2, color=LBLUE, scale_factor=1.04), run_time=0.8)
        self.clear_all()


class S09HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"{label('temperature')}: {dec(ODD[0], 0)} °C",
                           f"μ = {dec(MU[0], 1)} °C,   σ = {dec(SD[0], 2)} °C",
                           "z = ?"])
        with self.say("9.10"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        ans = MathTex(rf"z = \frac{{{dec(ODD[0], 0)} - {dec(MU[0], 1)}}}{{{dec(SD[0], 2)}}}", r"\approx",
                      rf"{dec(ODD_Z[0], 1)}", font_size=60)
        ans[2].set_color(HILITE)
        ans.move_to(UP * 0.4)
        with self.say("9.11") as (tr, t):
            self.play(Write(ans[0]), run_time=1.0)
            self.cue(tr, t, {"en": "about one point one", "uz": "taxminan bir"})
            self.play(Write(ans[1:]), run_time=0.7)
        self.clear_all()

        # why a whole lecture on one curve?
        pts = [[(x - N["mu"]) / N["sigma"] * 1.1, y * N["sigma"] * 7.0 - 1.6, 0] for x, y in N["normal_curve"]]
        bell = VMobject(stroke_color=LBLUE, stroke_width=5).set_points_smoothly(pts)
        q = txt("?", size=96, weight=BOLD, color=HILITE).next_to(bell, UP, buff=0.3)
        with self.say("9.12"):
            self.play(Create(bell), run_time=1.0)
            self.play(FadeIn(q, scale=0.5), run_time=0.6)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S09Scatter", "S09Matrix", "S09Ellipse", "S09HandsOn"]
