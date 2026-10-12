"""Lecture 2, section 3 — two socks from the drawer: drawing without replacement.

Every number on screen comes from N["socks"] (capture_l02.py, unit-tested by test_l02.py):
black, white, total, p_second_black_given, both_black_unreduced, both_black, with_replacement,
both_white_unreduced, pair_unreduced, pair.
"""
from lecture02_kit import *

S = N["socks"]
B, W, T = S["black"], S["white"], S["total"]
# the second-draw fractions are the counts left in the drawer; check them against the tested products
assert [B * (B - 1), T * (T - 1)] == S["both_black_unreduced"] and S["p_second_black_given"] == [B - 1, T - 1]
assert [W * (W - 1), T * (T - 1)] == S["both_white_unreduced"]
LAYOUT = "BWBBWBBWBW"                     # six black, four white, mixed as in a real drawer
assert LAYOUT.count("B") == B and LAYOUT.count("W") == W


def sock(black, scale=1.0):
    pts = [(0, 0), (0.32, 0), (0.32, -0.58), (0.58, -0.58), (0.66, -0.68), (0.64, -0.82), (0.56, -0.88),
           (0.06, -0.88), (0, -0.82)]
    body = Polygon(*[[x, y, 0] for x, y in pts], stroke_width=2.5,
                   stroke_color=GREY_A if black else GREY_B, fill_color="#262626" if black else WHITE,
                   fill_opacity=1).round_corners(0.05)
    cuff = Line([0.02, -0.12, 0], [0.30, -0.12, 0], stroke_width=2, color=GREY_B if black else GREY_C)
    return VGroup(body, cuff).scale(scale)


def drawer(width=6.6, height=2.0):
    return VMobject(stroke_color=GREY_B, stroke_width=4).set_points_as_corners(
        [[-width / 2, height / 2, 0], [-width / 2, -height / 2, 0], [width / 2, -height / 2, 0], [width / 2, height / 2, 0]])


def fr(a, b, size=50, color=WHITE):
    return MathTex(rf"\frac{{{a}}}{{{b}}}", font_size=size, color=color)


def drawer_with_socks(center=(-3.0, -0.6, 0), scale=1.0):
    d = drawer().scale(scale).move_to(center)
    socks = VGroup(*[sock(c == "B", 0.85 * scale) for c in LAYOUT]).arrange(RIGHT, buff=0.08 * scale)
    socks.move_to(d).shift(DOWN * 0.1 * scale)
    return d, socks


