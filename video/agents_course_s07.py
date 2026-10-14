"""Agent course, section 7 — vector indexes and databases: exact search is linear; the banking documents are small
enough to scan; IVF, PQ and HNSW each trade recall for speed or memory; what a vector database adds; filtering;
the HNSW snippet and its one knob; measuring recall against exact search.

Numbers: D["banking_mb"], D["ivf"], D["pq"], D["hnsw"], D["filter"], D["tau2"]["banking_documents"] and capture_deck's
inputs (D_EMB, IVF_*, PQ_*, HNSW_*, FILTER_KEEP, WANT, EXACT_SCAN_LIMIT). The cells, codes and graph drawn here are
sketches of the structures (seeded), not data: no number is read off them.
"""
import math

from agents_course_kit import *

N_DOCS = D["tau2"]["banking_documents"]
INDEX_FILE = "s6_vector_index.py"
RNG = np.random.default_rng(7)
FLOAT_B = D["pq"]["bytes_before"] // DECK_IN.D_EMB      # bytes per float32 component, as capture_deck counts them


def tex_int(n):
    """1000000 → '1{,}000{,}000' for MathTex."""
    return f"{n:,}".replace(",", "{,}")


def pow10(n):
    """10**6 → '10^{6}' (n must be a power of ten)."""
    e = round(math.log10(n))
    assert 10 ** e == n, n
    return f"10^{{{e}}}"


class S07Scan(LectureScene):
    def construct(self):
        self.section_card(7)
        # exact search: cost grows with the corpus; a straight line on log axes
        ax = Axes(x_range=[3, 9, 1], y_range=[3, 9, 1], x_length=7.0, y_length=4.2, tips=False,
                  axis_config={"color": GREY_B}).shift(DOWN * 0.3)
        ticks = VGroup(*[MathTex(f"10^{{{k}}}", font_size=28, color=GREY_B).next_to(ax.c2p(k, 3), DOWN, buff=0.2)
                         for k in range(3, 10, 2)])
        xl = txt(label("ac_corpus_size"), size=24, color=GREY_B).next_to(ticks, DOWN, buff=0.2)
        yl = txt(label("ac_search_time"), size=24, color=GREY_B).next_to(ax, UP, buff=0.25).align_to(ax, LEFT)
        line_ = ax.plot(lambda x: x, x_range=[3, 9], color=LBLUE, stroke_width=5)
        a, b = 4, 6
        da, db = Dot(ax.c2p(a, a), color=HILITE), Dot(ax.c2p(b, b), color=HILITE)
        times = MathTex(rf"\times {10 ** b // 10 ** a}", font_size=40, color=HILITE).next_to(ax.c2p((a + b) / 2, (a + b) / 2), UL, buff=0.3)
        with self.say("7.1") as (tr, t):
            self.play(Create(ax), FadeIn(ticks), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.cue(tr, t, {"en": "its cost is linear in the corpus"})
            self.play(Create(line_), run_time=0.8)
            self.cue(tr, t, {"en": "a hundred times the data"})
            self.play(FadeIn(da), FadeIn(db), FadeIn(times), run_time=0.6)
        self.clear_all()

        # the banking documents: N × D_EMB floats × 4 bytes, under three megabytes: just scan
        size = MathTex(rf"{N_DOCS} \times {tex_int(DECK_IN.D_EMB)} \times {FLOAT_B}\ \mathrm{{B}} = {D['banking_mb']}\ \mathrm{{MB}}",
                       font_size=54).move_to(UP * 1.4)
        under = VGroup(txt(label("ac_vectors"), size=22, color=GREY_B).next_to(size[0][0:3], DOWN, buff=0.25),
                       txt(label("ac_floats"), size=22, color=GREY_B).next_to(size[0][4:9], DOWN, buff=0.25))
        recall = MathTex(r"\mathrm{recall} = 1", font_size=48, color=GOOD).next_to(size, DOWN, buff=1.0)
        limit = VGroup(MathTex(rf"< {pow10(DECK_IN.EXACT_SCAN_LIMIT)}", font_size=52, color=HILITE),
                       txt(label("ac_scan_below"), size=30, color=HILITE)).arrange(RIGHT, buff=0.35)
        limit.next_to(recall, DOWN, buff=0.7)
        assert D["banking_under_limit"]
        with self.say("7.2") as (tr, t):
            self.play(Write(size), FadeIn(under), run_time=1.0)
            self.cue(tr, t, {"en": "with recall exactly one"})
            self.play(FadeIn(recall), run_time=0.4)
            self.cue(tr, t, {"en": "Below about a hundred thousand vectors"})
            self.play(FadeIn(limit, shift=UP * 0.2), run_time=0.5)
        self.clear_all()

        names = [(label("ac_ivf"), label("ac_ivf_what"), LBLUE), (label("ac_pq"), label("ac_pq_what"), HILITE),
                 (label("ac_hnsw"), label("ac_hnsw_what"), RLGREEN)]
        tiles = VGroup(*[VGroup(tile(n, color=c, width=3.2, height=1.2, size=36),
                                txt(w, size=22, color=GREY_B)).arrange(DOWN, buff=0.3) for n, w, c in names])
        tiles.arrange(RIGHT, buff=0.8)
        with self.say("7.3") as (tr, t):
            self.cue(tr, t, {"en": "three ideas cut the work"})
            self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in tiles], lag_ratio=0.3), run_time=1.2)
        self.clear_all()


