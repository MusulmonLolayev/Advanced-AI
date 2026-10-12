"""Lecture 5, section 5 — mini-batch gradients: a gradient is a sample mean.

Every number on screen comes from N (capture_l05.py, unit-tested by test_l05.py): batch_small,
batch_big, batch_ratio, batch_noise_ratio, batch_task, batch_task_noise_ratio. The training examples,
the gradient arrows and the batch-normalization dots are illustrations (seeded, marked "tasvir uchun").
"""
import numpy as np

from lecture05_kit import *

B0, B1, B_TASK = N["batch_small"], N["batch_big"], N["batch_task"]
RATIO, NOISE = N["batch_ratio"], N["batch_noise_ratio"]
TASK_RATIO, TASK_NOISE = B_TASK // B0, N["batch_task_noise_ratio"]
FULL_C, BATCH_C = HILITE, LBLUE


def example_grid(rows=10, cols=18, gap=0.28, r=0.06):
    return VGroup(*[Dot([c * gap, -r_ * gap, 0], radius=r, color=GREY_D) for r_ in range(rows) for c in range(cols)])


def noisy_arrows(origin, target, spread, n, rng, color=BATCH_C, width=3):
    """n arrows from origin whose tips scatter around target by `spread` (an illustration of noise)."""
    out = VGroup()
    for _ in range(n):
        tip = np.array(target) + np.array([*rng.normal(0, spread, 2), 0])
        out.add(Arrow(origin, tip, buff=0, color=color, stroke_width=width, max_tip_length_to_length_ratio=0.12,
                      stroke_opacity=0.75))
    return out


class S05Batch(LectureScene):
    def construct(self):
        self.section_card(5)
        rng = np.random.default_rng(5)
        grid = example_grid().move_to(LEFT * 3.4 + DOWN * 0.3)
        g_lab = txt(label("all_training_examples"), size=24, color=GREY_B).next_to(grid, UP, buff=0.25)
        slow = txt(label("far_too_slow"), size=24, color=RLRED).next_to(grid, DOWN, buff=0.25)
        pick = sorted(rng.choice(len(grid), 8, replace=False))
        box = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.3, stroke_color=BATCH_C, stroke_width=3)
        box.move_to(RIGHT * 3.6 + DOWN * 0.3)
        b_lab = txt(label("mini_batch"), size=26, weight=BOLD, color=BATCH_C).next_to(box, UP, buff=0.2)
        targets = [box.get_center() + np.array([(i % 4 - 1.5) * 0.5, (0.25 if i < 4 else -0.25), 0]) for i in range(8)]
        note = info(label("illustration"))
        with self.say("5.1") as (tr, t):
            self.play(FadeIn(grid, lag_ratio=0.002), FadeIn(g_lab), FadeIn(note), run_time=0.9)
            self.cue(tr, t, {"en": "far too slow", "uz": "juda sekin"})
            self.play(FadeIn(slow), run_time=0.4)
            self.cue(tr, t, {"en": "a mini-batch", "uz": "mini-paket"})
            self.play(Create(box), FadeIn(b_lab), *[grid[i].animate.move_to(p).set_color(BATCH_C).scale(1.6)
                                                     for i, p in zip(pick, targets)], run_time=1.0)
        self.play(FadeOut(VGroup(grid, g_lab, slow, box, b_lab, note)), *[FadeOut(grid[i]) for i in pick], run_time=0.4)

        # a batch gradient is a sample mean: centred on the full gradient, noise sigma_g / sqrt(B)
        origin = LEFT * 4.6 + DOWN * 1.6
        target = origin + np.array([3.0, 2.2, 0])
        full = Arrow(origin, target, buff=0, color=FULL_C, stroke_width=7, max_tip_length_to_length_ratio=0.1)
        cloud = noisy_arrows(origin, target, 0.55, 14, rng)
        full_t = txt(label("full_gradient"), size=24, color=FULL_C).next_to(full.get_end(), RIGHT, buff=0.75)
        full_t.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.05)
        f1 = MathTex(r"\hat{g} = \frac{1}{B}\sum_{i=1}^{B} g_i", font_size=44)
        f2 = MathTex(r"E[\hat{g}] = g", font_size=44, color=FULL_C)
        f3 = MathTex(r"\mathrm{SE} = \frac{\sigma_g}{\sqrt{B}}", font_size=48, color=BATCH_C)
        fs = VGroup(f1, f2, f3).arrange(DOWN, buff=0.4).move_to(RIGHT * 3.2 + UP * 0.2)
        unb = txt(label("unbiased_centred_on_the_full_gradient"), size=24, color=FULL_C)
        if unb.width > 5.4:
            unb.scale_to_fit_width(5.4)
        unb.next_to(fs, DOWN, buff=0.3)
        if unb.get_right()[0] > 6.3:
            unb.shift(LEFT * (unb.get_right()[0] - 6.3))
        note2 = info(label("illustration"))
        with self.say("5.2") as (tr, t):
            self.play(LaggedStart(*[GrowArrow(a) for a in cloud], lag_ratio=0.06), FadeIn(note2), run_time=1.0)
            self.play(Write(f1), run_time=0.7)
            self.cue(tr, t, {"en": "So it is unbiased", "uz": "tarafkash emas"})
            self.play(GrowArrow(full), FadeIn(full_t), Write(f2), FadeIn(unb), run_time=0.8)
            self.cue(tr, t, {"en": "its noise", "uz": "shovqini"})
            self.play(Write(f3), run_time=0.7)

        why = txt(label("why_training_works"), size=34, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.35)
        why.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.1)
        with self.say("5.3"):
            self.play(FadeIn(why, shift=DOWN * 0.2), Indicate(f3, color=HILITE, scale_factor=1.08), run_time=0.9)
        self.clear_all()


