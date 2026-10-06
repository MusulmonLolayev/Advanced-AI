"""Video 1 — Why Do We Need the Mean?

Every number shown here comes from statistics/raw/v01_numbers.txt, which is
produced (and asserted against the slide figures) by statistics/capture_v01.py.
"""
import json

import numpy as np
from common import *

RAW = Path(__file__).parent / "statistics" / "raw"
D = json.loads((RAW / "v01_numbers.json").read_text())
DRINKERS = np.loadtxt(RAW / "v01_drinkers.txt")

N_EMP = D["n_emp"]
N_DRINKERS = D["n_drinkers"]
PAYROLL_MEAN = D["payroll_mean"]
PAYROLL_TOTAL = D["payroll_total"]
DRINK_MEAN, DRINK_MED = D["drink_mean"], D["drink_median"]
AFTER_MEAN, AFTER_MED = D["after_mean"], D["after_median"]
BILLIONAIRE = D["billionaire"]
NINE, NINE_SUM, NINE_MEAN, NINE_BELOW = D["nine"], D["nine_sum"], D["nine_mean"], D["nine_below"]

# The narration speaks these figures in words, so fail loudly if the script's
# output ever moves away from what the voice says.
assert (N_EMP, N_DRINKERS, NINE_SUM, NINE_BELOW) == (600, 50, 453, 6)
assert (round(PAYROLL_MEAN), round(PAYROLL_TOTAL)) == (51613, 30968030)
assert (round(DRINK_MEAN), round(DRINK_MED)) == (50627, 47323)
assert (round(AFTER_MEAN), round(AFTER_MED)) == (2941226105, 47761)
assert round(NINE_MEAN, 3) == 50.333


def money(v, cents=False):
    return f"${v:,.2f}" if cents else f"${v:,.0f}"


# ─── log axis shared by scene 4 ───────────────────────────────────────────
LO, HI, LEFT_X, RIGHT_X = np.log10(2e4), np.log10(3e11), -5.6, 5.6


def xpos(s):
    return LEFT_X + (RIGHT_X - LEFT_X) * (np.log10(s) - LO) / (HI - LO)


class S1Problem(CourseScene):
    def construct(self):
        self.add(brand_mark())
        head = txt(f"{N_EMP} employees", size=34, color=GREY_B).to_edge(UP, buff=SAFE + 0.3)
        dots = VGroup(*[Dot(radius=0.045, color=RLBLUE, fill_opacity=0.85) for _ in range(N_EMP)])
        dots.arrange_in_grid(rows=20, cols=30, buff=0.17).move_to(ORIGIN + DOWN * 0.25)

        with self.voiceover(
            "Six hundred people work at this company. Here is what every one of them earns. "
            "Your manager asks a simple question: what do people earn here?"
        ):
            self.play(FadeIn(head), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots],
                                  lag_ratio=0.004, run_time=5.5))

        q = txt("What do people earn here?", size=40, weight=BOLD, color=HILITE)
        q.next_to(dots, DOWN, buff=0.5)
        with self.voiceover(
            "You cannot read out six hundred numbers. You need one number that stands for "
            "all of them. But which one?"
        ):
            self.play(Write(q), run_time=1.5)
            self.wait(1.0)
        self.clear_all()


