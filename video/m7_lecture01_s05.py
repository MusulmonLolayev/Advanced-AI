"""Module 7, Lecture 1, section 5 — the same model without tools: right numbers, citations that do not hold, and
amounts the code never states (traces/q2_under18_notools, q3_min_wage_notools, q3_min_wage_notools2)."""
from m7_lecture01_kit import *


def answer_box(name, marks, width=60, size=19):
    """A recorded no-tools answer, its markdown stripped, with the claims `marks` lit in red."""
    text = trace(name)["answer"].replace("**", "")
    text = re.sub(r"\n\s*\n", "\n", text).strip()
    marks = [m.replace(" ", "\u00a0") for m in marks]            # a lit claim never breaks across two lines
    for m in marks:
        text = text.replace(m.replace("\u00a0", " "), m)
    wrapped = "\n".join(textwrap.fill(p, width) for p in text.split("\n"))
    t = Text(wrapped, font=MONO, font_size=size, color=GREY_A, disable_ligatures=True,
             t2c={m: RLRED for m in marks if m in wrapped})
    frame = SurroundingRectangle(t, buff=0.3, corner_radius=0.12, color=GREY_B, stroke_width=2)
    return VGroup(frame, t)


class S05NoTools(Scene7):
    def construct(self):
        self.section_card(5)
        head = self.heading(label("m7_no_tools"), color=HILITE)
        q = VGroup(txt(label("m7_q_week"), size=24), txt(label("m7_q_minors"), size=24, color=HILITE))
        q.arrange(DOWN, buff=0.1).next_to(head, DOWN, buff=0.35)
        with self.say("5.37") as (tr, t):
            self.play(FadeIn(head), FadeIn(q), run_time=0.7)

        a2 = answer_box("q2_under18_notools", ["[Art. 183]"]).next_to(q, DOWN, buff=0.4)
        a2.scale_to_fit_width(min(a2.width, 12.4))
        right = txt(label("m7_numbers_right"), size=24, color=GOOD).to_edge(DOWN, buff=SAFE + 0.45)
        with self.say("5.38") as (tr, t):
            self.play(FadeIn(a2), run_time=0.7)
            self.cue(tr, t, {"uz": "Raqamlar toʻgʻri", "en": "The numbers are right"})
            self.play(FadeIn(right), run_time=0.4)
            self.cue(tr, t, {"uz": "Lekin manba", "en": "But it cites"})
            self.play(Indicate(a2[1], color=RLRED, scale_factor=1.02), run_time=0.6)
        self.clear_all()

        c183 = article_card("183", "415-moddasi", chars=330, width=9.5, size=19).move_to(UP * 1.2)
        wrong = txt(label("m7_wrong_citation"), size=28, weight=BOLD, color=RLRED).next_to(c183, DOWN, buff=0.35)
        c415 = article_card("415", "haftasiga oʻttiz olti soatdan", chars=160, width=9.5, size=18)
        c415.next_to(wrong, DOWN, buff=0.3)
        with self.say("5.39") as (tr, t):
            self.play(FadeIn(c183), run_time=0.7)
            self.cue(tr, t, {"uz": "Oʻttiz olti ham", "en": "Neither thirty-six"})
            self.play(FadeIn(wrong), run_time=0.4)
            self.cue(tr, t, {"uz": "Bu raqamlar", "en": "Those numbers"})
            self.play(FadeIn(c415, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        q3 = txt(label("m7_q_wage"), size=30, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        a3 = answer_box("q3_min_wage_notools", ["1,155,000", "[Art. 153]"], width=62, size=18)
        a3.scale_to_fit_width(min(a3.width, 12.4)).next_to(q3, DOWN, buff=0.35)
        with self.say("5.40") as (tr, t):
            self.play(FadeIn(q3), run_time=0.5)
            self.cue(tr, t, {"uz": "Vositasiz model", "en": "Without tools"})
            self.play(FadeIn(a3), run_time=0.7)

        # two columns: each answer, and under it the article it cites
        col_w, top = 6.2, 3.3
        t153 = fit(article_card("153", chars=90, width=5.6, size=18), col_w)
        again = txt(label("m7_asked_again"), size=24, color=GREY_B)
        a3b = fit(answer_box("q3_min_wage_notools2", ["1,270,000", "[Art. 209]"], width=62, size=18), col_w)   # wrapped like the left one, so both read at one size
        t209 = fit(article_card("209", chars=90, width=5.6, size=18), col_w)
        with self.say("5.41") as (tr, t):
            self.play(FadeOut(q3), a3.animate.scale_to_fit_width(col_w).move_to([-3.45, top, 0], aligned_edge=UP),
                      run_time=0.6)
            t153.next_to(a3, DOWN, buff=0.3)
            self.play(FadeIn(t153), run_time=0.5)
            self.cue(tr, t, {"uz": "Xuddi shu savolni", "en": "We asked the same question"})
            again.move_to([3.45, top, 0], aligned_edge=UP)
            a3b.next_to(again, DOWN, buff=0.15)
            self.play(FadeIn(again), FadeIn(a3b), run_time=0.7)
            self.cue(tr, t, {"uz": "Bu modda esa", "en": "And that article"})
            t209.next_to(a3b, DOWN, buff=0.3)
            self.play(FadeIn(t209), run_time=0.5)
        self.clear_all()

        c245 = article_card("245", "Prezidenti tomonidan", chars=260, width=9.5, size=19).move_to(UP * 0.9)
        none = txt(label("m7_no_amount"), size=30, weight=BOLD, color=HILITE).next_to(c245, DOWN, buff=0.4)
        steps = len(trace("q3_min_wage")["trace"])
        withtools = VGroup(txt(label("m7_with_tools"), size=26, color=GOOD),
                           tagged(steps, label("m7_steps"), size=26, value_color=GOOD, value_weight=BOLD))
        withtools.arrange(RIGHT, buff=0.3).next_to(none, DOWN, buff=0.35)
        with self.say("5.42") as (tr, t):
            self.play(FadeIn(none), run_time=0.5)
            self.cue(tr, t, {"uz": "Ikki yuz qirq", "en": "Article two hundred"})
            self.play(FadeIn(c245), run_time=0.6)
            self.cue(tr, t, {"uz": "Agentimiz yetti", "en": "Our agent reached"})
            self.play(FadeIn(withtools), run_time=0.5)
        self.clear_all()

        with self.say("5.43") as (tr, t):
            self.play(FadeIn(txt(label("m7_read_not_remember"), size=40, weight=BOLD, color=HILITE)), run_time=0.7)
        self.clear_all()
        card = pause([label("m7_pause_claims")])
        with self.say("5.44") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
        self.hands_on()
        self.clear_all()
        with self.say("5.45") as (tr, t):
            self.play(FadeIn(txt(label("m7_billed"), size=40, weight=BOLD, color=HILITE)), run_time=0.7)
        self.clear_all()


SCENES = ["S05NoTools"]
