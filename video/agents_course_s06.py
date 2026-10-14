"""Agent course, section 6 — embeddings and hybrid retrieval: BM25 as the number to beat, its blind spot
(paraphrase), cross- vs bi-encoders, contrastive training with in-batch and hard negatives, hybrid fusion,
τ²-bench's retrieval configs, retrieval as a tool, the snippet, and pinning the embedding model.

Numbers: D["tau2"] (document counts, the configs), D["batch"], D["rrf"], D["cited"] and capture_deck's inputs.
The banking documents' titles and the configs' tool lists are read from the τ²-bench clone, never typed.
"""
import re

from agents_course_kit import *

BANK = D["tau2"]
N_DOCS = BANK["banking_documents"]
DOCS = COURSE / "tau2-bench/data/tau2/domains/banking_knowledge/documents"
HYBRID_FILE = "s5_rag_hybrid.py"
RARE, COMMON = "overdraft", "account"          # the narration's two query words; their counts are D's


def doc_title(name):
    """A real banking document's title."""
    return json.loads((DOCS / f"{name}.json").read_text())["title"]


ANSWERS = doc_title("doc_checking_accounts_blue_account_005")        # "Understanding Blue Account overdraft fees"
NEAR_MISS = doc_title("doc_checking_accounts_blue_account_004")      # "Setting up overdraft protection …"


def config_tools():
    """{config: tools} from τ²-bench's knowledge README table."""
    readme = (COURSE / "tau2-bench/src/tau2/knowledge/README.md").read_text().split("## Retrieval Configs")[1]
    rows = re.findall(r"^\| `([a-z0-9_\-]+)` \| ([^|]*)\|", readme, flags=re.M)
    return {c: re.findall(r"`([^`]+)`", tools) for c, tools in rows}


def doc_card(title, color=GREY_B, size=22, width=None, mark=None):
    """A banking document by its real title; mark: a word of it to colour."""
    t = Text(title, font_size=size, color=WHITE, t2c={mark: HILITE} if mark else {})
    w = width or t.width + 0.6
    if t.width > w - 0.4:
        t.scale_to_fit_width(w - 0.4)
    r = RoundedRectangle(corner_radius=0.12, width=w, height=t.height + 0.45, stroke_color=color, stroke_width=3,
                         fill_color="#1b1b1f", fill_opacity=1)
    return VGroup(r, t.move_to(r))


class S06BM25(LectureScene):
    def construct(self):
        self.section_card(6)
        head = txt(label("ac_bm25_to_beat"), size=40, weight=BOLD, color=HILITE)
        perks = VGroup(tile(label("ac_no_training"), color=GREY_B, size=26), tile(label("ac_no_gpu"), color=GREY_B, size=26))
        perks.arrange(RIGHT, buff=0.6)
        VGroup(head, perks).arrange(DOWN, buff=0.7).move_to(UP * 0.3)
        with self.say("6.1") as (tr, t):
            self.cue(tr, t, {"en": "Start with BM25"})
            self.play(FadeIn(head, shift=UP * 0.2), run_time=0.6)
            self.cue(tr, t, {"en": "no training"})
            self.play(FadeIn(perks[0]), run_time=0.4)
            self.cue(tr, t, {"en": "no GPU"})
            self.play(FadeIn(perks[1]), run_time=0.4)
        self.clear_all()

        # the score: rarity × damped frequency; then the two words' document counts, out of N_DOCS
        f = MathTex(r"\mathrm{score}(q, d) = \sum_{w \in q}", r"\mathrm{IDF}(w)", r"\cdot",
                    r"\frac{tf\,(k_1 + 1)}{tf + k_1}", font_size=46).to_edge(UP, buff=SAFE + 0.5)
        under = VGroup(txt(label("ac_rarity"), size=24, color=HILITE).next_to(f[1], DOWN, buff=0.3),
                       txt(label("ac_damped_frequency"), size=24, color=LBLUE).next_to(f[3], DOWN, buff=0.3))
        pairs = [(mono(RARE, size=26, color=HILITE), BANK["docs_with"][RARE]),
                 (mono(COMMON, size=26), BANK["docs_with"][COMMON])]
        rects, tops, labs, floor = bars(pairs, lambda v: f"{v} / {N_DOCS}", height=2.4, step=3.6, width=1.4,
                                        base=-2.0, vmax=N_DOCS, size=28)
        rects[0].set_fill(HILITE)
        cap = txt(label("ac_documents_containing"), size=24, color=GREY_B).next_to(VGroup(rects, tops), UP, buff=0.35).set_x(0)
        rule = txt(label("ac_decides_ranking"), size=26, color=HILITE).next_to(labs, DOWN, buff=0.45)
        with self.say("6.2") as (tr, t):
            self.play(Write(f), run_time=1.0)
            self.cue(tr, t, {"en": "with diminishing returns"})
            self.play(Indicate(f[3], color=LBLUE), FadeIn(under[1]), run_time=0.6)
            self.cue(tr, t, {"en": "times how rare it is"})
            self.play(Indicate(f[1], color=HILITE), FadeIn(under[0]), run_time=0.6)
            self.cue(tr, t, {"en": "In the bank's documents"})
            self.play(Create(floor), FadeIn(labs), FadeIn(cap), run_time=0.5)
            self.play(GrowFromEdge(rects[0], DOWN), FadeIn(tops[0]), run_time=0.6)
            self.cue(tr, t, {"en": "\"account\" in"})
            self.play(GrowFromEdge(rects[1], DOWN), FadeIn(tops[1]), run_time=0.6)
            self.cue(tr, t, {"en": "So \"overdraft\" decides"})
            self.play(FadeIn(rule, shift=UP * 0.2), Indicate(rects[0], color=HILITE), run_time=0.6)
        self.clear_all()


