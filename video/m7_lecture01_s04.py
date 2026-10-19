"""Module 7, Lecture 1, section 4 — a real trajectory: the class agent's recorded run on the under-18 question
(traces/q2_under18.json; English: traces/uk/q2_under18.json), then one first Thought written before any reading
(Uzbek: q1_week's "likely Article 182"; English: q3_min_wage's "or delegates it to regulations")."""
from m7_lecture01_kit import *

Q2 = turns("q2_under18")
if UK:
    assert [re.search(r"\w+", a)[0] for _, a, _ in Q2] == ["search", "fetch", "fetch", "search", "fetch", "answer"]
else:
    assert [re.search(r"\w+", a)[0] for _, a, _ in Q2] == ["search", "fetch_article", "fetch_article", "answer"]
FIRST = turns("q3_min_wage" if UK else "q1_week")[0][0]          # a first Thought, written before any reading
REMEMBERED = "or delegates it to regulations" if UK else "likely Article 182"
LIT = ("WTR 4", "WTR 5A") if UK else ("Art. 182", "Art. 415")    # the search rows the narration names


def detail(thought, action, width=38):
    th = trace_line("thought", thought, size=19, width=width)
    ac = trace_line("action", action, size=19, width=width)
    return fit(VGroup(th, ac).arrange(DOWN, aligned_edge=LEFT, buff=0.22), 7.2)


def result_list(obs, lit=()):
    rows = obs.split("\n")
    g = VGroup(*[mono(short(r, 54), size=17, color=HILITE if r.startswith(lit) else GREY_A) for r in rows])
    g.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    return g.scale_to_fit_width(min(g.width, 7.0))


RIGHT_AT = [-1.0, 0.9, 0]                       # the step being taken: from here to x = 6.2


