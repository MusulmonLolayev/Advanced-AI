"""Agent course, section 8 — evaluation and safety: a demo is one run; τ²-bench grades the final database; a real
success and a real failure from our run; pass^k (with the course's second pause); our captured retail results and
their judge caveat; the interval on a rate; the harness snippet; indirect prompt injection and its defence in code.

Live results: raw/tau2_retail.json, raw/tau2_retail_trajectory.json, raw/tau2_retail_failure.json. Deck numbers:
D["p10"], D["pass_k_example"], D["ci"] and capture_deck's inputs (P_STEP, PASS_K_*, HALLU_P, Z95, EVAL_SIZES).
"""
from math import comb

from agents_course_kit import *

RETAIL = raw("tau2_retail.json")
OK_RUN = raw("tau2_retail_trajectory.json")
BAD_RUN = raw("tau2_retail_failure.json")
ROWS = chat_messages(OK_RUN["messages"])



def mark(ok, size=0.42):
    """A trial's outcome: a filled square with a tick or a cross."""
    sq = RoundedRectangle(corner_radius=0.06, width=size, height=size, stroke_width=0,
                          fill_color=GOOD if ok else BAD, fill_opacity=1)
    sym = MathTex(r"\checkmark" if ok else r"\times", font_size=34 * size / 0.42, color=BLACK).move_to(sq)
    return VGroup(sq, sym)


def database(caption, color=GREY_B, w=1.5, h=1.3):
    """A database drum with its caption under it."""
    top = Ellipse(width=w, height=0.38, stroke_color=color, stroke_width=3)
    body = VGroup(Line(top.get_left(), top.get_left() + DOWN * h, color=color, stroke_width=3),
                  Line(top.get_right(), top.get_right() + DOWN * h, color=color, stroke_width=3),
                  Arc(radius=w / 2, start_angle=PI, angle=PI, color=color, stroke_width=3)
                  .stretch_to_fit_height(0.19).move_to(top.get_center() + DOWN * h, aligned_edge=UP))
    drum = VGroup(top, body)
    return VGroup(drum, txt(caption, size=22, color=color).next_to(drum, DOWN, buff=0.25))


def pick(rows, role, contains=None, nth=0):
    """The nth chat row of a role whose text contains a phrase (the run's own messages, never retyped)."""
    hits = [r for r in rows if r[0] == role and (contains is None or contains in r[1])]
    return hits[nth]


class S08Demo(LectureScene):
    def construct(self):
        self.section_card(8)
        p, n = DECK_IN.P_STEP, 10
        good = round(n * D["p10"])                 # how many of ten runs look flawless at p^10
        runs = VGroup(*[mark(i < good, size=0.62) for i in range(n)]).arrange(RIGHT, buff=0.25).shift(UP * 0.2)
        cap = txt(label("ac_s8_demo_runs"), size=24, color=GREY_B).next_to(runs, UP, buff=0.4)
        eq = MathTex(rf"{p}^{{10}} = {D['p10']}", font_size=48, color=HILITE).next_to(runs, DOWN, buff=0.7)
        with self.say("8.1") as (tr, t):
            self.play(FadeIn(cap), FadeIn(runs[0]), run_time=0.5)
            self.cue(tr, t, {"en": "At ninety-five percent per step"})
            self.play(LaggedStart(*[FadeIn(r, scale=1.3) for r in runs[1:]], lag_ratio=0.15), run_time=1.5)
            self.cue(tr, t, {"en": "three times in five"})
            self.play(FadeIn(eq), run_time=0.5)
        self.clear_all()


