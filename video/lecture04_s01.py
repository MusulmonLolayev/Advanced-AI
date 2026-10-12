"""Lecture 4, section 1 — density: a value has probability zero, so ranges carry it as area.

The histograms are the figure script's 20,000 simulated gaps between customers (same generator and
seed, captured in l04_numbers.json as bin counts and heights); the curve is f(x) = 0.4 e^(−0.4x)
sampled in the same file. Every number shown comes from N.
"""
from math import exp

from lecture04_kit import *

RATE = N["rate"]
H2, H025 = N["hist"]["2.0"], N["hist"]["0.25"]
CURVE = N["pdf_curve"]                      # [[x, f(x)]], x from 0 to 12
X_MAX = H2["edges"][-1]
BAR_C, AREA_C = RLGREEN, LBLUE


def f(x):
    return RATE * exp(-RATE * x)


def gap_axes(y_max=0.4, x_len=9.6, y_len=4.0):
    return Axes(x_range=[0, X_MAX, 2], y_range=[0, y_max, 0.1], x_length=x_len, y_length=y_len, tips=False,
                axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 26},
                x_axis_config={"include_numbers": True},
                y_axis_config={"include_numbers": True, "decimal_number_config": {"num_decimal_places": 1}})


def hist_bars(ax, h, color=BAR_C, opacity=0.8):
    """One histogram from the captured heights: total area 1."""
    w = h["width"]
    return VGroup(*[Rectangle(width=ax.c2p(w, 0)[0] - ax.c2p(0, 0)[0], height=max(ax.c2p(0, y)[1] - ax.c2p(0, 0)[1], 1e-3),
                              stroke_color=BLACK, stroke_width=0.6 if w < 1 else 1.5, fill_color=color,
                              fill_opacity=opacity).move_to(ax.c2p(e + w / 2, y / 2))
                    for e, y in zip(h["edges"], h["heights"])])


def density_curve(ax, color=LBLUE, width=4):
    return ax.plot_line_graph([x for x, _ in CURVE], [y for _, y in CURVE], add_vertex_dots=False,
                              line_color=color, stroke_width=width)["line_graph"]


def area(ax, a, b, color=AREA_C, opacity=0.55):
    xs = [a] + [x for x, _ in CURVE if a < x < b] + [b]
    pts = [ax.c2p(a, 0)] + [ax.c2p(x, f(x)) for x in xs] + [ax.c2p(b, 0)]
    return Polygon(*pts, stroke_width=0, fill_color=color, fill_opacity=opacity)


