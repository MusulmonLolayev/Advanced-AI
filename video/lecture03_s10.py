"""Lecture 3, section 10 — the Poisson distribution: arrivals at the coffee shop, λ = 4 per ten minutes.

The bars are the figure script's 3000 simulated windows (same generator and seed, captured in
l03_numbers.json); the dots are the Poisson formula. Every number shown comes from N.
"""

from lecture03_kit import *

LAM = N["lam"]
SIM = N["pois_sim"]
PMF = N["pois_pmf"]                      # Poisson(4), k = 0 … 12
RUSH = N["rush"]
SEC = N["seconds"]
PS_NUM, PS_DEN = N["p_second"]           # 1/150
EMPTY_C, RUSH_C, BAR_C = RLRED, RLORANGE, RLBLUE


def count_bars(heights, x0=-5.4, step=0.72, base=-2.3, height=3.6, vmax=None, width=0.5, color=BAR_C, size=24):
    """Bars for k = 0, 1, 2, … with k under each bar. Returns (bars, ks, floor, xs, scale)."""
    vmax = vmax or max(heights)
    sc = height / vmax
    xs = [x0 + k * step for k in range(len(heights))]
    bars = VGroup(*[Rectangle(width=width, height=max(h * sc, 1e-3), stroke_width=0, fill_color=color,
                              fill_opacity=1).move_to([x, base + h * sc / 2, 0]) for x, h in zip(xs, heights)])
    ks = VGroup(*[MathTex(str(k), font_size=size, color=GREY_B).next_to([x, base, 0], DOWN, buff=0.15)
                  for k, x in enumerate(xs)])
    floor = Line([xs[0] - width, base, 0], [xs[-1] + width, base, 0], color=GREY_B, stroke_width=2)
    return bars, ks, floor, xs, sc


def pmf_dots(pmf, xs, base, sc, color=HILITE):
    return VGroup(*[Dot([x, base + p * sc, 0], radius=0.075, color=color) for x, p in zip(xs, pmf)])


def swatch_row(items, size=22):
    """[(mobject icon, words)] as a legend column."""
    return VGroup(*[VGroup(ic, txt(w, size=size, color=GREY_B)).arrange(RIGHT, buff=0.2) for ic, w in items]) \
        .arrange(DOWN, aligned_edge=LEFT, buff=0.2)


