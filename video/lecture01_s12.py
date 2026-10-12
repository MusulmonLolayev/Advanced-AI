"""Lecture 1, section 12 — the birthday problem.

The curve is L["bday_curve"] (P(shared birthday) for n = 1..70), the marked points
are L["bday"], the pair count is L["bday_pairs_23"]; all from capture_l01.py.
"""
from lecture01_kit import *

CURVE = L["bday_curve"]
BD = {int(k): v for k, v in L["bday"].items()}
PAIRS = L["bday_pairs_23"]
# the narration speaks these, so fail if the capture ever moves
assert round(BD[10] * 100) == 12 and round(BD[23] * 1000) == 507
assert round(BD[30] * 100) == 71 and round(BD[50] * 100) == 97 and BD[70] > 0.999
assert L["bday_first_over_half"] == 23 and PAIRS == 23 * 22 // 2 == 253
assert len(CURVE) == 70 and abs(CURVE[22] - BD[23]) < 1e-12


def pct(p):
    return f"{p * 100:.1f}%"


def bday_axes():
    ax = Axes(x_range=[0, 70, 10], y_range=[0, 1, 0.25], x_length=9.6, y_length=4.4,
              axis_config={"color": GREY_B, "stroke_width": 2, "include_tip": False},
              x_axis_config={"numbers_to_include": list(range(0, 71, 10)), "font_size": 22},
              y_axis_config={"numbers_to_include": [0, 0.25, 0.5, 0.75, 1], "font_size": 22,
                             "decimal_number_config": {"num_decimal_places": 2}})
    ax.move_to([0.2, -0.55, 0])
    xl = txt(label("people_in_the_room_n"), size=22, color=GREY_B)
    xl.next_to(ax.x_axis, DOWN, buff=0.45)
    yl = txt(label("p_shared_birthday"), size=22, color=GREY_B)
    yl.rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.55)
    return ax, VGroup(xl, yl)


def curve_part(ax, n0, n1):
    """The curve from n0 to n1 (inclusive), one vertex per group size."""
    pts = [ax.c2p(n, CURVE[n - 1]) for n in range(n0, n1 + 1)]
    return VMobject(color=RLBLUE, stroke_width=5).set_points_as_corners(pts)


def marker(ax, n, color=RLRED, side=DR):
    p = ax.c2p(n, BD[n])
    dot = Dot(p, radius=0.08, color=color)
    drop = DashedLine(ax.c2p(n, 0), p, color=color, stroke_width=2)
    lab = txt(f"n = {n}:  {pct(BD[n])}", size=24, weight=BOLD, color=color).next_to(dot, side, buff=0.15)
    lab.add_background_rectangle(opacity=0.9, buff=0.06)
    return VGroup(drop, dot, lab)


