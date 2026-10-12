"""Lecture 2, section 6 — Simpson's paradox: Berkeley graduate admissions, autumn 1973."""
from lecture02_kit import *

B = N["berkeley"]
DEPTS = list(B["dept"])
MEN_C, WOM_C = LBLUE, HILITE
MEN, WOMEN = label("men"), label("women")


def pct(x):
    return f"{round(100 * x)}%"


BASE, H = -2.3, 3.9            # bar floor and the height of 100 %


def vbar(rate, x, color, width=0.5, show=True, size=20):
    bar = Rectangle(width=width, height=max(rate * H, 1e-3), stroke_width=0, fill_color=color, fill_opacity=1)
    bar.move_to([x, BASE + rate * H / 2, 0])
    lab = txt(pct(rate), size=size, weight=BOLD, color=color).next_to(bar, UP, buff=0.08)
    return VGroup(bar, lab)


def rate_color(r):
    """Green for an easy department, red for a hard one, by its admission rate over both sexes."""
    return interpolate_color(ManimColor(RLRED), ManimColor(RLGREEN), min(r / 0.65, 1.0))


class S06Pooled(LectureScene):
    def construct(self):
        self.section_card(6)
        head = self.heading(label("berkeley_autumn_1973"), color=LBLUE)
        sub = txt(label("graduate_admissions_six_largest_departments"),
                  size=24, color=GREY_B).next_to(head, DOWN, buff=0.15)
        floor = Line([-2.0, BASE, 0], [2.0, BASE, 0], color=GREY_B, stroke_width=2)
        men = vbar(B["men_rate"], -0.85, MEN_C, width=1.1, size=34)
        wom = vbar(B["women_rate"], 0.85, WOM_C, width=1.1, size=34)
        ml = txt(MEN, size=26, color=MEN_C).next_to([-0.85, BASE, 0], DOWN, buff=0.2)
        wl = txt(WOMEN, size=26, color=WOM_C).next_to([0.85, BASE, 0], DOWN, buff=0.2)
        with self.say("6.1") as (tr, t):
            self.play(FadeIn(head), FadeIn(sub), run_time=0.7)
            self.cue(tr, t, {"en": "In the six largest", "uz": "Eng katta oltita"})
            self.play(Create(floor), GrowFromEdge(men[0], DOWN), FadeIn(men[1]), FadeIn(ml), run_time=0.8)
            self.play(GrowFromEdge(wom[0], DOWN), FadeIn(wom[1]), FadeIn(wl), run_time=0.8)

        pooled = VGroup(floor, men, wom, ml, wl)
        all_lab = txt(label("all_six"), size=22, color=GREY_B)
        with self.say("6.2") as (tr, t):
            self.play(Indicate(VGroup(men, wom), color=WHITE, scale_factor=1.05), run_time=0.8)
            self.cue(tr, t, {"en": "But let's look", "uz": "Lekin"})
            self.play(FadeOut(sub), pooled.animate.scale(0.62).move_to([-5.2, -0.9, 0]), run_time=0.9)
            all_lab.next_to(pooled, UP, buff=0.25)
            self.play(FadeIn(all_lab), run_time=0.4)

        # six departments, men and women side by side
        xs = [-2.6 + 1.6 * i for i in range(6)]
        dfloor = Line([-3.4, BASE, 0], [6.4, BASE, 0], color=GREY_B, stroke_width=2)
        pairs = VGroup()
        for d, x in zip(DEPTS, xs):
            v = B["dept"][d]
            m = vbar(v["men_rate"], x - 0.34, MEN_C, width=0.5, size=18)
            wo = vbar(v["women_rate"], x + 0.34, WOM_C, width=0.5, size=18)
            lab = txt(d, size=28, weight=BOLD).next_to([x, BASE, 0], DOWN, buff=0.2)
            pairs.add(VGroup(m, wo, lab))
        leg = legend([(MEN_C, MEN), (WOM_C, WOMEN)], size=22).next_to(head, DOWN, buff=0.25)

        with self.say("6.3") as (tr, t):
            self.play(Create(dfloor), FadeIn(leg), run_time=0.5)
            self.play(LaggedStart(*[AnimationGroup(GrowFromEdge(p[0][0], DOWN), GrowFromEdge(p[1][0], DOWN),
                                                   FadeIn(p[0][1]), FadeIn(p[1][1]), FadeIn(p[2]))
                                    for p in pairs], lag_ratio=0.15), run_time=1.8)
            self.cue(tr, t, {"en": "In department A", "uz": "Ey fakultetida"})
            a_box = SurroundingRectangle(pairs[0], buff=0.12, color=WHITE, stroke_width=3)
            self.play(Create(a_box), run_time=0.5)
            self.cue(tr, t, {"en": "In four of the six", "uz": "Oltita fakultetdan"})
            boxes = VGroup(*[SurroundingRectangle(pairs[DEPTS.index(d)][1], buff=0.08, color=RLGREEN, stroke_width=4)
                             for d in B["women_higher"]])
            self.play(FadeOut(a_box), LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.2), run_time=1.0)
        self.clear_all()


