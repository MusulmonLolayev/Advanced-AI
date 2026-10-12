"""Lecture 2, section 8 — Bayes' theorem.

A = owns a bike, B = takes the bus. We know P(B | A) and want P(A | B): the multiplication rule
written both ways round, set equal and divided by P(B), is Bayes' theorem. Checked on the students
(1/3 = 15 of the 45 bus takers), then its three pieces are named. Every number is N's.
"""
from lecture02_kit import *

P_BIKE = N["p_bike"]
R_BIKE, R_NOBIKE = N["p_bus_given_bike"], N["p_bus_given_nobike"]
BAYES = r"\frac{P(B \mid A)\,P(A)}{P(B)}"


def tfrac(ab):
    return rf"\tfrac{{{ab[0]}}}{{{ab[1]}}}"


def defs(y=2.6):
    """What A and B stand for, kept in the top-left corner."""
    g = VGroup(VGroup(MathTex("A", "=", font_size=36, color=LBLUE), txt(BIKE, size=28, color=LBLUE)).arrange(RIGHT, buff=0.15),
               VGroup(MathTex("B", "=", font_size=36, color=HILITE), txt(BUS, size=28, color=HILITE)).arrange(RIGHT, buff=0.15))
    g.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
    return g.to_corner(UL, buff=SAFE + 0.25)


def students_table(col, cell, color=HILITE, center=(3.6, -1.8, 0), scale=0.66):
    tb = bike_bus_table(size=34, cw=1.9, head_w=2.4, ch=0.7)
    for m in tb["collab"] + tb.get("tothead", []):      # long Uzbek headers must stay inside their column
        if m.width > 1.9 - 0.2:
            m.scale_to_fit_width(1.9 - 0.2)
    rect = tb["col_rect"](col, color=color)
    for m in (tb["grid"], rect):
        m.scale(scale, about_point=ORIGIN).shift(center)
    return tb, rect, tb["cell"][cell][col]


