"""Agent course, section 3 — memory: a real conversation filling the window, lost in the middle (schematic), capped
observations, three ways to rewrite history and its cache cost, what a summary must keep, three external stores,
MemGPT, the s3_memory.py snippet (shown, not run), storing inferences as facts, and re-authentication.

Data: raw/tau2_retail_trajectory.json (task 4: its tool results, the modify call), raw/tau2_retail_policy.md (the
authentication rule). Deck numbers: D["turns_uncapped"], D["turns_capped"], D["turns_ratio"], DECK_IN.WINDOW,
DECK_IN.A_UNCAPPED, DECK_IN.A_CAPPED.
"""
from agents_course_kit import *

TRAJ = raw("tau2_retail_trajectory.json")
MEM_FILE = "s3_memory.py"


def tool_results(messages):
    """[(tool name, its result text)] in call order: the agent's observations, as the run returned them."""
    calls = [c for m in messages for c in (m.get("tool_calls") or [])]
    results = [m["content"] for m in messages if m["role"] == "tool"]
    return [(c["name"], r) for c, r in zip(calls, results)]


OBS = tool_results(TRAJ["messages"])
MODIFY = next(c["arguments"] for m in TRAJ["messages"] for c in (m.get("tool_calls") or [])
              if c["name"] == "modify_pending_order_items")
ORDER_RECORD = next(r for n, r in OBS if n == "get_order_details" and MODIFY["order_id"] in r[:40])
AUTH_RULE = next(s.strip() for s in (RAWDIR / "tau2_retail_policy.md").read_text().split("\n")
                 if "even when the user already provides the user id" in s)


def obs_block(name, chars, k, width=5.2):
    r = Rectangle(width=width, height=max(chars * k, 0.12), stroke_color=GREY_D, stroke_width=1.5,
                  fill_color=HILITE if name == "get_order_details" else LBLUE, fill_opacity=0.55)
    t = mono(name, size=16, color=WHITE)
    if t.height > r.height - 0.04:
        t.scale_to_fit_height(max(r.height - 0.04, 0.08))
    return VGroup(r, t.move_to(r))


