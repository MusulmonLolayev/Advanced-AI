"""Lecture 2, section 7 — the law of total probability.

The hero picture is drawn natively: two bars whose widths are the group sizes (60 and 40 students)
and whose orange fill is each group's bus rate (0.25 and 0.75). The overall rate is the orange
area over the whole width, 0.45, nearer 0.25 because the bike bar is wider. Every number is N's.
"""
from lecture02_kit import *

P_BIKE, P_NOBIKE = N["p_bike"], 1 - N["p_bike"]
R_BIKE, R_NOBIKE = N["p_bus_given_bike"], N["p_bus_given_nobike"]
X0, X1, BASE, H = -6.0, 0.4, -2.5, 3.6        # the bars' floor spans X0..X1; height H means probability 1


def py(p):
    return BASE + p * H


def bars(widths=(0.5, 0.5), fill=True):
    """Two group bars side by side: frame (green, did not take the bus) and orange fill (took it)."""
    g = VGroup()
    x = X0
    for wd, r, lab in zip(widths, (R_BIKE, R_NOBIKE), (BIKE, NOBIKE)):
        W = wd * (X1 - X0)
        frame = Rectangle(width=W - 0.08, height=H, stroke_width=0, fill_color=NOBUS_C, fill_opacity=0.55)
        frame.move_to([x + W / 2, BASE + H / 2, 0])
        orange = Rectangle(width=W - 0.08, height=r * H, stroke_width=0, fill_color=BUS_C, fill_opacity=1)
        orange.move_to([x + W / 2, BASE + r * H / 2, 0])
        rate = MathTex(dec(r), font_size=40, color=WHITE).move_to([x + W / 2, BASE + r * H / 2, 0])
        name = txt(lab, size=26, color=GREY_B).move_to([x + W / 2, BASE - 0.35, 0])
        g.add(VGroup(frame, orange, rate, name))
        x += W
    return g


def margin_table(col, color=HILITE, y=-1.85):
    """The students' table, small, at the right, with one column outlined: the margin we land on."""
    tb = bike_bus_table(size=34, cw=1.9, head_w=2.4, ch=0.7)
    for m in tb["collab"] + tb.get("tothead", []):      # long Uzbek headers must stay inside their column
        if m.width > 1.9 - 0.2:
            m.scale_to_fit_width(1.9 - 0.2)
    rect = tb["col_rect"](col, color=color)
    for m in (tb["grid"], rect):
        m.scale(0.66, about_point=ORIGIN).shift([3.85, y, 0])
    return tb, rect


def floor():
    return Line([X0 - 0.1, BASE, 0], [X1 + 0.1, BASE, 0], color=GREY_B, stroke_width=2)


