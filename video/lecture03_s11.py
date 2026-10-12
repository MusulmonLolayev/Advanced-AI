"""Lecture 3, section 11 — the Dirichlet distribution over the cup shares, then the lecture close.

The thin lines are the figure script's own Dirichlet draws (same generator and seed, captured in
l03_numbers.json): six with α worth about four orders, six with α worth about forty.
"""
from lecture03_kit import *

CUPS = list(N["cups"])                     # small, medium, large
SHARES = [N["cups"][k] for k in CUPS]
FIRST = [N["first_orders"][k] for k in CUPS]
FIRST_SH = [N["first_shares"][k] for k in CUPS]
A_WEAK, A_STRONG = N["alphas"]["4"], N["alphas"]["40"]
DRAWS_WEAK, DRAWS_STRONG = N["dirichlet_draws"]["4"], N["dirichlet_draws"]["40"]
A_NEW = N["alpha_updated"]
MORE = N["more_medium"]
XS = [-2.4, 0.0, 2.4]


def share_bars(shares, base=-2.2, height=3.6, width=1.3, color=LBLUE, x0=0.0, vmax=None, size=36):
    """Cup shares as three bars with their value above and the cup's name under."""
    sc = height / (vmax or max(shares))
    bars = VGroup(*[Rectangle(width=width, height=max(v * sc, 1e-3), stroke_width=0, fill_color=color,
                              fill_opacity=1).move_to([x0 + x, base + v * sc / 2, 0]) for x, v in zip(XS, shares)])
    vals = VGroup(*[MathTex(dec(v), font_size=size).next_to(b, UP, buff=0.12) for b, v in zip(bars, shares)])
    names = VGroup(*[txt(CUP_NAME[k], size=26, color=GREY_B).next_to([x0 + x, base, 0], DOWN, buff=0.2)
                     for x, k in zip(XS, CUPS)])
    return bars, vals, names, sc


def cup(kind, color=LBLUE):
    """A cup outline, sized by kind."""
    h = {"small": 0.5, "medium": 0.7, "large": 0.9}[kind]
    body = Polygon([-0.22 * h / 0.7, h / 2, 0], [0.22 * h / 0.7, h / 2, 0], [0.16 * h / 0.7, -h / 2, 0],
                   [-0.16 * h / 0.7, -h / 2, 0], stroke_color=color, stroke_width=3)
    return body


def alpha_tex(a, size=40, color=WHITE, hl=None):
    """(α₁, α₂, α₃) with entry hl lit."""
    parts = [r"\alpha = (", dec(a[0]), ",\\,", dec(a[1]), ",\\,", dec(a[2]), ")"]
    m = MathTex(*parts, font_size=size, color=color)
    if hl is not None:
        m[1 + 2 * hl].set_color(HILITE)
    return m


def draw_panel(draws, width=6.0, height=2.3, color=LBLUE):
    """Each draw as a thin line across small, medium, large; shares on a 0–1 scale."""
    xs = [-width / 2 + 0.6, 0.0, width / 2 - 0.6]
    floor = Line([-width / 2, 0, 0], [width / 2, 0, 0], color=GREY_B, stroke_width=2)
    top = DashedLine([-width / 2, height, 0], [width / 2, height, 0], color=GREY_D, stroke_width=1.5)
    y0, y1 = MathTex("0", font_size=22, color=GREY_B), MathTex("1", font_size=22, color=GREY_B)
    y0.next_to(floor, LEFT, buff=0.12)
    y1.next_to(top, LEFT, buff=0.12)
    names = VGroup(*[txt(CUP_NAME[k], size=22, color=GREY_B).next_to([x, 0, 0], DOWN, buff=0.12)
                     for x, k in zip(xs, CUPS)])
    lines = VGroup(*[VGroup(VMobject(stroke_color=color, stroke_width=2.5, stroke_opacity=0.8)
                            .set_points_as_corners([[x, s * height, 0] for x, s in zip(xs, d)]),
                            *[Dot([x, s * height, 0], radius=0.05, color=color) for x, s in zip(xs, d)])
                     for d in draws])
    return VGroup(VGroup(floor, top, y0, y1, names), lines)


