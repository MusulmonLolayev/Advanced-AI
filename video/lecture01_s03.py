"""Lecture 1, section 3 — the histogram.

Every dot and bar is one of the 600 real salaries (statistics/raw/v01_salaries.txt);
the range, class width and class counts come from capture_l01.py (l01_numbers.json),
which asserts them against the figure script's own printout. The three "feature"
histograms are the course's other real data: machine B's bottle fills and branch C's
waiting times (l01_arrays.json).
"""
from lecture01_kit import *

EDGES, COUNTS = L["hist_edges"], L["hist_counts"]
assert COUNTS == [156, 311, 89, 32, 7, 3, 2] and EDGES[0] == 20_000 and EDGES[-1] == 160_000
assert len(np.unique(SAL)) == len(SAL) == 600
assert (round(L["sal_max"]), round(L["sal_min"]), round(L["sal_range"])) == (151_117, 27_092, 124_026)
assert round(L["hist_width_raw"]) == 17_718 and L["hist_k"] == 7
assert L["above_80k"] == sum(COUNTS[3:]) == 44

# ─── one salary axis for the whole section ────────────────────────────────
S0, S1, X0, X1, AY = 20_000, 160_000, -5.6, 5.6, -2.3
CW = (X1 - X0) / L["hist_k"]                     # one class, in screen units
PER_ROW, DS, DR = 12, 0.12, 0.042                 # dot stacks: 12 dots a row
ROWH = DS / PER_ROW                                # screen height of one person, as a bar


def sx(s):
    return X0 + (X1 - X0) * (s - S0) / (S1 - S0)


def salary_axis(labels=True):
    axis = Line([X0, AY, 0], [X1, AY, 0], stroke_width=2, color=GREY_B)
    g = VGroup(axis)
    if labels:
        for v in EDGES:
            tk = Line(UP * 0.08, DOWN * 0.08, stroke_width=2, color=GREY_B).move_to([sx(v), AY, 0])
            g.add(tk, txt(f"${v // 1000}k", size=20, color=GREY_B).next_to(tk, DOWN, buff=0.15))
    return g


