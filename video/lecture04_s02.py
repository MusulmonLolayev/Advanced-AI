"""Lecture 4, section 2 — the CDF: the area gathered from the left, and every range question as
F(b) − F(a). The gap between customers is exponential with rate N["rate"] per minute; every number
shown comes from N.
"""
from math import exp, log

from lecture04_kit import *

RATE = N["rate"]
CURVE = N["pdf_curve"]
X_MAX = CURVE[-1][0]
W, L = N["within"], N["lull"]                # 2 and 5 minutes
AREA_C, TAIL_C = LBLUE, RLRED


def f(x):
    return RATE * exp(-RATE * x)


def F(x):
    return 1 - exp(-RATE * x)


def axes(y_max, y_step, y_len, x_len=8.4, places=1):
    return Axes(x_range=[0, X_MAX, 2], y_range=[0, y_max, y_step], x_length=x_len, y_length=y_len, tips=False,
                axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 24},
                x_axis_config={"include_numbers": True},
                y_axis_config={"include_numbers": True, "decimal_number_config": {"num_decimal_places": places}})


def pdf_line(ax, color=LBLUE):
    return ax.plot_line_graph([x for x, _ in CURVE], [y for _, y in CURVE], add_vertex_dots=False,
                              line_color=color, stroke_width=4)["line_graph"]


def cdf_line(ax, color=HILITE, upto=None):
    xs = [x for x, _ in CURVE if upto is None or x <= upto + 1e-9]
    return ax.plot_line_graph(xs, [F(x) for x in xs], add_vertex_dots=False, line_color=color,
                              stroke_width=4)["line_graph"]


def area(ax, a, b, color=AREA_C, opacity=0.55):
    xs = [a] + [x for x, _ in CURVE if a < x < b] + [b]
    return Polygon(ax.c2p(a, 0), *[ax.c2p(x, f(x)) for x in xs], ax.c2p(b, 0), stroke_width=0,
                   fill_color=color, fill_opacity=opacity)


def lookup(ax, x, color=GREY_B):
    """The dashed read-off from x up to the CDF and across to its value."""
    return VGroup(DashedLine(ax.c2p(x, 0), ax.c2p(x, F(x)), color=color, stroke_width=2.5),
                  DashedLine(ax.c2p(x, F(x)), ax.c2p(0, F(x)), color=color, stroke_width=2.5),
                  Dot(ax.c2p(x, F(x)), radius=0.07, color=color))