class S06Applicants(LectureScene):
    """Where each sex applied: one strip per sex, widths by applicants, colour by how easy the department was."""

    def construct(self):
        X0, W = -4.4, 10.6
        heads = self.heading(label("where_they_applied"), color=LBLUE)

        def strip(sex, y, color, name):
            n_all = B[f"{sex}_applied"]
            segs, x = VGroup(), X0
            for d in DEPTS:
                n = B["dept"][d][f"{sex}_applied"]
                wd = W * n / n_all
                r = Rectangle(width=wd, height=0.9, stroke_color=BLACK, stroke_width=2,
                              fill_color=rate_color(B["dept"][d]["all_rate"]), fill_opacity=1)
                r.move_to([x + wd / 2, y, 0])
                lab = txt(d, size=24, weight=BOLD, color=BLACK).move_to(r) if wd > 0.45 else VGroup()
                segs.add(VGroup(r, lab))
                x += wd
            name_t = txt(name, size=26, weight=BOLD, color=color).next_to([X0, y, 0], LEFT, buff=0.25)
            return segs, name_t

        mseg, mname = strip("men", 0.9, MEN_C, MEN)
        wseg, wname = strip("women", -1.4, WOM_C, WOMEN)
        ramp = VGroup(*[Rectangle(width=0.2, height=0.22, stroke_width=0, fill_color=rate_color(0.65 * k / 10),
                                  fill_opacity=1) for k in range(11)]).arrange(RIGHT, buff=0)
        scale = VGroup(txt(label("hard"), size=20, color=RLRED), ramp,
                       txt(label("easy"), size=20, color=RLGREEN)).arrange(RIGHT, buff=0.2)
        scale_cap = txt(label("admission_rate"), size=20, color=GREY_B)
        key = VGroup(scale_cap, scale).arrange(DOWN, buff=0.1).next_to(heads, DOWN, buff=0.25)

        ab = VGroup(mseg[0], mseg[1])
        with self.say("6.4") as (tr, t):
            self.play(FadeIn(heads), FadeIn(key), run_time=0.6)
            self.play(FadeIn(mname), LaggedStart(*[GrowFromEdge(s, LEFT) for s in mseg], lag_ratio=0.1), run_time=1.2)
            self.cue(tr, t, {"en": "Over half the men", "uz": "Erkaklarning yarmidan"})
            br = Brace(ab, DOWN, color=MEN_C)
            share = txt(pct(B["men_share_AB"]), size=26, weight=BOLD, color=MEN_C).next_to(br, DOWN, buff=0.08)
            self.play(GrowFromCenter(br), FadeIn(share), run_time=0.7)
            self.cue(tr, t, {"en": "which admitted", "uz": "Bu fakultetlar"})
            rates = VGroup(*[txt(f"{B['all_pct'][d]}%", size=24, weight=BOLD, color=RLGREEN).next_to(mseg[i], UP, buff=0.1)
                             for i, d in enumerate("AB")])
            self.play(FadeIn(rates, shift=DOWN * 0.1), run_time=0.6)

        cef = [DEPTS.index(d) for d in "CEF"]
        with self.say("6.5") as (tr, t):
            self.play(FadeIn(wname), LaggedStart(*[GrowFromEdge(s, LEFT) for s in wseg], lag_ratio=0.1), run_time=1.2)
            outl = VGroup(*[SurroundingRectangle(wseg[i][0], buff=0.03, color=WHITE, stroke_width=4) for i in cef])
            share = txt(pct(B["women_share_CEF"]), size=26, weight=BOLD, color=WOM_C).next_to(wname, DOWN, buff=0.15)
            self.play(Create(outl), FadeIn(share), run_time=0.8)
            self.cue(tr, t, {"en": "which admitted", "uz": "Ular oʻttiz"})
            rates = VGroup(*[txt(f"{B['all_pct'][DEPTS[i]]}%", size=24, weight=BOLD, color=RLRED)
                             .next_to(wseg[i], DOWN, buff=0.12) for i in cef])
            self.play(FadeIn(rates, shift=UP * 0.1), run_time=0.6)

        name = txt(label("simpson_s_paradox"), size=40, weight=BOLD, color=HILITE)
        with self.say("6.6") as (tr, t):
            self.play(Indicate(VGroup(mseg, wseg), color=WHITE, scale_factor=1.03), run_time=1.0)
            self.cue(tr, t, {"en": "This is called", "uz": "Bu Simpson"})
            name.move_to(heads)
            self.play(FadeOut(heads), FadeIn(name, scale=1.2), run_time=0.7)
        self.clear_all()


