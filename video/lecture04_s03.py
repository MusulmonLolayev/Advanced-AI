"""Lecture 4, section 3 — the uniform and the exponential, and the exponential's missing memory.

A delivery promised within ten minutes (density 0.1, first three minutes 0.3); the gap between customers
(f = 0.4 e^(-0.4x), mean 2.5 minutes); the same process seen as Poisson counts and exponential gaps;
P(X > 5 | X > 3) = e^(-0.8) = 0.449 = P(X > 2). Every number shown comes from N (l04_numbers.json).
"""
from math import exp

from lecture04_kit import *

RATE, MEAN_GAP = N["rate"], N["mean_gap"]
DELIV, DENS = N["delivery"], N["delivery_density"]
FIRST, LAST = N["first"], N["last"]
WAITED, LULL = N["waited"], N["lull"]
X_MAX = round(N["pdf_curve"][-1][0])               # the captured curve's range, 12 minutes
UNI_C, EXP_C = RLGREEN, LBLUE


def f_exp(x):
    return RATE * exp(-RATE * x)


def axes(x_max, x_step, y_max, y_step, x_len=8.0, y_len=3.6, size=22):
    return Axes(x_range=[0, x_max, x_step], y_range=[0, y_max, y_step], x_length=x_len, y_length=y_len,
                tips=False, axis_config={"color": GREY_B, "stroke_width": 2, "include_numbers": True,
                                         "font_size": size})


def uniform_panel(center=ORIGIN, x_len=8.0, y_len=3.0):
    """Axes placed first, then the flat density on them (plotting before moving leaves the curve behind)."""
    ax = axes(DELIV, 1, 0.15, 0.05, x_len=x_len, y_len=y_len).move_to(center)
    flat = Line(ax.c2p(0, DENS), ax.c2p(DELIV, DENS), color=UNI_C, stroke_width=5)
    return ax, flat


def band(ax, a, b, h, color, opacity):
    """The exact area under a flat density between a and b."""
    return Polygon(ax.c2p(a, 0), ax.c2p(b, 0), ax.c2p(b, h), ax.c2p(a, h), stroke_width=0,
                   fill_color=color, fill_opacity=opacity)


def exp_panel(center=ORIGIN, x_len=8.0, y_len=3.4):
    ax = axes(X_MAX, 2, 0.45, 0.1, x_len=x_len, y_len=y_len).move_to(center)
    curve = ax.plot(f_exp, x_range=[0, X_MAX], color=EXP_C, stroke_width=5)
    return ax, curve


def note_below(ax, key_text, size=22):
    return txt(key_text, size=size, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.5)


class S03Uniform(LectureScene):
    def construct(self):
        self.section_card(3)
        name = txt(label("dist_uniform"), size=36, weight=BOLD, color=UNI_C).to_edge(UP, buff=SAFE + 0.3)
        ax, flat = uniform_panel(DOWN * 0.4)
        xl = note_below(ax, label("delivery_minute"))
        fill = band(ax, 0, DELIV, DENS, UNI_C, 0.18)
        with self.say("3.1") as (tr, t):
            self.play(FadeIn(name), Create(ax), FadeIn(xl), run_time=1.0)
            self.play(Create(flat), FadeIn(fill), run_time=0.9)

        promise = txt(label("within_ten_minutes"), size=30, color=HILITE).next_to(name, DOWN, buff=0.3)
        dens = MathTex(rf"f(x) = {dec(DENS)}", font_size=40, color=UNI_C).next_to(ax.c2p(DELIV, DENS), UR, buff=0.15)
        dens.shift(LEFT * 1.6 + UP * 0.25)
        first = band(ax, 0, FIRST, DENS, HILITE, 0.6)
        p_first = MathTex(rf"P(X < {FIRST}) = \tfrac{{{FIRST}}}{{{DELIV}}} = {dec(N['p_first'])}", font_size=40,
                          color=HILITE).next_to(ax.c2p(FIRST / 2, DENS), UP, buff=0.55).shift(RIGHT * 1.2)
        with self.say("3.2") as (tr, t):
            self.play(FadeIn(promise, shift=DOWN * 0.2), run_time=0.6)
            self.cue(tr, t, {"en": "The density", "uz": "Zichlik"})
            self.play(Write(dens), run_time=0.7)
            self.cue(tr, t, {"en": "The chance it lands", "uz": "Birinchi uch daqiqada"})
            self.play(FadeIn(first), Write(p_first), run_time=0.9)
        self.clear_all()