class S08Grading(LectureScene):
    def construct(self):
        final = database(label("ac_s8_final_db"), color=LBLUE).shift(LEFT * 3)
        target = database(label("ac_s8_expected_db"), color=GOOD).shift(RIGHT * 3)
        eq = MathTex("=", font_size=80, color=HILITE).move_to((final[0].get_center() + target[0].get_center()) / 2)
        msgs = txt(label("ac_s8_required_messages"), size=26, color=GREY_B).next_to(VGroup(final, target), DOWN, buff=0.6)
        with self.say("8.2") as (tr, t):
            self.cue(tr, t, {"en": "It compares the final database"})
            self.play(FadeIn(final), run_time=0.5)
            self.cue(tr, t, {"en": "with the state a correct solution"})
            self.play(FadeIn(target), FadeIn(eq), run_time=0.6)
            self.cue(tr, t, {"en": "checks the agent said"})
            self.play(FadeIn(msgs), run_time=0.4)
        self.clear_all()

        # any path to the right database passes; a correct refusal leaves it as it was and passes too
        db = database(label("ac_s8_expected_db"), color=GOOD).move_to(RIGHT * 3.8 + UP * 0.6)
        start = Dot(LEFT * 5 + UP * 0.6, color=WHITE, radius=0.1)

        def path(ys, color):
            pts = [start.get_center()] + [np.array([-5 + 7.6 * (i + 1) / (len(ys) + 1), 0.6 + y, 0]) for i, y in
                                          enumerate(ys)] + [db[0].get_left() + LEFT * 0.1]
            dots = VGroup(*[Dot(q, color=color, radius=0.08) for q in pts[1:-1]])
            line = VMobject(color=color, stroke_width=4).set_points_smoothly(pts)
            return VGroup(line, dots)
        a = path([1.2, 1.5, 1.0, 0.6], LBLUE)
        b = path([-0.9, -1.3, -0.7], HILITE)
        la = txt(label("ac_s8_path_a"), size=22, color=LBLUE).next_to(a, UP, buff=0.15)
        lb = txt(label("ac_s8_path_b"), size=22, color=HILITE).next_to(b, DOWN, buff=0.15)
        ok = mark(True, size=0.5).next_to(db[0], UP, buff=0.2)
        refusal = VGroup(bubble("assistant", label("ac_s8_refusal"), size=22),
                         txt(label("ac_s8_db_unchanged"), size=22, color=GOOD)).arrange(RIGHT, buff=0.5)
        refusal.add(mark(True, size=0.5).next_to(refusal, RIGHT, buff=0.3)).to_edge(DOWN, buff=SAFE + 0.5)
        with self.say("8.3") as (tr, t):
            self.play(FadeIn(start), FadeIn(db), run_time=0.4)
            self.play(Create(a), FadeIn(la), run_time=0.8)
            self.cue(tr, t, {"en": "any path"})
            self.play(Create(b), FadeIn(lb), FadeIn(ok), run_time=0.8)
            self.cue(tr, t, {"en": "a correct refusal"})
            self.play(FadeIn(refusal, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S08Trajectory(LectureScene):
    def construct(self):
        head = VGroup(tagged(OK_RUN["task_id"], label("ac_s8_task"), after=False, size=30, weight=BOLD, color=LBLUE),
                      tagged(OK_RUN["turns"], label("ac_s8_messages_word"), size=26, color=GREY_B),
                      tagged(OK_RUN["tool_calls"], label("ac_s8_tool_calls_word"), size=26, color=GREY_B),
                      run_pill()).arrange(RIGHT, buff=0.55).to_edge(UP, buff=SAFE + 0.25)
        # the lookup half of the conversation, then the write half: the run's own rows
        look = [pick(ROWS, "user"), pick(ROWS, "call", "find_user_id"), pick(ROWS, "call", "list_all_product"),
                pick(ROWS, "call", "get_user_details"), pick(ROWS, "call", "get_product_details"),
                pick(ROWS, "call", "get_order_details")]
        write = [pick(ROWS, "user", nth=2), pick(ROWS, "user", nth=3), pick(ROWS, "call", "modify_pending", 0),
                 pick(ROWS, "call", "modify_pending", 1), pick(ROWS, "assistant", "successfully")]
        page1 = chat_panel(look, size=18, max_rows=2, width=12).next_to(head, DOWN, buff=0.35)
        page2 = chat_panel(write, size=18, max_rows=2, width=12).next_to(head, DOWN, buff=0.35)
        tag = captured_tag("tau2_retail_trajectory.json").to_edge(DOWN, buff=SAFE + 0.15)

        # the grade: the final database against the expected one, and the reward the benchmark gave
        final = database(label("ac_s8_final_db"), color=LBLUE).shift(LEFT * 2.6 + UP * 0.2)
        target = database(label("ac_s8_expected_db"), color=GOOD).shift(RIGHT * 2.6 + UP * 0.2)
        eq = MathTex("=", font_size=80, color=HILITE).move_to((final[0].get_center() + target[0].get_center()) / 2)
        reward = tagged(f"{OK_RUN['reward']:g}", label("ac_s8_reward"), after=False, size=40, weight=BOLD, color=GOOD)
        reward.next_to(VGroup(final, target), DOWN, buff=0.5)
        with self.say("8.4") as (tr, t):
            self.play(FadeIn(head[0]), FadeIn(tag), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in page1], lag_ratio=0.3), run_time=1.8)
            self.cue(tr, t, {"en": "twenty-six messages"})
            self.play(FadeIn(head[1:]), run_time=0.4)
            self.cue(tr, t, {"en": "between the simulated customer"})
            self.play(FadeOut(page1), run_time=0.3)
            self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in page2], lag_ratio=0.3), run_time=1.6)
            self.cue(tr, t, {"en": "a reward of one"})
            self.play(FadeOut(page2), FadeIn(final), FadeIn(target), FadeIn(eq), run_time=0.5)
            self.play(FadeIn(reward, scale=1.2), run_time=0.4)
        self.wait(0.8)                  # the reward lands with the line's last words; let it be read
        self.clear_all()


