"""Agent course, section 2 — function calling and structured outputs: prose vs a call, τ²-bench's cancel schema,
the vague-description run, closed sets as enums, our return schema (run), why "reply in JSON" is not enough, three
levels of enforcement, constrained decoding, validate-and-retry, and the two captured runs (helpful vs lazy error).

Live results: raw/s2_structured.json, raw/s2_structured_unhelpful.json, raw/s1_agent_loop_vague.json. Testbed:
raw/tau2_retail_tools.json (cancel_pending_order) and τ²-bench's retail tools.py (its "Non-pending" error). Deck
numbers: D["q10"], DECK_IN.Q_FORMAT, D["tau2"]["cancel_reasons"].
"""
import re

from agents_course_kit import *
from agents_course_kit import _wrap

FILE = "s2_structured.py"
GOOD_RUN = raw("s2_structured.json")
LAZY_RUN = raw("s2_structured_unhelpful.json")
VAGUE = raw("s1_agent_loop_vague.json")
REASONS = D["tau2"]["cancel_reasons"]
CANCEL = tool("cancel_pending_order")["schema"]["function"]
# the free-string reason the narration quotes (2.4): model output, so English in every language
FREE_REASON = "changed my mind"
# τ²-bench's own refusal (2.12), read from its source so the screen shows the real message
NOT_PENDING = re.search(r'raise ValueError\("(Non-pending order cannot be cancelled)"\)',
                        (COURSE / "tau2-bench/src/tau2/domains/retail/tools.py").read_text())[1]


def schema(name, show=None, mark=None, width=10.4, size=24, rows=5):
    """schema_card() with its argument rows stacked (the kit's version prints them on one spot), larger type, and
    an ellipsis where the description is cut."""
    f = tool(name)["schema"]["function"]
    head = mono(f["name"], size=size + 4, color=HILITE, weight=BOLD)
    desc = _wrap(" ".join(f["description"].split()), 64)
    cut = len(desc) > rows
    desc = desc[:rows]
    if cut:
        desc[-1] += " …"
    body = VGroup(*[txt(r, size=size - 2, color=GREY_A) for r in desc]).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    if mark:
        for r, t in zip(desc, body):
            if any(w in r for w in mark.split()[:2]) and mark.split()[0] in r:
                t.set_color(HILITE)
    args = VGroup(*[mono(f"{p}: {spec.get('type', '')}", size=size - 2, color=LBLUE)
                    for p, spec in f["parameters"]["properties"].items() if not show or p in show])
    args.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    g = VGroup(head, body, args).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
    box = RoundedRectangle(corner_radius=0.15, width=g.width + 0.6, height=g.height + 0.5, stroke_color=GREY_B,
                           stroke_width=2.5, fill_color="#1b1b1f", fill_opacity=1)
    out = VGroup(box, g.move_to(box))
    if out.width > width:
        out.scale_to_fit_width(width)
    return out


def return_schema():
    """The RETURN schema exactly as s2_structured.py defines it (parsed from the file, not retyped)."""
    import ast
    tree = ast.parse((CODE / FILE).read_text())
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "RETURN")
    return ast.literal_eval(node.value)


def call_text(req):
    return f"submit_return({json.dumps(req, ensure_ascii=False)})"


def try_rows(run, max_chars=58):
    """A captured run's tries as bubbles: each request, then its error (or ✓)."""
    rows = VGroup()
    for i, t in enumerate(run["tries"], 1):
        n = txt(f"{i}", size=22, color=GREY_B, weight=BOLD)
        if t["request"] is None:
            req = bubble("assistant", label("ac_answered_in_text"), max_chars=max_chars, size=18)
        else:
            req = bubble("call", call_text(t["request"]), max_chars=max_chars, max_rows=2, size=18)
        if t["error"]:
            res = bubble("tool", t["error"], max_chars=max_chars, max_rows=2, size=18)
            res[0].set_stroke(BAD)
        else:
            res = VGroup(txt("✓", size=34, color=GOOD, weight=BOLD))
        row = VGroup(n, VGroup(req, res).arrange(DOWN, aligned_edge=LEFT, buff=0.08)).arrange(RIGHT, buff=0.3,
                                                                                              aligned_edge=UP)
        rows.add(row)
    return rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22)


