"""Lecture 4, section 10 — the Gaussian in AI, then the lecture close.

PCA uses the same 300 simulated days and their sample covariance (l04_numbers.json). The mixture
model's clusters, the network's weights and the diffusion pictures are illustrations, marked so.
"""
import numpy as np
from lecture04_kit import *
from lecture04_s09 import COV, MU, VALS, VECS, ellipse, matrix_tex, scatter_scene

SD0, BAND, WITHIN = N["init_sd"], N["init_band"], N["init_within"]
RULE = [N["rule"][k] for k in ("1", "2", "3")]


def curve(points, sx, sy, color=LBLUE, width=4):
    """A captured [x, y] curve, scaled to screen units and left at the origin."""
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly(
        [[x * sx, y * sy, 0] for x, y in points])


def bell(sd, width=4.0, height=1.6, color=LBLUE, n=161):
    """N(0, sd²) drawn over ±4 sd, for the weight pictures; the peak scaled to height."""
    xs = np.linspace(-4 * sd, 4 * sd, n)
    return VMobject(stroke_color=color, stroke_width=4).set_points_smoothly(
        [[x / (4 * sd) * width / 2, np.exp(-x * x / (2 * sd * sd)) * height, 0] for x in xs])


class S10PCA(LectureScene):
    def construct(self):
        self.section_card(10)
        ax, labs, dots = scatter_scene(self)
        dots.set_opacity(0.35)
        e2 = ellipse(ax, 2, LBLUE, 3)
        self.add(ax, labs, dots, e2)
        c = ax.c2p(*MU)
        arrows, tags = VGroup(), VGroup()
        for i, col in ((0, HILITE), (1, RLGREEN)):
            k = 2 * np.sqrt(VALS[i])
            a = ax.c2p(MU[0] - k * VECS[i][0], MU[1] - k * VECS[i][1])
            b = ax.c2p(MU[0] + k * VECS[i][0], MU[1] + k * VECS[i][1])
            arrows.add(DoubleArrow(a, b, buff=0, color=col, stroke_width=5, tip_length=0.2))
            tg = MathTex(rf"\lambda_{i + 1} = {dec(VALS[i], 1)}", font_size=30, color=col)
            tg.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.05)
            tags.add(tg)
        tags[0].next_to(arrows[0].get_end(), UR, buff=0.05)
        tags[1].next_to(arrows[1].get_start(), DOWN, buff=0.12)
        name = VGroup(txt(label("pca"), size=30, weight=BOLD, color=HILITE),
                      txt(label("principal_directions"), size=24, color=GREY_B)).arrange(DOWN, buff=0.15)
        if name.width > 4.4:                                  # the Uzbek name is long
            name.scale_to_fit_width(4.4)
        name.move_to([4.4, 2.4, 0])
        sig = matrix_tex([[dec(COV[0][0], 1), dec(COV[0][1], 1)], [dec(COV[1][0], 1), dec(COV[1][1], 1)]])
        diag = matrix_tex([[dec(VALS[0], 1), "0"], [r"0", dec(VALS[1], 1)]], color=WHITE)
        sig_g = VGroup(MathTex(r"\Sigma", font_size=40), sig).arrange(RIGHT, buff=0.15).scale(0.8)
        diag_g = VGroup(MathTex(r"\to", font_size=40), diag).arrange(RIGHT, buff=0.15).scale(0.8)
        mats = VGroup(sig_g, diag_g).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([4.5, -0.4, 0])
        de = diag.get_entries()
        de[0].set_color(HILITE)
        de[3].set_color(RLGREEN)
        with self.say("10.1") as (tr, t):
            self.play(GrowFromCenter(arrows[0]), FadeIn(tags[0]), FadeIn(name), run_time=1.0)
            self.play(GrowFromCenter(arrows[1]), FadeIn(tags[1]), run_time=0.8)
            self.cue(tr, t, {"en": "PCA diagonalizes", "uz": "U kovariatsiya matritsasini"})
            self.play(FadeIn(sig_g), run_time=0.6)
            self.play(FadeIn(diag_g, shift=DOWN * 0.2), run_time=0.8)
        self.clear_all()