class S06TwoQuestions(LectureScene):
    def construct(self):
        def panel(rates, caption, x):
            floor = Line([x - 1.3, BASE + 0.6, 0], [x + 1.3, BASE + 0.6, 0], color=GREY_B, stroke_width=2)
            bars = VGroup()
            for k, (r, c) in enumerate(zip(rates, (MEN_C, WOM_C))):
                bar = Rectangle(width=0.8, height=r * 3.2, stroke_width=0, fill_color=c, fill_opacity=1)
                bar.move_to([x + (k - 0.5) * 1.1, BASE + 0.6 + r * 1.6, 0])
                bars.add(VGroup(bar, txt(pct(r), size=26, weight=BOLD, color=c).next_to(bar, UP, buff=0.08)))
            cap = txt(caption, size=28, weight=BOLD).next_to(floor, DOWN, buff=0.3)
            return VGroup(floor, bars, cap)

        a = B["dept"]["A"]
        left = panel([B["men_rate"], B["women_rate"]], label("overall"), -3.2)
        right = panel([a["men_rate"], a["women_rate"]], label("within_one_department"), 3.2)
        dlab = txt("A", size=26, weight=BOLD, color=GREY_B).next_to(right[1], UP, buff=0.25)
        leg = legend([(MEN_C, MEN), (WOM_C, WOMEN)], size=22).to_edge(UP, buff=SAFE + 0.4)
        checks = VGroup(*[txt("✓", size=48, weight=BOLD, color=RLGREEN).next_to(p[2], DOWN, buff=0.2)
                          for p in (left, right)])
        with self.say("6.7") as (tr, t):
            self.play(FadeIn(leg), FadeIn(left), FadeIn(right), FadeIn(dlab), run_time=1.0)
            self.play(FadeIn(checks, scale=1.3), run_time=0.6)
            self.cue(tr, t, {"en": "the chance of admission overall", "uz": "umuman qabul"})
            self.play(Indicate(left[2], color=HILITE), run_time=0.7)
            self.cue(tr, t, {"en": "and the chance within", "uz": "bitta fakultet ichidagi"})
            self.play(Indicate(right[2], color=HILITE), run_time=0.7)
        self.clear_all()


