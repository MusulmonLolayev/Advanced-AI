"""Module 7, Lecture 1, section 3 — ReAct: thinking only and acting only each fail; interleaving fixes both."""
from m7_lecture01_kit import *


def bubble(width=3.6, color=THINK):
    return RoundedRectangle(corner_radius=0.3, width=width, height=0.6, stroke_color=color, stroke_width=3)


class S03ReAct(Scene7):
    def construct(self):
        self.section_card(3)
        left = txt(label("m7_think_only"), size=30, weight=BOLD, color=THINK).move_to(LEFT * 3.4 + UP * 2.6)
        right = txt(label("m7_act_only"), size=30, weight=BOLD, color=GOOD).move_to(RIGHT * 3.4 + UP * 2.6)
        with self.say("3.18") as (tr, t):
            self.play(FadeIn(left), FadeIn(right), run_time=0.7)

        bubbles = VGroup(*[bubble() for _ in range(4)]).arrange(DOWN, buff=0.35).next_to(left, DOWN, buff=0.4)
        links = VGroup(*[Arrow(a.get_bottom(), b.get_top(), buff=0.05, color=GREY_B) for a, b in zip(bubbles, bubbles[1:])])
        premise = txt(label("m7_wrong_premise"), size=22, color=RLRED).next_to(bubbles[0], RIGHT, buff=0.25)
        never = txt(label("m7_never_checked"), size=22, color=GREY_B).next_to(bubbles, DOWN, buff=0.3)
        with self.say("3.19") as (tr, t):
            self.play(LaggedStart(*[FadeIn(b) for b in bubbles], lag_ratio=0.3), FadeIn(links), run_time=1.2)
            self.cue(tr, t, {"uz": "hech narsani tekshirmaydi", "en": "checks nothing"})
            self.play(FadeIn(never), run_time=0.5)
            self.cue(tr, t, {"uz": "Notoʻgʻri boshlangʻich", "en": "A wrong premise"})
            self.play(bubbles[0].animate.set_stroke(RLRED, width=5), FadeIn(premise), run_time=0.5)
            for b in bubbles[1:]:
                self.play(b.animate.set_stroke(RLRED, width=5), run_time=0.35)

        calls = VGroup(*[mono("search[…]", size=22, color=GOOD) for _ in range(4)]).arrange(DOWN, buff=0.55)
        calls.next_to(right, DOWN, buff=0.5)
        noplan = txt(label("m7_no_plan"), size=22, color=GREY_B).next_to(calls, DOWN, buff=0.3)
        mark = txt("?", size=48, weight=BOLD, color=RLRED).next_to(calls[2], RIGHT, buff=0.3)
        with self.say("3.20") as (tr, t):
            self.play(LaggedStart(*[FadeIn(c) for c in calls], lag_ratio=0.3), run_time=1.2)
            self.cue(tr, t, {"uz": "Natija kutilmagan", "en": "When a result is surprising"})
            self.play(FadeIn(mark), FadeIn(noplan), run_time=0.6)
        self.clear_all()

        loop = loop_diagram(0.9).move_to(DOWN * 0.4)
        name = VGroup(txt("ReAct", size=44, weight=BOLD, color=HILITE),
                      txt(label("m7_yao"), size=26, color=GREY_B)).arrange(RIGHT, buff=0.4)
        name.to_edge(UP, buff=SAFE + 0.3)
        with self.say("3.21") as (tr, t):
            self.play(FadeIn(name), run_time=0.6)
            self.cue(tr, t, {"uz": "Model navbatma-navbat", "en": "The model writes in turns"})
            self.play(FadeIn(loop[0]), run_time=0.4)
            self.play(GrowArrow(loop[4]), FadeIn(loop[1]), run_time=0.5)
            self.play(GrowArrow(loop[5]), FadeIn(loop[2]), run_time=0.5)
            self.play(Create(loop[6]), run_time=0.6)
            self.play(GrowArrow(loop[7]), FadeIn(loop[3]), run_time=0.5)

        example = txt(label("m7_thought_example"), size=26, color=THINK).to_edge(DOWN, buff=SAFE + 0.6)
        with self.say("3.22") as (tr, t):
            self.play(Indicate(loop[0], color=THINK, scale_factor=1.08), run_time=0.7)
            self.play(FadeIn(example, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        reread = txt(label("m7_reread"), size=30, weight=BOLD).to_edge(UP, buff=SAFE + 0.4)
        rows = VGroup()
        for k in range(1, 5):
            row = VGroup(*[Rectangle(width=1.0, height=0.45, stroke_width=0, fill_opacity=0.9,
                                     fill_color=RLBLUE if j == 0 else (GOOD if j == k - 1 else GREY_D))
                           for j in range(k)]).arrange(RIGHT, buff=0.06)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(DOWN * 0.3)
        with self.say("3.23") as (tr, t):
            self.play(FadeIn(reread), run_time=0.5)
            for r in rows:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)

        better = txt(label("m7_better_both"), size=26, color=HILITE).to_edge(DOWN, buff=SAFE + 0.6)
        if better.width > 12.5:
            better.scale_to_fit_width(12.5)
        with self.say("3.24") as (tr, t):
            self.play(FadeOut(rows), FadeOut(reread), FadeIn(loop_diagram(0.7).move_to(UP * 0.6)), run_time=0.7)
            self.play(FadeIn(better), run_time=0.6)
        self.clear_all()

        card = pause([label("m7_pause_act")])
        with self.say("3.25") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
        self.hands_on()
        self.clear_all()
        with self.say("3.26") as (tr, t):
            self.play(FadeIn(law_title()), run_time=0.7)
        self.clear_all()


SCENES = ["S03ReAct"]
