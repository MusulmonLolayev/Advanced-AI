"""Lecture 1, section 11 — the three rules: complement, addition, multiplication.

Card counts and probabilities come from statistics/raw/l01_numbers.json (capture_l01.py).
"""
from fractions import Fraction

from lecture01_kit import *

C = L["cards"]
assert (C["hearts"], C["kings"], C["both"], C["union"], L["neither"]) == (13, 4, 1, 16, 36)
assert (L["p_king_given_heart"], L["p_king_of_hearts"], L["p_even"]) == ("1/13", "1/52", "1/2")

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = [("♥", RLRED), ("♦", RLRED), ("♣", WHITE), ("♠", WHITE)]
HEARTS, KING = 0, RANKS.index("K")
CW, CH, DX, DY = 0.74, 0.92, 0.86, 1.08
LB = interpolate_color(ManimColor(RLBLUE), WHITE, 0.4)   # course blue, lifted for text on black


def chip(label, color=RLBLUE, size=28, pad=0.25):
    """A label in a rounded box, the font size fixed (box() rescales text to its width)."""
    t = txt(label, size=size)
    r = RoundedRectangle(corner_radius=0.12, width=t.width + 2 * pad, height=t.height + 2 * pad,
                         stroke_color=color, stroke_width=3)
    return VGroup(r, t.move_to(r))


def deck(y=-0.55):
    """The 52 cards: one row per suit, one column per rank."""
    cards = VGroup()
    for r, (suit, col) in enumerate(SUITS):
        for c, rank in enumerate(RANKS):
            rect = RoundedRectangle(corner_radius=0.07, width=CW, height=CH, stroke_color=GREY_B, stroke_width=1.5,
                                    fill_color=BLACK, fill_opacity=1)
            lab = VGroup(txt(rank, size=20, color=col, weight=BOLD), txt(suit, size=22, color=col))
            lab.arrange(DOWN, buff=0.04).move_to(rect)
            cards.add(VGroup(rect, lab).move_to([(c - 6) * DX, y + (1.5 - r) * DY, 0]))
    return cards


def at_card(cards, r, c):
    return cards[r * 13 + c]


def light(cards, idx, color, opacity=0.4):
    return [cards[i][0].animate.set_fill(color, opacity=opacity).set_stroke(color, width=2.5) for i in idx]


HEART_IDX = [HEARTS * 13 + c for c in range(13)]
KING_IDX = [r * 13 + KING for r in range(4)]
UNION_IDX = sorted(set(HEART_IDX) | set(KING_IDX))
assert len(HEART_IDX) == C["hearts"] and len(KING_IDX) == C["kings"] and len(UNION_IDX) == C["union"]


