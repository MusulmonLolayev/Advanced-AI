"""Module 7, Lecture 1, section 1 — why an agent: a pipeline answers one question, a follow-up needs the loop."""
from m7_lecture01_kit import *


def chain(names, colors=None, buff=1.0, width=2.4):
    boxes = VGroup(*[node(n, color=(colors or {}).get(i, RLBLUE), width=width) for i, n in enumerate(names)])
    boxes.arrange(RIGHT, buff=buff)
    arrows = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.1, color=WHITE) for a, b in zip(boxes, boxes[1:])])
    return boxes, arrows


def agent_diagram():
    q = node(label("m7_question"))
    m = node(label("m7_model"), color=THINK)
    a = node(label("m7_answer"), color=HILITE)
    VGroup(q, m, a).arrange(RIGHT, buff=1.6)
    tool = node(label("m7_tool"), color=GOOD).next_to(m, DOWN, buff=1.3)
    go = CurvedArrow(m.get_bottom() + LEFT * 0.5, tool.get_top() + LEFT * 0.5, angle=TAU / 6, color=WHITE)
    back = CurvedArrow(tool.get_top() + RIGHT * 0.5, m.get_bottom() + RIGHT * 0.5, angle=TAU / 6, color=HILITE,
                       stroke_width=6)
    arrows = VGroup(Arrow(q.get_right(), m.get_left(), buff=0.1), Arrow(m.get_right(), a.get_left(), buff=0.1))
    return VGroup(q, m, a, tool, arrows, go, back), back


class S01Why(Scene7):
    def construct(self):
        self.section_card(1)
        q = txt(label("m7_q_week"), size=32, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        row, arrows = chain([label("m7_question"), label("m7_search"), label("m7_answer")], {2: HILITE})
        row.shift(UP * 0.3)
        arrows.shift(UP * 0.3)
        with self.say("1.2") as (tr, t):
            self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.6)
            self.cue(tr, t, {"uz": "Bu savolga bitta qidiruv", "en": "One search is enough"})
            self.play(LaggedStart(*[FadeIn(b) for b in row], lag_ratio=0.35), run_time=1.2)
            self.play(*[GrowArrow(a) for a in arrows], run_time=0.6)

        name = txt(label("m7_pipeline"), size=32, weight=BOLD, color=HILITE).next_to(row, UP, buff=0.45)
        known = txt(label("m7_steps_known"), size=26, color=GREY_B).next_to(row, DOWN, buff=0.6)
        with self.say("1.3") as (tr, t):
            self.play(FadeIn(name), run_time=0.5)
            self.cue(tr, t, {"uz": "Qadamlar soni ham", "en": "The number of steps"})
            self.play(FadeIn(known), run_time=0.5)

        q2 = txt(label("m7_q_minors"), size=30, color=HILITE).next_to(q, DOWN, buff=0.25)
        again = node(label("m7_search")).move_to(row[1].get_center() + DOWN * 1.9)
        a_again = Arrow(row[1].get_bottom(), again.get_top(), buff=0.1, color=RLRED)
        mark = txt("?", size=56, weight=BOLD, color=RLRED).next_to(again, RIGHT, buff=0.4)
        with self.say("1.4") as (tr, t):
            self.play(FadeIn(q2, shift=DOWN * 0.2), FadeOut(known), run_time=0.6)
            self.cue(tr, t, {"uz": "Umumiy qoidani", "en": "We find the general rule"})
            self.play(Indicate(row[1], color=HILITE, scale_factor=1.05), run_time=0.8)
            self.play(GrowArrow(a_again), FadeIn(again), run_time=0.7)

        unknown = txt(label("m7_steps_unknown"), size=28, color=RLRED).to_edge(DOWN, buff=SAFE + 0.5)
        with self.say("1.5") as (tr, t):
            self.play(FadeIn(mark), run_time=0.4)
            self.play(FadeIn(unknown), run_time=0.5)
        self.clear_all()

        diagram, back = agent_diagram()
        diagram.move_to(DOWN * 0.3)
        name2 = txt(label("m7_agent"), size=32, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.4)
        decides = txt(label("m7_model_decides"), size=28, color=THINK).to_edge(DOWN, buff=SAFE + 0.5)
        with self.say("1.6") as (tr, t):
            self.play(FadeIn(name2), FadeIn(diagram[:3]), FadeIn(diagram[4]), run_time=0.8)
            self.cue(tr, t, {"uz": "Agentda keyingi qadamni", "en": "In an agent"})
            self.play(FadeIn(diagram[3]), Create(diagram[5]), run_time=0.8)
            self.play(Create(back), run_time=0.8)
            self.play(FadeIn(decides), run_time=0.5)
        self.clear_all()

        top_row, top_arrows = chain([label("m7_question"), label("m7_search"), label("m7_answer")], {2: HILITE},
                                    buff=0.9, width=2.1)
        pipe = VGroup(top_row, top_arrows).scale(0.8)
        pipe_name = txt(label("m7_pipeline"), size=26, weight=BOLD, color=GREY_B)
        VGroup(pipe_name, pipe).arrange(RIGHT, buff=0.6).to_edge(UP, buff=SAFE + 0.4)
        diagram2, back2 = agent_diagram()
        diagram2.scale(0.8).move_to(DOWN * 1.2)
        agent_name = txt(label("m7_agent"), size=26, weight=BOLD, color=HILITE).next_to(diagram2, LEFT, buff=0.5)
        with self.say("1.7") as (tr, t):
            self.play(FadeIn(pipe_name), FadeIn(pipe), run_time=0.6)
            self.play(FadeIn(agent_name), FadeIn(diagram2), run_time=0.6)
            self.cue(tr, t, {"uz": "agentda strelka orqaga", "en": "in the agent, the arrow goes back"})
            for _ in range(2):
                self.play(ShowPassingFlash(back2.copy().set_stroke(YELLOW, width=10), time_width=0.6), run_time=0.9)
        self.clear_all()

        card = pause([label("m7_pause_leave"), label("m7_pause_teen"), label("m7_pause_which")])
        with self.say("1.8") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
        self.hands_on()
        self.clear_all()
        with self.say("1.9") as (tr, t):
            self.play(FadeIn(loop_diagram(0.8)), run_time=0.8)
        self.clear_all()


SCENES = ["S01Why"]