class S02Schema(LectureScene):
    def construct(self):
        self.section_card(2)
        prose = bubble("assistant", f"“{label('ac_prose_cancel')}”", max_chars=50, size=28).move_to(UP * 0.6)
        qs = VGroup(txt(label("ac_which_function"), size=28, color=HILITE),
                    txt(label("ac_which_arguments"), size=28, color=HILITE)).arrange(RIGHT, buff=1.2)
        qs.next_to(prose, DOWN, buff=0.7)
        with self.say("2.1") as (tr, t):
            self.play(FadeIn(prose), run_time=0.5)
            self.cue(tr, t, {"en": "our code is left guessing"})
            self.play(FadeIn(qs[0], shift=UP * 0.2), run_time=0.4)
            self.play(FadeIn(qs[1], shift=UP * 0.2), run_time=0.4)
        self.clear_all()

        # τ²-bench's cancel tool, as its schema says it
        card = schema("cancel_pending_order", show=["order_id", "reason"], width=10.0).move_to(RIGHT * 1.0)
        parts = VGroup(txt(label("ac_schema_name"), size=22, color=GREY_B),
                       txt(label("ac_schema_purpose"), size=22, color=GREY_B),
                       txt(label("ac_schema_arguments"), size=22, color=GREY_B))
        head, desc, args = card[1]
        for p, m in zip(parts, (head, desc, args)):
            p.next_to(card, LEFT, buff=0.25).match_y(m)
        side = VGroup(*parts)
        if side.get_left()[0] < -7.1 + SAFE:
            VGroup(card, side).arrange(RIGHT, buff=0.3).move_to(ORIGIN)
            for p, m in zip(parts, (head, desc, args)):
                p.match_y(m)
        with self.say("2.2") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
            self.cue(tr, t, {"en": "It declares a name"})
            self.play(FadeIn(parts[0]), Indicate(head, color=HILITE, scale_factor=1.05), run_time=0.5)
            self.cue(tr, t, {"en": "one line saying what the tool is for"})
            self.play(FadeIn(parts[1]), run_time=0.4)
            self.cue(tr, t, {"en": "the arguments as JSON Schema"})
            self.play(FadeIn(parts[2]), Indicate(args, color=LBLUE, scale_factor=1.05), run_time=0.5)
        self.clear_all()


