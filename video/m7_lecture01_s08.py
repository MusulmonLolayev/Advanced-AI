"""Module 7, Lecture 1, section 8 — designing the action space; a failure reply is an observation
(the class agent's real act(): fetch_article[1182])."""
from m7_lecture01_kit import *


def tool_name(name, color=GOOD):
    t = mono(name, size=24, color=color)
    r = RoundedRectangle(corner_radius=0.12, width=t.width + 0.5, height=0.75, stroke_color=color, stroke_width=3)
    return VGroup(r, t.move_to(r))


class S08Design(Scene7):
    def construct(self):
        self.section_card(8)
        head = self.heading(label("m7_action_space"), color=HILITE)
        with self.say("8.62") as (tr, t):
            self.play(FadeIn(head), run_time=0.5)

        big = VGroup(*[tool_name(n) for n in ("search[…]", "lookup[…]", "find_article[…]", "query_corpus[…]")])
        big.arrange(RIGHT, buff=0.3).scale_to_fit_width(12).move_to(UP * 1.0)
        large = txt(label("m7_too_large"), size=28, weight=BOLD, color=RLRED).next_to(big, UP, buff=0.3)
        which = txt(label("m7_which_one"), size=26, color=RLRED).next_to(big, DOWN, buff=0.3)
        with self.say("8.63") as (tr, t):
            self.play(FadeIn(large), LaggedStart(*[FadeIn(b) for b in big], lag_ratio=0.25), run_time=1.2)
            self.cue(tr, t, {"uz": "Model qaysi", "en": "The model is forced"})
            self.play(FadeIn(which), run_time=0.5)

        one = tool_name("search[…]").move_to(DOWN * 1.5)
        coarse = txt(label("m7_too_coarse"), size=28, weight=BOLD, color=RLRED).next_to(one, LEFT, buff=0.6)
        cannot = txt(label("m7_only_labor"), size=24, color=GREY_B).next_to(one, DOWN, buff=0.3)
        with self.say("8.64") as (tr, t):
            self.play(FadeIn(coarse), FadeIn(one), run_time=0.6)
            self.play(FadeIn(cannot), run_time=0.5)
        self.clear_all()

        r1 = txt(label("m7_rule_one_sentence"), size=32, weight=BOLD)
        r2 = txt(label("m7_rule_no_overlap"), size=32, weight=BOLD)
        rules = VGroup(r1, r2).arrange(DOWN, buff=0.4).move_to(UP * 0.5)
        with self.say("8.65") as (tr, t):
            self.play(FadeIn(r1), run_time=0.5)
            self.cue(tr, t, {"uz": "hech qachon ikkita", "en": "no two tools"})
            self.play(FadeIn(r2), run_time=0.5)
        self.clear_all()

        call = trace_line("action", "fetch_article[1182]", size=24).move_to(UP * 1.2 + LEFT * 4.2, aligned_edge=LEFT)
        obs = trace_line("observation", class_agent.act("fetch_article", "1182"), size=24)
        obs.next_to(call, DOWN, aligned_edge=LEFT, buff=0.35)
        call2 = trace_line("action", "calculator[36/5]", size=24).next_to(obs, DOWN, aligned_edge=LEFT, buff=0.6)
        obs2 = fit(trace_line("observation", class_agent.act("calculator", "36/5"), size=24, width=40), 11.0)
        obs2.next_to(call2, DOWN, aligned_edge=LEFT, buff=0.35)
        rule = txt(label("m7_failure_reply"), size=28, weight=BOLD, color=HILITE).to_edge(DOWN, buff=SAFE + 0.4)
        with self.say("8.66") as (tr, t):
            self.play(FadeIn(call), run_time=0.5)
            self.play(FadeIn(obs), run_time=0.5)
            self.cue(tr, t, {"uz": "nomaʼlum harakat", "en": "unknown action"})
            self.play(FadeIn(call2), FadeIn(obs2), run_time=0.6)
            self.cue(tr, t, {"uz": "U kuzatuv", "en": "It goes back"})
            self.play(FadeIn(rule), run_time=0.5)
        self.clear_all()

        card = pause([label("m7_pause_argument")])
        with self.say("8.67") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
        self.hands_on()
        self.clear_all()
        with self.say("8.68") as (tr, t):
            self.play(FadeIn(loop_diagram(0.8)), run_time=0.7)
        self.clear_all()


SCENES = ["S08Design"]