class S12Problem(LectureScene):
    def construct(self):
        self.section_card(12)
        room = RoundedRectangle(corner_radius=0.3, width=6.4, height=4.6, stroke_color=GREY_B, stroke_width=3)
        room.move_to([-2.6, -0.4, 0])
        rng = np.random.default_rng(23)
        pos = []
        while len(pos) < 23:      # 23 people, kept apart so every dot reads as a person
            p = np.array([rng.uniform(-5.4, 0.2), rng.uniform(-2.3, 1.5), 0])
            if all(np.linalg.norm(p - q) > 0.6 for q in pos):
                pos.append(p)
        people = VGroup(*[Dot(p, radius=0.11, color=RLBLUE) for p in pos])
        q = txt("?", size=96, weight=BOLD, color=HILITE).move_to([3.6, 0.6, 0])
        head = self.heading(label("how_many_people_before_p_shared_q"), size=30)
        bubble = RoundedRectangle(corner_radius=0.25, width=3.6, height=1.7, stroke_color=GREY_B,
                                  fill_color=BLACK, fill_opacity=0.8).move_to([3.8, -1.3, 0])
        guess = VGroup(txt(label("most_people_guess"), size=22, color=GREY_B),
                       txt("≈ 180", size=48, weight=BOLD)).arrange(DOWN, buff=0.15).move_to(bubble)

        t = line("12.1")
        with self.voiceover(t) as tr:
            self.play(FadeIn(head), Create(room), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in people], lag_ratio=0.08), run_time=1.6)
            self.play(FadeIn(q, scale=0.6), run_time=0.5)
            self.cue(tr, t, 1)
            self.play(FadeIn(bubble), FadeIn(guess), q.animate.shift(UP * 0.6), run_time=0.8)

        # counting the "shared" cases directly: pairs, a triple, two pairs... it tangles
        def link(i, j, c=HILITE):
            return Line(pos[i], pos[j], color=c, stroke_width=3)
        pair = link(0, 5)
        triple = VGroup(link(2, 7), link(7, 11), link(11, 2))
        two_pairs = VGroup(link(3, 9, RLGREEN), link(13, 17, RLGREEN))
        tags = VGroup(txt(label("a_pair"), size=22, color=HILITE),
                      txt(label("a_triple"), size=22, color=HILITE),
                      txt(label("two_pairs"), size=22, color=RLGREEN))
        tags.arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to([3.8, -1.3, 0])
        tangle = VGroup(*[link(i, j).set_stroke(width=1.5, opacity=0.6)
                          for i, j in rng.integers(0, 23, size=(40, 2)) if i != j])
        mess = txt("?!", size=60, weight=BOLD, color=RLRED).move_to(q)
        t = line("12.2")
        with self.voiceover(t) as tr:
            self.play(FadeOut(bubble), FadeOut(guess), run_time=0.5)
            self.cue(tr, t, 2)
            self.play(Create(pair), FadeIn(tags[0]), run_time=0.6)
            self.play(Create(triple), FadeIn(tags[1]), run_time=0.7)
            self.play(Create(two_pairs), FadeIn(tags[2]), run_time=0.7)
            self.play(LaggedStart(*[Create(l) for l in tangle], lag_ratio=0.05), FadeTransform(q, mess),
                      run_time=1.6)

        # the complement: everyone different
        lhs = txt(label("p_a_shared_pair"), size=34, color=HILITE)
        eq = txt("=", size=34)
        one = txt("1  −", size=34)
        rhs = txt(label("p_all_different"), size=34, color=RLGREEN)
        formula = VGroup(lhs, eq, one, rhs).arrange(RIGHT, buff=0.3).move_to(UP * 1.2)
        t = line("12.3")
        with self.voiceover(t) as tr:
            self.play(FadeOut(VGroup(pair, triple, two_pairs, tangle, tags, mess, head)), run_time=0.6)
            self.play(VGroup(room, people).animate.scale(0.55).move_to([0, -1.9, 0]), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeIn(rhs), people.animate.set_color(RLGREEN), run_time=0.7)
            self.cue(tr, t, 2)
            self.play(FadeIn(VGroup(lhs, eq, one)), run_time=0.8)
        self.play(FadeOut(VGroup(room, people)), formula.animate.to_edge(UP, buff=SAFE + 0.35), run_time=0.6)

        # a 365-day calendar; each new person must find a free day
        cells = VGroup(*[Square(0.2, stroke_color=GREY_D, stroke_width=1) for _ in range(365)])
        cells.arrange_in_grid(rows=15, cols=25, buff=0.03).move_to([-3.4, -0.9, 0])
        cal_lab = txt(label("365_days"), size=22, color=GREY_B).next_to(cells, DOWN, buff=0.2)
        who_lab = txt(label("person"), size=22, color=RLBLUE)
        taken = [40, 211, 300]
        fr = [MathTex(r"\frac{365}{365}", font_size=48), MathTex(r"\cdot\,\frac{364}{365}", font_size=48),
              MathTex(r"\cdot\,\frac{363}{365}\,\cdots", font_size=48)]
        VGroup(*fr).arrange(RIGHT, buff=0.15).move_to([3.4, -0.6, 0])
        who = [txt(str(i), size=24, weight=BOLD, color=RLBLUE) for i in (1, 2, 3)]
        for wlab, f in zip(who, fr):
            wlab.next_to(f, DOWN, buff=0.3)
        t = line("12.4")
        with self.voiceover(t) as tr:
            self.play(FadeIn(cells, lag_ratio=0.002), FadeIn(cal_lab), run_time=1.0)
            who_lab.next_to(who[0], LEFT, buff=0.5)
            for k in range(3):
                if k:
                    self.cue(tr, t, k)
                if k == 1:
                    self.play(cells[taken[0]].animate.set_fill(GREY_C, 1), run_time=0.3)
                if k == 2:
                    self.play(cells[taken[1]].animate.set_fill(GREY_C, 1), run_time=0.3)
                self.play(cells[taken[k]].animate.set_fill(RLBLUE, 1).set_stroke(WHITE, 2),
                          FadeIn(fr[k], shift=UP * 0.2), FadeIn(who[k]), *([FadeIn(who_lab)] if k == 0 else []),
                          run_time=0.7)

        prod_ = MathTex(r"=\;1\;-\;\frac{365}{365}\cdot\frac{364}{365}\cdot\frac{363}{365}\cdots\frac{365-n+1}{365}",
                        font_size=50)
        prod_.next_to(formula, DOWN, buff=0.8)
        prod_.set_x(0)
        brace = Brace(prod_[0][3:], DOWN, color=RLGREEN)
        blab = txt(label("all_different"), size=24, color=RLGREEN).next_to(brace, DOWN, buff=0.12)
        t = line("12.5")
        with self.voiceover(t) as tr:
            self.play(FadeOut(VGroup(cells, cal_lab, who_lab, *who)), ReplacementTransform(VGroup(*fr), prod_[0][3:]),
                      run_time=1.2)
            self.play(FadeIn(prod_[0][:3]), GrowFromCenter(brace), FadeIn(blab), run_time=0.9)
        self.clear_all()