class S04Trace(Scene7):
    def construct(self):
        self.section_card(4)
        head = law_title(size=30 if UK else 32).to_edge(UP, buff=SAFE + 0.3)
        count = tagged(len(ARTICLES), label("m7_articles"), size=30, value_color=HILITE, value_weight=BOLD)
        count.next_to(head, DOWN, buff=0.3)
        real = txt(label("m7_real_run"), size=24, color=GREY_B).next_to(count, DOWN, buff=0.3)
        with self.say("4.27") as (tr, t):
            self.play(FadeIn(head), FadeIn(count), run_time=0.7)
            self.cue(tr, t, {"uz": "Agent boshida", "en": "At the start"})
            self.play(FadeIn(real), run_time=0.5)
        self.clear_all()

        q = VGroup(txt(label("m7_q_week"), size=26, weight=BOLD), txt(label("m7_q_minors"), size=26, color=HILITE))
        q.arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UL, buff=SAFE + 0.2)
        with self.say("4.28") as (tr, t):
            self.play(FadeIn(q), run_time=0.7)

        # the left column keeps one line per step; the right side shows the step being taken
        self.log = VGroup()
        self.log_anchor = q.get_corner(DL) + DOWN * 0.45

        th, ac, obs = Q2[0]
        d = detail(th, ac).move_to(RIGHT_AT, aligned_edge=UL)
        olist = result_list(obs, LIT).next_to(d, DOWN, aligned_edge=LEFT, buff=0.6)
        ohead = txt(label("m7_observation"), size=22, weight=BOLD, color=GREY_B).next_to(olist, UP, aligned_edge=LEFT, buff=0.1)
        with self.say("4.29") as (tr, t):
            self.play(FadeIn(d[0]), run_time=0.6)
            self.cue(tr, t, {"uz": "Harakat: qidiruv", "en": "Action: search"})
            self.play(FadeIn(d[1]), FadeIn(self.log_step(1, ac)), run_time=0.6)
            self.cue(tr, t, {"uz": "Kuzatuv:", "en": "Observation:"})
            self.play(FadeIn(ohead), LaggedStart(*[FadeIn(r) for r in olist], lag_ratio=0.2), run_time=1.0)

        th, ac, obs = Q2[1]
        d2 = detail(th, ac).move_to(RIGHT_AT, aligned_edge=UL)
        if UK:
            a_week = fit(article_card(*FACT["week"], text=paragraph("WTR 4", "(1)"), lead=300, chars=300, width=6.4,
                                      size=19), 7.2)
        else:
            a_week = fit(article_card(*FACT["week"], chars=150, width=6.4, size=19), 7.2)
        a_week.next_to(d2, DOWN, aligned_edge=LEFT, buff=0.35)
        with self.say("4.30") as (tr, t):
            self.play(FadeOut(d), FadeOut(olist), FadeOut(ohead), FadeIn(d2), FadeIn(self.log_step(2, ac)), run_time=0.7)
            self.cue(tr, t, {"uz": "Unda shunday", "en": "It says"})
            self.play(FadeIn(a_week, shift=UP * 0.2), run_time=0.6)

        th, ac, obs = Q2[2]
        d3 = detail(th, ac).move_to(RIGHT_AT, aligned_edge=UL)
        if UK:
            a_minors = fit(article_card("WTR 5A", "40 hours a week", chars=120, width=6.4, size=19, lead=200,
                                        text=paragraph("WTR 5A", "(1)") + " " + paragraph("WTR 5A", "(a)") + " "
                                        + paragraph("WTR 5A", "(b)")), 7.2)
        else:
            a_minors = fit(article_card(*FACT["minors"], chars=230, width=6.4, size=19), 7.2)
        a_minors.next_to(d3, DOWN, aligned_edge=LEFT, buff=0.35)
        with self.say("4.31") as (tr, t):
            self.play(FadeOut(d2), FadeOut(a_week), FadeIn(d3[0]), run_time=0.6)
            self.cue(tr, t, {"uz": "Model toʻrt yuz", "en": "The model fetches"})
            self.play(FadeIn(d3[1]), FadeIn(self.log_step(3, ac)), run_time=0.5)
            self.play(FadeIn(a_minors, shift=UP * 0.2), run_time=0.6)
        last = VGroup(d3, a_minors)

        if UK:                                  # steps 4-5: a search for the term, then the definitions
            th4, ac4, obs4 = Q2[3]
            th5, ac5, _ = Q2[4]
            d4 = detail(th4, ac4).move_to(RIGHT_AT, aligned_edge=UL)
            list4 = result_list(obs4).next_to(d4, DOWN, aligned_edge=LEFT, buff=0.3)
            d5 = detail(th5, ac5).move_to(RIGHT_AT, aligned_edge=UL)
            a2 = fit(article_card("WTR 2", "attained the age of 15 but not the age of 18", chars=170, width=6.4, size=19,
                                  lead=20, head="WTR regulation 2 · Interpretation"), 7.2)
            a2.next_to(d5, DOWN, aligned_edge=LEFT, buff=0.35)
            with self.say("4.32") as (tr, t):
                self.play(FadeOut(last), FadeIn(d4), FadeIn(self.log_step(4, ac4)), run_time=0.6)
                self.play(LaggedStart(*[FadeIn(r) for r in list4], lag_ratio=0.15), run_time=0.8)
                self.cue(tr, t, "then fetches regulation two")
                self.play(FadeOut(d4), FadeOut(list4), FadeIn(d5), FadeIn(self.log_step(5, ac5)), run_time=0.6)
                self.play(FadeIn(a2, shift=UP * 0.2), run_time=0.6)
            last, asked = VGroup(d5, a2), 4
            answer_key, answer_step = "4.32a", 6
        else:
            asked, answer_key, answer_step = 2, "4.32", 4

        _, ac, _ = Q2[-1]
        answer = fit(trace_line("answer", short(re.sub(r"^answer\[|\]$", "", ac), 330), size=18, width=42), 7.2)
        answer.move_to(RIGHT_AT, aligned_edge=UL)
        with self.say(answer_key) as (tr, t):
            self.play(FadeOut(last), FadeIn(answer), FadeIn(self.log_step(answer_step, "answer[…]")), run_time=0.8)

        log = self.log
        pointer = Arrow(log[asked].get_right() + RIGHT * 1.6, log[asked].get_right() + RIGHT * 0.1, color=HILITE, buff=0)
        note = txt(label("m7_nobody_asked"), size=24, color=HILITE).next_to(log, DOWN, aligned_edge=LEFT, buff=0.5)
        if note.width > 6.0:
            note.scale_to_fit_width(6.0)
        with self.say("4.33") as (tr, t):
            self.play(FadeOut(answer), run_time=0.3)
            self.play(Indicate(log[asked], color=HILITE, scale_factor=1.05), GrowArrow(pointer), run_time=0.8)
            if UK:                              # the step-4 list, with no WTR 2 in it
                self.cue(tr, t, "did not even list")
                again = result_list(Q2[3][2]).move_to(RIGHT_AT + RIGHT * 0.6, aligned_edge=UL)
                self.play(FadeIn(again), run_time=0.5)
            self.play(FadeIn(note), run_time=0.5)
        self.clear_all()

        first = trace_line("thought", FIRST, size=24, width=44).move_to(UP * 0.8)
        under = Underline(first[1], color=HILITE, buff=0.05) if REMEMBERED in FIRST else None
        when = txt(label("m7_before_search"), size=26, color=HILITE).next_to(first, DOWN, buff=0.6)
        rule = txt(label("m7_cite_read"), size=30, weight=BOLD).next_to(when, DOWN, buff=0.6)
        if UK:
            which = txt(label("m7_q_wage"), size=24, color=GREY_B).next_to(first, UP, buff=0.5)
        with self.say("4.34") as (tr, t):
            if UK:
                self.play(FadeIn(which), run_time=0.4)
            self.play(FadeIn(first), run_time=0.6)
            if under is not None:
                self.play(Create(under), FadeIn(when), run_time=0.6)
            self.cue(tr, t, {"uz": "Chunki u", "en": "Because it must"})
            self.play(FadeIn(rule, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        card = pause([label("m7_pause_daily"), label("m7_pause_which_articles")])
        with self.say("4.35") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
        self.hands_on()
        self.clear_all()
        with self.say("4.36") as (tr, t):
            self.play(FadeIn(txt(label("m7_no_tools"), size=40, weight=BOLD, color=HILITE)), run_time=0.7)
        self.clear_all()

    def log_step(self, k, action):
        item = mono(f"{k}  {short(action, 30)}", size=17, color=GOOD if not action.startswith("answer") else HILITE)
        if len(self.log):
            item.next_to(self.log, DOWN, aligned_edge=LEFT, buff=0.18)
        else:
            item.move_to(self.log_anchor, aligned_edge=UL)
        self.log.add(item)
        return item


SCENES = ["S04Trace"]