class S2Mean(CourseScene):
    def construct(self):
        self.add(brand_mark())
        dots = VGroup(*[Dot(radius=0.045, color=RLBLUE, fill_opacity=0.85) for _ in range(N_EMP)])
        dots.arrange_in_grid(rows=20, cols=30, buff=0.17).move_to(UP * 0.6)
        self.add(dots)

        formula = MathTex(r"\bar{x} \;=\; \frac{1}{n}\sum_{i=1}^{n} x_i", font_size=54)
        formula.move_to(UP * 0.6)
        with self.voiceover(
            "The oldest answer is also the simplest. Add everything up, and share it out equally."
        ):
            self.play(LaggedStart(*[d.animate.move_to(UP * 0.6) for d in dots],
                                  lag_ratio=0.002, run_time=3.0))
            self.play(FadeOut(dots, scale=0.2), FadeIn(formula), run_time=1.0)

        value = txt(money(PAYROLL_MEAN), size=64, weight=BOLD, color=RLGREEN)
        value.next_to(formula, DOWN, buff=0.7)
        label = txt("the mean", size=30, color=GREY_B).next_to(value, DOWN, buff=0.3)
        with self.voiceover(
            "Here that comes to fifty-one thousand, six hundred and thirteen dollars. "
            "We call it the mean."
        ):
            self.play(FadeIn(value, shift=UP * 0.3), run_time=1.0)
            self.play(FadeIn(label), run_time=0.6)

        with self.voiceover(
            "Notice what it is really doing. It is the amount each person would get if all the "
            "money in the company were collected, and split evenly."
        ):
            self.play(Indicate(value, color=HILITE, scale_factor=1.12), run_time=1.6)
            self.wait(1.0)
        self.clear_all()


class S3Totals(CourseScene):
    def construct(self):
        self.add(brand_mark())
        head = txt("The mean remembers the total", size=38, weight=BOLD)
        head.to_edge(UP, buff=SAFE + 0.4)
        line = MathTex(
            rf"\${PAYROLL_MEAN:,.2f}".replace(",", "{,}"), r"\;\times\;", str(N_EMP),
            r"\;=\;", rf"\${PAYROLL_TOTAL:,.0f}".replace(",", "{,}"),
            font_size=52,
        )
        line[0].set_color(RLGREEN)
        line[4].set_color(HILITE)

        with self.voiceover(
            "That is why the mean is what you want whenever totals matter."
        ):
            self.play(FadeIn(head), run_time=0.8)
            self.play(FadeIn(line[0]), run_time=0.6)

        with self.voiceover(
            "Multiply it back by six hundred, and you recover the entire payroll: "
            "just under thirty-one million dollars."
        ):
            self.play(FadeIn(line[1]), FadeIn(line[2]), run_time=0.7)
            self.play(FadeIn(line[3]), FadeIn(line[4]), run_time=0.9)
            self.wait(0.8)

        note = txt("No other summary does that.", size=32, color=GREY_B)
        note.next_to(line, DOWN, buff=0.9)
        with self.voiceover(
            "No other summary does that. The mean is the one that remembers the total."
        ):
            self.play(FadeIn(note), run_time=0.8)
            self.wait(1.0)
        self.clear_all()


