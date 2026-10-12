"""Lecture 3, section 1 — a random variable and its distribution: two dice, then pastries per order.

Every number on screen comes from N (capture_l03.py, unit-tested by test_l03.py):
dice_ways, dice_outcomes, dice_p7, dice_p2, dice_7_vs_2, dice_p11, pastry_pmf.
"""
import textwrap

from lecture03_kit import *

WAYS = {int(s): w for s, w in N["dice_ways"].items()}
SUMS = sorted(WAYS)
EXAMPLE = tuple(N["example_roll"])           # the slide's example roll (narration 1.3: "uch va toʻrt")
ORANGE = range(N["monopoly_orange"][0], N["monopoly_orange"][1] + 1)   # six to nine squares past Jail
TASK = N["hands_on_sum"]                     # the hands-on sum; its answer is N["dice_p11"]
assert WAYS[TASK] == N["dice_p11"][0] * N["dice_outcomes"] // N["dice_p11"][1]
SUM_C = {s: interpolate_color(ManimColor(RLBLUE), ManimColor(HILITE), 1 - abs(s - 7) / 5) for s in SUMS}


def tfrac(a, b, size=48, color=WHITE):
    return MathTex(rf"\frac{{{a}}}{{{b}}}", font_size=size, color=color)


def pair_grid(cell=0.62, gap=0.06, size=26):
    """The 36 equally likely pairs as a 6 × 6 grid: first die across, second down, each cell
    showing the sum. Returns (grid, sums) with sums[i] the sum in cell i."""
    g, sums = VGroup(), []
    for b in range(1, 7):
        for a in range(1, 7):
            s = a + b
            sq = Square(cell, stroke_width=0, fill_color=SUM_C[s], fill_opacity=0.85)
            sq.add(MathTex(str(s), font_size=size, color=BLACK if abs(s - 7) <= 2 else WHITE))
            sq.move_to([(a - 1) * (cell + gap), -(b - 1) * (cell + gap), 0])
            g.add(sq)
            sums.append(s)
    assert len(g) == N["dice_outcomes"]
    return g.move_to(ORIGIN), sums


def stacks(grid, sums, base=-2.6, step=0.78, cell=0.5):
    """Target positions: each pair's cell stacked into the column of its sum."""
    seen = {s: 0 for s in SUMS}
    targets = VGroup()
    for sq, s in zip(grid, sums):
        k = seen[s]
        seen[s] += 1
        x = (SUMS.index(s) - (len(SUMS) - 1) / 2) * step
        targets.add(sq.copy().scale(cell / sq.width).move_to([x, base + (k + 0.5) * cell * 1.04, 0]))
    assert seen == WAYS
    return targets


def wrapped(text, width=24, **kw):
    """A long label as centred lines of at most `width` characters."""
    return VGroup(*[txt(l, **kw) for l in textwrap.wrap(text, width)]).arrange(DOWN, buff=0.12)