class S05Noise(LectureScene):
    def construct(self):
        rng = np.random.default_rng(8)
        rule = VGroup(MathTex(r"B \times 4", font_size=48), MathTex(r"\Rightarrow", font_size=48),
                      txt(label("noise_halves"), size=32, color=HILITE)).arrange(RIGHT, buff=0.35)
        rule.to_edge(UP, buff=SAFE + 0.35)
        # the same full gradient, batch arrows scattered by sigma_g/sqrt(B): small batch vs big batch
        panels = VGroup()
        for b, spread in ((B0, 0.85), (B1, 0.85 / NOISE)):
            origin = np.array([0, -1.4, 0])
            target = origin + np.array([1.4, 2.4, 0])
            full = Arrow(origin, target, buff=0, color=FULL_C, stroke_width=6, max_tip_length_to_length_ratio=0.1)
            cloud = noisy_arrows(origin, target, spread, 16, rng, width=2.5)
            cap = MathTex(rf"B = {b}", font_size=40, color=BATCH_C).next_to(origin, DOWN, buff=0.35)
            panels.add(VGroup(cloud, full, cap))
        panels.arrange(RIGHT, buff=2.4).move_to(LEFT * 2.4 + DOWN * 0.5)
        data = VGroup(txt(label("data"), size=26, color=GREY_B), MathTex(rf"\times {RATIO}", font_size=40))
        data.arrange(RIGHT, buff=0.2)
        noise = VGroup(txt(label("noise"), size=26, color=GREY_B),
                       MathTex(rf"\div \sqrt{{{RATIO}}} \approx {NOISE:.1f}", font_size=40, color=HILITE)).arrange(RIGHT, buff=0.2)
        cmp = VGroup(data, noise).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 4.0 + DOWN * 0.3)
        note = info(label("illustration"))
        with self.say("5.4") as (tr, t):
            self.play(FadeIn(rule[0]), run_time=0.4)
            self.cue(tr, t, {"en": "halves the gradient noise", "uz": "ikki baravar kamaytiradi"})
            self.play(FadeIn(rule[1:]), run_time=0.5)
            self.cue(tr, t, {"en": "That is why", "uz": "Shuning uchun"})
            self.play(*[FadeIn(p[2]) for p in panels], *[GrowArrow(p[1]) for p in panels], FadeIn(note), run_time=0.6)
            self.play(*[LaggedStart(*[GrowArrow(a) for a in p[0]], lag_ratio=0.04) for p in panels], run_time=1.0)
            self.cue(tr, t, {"en": "thirty-two times", "uz": "oʻttiz ikki"})
            self.play(FadeIn(data), run_time=0.5)
            self.cue(tr, t, {"en": "five point seven", "uz": "besh butun"})
            self.play(FadeIn(noise), run_time=0.5)
        self.clear_all()

        # batch normalization: a mean estimated from a tiny batch is itself noisy (an illustration)
        bn = txt(label("batch_normalization"), size=32, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.35)
        rows = VGroup()
        for name, k in ((label("small_mini_batch"), 3), (label("large_mini_batch"), 40)):
            line = NumberLine(x_range=[-3, 3, 1], length=6.5, color=GREY_D, include_numbers=False)
            pts = rng.normal(0, 1, k)
            dots = VGroup(*[Dot(line.n2p(np.clip(v, -2.9, 2.9)), radius=0.07, color=GREY_B) for v in pts])
            est = Line(line.n2p(pts.mean()) + UP * 0.45, line.n2p(pts.mean()) + DOWN * 0.45, color=HILITE, stroke_width=5)
            true = DashedLine(line.n2p(0) + UP * 0.45, line.n2p(0) + DOWN * 0.45, color=GREY_B, stroke_width=2)
            lab = txt(name, size=26, color=GREY_B).next_to(line, LEFT, buff=0.4)
            rows.add(VGroup(lab, line, dots, true, est))
        rows.arrange(DOWN, buff=1.0, aligned_edge=RIGHT).move_to(DOWN * 0.2)
        legend = VGroup(VGroup(Line(LEFT * 0.25, RIGHT * 0.25, color=HILITE, stroke_width=5),
                               txt(label("estimated_mean"), size=22, color=HILITE)).arrange(RIGHT, buff=0.15),
                        VGroup(DashedLine(LEFT * 0.25, RIGHT * 0.25, color=GREY_B, stroke_width=2),
                               txt(label("true_mean"), size=22, color=GREY_B)).arrange(RIGHT, buff=0.15)).arrange(RIGHT, buff=0.8)
        legend.next_to(rows, DOWN, buff=0.45)
        other = txt(label("layer_and_group_normalization"), size=28, color=HILITE).next_to(legend, DOWN, buff=0.35)
        note2 = info(label("illustration"))
        with self.say("5.5") as (tr, t):
            self.play(FadeIn(bn), FadeIn(note2), run_time=0.5)
            self.play(FadeIn(rows[1][:3]), FadeIn(rows[0][:3]), run_time=0.7)
            self.play(*[Create(r[3]) for r in rows], *[Create(r[4]) for r in rows], FadeIn(legend), run_time=0.7)
            self.cue(tr, t, {"en": "those estimates are noisy", "uz": "bu baholar shovqinli"})
            self.play(Indicate(rows[0][4], color=RLRED, scale_factor=1.3), run_time=0.7)
            self.cue(tr, t, {"en": "layer and group", "uz": "qatlam va guruh"})
            self.play(FadeIn(other), run_time=0.5)
        self.clear_all()


