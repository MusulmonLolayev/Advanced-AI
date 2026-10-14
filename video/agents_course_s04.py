"""Agent course, section 4 — multi-agent orchestration: a subagent as context isolation, what splitting does to the
bill (fewer raw tokens, colder caches) and to reliability (more steps), the one exception (a checker that can say
no), where it belongs (in front of the store's write tools), the orchestrator snippet (shown, not run), the
verifier's boundary, the human checkpoint in τ²-bench's own policy, and retry / fallback / escalate.

Deck numbers: D["orch"], D["verifier"], D["p_step"]. Testbed facts: raw/tau2_retail_tools.json (16 tools with their
types), raw/tau2_retail_policy.md (the confirmation rule), the retail catalogue and the s1 run's order from the
τ²-bench clone (capture_deck's RETAIL path), raw/s1_agent_loop.json (the order the lookup agent reads).
"""
from agents_course_kit import *

O = D["orch"]
V = D["verifier"]
SNIP = "s4_orchestrator.py"
_DB = json.loads((DECK_IN.RETAIL / "db.json").read_text())
_RUN = raw("s1_agent_loop.json")
_ORDER = _DB["orders"][_RUN["tool_calls"][0]["args"]["order_id"]]
_PRODUCT = _RUN["tool_calls"][1]["args"]["product_id"]
ITEM = next(i for i in _ORDER["items"] if i["product_id"] == _PRODUCT)      # the water bottle in the s1 order
CATALOGUE = sorted({p["name"] for p in _DB["products"].values()})
TOOLS = raw("tau2_retail_tools.json")["tools"]
POLICY_RULE = next(r for r in (RAWDIR / "tau2_retail_policy.md").read_text().splitlines()
                   if "explicit user confirmation" in r)


def num(v, size=34, color=WHITE):
    return MathTex(v if isinstance(v, str) else f"{v:,}".replace(",", "{,}"), font_size=size, color=color)


class S04Split(LectureScene):
    def construct(self):
        self.section_card(4)
        orch = tile(label("ac_s4_orchestrator"), color=LBLUE, width=3.6, size=28).move_to(UP * 1.7)
        subs = VGroup(*[tile(label(k), color=c, width=3.0, size=26) for k, c in
                        (("ac_s4_planner", GREY_B), ("ac_s4_worker", GREY_B), ("ac_s4_checker", HILITE))])
        subs.arrange(RIGHT, buff=0.9).move_to(DOWN * 1.2)
        links = VGroup(*[Arrow(orch.get_bottom(), s.get_top(), buff=0.12, color=GREY_B, stroke_width=4) for s in subs])
        with self.say("4.1") as (tr, t):
            self.play(FadeIn(orch), run_time=0.5)
            self.cue(tr, t, {"en": "a planner"})
            for s, a in zip(subs, links):
                self.play(GrowArrow(a), FadeIn(s), run_time=0.45)
        self.clear_all()

        # the lookup subagent reads the whole catalogue; only one item id goes back up
        main = tile(label("ac_s4_main_agent"), color=LBLUE, width=3.2, size=26).move_to(LEFT * 5.0 + UP * 1.6)
        names = VGroup(*[mono(n, size=22, color=GREY_B) for n in CATALOGUE])
        names.arrange_in_grid(cols=4, buff=(0.45, 0.1), col_alignments="l" * 4)
        names.scale_to_fit_width(8.0)
        if names.height > 4.4:
            names.scale_to_fit_height(4.4)
        head = txt(label("ac_s4_lookup_agent"), size=26, color=HILITE)
        cat = txt(label("ac_s4_catalogue"), size=22, color=GREY_B)
        inner = VGroup(head, cat, names).arrange(DOWN, buff=0.22)
        frame = RoundedRectangle(corner_radius=0.15, width=inner.width + 0.6, height=inner.height + 0.5,
                                 stroke_color=HILITE, stroke_width=3)
        box = VGroup(frame, inner.move_to(frame)).move_to(RIGHT * 2.0 + DOWN * 0.15)
        hit = names[CATALOGUE.index(ITEM["name"])]
        item = mono(ITEM["item_id"], size=26, color=HILITE)
        item_box = VGroup(SurroundingRectangle(item, color=HILITE, buff=0.15, corner_radius=0.08), item)
        item_box.next_to(main, DOWN, buff=1.4)
        up = Arrow(frame.get_left() + DOWN * 0.1, item_box.get_right(), buff=0.15, color=HILITE, stroke_width=4)
        only = txt(label("ac_s4_only_item"), size=22, color=HILITE).next_to(item_box, DOWN, buff=0.25)
        with self.say("4.2") as (tr, t):
            self.play(FadeIn(main), Create(frame), FadeIn(head), run_time=0.7)
            self.play(FadeIn(cat), LaggedStart(*[FadeIn(n) for n in names], lag_ratio=0.02), run_time=1.6)
            self.cue(tr, t, {"en": "The caller sees only"})
            self.play(hit.animate.set_color(HILITE).scale(1.25), run_time=0.4)
            self.play(GrowArrow(up), FadeIn(item_box), FadeIn(only), run_time=0.6)
            self.play(FadeOut(names), FadeOut(cat), run_time=0.5)      # the catalogue lives and dies inside
        self.clear_all()


