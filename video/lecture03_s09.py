"""Lecture 3, section 9 — categorical and multinomial: more than two answers, the cup sizes.

Every number on screen comes from N (capture_l03.py, unit-tested by test_l03.py):
cups, cup_customers, cups_expected, cup_hands_on, cups_expected_hands_on. The softmax panel's bar
heights reuse the cup shares and carry no numbers (labelled as an illustration).
"""
from lecture03_kit import *
from lecture03_s07 import person
from lecture03_s08 import CUP_KEYS, cup, cup_names, cups_row

SHARES = [N["cups"][k] for k in CUP_KEYS]
CUP_C = (LBLUE, HILITE, RLORANGE)


def share_bars(values, xs, base, height, vmax, fmt, width=0.9, size=34, colors=CUP_C):
    """One bar per cup at the cups' x positions, the value above each."""
    sc = height / vmax
    bars = VGroup(*[Rectangle(width=width, height=max(v * sc, 1e-3), stroke_width=0, fill_color=c, fill_opacity=1)
                    .move_to([x, base + v * sc / 2, 0]) for v, x, c in zip(values, xs, colors)])
    vals = VGroup(*[MathTex(fmt(v), font_size=size).next_to(b, UP, buff=0.12) for v, b in zip(values, bars)])
    return bars, vals


