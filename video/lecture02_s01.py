"""Lecture 2, section 1 — conditional probability: the die, then the 100 students.

Every number on screen comes from N (capture_l02.py, unit-tested by test_l02.py):
die_p6, die_p_even, die_p6_given_even, n, bus, bike, nobike, cells, p_bus, p_bus_given_bike,
p_bus_given_nobike.
"""
from lecture02_kit import *

C = N["cells"]


def tfrac(a, b, size=44, color=WHITE):
    return MathTex(rf"\frac{{{a}}}{{{b}}}", font_size=size, color=color)


def vfrac(a, b, size=56, color=WHITE):
    """A fraction built from separate numerator, bar and denominator, so each can morph on its own."""
    num = MathTex(str(a), font_size=size, color=color)
    den = MathTex(str(b), font_size=size, color=color)
    bar = Line(LEFT, RIGHT, stroke_width=4, color=color).set_width(max(num.width, den.width) + 0.3)
    num.next_to(bar, UP, buff=0.15)
    den.next_to(bar, DOWN, buff=0.15)
    return VGroup(num, bar, den)


def grey_where(grid, who, keep):
    """Animations that grey out every square whose (bike, bus) pair fails keep()."""
    return [sq.animate.set_fill(OUT_C) for sq, k in zip(grid, who) if not keep(k)]


def group_box(grid, who, test, color=RLBLUE):
    sel = VGroup(*[sq for sq, k in zip(grid, who) if test(k)])
    return SurroundingRectangle(sel, buff=0.1, color=color, stroke_width=4)


