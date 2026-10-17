"""Module 7, Lecture 1, section 2 — tool, action, action space, trajectory; the model only requests, our code runs."""
from m7_lecture01_kit import *


def tool_card(call, desc_key, color):
    name = mono(call, size=24, color=color)
    desc = txt(label(desc_key), size=22, color=GREY_A)
    inner = VGroup(name, desc).arrange(DOWN, buff=0.25)
    rect = RoundedRectangle(corner_radius=0.14, width=max(inner.width + 0.5, 3.6), height=inner.height + 0.6,
                            stroke_color=color, stroke_width=3)
    return VGroup(rect, inner.move_to(rect))


class S02Tools(Scene7):
    def construct(self):
        self.section_card(2)
        head = self.heading(label("m7_tool"), color=HILITE)
        define = txt(label("m7_tool_def"), size=30).next_to(head, DOWN, buff=0.5)
        with self.say("2.10") as (tr, t):
            self.play(FadeIn(head), run_time=0.5)
            self.cue(tr, t, {"uz": "Vosita bu model", "en": "A tool is a function"})
            self.play(FadeIn(define, shift=UP * 0.2), run_time=0.6)

        cards = VGroup(tool_card("search[…]", "m7_tool_search", GOOD),
                       tool_card("fetch_article[N]", "m7_tool_fetch", GOOD),
                       tool_card("answer[…]", "m7_tool_answer", HILITE)).arrange(RIGHT, buff=0.4)
        cards.scale_to_fit_width(min(cards.width, 12.6)).move_to(DOWN * 0.2)
        with self.say("2.11") as (tr, t):
            for c, k in zip(cards, [{"uz": "Qidiruv soʻzlar", "en": "Search finds"},
                                    {"uz": "Moddani olish bitta", "en": "Fetch article returns"},
                                    {"uz": "Javob esa", "en": "Answer ends"}]):
                self.cue(tr, t, k)
                self.play(FadeIn(c, shift=UP * 0.2), run_time=0.5)

        brace = Brace(cards, DOWN, color=HILITE)
        space = txt(label("m7_action_space"), size=30, weight=BOLD, color=HILITE).next_to(brace, DOWN, buff=0.2)
        with self.say("2.12") as (tr, t):
            self.play(GrowFromCenter(brace), FadeIn(space), run_time=0.7)
        self.clear_all()

        kinds = ["thought", "action", "observation"] * 3 + ["answer"]
        cells = VGroup(*[node(label({"thought": "m7_thought", "action": "m7_action", "observation": "m7_observation",
                                     "answer": "m7_final"}[k]), color=KIND_COLOR[k], width=1.15, height=0.7, size=18)
                         for k in kinds]).arrange(RIGHT, buff=0.12).move_to(UP * 0.4)
        tbrace = Brace(cells, DOWN, color=HILITE)
        tname = txt(label("m7_trajectory"), size=32, weight=BOLD, color=HILITE).next_to(tbrace, DOWN, buff=0.2)
        with self.say("2.13") as (tr, t):
            self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.15), run_time=1.6)
            self.play(GrowFromCenter(tbrace), FadeIn(tname), run_time=0.6)
        self.clear_all()

        model = node(label("m7_model"), color=THINK).move_to(LEFT * 4.6 + UP * 1.0)
        code = node(label("m7_our_code"), color=GOOD).move_to(RIGHT * 0.4 + UP * 1.0)
        tool = node(label("m7_tool"), color=GOOD).move_to(RIGHT * 4.8 + UP * 1.0)
        slip = mono("fetch_article[182]", size=22, color=GOOD).next_to(model, DOWN, buff=0.4)
        result = article_card("182", "haftasiga qirq soatdan ortiq", chars=170, width=8.0, size=18)
        result.scale(0.8).move_to(DOWN * 2.0)
        with self.say("2.14") as (tr, t):
            self.play(FadeIn(model), FadeIn(code), FadeIn(tool), run_time=0.6)
            self.cue(tr, t, {"uz": "U faqat soʻrov", "en": "It only writes a request"})
            self.play(Write(slip), run_time=0.8)
            self.cue(tr, t, {"uz": "Bajarish yoki", "en": "Our code decides"})
            self.play(slip.animate.next_to(code, DOWN, buff=0.4), run_time=0.8)
            self.play(Indicate(code, color=GOOD, scale_factor=1.05), run_time=0.5)
            self.play(FadeIn(result, shift=UP * 0.2), run_time=0.6)

        wall = DashedLine(UP * 2.6, DOWN * 0.1, color=RLRED, stroke_width=5).move_to(LEFT * 2.1 + UP * 1.1)
        wname = txt(label("m7_boundary"), size=26, weight=BOLD, color=RLRED).next_to(wall, UP, buff=0.1)
        req = txt(label("m7_request"), size=22, color=GREY_B).next_to(wall.get_top(), LEFT, buff=0.3).shift(DOWN * 0.3)
        exe = txt(label("m7_execution"), size=22, color=GREY_B).next_to(wall.get_top(), RIGHT, buff=0.3).shift(DOWN * 0.3)
        with self.say("2.15") as (tr, t):
            self.play(FadeOut(result), Create(wall), FadeIn(wname), run_time=0.8)
            self.play(FadeIn(req), FadeIn(exe), run_time=0.5)
        self.clear_all()

        card = pause([label("m7_pause_calc"), label("m7_pause_calc2")])
        with self.say("2.16") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
        self.hands_on()
        self.clear_all()
        with self.say("2.17") as (tr, t):
            self.play(FadeIn(loop_diagram(0.8)), run_time=0.8)
        self.clear_all()


SCENES = ["S02Tools"]