class S02Vague(LectureScene):
    def construct(self):
        card = schema("cancel_pending_order", show=["order_id", "reason"], width=10.0,
                      mark="explicit user confirmation").move_to(UP * 0.5)
        only = txt(label("ac_only_docs"), size=26, color=GREY_B).next_to(card, DOWN, buff=0.3)
        # the vague run: its description, then the three spellings it tried
        desc = re.search(r"'(.+)'", VAGUE["order_id_description"])[1]
        vd = VGroup(txt(label("ac_vague_description"), size=22, color=GREY_B),
                    mono(f'"{desc}"', size=22, color=BAD)).arrange(RIGHT, buff=0.3)
        calls = VGroup(*[VGroup(mono(f'{c["tool"]}("{c["args"]["order_id"]}")', size=22, color=HILITE),
                                txt("✗", size=30, color=BAD, weight=BOLD)).arrange(RIGHT, buff=0.3)
                         for c in VAGUE["tool_calls"]]).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        real = VGroup(txt(label("ac_real_id"), size=22, color=GREY_B),
                      mono(re.search(r"#W\d{7}", VAGUE["question"])[0], size=24, color=GOOD)).arrange(RIGHT, buff=0.3)
        low = VGroup(vd, calls, real).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        tag = captured_tag("s1_agent_loop_vague.json")
        with self.say("2.3") as (tr, t):
            self.play(FadeIn(card), run_time=0.5)
            self.cue(tr, t, {"en": "the only documentation the model ever reads"})
            self.play(FadeIn(only), run_time=0.4)
            self.cue(tr, t, {"en": "explicit yes first"})
            self.play(Indicate(card[1][1], color=HILITE, scale_factor=1.03), run_time=0.7)
            self.cue(tr, t, {"en": "We measured it"})
            self.play(FadeOut(only), FadeOut(card), run_time=0.4)
            VGroup(low, tag).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(ORIGIN)
            self.play(FadeIn(vd), run_time=0.4)
            self.cue(tr, t, {"en": "dropped the hash sign"})
            for c in calls:
                self.play(FadeIn(c, shift=RIGHT * 0.2), run_time=0.35)
            self.cue(tr, t, {"en": "never found the order"})
            self.play(FadeIn(real), FadeIn(tag), run_time=0.4)
        self.clear_all()

        # a closed set belongs in the type
        free = mono(f'"reason": "{FREE_REASON}"', size=30, color=WHITE).move_to(UP * 1.3)
        strike = Line(free.get_left(), free.get_right(), color=BAD, stroke_width=5)
        free_lab = txt(label("ac_free_string"), size=24, color=GREY_B).next_to(free, UP, buff=0.3)
        enum = VGroup(mono('"reason": {"enum": [', size=28),
                      *[mono(f'    "{r}"' + ("," if i < len(REASONS) - 1 else ""), size=28, color=GOOD)
                        for i, r in enumerate(REASONS)],
                      mono("]}", size=28)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(DOWN * 1.2)
        enum_lab = txt(label("ac_enum"), size=24, color=GOOD).next_to(enum, UP, buff=0.3)
        with self.say("2.4") as (tr, t):
            self.cue(tr, t, {"en": "exactly two reasons"})
            self.play(FadeIn(enum_lab), FadeIn(enum), run_time=0.6)
            self.cue(tr, t, {"en": "As a free string"})
            self.play(FadeIn(free_lab), FadeIn(free), run_time=0.5)
            self.cue(tr, t, {"en": "As an enum"})
            self.play(Create(strike), Indicate(enum, color=GOOD, scale_factor=1.05), run_time=0.7)
        self.clear_all()


class S02Return(LectureScene):
    def construct(self):
        props = return_schema()["properties"]
        rows = VGroup(*[mono(f'"{k}": {json.dumps(v)}', size=26, color=WHITE) for k, v in props.items()]) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        if rows.width > 12.0:
            rows.scale_to_fit_width(12.0)
        title = VGroup(mono(f"{FILE} · RETURN", size=22, color=GREY_B), run_pill(18)).arrange(RIGHT, buff=0.3)
        frame = SurroundingRectangle(rows, color=GREY_D, buff=0.35, corner_radius=0.12, fill_color="#1b1b1f",
                                     fill_opacity=1)
        title.next_to(frame, UP, buff=0.2, aligned_edge=LEFT)
        panel = VGroup(title, frame, rows).move_to(ORIGIN)
        marks = [SurroundingRectangle(r, color=HILITE, buff=0.08, corner_radius=0.05) for r in rows]
        with self.say("2.5") as (tr, t):
            self.play(FadeIn(panel), run_time=0.6)
            self.cue(tr, t, {"en": "must match a pattern"})
            self.play(Create(marks[0]), run_time=0.4)
            self.cue(tr, t, {"en": "The items are a list"})
            self.play(ReplacementTransform(marks[0], marks[1]), run_time=0.4)
            self.cue(tr, t, {"en": "the reason is an enum"})
            self.play(ReplacementTransform(marks[1], marks[2]), run_time=0.4)
        self.clear_all()

        # one reply in fifty malformed → a ten-step run parses completely 0.82 of the time
        q, q10 = DECK_IN.Q_FORMAT, D["q10"]
        eq = MathTex(rf"{q}^{{10}} = {q10}", font_size=64).move_to(UP * 1.6)
        w = 9.0
        ok = Rectangle(width=w * q10, height=0.8, stroke_width=0, fill_color=GOOD, fill_opacity=0.85)
        bad = Rectangle(width=w * (1 - q10), height=0.8, stroke_width=0, fill_color=BAD, fill_opacity=0.85)
        bar = VGroup(ok, bad).arrange(RIGHT, buff=0).move_to(DOWN * 0.4)
        ok_l = txt(label("ac_parses"), size=24, color=GOOD).next_to(ok, DOWN, buff=0.25)
        bad_l = txt(label("ac_dies_on_format"), size=24, color=BAD).next_to(bad, DOWN, buff=0.25).align_to(bad, RIGHT)
        with self.say("2.6") as (tr, t):
            self.cue(tr, t, {"en": "ninety-eight times in a hundred"})
            self.play(Write(eq), run_time=0.8)
            self.cue(tr, t, {"en": "parses completely"})
            self.play(GrowFromEdge(ok, LEFT), FadeIn(ok_l), run_time=0.6)
            self.cue(tr, t, {"en": "One run in five"})
            self.play(GrowFromEdge(bad, LEFT), FadeIn(bad_l), run_time=0.5)
        self.clear_all()

        # three levels of enforcement, weakest to strongest
        levels, arrows = flow_row([label("ac_ask_hope"), label("ac_validate_retry"), label("ac_constrain")],
                                  size=26, buff=0.6, height=1.0)
        cols = (GREY_B, HILITE, GOOD)
        for b, c in zip(levels, cols):
            b[0].set_stroke(c)
        row = VGroup(levels, arrows).move_to(ORIGIN)
        if row.width > 12.6:
            row.scale_to_fit_width(12.6)
        stronger = txt(label("ac_stronger"), size=22, color=GREY_B).next_to(row, DOWN, buff=0.4)
        with self.say("2.7") as (tr, t):
            self.cue(tr, t, {"en": "ask and hope"})
            self.play(FadeIn(levels[0]), run_time=0.4)
            self.cue(tr, t, {"en": "validate and retry"})
            self.play(GrowArrow(arrows[0]), FadeIn(levels[1]), run_time=0.4)
            self.cue(tr, t, {"en": "or constrain"})
            self.play(GrowArrow(arrows[1]), FadeIn(levels[2]), FadeIn(stronger), run_time=0.4)
        self.clear_all()


class S02Constrain(LectureScene):
    def construct(self):
        # sampling inside "reason": only tokens that continue an allowed value survive
        prefix = mono('"reason": "', size=30, color=GREY_B).move_to(UP * 2.0 + LEFT * 2.5)
        allowed = [r.split()[0] for r in REASONS]                     # first token of each allowed reason
        other = [w for w in FREE_REASON.split()[:1]] + [FREE_REASON.split()[-1]]
        cands = allowed + other
        rows = VGroup()
        for c in cands:
            ok = c in allowed
            rows.add(VGroup(mono(f'"{c}"', size=28, color=WHITE),
                            Rectangle(width=2.6, height=0.36, stroke_width=0, fill_color=LBLUE, fill_opacity=0.9)
                            ).arrange(RIGHT, buff=0.4))
            rows[-1].ok = ok
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(prefix, DOWN, buff=0.5).align_to(prefix, LEFT)
        lab = txt(label("ac_next_token"), size=22, color=GREY_B).next_to(rows, LEFT, buff=0.4)
        cite = txt(label("ac_willard_louf"), size=22, color=GREY_B).to_edge(DOWN, buff=SAFE + 0.5)
        with self.say("2.8") as (tr, t):
            self.play(FadeIn(prefix), FadeIn(rows), FadeIn(lab), run_time=0.6)
            self.cue(tr, t, {"en": "minus infinity"})
            outs = []
            for r in rows:
                if not r.ok:
                    inf = MathTex(r"-\infty", font_size=40, color=BAD).move_to(r[1])
                    outs += [Transform(r[1], inf), r[0].animate.set_color(GREY_D)]
            self.play(*outs, run_time=0.6)
            self.cue(tr, t, {"en": "only the allowed reasons"})
            self.play(*[Indicate(r, color=GOOD, scale_factor=1.06) for r in rows if r.ok], run_time=0.6)
            self.cue(tr, t, {"en": "Willard and Louf"})
            self.play(FadeIn(cite), run_time=0.4)
        self.clear_all()


class S02Check(LectureScene):
    def construct(self):
        panel = code_panel(FILE, "def check", "its items are", size=22, tag="run").move_to(ORIGIN)
        schema = highlight(panel, code_lines(FILE, "validate(req, RETURN)")[0])
        a, b = code_lines(FILE, "if bad :=", "its items are")
        facts = highlight(panel, a, color=LBLUE, last=b)
        with self.say("2.9") as (tr, t):
            self.play(FadeIn(panel), run_time=0.6)
            self.cue(tr, t, {"en": "validates every call against the schema"})
            self.play(Create(schema), run_time=0.4)
            self.cue(tr, t, {"en": "do these items belong to this order"})
            self.play(Create(facts), run_time=0.4)
            self.cue(tr, t, {"en": "Any error goes back to the model"})
            # the error branch replaces the check: two stacked panels would shrink both
            back = code_panel(FILE, "except ValidationError", '"Invalid:', size=22, tag="run").move_to(ORIGIN)
            self.play(FadeOut(VGroup(panel, schema, facts)), run_time=0.4)
            self.play(FadeIn(back), run_time=0.4)
            self.play(Create(highlight(back, code_lines(FILE, '"Invalid:')[0])), run_time=0.4)
        self.clear_all()

        # the captured run: wrong id, an error that lists the order's items, then right
        head = VGroup(txt(label("ac_our_run"), size=28, weight=BOLD, color=LBLUE), run_pill()).arrange(RIGHT, buff=0.3)
        msg = bubble("user", GOOD_RUN["message"], max_chars=64, max_rows=2, size=20)
        tries = try_rows(GOOD_RUN, max_chars=64)
        tag = captured_tag("s2_structured.json")
        col = VGroup(head, msg, tries, tag).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        if col.height > 6.9:
            col.scale_to_fit_height(6.9)
        if col.width < 11.5 and col.height < 6.9:                  # use the screen: grow to the frame
            col.scale(min(11.5 / col.width, 6.9 / col.height))
        col.move_to(ORIGIN)
        with self.say("2.10") as (tr, t):
            self.play(FadeIn(head), FadeIn(msg), run_time=0.5)
            self.cue(tr, t, {"en": "put it where the item number belongs"})
            self.play(FadeIn(tries[0][0]), FadeIn(tries[0][1][0]), run_time=0.5)
            self.cue(tr, t, {"en": "Our check listed the order's real items"})
            self.play(FadeIn(tries[0][1][1]), run_time=0.5)
            self.cue(tr, t, {"en": "the call was right"})
            self.play(FadeIn(tries[1]), FadeIn(tag), run_time=0.5)
        self.wait(0.8)
        self.clear_all()

        # the lazy error: names the problem, lists nothing; three failures
        head = VGroup(txt(label("ac_lazy_error"), size=28, weight=BOLD, color=BAD), run_pill()).arrange(RIGHT, buff=0.3)
        tries = try_rows(LAZY_RUN, max_chars=64)
        tag = captured_tag("s2_structured_unhelpful.json")
        col = VGroup(head, tries, tag).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        if col.height > 6.9:
            col.scale_to_fit_height(6.9)
        if col.width < 11.5 and col.height < 6.9:                  # use the screen: grow to the frame
            col.scale(min(11.5 / col.width, 6.9 / col.height))
        col.move_to(ORIGIN)
        rule = txt(label("ac_error_is_prompt"), size=30, weight=BOLD, color=HILITE)
        with self.say("2.11") as (tr, t):
            self.play(FadeIn(head), run_time=0.4)
            self.cue(tr, t, {"en": "without listing the valid IDs"})
            for r in tries:
                self.play(FadeIn(r, shift=DOWN * 0.1), run_time=0.4)
            self.play(FadeIn(tag), run_time=0.3)
            self.cue(tr, t, {"en": "An error message is a prompt"})
            self.play(FadeOut(col), run_time=0.4)
            rule.move_to(ORIGIN)
            self.play(FadeIn(rule, scale=1.1), run_time=0.4)
        self.clear_all()

        # recap, with τ²-bench's own refusal: a valid call can still be refused by the facts
        rows = bullets([label("ac_recap_2_schema"), label("ac_recap_2_enum"), label("ac_recap_2_truth"),
                        label("ac_recap_2_errors")], size=28)
        if rows.width > 12:
            rows.scale_to_fit_width(12)
        reply = VGroup(txt(label("ac_tau2_replies"), size=22, color=GREY_B),
                       mono(NOT_PENDING, size=24, color=BAD)).arrange(RIGHT, buff=0.3)
        head = self.heading(label("ac_recap"), color=HILITE)
        VGroup(rows, reply).arrange(DOWN, aligned_edge=LEFT, buff=0.6).next_to(head, DOWN, buff=0.5)
        with self.say("2.12") as (tr, t):
            self.play(FadeIn(head), run_time=0.4)
            self.play(FadeIn(rows[0], shift=RIGHT * 0.2), run_time=0.4)
            self.cue(tr, t, {"en": "enums and patterns"})
            self.play(FadeIn(rows[1], shift=RIGHT * 0.2), run_time=0.4)
            self.cue(tr, t, {"en": "constraints fix the shape"})
            self.play(FadeIn(rows[2], shift=RIGHT * 0.2), run_time=0.4)
            self.cue(tr, t, {"en": "still refuses an order"})
            self.play(FadeIn(reply), run_time=0.4)
            self.cue(tr, t, {"en": "Our code checks the facts"})
            self.play(FadeIn(rows[3], shift=RIGHT * 0.2), run_time=0.4)
        self.clear_all()


SCENES = ["S02Schema", "S02Vague", "S02Return", "S02Constrain", "S02Check"]