class S4Failure(CourseScene):
    def construct(self):
        self.add(brand_mark())
        axis = Line(LEFT_X * RIGHT, RIGHT_X * RIGHT, stroke_width=2, color=GREY_B)
        axis.shift(DOWN * 1.6)
        ticks = VGroup()
        for val, lab in ((1e5, "$100k"), (1e6, "$1M"), (1e7, "$10M"),
                         (1e8, "$100M"), (1e9, "$1B"), (1e10, "$10B"), (1e11, "$100B")):
            t = Line(UP * 0.1, DOWN * 0.1, stroke_width=2, color=GREY_B)
            t.move_to([xpos(val), axis.get_y(), 0])
            lb = txt(lab, size=20, color=GREY_B).next_to(t, DOWN, buff=0.18)
            ticks.add(t, lb)

        rng = np.random.default_rng(1)
        crowd = VGroup(*[
            Dot(radius=0.055, color=RLBLUE, fill_opacity=0.8).move_to(
                [xpos(s), axis.get_y() + 0.55 + rng.uniform(-0.3, 0.3), 0])
            for s in DRINKERS])

        mean_line = Line(DOWN * 0.25, UP * 2.2, color=RLRED, stroke_width=5)
        mean_line.move_to([xpos(DRINK_MEAN), axis.get_y() + 1.0, 0])
        med_line = DashedLine(DOWN * 0.25, UP * 2.2, color=RLGREEN, stroke_width=5)
        med_line.move_to([xpos(DRINK_MED), axis.get_y() + 1.0, 0])

        sw_m = Line(ORIGIN, RIGHT * 0.45, color=RLRED, stroke_width=5)
        sw_d = DashedLine(ORIGIN, RIGHT * 0.45, color=RLGREEN, stroke_width=5)
        m_val = txt(money(DRINK_MEAN), size=28, color=WHITE)
        d_val = txt(money(DRINK_MED), size=28, color=WHITE)
        legend = VGroup(
            VGroup(sw_m, txt("mean", size=26, color=GREY_B), m_val).arrange(RIGHT, buff=0.25),
            VGroup(sw_d, txt("median", size=26, color=GREY_B), d_val).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_corner(UL, buff=SAFE + 0.25)

        with self.voiceover(
            "Now watch it fail. Fifty of those six hundred employees go out for a drink."
        ):
            self.play(Create(axis), FadeIn(ticks), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in crowd],
                                  lag_ratio=0.03, run_time=2.0))

        with self.voiceover(
            "Their average salary is fifty thousand, six hundred and twenty-seven dollars, and "
            "the middle person earns forty-seven thousand, three hundred and twenty-three. "
            "Close together, as you would expect."
        ):
            self.play(Create(mean_line), Create(med_line), run_time=1.0)
            self.play(FadeIn(legend), run_time=0.8)
            self.wait(1.2)

        bill = Dot(radius=0.11, color=HILITE).move_to(
            [xpos(BILLIONAIRE), axis.get_y() + 0.55, 0])
        bill_lab = txt("a billionaire", size=24, color=HILITE).next_to(bill, UP, buff=0.25)
        with self.voiceover(
            "Then one more person walks in: a billionaire. Nobody already in that room gained "
            "a single cent."
        ):
            self.play(FadeIn(bill, scale=0.3), FadeIn(bill_lab), run_time=1.0)
            self.wait(1.2)

        new_m = txt(money(AFTER_MEAN), size=28, color=WHITE).move_to(m_val, aligned_edge=LEFT)
        new_d = txt(money(AFTER_MED), size=28, color=WHITE).move_to(d_val, aligned_edge=LEFT)
        with self.voiceover(
            "But the average salary in that room is now two point nine billion dollars."
        ):
            self.play(
                mean_line.animate.move_to([xpos(AFTER_MEAN), mean_line.get_y(), 0]),
                FadeTransform(m_val, new_m),
                med_line.animate.move_to([xpos(AFTER_MED), med_line.get_y(), 0]),
                FadeTransform(d_val, new_d),
                run_time=2.4,
            )
            self.wait(0.8)

        arrow = Arrow(mean_line.get_top() + UP * 1.0 + LEFT * 1.6, mean_line.get_top() + UP * 0.1,
                      buff=0.05, color=RLRED, stroke_width=4)
        nobody = txt("describes nobody here", size=28, color=RLRED)
        nobody.next_to(arrow.get_start(), LEFT, buff=0.15)
        with self.voiceover(
            "Look at where that red line lands. In empty space, between the crowd and the "
            "billionaire. It describes nobody present."
        ):
            self.play(GrowArrow(arrow), FadeIn(nobody), run_time=1.2)
            self.wait(1.6)
        self.clear_all()