class S12Curve(LectureScene):
    def construct(self):
        ax, labs = bday_axes()
        half = DashedLine(ax.c2p(0, 0.5), ax.c2p(70, 0.5), color=GREY_B, stroke_width=2)
        half_lab = txt("1/2", size=22, color=GREY_B).next_to(half, RIGHT, buff=0.1)
        m10, m23 = marker(ax, 10, HILITE, UL), marker(ax, 23)
        t = line("12.6")
        with self.voiceover(t) as tr:
            self.play(Create(ax), FadeIn(labs), run_time=1.0)
            self.play(Create(curve_part(ax, 1, 10)), run_time=1.0, rate_func=linear)
            self.play(FadeIn(m10), run_time=0.5)
            self.cue(tr, t, 1)
            self.play(Create(curve_part(ax, 10, 23)), Create(half), FadeIn(half_lab), run_time=1.3,
                      rate_func=linear)
            self.play(FadeIn(m23), run_time=0.5)
            self.cue(tr, t, 2)
            self.play(Indicate(m23[1], scale_factor=2.0, color=RLRED), run_time=0.8)

        m50, m70 = marker(ax, 50, RLGREEN), marker(ax, 70, RLGREEN)
        m70[2].move_to(ax.c2p(69.5, 0.68), aligned_edge=RIGHT)
        t = line("12.7")
        with self.voiceover(t) as tr:
            self.play(Create(curve_part(ax, 23, 50)), run_time=1.2, rate_func=linear)
            self.play(FadeIn(m50), run_time=0.5)
            self.cue(tr, t, {"en": 1, "uz": "yetmish"})
            self.play(Create(curve_part(ax, 50, 70)), run_time=0.8, rate_func=linear)
            self.play(FadeIn(m70), run_time=0.5)
        self.clear_all()


class S12Pairs(LectureScene):
    def construct(self):
        c, r = np.array([-2.6, -0.35, 0]), 2.8
        pos = [c + r * np.array([np.cos(TAU * i / 23 + PI / 2), np.sin(TAU * i / 23 + PI / 2), 0])
               for i in range(23)]
        people = VGroup(*[Dot(p, radius=0.1, color=RLBLUE) for p in pos])
        me = [Line(pos[0], pos[j], color=HILITE, stroke_width=2.5) for j in range(1, 23)]
        allp = VGroup(*[Line(pos[i], pos[j], color="#8C88F0", stroke_width=1.3, stroke_opacity=0.6)
                        for i in range(23) for j in range(i + 1, 23)])
        assert len(allp) == PAIRS
        n_me = txt(label("me_vs_the_others_n", n_me=len(me)), size=28, color=HILITE)
        n_all = VGroup(txt(label("every_pair"), size=28),
                       MathTex(rf"\frac{{23\cdot 22}}{{2}} = {PAIRS}", font_size=52))
        n_all.arrange(DOWN, buff=0.3)
        VGroup(n_me, n_all).arrange(DOWN, buff=0.8).move_to([3.7, 0, 0])
        t = line("12.8")
        with self.voiceover(t) as tr:
            self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in people], lag_ratio=0.05), run_time=1.2)
            self.cue(tr, t, 1)
            self.play(people[0].animate.set_color(HILITE).scale(1.5),
                      LaggedStart(*[Create(l) for l in me], lag_ratio=0.04), FadeIn(n_me), run_time=1.4)
            self.cue(tr, t, 2)
            self.play(LaggedStart(*[Create(l) for l in allp], lag_ratio=0.004), FadeIn(n_all[0]), run_time=2.2)
            self.play(FadeIn(n_all[1], shift=UP * 0.2), run_time=0.6)
            self.cue(tr, t, 3)
            self.play(Indicate(n_all[1], color=HILITE), run_time=1.0)
        self.wait(0.6)
        self.clear_all()