class S01Die(LectureScene):
    def construct(self):
        self.section_card(1)
        faces = VGroup(*[die_face(k, 0.95) for k in range(1, 7)]).arrange(RIGHT, buff=0.5).move_to(UP * 0.9)
        p6 = N["die_p6"]
        probs = VGroup(*[tfrac(*p6, size=46, color=GREY_B).next_to(f, DOWN, buff=0.3) for f in faces])
        with self.say("1.1") as (tr, t):
            self.play(LaggedStart(*[FadeIn(f, shift=DOWN * 0.3) for f in faces], lag_ratio=0.12), run_time=1.2)
            self.cue(tr, t, 1)
            self.play(FadeIn(probs), faces[5][0].animate.set_stroke(HILITE, width=5), run_time=0.8)

        friend = txt(w("“It's even.”", "«Juft son chiqdi»"), size=36, weight=BOLD, color=HILITE)
        friend.to_edge(UP, buff=SAFE + 0.4)
        g = N["die_p6_given_even"]
        even = [1, 3, 5]
        new = [tfrac(*g, size=50, color=HILITE if i == 5 else WHITE).move_to(probs[i]) for i in even]
        odd = [0, 2, 4]
        with self.say("1.2") as (tr, t):
            self.play(FadeIn(friend, shift=DOWN * 0.2), run_time=0.6)
            self.cue(tr, t, {"en": "Only two", "uz": "Endi faqat"})
            self.play(*[faces[i].animate.set_opacity(0.2) for i in odd],
                      *[FadeOut(probs[i]) for i in odd], run_time=0.8)
            self.cue(tr, t, {"en": "Now the chance", "uz": "Olti chiqish ehtimoli endi"})
            self.play(*[Transform(probs[i], m) for i, m in zip(even, new)], run_time=0.7)
            self.play(Indicate(probs[5], color=HILITE), run_time=0.6)

        same = txt(w("the die did not change", "kubik oʻzgarmadi"), size=28, color=GREY_B)
        knew = txt(w("what we know changed", "bilganimiz oʻzgardi"), size=30, weight=BOLD, color=LBLUE)
        VGroup(same, knew).arrange(DOWN, buff=0.25).move_to(DOWN * 2.3)
        with self.say("1.3") as (tr, t):
            self.play(FadeIn(same), run_time=0.6)
            self.cue(tr, t, 1)
            self.play(FadeIn(knew, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        head = self.heading(w("Conditional probability", "Shartli ehtimollik"), color=HILITE)
        f = MathTex(r"P(B \mid A)", "=", r"\frac{P(A \cap B)}{P(A)}", font_size=72).move_to(UP * 0.5)
        bar_lab = txt(w("“given”", "«… boʻlgandagi»"), size=28, color=HILITE)
        bar_lab.next_to(f[0], DOWN, buff=0.5)
        arrow = Arrow(bar_lab.get_top(), f[0].get_bottom() + DOWN * 0.05, buff=0.08, color=HILITE, stroke_width=4)
        with self.say("1.4") as (tr, t):
            self.play(FadeIn(head), Write(f[0]), run_time=0.9)
            self.play(FadeIn(bar_lab), GrowArrow(arrow), run_time=0.6)
            self.cue(tr, t, {"en": "To find it", "uz": "Uni topish uchun"})
            self.play(Write(f[1:]), run_time=1.2)

        pe = N["die_p_even"]
        calc = MathTex(r"\frac{%d/%d}{%d/%d}" % (*p6, *pe), "=", rf"\frac{{{g[0]}}}{{{g[1]}}}", font_size=60)
        calc.move_to(DOWN * 2.2)
        evens = VGroup(*[die_face(k, 0.6) for k in (2, 4, 6)]).arrange(RIGHT, buff=0.3).next_to(calc, RIGHT, buff=0.8)
        evens[2][0].set_stroke(HILITE, width=5)
        with self.say("1.5") as (tr, t):
            self.play(FadeOut(VGroup(bar_lab, arrow)), Write(calc), run_time=1.2)
            self.cue(tr, t, 1)
            self.play(FadeIn(evens, shift=LEFT * 0.2), run_time=0.6)
        self.clear_all()


class S01Students(LectureScene):
    def construct(self):
        grid, who = student_grid()
        grid.move_to([-3.1, -0.15, 0])
        leg = legend([(BUS_C, BUS), (NOBUS_C, NOBUS)]).next_to(grid, DOWN, buff=0.3)
        title = txt(STUDENTS.format(n=N["n"]), size=34, weight=BOLD).next_to(grid, UP, buff=0.3)
        fr = vfrac(N["bus"], N["n"]).move_to([2.4, 0.4, 0])
        eq = MathTex("=", dec(N["p_bus"]), font_size=56).next_to(fr, RIGHT, buff=0.35)
        p_lab = txt(w("P(bus)", "P(avtobusda)"), size=34, color=GREY_B).next_to(VGroup(fr, eq), UP, buff=0.6)
        with self.say("1.6") as (tr, t):
            self.cue(tr, t, {"en": "A year group", "uz": "Bir kursda"})
            self.play(FadeIn(title), LaggedStart(*[FadeIn(s, scale=0.5) for s in grid], lag_ratio=0.008),
                      run_time=1.4)
            self.cue(tr, t, {"en": "Forty-five", "uz": "Ulardan qirq"})
            self.play(FadeIn(leg), Indicate(VGroup(*[s for s, k in zip(grid, who) if k[1] == "bus"]),
                                            color=WHITE, scale_factor=1.05), run_time=0.9)
            self.cue(tr, t, {"en": "So the probability", "uz": "Demak, avtobusda"})
            self.play(FadeIn(p_lab), Write(fr), Write(eq), run_time=1.0)

        box = group_box(grid, who, lambda k: k[0] == "bike")
        blab = txt(w("bike: {n}", "velosipedli: {n}").format(n=N["bike"]), size=28, color=LBLUE, weight=BOLD)
        blab.next_to(box, UP, buff=0.12).align_to(box, LEFT)
        with self.say("1.7") as (tr, t):
            self.play(*grey_where(grid, who, lambda k: k[0] == "bike"), FadeOut(title), run_time=0.9)
            self.play(Create(box), FadeIn(blab), run_time=0.7)
            self.cue(tr, t, {"en": "and only fifteen", "uz": "ulardan avtobusda"})
            self.play(Indicate(VGroup(*[s for s, k in zip(grid, who) if k == ("bike", "bus")]),
                               color=WHITE, scale_factor=1.15), run_time=0.9)

        fr2 = vfrac(C["bike_bus"], N["bike"]).move_to(fr)
        eq2 = MathTex("=", dec(N["p_bus_given_bike"]), font_size=56, color=HILITE).next_to(fr2, RIGHT, buff=0.35)
        p_lab2 = txt(w("P(bus | bike)", "P(avtobusda | velosipedli)"), size=34, color=HILITE).move_to(p_lab)
        num_lab = txt(w("top", "surat"), size=24, color=GREY_B).next_to(fr2, LEFT, buff=0.6).align_to(fr2[0], DOWN)
        den_lab = txt(w("bottom", "maxraj"), size=24, color=GREY_B).next_to(fr2, LEFT, buff=0.6).align_to(fr2[2], UP)
        with self.say("1.8") as (tr, t):
            self.play(Indicate(grid, color=WHITE, scale_factor=1.02), run_time=0.8)
            self.cue(tr, t, {"en": "The top", "uz": "Surat"})
            self.play(FadeIn(num_lab), Transform(fr[0], fr2[0]), run_time=0.8)
            self.cue(tr, t, {"en": "the bottom", "uz": "maxraj"})
            self.play(FadeIn(den_lab), Transform(fr[2], fr2[2]), Transform(fr[1], fr2[1]), run_time=0.8)
            self.cue(tr, t, {"en": "zero point two five", "uz": "nol butun yuzdan"})
            self.play(Transform(eq, eq2), Transform(p_lab, p_lab2), run_time=0.8)

        omega = txt(w("new sample space = A", "yangi fazo = A"), size=28, weight=BOLD, color=LBLUE)
        omega.move_to(blab, aligned_edge=LEFT)
        with self.say("1.9") as (tr, t):
            self.play(box.animate.set_stroke(HILITE, width=6), run_time=0.6)
            self.cue(tr, t, {"en": "A becomes", "uz": "ey yangi"})
            self.play(Transform(blab, omega.set_color(HILITE)), run_time=0.7)
        self.clear_all()


class S01Spam(LectureScene):
    def construct(self):
        env = Rectangle(width=4.2, height=2.6, stroke_color=GREY_B, stroke_width=3).move_to([-3.4, 0.2, 0])
        flap = VMobject(stroke_color=GREY_B, stroke_width=3).set_points_as_corners(
            [env.get_corner(UL), env.get_center() + DOWN * 0.15, env.get_corner(UR)])
        words = txt(w("“free prize!”", "«bepul sovrin!»"), size=34, weight=BOLD, color=HILITE).move_to(env).shift(DOWN * 0.6)
        mail = VGroup(env, flap, words)
        model = node(w("classifier", "klassifikator"), color=LBLUE, size=28).move_to([1.0, 0.2, 0])
        a1 = Arrow(env.get_right(), model.get_left(), buff=0.15, color=GREY_B)
        out = txt(w("P(spam | “free prize”)", "P(spam | «bepul sovrin»)"), size=32, weight=BOLD, color=HILITE)
        out.next_to(model, DOWN, buff=1.0).set_x(2.6)
        a2 = Arrow(model.get_bottom(), out.get_top(), buff=0.12, color=GREY_B)
        if out.get_right()[0] > 6.4:
            out.shift(LEFT * (out.get_right()[0] - 6.4))
        with self.say("1.10") as (tr, t):
            self.play(FadeIn(model), run_time=0.6)
            self.cue(tr, t, {"en": "for example", "uz": "masalan"})
            self.play(FadeIn(mail, shift=RIGHT * 0.3), run_time=0.7)
            self.play(GrowArrow(a1), run_time=0.5)
            self.play(GrowArrow(a2), FadeIn(out, shift=DOWN * 0.2), run_time=0.8)
        self.clear_all()


class S01HandsOn(LectureScene):
    def construct(self):
        grid, who = student_grid(side=0.3, gap=0.05)
        grid.move_to([4.0, -0.3, 0])
        pc = pause_card([w("Look only at the {n} students with no bike", "Faqat {n} ta velosipedsiz talabaga qaraymiz").format(n=N["nobike"]),
                         w("How many of them take the bus?", "Ulardan nechtasi avtobusda qatnaydi?")])
        pc.move_to([-2.4, 0.2, 0])
        if pc.width > 7.6:
            pc.scale_to_fit_width(7.6).move_to([-2.4, 0.2, 0])
        with self.say("1.11") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(pc, shift=UP * 0.2), FadeIn(grid), run_time=0.8)
            self.play(*grey_where(grid, who, lambda k: k[0] == "nobike"), run_time=0.8)
        self.hands_on()

        box = group_box(grid, who, lambda k: k[0] == "nobike", color=HILITE)
        fr = vfrac(C["nobike_bus"], N["nobike"]).move_to([-2.4, -0.2, 0])
        eq = MathTex("=", dec(N["p_bus_given_nobike"]), font_size=56, color=HILITE).next_to(fr, RIGHT, buff=0.35)
        lab = txt(w("P(bus | no bike)", "P(avtobusda | velosipedsiz)"), size=34, color=HILITE)
        lab.next_to(VGroup(fr, eq), UP, buff=0.6)
        with self.say("1.12") as (tr, t):
            self.play(FadeOut(pc), Create(box), run_time=0.7)
            self.play(Indicate(VGroup(*[s for s, k in zip(grid, who) if k == ("nobike", "bus")]),
                               color=WHITE, scale_factor=1.15), run_time=0.8)
            self.cue(tr, t, {"en": "Thirty out of forty", "uz": "Qirqdan oʻttiz"})
            self.play(FadeIn(lab), Write(fr), Write(eq), run_time=1.0)
        self.clear_all()

        stages = VGroup(node(STUDENTS.format(n=N["n"]), size=32), node(BIKE, size=32), node(BUS, color=GREY_B, size=32))
        stages.arrange(RIGHT, buff=1.0)
        arrows = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.1, color=GREY_B) for a, b in zip(stages, stages[1:])])
        with self.say("1.13") as (tr, t):
            self.play(FadeIn(stages[0]), run_time=0.5)
            self.play(GrowArrow(arrows[0]), FadeIn(stages[1]), run_time=0.6)
            self.play(GrowArrow(arrows[1]), FadeIn(stages[2]), run_time=0.6)
        self.clear_all()


SCENES = ["S01Die", "S01Students", "S01Spam", "S01HandsOn"]
