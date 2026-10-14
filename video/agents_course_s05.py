"""Agent course, section 5 — retrieval-augmented generation on τ²-bench's banking_knowledge domain: a question whose
answer lives in 698 internal documents, read instead of remembered, the four stages and where each fails, chunking
by heading, two-stage retrieval, reciprocal rank fusion, the pipeline snippet (shown, not run), the captured BM25
run, and golden retrieval as the next experiment (not run).

Testbed facts: D["tau2"] (documents, words, retrieval configs), one real document from the clone
(capture_deck's BANKING path), raw/tau2_banking.json (the run). Deck numbers: D["rrf"], D["first_stage"],
capture_deck's RRF_LISTS and RRF_K.
"""
from agents_course_kit import *

T2 = D["tau2"]
RUN = raw("tau2_banking.json")
SNIP = "s5_rag_hybrid.py"
TOP = int(re.search(r"top=(\d+)", (CODE / SNIP).read_text())[1])          # what the snippet's reranker keeps
_DOC = json.loads((DECK_IN.BANKING / "documents" / "doc_bank_accounts_bank_accounts_(general)_001.json").read_text())
DOC_TITLE = _DOC["title"]
SECTIONS = [s.strip() for s in _DOC["content"].split("## ") if s.strip()]  # "Eligibility Requirements\n\n…", …
RULE = next(r.strip() for r in _DOC["content"].splitlines() if "does not exceed" in r)
CONFIGS = ("no_knowledge", RUN["retrieval_config"], "golden_retrieval")
assert all(c in T2["retrieval_configs"] for c in CONFIGS)