class S11Shares(LectureScene):
    def construct(self):
        self.section_card(11)
        bars, vals, names, sc = share_bars(SHARES, vmax=0.6)
        head = txt(label("cup_shares"), size=32, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.3)
        qs = VGroup(*[txt("?", size=40, weight=BOLD, color=HILITE).next_to(v, UP, buff=0.12) for v in vals])
        with self.say("11.1") as (tr, t):
            self.play(FadeIn(head), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2),
                      FadeIn(vals), FadeIn(names), run_time=1.2)
            self.cue(tr, t, 1)
            self.play(LaggedStart(*[FadeIn(q, scale=0.5) for q in qs], lag_ratio=0.2), run_time=0.8)

        # the first four orders, read literally
        orders = VGroup(*[cup(k) for k, n in zip(CUPS, FIRST) for _ in range(n)]).arrange(RIGHT, buff=0.35,
                                                                                         aligned_edge=DOWN)
        o_head = txt(label("the_first_orders"), size=26, color=GREY_B)
        o_group = VGroup(o_head, orders).arrange(RIGHT, buff=0.5).next_to(head, DOWN, buff=0.35)
        bars2, vals2, _, _ = share_bars(FIRST_SH, vmax=0.6)
        qs2 = VGroup(*[txt("?", size=40, weight=BOLD, color=HILITE).next_to(v, UP, buff=0.12) for v in vals2])
        with self.say("11.2") as (tr, t):
            self.play(FadeOut(qs), FadeIn(o_group), run_time=0.7)
            self.cue(tr, t, {"en": "Read literally", "uz": "Toʻgʻridan-toʻgʻri"})
            self.play(*[Transform(a, b) for a, b in zip(bars, bars2)], *[Transform(a, b) for a, b in zip(vals, vals2)],
                      run_time=1.0)
            self.cue(tr, t, {"en": "But after only four", "uz": "Lekin toʻrtta"})
            self.play(LaggedStart(*[FadeIn(q, scale=0.5) for q in qs2], lag_ratio=0.2), run_time=0.8)
        self.clear_all()

        # the answer is three numbers at once, always adding up to one
        three = MathTex("p_1", "+", "p_2", "+", "p_3", "=", "1", font_size=72)
        for i in (0, 2, 4):
            three[i].set_color(LBLUE)
        cups3 = VGroup(*[cup(k) for k in CUPS])
        for c, i in zip(cups3, (0, 2, 4)):
            c.next_to(three[i], DOWN, buff=0.35)
        plaus = txt(label("which_sets_of_shares_are_plausible_q"), size=30, color=GREY_B).move_to(UP * 1.8)
        with self.say("11.3") as (tr, t):
            self.play(FadeIn(plaus), run_time=0.7)
            self.cue(tr, t, {"en": "The hard part", "uz": "Qiyin tomoni"})
            self.play(Write(three), FadeIn(cups3), run_time=1.0)
        self.clear_all()