class S01Dice(LectureScene):
    def construct(self):
        self.section_card(1)
        events = VGroup(txt(label("it_s_even"), size=30), txt(label("the_student_takes_the_bus"), size=30))
        events.arrange(DOWN, buff=0.35).move_to([-3.4, 0.4, 0])
        ev_head = txt(label("events"), size=26, color=GREY_B).next_to(events, UP, buff=0.5)
        qs = VGroup(*[txt(k, size=34, weight=BOLD, color=HILITE)
                      for k in (label("how_many_q"), label("how_much_q"), label("how_long_q"))]).arrange(DOWN, buff=0.35)
        qs.move_to([3.4, 0.4, 0])
        q_head = txt(label("numbers"), size=26, color=GREY_B).next_to(qs, UP, buff=0.5)
        with self.say("1.1") as (tr, t):
            self.play(FadeIn(ev_head), LaggedStart(*[FadeIn(e, shift=RIGHT * 0.2) for e in events], lag_ratio=0.4),
                      run_time=1.2)
            self.cue(tr, t, {"en": "But most questions", "uz": "Lekin koʻp savollar"})
            self.play(FadeIn(q_head), LaggedStart(*[FadeIn(q, shift=LEFT * 0.2) for q in qs], lag_ratio=0.3),
                      run_time=1.2)
        self.clear_all()

        a, b = EXAMPLE
        dice = VGroup(die_face(a, 1.3), die_face(b, 1.3)).arrange(RIGHT, buff=0.5).move_to([-2.6, 0.6, 0])
        plus = MathTex(f"{a} + {b}", font_size=56, color=GREY_B).next_to(dice, DOWN, buff=0.5)
        xval = MathTex("X", "=", str(a + b), font_size=84, color=HILITE).move_to([3.0, 0.6, 0])
        arrow = Arrow(dice.get_right(), xval.get_left(), buff=0.3, color=GREY_B)
        with self.say("1.2") as (tr, t):
            self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.6, rate_func=rush_from) for d in dice], lag_ratio=0.3),
                      run_time=1.0)
            self.cue(tr, t, {"en": "The roll is chance", "uz": "Tashlash"})
            self.play(Write(plus), run_time=0.6)
            self.cue(tr, t, {"en": "the sum is", "uz": "yigʻindi esa"})
            self.play(GrowArrow(arrow), Write(xval), run_time=0.9)

        rv = txt(label("random_variable"), size=34, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.4)
        rule = VGroup(txt(label("outcome"), size=30), MathTex(r"\longmapsto", font_size=48),
                      txt(label("number"), size=30)).arrange(RIGHT, buff=0.3).next_to(rv, DOWN, buff=0.35)
        with self.say("1.3") as (tr, t):
            self.play(FadeIn(rv, shift=DOWN * 0.2), run_time=0.6)
            self.play(FadeIn(rule), run_time=0.7)
            self.cue(tr, t, {"en": "If the outcome", "uz": "Natija"})
            self.play(Indicate(dice, color=HILITE, scale_factor=1.05), Indicate(xval, color=HILITE), run_time=1.0)
        self.clear_all()

        vals = MathTex(r"\{", *[f"{s}" + ("," if s != SUMS[-1] else "") for s in SUMS], r"\}", font_size=52)
        vals.arrange(RIGHT, buff=0.32).move_to(UP * 0.4)
        xs = MathTex("X", r"\in", font_size=52).next_to(vals, LEFT, buff=0.3)
        disc = txt(label("discrete"), size=40, weight=BOLD, color=LBLUE).next_to(vals, DOWN, buff=0.8)
        with self.say("1.4") as (tr, t):
            self.play(FadeIn(xs), LaggedStart(*[FadeIn(v, shift=UP * 0.2) for v in vals], lag_ratio=0.08),
                      run_time=1.3)
            self.cue(tr, t, {"en": "We call such", "uz": "Bunday miqdorni"})
            self.play(FadeIn(disc, shift=UP * 0.2), run_time=0.6)
        self.clear_all()

        grid, sums = pair_grid()
        grid.move_to([0, 0.35, 0])
        first = txt(label("first_die"), size=24, color=GREY_B).next_to(grid, UP, buff=0.2)
        second = txt(label("second_die"), size=24, color=GREY_B).rotate(PI / 2).next_to(grid, LEFT, buff=0.2)
        n36 = tagged(N["dice_outcomes"], label("equally_likely_pairs"), size=28, color=GREY_B)
        n36.next_to(grid, RIGHT, buff=0.6)
        seven = VGroup(*[sq for sq, s in zip(grid, sums) if s == 7])
        two = VGroup(*[sq for sq, s in zip(grid, sums) if s == 2])
        target = stacks(grid, sums)
        ways = VGroup(*[MathTex(str(WAYS[s]), font_size=30, color=GREY_B) for s in SUMS])
        xlabs = VGroup(*[MathTex(str(s), font_size=30) for s in SUMS])
        for s, w, xl in zip(SUMS, ways, xlabs):
            col = VGroup(*[m for m, ss in zip(target, sums) if ss == s])
            w.next_to(col, UP, buff=0.12)
            xl.next_to([col.get_x(), -2.6, 0], DOWN, buff=0.18)
        floor = Line([target.get_left()[0] - 0.2, -2.6, 0], [target.get_right()[0] + 0.2, -2.6, 0],
                     color=GREY_B, stroke_width=2)
        with self.say("1.5") as (tr, t):
            self.play(LaggedStart(*[FadeIn(sq, scale=0.6) for sq in grid], lag_ratio=0.02), FadeIn(first),
                      FadeIn(second), run_time=1.4)
            self.cue(tr, t, {"en": "Two dice give", "uz": "Ikki kubikda"})
            self.play(FadeIn(n36), run_time=0.5)
            self.cue(tr, t, {"en": "A sum of two", "uz": "Yigʻindi ikki"})
            self.play(Indicate(two, color=WHITE, scale_factor=1.3), run_time=0.8)
            self.cue(tr, t, {"en": "Seven comes", "uz": "Yetti esa"})
            self.play(Indicate(seven, color=WHITE, scale_factor=1.15), run_time=0.8)
            self.play(FadeOut(VGroup(first, second, n36)), Transform(grid, target), run_time=1.6)
            self.play(Create(floor), FadeIn(xlabs), FadeIn(ways), run_time=0.6)

        i7, i2 = SUMS.index(7), SUMS.index(2)
        p7 = VGroup(MathTex("p(7)", "=", font_size=48),
                    tfrac(WAYS[7], N["dice_outcomes"]), MathTex("=", font_size=48),
                    tfrac(*N["dice_p7"], color=HILITE)).arrange(RIGHT, buff=0.2).move_to([-3.6, 2.6, 0])
        times = MathTex("=", rf"{N['dice_7_vs_2']}\times p(2)", font_size=48, color=GREY_B).next_to(p7, RIGHT, buff=0.25)
        with self.say("1.6") as (tr, t):
            self.play(Indicate(ways[i7], color=HILITE, scale_factor=1.4), FadeIn(p7[:3]), run_time=0.9)
            self.play(FadeIn(p7[3:]), run_time=0.6)
            self.cue(tr, t, {"en": "six times more likely", "uz": "olti marta"})
            self.play(FadeIn(times), Indicate(ways[i2], color=WHITE, scale_factor=1.4), run_time=0.8)

        probs = VGroup(*[tfrac(WAYS[s], N["dice_outcomes"], size=30, color=GREY_B).move_to(w).shift(UP * 0.12)
                         for s, w in zip(SUMS, ways)])
        pmf_head = txt(label("probability_mass_function"), size=32, weight=BOLD, color=LBLUE)
        pmf_head.move_to(p7).align_to(p7, LEFT)
        total = MathTex(r"\sum_x p(x) = 1", font_size=48, color=HILITE).to_corner(UR, buff=SAFE + 0.5)
        with self.say("1.7") as (tr, t):
            self.play(FadeOut(VGroup(p7, times)), Transform(ways, probs), run_time=0.9)
            self.play(FadeIn(pmf_head, shift=DOWN * 0.2), run_time=0.6)
            self.cue(tr, t, {"en": "The probabilities", "uz": "Ehtimollar"})
            self.play(Write(total), run_time=0.9)
        self.clear_all()

        # Monopoly: the stretch past Jail a player most often reaches is where the sum peaks
        cell, y0 = 0.62, -1.7
        board = VGroup(*[Square(cell, stroke_color=GREY_B, stroke_width=2,
                                fill_color=RLORANGE if d in ORANGE else BLACK, fill_opacity=0.85 if d in ORANGE else 0)
                         for d in range(0, SUMS[-1] + 1)]).arrange(RIGHT, buff=0.0).move_to([0, y0, 0])
        jail = txt(label("jail"), size=22, color=GREY_B).next_to(board[0], DOWN, buff=0.15)
        dist = VGroup(*[MathTex(str(d), font_size=26, color=BLACK if d in ORANGE else GREY_B).move_to(board[d])
                        for d in range(1, SUMS[-1] + 1)])
        past = txt(label("squares_past_jail"), size=22, color=GREY_B)
        orange = txt(label("orange_properties"), size=24, color=RLORANGE)
        orange.next_to(VGroup(*[board[d] for d in ORANGE]), DOWN, buff=0.15)
        past.next_to(board, DOWN, buff=0.15).align_to(board, RIGHT)
        if past.get_left()[0] < orange.get_right()[0] + 0.3:     # too long beside the orange label: a row lower
            past.next_to(VGroup(jail, orange), DOWN, buff=0.2).align_to(board, RIGHT)
        hmax = 2.6 / max(WAYS.values())
        bars = VGroup(*[Rectangle(width=cell * 0.7, height=WAYS[s] * hmax, stroke_width=0,
                                  fill_color=RLORANGE if s in ORANGE else RLBLUE, fill_opacity=1)
                        .move_to([board[s].get_x(), board.get_top()[1] + 0.12 + WAYS[s] * hmax / 2, 0]) for s in SUMS])
        title = txt(label("monopoly"), size=30, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        with self.say("1.8") as (tr, t):
            self.play(FadeIn(title), FadeIn(board), FadeIn(jail), FadeIn(dist), FadeIn(past), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06), run_time=1.2)
            self.cue(tr, t, {"en": "In Monopoly", "uz": "Monopoliyada"})
            self.play(FadeIn(orange), Indicate(VGroup(*[bars[SUMS.index(s)] for s in ORANGE]), color=WHITE,
                                                scale_factor=1.05), run_time=1.0)
        self.clear_all()