class S01Gaps(LectureScene):
    def construct(self):
        self.section_card(1)
        # a stretch of the day: customers walk in; the time between two of them is measured
        line_ = NumberLine(x_range=[0, X_MAX, 2], length=11, color=GREY_B, include_numbers=True, font_size=22)
        line_.move_to(UP * 0.6)
        unit = txt(label("minutes", 1), size=22, color=GREY_B).next_to(line_, RIGHT, buff=0.25)
        spots = [0.6, 3.1, 4.0, 7.3, 9.4, 10.2]            # where they walk in: a picture, not data
        guests = VGroup(*[Dot(line_.n2p(s) + UP * 0.45, radius=0.13, color=HILITE) for s in spots])
        a, b = guests[3].get_center(), guests[4].get_center()
        gap = BraceBetweenPoints(a + UP * 0.25, b + UP * 0.25, UP, color=LBLUE)
        gap_l = txt(label("gap_between_customers"), size=26, color=LBLUE).next_to(gap, UP, buff=0.12)
        note = info(label("illustration"))
        with self.say("1.1") as (tr, t):
            self.play(Create(line_), FadeIn(unit), FadeIn(note), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(g, shift=DOWN * 0.5) for g in guests], lag_ratio=0.25), run_time=1.3)
            self.cue(tr, t, {"en": "the time between", "uz": "orasidagi vaqtni"})
            self.play(GrowFromCenter(gap), FadeIn(gap_l), run_time=0.7)
        self.clear_all()

        # between two and three minutes the possible answers cannot be listed
        lo, hi = N["between"]
        zoom = NumberLine(x_range=[lo, hi, 0.1], length=10, color=GREY_B, include_numbers=False).move_to(UP * 0.4)
        ends = VGroup(MathTex(str(lo), font_size=36).next_to(zoom.n2p(lo), DOWN, buff=0.25),
                      MathTex(str(hi), font_size=36).next_to(zoom.n2p(hi), DOWN, buff=0.25))
        fine = VGroup(*[Line(UP * 0.08, DOWN * 0.08, stroke_width=1, color=GREY_C).move_to(zoom.n2p(lo + k / 100))
                        for k in range(1, 100) if k % 10])
        x25 = Dot(zoom.n2p(N["exact"]), radius=0.1, color=HILITE)
        x25_l = MathTex(dec(N["exact"]), font_size=36, color=HILITE).next_to(x25, UP, buff=0.2)
        many = txt(label("infinitely_many_answers"), size=30, color=LBLUE).to_edge(UP, buff=SAFE + 0.6)
        cont = txt(label("continuous"), size=34, weight=BOLD, color=HILITE).next_to(zoom, DOWN, buff=1.0)
        with self.say("1.2") as (tr, t):
            self.play(Create(zoom), FadeIn(ends), run_time=0.8)
            self.play(FadeIn(x25, scale=1.5), FadeIn(x25_l), run_time=0.5)
            self.play(LaggedStart(*[Create(m) for m in fine], lag_ratio=0.01), FadeIn(many), run_time=1.2)
            self.cue(tr, t, {"en": "We call such", "uz": "Bunday miqdorni"})
            self.play(FadeIn(cont, shift=UP * 0.2), run_time=0.6)

        zero = MathTex(rf"P(X = {dec(N['exact'])}) = 0", font_size=56, color=HILITE).next_to(zoom, DOWN, buff=1.0)
        with self.say("1.3") as (tr, t):
            self.play(FadeOut(cont), run_time=0.3)
            self.cue(tr, t, {"en": "So the chance", "uz": "Shuning uchun"})
            self.play(Write(zero), Indicate(x25, color=HILITE, scale_factor=1.6), run_time=1.0)

        band = Rectangle(width=zoom.n2p(hi)[0] - zoom.n2p(lo)[0], height=0.5, stroke_width=0,
                         fill_color=LBLUE, fill_opacity=0.35).move_to(zoom.n2p((lo + hi) / 2))
        rng = MathTex(rf"P({lo} < X < {hi})", font_size=56, color=LBLUE).move_to(zero)
        ask = txt(label("ask_about_a_range"), size=28, color=GREY_B).next_to(rng, DOWN, buff=0.35)
        with self.say("1.4") as (tr, t):
            self.play(FadeIn(band), FadeOut(x25), FadeOut(x25_l), Transform(zero, rng), run_time=0.9)
            self.play(FadeIn(ask, shift=UP * 0.2), run_time=0.6)
        self.clear_all()


