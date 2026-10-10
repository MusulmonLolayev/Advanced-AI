"""Lecture 1, section 6 — variance.

The five bus and five car commute times are the slides' worked example; every deviation,
square, sum and variance shown is read from statistics/raw/l01_numbers.json, which
statistics/capture_l01.py computes and asserts. The narration is the approved section 6
of narration/lecture01.md.
"""
from lecture01_kit import *

BUS, CAR = L["bus"], L["car"]
MEAN = L["bus_mean"]
assert MEAN == L["car_mean"] == 30
assert L["car_dev"] == [-12, 12, -5, 5, 0] and L["car_sq"] == [144, 144, 25, 25, 0]
assert (L["car_ss"], L["car_var"], L["bus_ss"], L["bus_var"]) == (338, 84.5, 2, 0.5)
assert L["car_worst_late"] == 12 and round(L["car_std"]) == 9 and L["bus_std"] < 1

X0, X1 = -3.8, 5.8                     # minutes axis, left/right ends


def fmt(v):
    return f"{v:+g}".replace("-", "−") if v else "0"


def row(vals, y, name, lo=15, hi=45, step=5, r=0.13, color=RLBLUE):
    """A labelled minutes axis with one dot per day (repeats stack upward)."""
    def mx(v):
        return X0 + (X1 - X0) * (v - lo) / (hi - lo)
    axis = VGroup(Line([X0 - 0.2, y, 0], [X1 + 0.2, y, 0], color=GREY_B, stroke_width=2))
    for v in range(lo, hi + 1, step):
        tk = Line(UP * 0.07, DOWN * 0.07, color=GREY_B, stroke_width=2).move_to([mx(v), y, 0])
        axis.add(tk, txt(str(v), size=20, color=GREY_B).next_to(tk, DOWN, buff=0.12))
    seen, dots = {}, VGroup()
    for v in vals:
        k = seen.get(v, 0)
        seen[v] = k + 1
        dots.add(Dot([mx(v), y + r + 0.04 + 2.2 * r * k, 0], radius=r, color=color))
    lab = txt(name, size=30, weight=BOLD).move_to([-5.55, y + 0.35, 0])
    vals_t = txt("  ".join(str(v) for v in vals), size=20, color=GREY_B).next_to(lab, DOWN, buff=0.15)
    mline = Line([mx(MEAN), y - 0.3, 0], [mx(MEAN), y + 1.15, 0], color=RLRED, stroke_width=4)
    return dict(axis=axis, dots=dots, lab=lab, vals=vals_t, mline=mline, mx=mx, y=y)


def everything(r):
    return VGroup(r["axis"], r["dots"], r["lab"], r["vals"], r["mline"])


def dev_arrows(r, vals, gap=0.38, y0=0.5):
    """One horizontal arrow per day, from the mean to that day's time, stacked upward."""
    arrows, labels = VGroup(), VGroup()
    for i, v in enumerate(vals):
        y = r["y"] + y0 + gap * i
        a, b = r["mx"](MEAN), r["mx"](v)
        if v == MEAN:
            arrows.add(Dot([a, y, 0], radius=0.05, color=HILITE))
        else:
            arrows.add(Arrow([a, y, 0], [b, y, 0], buff=0, color=HILITE, stroke_width=4,
                             max_tip_length_to_length_ratio=0.12))
        lab = txt(fmt(v - MEAN), size=22, color=HILITE)
        lab.next_to(arrows[-1], RIGHT if v >= MEAN else LEFT, buff=0.12)
        labels.add(lab)
    return arrows, labels


def squares(devs, unit, y_bottom):
    """Each deviation as a square of that side; its area is the squared deviation."""
    sq = VGroup()
    for d in devs:
        side = max(abs(d) * unit, 1e-3)
        s = Square(side_length=side, stroke_color=HILITE, stroke_width=3, fill_color=HILITE, fill_opacity=0.35)
        lab = txt(f"{d * d:g}", size=26 if side > 0.6 else 22, weight=BOLD)
        sq.add(VGroup(s, lab))
    sq.arrange(RIGHT, buff=0.45, aligned_edge=DOWN)
    for g in sq:
        g[1].move_to(g[0]) if g[0].height > 0.6 else g[1].next_to(g[0], UP, buff=0.1)
    sq.move_to([0.9, y_bottom, 0], aligned_edge=DOWN)
    return sq


