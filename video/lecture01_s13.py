"""Lecture 1, section 13 — mutually exclusive vs independent events, on one die.

Every probability shown is a fraction capture_l01.py computed and asserted
(p_even, p_gt4, p_even_and_gt4, p_even_times_odd, p_even_and_odd, p_lt3, p_even_and_lt3).
"""
from fractions import Fraction

from lecture01_kit import *

P = {k: L[k] for k in ("p_even", "p_gt4", "p_even_and_gt4", "p_even_times_odd", "p_even_and_odd",
                       "p_lt3", "p_even_and_lt3")}
# the narration speaks these
assert (P["p_even"], P["p_gt4"], P["p_even_and_gt4"]) == ("1/2", "1/3", "1/6")
assert (P["p_even_times_odd"], P["p_even_and_odd"]) == ("1/4", "0")
assert (P["p_lt3"], P["p_even_and_lt3"]) == ("1/3", "1/6")
assert Fraction(P["p_even"]) * Fraction(P["p_gt4"]) == Fraction(P["p_even_and_gt4"])
assert Fraction(P["p_even"]) * Fraction(P["p_lt3"]) == Fraction(P["p_even_and_lt3"])
LBLUE = "#8C88F0"   # RLBLUE is too dark for text on black


def tex(fr):
    """'1/2' -> \\frac{1}{2}; '0' stays 0."""
    if "/" not in fr:
        return fr
    a, b = fr.split("/")
    return rf"\frac{{{a}}}{{{b}}}"


def venn(sets, centers, radii, colors, labels, faces_at, face_size=0.62):
    """Circles over a die's six faces; faces_at maps face -> position."""
    circles = VGroup(*[Circle(radius=r, color=c, stroke_width=4).set_fill(c, 0.12).move_to(p)
                       for p, r, c in zip(centers, radii, colors)])
    labs = VGroup(*[txt(l, size=26, weight=BOLD, color=LBLUE if c == RLBLUE else c) for l, c in zip(labels, colors)])
    for lab, circ, p in zip(labs, circles, centers):
        lab.next_to(circ, UP, buff=0.12)
    faces = {n: die_face(n, face_size).move_to(faces_at[n]) for n in range(1, 7)}
    return circles, labs, faces


def omega_box(width=8.4, height=4.6, center=(-2.2, -0.5, 0)):
    box = RoundedRectangle(corner_radius=0.2, width=width, height=height, stroke_color=GREY_B, stroke_width=2)
    box.move_to(center)
    lab = MathTex(r"\Omega", font_size=40, color=GREY_B).next_to(box.get_corner(UL), DR, buff=0.15)
    return VGroup(box, lab)