class S07IVF(LectureScene):
    def construct(self):
        # a sketch of IVF: cells around centroids; only the cells nearest the query are opened
        W, H, res = 7.6, 4.6, 0.012
        cents = np.column_stack([RNG.uniform(-W / 2, W / 2, 30), RNG.uniform(-H / 2, H / 2, 30)])
        q = np.array([0.4, 0.2])
        probe = set(np.argsort(((cents - q) ** 2).sum(1))[:DECK_IN.IVF_NPROBE])
        xs, ys = np.arange(-W / 2, W / 2, res), np.arange(H / 2, -H / 2, -res)
        gx, gy = np.meshgrid(xs, ys)
        cell = ((gx[..., None] - cents[:, 0]) ** 2 + (gy[..., None] - cents[:, 1]) ** 2).argmin(-1)
        edge = (np.diff(cell, axis=0, prepend=cell[:1]) != 0) | (np.diff(cell, axis=1, prepend=cell[:, :1]) != 0)
        edge = edge | np.roll(edge, 1, 0) | np.roll(edge, 1, 1)          # two pixels wide, visible at 1080p
        img = np.zeros(cell.shape + (3,), dtype=np.uint8)
        shade = np.isin(cell, list(probe))
        img[shade] = (58, 53, 183)                              # RLBLUE: the probed cells
        img[edge] = (150, 150, 150)
        cells = ImageMobject(img).set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"]).set_width(W)
        cells.move_to(LEFT * 2.4 + DOWN * 0.2)
        to_scene = lambda p: cells.get_center() + np.array([p[0], p[1], 0])
        qd = Star(n=5, outer_radius=0.16, color=HILITE, fill_opacity=1).move_to(to_scene(q))
        # a point just outside the probed cells, close to the query: the neighbour IVF loses
        outside = [(np.hypot(x - q[0], y - q[1]), x, y) for x, y, c in
                   zip(gx.ravel()[::7], gy.ravel()[::7], cell.ravel()[::7]) if c not in probe]
        _, lx, ly = min(outside)
        lost = Dot(to_scene((lx + 0.08 * np.sign(lx - q[0]), ly + 0.08 * np.sign(ly - q[1]))), color=BAD, radius=0.09)
        lost_l = txt(label("ac_lost_neighbour"), size=22, color=BAD)
        side = VGroup(
            tagged(DECK_IN.IVF_NPROBE, label("ac_cells_probed"), size=28),
            MathTex(rf"{tex_int(DECK_IN.IVF_NLIST)} + {DECK_IN.IVF_NPROBE} \times {tex_int(DECK_IN.IVF_N // DECK_IN.IVF_NLIST)}",
                    rf"= {tex_int(D['ivf']['ops'])}", font_size=38),
            VGroup(MathTex(r"\text{vs}\ ", tex_int(DECK_IN.IVF_N), font_size=38, color=GREY_B)),
            txt(label("ac_distance_computations"), size=22, color=GREY_B))
        side.arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(cells, RIGHT, buff=0.5)
        if side.get_right()[0] > config.frame_width / 2 - SAFE - 0.2:
            side.scale_to_fit_width(config.frame_width / 2 - SAFE - 0.2 - side.get_left()[0]).next_to(cells, RIGHT, buff=0.5)
        lost_l.next_to(cells, DOWN, buff=0.25).align_to(cells, LEFT)
        with self.say("7.4") as (tr, t):
            self.cue(tr, t, {"en": "IVF clusters the corpus into cells"})
            self.play(FadeIn(cells), run_time=0.8)
            self.cue(tr, t, {"en": "opens only the cells nearest the query"})
            self.play(FadeIn(qd, scale=1.6), FadeIn(side[0]), run_time=0.6)
            self.cue(tr, t, {"en": "that is nine thousand distance computations"})
            self.play(FadeIn(side[1]), FadeIn(side[3]), run_time=0.6)
            self.cue(tr, t, {"en": "instead of a million"})
            self.play(FadeIn(side[2]), run_time=0.4)
            self.cue(tr, t, {"en": "A neighbour sitting just across a cell boundary"})
            self.play(FadeIn(lost, scale=1.6), FadeIn(lost_l), run_time=0.6)
        self.clear_all()