class S07Groups(LectureScene):
    def construct(self):
        self.section_card(7)
        b = bars()
        fl = floor()
        ask = MathTex(r"P(\text{" + BUS + r"}) = \;?", font_size=48).move_to([3.8, 2.4, 0])
        with self.say("7.1") as (tr, t):
            self.play(Write(ask), Create(fl), run_time=0.8)
            self.cue(tr, t, {"en": "Zero point two five", "uz": "Velosipedi borlarda"})
            self.play(FadeIn(b[0][0]), GrowFromEdge(b[0][1], DOWN), FadeIn(b[0][2]), FadeIn(b[0][3]), run_time=0.9)
            self.cue(tr, t, {"en": "zero point seven five", "uz": "yoʻqlarda"})
            self.play(FadeIn(b[1][0]), GrowFromEdge(b[1][1], DOWN), FadeIn(b[1][2]), FadeIn(b[1][3]), run_time=0.9)

        avg = (R_BIKE + R_NOBIKE) / 2
        assert avg == N["plain_average"]
        half = DashedLine([X0, py(avg), 0], [X1, py(avg), 0], color=WHITE, stroke_width=3)
        half_eq = MathTex(r"\tfrac{" + dec(R_BIKE) + " + " + dec(R_NOBIKE) + "}{2}", "=", dec(N["plain_average"]),
                          font_size=40).move_to([3.8, 0.9, 0])
        cross = Cross(half_eq, stroke_color=BAD, stroke_width=6)
        wide = bars((P_BIKE, P_NOBIKE))
        sizes = VGroup(*[txt(STUDENTS.format(n=k), size=26, color=LBLUE).next_to(wb[3], DOWN, buff=0.12)
                         for k, wb in zip((N["bike"], N["nobike"]), wide)])
        with self.say("7.2") as (tr, t):
            self.play(Create(half), Write(half_eq), run_time=1.0)
            self.cue(tr, t, {"en": "But the groups", "uz": "Lekin guruhlar"})
            self.play(Create(cross), FadeOut(half), run_time=0.6)
            self.play(Transform(b, wide), run_time=1.2)
            self.play(FadeIn(sizes, shift=UP * 0.2), run_time=0.6)

        weighted = MathTex(dec(R_BIKE), r"\times", dec(P_BIKE), "+", dec(R_NOBIKE), r"\times", dec(P_NOBIKE),
                           font_size=44).move_to([3.8, 0.9, 0])
        weighted[0:3].set_color(HILITE)
        weighted[4:7].set_color(RLGREEN)
        with self.say("7.3") as (tr, t):
            self.play(FadeOut(half_eq), FadeOut(cross), run_time=0.4)
            self.play(Write(weighted[0:3]), Indicate(b[0], color=HILITE, scale_factor=1.03), run_time=1.0)
            self.cue(tr, t, {"en": "plus", "uz": "qoʻshuv"})
            self.play(Write(weighted[3:]), Indicate(b[1], color=RLGREEN, scale_factor=1.03), run_time=1.0)

        s1, s2 = N["total_terms"]
        sums = MathTex("=", dec(s1), "+", dec(s2), "=", dec(N["total_bus"]), font_size=44)
        sums.next_to(weighted, DOWN, buff=0.35).align_to(weighted, LEFT)
        sums[5].set_color(HILITE)
        tb, rect = margin_table(0)
        line_45 = DashedLine([X0, py(N["total_bus"]), 0], [X1, py(N["total_bus"]), 0], color=WHITE, stroke_width=3)
        with self.say("7.4") as (tr, t):
            self.play(Write(sums[:5]), run_time=1.0)
            self.play(Write(sums[5]), Create(line_45), run_time=0.8)
            self.cue(tr, t, {"en": "Exactly", "uz": "Aynan"})
            self.play(FadeIn(tb["grid"]), run_time=0.6)
            self.play(Create(rect), Indicate(tb["coltot"][0], color=HILITE, scale_factor=1.4), run_time=0.9)
        self.clear_all()


