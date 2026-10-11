"""Lecture 2, section 4 — contingency tables: joint, marginal and conditional by choosing a denominator."""
from lecture02_kit import *

C = N["cells"]


def frac(a, b, size=44, color=WHITE):
    """A display fraction: the kit's \\tfrac is too small to read at video scale."""
    return MathTex(rf"\frac{{{a}}}{{{b}}}", font_size=size, color=color)


def placed(T, v):
    """Move a kit table; its highlight rectangles are built in the table's own coordinates,
    so remember the shift and apply it to every highlight."""
    T["grid"].shift(v)
    T["off"] = T.get("off", ORIGIN) + np.array(v, dtype=float)
    return T


def hl(T, kind, *a, color=HILITE):
    return T[kind](*a, color=color).shift(T.get("off", ORIGIN))


def ring(m, color=HILITE):
    return SurroundingRectangle(m, buff=0.12, color=color, stroke_width=4, corner_radius=0.08)


def small_table():
    return bike_bus_table(size=26, cw=2.1, head_w=2.4)


def prob_row(name, color, a, b, val=None):
    """A named probability: 'joint   15/100 = 0.15'."""
    parts = [txt(name, size=28, weight=BOLD, color=color), frac(a, b, size=40)]
    if val is not None:
        parts += [MathTex("=", font_size=44), MathTex(val, font_size=44)]
    return VGroup(*parts).arrange(RIGHT, buff=0.3)