def doc_card(title, rows, width=6.6, size=20, title_color=HILITE):
    head = txt(title, size=size + 2, weight=BOLD, color=title_color)
    body = VGroup(*[txt(r, size=size, color=GREY_A) for r in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    g = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
    if g.width > width - 0.4:
        g.scale_to_fit_width(width - 0.4)
    box = RoundedRectangle(corner_radius=0.12, width=width, height=g.height + 0.45, stroke_color=GREY_B,
                           stroke_width=2.5, fill_color="#1b1b1f", fill_opacity=1)
    return VGroup(box, g.move_to(box))


def section_rows(sec, n=3, chars=58):
    """A document section's heading and its first lines, wrapped."""
    head, _, body = sec.partition("\n")
    rows = []
    for r in body.strip().splitlines():
        rows += textwrap.wrap(r.strip(), chars)
    return head, rows[:n]


class S05Docs(LectureScene):
    def construct(self):
        self.section_card(5)
        q = bubble("user", label("ac_s5_question"), size=24).move_to(LEFT * 3.6 + UP * 1.8)
        n = T2["banking_documents"]
        cols = 35
        cells = VGroup(*[Rectangle(width=0.13, height=0.17, stroke_width=0, fill_color=GREY_C, fill_opacity=0.9)
                         for _ in range(n)])
        cells.arrange_in_grid(cols=cols, buff=(0.05, 0.05)).move_to(RIGHT * 3.0 + DOWN * 0.5)
        shelf_label = txt(label("ac_s5_documents"), size=24, color=GREY_B).next_to(cells, UP, buff=0.25)
        with self.say("5.1") as (tr, t):
            self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": "is not in the database"})
            self.play(FadeIn(shelf_label), LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.002), run_time=1.4)

        # how many, how big, and one opened
        count = VGroup(tagged(f"{n:,}", label("ac_s5_docs_word"), size=30, value_color=HILITE, value_weight=BOLD),
                       tagged(f"{T2['banking_words']:,}", label("ac_s5_words"), size=30, value_color=HILITE,
                              value_weight=BOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        count.next_to(q, DOWN, buff=0.7).align_to(q, LEFT)
        head, rows = section_rows(SECTIONS[0], n=8)
        opened = doc_card(DOC_TITLE, [head] + rows, width=7.4, size=22).move_to(RIGHT * 2.9 + DOWN * 0.5)
        with self.say("5.2") as (tr, t):
            self.play(FadeIn(count[0]), run_time=0.5)
            self.cue(tr, t, {"en": "a hundred and thirty-seven thousand words"})
            self.play(FadeIn(count[1]), run_time=0.5)
            self.cue(tr, t, {"en": "eligibility rules"})
            self.play(Indicate(cells[0], color=HILITE, scale_factor=3), run_time=0.5)
            self.play(FadeOut(cells), FadeOut(shelf_label), FadeIn(opened, scale=0.9), run_time=0.7)
        self.clear_all()

        # weights sealed, documents open: stop asking the model to remember, ask it to read
        weights = tile(label("ac_s5_weights"), color=GREY_B, width=3.6, height=1.3, size=26).move_to(LEFT * 3.6 + UP * 0.4)
        lock = weights[0].copy().set_fill(GREY_E, opacity=1).set_stroke(width=0)   # sealed: nothing new gets in
        shelf = VGroup(*[Rectangle(width=0.32, height=1.3, stroke_color=GREY_B, stroke_width=2, fill_color=GREY_D,
                                   fill_opacity=0.6) for _ in range(9)]).arrange(RIGHT, buff=0.08)
        shelf_name = txt(label("ac_s5_documents"), size=24, color=HILITE).next_to(shelf, UP, buff=0.2)
        docs = VGroup(shelf, shelf_name).move_to(RIGHT * 3.4 + UP * 0.4)
        rem = txt(label("ac_s5_remember"), size=26, color=BAD).next_to(weights, DOWN, buff=0.35)
        cross = Line(rem.get_left(), rem.get_right(), color=BAD, stroke_width=4)
        read = txt(label("ac_s5_read"), size=26, color=GOOD).next_to(shelf, DOWN, buff=0.35)
        rag = txt(label("ac_s5_rag"), size=30, weight=BOLD, color=LBLUE).move_to(DOWN * 2.4)
        with self.say("5.3") as (tr, t):
            self.play(FadeIn(lock), FadeIn(weights), run_time=0.6)
            self.cue(tr, t, {"en": "stop asking it to remember"})
            self.play(FadeIn(rem), run_time=0.3)
            self.play(Create(cross), run_time=0.4)
            self.cue(tr, t, {"en": "ask it to read"})
            self.play(FadeIn(docs), FadeIn(read), run_time=0.6)
            self.cue(tr, t, {"en": "retrieval-augmented generation"})
            self.play(FadeIn(rag, shift=UP * 0.2), run_time=0.5)
        self.clear_all()


class S05Pipeline(LectureScene):
    def construct(self):
        names = ["ac_s5_chunk", "ac_s5_retrieve", "ac_s5_augment", "ac_s5_generate"]
        fails = ["ac_s5_fail_chunk", "ac_s5_fail_retrieve", "ac_s5_fail_augment", "ac_s5_fail_generate"]
        boxes, arrows = flow_row([label(k) for k in names], color=LBLUE, size=28, buff=0.6, width=2.6)
        under = VGroup(*[txt(label(k), size=23, color=BAD).next_to(b, DOWN, buff=0.3) for k, b in zip(fails, boxes)])
        for u, b in zip(under, boxes):
            if u.width > b.width + 0.4:
                u.scale_to_fit_width(b.width + 0.4)
        row = VGroup(boxes, arrows, under).move_to(UP * 0.3)
        with self.say("5.4") as (tr, t):
            for i, (b, cue_) in enumerate(zip(boxes, ("chunk the documents", "retrieve the top few", "augment the prompt",
                                                       "generate an answer"))):
                self.cue(tr, t, {"en": cue_})
                self.play(FadeIn(b), *([GrowArrow(arrows[i - 1])] if i else []), run_time=0.45)
            self.cue(tr, t, {"en": "Each stage fails"})
            self.play(LaggedStart(*[FadeIn(u, shift=DOWN * 0.15) for u in under], lag_ratio=0.25), run_time=1.0)

        # the ceiling: a fixed-size cut between a rule's condition and its number
        cut_at = RULE.index("does not exceed") + len("does not exceed")
        left, right = mono(RULE[:cut_at], size=28), mono(RULE[cut_at:].strip(), size=28, color=HILITE)
        pieces = VGroup(left, right).arrange(RIGHT, buff=0.2).move_to(DOWN * 1.0)
        if pieces.width > 12.2:
            pieces.scale_to_fit_width(12.2)
        gap = (left.get_right() + right.get_left()) / 2
        knife = DashedLine(gap + UP * 0.9, gap + DOWN * 0.9, color=BAD, stroke_width=4)
        knife_l = txt(label("ac_s5_fixed_cut"), size=22, color=BAD).next_to(knife, DOWN, buff=0.15)
        title = txt(DOC_TITLE, size=22, color=GREY_B).next_to(pieces, UP, buff=1.0)
        with self.say("5.5") as (tr, t):
            self.play(row.animate.scale(0.75).to_edge(UP, buff=SAFE + 0.3), run_time=0.5)
            self.play(Indicate(boxes[0], color=HILITE), FadeIn(title), FadeIn(pieces), run_time=0.6)
            self.cue(tr, t, {"en": "land in different chunks"})
            self.play(Create(knife), FadeIn(knife_l), run_time=0.5)
            self.play(left.animate.shift(LEFT * 0.35), right.animate.shift(RIGHT * 0.35), run_time=0.5)
        self.clear_all()

        # chunk by heading, with the title in front of every chunk
        heads = [section_rows(s, n=3, chars=40) for s in SECTIONS[:2]]
        src = doc_card(DOC_TITLE, [f"## {h}" for h, _ in heads], width=5.4, size=22).move_to(LEFT * 3.7)
        chunks = VGroup(*[doc_card(DOC_TITLE, [f"## {h}"] + rows, width=6.2, size=18, title_color=GREY_B)
                          for h, rows in heads]).arrange(DOWN, buff=0.4).move_to(RIGHT * 3.2)
        for c in chunks:
            c[1][0].set_color(HILITE)           # the prepended title
        links = VGroup(*[Arrow(src.get_right(), c.get_left(), buff=0.15, color=GREY_B, stroke_width=3) for c in chunks])
        cap = txt(label("ac_s5_by_heading"), size=24, color=LBLUE).to_edge(UP, buff=SAFE + 0.4)
        with self.say("5.6") as (tr, t):
            self.play(FadeIn(src), run_time=0.5)
            self.cue(tr, t, {"en": "we chunk by heading"})
            self.play(FadeIn(cap), *[GrowArrow(a) for a in links], *[FadeIn(c, shift=RIGHT * 0.2) for c in chunks],
                      run_time=0.8)
            self.cue(tr, t, {"en": "prepend the title"})
            self.play(*[Indicate(c[1][0], color=HILITE) for c in chunks], run_time=0.7)
        self.clear_all()


class S05Retrieval(LectureScene):
    def construct(self):
        # the funnel: every chunk → the first stage's candidates → the reranker's top few
        widths = (10.0, 5.6, 2.2)
        values = (None, D["first_stage"], TOP)
        rows = VGroup()
        for w, v in zip(widths, values):
            bar = RoundedRectangle(corner_radius=0.1, width=w, height=0.8, stroke_color=LBLUE, stroke_width=3,
                                   fill_color=LBLUE, fill_opacity=0.25)
            inner = txt(label("ac_s5_all_chunks"), size=26) if v is None else MathTex(str(v), font_size=40)
            rows.add(VGroup(bar, inner.move_to(bar)))
        rows.arrange(DOWN, buff=0.75).move_to(LEFT * 0.4 + DOWN * 0.1)
        notes = VGroup(txt(label("ac_s5_first_stage"), size=22, color=GREY_B),
                       txt(label("ac_s5_reranker"), size=22, color=GREY_B))
        arrows = VGroup()
        for i, nt in enumerate(notes):
            a = Arrow(rows[i].get_bottom(), rows[i + 1].get_top(), buff=0.08, color=GREY_B, stroke_width=4)
            arrows.add(a)
            nt.next_to(a, RIGHT, buff=0.4)
        owns = VGroup(txt(label("ac_s5_recall"), size=26, weight=BOLD, color=GOOD).next_to(notes[0], DOWN, buff=0.1)
                      .align_to(notes[0], LEFT),
                      txt(label("ac_s5_precision"), size=26, weight=BOLD, color=HILITE).next_to(notes[1], DOWN, buff=0.1)
                      .align_to(notes[1], LEFT))
        with self.say("5.7") as (tr, t):
            self.play(FadeIn(rows[0]), run_time=0.5)
            self.cue(tr, t, {"en": "A cheap first stage"})
            self.play(GrowArrow(arrows[0]), FadeIn(rows[1]), FadeIn(notes[0]), run_time=0.6)
            self.cue(tr, t, {"en": "An expensive reranker"})
            self.play(GrowArrow(arrows[1]), FadeIn(rows[2]), FadeIn(notes[1]), run_time=0.6)
            self.cue(tr, t, {"en": "Recall is set"})
            self.play(FadeIn(owns[0]), run_time=0.4)
            self.cue(tr, t, {"en": "precision at the second"})
            self.play(FadeIn(owns[1]), run_time=0.4)
        self.clear_all()

        # reciprocal rank fusion on the deck's two lists
        k = DECK_IN.RRF_K
        formula = MathTex(r"\mathrm{RRF}(d) = \sum_{\text{lists}} \frac{1}{" + str(k) + r" + \mathrm{rank}}", font_size=44)
        formula.to_edge(UP, buff=SAFE + 0.35)
        heads = [mono("", size=24), mono("BM25", size=24, color=LBLUE), mono("dense", size=24, color=LBLUE),
                 MathTex(r"\mathrm{RRF}", font_size=36, color=HILITE)]
        table = [heads]
        for doc, ranks in DECK_IN.RRF_LISTS.items():
            row = [mono(doc[-1].upper(), size=28, weight=BOLD)]
            for r in ranks:
                row.append(MathTex(str(r), font_size=36) if r is not None
                           else txt(label("ac_s5_missing"), size=22, color=GREY_C))
            row.append(MathTex(f"{D['rrf'][doc]:.4f}", font_size=36))
            table.append(row)
        grid = VGroup(*[m for r in table for m in r]).arrange_in_grid(rows=len(table), cols=4, buff=(1.2, 0.35))
        grid.next_to(formula, DOWN, buff=0.9)
        rank_head = txt(label("ac_s5_rank"), size=20, color=GREY_B).next_to(VGroup(heads[1], heads[2]), UP, buff=0.12)
        winner = D["rrf_order"][0]
        win_row = VGroup(*table[1 + list(DECK_IN.RRF_LISTS).index(winner)])
        win_box = SurroundingRectangle(win_row, color=GOOD, buff=0.15, corner_radius=0.08)
        a_row = VGroup(*table[1 + list(DECK_IN.RRF_LISTS).index("doc_a")])
        with self.say("5.8") as (tr, t):
            self.play(FadeIn(formula), run_time=0.5)
            self.cue(tr, t, {"en": "each document scores"})
            self.play(FadeIn(VGroup(*heads)), FadeIn(rank_head), run_time=0.4)
            for r in table[1:]:
                self.play(FadeIn(VGroup(*r[:3])), run_time=0.25)
            self.cue(tr, t, {"en": "first in one list and missing"})
            self.play(FadeIn(a_row[3]), run_time=0.4)
            self.play(Indicate(a_row, color=HILITE, scale_factor=1.03), run_time=0.5)
            self.cue(tr, t, {"en": "third in one and first"})
            self.play(*[FadeIn(r[3]) for r in table[1:] if r[3] is not a_row[3]], run_time=0.5)
            self.cue(tr, t, {"en": "and wins"})
            self.play(Create(win_box), run_time=0.5)
        self.clear_all()

        # the snippet: fifty from each search, fused, reranked to the top few, pasted with their ids
        panel = code_panel(SNIP, "def rrf", "Question: {question}", size=22, tag="shown").move_to(UP * 0.3)  # clear of the brand mark
        marks = [(c, highlight(panel, code_lines(SNIP, s)[0], last=code_lines(SNIP, e or s)[0])) for c, s, e in
                 (("fifty candidates from each search", "bm25.search(question, 50)", "dense.search(question, 50)"),
                  ("let a reranker keep the best", "rerank(question", None),
                  ("paste each one with its ID", 'f"[{p.id}] {p.text}"', None),
                  ("answer only from these passages", "Answer only from these passages", "If they do not"))]
        with self.say("5.9") as (tr, t):
            self.play(FadeIn(panel), run_time=0.7)
            for cue_, m in marks:
                self.cue(tr, t, {"en": cue_})
                self.play(Create(m), run_time=0.4)
        self.clear_all()


class S05Run(LectureScene):
    def construct(self):
        cmd = mono(f"tau2 run --domain banking_knowledge --retrieval-config {RUN['retrieval_config']}", size=24,
                   color=LBLUE)
        cmd_box = VGroup(SurroundingRectangle(cmd, color=GREY_D, buff=0.25, corner_radius=0.1, fill_color="#1b1b1f",
                                              fill_opacity=1), cmd).to_edge(UP, buff=SAFE + 0.6)
        if cmd_box.width > 12.8:
            cmd_box.scale_to_fit_width(12.8)
        stats = VGroup()
        for v, key, col in ((RUN["n_tasks"], "ac_s5_tasks", WHITE), (RUN["kb_searches"], "ac_s5_searches", WHITE),
                            (f"{round(100 * RUN['pass_1'])}\\%", "ac_s5_passed", GOOD)):
            stats.add(VGroup(MathTex(str(v), font_size=72, color=col), txt(label(key), size=26, color=GREY_B))
                      .arrange(DOWN, buff=0.2))
        stats.arrange(RIGHT, buff=1.6).move_to(DOWN * 0.4)
        head = VGroup(txt(label("ac_our_run"), size=26, weight=BOLD, color=LBLUE), run_pill()).arrange(RIGHT, buff=0.3)
        head.next_to(cmd_box, DOWN, buff=0.5)
        tag = captured_tag("tau2_banking.json").next_to(stats, DOWN, buff=0.6)
        with self.say("5.10") as (tr, t):
            self.play(FadeIn(cmd_box), run_time=0.5)
            self.cue(tr, t, {"en": "We ran the offline BM25 config"})
            self.play(FadeIn(head), FadeIn(stats[0]), run_time=0.5)
            self.cue(tr, t, {"en": "The agent searched"})
            self.play(FadeIn(stats[1]), run_time=0.4)
            self.cue(tr, t, {"en": "and passed"})
            self.play(FadeIn(stats[2]), FadeIn(tag), run_time=0.5)
        self.wait(0.6)
        self.clear_all()

        # the flag as an experiment: no documents, BM25, exactly the right documents (only BM25 run)
        base, h = -2.4, 4.0
        xs = (-4.0, 0.0, 4.0)
        ceiling = DashedLine([xs[0] - 1.4, base + h, 0], [xs[2] + 1.4, base + h, 0], color=GREY_C, stroke_width=2)
        full = MathTex(r"100\%", font_size=30, color=GREY_C).next_to(ceiling, LEFT, buff=0.15)
        floor = Line([xs[0] - 1.4, base, 0], [xs[2] + 1.4, base, 0], color=GREY_B, stroke_width=2)
        cols = VGroup()
        for x, name in zip(xs, CONFIGS):
            if name == RUN["retrieval_config"]:
                bar = Rectangle(width=2.0, height=RUN["pass_1"] * h, stroke_width=0, fill_color=LBLUE, fill_opacity=1)
                bar.move_to([x, base + RUN["pass_1"] * h / 2, 0])
                top = MathTex(f"{round(100 * RUN['pass_1'])}\\%", font_size=40).next_to(bar, UP, buff=0.12)
            else:
                bar = DashedVMobject(Rectangle(width=2.4, height=h, stroke_color=GREY_C, stroke_width=2), num_dashes=44)
                bar.move_to([x, base + h / 2, 0])
                top = txt(label("ac_s5_not_run"), size=20, color=GREY_C).move_to(bar)
                if top.width > 2.1:
                    top.scale_to_fit_width(2.1)
            name_m = mono(name, size=20, color=GREY_B).next_to([x, base, 0], DOWN, buff=0.25)
            cols.add(VGroup(bar, top, name_m))
        gap_r = txt(label("ac_s5_gap_retrieval"), size=22, color=HILITE)
        gap_r.move_to([(xs[1] + xs[2]) / 2, base + h * 0.78, 0])
        gap_m = txt(label("ac_s5_gap_reasoning"), size=22, color=GREY_A).next_to(ceiling, UP, buff=0.15).set_x(xs[2])
        bm_top = Arrow(gap_r.get_bottom() + LEFT * 0.4, cols[1][0].get_corner(UR) + RIGHT * 0.1, buff=0.1, color=HILITE,
                       stroke_width=3)
        with self.say("5.11") as (tr, t):
            self.play(Create(floor), FadeIn(cols[1]), run_time=0.6)
            self.cue(tr, t, {"en": "One config gives no documents"})
            self.play(FadeIn(cols[0]), run_time=0.4)
            self.cue(tr, t, {"en": "golden retrieval"})
            self.play(FadeIn(cols[2]), Create(ceiling), FadeIn(full), run_time=0.5)
            self.cue(tr, t, {"en": "what better retrieval can win"})
            self.play(FadeIn(gap_r), GrowArrow(bm_top), run_time=0.5)
            self.cue(tr, t, {"en": "the rest is the model's reasoning"})
            self.play(FadeIn(gap_m), run_time=0.4)
        self.clear_all()

        recap(self, "5.12", [label("ac_s5_recap_chunking"), label("ac_s5_recap_recall"),
                             label("ac_s5_recap_precision"), label("ac_s5_recap_ids"), label("ac_s5_recap_golden")])


SCENES = ["S05Docs", "S05Pipeline", "S05Retrieval", "S05Run"]