class S03Exponential(LectureScene):
    def construct(self):
        name = txt(label("dist_exponential"), size=36, weight=BOLD, color=EXP_C).to_edge(UP, buff=SAFE + 0.3)
        ax, curve = exp_panel(DOWN * 0.5)
        xl = note_below(ax, label("minutes_to_next_customer"))
        f = MathTex(r"f(x) = \lambda e^{-\lambda x}", font_size=44).move_to(ax.c2p(7.5, 0.36))
        mean = MathTex(rf"E[X] = \frac{{1}}{{\lambda}} = \frac{{1}}{{{dec(RATE)}}} = {dec(MEAN_GAP)}", font_size=40,
                       color=EXP_C).next_to(f, DOWN, buff=0.3)
        with self.say("3.3") as (tr, t):
            self.play(FadeIn(name), Create(ax), FadeIn(xl), run_time=1.0)
            self.play(Create(curve), Write(f), run_time=1.0)
            self.cue(tr, t, {"en": "The average wait", "uz": "Oʻrtacha kutish"})
            self.play(Write(mean), run_time=0.8)
        self.clear_all()

        # the two shapes side by side
        ua, uf2 = uniform_panel(LEFT * 3.4 + DOWN * 0.3, x_len=5.2, y_len=2.6)
        ea, ec2 = exp_panel(RIGHT * 3.4 + DOWN * 0.3, x_len=5.2, y_len=2.6)
        un = txt(label("dist_uniform"), size=30, weight=BOLD, color=UNI_C).next_to(ua, UP, buff=0.35)
        en = txt(label("dist_exponential"), size=30, weight=BOLD, color=EXP_C).next_to(ea, UP, buff=0.35)
        us = txt(label("no_moment_is_special"), size=24, color=UNI_C).next_to(ua.x_axis, DOWN, buff=0.55)
        es = txt(label("short_waits_are_commonest"), size=24, color=EXP_C).next_to(ea.x_axis, DOWN, buff=0.55)
        short = ea.get_area(ec2, x_range=[0, N["within"]], color=EXP_C, opacity=0.5)
        with self.say("3.4") as (tr, t):
            self.play(Create(ua), Create(uf2), FadeIn(un), Create(ea), Create(ec2), FadeIn(en), run_time=1.0)
            self.cue(tr, t, {"en": "under the uniform", "uz": "tekisda"})
            self.play(FadeIn(us), Indicate(uf2, color=WHITE, scale_factor=1.04), run_time=0.8)
            self.cue(tr, t, {"en": "under the exponential", "uz": "eksponensialda esa"})
            self.play(FadeIn(es), FadeIn(short), run_time=0.8)
        self.clear_all()


class S03Process(LectureScene):
    def construct(self):
        # one stream of arrivals, seen two ways: counts per window, and the gaps between
        L = 11.0
        line = NumberLine(x_range=[0, 20, 10], length=L, include_numbers=False, color=GREY_B)
        line.move_to(DOWN * 0.2)
        spots = [1.3, 2.6, 3.1, 6.4, 8.9, 11.2, 12.0, 14.7, 17.9, 19.2]   # a picture of arrivals, not data
        guests = VGroup(*[Dot(line.n2p(s), radius=0.12, color=HILITE) for s in spots])
        windows = VGroup(*[Rectangle(width=L / 2 - 0.08, height=0.9, stroke_color=LBLUE, stroke_width=3)
                           .move_to(line.n2p(5 + 10 * k)) for k in (0, 1)])
        pc = txt(label("poisson_how_many"), size=26, color=LBLUE).next_to(windows, UP, buff=0.55)
        wl = VGroup(*[txt(label("ten_minute_window"), size=20, color=LBLUE).next_to(w, UP, buff=0.08) for w in windows])
        gaps = VGroup(*[BraceBetweenPoints(line.n2p(a), line.n2p(b), DOWN, color=EXP_C, buff=0.6)
                        for a, b in zip(spots[3:5], spots[4:6])])
        ec = txt(label("exponential_how_long"), size=26, color=EXP_C).next_to(gaps, DOWN, buff=0.3)
        ec.set_x(line.n2p(10)[0])
        title = txt(label("one_process_two_views"), size=34, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        note = info(label("illustration"))
        with self.say("3.5") as (tr, t):
            self.play(FadeIn(title), Create(line), FadeIn(note), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(g, scale=0.5) for g in guests], lag_ratio=0.12), run_time=1.0)
            self.cue(tr, t, {"en": "The Poisson counts", "uz": "Puasson oʻn daqiqada"})
            self.play(Create(windows), FadeIn(wl), run_time=0.6)
            self.play(FadeIn(pc), run_time=0.4)
            self.cue(tr, t, {"en": "the exponential measures", "uz": "eksponensial esa"})
            self.play(*[GrowFromCenter(g) for g in gaps], FadeIn(ec), run_time=0.8)
        self.clear_all()