class S5Median(CourseScene):
    def construct(self):
        self.add(brand_mark())
        head = txt("The line that did not move", size=38, weight=BOLD, color=RLGREEN)
        head.to_edge(UP, buff=SAFE + 0.4)
        labels = VGroup(txt("before", size=30, color=GREY_B),
                        txt("after", size=30, color=GREY_B))
        labels.arrange(DOWN, aligned_edge=RIGHT, buff=0.75)
        values = VGroup(txt(money(DRINK_MED), size=44, color=WHITE),
                        txt(money(AFTER_MED), size=44, color=WHITE))
        values.arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        values.next_to(labels, RIGHT, buff=0.6)
        for lb, v in zip(labels, values):
            lb.match_y(v)
        rows = VGroup(VGroup(labels[0], values[0]), VGroup(labels[1], values[1]))
        VGroup(labels, values).move_to(ORIGIN)

        with self.voiceover(
            "Now the dashed line. Before: forty-seven thousand, three hundred and twenty-three."
        ):
            self.play(FadeIn(head), run_time=0.7)
            self.play(FadeIn(rows[0]), run_time=0.8)

        with self.voiceover(
            "After: forty-seven thousand, seven hundred and sixty-one. It moved by four hundred "
            "dollars."
        ):
            self.play(FadeIn(rows[1]), run_time=0.8)
            self.wait(1.2)

        nxt = txt("That line is the median.", size=36, weight=BOLD, color=HILITE)
        nxt.next_to(rows, DOWN, buff=0.9)
        with self.voiceover(
            "That line is the median, and it is the subject of the next video."
        ):
            self.play(FadeIn(nxt), run_time=0.8)
            self.wait(1.0)
        self.clear_all()


class S6HandsOn(CourseScene):
    def construct(self):
        self.add(brand_mark())
        nums = txt("  ".join(str(n) for n in NINE), size=46, weight=BOLD, color=RLBLUE)
        unit = txt("salaries, in thousands of dollars", size=26, color=GREY_B)
        card = pause_card(["Work out the mean of these nine.",
                           "Count how many of the nine earn less than it."])
        block = VGroup(card, nums, unit).arrange(DOWN, buff=0.5)

        with self.voiceover(
            "Your turn. Pause the video. Here are nine salaries, in thousands of dollars. "
            "Work out the mean. Then count how many of the nine people earn less than it."
        ):
            self.play(FadeIn(block), run_time=1.0)
        self.wait(3)

        self.play(FadeOut(card), FadeOut(unit), run_time=0.6)
        self.play(nums.animate.to_edge(UP, buff=SAFE + 0.8), run_time=0.8)
        steps = VGroup(
            txt(f"total  =  {NINE_SUM}", size=40),
            txt(f"mean  =  {NINE_SUM} ÷ {len(NINE)}  =  {NINE_MEAN:.3f}", size=40, color=RLGREEN),
        ).arrange(DOWN, buff=0.45).next_to(nums, DOWN, buff=0.8)
        with self.voiceover(
            "The total is four hundred and fifty-three, so the mean is fifty thousand, three "
            "hundred and thirty-three dollars."
        ):
            self.play(FadeIn(steps[0]), run_time=0.7)
            self.play(FadeIn(steps[1]), run_time=0.8)
            self.wait(0.8)

        sting = txt(f"{NINE_BELOW} of the {len(NINE)} earn less than that", size=36, weight=BOLD, color=HILITE)
        sting.next_to(steps, DOWN, buff=0.8)
        with self.voiceover(
            "And six of the nine earn less than that. Even with no billionaire anywhere, the "
            "mean already sits above most of the people in it."
        ):
            self.play(FadeIn(sting), run_time=0.8)
            self.wait(1.6)
        self.clear_all()


class S7Next(CourseScene):
    def construct(self):
        card = next_card(2, "Why Do We Need the Median?")
        with self.voiceover("Which is exactly the problem the median solves."):
            self.play(FadeIn(card, shift=UP * 0.3), run_time=1.0)
            self.wait(1.4)
        self.play(FadeOut(card), run_time=0.6)
        self.play(FadeIn(brand_outro()), run_time=1.0)
        self.wait(2.0)


SCENES = ["S1Problem", "S2Mean", "S3Totals", "S4Failure", "S5Median", "S6HandsOn", "S7Next"]
