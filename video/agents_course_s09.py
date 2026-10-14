"""Agent course, section 9 — what to build next: one τ²-bench domain, your own agent, four steps, the harness graded
as heavily as the agent, three ideas to keep, and the course's closing card.
"""
from agents_course_kit import *


def step_tile(n, words_text, color):
    num = MathTex(str(n), font_size=40, color=color)
    ring = Circle(radius=0.36, color=color, stroke_width=3)
    head = VGroup(ring, num.move_to(ring))
    words = txt(words_text, size=24)
    g = VGroup(head, words).arrange(RIGHT, buff=0.35)
    box = RoundedRectangle(corner_radius=0.14, width=11.0, height=g.height + 0.45, stroke_color=color, stroke_width=2.5)
    return VGroup(box, g.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.35))


class S09Project(LectureScene):
    def construct(self):
        self.section_card(9)
        agent = tile(label("ac_s8_your_agent"), color=LBLUE, size=28)
        bench = tile("τ²-bench", color=HILITE, size=28)
        card = VGroup(agent, MathTex("+", font_size=56, color=GREY_B), bench).arrange(RIGHT, buff=0.5)
        cap = txt(label("ac_s8_project"), size=26, color=GREY_B).next_to(card, UP, buff=0.4)
        top = VGroup(cap, card).move_to(UP * 0.4)
        with self.say("9.1") as (tr, t):
            self.play(FadeIn(cap), run_time=0.4)
            self.cue(tr, t, {"en": "take one tau-two-bench domain"})
            self.play(FadeIn(bench), run_time=0.4)
            self.cue(tr, t, {"en": "write your own agent loop"})
            self.play(FadeIn(agent), FadeIn(card[1]), run_time=0.5)

        steps = VGroup(*[step_tile(i + 1, k, c) for i, (k, c) in enumerate(
            ((label("ac_s8_step_loop"), LBLUE), (label("ac_s8_step_retrieval"), RLGREEN),
             (label("ac_s8_step_memory"), HILITE), (label("ac_s8_step_eval"), GOOD)))])
        steps.arrange(DOWN, buff=0.18).next_to(card, DOWN, buff=0.5)
        with self.say("9.2") as (tr, t):
            self.play(top.animate.scale(0.85).to_edge(UP, buff=SAFE + 0.2), run_time=0.5)
            steps.next_to(top, DOWN, buff=0.4)
            room = steps.get_top()[1] - (-config.frame_height / 2 + SAFE + 0.5)   # stay clear of the bottom edge
            if steps.height > room:
                steps.scale_to_fit_height(room).next_to(top, DOWN, buff=0.4)
            self.cue(tr, t, {"en": "First, the loop"})
            self.play(FadeIn(steps[0], shift=RIGHT * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": "Second, retrieval"})
            self.play(FadeIn(steps[1], shift=RIGHT * 0.2), run_time=0.5)
        with self.say("9.3") as (tr, t):
            self.cue(tr, t, {"en": "Third, memory"})
            self.play(FadeIn(steps[2], shift=RIGHT * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": "Fourth, the full evaluation"})
            self.play(FadeIn(steps[3], shift=RIGHT * 0.2), run_time=0.5)
        self.clear_all()

        harness = tile(label("ac_s8_harness"), color=GOOD, width=3.2, size=34)
        demo = tile(label("ac_s8_demo"), color=GREY_B, width=3.2, size=34)
        cmp_ = VGroup(harness, MathTex(r"\geq", font_size=72, color=HILITE), demo).arrange(RIGHT, buff=0.6)
        with self.say("9.4") as (tr, t):
            self.play(FadeIn(harness), run_time=0.4)
            self.cue(tr, t, {"en": "as heavily as the agent"})
            self.play(FadeIn(cmp_[1]), FadeIn(demo), run_time=0.5)
            self.cue(tr, t, {"en": "The harness is what tells us the truth"})
            self.play(Indicate(harness, color=GOOD, scale_factor=1.06), run_time=0.8)
        self.clear_all()


class S09Close(LectureScene):
    def construct(self):
        keep = bullets([label("ac_s8_keep_1"), label("ac_s8_keep_2"), label("ac_s8_keep_3")], size=30)
        if keep.width > 12:
            keep.scale_to_fit_width(12)
        keep.move_to(ORIGIN)
        with self.say("9.5") as (tr, t):
            self.cue(tr, t, {"en": "reliability multiplies"})
            self.play(FadeIn(keep[0], shift=RIGHT * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": "Retrieval sets the ceiling"})
            self.play(FadeIn(keep[1], shift=RIGHT * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": "anything the agent reads is untrusted"})
            self.play(FadeIn(keep[2], shift=RIGHT * 0.2), run_time=0.5)
        self.clear_all()

        title = txt(label("ac_course_title"), size=48, weight=BOLD, color=LBLUE)
        repo = VGroup(txt(label("ac_s8_code_in_repo"), size=26, color=GREY_B),
                      mono(str(CODE.relative_to(HERE.parent)) + "/", size=24, color=LBLUE)).arrange(DOWN, buff=0.2)
        thanks = txt(label("ac_s8_thanks"), size=34, color=HILITE)
        card = VGroup(title, repo, thanks).arrange(DOWN, buff=0.6)
        with self.say("9.6") as (tr, t):
            self.play(FadeIn(title, shift=UP * 0.2), FadeIn(repo), run_time=0.6)
            self.cue(tr, t, {"en": "Thank you for watching"})
            self.play(FadeIn(thanks), run_time=0.5)
        self.wait(1.2)
        self.clear_all()


SCENES = ["S09Project", "S09Close"]