class S06PooledModel(LectureScene):
    """AI: a model fitted to pooled data learns a trend that holds in no group (an illustration)."""

    def construct(self):
        ax = Axes(x_range=[0, 10, 2], y_range=[0, 10, 2], x_length=6.4, y_length=4.2, tips=False,
                  axis_config={"color": GREY_B, "include_ticks": False}).move_to([-1.2, -0.3, 0])
        g1 = [(1, 6.0), (1.8, 6.8), (2.6, 7.3), (3.4, 8.1), (4.2, 8.8)]
        g2 = [(5.6, 1.4), (6.4, 2.1), (7.2, 2.8), (8.0, 3.4), (8.8, 4.2)]
        d1 = VGroup(*[Dot(ax.c2p(x, y), radius=0.09, color=LBLUE) for x, y in g1])
        d2 = VGroup(*[Dot(ax.c2p(x, y), radius=0.09, color=HILITE) for x, y in g2])
        l1 = Line(ax.c2p(0.6, 5.6), ax.c2p(4.6, 9.2), color=LBLUE, stroke_width=4)
        l2 = Line(ax.c2p(5.2, 1.0), ax.c2p(9.2, 4.6), color=HILITE, stroke_width=4)
        pooled = DashedLine(ax.c2p(0.5, 8.8), ax.c2p(9.5, 1.8), color=RLRED, stroke_width=5)
        tag1 = txt(label("group_1"), size=22, color=LBLUE).next_to(l1, UP, buff=0.1)
        tag2 = txt(label("group_2"), size=22, color=HILITE).next_to(l2, UP, buff=0.1)
        ptag = txt(label("pooled_model"), size=24, color=RLRED).move_to(ax.c2p(7.6, 7.6))
        note = info(label("illustration"))
        q = VGroup(txt("?", size=80, weight=BOLD, color=HILITE),
                   txt(label("how_were_the_data_selected_q"), size=26))
        q.arrange(DOWN, buff=0.2).move_to([4.6, 0.2, 0])
        if q.get_right()[0] > 6.5:
            q.shift(LEFT * (q.get_right()[0] - 6.5))
        with self.say("6.8") as (tr, t):
            self.play(Create(ax), FadeIn(d1), FadeIn(d2), FadeIn(note), run_time=0.9)
            self.play(Create(pooled), FadeIn(ptag), run_time=0.8)
            self.play(Create(l1), Create(l2), FadeIn(tag1), FadeIn(tag2), run_time=0.8)
            self.cue(tr, t, {"en": "So we always ask", "uz": "Shuning uchun doim"})
            self.play(VGroup(ax, d1, d2, l1, l2, pooled, tag1, tag2, ptag).animate.shift(LEFT * 1.0),
                      FadeIn(q, shift=LEFT * 0.2), run_time=0.8)
        self.clear_all()


def hospital(color):
    body = Rectangle(width=2.0, height=1.6, stroke_color=color, stroke_width=4)
    roof = Polygon(body.get_corner(UL), body.get_corner(UR), body.get_top() + UP * 0.6,
                   stroke_color=color, stroke_width=4)
    cross = VGroup(Rectangle(width=0.6, height=0.18, stroke_width=0, fill_color=RLRED, fill_opacity=1),
                   Rectangle(width=0.18, height=0.6, stroke_width=0, fill_color=RLRED, fill_opacity=1)).move_to(body)
    return VGroup(body, roof, cross)