class S11Draws(LectureScene):
    def construct(self):
        name = txt(label("dist_dirichlet"), size=34, weight=BOLD, color=LBLUE).to_edge(UP, buff=SAFE + 0.25)
        big = draw_panel(DRAWS_WEAK, width=7.0, height=3.4).move_to(DOWN * 0.3)
        each = txt(label("each_draw_a_whole_set_of_shares"), size=26, color=GREY_B).next_to(big, DOWN, buff=0.5)
        with self.say("11.4") as (tr, t):
            self.play(FadeIn(name), FadeIn(big[0]), run_time=0.7)
            self.play(LaggedStart(*[Create(l) for l in big[1]], lag_ratio=0.35), run_time=1.8)
            self.play(FadeIn(each), run_time=0.5)
        self.clear_all()

        # α counts the orders already seen: about four scatters the draws, about forty holds them
        weak = draw_panel(DRAWS_WEAK).move_to([-2.0, 1.25, 0])
        strong = draw_panel(DRAWS_STRONG, color=RLGREEN).move_to([-2.0, -2.15, 0])

        def tag(a, color):
            seen = tagged(f"≈ {sum(a):g}", label("orders_seen"), size=24, color=GREY_B)
            return VGroup(alpha_tex(a, size=36, color=color), seen).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        t_weak = tag(A_WEAK, LBLUE).next_to(weak, RIGHT, buff=0.6)
        t_strong = tag(A_STRONG, RLGREEN).next_to(strong, RIGHT, buff=0.6)
        with self.say("11.5") as (tr, t):
            self.play(FadeIn(weak[0]), run_time=0.5)
            self.cue(tr, t, {"en": "An alpha worth", "uz": "Taxminan toʻrtta"})
            self.play(FadeIn(t_weak), LaggedStart(*[Create(l) for l in weak[1]], lag_ratio=0.2), run_time=1.2)
            self.cue(tr, t, {"en": "One worth about forty", "uz": "Taxminan qirqtaga"})
            self.play(FadeIn(strong[0]), FadeIn(t_strong),
                      LaggedStart(*[Create(l) for l in strong[1]], lag_ratio=0.2), run_time=1.2)
        self.clear_all()

        # updating is counting
        a = alpha_tex(A_WEAK, size=60, hl=1).move_to(UP * 0.4)
        plus = MathTex(rf"+{MORE}", font_size=56, color=HILITE).next_to(a[3], UP, buff=0.5)
        new_cups = VGroup(*[cup("medium", HILITE) for _ in range(MORE)]).arrange(RIGHT, buff=0.3)
        new_cups.next_to(plus, UP, buff=0.35)
        rule = txt(label("updating_is_counting"), size=30, color=GREY_B).next_to(a, DOWN, buff=0.7)
        with self.say("11.6") as (tr, t):
            self.play(Write(a), FadeIn(rule), run_time=0.9)
            self.cue(tr, t, {"en": "if three more", "uz": "yana uchta"})
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.4) for c in new_cups], lag_ratio=0.25), run_time=0.9)
            self.play(FadeIn(plus, shift=DOWN * 0.2), run_time=0.5)
        self.clear_all()


class S11AI(LectureScene):
    def construct(self):
        # a softmax gives shares only; a network that predicts α can also say how much it has seen
        sm_bars, sm_vals, sm_names, _ = share_bars(SHARES, height=2.2, width=0.8, x0=-3.6, vmax=0.6, size=28)
        for b, x in zip(sm_bars, XS):
            b.set_x(-3.6 + x * 0.55)
        for v, b in zip(sm_vals, sm_bars):
            v.next_to(b, UP, buff=0.1)
        for n, b in zip(sm_names, sm_bars):
            n.scale(0.8).next_to(b, DOWN, buff=0.15).set_y(-2.45)
        sm_head = txt(label("softmax"), size=30, weight=BOLD, color=LBLUE).move_to([-3.6, 2.4, 0])
        sm_q = txt(label("how_sure_q"), size=26, color=HILITE).next_to(sm_head, DOWN, buff=0.3)
        right = draw_panel(DRAWS_WEAK, width=4.6, height=2.0).move_to([3.0, -1.0, 0])
        r_head = MathTex(r"\alpha", font_size=60, color=LBLUE).move_to([3.0, 2.4, 0])
        quote = txt(label("i_have_barely_seen_this"), size=26, color=HILITE).next_to(r_head, DOWN, buff=0.3)
        uses = VGroup(tagged(label("module_3"), f"· {label('topic_models')}", size=24, color=GREY_B),
                      tagged(label("module_5"), f"· {label('alphazero_move_priors')}", size=24, color=GREY_B)
                      ).arrange(RIGHT, buff=0.8).to_edge(DOWN, buff=SAFE + 0.35)
        with self.say("11.7") as (tr, t):
            self.play(FadeIn(sm_head), LaggedStart(*[GrowFromEdge(b, DOWN) for b in sm_bars], lag_ratio=0.15),
                      FadeIn(sm_vals), FadeIn(sm_names), run_time=1.0)
            self.play(FadeIn(sm_q), run_time=0.5)
            self.cue(tr, t, {"en": "A network that", "uz": "Alfani bashorat"})
            self.play(FadeIn(r_head), FadeIn(right[0]), LaggedStart(*[Create(l) for l in right[1]], lag_ratio=0.2),
                      run_time=1.2)
            self.play(FadeIn(quote), run_time=0.5)
            self.cue(tr, t, {"en": "That is the idea", "uz": "Bu uchinchi"})
            self.play(FadeIn(uses, shift=UP * 0.2), run_time=0.7)
        self.clear_all()


