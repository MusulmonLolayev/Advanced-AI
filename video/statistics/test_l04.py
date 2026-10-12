"""Unit tests for every Lecture 4 calculation.

Each test recomputes a value with capture_l04.compute() and checks it against what the slides
(statistics/lectures/lecture04_*.tex) and the narration (narration/lecture04.md) say. The saved
JSON the video reads must equal a fresh compute(), and the figure script must still print the
same numbers.
    uv run python -m unittest discover -s statistics -p 'test_l04.py'
"""
import json
import sys
import unittest
from math import exp, log
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import capture_l04 as C  # noqa: E402

V = C.compute()


class Section1Density(unittest.TestCase):
    def test_gaps(self):
        self.assertEqual((V["n_gaps"], V["mean_gap"]), (20000, 2.5))
        self.assertEqual(round(V["gaps_mean"], 3), 2.492)

    def test_histograms(self):
        wide, narrow = V["hist"]["2.0"], V["hist"]["0.25"]
        self.assertEqual((wide["bars"], narrow["bars"]), (6, 48))     # six bars, forty-eight bars
        self.assertEqual((wide["counts"][0], narrow["counts"][0]), (11119, 1894))
        self.assertEqual((round(wide["heights"][0], 3), round(narrow["heights"][0], 3)), (0.278, 0.379))

    def test_range(self):
        self.assertEqual(V["between"], [2, 3])
        self.assertTrue(V["between"][0] < V["exact"] < V["between"][1])

    def test_density_can_exceed_one(self):
        self.assertEqual(V["window_density"], 2.0)                    # hands-on: 1 / 0.5

    def test_curve_area(self):
        xs = [x for x, _ in V["pdf_curve"]]
        area = sum((xs[i + 1] - xs[i]) * (V["pdf_curve"][i][1] + V["pdf_curve"][i + 1][1]) / 2
                   for i in range(len(xs) - 1))
        self.assertAlmostEqual(area, 1 - exp(-V["rate"] * 12), places=3)


class Section2Cdf(unittest.TestCase):
    def test_within_two(self):
        self.assertEqual(round(V["p_within"], 2), 0.55)
        self.assertAlmostEqual(V["p_within"], 1 - exp(-0.8))

    def test_lull(self):
        self.assertEqual(round(100 * V["p_lull"], 1), 13.5)

    def test_between(self):                                           # hands-on
        self.assertEqual((round(V["F_lull"], 3), round(V["F_within"], 3)), (0.865, 0.551))
        self.assertEqual(round(V["p_between"], 3), 0.314)

    def test_alert(self):
        self.assertAlmostEqual(1 - exp(-V["rate"] * V["alert_x"]), V["alert_q"])


class Section3UniformExponential(unittest.TestCase):
    def test_uniform(self):
        self.assertEqual((V["delivery_density"], V["p_first"]), (0.1, 0.3))
        self.assertEqual(V["p_last"], 0.2)                             # hands-on

    def test_memoryless(self):
        self.assertAlmostEqual(V["p_more_given"], V["p_more_than_2"])
        self.assertEqual(round(V["p_more_given"], 3), 0.449)


class Section4Sampling(unittest.TestCase):
    def test_inverse_cdf(self):
        self.assertEqual(round(V["x_half"], 2), 1.73)
        self.assertAlmostEqual(V["x_half"], log(2) / V["rate"])
        self.assertAlmostEqual(V["median_gap_check"], 0.5, delta=0.01)   # half the gaps are shorter
        self.assertEqual(round(V["x_task"], 2), 5.76)                     # hands-on, u = 0.9


class Section5Beta(unittest.TestCase):
    def test_two_beliefs(self):
        f, m = V["beta"]["first"], V["beta"]["more"]
        self.assertEqual((f["a"], f["b"], m["a"], m["b"]), (4, 8, 31, 71))
        self.assertEqual((round(f["mean"], 2), round(f["sd"], 2)), (0.33, 0.13))
        self.assertEqual((round(m["mean"], 2), round(m["sd"], 2)), (0.3, 0.05))

    def test_update(self):                                             # hands-on
        self.assertEqual((V["beta_next"]["a"], V["beta_next"]["b"]), (5, 8))
        self.assertEqual(round(V["beta_next"]["mean"], 2), 0.38)

    def test_plausible(self):
        lo, hi = V["beta_plausible"]
        f = V["beta"]["first"]
        self.assertTrue(abs(lo - f["mean"]) < 1.5 * f["sd"] and abs(hi - f["mean"]) < 1.5 * f["sd"])

    def test_curves_are_densities(self):
        for c in [V["beta_next"]] + V["clicks"]:
            xs, ys = zip(*c["curve"])
            area = sum((xs[i + 1] - xs[i]) * (ys[i] + ys[i + 1]) / 2 for i in range(len(xs) - 1))
            self.assertAlmostEqual(area, 1.0, places=2)

    def test_clicks(self):
        a, b = V["clicks"]
        self.assertGreater(a["sd"], 5 * b["sd"])                       # 12 of 15 is far less sure