class S03Window(LectureScene):
    def construct(self):
        self.section_card(3)
        # the run's observations stacked as they entered the context (height ∝ characters returned)
        sizes = [(n, len(r)) for n, r in OBS if n in ("get_user_details", "get_product_details", "get_order_details")]
        k = 4.6 / sum(c for _, c in sizes)
        blocks = VGroup(*[obs_block(n, c, k) for n, c in sizes]).arrange(UP, buff=0.03)
        blocks.move_to(DOWN * 0.45 + LEFT * 1.5)
        floor = blocks.get_bottom()[1]
        win = DashedLine([-5.2, blocks.get_top()[1] + 0.12, 0], [2.4, blocks.get_top()[1] + 0.12, 0], color=BAD,
                         stroke_width=4)
        win_l = txt(label("ac_context_window"), size=24, color=BAD).next_to(win, RIGHT, buff=0.25)
        cap = VGroup(txt(label("ac_task"), size=22, color=GREY_B), mono(TRAJ["task_id"], size=22, color=GREY_B)) \
            .arrange(RIGHT, buff=0.15).next_to(blocks, DOWN, buff=0.25)
        with self.say("3.1") as (tr, t):
            self.play(FadeIn(cap), run_time=0.3)
            self.cue(tr, t, {"en": "the profile"})
            self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.15) for b in blocks], lag_ratio=0.25), run_time=2.0)
            self.cue(tr, t, {"en": "meets the edge of the context window"})
            self.play(Create(win), FadeIn(win_l), run_time=0.5)
            self.cue(tr, t, {"en": "a bigger window"})
            up = VGroup(win, win_l)
            self.play(up.animate.shift(UP * 1.2), run_time=0.6)

        # lost in the middle: the shape Liu et al. report (schematic, no measured values)
        self.play(FadeOut(VGroup(blocks, cap, win, win_l)), run_time=0.3)
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 1], x_length=7.0, y_length=3.6,
                  axis_config={"color": GREY_B, "include_ticks": False}).shift(DOWN * 0.3)
        u = ax.plot(lambda x: 0.85 - 0.45 * np.sin(np.pi * x), x_range=[0, 1], color=LBLUE, stroke_width=5)
        ticks = VGroup(*[txt(label(k_), size=22, color=GREY_B).next_to(ax.c2p(x, 0), DOWN, buff=0.25)
                         for k_, x in (("ac_pos_first", 0), ("ac_pos_middle", 0.5), ("ac_pos_last", 1))])
        yl = txt(label("ac_used_well"), size=22, color=GREY_B).next_to(ax, UP, buff=0.2).align_to(ax, LEFT)
        note = txt(label("ac_schematic_liu"), size=20, color=GREY_C).to_edge(DOWN, buff=SAFE + 0.5)
        with self.say("3.2") as (tr, t):
            self.cue(tr, t, {"en": "the bill still grows quadratically"})
            self.play(Create(ax), FadeIn(ticks), FadeIn(yl), run_time=0.6)
            self.cue(tr, t, {"en": "at the start and end"})
            self.play(Create(u), run_time=1.0)
            self.cue(tr, t, {"en": "lost in the middle"})
            self.play(Indicate(ticks[1], color=BAD), FadeIn(note), run_time=0.6)
        self.clear_all()

        # the cheapest lever: smaller observations last longer in the same window
        pairs = [(tagged(f"{DECK_IN.A_UNCAPPED:,}", label("ac_tokens_per_call"), size=22, color=GREY_B),
                  D["turns_uncapped"]),
                 (tagged(f"{DECK_IN.A_CAPPED:,}", label("ac_tokens_per_call"), size=22, color=GREY_B),
                  D["turns_capped"])]
        rects, tops, labs, flo = bars(pairs, lambda v: f"{v}", height=3.4, step=4.2, width=1.5, base=-2.0)
        unit = VGroup(txt(label("ac_turns_in_window"), size=26, color=GREY_B),
                      tagged(f"{DECK_IN.WINDOW:,}", label("ac_tokens"), size=26, color=GREY_B)) \
            .arrange(RIGHT, buff=0.3).to_edge(UP, buff=SAFE + 0.3)
        rects[1].set_fill(GOOD)
        ratio = MathTex(rf"\times {D['turns_ratio']}", font_size=48, color=GOOD).next_to(rects[1], LEFT, buff=0.5) \
            .shift(UP * 0.8)
        with self.say("3.3") as (tr, t):
            self.play(FadeIn(unit), Create(flo), FadeIn(labs), run_time=0.5)
            self.cue(tr, t, {"en": "lasts eleven turns"})
            self.play(GrowFromEdge(rects[0], DOWN), FadeIn(tops[0]), run_time=0.6)
            self.cue(tr, t, {"en": "lasts sixty-two"})
            self.play(GrowFromEdge(rects[1], DOWN), FadeIn(tops[1]), run_time=0.7)
            self.cue(tr, t, {"en": "five point six times"})
            self.play(FadeIn(ratio), run_time=0.4)
        self.clear_all()


