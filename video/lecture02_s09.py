"""Lecture 2, section 9 — what a positive test means: 10,000 people, 100 ill, 495 false alarms."""
import numpy as np
from lecture02_kit import *

S1, S10 = N["screen"], N["screen_1in10"]
FP_RATE = S1["false_pos"] / S1["healthy"]           # 0.05, the test's false-alarm rate
ILL_C, FALSE_C, WELL_C = RLRED, RLORANGE, "#2F5557"   # healthy people stay dim so the positives stand out


def num(n):
    return f"{n:,}"


def pct(x):
    return f"{round(100 * x)}%"


def ptx(a, b, size=44, color=WHITE):
    """P(a | b) with two short words (no ʻ/ʼ, which LaTeX cannot set)."""
    return MathTex(rf"P(\text{{{a}}} \mid \text{{{b}}})", font_size=size, color=color)


POS, ILL = w("positive", "musbat"), w("ill", "kasal")


def people_image(ill, false_pos, height=5.0, cols=100):
    """All the tested people as one image, one cell per person: ill first (red), then the false
    alarms (orange), then everyone else (dim green). 10,000 squares as one bitmap, not 10,000 objects."""
    total = S1["tested"]
    rows = total // cols
    colours = np.empty((total, 3), dtype=np.uint8)
    hexrgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
    colours[:] = hexrgb(WELL_C)
    colours[:ill] = hexrgb(ILL_C)
    colours[ill:ill + false_pos] = hexrgb(FALSE_C)
    k, gap = 16, 3                                      # pixels per cell, of which the last few stay black;
    img = np.zeros((rows * k, cols * k, 3), dtype=np.uint8)   # fine enough to scale smoothly without moiré
    grid = colours.reshape(rows, cols, 3)
    for dy in range(k - gap):
        for dx in range(k - gap):
            img[dy::k, dx::k] = grid
    m = ImageMobject(img)
    m.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
    m.set_height(height)
    return m


def positives_bar(ill, false_pos, width=10.0, height=0.9):
    """The positives magnified into one bar: the truly ill, then the false alarms."""
    total = ill + false_pos
    a = Rectangle(width=width * ill / total, height=height, stroke_width=0, fill_color=ILL_C, fill_opacity=1)
    b = Rectangle(width=width * false_pos / total, height=height, stroke_width=0, fill_color=FALSE_C, fill_opacity=1)
    VGroup(a, b).arrange(RIGHT, buff=0)
    la = txt(f"{num(ill)} {w('ill', 'kasal')}", size=26, weight=BOLD).next_to(a, DOWN, buff=0.2)
    lb = txt(f"{num(false_pos)} {w('false alarms', 'yolgʻon signal')}", size=26, weight=BOLD).next_to(b, DOWN, buff=0.2)
    if la.get_right()[0] > lb.get_left()[0] - 0.2:      # a thin red slice: keep its label clear of the orange one
        la.next_to(a, UP, buff=0.2)
    return VGroup(a, b), VGroup(la, lb)


