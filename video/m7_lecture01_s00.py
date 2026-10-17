"""Module 7, Lecture 1 — the opening: the module, the question, and the 581 real articles our agent will read."""
from m7_lecture01_kit import *


class S00Opening(Scene7):
    def construct(self):
        card = title_card(label("m7_title"), label("m7_subtitle"))
        with self.say("0.0") as (tr, t):
            self.play(FadeIn(card, shift=UP * 0.3), run_time=0.8)

        head = txt(ARTICLES["1"]["code_title"], size=34, weight=BOLD).to_edge(UP, buff=SAFE + 0.3)
        tiles = VGroup(*[Square(0.15, stroke_width=0, fill_color=RLBLUE, fill_opacity=0.85) for _ in ARTICLES])
        tiles.arrange_in_grid(cols=42, buff=0.05).next_to(head, DOWN, buff=0.5)
        count = tagged(len(ARTICLES), label("m7_articles"), size=34, value_color=HILITE, value_weight=BOLD)
        count.next_to(tiles, DOWN, buff=0.4)
        with self.say("0.1") as (tr, t):
            self.play(Indicate(card[1], color=HILITE, scale_factor=1.05), run_time=0.8)
            self.cue(tr, t, {"uz": "Oʻzbekiston Mehnat kodeksi", "en": "We build a small agent"})
            self.play(FadeOut(card), FadeIn(head), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(x) for x in tiles], lag_ratio=0.004), run_time=2.4)
            self.play(FadeIn(count, shift=UP * 0.2), run_time=0.5)
        self.clear_all()


SCENES = ["S00Opening"]