class S03Rewrite(LectureScene):
    def construct(self):
        notes = VGroup(*[txt(label(k), size=20, color=GREY_B)
                         for k in ("ac_compress_note", "ac_truncate_note", "ac_summarise_note")])
        names = [label("ac_compress"), label("ac_truncate"), label("ac_summarise")]
        moves, _ = flow_row(names, size=28, buff=0.8, height=1.0)
        # the gap between boxes leaves room for the wider notes under them, so neighbouring notes never touch
        gap = max(0.8, max((notes[i].width + notes[i + 1].width - moves[i].width - moves[i + 1].width) / 2 + 0.4
                           for i in range(2)))
        moves, arrows = flow_row(names, size=28, buff=gap, height=1.0)
        for b, c in zip(moves, (GOOD, HILITE, BAD)):
            b[0].set_stroke(c)
        for n, b in zip(notes, moves):
            n.next_to(b, DOWN, buff=0.3)
        row = VGroup(moves, arrows, notes).move_to(UP * 0.3)
        if row.width > 12.6:
            row.scale_to_fit_width(12.6)
        risk = txt(label("ac_more_risk"), size=22, color=GREY_B).next_to(row, DOWN, buff=0.5)
        with self.say("3.4") as (tr, t):
            self.cue(tr, t, {"en": "Compress"})
            self.play(FadeIn(moves[0]), FadeIn(notes[0]), run_time=0.4)
            self.cue(tr, t, {"en": "Truncate"})
            self.play(GrowArrow(arrows[0]), FadeIn(moves[1]), FadeIn(notes[1]), run_time=0.4)
            self.cue(tr, t, {"en": "Summarise"})
            self.play(GrowArrow(arrows[1]), FadeIn(moves[2]), FadeIn(notes[2]), FadeIn(risk), run_time=0.4)
        self.clear_all()

        # a rewrite kills the cached prefix from the edit onward
        n = 10
        cells = VGroup(*[Rectangle(width=0.95, height=0.7, stroke_width=0, fill_color=GREY_C, fill_opacity=1)
                         for _ in range(n)]).arrange(RIGHT, buff=0.08).move_to(UP * 0.4)
        lab = txt(label("ac_turns_cached"), size=22, color=GREY_B).next_to(cells, UP, buff=0.3)
        summ = Rectangle(width=cells[:4].width, height=0.7, stroke_color=HILITE, stroke_width=3, fill_color=BLACK,
                         fill_opacity=1).move_to(cells[:4])
        summ_t = txt(label("ac_summary"), size=22, color=HILITE).move_to(summ)
        key = VGroup(VGroup(Square(0.3, fill_color=GREY_C, fill_opacity=1, stroke_width=0),
                            txt(label("ac_cached"), size=22, color=GREY_B)).arrange(RIGHT, buff=0.2),
                     VGroup(Square(0.3, fill_color=LBLUE, fill_opacity=1, stroke_width=0),
                            txt(label("ac_billed_again"), size=22, color=GREY_B)).arrange(RIGHT, buff=0.2)) \
            .arrange(RIGHT, buff=0.8).next_to(cells, DOWN, buff=0.6)
        rule = txt(label("ac_rewrite_rule"), size=26, color=HILITE).next_to(key, DOWN, buff=0.5)
        with self.say("3.5") as (tr, t):
            self.play(FadeIn(lab), FadeIn(cells), FadeIn(key[0]), run_time=0.5)
            self.cue(tr, t, {"en": "kills the cached prefix"})
            self.play(FadeOut(cells[:4]), FadeIn(summ), FadeIn(summ_t), run_time=0.5)
            self.play(*[c.animate.set_fill(LBLUE) for c in cells[4:]], FadeIn(key[1]), run_time=0.6)
            self.cue(tr, t, {"en": "when the window binds"})
            self.play(FadeIn(rule), run_time=0.4)
        self.clear_all()

        # a summary keeps identifiers: what the agent can still act on
        kept = VGroup(mono(f'{MODIFY["order_id"]}: {MODIFY["item_ids"][0]} → {MODIFY["new_item_ids"][0]}',
                           size=26, color=GOOD),
                      txt(label("ac_confirmed"), size=26, color=GOOD)).arrange(RIGHT, buff=0.3)
        kept_l = txt(label("ac_kept"), size=24, color=GOOD)
        top = VGroup(kept_l, kept).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(UP * 1.6)
        rec = VGroup(*[mono(r, size=18, color=GREY_C) for r in textwrap.wrap(ORDER_RECORD, 70)[:6]]) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.08)        # the stored tool result, as the run returned it
        drop_l = txt(label("ac_dropped"), size=24, color=BAD)
        low = VGroup(drop_l, rec).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(top, DOWN, buff=0.7)
        VGroup(top, low).move_to(ORIGIN)
        cross = Cross(rec, stroke_color=BAD, stroke_width=4)
        with self.say("3.6") as (tr, t):
            self.cue(tr, t, {"en": "the order number"})
            self.play(FadeIn(kept_l), FadeIn(kept), run_time=0.6)
            self.cue(tr, t, {"en": "The agent can still act on what it kept"})
            self.play(FadeIn(drop_l), FadeIn(rec), run_time=0.5)
            self.cue(tr, t, {"en": "never recover what it threw away"})
            self.play(Create(cross), run_time=0.5)
        self.clear_all()