class S06HandsOn(LectureScene):
    def construct(self):
        h1, h2 = hospital(LBLUE).move_to([-2.4, -1.0, 0]), hospital(HILITE).move_to([2.4, -1.0, 0])
        pc = pause_card([label("hospital_b_has_the_worse_overall"),
                         label("can_it_be_better_at_every_q")])
        pc.scale(0.78).to_edge(UP, buff=SAFE + 0.15)
        tags = VGroup(txt("A", size=30, weight=BOLD, color=LBLUE).next_to(h1, DOWN, buff=0.2),
                      txt("B", size=30, weight=BOLD, color=HILITE).next_to(h2, DOWN, buff=0.2))
        with self.say("6.9") as (tr, t):
            self.play(FadeIn(h1), FadeIn(h2), FadeIn(tags), run_time=0.7)
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(pc, shift=DOWN * 0.2), run_time=0.6)
        self.hands_on()

        hard = VGroup(*[Dot(radius=0.11, color=RLRED) for _ in range(8)]).arrange_in_grid(2, 4, buff=0.15)
        hard.next_to(h2, RIGHT, buff=0.35)
        hard_l = txt(label("hardest_cases"), size=24, color=RLRED).next_to(hard, DOWN, buff=0.2)
        hard_l.align_to(hard, LEFT)
        easy = VGroup(*[Dot(radius=0.11, color=RLGREEN) for _ in range(8)]).arrange_in_grid(2, 4, buff=0.15)
        easy.next_to(h1, LEFT, buff=0.35)
        yes = txt(label("yes"), size=44, weight=BOLD, color=RLGREEN).move_to([0, 1.6, 0])
        with self.say("6.10") as (tr, t):
            self.play(FadeOut(pc), FadeIn(yes, scale=1.3), run_time=0.6)
            self.cue(tr, t, {"en": "if it takes", "uz": "Agar u"})
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in hard], lag_ratio=0.08), FadeIn(hard_l),
                      LaggedStart(*[FadeIn(d, scale=0.5) for d in easy], lag_ratio=0.08), run_time=1.0)
        self.clear_all()

        # Part 0 closes; Part 1 opens on weighting each group's answer by its size
        done = VGroup(txt("✓", size=48, weight=BOLD, color=RLGREEN), txt(PARTS[0], size=34)).arrange(RIGHT, buff=0.3)
        done.move_to([0, 2.2, 0])
        if done.width > 12.4:
            done.scale_to_fit_width(12.4)
        k = 4.6 / N["n"]
        floor_y = -2.0
        gb = Rectangle(width=N["bike"] * k, height=N["p_bus_given_bike"] * 2.6, stroke_width=0,
                       fill_color=BUS_C, fill_opacity=1)
        gn = Rectangle(width=N["nobike"] * k, height=N["p_bus_given_nobike"] * 2.6, stroke_width=0,
                       fill_color=BUS_C, fill_opacity=1)
        VGroup(gb, gn).arrange(RIGHT, buff=0.08, aligned_edge=DOWN).move_to([-2.6, floor_y, 0], aligned_edge=DOWN)
        gl = VGroup(txt(BIKE, size=22, color=GREY_B).next_to(gb, DOWN, buff=0.15),
                    txt(NOBIKE, size=22, color=GREY_B).next_to(gn, DOWN, buff=0.15))
        wts = VGroup(txt(STUDENTS.format(n=N["bike"]), size=22).next_to(gb, UP, buff=0.12),
                     txt(STUDENTS.format(n=N["nobike"]), size=22).next_to(gn, UP, buff=0.12))
        nxt = txt(PARTS[1], size=32, weight=BOLD, color=HILITE)
        nxt.next_to(VGroup(gb, gn), RIGHT, buff=1.0).set_y(-0.9)
        if nxt.get_right()[0] > 6.5:
            nxt.shift(LEFT * (nxt.get_right()[0] - 6.5))
        with self.say("6.11") as (tr, t):
            self.play(FadeIn(done, shift=UP * 0.2), run_time=0.7)
            self.cue(tr, t, {"en": "There is:", "uz": "Bor:"})
            self.play(GrowFromEdge(gb, DOWN), GrowFromEdge(gn, DOWN), FadeIn(gl), run_time=0.8)
            self.play(FadeIn(wts), run_time=0.5)
            self.cue(tr, t, {"en": "That is part one", "uz": "Buni birinchi qismda"})
            self.play(FadeIn(nxt, shift=LEFT * 0.2), run_time=0.6)
        self.clear_all()


SCENES = ["S06Pooled", "S06Applicants", "S06TwoQuestions", "S06PooledModel", "S06HandsOn"]