class S11Complement(LectureScene):
    def construct(self):
        self.section_card(11)
        names = [label("complement"), label("addition"), label("multiplication")]
        slots = VGroup(*[chip(f"{k}. {n}", size=30) for k, n in enumerate(names, 1)])
        slots.arrange(RIGHT, buff=0.35).move_to(UP * 0.3)
        with self.say("11.1") as (tr, t):
            self.cue(tr, t, 2)
            self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in slots], lag_ratio=0.3), run_time=1.4)
        top = slots.copy().scale(0.62).to_edge(UP, buff=SAFE + 0.15)
        self.play(Transform(slots, top), run_time=0.6)

        faces = {n: die_face(n, size=0.85) for n in range(1, 7)}
        evens = VGroup(*[faces[n] for n in (2, 4, 6)]).arrange(RIGHT, buff=0.3)
        odds = VGroup(*[faces[n] for n in (1, 3, 5)]).arrange(RIGHT, buff=0.3)
        VGroup(evens, odds).arrange(RIGHT, buff=1.2).move_to(UP * 0.7)
        om = RoundedRectangle(corner_radius=0.3, width=9.4, height=2.5, stroke_color=GREY_B, stroke_width=3)
        om.move_to(UP * 0.7)
        om_lab = MathTex(r"\Omega", font_size=48, color=GREY_B).next_to(om, LEFT, buff=0.25)
        VGroup(evens, odds).shift(UP * 0.2)
        a_box = SurroundingRectangle(evens, buff=0.2, corner_radius=0.15, color=RLBLUE, fill_color=RLBLUE,
                                     fill_opacity=0.3, stroke_width=3)
        c_box = SurroundingRectangle(odds, buff=0.2, corner_radius=0.15, color=HILITE, fill_color=HILITE,
                                     fill_opacity=0.3, stroke_width=3)
        a_lab = MathTex("A", font_size=40, color=LB).next_to(a_box, DOWN, buff=0.15)
        c_lab = MathTex("A^{c}", font_size=40, color=HILITE).next_to(c_box, DOWN, buff=0.15)
        eq = MathTex(r"P(A^{c})", "=", "1 - P(A)", "=", r"1 - \tfrac{1}{2}", "=", r"\tfrac{1}{2}", font_size=44)
        eq.move_to(DOWN * 2.1)
        eq[0].set_color(HILITE)
        with self.say("11.2") as (tr, t):
            self.play(Indicate(slots[0], color=HILITE), Create(om), FadeIn(om_lab),
                      LaggedStart(*[FadeIn(f) for n, f in sorted(faces.items())], lag_ratio=0.1), run_time=1.2)
            self.play(FadeIn(a_box), FadeIn(a_lab), FadeIn(c_box), FadeIn(c_lab), run_time=0.7)
            self.cue(tr, t, 1)
            self.play(Write(eq[:3]), run_time=1.0)
            self.cue(tr, t, 2)
            self.play(Write(eq[3:]), run_time=1.2)

        # Text, not \text{}: LaTeX here cannot set the Uzbek ʻ
        rule = VGroup(txt(f"P({label("at_least_one")})", size=34), MathTex("=", font_size=42),
                      txt(f"1 − P({label("none")})", size=34)).arrange(RIGHT, buff=0.3)
        rule.move_to(DOWN * 2.1)
        rule[2].set_color(HILITE)
        with self.say("11.3") as (tr, t):
            self.play(FadeOut(eq), FadeIn(rule[0]), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeIn(rule[1:]), run_time=0.8)
            self.play(Indicate(rule[2], color=HILITE), run_time=0.9)
        self.clear_all()