class S04Table(LectureScene):
    def construct(self):
        self.section_card(4)
        grid, who = student_grid(side=0.22, gap=0.045)
        grid.move_to([-4.7, 0.1, 0])
        n_bike = N["bike"]
        top, bot = VGroup(*grid[:n_bike]), VGroup(*grid[n_bike:])
        b_box = SurroundingRectangle(top, buff=0.06, color=LBLUE, stroke_width=3)
        n_box = SurroundingRectangle(bot, buff=0.06, color=GREY_B, stroke_width=3)
        b_lab = txt(f"{BIKE} · {N['bike']}", size=22, color=LBLUE).next_to(b_box, UP, buff=0.12)
        n_lab = txt(f"{NOBIKE} · {N['nobike']}", size=22, color=GREY_B).next_to(n_box, DOWN, buff=0.12)
        leg = legend([(BUS_C, BUS), (NOBUS_C, NOBUS)], size=20).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        leg.next_to(n_lab, DOWN, buff=0.25)
        b_br, n_br = b_box, n_box

        with self.say("4.1") as (tr, t):
            self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in grid], lag_ratio=0.01), run_time=1.4)
            self.cue(tr, t, {"en": "We know two things", "uz": "Har bir talaba haqida"})
            self.play(Create(b_box), FadeIn(b_lab), Create(n_box), FadeIn(n_lab), run_time=0.8)
            self.play(FadeIn(leg), run_time=0.6)

        T = placed(small_table(), [1.8, -0.1, 0])
        body = [[T["cell"][r][c] for c in range(2)] for r in range(2)]
        lines = [m for m in T["grid"] if isinstance(m, Line)]
        labels = T["collab"] + T["rowlab"] + T["tothead"] + T["totlab"]
        margins = VGroup(*T["rowtot"], *T["coltot"], T["grand"])
        title = self.heading(w("Contingency table", "Kontingentlik jadvali"), color=LBLUE)

        with self.say("4.2") as (tr, t):
            self.play(*[Create(l) for l in lines], FadeIn(VGroup(*labels)), run_time=0.8)
            for k, (b, u) in enumerate(ORDER):
                r, c = (0 if b == "bike" else 1), (0 if u == "bus" else 1)
                pick = VGroup(*[s.copy() for s, x in zip(grid, who) if x == (b, u)])
                self.play(ReplacementTransform(pick, body[r][c]), run_time=0.6)
            self.cue(tr, t, {"en": "with the row", "uz": "Qator va ustun"})
            self.play(FadeIn(margins, shift=LEFT * 0.2), run_time=0.8)
            self.cue(tr, t, {"en": "This is called", "uz": "Bu kontingentlik"})
            self.play(FadeIn(title), run_time=0.6)

        # the three probabilities, each with its denominator lit
        v = [-T["grid"].get_center()[0], 1.15 - T["grid"].get_center()[1], 0]
        self.play(FadeOut(VGroup(grid, b_br, n_br, b_lab, n_lab, leg)), T["grid"].animate.shift(v), run_time=0.7)
        T["off"] = T["off"] + np.array(v)

        rows = VGroup(
            prob_row(w("joint", "birgalikdagi"), HILITE, C["bike_bus"], N["n"], dec(N["joint_bike_bus"])),
            prob_row(w("marginal", "marginal"), LBLUE, N["bus"], N["n"], dec(N["p_bus"])),
            prob_row(w("conditional", "shartli"), RLGREEN, C["bike_bus"], N["bike"], dec(N["p_bus_given_bike"])),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        rows.move_to([0, 1.15 - 1.44 - 0.3 - rows.height / 2, 0])

        with self.say("4.3") as (tr, t):
            self.cue(tr, t, {"en": "The first is joint", "uz": "Birinchisi"})
            num = ring(T["cell"][0][0])
            den = VGroup(hl(T, "body_rect", color=GREY_B), ring(T["grand"], color=LBLUE))
            self.play(Create(num), Create(den), run_time=0.8)
            self.cue(tr, t, {"en": "Bike and bus", "uz": "Velosiped va avtobus"})
            self.play(FadeIn(rows[0], shift=UP * 0.2), run_time=0.7)

        with self.say("4.4") as (tr, t):
            num2 = ring(T["coltot"][0])
            self.play(Transform(num, num2), Transform(den, VGroup(ring(T["grand"], color=LBLUE))), run_time=0.8)
            self.cue(tr, t, {"en": "Bus:", "uz": "Avtobus:"})
            self.play(FadeIn(rows[1], shift=UP * 0.2), run_time=0.7)

        with self.say("4.5") as (tr, t):
            self.play(Transform(num, ring(T["cell"][0][0])),
                      Transform(den, VGroup(hl(T, "row_rect", 0, color=RLGREEN), ring(T["rowtot"][0], color=LBLUE))),
                      run_time=0.8)
            self.cue(tr, t, {"en": "Bus among", "uz": "Velosipedi borlar"})
            self.play(FadeIn(rows[2], shift=UP * 0.2), run_time=0.7)

        # conditioning is choosing a denominator: whole table, then one row
        with self.say("4.6") as (tr, t):
            self.play(FadeOut(num), FadeOut(rows), FadeOut(den), run_time=0.5)
            box = hl(T, "body_rect", color=HILITE)
            self.cue(tr, t, {"en": "the whole table", "uz": "butun jadval"})
            self.play(Create(box), run_time=0.8)
            self.cue(tr, t, {"en": "one row or column", "uz": "bitta qator"})
            self.play(Transform(box, hl(T, "row_rect", 0, color=HILITE)), run_time=0.7)
            self.play(Transform(box, hl(T, "col_rect", 0, color=HILITE)), run_time=0.7)
        self.clear_all()


class S04Confusion(LectureScene):
    """AI: a confusion matrix is the same kind of table (illustrative, no counts)."""

    def construct(self):
        head = self.heading(w("Confusion matrix", "Xatolar matritsasi"), color=LBLUE)
        cw, ch = 2.7, 1.2
        cols = [w("model: spam", "model: spam"), w("model: not spam", "model: spam emas")]
        rows = [w("true: spam", "haqiqiy: spam"), w("true: not spam", "haqiqiy: spam emas")]
        x0, y0 = -0.3, -0.2
        cells = VGroup()
        for r in range(2):
            for c in range(2):
                ok = r == c
                sq = Rectangle(width=cw, height=ch, stroke_color=GREY_B, stroke_width=2,
                               fill_color=RLGREEN if ok else RLRED, fill_opacity=0.25)
                sq.move_to([x0 + (c - 0.5) * cw, y0 - (r - 0.5) * ch, 0])
                mark = txt("✓" if ok else "✗", size=44, weight=BOLD, color=RLGREEN if ok else RLRED).move_to(sq)
                cells.add(VGroup(sq, mark))
        clabs = VGroup(*[txt(s, size=24, color=GREY_B).next_to(cells[c], UP, buff=0.2) for c, s in enumerate(cols)])
        rlabs = VGroup(*[txt(s, size=24, color=GREY_B).next_to(cells[2 * r], LEFT, buff=0.25) for r, s in enumerate(rows)])
        row_hl = SurroundingRectangle(VGroup(cells[0], cells[1]), buff=0.05, color=HILITE, stroke_width=5)
        cond = MathTex(r"P(\text{model: spam} \mid \text{spam})", font_size=40, color=HILITE)
        cond.next_to(VGroup(cells), DOWN, buff=0.5)
        VGroup(cells, clabs, rlabs, row_hl, cond).move_to(DOWN * 0.3)

        with self.say("4.7") as (tr, t):
            self.play(FadeIn(head), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in cells], lag_ratio=0.15),
                      FadeIn(clabs), FadeIn(rlabs), run_time=1.2)
            self.cue(tr, t, {"en": "Most of the scores", "uz": "Modelni baholaydigan"})
            self.play(Create(row_hl), run_time=0.6)
            self.play(Write(cond), run_time=0.8)
        self.clear_all()