class Section6Normal(unittest.TestCase):
    def test_rule(self):
        self.assertEqual([round(100 * V["rule"][k], 2) for k in "123"], [68.27, 95.45, 99.73])
        self.assertEqual(V["rule_ranges"], {"1": [58.0, 62.0], "2": [56.0, 64.0], "3": [54.0, 66.0]})


class Section7Label(unittest.TestCase):
    def test_shortfall(self):
        self.assertEqual(V["label_z"], -2.5)
        self.assertEqual(round(100 * V["label_short"], 2), 0.62)
        self.assertEqual(round(V["label_per_1000"]), 6)

    def test_tighter(self):                                            # hands-on
        self.assertEqual(round(V["tight_z"], 1), -3.3)
        self.assertEqual(round(V["tight_per_10000"]), 4)
        self.assertEqual(round(10_000 * V["label_short"]), 62)        # "before, it was sixty-two"

    def test_three_sigma(self):
        self.assertEqual(round(1000 * V["three_sigma_outside"]), 3)    # 3 in 1000 outside 3 sigma


class Section8ZScores(unittest.TestCase):
    def test_which_bake(self):
        self.assertEqual((V["z_light"], round(V["z_loaf"], 2)), (-1.5, -1.33))
        self.assertEqual((round(100 * V["p_light"], 1), round(100 * V["p_loaf"], 1)), (6.7, 9.1))
        self.assertLess(V["z_light"], V["z_loaf"])                    # the croissant is more unusual

    def test_hands_on(self):
        self.assertEqual(V["z_heavy"], 1.5)


class Section9Bivariate(unittest.TestCase):
    def test_moments(self):
        self.assertEqual([round(x, 1) for x in V["day_mean"]], [21.8, 39.5])
        c = V["day_cov"]
        self.assertEqual([round(c[0][0], 1), round(c[0][1], 1), round(c[1][1], 1)], [31.9, 49.6, 128.4])
        self.assertEqual([round(x, 1) for x in V["day_sd"]], [5.6, 11.3])
        self.assertEqual(round(V["day_sd"][0], 2), 5.65)
        self.assertEqual(round(V["day_corr"], 2), 0.77)

    def test_odd_day(self):                                            # hands-on: 28 °C
        self.assertEqual([round(z, 1) for z in V["odd_z"]], [1.1, -1.3])
        self.assertEqual(round(V["odd_mahalanobis"], 1), 3.5)
        self.assertTrue(all(abs(z) < 2 for z in V["odd_z"]))          # neither column alone is odd


class Section10Init(unittest.TestCase):
    def test_within_two_sd(self):
        self.assertEqual(round(100 * V["init_within"]), 95)


class Sources(unittest.TestCase):
    def test_saved_json_is_fresh(self):
        saved = json.loads((C.OUT / "l04_numbers.json").read_text())
        self.assertEqual(saved, json.loads(json.dumps(C.compute())))

    def test_figure_script_agrees(self):
        fig = (C.OUT / "l04_figures.txt").read_text()
        for line in ("n=20000  mean gap=2.492 min",
                     "width=2: first bar holds 11119 of 20000 gaps  -> height 0.278",
                     "width=0.25: first bar holds 1894 of 20000 gaps  -> height 0.379",
                     "P(gap < 2.0 min) = 1 - e^(-0.4*2.0) = 0.5507", "= e^(-2.0)       = 0.1353",
                     "Beta(4, 8): mean=0.3333  sd=0.1307", "Beta(31, 71): mean=0.3039  sd=0.0453",
                     "within 1 sd: quoted 68%, exact 68.27%", "a 57 g croissant: z = -1.50,  P(X < 57) = 0.0668",
                     "a 480 g loaf   : z = -1.333,  P(X < 480) = 0.0912", "P(croissant < 55 g) = 0.00621",
                     "n=300  mean temp=21.81°C  mean cups=39.5", "sample sd: temp=5.65  cups=11.33",
                     "corr=0.775", "z_temp=+1.10  z_cups=-1.28  Mahalanobis=3.54 sd"):
            self.assertIn(line, fig)


if __name__ == "__main__":
    unittest.main()