class S01Pastries(LectureScene):
    def construct(self):
        bars, probs, vals, floor = pmf_bars(PASTRY, base=-2.2, height=3.6, step=1.9, width=1.25, size=40)
        cap = txt(label("pastries"), size=28, color=GREY_B).next_to(vals, DOWN, buff=0.25)
        VGroup(bars, probs, vals, floor, cap).shift(LEFT * 2.9)
        head = VGroup(MathTex("X:", font_size=48), txt(label("pastries"), size=32)).arrange(RIGHT, buff=0.3)
        head.to_edge(UP, buff=SAFE + 0.4)
        total = MathTex(" + ".join(dec(PASTRY[k]) for k in sorted(PASTRY)), "=", dec(sum(PASTRY.values())),
                        font_size=48, color=HILITE).move_to([3.4, 0.2, 0])
        with self.say("1.9") as (tr, t):
            self.play(FadeIn(head), Create(floor), FadeIn(vals), FadeIn(cap), run_time=0.8)
            self.cue(tr, t, {"en": "No pastry", "uz": "Nol pishiriq"})
            for i in range(len(bars)):
                self.play(GrowFromEdge(bars[i], DOWN), FadeIn(probs[i]), run_time=0.55)
            self.cue(tr, t, {"en": "They add up", "uz": "Yigʻindi bir"})
            self.play(Write(total), run_time=0.8)

        then = wrapped(label("counts_in_a_sample_we_measured"), size=30, color=GREY_B)
        now = wrapped(label("probabilities_for_a_customer_not_yet_served"), size=30, weight=BOLD, color=LBLUE)
        tag1 = txt(label("lecture_1"), size=24, color=GREY_B).next_to(then, UP, buff=0.15)
        g1 = VGroup(tag1, then).move_to([3.4, 0.2, 0])
        now.move_to(then)
        cross = VGroup(*[Line(l.get_left(), l.get_right(), color=RLRED, stroke_width=4) for l in then])
        with self.say("1.10") as (tr, t):
            self.play(FadeOut(total), FadeIn(g1), run_time=0.7)
            self.cue(tr, t, {"en": "One difference", "uz": "Farqi bitta"})
            self.play(Create(cross), run_time=0.5)
            self.cue(tr, t, {"en": "these are probabilities", "uz": "bu yerda esa"})
            self.play(FadeOut(VGroup(then, cross)), FadeIn(now, shift=UP * 0.2),
                      tag1.animate.set_opacity(0), run_time=0.8)
        self.clear_all()

        # a language model's next word: a distribution over words (heights for illustration only)
        prompt = txt(label("lm_prompt"), size=34).to_edge(UP, buff=SAFE + 0.5)
        words = [label("lm_next_a"), label("lm_next_b"), label("lm_next_c"), label("lm_next_d")]
        shares = [0.46, 0.28, 0.17, 0.09]                 # illustrative; no number is shown
        base, h = -2.3, 3.6
        lm_bars = VGroup(*[Rectangle(width=1.3, height=p * h / max(shares), stroke_width=0, fill_color=LBLUE,
                                     fill_opacity=1) for p in shares]).arrange(RIGHT, buff=0.5, aligned_edge=DOWN)
        lm_bars.move_to([0, base, 0], aligned_edge=DOWN)
        wl = VGroup(*[txt(w, size=26).next_to(b, DOWN, buff=0.2) for w, b in zip(words, lm_bars)])
        model = txt(label("language_model"), size=28, weight=BOLD, color=HILITE).next_to(prompt, DOWN, buff=0.35)
        one = MathTex(r"\sum = 1", font_size=44, color=HILITE).next_to(lm_bars, RIGHT, buff=0.6).shift(UP * 1.0)
        note = info(label("illustration"))
        with self.say("1.11") as (tr, t):
            self.play(FadeIn(prompt), FadeIn(note), run_time=0.6)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in lm_bars], lag_ratio=0.15), FadeIn(wl), run_time=1.2)
            self.play(Write(one), run_time=0.6)
            self.cue(tr, t, {"en": "A language model", "uz": "Masalan, tilli model"})
            self.play(FadeIn(model, shift=DOWN * 0.2), run_time=0.6)
        self.clear_all()


