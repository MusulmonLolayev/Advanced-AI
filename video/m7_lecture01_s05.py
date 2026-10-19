"""Module 7, Lecture 1, section 5 — the same model without tools: right numbers, citations that do not hold, and
amounts the law never states (traces/q2_under18_notools, q3_min_wage_notools, q3_min_wage_notools2; English:
traces/uk/, where the wage figures are right but from memory)."""
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

        marks = ["[WTR 4(2)]", "[WTR 5(1)]"] if UK else ["[Art. 183]"]
        a2 = answer_box("q2_under18_notools", marks).next_to(q, DOWN, buff=0.4)
        a2.scale_to_fit_width(min(a2.width, 12.4))
        right = txt(label("m7_numbers_right"), size=24, color=GOOD).to_edge(DOWN, buff=SAFE + 0.45)
        with self.say("5.38") as (tr, t):
            self.play(FadeIn(a2), run_time=0.7)
            self.cue(tr, t, {"uz": "Raqamlar toʻgʻri", "en": "The numbers are right"})
            self.play(FadeIn(right), run_time=0.4)
            self.cue(tr, t, {"uz": "Lekin manba", "en": "But look at where"})
            self.play(Indicate(a2[1], color=RLRED, scale_factor=1.02), run_time=0.6)
        self.clear_all()

        if UK:
            self.uk_citations()
        else:
            self.uz_citations()

        q3 = txt(label("m7_q_wage"), size=30, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        first_marks = ["£12.71", "NMW Regulations 2015"] if UK else ["1,155,000", "[Art. 153]"]
        a3 = answer_box("q3_min_wage_notools", first_marks, width=62, size=18)
        a3.scale_to_fit_width(min(a3.width, 12.4))
        if a3.height > 5.6:
            a3.scale_to_fit_height(5.6)
        a3.next_to(q3, DOWN, buff=0.35)
        with self.say("5.40") as (tr, t):
            self.play(FadeIn(q3), run_time=0.5)
            self.cue(tr, t, {"uz": "Vositasiz model", "en": "Without tools"})
            self.play(FadeIn(a3), run_time=0.7)

        # two columns: each answer, and under it what its claims rest on
        col_w, top = 6.2, 3.3
        again = txt(label("m7_asked_again"), size=24, color=GREY_B)
        again_marks = ["[NMWA 2(1)]", "[NMWA 2(2)]"] if UK else ["1,270,000", "[Art. 209]"]
        a3b = fit(answer_box("q3_min_wage_notools2", again_marks, width=62, size=18), col_w)   # wrapped like the left one, so both read at one size
        if UK:
            under_left = fit(VGroup(txt(label("m7_from_memory"), size=24, weight=BOLD, color=RLRED),
                                    txt(label("m7_not_in_corpus"), size=22, color=GREY_B)).arrange(DOWN, buff=0.12), col_w)
            under_right = fit(article_card("NMWA 2", text=paragraph("NMWA 2", "(1)"), chars=120, width=5.6, size=18,
                                           head="NMWA section 2(1)"), col_w)
            cues = ({"en": "But nothing we gave"}, {"en": "We asked the same question"}, {"en": "and section two cited"})
        else:
            under_left = fit(article_card("153", chars=90, width=5.6, size=18), col_w)
            under_right = fit(article_card("209", chars=90, width=5.6, size=18), col_w)
            cues = (None, {"uz": "Xuddi shu savolni"}, {"uz": "Bu modda esa"})
        with self.say("5.41") as (tr, t):
            self.play(FadeOut(q3), a3.animate.scale_to_fit_width(col_w).move_to([-3.45, top, 0], aligned_edge=UP),
                      run_time=0.6)
            if a3.height > 4.6:
                self.play(a3.animate.scale_to_fit_height(4.6).move_to([-3.45, top, 0], aligned_edge=UP), run_time=0.3)
            if cues[0]:
                self.cue(tr, t, cues[0])
            under_left.next_to(a3, DOWN, buff=0.3)
            self.play(FadeIn(under_left), run_time=0.5)
            self.cue(tr, t, cues[1])
            again.move_to([3.45, top, 0], aligned_edge=UP)
            a3b.next_to(again, DOWN, buff=0.15)
            self.play(FadeIn(again), FadeIn(a3b), run_time=0.7)
            self.cue(tr, t, cues[2])
            under_right.next_to(a3b, DOWN, buff=0.3)
            self.play(FadeIn(under_right), run_time=0.5)
        self.clear_all()

        if UK:
            rule = article_card("NMWA 1", "such single hourly rate as the Secretary of State may from time to time "
                                "prescribe", text=paragraph("NMWA 1", "(3)"), chars=200, width=9.5, size=20,
                                head="NMWA section 1(3)").move_to(UP * 0.9)
        else:
            rule = article_card("245", "Prezidenti tomonidan", chars=260, width=9.5, size=19).move_to(UP * 0.9)
        none = txt(label("m7_no_amount"), size=30, weight=BOLD, color=HILITE).next_to(rule, DOWN, buff=0.4)
        steps = len(trace("q3_min_wage")["trace"])
        withtools = VGroup(txt(label("m7_with_tools"), size=26, color=GOOD),
                           tagged(steps, label("m7_steps"), size=26, value_color=GOOD, value_weight=BOLD))
        withtools.arrange(RIGHT, buff=0.3).next_to(none, DOWN, buff=0.35)
        with self.say("5.42") as (tr, t):
            self.play(FadeIn(none), run_time=0.5)
            self.cue(tr, t, {"uz": "Ikki yuz qirq", "en": "Section one says"})
            self.play(FadeIn(rule), run_time=0.6)
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

    def uz_citations(self):
        c183 = article_card("183", "415-moddasi", chars=330, width=9.5, size=19).move_to(UP * 1.2)
        wrong = txt(label("m7_wrong_citation"), size=28, weight=BOLD, color=RLRED).next_to(c183, DOWN, buff=0.35)
        c415 = article_card("415", "haftasiga oʻttiz olti soatdan", chars=160, width=9.5, size=18)
        c415.next_to(wrong, DOWN, buff=0.3)
        with self.say("5.39") as (tr, t):
            self.play(FadeIn(c183), run_time=0.7)
            self.cue(tr, t, {"uz": "Oʻttiz olti ham"})
            self.play(FadeIn(wrong), run_time=0.4)
            self.cue(tr, t, {"uz": "Bu raqamlar"})
            self.play(FadeIn(c415, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

    def uk_citations(self):
        """Each citation opened to its real paragraph: 4(2), 5(1) (repealed), and 5A(1)(a), which nothing cited."""
        def cited(aid, mark, head, note_key, color):
            c = article_card(aid, text=paragraph(aid, mark), chars=150, width=10.5, size=18, head=head)
            note = txt(label(note_key), size=22, weight=BOLD, color=color)
            return fit(VGroup(c, note).arrange(RIGHT, buff=0.35), 12.6)
        c42 = cited("WTR 4", "(2)", "WTR regulation 4(2)", "m7_wrong_citation", RLRED)
        c51 = cited("WTR 5", "(1)", "WTR regulation 5(1)", "m7_repealed", RLRED)
        c5a = cited("WTR 5A", "(a)", "WTR regulation 5A(1)(a)", "m7_never_cited", HILITE)
        VGroup(c42, c51, c5a).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(UP * 0.25)
        with self.say("5.39") as (tr, t):
            self.cue(tr, t, "Paragraph two")
            self.play(FadeIn(c42), run_time=0.6)
            self.cue(tr, t, "The written agreement")
            self.play(FadeIn(c51), run_time=0.6)
            self.cue(tr, t, "And the limit")
            self.play(FadeIn(c5a), run_time=0.6)
        self.clear_all()


SCENES = ["S05NoTools"]