class S06Commute(LectureScene):
    def construct(self):
        self.section_card(6)
        bus = row(BUS, 1.3, w("bus", "avtobus"))
        car = row(CAR, -1.4, w("car", "mashina"))

        t = line("6.1")
        with self.voiceover(t) as tr:
            self.play(FadeIn(bus["lab"]), Create(bus["axis"]), run_time=0.8)
            self.play(FadeIn(car["lab"]), Create(car["axis"]), run_time=0.8)

        t = line("6.2")
        with self.voiceover(t) as tr:
            self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.4) for d in bus["dots"]], lag_ratio=0.3),
                      FadeIn(bus["vals"]), run_time=1.6)
            self.cue(tr, t, 2)
            self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.4) for d in car["dots"]], lag_ratio=0.3),
                      FadeIn(car["vals"]), run_time=1.6)

        mtx = [txt(f"{w('mean', 'oʻrtacha')} = {MEAN:g}", size=24, color=RLRED).next_to(r["mline"], UP, buff=0.1)
               for r in (bus, car)]
        t = line("6.3")
        with self.voiceover(t) as tr:
            self.play(Create(bus["mline"]), Create(car["mline"]), FadeIn(mtx[0]), FadeIn(mtx[1]), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(Indicate(mtx[0], color=RLRED), Indicate(mtx[1], color=RLRED), run_time=1.0)

        i42 = CAR.index(max(CAR))
        late = Arrow([car["mx"](MEAN), car["y"] + 0.75, 0], [car["mx"](max(CAR)), car["y"] + 0.75, 0], buff=0,
                     color=HILITE, stroke_width=5, max_tip_length_to_length_ratio=0.12)
        late_t = txt(f"+{L['car_worst_late']:g} {w('min late', 'daqiqa kech')}", size=24, color=HILITE)
        late_t.next_to(late, UP, buff=0.1)
        q = self.heading(w("How spread out?", "Qanchalik tarqoq?"), color=HILITE)
        t = line("6.4")
        with self.voiceover(t) as tr:
            self.play(car["dots"][i42].animate.set_color(HILITE).scale(1.4), run_time=0.6)
            self.play(GrowArrow(late), FadeIn(late_t), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.7)

        # zoom in on the car: its row moves up, the squares get the bottom half
        up = UP * 1.6
        arrows, labs = dev_arrows(car, CAR)
        arrows.shift(up)
        labs.shift(up)
        t = line("6.5")
        with self.voiceover(t) as tr:
            self.play(FadeOut(everything(bus)), FadeOut(mtx[0]), FadeOut(mtx[1]), FadeOut(late), FadeOut(late_t),
                      FadeOut(q),
                      car["dots"][i42].animate.set_color(RLBLUE).scale(1 / 1.4), run_time=0.7)
            self.play(everything(car).animate.shift(up), run_time=0.8)
            self.cue(tr, t, 2)
            for a, l in zip(arrows, labs):
                self.play(GrowArrow(a) if isinstance(a, Arrow) else FadeIn(a), FadeIn(l), run_time=0.45)

        zero = MathTex(" + ".join(f"({d:g})" if d < 0 else f"{d:g}" for d in L["car_dev"]) + " = 0",
                       font_size=40, color=HILITE).to_edge(UP, buff=SAFE + 0.15)
        zero_x = SurroundingRectangle(zero, color=RLRED, buff=0.12, stroke_width=4)
        sq = squares(L["car_dev"], 0.16, -3.05)
        t = line("6.6")
        with self.voiceover(t) as tr:
            self.play(FadeIn(zero), run_time=0.8)
            self.play(Create(zero_x), run_time=0.5)
            self.cue(tr, t, {"en": "So we square", "uz": "Shuning uchun"})
            self.play(*[ReplacementTransform(a.copy(), s) for a, s in zip(arrows, sq)], run_time=1.6)

        add = MathTex(" + ".join(f"{v:g}" for v in L["car_sq"]) + f" = {L['car_ss']:g}", font_size=40)
        div = MathTex(rf"s^2 = \frac{{{L['car_ss']:g}}}{{n-1}} = \frac{{{L['car_ss']:g}}}{{4}} = {L['car_var']:g}",
                      font_size=44, color=HILITE)
        name = txt(w("variance", "dispersiya"), size=34, weight=BOLD, color=HILITE)
        top = VGroup(add, div).arrange(DOWN, buff=0.25).to_edge(UP, buff=SAFE + 0.1)
        t = line("6.7")
        with self.voiceover(t) as tr:
            self.play(FadeOut(zero), FadeOut(zero_x), FadeOut(arrows), FadeOut(labs),
                      FadeIn(add), run_time=0.9)
            self.cue(tr, t, 1)
            self.play(FadeIn(div), run_time=0.9)
            self.cue(tr, t, 3)
            name.next_to(div, RIGHT, buff=0.4)
            self.play(FadeIn(name, shift=LEFT * 0.2), Indicate(div, color=HILITE, scale_factor=1.06), run_time=1.0)
        self.clear_all()


class S06BusHandsOn(LectureScene):
    def construct(self):
        bus = row(BUS, -1.2, w("bus", "avtobus"), lo=27, hi=33, step=1, r=0.16)
        mt = txt(f"{w('mean', 'oʻrtacha')} = {MEAN:g}", size=24, color=RLRED).next_to(bus["mline"], UP, buff=0.1)
        pc = pause_card([w("We work out the bus's variance.", "Avtobusning dispersiyasini hisoblaymiz.")])
        pc.to_edge(UP, buff=SAFE + 0.3)
        with self.say("6.8"):
            self.play(FadeIn(pc), run_time=0.7)
            self.play(FadeIn(everything(bus)), FadeIn(mt), run_time=1.0)
        self.hands_on()

        arrows, labs = dev_arrows(bus, BUS, gap=0.0, y0=1.45)
        moving = [i for i, d in enumerate(L["bus_dev"]) if d]
        sq = squares([L["bus_dev"][i] for i in moving], 0.7, 0.6)
        sq.set_x(0.9)
        calc = MathTex(rf"{' + '.join(f'{L['bus_sq'][i]:g}' for i in moving)} = {L['bus_ss']:g}", r"\qquad",
                       rf"s^2 = \frac{{{L['bus_ss']:g}}}{{4}} = {L['bus_var']:g}", font_size=44, color=HILITE)
        calc.to_edge(UP, buff=SAFE + 0.4)
        t = line("6.9")
        with self.voiceover(t) as tr:
            self.play(FadeOut(pc), FadeOut(mt), run_time=0.5)
            self.play(*[GrowArrow(arrows[i]) for i in moving], *[FadeIn(labs[i]) for i in moving], run_time=0.9)
            self.cue(tr, t, 1)
            self.play(*[ReplacementTransform(arrows[i].copy(), s) for i, s in zip(moving, sq)], run_time=1.0)
            self.play(FadeIn(calc), run_time=0.9)
        self.clear_all()


class S06Std(LectureScene):
    def construct(self):
        bus = row(BUS, 0.3, w("bus", "avtobus"))
        car = row(CAR, -2.2, w("car", "mashina"))
        self.play(FadeIn(everything(bus)), FadeIn(everything(car)), run_time=0.8)

        def band(r, s, color):
            a, b = r["mx"](MEAN - s), r["mx"](MEAN + s)
            rect = Rectangle(width=b - a, height=0.95, stroke_width=0, fill_color=color, fill_opacity=0.3)
            rect.move_to([(a + b) / 2, r["y"] + 0.48, 0])
            return rect
        bands = [band(bus, L["bus_std"], RLGREEN), band(car, L["car_std"], HILITE)]
        stds = [txt(f"s ≈ {L['bus_std']:.2f} {w('min', 'daqiqa')}", size=26, color=RLGREEN),
                txt(f"s ≈ {L['car_std']:.2f} {w('min', 'daqiqa')}", size=26, color=HILITE)]
        for st, r in zip(stds, (bus, car)):
            st.move_to([r["mx"](MEAN) + 3.6, r["y"] + 1.3, 0])
        unit = MathTex(r"s^2:\ \text{" + w("min", "daqiqa") + r"}^2", font_size=44).to_edge(UP, buff=SAFE + 0.3)
        root = MathTex(r"s = \sqrt{s^2}", font_size=48).to_edge(UP, buff=SAFE + 0.3)
        roots = MathTex(rf"\sqrt{{{L['car_var']:g}}} \approx {L['car_std']:.2f}", r"\qquad",
                        rf"\sqrt{{{L['bus_var']:g}}} \approx {L['bus_std']:.2f}", font_size=40)
        roots.next_to(root, DOWN, buff=0.2)
        t = line("6.10")
        with self.voiceover(t) as tr:
            self.play(FadeIn(unit), run_time=0.7)
            self.cue(tr, t, 1)
            self.play(FadeOut(unit), FadeIn(root), FadeIn(roots), run_time=0.9)
            self.cue(tr, t, 2)
            self.play(FadeIn(bands[1]), FadeIn(stds[1]), run_time=0.8)
            self.play(FadeIn(bands[0]), FadeIn(stds[0]), run_time=0.8)

        formula = MathTex(r"s^2 = \frac{\sum_{i=1}^{n} (x_i - ", r"\bar{x}", r")^2}{", r"n - 1", "}", font_size=48)
        formula.to_edge(UP, buff=SAFE + 0.2).set_x(-1.5)
        formula[3].set_color(HILITE)
        note = txt(w("x̄ comes from this same sample", "x̄ shu tanlanmaning oʻzidan"), size=24, color=RLGREEN)
        note.next_to(formula, RIGHT, buff=0.5).shift(UP * 0.25)
        t = line("6.11")
        with self.voiceover(t) as tr:
            self.play(FadeOut(root), FadeOut(roots), FadeIn(formula), run_time=0.9)
            self.play(Indicate(formula[3], color=HILITE, scale_factor=1.3), run_time=0.9)
            self.cue(tr, t, 1)
            self.play(formula[1].animate.set_color(RLGREEN), FadeIn(note, shift=LEFT * 0.2), run_time=0.9)
            self.cue(tr, t, {"en": "Dividing", "uz": "n minus birga boʻlib"})
            self.play(Indicate(formula[3], color=HILITE, scale_factor=1.3), run_time=0.9)

        tags = [txt(w("steady", "barqaror"), size=26, color=RLGREEN), txt(w("jumpy", "beqaror"), size=26, color=HILITE)]
        for tg, r in zip(tags, (bus, car)):
            tg.next_to(r["vals"], DOWN, buff=0.15)
        cap = txt(w("same mean, different variance", "bir xil oʻrtacha, har xil dispersiya"), size=32, weight=BOLD)
        cap.to_edge(UP, buff=SAFE + 0.4)
        t = line("6.12")
        with self.voiceover(t) as tr:
            self.play(FadeOut(formula), FadeOut(note), run_time=0.6)
            self.play(FadeIn(tags[0]), FadeIn(tags[1]), Indicate(bands[0], color=RLGREEN), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(FadeIn(cap, shift=DOWN * 0.2), Indicate(bands[1], color=HILITE), run_time=1.0)
        self.clear_all()


class S06Teaser(LectureScene):
    """Toward section 7: a fill axis with the legal band."""
    def construct(self):
        lo, hi, y = 486, 514, -1.6
        def fx(v):
            return -5.5 + 11 * (v - lo) / (hi - lo)
        axis = VGroup(Line([fx(lo), y, 0], [fx(hi), y, 0], color=GREY_B, stroke_width=2))
        for v in (490, 495, 500, 505, 510):
            tk = Line(UP * 0.08, DOWN * 0.08, color=GREY_B, stroke_width=2).move_to([fx(v), y, 0])
            axis.add(tk, txt(str(v), size=22, color=GREY_B).next_to(tk, DOWN, buff=0.15))
        axis.add(txt("ml", size=22, color=GREY_B).next_to(axis, RIGHT, buff=0.2))
        bandr = Rectangle(width=fx(505) - fx(495), height=2.6, stroke_width=0, fill_color=RLGREEN, fill_opacity=0.18)
        bandr.move_to([fx(500), y + 1.3, 0])
        limits = VGroup(*[DashedLine([fx(v), y, 0], [fx(v), y + 2.6, 0], color=RLRED, stroke_width=3)
                          for v in (495, 505)])
        # a bottle, drawn
        body = RoundedRectangle(corner_radius=0.15, width=0.8, height=1.4, stroke_color=WHITE, stroke_width=3)
        neck = Rectangle(width=0.3, height=0.45, stroke_color=WHITE, stroke_width=3).next_to(body, UP, buff=0)
        fill = Rectangle(width=0.74, height=1.0, stroke_width=0, fill_color=RLBLUE, fill_opacity=0.8)
        fill.align_to(body, DOWN).shift(UP * 0.03)
        bottle = VGroup(fill, body, neck).move_to([fx(500), 2.0, 0])
        with self.say("6.13"):
            self.play(FadeIn(bottle, shift=DOWN * 0.3), Create(axis), run_time=1.0)
            self.play(FadeIn(bandr), Create(limits), run_time=1.0)
        self.clear_all()


SCENES = ["S06Commute", "S06BusHandsOn", "S06Std", "S06Teaser"]
