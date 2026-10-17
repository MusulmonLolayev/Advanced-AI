"""Module 7, Lecture 1, section 4 — a real trajectory: the class agent's recorded run on the under-18 question
(agents/class_agent/traces/q2_under18.json), then Q1's first thought (q1_week.json)."""
from m7_lecture01_kit import *

Q2 = turns("q2_under18")
Q1 = turns("q1_week")
assert [re.search(r"\w+", a)[0] for _, a, _ in Q2] == ["search", "fetch_article", "fetch_article", "answer"]


def detail(thought, action, width=38):
    th = trace_line("thought", thought, size=19, width=width)
    ac = trace_line("action", action, size=19, width=width)
    return fit(VGroup(th, ac).arrange(DOWN, aligned_edge=LEFT, buff=0.22), 7.2)


RIGHT_AT = [-1.0, 0.9, 0]                       # the step being taken: from here to x = 6.2


class S04Trace(Scene7):
    def construct(self):
        self.section_card(4)
        head = txt(ARTICLES["1"]["code_title"], size=32, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
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
        log = VGroup()
        log_anchor = q.get_corner(DL) + DOWN * 0.45

        def log_step(k, action):
            item = mono(f"{k}  {short(action, 30)}", size=17, color=GOOD if not action.startswith("answer") else HILITE)
            if len(log):
                item.next_to(log, DOWN, aligned_edge=LEFT, buff=0.18)
            else:
                item.move_to(log_anchor, aligned_edge=UL)
            log.add(item)
            return item

        th, ac, obs = Q2[0]
        d = detail(th, ac).move_to(RIGHT_AT, aligned_edge=UL)
        rows = obs.split("\n")
        olist = VGroup(*[mono(r, size=17, color=HILITE if r.startswith(("Art. 182", "Art. 415")) else GREY_A)
                         for r in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        olist.scale_to_fit_width(min(olist.width, 7.0)).next_to(d, DOWN, aligned_edge=LEFT, buff=0.35)
        ohead = txt(label("m7_observation"), size=22, weight=BOLD, color=GREY_B).next_to(olist, UP, aligned_edge=LEFT, buff=0.1)
        with self.say("4.29") as (tr, t):
            self.play(FadeIn(d[0]), run_time=0.6)
            self.cue(tr, t, {"uz": "Harakat: qidiruv", "en": "Action: search"})
            self.play(FadeIn(d[1]), FadeIn(log_step(1, ac)), run_time=0.6)
            self.cue(tr, t, {"uz": "Kuzatuv:", "en": "Observation:"})
            self.play(FadeIn(ohead), LaggedStart(*[FadeIn(r) for r in olist], lag_ratio=0.2), run_time=1.0)

        th, ac, obs = Q2[1]
        d2 = detail(th, ac).move_to(RIGHT_AT, aligned_edge=UL)
        a182 = fit(article_card("182", "haftasiga qirq soatdan ortiq", chars=150, width=6.4, size=19), 7.2)
        a182.next_to(d2, DOWN, aligned_edge=LEFT, buff=0.35)
        with self.say("4.30") as (tr, t):
            self.play(FadeOut(d), FadeOut(olist), FadeOut(ohead), FadeIn(d2), FadeIn(log_step(2, ac)), run_time=0.7)
            self.cue(tr, t, {"uz": "Unda shunday", "en": "It says"})
            self.play(FadeIn(a182, shift=UP * 0.2), run_time=0.6)

        th, ac, obs = Q2[2]
        d3 = detail(th, ac).move_to(RIGHT_AT, aligned_edge=UL)
        a415 = fit(article_card("415", "haftasiga oʻttiz olti soatdan", chars=230, width=6.4, size=19), 7.2)
        a415.next_to(d3, DOWN, aligned_edge=LEFT, buff=0.35)
        with self.say("4.31") as (tr, t):
            self.play(FadeOut(d2), FadeOut(a182), FadeIn(d3[0]), run_time=0.6)
            self.cue(tr, t, {"uz": "Model toʻrt yuz", "en": "The model fetches"})
            self.play(FadeIn(d3[1]), FadeIn(log_step(3, ac)), run_time=0.5)
            self.play(FadeIn(a415, shift=UP * 0.2), run_time=0.6)

        th, ac, _ = Q2[3]
        answer = fit(trace_line("answer", short(re.sub(r"^answer\[|\]$", "", ac), 330), size=18, width=42), 7.2)
        answer.move_to(RIGHT_AT, aligned_edge=UL)
        with self.say("4.32") as (tr, t):
            self.play(FadeOut(d3), FadeOut(a415), FadeIn(answer), FadeIn(log_step(4, "answer[…]")), run_time=0.8)

        pointer = Arrow(log[2].get_right() + RIGHT * 1.6, log[2].get_right() + RIGHT * 0.1, color=HILITE, buff=0)
        note = txt(label("m7_nobody_asked"), size=24, color=HILITE).next_to(log, DOWN, aligned_edge=LEFT, buff=0.5)
        if note.width > 6.0:
            note.scale_to_fit_width(6.0)
        with self.say("4.33") as (tr, t):
            self.play(FadeOut(answer), run_time=0.3)
            self.play(Indicate(log[2], color=HILITE, scale_factor=1.05), GrowArrow(pointer), run_time=0.8)
            self.play(FadeIn(note), run_time=0.5)
        self.clear_all()

        th1 = Q1[0][0]
        first = trace_line("thought", th1, size=24, width=44).move_to(UP * 0.8)
        key = "likely Article 182"
        body = first[1]
        under = None
        if key in th1:
            under = Underline(body, color=HILITE, buff=0.05)
        when = txt(label("m7_before_search"), size=26, color=HILITE).next_to(first, DOWN, buff=0.6)
        rule = txt(label("m7_cite_read"), size=30, weight=BOLD).next_to(when, DOWN, buff=0.6)
        with self.say("4.34") as (tr, t):
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


SCENES = ["S04Trace"]