class S08Reverse(LectureScene):
    def construct(self):
        self.section_card(8)
        d = defs()
        a = node(BIKE, color=LBLUE, size=32).move_to([-3.2, 0.6, 0])
        b = node(BUS, color=HILITE, size=32).move_to([3.2, 0.6, 0])
        fwd = Arrow(a.get_right(), b.get_left(), buff=0.15, color=GREY_B, stroke_width=5)
        have = MathTex(r"P(B \mid A)", "=", dec(R_BIKE), font_size=44).next_to(fwd, UP, buff=0.2)
        ok = txt("✓", size=40, color=RLGREEN).next_to(have, RIGHT, buff=0.25)
        back = Arrow(b.get_left(), a.get_right(), buff=0.15, color=HILITE, stroke_width=6).shift(DOWN * 1.1)
        want = MathTex(r"P(A \mid B)", "=", r"\;?", font_size=48, color=HILITE).next_to(back, DOWN, buff=0.2)
        with self.say("8.1") as (tr, t):
            self.play(FadeIn(d), FadeIn(a), FadeIn(b), run_time=0.7)
            self.play(GrowArrow(fwd), Write(have), FadeIn(ok), run_time=1.0)
            self.cue(tr, t, {"en": "We want the reverse", "uz": "Bizga esa"})
            self.play(TransformFromCopy(fwd, back), run_time=0.9)
            self.play(Write(want), run_time=0.7)
        self.play(FadeOut(VGroup(a, b, fwd, have, ok, back, want)), run_time=0.4)

        both = MathTex(r"P(A \cap B)", "=", r"P(A)\,P(B \mid A)", "=", r"P(B)\,P(A \mid B)", font_size=50)
        both.move_to(UP * 0.9)
        b1 = SurroundingRectangle(both[2], color=LBLUE, buff=0.12)
        b2 = SurroundingRectangle(both[4], color=HILITE, buff=0.12)
        with self.say("8.2") as (tr, t):
            self.cue(tr, t, {"en": "A and B together", "uz": "Ey va bi birga"})
            self.play(Write(both[0]), run_time=0.7)
            self.play(Write(both[1:3]), Create(b1), run_time=1.0)
            self.cue(tr, t, {"en": "It is also", "uz": "Shu bilan birga"})
            self.play(Write(both[3:]), Create(b2), run_time=1.0)

        eq = MathTex(r"P(B)\,P(A \mid B)", "=", r"P(A)\,P(B \mid A)", font_size=50).move_to(UP * 0.9)
        bayes = MathTex(r"P(A \mid B)", "=", BAYES, font_size=60).move_to(UP * 0.6)
        frame = SurroundingRectangle(bayes, color=HILITE, buff=0.25)
        name = txt(label("bayes_theorem"), size=34, weight=BOLD, color=HILITE).next_to(frame, UP, buff=0.2)
        with self.say("8.3") as (tr, t):
            self.play(FadeOut(b1), FadeOut(b2), TransformMatchingShapes(both, eq), run_time=1.2)
            self.play(TransformMatchingShapes(eq, bayes), run_time=1.4)
            self.cue(tr, t, {"en": "That is", "uz": "Mana shu"})
            self.play(Create(frame), FadeIn(name, shift=UP * 0.2), run_time=0.8)

        den = MathTex(r"P(B)", "=", r"P(B \mid A)\,P(A)", "+", r"P(B \mid A^c)\,P(A^c)", font_size=44)
        den.next_to(frame, DOWN, buff=1.0)
        arr = Arrow(bayes[2].get_bottom() + DOWN * 0.05, den[0].get_top(), buff=0.12, color=LBLUE, stroke_width=4)
        tot = txt(label("law_of_total_probability"), size=26, color=LBLUE).next_to(den, DOWN, buff=0.3)
        with self.say("8.4"):
            self.play(GrowArrow(arr), Write(den), run_time=1.3)
            self.play(FadeIn(tot), run_time=0.5)
        self.clear_all()


class S08Check(LectureScene):
    def construct(self):
        d = defs()
        calc = MathTex(r"P(A \mid B)", "=", rf"\frac{{{dec(R_BIKE)} \times {dec(P_BIKE)}}}{{{dec(N['p_bus'])}}}",
                       "=", tfrac(N["bayes_bike_given_bus"]), font_size=54).move_to([-2.3, 0.9, 0])
        calc[4].set_color(HILITE)
        tb, rect, c15 = students_table(0, 0)
        frac_t = MathTex(str(N["cells"]["bike_bus"]), "/", str(N["bus"]), "=", tfrac(N["p_bike_given_bus"]),
                         font_size=48, color=HILITE).next_to(tb["grid"], UP, buff=0.4)
        with self.say("8.5") as (tr, t):
            self.play(FadeIn(d), Write(calc[:3]), run_time=1.4)
            self.cue(tr, t, {"en": "gives one third", "uz": "Uchdan bir"})
            self.play(Write(calc[3:]), run_time=0.8)
            self.cue(tr, t, {"en": "The table agrees", "uz": "Jadval ham"})
            self.play(FadeIn(tb["grid"]), run_time=0.6)
            self.play(Create(rect), run_time=0.5)
            self.play(Indicate(c15, color=HILITE, scale_factor=1.5), Write(frac_t), run_time=1.0)
        self.clear_all()