class S11HandsOn(LectureScene):
    def construct(self):
        a_str = ", ".join(dec(x) for x in A_WEAK)
        card = pause_card([f"α = ({a_str})", f"+{MORE} {label('medium')}", f"{label('new_alpha')} = ?"])
        with self.say("11.8"):
            self.play(FadeIn(card), run_time=0.8)
        self.hands_on()
        self.play(FadeOut(card), run_time=0.4)

        new = alpha_tex(A_NEW, size=64, hl=1).move_to(UP * 2.2)
        before, after = A_WEAK[1] / sum(A_WEAK), A_NEW[1] / sum(A_NEW)
        assert abs(after - N["alpha_updated_mean"][1]) < 1e-12
        share_l = txt(label("medium_cup_share"), size=28, color=GREY_B).move_to(UP * 0.9)
        calc = MathTex(rf"\tfrac{{{A_WEAK[1]:g}}}{{{sum(A_WEAK):g}}} = {dec(before)}", r"\;\to\;",
                       rf"\tfrac{{{A_NEW[1]:g}}}{{{sum(A_NEW):g}}} \approx {dec(after)}", font_size=50)
        calc[2].set_color(HILITE)
        calc.next_to(share_l, DOWN, buff=0.3)
        sc = 2.6
        b0 = Rectangle(width=1.4, height=before * sc, stroke_width=0, fill_color=LBLUE, fill_opacity=1)
        b0.move_to([0, -2.6 + before * sc / 2, 0])
        b1 = Rectangle(width=1.4, height=after * sc, stroke_width=0, fill_color=HILITE, fill_opacity=1)
        b1.move_to([0, -2.6 + after * sc / 2, 0])
        floor = Line([-1.2, -2.6, 0], [1.2, -2.6, 0], color=GREY_B, stroke_width=2)
        with self.say("11.9") as (tr, t):
            self.play(Write(new), run_time=0.9)
            self.cue(tr, t, 1)
            self.play(FadeIn(share_l), Write(calc[0]), Create(floor), GrowFromEdge(b0, DOWN), run_time=0.9)
            self.play(Write(calc[1:]), Transform(b0, b1), run_time=0.9)
        self.clear_all()