class S03Socks(LectureScene):
    def construct(self):
        self.section_card(3)
        d, socks = drawer_with_socks()
        q = txt(label("p_both_black_q"), size=36, weight=BOLD, color=HILITE).move_to([3.6, 3.0, 0])
        with self.say("3.1") as (tr, t):
            self.play(Create(d), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.3) for s in socks], lag_ratio=0.08), run_time=1.2)
            self.cue(tr, t, {"en": "What is the chance", "uz": "Ikkalasi ham qora"})
            self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.6)

        first = socks[0]
        r1 = VGroup(txt(label("1st_black"), size=28, color=GREY_B), fr(B, T)).arrange(RIGHT, buff=0.4)
        r1.move_to([3.6, 1.85, 0])
        with self.say("3.2") as (tr, t):
            self.play(first.animate.move_to([-3.0, 1.9, 0]), run_time=0.8)
            self.play(FadeIn(r1), run_time=0.5)

        rest = socks[1:]
        r2 = VGroup(txt(label("2nd_black_1st_black"), size=28, color=GREY_B),
                    fr(B - 1, T - 1)).arrange(RIGHT, buff=0.4)
        r2.next_to(r1, DOWN, buff=0.3).align_to(r1, RIGHT)
        with self.say("3.3") as (tr, t):
            self.play(first.animate.move_to([-6.0, 1.9, 0]).set_opacity(0.35), rest.animate.arrange(RIGHT, buff=0.15).move_to(d).shift(DOWN * 0.1),
                      run_time=0.9)
            self.cue(tr, t, {"en": "Nine socks", "uz": "Toʻqqizta paypoq"})
            self.play(Indicate(VGroup(*[s for s, c in zip(rest, LAYOUT[1:]) if c == "B"]), color=GREY_A,
                               scale_factor=1.12), run_time=0.9)
            self.cue(tr, t, {"en": "So the chance", "uz": "Demak"})
            self.play(FadeIn(r2), run_time=0.6)

        bb, bbu = S["both_black"], S["both_black_unreduced"]
        prod = MathTex(rf"\frac{{{B}}}{{{T}}} \times \frac{{{B - 1}}}{{{T - 1}}}", "=", rf"\frac{{{bbu[0]}}}{{{bbu[1]}}}",
                       "=", rf"\frac{{{bb[0]}}}{{{bb[1]}}}", font_size=48).next_to(r2, DOWN, buff=0.4).set_x(3.3)
        prod[4].set_color(HILITE)
        with self.say("3.4") as (tr, t):
            self.play(Write(prod[:3]), run_time=1.2)
            self.cue(tr, t, {"en": "one third", "uz": "uchdan bir"})
            self.play(Write(prod[3:]), run_time=0.7)

        back = VGroup(txt(label("put_back"), size=28, color=LBLUE),
                      MathTex(rf"\frac{{{B}}}{{{T}}} \times \frac{{{B}}}{{{T}}} = {dec(S['with_replacement'])}",
                              font_size=48, color=LBLUE)).arrange(RIGHT, buff=0.4)
        back.next_to(prod, DOWN, buff=0.35).set_x(3.3)
        with self.say("3.5") as (tr, t):
            self.play(first.animate.move_to(socks[0].get_center()).set_opacity(1), run_time=0.6)
            self.play(first.animate.move_to(d.get_center() + LEFT * 3.0 + DOWN * 0.1),
                      rest.animate.arrange(RIGHT, buff=0.08).move_to(d).shift(DOWN * 0.1 + RIGHT * 0.34), run_time=0.8)
            self.cue(tr, t, {"en": "six tenths times", "uz": "oʻndan oltini oʻndan"})
            self.play(FadeIn(back, shift=UP * 0.2), run_time=0.8)
        self.clear_all()

        left = VGroup(txt(label("without_replacement"), size=32, weight=BOLD, color=HILITE),
                      MathTex(rf"\frac{{{bb[0]}}}{{{bb[1]}}}", font_size=80, color=HILITE)).arrange(DOWN, buff=0.4)
        right = VGroup(txt(label("with_replacement"), size=32, weight=BOLD, color=LBLUE),
                       MathTex(dec(S["with_replacement"]), font_size=80, color=LBLUE)).arrange(DOWN, buff=0.4)
        VGroup(left, right).arrange(RIGHT, buff=2.6).move_to(UP * 0.4)
        neq = MathTex(r"\neq", font_size=80).move_to((left[1].get_center() + right[1].get_center()) / 2)
        dep = txt(label("the_2nd_draw_depends_on_the"), size=30, color=GREY_B)
        dep.move_to(DOWN * 2.2)
        with self.say("3.6") as (tr, t):
            self.play(FadeIn(left, shift=RIGHT * 0.3), run_time=0.7)
            self.play(FadeIn(dep), run_time=0.5)
            self.cue(tr, t, 1)
            self.play(FadeIn(right, shift=LEFT * 0.3), Write(neq), run_time=0.9)
        self.clear_all()


