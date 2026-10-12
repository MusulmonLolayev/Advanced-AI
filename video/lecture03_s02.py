"""Lecture 3, section 2 — expectation: pastries per order, the school raffle, then one die.

Every number on screen comes from N (capture_l03.py, unit-tested by test_l03.py):
pastry_pmf, pastry_mean, customers, pastries_per_100, raffle_A, raffle_tickets, raffle_price,
raffle_raised, raffle_kept, raffle_A_prize, die_sum, die_mean.
"""
import numpy as np
from lecture03_kit import *

RA = N["raffle_A"]
WIN, LOSE = sorted((int(k) for k in RA["pmf"]), reverse=True)        # +398, -2
P_WIN, P_LOSE = RA["pmf"][str(WIN)], RA["pmf"][str(LOSE)]


def money(v, cents=False):
    s = f"{abs(v):,.2f}" if cents else f"{abs(v):,.0f}"
    return ("-" if v < 0 else "") + r"\$" + s


def chip(tex, words, color=WHITE, size=46):
    """A value as math with its words under it (the value is language-neutral)."""
    v = MathTex(tex, font_size=size, color=color)
    return VGroup(v, txt(words, size=24, color=GREY_B).next_to(v, DOWN, buff=0.15))


def cloud(n=260, seed=3, w=5.2, h=3.0):
    """Many examples as dots in an ellipse (positions are decoration, not data)."""
    rng = np.random.default_rng(seed)
    pts = []
    while len(pts) < n:
        x, y = rng.uniform(-1, 1, 2)
        if x * x + y * y < 1:
            pts.append([x * w / 2, y * h / 2, 0])
    return VGroup(*[Dot(p, radius=0.04, color=GREY_B) for p in pts])


class S02Expectation(LectureScene):
    def construct(self):
        self.section_card(2)
        bars, probs, vals, floor = pmf_bars(PASTRY, base=-2.2, height=2.7, step=2.0, width=1.15, size=36)
        cap = txt(label("pastries"), size=24, color=GREY_B).next_to(vals, DOWN, buff=0.2)
        plot = VGroup(bars, probs, vals, floor, cap).shift(LEFT * 3.0)
        head = txt(label("expectation"), size=34, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        f = MathTex(r"E[X]", "=", r"\sum_x x\,p(x)", "=", r"\mu", font_size=50).next_to(head, DOWN, buff=0.3)
        with self.say("2.1") as (tr, t):
            self.play(FadeIn(plot), run_time=0.8)
            self.play(FadeIn(head), Write(f[:3]), run_time=1.0)
            self.cue(tr, t, {"en": "We also write it as mu", "uz": "Uni mu harfi"})
            self.play(Write(f[3:]), run_time=0.6)
            self.play(f[4].animate.set_color(HILITE), run_time=0.4)

        ks = sorted(PASTRY)
        prods = VGroup(*[MathTex(rf"{k}\times {dec(PASTRY[k])}", font_size=36, color=HILITE)
                         .next_to(pr, UP, buff=0.2) for k, pr in zip(ks, probs)])
        total = MathTex(r"E[X]", "=", " + ".join(rf"{k}({dec(PASTRY[k])})" for k in ks), "=", dec(N["pastry_mean"]),
                        font_size=46).move_to(f)
        total[-1].set_color(HILITE)
        with self.say("2.2") as (tr, t):
            self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in prods], lag_ratio=0.5), run_time=1.8)
            self.cue(tr, t, {"en": "The result is", "uz": "Natija nol"})
            self.play(FadeOut(f), FadeIn(total), FadeOut(prods), run_time=0.9)

        cust = tagged(N["customers"], label("customers"), size=34)
        arrow = MathTex(r"\longrightarrow", font_size=50)
        pas = tagged(f"≈ {N['pastries_per_100']:g}", label("pastries_short"), size=34, color=HILITE)
        row = VGroup(cust, arrow, pas).arrange(RIGHT, buff=0.3).move_to([3.3, 0.6, 0])
        if row.width > 6.4:
            row.scale_to_fit_width(6.4)
        calc = MathTex(rf"{N['customers']}\times {dec(N['pastry_mean'])} = {N['pastries_per_100']:g}", font_size=36,
                       color=GREY_B).next_to(row, DOWN, buff=0.2)
        with self.say("2.3") as (tr, t):
            self.play(FadeIn(row, shift=UP * 0.2), FadeIn(calc), run_time=1.0)

        # 0.4 is not a possible order: mark it between the bars for 0 and 1
        x0, x1 = vals[0].get_x(), vals[1].get_x()
        xm = x0 + (x1 - x0) * N["pastry_mean"]
        mark = DashedLine([xm, floor.get_y(), 0], [xm, floor.get_y() + 3.1, 0], color=HILITE, stroke_width=4)
        mtag = MathTex(dec(N["pastry_mean"]), font_size=34, color=HILITE).next_to(mark, UP, buff=0.1)
        nope = txt(label("no_order_holds_this"), size=26, color=RLRED)
        lr = txt(label("long_run_average"), size=30, weight=BOLD, color=LBLUE)
        VGroup(nope, lr).arrange(DOWN, buff=0.3).move_to([3.3, 0.4, 0])
        with self.say("2.4") as (tr, t):
            self.play(FadeOut(VGroup(row, calc)), Create(mark), FadeIn(mtag), run_time=0.9)
            self.play(FadeIn(nope), run_time=0.5)
            self.cue(tr, t, {"en": "An expectation does not", "uz": "Kutilma bitta"})
            self.play(FadeIn(lr, shift=UP * 0.2), run_time=0.7)
        self.clear_all()


