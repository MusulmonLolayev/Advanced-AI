"""Lecture 1, section 1 — data types: categorical (nominal, ordinal) and numerical
(discrete, continuous). The example salary is a real one from the 600 (SAL); the
600 dots at the end are the same salaries as sections 3-4."""
from lecture01_kit import *
from lecture01_s04 import hist_axis, hist_dots

EXAMPLE_SALARY = SAL[len(SAL) // 2]     # the person in the middle of the 600

VARS = [  # (label, example value, categorical?)
    (label("eye_colour"), label("brown"), True),
    (label("city_of_birth"), label("samarkand"), True),
    (label("rating"), label("medium"), True),
    (label("number_of_children"), "2", False),
    (label("salary"), money(EXAMPLE_SALARY), False),
    (label("height"), label("172_4_cm"), False),
]
CAT, NUM = label("categorical"), label("numerical")
LEAVES = ["nominal", "ordinal", label("discrete"), label("continuous")]


def tree_header():
    """The four data types as a strip along the top, grouped under their two families."""
    leaves = VGroup()
    for n in LEAVES:
        r = RoundedRectangle(corner_radius=0.1, width=2.7, height=0.62, stroke_color=GREY_D, stroke_width=3)
        leaves.add(VGroup(r, txt(n, size=24).move_to(r)))
    leaves.arrange(RIGHT, buff=0.25)
    leaves[2:].shift(RIGHT * 0.5)
    fam = VGroup(txt(CAT, size=24, color=GREY_B).next_to(leaves[:2], UP, buff=0.18),
                 txt(NUM, size=24, color=GREY_B).next_to(leaves[2:], UP, buff=0.18))
    return VGroup(fam, leaves).to_edge(UP, buff=SAFE + 0.2)


def lit(header, i, color=HILITE):
    return [header[1][j][0].animate.set_stroke(color if j == i else GREY_D, width=4 if j == i else 3)
            for j in range(4)]


class S01DataTypes(LectureScene):
    def construct(self):
        self.section_card(1)
        cards = VGroup(*[card(lab, val) for lab, val, _ in VARS]).arrange_in_grid(rows=2, cols=3, buff=(0.5, 0.45))

        with self.say("1.1") as (tr, t):
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.6) for c in cards], lag_ratio=0.15), run_time=1.8)

        # (Tashkent + Samarkand) / 2: arithmetic on categories means nothing
        with self.say("1.2") as (tr, t):
            self.play(cards.animate.scale(0.62).arrange(RIGHT, buff=0.15).to_edge(UP, buff=SAFE + 0.3), run_time=0.9)
            self.play(cards[1][0].animate.set_stroke(HILITE, width=5), run_time=0.4)
            self.cue(tr, t, 1)
            eq = MathTex(r"\frac{\text{" + label("tashkent") + r"} + \text{" + label("samarkand") +
                         r"}}{2}", "=", "?", font_size=64)
            self.play(Write(eq), run_time=1.4)
            self.cue(tr, t, 2)
            cross = Cross(eq, stroke_color=BAD, stroke_width=8)
            self.play(Create(cross), run_time=0.6)

        # two families: categories and numbers
        left = RoundedRectangle(corner_radius=0.2, width=6.2, height=3.9, stroke_color=RLBLUE, stroke_width=3)
        right = left.copy().set_stroke(RLGREEN)
        bins = VGroup(left, right).arrange(RIGHT, buff=0.5).move_to(DOWN * 0.75)
        labs = VGroup(txt(CAT, size=32, weight=BOLD, color=RLBLUE).next_to(left, UP, buff=0.15),
                      txt(NUM, size=32, weight=BOLD, color=RLGREEN).next_to(right, UP, buff=0.15))
        with self.say("1.3") as (tr, t):
            self.play(FadeOut(eq), FadeOut(cross), cards[1][0].animate.set_stroke(RLBLUE, width=3), run_time=0.6)
            self.play(Create(left), Create(right), run_time=0.8)
            targets = []
            for k, (c, (_, _, is_cat)) in enumerate(zip(cards, VARS)):
                b = left if is_cat else right
                slot = [k % 3]
                targets.append(c.animate.scale(1.25).move_to(b.get_center() + UP * (1.25 - 1.25 * slot[0])))
            self.play(*targets, run_time=1.4)
            self.cue(tr, t, 1)
            self.play(FadeIn(labs[0], scale=1.2), FadeIn(labs[1]), run_time=0.7)

        # the four leaves get a strip at the top; each is shown on its own below it
        header = tree_header()
        with self.say("1.4") as (tr, t):
            self.play(FadeOut(VGroup(cards, bins, labs)), FadeIn(header), run_time=0.9)
            self.play(*lit(header, 0), run_time=0.4)
            eyes = VGroup(*[VGroup(Circle(radius=0.42, fill_color=c, fill_opacity=1, stroke_width=0),
                                   txt(n, size=22, color=GREY_B))
                            for c, n in ((ManimColor("#7B4A2A"), label("brown")),
                                         (ManimColor("#3B7DD8"), label("blue")),
                                         (ManimColor("#4E9A55"), label("green")),
                                         (ManimColor("#8C8C8C"), label("grey")))])
            for e in eyes:
                e[1].next_to(e[0], DOWN, buff=0.15)
            eyes.arrange(RIGHT, buff=0.8).move_to(UP * 0.3)
            cities = VGroup(*[txt(c, size=30) for c in ("Toshkent", "Samarqand", "Buxoro", "Xiva")])
            cities.arrange(RIGHT, buff=0.9).move_to(DOWN * 1.6)
            self.play(LaggedStart(*[FadeIn(e, scale=0.6) for e in eyes], lag_ratio=0.15),
                      LaggedStart(*[FadeIn(c) for c in cities], lag_ratio=0.15), run_time=1.2)
            for a, b in ((0, 2), (1, 3), (0, 1)):     # any order is as good as any other
                self.play(Swap(eyes[a], eyes[b]), Swap(cities[a], cities[b]), run_time=0.7)
            self.cue(tr, t, 1)
            self.play(Indicate(header[1][0], color=HILITE), run_time=0.8)

        # ordinal: an order, but unequal steps
        with self.say("1.5") as (tr, t):
            self.play(FadeOut(eyes), FadeOut(cities), *lit(header, 1), run_time=0.6)
            xs = (-4.5, -1.8, 4.0)
            ax = Arrow([-5.6, -0.6, 0], [5.6, -0.6, 0], buff=0, color=GREY_B, stroke_width=3)
            pts = VGroup(*[Dot([x, -0.6, 0], radius=0.14, color=HILITE) for x in xs])
            names = VGroup(*[txt(n, size=32).next_to(d, UP, buff=0.3)
                             for n, d in zip((label("low"), label("medium"), label("high")), pts)])
            self.play(GrowArrow(ax), run_time=0.6)
            self.play(LaggedStart(*[AnimationGroup(FadeIn(d, scale=0.5), FadeIn(n)) for d, n in zip(pts, names)],
                                  lag_ratio=0.35), run_time=1.4)
            self.cue(tr, t, {"en": "but the steps", "uz": "lekin"})
            gaps = VGroup(*[BraceBetweenPoints([a, -0.75, 0], [b, -0.75, 0], DOWN, color=GREY_B)
                            for a, b in zip(xs, xs[1:])])
            q = VGroup(*[txt("?", size=36, color=HILITE).next_to(g, DOWN, buff=0.12) for g in gaps])
            neq = MathTex(r"\neq", font_size=56, color=BAD).move_to((q[0].get_center() + q[1].get_center()) / 2)
            self.play(GrowFromCenter(gaps[0]), GrowFromCenter(gaps[1]), FadeIn(q), run_time=0.8)
            self.play(FadeIn(neq, scale=1.3), run_time=0.5)
        ordinal = VGroup(ax, pts, names, gaps, q, neq)

        # discrete: whole numbers only
        with self.say("1.6") as (tr, t):
            self.play(FadeOut(ordinal), *lit(header, 2), run_time=0.6)
            self.cue(tr, t, 1)
            nl = NumberLine(x_range=[0, 4, 1], length=9, include_numbers=True, font_size=34,
                            color=GREY_B).move_to(DOWN * 0.8)
            self.play(Create(nl), run_time=0.8)
            self.cue(tr, t, 2)
            kids = VGroup(*[Dot(nl.n2p(k) + UP * 0.45, radius=0.16, color=RLGREEN) for k in (1, 2, 3)])
            self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in kids], lag_ratio=0.4), run_time=1.0)
            self.cue(tr, t, 3)
            half = Dot(nl.n2p(2.5) + UP * 0.45, radius=0.16, color=GREY_B)
            hl = txt("2.5", size=30, color=GREY_B).next_to(half, UP, buff=0.25)
            self.play(FadeIn(half), FadeIn(hl), run_time=0.5)
            self.play(Create(Cross(VGroup(half, hl), stroke_color=BAD, stroke_width=6)), run_time=0.5)

        # continuous: a ruler, read to as many decimals as we like
        with self.say("1.7") as (tr, t):
            self.play(*[FadeOut(m) for m in self.mobjects if m is not header and m is not self.brand],
                      *lit(header, 3), run_time=0.6)
            ruler = NumberLine(x_range=[171, 174, 1], length=10, include_numbers=True, font_size=30,
                               color=GREY_B, decimal_number_config={"num_decimal_places": 0}).move_to(DOWN * 1.2)
            minor = VGroup(*[Line(UP * 0.08, DOWN * 0.08, stroke_width=1.5, color=GREY_C).move_to(ruler.n2p(171 + k / 10))
                             for k in range(31) if k % 10])
            unit = txt(label("cm"), size=26, color=GREY_B).next_to(ruler, RIGHT, buff=0.3)
            val = ValueTracker(172.0)
            mark = always_redraw(lambda: Triangle(color=HILITE, fill_opacity=1).scale(0.16).rotate(PI)
                                 .move_to(ruler.n2p(val.get_value()) + UP * 0.35))
            self.play(Create(ruler), FadeIn(minor), FadeIn(unit), run_time=0.9)
            read = txt("172", size=56, weight=BOLD).move_to(UP * 0.7)
            self.add(mark)
            self.play(FadeIn(read), run_time=0.4)
            for v, s in ((172.4, "172.4"), (172.43, "172.43")):
                self.play(val.animate.set_value(v), Transform(read, txt(s, size=56, weight=BOLD).move_to(read)),
                          run_time=1.0)
            self.cue(tr, t, 1)
            self.play(Indicate(header[1][3], color=HILITE), run_time=0.8)
        self.clear_all()


