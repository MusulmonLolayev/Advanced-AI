"""Agent course, section 1 — the agent loop: pipeline vs agent, ReAct, the core loop (run), its bill, prefix
caching, the captured run, and why reliability multiplies (p^k), with the course's first pause.

Live results: raw/s1_agent_loop.json (the water-bottle question, run once against DeepSeek). Deck numbers:
D["bill"], D["cache10"], D["p10"], D["p_low_10"], D["p_low_5"] and capture_deck's inputs (S, A, prices, p).
"""
from agents_course_kit import *

RUN = raw("s1_agent_loop.json")
CALLS = RUN["tool_calls"]                       # [{tool, args}] as the run made them
ORDER = CALLS[0]["args"]["order_id"]
PRODUCT = CALLS[1]["args"]["product_id"]
LOOP_FILE = "s1_agent_loop.py"


def tool_box(name, arg=None, color=HILITE):
    t = mono(name, size=22, color=color)
    g = VGroup(t) if arg is None else VGroup(t, mono(arg, size=20, color=GREY_B)).arrange(DOWN, buff=0.12)
    r = RoundedRectangle(corner_radius=0.12, width=g.width + 0.45, height=g.height + 0.35, stroke_color=color,
                         stroke_width=3)
    return VGroup(r, g.move_to(r))


class S01Pipeline(LectureScene):
    def construct(self):
        self.section_card(1)
        req = tile(label("ac_request"), color=GREY_B, width=2.4, size=24)
        look = tool_box(CALLS[0]["tool"], ORDER)
        ans = tile(label("ac_answer"), color=GOOD, width=2.4, size=24)
        row, arrows = flow_row([req, look, ans], buff=0.8)
        top = VGroup(row, arrows).move_to(UP * 1.4)
        with self.say("1.1") as (tr, t):
            self.play(FadeIn(req), run_time=0.5)
            self.play(GrowArrow(arrows[0]), FadeIn(look), run_time=0.7)
            self.cue(tr, t, {"en": "One lookup, one answer"})
            self.play(GrowArrow(arrows[1]), FadeIn(ans), run_time=0.6)

        # the second lookup's argument comes out of the first result
        second = tool_box(CALLS[1]["tool"], PRODUCT).move_to(DOWN * 1.2)
        found = mono(f'"product_id": "{PRODUCT}"', size=20, color=LBLUE).next_to(look, DOWN, buff=0.35)
        link = Arrow(found.get_bottom(), second.get_top(), buff=0.1, color=LBLUE, stroke_width=4)
        with self.say("1.2") as (tr, t):
            self.cue(tr, t, {"en": "The agent must read the order"})
            self.play(Indicate(look, color=HILITE), run_time=0.6)
            self.cue(tr, t, {"en": "find the bottle's product number"})
            self.play(FadeIn(found, shift=DOWN * 0.2), run_time=0.6)
            self.cue(tr, t, {"en": "only then look that product up"})
            self.play(GrowArrow(link), FadeIn(second), run_time=0.7)

        # pipeline: we chose the steps; agent: the model chooses while it runs
        self.play(FadeOut(VGroup(top, found, link, second)), run_time=0.4)
        model = tile(label("ac_model"), color=LBLUE, width=2.6, size=26).move_to(LEFT * 2.6)
        tools = tile(label("ac_tools_word"), color=HILITE, width=2.6, size=26).move_to(RIGHT * 2.6)
        go = CurvedArrow(model.get_top() + RIGHT * 0.4, tools.get_top() + LEFT * 0.4, angle=-TAU / 6, color=GREY_B)
        back = CurvedArrow(tools.get_bottom() + LEFT * 0.4, model.get_bottom() + RIGHT * 0.4, angle=-TAU / 6, color=HILITE)
        pipe = txt(label("ac_pipeline_rule"), size=28, color=GREY_B).to_edge(UP, buff=SAFE + 0.4)
        agent = txt(label("ac_agent_rule"), size=28, color=HILITE).next_to(back, DOWN, buff=0.4)
        with self.say("1.3") as (tr, t):
            self.play(FadeIn(model), FadeIn(tools), Create(go), run_time=0.8)
            self.cue(tr, t, {"en": "In a pipeline"})
            self.play(FadeIn(pipe), run_time=0.5)
            self.cue(tr, t, {"en": "In an agent"})
            self.play(Create(back), FadeIn(agent), run_time=0.8)
        self.clear_all()