class S11Addition(LectureScene):
    def construct(self):
        cards = deck()
        head = txt(label("2_addition"), size=30, weight=BOLD, color=LB).to_corner(UL, buff=SAFE + 0.15)
        p_h = MathTex(r"P(\heartsuit) = \tfrac{13}{52}", font_size=38, color=RLRED).move_to([0.2, 3.2, 0])
        p_k = MathTex(r"P(K) = \tfrac{4}{52}", font_size=38, color=HILITE).move_to([4.2, 3.2, 0])
        with self.say("11.4") as (tr, t):
            self.play(FadeIn(head), LaggedStart(*[FadeIn(c) for c in cards], lag_ratio=0.01), run_time=1.4)
            self.cue(tr, t, {"en": "A heart", "uz": "Yurak belgili"})
            self.play(*light(cards, HEART_IDX, RLRED), FadeIn(p_h), run_time=0.9)
            self.cue(tr, t, {"en": "A king", "uz": "Qirol chiqishi"})
            self.play(*light(cards, KING_IDX, HILITE), FadeIn(p_k), run_time=0.9)

        koh = at_card(cards, HEARTS, KING)
        wrong = MathTex(r"\tfrac{13}{52} + \tfrac{4}{52}", r"\;?", font_size=40).move_to([0, 2.35, 0])
        with self.say("11.5") as (tr, t):
            self.play(FadeIn(wrong), run_time=0.7)
            self.cue(tr, t, 2)
            self.play(koh[0].animate.set_fill(RLGREEN, opacity=0.9), run_time=0.4)
            self.play(Indicate(koh, color=RLGREEN, scale_factor=1.6), run_time=1.0)
            self.play(Indicate(koh, color=RLGREEN, scale_factor=1.6), run_time=1.0)

        # 11.5a: the same double count as two overlapping circles
        cards.save_state()
        ch = Circle(radius=1.55, color=RLRED, stroke_width=5).set_fill(RLRED, 0.18).move_to([-0.95, -0.55, 0])
        ck = Circle(radius=1.55, color=HILITE, stroke_width=5).set_fill(HILITE, 0.18).move_to([0.95, -0.55, 0])
        both = Intersection(ch, ck, stroke_width=0, fill_color=RLGREEN, fill_opacity=0.85)
        n_h = MathTex(rf"\heartsuit:\ {C['hearts']}", font_size=38, color=RLRED).move_to([-1.55, -0.55, 0])
        n_k = MathTex(rf"K:\ {C['kings']}", font_size=38, color=HILITE).move_to([1.6, -0.55, 0])
        n_b = MathTex(str(C["both"]), font_size=40, color=BLACK).move_to(both)
        with self.say("11.5a") as (tr, t):
            self.play(cards.animate.set_opacity(0.12), run_time=0.5)
            self.play(Create(ch), Create(ck), FadeIn(n_h), FadeIn(n_k), run_time=0.9)
            self.cue(tr, t, 1)
            self.play(FadeIn(both), FadeIn(n_b), run_time=0.5)
            for _ in range(2):          # counted once with the hearts, once with the kings
                self.play(Indicate(VGroup(both, n_b), color=RLGREEN, scale_factor=1.15), run_time=0.7)
        self.play(FadeOut(VGroup(ch, ck, both, n_h, n_k, n_b)), Restore(cards), run_time=0.6)

        a, b = C["union"], 52
        right = MathTex(r"P(\heartsuit \cup K)", "=", r"\tfrac{13 + 4 - 1}{52}", "=", rf"\tfrac{{{a}}}{{{b}}}",
                        font_size=42).move_to([0, 3.2, 0])
        right[4].set_color(HILITE)
        with self.say("11.6") as (tr, t):
            self.play(FadeOut(wrong), FadeOut(p_h), FadeOut(p_k), run_time=0.5)
            self.play(Write(right[:3]), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(Write(right[3:]), *[Indicate(cards[i], color=HILITE, scale_factor=1.12) for i in UNION_IDX],
                      run_time=1.4)
        self.clear_all()


class S11Multiply(LectureScene):
    def construct(self):
        cards = deck(y=-0.85)
        head = txt(label("3_multiplication"), size=30, weight=BOLD, color=LB)
        head.to_corner(UL, buff=SAFE + 0.15)
        rule = MathTex(r"P(A \cap B)", "=", "P(A)", r"\cdot", r"P(B \mid A)", font_size=46).move_to([1.2, 3.1, 0])
        with self.say("11.7") as (tr, t):
            self.play(FadeIn(head), LaggedStart(*[FadeIn(c) for c in cards], lag_ratio=0.01), run_time=1.2)
            self.cue(tr, t, 1)
            self.play(Write(rule), run_time=1.6)

        a, b = L["p_king_of_hearts"].split("/")
        calc = MathTex(r"\tfrac{13}{52}", r"\cdot", r"\tfrac{1}{13}", "=", rf"\tfrac{{{a}}}{{{b}}}", font_size=46)
        calc.next_to(rule, DOWN, buff=0.3)
        calc[0].set_color(RLRED)
        calc[2].set_color(HILITE)
        calc[4].set_color(RLGREEN)
        others = [i for i in range(52) if i not in HEART_IDX]
        koh = at_card(cards, HEARTS, KING)
        with self.say("11.8") as (tr, t):
            self.cue(tr, t, {"en": "first a heart", "uz": "Avval"})
            self.play(*light(cards, HEART_IDX, RLRED), FadeIn(calc[0]), run_time=0.9)
            self.cue(tr, t, {"en": "Given", "uz": "Yurak chiqqanini"})
            self.play(*[cards[i].animate.set_opacity(0.2) for i in others], run_time=0.7)
            self.play(koh[0].animate.set_fill(HILITE, opacity=0.9), FadeIn(calc[1:3]), run_time=0.8)
            self.cue(tr, t, {"en": "Multiply", "uz": "Koʻpaytirsak"})
            self.play(FadeIn(calc[3:]), koh[0].animate.set_fill(RLGREEN, opacity=0.9), run_time=0.9)

        cond = txt(label("conditional_probability_lecture_2"), size=28, color=HILITE)
        cond.move_to([1.2, 1.55, 0])
        hl = SurroundingRectangle(rule[4], color=HILITE, buff=0.1)
        with self.say("11.9") as (tr, t):
            self.play(FadeOut(calc), Create(hl), run_time=0.7)
            self.play(FadeIn(cond, shift=UP * 0.15), run_time=0.7)
        self.play(FadeOut(cards), FadeOut(cond), FadeOut(hl), FadeOut(rule), FadeOut(head), run_time=0.6)

        # 11.9a: complement and multiplication together: at least one six in four rolls
        rolls = VGroup(*[die_face(6, size=0.95) for _ in range(4)]).arrange(RIGHT, buff=0.9).move_to([0, 0.95, 0])
        crosses = VGroup(*[Cross(f, stroke_color=RLRED, stroke_width=5, scale_factor=0.9) for f in rolls])
        each = VGroup(*[MathTex(r"\tfrac{5}{6}", font_size=40).next_to(f, DOWN, buff=0.35) for f in rolls])
        not6 = txt(label("not_a_six"), size=24, color=GREY_B).next_to(each, LEFT, buff=0.5)
        n4 = tagged(len(rolls), label("times_rolled"), size=28, color=GREY_B).next_to(rolls, UP, buff=0.35)
        none = VGroup(txt(f"P({label('none')})", size=34), MathTex(
            rf"= \left(\tfrac{{5}}{{6}}\right)^{{4}} \approx {L['no_six_4']:.2f}", font_size=44))
        none.arrange(RIGHT, buff=0.2).move_to([0, -1.45, 0])
        least = VGroup(txt(f"P({label('at_least_one')})", size=34, color=HILITE), MathTex(
            rf"= 1 - {L['no_six_4']:.2f} \approx {L['at_least_one_six_4']:.2f}", font_size=44, color=HILITE))
        least.arrange(RIGHT, buff=0.2).next_to(none, DOWN, buff=0.45)
        rules = VGroup(chip(f"1. {label('complement')}", size=24), chip(f"3. {label('multiplication')}", size=24))
        rules.arrange(RIGHT, buff=0.4).to_edge(UP, buff=SAFE + 0.1)
        with self.say("11.9a") as (tr, t):
            self.play(FadeIn(rules, shift=DOWN * 0.2), run_time=0.6)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(f, scale=0.6) for f in rolls], lag_ratio=0.15), FadeIn(n4), run_time=1.0)
            self.cue(tr, t, {"en": "No six on one", "uz": "Bitta tashlashda"})
            self.play(LaggedStart(*[Create(c) for c in crosses], lag_ratio=0.15), FadeIn(each), FadeIn(not6),
                      run_time=1.2)
            self.cue(tr, t, {"en": "No six in four", "uz": "Toʻrt marta chiqmasligi"})
            self.play(Write(none), run_time=1.0)
            self.cue(tr, t, {"en": "So at least", "uz": "Demak"})
            self.play(Write(least), run_time=1.0)
        self.play(FadeOut(VGroup(rolls, crosses, each, not6, n4, none, least, rules)), run_time=0.5)

        words = [label("the"), label("weather"), label("is"), label("hot")]
        terms = [r"P(w_1)", r"P(w_2 \mid w_1)", r"P(w_3 \mid w_1, w_2)", r"P(w_4 \mid w_1, w_2, w_3)"]
        parts = [r"P(\text{" + label("sentence") + r"}) =", terms[0], r"\cdot", terms[1], r"\cdot", terms[2],
                 r"\cdot", terms[3]]
        row = MathTex(*parts, font_size=34).move_to(DOWN * 0.9)
        row[0].set_color(HILITE)
        fac = VGroup(row[1], row[3], row[5], row[7])
        chips = VGroup(*[chip(s_, size=30) for s_ in words])
        chips.arrange(RIGHT, buff=0.6).move_to([fac.get_center()[0], 1.0, 0])
        arrows = VGroup(*[Arrow(c.get_bottom(), f.get_top(), buff=0.12, color=GREY_B, stroke_width=3,
                                max_tip_length_to_length_ratio=0.25) for c, f in zip(chips, fac)])
        lm = txt(label("language_model"), size=30, weight=BOLD, color=LB).to_edge(UP, buff=SAFE + 0.3)
        dots = VGroup(row[2], row[4], row[6])
        total = row[0]
        with self.say("11.10") as (tr, t):
            self.play(FadeIn(lm), LaggedStart(*[FadeIn(c) for c in chips], lag_ratio=0.15), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(f)) for a, f in zip(arrows, fac)],
                                  lag_ratio=0.5), run_time=2.4)
            self.play(FadeIn(dots), FadeIn(total), run_time=0.7)
        self.clear_all()