class S01Density(LectureScene):
    def construct(self):
        ax = gap_axes().move_to(DOWN * 0.3 + RIGHT * 0.3)
        xl = txt(label("gap_axis"), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.95)
        yl = txt(label("density"), size=22, color=GREY_B).next_to(ax.y_axis, UP, buff=0.15)
        wide = hist_bars(ax, H2)
        narrow = hist_bars(ax, H025)
        n_l = tagged(f"{N['n_gaps']:,}", label("simulated_gaps"), size=26, color=GREY_B)
        n_l.to_corner(UR, buff=SAFE + 0.4)

        def width_tag(h):
            return VGroup(txt(f"{label('bin_width')}: {dec(h['width'])} {label('minutes', 1)}", size=26),
                          tagged(h["bars"], label("bars_word"), size=26, color=HILITE)) \
                .arrange(DOWN, aligned_edge=RIGHT, buff=0.15).next_to(n_l, DOWN, buff=0.3, aligned_edge=RIGHT)

        tag2, tag025 = width_tag(H2), width_tag(H025)
        total = VGroup(txt(label("total_area"), size=26, color=GREY_B), MathTex("= 1", font_size=36)) \
            .arrange(RIGHT, buff=0.15).next_to(tag2, DOWN, buff=0.3, aligned_edge=RIGHT)
        with self.say("1.5") as (tr, t):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(n_l), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in wide], lag_ratio=0.15), FadeIn(tag2), run_time=1.2)
            self.play(FadeIn(total), run_time=0.5)

        curve = density_curve(ax)
        f_l = MathTex(r"f(x) = 0.4\,e^{-0.4x}".replace("0.4", dec(RATE)), font_size=36, color=LBLUE)
        f_l.next_to(ax.c2p(1.3, f(1.3)), RIGHT, buff=0.35)
        f_l.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06)
        name = txt(label("density"), size=30, weight=BOLD, color=LBLUE).next_to(f_l, UP, buff=0.15, aligned_edge=LEFT)
        with self.say("1.6") as (tr, t):
            self.cue(tr, t, {"en": "A quarter of a minute", "uz": "Chorak daqiqalik"})
            self.play(ReplacementTransform(wide, narrow), Transform(tag2, tag025), run_time=1.4)
            self.cue(tr, t, {"en": "Keep narrowing", "uz": "Ustunlarni toraytirib"})
            self.play(Create(curve), narrow.animate.set_fill(opacity=0.35), run_time=1.4)
            self.cue(tr, t, {"en": "That curve is", "uz": "Bu egri chiziqni"})
            self.play(FadeIn(f_l), FadeIn(name), run_time=0.6)

        # probability as area under the curve
        shade = area(ax, 2, 3)
        formula = MathTex(r"P(a < X < b) = \int_a^b f(x)\,dx", font_size=44).to_edge(UP, buff=SAFE + 0.25)
        pdf_name = txt(label("probability_density_function"), size=26, color=GREY_B).next_to(formula, DOWN, buff=0.12)
        ab = VGroup(MathTex("a", font_size=32, color=LBLUE).next_to(ax.c2p(2, 0), DOWN, buff=0.6),
                    MathTex("b", font_size=32, color=LBLUE).next_to(ax.c2p(3, 0), DOWN, buff=0.6))
        whole = MathTex(r"\int_0^\infty f(x)\,dx = 1", font_size=36).next_to(tag2, DOWN, buff=0.35, aligned_edge=RIGHT)
        with self.say("1.7") as (tr, t):
            self.play(FadeOut(narrow), FadeOut(name), FadeOut(total), FadeOut(n_l), FadeOut(tag2),
                      Write(formula), FadeIn(pdf_name), run_time=1.0)
            self.cue(tr, t, {"en": "the chance of landing", "uz": "ey va bi orasida"})
            self.play(FadeIn(shade), FadeIn(ab), run_time=0.8)
            self.cue(tr, t, {"en": "The whole area", "uz": "Butun yuz"})
            self.play(FadeIn(area(ax, 0, X_MAX, opacity=0.15)), FadeIn(whole), run_time=0.8)

        # the integral is the sum of Lecture 3 with infinitely thin bars
        thin = VGroup(*[Rectangle(width=ax.c2p(0.1, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, f(2.05 + k * 0.1))[1] - ax.c2p(0, 0)[1],
                                  stroke_width=0.5, stroke_color=BLACK, fill_color=HILITE, fill_opacity=0.8)
                        .move_to(ax.c2p(2.05 + k * 0.1, f(2.05 + k * 0.1) / 2)) for k in range(10)])
        sig = VGroup(MathTex(r"\sum", font_size=56), MathTex(r"\to", font_size=44), MathTex(r"\int", font_size=56),
                     txt(label("add_up_the_area"), size=26, color=HILITE)).arrange(RIGHT, buff=0.3)
        sig.next_to(whole, DOWN, buff=0.4, aligned_edge=RIGHT)
        with self.say("1.8") as (tr, t):
            self.play(FadeIn(thin, lag_ratio=0.1), FadeIn(sig[0]), run_time=0.9)
            self.play(FadeIn(sig[1]), FadeIn(sig[2]), FadeIn(sig[3]), FadeOut(thin), run_time=0.8)

        not_p = txt(label("a_density_is_not_a_probability"), size=28, weight=BOLD, color=RLRED)
        per = VGroup(txt(label("probability_per_minute"), size=24, color=LBLUE),
                     txt(label("speed_distance_per_hour"), size=22, color=GREY_B)).arrange(DOWN, aligned_edge=RIGHT, buff=0.15)
        notes = VGroup(not_p, per).arrange(DOWN, aligned_edge=RIGHT, buff=0.3)
        notes.align_to(ax.c2p(0, 0.08), DOWN).align_to(ax.c2p(X_MAX, 0), RIGHT)  # above the flat tail of the curve
        for m in (not_p, *per):
            m.add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06)
        with self.say("1.9") as (tr, t):
            self.play(FadeOut(sig), FadeOut(whole), FadeIn(not_p), run_time=0.7)
            self.cue(tr, t, {"en": "It is probability per minute", "uz": "U bir daqiqaga"})
            self.play(FadeIn(per[0]), run_time=0.5)
            self.cue(tr, t, {"en": "the way speed", "uz": "xuddi tezlik"})
            self.play(FadeIn(per[1]), run_time=0.5)
        self.clear_all()

        # AI: a generative model learns a density over its data (a picture: no numbers shown)
        ax2 = Axes(x_range=[0, 10, 1], y_range=[0, 1, 0.5], x_length=9, y_length=3.4, tips=False,
                   axis_config={"color": GREY_B, "stroke_width": 2, "include_ticks": False}).move_to(DOWN * 0.6)
        xs = [i / 20 for i in range(201)]
        bump = [0.9 * exp(-(x - 3) ** 2 / 0.8) + 0.5 * exp(-(x - 7) ** 2 / 1.5) for x in xs]
        dens = ax2.plot_line_graph(xs, bump, add_vertex_dots=False, line_color=LBLUE, stroke_width=4)["line_graph"]
        fill = Polygon(ax2.c2p(0, 0), *[ax2.c2p(x, y) for x, y in zip(xs, bump)], ax2.c2p(10, 0),
                       stroke_width=0, fill_color=LBLUE, fill_opacity=0.25)
        head = txt(label("generative_model"), size=34, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.4)
        dl = txt(label("data_axis"), size=24, color=GREY_B).next_to(ax2.x_axis, DOWN, buff=0.25)
        com = txt(label("common_data"), size=26, color=HILITE).next_to(ax2.c2p(3, 0.9), UP, buff=0.2)
        rare = txt(label("rare_data"), size=26, color=GREY_B).next_to(ax2.c2p(9.6, 0.05), UP, buff=0.35)
        ill = info(label("illustration"))
        with self.say("1.10") as (tr, t):
            self.play(FadeIn(head), Create(ax2), FadeIn(dl), FadeIn(ill), run_time=0.8)
            self.cue(tr, t, {"en": "a density", "uz": "aynan zichlikni"})
            self.play(Create(dens), FadeIn(fill), run_time=1.0)
            self.cue(tr, t, {"en": "which data is common", "uz": "qanday berilganlar"})
            self.play(FadeIn(com), FadeIn(rare), run_time=0.7)
        self.clear_all()