class S03Split(LectureScene):
    def construct(self):
        rows = VGroup(*[RoundedRectangle(corner_radius=0.06, width=0.5, height=0.5, stroke_width=0,
                                         fill_color=LBLUE, fill_opacity=0.9) for _ in range(12)])
        rows.arrange(RIGHT, buff=0.15).move_to(UP * 1.9)
        data_lab = txt(label("dataset"), size=28, color=GREY_B).next_to(rows, UP, buff=0.25)
        train = RoundedRectangle(corner_radius=0.15, width=5.4, height=1.6, stroke_color=RLGREEN, stroke_width=3).move_to([-3.0, -1.3, 0])
        test = RoundedRectangle(corner_radius=0.15, width=3.2, height=1.6, stroke_color=HILITE, stroke_width=3).move_to([3.4, -1.3, 0])
        tl = txt(label("training"), size=28, weight=BOLD, color=RLGREEN).next_to(train, DOWN, buff=0.2)
        el = txt(label("test"), size=28, weight=BOLD, color=HILITE).next_to(test, DOWN, buff=0.2)
        to_test = {2, 6, 9, 11}
        tr_slots = [train.get_left() + RIGHT * (0.5 + 0.6 * k) for k in range(8)]
        te_slots = [test.get_left() + RIGHT * (0.5 + 0.6 * k) + UP * 0 for k in range(4)]
        moves, a, b = [], 0, 0
        for i, r in enumerate(rows):
            if i in to_test:
                moves.append(r.animate.move_to(te_slots[b]).set_fill(HILITE)); b += 1
            else:
                moves.append(r.animate.move_to(tr_slots[a]).set_fill(RLGREEN)); a += 1
        once = txt(label("each_example_goes_to_one_part"), size=26,
                   color=GREY_B).move_to(DOWN * 3.15)
        with self.say("3.7") as (tr, t):
            self.play(FadeIn(data_lab), LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.05), run_time=0.9)
            self.play(Create(train), Create(test), FadeIn(tl), FadeIn(el), run_time=0.7)
            self.cue(tr, t, {"en": "we also draw", "uz": "misollarni qaytarmasdan"})
            self.play(LaggedStart(*moves, lag_ratio=0.12), run_time=2.0)
            self.cue(tr, t, {"en": "no example", "uz": "bitta misol"})
            self.play(FadeIn(once), run_time=0.6)
        self.clear_all()


class S03HandsOn(LectureScene):
    def construct(self):
        d, socks = drawer_with_socks(center=(3.4, -0.4, 0), scale=0.62)
        pc = pause_card([label("both_white_q"),
                         label("a_matching_pair_both_black_or_q")])
        pc.move_to([-2.6, 0.4, 0])
        if pc.width > 7.2:
            pc.scale_to_fit_width(7.2).move_to([-2.6, 0.4, 0])
        with self.say("3.8") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(pc, shift=UP * 0.2), Create(d), FadeIn(socks), run_time=0.9)
        self.hands_on()

        wwu, bbu, pu = S["both_white_unreduced"], S["both_black_unreduced"], S["pair_unreduced"]
        white = MathTex(rf"\frac{{{W}}}{{{T}}} \times \frac{{{W - 1}}}{{{T - 1}}}", "=", rf"\frac{{{wwu[0]}}}{{{wwu[1]}}}",
                        font_size=50).move_to([-2.6, 1.2, 0])
        lab_w = txt(label("both_white"), size=28, color=GREY_B).next_to(white, LEFT, buff=0.4)
        pair = MathTex(rf"\frac{{{bbu[0]}}}{{{bbu[1]}}} + \frac{{{wwu[0]}}}{{{wwu[1]}}}", "=",
                       rf"\frac{{{pu[0]}}}{{{pu[1]}}}", r"\approx", dec(round(S["pair"], 2)), font_size=50).move_to([-2.0, -0.6, 0])
        pair[4].set_color(HILITE)
        lab_p = txt(label("pair"), size=28, color=GREY_B).next_to(pair, LEFT, buff=0.4)
        half = txt(label("less_than_half"), size=32, weight=BOLD, color=HILITE).move_to([-2.0, -2.2, 0])
        with self.say("3.9") as (tr, t):
            self.play(FadeOut(pc), run_time=0.4)
            self.play(FadeIn(lab_w), Write(white), run_time=1.1)
            self.cue(tr, t, {"en": "A pair", "uz": "Juft esa"})
            self.play(FadeIn(lab_p), Write(pair[:3]), run_time=1.1)
            self.cue(tr, t, {"en": "about zero point", "uz": "taxminan"})
            self.play(Write(pair[3:]), run_time=0.6)
            self.cue(tr, t, {"en": "Less than half", "uz": "Bu yarimdan"})
            self.play(FadeIn(half, scale=1.2), run_time=0.6)
        self.clear_all()

        tb = bike_bus_table(size=30)
        tb["grid"].move_to(DOWN * 0.2)
        with self.say("3.10") as (tr, t):
            self.cue(tr, t, {"en": "To see two", "uz": "Ikki xususiyatni"})
            self.play(FadeIn(tb["grid"], shift=UP * 0.2), run_time=0.9)
        self.clear_all()


SCENES = ["S03Socks", "S03Split", "S03HandsOn"]
