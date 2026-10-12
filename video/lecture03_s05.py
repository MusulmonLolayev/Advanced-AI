"""Lecture 3, section 5 — roulette: why a gambler cannot end in profit.

18 of 37 pockets are red, so a $1 bet on red has E[X] = -1/37 ≈ -2.7 cents; expectations add, so the expected
balance after n bets is n·E[X], and the chance of being ahead drains away (36 %, 19 %, 0.3 %). The doubling
system: nine losses use up 1 + 2 + … + 256 = $511, the tenth stake ($512) is out of reach. Every number is N's.
"""
from lecture03_kit import *

RED, POCKETS = N["roulette_red"], N["roulette_pockets"]
GREEN = POCKETS - 2 * RED
MEAN = N["roulette_mean"]
M = N["martingale"]
R = N["roulette"]


def mtex(s, size=40, color=WHITE):
    return MathTex(s.replace(",", "{,}"), font_size=size, color=color)


def cents(v, places=1):
    """-0.027 -> −2.7 (a text minus, for Text; MathTex takes "-")."""
    return f"{100 * v:.{places}f}".replace("-", "−")


def node(text, color=RLBLUE, size=28):
    """A word in a rounded box (Lecture 2's kit has the same one)."""
    t = txt(text, size=size)
    r = RoundedRectangle(corner_radius=0.1, width=t.width + 0.4, height=t.height + 0.3, stroke_color=color,
                         stroke_width=2.5, fill_color=BLACK, fill_opacity=0.8)
    return VGroup(r, t.move_to(r))


def wheel(radius=2.0):
    """The wheel: RED red pockets and RED black alternate around it, GREEN green one at the top."""
    n = POCKETS
    is_red = [False] * GREEN + [i % 2 == 0 for i in range(n - GREEN)]
    colors = [RLGREEN] * GREEN + [RLRED if r else GREY_E for r in is_red[GREEN:]]
    sectors = VGroup(*[AnnularSector(inner_radius=radius * 0.62, outer_radius=radius, angle=TAU / n,
                                     start_angle=PI / 2 - (i + 1) * TAU / n, fill_color=c, fill_opacity=1,
                                     stroke_color=BLACK, stroke_width=1.5) for i, c in enumerate(colors)])
    hub = VGroup(Circle(radius=radius * 0.62, stroke_color=GREY_B, stroke_width=2, fill_color=BLACK, fill_opacity=1),
                 Circle(radius=radius * 0.12, stroke_width=0, fill_color=GREY_B, fill_opacity=1))
    return VGroup(sectors, hub), is_red


class S05Wheel(LectureScene):
    def construct(self):
        self.section_card(5)
        w, is_red = wheel()
        w.move_to(LEFT * 3.4)
        reds = VGroup(*[s for s, r in zip(w[0], is_red) if r])
        assert len(reds) == RED
        bet = txt(label("bet_on_red"), size=30, weight=BOLD, color=RLRED).move_to([2.6, 2.4, 0])
        share = mtex(rf"\frac{{{RED}}}{{{POCKETS}}}", 60, RLRED)
        share_l = txt(label("red"), size=28, color=RLRED)
        sg = VGroup(share, share_l).arrange(RIGHT, buff=0.3).move_to([2.6, 1.0, 0])
        with self.say("5.1") as (tr, t):
            self.play(FadeIn(w, scale=0.9), run_time=1.0)
            self.play(FadeIn(bet), run_time=0.5)
            self.cue(tr, t, {"en": "But only eighteen", "uz": "Lekin oʻttiz"})
            self.play(Indicate(reds, color=RLRED, scale_factor=1.04), Write(share), FadeIn(share_l), run_time=1.0)

        e = mtex(rf"E[X] = (+1)\tfrac{{{RED}}}{{{POCKETS}}} + (-1)\tfrac{{{POCKETS - RED}}}{{{POCKETS}}}"
                 rf" = -\tfrac{{{-N['roulette_mean_frac'][0]}}}{{{N['roulette_mean_frac'][1]}}}", 40)
        e.move_to([2.4, -0.4, 0])
        c = tagged(f"≈ {cents(MEAN)}¢", label("per_dollar"), size=34, weight=BOLD, color=HILITE)
        c.next_to(e, DOWN, buff=0.45)
        with self.say("5.2") as (tr, t):
            self.play(Write(e), run_time=1.3)
            self.play(FadeIn(c), run_time=0.5)
            self.cue(tr, t, {"en": "The wheel has no memory", "uz": "Gʻildirak"})
            self.play(Rotate(w, angle=-3 * TAU, about_point=w.get_center(), rate_func=rate_functions.ease_out_cubic),
                      run_time=2.2)
        self.clear_all()