class S04Cost(LectureScene):
    def construct(self):
        steps = [MathTex(f"{O['steps_single']}", font_size=30, color=GREY_B),
                 MathTex(rf"{DECK_IN.SUBAGENTS} \times {DECK_IN.SUB_STEPS}", font_size=30, color=GREY_B)]
        names = [label("ac_s4_single"), label("ac_s4_multi")]
        labs = [VGroup(txt(n, size=22, color=GREY_B), VGroup(s, txt(label("ac_steps"), size=20, color=GREY_B))
                       .arrange(RIGHT, buff=0.15)).arrange(DOWN, buff=0.12) for n, s in zip(names, steps)]
        rects, tops, labels_, floor = bars([(labs[0], O["single_tokens"]), (labs[1], O["multi_tokens"])],
                                           lambda v: f"{v:,}", height=3.4, step=3.6, width=1.5, base=-2.0)
        unit = txt(label("ac_s4_input_tokens"), size=26, color=GREY_B).to_edge(UP, buff=SAFE + 0.3)
        fewer = MathTex(rf"-{O['fewer_pct']}\%", font_size=44, color=GOOD).next_to(tops[1], RIGHT, buff=0.3)
        with self.say("4.3") as (tr, t):
            self.play(FadeIn(unit), Create(floor), FadeIn(labels_), run_time=0.6)
            self.cue(tr, t, {"en": "twelve-step single agent"})
            self.play(GrowFromEdge(rects[0], DOWN), FadeIn(tops[0]), run_time=0.6)
            self.cue(tr, t, {"en": "three subagents"})
            self.play(GrowFromEdge(rects[1], DOWN), FadeIn(tops[1]), run_time=0.6)
            self.cue(tr, t, {"en": "thirty percent fewer"})
            self.play(FadeIn(fewer), run_time=0.4)

        # under caching: split each bar into the full-rate part (blue) and the cached part (grey)
        k = rects[0].height / O["single_tokens"]
        split = VGroup()
        for r, full, hit in ((rects[0], O["single_full"], O["single_hit"]), (rects[1], O["multi_full"], O["multi_hit"])):
            g = Rectangle(width=r.width, height=hit * k, stroke_width=0, fill_color=GREY_C, fill_opacity=1)
            b = Rectangle(width=r.width, height=full * k, stroke_width=0, fill_color=LBLUE, fill_opacity=1)
            col = VGroup(b, g).arrange(UP, buff=0).align_to(r, DOWN).set_x(r.get_x())
            split.add(col)
        full_vals = VGroup(num(O["single_full"], 28, LBLUE).next_to(split[0][0], LEFT, buff=0.15),
                           num(O["multi_full"], 28, LBLUE).next_to(split[1][0], RIGHT, buff=0.15),
                           num(O["single_hit"], 28, GREY_B).next_to(split[0][1], LEFT, buff=0.15),
                           num(O["multi_hit"], 28, GREY_B).next_to(split[1][1], RIGHT, buff=0.15))
        legend = VGroup(*[VGroup(Square(0.28, fill_color=c, fill_opacity=1, stroke_width=0),
                                 txt(label(k_), size=22, color=GREY_B)).arrange(RIGHT, buff=0.2)
                          for c, k_ in ((LBLUE, "ac_s4_full_rate"), (GREY_C, "ac_cached"))])
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UR, buff=SAFE + 0.4)
        evals = VGroup(MathTex(rf"\${O['single_eval']:.2f}", font_size=40, color=GOOD),
                       MathTex(rf"\${O['multi_eval']:.2f}", font_size=40, color=BAD))
        for e, c in zip(evals, split):
            e.next_to(c, UP, buff=0.2)
        ratio = MathTex(rf"\times {O['bill_ratio']}", font_size=44, color=BAD).next_to(evals[1], RIGHT, buff=0.35)
        per = tagged(f"{DECK_IN.EVAL_QUERIES:,}", label("ac_s4_per_queries"), size=22, color=GREY_B)
        per.next_to(legend, DOWN, buff=0.35, aligned_edge=LEFT)
        with self.say("4.4") as (tr, t):
            self.cue(tr, t, {"en": "its own prefix and a cold cache"})
            self.play(FadeOut(tops), FadeOut(fewer), FadeIn(split), FadeOut(rects), FadeIn(legend), run_time=0.8)
            self.play(FadeIn(full_vals), run_time=0.4)
            self.cue(tr, t, {"en": "one point six times"})
            self.play(FadeIn(evals), FadeIn(per), run_time=0.5)
            self.play(FadeIn(ratio), run_time=0.4)

        # delegation adds steps: the orchestrator's turns are steps too
        chart = VGroup(floor, labels_, split, full_vals, evals, ratio, unit, legend, per)
        p = D["p_step"]
        rel = VGroup(MathTex(rf"{p}^{{{O['steps_single']}}} = {O['p_single']}", font_size=46),
                     MathTex(r"\downarrow", font_size=46, color=GREY_B),
                     MathTex(rf"{p}^{{{O['steps_multi']}}} = {O['p_multi']}", font_size=46, color=BAD)) \
            .arrange(DOWN, buff=0.3).move_to(RIGHT * 4.3)
        with self.say("4.5") as (tr, t):
            self.play(chart.animate.scale(0.82).to_edge(LEFT, buff=SAFE + 0.2), run_time=0.6)
            self.cue(tr, t, {"en": "twelve becomes sixteen"})
            self.play(FadeIn(rel[0]), run_time=0.5)
            self.cue(tr, t, {"en": "drops to zero point four four"})
            self.play(FadeIn(rel[1]), FadeIn(rel[2]), run_time=0.5)

        # both worse by default; the exception is a checker that can say no
        act = tile(label("ac_s4_action"), color=GREY_B, width=2.6, size=26)
        chk = tile(label("ac_s4_checker"), color=HILITE, width=2.8, size=26)
        rej = pill(label("ac_s4_reject"), BAD, size=26)
        row, arrows = flow_row([act, chk, rej], buff=0.8)
        VGroup(row, arrows).move_to(DOWN * 0.2)
        with self.say("4.6") as (tr, t):
            self.play(Indicate(evals[1], color=BAD), Indicate(rel[2], color=BAD), run_time=0.8)
            self.cue(tr, t, {"en": "There is one exception"})
            self.play(FadeOut(chart), FadeOut(rel), run_time=0.4)
            self.play(FadeIn(act), GrowArrow(arrows[0]), FadeIn(chk), run_time=0.6)
            self.play(GrowArrow(arrows[1]), FadeIn(rej, scale=1.2), run_time=0.5)
        self.clear_all()