class S01WhyItMatters(LectureScene):
    def construct(self):
        # the 2x2 map: which calculation goes with which type
        header = tree_header()
        with self.say("1.8") as (tr, t):
            self.add(header)
            self.play(header.animate.move_to(UP * 1.4), run_time=0.9)
            self.cue(tr, t, 2)
            num_ops = txt(label("mean_std_deviation"), size=28, color=RLGREEN)
            num_ops.next_to(header[1][2:], DOWN, buff=0.7)
            self.play(FadeIn(num_ops, shift=DOWN * 0.2), run_time=0.7)
            self.cue(tr, t, 3)
            cat_ops = txt(label("count_proportion"), size=28, color=RLBLUE)
            cat_ops.next_to(header[1][:2], DOWN, buff=0.7)
            self.play(FadeIn(cat_ops, shift=DOWN * 0.2), run_time=0.7)
        self.play(FadeOut(VGroup(header, num_ops, cat_ops)), run_time=0.6)

        # a city name cannot be a number; it becomes a category code
        cities = ("Toshkent", "Samarqand", "Buxoro")
        names = VGroup(*[txt(c, size=36) for c in cities]).arrange(DOWN, aligned_edge=RIGHT, buff=0.6).shift(LEFT * 2.5)
        wrong = VGroup(*[txt(f"→  {k}", size=36, color=GREY_B).next_to(n, RIGHT, buff=0.4)
                         for k, n in zip((1, 2, 3), names)])
        onehot = VGroup(*[MathTex(v, font_size=44, color=HILITE).next_to(n, RIGHT, buff=0.5).set_x(1.6, LEFT)
                          for v, n in zip((r"\rightarrow\; [1,\,0,\,0]", r"\rightarrow\; [0,\,1,\,0]",
                                           r"\rightarrow\; [0,\,0,\,1]"), names)])
        with self.say("1.9") as (tr, t):
            self.play(LaggedStart(*[FadeIn(n) for n in names], lag_ratio=0.2), run_time=0.9)
            self.cue(tr, t, {"en": 1, "uz": "Shahar"})
            self.play(FadeIn(wrong), run_time=0.6)
            x = Cross(wrong, stroke_color=BAD, stroke_width=6)
            self.play(Create(x), run_time=0.5)
            self.cue(tr, t, {"en": 2, "uz": "avval"})
            self.play(FadeOut(wrong), FadeOut(x), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(o, shift=RIGHT * 0.3) for o in onehot], lag_ratio=0.25), run_time=1.2)
        self.clear_all()

        # hands-on: three variables to sort
        qs = (label("blood_type_q"), label("finishing_place_in_an_exam_q"),
              label("room_temperature_q"))
        pc = pause_card(qs).move_to(UP * 0.4)
        with self.say("1.10"):
            self.play(FadeIn(pc), run_time=0.8)
        self.hands_on()

        ans = ("nominal", "ordinal", label("continuous"))
        tags = VGroup(*[txt(a, size=28, weight=BOLD, color=GOOD).next_to(pc[1][i], RIGHT, buff=0.5)
                        for i, a in enumerate(ans)])
        with self.say("1.11") as (tr, t):
            self.play(FadeIn(tags[0], shift=LEFT * 0.2), run_time=0.5)
            self.cue(tr, t, 1)
            self.play(FadeIn(tags[1], shift=LEFT * 0.2), run_time=0.5)
            self.cue(tr, t, {"en": 3, "uz": 2})
            self.play(FadeIn(tags[2], shift=LEFT * 0.2), run_time=0.5)
        self.clear_all()

        # our 600 salaries: numerical, continuous - but whose?
        dots, axis = hist_dots(), hist_axis()
        tag = txt(f"{NUM} · {LEAVES[3]}", size=30, color=RLGREEN).to_edge(UP, buff=SAFE + 0.4)
        with self.say("1.12") as (tr, t):
            self.play(FadeIn(axis), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.002), run_time=1.6)
            self.play(FadeIn(tag), run_time=0.5)
            self.cue(tr, t, {"en": 2, "uz": 1})
            q = txt("?", size=96, weight=BOLD, color=HILITE).move_to([3.2, 0.9, 0])
            self.play(FadeIn(q, scale=0.5), run_time=0.6)
            self.cue(tr, t, {"en": 3, "uz": 2})
            self.play(VGroup(dots, axis).animate.scale(0.45).move_to(DOWN * 0.6), FadeOut(q), run_time=1.0)
            whole = DashedVMobject(Ellipse(width=11.5, height=5.6, color=GREY_B), num_dashes=60).move_to(DOWN * 0.4)
            self.play(Create(whole), run_time=1.0)
        self.clear_all()


SCENES = ["S01DataTypes", "S01WhyItMatters"]