class S05Balance(LectureScene):
    def construct(self):
        ns = sorted(int(n) for n in R)
        n_max = ns[-2]                                           # the axis runs to 1000 bets, the hands-on's count
        ax = Axes(x_range=[0, n_max, 250], y_range=[-30, 5, 10], x_length=8.5, y_length=4.4, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2, "include_numbers": True, "font_size": 22})
        ax.move_to(DOWN * 0.3)
        # the x axis runs along the top (balances are negative): its name sits at the empty top right
        xl = txt(label("number_of_bets"), size=24, color=GREY_B)
        xl.next_to(ax.c2p(n_max, 0), DOWN, buff=0.5).align_to(ax.c2p(n_max, 0), RIGHT)
        yl = txt(label("expected_balance_dollars"), size=24, color=GREY_B).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        line = ax.plot(lambda n: n * MEAN, x_range=[0, n_max], color=RLRED, stroke_width=5)
        rule = mtex(r"n \cdot E[X]", 44, RLRED)
        rule.next_to(ax.c2p(n_max * 0.5, n_max * 0.5 * MEAN), DOWN + LEFT, buff=0.3)
        dots = VGroup(*[Dot(ax.c2p(n, R[str(n)]["balance"]), radius=0.08, color=HILITE) for n in ns[1:-1]])
        # the two readings, listed in the empty lower left of the plot
        rows = VGroup(*[mtex(rf"n = {n:,}: \;\; {R[str(n)]['balance']:.2f}", 32, HILITE) for n in ns[1:-1]])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(ax.c2p(0, -30), UP + RIGHT, buff=0.3)
        marks = VGroup(dots, rows)
        with self.say("5.3") as (tr, t):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.cue(tr, t, {"en": "the expected balance is", "uz": "kutilayotgan balans"})
            self.play(Create(line), Write(rule), run_time=1.4)
            self.play(LaggedStart(*[FadeIn(m) for m in marks], lag_ratio=0.4), run_time=0.8)
            self.cue(tr, t, {"en": "Playing longer", "uz": "Uzoq oʻynash"})
            self.play(Indicate(line, color=RLRED, scale_factor=1.02), run_time=0.8)
        self.play(FadeOut(VGroup(ax, xl, yl, line, rule, marks)), run_time=0.4)

        # the chance of being ahead after n bets
        shown = [n for n in ns if n >= 100]
        floor, hk = -2.3, 4.0
        bars = VGroup()
        for i, n in enumerate(shown):
            p = R[str(n)]["p_ahead"]
            x = (i - (len(shown) - 1) / 2) * 2.6
            b = Rectangle(width=1.4, height=max(p * hk / 0.5, 0.04), stroke_width=0, fill_color=HILITE, fill_opacity=1)
            b.move_to([x, floor + b.height / 2, 0])
            pct = f"{100 * p:.0f}%" if p >= 0.01 else f"{100 * p:.1f}%"
            bars.add(VGroup(b, txt(pct, size=40, weight=BOLD).next_to(b, UP, buff=0.15),
                            mtex(rf"n = {n:,}", 32, GREY_B).next_to([x, floor, 0], DOWN, buff=0.25)))
        head = txt(label("chance_of_being_ahead"), size=32, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.4)
        with self.say("5.4") as (tr, t):
            self.play(FadeIn(head), run_time=0.5)
            for b, cue in zip(bars, [{"en": "thirty-six percent", "uz": "yuz tikishdan"},
                                     {"en": "nineteen percent", "uz": "ming tikishdan"},
                                     {"en": "zero point three", "uz": "oʻn ming tikishdan"}]):
                self.cue(tr, t, cue)
                self.play(GrowFromEdge(b[0], DOWN), FadeIn(b[1]), FadeIn(b[2]), run_time=0.7)

        # from above the first label to above the last, clearing the middle one
        drift = Arrow(bars[0][1].get_corner(UR) + RIGHT * 0.3 + UP * 0.3, bars[-1][1].get_top() + UP * 0.6, buff=0.1,
                      color=RLRED, stroke_width=5)
        with self.say("5.5") as (tr, t):
            self.play(Indicate(bars[0], color=HILITE, scale_factor=1.06), run_time=0.9)
            self.cue(tr, t, {"en": "But the balance drifts down", "uz": "Lekin balans"})
            self.play(GrowArrow(drift), run_time=0.9)
        self.clear_all()