class S08Names(LectureScene):
    def construct(self):
        f = MathTex(r"P(A \mid B)", "=", r"{P(B \mid A)", r"\,P(A)", r"\over", r"P(B)}", font_size=72).move_to(UP * 0.2 + LEFT * 1.0)
        like_b = Brace(f[2], UP, color=HILITE, buff=0.12)
        prior_b = Brace(f[3], UP, color=LBLUE, buff=0.12)
        post_b = Brace(f[0], DOWN, color=RLGREEN, buff=0.12)
        like_l = txt(label("likelihood"), size=28, weight=BOLD, color=HILITE).next_to(like_b, UP, buff=0.12)
        # the prior's label sits one level higher and to the right, so the two never collide
        prior_l = txt(label("prior"), size=28, weight=BOLD, color=LBLUE)
        prior_l.next_to(like_l, UP, buff=0.3).set_x(prior_b.get_tip()[0] + 0.5)
        prior_link = Line(prior_b.get_tip(), prior_l.get_bottom(), color=LBLUE, stroke_width=2)
        post_l = txt(label("posterior"), size=28, weight=BOLD, color=RLGREEN).next_to(post_b, DOWN, buff=0.12)
        post_link = VMobject()
        with self.say("8.6") as (tr, t):
            self.play(Write(f), run_time=1.2)
            self.cue(tr, t, {"en": "The probability of A is", "uz": "Ey ning ehtimoli"})
            self.play(f[3].animate.set_color(LBLUE), GrowFromCenter(prior_b), run_time=0.7)
            self.play(Create(prior_link), FadeIn(prior_l), run_time=0.6)
        with self.say("8.7") as (tr, t):
            self.play(f[2].animate.set_color(HILITE), GrowFromCenter(like_b), FadeIn(like_l), run_time=0.9)
            self.cue(tr, t, {"en": "The probability of A given B", "uz": "Bi sodir boʻlgandagi ey"})
            self.play(f[0].animate.set_color(RLGREEN), GrowFromCenter(post_b), run_time=0.7)
            self.play(FadeIn(post_l), run_time=0.6)
        named = VGroup(f, prior_b, like_b, post_b, prior_l, like_l, post_l, prior_link, post_link)
        self.play(named.animate.scale(0.5).to_corner(UR, buff=SAFE + 0.2), run_time=0.7)

        # rain and the wet pavement: prior → evidence → posterior, not certainty
        cloud = VGroup(*[Circle(radius=r, fill_color=GREY_B, fill_opacity=1, stroke_width=0).move_to(p)
                         for r, p in ((0.45, [-0.35, 0, 0]), (0.6, [0.25, 0.15, 0]), (0.4, [0.85, 0, 0]))])
        cloud.move_to([-4.6, 1.5, 0])
        drops = VGroup(*[Line([x, 0.75, 0], [x - 0.12, 0.35, 0], color=LBLUE, stroke_width=4) for x in (-5.0, -4.6, -4.2)])
        rain_l = txt(label("rain"), size=26, color=GREY_B).next_to(cloud, UP, buff=0.15)
        pave = Rectangle(width=3.6, height=0.35, stroke_width=0, fill_color=GREY_D, fill_opacity=1).move_to([-3.4, -0.9, 0])
        wet = Rectangle(width=3.6, height=0.35, stroke_width=0, fill_color=LBLUE, fill_opacity=0.85).move_to(pave)
        pave_l = txt(label("wet_pavement"), size=26, color=LBLUE).next_to(pave, DOWN, buff=0.15)
        ev = txt(label("evidence"), size=24, color=HILITE).next_to(pave_l, DOWN, buff=0.1)
        truck = VGroup(RoundedRectangle(corner_radius=0.1, width=1.3, height=0.6, fill_color=RLGREEN, fill_opacity=1,
                                        stroke_width=0),
                       Circle(radius=0.14, fill_color=GREY_B, fill_opacity=1, stroke_width=0).shift([-0.38, -0.32, 0]),
                       Circle(radius=0.14, fill_color=GREY_B, fill_opacity=1, stroke_width=0).shift([0.38, -0.32, 0]))
        truck.move_to([-1.0, -0.15, 0])
        spray = VGroup(*[Line([-1.7, -0.3 - 0.08 * k, 0], [-2.1, -0.65, 0], color=LBLUE, stroke_width=3) for k in range(3)])
        truck_l = txt(label("street_cleaner"), size=24, color=RLGREEN).next_to(truck, UP, buff=0.2)
        # the belief in rain as a bar, drawn without numbers: it rises, but stops short of the top
        bx, bb, bh = 2.4, -2.6, 3.6
        frame_ = Rectangle(width=0.9, height=bh, stroke_color=GREY_B, stroke_width=2).move_to([bx, bb + bh / 2, 0])
        top = DashedLine([bx - 0.7, bb + bh, 0], [bx + 0.7, bb + bh, 0], color=GREY_B, stroke_width=2)
        top_l = txt(label("certain"), size=22, color=GREY_B).next_to(top, RIGHT, buff=0.1)
        lo, hi = 0.3, 0.8                      # illustrative heights
        belief = Rectangle(width=0.86, height=lo * bh, stroke_width=0, fill_color=LBLUE, fill_opacity=0.9)
        belief.move_to([bx, bb + lo * bh / 2, 0])
        belief_hi = Rectangle(width=0.86, height=hi * bh, stroke_width=0, fill_color=RLGREEN, fill_opacity=0.9)
        belief_hi.move_to([bx, bb + hi * bh / 2, 0])
        bl = txt(label("p_rain"), size=26).next_to(frame_, DOWN, buff=0.15)
        stage = txt(label("prior", 1), size=24, color=LBLUE).next_to(frame_, LEFT, buff=0.2).set_y(bb + lo * bh)
        stage2 = txt(label("posterior", 1), size=24, color=RLGREEN).next_to(frame_, LEFT, buff=0.2).set_y(bb + hi * bh)
        with self.say("8.8") as (tr, t):
            self.play(FadeIn(cloud), FadeIn(rain_l), FadeIn(frame_), Create(top), FadeIn(top_l), FadeIn(bl), run_time=0.8)
            self.play(GrowFromEdge(belief, DOWN), FadeIn(stage), run_time=0.7)
            self.cue(tr, t, {"en": "The pavement is wet", "uz": "Yoʻlak hoʻl"})
            self.play(FadeIn(pave), run_time=0.3)
            self.play(FadeIn(wet), FadeIn(pave_l), FadeIn(ev), run_time=0.7)
            self.cue(tr, t, {"en": "Rain almost always", "uz": "Yomgʻir yoqsa"})
            self.play(Create(drops), run_time=0.6)
            self.play(Transform(belief, belief_hi), FadeOut(stage), FadeIn(stage2), run_time=1.0)
            self.cue(tr, t, {"en": "But not to certainty", "uz": "Lekin aniq"})
            self.play(Indicate(top_l, color=RLRED), run_time=0.6)
            self.play(FadeIn(truck), FadeIn(truck_l), Create(spray), run_time=0.9)
        self.clear_all()

        # AI: update a belief with evidence; naive Bayes asks P(spam | words)
        steps = VGroup(node(label("belief"), color=LBLUE, size=30),
                       node(label("evidence_data"), color=HILITE, size=30),
                       node(label("updated_belief"), color=RLGREEN, size=30)).arrange(RIGHT, buff=1.0)
        steps.move_to(UP * 1.4)
        arrows = VGroup(Arrow(steps[0].get_right(), steps[1].get_left(), buff=0.1, color=GREY_B),
                        Arrow(steps[1].get_right(), steps[2].get_left(), buff=0.1, color=GREY_B))
        loop = CurvedArrow(steps[2].get_bottom() + DOWN * 0.1, steps[0].get_bottom() + DOWN * 0.1, angle=-TAU / 6,
                           color=GREY_B)
        env = VGroup(Rectangle(width=2.2, height=1.4, stroke_color=WHITE, stroke_width=3),
                     Line([-1.1, 0.7, 0], [0, -0.05, 0], color=WHITE, stroke_width=3),
                     Line([1.1, 0.7, 0], [0, -0.05, 0], color=WHITE, stroke_width=3)).move_to([-2.3, -2.0, 0])
        spam = txt(label("p_spam_words"), size=34, color=HILITE).next_to(env, RIGHT, buff=0.6)
        with self.say("8.9") as (tr, t):
            self.play(FadeIn(steps[0]), run_time=0.5)
            self.play(GrowArrow(arrows[0]), FadeIn(steps[1]), run_time=0.7)
            self.play(GrowArrow(arrows[1]), FadeIn(steps[2]), run_time=0.7)
            self.cue(tr, t, {"en": "and that is exactly", "uz": "Berilganlardan"})
            self.play(Create(loop), run_time=0.8)
            self.cue(tr, t, {"en": "The naive Bayes", "uz": "Sodda Bayes"})
            self.play(Create(env), run_time=0.6)
            self.play(Write(spam), run_time=0.8)
        self.clear_all()


