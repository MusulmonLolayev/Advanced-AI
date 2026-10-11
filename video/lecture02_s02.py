"""Lecture 2, section 2 — tree diagrams: multiply along the branches.

Every number on screen comes from N (capture_l02.py, unit-tested by test_l02.py):
n, p_bike, p_bus_given_bike, p_bus_given_nobike, tree_paths, tree_counts, tree_sum, tree_reversed, cells.
"""
from lecture02_kit import *

PB, PBB, PBN = N["p_bike"], N["p_bus_given_bike"], N["p_bus_given_nobike"]
KEYS = [["bike_bus", "bike_nobus"], ["nobike_bus", "nobike_nobus"]]


def student_tree():
    return tree(STUDENTS.format(n=N["n"]), [(BIKE, PB), (NOBIKE, 1 - PB)],
                [[(BUS, PBB), (NOBUS, 1 - PBB)], [(BUS, PBN), (NOBUS, 1 - PBN)]])


def product(i, j, T, size=32):
    """'0.6 × 0.25 = 0.15 → 15' to the right of leaf (i, j)."""
    a = PB if i == 0 else 1 - PB
    b = [PBB, PBN][i] if j == 0 else 1 - [PBB, PBN][i]
    k = KEYS[i][j]
    m = MathTex(rf"{dec(a)} \times {dec(b)}", "=", dec(N["tree_paths"][k]), font_size=size)
    cnt = txt(f"→ {N['tree_counts'][k]}", size=size - 4, weight=BOLD, color=HILITE)
    g = VGroup(m, cnt).arrange(RIGHT, buff=0.3).next_to(T["n2"][i][j], RIGHT, buff=0.4)
    return g


class S02Tree(LectureScene):
    def construct(self):
        self.section_card(2)
        T = student_tree()
        s1 = txt(w("stage 1: bike?", "1-bosqich: velosiped"), size=24, color=GREY_B).move_to([-2.2, 3.25, 0])
        s2 = txt(w("stage 2: bus?", "2-bosqich: avtobus"), size=24, color=GREY_B).move_to([1.4, 3.25, 0])
        with self.say("2.1") as (tr, t):
            self.play(FadeIn(T["root"], shift=RIGHT * 0.3), run_time=0.6)
            self.cue(tr, t, {"en": "first", "uz": "avval"})
            self.play(FadeIn(s1), run_time=0.5)
            self.cue(tr, t, {"en": "then", "uz": "keyin"})
            self.play(FadeIn(s2), run_time=0.5)

        with self.say("2.2") as (tr, t):
            self.cue(tr, t, {"en": "Owns a bike", "uz": "Velosipedi bor"})
            self.play(Create(T["e1"][0]), FadeIn(T["n1"][0]), FadeIn(T["p1"][0]), run_time=0.8)
            self.cue(tr, t, {"en": "No bike", "uz": "yoʻq —"})
            self.play(Create(T["e1"][1]), FadeIn(T["n1"][1]), FadeIn(T["p1"][1]), run_time=0.8)

        with self.say("2.3") as (tr, t):
            for i in range(2):
                if i == 1:
                    self.cue(tr, t, 1)
                self.play(*[Create(T["e2"][i][j]) for j in range(2)], *[FadeIn(T["n2"][i][j]) for j in range(2)],
                          *[FadeIn(T["p2"][i][j]) for j in range(2)], run_time=0.9)

        rule = txt(w("multiply along the path", "yoʻl boʻylab koʻpaytiramiz"), size=30, weight=BOLD, color=HILITE)
        rule.move_to([-2.0, -3.25, 0])
        path = [T["e1"][0], T["e2"][0][0]]
        with self.say("2.4") as (tr, t):
            self.play(FadeIn(rule, shift=UP * 0.2), run_time=0.6)
            self.play(*[e.animate.set_stroke(HILITE, width=6) for e in path], run_time=0.7)

        prods = [[product(i, j, T) for j in range(2)] for i in range(2)]
        with self.say("2.5") as (tr, t):
            self.play(Indicate(T["p1"][0], color=WHITE), Indicate(T["p2"][0][0], color=WHITE), run_time=0.8)
            self.play(Write(prods[0][0][0]), run_time=0.9)
            self.cue(tr, t, {"en": "That is fifteen", "uz": "Yaʼni oʻn besh"})
            self.play(FadeIn(prods[0][0][1], shift=LEFT * 0.2), run_time=0.6)

        total = MathTex(" + ".join(dec(N["tree_paths"][k]) for row in KEYS for k in row), "=", dec(N["tree_sum"]),
                        font_size=40, color=HILITE).move_to([2.6, -3.25, 0])
        with self.say("2.6") as (tr, t):
            self.play(*[e.animate.set_stroke(GREY_B, width=2.5) for e in path], run_time=0.3)
            for i, j in ((0, 1), (1, 0), (1, 1)):
                self.play(FadeIn(prods[i][j], shift=LEFT * 0.2), run_time=0.5)
            self.cue(tr, t, 1)
            self.play(FadeOut(rule), Write(total), run_time=1.0)
        self.clear_all()