class S10Mixture(LectureScene):
    def construct(self):
        rng = np.random.default_rng(3)                       # an illustration: three made-up clusters
        centres = [(-3.2, 0.2), (0.4, -1.1), (3.0, 0.5)]
        shapes = [(1.0, 0.45, 25), (1.2, 0.55, -35), (0.8, 0.5, 70)]
        colors = [LBLUE, RLGREEN, HILITE]
        pts, ells = VGroup(), VGroup()
        for (cx, cy), (a, b, ang), col in zip(centres, shapes, colors):
            th = np.deg2rad(ang)
            R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
            for z in rng.normal(size=(45, 2)):
                x, y = R @ (z * [a, b]) + [cx, cy]
                pts.add(Dot([x, y, 0], radius=0.045, color=col, fill_opacity=0.8))
            ells.add(Ellipse(width=4 * a, height=4 * b, color=col, stroke_width=3).rotate(th).move_to([cx, cy, 0]))
        head = VGroup(txt(label("clustering"), size=30, weight=BOLD, color=LBLUE),
                      txt(label("gaussian_mixture_model"), size=26, color=GREY_B)).arrange(DOWN, buff=0.15)
        head.to_edge(UP, buff=SAFE + 0.3)
        note = info(label("illustration"))
        with self.say("10.2") as (tr, t):
            self.play(FadeIn(head), FadeIn(note), LaggedStart(*[FadeIn(d, scale=0.5) for d in pts], lag_ratio=0.01),
                      run_time=1.4)
            self.cue(tr, t, {"en": "one per cluster", "uz": "har bir klasterga"})
            self.play(LaggedStart(*[Create(e) for e in ells], lag_ratio=0.4), run_time=1.2)
        self.clear_all()


