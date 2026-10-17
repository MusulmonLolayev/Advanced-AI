"""Module 7, Lecture 1, section 7 — the cache: each turn starts with the last turn's text, so its prefix is cheap.
Numbers: N: cents_per_million(_cached), cache_price_ratio, fresh_10, cached_10, cache_ratio, eval_cached, eval_full."""
from m7_lecture01_kit import *


def money(v):
    return MathTex(rf"\${v}", font_size=48)


class S07Cache(Scene7):
    def construct(self):
        self.section_card(7)
        toks = VGroup(*[Square(0.45, stroke_color=GREY_B, stroke_width=2) for _ in range(10)]).arrange(RIGHT, buff=0.08)
        toks.move_to(UP * 1.2)
        store = node(label("m7_cache"), color=HILITE, width=2.6).move_to(DOWN * 1.4)
        with self.say("7.54") as (tr, t):
            self.play(FadeIn(toks), run_time=0.5)
            self.play(LaggedStart(*[s.animate.set_fill(RLBLUE, opacity=0.9) for s in toks], lag_ratio=0.1), run_time=1.2)
            self.cue(tr, t, {"uz": "Server uni", "en": "A server can"})
            ghost = toks.copy()
            self.play(FadeIn(store), ghost.animate.scale(0.25).move_to(store).set_opacity(0), run_time=0.8)
            self.remove(ghost)
        self.clear_all()

        def turn_bar(steps, new_from):
            cells = VGroup(*[Rectangle(width=0.55, height=0.5, stroke_width=0, fill_opacity=0.9,
                                       fill_color=GREY_D if j < new_from else GOOD) for j in range(steps)])
            return cells.arrange(RIGHT, buff=0.05)
        b1 = turn_bar(6, 0).move_to(UP * 1.0, aligned_edge=LEFT).shift(LEFT * 4.5)
        b2 = turn_bar(7, 6).move_to(DOWN * 0.2, aligned_edge=LEFT).shift(LEFT * 4.5)
        cached_lab = txt(label("m7_cached"), size=24, color=GREY_B).next_to(b2[:6], DOWN, buff=0.2)
        new_lab = txt(label("m7_new"), size=24, color=GOOD).next_to(b2[6], DOWN, buff=0.2)
        with self.say("7.55") as (tr, t):
            self.play(FadeIn(b1), run_time=0.5)
            self.play(TransformFromCopy(b1, b2[:6]), FadeIn(b2[6]), run_time=0.8)
            self.cue(tr, t, {"uz": "Faqat oxirgi", "en": "Only the tokens"})
            self.play(FadeIn(cached_lab), FadeIn(new_lab), run_time=0.5)
        self.clear_all()

        full = VGroup(MathTex(rf"{N['cents_per_million']:g}\ \text{{¢}}", font_size=60),
                      txt(label("m7_new"), size=24, color=GOOD)).arrange(DOWN, buff=0.2)
        cached = VGroup(MathTex(rf"{N['cents_per_million_cached']:g}\ \text{{¢}}", font_size=60),
                        txt(label("m7_cached"), size=24, color=GREY_B)).arrange(DOWN, buff=0.2)
        pair = VGroup(full, cached).arrange(RIGHT, buff=2.6).move_to(UP * 0.4)
        per = txt(label("m7_per_million"), size=26, color=GREY_B).next_to(pair, UP, buff=0.5)
        ratio = VGroup(MathTex(rf"\times {N['cache_price_ratio']}", font_size=56, color=HILITE),
                       txt(label("m7_cheaper"), size=26, color=HILITE)).arrange(RIGHT, buff=0.25).next_to(pair, DOWN, buff=0.7)
        with self.say("7.56") as (tr, t):
            self.play(FadeIn(per), FadeIn(full), run_time=0.6)
            self.play(FadeIn(cached), run_time=0.5)
            self.play(FadeIn(ratio, scale=1.2), run_time=0.5)
        self.clear_all()

        total = N["fresh_10"] + N["cached_10"]
        w = 11.0 / total
        fresh = Rectangle(width=N["fresh_10"] * w, height=0.8, stroke_width=0, fill_color=GOOD, fill_opacity=0.95)
        cach = Rectangle(width=N["cached_10"] * w, height=0.8, stroke_width=0, fill_color=GREY_D, fill_opacity=0.95)
        bar = VGroup(fresh, cach).arrange(RIGHT, buff=0).move_to(UP * 0.8)
        nf = VGroup(MathTex(f"{N['fresh_10']:,}".replace(",", "{,}"), font_size=36, color=GOOD),
                    txt(label("m7_new"), size=22, color=GOOD)).arrange(DOWN, buff=0.1).next_to(fresh, DOWN, buff=0.25)
        nc = VGroup(MathTex(f"{N['cached_10']:,}".replace(",", "{,}"), font_size=36),
                    txt(label("m7_cached"), size=22, color=GREY_B)).arrange(DOWN, buff=0.1).next_to(cach, DOWN, buff=0.25)
        steps10 = tagged(10, label("m7_steps"), size=28).next_to(bar, UP, buff=0.35)
        run_ratio = VGroup(txt(label("m7_one_run"), size=26), MathTex(rf"\times {N['cache_ratio']}", font_size=48, color=HILITE),
                           txt(label("m7_cheaper"), size=26, color=HILITE)).arrange(RIGHT, buff=0.25)
        run_ratio.to_edge(DOWN, buff=SAFE + 0.6)
        with self.say("7.57") as (tr, t):
            self.play(FadeIn(steps10), GrowFromEdge(bar, LEFT), run_time=0.8)
            self.play(FadeIn(nf), FadeIn(nc), run_time=0.5)
            self.cue(tr, t, {"uz": "Natijada", "en": "One run"})
            self.play(FadeIn(run_ratio), run_time=0.5)
        self.clear_all()

        evalq = tagged(500, label("m7_eval_questions"), size=32).to_edge(UP, buff=SAFE + 0.6)
        before = MathTex(rf"\${N['eval_full']}", font_size=64, color=GREY_B)
        after = MathTex(rf"\${N['eval_cached']}", font_size=72, color=HILITE)
        arrow = Arrow(LEFT, RIGHT, color=WHITE)
        VGroup(before, arrow, after).arrange(RIGHT, buff=0.6).move_to(ORIGIN)
        with self.say("7.58") as (tr, t):
            self.play(FadeIn(evalq), FadeIn(before), run_time=0.6)
            self.play(GrowArrow(arrow), FadeIn(after), run_time=0.6)
        self.clear_all()

        keep = txt(label("m7_keep_start"), size=30, weight=BOLD).to_edge(UP, buff=SAFE + 0.5)
        cells = VGroup(*[Rectangle(width=0.7, height=0.55, stroke_width=0, fill_color=GREY_D, fill_opacity=0.95)
                         for _ in range(10)]).arrange(RIGHT, buff=0.05).move_to(DOWN * 0.1)
        date = VGroup(Rectangle(width=0.9, height=0.55, stroke_width=0, fill_color=RLRED, fill_opacity=0.95),
                      txt(label("m7_date"), size=18))
        date[1].move_to(date[0])
        lost = txt(label("m7_cache_lost"), size=26, color=RLRED).next_to(cells, DOWN, buff=0.5)
        with self.say("7.59") as (tr, t):
            self.play(FadeIn(keep), FadeIn(cells), run_time=0.6)
            self.cue(tr, t, {"uz": "Tizim koʻrsatmasiga", "en": "If we put"})
            date.next_to(cells, LEFT, buff=0.05)
            self.play(FadeIn(date, shift=RIGHT * 0.3), VGroup(cells).animate.shift(RIGHT * 0.5), run_time=0.6)
            self.play(LaggedStart(*[c.animate.set_fill(RLORANGE) for c in cells], lag_ratio=0.08), FadeIn(lost), run_time=1.0)
        self.clear_all()

        card = pause([label("m7_pause_date")])
        with self.say("7.60") as (tr, t):
            self.play(FadeIn(card), run_time=0.6)
        self.hands_on()
        self.clear_all()
        with self.say("7.61") as (tr, t):
            self.play(FadeIn(txt(label("m7_action_space"), size=44, weight=BOLD, color=HILITE)), run_time=0.7)
        self.clear_all()


SCENES = ["S07Cache"]