class S11Summary(LectureScene):
    def construct(self):
        head = self.heading(label("lecture_3_summary"), color=LBLUE)

        def mini_bars(hs, color=LBLUE):
            return VGroup(*[Rectangle(width=0.14, height=h * 0.6, stroke_width=0, fill_color=color, fill_opacity=1)
                            for h in hs]).arrange(RIGHT, buff=0.05, aligned_edge=DOWN)

        def mini_mean():
            g = mini_bars([0.9, 0.35, 0.2])
            return VGroup(g, Line(g.get_corner(DL) + RIGHT * 0.12, g.get_corner(UL) + RIGHT * 0.12, color=HILITE,
                                  stroke_width=3))

        def mini_shift():
            g = mini_bars([0.9, 0.35, 0.2], GREY_B)
            return VGroup(g, Arrow(LEFT * 0.25, RIGHT * 0.25, buff=0, color=HILITE, stroke_width=3,
                                   max_tip_length_to_length_ratio=0.35).next_to(g, RIGHT, buff=0.05))

        def mini_coin():
            return VGroup(Circle(radius=0.22, color=LBLUE, stroke_width=3), mini_bars([0.5, 0.5]).scale(0.6))

        def mini_cups():
            return VGroup(*[cup(k) for k in CUPS]).arrange(RIGHT, buff=0.08, aligned_edge=DOWN).scale(0.55)

        def mini_poisson():
            return mini_bars([p / max(N["pois_pmf"]) for p in N["pois_pmf"][:9]], HILITE).scale(0.8)

        def mini_lines():
            return draw_panel(DRAWS_WEAK[:3], width=2.4, height=0.9)[1]

        def rows_of(items):
            rows = VGroup()
            for icon, text in items:
                ic = icon()
                if ic.height > 0.55:
                    ic.scale_to_fit_height(0.55)
                if ic.width > 0.7:
                    ic.scale_to_fit_width(0.7)
                slot = VGroup(Square(0.75, stroke_width=0), ic)
                ic.move_to(slot[0])
                rows.add(VGroup(slot, txt(text, size=28)).arrange(RIGHT, buff=0.35))
            rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT).next_to(head, DOWN, buff=0.6)
            if rows.width > 12.4:
                rows.scale_to_fit_width(12.4)
            return rows.set_x(0)

        part0 = rows_of([(lambda: mini_bars([0.9, 0.35, 0.2]), label("summary_random_variable")),
                         (mini_mean, label("summary_expectation_variance")),
                         (mini_shift, label("summary_shift_scale"))])
        with self.say("11.10") as (tr, t):
            self.play(FadeIn(head), run_time=0.6)
            for k, r in enumerate(part0, 1):
                self.cue(tr, t, k)
                self.play(FadeIn(r, shift=RIGHT * 0.3), run_time=0.6)
        self.play(FadeOut(part0), run_time=0.4)

        part1 = rows_of([(mini_coin, label("summary_bernoulli_binomial")),
                         (mini_cups, label("summary_categorical_multinomial")),
                         (mini_poisson, label("summary_poisson")),
                         (mini_lines, label("summary_dirichlet"))])
        with self.say("11.11") as (tr, t):
            self.play(FadeIn(part1[0], shift=RIGHT * 0.3), FadeIn(part1[1], shift=RIGHT * 0.3), run_time=0.8)
            for k, r in zip((1, 2), part1[2:]):
                self.cue(tr, t, k)
                self.play(FadeIn(r, shift=RIGHT * 0.3), run_time=0.6)
        self.clear_all()

        end = VGroup(txt(label("lecture_3"), size=56, weight=BOLD, color=RLBLUE),
                     txt(label("the_end"), size=34, color=GREY_B)).arrange(DOWN, buff=0.3).move_to(UP * 0.4)
        nxt = VGroup(txt(label("next"), size=28, color=GREY_B),
                     txt(label("lecture_4_continuous_random_variables_and_the_gaussian"), size=40, weight=BOLD,
                         color=RLBLUE),
                     MathTex(r"\int f(x)\,dx = 1", font_size=64, color=HILITE)).arrange(DOWN, buff=0.4)
        if nxt.width > 12.4:
            nxt.scale_to_fit_width(12.4)
        with self.say("11.12") as (tr, t):
            self.play(FadeIn(end, shift=UP * 0.3), run_time=0.9)
            self.cue(tr, t, {"en": "In the next lecture", "uz": "Keyingi maʼruzada"})
            self.play(FadeOut(end), FadeIn(nxt, shift=UP * 0.3), run_time=1.0)
        self.play(FadeOut(nxt), run_time=0.6)
        self.play(FadeIn(brand_outro()), run_time=1.0)
        self.wait(2.0)
        self.clear_all(run_time=0.6)


SCENES = ["S11Shares", "S11Draws", "S11AI", "S11HandsOn", "S11Summary"]
