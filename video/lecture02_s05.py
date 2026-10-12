"""Lecture 2, section 5 — independence checked from a table: bike/bus vs glasses/bus."""
from lecture02_kit import *

C = N["cells"]


def frac(a, b, size=44, color=WHITE):
    """A display fraction: the kit's \\tfrac is too small to read at video scale."""
    return MathTex(rf"\frac{{{a}}}{{{b}}}", font_size=size, color=color)


def placed(T, v):
    """Move a kit table, remembering the shift for its highlight rectangles."""
    T["grid"].shift(v)
    T["off"] = T.get("off", ORIGIN) + np.array(v, dtype=float)
    return T


def hl(T, kind, *a, color=HILITE):
    return T[kind](*a, color=color).shift(T.get("off", ORIGIN))


def ring(m, color=HILITE):
    return SurroundingRectangle(m, buff=0.12, color=color, stroke_width=4, corner_radius=0.08)


BASE, H = -2.3, 4.0            # bar floor and the height of probability 1


def pbar(p, x, color, label, width=1.3):
    bar = Rectangle(width=width, height=max(p * H, 1e-3), stroke_width=0, fill_color=color, fill_opacity=1)
    bar.move_to([x, BASE + p * H / 2, 0])
    val = MathTex(dec(p), font_size=40).next_to(bar, UP, buff=0.12)
    lab = txt(label, size=24, color=GREY_B).next_to([x, BASE, 0], DOWN, buff=0.2)
    return VGroup(bar, val, lab)


def glasses_icon(color=WHITE):
    l = Circle(radius=0.28, color=color, stroke_width=4).shift(LEFT * 0.38)
    r = Circle(radius=0.28, color=color, stroke_width=4).shift(RIGHT * 0.38)
    bridge = ArcBetweenPoints(l.get_right(), r.get_left(), angle=-PI / 2, color=color, stroke_width=4)
    return VGroup(l, r, bridge)


class S05Bars(LectureScene):
    def construct(self):
        self.section_card(5)
        rule = VGroup(MathTex(r"P(B \mid A)", "=", "P(B)", font_size=64),
                      txt(label("independent"), size=34, weight=BOLD, color=RLGREEN)).arrange(DOWN, buff=0.4)
        with self.say("5.1") as (tr, t):
            self.play(Write(rule[0]), run_time=1.0)
            self.cue(tr, t, {"en": "In other words", "uz": "Yaʼni"})
            self.play(Indicate(rule[0], color=HILITE, scale_factor=1.1), FadeIn(rule[1]), run_time=0.9)

        floor = Line([-5.0, BASE, 0], [5.0, BASE, 0], color=GREY_B, stroke_width=2)
        mid = pbar(N["p_bus"], 0, BUS_C, label("all_students"))
        left = pbar(N["p_bus_given_bike"], -3.4, BUS_C, BIKE)
        right = pbar(N["p_bus_given_nobike"], 3.4, BUS_C, NOBIKE)
        level = DashedLine([-4.6, BASE + N["p_bus"] * H, 0], [4.6, BASE + N["p_bus"] * H, 0],
                           color=LBLUE, stroke_width=3)
        head = self.heading(label("takes_the_bus"), color=BUS_C)
        with self.say("5.2") as (tr, t):
            self.play(FadeOut(rule[1]), rule[0].animate.scale(0.6).to_corner(UR, buff=SAFE + 0.3), FadeIn(head),
                      Create(floor), run_time=0.7)
            self.cue(tr, t, {"en": "Overall", "uz": "Umuman"})
            self.play(GrowFromEdge(mid[0], DOWN), FadeIn(mid[1:]), run_time=0.8)
            self.play(Create(level), run_time=0.5)
            self.cue(tr, t, {"en": "Among bike owners", "uz": "Velosipedi borlarda"})
            self.play(GrowFromEdge(left[0], DOWN), FadeIn(left[1:]), run_time=0.7)
            self.cue(tr, t, {"en": "among the rest", "uz": "velosipedi yoʻqlarda"})
            self.play(GrowFromEdge(right[0], DOWN), FadeIn(right[1:]), run_time=0.7)

        lvl_y = BASE + N["p_bus"] * H
        down = Arrow([-4.35, lvl_y + 0.05, 0], [-4.35, BASE + N["p_bus_given_bike"] * H + 0.05, 0], buff=0,
                     color=RLRED, stroke_width=6, max_tip_length_to_length_ratio=0.35)
        up = Arrow([4.35, lvl_y - 0.05, 0], [4.35, BASE + N["p_bus_given_nobike"] * H - 0.05, 0], buff=0,
                   color=RLRED, stroke_width=6, max_tip_length_to_length_ratio=0.25)
        verdict = txt(label("not_independent"), size=34, weight=BOLD, color=RLRED)
        verdict.move_to([0, 2.15, 0])
        with self.say("5.3") as (tr, t):
            self.play(GrowArrow(down), GrowArrow(up), run_time=0.9)
            self.cue(tr, t, {"en": "So they are", "uz": "Demak"})
            self.play(FadeIn(verdict, scale=1.2), run_time=0.6)
        self.clear_all()