class S05Doubling(LectureScene):
    def construct(self):
        k = M["losses_covered"]
        stakes = [2 ** i for i in range(k)]
        assert sum(stakes) == M["lost_after"] and 2 ** k == M["next_stake"]
        purse = tagged(f"${M['bankroll']:,}", f"{label('bankroll')}:", after=False, size=32, weight=BOLD,
                       color=RLGREEN).to_edge(UP, buff=SAFE + 0.35)
        boxes = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.08, width=1.05, height=0.7, stroke_color=RLRED,
                                                 stroke_width=3, fill_color=RLRED, fill_opacity=0.25),
                                mtex(f"{s}", 32)).arrange(ORIGIN) for s in stakes])
        boxes.arrange(RIGHT, buff=0.18).move_to(UP * 1.0)
        if boxes.width > 12:
            boxes.scale_to_fit_width(12)
        losses = txt(label("losses_in_a_row"), size=26, color=RLRED).next_to(boxes, DOWN, buff=0.25)
        total = mtex(" + ".join(str(s) for s in stakes[:3]) + r" + \dots + " + str(stakes[-1]) + f" = {M['lost_after']}",
                     44, RLRED).move_to(DOWN * 0.6)
        nxt = VGroup(RoundedRectangle(corner_radius=0.08, width=1.5, height=0.8, stroke_color=GREY_B, stroke_width=3),
                     mtex(f"{M['next_stake']}", 38)).arrange(ORIGIN).move_to(DOWN * 2.1)
        nxt_l = txt(label("next_bet"), size=26, color=GREY_B).next_to(nxt, LEFT, buff=0.3)
        cross = Cross(nxt, stroke_color=RLRED, stroke_width=6)
        with self.say("5.6") as (tr, t):
            self.cue(tr, t, {"en": "With a thousand dollars", "uz": "Ming dollar bilan"})
            self.play(FadeIn(purse), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.15) for b in boxes], lag_ratio=0.12), FadeIn(losses),
                      run_time=1.6)
            self.cue(tr, t, {"en": "five hundred and eleven", "uz": "besh yuz oʻn bir"})
            self.play(Write(total), run_time=0.9)
            self.cue(tr, t, {"en": "The next bet needs", "uz": "Keyingi tikish"})
            self.play(FadeIn(nxt), FadeIn(nxt_l), run_time=0.6)
            self.play(Create(cross), run_time=0.5)
        self.play(FadeOut(VGroup(boxes, losses, nxt, nxt_l, cross)), total.animate.to_edge(UP, buff=SAFE + 1.2),
                  run_time=0.6)

        q = POCKETS - RED
        ruin = mtex(rf"\left(\tfrac{{{q}}}{{{POCKETS}}}\right)^{{{k}}} \approx \tfrac{{1}}{{{M['one_in']}}}", 48, RLRED)
        ruin.move_to(UP * 0.6 + LEFT * 3.2)
        per = tagged(f"{cents(M['mean'], 0)}¢", label("per_session"), size=34, weight=BOLD, color=HILITE)
        per.move_to(UP * 0.6 + RIGHT * 3.0)
        # many sessions won by $1, then one session that loses the whole $511 (heights not to scale)
        floor = -1.4
        wins = VGroup(*[Rectangle(width=0.32, height=0.25, stroke_width=0, fill_color=RLGREEN, fill_opacity=1)
                        for _ in range(16)]).arrange(RIGHT, buff=0.1)
        wins.move_to([-1.2, floor + 0.125, 0])
        loss = Rectangle(width=0.32, height=1.9, stroke_width=0, fill_color=RLRED, fill_opacity=1)
        loss.next_to(wins, RIGHT, buff=0.1).align_to([0, floor, 0], UP)
        base = Line([wins.get_left()[0] - 0.3, floor, 0], [loss.get_right()[0] + 0.3, floor, 0], color=GREY_B, stroke_width=2)
        win_v = mtex(rf"+\${stakes[0]}", 28, RLGREEN).next_to(wins, UP, buff=0.15)
        loss_v = mtex(rf"-\${M['lost_after']}", 28, RLRED).next_to(loss, RIGHT, buff=0.15)
        with self.say("5.7") as (tr, t):
            self.play(Write(ruin), run_time=1.0)
            self.cue(tr, t, {"en": "and the expectation stays", "uz": "va kutilma"})
            self.play(FadeIn(per), run_time=0.6)
            self.cue(tr, t, {"en": "Many small wins", "uz": "Koʻp kichik"})
            self.play(Create(base), LaggedStart(*[GrowFromEdge(b, DOWN) for b in wins], lag_ratio=0.06), FadeIn(win_v),
                      run_time=1.2)
            self.play(GrowFromEdge(loss, UP), FadeIn(loss_v), run_time=0.7)
        self.clear_all()

        # AI: an agent adds up expected rewards step by step; negative per step means a falling total
        steps = 8
        ax = Axes(x_range=[0, steps, 1], y_range=[-steps, 1, 2], x_length=7.5, y_length=3.6, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2}).move_to(DOWN * 0.9 + RIGHT * 1.2)
        xl = txt(label("step"), size=24, color=GREY_B).next_to(ax.x_axis.get_right(), UP, buff=0.15)
        cum = ax.plot_line_graph(list(range(steps + 1)), [-i for i in range(steps + 1)], line_color=RLRED,
                                 vertex_dot_radius=0.06, vertex_dot_style={"fill_color": RLRED}, stroke_width=4)
        per_step = mtex(r"E[r_t] < 0", 40, RLRED).move_to(UP * 2.3 + LEFT * 3.4)
        tot = mtex(r"\sum_t E[r_t]", 40, RLRED).next_to(ax.c2p(steps, -steps), UP + LEFT, buff=0.2)
        agent = node(label("agent"), color=LBLUE, size=28).move_to(UP * 2.3 + RIGHT * 1.6)
        note = info(label("illustration"))
        with self.say("5.8") as (tr, t):
            self.play(FadeIn(agent), FadeIn(note), run_time=0.6)
            self.play(Create(ax), FadeIn(xl), run_time=0.7)
            self.cue(tr, t, {"en": "A strategy whose", "uz": "Har qadamda kutilmasi"})
            self.play(Write(per_step), run_time=0.6)
            self.play(Create(cum), Write(tot), run_time=1.4)
        self.clear_all()