class S07Formula(LectureScene):
    def construct(self):
        head = self.heading(w("The law of total probability", "Toʻla ehtimollik formulasi"), color=LBLUE)
        f = MathTex(r"P(B)", "=", r"\sum_{i=1}^{k}", r"P(B \mid A_i)", r"\,P(A_i)", font_size=60)
        f.next_to(head, DOWN, buff=0.45)
        # the partition: groups that never overlap and together cover everything
        om = Rectangle(width=7.0, height=3.0, stroke_color=GREY_B, stroke_width=2.5).move_to([0, -1.6, 0])
        cut = om.get_left()[0] + 7.0 * P_BIKE
        div = Line([cut, om.get_top()[1], 0], [cut, om.get_bottom()[1], 0], color=GREY_B, stroke_width=2.5)
        a1 = MathTex("A_1", font_size=40, color=LBLUE).move_to([om.get_left()[0] + 0.45, om.get_top()[1] - 0.4, 0])
        a2 = MathTex("A_2", font_size=40, color=LBLUE).move_to([cut + 0.45, om.get_top()[1] - 0.4, 0])
        n1 = txt(BIKE, size=24, color=GREY_B).next_to(om.get_corner(DL), UR, buff=0.15)
        n2 = txt(NOBIKE, size=24, color=GREY_B).next_to([cut, om.get_bottom()[1], 0], UR, buff=0.15)
        blob = Ellipse(width=5.2, height=1.3, color=HILITE, fill_color=HILITE, fill_opacity=0.35).move_to([cut + 0.6, -1.55, 0])
        blab = MathTex("B", font_size=40, color=HILITE).move_to(blob)
        with self.say("7.5") as (tr, t):
            self.play(FadeIn(head), Write(f), run_time=1.2)
            self.cue(tr, t, {"en": "We split", "uz": "Fazoni"})
            self.play(Create(om), run_time=0.5)
            self.play(Create(div), FadeIn(a1), FadeIn(a2), FadeIn(n1), FadeIn(n2), run_time=0.8)
            self.cue(tr, t, {"en": "work out", "uz": "har bir guruh"})
            self.play(FadeIn(blob), FadeIn(blab), run_time=0.6)
            self.play(Indicate(f[3], color=HILITE), run_time=0.7)
            self.cue(tr, t, {"en": "and average", "uz": "va guruh"})
            self.play(Indicate(f[4], color=HILITE), run_time=0.7)
        self.clear_all()

        b = bars((P_BIKE, P_NOBIKE))
        fl = floor()
        wbr = VGroup()
        x = X0
        for wd, k in zip((P_BIKE, P_NOBIKE), (N["bike"], N["nobike"])):
            W = wd * (X1 - X0)
            br = BraceBetweenPoints([x + 0.04, BASE + H + 0.1, 0], [x + W - 0.04, BASE + H + 0.1, 0], UP, color=LBLUE)
            wbr.add(VGroup(br, txt(STUDENTS.format(n=k), size=24, color=LBLUE).next_to(br, UP, buff=0.08)))
            x += W
        line_45 = DashedLine([X0, py(N["total_bus"]), 0], [X1 + 0.3, py(N["total_bus"]), 0], color=WHITE, stroke_width=4)
        l45 = MathTex(dec(N["total_bus"]), font_size=44).next_to(line_45, RIGHT, buff=0.15)
        ticks = VGroup(*[VGroup(DashedLine([X1 + 0.3, py(r), 0], [X1 + 1.6, py(r), 0], color=GREY_B, stroke_width=2),
                                MathTex(dec(r), font_size=34, color=GREY_B).next_to([X1 + 1.6, py(r), 0], RIGHT, buff=0.1))
                         for r in (R_BIKE, R_NOBIKE)])
        near = Arrow([X1 + 2.9, py(N["total_bus"]) + 0.05, 0], [X1 + 2.9, py(R_BIKE) + 0.1, 0], buff=0.05,
                     color=HILITE, stroke_width=5, max_tip_length_to_length_ratio=0.35)
        legend_ = legend([(BUS_C, BUS), (NOBUS_C, NOBUS)], size=22).move_to([3.9, 2.8, 0])
        with self.say("7.6") as (tr, t):
            self.play(Create(fl), *[FadeIn(m[0]) for m in b], *[FadeIn(m[3]) for m in b], FadeIn(legend_), run_time=0.8)
            self.play(FadeIn(wbr), run_time=0.6)
            self.cue(tr, t, {"en": "the coloured part", "uz": "rangli qismi"})
            self.play(*[GrowFromEdge(m[1], DOWN) for m in b], *[FadeIn(m[2]) for m in b], run_time=1.0)
            self.cue(tr, t, {"en": "The overall answer", "uz": "Umumiy javob"})
            self.play(FadeIn(ticks), run_time=0.6)
            self.play(Create(line_45), Write(l45), run_time=0.9)
            self.cue(tr, t, {"en": "nearer", "uz": "yaqinroq"})
            self.play(GrowArrow(near), run_time=0.6)
            self.play(Indicate(b[0][0], color=LBLUE, scale_factor=1.03), Indicate(wbr[0], color=LBLUE), run_time=0.9)
        self.clear_all()

        # AI: overall accuracy is a weighted average of the groups' accuracies (an illustration, no real model)
        gx0, gx1, gb, gh = -4.6, 2.6, -2.2, 3.4
        big_w, small_w = 0.85, 0.15
        accs = (0.9, 0.3)                    # illustrative bar heights, drawn without numbers
        ai = VGroup()
        x = gx0
        for wd, a, lab in zip((big_w, small_w), accs, (w("large group", "katta guruh"), w("small group", "kichik guruh"))):
            W = wd * (gx1 - gx0)
            fr = Rectangle(width=W - 0.08, height=gh, stroke_color=GREY_D, stroke_width=2).move_to([x + W / 2, gb + gh / 2, 0])
            fi = Rectangle(width=W - 0.08, height=a * gh, stroke_width=0, fill_color=RLGREEN if a > 0.5 else RLRED,
                           fill_opacity=0.9).move_to([x + W / 2, gb + a * gh / 2, 0])
            ai.add(VGroup(fr, fi, txt(lab, size=24, color=GREY_B).next_to(fr, DOWN, buff=0.15)))
            x += W
        overall = big_w * accs[0] + small_w * accs[1]
        ov = DashedLine([gx0, gb + overall * gh, 0], [gx1 + 0.3, gb + overall * gh, 0], color=WHITE, stroke_width=4)
        ovl = txt(w("overall accuracy", "umumiy aniqlik"), size=26).next_to(ov, RIGHT, buff=0.15)
        ill = txt(w("illustration", "tasvir uchun"), size=20, color=GREY_B).next_to(ai, DOWN, buff=0.55).set_x(-1.0)
        ahead = self.heading(w("Model accuracy", "Model aniqligi"), color=LBLUE)
        with self.say("7.7") as (tr, t):
            self.play(FadeIn(ahead), *[FadeIn(g[0]) for g in ai], *[FadeIn(g[2]) for g in ai], FadeIn(ill), run_time=0.8)
            self.play(*[GrowFromEdge(g[1], DOWN) for g in ai], run_time=0.9)
            self.play(Create(ov), FadeIn(ovl), run_time=0.8)
            self.cue(tr, t, {"en": "So the overall", "uz": "Shuning uchun"})
            self.play(Indicate(ovl, color=RLGREEN), run_time=0.7)
            self.play(Indicate(ai[1][1], color=RLRED, scale_factor=1.1), run_time=0.9)
        self.clear_all()