class S09Reverse(LectureScene):
    def construct(self):
        self.section_card(9)
        # the test is checked on people already known to be ill
        sick = VGroup(*[Dot(radius=0.13, color=ILL_C) for _ in range(9)]).arrange_in_grid(3, 3, buff=0.18)
        sick_l = txt(w("known to be ill", "kasalligi aniq"), size=24, color=GREY_B).next_to(sick, DOWN, buff=0.2)
        tube = node(w("test", "test"), color=LBLUE, size=28)
        plus = txt("+", size=60, weight=BOLD, color=HILITE)
        row1 = VGroup(VGroup(sick, sick_l), tube, plus).arrange(RIGHT, buff=1.1).move_to(UP * 1.7)
        arrows1 = VGroup(Arrow(row1[0].get_right(), tube.get_left(), buff=0.2, color=GREY_B),
                         Arrow(tube.get_right(), plus.get_left(), buff=0.2, color=GREY_B))
        have = ptx(POS, ILL, color=LBLUE)
        have_l = txt(w("a property of the test", "testning xususiyati"), size=26, color=LBLUE)
        have_g = VGroup(have, have_l).arrange(DOWN, buff=0.2).move_to(LEFT * 3.3 + DOWN * 1.2)
        with self.say("9.1") as (tr, t):
            self.play(FadeIn(row1[0]), run_time=0.6)
            self.play(GrowArrow(arrows1[0]), FadeIn(tube), run_time=0.6)
            self.play(GrowArrow(arrows1[1]), FadeIn(plus, scale=1.4), run_time=0.6)
            self.cue(tr, t, {"en": "That gives us", "uz": "Bu bizga"})
            self.play(Write(have), run_time=0.9)
            self.play(FadeIn(have_l), run_time=0.5)

        want = ptx(ILL, POS, color=HILITE)
        want_l = txt(w("what the patient wants", "bemorga kerak"), size=26, color=HILITE)
        want_g = VGroup(want, want_l).arrange(DOWN, buff=0.2).move_to(RIGHT * 3.3 + DOWN * 1.2)
        swap = CurvedArrow(have.get_top() + UP * 0.1, want.get_top() + UP * 0.1, angle=-PI / 3, color=GREY_B)
        base = txt(w("+ how common the illness is", "+ kasallik qanchalik keng tarqalgani"), size=24,
                   color=GREY_B).next_to(want_g, DOWN, buff=0.3)
        with self.say("9.2") as (tr, t):
            self.play(Create(swap), run_time=0.8)
            self.play(Write(want), FadeIn(want_l), run_time=0.9)
            self.cue(tr, t, {"en": "And that also", "uz": "U kasallik"})
            self.play(FadeIn(base, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        # the prosecutor's fallacy
        head = self.heading(w("The prosecutor's fallacy", "Prokuror xatosi"), color=RLRED)
        quote = txt(w("“Only 1 innocent person in a million would match”",
                      "«Million begunoh odamdan faqat bittasi mos keladi»"), size=30)
        quote.next_to(head, DOWN, buff=0.7)
        match, innocent = w("match", "moslik"), w("innocent", "begunoh")
        said = ptx(match, innocent, size=48, color=LBLUE)
        neq = MathTex(r"\neq", font_size=60, color=RLRED)
        meant = ptx(innocent, match, size=48, color=HILITE)
        eqs = VGroup(said, neq, meant).arrange(RIGHT, buff=0.5).next_to(quote, DOWN, buff=0.9)
        cross = Cross(meant, stroke_color=RLRED, stroke_width=6).scale(0.9)
        with self.say("9.3") as (tr, t):
            self.play(FadeIn(head), run_time=0.6)
            self.cue(tr, t, {"en": "\"Only one", "uz": "«Million"})
            self.play(FadeIn(quote, shift=UP * 0.2), run_time=0.8)
            self.cue(tr, t, {"en": "is the chance of a match", "uz": "degani"})
            self.play(Write(said), run_time=0.8)
            self.cue(tr, t, {"en": "not the chance", "uz": "mos kelgandagi"})
            self.play(FadeIn(neq), Write(meant), run_time=0.8)
        self.clear_all()


class S09Count(LectureScene):
    def construct(self):
        # 10,000 tested: 100 ill, 9,900 healthy
        img = people_image(S1["ill"], 0).move_to(LEFT * 2.6 + DOWN * 0.15)
        side = VGroup(
            txt(w(f"{num(S1['tested'])} people tested", f"{num(S1['tested'])} kishi tekshirildi"), size=30, weight=BOLD),
            VGroup(Square(0.3, stroke_width=0, fill_color=ILL_C, fill_opacity=1),
                   txt(f"{num(S1['ill'])} {w('ill', 'kasal')}", size=28)).arrange(RIGHT, buff=0.2),
            VGroup(Square(0.3, stroke_width=0, fill_color=WELL_C, fill_opacity=1),
                   txt(f"{num(S1['healthy'])} {w('healthy', 'sogʻlom')}", size=28)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(RIGHT * 3.6 + UP * 1.0)
        rate = txt(w(f"1 in {S1['tested'] // S1['ill']} is ill", f"{S1['tested'] // S1['ill']} kishidan biri kasal"),
                   size=26, color=GREY_B).next_to(side, UP, buff=0.4, aligned_edge=LEFT)
        with self.say("9.4") as (tr, t):
            self.play(FadeIn(rate), run_time=0.5)
            self.cue(tr, t, {"en": "We test", "uz": "Oʻn ming"})
            self.play(FadeIn(img), FadeIn(side[0]), run_time=1.0)
            self.cue(tr, t, {"en": "one hundred are ill", "uz": "yuztasi kasal"})
            tl = img.get_corner(UL)
            ptr = Arrow(tl + LEFT * 1.0 + DOWN * 0.03, tl + LEFT * 0.05 + DOWN * 0.03, buff=0, color=ILL_C,
                        stroke_width=5, max_tip_length_to_length_ratio=0.3)
            self.play(FadeIn(side[1]), GrowArrow(ptr), run_time=0.5)
            self.cue(tr, t, {"en": "nine thousand", "uz": "toʻqqiz ming"})
            self.play(FadeIn(side[2]), run_time=0.5)

        # the test catches every ill person, and flags 5 % of the healthy too
        img2 = people_image(S1["ill"], S1["false_pos"]).move_to(img)
        fa = VGroup(Square(0.3, stroke_width=0, fill_color=FALSE_C, fill_opacity=1),
                    txt(f"{num(S1['false_pos'])} {w('false alarms', 'yolgʻon signal')}", size=28)).arrange(RIGHT, buff=0.2)
        fa.next_to(side, DOWN, buff=0.4, aligned_edge=LEFT)
        five = MathTex(rf"{pct(FP_RATE)[:-1]}\% \times {num(S1['healthy'])} = {num(S1['false_pos'])}".replace(",", "{,}"),
                       font_size=38, color=FALSE_C).next_to(fa, DOWN, buff=0.4, aligned_edge=LEFT)
        with self.say("9.5") as (tr, t):
            self.play(Indicate(side[1], color=ILL_C, scale_factor=1.05), run_time=0.8)
            self.cue(tr, t, {"en": "But it also", "uz": "Lekin u"})
            self.play(FadeIn(img2), run_time=1.0)
            self.add(img2)
            self.remove(img)
            self.play(FadeIn(fa), Write(five), run_time=0.9)

        # the positives, magnified
        bar, labs = positives_bar(S1["ill"], S1["false_pos"])
        bgroup = VGroup(bar, labs).move_to(DOWN * 1.2)
        head = txt(w(f"{num(S1['positives'])} test positive", f"{num(S1['positives'])} kishi musbat"),
                   size=34, weight=BOLD).next_to(bar, UP, buff=0.9)
        ppv = MathTex(rf"\frac{{{S1['ill']}}}{{{S1['positives']}}} \approx {pct(S1['ppv'])[:-1]}\%",
                      font_size=56, color=HILITE).next_to(head, UP, buff=0.5)
        with self.say("9.6") as (tr, t):
            self.play(FadeOut(VGroup(side, fa, five, rate)), img2.animate.scale(0.5).to_corner(UL, buff=SAFE + 0.2),
                      run_time=0.8)
            self.play(FadeIn(head), GrowFromEdge(bar, LEFT), run_time=1.0)
            self.play(FadeIn(labs), run_time=0.5)
            self.cue(tr, t, {"en": "Only one hundred", "uz": "Ulardan faqat"})
            self.play(Indicate(bar[0], color=ILL_C, scale_factor=1.1), run_time=0.8)
            self.cue(tr, t, {"en": "One hundred out of", "uz": "Besh yuz toʻqson beshdan"})
            self.play(Write(ppv), run_time=0.9)
        self.clear_all()

        # why: 5 % of a huge group beats 100 % of a tiny one
        k = 2.9 / S1["false_pos"]
        floor = -2.5
        big = Rectangle(width=1.6, height=S1["false_pos"] * k, stroke_width=0, fill_color=FALSE_C, fill_opacity=1)
        small = Rectangle(width=1.6, height=S1["ill"] * k, stroke_width=0, fill_color=ILL_C, fill_opacity=1)
        big.move_to([-2.2, floor + big.height / 2, 0])
        small.move_to([2.2, floor + small.height / 2, 0])
        lb = txt(w(f"{pct(FP_RATE)} of {num(S1['healthy'])}", f"{num(S1['healthy'])} ning {pct(FP_RATE)} i"),
                 size=28).next_to(big, DOWN, buff=0.25)
        ls = txt(w(f"100% of {num(S1['ill'])}", f"{num(S1['ill'])} ning 100% i"), size=28).next_to(small, DOWN, buff=0.25)
        vb = txt(num(S1["false_pos"]), size=34, weight=BOLD).next_to(big, UP, buff=0.15)
        vs = txt(num(S1["ill"]), size=34, weight=BOLD).next_to(small, UP, buff=0.15)
        ratio = txt(w(f"healthy : ill = {N['healthy_per_ill']:g} : 1", f"sogʻlom : kasal = {N['healthy_per_ill']:g} : 1"),
                    size=30, color=GREY_B).to_edge(UP, buff=SAFE + 0.4)
        per = VGroup(*[Dot(radius=0.14, color=FALSE_C) for _ in range(round(N["false_per_real"]))],
                     Dot(radius=0.14, color=ILL_C)).arrange(RIGHT, buff=0.18)
        per_l = txt(w(f"≈ {round(N['false_per_real'])} false alarms per real case",
                      f"har bir haqiqiy holatga ≈ {round(N['false_per_real'])} yolgʻon signal"), size=28)
        per_g = VGroup(per, per_l).arrange(RIGHT, buff=0.4).next_to(ratio, DOWN, buff=0.3)
        with self.say("9.7") as (tr, t):
            self.cue(tr, t, {"en": "Five percent", "uz": "Katta guruhning"})
            self.play(GrowFromEdge(big, DOWN), FadeIn(lb), FadeIn(vb), run_time=0.9)
            self.play(GrowFromEdge(small, DOWN), FadeIn(ls), FadeIn(vs), run_time=0.7)
            self.cue(tr, t, {"en": "Healthy people", "uz": "Sogʻlomlar"})
            self.play(FadeIn(ratio), run_time=0.6)
            self.cue(tr, t, {"en": "so there are", "uz": "shuning uchun"})
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in per], lag_ratio=0.15), FadeIn(per_l), run_time=1.0)
        self.clear_all()


class S09Fraud(LectureScene):
    def construct(self):
        # a stream of card payments; the detector raises alarms, and most of them are false
        n, flagged, fraud = 40, {3, 9, 16, 22, 29, 35}, {22}
        cards = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.42, height=0.28, stroke_color=GREY_B,
                                          stroke_width=1.5, fill_color=RLRED if i in fraud else GREY_E, fill_opacity=1)
                         for i in range(n)]).arrange_in_grid(4, 10, buff=(0.3, 0.45)).move_to(DOWN * 0.3)
        bells = VGroup(*[Triangle(color=FALSE_C if i not in fraud else RLRED, fill_opacity=1, stroke_width=0)
                         .scale(0.13).next_to(cards[i], UP, buff=0.06) for i in sorted(flagged)])
        head = self.heading(w("Fraud detector", "Firibgarlikni aniqlovchi model"), color=LBLUE)
        tally = txt(w(f"{len(flagged)} alarms, {len(fraud)} real fraud", f"{len(flagged)} ta signal, {len(fraud)} tasi haqiqiy"),
                    size=28, color=FALSE_C).next_to(cards, DOWN, buff=0.5)
        note = info(w("illustration", "tasvir uchun"))
        with self.say("9.8") as (tr, t):
            self.play(FadeIn(head), LaggedStart(*[FadeIn(c) for c in cards], lag_ratio=0.02), FadeIn(note), run_time=1.2)
            self.cue(tr, t, {"en": "because fraud", "uz": "firibgarlik kamdan-kam"})
            self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.15) for b in bells], lag_ratio=0.15), run_time=1.0)
            self.play(FadeIn(tally), run_time=0.5)
        self.clear_all()


