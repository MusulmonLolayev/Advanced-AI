"""Unit tests for every Lecture 2 calculation.

Each test recomputes a value with capture_l02.compute() and checks it against what the slides
(statistics/lectures/lecture02_*.tex) and the narration (narration/lecture02.md) say. The saved
JSON the video reads must equal a fresh compute(), and the figure script must still print the
same numbers.
    uv run python -m unittest statistics/test_l02.py
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import capture_l02 as C  # noqa: E402

V = C.compute()


class Section1Conditional(unittest.TestCase):
    def test_die(self):
        self.assertEqual(V["die_p6"], [1, 6])
        self.assertEqual(V["die_p_even"], [1, 2])
        self.assertEqual(V["die_p6_given_even"], [1, 3])     # one of the three even faces

    def test_students(self):
        self.assertEqual((V["n"], V["bike"], V["nobike"], V["bus"], V["nobus"]), (100, 60, 40, 45, 55))
        self.assertEqual(V["p_bus"], 0.45)
        self.assertEqual(V["p_bus_given_bike"], 0.25)          # 15 / 60
        self.assertEqual(V["p_bus_given_nobike"], 0.75)        # 30 / 40, the hands-on


class Section2Tree(unittest.TestCase):
    def test_paths(self):
        self.assertEqual(V["p_bike"], 0.6)
        self.assertAlmostEqual(V["tree_paths"]["bike_bus"], 0.15)
        self.assertEqual(V["tree_counts"], {"bike_bus": 15, "bike_nobus": 45, "nobike_bus": 30, "nobike_nobus": 10})
        self.assertEqual(V["tree_counts"], V["cells"])          # the tree's leaves are the table's cells
        self.assertEqual(V["tree_sum"], 1.0)

    def test_reversed_tree(self):
        self.assertEqual(V["tree_reversed"], {"bus": 0.45, "nobus": 0.55})


class Section3Socks(unittest.TestCase):
    def test_both_black(self):
        s = V["socks"]
        self.assertEqual((s["black"], s["white"], s["total"]), (6, 4, 10))
        self.assertEqual(s["p_first_black"], [3, 5])           # 6/10
        self.assertEqual(s["p_second_black_given"], [5, 9])
        self.assertEqual(s["both_black_unreduced"], [30, 90])
        self.assertEqual(s["both_black"], [1, 3])

    def test_with_replacement(self):
        self.assertAlmostEqual(V["socks"]["with_replacement"], 0.36)

    def test_white_and_pair(self):
        s = V["socks"]
        self.assertEqual(s["both_white_unreduced"], [12, 90])
        self.assertEqual(s["pair_unreduced"], [42, 90])
        self.assertEqual(round(s["pair"], 2), 0.47)
        self.assertLess(s["pair"], 0.5)                         # "less than half the time"


class Section4Table(unittest.TestCase):
    def test_three_probabilities(self):
        self.assertEqual(V["joint_bike_bus"], 0.15)
        self.assertEqual(V["p_bus"], 0.45)
        self.assertEqual(V["p_bus_given_bike"], 0.25)

    def test_hands_on(self):
        self.assertEqual(V["p_bike_given_bus"], [1, 3])        # 15 / 45


class Section5Independence(unittest.TestCase):
    def test_bike_bus_dependent(self):
        self.assertNotEqual(V["p_bus_given_bike"], V["p_bus"])
        self.assertEqual(V["expected_bike_bus"], 27)
        self.assertEqual(V["cells"]["bike_bus"], 15)

    def test_glasses_independent(self):
        self.assertEqual(V["p_bus_given_glasses"], V["p_bus"])
        self.assertEqual(V["expected_glasses_bus"], 18)
        self.assertEqual(V["glasses_bus"], 18)

    def test_hands_on(self):
        self.assertEqual(V["expected_nobike_bus"], 18)
        self.assertEqual(V["cells"]["nobike_bus"], 30)


class Section6Berkeley(unittest.TestCase):
    B = V["berkeley"]

    def test_slide_table(self):
        # every percentage in the slide's table, men then women
        slide = {"A": [62, 82], "B": [63, 68], "C": [37, 34], "D": [33, 35], "E": [28, 24], "F": [6, 7]}
        self.assertEqual(self.B["pct"], slide)
        self.assertEqual((self.B["men_applied"], self.B["women_applied"]), (2691, 1835))
        self.assertEqual((round(100 * self.B["men_rate"]), round(100 * self.B["women_rate"])), (45, 30))

    def test_reversal(self):
        self.assertEqual(self.B["women_higher"], ["A", "B", "D", "F"])

    def test_why(self):
        self.assertGreater(self.B["men_share_AB"], 0.5)                       # over half the men
        self.assertEqual(round(self.B["women_share_CEF"], 2), 0.72)          # nearly three quarters
        a = self.B["all_pct"]
        self.assertEqual((a["A"], a["B"]), (64, 63))
        self.assertEqual((a["C"], a["E"], a["F"]), (35, 25, 6))              # the slide said 7 for F
        # C, E and F are "much harder" than A and B (all under 40 % against over 60 %); they are not
        # the three hardest — D (34 %) is harder than C (35 %), so the narration must not say so
        self.assertTrue(max(a["C"], a["E"], a["F"]) < 40 < 60 < min(a["A"], a["B"]))
        self.assertEqual(sorted(sorted(a, key=a.get)[:3]), ["D", "E", "F"])


class Section7TotalProbability(unittest.TestCase):
    def test_weighted_average(self):
        self.assertEqual(V["plain_average"], 0.5)
        self.assertAlmostEqual(V["total_terms"][0], 0.15)
        self.assertAlmostEqual(V["total_terms"][1], 0.30)
        self.assertAlmostEqual(V["total_bus"], V["p_bus"])                   # the table's margin
        self.assertTrue(0.25 < V["total_bus"] < 0.5)                         # nearer 0.25

    def test_hands_on(self):
        self.assertAlmostEqual(V["total_nobus_terms"][0], 0.45)
        self.assertAlmostEqual(V["total_nobus_terms"][1], 0.10)
        self.assertAlmostEqual(V["total_nobus"], 0.55)


class Section8Bayes(unittest.TestCase):
    def test_students(self):
        self.assertEqual(V["bayes_bike_given_bus"], [1, 3])
        self.assertEqual(V["bayes_bike_given_bus"], V["p_bike_given_bus"])   # the table agrees

    def test_hands_on(self):
        self.assertEqual(V["bayes_nobike_given_bus"], [2, 3])                # 30 / 45


class Section9Screening(unittest.TestCase):
    def test_one_in_hundred(self):
        s = V["screen"]
        self.assertEqual((s["ill"], s["healthy"], s["false_pos"], s["positives"]), (100, 9900, 495, 595))
        self.assertEqual(round(100 * s["ppv"]), 17)
        self.assertEqual(round(V["false_per_real"]), 5)
        self.assertEqual(V["healthy_per_ill"], 99)
        self.assertEqual(s["tested"] // s["ill"], 100)          # shown as P(ill) = 1/100

    def test_hands_on(self):
        s = V["screen_1in10"]
        self.assertEqual((s["ill"], s["healthy"], s["false_pos"], s["positives"]), (1000, 9000, 450, 1450))
        self.assertEqual(s["tested"] // s["ill"], 10)           # shown as P(ill) = 1/10
        self.assertEqual(round(100 * s["ppv"]), 69)


class Section10BaseRates(unittest.TestCase):
    def test_marks(self):
        m = {k: round(100 * v) for k, v in V["base_marks"].items()}
        self.assertEqual(m, {"0.001": 2, "0.01": 17, "0.1": 69})
        self.assertEqual(round(100 * V["screen_1in1000"]["ppv"]), 2)

    def test_accuracy(self):
        self.assertAlmostEqual(V["acc_always_healthy"]["0.01"], 0.99)
        self.assertAlmostEqual(V["acc_always_healthy"]["0.001"], 0.999)     # hands-on

    def test_curve(self):
        ys = [y for _, y in V["base_curve"]]
        self.assertEqual(ys, sorted(ys))                                     # rises with the base rate


class Sources(unittest.TestCase):
    def test_saved_json_is_fresh(self):
        saved = json.loads((C.OUT / "l02_numbers.json").read_text())
        self.assertEqual(saved, json.loads(json.dumps(C.compute())))

    def test_figure_script_agrees(self):
        fig = (C.OUT / "l02_figures.txt").read_text()
        for line in ("P(bus)=0.45  P(bike)=0.60", "P(bus|bike)=0.25  P(bus|no bike)=0.75",
                     "= 27  vs observed 15", "positives = 595", "100/595 = 0.1681",
                     "prevalence 0.100%  →  P(disease | positive) = 0.020",
                     "prevalence 10.000%  →  P(disease | positive) = 0.690"):
            self.assertIn(line, fig)


if __name__ == "__main__":
    unittest.main()