class S07HandsOn(LectureScene):
    def construct(self):
        b = bars((P_BIKE, P_NOBIKE))
        fl = floor()
        task = pause_card([w("P(no bus) with the same formula = ?", "Shu formula bilan: avtobusda qatnamaslik ehtimoli = ?")])
        task.scale(0.85)
        if task.width > 12.4:
            task.scale_to_fit_width(12.4)
        task.move_to([0, 2.75, 0])
        with self.say("7.8") as (tr, t):
            self.play(Create(fl), *[FadeIn(m) for m in b], run_time=0.9)
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(task), *[m[0].animate.set_fill(NOBUS_C, opacity=0.95) for m in b], run_time=0.8)
        self.hands_on()

        n1, n2 = N["total_nobus_terms"]
        ans = MathTex(dec(1 - R_BIKE), r"\times", dec(P_BIKE), "+", dec(1 - R_NOBIKE), r"\times", dec(P_NOBIKE),
                      font_size=42).move_to([3.8, 1.0, 0])
        ans2 = MathTex("=", dec(n1), "+", dec(n2), "=", dec(N["total_nobus"]), font_size=42)
        ans2.next_to(ans, DOWN, buff=0.35).align_to(ans, LEFT)
        ans2[5].set_color(RLGREEN)
        tb, rect = margin_table(1, color=RLGREEN)
        with self.say("7.9") as (tr, t):
            self.play(FadeOut(task), Write(ans), run_time=1.2)
            self.play(Write(ans2), run_time=1.2)
            self.cue(tr, t, {"en": "The table's", "uz": "Jadvaldagi"})
            self.play(FadeIn(tb["grid"]), Create(rect), run_time=0.7)
            self.play(Indicate(tb["coltot"][1], color=RLGREEN, scale_factor=1.4), run_time=0.7)
        self.clear_all()

        # the question for the next section: the same two attributes, the arrow reversed
        a = node(BIKE, color=LBLUE, size=30).move_to([-3.0, 0.2, 0])
        bb = node(BUS, color=HILITE, size=30).move_to([3.0, 0.2, 0])
        fwd = Arrow(a.get_right(), bb.get_left(), buff=0.15, color=GREY_B, stroke_width=5)
        known = MathTex(r"P(B \mid A)", font_size=40, color=GREY_B).next_to(fwd, UP, buff=0.15)
        back = Arrow(bb.get_left(), a.get_right(), buff=0.15, color=HILITE, stroke_width=5).shift(DOWN * 0.7)
        want = MathTex(r"P(A \mid B) = \;?", font_size=44, color=HILITE).next_to(back, DOWN, buff=0.15)
        la = MathTex("A", font_size=40, color=LBLUE).next_to(a, UP, buff=0.2)
        lb = MathTex("B", font_size=40, color=HILITE).next_to(bb, UP, buff=0.2)
        with self.say("7.10") as (tr, t):
            self.play(FadeIn(a), FadeIn(bb), FadeIn(la), FadeIn(lb), GrowArrow(fwd), FadeIn(known), run_time=1.0)
            self.cue(tr, t, {"en": "And the other way", "uz": "Teskarisi"})
            self.play(GrowArrow(back), Write(want), run_time=1.0)
        self.clear_all(run_time=0.3)   # the next section opens on a silent card


SCENES = ["S07Groups", "S07Formula", "S07HandsOn"]