class S03Memory(LectureScene):
    def construct(self):
        ax, curve = exp_panel(DOWN * 0.7 + LEFT * 0.4, x_len=8.4, y_len=3.6)
        xl = note_below(ax, label("minutes_to_next_customer"))
        waited = ax.get_area(curve, x_range=[0, WAITED], color=GREY_D, opacity=0.7)
        w_lab = txt(label("already_waited"), size=22, color=WHITE).move_to(ax.c2p(WAITED / 2, 0.06))
        if w_lab.width > ax.c2p(WAITED, 0)[0] - ax.c2p(0, 0)[0] - 0.1:
            w_lab.scale_to_fit_width(ax.c2p(WAITED, 0)[0] - ax.c2p(0, 0)[0] - 0.1)
        beyond = ax.get_area(curve, x_range=[LULL, X_MAX], color=HILITE, opacity=0.55)
        # the tail after three minutes, moved back to zero and scaled up, lies exactly on the curve
        tail = ax.plot(f_exp, x_range=[WAITED, X_MAX], color=HILITE, stroke_width=5)
        lifted = ax.plot(lambda x: f_exp(x + WAITED) * exp(RATE * WAITED), x_range=[0, X_MAX - WAITED],
                         color=HILITE, stroke_width=5)
        formula = MathTex(rf"P(X > {LULL} \mid X > {WAITED}) = \frac{{e^{{-{dec(RATE * LULL)}}}}}{{e^{{-{dec(RATE * WAITED)}}}}}"
                          rf" = e^{{-{dec(RATE * (LULL - WAITED))}}} = {dec(N['p_more_given'], 3)} = P(X > {LULL - WAITED})",
                          font_size=38, color=HILITE).to_edge(UP, buff=SAFE + 0.35)
        with self.say("3.6") as (tr, t):
            self.play(Create(ax), Create(curve), FadeIn(xl), run_time=0.9)
            self.play(FadeIn(waited), FadeIn(w_lab), run_time=0.6)
            self.cue(tr, t, {"en": "What is the chance", "uz": "Yana ikki daqiqadan"})
            self.play(FadeIn(beyond), Create(tail), run_time=0.8)
            self.cue(tr, t, {"en": "Zero point four four nine", "uz": "Nol butun mingdan"})
            self.play(Write(formula), Transform(tail, lifted), run_time=1.4)

        mem = txt(label("memoryless_property"), size=34, weight=BOLD, color=LBLUE).next_to(formula, DOWN, buff=0.35)
        link = txt(f"{label('lecture_3')} · {label('dist_poisson')}", size=26, color=GREY_B).next_to(mem, DOWN, buff=0.2)
        with self.say("3.7") as (tr, t):
            self.play(FadeIn(mem, shift=DOWN * 0.2), Indicate(tail, color=WHITE, scale_factor=1.03), run_time=0.9)
            self.cue(tr, t, {"en": "The Poisson of the third lecture", "uz": "Uchinchi maʼruzadagi Puasson"})
            self.play(FadeIn(link), run_time=0.6)
        self.clear_all()


