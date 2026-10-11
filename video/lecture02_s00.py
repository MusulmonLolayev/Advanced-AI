"""Lecture 2 — the opening: one greeting and the two parts."""
from lecture02_kit import *


class S00Opening(LectureScene):
    def construct(self):
        num = txt(ui("lecture", n=2), size=64, weight=BOLD, color=RLBLUE)
        sub = txt(w("Conditional probability, independence and Bayes' theorem",
                    "Shartli ehtimollik, erklilik va Bayes teoremasi"), size=32, color=GREY_B)
        title = VGroup(num, sub).arrange(DOWN, buff=0.4)
        rows = VGroup(*[txt(PARTS[n], size=32) for n in (0, 1)]).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        marks = VGroup(*[Line(ORIGIN, RIGHT * 0.5, color=c, stroke_width=8).next_to(r, LEFT, buff=0.3)
                         for c, r in zip((RLBLUE, HILITE), rows)])
        plan = VGroup(marks, rows).move_to(DOWN * 0.9)
        given = MathTex(r"P(B \mid A)", font_size=60, color=HILITE).next_to(plan, DOWN, buff=0.6)

        with self.say("0.0") as (tr, t):
            self.play(FadeIn(num, shift=UP * 0.3), run_time=0.8)
            self.play(FadeIn(sub), run_time=0.6)
            self.cue(tr, t, {"en": "It also has", "uz": "Bu maʼruza ham"})
            self.play(title.animate.scale(0.8).to_edge(UP, buff=SAFE + 0.4), run_time=0.8)
            self.cue(tr, t, {"en": "In part zero", "uz": "Nolinchi qismda"})
            self.play(GrowFromEdge(marks[0], LEFT), FadeIn(rows[0], shift=RIGHT * 0.3), run_time=0.7)
            self.cue(tr, t, {"en": "and in part one", "uz": "birinchi qismda"})
            self.play(GrowFromEdge(marks[1], LEFT), FadeIn(rows[1], shift=RIGHT * 0.3), run_time=0.7)
            self.play(Write(given), run_time=0.8)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent card


SCENES = ["S00Opening"]