class S06Paraphrase(LectureScene):
    def construct(self):
        q_text = label("ac_q_negative_balance")
        q = bubble("user", q_text, max_chars=60, size=26)
        who = txt(label("ac_customer_asks"), size=22, color=GREY_B).next_to(q, UP, buff=0.15, aligned_edge=LEFT)
        doc = doc_card(ANSWERS, color=GOOD, size=26, mark=RARE)
        what = txt(label("ac_answering_doc"), size=22, color=GOOD).next_to(doc, UP, buff=0.15, aligned_edge=LEFT)
        top = VGroup(who, q).move_to(UP * 1.9 + LEFT * 1.5)
        bottom = VGroup(what, doc).move_to(DOWN * 0.6 + RIGHT * 1.5)
        shared = set(re.findall(r"\w+", q_text.lower())) & set(re.findall(r"\w+", ANSWERS.lower()))
        assert not shared, shared                     # the point of the line: no word in common
        none = VGroup(txt(label("ac_shared_words"), size=26, color=GREY_B), MathTex(r"\varnothing", font_size=48, color=BAD))
        none.arrange(RIGHT, buff=0.3).next_to(bottom, DOWN, buff=0.7)
        verdict = txt(label("ac_never_read"), size=28, color=BAD, weight=BOLD).next_to(none, DOWN, buff=0.4)
        with self.say("6.3") as (tr, t):
            self.cue(tr, t, {"en": "A customer asks"})
            self.play(FadeIn(who), FadeIn(q, shift=RIGHT * 0.2), run_time=0.6)
            self.cue(tr, t, {"en": "the document that answers it"})
            self.play(FadeIn(what), FadeIn(doc, shift=LEFT * 0.2), run_time=0.6)
            self.cue(tr, t, {"en": "BM25 only sees shared words"})
            self.play(FadeIn(none), run_time=0.5)
            self.cue(tr, t, {"en": "It is not misunderstood"})
            self.play(FadeIn(verdict, shift=UP * 0.2), run_time=0.5)
        self.clear_all()