class S08Failure(LectureScene):
    def construct(self):
        why = BAD_RUN["why"]
        head = VGroup(tagged(BAD_RUN["task_id"], label("ac_s8_task"), after=False, size=30, weight=BOLD, color=BAD),
                      tagged(BAD_RUN["tool_calls"], label("ac_s8_tool_calls_word"), size=26, color=GREY_B)) \
            .arrange(RIGHT, buff=0.55).to_edge(UP, buff=SAFE + 0.3)
        reason = txt(label("ac_s8_benchmark_reason"), size=24, color=GREY_B).next_to(head, DOWN, buff=0.5)
        db = VGroup(txt(label("ac_s8_db_matches"), size=28), mark(why["db_match"], size=0.5)).arrange(RIGHT, buff=0.4)
        miss = why["expected_actions_not_taken"][0]
        call = mono(f"{miss['name']}(", size=22, color=BAD, weight=BOLD)
        args = json_block(miss["arguments"], size=20, color=GREY_A, chars=48)
        missed = VGroup(VGroup(call, args).arrange(DOWN, aligned_edge=LEFT, buff=0.15),
                        txt(label("ac_s8_expected_not_taken"), size=24, color=BAD)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        box = SurroundingRectangle(missed, color=BAD, buff=0.3, corner_radius=0.12)
        body = VGroup(db, VGroup(box, missed)).arrange(DOWN, buff=0.6).next_to(reason, DOWN, buff=0.45)
        tag = captured_tag("tau2_retail_failure.json").to_edge(DOWN, buff=SAFE + 0.15)
        with self.say("8.5") as (tr, t):
            self.play(FadeIn(head), run_time=0.4)
            self.cue(tr, t, {"en": "the benchmark's own reason"})
            self.play(FadeIn(reason), FadeIn(db), run_time=0.5)
            self.play(Create(box), FadeIn(missed), FadeIn(tag), run_time=0.7)
        self.clear_all()


class S08PassK(LectureScene):
    def construct(self):
        n, c = DECK_IN.PASS_K_TRIALS, DECK_IN.PASS_K_SUCCESSES
        fail_at = 2                                   # the one failure is drawn third: ✓ ✓ ✗ ✓
        trials = VGroup(*[mark(i != fail_at or c == n, size=0.8) for i in range(n)]).arrange(RIGHT, buff=0.35)
        cap = txt(label("ac_s8_one_task_four_trials"), size=26, color=GREY_B).next_to(trials, UP, buff=0.45)
        group = VGroup(cap, trials).move_to(UP * 0.4)
        with self.say("8.6") as (tr, t):
            self.cue(tr, t, {"en": "runs each task several times"})
            self.play(FadeIn(cap), LaggedStart(*[FadeIn(m, scale=1.3) for m in trials], lag_ratio=0.25), run_time=1.2)
            self.cue(tr, t, {"en": "all succeed"})
            self.play(Indicate(trials, color=HILITE, scale_factor=1.05), run_time=0.8)
        self.play(FadeOut(group), run_time=0.3)

        card = pause_card_math(rf"{c}/{n}:\quad \mathrm{{pass}}^{{1}} = \,?\qquad \mathrm{{pass}}^{{{n}}} = \,?")
        with self.say("8.7"):
            self.play(FadeIn(card), run_time=0.5)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.3)

        ex = D["pass_k_example"]
        pairs = [(MathTex(rf"k={k}", font_size=32), ex[str(k)]) for k in range(1, n + 1)]
        rects, tops, labs, floor = bars(pairs, lambda v: f"{v:g}", height=3.2, step=2.0, width=1.0, vmax=1)
        formula = MathTex(rf"\mathrm{{pass}}^k = \binom{{{c}}}{{k}} \Big/ \binom{{{n}}}{{k}}", font_size=44,
                          color=HILITE).to_edge(UP, buff=SAFE + 0.4)
        chart = VGroup(rects, tops, labs, floor).next_to(formula, DOWN, buff=0.6)
        with self.say("8.8") as (tr, t):
            self.play(FadeIn(formula), Create(chart[3]), FadeIn(chart[2]), run_time=0.5)
            for k, cue in ((0, "Pass to the one"), (1, "Pass to the two"), (3, "Pass to the four")):
                self.cue(tr, t, {"en": cue})
                todo = [k] if k != 3 else [2, 3]
                self.play(*[GrowFromEdge(rects[i], DOWN) for i in todo], *[FadeIn(tops[i]) for i in todo],
                          run_time=0.5)
        self.clear_all()