class S01HandsOn(LectureScene):
    def construct(self):
        secs = round(N["window_30s"] * 60)
        card = pause_card([f"{label('delivery_window')}: {secs} {label('seconds')}",
                           label("density_per_minute_q")])
        with self.say("1.11"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        # the answer: a flat density over half a minute, height two, area one
        w, hgt = N["window_30s"], N["window_density"]
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 2.5, 1], x_length=6.0, y_length=4.0, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2, "font_size": 24, "include_numbers": True},
                  x_axis_config={"decimal_number_config": {"num_decimal_places": 1}}).move_to(LEFT * 2.4 + DOWN * 0.2)
        xl = txt(label("minutes", 1), size=22, color=GREY_B).next_to(ax.x_axis, DOWN, buff=0.45)
        box = Rectangle(width=ax.c2p(w, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, hgt)[1] - ax.c2p(0, 0)[1],
                        stroke_color=LBLUE, stroke_width=3, fill_color=LBLUE, fill_opacity=0.45)
        box.move_to(ax.c2p(w / 2, hgt / 2))
        one = DashedLine(ax.c2p(0, 1), ax.c2p(1, 1), color=GREY_C, stroke_width=2)
        calc = VGroup(MathTex(rf"{dec(w)} \times {dec(hgt)} = 1", font_size=48),
                      MathTex(rf"f(x) = {dec(hgt)} > 1", font_size=48, color=HILITE)).arrange(DOWN, buff=0.4)
        calc.move_to(RIGHT * 3.6 + UP * 0.4)
        with self.say("1.12") as (tr, t):
            self.play(Create(ax), FadeIn(xl), run_time=0.7)
            self.cue(tr, t, {"en": "So the height is two", "uz": "Demak, balandlik ikki"})
            self.play(GrowFromEdge(box, DOWN), Write(calc[0]), run_time=1.0)
            self.cue(tr, t, {"en": "The density is above one", "uz": "Zichlik birdan katta"})
            self.play(Create(one), Write(calc[1]), run_time=0.8)
        self.clear_all()

        # the next question: add the area up once and keep it
        ax2 = gap_axes(x_len=8.6, y_len=3.4).move_to(DOWN * 0.4)
        curve = density_curve(ax2)
        sweep = ValueTracker(0.05)
        fill = always_redraw(lambda: area(ax2, 0, sweep.get_value(), opacity=0.5))
        q = txt(label("add_it_up_once_q"), size=34, weight=BOLD, color=HILITE).to_edge(UP, buff=SAFE + 0.5)
        with self.say("1.13") as (tr, t):
            self.play(Create(ax2), Create(curve), run_time=0.8)
            self.add(fill)
            self.play(sweep.animate.set_value(X_MAX), FadeIn(q), run_time=1.6)
        self.remove(fill)
        self.add(area(ax2, 0, X_MAX, opacity=0.5))
        self.clear_all(run_time=0.3)   # the next scene opens on a silent section card


SCENES = ["S01Gaps", "S01Density", "S01HandsOn"]
