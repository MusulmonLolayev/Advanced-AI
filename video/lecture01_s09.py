"""Lecture 1, section 9 — always plot the data (Anscombe's quartet).

The four datasets and their statistics come from statistics/raw/l01_numbers.json
(capture_l01.py, checked against the figure script's printed table).
"""
from lecture01_kit import *

ANS = L["anscombe"]
NAMES = ["I", "II", "III", "IV"]
# the narration says these aloud; fail if the data ever stops rounding to them
for _s in ANS.values():
    assert round(_s["mean_x"], 2) == 9 and round(_s["mean_y"], 2) == 7.50
    assert round(_s["var_x"], 2) == 11 and round(_s["corr"], 2) == 0.82
    assert round(_s["slope"], 2) == 0.5 and round(_s["intercept"], 2) == 3.0
    assert len(_s["x"]) == len(_s["y"]) == 11

COLS = [-5.25, -1.75, 1.75, 5.25]          # one column per dataset
PW, PH, PY = 3.0, 2.9, 0.35                # panel width, height, centre y
X0, X1, Y0, Y1 = 2, 20, 2, 14              # the figure script's axis limits
DOT = interpolate_color(ManimColor(RLBLUE), WHITE, 0.35)   # course blue, lifted to read on black


def ppos(i, x, y):
    """A data point's position inside panel i."""
    cx = COLS[i]
    return np.array([cx - PW / 2 + PW * (x - X0) / (X1 - X0), PY - PH / 2 + PH * (y - Y0) / (Y1 - Y0), 0])


def panel_frame(i):
    r = Rectangle(width=PW, height=PH, stroke_color=GREY_B, stroke_width=2).move_to([COLS[i], PY, 0])
    name = txt(NAMES[i], size=24, weight=BOLD, color=GREY_B).next_to(r, UP, buff=0.12)
    return VGroup(r, name)


def panel_dots(i):
    s = ANS[NAMES[i]]
    return VGroup(*[Dot(ppos(i, x, y), radius=0.065, color=DOT) for x, y in zip(s["x"], s["y"])])


def fit_line(i):
    s = ANS[NAMES[i]]
    return Line(ppos(i, X0, s["intercept"] + s["slope"] * X0), ppos(i, X1, s["intercept"] + s["slope"] * X1),
                color=RLRED, stroke_width=3)


def table(i):
    s = ANS[NAMES[i]]
    head = VGroup(txt("x", size=22, color=GREY_B), txt("y", size=22, color=GREY_B))
    rows = VGroup(*[VGroup(txt(f"{x:g}", size=20), txt(f"{y:.2f}", size=20)) for x, y in zip(s["x"], s["y"])])
    for r in [head, *rows]:
        r[0].move_to([COLS[i] - 0.55, 0, 0])
        r[1].move_to([COLS[i] + 0.45, 0, 0])
    name = txt(NAMES[i], size=26, weight=BOLD, color=RLBLUE).move_to([COLS[i], 3.25, 0])
    head.set_y(2.75)
    for k, r in enumerate(rows):
        r.set_y(2.35 - 0.3 * k)
    return name, head, rows


def stat_block(i, which):
    s = ANS[NAMES[i]]
    items = {"mx": rf"\bar{{x}} = {s['mean_x']:.0f}", "my": rf"\bar{{y}} = {s['mean_y']:.2f}",
             "vx": rf"s_x^2 = {s['var_x']:.0f}", "r": rf"r = {s['corr']:.3f}",
             "fit": rf"y = {s['intercept']:.0f} + {s['slope']:.1f}x"}
    return MathTex(items[which], font_size=30)


CAPTIONS = [w("a straight line", "chiziqli"), w("a curve", "egri chiziq"),
            w("one outlier", "bitta chetga chiqqan nuqta"), w("no relationship", "bogʻlanish yoʻq")]