class S03Lunch(LectureScene):
    def construct(self):
        # real arrivals bunch at lunchtime, and then neither model fits
        L = 11.0
        line = NumberLine(x_range=[0, 20, 10], length=L, include_numbers=False, color=GREY_B).move_to(UP * 0.6)
        quiet = [0.8, 4.1, 7.6]
        rush = [9.2, 9.5, 9.7, 10.0, 10.2, 10.3, 10.6, 10.9, 11.1, 11.4]
        late = [15.3, 18.6]
        guests = VGroup(*[Dot(line.n2p(s), radius=0.12, color=HILITE) for s in quiet + rush + late])
        lunch = BraceBetweenPoints(line.n2p(rush[0]), line.n2p(rush[-1]), UP, color=RLRED, buff=0.3)
        l_lab = txt(label("lunchtime"), size=26, color=RLRED).next_to(lunch, UP, buff=0.15)
        claim = txt(label("a_strong_claim_about_the_world"), size=34, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        note = info(label("illustration"))
        with self.say("3.8") as (tr, t):
            self.play(FadeIn(claim), Create(line), FadeIn(note), run_time=0.8)
            self.cue(tr, t, {"en": "Real customers cluster", "uz": "Haqiqatda tushlik"})
            self.play(LaggedStart(*[FadeIn(g, scale=0.5) for g in guests], lag_ratio=0.06), run_time=1.0)
            self.play(GrowFromCenter(lunch), FadeIn(l_lab), run_time=0.7)

        # the AI use: requests arriving in waves, against capacity planned on a steady rate
        ax = Axes(x_range=[0, 12, 1], y_range=[0, 10, 2], x_length=7.4, y_length=2.2, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2}).move_to(DOWN * 1.6 + RIGHT * 0.8)
        wave = ax.plot(lambda x: 4 + 3.6 * exp(-((x - 6.5) ** 2) / 1.6), x_range=[0, 12], color=HILITE, stroke_width=4)
        cap = DashedLine(ax.c2p(0, 5.5), ax.c2p(12, 5.5), color=LBLUE, stroke_width=3)
        over = ax.get_area(wave, x_range=[5.3, 7.7], bounded_graph=ax.plot(lambda x: 5.5, x_range=[5.3, 7.7]),
                           color=RLRED, opacity=0.6)
        srv = txt(label("model_server"), size=24, weight=BOLD, color=GREY_B).next_to(ax, LEFT, buff=0.3).shift(UP * 0.6)
        req = txt(label("requests_per_second"), size=20, color=HILITE).next_to(srv, DOWN, buff=0.15)
        # a legend on the left: the label is too long to sit on the line beside the wave
        c_lab = VGroup(DashedLine(ORIGIN, RIGHT * 0.45, color=LBLUE, stroke_width=3),
                       txt(label("capacity_planned"), size=18, color=LBLUE)).arrange(RIGHT, buff=0.15)
        short = txt(label("falls_short"), size=22, color=RLRED).next_to(ax.c2p(6.5, 7.6), UP, buff=0.1)
        VGroup(srv, req).next_to(ax, LEFT, buff=0.35)
        c_lab.next_to(req, DOWN, buff=0.3).align_to(req, RIGHT)
        with self.say("3.9") as (tr, t):
            self.play(line.animate.shift(UP * 0.4), guests.animate.shift(UP * 0.4), lunch.animate.shift(UP * 0.4),
                      l_lab.animate.shift(UP * 0.4), run_time=0.5)
            self.play(Create(ax), FadeIn(srv), FadeIn(req), Create(wave), run_time=1.0)
            self.cue(tr, t, {"en": "capacity planned", "uz": "rejalashtirilgan quvvat"})
            self.play(Create(cap), FadeIn(c_lab), run_time=0.7)
            self.play(FadeIn(over), FadeIn(short), run_time=0.6)
        self.clear_all()


class S03HandsOn(LectureScene):
    def construct(self):
        card = pause_card([f"{label('within_ten_minutes')}:  0 – {DELIV} {label('minutes', 1)}",
                           f"P({DELIV - LAST} < X < {DELIV}) = ?"])
        card.to_edge(UP, buff=SAFE + 0.3)
        with self.say("3.10"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        ax, flat = uniform_panel(DOWN * 0.6)
        xl = note_below(ax, label("delivery_minute"))
        last = band(ax, DELIV - LAST, DELIV, DENS, HILITE, 0.6)
        p_last = MathTex(rf"P({DELIV - LAST} < X < {DELIV}) = \tfrac{{{LAST}}}{{{DELIV}}} = {dec(N['p_last'])}",
                         font_size=42, color=HILITE).to_edge(UP, buff=SAFE + 0.5)
        only = txt(label("only_the_length_matters"), size=28, color=UNI_C).next_to(p_last, DOWN, buff=0.3)
        with self.say("3.11") as (tr, t):
            self.play(Create(ax), Create(flat), FadeIn(xl), run_time=0.8)
            self.play(FadeIn(last), Write(p_last), run_time=0.9)
            self.cue(tr, t, {"en": "Under the uniform", "uz": "Tekis taqsimotda"})
            self.play(FadeIn(only), run_time=0.6)
        self.clear_all()

        q = txt(label("how_does_a_computer_make_random_numbers_q"), size=36, weight=BOLD, color=HILITE)
        with self.say("3.12"):
            self.play(FadeIn(q, shift=UP * 0.2), run_time=0.8)
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S03Uniform", "S03Exponential", "S03Process", "S03Memory", "S03Lunch", "S03HandsOn"]