def class_of(s):
    return int((s - S0) // 20_000)


def stack_positions():
    pos, filled = [], [0] * len(COUNTS)
    for s in SAL:
        c = class_of(s)
        k = filled[c]
        filled[c] += 1
        x = X0 + (c + 0.5) * CW + (k % PER_ROW - (PER_ROW - 1) / 2) * DS
        pos.append([x, AY + 0.08 + (k // PER_ROW) * DS, 0])
    assert filled == COUNTS
    return pos


def hist_bars(gap=0.0, color=RLBLUE):
    return VGroup(*[Rectangle(width=CW - gap, height=n * ROWH, stroke_color=BLACK, stroke_width=1.5,
                              fill_color=color, fill_opacity=1).move_to([X0 + (c + 0.5) * CW, AY + n * ROWH / 2, 0])
                    for c, n in enumerate(COUNTS)])


def k_bars(k, top=3.0, color=RLBLUE):
    """The 600 salaries in k equal classes over the section's axis; the tallest bar is `top` high."""
    counts, _ = np.histogram(SAL, bins=k, range=(S0, S1))
    w = (X1 - X0) / k
    return VGroup(*[Rectangle(width=w, height=max(n * top / counts.max(), 1e-3), stroke_color=BLACK,
                              stroke_width=1 if k > 20 else 1.5, fill_color=color, fill_opacity=1)
                    .move_to([X0 + (c + 0.5) * w, AY + n * top / counts.max() / 2, 0]) for c, n in enumerate(counts)])


def step_head(step, words):
    return txt(f"{step}: {words}", size=34, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.3)


def mini_hist(values, lo, hi, bins, title, width=3.6, height=2.0, flag_above=None):
    counts, edges = np.histogram(values, bins=bins, range=(lo, hi))
    bw = width / bins
    k = height / counts.max()
    base = Line(LEFT * width / 2, RIGHT * width / 2, color=GREY_B, stroke_width=2)
    bars = VGroup(*[Rectangle(width=bw, height=max(n * k, 1e-3), stroke_color=BLACK, stroke_width=1,
                              fill_color=RLBLUE, fill_opacity=1).move_to([-width / 2 + (i + 0.5) * bw, n * k / 2, 0])
                    for i, n in enumerate(counts)])
    lab = txt(title, size=24, color=GREY_A).next_to(base, DOWN, buff=0.25)
    g = VGroup(bars, base, lab)
    flags = VGroup()
    if flag_above is not None:
        for v in values:
            if v > flag_above:
                flags.add(Dot([-width / 2 + width * (v - lo) / (hi - lo), 0.12, 0], radius=0.06, color=RLRED))
    return g, flags


class S03Classes(LectureScene):
    def construct(self):
        self.section_card(3)
        rng = np.random.default_rng(3)
        shown = SAL[rng.permutation(len(SAL))]
        col = VGroup(*[txt(money(v), size=26) for v in shown[:48]]).arrange(DOWN, aligned_edge=RIGHT, buff=0.14)
        col.move_to([0, 0, 0], aligned_edge=UP).shift(UP * 3.4)
        axis = salary_axis()
        jit = rng.uniform(-0.12, 0.12, len(SAL))
        strip = [[sx(s), AY + 0.35 + j, 0] for s, j in zip(SAL, jit)]
        order = np.argsort(np.argsort(shown))          # where each shown value sits in sorted SAL
        dots = VGroup(*[Dot(p, radius=0.03, color=RLBLUE, fill_opacity=0.9) for p in strip])

        def fade_edges(m):
            # the list fades out before it reaches the frame edge
            for c in m:
                c.set_opacity(float(np.clip((2.9 - abs(c.get_y())) / 0.5, 0, 1)))
        fade_edges(col)
        with self.say("3.1") as (tr, t):
            self.play(FadeIn(col, lag_ratio=0.02), run_time=0.8)
            fade_edges(col)
            speed = (col.height - 6.2) / 2.4
            col.add_updater(lambda m, dt: fade_edges(m.shift(UP * speed * dt)))
            self.wait(2.4)
            self.cue(tr, t, 1)
            col.clear_updaters()
            visible = [i for i, c in enumerate(col) if abs(c.get_y()) < 2.9]
            self.play(FadeIn(axis),
                      *[ReplacementTransform(col[i], dots[order[i]]) for i in visible],
                      *[FadeOut(col[i]) for i in range(len(col)) if i not in visible], run_time=1.4)
            rest = [d for j, d in enumerate(dots) if j not in {order[i] for i in visible}]
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in rest], lag_ratio=0.002), run_time=1.4)

        hairs = VGroup(*[Line([sx(s), AY, 0], [sx(s), AY + 1.2, 0], stroke_width=1.2, color=RLBLUE) for s in SAL])
        once = txt(label("each_value_once"), size=30, color=HILITE).move_to([0, 0.6, 0])
        one = txt("1", size=26, color=GREY_B).move_to([X0 - 0.35, AY + 1.2, 0])
        with self.say("3.2") as (tr, t):
            self.play(ReplacementTransform(dots, hairs), run_time=1.6)
            self.cue(tr, t, 1)
            self.play(FadeIn(once, shift=UP * 0.2), FadeIn(one), run_time=0.8)

        lo, hi = hairs[0], hairs[-1]
        head = step_head(label("step_1"), label("the_range"))
        lab_lo = txt(money(L["sal_min"]), size=24, color=HILITE).next_to(lo, UP, buff=0.15)
        lab_hi = txt(money(L["sal_max"]), size=24, color=HILITE).next_to(hi, UP, buff=0.15)
        br = BraceBetweenPoints([sx(L["sal_min"]), AY + 1.95, 0], [sx(L["sal_max"]), AY + 1.95, 0], UP, color=GREY_B)
        rng_lab = txt(money(L["sal_range"]), size=36, weight=BOLD).next_to(br, UP, buff=0.15)
        with self.say("3.3") as (tr, t):
            self.play(FadeOut(once), FadeOut(one), run_time=0.5)
            self.cue(tr, t, 1)
            self.play(FadeIn(head), run_time=0.6)
            self.cue(tr, t, 2)
            self.play(lo.animate.set_stroke(HILITE, width=5), hi.animate.set_stroke(HILITE, width=5),
                      FadeIn(lab_lo), FadeIn(lab_hi), run_time=0.9)
            self.cue(tr, t, 3)
            self.play(GrowFromCenter(br), FadeIn(rng_lab, shift=UP * 0.2), run_time=1.0)

        head2 = step_head(label("step_2"), label("number_of_classes"))
        k_lab = MathTex("k", "=", str(L["hist_k"]), font_size=72).move_to([0, 1.7, 0])
        k_lab[0].set_color(HILITE)
        with self.say("3.4") as (tr, t):
            self.play(FadeOut(head), FadeIn(head2), FadeOut(br), FadeOut(rng_lab), FadeOut(lab_lo), FadeOut(lab_hi),
                      run_time=0.8)
            self.cue(tr, t, 2)
            self.play(FadeIn(k_lab, scale=1.2), run_time=0.8)

        head3 = step_head(label("step_3"), label("class_width"))
        div = MathTex(f"{L['sal_range']:,.0f}".replace(",", "{,}"), r"\div", str(L["hist_k"]), "=",
                      f"{L['hist_width_raw']:,.0f}".replace(",", "{,}"), r"\;\to\;", "20{,}000", font_size=54)
        div.move_to([0, 1.7, 0])
        div[6].set_color(HILITE)
        edges = VGroup(*[DashedLine([sx(v), AY + 2.6, 0], [sx(v), AY, 0], color=HILITE, stroke_width=2.5)
                         for v in EDGES])
        with self.say("3.5") as (tr, t):
            self.play(FadeOut(head2), FadeIn(head3), FadeOut(k_lab), run_time=0.7)
            self.cue(tr, t, {"en": 2, "uz": 1})
            self.play(FadeIn(div[:5]), run_time=1.0)
            self.cue(tr, t, {"en": 3, "uz": 2})
            self.play(FadeIn(div[5:], shift=LEFT * 0.2), run_time=0.7)
            self.play(LaggedStart(*[Create(e) for e in edges], lag_ratio=0.12), run_time=1.4)

        # how many classes: too few hides the shape, too many shreds it
        few, many, ok = k_bars(2), k_bars(60), k_bars(L["hist_k"])
        verdict = [(2, label("too_few"), RLRED), (60, label("too_many"), RLRED), (L["hist_k"], label("good"), GOOD)]
        tags = [VGroup(tagged(k, label("classes_count"), size=32), txt(v, size=32, weight=BOLD, color=c))
                .arrange(RIGHT, buff=0.4).move_to([0, 1.55, 0]) for k, v, c in verdict]
        head_k = self.heading(label("number_of_classes"))
        with self.say("3.5a") as (tr, t):
            self.play(FadeOut(head3), FadeOut(div), hairs.animate.set_stroke(opacity=0),
                      edges.animate.set_opacity(0), FadeIn(head_k), run_time=0.7)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in few], lag_ratio=0.2), FadeIn(tags[0]), run_time=1.0)
            self.cue(tr, t, 2)
            self.play(ReplacementTransform(few, many), ReplacementTransform(tags[0], tags[1]), run_time=1.4)
            self.cue(tr, t, 3)
            self.play(ReplacementTransform(many, ok), ReplacementTransform(tags[1], tags[2]), run_time=1.4)
        self.play(FadeOut(ok), FadeOut(tags[2]), FadeOut(head_k), hairs.animate.set_stroke(opacity=1),
                  edges.animate.set_opacity(1), FadeIn(head3), run_time=0.6)

        head4 = step_head(label("step_4"), label("count_each_class"))
        stacks = VGroup(*[Dot(p, radius=DR, color=RLBLUE, fill_opacity=1) for p in stack_positions()])
        nums = VGroup(*[Integer(0, font_size=34).move_to([X0 + (c + 0.5) * CW, AY + 0.08 + ((n - 1) // PER_ROW + 1) * DS + 0.3, 0])
                        for c, n in enumerate(COUNTS)])
        with self.say("3.6"):
            self.play(FadeOut(head3), FadeIn(head4), edges.animate.set_opacity(0.35), run_time=0.7)
            self.play(FadeIn(nums), run_time=0.3)
            self.play(ReplacementTransform(hairs, stacks),
                      *[ChangeDecimalToValue(nm, n) for nm, n in zip(nums, COUNTS)], run_time=2.6)
        self.wait(0.3)

        hl = SurroundingRectangle(VGroup(*[d for d, s in zip(stacks, SAL) if class_of(s) == 1]), buff=0.12,
                                  color=HILITE, stroke_width=4)
        half = tagged(f"{COUNTS[1]}/{sum(COUNTS)}:", label("more_than_half"), size=28, color=HILITE)
        half.next_to(hl, RIGHT, buff=0.3).shift(UP * 0.6)
        tail = Arrow([sx(85_000), AY + 1.25, 0], [sx(158_000), AY + 0.9, 0], buff=0, color=RLRED, stroke_width=5)
        tail_lab = txt(label("thin_tail"), size=26, color=RLRED).next_to(tail, UP, buff=0.15).shift(RIGHT * 1.2)
        with self.say("3.7") as (tr, t):
            self.play(Create(hl), nums[1].animate.set_color(HILITE), run_time=0.8)
            self.play(FadeIn(half), run_time=0.6)
            self.cue(tr, t, {"en": 2, "uz": 1})
            self.play(GrowArrow(tail), FadeIn(tail_lab), run_time=1.0)

        bars = hist_bars()
        gapped = hist_bars(gap=0.35)
        head5 = step_head(label("step_5"), label("draw_touching_bars"))
        gaps = VGroup(*[Rectangle(width=0.35, height=2.4, stroke_width=0, fill_color=RLRED, fill_opacity=0.5)
                        .move_to([X0 + c * CW, AY + 1.2, 0]) for c in range(1, len(COUNTS))])
        with self.say("3.8") as (tr, t):
            self.play(FadeOut(head4), FadeIn(head5), FadeOut(hl), FadeOut(half), FadeOut(tail), FadeOut(tail_lab),
                      FadeOut(edges), nums[1].animate.set_color(WHITE), run_time=0.7)
            self.remove(stacks)
            self.play(ReplacementTransform(stacks.copy(), bars), run_time=1.4)
            for nm, b in zip(nums, bars):
                nm.generate_target().next_to(b, UP, buff=0.12)
            self.play(*[MoveToTarget(nm) for nm in nums], run_time=0.5)
            self.cue(tr, t, 2)
            self.play(Transform(bars, gapped), FadeIn(gaps), run_time=0.8)
            self.play(Indicate(gaps, color=RLRED, scale_factor=1.05), run_time=0.8)
            self.play(Transform(bars, hist_bars()), FadeOut(gaps), run_time=0.8)

        name = txt(label("histogram"), size=44, weight=BOLD, color=RLBLUE).to_edge(UP, buff=SAFE + 0.3)
        skew = Arrow([sx(70_000), 0.4, 0], [sx(150_000), 0.4, 0], buff=0, color=HILITE, stroke_width=6)
        skew_lab = txt(label("skewed_right"), size=32, color=HILITE).next_to(skew, UP, buff=0.15)
        with self.say("3.9") as (tr, t):
            self.play(FadeOut(head5), FadeIn(name, shift=DOWN * 0.2), run_time=0.8)
            self.cue(tr, t, 2)
            self.play(GrowArrow(skew), FadeIn(skew_lab), run_time=1.0)
        self.clear_all()

        # three shapes to read: symmetric (a sketch), right-skewed (our salaries), two peaks (a sketch)
        def sketch(f, bins=14, width=3.6, height=2.0):
            xs = (np.arange(bins) + 0.5) / bins
            ys = np.array([f(x) for x in xs]); ys = ys * height / ys.max()
            bw = width / bins
            bars = VGroup(*[Rectangle(width=bw, height=max(y, 1e-3), stroke_color=BLACK, stroke_width=1,
                                      fill_color=RLBLUE, fill_opacity=1).move_to([-width / 2 + (i + 0.5) * bw, y / 2, 0])
                            for i, y in enumerate(ys)])
            return VGroup(bars, Line(LEFT * width / 2, RIGHT * width / 2, color=GREY_B, stroke_width=2))

        bell = lambda x: np.exp(-((x - 0.5) / 0.16) ** 2 / 2)
        twin = lambda x: np.exp(-((x - 0.27) / 0.09) ** 2 / 2) + 0.85 * np.exp(-((x - 0.72) / 0.1) ** 2 / 2)
        sal_g, _ = mini_hist(SAL, S0, S1, 14, label("salary"))
        panels = [sketch(bell), VGroup(sal_g[0], sal_g[1]), sketch(twin)]
        names = [label("symmetric"), label("skewed_right"), label("two_peaks")]
        cols = (RLGREEN, HILITE, BLUE_B)
        shapes = VGroup()
        for g, nm, c, x in zip(panels, names, cols, (-4.5, 0, 4.5)):
            title = txt(nm, size=30, weight=BOLD, color=c).next_to(g, DOWN, buff=0.3)
            shapes.add(VGroup(g, title).scale(1.1).move_to([x, 0.1, 0]))
        head_s = self.heading(label("histogram"))
        sal_tag = txt(label("salary"), size=22, color=GREY_B).next_to(shapes[1][1], DOWN, buff=0.15)
        ill = VGroup(*[txt(label("illustration", 1), size=20, color=GREY_B).next_to(shapes[i][1], DOWN, buff=0.15)
                       for i in (0, 2)])
        with self.say("3.9a") as (tr, t):
            self.play(FadeIn(head_s), run_time=0.5)
            self.cue(tr, t, 1)
            self.play(FadeIn(shapes[0], shift=UP * 0.3), FadeIn(ill[0]), run_time=0.9)
            self.cue(tr, t, {"uz": 2, "en": 3})
            self.play(FadeIn(shapes[1], shift=UP * 0.3), FadeIn(sal_tag), run_time=0.9)
            self.cue(tr, t, {"uz": 3, "en": 5})
            self.play(FadeIn(shapes[2], shift=UP * 0.3), FadeIn(ill[1]), run_time=0.9)
        self.clear_all()


class S03Features(LectureScene):
    def construct(self):
        wC = ARR["waits_C"]
        whiC = next(b for b in L["branches"] if b["name"] == "C")["whi"]
        panels = [mini_hist(SAL, 20_000, 160_000, 14, label("salary")),
                  mini_hist(ARR["fills_B"], 486, 514, 28, label("bottle_fill_ml")),
                  mini_hist(wC, 0, 80, 16, label("waiting_time_min"), flag_above=whiC)]
        for (g, fl), x in zip(panels, (-4.6, 0, 4.6)):
            VGroup(g, fl).shift([x, -0.6, 0])
        head = self.heading(label("every_feature_one_histogram"))
        strange = txt(label("strange_values"), size=26, color=RLRED)
        strange.move_to([4.6, 1.75, 0])
        pointer = Arrow(strange.get_bottom(), panels[2][1].get_center() + UP * 0.1, buff=0.1, color=RLRED,
                        stroke_width=4, tip_length=0.2)
        with self.say("3.10") as (tr, t):
            self.cue(tr, t, 1)
            self.play(FadeIn(head), LaggedStart(*[FadeIn(g, shift=UP * 0.3) for g, _ in panels], lag_ratio=0.4),
                      run_time=2.0)
            self.cue(tr, t, {"en": "where the strange", "uz": 2})
            self.play(FadeIn(panels[2][1], scale=1.5), FadeIn(strange), GrowArrow(pointer), run_time=1.0)
        self.clear_all()


class S03HandsOn(LectureScene):
    def construct(self):
        rows = VGroup()
        for c, n in enumerate(COUNTS):
            a, b = EDGES[c] // 1000, EDGES[c + 1] // 1000
            r = VGroup(txt(f"${a}k – ${b}k", size=34), txt(str(n), size=34, weight=BOLD))
            r[1].move_to([1.9, 0, 0], aligned_edge=RIGHT)
            r[0].move_to([-2.0, 0, 0], aligned_edge=LEFT)
            rows.add(r)
        rows.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        hdr = VGroup(txt(label("class"), size=28, color=GREY_B), txt(label("people"), size=28, color=GREY_B))
        hdr[0].move_to([-2.0, 0, 0], aligned_edge=LEFT)
        hdr[1].move_to([1.9, 0, 0], aligned_edge=RIGHT)
        table = VGroup(hdr, rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        for r in rows:
            r[1].set_x(hdr[1].get_right()[0], RIGHT)
        table.move_to([-3.3, -0.4, 0])
        edge = L["above_80k_edge"]
        card_ = pause_card([f"{label('salary')} > ${edge / 1000:g}k:  {label('how_many_q')}"])
        card_.move_to([3.2, 1.2, 0])
        if card_.width > 6.4:
            card_.scale_to_fit_width(6.4)
        with self.say("3.11"):
            self.play(FadeIn(table), FadeIn(card_), run_time=1.0)
        self.hands_on()

        last = rows[3:]
        hl = SurroundingRectangle(last, buff=0.12, color=HILITE, stroke_width=4)
        eq = MathTex("+".join(map(str, COUNTS[3:])), "=", str(L["above_80k"]), font_size=60).move_to([3.2, -0.4, 0])
        eq[2].set_color(HILITE)
        with self.say("3.12") as (tr, t):
            self.play(FadeOut(card_), Create(hl), *[r[1].animate.set_color(HILITE) for r in last], run_time=0.9)
            self.cue(tr, t, 1)
            self.play(FadeIn(eq[0]), run_time=0.9)
            self.cue(tr, t, 2)
            self.play(FadeIn(eq[1:], scale=1.2), run_time=0.7)
        self.clear_all()

        bars = hist_bars()
        q = box(label("one_number_q"), color=HILITE, width=3.4, height=1.1, size=32).move_to([2.6, 1.3, 0])
        with self.say("3.13") as (tr, t):
            self.play(FadeIn(salary_axis()), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1),
                      run_time=1.2)
            self.cue(tr, t, 1)
            self.play(FadeIn(q, scale=0.8), run_time=0.8)
        self.clear_all()


SCENES = ["S03Classes", "S03Features", "S03HandsOn"]