def summary_line():
    s = ANS["I"]
    t = MathTex(rf"\bar{{x}} = {s['mean_x']:.0f} \quad \bar{{y}} = {s['mean_y']:.2f} \quad s_x^2 = {s['var_x']:.0f}"
                rf" \quad r = {s['corr']:.3f} \quad y = {s['intercept']:.0f} + {s['slope']:.1f}x", font_size=32)
    lab = txt(w("— in all four", "— toʻrttasida ham"), size=24, color=GREY_B)
    return VGroup(t, lab).arrange(RIGHT, buff=0.3).move_to([-0.3, -2.75, 0])


def panels_static():
    frames = VGroup(*[panel_frame(i) for i in range(4)])
    dots = VGroup(*[panel_dots(i) for i in range(4)])
    return frames, dots


class S09Tables(LectureScene):
    def construct(self):
        self.section_card(9)
        tabs = [table(i) for i in range(4)]
        t1 = line("9.1")
        with self.voiceover(t1) as tr:
            self.play(LaggedStart(*[FadeIn(VGroup(n, h)) for n, h, _ in tabs], lag_ratio=0.15), run_time=1.0)
            self.cue(tr, t1, 1)
            self.play(LaggedStart(*[LaggedStart(*[FadeIn(r, shift=DOWN * 0.1) for r in rows], lag_ratio=0.08)
                                    for _, _, rows in tabs], lag_ratio=0.1), run_time=2.0)

        ys = {"mx": -1.15, "my": -1.6, "vx": -2.05, "r": -2.5, "fit": -2.95}
        blocks = {k: VGroup(*[stat_block(i, k).move_to([COLS[i], y, 0]) for i in range(4)]) for k, y in ys.items()}
        with self.say("9.2") as (tr, t):
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(b) for b in blocks["mx"]], lag_ratio=0.2), run_time=1.0)
            self.cue(tr, t, 2)
            self.play(LaggedStart(*[FadeIn(b) for b in blocks["my"]], lag_ratio=0.2), run_time=1.0)

        with self.say("9.3") as (tr, t):
            self.play(LaggedStart(*[FadeIn(b) for b in blocks["vx"]], lag_ratio=0.2), run_time=1.0)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(b) for b in blocks["r"]], lag_ratio=0.2), run_time=1.0)
            self.cue(tr, t, 2)
            self.play(LaggedStart(*[FadeIn(b) for b in blocks["fit"]], lag_ratio=0.2), run_time=1.0)

        eqs = VGroup(*[MathTex("=", font_size=44, color=HILITE).move_to([(COLS[i] + COLS[i + 1]) / 2, -2.05, 0])
                       for i in range(3)])
        frames = VGroup(*[panel_frame(i) for i in range(4)])
        dots = [panel_dots(i) for i in range(4)]
        summ = summary_line()
        with self.say("9.4") as (tr, t):
            self.play(LaggedStart(*[GrowFromCenter(e) for e in eqs], lag_ratio=0.2), run_time=0.9)
            self.cue(tr, t, 1)
            # each table row becomes its point
            self.play(*[FadeOut(VGroup(n, h)) for n, h, _ in tabs], FadeOut(eqs),
                      FadeOut(VGroup(*blocks.values())), FadeIn(frames), FadeIn(summ), run_time=0.8)
            self.play(*[ReplacementTransform(r, d) for i in range(4) for r, d in zip(tabs[i][2], dots[i])],
                      run_time=1.8)
        self.clear_all()