class S07PQ(LectureScene):
    def construct(self):
        m = DECK_IN.PQ_M
        pq = D["pq"]
        seg_w = 12.0 / m
        vec = VGroup(*[Rectangle(width=seg_w, height=0.7, stroke_width=0.6, stroke_color=BLACK,
                                 fill_color=interpolate_color(ManimColor(LBLUE), ManimColor(RLGREEN), RNG.uniform()),
                                 fill_opacity=1) for _ in range(m)]).arrange(RIGHT, buff=0).move_to(UP * 1.6)
        vec_l = VGroup(txt(label("ac_one_vector"), size=24, color=GREY_B),
                       MathTex(rf"{tex_int(DECK_IN.D_EMB)} \times {FLOAT_B}\ \mathrm{{B}} = {tex_int(pq['bytes_before'])}\ \mathrm{{B}}",
                               font_size=34)).arrange(RIGHT, buff=0.4).next_to(vec, UP, buff=0.3)
        codes = VGroup(*[Square(seg_w * 0.8, stroke_width=0, fill_color=HILITE, fill_opacity=0.35 + 0.65 * RNG.uniform())
                         for _ in range(m)])
        for c, s in zip(codes, vec):
            c.move_to(s.get_center() + DOWN * 1.5)
        links = VGroup(*[Line(s.get_bottom(), c.get_top(), stroke_width=1, color=GREY_D) for s, c in zip(vec, codes)])
        code_l = txt(label("ac_one_byte_each"), size=24, color=HILITE).next_to(codes, DOWN, buff=0.3)
        sizes = VGroup(
            VGroup(MathTex(rf"{tex_int(pq['bytes_before'])}\ \mathrm{{B}} \to {pq['bytes_after']}\ \mathrm{{B}}", font_size=44),
                   txt(label("ac_per_vector"), size=24, color=GREY_B)).arrange(RIGHT, buff=0.35),
            VGroup(MathTex(rf"{tex_int(pq['gb_before'])}\ \mathrm{{GB}} \to {pq['gb_after']}\ \mathrm{{GB}}", font_size=44, color=GOOD),
                   txt(label("ac_billion_vectors"), size=24, color=GREY_B)).arrange(RIGHT, buff=0.35))
        sizes.arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(code_l, DOWN, buff=0.5)
        assert DECK_IN.PQ_N == 10 ** 9 and pq["reduction"] == m
        with self.say("7.5") as (tr, t):
            self.cue(tr, t, {"en": "Product quantization compresses each vector"})
            self.play(FadeIn(vec), FadeIn(vec_l), run_time=0.6)
            self.cue(tr, t, {"en": "Split it into sixty-four pieces"})
            self.play(Indicate(vec, color=WHITE, scale_factor=1.02), run_time=0.6)
            self.cue(tr, t, {"en": "store each piece as one byte"})
            self.play(Create(links), LaggedStart(*[FadeIn(c) for c in codes], lag_ratio=0.02), FadeIn(code_l), run_time=1.0)
            self.cue(tr, t, {"en": "Four thousand ninety-six bytes become sixty-four"})
            self.play(FadeIn(sizes[0]), run_time=0.5)
            self.cue(tr, t, {"en": "a billion vectors fit"})
            self.play(FadeIn(sizes[1]), run_time=0.5)
        self.clear_all()