class S01HandsOn(LectureScene):
    def construct(self):
        grid, sums = pair_grid(cell=0.46)
        grid.move_to([3.6, -0.2, 0])
        card = pause_card([f"P(X = {TASK}) = ?"]).move_to([-3.2, 0.6, 0])
        with self.say("1.12") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(card, shift=UP * 0.2), FadeIn(grid), run_time=0.8)
        self.hands_on()

        eleven = VGroup(*[sq for sq, s in zip(grid, sums) if s == TASK])
        others = [sq.animate.set_opacity(0.18) for sq, s in zip(grid, sums) if s != TASK]
        ans = VGroup(MathTex(f"P(X = {TASK})", "=", font_size=48), tfrac(WAYS[TASK], N["dice_outcomes"]),
                     MathTex("=", font_size=48), tfrac(*N["dice_p11"], color=HILITE)).arrange(RIGHT, buff=0.2)
        ans.move_to([-3.2, -0.6, 0])
        pairs = MathTex(r",\ ".join(f"({a}, {TASK - a})" for a in range(1, 7) if 1 <= TASK - a <= 6),
                        font_size=40, color=GREY_B).next_to(ans, UP, buff=0.4)
        with self.say("1.13") as (tr, t):
            self.play(FadeOut(card), *others, Indicate(eleven, color=WHITE, scale_factor=1.2), run_time=1.0)
            self.play(FadeIn(pairs), run_time=0.5)
            self.cue(tr, t, {"en": "Two in thirty-six", "uz": "Oʻttiz oltidan ikki"})
            self.play(Write(ans), run_time=1.0)
        self.clear_all()

        bars, probs, vals, floor = pmf_bars(PASTRY, base=-2.2, height=3.0, step=2.0, width=1.2, size=36)
        q = txt(label("how_many_pastries_on_average_q"), size=34, weight=BOLD, color=HILITE)
        q.to_edge(UP, buff=SAFE + 0.5)
        with self.say("1.14") as (tr, t):
            self.play(Create(floor), FadeIn(vals), *[GrowFromEdge(b, DOWN) for b in bars], FadeIn(probs), run_time=1.0)
            self.cue(tr, t, {"en": "But what if", "uz": "Lekin bitta son"})
            self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.7)
        self.clear_all()


SCENES = ["S01Dice", "S01Pastries", "S01HandsOn"]
