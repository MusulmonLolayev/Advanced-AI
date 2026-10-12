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


class Draft2AddedLines(unittest.TestCase):
    """The numbers the draft-2 lines (lettered keys, e.g. 1.4a) speak or show."""
    D = V["depth"]

    def test_rounded_reading(self):                                    # 1.4a: about 1.5 %
        self.assertEqual(self.D["rounded"], [2.45, 2.55])
        self.assertAlmostEqual(self.D["p_rounded"], exp(-0.98) - exp(-1.02))
        self.assertEqual(round(100 * self.D["p_rounded"], 1), 1.5)

    def test_first_bar(self):                                          # 1.5a
        self.assertEqual(self.D["first_bar_count"], 11119)
        self.assertEqual(round(self.D["first_bar_share"], 3), 0.556)
        self.assertEqual(round(self.D["first_bar_height"], 3), 0.278)
        self.assertAlmostEqual(self.D["first_bar_height"], V["hist"]["2.0"]["heights"][0])

    def test_density_times_length(self):                               # 1.9a: 0.4 × 0.1
        self.assertEqual(round(self.D["short_estimate"], 2), 0.04)
        self.assertEqual(round(self.D["short_exact"], 2), 0.04)
        self.assertEqual(round(self.D["short_exact"], 3), 0.039)

    def test_rate_and_gap(self):                                       # 2.1a: 4 / 10 = 0.4, 1 / 0.4 = 2.5
        self.assertAlmostEqual(4 / 10, V["rate"])
        self.assertAlmostEqual(1 / V["rate"], 2.5)

    def test_running_total(self):                                      # 2.4a: 55, 86, 98 %
        self.assertEqual([round(100 * x) for x in (V["F_within"], V["F_lull"], self.D["F_far"])], [55, 86, 98])

    def test_alert_point(self):                                        # 2.8a: 11.5 minutes
        self.assertEqual(round(V["alert_x"], 1), 11.5)
        self.assertAlmostEqual(V["alert_x"], log(100) / 0.4)

    def test_uniform_line(self):                                       # 3.2a
        self.assertEqual((V["delivery_density"], self.D["uniform_mean"]), (0.1, 5.0))

    def test_uniform_remembers(self):                                  # 3.7a
        self.assertEqual(self.D["waited_delivery"], 8)
        self.assertEqual(V["delivery"] - self.D["waited_delivery"], 2)
        self.assertEqual(self.D["p_rest_given_waited"], 1.0)

    def test_median_below_mean(self):                                  # 4.4a: 1.73 < 2.5
        self.assertEqual((round(self.D["median_gap"], 2), self.D["mean_gap"]), (1.73, 2.5))
        self.assertAlmostEqual(self.D["median_gap"], log(2) / 0.4)

    def test_prior_counts(self):                                       # 5.4a: Beta(1, 1) + 3, + 7
        a0, b0 = self.D["prior"]
        self.assertEqual((a0 + 3, b0 + 7), (V["beta"]["first"]["a"], V["beta"]["first"]["b"]))

    def test_spread_shrinks_slower(self):                              # 5.5a: ×10 data, ÷ about 3
        self.assertEqual(self.D["data_ratio"], 10)
        self.assertEqual(round(self.D["beta_sd_ratio"]), 3)
        self.assertEqual((round(V["beta"]["first"]["sd"], 2), round(V["beta"]["more"]["sd"], 2)), (0.13, 0.05))

    def test_clicks(self):                                             # 5.7a: both 0.8; 0.1 vs 0.01; 8×
        self.assertEqual(self.D["clicks_share"], [0.8, 0.8])
        self.assertEqual((round(V["clicks"][0]["sd"], 1), round(V["clicks"][1]["sd"], 2)), (0.1, 0.01))
        self.assertEqual(round(self.D["clicks_sd_ratio"]), 8)

    def test_dice(self):                                               # 6.2a
        one, two, ten = (self.D["dice"][k] for k in ("1", "2", "10"))
        for p in one["pmf"]:
            self.assertAlmostEqual(p, 1 / 6)
        self.assertEqual(two["mode"], 7)
        self.assertAlmostEqual(two["p_mode"], 6 / 36)
        self.assertEqual(ten["mode"], 35)
        self.assertAlmostEqual(sum(ten["pmf"]), 1)

    def test_one_in_outside(self):                                     # 6.6a: 1 in 3, 22, 370
        self.assertEqual([round(self.D["one_in_outside"][k]) for k in "123"], [3, 22, 370])

    def test_left_tail_only(self):                                     # 7.2a: the label's shortfall is one tail
        self.assertAlmostEqual(V["label_short"], (1 - (2 * C.Phi(2.5) - 1)) / 2)

    def test_raise_the_mean(self):                                     # 7.8a: mu 61 → 13 in 10,000, vs 4
        self.assertEqual(self.D["mu_up_z"], -3.0)
        self.assertEqual(round(self.D["mu_up_per_10000"]), 13)
        self.assertEqual(round(V["tight_per_10000"]), 4)
        self.assertEqual(self.D["mu_up"] - V["mu"], 1.0)

    def test_rulers(self):                                             # 8.1a
        self.assertEqual(self.D["ruler"]["croissant"], [56, 58, 60, 62, 64])
        self.assertEqual(self.D["ruler"]["loaf"], [470, 485, 500, 515, 530])

    def test_covariance_products(self):                                # 9.2a: 240 of 300
        self.assertEqual(self.D["cov_positive_days"], 240)
        self.assertAlmostEqual(self.D["cov_from_products"], V["day_cov"][0][1])
        self.assertEqual(round(self.D["cov_from_products"], 1), 49.6)

    def test_correlation_scale(self):                                  # 9.5a
        self.assertTrue(-1 < V["day_corr"] < 1)
        self.assertEqual(round(V["day_corr"], 2), 0.77)

    def test_expected_cups(self):                                      # 9.8a: about 49, 24 short
        self.assertEqual(round(self.D["expected_cups_at_28"]), 49)
        self.assertEqual(round(self.D["cups_short"]), 24)

    def test_long_axis_share(self):                                    # 10.1a: 93 %
        self.assertEqual(round(100 * self.D["pca_share"]), 93)


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