class S06Encoders(LectureScene):
    def construct(self):
        # cost per question: a cross-encoder reads every document with the question; a bi-encoder encodes the question
        pairs = [(label("ac_cross_encoder"), N_DOCS), (label("ac_bi_encoder"), 1)]
        rects, tops, labs, floor = bars(pairs, lambda v: f"{v}", height=3.6, step=4.0, width=1.6, base=-2.4, size=30)
        rects[0].set_fill(BAD)
        rects[1].set_fill(GOOD)
        unit = txt(label("ac_passes_per_question"), size=26, color=GREY_B).to_edge(UP, buff=SAFE + 0.4)
        with self.say("6.4") as (tr, t):
            self.play(FadeIn(unit), Create(floor), FadeIn(labs[0]), run_time=0.5)
            self.cue(tr, t, {"en": "A cross-encoder reads question and document together"})
            self.play(GrowFromEdge(rects[0], DOWN), run_time=0.8)
            self.cue(tr, t, {"en": "six hundred and ninety-eight passes"})
            self.play(FadeIn(tops[0]), run_time=0.4)
            self.cue(tr, t, {"en": "for a single question"})
            self.play(FadeIn(labs[1]), GrowFromEdge(rects[1], DOWN), FadeIn(tops[1]), run_time=0.5)
        self.clear_all()

        # two towers: documents encoded once, offline; a query is one pass plus dot products
        def tower(name, color, vec):
            src = tile(name, color=color, width=2.6, size=24)
            enc = tile(label("ac_encoder"), color=LBLUE, width=2.6, size=24)
            v = MathTex(vec, font_size=46, color=color)
            col = VGroup(src, enc, v).arrange(DOWN, buff=0.55)
            arrows = VGroup(Arrow(src.get_bottom(), enc.get_top(), buff=0.08, color=GREY_B),
                            Arrow(enc.get_bottom(), v.get_top(), buff=0.08, color=GREY_B))
            return VGroup(col, arrows)
        qt = tower(label("ac_question"), WHITE, r"\vec q").move_to(LEFT * 3.2 + UP * 0.3)
        dt = tower(label("ac_document"), GREY_B, r"\vec d").move_to(RIGHT * 3.2 + UP * 0.3)
        off = txt(label("ac_offline_once"), size=22, color=GOOD).next_to(dt, RIGHT, buff=0.3).shift(UP * 0.3)
        per = txt(label("ac_per_query"), size=22, color=HILITE).next_to(qt, LEFT, buff=0.3).shift(UP * 0.3)
        dot = MathTex(r"\vec q \cdot \vec d", font_size=56, color=HILITE).move_to(DOWN * 2.6)
        links = VGroup(Line(qt[0][2].get_bottom(), dot.get_left() + LEFT * 0.1, color=GREY_B),
                       Line(dt[0][2].get_bottom(), dot.get_right() + RIGHT * 0.1, color=GREY_B))
        arith = txt(label("ac_arithmetic_not_model"), size=24, color=GREY_B).next_to(dot, RIGHT, buff=0.5)
        bi = txt(label("ac_bi_encoder"), size=30, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        with self.say("6.5") as (tr, t):
            self.play(FadeIn(bi), run_time=0.4)
            self.cue(tr, t, {"en": "encodes the question and each document separately"})
            self.play(FadeIn(qt), FadeIn(dt), run_time=0.8)
            self.cue(tr, t, {"en": "encoded once, offline"})
            self.play(FadeIn(off), run_time=0.4)
            self.cue(tr, t, {"en": "A query becomes one model pass"})
            self.play(FadeIn(per), run_time=0.4)
            self.cue(tr, t, {"en": "plus dot products"})
            self.play(Create(links), FadeIn(dot), run_time=0.6)
            self.cue(tr, t, {"en": "which is arithmetic"})
            self.play(FadeIn(arith), run_time=0.4)
        self.clear_all()


class S06Contrastive(LectureScene):
    def construct(self):
        n = D["batch"]["pairs"]
        sim = np.full((n, n), 38, dtype=np.uint8)               # every other pair in the batch: pushed apart
        np.fill_diagonal(sim, 255)                               # each question's own document: pulled close
        rgb = np.stack([sim * 0.96, sim * 0.74, sim * 0.44], axis=-1).astype(np.uint8)   # HILITE's hue
        grid = ImageMobject(rgb).set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"]).set_height(4.6)
        grid.move_to(LEFT * 3.6 + DOWN * 0.3)
        frame = SurroundingRectangle(grid, color=GREY_B, buff=0, stroke_width=2)
        ql = txt(label("ac_questions_axis"), size=22, color=GREY_B).rotate(PI / 2).next_to(frame, LEFT, buff=0.2)
        dl = txt(label("ac_documents_axis"), size=22, color=GREY_B).next_to(frame, UP, buff=0.2)
        side = VGroup(tagged(n, label("ac_pairs"), size=34),
                      tagged(D["batch"]["negatives_each"], label("ac_free_negatives"), size=34, value_color=HILITE))
        side.arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        room = (config.frame_width / 2 - SAFE - 0.3) - (frame.get_right()[0] + 0.6)
        if side.width > room:
            side.scale_to_fit_width(room)
        side.next_to(frame, RIGHT, buff=0.6)
        with self.say("6.6") as (tr, t):
            self.play(FadeIn(grid), Create(frame), FadeIn(ql), FadeIn(dl), run_time=0.8)
            self.cue(tr, t, {"en": "In a batch of sixty-four pairs"})
            self.play(FadeIn(side[0]), run_time=0.4)
            self.cue(tr, t, {"en": "sixty-three wrong documents for free"})
            self.play(FadeIn(side[1]), run_time=0.4)
        self.clear_all()

        # a hard negative: a real document that shares the topic but does not answer the question
        q = bubble("user", label("ac_q_negative_balance"), max_chars=60, size=24).to_edge(UP, buff=SAFE + 0.5)
        pos = doc_card(ANSWERS, color=GOOD, size=24)
        neg = doc_card(NEAR_MISS, color=BAD, size=24)
        VGroup(pos, neg).arrange(DOWN, buff=1.0).next_to(q, DOWN, buff=0.9).shift(RIGHT * 1.2)
        pos_l = txt(label("ac_positive"), size=22, color=GOOD).next_to(pos, LEFT, buff=0.3)
        neg_l = VGroup(txt(label("ac_hard_negative"), size=22, color=BAD),
                       txt(label("ac_from_bm25"), size=20, color=GREY_B)).arrange(DOWN, aligned_edge=RIGHT, buff=0.1)
        neg_l.next_to(neg, DOWN, buff=0.2).align_to(neg, RIGHT)
        gain = VGroup(txt(label("ac_dpr"), size=24, color=LBLUE),
                      VGroup(Text("+" + D["cited"]["dpr_gain_points"].replace("$--$", "–"), font_size=36,
                                  color=HILITE, weight=BOLD),
                             txt(label("ac_points_over_bm25"), size=24)).arrange(RIGHT, buff=0.2))
        gain.arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(DL, buff=SAFE + 0.4)
        with self.say("6.7") as (tr, t):
            self.play(FadeIn(q), FadeIn(pos), FadeIn(pos_l), run_time=0.6)
            self.cue(tr, t, {"en": "documents that look right but aren't"})
            self.play(FadeIn(neg, shift=UP * 0.2), FadeIn(neg_l), run_time=0.6)
            self.cue(tr, t, {"en": "Karpukhin and colleagues"})
            self.play(FadeIn(gain), run_time=0.5)
        self.clear_all()


class S06Hybrid(LectureScene):
    def construct(self):
        # two rankings that disagree, fused by section 5's RRF (its own example lists)
        lists = DECK_IN.RRF_LISTS
        def ranking(i):
            return [d for d, r in sorted(lists.items(), key=lambda kv: kv[1][i] or 99) if r[i] is not None]
        def column(head, color, ids):
            h = txt(head, size=24, color=color)
            rows = VGroup(*[VGroup(mono(f"{k}.", size=22, color=GREY_B), mono(d, size=24))
                            .arrange(RIGHT, buff=0.2) for k, d in enumerate(ids, 1)]).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
            return VGroup(h, rows).arrange(DOWN, buff=0.35)
        sparse = column(label("ac_sparse"), HILITE, ranking(0))
        dense = column(label("ac_dense"), LBLUE, ranking(1))
        fused = column(label("ac_fused"), GOOD, D["rrf_order"])
        VGroup(sparse, dense).arrange(DOWN, buff=0.6).move_to(LEFT * 3.4)
        fused.move_to(RIGHT * 3.4)
        weak = VGroup(txt(label("ac_misses_paraphrase"), size=20, color=GREY_B).next_to(sparse, RIGHT, buff=0.4),
                      txt(label("ac_blurs_exact_tokens"), size=20, color=GREY_B).next_to(dense, RIGHT, buff=0.4))
        x0 = max(weak[0].get_right()[0], weak[1].get_right()[0]) + 0.2
        arrows = VGroup(Arrow([x0, sparse.get_y(), 0], fused.get_left(), buff=0.2, color=GREY_B),
                        Arrow([x0, dense.get_y(), 0], fused.get_left(), buff=0.2, color=GREY_B))
        VGroup(sparse, dense, fused, weak, arrows).scale(1.3).move_to(ORIGIN)
        with self.say("6.8") as (tr, t):
            self.cue(tr, t, {"en": "Dense retrieval blurs exact tokens"})
            self.play(FadeIn(dense), FadeIn(weak[1]), run_time=0.6)
            self.cue(tr, t, {"en": "sparse misses paraphrase"})
            self.play(FadeIn(sparse), FadeIn(weak[0]), run_time=0.6)
            self.cue(tr, t, {"en": "fuse them"})
            self.play(GrowArrow(arrows[0]), GrowArrow(arrows[1]), FadeIn(fused), run_time=0.8)
        self.clear_all()

        # τ²-bench's retrieval configs, from its README: the one we ran is marked
        tools = config_tools()
        ran = raw("tau2_banking.json")["retrieval_config"]
        shown = ["bm25", "openai_embeddings", "alltools"]
        assert ran in shown and all(c in tools for c in shown)
        hdr = VGroup(txt(label("ac_config"), size=28, color=GREY_B), txt(label("ac_kb_tools"), size=28, color=GREY_B))
        rows = [VGroup(mono(c, size=30, color=HILITE if c == ran else WHITE),
                       mono(", ".join(tools[c]), size=28, color=GREY_A)) for c in shown]
        rr = VGroup(mono(f"{ran}_reranker", size=30, color=WHITE), txt(label("ac_reranker_suffix"), size=28, color=GREY_A))
        rows.insert(2, rr)
        table = VGroup(hdr, *rows)
        for r in table:
            r.arrange(RIGHT, buff=0.5)
        table.arrange(DOWN, buff=0.5)
        x1 = max(r[0].width for r in table) + 0.7
        for r in table:
            r[0].align_to(ORIGIN, LEFT)
            r[1].align_to(RIGHT * x1, LEFT)
        if table.width > 11.8:
            table.scale_to_fit_width(11.8)
        table.move_to(UP * 0.5)
        line_ = Line(table.get_left() + LEFT * 0.2, table.get_right() + RIGHT * 0.2, color=GREY_D).next_to(hdr, DOWN, buff=0.22)
        line_.set_x(table.get_x())
        mark = VGroup(run_pill(20), captured_tag("tau2_banking.json").scale(1.2)).arrange(RIGHT, buff=0.3)
        mark.next_to(table, DOWN, buff=0.6)
        with self.say("6.9") as (tr, t):
            self.play(FadeIn(hdr), Create(line_), run_time=0.4)
            self.cue(tr, t, {"en": "BM25, dense embeddings"})
            self.play(FadeIn(rows[0]), FadeIn(rows[1]), run_time=0.6)
            self.cue(tr, t, {"en": "a reranker added with one suffix"})
            self.play(FadeIn(rows[2]), run_time=0.4)
            self.cue(tr, t, {"en": "an all-tools mode"})
            self.play(FadeIn(rows[3]), run_time=0.5)
            self.play(Indicate(rows[0][0], color=HILITE), FadeIn(mark), run_time=0.6)
        self.clear_all()

        # retrieval as a tool: section 1's loop, its tools now the document searches and a shell
        model = tile(label("ac_model"), color=LBLUE, width=2.6, size=26).move_to(LEFT * 3.6)
        kb = VGroup(*[tile_mono(n) for n in tools["alltools"]]).arrange(DOWN, buff=0.3).move_to(RIGHT * 3.0)
        go = CurvedArrow(model.get_top() + RIGHT * 0.3, kb.get_top() + LEFT * 0.6, angle=-TAU / 6, color=GREY_B)
        back = CurvedArrow(kb.get_bottom() + LEFT * 0.6, model.get_bottom() + RIGHT * 0.3, angle=-TAU / 6, color=HILITE)
        cap = txt(label("ac_retrieval_as_tool"), size=28, color=HILITE).to_edge(DOWN, buff=SAFE + 0.6)
        with self.say("6.10") as (tr, t):
            self.play(FadeIn(model), FadeIn(kb), run_time=0.6)
            self.cue(tr, t, {"en": "again and again"})
            self.play(Create(go), Create(back), run_time=0.8)
            self.play(FadeIn(cap), run_time=0.4)
            self.cue(tr, t, {"en": "the agent loop from section one"})
            self.play(Indicate(VGroup(go, back), color=HILITE), run_time=0.8)
        self.clear_all()

        # the snippet: two searches, one fusion, ranked by position
        panel = code_panel(HYBRID_FILE, "def rrf", "dense.search(question, 50)", size=22, tag="shown").move_to(ORIGIN)
        by_rank = highlight(panel, code_lines(HYBRID_FILE, "1 / (k + rank)")[0])
        call = highlight(panel, code_lines(HYBRID_FILE, "candidates = rrf(")[0],
                         last=code_lines(HYBRID_FILE, "dense.search(question, 50)")[0])
        with self.say("6.11") as (tr, t):
            self.play(FadeIn(panel), run_time=0.7)
            self.cue(tr, t, {"en": "two searches and one fusion"})
            self.play(Create(call), run_time=0.5)
            self.cue(tr, t, {"en": "ranked by position"})
            self.play(Create(by_rank), run_time=0.5)
        self.clear_all()

        # pin the embedding model: a new version makes every stored vector stale
        pinned = txt(label("ac_emb_pinned"), size=34, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.5)
        old = VGroup(*[Rectangle(width=2.6, height=0.32, stroke_width=0, fill_color=LBLUE, fill_opacity=0.9)
                       for _ in range(6)]).arrange(DOWN, buff=0.12)
        old_tag = mono("v1", size=24, color=LBLUE).next_to(old, UP, buff=0.2)
        old_cap = txt(label("ac_stored_vectors"), size=22, color=GREY_B).next_to(old, DOWN, buff=0.25)
        store = VGroup(old_tag, old, old_cap).move_to(LEFT * 2.6 + DOWN * 0.3)
        new = tile(label("ac_new_model_version"), color=BAD, size=24)
        new_tag = mono("v2", size=24, color=BAD).next_to(new, UP, buff=0.15)
        newg = VGroup(new_tag, new).move_to(RIGHT * 3.2 + DOWN * 0.3)
        crosses = VGroup(*[Cross(r, stroke_color=BAD, stroke_width=3, scale_factor=0.9) for r in old])
        stale = txt(label("ac_reembed_all"), size=26, color=BAD).next_to(store, DOWN, buff=0.35)
        with self.say("6.12") as (tr, t):
            self.play(FadeIn(pinned), FadeIn(store), run_time=0.6)
            self.cue(tr, t, {"en": "A new model version"})
            self.play(FadeIn(newg, shift=LEFT * 0.3), run_time=0.5)
            self.cue(tr, t, {"en": "invalidates every stored vector"})
            self.play(LaggedStart(*[Create(c) for c in crosses], lag_ratio=0.1), FadeIn(stale), run_time=0.8)
        self.clear_all()

        recap(self, "6.13", [label("ac_recap_6_bm25"), label("ac_recap_6_bi"), label("ac_recap_6_neg"),
                             label("ac_recap_6_tool"), label("ac_recap_6_hybrid")])


def tile_mono(name, color=HILITE):
    """A tool by its real name, boxed."""
    t = mono(name, size=24, color=color)
    r = RoundedRectangle(corner_radius=0.12, width=t.width + 0.5, height=0.8, stroke_color=color, stroke_width=3)
    return VGroup(r, t.move_to(r))


SCENES = ["S06BM25", "S06Paraphrase", "S06Encoders", "S06Contrastive", "S06Hybrid"]