class S07HNSW(LectureScene):
    def construct(self):
        # a sketch of HNSW: sparser copies of the neighbour graph stacked on top; search walks down greedily
        counts = (40, 12, 4)
        layers, planes = [], VGroup()
        pts_all = RNG.uniform(-1, 1, (counts[0], 2))
        for k, n in enumerate(counts):
            idx = np.arange(n)                          # each layer keeps a prefix of the one below
            y0 = -2.3 + 1.75 * k
            plane = Polygon([-4.2, y0 - 0.55, 0], [3.0, y0 - 0.55, 0], [4.2, y0 + 0.55, 0], [-3.0, y0 + 0.55, 0],
                            stroke_color=GREY_D, stroke_width=1.5, fill_color=GREY_E, fill_opacity=0.25)
            to = lambda p, y0=y0: np.array([p[0] * 3.3 + p[1] * 0.6, y0 + p[1] * 0.45, 0])
            pos = {i: to(pts_all[i]) for i in idx}
            dots = VGroup(*[Dot(pos[i], radius=0.05, color=GREY_B) for i in idx])
            edges = VGroup()
            for i in idx:
                near = sorted(idx, key=lambda j: np.sum((pts_all[i] - pts_all[j]) ** 2))[1:3]
                edges.add(*[Line(pos[i], pos[j], stroke_width=1, color=GREY_C) for j in near])
            layers.append((pos, dots, edges))
            planes.add(plane)
        graph = VGroup(planes, *[VGroup(e, d) for _, d, e in layers]).move_to(LEFT * 1.6)
        # greedy path: enter at the top layer's first node, step to the neighbour closest to the target, drop down
        target = 17
        path_pts, cur = [], 0
        for k in range(len(counts) - 1, -1, -1):
            pos = layers[k][0]
            ids = list(pos)
            while True:
                path_pts.append(layers[k][1][ids.index(cur)].get_center())
                nxt = min(ids, key=lambda j: np.sum((pts_all[j] - pts_all[target]) ** 2) + 0.05 * np.sum((pts_all[j] - pts_all[cur]) ** 2))
                if nxt == cur or np.sum((pts_all[nxt] - pts_all[target]) ** 2) >= np.sum((pts_all[cur] - pts_all[target]) ** 2):
                    break
                cur = nxt
        path = VMobject(color=HILITE, stroke_width=4).set_points_as_corners(path_pts)
        entry = txt(label("ac_entry"), size=22, color=HILITE).next_to(path_pts[0], UP, buff=0.15)
        hit = Dot(path_pts[-1], radius=0.1, color=HILITE)
        side = VGroup(tagged(DECK_IN.HNSW_M, label("ac_links_per_node"), size=28),
                      MathTex(rf"\log_{{{DECK_IN.HNSW_M}}}\left({pow10(DECK_IN.HNSW_N)}\right) \approx {D['hnsw']['layers']}",
                              font_size=40),
                      txt(label("ac_layers"), size=24, color=GREY_B))
        side.arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(graph, RIGHT, buff=0.4)
        if side.get_right()[0] > config.frame_width / 2 - SAFE - 0.2:
            side.scale_to_fit_width(config.frame_width / 2 - SAFE - 0.2 - side.get_left()[0]).next_to(graph, RIGHT, buff=0.4)
        with self.say("7.6") as (tr, t):
            self.cue(tr, t, {"en": "HNSW builds a graph of near neighbours"})
            self.play(FadeIn(planes[0]), FadeIn(graph[1]), run_time=0.7)
            self.cue(tr, t, {"en": "sparser copies stacked on top"})
            self.play(FadeIn(planes[1:]), FadeIn(graph[2]), FadeIn(graph[3]), run_time=0.7)
            self.cue(tr, t, {"en": "Search enters at the top"})
            self.play(FadeIn(entry), Create(path), run_time=1.4)
            self.play(FadeIn(hit, scale=1.5), run_time=0.3)
            self.cue(tr, t, {"en": "With sixteen links per node"})
            self.play(FadeIn(side), run_time=0.6)
        self.clear_all()