class S02Area(LectureScene):
    def construct(self):
        self.section_card(2)
        top = axes(0.4, 0.1, 2.5).move_to(UP * 1.75 + RIGHT * 0.9)
        y_top = txt(label("density"), size=22, color=GREY_B).next_to(top.y_axis, LEFT, buff=0.55)
        curve = pdf_line(top)
        rate = VGroup(MathTex(rf"\lambda = {dec(RATE)}", font_size=40, color=HILITE),
                      txt(label("per_minute"), size=22, color=GREY_B)).arrange(DOWN, buff=0.08)
        mean = VGroup(MathTex(rf"1/\lambda = {dec(N['mean_gap'])}", font_size=40, color=HILITE),
                      txt(label("average_gap"), size=22, color=GREY_B)).arrange(DOWN, buff=0.08)
        fx = MathTex(rf"f(x) = {dec(RATE)}\,e^{{-{dec(RATE)}x}}", font_size=40, color=LBLUE)
        side = VGroup(rate, mean, fx).arrange(DOWN, buff=0.35).move_to(RIGHT * 3.6 + DOWN * 1.8)
        with self.say("2.1") as (tr, t):
            self.play(Create(top), FadeIn(y_top), FadeIn(rate), run_time=0.9)
            self.cue(tr, t, {"en": "So the average gap", "uz": "Demak, mijozlar"})
            self.play(FadeIn(mean), run_time=0.6)
            self.cue(tr, t, {"en": "and its density", "uz": "uning zichligi"})
            self.play(Create(curve), Write(fx), run_time=1.0)

        shade = area(top, 0, W)
        nxt = txt(label("next_customer"), size=24, color=GREY_B)
        p2 = MathTex(rf"P(X < {W}) = 1 - e^{{-{dec(RATE * W)}}} = {dec(N['p_within'])}", font_size=40, color=AREA_C)
        res = VGroup(nxt, p2).arrange(DOWN, buff=0.1).next_to(top.c2p(6.5, 0.3), DOWN, buff=0)
        res.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06)
        with self.say("2.2") as (tr, t):
            self.play(FadeOut(side), FadeIn(nxt), run_time=0.5)
            self.cue(tr, t, {"en": "We shade the area", "uz": "Noldan ikkigacha"})
            self.play(FadeIn(shade), run_time=0.8)
            self.play(Write(p2), run_time=0.8)

        # the same area gathered from the left: the CDF
        bot = axes(1.0, 0.25, 2.5, places=2).move_to(DOWN * 1.95 + RIGHT * 0.9)
        y_bot = MathTex("F(x)", font_size=34, color=HILITE).next_to(bot.y_axis, LEFT, buff=0.55)
        sweep = ValueTracker(0.05)
        fill = always_redraw(lambda: area(top, 0, sweep.get_value(), opacity=0.35))
        trace = always_redraw(lambda: cdf_line(bot, upto=max(sweep.get_value(), 0.1)))
        with self.say("2.3") as (tr, t):
            self.play(Create(bot), FadeIn(y_bot), FadeOut(shade), run_time=0.8)
            self.add(fill, trace)
            self.play(sweep.animate.set_value(W), run_time=1.4)
            self.cue(tr, t, {"en": "The curve we get", "uz": "Hosil boʻlgan egri chiziq"})
            look = lookup(bot, W, color=AREA_C)
            v = MathTex(dec(N["F_within"]), font_size=32, color=AREA_C).next_to(bot.c2p(W / 2, F(W)), UP, buff=0.06)
            self.play(Create(look), FadeIn(v), run_time=0.7)
            self.cue(tr, t, {"en": "This is the cumulative", "uz": "Bu taqsimot funksiyasi"})
            self.play(sweep.animate.set_value(X_MAX), run_time=1.6)
        self.remove(fill, trace)
        full = cdf_line(bot)
        self.add(area(top, 0, X_MAX, opacity=0.35), full)

        name = VGroup(txt(label("cumulative_distribution_function"), size=26, weight=BOLD, color=HILITE),
                      MathTex(r"F(x) = P(X \le x)", font_size=36, color=HILITE)).arrange(DOWN, buff=0.1)
        name.next_to(bot.c2p(7.6, 0.8), DOWN, buff=0)                 # under the flat right end of the curve
        name.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06)
        never = txt(label("never_decreases"), size=24, color=GREY_B).next_to(name, DOWN, buff=0.15)
        with self.say("2.4") as (tr, t):
            self.play(FadeIn(name), run_time=0.6)
            self.play(FadeIn(never), Indicate(full, color=WHITE, scale_factor=1.0), run_time=0.8)
            self.cue(tr, t, {"en": "Fifty-five percent", "uz": "Tanaffuslarning ellik besh"})
            self.play(Indicate(v, color=HILITE, scale_factor=1.3), run_time=0.8)

        tail = area(top, L, X_MAX, color=TAIL_C, opacity=0.7)
        quiet = VGroup(txt(label("a_quiet_stretch"), size=24, color=TAIL_C),
                       MathTex(rf"P(X > {L}) = e^{{-{dec(RATE * L)}}} = {pct(N['p_lull'])}".replace("%", r"\%"),
                               font_size=36, color=TAIL_C)).arrange(DOWN, buff=0.08)
        quiet.next_to(top.c2p(9, 0.22), UP, buff=0)
        lull = txt(label("a_lull_is_not_the_end"), size=24, color=GREY_B).next_to(quiet, DOWN, buff=0.15)
        for m in (quiet, lull):
            m.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06)
        with self.say("2.5") as (tr, t):
            self.play(FadeOut(res), FadeIn(tail), FadeIn(quiet), run_time=0.9)
            self.cue(tr, t, {"en": "So a lull", "uz": "Demak, sokinlik"})
            self.play(FadeIn(lull), run_time=0.6)
        self.clear_all()