class S05HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"B:  {B0} → {B_TASK}", label("how_many_times_less_noise_q")])
        card.to_edge(UP, buff=SAFE + 0.3)
        with self.say("5.6"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        ans = MathTex(rf"\sqrt{{\frac{{{B_TASK}}}{{{B0}}}}} = \sqrt{{{TASK_RATIO}}} = {TASK_NOISE:g}", font_size=60, color=HILITE)
        half = txt(label("noise_halves"), size=34, color=HILITE)
        VGroup(ans, half).arrange(DOWN, buff=0.5).move_to(UP * 0.3)
        with self.say("5.7") as (tr, t):
            self.play(Write(ans), run_time=1.0)
            self.cue(tr, t, {"en": "so the noise halves", "uz": "demak shovqin"})
            self.play(FadeIn(half), run_time=0.5)
        self.clear_all()

        # Part 0 closes on the question Part 1 answers
        grad = MathTex(r"\nabla_\theta \, ? ", font_size=96, color=HILITE).move_to(UP * 0.4)
        whose = txt(label("whose_gradient_q"), size=32, color=GREY_B).next_to(grad, DOWN, buff=0.4)
        nxt = txt(PARTS[1], size=34, weight=BOLD).to_edge(UP, buff=SAFE + 0.6)
        with self.say("5.8") as (tr, t):
            self.cue(tr, t, {"en": "But whose gradient", "uz": "Lekin bu gradient"})
            self.play(Write(grad), FadeIn(whose), run_time=0.9)
            self.cue(tr, t, {"en": "In part one", "uz": "Birinchi qismda"})
            self.play(FadeIn(nxt, shift=DOWN * 0.2), run_time=0.7)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S05Batch", "S05Noise", "S05HandsOn"]