class S05HandsOn(LectureScene):
    def construct(self):
        n = sorted(int(x) for x in R)[-2]                         # the thousand bets
        card = pause_card([f"n = {n:,}", label("expected_balance_q")])
        per = mtex(rf"E[X] = -\tfrac{{{-N['roulette_mean_frac'][0]}}}{{{N['roulette_mean_frac'][1]}}}", 44, GREY_B)
        VGroup(card, per).arrange(DOWN, buff=0.6).move_to(UP * 0.2)
        with self.say("5.9") as (tr, t):
            self.cue(tr, t, {"en": "Pause the video", "uz": "Videoni toʻxtating"})
            self.play(FadeIn(card), FadeIn(per), run_time=0.8)
        self.hands_on()

        ans = mtex(rf"{n:,} \times \left(-\tfrac{{1}}{{{N['roulette_mean_frac'][1]}}}\right) \approx "
                   rf"-\${-R[str(n)]['balance']:.2f}", 52, HILITE).move_to(DOWN * 0.4)
        with self.say("5.10"):
            self.play(FadeOut(card), per.animate.to_edge(UP, buff=SAFE + 0.5), run_time=0.5)
            self.play(Write(ans), run_time=1.2)
        self.clear_all()

        # the question for the next section: change every outcome, what happens to E and Var?
        bars, probs, vals, floor = pmf_bars(PASTRY, base=-2.0, height=2.6, step=1.3, width=0.8)
        g = VGroup(bars, probs, vals, floor).move_to(LEFT * 3.2 + DOWN * 0.3)
        qs = VGroup(mtex(rf"{N['price']}X \;?", 52, HILITE), mtex(rf"X + {N['coffee']} \;?", 52, HILITE)).arrange(DOWN, buff=0.6)
        qs.move_to(RIGHT * 3.0)
        with self.say("5.11") as (tr, t):
            self.play(FadeIn(g), run_time=0.7)
            self.play(FadeIn(qs[0], shift=LEFT * 0.3), run_time=0.6)
            self.cue(tr, t, {"en": "or add a fixed amount", "uz": "yoki unga doimiy"})
            self.play(FadeIn(qs[1], shift=LEFT * 0.3), run_time=0.6)
        self.clear_all(run_time=0.3)   # the next section opens on a silent card


SCENES = ["S05Wheel", "S05Balance", "S05Doubling", "S05HandsOn"]