class S05Glasses(LectureScene):
    def construct(self):
        icon = glasses_icon().move_to([-4.3, 2.3, 0])
        side, gap = 0.36, 0.07
        sq = VGroup()
        for i in range(N["glasses"]):
            r, c = divmod(i, 10)
            sq.add(Square(side, stroke_width=0, fill_color=BUS_C if i < N["glasses_bus"] else NOBUS_C,
                          fill_opacity=1).move_to([c * (side + gap), -r * (side + gap), 0]))
        sq.move_to([-3.3, 0.4, 0])
        cap = txt(label("n_wear_glasses").format(n=N["glasses"]), size=26)
        cap.next_to(icon, RIGHT, buff=0.35)
        calc = VGroup(frac(N["glasses_bus"], N["glasses"], size=60), MathTex("=", font_size=54),
                      MathTex(dec(N["p_bus_given_glasses"]), font_size=54, color=BUS_C)).arrange(RIGHT, buff=0.3)
        calc.next_to(sq, DOWN, buff=0.6)
        leg = legend([(BUS_C, BUS), (NOBUS_C, NOBUS)], size=22).next_to(calc, DOWN, buff=0.4)

        with self.say("5.4") as (tr, t):
            self.play(Create(icon), FadeIn(cap), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in sq], lag_ratio=0.02), FadeIn(leg), run_time=1.2)
            self.cue(tr, t, {"en": "Eighteen out of forty", "uz": "Qirqdan oʻn sakkiz"})
            self.play(Write(calc), run_time=0.9)

        floor = Line([1.2, BASE, 0], [6.2, BASE, 0], color=GREY_B, stroke_width=2)
        all_b = pbar(N["p_bus"], 2.4, BUS_C, label("all"), width=1.1)
        gl_b = pbar(N["p_bus_given_glasses"], 4.9, BUS_C, label("glasses"), width=1.1)
        level = DashedLine([1.4, BASE + N["p_bus"] * H, 0], [6.0, BASE + N["p_bus"] * H, 0],
                           color=LBLUE, stroke_width=3)
        verdict = txt(label("independent"), size=34, weight=BOLD, color=RLGREEN).move_to([3.65, 2.4, 0])
        with self.say("5.5") as (tr, t):
            self.play(Create(floor), GrowFromEdge(all_b[0], DOWN), FadeIn(all_b[1:]), run_time=0.7)
            self.play(GrowFromEdge(gl_b[0], DOWN), FadeIn(gl_b[1:]), Create(level), run_time=0.7)
            self.cue(tr, t, {"en": "These two", "uz": "Bu ikkisi"})
            self.play(FadeIn(verdict, scale=1.2), run_time=0.6)
        self.clear_all()