class S09Cups(LectureScene):
    def construct(self):
        self.section_card(9)
        row = cups_row(1.1).move_to(LEFT * 3.4 + DOWN * 0.2)
        shares = VGroup(*[MathTex(dec(p), font_size=40, color=c).next_to(cu, UP, buff=0.3)
                          for p, cu, c in zip(SHARES, row[0], CUP_C)])
        total = MathTex(rf"{' + '.join(dec(p) for p in SHARES)} = {dec(sum(SHARES))}", font_size=40)
        total.next_to(row, DOWN, buff=0.6)
        with self.say("9.1") as (tr, t):
            self.play(FadeIn(row[0], shift=UP * 0.2), FadeIn(row[1]), run_time=0.8)
            self.cue(tr, t, {"en": "small, zero point two", "uz": "kichik —"})
            self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.15) for s in shares], lag_ratio=0.5), run_time=1.6)
            self.cue(tr, t, {"en": "They add up", "uz": "Yigʻindi bir"})
            self.play(Write(total), run_time=0.7)

        base = -2.0
        bars, _ = share_bars(SHARES, [2.2, 3.6, 5.0], base, 3.0, max(SHARES), dec, width=1.0)
        cats = VGroup(*[txt(nm, size=22, color=GREY_B).next_to([b.get_x(), base, 0], DOWN, buff=0.15)
                        for nm, b in zip(cup_names(), bars)])
        floor = Line([1.4, base, 0], [5.8, base, 0], color=GREY_B, stroke_width=2)
        cat_name = txt(label("dist_categorical"), size=32, weight=BOLD, color=HILITE).next_to(floor, UP, buff=3.6)
        bern_like = VGroup(txt(label("dist_bernoulli"), size=24, color=GREY_B), MathTex("+", font_size=36, color=GREY_B),
                           txt(label("more_answers"), size=24, color=GREY_B)).arrange(RIGHT, buff=0.15)
        bern_like.next_to(cat_name, DOWN, buff=0.2)
        with self.say("9.2") as (tr, t):
            self.play(Create(floor), *[GrowFromEdge(b, DOWN) for b in bars], FadeIn(cats), run_time=1.0)
            self.play(FadeIn(cat_name), FadeIn(bern_like), run_time=0.7)
        self.clear_all()

        # ten customers: how many of each. Left column: the name and the rule; right: the counts
        n = N["cup_customers"]
        crowd = VGroup(*[person(GREY_B, 0.6) for _ in range(n)]).arrange(RIGHT, buff=0.2).to_edge(UP, buff=SAFE + 0.4)
        nlab = MathTex(f"n = {n}", font_size=38, color=GREY_B).next_to(crowd, DOWN, buff=0.25)
        multi = txt(label("dist_multinomial"), size=34, weight=BOLD, color=HILITE).move_to([-3.4, 0.9, 0])
        rule_w = VGroup(txt(label("dist_binomial"), size=24, color=GREY_B), MathTex("+", font_size=36, color=GREY_B),
                        txt(label("more_answers"), size=24, color=GREY_B)).arrange(RIGHT, buff=0.15)
        rule_w.next_to(multi, DOWN, buff=0.3)
        rule = MathTex(r"E[X_i] = n\,p_i", font_size=52).next_to(rule_w, DOWN, buff=0.5)
        with self.say("9.3") as (tr, t):
            self.play(LaggedStart(*[FadeIn(p_, shift=DOWN * 0.2) for p_ in crowd], lag_ratio=0.06), FadeIn(nlab),
                      run_time=1.0)
            self.play(FadeIn(multi), run_time=0.5)
            self.cue(tr, t, {"en": "a binomial with more", "uz": "javoblari ikkitadan koʻp binomial"})
            self.play(FadeIn(rule_w), run_time=0.5)
            self.cue(tr, t, {"en": "The expected counts", "uz": "Kutilayotgan sonlar"})
            self.play(Write(rule), run_time=0.8)

        exp = [N["cups_expected"][k] for k in CUP_KEYS]
        cups = cups_row(0.8).move_to([2.9, -2.1, 0])       # clear of the brand mark, bottom right
        xs = [c.get_x() for c in cups[0]]
        ebars, evals = share_bars(exp, xs, cups[0].get_top()[1] + 0.2, 2.3, max(exp), dec, width=0.8, size=36)
        differ = txt(label("every_morning_differs"), size=26, color=GREY_B).next_to(rule, DOWN, buff=0.7)
        with self.say("9.4") as (tr, t):
            self.play(FadeIn(cups), run_time=0.5)
            self.play(*[GrowFromEdge(b, DOWN) for b in ebars], FadeIn(evals), run_time=1.0)
            self.cue(tr, t, {"en": "But any single morning", "uz": "Lekin har bir"})
            self.play(FadeIn(differ, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S09Softmax(LectureScene):
    def construct(self):
        net = VGroup()
        layers = [3, 4, 4]
        cols = []
        for j, k in enumerate(layers):
            col = VGroup(*[Circle(radius=0.16, stroke_color=GREY_B, stroke_width=2.5) for _ in range(k)])
            col.arrange(DOWN, buff=0.35).move_to([-5.6 + 1.2 * j, 0.2, 0])
            cols.append(col)
            net.add(col)
        edges = VGroup(*[Line(a.get_center(), b.get_center(), stroke_width=1, color=GREY_D).set_z_index(-1)
                         for c1, c2 in zip(cols, cols[1:]) for a in c1 for b in c2])
        out = VGroup(*[Circle(radius=0.16, stroke_color=HILITE, stroke_width=3) for _ in SHARES]).arrange(DOWN, buff=0.5)
        out.move_to([-1.6, 0.2, 0])
        edges.add(*[Line(a.get_center(), b.get_center(), stroke_width=1, color=GREY_D).set_z_index(-1)
                    for a in cols[-1] for b in out])
        out_l = txt(label("output_layer"), size=24, color=HILITE).next_to(out, DOWN, buff=0.5)
        sm = RoundedRectangle(corner_radius=0.12, width=2.0, height=0.9, stroke_color=LBLUE, stroke_width=3)
        sm_t = txt(label("softmax"), size=26, color=LBLUE).move_to(sm)
        smg = VGroup(sm, sm_t).move_to([0.9, 0.2, 0])
        a1 = Arrow(out.get_right(), smg.get_left(), buff=0.2, color=GREY_B)
        base = -1.6
        xs = [3.3, 4.5, 5.7]
        bars, _ = share_bars(SHARES, xs, base, 3.0, max(SHARES), dec, width=0.8)
        floor = Line([2.7, base, 0], [6.3, base, 0], color=GREY_B, stroke_width=2)
        a2 = Arrow(smg.get_right(), [2.6, 0.2, 0], buff=0.15, color=GREY_B)
        cls = txt(label("classes"), size=24, color=GREY_B).next_to(floor, DOWN, buff=0.2)
        one = MathTex(r"\sum = 1", font_size=44, color=HILITE).next_to(VGroup(bars, floor), UP, buff=0.3)
        cat = txt(label("dist_categorical"), size=30, weight=BOLD, color=HILITE).next_to(cls, DOWN, buff=0.35)
        note = info(label("illustration"))
        with self.say("9.5") as (tr, t):
            self.play(Create(edges), FadeIn(net), FadeIn(out), FadeIn(out_l), FadeIn(note), run_time=1.2)
            self.play(Create(floor), *[GrowFromEdge(b, DOWN) for b in bars], FadeIn(cls), run_time=0.8)
            self.cue(tr, t, {"en": "and they add up", "uz": "ularning yigʻindisi"})
            self.play(Write(one), run_time=0.6)
            self.cue(tr, t, {"en": "That is the softmax", "uz": "Bu softmaks"})
            self.play(GrowArrow(a1), FadeIn(smg), GrowArrow(a2), run_time=0.8)
            self.cue(tr, t, {"en": "a categorical distribution", "uz": "kategorial taqsimot"})
            self.play(FadeIn(cat, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S09HandsOn(LectureScene):
    def construct(self):
        n = N["cup_hands_on"]
        card = pause_card([f"n = {n}",
                           "   ".join(f"{nm}: ?" for nm in cup_names())])
        card.to_edge(UP, buff=SAFE + 0.4)
        row = cups_row(0.9).move_to(DOWN * 1.7)
        sh = VGroup(*[MathTex(dec(p), font_size=34, color=c).next_to(cu, UP, buff=0.2)
                      for p, cu, c in zip(SHARES, row[0], CUP_C)])
        with self.say("9.6"):
            self.play(FadeIn(card), FadeIn(row), FadeIn(sh), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), FadeOut(sh), run_time=0.4)

        exp = [N["cups_expected_hands_on"][k] for k in CUP_KEYS]
        calc = MathTex(*[rf"{n} \times {dec(p)} = {dec(e)}" + (r",\quad" if i < 2 else "")
                         for i, (p, e) in enumerate(zip(SHARES, exp))], font_size=40)
        calc.to_edge(UP, buff=SAFE + 0.5)
        xs = [c.get_x() for c in row[0]]
        ebars, evals = share_bars(exp, xs, row[0].get_top()[1] + 0.25, 2.4, max(exp), dec, width=0.9, size=40)
        with self.say("9.7"):
            self.play(Write(calc), *[GrowFromEdge(b, DOWN) for b in ebars], FadeIn(evals), run_time=1.0)
        self.wait(0.6)                                 # the short answer line: let the bars stay a moment
        self.clear_all()

        door = Rectangle(width=1.6, height=2.8, stroke_color=GREY_B, stroke_width=4).move_to(RIGHT * 1.5 + DOWN * 0.2)
        knob = Dot(door.get_right() + LEFT * 0.25, radius=0.07, color=GREY_B)
        crowd = VGroup(*[person(GREY_B, 0.7) for _ in range(4)]).arrange(RIGHT, buff=0.35)
        crowd.next_to(door, LEFT, buff=0.8).align_to(door, DOWN)
        q = txt("?", size=72, weight=BOLD, color=HILITE).next_to(door, RIGHT, buff=0.6)
        with self.say("9.8") as (tr, t):
            self.play(FadeIn(door), FadeIn(knob), run_time=0.5)
            self.cue(tr, t, {"en": "What about", "uz": "Eshikdan"})
            self.play(LaggedStart(*[FadeIn(p_, shift=RIGHT * 0.3) for p_ in crowd], lag_ratio=0.2),
                      FadeIn(q, scale=0.6), run_time=1.0)
        self.clear_all()


SCENES = ["S09Cups", "S09Softmax", "S09HandsOn"]
