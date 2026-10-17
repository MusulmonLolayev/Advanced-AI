"""Module 7, Lecture 1, section 10 — errors compound (p to the power k), and the closing.
Numbers: N: p_good_k_long, p_lever_k_long, p_lever_k_short; the curves are 0.95^k and 0.90^k (m7/capture_l01.py)."""
from m7_lecture01_kit import *


class S10Compound(Scene7):
    def construct(self):
        self.section_card(10)
        rule = MathTex(r"P(A_1 \cap A_2 \cap \dots \cap A_k)", "=", r"P(A_1)\,P(A_2)\cdots P(A_k)", font_size=46)
        rule.move_to(UP * 0.5)
        with self.say("10.77") as (tr, t):
            self.play(Write(rule), run_time=1.4)
        self.clear_all()

        tiles = VGroup(*[MathTex("p", font_size=48) for _ in range(C.K_LONG)]).arrange(RIGHT, buff=0.35).move_to(UP * 0.8)
        dots = VGroup(*[MathTex(r"\cdot", font_size=48).move_to((a.get_center() + b.get_center()) / 2)
                        for a, b in zip(tiles, tiles[1:])])
        power = MathTex(rf"p^{{{C.K_LONG}}}", font_size=72, color=HILITE).next_to(tiles, DOWN, buff=0.7)
        with self.say("10.78") as (tr, t):
            self.play(LaggedStart(*[FadeIn(x) for x in tiles], lag_ratio=0.1), FadeIn(dots), run_time=1.2)
            self.cue(tr, t, {"uz": "Unda oʻn", "en": "Then the chance"})
            self.play(TransformFromCopy(VGroup(tiles, dots), power), run_time=0.8)
        self.clear_all()

        ax = Axes(x_range=[0, 20, 5], y_range=[0, 1, 0.25], x_length=9, y_length=4.6, tips=False,
                  axis_config={"include_numbers": True, "font_size": 24}).move_to(UP * 0.15 + LEFT * 0.6)
        xl = txt(label("m7_number_of_steps"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.4)
        yl = txt(label("m7_all_right"), size=22, color=GREY_B).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.45)
        good = ax.plot(lambda k: C.P_GOOD ** k, x_range=[0, 20], color=GOOD)
        good_lab = MathTex(f"p = {C.P_GOOD}", font_size=32, color=GOOD).next_to(ax.c2p(20, C.P_GOOD ** 20), UP, buff=0.15)
        k10 = ax.c2p(C.K_LONG, N["p_good_k_long"])
        dot = Dot(k10, color=HILITE, radius=0.09)
        val = MathTex(f"{N['p_good_k_long']}", font_size=40, color=HILITE).next_to(dot, UR, buff=0.12)
        six = txt(label("m7_six_in_ten"), size=24, color=HILITE).to_corner(UR, buff=SAFE + 0.4)
        with self.say("10.79") as (tr, t):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.play(Create(good), FadeIn(good_lab), run_time=1.0)
            self.cue(tr, t, {"uz": "Lekin oʻn", "en": "But after ten"})
            self.play(FadeIn(dot, scale=1.5), FadeIn(val), run_time=0.6)
            self.play(FadeIn(six), run_time=0.4)

        worse = fit(txt(label("m7_worse"), size=24, color=RLRED), 6.0)
        worse.next_to(six, DOWN, buff=0.2).align_to(six, RIGHT)
        with self.say("10.80") as (tr, t):
            self.play(FadeIn(worse), run_time=0.5)

        lever = ax.plot(lambda k: C.P_LEVER ** k, x_range=[0, 20], color=RLORANGE)
        lever_lab = MathTex(f"p = {C.P_LEVER}", font_size=32, color=RLORANGE).next_to(ax.c2p(20, C.P_LEVER ** 20), UP, buff=0.15)
        d10 = Dot(ax.c2p(C.K_LONG, N["p_lever_k_long"]), color=RLORANGE, radius=0.08)
        d5 = Dot(ax.c2p(C.K_SHORT, N["p_lever_k_short"]), color=RLORANGE, radius=0.08)
        v10 = MathTex(f"{N['p_lever_k_long']}", font_size=34, color=RLORANGE).next_to(d10, DOWN, buff=0.12)
        v5 = MathTex(f"{N['p_lever_k_short']}", font_size=34, color=RLORANGE).next_to(d5, DL, buff=0.1)
        with self.say("10.81") as (tr, t):
            self.play(FadeOut(worse), FadeOut(six), Create(lever), FadeIn(lever_lab), run_time=1.0)
            self.cue(tr, t, {"uz": "oʻn qadam nol", "en": "ten steps give"})
            self.play(FadeIn(d10), FadeIn(v10), run_time=0.5)
            self.cue(tr, t, {"uz": "besh qadam esa", "en": "and five steps"})
            self.play(FadeIn(d5), FadeIn(v5), run_time=0.5)
            self.play(Indicate(v5, color=RLORANGE), run_time=0.6)
        self.clear_all()

        levers = VGroup(*[txt(f"{i}. {label(k)}", size=34, weight=BOLD) for i, k in
                          enumerate(("m7_fewer", "m7_better", "m7_recovery"), 1)]).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        with self.say("10.82") as (tr, t):
            for x in levers:
                self.play(FadeIn(x, shift=RIGHT * 0.2), run_time=0.5)
        self.clear_all()

        card = pause([label("m7_pause_99")])
        math = MathTex(r"p = 0.99,\quad k = 20,\quad p^{k} = \;?", font_size=48).next_to(card, DOWN, buff=0.5)
        with self.say("10.83") as (tr, t):
            self.play(FadeIn(card), FadeIn(math), run_time=0.6)
        self.hands_on()
        self.clear_all()
        with self.say("10.84") as (tr, t):
            self.play(FadeIn(txt(label("m7_trajectory"), size=44, weight=BOLD, color=HILITE)), run_time=0.7)
        self.clear_all()


class S10Closing(Scene7):
    def construct(self):
        rows = VGroup(*[txt(label(k), size=32) for k in ("m7_sum_agent", "m7_sum_react", "m7_sum_context",
                                                          "m7_sum_reliability")]).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say("10.85") as (tr, t):
            for x, k in zip(rows, [{"uz": "Agent bu", "en": "An agent is"}, {"uz": "Riekt fikr", "en": "ReAct takes"},
                                   {"uz": "Qoralama bu", "en": "The scratchpad"}, {"uz": "Ishonchlilik esa", "en": "And reliability"}]):
                self.cue(tr, t, k)
                self.play(FadeIn(x, shift=RIGHT * 0.2), run_time=0.5)
        self.clear_all()
        nxt = txt(label("m7_next"), size=44, weight=BOLD, color=RLBLUE)
        with self.say("10.86") as (tr, t):
            self.play(FadeIn(nxt), run_time=0.7)
        self.clear_all()
        self.play(FadeIn(brand_outro()), run_time=1.0)
        self.wait(1.5)


SCENES = ["S10Compound", "S10Closing"]