class S02LanguageModel(LectureScene):
    def construct(self):
        words = {"en": ("The", ("cat", ("sat", "ran")), ("dog", ("barked", "slept"))),
                 "uz": ("Bugun", ("havo", ("issiq", "sovuq")), ("men", ("keldim", "ketdim")))}[LANG]
        root = node(words[0], size=30).move_to([-4.6, 0.6, 0])
        lvl1, lvl2, e1, e2 = [], [], [], []
        for i, (wd, kids) in enumerate(words[1:]):
            n1 = node(wd, color=GREY_B, size=30).move_to([-1.4, 0.6 + (1.3 if i == 0 else -1.3), 0])
            lvl1.append(n1)
            e1.append(Line(root.get_right(), n1.get_left(), color=GREY_B, stroke_width=2.5))
            for j, k in enumerate(kids):
                n2 = node(k, color=GREY_B, size=30).move_to([1.9, n1.get_y() + (0.6 if j == 0 else -0.6), 0])
                lvl2.append(n2)
                e2.append(Line(n1.get_right(), n2.get_left(), color=GREY_B, stroke_width=2.5))
        f = MathTex(r"P(w_1, w_2, w_3)", "=", r"P(w_1)\,", r"P(w_2 \mid w_1)\,", r"P(w_3 \mid w_1, w_2)",
                    font_size=40).move_to([0, -2.6, 0])
        with self.say("2.7") as (tr, t):
            self.play(FadeIn(root), run_time=0.5)
            self.cue(tr, t, {"en": "each word", "uz": "har bir soʻz"})
            self.play(*[Create(e) for e in e1], *[FadeIn(n) for n in lvl1], run_time=0.7)
            self.play(*[Create(e) for e in e2], *[FadeIn(n) for n in lvl2], run_time=0.7)
            self.play(e1[0].animate.set_stroke(HILITE, width=6), lvl1[0][0].animate.set_stroke(HILITE),
                      e2[0].animate.set_stroke(HILITE, width=6), lvl2[0][0].animate.set_stroke(HILITE), run_time=0.7)
            self.cue(tr, t, {"en": "and the sentence", "uz": "gapning ehtimoli"})
            self.play(Write(f), run_time=1.2)
        self.clear_all()


class S02HandsOn(LectureScene):
    def construct(self):
        pc = pause_card([w("Bus first, then bike", "Avval avtobus, keyin velosiped"),
                         w("What goes on the first two branches?", "Birinchi ikki shoxda qanday sonlar turadi?")])
        pc.move_to([-2.6, 0.4, 0])
        if pc.width > 7.4:
            pc.scale_to_fit_width(7.4).move_to([-2.6, 0.4, 0])
        root = node(STUDENTS.format(n=N["n"]), size=26).move_to([2.6, 0, 0])
        ends = [node(BUS, size=26).move_to([5.3, 1.3, 0]), node(NOBUS, size=26).move_to([5.3, -1.3, 0])]
        edges = [Line(root.get_right(), e.get_left(), color=GREY_B, stroke_width=2.5) for e in ends]
        qs = [MathTex("?", font_size=40, color=HILITE).move_to(e.get_center() + (UP if k == 0 else DOWN) * 0.35)
              for k, e in enumerate(edges)]
        skeleton = VGroup(root, *ends, *edges, *qs)
        with self.say("2.8") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(pc, shift=UP * 0.2), run_time=0.7)
            self.cue(tr, t, {"en": "We draw", "uz": "Daraxtni teskari"})
            self.play(FadeIn(skeleton), run_time=0.8)
        self.hands_on()

        c, rv = N["cells"], N["tree_reversed"]
        ans = [MathTex(dec(rv["bus"]), font_size=40, color=HILITE).move_to(qs[0]),
               MathTex(dec(rv["nobus"]), font_size=40, color=HILITE).move_to(qs[1])]
        sum_ = MathTex(f"{c['bike_bus']} + {c['nobike_bus']}", "=", str(N["bus"]), font_size=48).move_to([-2.6, 0.6, 0])
        frs = VGroup(MathTex(rf"\frac{{{N['bus']}}}{{{N['n']}}} = {dec(rv['bus'])}", font_size=48),
                     MathTex(rf"\frac{{{N['nobus']}}}{{{N['n']}}} = {dec(rv['nobus'])}", font_size=48)
                     ).arrange(RIGHT, buff=0.9).move_to([-2.6, -1.0, 0])
        with self.say("2.9") as (tr, t):
            self.play(FadeOut(pc), Write(sum_), run_time=1.0)
            self.cue(tr, t, {"en": "zero point four five", "uz": "nol butun yuzdan qirq"})
            self.play(Write(frs[0]), Transform(qs[0], ans[0]), run_time=0.9)
            self.cue(tr, t, {"en": "The rest", "uz": "Qatnamaydiganlar"})
            self.play(Write(frs[1]), Transform(qs[1], ans[1]), run_time=0.9)
        self.clear_all()

        T = student_tree()
        g = tree_group(T)
        dep = txt(w("stage 2 depends on stage 1", "2-bosqich 1-bosqichga bogʻliq"), size=30, weight=BOLD,
                  color=HILITE).move_to([2.6, 3.2, 0])
        with self.say("2.10") as (tr, t):
            self.play(FadeIn(g), run_time=0.8)
            self.play(*[Indicate(T["p2"][i][0], color=HILITE, scale_factor=1.4) for i in range(2)], FadeIn(dep),
                      run_time=1.0)
        self.clear_all()


SCENES = ["S02Tree", "S02LanguageModel", "S02HandsOn"]