class S13Definitions(LectureScene):
    def construct(self):
        self.section_card(13)
        left_t = txt(label("mutually_exclusive"), size=34, weight=BOLD, color=RLRED)
        right_t = txt(label("independent"), size=34, weight=BOLD, color=RLGREEN)
        left_t.move_to([-3.5, 2.2, 0])
        right_t.move_to([3.5, 2.2, 0])
        neq = MathTex(r"\neq", font_size=72).move_to([0, 2.2, 0])
        die = die_face(6, 0.9).move_to([0, 0.0, 0])
        t = line("13.1")
        with self.voiceover(t) as tr:
            self.play(FadeIn(left_t, shift=RIGHT * 0.3), FadeIn(right_t, shift=LEFT * 0.3), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(Write(neq), Indicate(left_t, color=RLRED), Indicate(right_t, color=RLGREEN), run_time=1.0)
            self.cue(tr, t, 2)
            self.play(FadeIn(die, scale=0.6), Rotate(die, PI / 2), run_time=0.9)

        a = Circle(radius=1.0, color=RLBLUE, stroke_width=4).set_fill(RLBLUE, 0.15).move_to([-4.7, 0.0, 0])
        b = Circle(radius=1.0, color=HILITE, stroke_width=4).set_fill(HILITE, 0.15).move_to([-2.3, 0.0, 0])
        ab = VGroup(txt("A", size=30, weight=BOLD, color=LBLUE).move_to(a),
                    txt("B", size=30, weight=BOLD, color=HILITE).move_to(b))
        empty = MathTex(r"A\cap B=\varnothing", font_size=44).move_to([-3.5, -1.7, 0])
        zero = MathTex(r"P(A\cap B)=0", font_size=44, color=RLRED).next_to(empty, DOWN, buff=0.35)
        t = line("13.2")
        with self.voiceover(t) as tr:
            self.play(FadeOut(die), run_time=0.4)
            self.play(GrowFromCenter(a), GrowFromCenter(b), FadeIn(ab), run_time=0.9)
            self.cue(tr, t, 1)
            self.play(FadeIn(empty), run_time=0.6)
            self.play(FadeIn(zero, shift=UP * 0.2), run_time=0.6)

        a2 = Circle(radius=1.1, color=RLBLUE, stroke_width=4).set_fill(RLBLUE, 0.15).move_to([2.9, 0.0, 0])
        b2 = Circle(radius=1.1, color=HILITE, stroke_width=4).set_fill(HILITE, 0.15).move_to([4.1, 0.0, 0])
        ab2 = VGroup(txt("A", size=30, weight=BOLD, color=LBLUE).move_to([2.35, 0.0, 0]),
                     txt("B", size=30, weight=BOLD, color=HILITE).move_to([4.65, 0.0, 0]))
        prod = MathTex(r"P(A\cap B)=P(A)\cdot P(B)", font_size=44, color=RLGREEN).move_to([3.5, -1.7, 0])
        know = txt(label("knowing_a_tells_us_nothing_about"),
                   size=24, color=GREY_B)
        know.scale_to_fit_width(min(know.width, 6.0)).next_to(prod, DOWN, buff=0.4)
        t = line("13.3")
        with self.voiceover(t) as tr:
            self.play(GrowFromCenter(a2), GrowFromCenter(b2), FadeIn(ab2), run_time=0.9)
            self.play(FadeIn(prod, shift=UP * 0.2), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeIn(know), run_time=0.7)
        self.clear_all()

        # 13.3a: a coin and a die thrown together: nothing passes from one to the other
        coin = VGroup(Circle(radius=0.95, color=RLORANGE, stroke_width=5).set_fill(RLORANGE, 0.2),
                      txt(label("heads"), size=30, weight=BOLD, color=RLORANGE)).move_to([-3.2, 0.4, 0])
        die = die_face(4, 1.7).move_to([3.2, 0.4, 0])
        link = DashedLine(coin.get_right() + RIGHT * 0.3, die.get_left() + LEFT * 0.3, color=GREY_B, stroke_width=4)
        link.add_tip(tip_length=0.25)
        cross = Cross(Square(0.7).move_to(link.get_center()), stroke_color=RLRED, stroke_width=7)
        none = txt(label("no_effect"), size=28, color=RLRED).next_to(cross, UP, buff=0.3)
        ind = txt(label("independent"), size=40, weight=BOLD, color=RLGREEN).move_to([0, -2.2, 0])
        t = line("13.3a")
        with self.voiceover(t) as tr:
            self.cue(tr, t, 1)
            self.play(FadeIn(coin, shift=RIGHT * 0.3), FadeIn(die, shift=LEFT * 0.3), run_time=0.8)
            self.cue(tr, t, 2)
            self.play(Create(link), run_time=0.6)
            self.play(Create(cross), FadeIn(none), run_time=0.6)
            self.cue(tr, t, 3)
            self.play(FadeIn(ind, scale=0.8), run_time=0.6)
        self.clear_all()


# one die, two events: A = even, B = more than four
FACE_AB = {2: (-4.3, 0.2, 0), 4: (-4.3, -1.2, 0), 6: (-2.55, -0.5, 0), 5: (-1.2, -0.5, 0),
           1: (-5.75, 1.15, 0), 3: (-0.1, 1.15, 0)}


class S13Die(LectureScene):
    def construct(self):
        om = omega_box()
        circles, labs, faces = venn([], [(-3.6, -0.5, 0), (-1.75, -0.5, 0)], [1.65, 1.3], [RLBLUE, HILITE],
                                    [label("a_even"), label("b_more_than_4")], FACE_AB)
        labs[1].next_to(circles[1], DOWN, buff=0.12)
        pa = MathTex(r"P(A)=" + tex(P["p_even"]), font_size=44, color=LBLUE)
        pb = MathTex(r"P(B)=" + tex(P["p_gt4"]), font_size=44, color=HILITE)
        col = VGroup(pa, pb).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([3.9, 2.4, 0])
        t = line("13.4")
        with self.voiceover(t) as tr:
            self.play(FadeIn(om), LaggedStart(*[FadeIn(faces[n], scale=0.5) for n in range(1, 7)],
                                              lag_ratio=0.12), run_time=1.2)
            self.cue(tr, t, 1)
            self.play(Create(circles[0]), FadeIn(labs[0]), run_time=0.7)
            self.cue(tr, t, 2)
            self.play(*[Indicate(faces[n], color=RLBLUE) for n in (2, 4, 6)], FadeIn(pa), run_time=0.9)
            self.cue(tr, t, 3)
            self.play(Create(circles[1]), FadeIn(labs[1]), run_time=0.7)
            self.cue(tr, t, 4)
            self.play(*[Indicate(faces[n], color=HILITE) for n in (5, 6)], FadeIn(pb), run_time=0.9)

        pab = MathTex(r"P(A\cap B)=" + tex(P["p_even_and_gt4"]), font_size=44, color=WHITE)
        chk = MathTex(tex(P["p_even"]) + r"\cdot" + tex(P["p_gt4"]) + "=" + tex(P["p_even_and_gt4"]),
                      font_size=44, color=WHITE)
        ok = txt(label("independent_ok"), size=34, weight=BOLD, color=RLGREEN)
        VGroup(pab, chk, ok).arrange(DOWN, buff=0.35, aligned_edge=LEFT).next_to(col, DOWN, buff=0.4, aligned_edge=LEFT)
        t = line("13.5")
        with self.voiceover(t) as tr:
            self.play(faces[6].animate.set_color(RLGREEN).scale(1.25), FadeIn(pab), run_time=0.9)
            self.cue(tr, t, {"en": 2, "uz": 1})
            self.play(FadeIn(chk, shift=UP * 0.2), run_time=0.8)
            self.cue(tr, t, {"en": 3, "uz": 2})
            self.play(FadeIn(ok, scale=0.8), run_time=0.6)

        noex = txt(label("not_exclusive_6_is_in_both"), size=28, color=RLRED)
        noex.move_to([-2.2, -3.25, 0])
        arrow = Arrow(noex.get_top(), faces[6].get_bottom(), buff=0.15, color=RLRED, stroke_width=4)
        t = line("13.6")
        with self.voiceover(t) as tr:
            self.play(Indicate(faces[6], color=RLRED, scale_factor=1.3), run_time=0.8)
            self.play(FadeIn(noex), GrowArrow(arrow), run_time=0.8)
        self.clear_all()


FACE_EO = {2: (-4.6, 0.3, 0), 4: (-3.7, -1.0, 0), 6: (-5.2, -1.1, 0),
           1: (-0.9, 0.3, 0), 3: (0.0, -1.0, 0), 5: (-1.5, -1.1, 0)}


class S13EvenOdd(LectureScene):
    def construct(self):
        om = omega_box(width=7.9, center=(-2.45, -0.5, 0))
        circles, labs, faces = venn([], [(-4.5, -0.5, 0), (-0.8, -0.5, 0)], [1.45, 1.45], [RLBLUE, RLRED],
                                    [label("a_even"), label("c_odd")], FACE_EO)
        excl = txt(label("mutually_exclusive_ok"), size=30, weight=BOLD, color=RLRED)
        ask = txt(label("independent_q"), size=34, weight=BOLD, color=HILITE)
        VGroup(excl, ask).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to([4.4, 2.2, 0])
        t = line("13.7")
        with self.voiceover(t) as tr:
            self.play(FadeIn(om), LaggedStart(*[FadeIn(faces[n], scale=0.5) for n in range(1, 7)],
                                              lag_ratio=0.1), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(Create(circles[0]), Create(circles[1]), FadeIn(labs), run_time=0.9)
            self.cue(tr, t, 2)
            self.play(FadeIn(excl), run_time=0.6)
            self.cue(tr, t, 3)
            self.play(FadeIn(ask, scale=0.8), run_time=0.6)

        prod = MathTex(r"P(A)\cdot P(C)=" + tex(P["p_even"]) + r"\cdot" + tex(P["p_even"]) + "=" +
                       tex(P["p_even_times_odd"]), font_size=36)
        both = MathTex(r"P(A\cap C)=" + tex(P["p_even_and_odd"]), font_size=40, color=RLRED)
        neq = MathTex(r"\neq", font_size=48)
        dep = txt(label("dependent"), size=34, weight=BOLD, color=RLRED)
        grp = VGroup(prod, neq, both, dep).arrange(DOWN, buff=0.25).move_to([4.45, -0.9, 0])
        knows = Arrow(circles[0].get_bottom() + DOWN * 0.1, circles[1].get_bottom() + DOWN * 0.1, path_arc=0.9,
                      color=HILITE, stroke_width=4)
        knows_l = txt(label("even_certainly_not_odd"), size=24, color=HILITE)
        knows_l.next_to(knows, DOWN, buff=0.3).add_background_rectangle(opacity=0.9, buff=0.06)
        t = line("13.8")
        with self.voiceover(t) as tr:
            self.play(Transform(ask, txt(label("no"), size=40, weight=BOLD, color=RLRED).move_to(ask)),
                      run_time=0.5)
            self.cue(tr, t, 1)
            self.play(Create(knows), FadeIn(knows_l), run_time=1.0)
            self.cue(tr, t, 3)
            self.play(FadeIn(prod), run_time=0.7)
            self.play(FadeIn(neq), FadeIn(both), run_time=0.7)
            self.play(FadeIn(dep, scale=0.8), run_time=0.5)

        rule = VGroup(txt(label("exclusive_p_0"), size=34, weight=BOLD),
                      MathTex(r"\Downarrow", font_size=56),
                      txt(label("always_dependent"), size=40, weight=BOLD, color=RLRED))
        rule.arrange(DOWN, buff=0.25)
        frame = SurroundingRectangle(rule, buff=0.4, color=RLRED, corner_radius=0.15)
        rg = VGroup(frame, rule)
        rg.scale_to_fit_width(min(rg.width, 4.6)).move_to([4.4, -0.3, 0])
        t = line("13.9")
        with self.voiceover(t) as tr:
            self.play(FadeOut(VGroup(prod, neq, both, dep, excl, ask, knows, knows_l)), run_time=0.5)
            self.cue(tr, t, 1)
            self.play(FadeIn(rg, scale=0.9), run_time=0.9)
        self.clear_all()

        # 13.9a: exclusive is a picture, independent is a number
        div = Line(UP * 2.6, DOWN * 2.8, color=GREY_D, stroke_width=2)
        lt = txt(label("mutually_exclusive"), size=32, weight=BOLD, color=RLRED).move_to([-3.6, 2.4, 0])
        rt = txt(label("independent"), size=32, weight=BOLD, color=RLGREEN).move_to([3.6, 2.4, 0])
        ca = Circle(radius=1.0, color=RLBLUE, stroke_width=4).set_fill(RLBLUE, 0.15).move_to([-4.85, 0.1, 0])
        cb = Circle(radius=1.0, color=HILITE, stroke_width=4).set_fill(HILITE, 0.15).move_to([-2.35, 0.1, 0])
        abl = VGroup(txt("A", size=30, weight=BOLD, color=LBLUE).move_to(ca),
                     txt("B", size=30, weight=BOLD, color=HILITE).move_to(cb))
        pic = txt(label("picture"), size=30, color=GREY_B).move_to([-3.6, -2.0, 0])
        eqn = MathTex(r"P(A\cap B)", "=", r"P(A)\cdot P(B)", font_size=46, color=RLGREEN).move_to([3.6, 0.1, 0])
        num = txt(label("numbers"), size=30, color=GREY_B).move_to([3.6, -2.0, 0])
        t = line("13.9a")
        with self.voiceover(t) as tr:
            self.play(Create(div), FadeIn(lt), FadeIn(rt), run_time=0.7)
            self.cue(tr, t, 1)
            self.play(GrowFromCenter(ca), GrowFromCenter(cb), FadeIn(abl), run_time=0.8)
            self.play(FadeIn(pic, shift=UP * 0.2), run_time=0.5)
            self.cue(tr, t, 2)
            self.play(Write(eqn), run_time=1.0)
            self.play(FadeIn(num, shift=UP * 0.2), run_time=0.5)
        self.clear_all()


class S13HandsOn(LectureScene):
    def construct(self):
        # naive Bayes: a message's words treated as independent given "spam"
        words = [label("free"), label("prize"), label("click")]
        chips = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.12, width=2.4, height=0.8, stroke_color=HILITE,
                                                 stroke_width=3), txt(x, size=30)) for x in words])
        for c in chips:
            c[1].move_to(c[0])
        chips.arrange(RIGHT, buff=0.9).move_to(UP * 1.6)
        spam = txt(label("spam_q"), size=30, color=RLRED).next_to(chips, UP, buff=0.4)
        f = MathTex(r"P(w_1, w_2, w_3 \mid \text{spam})", r"\approx",
                    r"P(w_1\mid\text{spam})\,P(w_2\mid\text{spam})\,P(w_3\mid\text{spam})", font_size=40)
        f.move_to(DOWN * 0.4)
        f[2].set_color(RLGREEN)
        cuts = VGroup(*[Line(UP * 0.35, DOWN * 0.35, color=RLGREEN, stroke_width=5).move_to(
            (chips[i].get_right() + chips[i + 1].get_left()) / 2) for i in range(2)])
        indep = txt(label("each_word_independent_of_the_others"), size=26,
                    color=RLGREEN).next_to(f, DOWN, buff=0.6)
        t = line("13.10")
        with self.voiceover(t) as tr:
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in chips], lag_ratio=0.2),
                      FadeIn(spam), run_time=1.0)
            self.play(Write(f[0]), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeIn(cuts), FadeIn(f[1:]), run_time=1.0)
            self.play(FadeIn(indep), run_time=0.6)
        self.clear_all()

        card = pause_card([label("a_even_c_less_than_3"),
                           label("are_a_and_c_independent_we")])
        card.to_edge(UP, buff=SAFE + 0.3)
        row = VGroup(*[die_face(n, 0.75) for n in range(1, 7)]).arrange(RIGHT, buff=0.45).move_to(DOWN * 1.6)
        with self.voiceover(line("13.11")):
            self.play(FadeIn(card), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(f_, scale=0.5) for f_ in row], lag_ratio=0.1), run_time=0.9)
        self.hands_on()

        faces_at = {2: (-2.55, -0.5, 0), 4: (-4.6, 0.1, 0), 6: (-4.3, -1.3, 0), 1: (-1.1, -0.5, 0),
                    3: (-5.75, 1.15, 0), 5: (0.1, 1.15, 0)}
        om = omega_box()
        circles, labs, faces = venn([], [(-3.75, -0.5, 0), (-1.75, -0.5, 0)], [1.6, 1.25], [RLBLUE, HILITE],
                                    [label("a_even"), label("c_less_than_3")], faces_at)
        circles[0].set_stroke(RLBLUE)
        labs[1].next_to(circles[1], DOWN, buff=0.12)
        pac = MathTex(r"P(A\cap C)=" + tex(P["p_even_and_lt3"]), font_size=44)
        chk = MathTex(tex(P["p_even"]) + r"\cdot" + tex(P["p_lt3"]) + "=" + tex(P["p_even_and_lt3"]), font_size=44)
        ok = txt(label("independent_ok"), size=34, weight=BOLD, color=RLGREEN)
        col = VGroup(pac, chk, ok).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to([4.3, 0.2, 0])
        t = line("13.12")
        with self.voiceover(t) as tr:
            self.play(FadeOut(card), ReplacementTransform(row, VGroup(*[faces[n] for n in range(1, 7)])),
                      FadeIn(om), Create(circles), FadeIn(labs), run_time=1.2)
            self.play(faces[2].animate.set_color(RLGREEN).scale(1.25), FadeIn(pac), run_time=0.7)
            self.cue(tr, t, {"en": 2, "uz": 1})
            self.play(FadeIn(chk, shift=UP * 0.2), run_time=0.7)
            self.cue(tr, t, {"en": 3, "uz": 2})
            self.play(FadeIn(ok, scale=0.8), run_time=0.6)
        self.clear_all()

        # a fair die counts equally likely faces; tomorrow's weather has nothing like that
        fair = VGroup(*[die_face(n, 0.8) for n in range(1, 7)]).arrange_in_grid(2, 3, buff=0.3)
        fair_l = MathTex(r"\tfrac{1}{6}\ \text{" + label("each") + "}", font_size=52)
        fair_g = VGroup(fair, fair_l).arrange(DOWN, buff=0.35).move_to([-3.4, 0, 0])
        cloud = VGroup(*[Circle(radius=r, color=GREY_B, stroke_width=0).set_fill(GREY_B, 0.9).move_to(p)
                         for r, p in ((0.55, (-0.55, 0, 0)), (0.75, (0.1, 0.25, 0)), (0.55, (0.8, 0, 0)))])
        drops = VGroup(*[Line(UP * 0.12, DOWN * 0.12, color=RLBLUE, stroke_width=5).move_to([x, -0.85, 0])
                         for x in (-0.5, 0.1, 0.7)])
        rain = VGroup(cloud, drops)
        q = txt(label("equally_likely_q"), size=32, weight=BOLD, color=HILITE)
        rain_g = VGroup(rain, q).arrange(DOWN, buff=0.4).move_to([3.4, 0, 0])
        t = line("13.13")
        with self.voiceover(t) as tr:
            self.play(FadeIn(fair_g), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeIn(rain, shift=DOWN * 0.2), run_time=0.7)
            self.play(FadeIn(q, scale=0.8), run_time=0.6)
        self.clear_all()


SCENES = ["S13Definitions", "S13Die", "S13EvenOdd", "S13HandsOn"]