class S02Cdf(LectureScene):
    def construct(self):
        ax = axes(1.0, 0.25, 4.2, x_len=8.0, places=2).move_to(LEFT * 1.6 + DOWN * 0.3)
        yl = MathTex("F(x)", font_size=36, color=HILITE).next_to(ax.y_axis, UP, buff=0.15)
        xl = txt(label("gap_axis"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.5)
        full = cdf_line(ax)
        a, b = 1.5, 4.0                                    # where a and b sit: letters only, no values shown
        la, lb = lookup(ax, a), lookup(ax, b, color=HILITE)
        ab = VGroup(MathTex("a", font_size=34).next_to(ax.c2p(a, 0), UP, buff=0.12),
                    MathTex("b", font_size=34, color=HILITE).next_to(ax.c2p(b, 0), UP, buff=0.12))
        gapb = BraceBetweenPoints(ax.c2p(0, F(a)), ax.c2p(0, F(b)), LEFT, color=HILITE).shift(LEFT * 0.75)
        rule = MathTex(r"P(a < X < b) = F(b) - F(a)", font_size=44).to_edge(UP, buff=SAFE + 0.3)
        two = txt(label("two_lookups_and_a_subtraction"), size=26, color=GREY_B).next_to(rule, DOWN, buff=0.15)
        with self.say("2.6") as (tr, t):
            self.play(Create(ax), FadeIn(yl), FadeIn(xl), Create(full), run_time=1.0)
            self.cue(tr, t, {"en": "the chance of landing between", "uz": "ey va bi orasida boʻlish"})
            self.play(Create(la), Create(lb), FadeIn(ab), run_time=0.9)
            self.play(Write(rule), GrowFromCenter(gapb), FadeIn(two), run_time=0.9)

        # what tables and software report: F, looked up
        rows = [(W, N["F_within"]), (L, N["F_lull"])]
        table = VGroup(*[VGroup(MathTex(rf"F({x})", font_size=40), MathTex(rf"= {dec(v, 3)}", font_size=40))
                         .arrange(RIGHT, buff=0.15) for x, v in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        frame_ = SurroundingRectangle(table, buff=0.3, color=GREY_B, stroke_width=2, corner_radius=0.1)
        tab = VGroup(frame_, table).move_to(RIGHT * 4.3 + DOWN * 0.3)
        rep = txt(label("tables_report_the_cdf"), size=22, color=GREY_B).next_to(tab, DOWN, buff=0.3)
        if rep.width > 4.4:
            rep.scale_to_fit_width(4.4)
        with self.say("2.7") as (tr, t):
            self.play(FadeOut(two), FadeOut(gapb), FadeOut(la), FadeOut(lb), FadeOut(ab), Create(frame_),
                      FadeIn(table), FadeIn(rep), run_time=1.0)
        self.clear_all()

        # AI: an alert for the slowest requests sits where the CDF reaches 0.99 (a picture)
        Q = N["alert_q"]                                    # "the slowest one percent" (narration 2.8)
        ax2 = axes(1.0, 0.25, 4.0, x_len=8.6, places=2).move_to(UP * 0.2)
        ax2.x_axis.numbers.set_opacity(0)                  # no time scale: an illustration
        yl2 = MathTex("F(x)", font_size=36, color=HILITE).next_to(ax2.y_axis, UP, buff=0.15)
        xl2 = txt(label("request_time"), size=24, color=GREY_B).next_to(ax2.x_axis, DOWN, buff=0.3)
        curve = cdf_line(ax2)
        xq = -log(1 - Q) / RATE
        hline = DashedLine(ax2.c2p(0, Q), ax2.c2p(xq, Q), color=RLRED, stroke_width=3)
        vline = DashedLine(ax2.c2p(xq, Q), ax2.c2p(xq, 0), color=RLRED, stroke_width=3)
        qv = MathTex(rf"F = {dec(Q)}", font_size=34, color=RLRED).next_to(ax2.c2p(xq / 2, Q), UP, buff=0.12)
        zone = Rectangle(width=ax2.c2p(X_MAX, 0)[0] - ax2.c2p(xq, 0)[0], height=ax2.c2p(0, 1)[1] - ax2.c2p(0, 0)[1],
                         stroke_width=0, fill_color=RLRED, fill_opacity=0.18)
        zone.move_to([(ax2.c2p(xq, 0)[0] + ax2.c2p(X_MAX, 0)[0]) / 2, ax2.c2p(0, 0.5)[1], 0])
        alert = txt(label("alert"), size=28, weight=BOLD, color=RLRED).next_to(zone, UP, buff=0.1)
        ill = info(label("illustration"))
        with self.say("2.8") as (tr, t):
            self.play(Create(ax2), FadeIn(yl2), FadeIn(xl2), Create(curve), FadeIn(ill), run_time=1.0)
            self.cue(tr, t, {"en": "where the CDF reaches", "uz": "nol butun yuzdan toʻqson toʻqqizga"})
            self.play(Create(hline), FadeIn(qv), run_time=0.6)
            self.play(Create(vline), FadeIn(zone), FadeIn(alert), run_time=0.7)
        self.clear_all()


class S02HandsOn(LectureScene):
    def construct(self):
        card = pause_card([label("gap_in_this_range_q"), f"P({W} < X < {L}) = ?"])
        with self.say("2.9"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        ax = axes(1.0, 0.25, 4.2, x_len=7.6, places=2).move_to(LEFT * 2.2 + DOWN * 0.3)
        yl = MathTex("F(x)", font_size=36, color=HILITE).next_to(ax.y_axis, UP, buff=0.15)
        curve = cdf_line(ax)
        lw, ll = lookup(ax, W), lookup(ax, L, color=HILITE)
        vw = MathTex(dec(N["F_within"], 3), font_size=30).next_to(ax.c2p(0.9, F(W)), UP, buff=0.06)
        vl = MathTex(dec(N["F_lull"], 3), font_size=30, color=HILITE).next_to(ax.c2p(2.0, F(L)), UP, buff=0.06)
        for v in (vw, vl):
            v.add_background_rectangle(color=BLACK, opacity=0.95, buff=0.04)
        calc = VGroup(MathTex(rf"F({L}) - F({W})", font_size=44),
                      MathTex(rf"= {dec(N['F_lull'], 3)} - {dec(N['F_within'], 3)}", font_size=44),
                      MathTex(rf"= {dec(N['p_between'], 3)}", font_size=52, color=HILITE)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        calc.move_to(RIGHT * 4.0 + UP * 0.6)
        third = txt(label("just_under_a_third"), size=28, color=GREY_B).next_to(calc, DOWN, buff=0.4)
        with self.say("2.10") as (tr, t):
            self.play(Create(ax), FadeIn(yl), Create(curve), run_time=0.8)
            self.play(Create(ll), FadeIn(vl), run_time=0.6)
            self.cue(tr, t, {"en": "F at two", "uz": "ikkidagi qiymat"})
            self.play(Create(lw), FadeIn(vw), Write(calc[0]), Write(calc[1]), run_time=0.9)
            self.cue(tr, t, {"en": "The difference", "uz": "Ayirmasi"})
            self.play(Write(calc[2]), FadeIn(third), run_time=0.8)
        self.clear_all()

        # the next question: where did this curve come from, and are there other shapes?
        ax2 = axes(0.4, 0.1, 3.4, x_len=8.6).move_to(DOWN * 0.4)
        ax2.x_axis.numbers.set_opacity(0)
        ax2.y_axis.numbers.set_opacity(0)
        expo = pdf_line(ax2)
        flat = Line(ax2.c2p(0, N["delivery_density"]), ax2.c2p(N["delivery"], N["delivery_density"]), color=RLGREEN,
                    stroke_width=4)                      # section 3's uniform, ahead of time
        q = txt(label("other_shapes_q"), size=36, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.5)
        with self.say("2.11") as (tr, t):
            self.play(Create(ax2), Create(expo), run_time=0.8)
            self.cue(tr, t, {"en": "are there other shapes", "uz": "boshqa shakllar ham bormi"})
            self.play(Create(flat), FadeIn(q), run_time=0.8)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S02Area", "S02Cdf", "S02HandsOn"]