class S08HandsOn(LectureScene):
    def construct(self):
        d = defs()
        f = MathTex(r"P(A \mid B)", "=", BAYES, font_size=46).to_corner(UR, buff=SAFE + 0.3)
        task = pause_card([label("p_no_bike_bus_q"),
                           label("use_bayes_theorem")])
        if task.width > 12:
            task.scale_to_fit_width(12)
        task.move_to(DOWN * 0.6)
        with self.say("8.10") as (tr, t):
            self.play(FadeIn(d), Write(f), run_time=0.9)
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(task), run_time=0.7)
        self.hands_on()

        ans = MathTex(r"P(A^c \mid B)", "=", rf"\frac{{{dec(R_NOBIKE)} \times {dec(1 - P_BIKE)}}}{{{dec(N['p_bus'])}}}",
                      "=", tfrac(N["bayes_nobike_given_bus"]), font_size=52).move_to([-2.4, 0.4, 0])
        ans[4].set_color(HILITE)
        tb, rect, c30 = students_table(0, 1)
        frac_t = MathTex(str(N["cells"]["nobike_bus"]), "/", str(N["bus"]), "=", tfrac(N["bayes_nobike_given_bus"]),
                         font_size=48, color=HILITE).next_to(tb["grid"], UP, buff=0.4)
        with self.say("8.11") as (tr, t):
            self.play(FadeOut(task), Write(ans[:3]), run_time=1.3)
            self.play(Write(ans[3:]), run_time=0.7)
            self.cue(tr, t, {"en": "The table says", "uz": "Jadvalda ham"})
            self.play(FadeIn(tb["grid"]), Create(rect), run_time=0.7)
            self.play(Indicate(c30, color=HILITE, scale_factor=1.5), Write(frac_t), run_time=0.9)
        self.clear_all()

        # the question for the next section: one direction is easy to measure, the other is the one we want
        easy = VGroup(MathTex(r"P(B \mid A)", font_size=56, color=GREY_B),
                      txt(label("easy_to_measure"), size=28, color=GREY_B)).arrange(DOWN, buff=0.25)
        need = VGroup(MathTex(r"P(A \mid B)", font_size=56, color=HILITE),
                      txt(label("what_we_need"), size=28, color=HILITE)).arrange(DOWN, buff=0.25)
        VGroup(easy, need).arrange(RIGHT, buff=2.4).move_to(UP * 0.2)
        swap = DoubleArrow(easy[0].get_right(), need[0].get_left(), buff=0.3, color=GREY_B, stroke_width=4)
        with self.say("8.12") as (tr, t):
            self.play(FadeIn(easy), run_time=0.7)
            self.cue(tr, t, {"en": "In real life", "uz": "Hayotda"})
            self.play(GrowFromCenter(swap), FadeIn(need), run_time=0.9)
        self.clear_all(run_time=0.3)   # the next section opens on a silent card


SCENES = ["S08Reverse", "S08Check", "S08Names", "S08HandsOn"]