class S03Stores(LectureScene):
    def construct(self):
        now = tile(label("ac_tier_now"), color=LBLUE, width=6.0, size=26)
        fetch = tile(label("ac_tier_fetch"), color=GREY_B, width=6.0, size=26)
        tiers = VGroup(now, fetch).arrange(DOWN, buff=0.9).move_to(UP * 0.2)
        arr = DoubleArrow(now.get_bottom(), fetch.get_top(), buff=0.08, color=GREY_B)
        ends = txt(label("ac_session_ends"), size=22, color=GREY_B).next_to(tiers, DOWN, buff=0.4)
        with self.say("3.7") as (tr, t):
            self.play(FadeIn(now), run_time=0.4)
            self.cue(tr, t, {"en": "because the session ends"})
            self.play(FadeIn(ends), run_time=0.3)
            self.cue(tr, t, {"en": "Three stores"})
            self.play(GrowArrow(arr), FadeIn(fetch), run_time=0.5)
        self.clear_all()

        # three stores, one real example each from the run
        kv = mono(f'{MODIFY["payment_method_id"]}', size=20, color=WHITE)
        doc = txt(label("ac_sections_5_7"), size=20, color=WHITE)
        epi = VGroup(mono(f'{MODIFY["order_id"]}: {MODIFY["item_ids"][0]} → {MODIFY["new_item_ids"][0]}', size=18),
                     txt(label("ac_confirmed"), size=18)).arrange(RIGHT, buff=0.2)
        cols = VGroup()
        for name, note, ex, c in (("ac_kv_store", "ac_kv_note", kv, LBLUE), ("ac_doc_store", "ac_doc_note", doc, HILITE),
                                  ("ac_episodic", "ac_episodic_note", epi, GOOD)):
            head = tile(label(name), color=c, width=3.9, size=24)
            n_ = txt(label(note), size=20, color=GREY_B)
            if ex.width > 3.9:
                ex.scale_to_fit_width(3.9)
            cols.add(VGroup(head, n_, ex).arrange(DOWN, buff=0.35))
        cols.arrange(RIGHT, buff=0.5, aligned_edge=UP).move_to(ORIGIN)
        with self.say("3.8") as (tr, t):
            self.cue(tr, t, {"en": "A key-value store"})
            self.play(FadeIn(cols[0]), run_time=0.5)
            self.cue(tr, t, {"en": "A document store"})
            self.play(FadeIn(cols[1]), run_time=0.5)
            self.cue(tr, t, {"en": "an episodic buffer"})
            self.play(FadeIn(cols[2]), run_time=0.5)
        self.clear_all()

        # MemGPT: the model pages its own memory, like RAM and disk, through tool calls
        ram = tile(label("ac_main_context"), color=LBLUE, width=4.4, height=2.0, size=26)
        disk = tile(label("ac_external_context"), color=GREY_B, width=4.4, height=2.0, size=26)
        VGroup(ram, disk).arrange(RIGHT, buff=3.0).move_to(DOWN * 0.2)
        ram_s = txt(label("ac_like_ram"), size=22, color=GREY_B).next_to(ram, DOWN, buff=0.25)
        disk_s = txt(label("ac_like_disk"), size=22, color=GREY_B).next_to(disk, DOWN, buff=0.25)
        out = Arrow(ram.get_right() + UP * 0.4, disk.get_left() + UP * 0.4, buff=0.1, color=HILITE)
        inn = Arrow(disk.get_left() + DOWN * 0.4, ram.get_right() + DOWN * 0.4, buff=0.1, color=HILITE)
        call = txt(label("ac_tool_calls"), size=22, color=HILITE).next_to(out, UP, buff=0.15)
        head = txt(label("ac_memgpt"), size=26, color=GREY_B).to_edge(UP, buff=SAFE + 0.3)
        with self.say("3.9") as (tr, t):
            self.play(FadeIn(head), FadeIn(ram), FadeIn(disk), run_time=0.5)
            self.cue(tr, t, {"en": "like RAM and disk"})
            self.play(FadeIn(ram_s), FadeIn(disk_s), run_time=0.4)
            self.cue(tr, t, {"en": "through ordinary tool calls"})
            self.play(GrowArrow(out), GrowArrow(inn), FadeIn(call), run_time=0.6)
        self.clear_all()

        fit = code_panel(MEM_FILE, "def fit", "return [system", size=22, width=13.0, tag="shown").move_to(ORIGIN)
        keep = highlight(fit, code_lines(MEM_FILE, "keep ids and decisions")[0])
        notes = code_panel(MEM_FILE, "class Notes", "def recall", size=22, width=13.0, tag="shown").move_to(ORIGIN)
        with self.say("3.10") as (tr, t):
            self.play(FadeIn(fit), run_time=0.6)
            self.cue(tr, t, {"en": "fold the oldest turns into a summary"})
            self.play(Create(keep), run_time=0.4)
            self.cue(tr, t, {"en": "a note store"})
            self.play(FadeOut(VGroup(fit, keep)), run_time=0.3)
            self.play(FadeIn(notes), run_time=0.5)
        self.clear_all()