class S02Raffle(LectureScene):
    def construct(self):
        n = N["raffle_tickets"]
        tickets = VGroup(*[Rectangle(width=0.2, height=0.13, stroke_width=0, fill_color=GREY_D, fill_opacity=1)
                           for _ in range(n)]).arrange_in_grid(rows=20, buff=(0.05, 0.06)).move_to([-3.4, -0.2, 0])
        gold = tickets[n // 2 + 12]
        head = txt(label("raffle"), size=34, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        sold = tagged(n, label("tickets"), size=30).next_to(tickets, UP, buff=0.25)
        price = MathTex(rf"{n}\times \${N['raffle_price']} = \${N['raffle_raised']}", font_size=40).move_to([3.0, 1.6, 0])
        prize = chip(rf"\${N['raffle_A_prize']}", label("bike", 1), color=HILITE).move_to([3.0, -0.2, 0])
        with self.say("2.5") as (tr, t):
            self.play(FadeIn(head), LaggedStart(*[FadeIn(k) for k in tickets], lag_ratio=0.002), FadeIn(sold),
                      run_time=1.4)
            self.play(Write(price), run_time=0.8)
            self.cue(tr, t, {"en": "One ticket wins", "uz": "Bitta chipta"})
            self.play(gold.animate.set_fill(HILITE).scale(1.8), FadeIn(prize, shift=LEFT * 0.2), run_time=0.9)

        gain = txt(label("net_gain"), size=28, color=LBLUE).move_to([3.0, 1.6, 0])
        pw = MathTex(rf"p({WIN}) = \tfrac{{{P_WIN[0]}}}{{{P_WIN[1]}}}", font_size=44, color=HILITE)
        pl = MathTex(rf"p({LOSE}) = \tfrac{{{P_LOSE[0]}}}{{{P_LOSE[1]}}}", font_size=44)
        pmf = VGroup(pw, pl).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([3.0, 0.1, 0])
        with self.say("2.6") as (tr, t):
            self.play(FadeOut(price), FadeOut(prize), FadeIn(gain, shift=DOWN * 0.2), run_time=0.7)
            self.cue(tr, t, {"en": "With probability", "uz": "Besh yuzdan bir"})
            self.play(FadeIn(pw), Indicate(gold, color=WHITE), run_time=0.8)
            self.play(FadeIn(pl), tickets.animate.set_fill(GREY_C), gold.animate.set_fill(HILITE), run_time=0.8)

        e = MathTex(rf"E[X] = {WIN}\cdot\tfrac{{{P_WIN[0]}}}{{{P_WIN[1]}}} - {-LOSE}\cdot\tfrac{{{P_LOSE[0]}}}{{{P_LOSE[1]}}}",
                    "=", money(RA["mean"], cents=True), font_size=44).to_edge(UP, buff=SAFE + 0.35)
        e[2].set_color(HILITE)
        keep = chip(rf"\${N['raffle_raised']} - \${N['raffle_A_prize']} = \${N['raffle_kept']}", label("the_school_keeps"),
                    size=42).move_to([3.0, -1.4, 0])
        with self.say("2.7") as (tr, t):
            self.play(FadeOut(VGroup(head, gain, sold)), pmf.animate.scale(0.8).move_to([3.0, 0.4, 0]), run_time=0.6)
            self.play(Write(e), run_time=1.3)
            self.cue(tr, t, {"en": "The school keeps", "uz": "Maktab yigʻilgan"})
            self.play(FadeIn(keep, shift=UP * 0.2), run_time=0.8)
        self.clear_all()

        outs = VGroup(MathTex(money(LOSE), font_size=56), MathTex("+" + money(WIN), font_size=56, color=HILITE))
        outs.arrange(RIGHT, buff=1.0)
        buyer = VGroup(outs, txt(label("what_a_buyer_gets"), size=26, color=GREY_B)).arrange(DOWN, buff=0.3)
        mean = MathTex(money(RA["mean"], cents=True), font_size=56, color=LBLUE)
        school = VGroup(mean, txt(label("what_the_school_budgets_on"), size=26, color=GREY_B)).arrange(DOWN, buff=0.3)
        neq = MathTex(r"\neq", font_size=64, color=RLRED)
        VGroup(buyer, neq, school).arrange(RIGHT, buff=1.0).move_to(UP * 0.2)
        neq.match_y(outs)
        with self.say("2.8") as (tr, t):
            self.play(FadeIn(buyer, shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeIn(neq), FadeIn(school), run_time=0.8)
            self.cue(tr, t, {"en": "Yet the school", "uz": "Lekin maktab"})
            self.play(Indicate(school, color=LBLUE, scale_factor=1.08), run_time=0.9)
        self.clear_all()

        dots = cloud().move_to([-2.4, -0.2, 0])
        allx = txt(label("all_examples"), size=26, color=GREY_B).next_to(dots, UP, buff=0.25)
        loss = txt(f"E[{label('error')}]", size=48, weight=BOLD, color=HILITE).move_to([3.6, 0.5, 0])
        down = VGroup(MathTex(r"\downarrow", font_size=60, color=HILITE),
                      txt(label("training"), size=28)).arrange(RIGHT, buff=0.25).next_to(loss, DOWN, buff=0.4)
        arrow = Arrow(dots.get_right(), loss.get_left(), buff=0.3, color=GREY_B)
        with self.say("2.9") as (tr, t):
            self.play(FadeIn(loss), FadeIn(down), run_time=0.8)
            self.cue(tr, t, {"en": "the average error", "uz": "model uchratishi"})
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.004), FadeIn(allx),
                      GrowArrow(arrow), run_time=1.4)
        self.clear_all()


class S02HandsOn(LectureScene):
    def construct(self):
        faces = VGroup(*[die_face(k, 0.8) for k in range(1, 7)]).arrange(RIGHT, buff=0.35).move_to([0, -1.6, 0])
        sixth = VGroup(*[MathTex(r"\tfrac{1}{6}", font_size=40, color=GREY_B).next_to(f, DOWN, buff=0.2) for f in faces])
        card = pause_card(["E[X] = ?"]).move_to(UP * 1.4)
        with self.say("2.10") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(card, shift=UP * 0.2), LaggedStart(*[FadeIn(f) for f in faces], lag_ratio=0.1),
                      FadeIn(sixth), run_time=1.0)
        self.hands_on()

        ans = MathTex(r"E[X] = \frac{" + " + ".join(str(k) for k in range(1, 7)) + "}{6}", "=",
                      rf"\frac{{{N['die_sum']}}}{{6}}", "=", dec(N["die_mean"]), font_size=50).move_to(UP * 1.3)
        ans[-1].set_color(HILITE)
        never = txt(label("no_face_shows_it"), size=28, color=RLRED).next_to(ans, DOWN, buff=0.45)
        with self.say("2.11") as (tr, t):
            self.play(FadeOut(card), run_time=0.4)
            self.cue(tr, t, {"en": "One to six", "uz": "Birdan oltigacha"})
            self.play(Write(ans[:3]), run_time=1.1)
            self.cue(tr, t, {"en": "divided by six", "uz": "oltiga boʻlsak"})
            self.play(Write(ans[3:]), run_time=0.7)
            self.cue(tr, t, {"en": "Again, a number", "uz": "Yana kubikda"})
            self.play(FadeIn(never), Indicate(faces, color=GREY_B, scale_factor=1.03), run_time=0.8)
        self.clear_all()

        dots = cloud(n=320, w=7.0, h=3.6).move_to(DOWN * 0.3)
        allx = txt(label("all_examples"), size=26, color=GREY_B).next_to(dots, UP, buff=0.25)
        seen = VGroup(*dots[:14])
        q = txt("E[X] = ?", size=40, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.3)
        with self.say("2.12") as (tr, t):
            self.play(FadeIn(dots), FadeIn(allx), run_time=0.8)
            self.play(dots.animate.set_opacity(0.25), *[d.animate.set_color(HILITE).set_opacity(1).scale(1.6)
                                                         for d in seen], run_time=0.9)
            self.cue(tr, t, {"en": "How do we find", "uz": "Unda kutilmani"})
            self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.6)
        self.clear_all()


SCENES = ["S02Expectation", "S02Raffle", "S02HandsOn"]