class S09Panels(LectureScene):
    def construct(self):
        frames, dots = panels_static()
        summ = summary_line()
        self.add(frames, dots, summ)
        lines = [fit_line(i) for i in range(4)]
        caps = [txt(c, size=22, color=HILITE).move_to([COLS[i], PY - PH / 2 - 0.35, 0]) for i, c in enumerate(CAPTIONS)]
        for c in caps:
            if c.width > PW + 0.3:
                c.scale_to_fit_width(PW + 0.3)

        def focus(i):
            anims = []
            for j in range(4):
                on = j == i
                anims += [frames[j][0].animate.set_stroke(HILITE if on else GREY_D, width=4 if on else 2),
                          dots[j].animate.set_opacity(1 if on else 0.3)]
            return anims

        for i in range(4):
            with self.say(f"9.{5 + i}") as (tr, t):
                self.play(*focus(i), run_time=0.6)
                self.play(Create(lines[i]), FadeIn(caps[i], shift=UP * 0.15), run_time=1.0)
                if i == 2:      # the outlier that drags the line
                    s = ANS["III"]
                    k = int(np.argmax(s["y"]))
                    self.play(Flash(dots[2][k], color=RLRED, line_length=0.18), run_time=0.8)
                if i == 3:      # the single far-off point
                    s = ANS["IV"]
                    k = int(np.argmax(s["x"]))
                    self.play(Flash(dots[3][k], color=RLRED, line_length=0.18), run_time=0.8)

        who = txt("F. J. Anscombe, 1973", size=34, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        with self.say("9.9") as (tr, t):
            self.play(*[f[0].animate.set_stroke(GREY_B, width=2) for f in frames],
                      *[d.animate.set_opacity(1) for d in dots], FadeIn(who), run_time=0.8)
            self.cue(tr, t, 1)
            self.play(Indicate(VGroup(*dots), color=HILITE, scale_factor=1.05), run_time=1.2)

        acc_t = txt(w("accuracy = one number", "aniqlik = bitta son"), size=30)
        acc = VGroup(SurroundingRectangle(acc_t, buff=0.22, corner_radius=0.12, color=HILITE, stroke_width=3), acc_t)
        acc.to_edge(UP, buff=SAFE + 0.2)
        with self.say("9.10") as (tr, t):
            self.play(FadeOut(who), FadeIn(acc), run_time=0.7)
            self.cue(tr, t, 2)
            self.play(*[Indicate(VGroup(lines[i], dots[i]), color=HILITE, scale_factor=1.04) for i in range(4)],
                      run_time=1.2)
        self.clear_all()


class S09HandsOn(LectureScene):
    def construct(self):
        frames, dots = panels_static()
        lines = VGroup(*[fit_line(i) for i in range(4)])
        self.add(frames, dots, lines)
        task = pause_card([w("In which panel is a straight line right?",
                             "Qaysi birida toʻgʻri chiziq toʻgʻri keladi?")])
        task.scale(0.8).to_edge(UP, buff=SAFE + 0.05)
        with self.say("9.11") as (tr, t):
            self.cue(tr, t, 1)
            self.play(FadeIn(task), run_time=0.7)
        self.hands_on()

        marks = VGroup()
        for i in range(4):
            m = txt("✓" if i == 0 else "✗", size=56, weight=BOLD, color=GOOD if i == 0 else BAD)
            marks.add(m.next_to(frames[i][0], DOWN, buff=0.25))
        with self.say("9.12") as (tr, t):
            self.play(FadeOut(task), FadeIn(marks[0], scale=0.5), frames[0][0].animate.set_stroke(GOOD, width=4),
                      run_time=0.8)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in marks[1:]], lag_ratio=0.25),
                      *[frames[i][0].animate.set_stroke(BAD, width=3) for i in range(1, 4)], run_time=1.2)

        everything = VGroup(frames, dots, lines, marks)
        done = txt(w("Part 0  ✓", "0-qism  ✓"), size=48, weight=BOLD, color=RLBLUE)
        nxt = txt(w("next: probability", "keyingi: ehtimollik"), size=30, color=GREY_B)
        with self.say("9.13") as (tr, t):
            self.play(everything.animate.scale(0.45).move_to(UP * 1.6), run_time=1.0)
            done.next_to(everything, DOWN, buff=0.6)
            self.play(FadeIn(done, shift=UP * 0.2), run_time=0.7)
            self.cue(tr, t, 1)
            nxt.next_to(done, DOWN, buff=0.35)
            self.play(FadeIn(nxt), run_time=0.7)
        self.clear_all()


SCENES = ["S09Tables", "S09Panels", "S09HandsOn"]