class S03Failure(LectureScene):
    def construct(self):
        entry = tile(label("ac_always_gift_card"), color=GREY_B, width=6.4, height=1.1, size=28).move_to(UP * 0.4)
        stamp = pill(label("ac_inferred"), BAD, size=22).next_to(entry, UR, buff=-0.2).rotate(-0.12)
        cross = Cross(entry, stroke_color=BAD, stroke_width=5)
        rule = txt(label("ac_never_infer"), size=28, color=HILITE).next_to(entry, DOWN, buff=0.9)
        with self.say("3.11") as (tr, t):
            self.cue(tr, t, {"en": "always pays by gift card"})
            self.play(FadeIn(entry), run_time=0.4)
            self.play(FadeIn(stamp, scale=1.3), run_time=0.4)
            self.cue(tr, t, {"en": "inherits a false premise"})
            self.play(Create(cross), FadeIn(rule), run_time=0.6)
        self.clear_all()

        # the store's own policy: authenticate in every conversation
        rows = VGroup(*[txt(r, size=24, color=WHITE) for r in textwrap.wrap(AUTH_RULE, 64)]) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        frame = SurroundingRectangle(rows, color=GREY_B, buff=0.3, corner_radius=0.1)
        src = mono("tau2_retail_policy.md", size=18, color=GREY_C).next_to(frame, UP, buff=0.15, aligned_edge=LEFT)
        pol = VGroup(src, frame, rows).move_to(UP * 1.4)
        then = tile(label("ac_event_past"), color=GREY_B, width=5.6, size=24)
        now = tile(label("ac_auth_now"), color=GOOD, width=5.6, size=24)
        pair = VGroup(then, now).arrange(RIGHT, buff=0.6).next_to(pol, DOWN, buff=0.8)
        with self.say("3.12") as (tr, t):
            self.play(FadeIn(pol), run_time=0.6)
            self.cue(tr, t, {"en": "even when they offer a user ID"})
            self.play(Indicate(rows[-1], color=HILITE, scale_factor=1.03), run_time=0.6)
            self.cue(tr, t, {"en": "last week's event"})
            self.play(FadeIn(then), run_time=0.4)
            self.cue(tr, t, {"en": "who is typing now"})
            self.play(FadeIn(now), run_time=0.4)
        self.clear_all()

        recap(self, "3.13", [label("ac_recap_3_cap"), label("ac_recap_3_rewrite"), label("ac_recap_3_provenance"),
                             label("ac_recap_3_recheck")])


SCENES = ["S03Window", "S03Rewrite", "S03Stores", "S03Failure"]
