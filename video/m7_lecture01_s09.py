"""Module 7, Lecture 1, section 9 — how the loop breaks; the step budget on the recorded minimum-wage runs
(traces/q3_min_wage.json: 7 steps, English traces/uk/: 4; q3_min_wage_steps3.json: stopped after 3), and in English
the run's step that proved nothing (search[£])."""
from m7_lecture01_kit import *

FULL = turns("q3_min_wage")
CUT = turns("q3_min_wage_steps3")
LIMIT = class_agent.run.__defaults__[0]                     # run(question, model, max_steps=8, ...)
CUT_LIMIT = trace("q3_min_wage_steps3")["max_steps"]


def tile(action, width=1.5):
    name = re.match(r"(\w+)\[(.*)\]", action, re.S)
    short_name = {"search": "search", "fetch_article": "fetch", "fetch": "fetch", "answer": "answer"}[name[1]]
    arg = name[2] if name[1] == FETCH else ""
    color = HILITE if name[1] == "answer" else GOOD
    r = RoundedRectangle(corner_radius=0.1, width=width, height=1.0, stroke_color=color, stroke_width=3,
                         fill_color=BLACK, fill_opacity=0.6)
    t = VGroup(mono(short_name, size=18, color=color), mono(arg, size=18, color=WHITE) if arg else VGroup())
    t.arrange(DOWN, buff=0.08).move_to(r)
    return VGroup(r, t)


def ruler(n, width=1.5, buff=0.12):
    slots = VGroup(*[DashedVMobject(RoundedRectangle(corner_radius=0.1, width=width, height=1.0, stroke_color=GREY_D,
                                                    stroke_width=2), num_dashes=24) for _ in range(n)])
    return slots.arrange(RIGHT, buff=buff)