class S07Database(LectureScene):
    def construct(self):
        core = tile(label("ac_vector_index"), color=LBLUE, width=3.4, height=1.2, size=30)
        parts = [label("ac_payload"), label("ac_filters"), label("ac_live_updates"), label("ac_persistence")]
        ring = VGroup(*[tile(p, color=GREY_B, size=24) for p in parts])
        for t_, ang in zip(ring, (90, 0, 270, 180)):
            t_.move_to(core.get_center() + np.array([3.6 * np.cos(np.radians(ang)), 1.7 * np.sin(np.radians(ang)), 0]))
        for t_ in (core, *ring):
            t_[0].set_fill(BLACK, 1)
        spokes = VGroup(*[Line(core.get_center(), t_.get_center(), color=GREY_D, stroke_width=2) for t_ in ring])
        spokes.set_z_index(-1)
        sys_ = VGroup(spokes, core, ring).move_to(UP * 0.5)
        lib = VGroup(txt(label("ac_library"), size=24, color=GREY_B), mono("FAISS", size=26)).arrange(RIGHT, buff=0.3)
        dbs = VGroup(txt(label("ac_databases"), size=24, color=GREY_B),
                     *[mono(n, size=26) for n in ("pgvector", "Qdrant", "Pinecone")]).arrange(RIGHT, buff=0.3)
        names = VGroup(lib, dbs).arrange(RIGHT, buff=1.2).to_edge(DOWN, buff=SAFE + 0.5)
        with self.say("7.7") as (tr, t):
            self.play(FadeIn(core), run_time=0.4)
            self.cue(tr, t, {"en": "the text with each vector"})
            for s, t_ in zip(spokes, ring):
                self.play(Create(s), FadeIn(t_), run_time=0.35)
            self.cue(tr, t, {"en": "FAISS is a library"})
            self.play(FadeIn(lib), run_time=0.4)
            self.cue(tr, t, {"en": "pgvector, Qdrant and Pinecone"})
            self.play(FadeIn(dbs), run_time=0.4)
        self.clear_all()

        # filtering after the search: of WANT results, a FILTER_KEEP share survives — half a result
        want, keep = DECK_IN.WANT, DECK_IN.FILTER_KEEP
        slots = VGroup(*[Square(0.8, stroke_color=GREY_B, stroke_width=2.5) for _ in range(want)]).arrange(RIGHT, buff=0.18)
        slots.move_to(UP * 1.6)
        frac_ = D["filter"]["post_survive"]
        survivor = Rectangle(width=0.8 * frac_, height=0.8, stroke_width=0, fill_color=GOOD, fill_opacity=1)
        survivor.align_to(slots[0], LEFT).align_to(slots[0], DOWN)
        after = txt(label("ac_filter_after"), size=28, color=BAD).next_to(slots, UP, buff=0.35)
        eq = VGroup(MathTex(rf"{want} \times {keep} = {frac_}", font_size=48),
                    txt(label("ac_results_survive"), size=26, color=GREY_B)).arrange(RIGHT, buff=0.35).next_to(slots, DOWN, buff=0.4)
        with self.say("7.8") as (tr, t):
            self.cue(tr, t, {"en": "Ask for the ten nearest documents"})
            self.play(FadeIn(slots), run_time=0.5)
            self.cue(tr, t, {"en": "If we filter after the search"})
            self.play(FadeIn(after), run_time=0.4)
            self.cue(tr, t, {"en": "half a result survives"})
            self.play(FadeIn(survivor), FadeIn(eq), run_time=0.6)

        # filtering first: exact over the kept share — small on our documents, huge on a billion vectors
        first = txt(label("ac_filter_first"), size=28, color=GOOD).move_to(DOWN * 1.3)
        cols = VGroup(
            VGroup(MathTex(tex_int(D["filter"]["pre_banking"]), font_size=56, color=GOOD),
                   txt(label("ac_our_documents"), size=24, color=GREY_B)).arrange(DOWN, buff=0.2),
            VGroup(MathTex(tex_int(D["filter"]["pre_large"]), font_size=56, color=BAD),
                   txt(label("ac_billion_vectors"), size=24, color=GREY_B)).arrange(DOWN, buff=0.2))
        cols.arrange(RIGHT, buff=2.0).next_to(first, DOWN, buff=0.4)
        unit = txt(label("ac_vectors_to_scan"), size=22, color=GREY_B).next_to(first, RIGHT, buff=0.5)
        with self.say("7.9") as (tr, t):
            self.play(FadeIn(first), FadeIn(unit), run_time=0.4)
            self.cue(tr, t, {"en": "on our documents that is about thirty-five"})
            self.play(FadeIn(cols[0]), run_time=0.5)
            self.cue(tr, t, {"en": "On a billion vectors"})
            self.play(FadeIn(cols[1]), run_time=0.5)
        self.clear_all()