class S05Expected(LectureScene):
    def construct(self):
        num = txt(label("row_total_column_total"), size=34)
        bar = Line(LEFT, RIGHT, color=WHITE, stroke_width=3).set_width(num.width + 0.3)
        den = txt(label("grand_total"), size=34)
        f = VGroup(num, bar, den).arrange(DOWN, buff=0.18)
        lhs = txt(label("expected_cell"), size=34, color=HILITE)
        formula = VGroup(lhs, f).arrange(RIGHT, buff=0.35)
        head = self.heading(label("if_independent"), color=RLGREEN)
        with self.say("5.6") as (tr, t):
            self.play(FadeIn(head), run_time=0.5)
            self.cue(tr, t, {"en": "Under independence", "uz": "Erkli boʻlsa"})
            self.play(FadeIn(formula, shift=UP * 0.2), run_time=1.0)

        T = placed(bike_bus_table(size=22, cw=1.5, head_w=2.0), [0, 0, 0])
        T = placed(T, [-T["grid"].get_center()[0], 1.0 - T["grid"].get_center()[1], 0])
        e1 = VGroup(MathTex(r"\frac{" + f"{N['bike']}" + r"\times" + f"{N['bus']}" + r"}{" + f"{N['n']}" + r"}",
                            font_size=46),
                    MathTex("=", font_size=44), MathTex(f"{N['expected_bike_bus']:g}", font_size=46, color=HILITE)
                    ).arrange(RIGHT, buff=0.25)
        o1 = VGroup(txt(label("table"), size=28, color=GREY_B),
                    MathTex(str(C["bike_bus"]), font_size=46, color=RLRED)).arrange(RIGHT, buff=0.2)
        r1 = VGroup(e1, o1).arrange(RIGHT, buff=0.6)
        gl = glasses_icon().scale(0.6)
        e2 = VGroup(MathTex(r"\frac{" + f"{N['glasses']}" + r"\times" + f"{N['bus']}" + r"}{" + f"{N['n']}" + r"}",
                            font_size=46),
                    MathTex("=", font_size=44), MathTex(f"{N['expected_glasses_bus']:g}", font_size=46, color=HILITE)
                    ).arrange(RIGHT, buff=0.25)
        o2 = VGroup(txt(label("observed"), size=28, color=GREY_B),
                    MathTex(str(N["glasses_bus"]), font_size=46, color=RLGREEN)).arrange(RIGHT, buff=0.2)
        r2 = VGroup(gl, e2, o2).arrange(RIGHT, buff=0.4)
        x1 = MathTex(r"\neq", font_size=50, color=RLRED)
        eq2 = MathTex("=", font_size=50, color=RLGREEN)
        r1 = VGroup(e1, x1, o1).arrange(RIGHT, buff=0.35)
        r2 = VGroup(gl, e2, eq2, o2).arrange(RIGHT, buff=0.35)
        rows = VGroup(r1, r2).arrange(DOWN, buff=0.3)
        rows.next_to(T["grid"], DOWN, buff=0.35).set_x(0)
        ok2 = txt("✓", size=44, weight=BOLD, color=RLGREEN).next_to(o2, RIGHT, buff=0.2)

        with self.say("5.7") as (tr, t):
            self.play(FadeOut(formula), FadeIn(T["grid"]), run_time=0.8)
            self.play(Create(ring(T["rowtot"][0])), Create(ring(T["coltot"][0])), run_time=0.5)
            self.play(Write(e1), run_time=0.9)
            self.cue(tr, t, {"en": "The table says", "uz": "Jadvalda esa"})
            self.play(Create(ring(T["cell"][0][0], color=RLRED)), FadeIn(x1), FadeIn(o1), run_time=0.6)
            self.cue(tr, t, {"en": "For glasses", "uz": "Koʻzoynak uchun"})
            self.play(FadeIn(gl), Write(e2), run_time=0.9)
            self.cue(tr, t, {"en": "Exactly what we see", "uz": "Aynan jadvaldagidek"})
            self.play(FadeIn(eq2), FadeIn(o2), FadeIn(ok2, scale=1.3), run_time=0.6)
        self.clear_all()


class S05Features(LectureScene):
    """AI: a feature independent of the labels teaches the model nothing (illustration)."""

    def construct(self):
        floor = Line([-5.6, -1.6, 0], [-1.0, -1.6, 0], color=GREY_B, stroke_width=2)
        bars = VGroup(*[Rectangle(width=1.2, height=2.0, stroke_width=0, fill_color=HILITE, fill_opacity=1)
                        .move_to([x, -0.6, 0]) for x in (-4.4, -2.2)])
        labs = VGroup(*[txt(s, size=24, color=GREY_B).next_to([x, -1.6, 0], DOWN, buff=0.2)
                        for s, x in ((label("feature_0"), -4.4), (label("feature_1"), -2.2))])
        eq = MathTex(r"P(y \mid x) = P(y)", font_size=46, color=HILITE).move_to([-3.3, 1.5, 0])
        ylab = txt(label("share_of_label_y"), size=24, color=GREY_B).next_to(eq, DOWN, buff=0.25)
        model = RoundedRectangle(corner_radius=0.2, width=2.8, height=1.6, stroke_color=LBLUE, stroke_width=3)
        model.move_to([3.6, 0, 0])
        mlab = txt(label("model"), size=30, weight=BOLD, color=LBLUE).move_to(model)
        arr = Arrow([-0.6, 0, 0], model.get_left(), buff=0.1, color=GREY_B, stroke_width=5)
        nothing = txt(label("learns_nothing"), size=28, color=RLRED).next_to(model, DOWN, buff=0.3)
        with self.say("5.8") as (tr, t):
            self.play(Create(floor), GrowFromEdge(bars[0], DOWN), GrowFromEdge(bars[1], DOWN), FadeIn(labs), run_time=1.0)
            self.play(Write(eq), FadeIn(ylab), run_time=0.8)
            self.cue(tr, t, {"en": "the model can learn", "uz": "model undan"})
            self.play(GrowArrow(arr), Create(model), FadeIn(mlab), run_time=0.7)
            self.play(FadeIn(nothing), run_time=0.5)
        self.clear_all()