class S10Weights(LectureScene):
    def construct(self):
        # starting a network: every weight drawn from N(0, σ²), σ set by the layer width
        rng = np.random.default_rng(7)                       # an illustration: the drawn weights
        layers = [3, 5, 5, 2]
        xs = [-5.6, -4.0, -2.4, -0.8]
        nodes = [VGroup(*[Circle(radius=0.16, color=GREY_B, stroke_width=2.5, fill_color=BLACK, fill_opacity=1)
                          .move_to([x, (k - (n - 1) / 2) * 0.75 - 0.3, 0]) for k in range(n)]) for x, n in zip(xs, layers)]
        edges = VGroup()
        for a, b in zip(nodes, nodes[1:]):
            for p in a:
                for q in b:
                    w = rng.normal(0, 1)
                    edges.add(Line(p.get_center(), q.get_center(), stroke_width=0.6 + 2.4 * min(abs(w), 2) / 2,
                                   color=LBLUE if w > 0 else RLRED, stroke_opacity=0.75))
        net = VGroup(edges, *nodes)
        net_head = txt(label("starting_a_network"), size=30, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        b = bell(1.0, width=4.2, height=1.8).move_to([3.6, 0.2, 0])
        b_floor = Line(b.get_corner(DL), b.get_corner(DR), color=GREY_B, stroke_width=2)
        dist = MathTex(r"w \sim \mathcal{N}(0,\ \sigma^2)", font_size=44).next_to(b, UP, buff=0.4)
        w_lab = txt(label("weights"), size=24, color=GREY_B).next_to(b_floor, DOWN, buff=0.2)
        rule = VGroup(MathTex(r"\sigma \propto \tfrac{1}{\sqrt{n}}", font_size=44, color=HILITE),
                      tagged("n", f"= {label('layer_width')}", size=24, color=GREY_B)).arrange(RIGHT, buff=0.3)
        rule.next_to(w_lab, DOWN, buff=0.45)
        note = info(label("illustration"))
        with self.say("10.3") as (tr, t):
            self.play(FadeIn(net_head), FadeIn(VGroup(*nodes)), FadeIn(note), run_time=0.8)
            self.play(Create(b_floor), Create(b), Write(dist), FadeIn(w_lab), run_time=1.0)
            self.play(LaggedStart(*[Create(e) for e in edges], lag_ratio=0.01), run_time=1.0)
            self.cue(tr, t, {"en": "its sigma set by", "uz": "sigmasi qatlam"})
            self.play(FadeIn(rule, shift=UP * 0.2), run_time=0.7)
        self.clear_all()

        # regularization: a Gaussian belief about the weights gives the L2 penalty
        prior = MathTex(r"w \sim \mathcal{N}(0,\ \tau^2)", font_size=50).move_to(LEFT * 3.3 + UP * 0.6)
        arrow = Arrow(LEFT * 1.3 + UP * 0.6, RIGHT * 0.6 + UP * 0.6, buff=0, color=GREY_B, stroke_width=4)
        pen = MathTex(r"L(w)", r"+", r"\lambda \lVert w \rVert^2", font_size=50).move_to(RIGHT * 3.3 + UP * 0.6)
        pen[2].set_color(HILITE)
        reg_head = txt(label("regularization"), size=30, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        pen_lab = txt(label("l2_penalty"), size=26, color=HILITE).next_to(pen[2], DOWN, buff=0.3)
        later = txt(label("lecture_6"), size=26, color=GREY_B).move_to(DOWN * 1.6)
        pb = bell(1.0, width=2.6, height=1.0).next_to(prior, DOWN, buff=0.4)
        with self.say("10.4") as (tr, t):
            self.play(FadeIn(reg_head), Write(prior), Create(pb), run_time=1.0)
            self.cue(tr, t, {"en": "the most probable weights", "uz": "eng ehtimolli vaznlar"})
            self.play(GrowArrow(arrow), Write(pen), run_time=0.9)
            self.play(FadeIn(pen_lab), run_time=0.5)
            self.cue(tr, t, {"en": "We derive it", "uz": "Buni oltinchi"})
            self.play(FadeIn(later, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        # generative models: a VAE's latent Gaussian; diffusion adds normal noise step by step
        enc = Polygon([-0.7, 0.7, 0], [0.7, 0.35, 0], [0.7, -0.35, 0], [-0.7, -0.7, 0], color=LBLUE, stroke_width=3)
        dec_ = Polygon([-0.7, 0.35, 0], [0.7, 0.7, 0], [0.7, -0.7, 0], [-0.7, -0.35, 0], color=LBLUE, stroke_width=3)
        z = MathTex(r"z \sim \mathcal{N}(\boldsymbol{\mu},\ \Sigma)", font_size=36, color=HILITE)
        zbox = SurroundingRectangle(z, buff=0.18, color=HILITE, stroke_width=3, corner_radius=0.1)
        vae = VGroup(enc, VGroup(zbox, z), dec_).arrange(RIGHT, buff=0.6)
        vae_arrows = VGroup(Arrow(enc.get_right(), zbox.get_left(), buff=0.08, color=GREY_B, stroke_width=3),
                            Arrow(zbox.get_right(), dec_.get_left(), buff=0.08, color=GREY_B, stroke_width=3))
        vae_g = VGroup(vae, vae_arrows)
        vae_lab = txt(label("variational_autoencoder"), size=26, weight=BOLD, color=LBLUE)
        lat_lab = txt(label("latent_variable"), size=22, color=HILITE)
        vae_all = VGroup(vae_lab, vae_g).arrange(DOWN, buff=0.3).move_to(UP * 1.65)
        lat_lab.next_to(zbox, DOWN, buff=0.15)

        rng = np.random.default_rng(11)                      # an illustration: a picture dissolving into noise
        base = np.array([[1.0 if (i - 2.5) ** 2 + (j - 2.5) ** 2 < 5.5 and (i - 2.5) ** 2 + (j - 2.5) ** 2 > 1.5 else 0.0
                          for j in range(6)] for i in range(6)])
        tiles = VGroup()
        for s in (0.0, 0.25, 0.5, 1.0):
            img = np.clip(base * (1 - s) + rng.normal(0, s * 0.5, size=base.shape) + s * 0.5 * 0, 0, 1)
            g = VGroup(*[Square(0.2, stroke_width=0, fill_color=interpolate_color(BLACK, WHITE, float(v)),
                                fill_opacity=1).move_to([j * 0.2, -i * 0.2, 0]) for i in range(6) for j in range(6)
                         for v in [img[i, j]]])
            tiles.add(VGroup(SurroundingRectangle(g, buff=0.03, color=GREY_D, stroke_width=1.5), g))
        tiles.arrange(RIGHT, buff=1.0)
        steps = VGroup(*[MathTex(r"+\,\mathcal{N}(0,\sigma^2)", font_size=22, color=GREY_B).move_to(
            (tiles[i].get_right() + tiles[i + 1].get_left()) / 2 + UP * 0.25) for i in range(3)])
        step_arrows = VGroup(*[Arrow(tiles[i].get_right(), tiles[i + 1].get_left(), buff=0.08, color=GREY_B,
                                     stroke_width=2.5, max_tip_length_to_length_ratio=0.2) for i in range(3)])
        dif_lab = txt(label("diffusion_model"), size=26, weight=BOLD, color=LBLUE)
        dif_all = VGroup(dif_lab, VGroup(tiles, steps, step_arrows)).arrange(DOWN, buff=0.3).move_to(DOWN * 1.75)
        steps.set_y(tiles.get_bottom()[1] - 0.25)                # under the arrows, clear of the title
        gen_head = txt(label("generative_models"), size=30, weight=BOLD, color=GREY_B).to_edge(UP, buff=SAFE + 0.15)
        note = info(label("illustration"))
        with self.say("10.5") as (tr, t):
            self.play(FadeIn(gen_head), FadeIn(vae_lab), Create(enc), Create(dec_), run_time=0.8)
            self.play(GrowArrow(vae_arrows[0]), FadeIn(VGroup(zbox, z)), GrowArrow(vae_arrows[1]), FadeIn(lat_lab),
                      run_time=1.0)
            self.cue(tr, t, {"en": "and a diffusion model", "uz": "diffuziya modeli esa"})
            self.play(FadeIn(dif_lab), FadeIn(tiles[0]), FadeIn(note), run_time=0.6)
            for i in range(3):
                self.play(GrowArrow(step_arrows[i]), FadeIn(steps[i]), FadeIn(tiles[i + 1]), run_time=0.45)
        self.clear_all()


class S10HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"w ~ N(0, {dec(SD0, 1)}²)",
                           f"P(−{dec(BAND, 1)} < w < {dec(BAND, 1)}) = ?"])
        with self.say("10.6"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        # the weights' bell, with ±2σ shaded
        ax = Axes(x_range=[-4 * SD0, 4 * SD0, SD0], y_range=[0, 4.5, 1], x_length=8.0, y_length=3.4, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2},
                  x_axis_config={"include_numbers": True, "font_size": 22, "decimal_number_config": {"num_decimal_places": 1}},
                  y_axis_config={"include_ticks": False}).move_to(DOWN * 0.6)
        ax.y_axis.set_opacity(0)

        def pdf(x):
            return np.exp(-x * x / (2 * SD0 * SD0)) / (SD0 * np.sqrt(2 * np.pi))

        g = ax.plot(pdf, x_range=[-4 * SD0, 4 * SD0], color=LBLUE, stroke_width=4)
        area = ax.get_area(g, x_range=[-BAND, BAND], color=HILITE, opacity=0.45)
        share = MathTex(rf"\approx {round(100 * WITHIN)}\%", font_size=56, color=HILITE).move_to(ax.c2p(0, 1.4))
        two = MathTex(r"\pm 2\sigma", font_size=40, color=HILITE).next_to(ax.c2p(0, 4.1), UP, buff=0.1)
        rule = MathTex(rf"{round(100 * RULE[0])}\%", r"\ \cdot\ ", rf"{round(100 * RULE[1])}\%", r"\ \cdot\ ",
                       rf"{dec(100 * RULE[2], 1)}\%", font_size=44).to_edge(UP, buff=SAFE + 0.35)
        rule[2].set_color(HILITE)
        with self.say("10.7") as (tr, t):
            self.play(Create(ax), Create(g), run_time=0.9)
            self.play(FadeIn(area), FadeIn(two), run_time=0.6)
            self.play(Write(share), run_time=0.6)
            self.cue(tr, t, {"en": "The sixty-eight", "uz": "Oltmish sakkiz"})
            self.play(FadeIn(rule, shift=DOWN * 0.2), run_time=0.7)
        self.clear_all()


class S10Summary(LectureScene):
    def construct(self):
        head = self.heading(label("lecture_4_summary"), color=LBLUE)

        def mini(points, sx, sy, color=LBLUE):
            return curve(points, sx, sy, color=color, width=3)

        def mini_density():
            c = mini(N["pdf_curve"], 0.06, 1.6)
            fill = VGroup(*[Rectangle(width=0.05, height=max(1.6 * y, 1e-3), stroke_width=0, fill_color=HILITE,
                                      fill_opacity=0.5).move_to([x * 0.06, 0.8 * y, 0])
                            for x, y in N["pdf_curve"][:45:3]])
            return VGroup(fill, c)

        def mini_cdf():
            pts, run = [], 0.0
            for (x0, y0), (x1, y1) in zip(N["pdf_curve"], N["pdf_curve"][1:]):
                run += (x1 - x0) * (y0 + y1) / 2
                pts.append([x1, run])
            return mini(pts, 0.06, 0.6, HILITE)

        def mini_flat_exp():
            flat = Line([0, 0.25, 0], [0.32, 0.25, 0], color=LBLUE, stroke_width=3)
            return VGroup(flat, mini(N["pdf_curve"], 0.03, 1.2).shift(RIGHT * 0.42))

        def mini_beta():
            return VGroup(mini(N["beta"]["first"]["curve"], 0.7, 0.06),
                          mini(N["beta"]["more"]["curve"], 0.7, 0.06, HILITE))

        def mini_bell():
            return mini(N["normal_curve"], 0.08, 2.0)

        def mini_ellipse():
            return Ellipse(width=0.7, height=0.3, color=LBLUE, stroke_width=3).rotate(PI / 6)

        def rows_of(items):
            rows = VGroup()
            for icon, text in items:
                ic = icon()
                if ic.height > 0.5:
                    ic.scale_to_fit_height(0.5)
                if ic.width > 0.7:
                    ic.scale_to_fit_width(0.7)
                slot = VGroup(Square(0.75, stroke_width=0), ic)
                ic.move_to(slot[0])
                rows.add(VGroup(slot, txt(text, size=28)).arrange(RIGHT, buff=0.35))
            rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT).next_to(head, DOWN, buff=0.6)
            if rows.width > 12.4:
                rows.scale_to_fit_width(12.4)
            return rows.set_x(0)

        part0 = rows_of([(mini_density, label("summary_density")), (mini_cdf, label("summary_cdf"))])
        with self.say("10.8") as (tr, t):
            self.play(FadeIn(head), run_time=0.6)
            self.cue(tr, t, {"en": "A continuous variable", "uz": "Uzluksiz miqdorda"})
            self.play(FadeIn(part0[0], shift=RIGHT * 0.3), run_time=0.6)
            self.cue(tr, t, {"en": "The CDF turns", "uz": "Taqsimot funksiyasi har"})
            self.play(FadeIn(part0[1], shift=RIGHT * 0.3), run_time=0.6)
        self.play(FadeOut(part0), run_time=0.4)

        part1 = rows_of([(mini_flat_exp, label("summary_uniform_exponential")),
                         (mini_beta, label("summary_beta")),
                         (mini_bell, label("summary_normal_z")),
                         (mini_ellipse, label("summary_multivariate"))])
        with self.say("10.9") as (tr, t):
            self.play(FadeIn(part1[0], shift=RIGHT * 0.3), run_time=0.6)
            for r, cue in zip(part1[1:], ({"en": "Beta for a belief", "uz": "Beta — bitta"},
                                          {"en": "The normal distribution follows", "uz": "Normal taqsimot oltmish"},
                                          {"en": "In several dimensions", "uz": "Koʻp oʻlchovda"})):
                self.cue(tr, t, cue)
                self.play(FadeIn(r, shift=RIGHT * 0.3), run_time=0.6)
        self.clear_all()

        end = VGroup(txt(label("lecture_4"), size=56, weight=BOLD, color=RLBLUE),
                     txt(label("the_end"), size=34, color=GREY_B)).arrange(DOWN, buff=0.3).move_to(UP * 0.4)
        title5 = txt(label("lecture_5_the_clt_and_maximum_likelihood"), size=40, weight=BOLD, color=LBLUE)
        if title5.width > 12.4:                               # the Uzbek title is long: shrink only the title
            title5.scale_to_fit_width(12.4)
        nxt = VGroup(txt(label("next"), size=28, color=GREY_B), title5,
                     MathTex(r"\bar{x} \;\approx\; \mathcal{N}\!\left(\mu,\ \tfrac{\sigma^2}{n}\right)", font_size=60,
                             color=HILITE)).arrange(DOWN, buff=0.4)
        with self.say("10.10") as (tr, t):
            self.play(FadeIn(end, shift=UP * 0.3), run_time=0.9)
            self.cue(tr, t, {"en": "In the next lecture", "uz": "Keyingi maʼruzada"})
            self.play(FadeOut(end), FadeIn(nxt, shift=UP * 0.3), run_time=1.0)
        self.play(FadeOut(nxt), run_time=0.6)
        self.play(FadeIn(brand_outro()), run_time=1.0)
        self.wait(2.0)
        self.clear_all(run_time=0.6)


SCENES = ["S10PCA", "S10Mixture", "S10Weights", "S10HandsOn", "S10Summary"]