class S04Verifier(LectureScene):
    def construct(self):
        d, c = V["draft"], V["catch"]
        eq = MathTex(f"{d:.2f}", "+", f"{1 - d:.2f}", r"\times", f"{c:.2f}", r"\times", f"{d:.2f}", "=", f"{V['with']:.2f}",
                     font_size=56)
        eq.to_edge(UP, buff=SAFE + 0.5)
        for i, col in ((0, GOOD), (2, BAD), (4, HILITE), (6, GOOD), (8, GOOD)):
            eq[i].set_color(col)
        # the same sum as a tree: right first time, or wrong → caught → right on the retry
        root = tile(label("ac_s4_main_agent"), color=LBLUE, width=2.8, size=24).move_to(LEFT * 4.6 + DOWN * 1.0)
        ok1 = Dot(radius=0.14, color=GOOD).move_to(LEFT * 0.6 + UP * 0.4)
        chk = tile(label("ac_s4_checker"), color=HILITE, width=2.4, size=24).move_to(LEFT * 0.6 + DOWN * 2.3)
        retry = tile(label("ac_s4_retry"), color=GOOD, width=2.2, size=24).move_to(RIGHT * 2.7 + DOWN * 2.3)
        ok2 = Dot(radius=0.14, color=GOOD).move_to(RIGHT * 5.0 + DOWN * 2.3)
        def edge(a, b, val, col, side=UP):
            ar = Arrow(a, b, buff=0.15, color=col, stroke_width=4, max_tip_length_to_length_ratio=0.12)
            return VGroup(ar, MathTex(val, font_size=34, color=col).next_to(ar.get_center(), side, buff=0.15))
        e1 = edge(root.get_right(), ok1.get_center(), f"{d:.2f}", GOOD)
        e2 = edge(root.get_right(), chk.get_left(), f"{1 - d:.2f}", BAD, side=DL)
        e3 = edge(chk.get_right(), retry.get_left(), f"{c:.2f}", HILITE)
        e4 = edge(retry.get_right(), ok2.get_center(), f"{d:.2f}", GOOD)
        with self.say("4.7") as (tr, t):
            self.play(FadeIn(root), run_time=0.4)
            self.cue(tr, t, {"en": "eighty percent of the time"})
            self.play(GrowArrow(e1[0]), FadeIn(e1[1]), FadeIn(ok1), FadeIn(eq[0]), run_time=0.6)
            self.cue(tr, t, {"en": "a checker catches"})
            self.play(GrowArrow(e2[0]), FadeIn(e2[1]), FadeIn(chk), run_time=0.5)
            self.play(GrowArrow(e3[0]), FadeIn(e3[1]), FadeIn(eq[1:5]), run_time=0.5)
            self.cue(tr, t, {"en": "one retry"})
            self.play(FadeIn(retry), GrowArrow(e4[0]), FadeIn(e4[1]), FadeIn(ok2), FadeIn(eq[5:7]), run_time=0.6)
            self.cue(tr, t, {"en": "Success rises"})
            self.play(FadeIn(eq[7:]), run_time=0.5)
            self.play(Indicate(eq[8], color=GOOD), Indicate(VGroup(ok1, ok2), color=GOOD, scale_factor=1.3), run_time=0.7)
        self.clear_all()

        # the store's sixteen tools by what they do; the checker belongs in front of the seven that write
        groups = [("ac_s4_read", "READ", GREY_B), ("ac_s4_write", "WRITE", HILITE), ("ac_s4_other", "GENERIC", GREY_B)]
        cols = VGroup()
        for key, typ, col in groups:
            names = [t_["name"] for t_ in TOOLS if t_["type"] == typ]
            head = VGroup(txt(label(key), size=28, weight=BOLD, color=col), MathTex(str(len(names)), font_size=34, color=col)) \
                .arrange(RIGHT, buff=0.25)
            rows = VGroup(*[mono(n, size=18, color=col) for n in names]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
            cols.add(VGroup(head, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.35))
        cols.arrange(RIGHT, buff=0.7, aligned_edge=UP).move_to(DOWN * 0.1)
        if cols.width > 12.8:
            cols.scale_to_fit_width(12.8)
        frame = SurroundingRectangle(cols[1], color=HILITE, buff=0.25, corner_radius=0.12, stroke_width=3)
        with self.say("4.8") as (tr, t):
            self.play(LaggedStart(*[FadeIn(c) for c in cols], lag_ratio=0.3), run_time=1.2)
            self.cue(tr, t, {"en": "seven write"})
            self.play(Create(frame), cols[0].animate.set_opacity(0.4), cols[2].animate.set_opacity(0.4), run_time=0.7)
        self.clear_all()


class S04Snippet(LectureScene):
    def construct(self):
        panel = code_panel(SNIP, "def handle", "return results", size=22, tag="shown").move_to(UP * 0.3)  # clear of the brand mark
        marks = [highlight(panel, code_lines(SNIP, "def handle")[0]),
                 highlight(panel, code_lines(SNIP, "out = work(")[0]),
                 highlight(panel, code_lines(SNIP, "ok, why = verify")[0]),
                 highlight(panel, code_lines(SNIP, "return ask_human")[0], color=BAD)]
        with self.say("4.9") as (tr, t):
            self.play(FadeIn(panel), run_time=0.7)
            for cue_, m in zip(("The orchestrator splits", "Each worker sees only", "A verifier checks", "a human decides"),
                               marks):
                self.cue(tr, t, {"en": cue_})
                self.play(Create(m), run_time=0.4)
        self.clear_all()

        # the verifier's boundary: checks as plain code, versus a verifier that can write
        left_head = txt(label("ac_s4_verifier_code"), size=26, color=GOOD)
        checks = VGroup(mono("order_id in db.orders", size=24, color=GOOD), mono("sum(items) == total", size=24, color=GOOD)) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        left = VGroup(left_head, checks).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(LEFT * 3.4 + UP * 0.2)
        right_head = txt(label("ac_s4_verifier_tools"), size=26, color=BAD)
        ver = tile(label("ac_s4_checker"), color=HILITE, width=2.6, size=24)
        write = next(t_["name"] for t_ in TOOLS if t_["type"] == "WRITE" and t_["name"].startswith("cancel"))
        wr = VGroup(mono(write, size=20, color=BAD))
        wr_box = VGroup(SurroundingRectangle(wr, color=BAD, buff=0.18, corner_radius=0.08), wr)
        drift = VGroup(ver, wr_box).arrange(DOWN, buff=0.8)
        drift_arrow = Arrow(ver.get_bottom(), wr_box.get_top(), buff=0.1, color=BAD, stroke_width=4)
        acts = txt(label("ac_s4_acts_itself"), size=22, color=BAD)
        right = VGroup(right_head, drift, acts).arrange(DOWN, buff=0.4).move_to(RIGHT * 3.4 + UP * 0.1)
        drift_arrow.put_start_and_end_on(ver.get_bottom() + DOWN * 0.08, wr_box.get_top() + UP * 0.08)
        sep = Line(UP * 2.6, DOWN * 2.6, color=GREY_D, stroke_width=2)
        with self.say("4.10") as (tr, t):
            self.play(FadeIn(left_head), run_time=0.4)
            self.cue(tr, t, {"en": "Do these IDs exist"})
            self.play(FadeIn(checks[0]), run_time=0.4)
            self.cue(tr, t, {"en": "Do the totals add up"})
            self.play(FadeIn(checks[1]), run_time=0.4)
            self.cue(tr, t, {"en": "Give a verifier write tools"})
            self.play(Create(sep), FadeIn(right_head), FadeIn(ver), run_time=0.5)
            self.cue(tr, t, {"en": "fix the order itself"})
            self.play(GrowArrow(drift_arrow), FadeIn(wr_box), FadeIn(acts), run_time=0.6)
        self.clear_all()


class S04Human(LectureScene):
    def construct(self):
        head = txt(label("ac_s4_policy"), size=24, color=GREY_B)
        rule = VGroup(*[txt(r, size=28, color=WHITE) for r in textwrap.wrap(POLICY_RULE, 64)]) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        for r in rule:
            if "explicit user confirmation" in r.text or "confirmation" in r.text:
                r.set_color(HILITE)
        card = VGroup(head, rule).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        card = VGroup(RoundedRectangle(corner_radius=0.12, width=card.width + 0.5, height=card.height + 0.4,
                                       stroke_color=GREY_D, stroke_width=2, fill_color="#1b1b1f", fill_opacity=1),
                      card)
        card[1].move_to(card[0])
        card.to_edge(UP, buff=SAFE + 0.25)
        if card.width > 12.6:
            card.scale_to_fit_width(12.6)
        writes = [t_["name"] for t_ in TOOLS if t_["type"] == "WRITE"]
        gates = VGroup()
        for w in writes:
            g = pill(label("ac_s4_yes"), GOOD, size=22)
            n = mono(w, size=22, color=HILITE)
            gates.add(VGroup(g, Arrow(ORIGIN, RIGHT * 0.6, buff=0, color=GREY_B, stroke_width=3,
                                      max_tip_length_to_length_ratio=0.35), n).arrange(RIGHT, buff=0.15))
        gates.arrange_in_grid(cols=2, buff=(0.9, 0.3), col_alignments="ll").next_to(card, DOWN, buff=0.6)
        if gates.width > 12.6:
            gates.scale_to_fit_width(12.6)
        VGroup(card, gates).move_to(ORIGIN)
        with self.say("4.11") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
            self.cue(tr, t, {"en": "explicit yes"})
            self.play(LaggedStart(*[FadeIn(g, shift=RIGHT * 0.15) for g in gates], lag_ratio=0.15), run_time=1.4)
            self.cue(tr, t, {"en": "That is where humans belong"})
            self.play(Indicate(VGroup(*[g[0] for g in gates]), color=GOOD, scale_factor=1.08), run_time=0.8)
        self.clear_all()

        steps = [label("ac_s4_retry"), label("ac_s4_fallback"), label("ac_s4_escalate")]
        boxes, arrows = flow_row(steps, color=LBLUE, size=28, buff=1.0, width=3.0)
        fixes = VGroup(*[txt(label(k), size=22, color=GREY_B).next_to(b, DOWN, buff=0.25) for k, b in
                         zip(("ac_s4_retry_fixes", "ac_s4_fallback_fixes", "ac_s4_escalate_fixes"), boxes)])
        top = VGroup(boxes, arrows, fixes).move_to(UP * 1.6)
        card = schema_card("transfer_to_human_agents", width=9.5, size=20).next_to(top, DOWN, buff=0.5)
        with self.say("4.12") as (tr, t):
            self.play(FadeIn(boxes[0]), FadeIn(fixes[0]), run_time=0.4)
            self.cue(tr, t, {"en": "fallback fixes"})
            self.play(GrowArrow(arrows[0]), FadeIn(boxes[1]), FadeIn(fixes[1]), run_time=0.5)
            self.cue(tr, t, {"en": "escalation is for everything else"})
            self.play(GrowArrow(arrows[1]), FadeIn(boxes[2]), FadeIn(fixes[2]), run_time=0.5)
            self.cue(tr, t, {"en": "transfer to a human agent"})
            self.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        recap(self, "4.13", [label("ac_s4_recap_split"), label("ac_s4_recap_count"), label("ac_s4_recap_reject")])


SCENES = ["S04Split", "S04Cost", "S04Verifier", "S04Snippet", "S04Human"]