class S08Results(LectureScene):
    def construct(self):
        # every task × trial of our run, as the benchmark graded it
        by_task = sorted(RETAIL["rewards_by_task"].items(), key=lambda kv: int(kv[0]))
        grid = VGroup(*[VGroup(*[mark(r == 1, size=0.38) for r in rs]).arrange(DOWN, buff=0.1) for _, rs in by_task])
        grid.arrange(RIGHT, buff=0.14)
        ids = VGroup(*[mono(tid, size=16, color=GREY_B).next_to(col, UP, buff=0.12) for (tid, _), col in
                       zip(by_task, grid)])
        g_cap = VGroup(tagged(RETAIL["n_tasks"], label("ac_s8_tasks"), size=24, color=GREY_B),
                       MathTex(r"\times", font_size=30, color=GREY_B),
                       tagged(RETAIL["n_trials"], label("ac_s8_trials"), size=24, color=GREY_B)).arrange(RIGHT, buff=0.2)
        left = VGroup(g_cap, VGroup(ids, grid)).arrange(DOWN, buff=0.35).move_to(LEFT * 3.4 + UP * 0.3)

        pk = RETAIL["pass_hat_k"]
        pairs = [(MathTex(rf"k={k}", font_size=30), pk[k]) for k in sorted(pk, key=int)]
        rects, tops, labs, floor = bars(pairs, lambda v: f"{v:.2f}", height=2.8, step=1.6, width=0.9, vmax=1,
                                        size=24)
        name = MathTex(r"\mathrm{pass}^k", font_size=40, color=LBLUE)
        chart = VGroup(rects, tops, labs, floor)
        right = VGroup(name, chart).arrange(DOWN, buff=0.4).move_to(RIGHT * 3.3 + UP * 0.5)
        cost = VGroup(MathTex(rf"\${RETAIL['cost_usd']:.2f}", font_size=40, color=HILITE),
                      txt(label("ac_s8_cost"), size=22, color=GREY_B)).arrange(RIGHT, buff=0.25).next_to(right, DOWN, buff=0.45)
        caveat = txt(label("ac_s8_judge_caveat"), size=20, color=HILITE).to_edge(DOWN, buff=SAFE + 0.55)
        tag = captured_tag("tau2_retail.json").next_to(caveat, DOWN, buff=0.12)
        with self.say("8.9") as (tr, t):
            self.play(FadeIn(g_cap), FadeIn(ids), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(col, shift=DOWN * 0.1) for col in grid], lag_ratio=0.12),
                      FadeIn(caveat), FadeIn(tag), run_time=1.4)
            self.cue(tr, t, {"en": "Pass to the one was"})
            self.play(FadeIn(name), Create(floor), FadeIn(labs), GrowFromEdge(rects[0], DOWN), FadeIn(tops[0]),
                      run_time=0.6)
            self.cue(tr, t, {"en": "fell to"})
            self.play(*[GrowFromEdge(r, DOWN) for r in rects[1:]], *[FadeIn(x) for x in tops[1:]], run_time=0.7)
            self.cue(tr, t, {"en": "The whole run cost"})
            self.play(FadeIn(cost), run_time=0.4)

        # the caveat, in the run file's own words
        note = VGroup(*[mono(r, size=20, color=GREY_A) for r in textwrap.wrap(RETAIL["note"], 58)]) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        note_box = VGroup(SurroundingRectangle(note, color=HILITE, buff=0.3, corner_radius=0.12), note)
        with self.say("8.10") as (tr, t):
            self.play(FadeOut(VGroup(left, right, cost)), caveat.animate.to_edge(UP, buff=SAFE + 0.4), run_time=0.5)
            self.play(FadeIn(note_box.move_to(ORIGIN)), tag.animate.next_to(note_box, DOWN, buff=0.3), run_time=0.6)
        self.clear_all()