class S01ReAct(LectureScene):
    def construct(self):
        names = [label("ac_thought"), label("ac_action"), label("ac_observation")]
        nodes = VGroup(*[tile(n, color=c, width=2.9, size=26) for n, c in zip(names, (LBLUE, HILITE, RLGREEN))])
        for n, ang in zip(nodes, (90, -30, 210)):
            n.move_to(2.0 * np.array([np.cos(np.radians(ang)) * 1.6, np.sin(np.radians(ang)), 0]) + DOWN * 0.2)
        cyc = VGroup(*[CurvedArrow(a.get_center(), b.get_center(), angle=-TAU / 8, color=GREY_B)
                       for a, b in zip(nodes, [*nodes[1:], nodes[0]])])
        for a in cyc:
            a.scale(0.55)
        react = txt(label("ac_react"), size=26, color=GREY_B).to_edge(UP, buff=SAFE + 0.3)
        with self.say("1.4") as (tr, t):
            self.play(FadeIn(react), run_time=0.4)
            self.cue(tr, t, {"en": "each turn the model writes a thought"})
            for n, a in zip(nodes, cyc):
                self.play(FadeIn(n), Create(a), run_time=0.6)
        self.clear_all()

        # the model emits a request; our code stands between it and the tools
        model = tile(label("ac_model"), color=LBLUE, width=2.4, size=26)
        request = json_block({"name": CALLS[0]["tool"], "arguments": CALLS[0]["args"]}, size=20, chars=30)
        req_box = VGroup(SurroundingRectangle(request, color=GREY_B, buff=0.2, corner_radius=0.1), request)
        gate = tile(label("ac_your_code"), color=HILITE, width=2.4, size=26)
        tools = tile(label("ac_tools_word"), color=GREY_B, width=2.2, size=26)
        row, arrows = flow_row([model, req_box, gate, tools], buff=0.45)
        VGroup(row, arrows).scale_to_fit_width(12.6).move_to(ORIGIN)
        with self.say("1.5") as (tr, t):
            self.play(FadeIn(model), run_time=0.4)
            self.cue(tr, t, {"en": "It emits a request"})
            self.play(GrowArrow(arrows[0]), FadeIn(req_box), run_time=0.6)
            self.cue(tr, t, {"en": "Our code decides"})
            self.play(GrowArrow(arrows[1]), FadeIn(gate), run_time=0.5)
            self.play(GrowArrow(arrows[2]), FadeIn(tools), run_time=0.5)
        self.clear_all()