class S11HandsOn(LectureScene):
    def construct(self):
        cards = deck(y=-1.1)
        for i in UNION_IDX:
            cards[i][0].set_fill(HILITE, opacity=0.4).set_stroke(HILITE, width=2.5)
        task = pause_card([label("p_neither_a_heart_nor_a_q")])
        task.scale(0.85).to_edge(UP, buff=SAFE + 0.1)
        with self.say("11.11") as (tr, t):
            self.play(LaggedStart(*[FadeIn(c) for c in cards], lag_ratio=0.01), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(FadeIn(task), run_time=0.7)
        self.hands_on()

        rest = [i for i in range(52) if i not in UNION_IDX]
        assert len(rest) == L["neither"]
        eq = MathTex(r"1 - \tfrac{16}{52}", "=", rf"\tfrac{{{L['neither']}}}{{52}}", font_size=48).move_to([0, 2.9, 0])
        eq[2].set_color(RLGREEN)
        with self.say("11.12") as (tr, t):
            self.play(FadeOut(task), Write(eq[0]), run_time=0.9)
            self.cue(tr, t, 1)
            self.play(*light(cards, rest, RLGREEN), Write(eq[1:]), run_time=1.4)
        self.clear_all(run_time=0.5)

        cal = VGroup(*[Square(side_length=0.42, stroke_color=GREY_B, stroke_width=1.5) for _ in range(35)])
        cal.arrange_in_grid(rows=5, cols=7, buff=0.06).move_to(DOWN * 0.3)
        top = Rectangle(width=cal.width, height=0.45, stroke_width=0, fill_color=RLRED, fill_opacity=1)
        top.next_to(cal, UP, buff=0.06)
        hit = [9, 23]
        name = txt(label("birthdays"), size=36, weight=BOLD).next_to(top, UP, buff=0.4)
        with self.say("11.13"):
            self.play(FadeIn(top), LaggedStart(*[FadeIn(s) for s in cal], lag_ratio=0.02), FadeIn(name), run_time=1.2)
            self.play(*[cal[i].animate.set_fill(HILITE, opacity=0.9) for i in hit], run_time=0.7)
        self.clear_all()


SCENES = ["S11Complement", "S11Addition", "S11Multiply", "S11HandsOn"]