class S12HandsOn(LectureScene):
    def construct(self):
        ax, labs = bday_axes()
        curve = curve_part(ax, 1, 70)
        half = DashedLine(ax.c2p(0, 0.5), ax.c2p(70, 0.5), color=GREY_B, stroke_width=2)
        m23 = marker(ax, 23)
        uses = VGroup(txt(label("hash_collisions"), size=26, color=HILITE),
                      txt(label("duplicate_records"), size=26, color=HILITE))
        uses.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        uses_box = SurroundingRectangle(uses, buff=0.25, color=HILITE, corner_radius=0.12)
        uses_g = VGroup(uses_box, uses).move_to(ax.c2p(47, 0.27))
        t = line("12.9")
        with self.voiceover(t) as tr:
            self.play(FadeIn(ax), FadeIn(labs), Create(curve), Create(half), FadeIn(m23), run_time=1.4)
            self.play(FadeIn(uses_g, shift=UP * 0.2), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(Indicate(m23[1], scale_factor=2.0, color=RLRED), run_time=0.8)

        card = pause_card([label("a_class_of_30_what_is_q"),
                           label("we_read_it_off_the_curve")])
        card.scale_to_fit_width(min(card.width, 5.9)).move_to([-3.75, 0.3, 0])
        with self.voiceover(line("12.10")):
            self.play(FadeOut(uses_g), FadeOut(m23), run_time=0.4)
            self.play(VGroup(ax, labs, curve, half).animate.scale(0.66).move_to([3.05, -0.4, 0]), run_time=0.9)
            self.play(FadeIn(card), run_time=0.7)
        self.hands_on()

        t = line("12.11")
        with self.voiceover(t) as tr:
            self.play(FadeOut(card), run_time=0.4)
            self.play(VGroup(ax, labs, curve, half).animate.scale(1 / 0.66).move_to(ORIGIN), run_time=0.8)
            m30 = marker(ax, 30, RLGREEN, UL)
            across = DashedLine(ax.c2p(0, BD[30]), ax.c2p(30, BD[30]), color=RLGREEN, stroke_width=2)
            self.play(Create(m30[0]), FadeIn(m30[1]), run_time=0.6)
            self.play(Create(across), FadeIn(m30[2]), run_time=0.7)

        # what "unrelated" assumed: two people, two independent days
        a, b = Dot([-2.5, -0.2, 0], radius=0.16, color=RLBLUE), Dot([2.5, -0.2, 0], radius=0.16, color=RLBLUE)
        la = txt(label("person_1"), size=24, color=GREY_B).next_to(a, DOWN, buff=0.25)
        lb = txt(label("person_2"), size=24, color=GREY_B).next_to(b, DOWN, buff=0.25)
        tie = DashedLine(a.get_right(), b.get_left(), color=HILITE, stroke_width=4)
        ask = txt(label("unrelated_q"), size=40, weight=BOLD, color=HILITE).next_to(tie, UP, buff=0.3)
        t = line("12.12")
        with self.voiceover(t) as tr:
            self.play(FadeOut(VGroup(ax, labs, curve, half, m30, across)), run_time=0.6)
            self.play(FadeIn(a), FadeIn(b), FadeIn(la), FadeIn(lb), run_time=0.6)
            self.cue(tr, t, 1)
            self.play(Create(tie), FadeIn(ask, shift=UP * 0.2), run_time=0.9)
        self.clear_all()


SCENES = ["S12Problem", "S12Curve", "S12Pairs", "S12HandsOn"]