class S01Code(LectureScene):
    def construct(self):
        panel = code_panel(LOOP_FILE, "def run", 'return "stopped', size=20, tag="run").move_to(UP * 0.3)  # clear of the brand mark
        marks = [(f, highlight(panel, code_lines(LOOP_FILE, f)[0])) for f in
                 ("for _ in range(max_steps)", "messages.append(msg)", "TOOLS[call.function.name]", "if not msg.tool_calls")]
        with self.say("1.6") as (tr, t):
            self.play(FadeIn(panel), run_time=0.8)
            self.cue(tr, t, {"en": "two read-only tools"})
            for _, m in marks:
                self.play(Create(m), run_time=0.45)
                self.wait(0.25)
                self.play(FadeOut(m), run_time=0.25)

        # the messages list: the agent's whole memory, one block per turn (the run's own turns)
        turns = [(label("ac_msg_system"), GREY_B), (label("ac_msg_user"), WHITE)]
        for c in CALLS:                           # tool names are the run's data; the rest are labels
            turns += [(f"→ {c['tool']}", HILITE), (label("ac_msg_tool_result"), GREY_B)]
        turns += [(label("ac_answer"), GOOD)]
        blocks = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.08, width=4.6, height=0.46, stroke_color=c,
                                                  stroke_width=2.5),
                                 mono(n, size=18, color=c)) for n, c in turns])
        for b in blocks:
            b[1].move_to(b[0])
        blocks.arrange(DOWN, buff=0.1)
        cap = mono("messages", size=24, color=LBLUE).next_to(blocks, UP, buff=0.25)
        col = VGroup(cap, blocks).move_to(DOWN * 0.1)
        with self.say("1.7") as (tr, t):
            self.play(FadeOut(panel), run_time=0.4)          # the list is the subject now; a shrunk panel is unreadable
            self.play(FadeIn(cap), run_time=0.3)
            for b in blocks:
                self.play(FadeIn(b, shift=DOWN * 0.1), run_time=0.35)
            self.cue(tr, t, {"en": "The scratchpad is just the context window"})
            self.play(Indicate(blocks, color=LBLUE, scale_factor=1.03), run_time=0.8)
        self.clear_all()


class S01Cost(LectureScene):
    def construct(self):
        bill = D["bill"]
        steps = [int(k) for k in bill]
        pairs = [(MathTex(str(k), font_size=34), bill[str(k)]["billed"]) for k in map(str, steps)]
        rects, tops, labs, floor = bars(pairs, lambda v: f"{v:,}", height=3.6, step=2.4, width=1.2)
        cap = txt(label("ac_steps"), size=24, color=GREY_B).next_to(labs, DOWN, buff=0.2)
        unit = txt(label("ac_input_tokens_billed"), size=26, color=GREY_B).to_edge(UP, buff=SAFE + 0.3)
        ratio = MathTex(rf"\times {D['bill_ratio_20_10']}", font_size=44, color=HILITE).next_to(rects[2], LEFT, buff=0.3)
        with self.say("1.8") as (tr, t):
            self.play(FadeIn(unit), Create(floor), FadeIn(labs), FadeIn(cap), run_time=0.6)
            self.cue(tr, t, {"en": "a ten-step run bills"})
            self.play(GrowFromEdge(rects[0], DOWN), GrowFromEdge(rects[1], DOWN), FadeIn(tops[:2]), run_time=0.8)
            self.cue(tr, t, {"en": "Twenty steps bill"})
            self.play(GrowFromEdge(rects[2], DOWN), FadeIn(tops[2]), run_time=0.7)
            self.cue(tr, t, {"en": "three point four times"})
            self.play(FadeIn(ratio), run_time=0.4)
        self.clear_all()

        # prefix caching: each turn re-sends the previous prompt (cached, grey) plus the new step (blue)
        S_, A_, n = DECK_IN.S, DECK_IN.A, 10
        k = 3.2 / (S_ + (n - 1) * A_)
        cols = VGroup()
        for i in range(n):
            old = (S_ + (i - 1) * A_) if i else 0
            new = S_ if i == 0 else A_
            g = Rectangle(width=0.55, height=max(old * k, 1e-3), stroke_width=0, fill_color=GREY_C, fill_opacity=1)
            b = Rectangle(width=0.55, height=new * k, stroke_width=0, fill_color=LBLUE, fill_opacity=1)
            VGroup(g, b).arrange(UP, buff=0)
            cols.add(VGroup(g, b))
        cols.arrange(RIGHT, buff=0.18, aligned_edge=DOWN).move_to(LEFT * 2.4 + DOWN * 0.4)
        for c in cols:
            if c[0].height < 0.01:
                c[0].set_opacity(0)
        turn = txt(label("ac_turn"), size=22, color=GREY_B).next_to(cols, DOWN, buff=0.25)
        price = VGroup(
            VGroup(Square(0.3, fill_color=GREY_C, fill_opacity=1, stroke_width=0),
                   MathTex(rf"\${DECK_IN.PRICE_CACHED}", font_size=36), txt(label("ac_cached"), size=24, color=GREY_B)),
            VGroup(Square(0.3, fill_color=LBLUE, fill_opacity=1, stroke_width=0),
                   MathTex(rf"\${DECK_IN.PRICE_IN}", font_size=36), txt(label("ac_new"), size=24, color=GREY_B)))
        for p in price:
            p.arrange(RIGHT, buff=0.25)
        per = txt(label("ac_per_million_tokens"), size=22, color=GREY_B)
        c10 = D["cache10"]
        evals = VGroup(MathTex(rf"\${c10['eval_cached']:.2f}", font_size=44, color=GOOD),
                       MathTex(r"\text{vs}", font_size=32, color=GREY_B),
                       MathTex(rf"\${c10['eval_uncached']:.2f}", font_size=44, color=BAD)).arrange(RIGHT, buff=0.3)
        per_q = tagged(f"{DECK_IN.EVAL_QUERIES:,}", label("ac_queries"), size=24, color=GREY_B)
        side = VGroup(price[0], price[1], per, evals, per_q).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        side.next_to(cols, RIGHT, buff=1.0)
        with self.say("1.9") as (tr, t):
            self.play(LaggedStart(*[GrowFromEdge(c, DOWN) for c in cols], lag_ratio=0.1), FadeIn(turn), run_time=1.4)
            self.cue(tr, t, {"en": "billed at a cached rate"})
            self.play(FadeIn(price), FadeIn(per), run_time=0.6)
            self.cue(tr, t, {"en": "On our ten-step run"})
            self.play(FadeIn(evals), FadeIn(per_q), run_time=0.6)

        # a timestamp at the top of the prompt changes the first bytes, so nothing is a cached prefix any more
        stamp = VGroup(Rectangle(width=cols.width + 0.2, height=0.32, stroke_color=BAD, stroke_width=2.5),
                       txt(label("ac_timestamp"), size=18, color=BAD))
        stamp[1].move_to(stamp[0])
        stamp.next_to(cols, DOWN, buff=0.06).shift(UP * 0.0)
        with self.say("1.10") as (tr, t):
            self.cue(tr, t, {"en": "never put a timestamp"})
            self.play(FadeOut(turn), FadeIn(stamp, shift=UP * 0.2), run_time=0.5)
            self.play(*[c[0].animate.set_fill(LBLUE) for c in cols[1:]], run_time=0.8)
        self.clear_all()