class S04HandsOn(LectureScene):
    def construct(self):
        T = placed(small_table(), [0, -1.3, 0])
        pc = pause_card([w("A student takes the bus.", "Talaba avtobusda qatnaydi."),
                         w("What is the probability they own a bike?", "Velosipedi boʻlish ehtimoli qancha?")])
        pc.scale(0.85).to_edge(UP, buff=SAFE + 0.2)
        with self.say("4.8") as (tr, t):
            self.play(FadeIn(T["grid"]), run_time=0.6)
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(pc, shift=DOWN * 0.2), run_time=0.6)
        self.hands_on()

        a, b = N["p_bike_given_bus"]
        with self.say("4.9") as (tr, t):
            self.play(FadeOut(pc), run_time=0.4)
            col = hl(T, "col_rect", 0, color=HILITE)
            self.play(Create(col), Indicate(T["coltot"][0], color=LBLUE), run_time=0.8)
            self.cue(tr, t, {"en": "Fifteen of them", "uz": "Ulardan oʻn beshtasining"})
            self.play(Create(ring(T["cell"][0][0])), run_time=0.5)
            ans = VGroup(frac(C["bike_bus"], N["bus"], size=56), MathTex("=", font_size=50),
                         frac(a, b, size=56, color=HILITE)).arrange(RIGHT, buff=0.3).move_to([0, 2.0, 0])
            self.play(Write(ans), run_time=0.9)

        # knowing about the bike changed the answer about the bus
        with self.say("4.10") as (tr, t):
            self.clear_all()
            bus, bike = w("bus", "avtobus"), w("bike", "velosiped")
            p1 = VGroup(ptex(rf"P(\text{{{bus}}})", size=44), MathTex("=", font_size=44),
                        MathTex(dec(N["p_bus"]), font_size=44)).arrange(RIGHT, buff=0.25)
            p2 = VGroup(ptex(rf"P(\text{{{bus}}} \mid \text{{{bike}}})", size=44), MathTex("=", font_size=44),
                        MathTex(dec(N["p_bus_given_bike"]), font_size=44)).arrange(RIGHT, buff=0.25)
            neq = MathTex(r"\neq", font_size=60, color=RLRED)
            g = VGroup(p1, neq, p2).arrange(RIGHT, buff=0.5).move_to(UP * 0.4)
            if g.width > 12:
                g.scale_to_fit_width(12)
            self.play(FadeIn(p1), run_time=0.6)
            self.play(FadeIn(neq), FadeIn(p2), run_time=0.7)
            self.cue(tr, t, {"en": "Is that always so", "uz": "Bu har doim"})
            q = txt("?", size=96, weight=BOLD, color=HILITE).next_to(g, DOWN, buff=0.5)
            self.play(FadeIn(q, scale=1.3), run_time=0.6)
        self.clear_all()


SCENES = ["S04Table", "S04Confusion", "S04HandsOn"]