class S10Arrivals(LectureScene):
    def construct(self):
        self.section_card(10)
        # one ten-minute window, and the customers who walk in during it
        win = Rectangle(width=9.0, height=0.7, stroke_color=GREY_B, stroke_width=3).move_to(UP * 1.6)
        win_l = txt(label("ten_minute_window"), size=24, color=GREY_B).next_to(win, DOWN, buff=0.2)
        spots = [0.14, 0.41, 0.58, 0.87][:LAM]       # where the arrivals land: a picture, not data
        guests = VGroup(*[Dot(win.get_left() + RIGHT * 9.0 * f, radius=0.13, color=HILITE) for f in spots])
        rate = VGroup(txt(label("average_rate"), size=24, color=GREY_B),
                      MathTex(rf"\lambda = {LAM}", font_size=48, color=HILITE)).arrange(DOWN, buff=0.15)
        rate.next_to(win, UP, buff=0.35)
        with self.say("10.1") as (tr, t):
            self.play(Create(win), FadeIn(win_l), FadeIn(rate), run_time=0.9)
            self.cue(tr, t, {"en": "We count", "uz": "Bitta oʻn daqiqalik"})
            self.play(LaggedStart(*[FadeIn(g, shift=DOWN * 0.6) for g in guests], lag_ratio=0.35), run_time=1.4)

        name = txt(label("dist_poisson"), size=34, weight=BOLD, color=LBLUE).move_to(DOWN * 0.3)
        formula = MathTex(r"P(X = k) = \frac{e^{-\lambda}\,\lambda^{k}}{k!}", font_size=52)
        formula.next_to(name, DOWN, buff=0.35)
        with self.say("10.2") as (tr, t):
            self.play(FadeIn(name), Write(formula), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(Indicate(rate[1], color=HILITE, scale_factor=1.15), run_time=0.8)
        self.clear_all()

        # the binomial needs n; the Poisson never counts the customers who stayed away
        binom = VGroup(txt(label("dist_binomial"), size=34, weight=BOLD, color=GREY_B),
                       MathTex("(", "n", r",\, p)", font_size=48, color=GREY_B)).arrange(RIGHT, buff=0.1)
        pois = VGroup(txt(label("dist_poisson"), size=34, weight=BOLD, color=LBLUE),
                      MathTex(r"(\lambda)", font_size=48, color=HILITE)).arrange(RIGHT, buff=0.1)
        VGroup(binom, pois).arrange(RIGHT, buff=1.6).move_to(UP * 1.6)
        cross = Cross(binom[1][1], stroke_color=RLRED, stroke_width=6).scale(1.4)
        away = txt(label("we_never_count_who_stayed_away"), size=26, color=GREY_B).next_to(binom, DOWN, buff=0.45)
        with self.say("10.3") as (tr, t):
            self.play(FadeIn(binom), FadeIn(pois), run_time=0.8)
            self.cue(tr, t, {"en": "there is no n", "uz": "bu yerda en yoʻq"})
            self.play(Create(cross), run_time=0.6)
            self.play(FadeIn(away, shift=UP * 0.2), run_time=0.6)

        mv = MathTex(r"E[X] = \lambda", r"\qquad", r"\mathrm{Var}(X) = \lambda", font_size=56).move_to(DOWN * 1.2)
        claim = txt(label("a_strong_checkable_claim"), size=26, color=HILITE).next_to(mv, DOWN, buff=0.4)
        with self.say("10.4") as (tr, t):
            self.play(Write(mv), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(FadeIn(claim, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S10Windows(LectureScene):
    def construct(self):
        bars, ks, floor, xs, sc = count_bars(SIM["freq"], vmax=max(max(SIM["freq"]), max(PMF)))
        dots = pmf_dots(PMF, xs, -2.3, sc)
        xl = txt(label("customers_in_a_window"), size=22, color=GREY_B).next_to(ks, DOWN, buff=0.2)
        legend = swatch_row([(Square(0.24, stroke_width=0, fill_color=BAR_C, fill_opacity=1), label("simulated_windows")),
                             (Dot(radius=0.09, color=HILITE), label("poisson_formula"))])
        legend.move_to([4.75, 2.6, 0])
        stats = VGroup(MathTex(rf"\bar{{x}} = {SIM['mean']:.2f}", font_size=40),
                       MathTex(rf"s^2 = {SIM['var']:.2f}", font_size=40),
                       MathTex(rf"\lambda = {LAM}", font_size=40, color=HILITE)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        stats.next_to(legend, DOWN, buff=0.5).align_to(legend, LEFT)
        note = tagged(f"{SIM['windows']:,}", label("simulated_windows"), size=20, color=GREY_B)
        note.to_edge(DOWN, buff=SAFE + 0.1).set_x(-1.0)
        with self.say("10.5") as (tr, t):
            self.play(Create(floor), FadeIn(ks), FadeIn(xl), FadeIn(note), FadeIn(legend[0]),
                      LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06), run_time=1.6)
            self.play(FadeIn(legend[1]), LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.05),
                      run_time=1.0)
            self.cue(tr, t, {"en": "The mean is", "uz": "Oʻrtacha —"})
            self.play(FadeIn(stats[0]), run_time=0.5)
            self.play(FadeIn(stats[1]), run_time=0.5)
            self.cue(tr, t, {"en": "close to each other", "uz": "Ikkalasi"})
            self.play(FadeIn(stats[2]), run_time=0.5)

        # an empty window, and a rush of eight or more
        self.play(FadeOut(stats), run_time=0.3)
        empty_t = VGroup(txt(label("empty"), size=24, color=EMPTY_C),
                         MathTex(rf"P(X = 0) \approx {N['pois_p0']:.3f} \approx \tfrac{{1}}{{{N['pois_empty_one_in']}}}",
                                 font_size=36, color=EMPTY_C)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        rush_t = VGroup(txt(label("rush"), size=24, color=RUSH_C),
                        MathTex(rf"P(X \ge {RUSH}) \approx {N['pois_rush']:.3f}", font_size=36, color=RUSH_C)
                        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        VGroup(empty_t, rush_t).arrange(DOWN, aligned_edge=LEFT, buff=0.45).next_to(legend, DOWN, buff=0.5) \
            .align_to(legend, LEFT)
        with self.say("10.6") as (tr, t):
            self.play(bars[0].animate.set_fill(EMPTY_C), FadeIn(empty_t), run_time=0.8)
            self.cue(tr, t, {"en": "Eight or more", "uz": "Sakkiz yoki"})
            self.play(*[b.animate.set_fill(RUSH_C) for b in bars[RUSH:]], FadeIn(rush_t), run_time=0.8)
        self.clear_all()

        # a ten-hour day: sixty windows, about three of them rushes
        day = VGroup(*[Square(0.42, stroke_color=GREY_B, stroke_width=1.5, fill_color=GREY_E, fill_opacity=1)
                       for _ in range(N["day_windows"])]).arrange_in_grid(rows=4, buff=0.1).move_to(UP * 0.4)
        day_l = VGroup(txt(label("a_ten_hour_day"), size=28, weight=BOLD),
                       tagged(N["day_windows"], label("windows"), size=24, color=GREY_B)).arrange(DOWN, buff=0.15)
        day_l.next_to(day, UP, buff=0.3)
        n_rush = round(N["day_rushes"])
        picks = [round((i + 0.5) * len(day) / n_rush) + 3 for i in range(n_rush)]   # where they fall: a picture
        calc = MathTex(rf"{N['day_windows']} \times {N['pois_rush']:.3f} \approx {N['day_rushes']:.1f}",
                       font_size=46, color=RUSH_C).next_to(day, DOWN, buff=0.45)
        ill = info(label("illustration"))
        with self.say("10.7") as (tr, t):
            self.play(FadeIn(day_l), LaggedStart(*[FadeIn(s) for s in day], lag_ratio=0.01), run_time=1.2)
            self.cue(tr, t, 1)
            self.play(*[day[i].animate.set_fill(RUSH_C) for i in picks], Write(calc), FadeIn(ill), run_time=1.0)
        self.clear_all()


class S10Meet(LectureScene):
    def construct(self):
        # ten minutes cut into 600 seconds, each with a 1/150 chance of an arrival
        strip = Rectangle(width=11.0, height=0.45, stroke_color=GREY_B, stroke_width=2).move_to(UP * 2.9)
        ticks = VGroup(*[Line(strip.get_left() + RIGHT * 11.0 * i / SEC + UP * 0.22,
                              strip.get_left() + RIGHT * 11.0 * i / SEC + DOWN * 0.22, stroke_width=0.6,
                              color=GREY_D) for i in range(1, SEC)])
        secs = tagged(SEC, label("seconds"), size=24, color=GREY_B).next_to(strip, DOWN, buff=0.15)
        np_eq = MathTex(rf"n\,p = {SEC} \times \tfrac{{{PS_NUM}}}{{{PS_DEN}}} = {LAM}", font_size=44, color=HILITE)
        np_eq.next_to(secs, DOWN, buff=0.3)
        # Binomial(600, 1/150), captured and tested (capture_l03.py), drawn against the Poisson dots
        binom = N["bin600_pmf"][:len(PMF)]
        bars, ks, floor, xs, sc = count_bars(binom, x0=-5.0, base=-2.6, height=2.8, vmax=max(max(binom), max(PMF)),
                                             color=LBLUE)
        dots = pmf_dots(PMF, xs, -2.6, sc)
        legend = swatch_row([(Square(0.24, stroke_width=0, fill_color=LBLUE, fill_opacity=1), label("dist_binomial")),
                             (Dot(radius=0.09, color=HILITE), label("dist_poisson"))])
        legend.move_to([4.6, 0.2, 0])
        diff = VGroup(txt(label("largest_difference"), size=24, color=GREY_B),
                      MathTex(rf"\approx {N['bin_vs_pois']:.4f}", font_size=40, color=HILITE)).arrange(DOWN, buff=0.12)
        diff.next_to(legend, DOWN, buff=0.45)
        with self.say("10.8") as (tr, t):
            self.play(Create(strip), run_time=0.5)
            self.cue(tr, t, {"en": "split the ten minutes", "uz": "oʻn daqiqani"})
            self.play(Create(ticks, lag_ratio=0.002), FadeIn(secs), run_time=1.0)
            self.cue(tr, t, {"en": "n times p", "uz": "En karra pi"})
            self.play(Write(np_eq), run_time=0.8)
            self.play(Create(floor), FadeIn(ks), FadeIn(legend),
                      LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.05), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.05), run_time=0.8)
            self.cue(tr, t, {"en": "and the two distributions", "uz": "va ikki taqsimot"})
            self.play(FadeIn(diff, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S10Server(LectureScene):
    def construct(self):
        # AI: requests to a model's server per second; a very unlikely count is a warning
        server = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.6, stroke_color=LBLUE, stroke_width=3)
        server.move_to(LEFT * 3.9 + UP * 0.6)
        s_l = txt(label("model_server"), size=24, color=LBLUE).move_to(server)
        reqs = VGroup(*[Arrow(LEFT * 1.0, ORIGIN, buff=0, color=GREY_B, stroke_width=3,
                              max_tip_length_to_length_ratio=0.25).next_to(server, LEFT, buff=0.1)
                        .shift(UP * (0.45 - 0.3 * i)) for i in range(LAM)])
        bars, ks, floor, xs, sc = count_bars(PMF, x0=-1.6, step=0.62, base=-2.0, height=3.2, width=0.42)
        xl = txt(label("requests_per_second"), size=22, color=GREY_B).next_to(ks, DOWN, buff=0.15)
        far = len(PMF) - 1
        warn = VGroup(txt(label("unusual"), size=26, color=RLRED),
                      MathTex(rf"P(X = {far}) \approx {PMF[far]:.4f}", font_size=34, color=RLRED)
                      ).arrange(DOWN, buff=0.12).next_to(bars[far], UP, buff=0.9).shift(LEFT * 0.6)
        ptr = Arrow(warn.get_bottom(), bars[far].get_top() + UP * 0.05, buff=0.08, color=RLRED, stroke_width=3,
                    max_tip_length_to_length_ratio=0.2)
        ill = info(label("illustration"))
        with self.say("10.9") as (tr, t):
            self.play(Create(server), FadeIn(s_l), FadeIn(ill), run_time=0.7)
            self.play(LaggedStart(*[GrowArrow(a) for a in reqs], lag_ratio=0.25), run_time=0.9)
            self.play(Create(floor), FadeIn(ks), FadeIn(xl),
                      LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.05), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(bars[far].animate.set_fill(RLRED), FadeIn(warn), GrowArrow(ptr), run_time=0.8)
        self.clear_all()


class S10HandsOn(LectureScene):
    def construct(self):
        card = pause_card([label("how_many_empty_windows_in_a_day_q"),
                           f"{N['day_windows']} × P(X = 0) = ?"])
        with self.say("10.10"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        day = VGroup(*[Square(0.42, stroke_color=GREY_B, stroke_width=1.5, fill_color=GREY_E, fill_opacity=1)
                       for _ in range(N["day_windows"])]).arrange_in_grid(rows=4, buff=0.1).move_to(UP * 0.9)
        n_empty = round(N["day_empty"])
        calc = MathTex(rf"{N['day_windows']} \times {N['pois_p0']:.3f} \approx {N['day_empty']:.1f}",
                       font_size=52, color=EMPTY_C).next_to(day, DOWN, buff=0.5)
        e_l = tagged(f"≈ {n_empty}", label("empty"), size=30, color=EMPTY_C).next_to(calc, DOWN, buff=0.3)
        with self.say("10.11") as (tr, t):
            self.play(FadeIn(day), Write(calc), run_time=1.0)
            self.play(*[day[27 + i].animate.set_fill(BLACK).set_stroke(EMPTY_C, width=3) for i in range(n_empty)],
                      FadeIn(e_l), run_time=0.6)
        self.clear_all()

        # the next question: where do the shares come from, and how sure are we?
        cups = list(N["cups"].items())
        sc = 3.6 / max(v for _, v in cups)
        xs = [-2.4, 0.0, 2.4]
        bars = VGroup(*[Rectangle(width=1.3, height=v * sc, stroke_width=0, fill_color=LBLUE, fill_opacity=1)
                        .move_to([x, -2.2 + v * sc / 2, 0]) for x, (_, v) in zip(xs, cups)])
        vals = VGroup(*[MathTex(dec(v), font_size=36).next_to(b, UP, buff=0.12) for b, (_, v) in zip(bars, cups)])
        names = VGroup(*[txt(CUP_NAME[k], size=26, color=GREY_B).next_to([x, -2.2, 0], DOWN, buff=0.2)
                         for x, (k, _) in zip(xs, cups)])
        qs = VGroup(*[txt("?", size=44, weight=BOLD, color=HILITE).next_to(v, UP, buff=0.15) for v in vals])
        with self.say("10.12") as (tr, t):
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2), FadeIn(vals), FadeIn(names),
                      run_time=1.0)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(q, scale=0.5) for q in qs], lag_ratio=0.2), run_time=0.8)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S10Arrivals", "S10Windows", "S10Meet", "S10Server", "S10HandsOn"]