class S05HandsOn(LectureScene):
    def construct(self):
        T = placed(bike_bus_table(size=26, cw=2.1, head_w=2.4), [0, -1.3, 0])
        pc = pause_card([label("suppose_bike_and_bus_were_independent"),
                         label("how_many_students_in_no_bike_q")])
        pc.scale(0.82).to_edge(UP, buff=SAFE + 0.2)
        q = txt("?", size=40, weight=BOLD, color=HILITE)
        with self.say("5.9") as (tr, t):
            self.play(FadeIn(T["grid"]), run_time=0.6)
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(pc, shift=DOWN * 0.2), Create(ring(T["cell"][1][0])), run_time=0.6)
        self.hands_on()

        calc = VGroup(MathTex(r"\frac{" + f"{N['nobike']}" + r"\times" + f"{N['bus']}" + r"}{" + f"{N['n']}" + r"}",
                              font_size=50),
                      MathTex("=", font_size=48), MathTex(f"{N['expected_nobike_bus']:g}", font_size=50, color=HILITE),
                      txt(label("table"), size=30, color=GREY_B),
                      MathTex(str(C["nobike_bus"]), font_size=50, color=RLRED)).arrange(RIGHT, buff=0.3)
        calc.move_to([0, 2.0, 0])
        with self.say("5.10") as (tr, t):
            self.play(FadeOut(pc), run_time=0.4)
            self.play(Create(ring(T["rowtot"][1])), Create(ring(T["coltot"][0])), Write(calc[:3]), run_time=1.0)
            self.cue(tr, t, {"en": "The table says", "uz": "Jadvalda esa"})
            self.play(FadeIn(calc[3:]), Indicate(T["cell"][1][0], color=RLRED), run_time=0.7)
            self.cue(tr, t, {"en": "Dependence again", "uz": "Yana bogʻliqlik"})
            dep = txt(label("dependent"), size=34, weight=BOLD, color=RLRED).next_to(calc, DOWN, buff=0.35)
            self.play(FadeIn(dep, scale=1.2), run_time=0.5)
        self.clear_all()

        # pooling groups can turn an answer around: two group tables merge into one
        def mini(color):
            g = VGroup(*[Square(0.5, stroke_color=color, stroke_width=3) for _ in range(4)]).arrange_in_grid(2, 2, buff=0)
            return g
        g1, g2 = mini(LBLUE).move_to([-4.0, 0.6, 0]), mini(HILITE).move_to([-1.6, 0.6, 0])
        l1 = txt(label("group_1"), size=24, color=LBLUE).next_to(g1, UP, buff=0.2)
        l2 = txt(label("group_2"), size=24, color=HILITE).next_to(g2, UP, buff=0.2)
        pooled = mini(WHITE).scale(1.4).move_to([3.2, 0.6, 0])
        lp = txt(label("pooled"), size=24).next_to(pooled, UP, buff=0.2)
        arr = Arrow([-0.8, 0.6, 0], pooled.get_left(), buff=0.25, color=GREY_B, stroke_width=5)
        flip = MathTex(r"\circlearrowleft", font_size=90, color=RLRED).next_to(pooled, DOWN, buff=0.35)
        with self.say("5.11") as (tr, t):
            self.play(Create(g1), Create(g2), FadeIn(l1), FadeIn(l2), run_time=0.8)
            self.play(GrowArrow(arr), TransformFromCopy(VGroup(g1, g2), pooled), FadeIn(lp), run_time=1.0)
            self.cue(tr, t, {"en": "the answer can turn", "uz": "javob butunlay"})
            self.play(FadeIn(flip, scale=0.6), run_time=0.6)
        self.clear_all()


SCENES = ["S05Bars", "S05Glasses", "S05Expected", "S05Features", "S05HandsOn"]