class S09Breaks(Scene7):
    def construct(self):
        self.section_card(9)
        ways = VGroup(*[txt(label(k), size=30, weight=BOLD) for k in ("m7_endless", "m7_invalid", "m7_compound")])
        ways.arrange(RIGHT, buff=0.9).to_edge(UP, buff=SAFE + 0.5)
        same = VGroup(*[mono(f"search[{FACT['repeat_query']}]", size=22, color=GOOD) for _ in range(3)]).arrange(DOWN, buff=0.35)
        same.move_to(DOWN * 0.4)
        with self.say("9.69") as (tr, t):
            self.play(LaggedStart(*[FadeIn(w) for w in ways], lag_ratio=0.3), run_time=1.0)
            self.cue(tr, t, {"uz": "Birinchisi", "en": "The first"})
            self.play(ways[0].animate.set_color(RLRED), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(s) for s in same], lag_ratio=0.4), run_time=1.2)
        self.play(FadeOut(same), run_time=0.3)

        slots = ruler(LIMIT).move_to(DOWN * 0.2)
        limit_lab = VGroup(txt(label("m7_step_limit"), size=24, color=GREY_B), MathTex(str(LIMIT), font_size=36))
        limit_lab.arrange(RIGHT, buff=0.2).next_to(slots, UP, buff=0.3)
        tiles = VGroup(*[tile(a).move_to(s) for (_, a, _), s in zip(FULL, slots)])
        with self.say("9.70") as (tr, t):
            self.play(FadeIn(slots), FadeIn(limit_lab), run_time=0.6)
            self.cue(tr, t, {"uz": "Eng kam ish haqi", "en": "The minimum-wage question"})
            self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in tiles], lag_ratio=0.35), run_time=2.4)

        slots3 = ruler(LIMIT).move_to(DOWN * 2.1)
        tiles3 = VGroup(*[tile(a).move_to(s) for (_, a, _), s in zip(CUT, slots3)])
        wall = Line(UP * 0.6, DOWN * 0.6, color=RLRED, stroke_width=10).next_to(slots3[CUT_LIMIT - 1], RIGHT, buff=0.06)
        none = txt(label("m7_no_answer"), size=28, weight=BOLD, color=RLRED).next_to(wall, RIGHT, buff=0.5)
        with self.say("9.71") as (tr, t):
            self.play(FadeIn(slots3[:CUT_LIMIT]), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(x) for x in tiles3], lag_ratio=0.3), run_time=1.0)
            self.play(Create(wall), run_time=0.4)
            self.cue(tr, t, {"uz": "Hech qanday javob", "en": "No answer"})
            self.play(FadeIn(none), run_time=0.4)
        self.clear_all()

        last = re.search(rf"{FETCH}\[(.+?)\]", [a for _, a, _ in CUT if a.startswith(FETCH + "[")][-1])[1]
        msg = VGroup(txt(label("m7_not_found"), size=34, weight=BOLD, color=HILITE),
                     tagged(last, label("m7_last_read"), after=False, size=30))
        msg.arrange(DOWN, buff=0.35)
        frame = SurroundingRectangle(msg, buff=0.4, corner_radius=0.15, color=HILITE)
        with self.say("9.72") as (tr, t):
            self.play(FadeIn(msg), Create(frame), run_time=0.8)
        self.clear_all()

        ways2 = ways.copy().set_color(WHITE)
        bad = trace_line("action", "calculator[36/5]", size=22).move_to(UP * 0.4 + LEFT * 4.2, aligned_edge=LEFT)
        reply = fit(trace_line("observation", act("calculator", "36/5"), size=22, width=40), 11.0)
        reply.next_to(bad, DOWN, aligned_edge=LEFT, buff=0.3)
        with self.say("9.73") as (tr, t):
            self.play(FadeIn(ways2), run_time=0.4)
            self.play(ways2[1].animate.set_color(RLRED), FadeIn(bad), run_time=0.6)
            self.cue(tr, t, {"uz": "Davosi xatoni", "en": "The cure is"})
            self.play(FadeIn(reply), run_time=0.5)

        chainrow = VGroup(*[Square(0.6, stroke_color=GOOD, stroke_width=3) for _ in range(6)]).arrange(RIGHT, buff=0.35)
        chainrow.move_to(DOWN * 2.0)
        links = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.05, stroke_width=3) for a, b in zip(chainrow, chainrow[1:])])
        with self.say("9.74") as (tr, t):
            self.play(FadeOut(bad), FadeOut(reply), ways2[1].animate.set_color(WHITE), ways2[2].animate.set_color(RLRED),
                      run_time=0.5)
            self.play(FadeIn(chainrow), FadeIn(links), run_time=0.6)
            self.cue(tr, t, {"uz": "bitta yomon", "en": "one bad observation"})
            self.play(chainrow[1].animate.set_fill(RLRED, opacity=0.9), run_time=0.4)
            for s in chainrow[2:]:
                self.play(s.animate.set_stroke(RLRED), run_time=0.25)
        self.clear_all()

        if "9.74a" in NARRATION:               # English: the minimum-wage run's step 3, a search that cannot match
            k = next(i for i, (_, a, _) in enumerate(FULL) if a == "search[£]")
            th_next = FULL[k + 1][0]
            row = VGroup(mono(f"{k + 1}", size=26, color=HILITE),
                         trace_line("action", FULL[k][1], size=24)).arrange(RIGHT, buff=0.4)
            row.move_to(UP * 2.0 + LEFT * 5.0, aligned_edge=LEFT)
            got = trace_line("observation", FULL[k][2], size=24).next_to(row, DOWN, aligned_edge=LEFT, buff=0.3)
            words = txt(label("m7_words_only"), size=22, color=GREY_B).next_to(got, DOWN, aligned_edge=LEFT, buff=0.25)
            then = fit(trace_line("thought", th_next, size=22, width=56), 11.8)
            then.next_to(words, DOWN, aligned_edge=LEFT, buff=0.45)
            key = "No monetary figure appears anywhere"
            line1 = then[1]
            under = Underline(line1, color=RLRED, buff=0.04)
            proof = txt(label("m7_proved_nothing"), size=28, weight=BOLD, color=RLRED).to_edge(DOWN, buff=SAFE + 0.5)
            assert key in th_next
            with self.say("9.74a") as (tr, t):
                self.cue(tr, t, "the model searched for the pound sign")
                self.play(FadeIn(row), run_time=0.5)
                self.cue(tr, t, "Our search reads only words")
                self.play(FadeIn(got), FadeIn(words), run_time=0.5)
                self.cue(tr, t, "and the model took")
                self.play(FadeIn(then), run_time=0.5)
                self.play(Create(under), run_time=0.5)
                self.cue(tr, t, "But that step proved nothing")
                self.play(FadeIn(proof), run_time=0.5)
            self.clear_all()

        card = pause([label("m7_pause_repeat")])
        with self.say("9.75") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
        self.hands_on()
        self.clear_all()
        with self.say("9.76") as (tr, t):
            self.play(FadeIn(MathTex(r"p \cdot p \cdot p \cdots", font_size=60)), run_time=0.7)
        self.clear_all()


SCENES = ["S09Breaks"]