class S07Code(LectureScene):
    def construct(self):
        panel = code_panel(INDEX_FILE, "def build", "return list(zip", size=22, tag="shown").move_to(UP * 0.3)  # clear of the brand mark
        make = highlight(panel, code_lines(INDEX_FILE, "IndexHNSWFlat")[0],
                         last=code_lines(INDEX_FILE, "METRIC_INNER_PRODUCT")[0])
        knob = highlight(panel, code_lines(INDEX_FILE, "index.hnsw.efSearch")[0], color=GOOD)
        with self.say("7.10") as (tr, t):
            self.play(FadeIn(panel), run_time=0.7)
            self.cue(tr, t, {"en": "builds an HNSW index with FAISS"})
            self.play(Create(make), run_time=0.5)
            self.cue(tr, t, {"en": "one knob, ef search"})
            self.play(Create(knob), run_time=0.5)
        self.clear_all()

        # measure the index against exact search, computed once
        def row(name, color):
            boxes = VGroup(*[Square(0.62, stroke_color=color, stroke_width=2.5) for _ in range(10)]).arrange(RIGHT, buff=0.12)
            return VGroup(txt(name, size=24, color=color), boxes).arrange(RIGHT, buff=0.4)
        exact = row(label("ac_exact_top10"), GOOD)
        approx = row(label("ac_index_top10"), LBLUE)
        rows = VGroup(exact, approx).arrange(DOWN, buff=0.5, aligned_edge=RIGHT).move_to(UP * 0.8)
        f = MathTex(r"\mathrm{recall@}10 = \frac{|\,\mathrm{exact} \cap \mathrm{index}\,|}{10}", font_size=48).next_to(rows, DOWN, buff=0.6)
        gt = txt(label("ac_ground_truth_first"), size=32, weight=BOLD, color=HILITE).next_to(f, DOWN, buff=0.5)
        with self.say("7.11") as (tr, t):
            self.cue(tr, t, {"en": "no index tells you what it missed"})
            self.play(FadeIn(approx), run_time=0.5)
            self.cue(tr, t, {"en": "compute the exact top ten"})
            self.play(FadeIn(exact), run_time=0.5)
            self.cue(tr, t, {"en": "measure every index setting against it"})
            self.play(Write(f), FadeIn(gt), run_time=0.8)
        self.clear_all()

        # recap: choose by what runs out first
        head = self.heading(label("ac_recap"), color=HILITE)
        table = VGroup(
            VGroup(MathTex(rf"< {pow10(DECK_IN.EXACT_SCAN_LIMIT)}", font_size=40), txt(label("ac_scan_exactly"), size=30, color=GOOD)),
            VGroup(txt(label("ac_memory_to_spare"), size=28, color=GREY_B), txt(label("ac_hnsw"), size=30, color=RLGREEN)),
            VGroup(txt(label("ac_memory_runs_out"), size=28, color=GREY_B),
                   VGroup(txt(label("ac_ivf"), size=30, color=LBLUE), MathTex("+", font_size=36),
                          txt(label("ac_pq"), size=30, color=HILITE)).arrange(RIGHT, buff=0.2)))
        x1 = max(r[0].width for r in table) + 0.8
        table.arrange(DOWN, buff=0.45)
        for r in table:
            r[0].align_to(ORIGIN, LEFT)
            r[1].align_to(RIGHT * x1, LEFT)
        table.move_to(UP * 0.4)
        measure = bullets([label("ac_measure_recall")], size=30).next_to(table, DOWN, buff=0.7)
        with self.say("7.12") as (tr, t):
            self.play(FadeIn(head), run_time=0.4)
            self.cue(tr, t, {"en": "scan small corpora exactly"})
            self.play(FadeIn(table[0]), run_time=0.4)
            self.cue(tr, t, {"en": "choose IVF, PQ or HNSW"})
            self.play(FadeIn(table[1]), FadeIn(table[2]), run_time=0.6)
            self.cue(tr, t, {"en": "measure recall"})
            self.play(FadeIn(measure, shift=RIGHT * 0.2), run_time=0.45)
        self.clear_all()


SCENES = ["S07Scan", "S07IVF", "S07PQ", "S07HNSW", "S07Database", "S07Code"]