class S01Run(LectureScene):
    def construct(self):
        head = VGroup(txt(label("ac_our_run"), size=30, weight=BOLD, color=LBLUE), run_pill()).arrange(RIGHT, buff=0.3)
        head.to_edge(UP, buff=SAFE + 0.3)
        q = bubble("user", RUN["question"], max_chars=60, max_rows=2, size=20)
        calls = VGroup(*[bubble("call", f"{c['tool']}({json.dumps(c['args'])})", max_chars=60, size=20) for c in CALLS])
        answer_rows = [r.replace("**", "") for r in RUN["answer"].splitlines() if r.strip() and not r.startswith("|")][:3]
        ans = bubble("assistant", "\n".join(answer_rows), max_chars=60, max_rows=4, size=20)
        conv = VGroup(q, *calls, ans).arrange(DOWN, buff=0.22, aligned_edge=LEFT).next_to(head, DOWN, buff=0.45)
        conv.scale_to_fit_width(min(11.0, conv.width * 1.45))
        conv.next_to(head, DOWN, buff=0.45).set_x(0)
        tag = captured_tag("s1_agent_loop.json").next_to(conv, DOWN, buff=0.3)
        with self.say("1.11") as (tr, t):
            self.play(FadeIn(head), FadeIn(q), run_time=0.5)
            self.cue(tr, t, {"en": "it read the order"})
            self.play(FadeIn(calls[0], shift=RIGHT * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": "looked the product up"})
            self.play(FadeIn(calls[1], shift=RIGHT * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": "and answered"})
            self.play(FadeIn(ans), FadeIn(tag), run_time=0.5)
        self.wait(1.0)                  # the answer arrives with the line's last words; let it be read
        self.clear_all()


class S01Reliability(LectureScene):
    def construct(self):
        p, p_low = DECK_IN.P_STEP, DECK_IN.P_STEP_LOW
        ax = Axes(x_range=[0, 20, 5], y_range=[0, 1, 0.25], x_length=7.5, y_length=4.2,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 24}).shift(LEFT * 1.5 + DOWN * 0.3)
        xl = txt(label("ac_steps"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = txt(label("ac_run_succeeds"), size=22, color=GREY_B).next_to(ax, UP, buff=0.2).align_to(ax, LEFT)
        c95 = ax.plot(lambda k: p ** k, x_range=[0, 20], color=LBLUE, stroke_width=4)
        d10 = Dot(ax.c2p(10, D["p10"]), color=HILITE, radius=0.09)
        v10 = MathTex(rf"{p}^{{10}} = {D['p10']}", font_size=40, color=HILITE).next_to(ax, RIGHT, buff=0.4).shift(UP * 1.2)
        with self.say("1.12") as (tr, t):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.play(Create(c95), run_time=1.0)
            self.cue(tr, t, {"en": "zero point nine five to the tenth power"})
            self.play(FadeIn(d10, scale=1.5), FadeIn(v10), run_time=0.6)

        graph = VGroup(ax, xl, yl, c95, d10, v10)
        self.play(FadeOut(graph), run_time=0.3)
        card = pause_card_math(rf"p = {p_low:.2f}:\quad k = 10 \;\to\; k = 5")
        with self.say("1.13"):
            self.play(FadeIn(card), run_time=0.5)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.3)

        c90 = ax.plot(lambda k: p_low ** k, x_range=[0, 20], color=HILITE, stroke_width=4)
        d_10 = Dot(ax.c2p(10, D["p_low_10"]), color=BAD, radius=0.09)
        d_5 = Dot(ax.c2p(5, D["p_low_5"]), color=GOOD, radius=0.09)
        ans = VGroup(MathTex(rf"{p_low:.2f}^{{10}} = {D['p_low_10']:.2f}", font_size=40, color=BAD),
                     MathTex(rf"{p_low:.2f}^{{5}} = {D['p_low_5']:.2f}", font_size=40, color=GOOD)) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(ax, RIGHT, buff=0.4).shift(UP * 0.8)
        with self.say("1.14") as (tr, t):
            self.play(FadeIn(ax), FadeIn(xl), FadeIn(yl), Create(c90), run_time=0.8)
            self.play(FadeIn(d_10), FadeIn(ans[0]), run_time=0.5)
            self.play(FadeIn(d_5), FadeIn(ans[1]), run_time=0.5)
        self.clear_all()

        # the guard in our loop: a hard step budget, and its exit
        panel = code_panel(LOOP_FILE, "def run", 'return "stopped', size=20, tag="run").move_to(UP * 0.3)  # clear of the brand mark
        budget = highlight(panel, code_lines(LOOP_FILE, "def run")[0])
        stop = highlight(panel, code_lines(LOOP_FILE, 'return "stopped')[0], color=BAD)
        with self.say("1.15") as (tr, t):
            self.play(FadeIn(panel), run_time=0.6)
            self.play(Create(budget), run_time=0.5)
            self.cue(tr, t, {"en": "stop when it runs out"})
            self.play(Create(stop), run_time=0.5)
        self.clear_all()

        recap(self, "1.16", [label("ac_recap_1_loop"), label("ac_recap_1_cost"), label("ac_recap_1_reliability")])


SCENES = ["S01Pipeline", "S01ReAct", "S01Code", "S01Cost", "S01Run", "S01Reliability"]