class S08Interval(LectureScene):
    def construct(self):
        p, z = DECK_IN.HALLU_P, DECK_IN.Z95
        small, big = 20, 200
        half = lambda n: 100 * z * np.sqrt(p * (1 - p) / n)
        ax = Axes(x_range=[0, 220, 50], y_range=[0, 20, 5], x_length=8.5, y_length=4.2,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 24}).shift(DOWN * 0.6 + LEFT * 0.6)
        xl = txt(label("ac_s8_tasks_in_test"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = txt(label("ac_s8_ci_half_width"), size=22, color=GREY_B).next_to(ax, UP, buff=0.45).align_to(ax, LEFT)
        n0 = (100 * z * np.sqrt(p * (1 - p)) / 19.5) ** 2      # where the curve enters the 0-20 axis
        curve = ax.plot(half, x_range=[n0, 220], color=LBLUE, stroke_width=4)
        rate = MathTex(rf"p = {p:.2f}", font_size=36, color=GREY_B).next_to(ax, RIGHT, buff=0.3).shift(UP * 1.6)
        pts = VGroup()
        for n, col in ((small, BAD), (big, GOOD)):
            d = Dot(ax.c2p(n, D["ci"][str(n)]), color=col, radius=0.1)
            v = MathTex(rf"n={n}:\ \pm{D['ci'][str(n)]}", font_size=34, color=col).next_to(d, UR, buff=0.15)
            pts.add(VGroup(d, v))
        with self.say("8.11") as (tr, t):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.7)
            self.cue(tr, t, {"en": "At a true rate near twenty percent"})
            self.play(Create(curve), FadeIn(rate), run_time=0.9)
            self.cue(tr, t, {"en": "a twenty-task test"})
            self.play(FadeIn(pts[0], scale=1.3), run_time=0.5)
            self.cue(tr, t, {"en": "Two hundred tasks"})
            self.play(FadeIn(pts[1], scale=1.3), run_time=0.5)
        self.clear_all()

        f = "s7_eval_harness.py"
        panel = code_panel(f, "def run_suite", "for r in results.values()", size=20, tag="shown").move_to(UP * 0.3)  # clear of the brand mark
        with self.say("8.12") as (tr, t):
            self.play(FadeIn(panel), run_time=0.6)
            self.cue(tr, t, {"en": "several runs per task"})
            m1 = highlight(panel, code_lines(f, "for _ in range(trials)")[0])
            self.play(Create(m1), run_time=0.4)
            self.cue(tr, t, {"en": "graded by its final state"})
            m2 = highlight(panel, code_lines(f, "final_db == t.expected_db")[0])
            self.play(ReplacementTransform(m1, m2), run_time=0.4)
            self.cue(tr, t, {"en": "pass to the k from the counts"})
            m3 = highlight(panel, code_lines(f, "return sum(comb")[0], last=code_lines(f, "for r in results.values()")[0])
            self.play(ReplacementTransform(m2, m3), run_time=0.4)
        self.clear_all()


class S08Injection(LectureScene):
    def construct(self):
        page_box = RoundedRectangle(corner_radius=0.12, width=6.2, height=3.6, stroke_color=GREY_B, stroke_width=2.5)
        title = txt(label("ac_s8_kb_page"), size=24, color=GREY_B).next_to(page_box.get_top(), DOWN, buff=0.25)
        filler = VGroup(*[Rectangle(width=w, height=0.13, stroke_width=0, fill_color=GREY_D, fill_opacity=1)
                          for w in (5.2, 4.6, 5.0)]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        planted = VGroup(*[txt(r, size=22, color=BAD) for r in textwrap.wrap(label("ac_s8_planted"), 40)]) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        more = Rectangle(width=4.0, height=0.13, stroke_width=0, fill_color=GREY_D, fill_opacity=1)
        body = VGroup(filler, planted, more).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(title, DOWN, buff=0.3)
        page = VGroup(page_box, title, body).move_to(LEFT * 3.2)
        note = txt(label("ac_s8_illustration"), size=20, color=DIM).next_to(page_box, DOWN, buff=0.25)

        # the model's context: our instructions, the customer, and the page, all in one channel
        ctx = VGroup(tile(label("ac_s8_ctx_system"), color=LBLUE, width=4.8, size=22),
                     tile(label("ac_s8_ctx_user"), color=GREY_B, width=4.8, size=22),
                     tile(label("ac_s8_ctx_doc"), color=BAD, width=4.8, size=22)).arrange(DOWN, buff=0.15)
        ctx_cap = txt(label("ac_s8_context"), size=24, color=GREY_B).next_to(ctx, UP, buff=0.3)
        right = VGroup(ctx_cap, ctx).move_to(RIGHT * 3.4)
        arrow = Arrow(page_box.get_right(), ctx[2].get_left(), buff=0.15, color=BAD, stroke_width=4)
        with self.say("8.13") as (tr, t):
            self.play(FadeIn(page_box), FadeIn(title), FadeIn(filler), FadeIn(more), FadeIn(note), run_time=0.6)
            self.cue(tr, t, {"en": "in the same channel as our instructions"})
            self.play(FadeIn(ctx_cap), FadeIn(ctx[:2]), run_time=0.5)
            self.play(GrowArrow(arrow), FadeIn(ctx[2]), run_time=0.5)
            self.cue(tr, t, {"en": "one planted sentence"})
            self.play(FadeIn(planted), run_time=0.5)
            self.play(Indicate(planted, color=BAD, scale_factor=1.04), run_time=0.7)
        self.clear_all()


class S08Defence(LectureScene):
    def construct(self):
        f = "s8_injection_defence.py"
        rule = txt(label("ac_s8_prompt_rule"), size=30, color=GREY_B).move_to(UP * 0.4)
        strike = Line(rule.get_left() + LEFT * 0.1, rule.get_right() + RIGHT * 0.1, color=BAD, stroke_width=5)
        verdict = txt(label("ac_s8_not_a_defence"), size=28, color=BAD).next_to(rule, DOWN, buff=0.5)
        panel = code_panel(f, "def wrap_untrusted", "return None", size=19, tag="shown").move_to(UP * 0.35)
        sandbox = tile(label("ac_s8_sandbox"), color=GOOD, size=24).to_edge(DOWN, buff=SAFE + 0.35)
        with self.say("8.14") as (tr, t):
            self.play(FadeIn(rule), run_time=0.4)
            self.cue(tr, t, {"en": "is not a defence"})
            self.play(Create(strike), FadeIn(verdict), run_time=0.5)
            self.cue(tr, t, {"en": "Real defences limit"})
            self.play(FadeOut(VGroup(rule, strike, verdict)), run_time=0.3)
            self.play(FadeIn(panel), run_time=0.6)
            self.cue(tr, t, {"en": "wraps every tool result"})
            m = highlight(panel, code_lines(f, "def wrap_untrusted")[0])
            self.play(Create(m), run_time=0.4)
            self.cue(tr, t, {"en": "refuses a write"})
            m2 = highlight(panel, code_lines(f, 'return "refused: acts on another user"')[0])
            self.play(ReplacementTransform(m, m2), run_time=0.4)
            self.cue(tr, t, {"en": "asks for an explicit yes"})
            m3 = highlight(panel, code_lines(f, "if not confirm(")[0])
            self.play(ReplacementTransform(m2, m3), run_time=0.4)
            self.cue(tr, t, {"en": "it also gets a sandbox"})
            self.play(FadeIn(sandbox, shift=UP * 0.2), run_time=0.5)
        self.clear_all()

        recap(self, "8.15", [label("ac_recap_8_outcomes"), label("ac_recap_8_reliability"),
                             label("ac_recap_8_interval"), label("ac_recap_8_blast")])


SCENES = ["S08Demo", "S08Grading", "S08Trajectory", "S08Failure", "S08PassK", "S08Results", "S08Interval",
          "S08Injection", "S08Defence"]
