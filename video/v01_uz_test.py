"""Uzbek voice test — two scenes from video 1, narrated by uz-UZ-SardorNeural.

Built to judge the voice in context: how it reads Uzbek prose, how it reads
large sums, and whether the oʻ/gʻ okina (U+02BB) survives. The translation is
mine and needs a native reviewer before anything ships.
"""
import json

from common import *

RAW = Path(__file__).parent / "statistics" / "raw"
D = json.loads((RAW / "v01_numbers.json").read_text())
PAYROLL_MEAN, PAYROLL_TOTAL, N_EMP = D["payroll_mean"], D["payroll_total"], D["n_emp"]
DRINK_MED, AFTER_MED = D["drink_median"], D["after_median"]


def money(v, cents=False):
    return f"${v:,.2f}" if cents else f"${v:,.0f}"


class UzTotals(CourseScene):
    def construct(self):
        self.add(brand_mark())
        head = txt("Oʻrtacha qiymat yigʻindini eslab qoladi", size=36, weight=BOLD)
        head.to_edge(UP, buff=SAFE + 0.4)
        line = MathTex(
            rf"\${PAYROLL_MEAN:,.2f}".replace(",", "{,}"), r"\;\times\;", str(N_EMP),
            r"\;=\;", rf"\${PAYROLL_TOTAL:,.0f}".replace(",", "{,}"), font_size=52)
        line[0].set_color(RLGREEN)
        line[4].set_color(HILITE)

        with self.voiceover(
            "Shuning uchun umumiy yigʻindi muhim boʻlganda aynan oʻrtacha qiymat kerak boʻladi."
        ):
            self.play(FadeIn(head), run_time=0.8)
            self.play(FadeIn(line[0]), run_time=0.6)

        with self.voiceover(
            "Uni olti yuzga koʻpaytiring va butun ish haqi fondini qaytarib olasiz: "
            "oʻttiz bir million dollarga yaqin."
        ):
            self.play(FadeIn(line[1]), FadeIn(line[2]), run_time=0.7)
            self.play(FadeIn(line[3]), FadeIn(line[4]), run_time=0.9)
            self.wait(0.8)

        note = txt("Buni boshqa hech bir koʻrsatkich qila olmaydi.", size=30, color=GREY_B)
        note.next_to(line, DOWN, buff=0.9)
        with self.voiceover(
            "Buni boshqa hech bir koʻrsatkich qila olmaydi. "
            "Oʻrtacha qiymat yigʻindini eslab qoladi."
        ):
            self.play(FadeIn(note), run_time=0.8)
            self.wait(1.0)
        self.clear_all()


class UzMedian(CourseScene):
    def construct(self):
        self.add(brand_mark())
        head = txt("Siljimagan chiziq", size=38, weight=BOLD, color=RLGREEN)
        head.to_edge(UP, buff=SAFE + 0.4)
        labels = VGroup(txt("avval", size=30, color=GREY_B), txt("keyin", size=30, color=GREY_B))
        labels.arrange(DOWN, aligned_edge=RIGHT, buff=0.75)
        values = VGroup(txt(money(DRINK_MED), size=44), txt(money(AFTER_MED), size=44))
        values.arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        values.next_to(labels, RIGHT, buff=0.6)
        for lb, v in zip(labels, values):
            lb.match_y(v)
        VGroup(labels, values).move_to(ORIGIN)

        with self.voiceover(
            "Endi uzuq chiziqqa qarang. Avval: qirq yetti ming uch yuz yigirma uch dollar."
        ):
            self.play(FadeIn(head), run_time=0.7)
            self.play(FadeIn(labels[0]), FadeIn(values[0]), run_time=0.8)

        with self.voiceover(
            "Keyin: qirq yetti ming yetti yuz oltmish bir dollar. "
            "U atigi toʻrt yuz dollarga siljidi."
        ):
            self.play(FadeIn(labels[1]), FadeIn(values[1]), run_time=0.8)
            self.wait(1.2)

        nxt = txt("Bu chiziq — mediana.", size=36, weight=BOLD, color=HILITE)
        nxt.next_to(values, DOWN, buff=0.9)
        with self.voiceover(
            "Bu chiziq — mediana, va u keyingi videoning mavzusi."
        ):
            self.play(FadeIn(nxt), run_time=0.8)
            self.wait(1.0)
        self.clear_all()


SCENES = ["UzTotals", "UzMedian"]
