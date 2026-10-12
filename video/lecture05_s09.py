"""Lecture 5, section 9 — which bell curve fits the 40 espresso shots?

The shots are the figure script's own (same generator and seed, captured in l05_numbers.json); the
three curves are drawn from the captured mu and sigma of the MLE fit and the two candidates, and
their log-likelihoods are the captured ones. The gradient-descent picture climbs the same shots'
log-likelihood in mu (no number shown on it).
"""
import numpy as np
from lecture05_kit import *

SHOTS = np.array(N["shots"])
FITS = N["fits"]
COLORS = {"mle": HILITE, "low": RLRED, "wide": RLGREEN}
NAMES = {"mle": label("mle_fit"), "low": label("mle_centre_too_low"), "wide": label("mle_too_wide")}
X0, X1 = 24.0, 36.0


def shot_axes():
    ax = Axes(x_range=[X0, X1, 2], y_range=[0, 0.4, 0.1], x_length=7.4, y_length=4.0, tips=False,
              axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 22},
              x_axis_config={"include_numbers": True}, y_axis_config={"include_numbers": False})
    ax.move_to(LEFT * 2.4 + DOWN * 0.3)
    xl = txt(label("espresso_ml"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.45)
    yl = txt(label("density"), size=22, color=GREY_B).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
    return ax, VGroup(xl, yl)


def histogram(ax):
    counts, edges = np.histogram(SHOTS, bins=10)                   # the figure's own bins
    w = edges[1] - edges[0]
    dens = counts / (len(SHOTS) * w)
    return VGroup(*[Rectangle(width=ax.c2p(edges[i + 1], 0)[0] - ax.c2p(edges[i], 0)[0],
                              height=max(ax.c2p(0, d)[1] - ax.c2p(0, 0)[1], 1e-3),
                              stroke_color=BLACK, stroke_width=1, fill_color=GREY_D, fill_opacity=0.9)
                    .move_to(ax.c2p((edges[i] + edges[i + 1]) / 2, d / 2)) for i, d in enumerate(dens)])


def ticks(ax):
    return VGroup(*[Line(ax.c2p(x, 0) + DOWN * 0.02, ax.c2p(x, 0) + UP * 0.18, stroke_width=2, color=LBLUE)
                    for x in SHOTS])


def bell(ax, mu, sd, color):
    xs = np.linspace(X0, X1, 241)
    ys = np.exp(-(xs - mu) ** 2 / (2 * sd * sd)) / (sd * np.sqrt(2 * np.pi))
    return VMobject(stroke_color=color, stroke_width=4).set_points_smoothly([ax.c2p(x, y) for x, y in zip(xs, ys)])


def score_row(key):
    f = FITS[key]
    params = MathTex(rf"\mu = {dec(f['mu'], 2)},\ \sigma = {dec(f['sigma'], 2)}", font_size=26, color=GREY_B)
    score = MathTex(rf"\ell = {dec(f['loglik'], 1)}", font_size=34, color=COLORS[key])
    name = txt(NAMES[key], size=22, color=COLORS[key])
    if name.width > 4.6:
        name.scale_to_fit_width(4.6)
    return VGroup(name, VGroup(score, params).arrange(RIGHT, buff=0.3)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)


class S09Shots(LectureScene):
    def construct(self):
        self.section_card(9)
        ax, labs = shot_axes()
        hist, tk = histogram(ax), ticks(ax)
        count = tagged(N["shot_n"], label("mle_espresso_shots"), size=28, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        with self.say("9.1") as (tr, t):
            self.play(FadeIn(count), Create(ax), FadeIn(labs), run_time=0.8)
            self.cue(tr, t, {"en": "The ticks", "uz": "Oʻqdagi chiziqchalar"})
            self.play(LaggedStart(*[Create(x) for x in tk], lag_ratio=0.03), run_time=1.0)
            self.play(LaggedStart(*[GrowFromEdge(r, DOWN) for r in hist], lag_ratio=0.05), run_time=0.8)

        curve = bell(ax, FITS["mle"]["mu"], FITS["mle"]["sigma"], HILITE)
        row = score_row("mle").move_to([4.4, 1.8, 0])
        with self.say("9.2") as (tr, t):
            self.play(Create(curve), FadeIn(row[0]), run_time=1.0)
            self.play(FadeIn(row[1][1]), run_time=0.6)
            self.cue(tr, t, {"en": "The log-likelihood", "uz": "Logarifmik haqiqatga"})
            self.play(FadeIn(row[1][0], shift=LEFT * 0.2), run_time=0.6)
        self.wait(0.1)


class S09Candidates(LectureScene):
    def construct(self):
        ax, labs = shot_axes()
        hist, tk = histogram(ax), ticks(ax)
        curves = {k: bell(ax, FITS[k]["mu"], FITS[k]["sigma"], COLORS[k]) for k in FITS}
        rows = {k: score_row(k) for k in FITS}
        board = VGroup(rows["mle"], rows["low"], rows["wide"]).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        board.move_to([4.4, 0.6, 0])
        count = tagged(N["shot_n"], label("mle_espresso_shots"), size=28, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        self.add(count, ax, labs, hist, tk, curves["mle"], rows["mle"])
        with self.say("9.3"):
            self.play(Create(curves["low"]), FadeIn(rows["low"], shift=LEFT * 0.2), run_time=1.2)
        with self.say("9.4"):
            self.play(Create(curves["wide"]), FadeIn(rows["wide"], shift=LEFT * 0.2), run_time=1.2)

        lead = tagged(f"+{dec(N['fit_margin'], 1)}", label("mle_ahead"), size=28, color=HILITE)
        lead.next_to(board, DOWN, buff=0.45).align_to(board, LEFT)
        ring = SurroundingRectangle(rows["mle"], buff=0.12, color=HILITE, stroke_width=3)
        with self.say("9.5") as (tr, t):
            self.play(curves["mle"].animate.set_stroke(width=7), run_time=0.6)
            self.cue(tr, t, {"en": "the best curve leads", "uz": "eng yaxshi egri chiziq"})
            self.play(Create(ring), FadeIn(lead, shift=UP * 0.2), run_time=0.8)

        search = VGroup(txt(label("mle_search_over_curves"), size=30, weight=BOLD, color=LBLUE),
                        txt(label("mle_every_candidate_gets_a_score"), size=24, color=GREY_B)).arrange(DOWN, buff=0.15)
        if search.width > 6.4:
            search.scale_to_fit_width(6.4)
        search.move_to(count)
        win = txt(label("mle_the_winner"), size=26, weight=BOLD, color=HILITE).next_to(ring, UP, buff=0.12)
        with self.say("9.6") as (tr, t):
            self.play(FadeOut(count), FadeIn(search), run_time=0.7)
            self.cue(tr, t, {"en": "and the winner", "uz": "va gʻolib"})
            self.play(FadeIn(win, shift=DOWN * 0.2), Indicate(rows["mle"], color=HILITE, scale_factor=1.04), run_time=0.8)
        self.clear_all()


class S09Descent(LectureScene):
    def construct(self):
        # the shots' log-likelihood as a function of mu, at the fitted sigma; gradient ascent climbs it
        sd = FITS["mle"]["sigma"]
        n, xbar = len(SHOTS), SHOTS.mean()

        def ll(m):
            return float(-n / 2 * np.log(2 * np.pi * sd * sd) - ((SHOTS - m) ** 2).sum() / (2 * sd * sd))

        lo = min(ll(26.0), ll(34.0))                                 # the curve's lowest point sits on the axis
        ax = Axes(x_range=[26, 34, 1], y_range=[0, ll(xbar) - lo + 10, 50], x_length=8.0, y_length=3.8, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 22},
                  x_axis_config={"include_numbers": True}, y_axis_config={"include_ticks": False}).move_to(DOWN * 0.5)
        xs = np.linspace(26, 34, 161)
        c = VMobject(stroke_color=LBLUE, stroke_width=4).set_points_smoothly([ax.c2p(m, ll(m) - lo) for m in xs])
        xl = MathTex(r"\mu", font_size=36, color=GREY_B).next_to(ax.x_axis, RIGHT, buff=0.2)
        yl = txt(label("mle_log_likelihood"), size=22, color=GREY_B).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        steps, m = [], 27.0
        for _ in range(6):                                            # each step goes half-way to the peak
            steps.append(m)
            m = m + 0.5 * sd * sd / n * ((SHOTS - m).sum() / (sd * sd))
        dots = [Dot(ax.c2p(s, ll(s) - lo), radius=0.09, color=HILITE) for s in steps]
        head = VGroup(txt(label("mle_gradient_descent"), size=34, weight=BOLD, color=LBLUE),
                      txt(label("mle_step_by_step"), size=24, color=GREY_B)).arrange(DOWN, buff=0.12)
        head.to_edge(UP, buff=SAFE + 0.3)
        rule = MathTex(r"\theta \;\leftarrow\; \theta + \eta\, \nabla_\theta\, \ell", font_size=40, color=HILITE)
        rule.next_to(head, DOWN, buff=0.25).align_to(ax, RIGHT)        # clear of the axis title on the left
        with self.say("9.7"):
            self.play(FadeIn(head), Create(ax), FadeIn(xl), FadeIn(yl), Create(c), run_time=1.0)
            self.play(FadeIn(rule), FadeIn(dots[0]), run_time=0.5)
            for a, b in zip(dots, dots[1:]):
                self.play(FadeIn(b), Create(Arrow(a.get_center(), b.get_center(), buff=0.1, color=HILITE,
                                                  stroke_width=3, max_tip_length_to_length_ratio=0.3)), run_time=0.35)
        self.clear_all()


class S09HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"σ̂ = {dec(N['sigma_mle'], 2)}   (÷ n)",
                           f"÷ (n − 1):   σ  {label('mle_larger_or_smaller_q')}"])
        with self.say("9.8"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        cmp_ = MathTex(rf"s = {dec(N['s_lecture1'], 2)}", r"\;>\;", rf"\hat{{\sigma}} = {dec(N['sigma_mle'], 2)}",
                       font_size=64).move_to(UP * 0.6)
        cmp_[0].set_color(HILITE)
        div = VGroup(MathTex(r"\frac{1}{n-1}", font_size=48, color=HILITE), MathTex(r">", font_size=48),
                     MathTex(r"\frac{1}{n}", font_size=48)).arrange(RIGHT, buff=0.3).next_to(cmp_, DOWN, buff=0.6)
        big = txt(label("mle_larger"), size=30, weight=BOLD, color=HILITE).next_to(cmp_[0], UP, buff=0.3)
        with self.say("9.9") as (tr, t):
            self.play(Write(cmp_), FadeIn(big), run_time=1.0)
            self.cue(tr, t, {"en": "Dividing by a smaller", "uz": "Kichikroq songa"})
            self.play(FadeIn(div, shift=UP * 0.2), run_time=0.7)
        self.play(FadeOut(VGroup(cmp_, div, big)), run_time=0.4)

        # a small network, and the question of its loss
        layers = [3, 4, 2]
        nodes = VGroup(*[VGroup(*[Circle(radius=0.16, color=GREY_B, stroke_width=2) for _ in range(k)])
                         .arrange(DOWN, buff=0.35) for k in layers]).arrange(RIGHT, buff=1.4).move_to(DOWN * 0.4)
        edges = VGroup(*[Line(a.get_right(), b.get_left(), stroke_width=1.2, color=GREY_D)
                         for l1, l2 in zip(nodes, nodes[1:]) for a in l1 for b in l2])
        name = txt(label("mle_neural_network"), size=24, color=GREY_B).next_to(nodes, DOWN, buff=0.35)
        q = txt(label("mle_which_loss_q"), size=34, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.6)
        if q.width > 12.0:
            q.scale_to_fit_width(12.0)
        with self.say("9.10"):
            self.play(Create(edges), FadeIn(nodes), FadeIn(name), run_time=0.9)
            self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.6)
        self.clear_all()


SCENES = ["S09Shots", "S09Candidates", "S09Descent", "S09HandsOn"]