class S09HandsOn(LectureScene):
    def construct(self):
        card = pause_card([w(f"1 person in {S10['tested'] // S10['ill']} has the disease.",
                             f"{S10['tested'] // S10['ill']} kishidan biri kasal."),
                           w(f"Same test: never misses, {pct(FP_RATE)} false alarms.",
                             f"Test oʻsha: kasalni oʻtkazib yubormaydi, {pct(FP_RATE)} yolgʻon signal."),
                           w("P(ill | positive) = ?", "P(kasal | musbat) = ?")])
        with self.say("9.9"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        img = people_image(S10["ill"], S10["false_pos"], height=4.2).move_to(LEFT * 3.9 + UP * 0.6)
        rows = VGroup(
            txt(w(f"{num(S10['ill'])} ill", f"{num(S10['ill'])} kasal"), size=28, color=ILL_C),
            txt(w(f"{num(S10['healthy'])} healthy", f"{num(S10['healthy'])} sogʻlom"), size=28, color=GREY_B),
            MathTex(rf"{pct(FP_RATE)[:-1]}\% \times {num(S10['healthy'])} = {num(S10['false_pos'])}".replace(",", "{,}"),
                    font_size=36, color=FALSE_C),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 2.6 + UP * 1.6)
        bar, labs = positives_bar(S10["ill"], S10["false_pos"], width=6.6, height=0.7)
        bgroup = VGroup(bar, labs).move_to(RIGHT * 2.6 + DOWN * 2.2)
        ppv = MathTex(rf"\frac{{{num(S10['ill'])}}}{{{num(S10['positives'])}}} \approx {pct(S10['ppv'])[:-1]}\%".replace(",", "{,}"),
                      font_size=50, color=HILITE).move_to(RIGHT * 2.6 + DOWN * 0.2)
        with self.say("9.10") as (tr, t):
            self.play(FadeIn(img), FadeIn(rows[0]), FadeIn(rows[1]), run_time=0.9)
            self.cue(tr, t, {"en": "False alarms", "uz": "Yolgʻon signallar"})
            self.play(Write(rows[2]), run_time=0.8)
            self.cue(tr, t, {"en": "A thousand out of", "uz": "Bir ming toʻrt yuz ellikdan"})
            self.play(GrowFromEdge(bar, LEFT), FadeIn(labs), run_time=0.8)
            self.play(Write(ppv), run_time=0.8)
        self.clear_all()

        # same test, two base rates
        cases = [(S1, w("1 in 100", "100 kishidan 1")), (S10, w("1 in 10", "10 kishidan 1"))]
        floor, hk = -2.0, 3.6
        bars = VGroup()
        for i, (s, lab) in enumerate(cases):
            b = Rectangle(width=1.8, height=hk * s["ppv"], stroke_width=0, fill_color=HILITE, fill_opacity=1)
            b.move_to([-2.0 + 4.0 * i, floor + b.height / 2, 0])
            bars.add(VGroup(b, txt(pct(s["ppv"]), size=40, weight=BOLD).next_to(b, UP, buff=0.15),
                            txt(lab, size=28, color=GREY_B).next_to(b, DOWN, buff=0.25)))
        same = txt(w("the same test", "test oʻsha-oʻsha"), size=32, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.5)
        yl = txt("P(kasal | musbat)" if LANG == "uz" else "P(ill | positive)", size=26, color=GREY_B).next_to(same, DOWN, buff=0.3)
        with self.say("9.11") as (tr, t):
            self.play(FadeIn(same), FadeIn(yl), run_time=0.6)
            self.play(LaggedStart(*[GrowFromEdge(b[0], DOWN) for b in bars], lag_ratio=0.3),
                      LaggedStart(*[FadeIn(VGroup(b[1], b[2])) for b in bars], lag_ratio=0.3), run_time=1.2)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S09Reverse", "S09Count", "S09Fraud", "S09HandsOn"]
