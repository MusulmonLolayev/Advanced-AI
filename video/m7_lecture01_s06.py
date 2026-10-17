"""Module 7, Lecture 1, section 6 — the scratchpad is the context window, so input tokens grow quadratically.
Numbers: N (m7/capture_l01.py): turn_1..3, billed_3/10/20, new_only_3/10/20, ratio_20_10."""
from m7_lecture01_kit import *

S = N["turn_1"]
A = N["turn_2"] - N["turn_1"]
STEPS = (3, 10, 20)


class S06Cost(Scene7):
    def construct(self):
        self.section_card(6)
        head = self.heading(label("m7_sum_context"), color=HILITE)
        rows = VGroup()
        for k in range(1, 5):
            parts = [Rectangle(width=1.6, height=0.42, stroke_width=0, fill_color=RLBLUE, fill_opacity=0.9)]
            parts += [Rectangle(width=0.7, height=0.42, stroke_width=0, fill_color=GOOD if j == k - 1 else GREY_D,
                                fill_opacity=0.9) for j in range(k - 1)]
            rows.add(VGroup(*parts).arrange(RIGHT, buff=0.05))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to(DOWN * 0.4)
        with self.say("6.46") as (tr, t):
            self.play(FadeIn(head), run_time=0.5)
            for r in rows:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.clear_all()

        unit = 4.2 / S                                              # scene units per token
        fixed = Rectangle(width=S * unit, height=0.6, stroke_width=0, fill_color=RLBLUE, fill_opacity=0.9)
        step = Rectangle(width=A * unit, height=0.6, stroke_width=0, fill_color=GOOD, fill_opacity=0.9)
        VGroup(fixed, step).arrange(RIGHT, buff=0.08).move_to(UP * 1.5)
        lf = VGroup(txt(label("m7_fixed_part"), size=24), MathTex(f"S = {S:,}".replace(",", "{,}"), font_size=36))
        lf.arrange(DOWN, buff=0.12).next_to(fixed, DOWN, buff=0.25)
        ls = VGroup(txt(label("m7_each_step"), size=24), MathTex(f"a = {A}", font_size=36))
        ls.arrange(DOWN, buff=0.12).next_to(step, DOWN, buff=0.25)
        with self.say("6.47") as (tr, t):
            self.play(FadeIn(fixed), FadeIn(lf), run_time=0.6)
            self.cue(tr, t, {"uz": "Har bir qadam", "en": "Each step adds"})
            self.play(FadeIn(step), FadeIn(ls), run_time=0.6)
        self.clear_all()

        bars = VGroup()
        for k, key in enumerate(("turn_1", "turn_2", "turn_3"), 1):
            r = Rectangle(width=N[key] * 4.2 / S, height=0.55, stroke_width=0, fill_color=RLBLUE, fill_opacity=0.9)
            name = VGroup(txt(label("m7_turn"), size=22, color=GREY_B), MathTex(str(k), font_size=32)).arrange(RIGHT, buff=0.12)
            num = MathTex(f"{N[key]:,}".replace(",", "{,}"), font_size=34)
            bars.add(VGroup(name, r, num))
        for b in bars:
            b[1].next_to(b[0], RIGHT, buff=0.35)
            b[2].next_to(b[1], RIGHT, buff=0.25)
        bars.arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(LEFT * 0.8)
        with self.say("6.48") as (tr, t):
            for b in bars:
                self.play(FadeIn(b, shift=RIGHT * 0.2), run_time=0.5)
        self.clear_all()

        vmax = N["billed_20"]
        h = 4.6 / vmax
        cols = VGroup()
        for n in STEPS:
            fixed_part = n * S
            reread = N[f"billed_{n}"] - fixed_part
            lo = Rectangle(width=1.3, height=fixed_part * h, stroke_width=0, fill_color=RLBLUE, fill_opacity=0.9)
            hi = Rectangle(width=1.3, height=max(reread * h, 1e-3), stroke_width=0, fill_color=RLORANGE, fill_opacity=0.9)
            hi.next_to(lo, UP, buff=0)
            num = MathTex(f"{N[f'billed_{n}']:,}".replace(",", "{,}"), font_size=32).next_to(hi, UP, buff=0.12)
            name = tagged(n, label("m7_steps"), size=24).next_to(lo, DOWN, buff=0.15)
            cols.add(VGroup(lo, hi, num, name))
        cols.arrange(RIGHT, buff=1.6, aligned_edge=DOWN).move_to(DOWN * 0.2 + LEFT * 1.4)
        key_fixed = VGroup(Square(0.25, fill_color=RLBLUE, fill_opacity=0.9, stroke_width=0),
                           txt(label("m7_fixed_part"), size=22)).arrange(RIGHT, buff=0.15)
        key_re = VGroup(Square(0.25, fill_color=RLORANGE, fill_opacity=0.9, stroke_width=0),
                        txt(label("m7_reread_part"), size=22)).arrange(RIGHT, buff=0.15)
        keys = VGroup(key_fixed, key_re).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UR, buff=SAFE + 0.3)
        with self.say("6.49") as (tr, t):
            self.play(FadeIn(keys), run_time=0.4)
            for c, k in zip(cols, [{"uz": "Uch qadam", "en": "For three steps"},
                                   {"uz": "Oʻn qadam", "en": "For ten steps"},
                                   {"uz": "Yigirma qadam", "en": "For twenty steps"}]):
                self.cue(tr, t, k)
                self.play(GrowFromEdge(c[0], DOWN), run_time=0.4)
                self.play(GrowFromEdge(c[1], DOWN), FadeIn(c[2]), FadeIn(c[3]), run_time=0.5)

        ratio = MathTex(rf"\times {N['ratio_20_10']}", font_size=56, color=HILITE)
        ratio.next_to(cols[2], RIGHT, buff=0.5)
        formula = MathTex(r"n S", "+", r"a\,\frac{n(n-1)}{2}", font_size=44).to_corner(UL, buff=SAFE + 0.3)
        formula[2].set_color(RLORANGE)
        with self.say("6.50") as (tr, t):
            self.cue(tr, t, {"uz": "Narx esa", "en": "The bill grew"})
            self.play(FadeIn(ratio, scale=1.3), run_time=0.6)
            self.cue(tr, t, {"uz": "Sababi", "en": "The reason"})
            self.play(Write(formula), run_time=1.0)
            self.play(Indicate(formula[2], color=RLORANGE), run_time=0.7)

        thin = VGroup()
        for c, n in zip(cols, STEPS):
            v = N[f"new_only_{n}"]
            r = Rectangle(width=0.35, height=v * h, stroke_width=0, fill_color=GOOD, fill_opacity=0.95)
            r.next_to(c[0], RIGHT, buff=0.1, aligned_edge=DOWN)
            num = MathTex(f"{v:,}".replace(",", "{,}"), font_size=24, color=GOOD).next_to(r, UP, buff=0.08)
            thin.add(VGroup(r, num))
        key_new = VGroup(Square(0.25, fill_color=GOOD, fill_opacity=0.95, stroke_width=0),
                         txt(label("m7_new_only"), size=22)).arrange(RIGHT, buff=0.15).next_to(keys, DOWN, aligned_edge=LEFT, buff=0.2)
        with self.say("6.51") as (tr, t):
            self.play(FadeIn(key_new), LaggedStart(*[GrowFromEdge(x, DOWN) for x in thin], lag_ratio=0.3), run_time=1.0)
        self.clear_all()

        card = pause([label("m7_pause_five")])
        with self.say("6.52") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
        self.hands_on()
        self.clear_all()
        with self.say("6.53") as (tr, t):
            self.play(FadeIn(txt(label("m7_cache"), size=44, weight=BOLD, color=HILITE)), run_time=0.7)
        self.clear_all()


SCENES = ["S06Cost"]
