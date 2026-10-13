"""Unit tests for every Lecture 8 calculation.

Each test recomputes a value with capture_l08.compute() and checks it against what the slides
(statistics/lectures/lecture08_*.tex) and the narration (narration/lecture08.md) say. The saved
JSON the video reads must equal a fresh compute(), and the figure script must still print the
same numbers.
    uv run python -m unittest discover -s statistics -p 'test_l08.py'
"""
import json
import sys
import unittest
from math import comb, exp, log
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import capture_l08 as C  # noqa: E402

V = C.compute()
L03 = json.loads((Path(__file__).parent / "raw/l03_numbers.json").read_text())
L05 = json.loads((Path(__file__).parent / "raw/l05_numbers.json").read_text())


class Section1Averages(unittest.TestCase):
    def test_bernoulli_share(self):
        self.assertEqual((V["k"], V["n"]), (66, 200))
        self.assertEqual(round(V["p_hat"], 2), 0.33)                 # "nol butun yuzdan oʻttiz uch"

    def test_poisson_average_is_lecture3s(self):
        self.assertAlmostEqual(V["sim_mean"], L03["pois_sim"]["mean"])
        self.assertEqual(V["sim_mean_slide"], 3.96)                  # the slide's 3.96

    def test_pause_zeros_and_ones(self):
        ones = [1] * V["k"] + [0] * (V["n"] - V["k"])
        self.assertEqual(sum(ones), 66)
        self.assertAlmostEqual(sum(ones) / len(ones), 0.33)


class Section2Logit(unittest.TestCase):
    def test_coffee_shop(self):
        self.assertAlmostEqual(V["p"], 0.3)
        self.assertAlmostEqual(V["odds"], 3 / 7)
        self.assertEqual(round(V["odds"], 2), 0.43)
        self.assertEqual(round(V["eta"], 2), -0.85)                  # slide: eta = -0.85

    def test_sure_runs_off(self):
        self.assertEqual([round(e, 1) for e in V["eta_sure"]], [4.6, 6.9])

    def test_sigmoid_returns_p(self):
        self.assertAlmostEqual(V["sigmoid_back"], 0.3)
        self.assertEqual(V["sigmoid_zero"], 0.5)                     # eta = 0 means p = 1/2

    def test_pause_mirror(self):
        self.assertAlmostEqual(V["eta_mirror"], -V["eta"])
        self.assertEqual(round(V["eta_mirror"], 2), 0.85)


class Section3Softmax(unittest.TestCase):
    def test_scores(self):
        self.assertEqual([round(s, 2) for s in V["scores"]], [-1.61, -0.69, -1.20])   # slide's scores
        for got, want in zip(V["softmax_scores"], (0.2, 0.5, 0.3)):
            self.assertAlmostEqual(got, want)

    def test_plus_two_changes_nothing(self):
        self.assertEqual([round(s, 2) for s in V["scores_shifted"]], [0.39, 1.31, 0.80])
        for got, want in zip(V["softmax_shifted"], (0.2, 0.5, 0.3)):
            self.assertAlmostEqual(got, want)

    def test_gap_is_log_ratio(self):
        self.assertAlmostEqual(V["score_gap_mid_small"], log(V["share_ratio_mid_small"]))
        self.assertEqual(round(V["score_gap_mid_small"], 2), 0.92)
        self.assertEqual(V["share_ratio_mid_small"], 2.5)

    def test_two_class_softmax_is_sigmoid(self):
        self.assertAlmostEqual(V["softmax_two"], V["sigmoid_back"])
        self.assertAlmostEqual(V["softmax_two"], 0.3)

    def test_pause_equal_scores(self):
        for s in V["softmax_zeros"]:
            self.assertAlmostEqual(s, 1 / 3)


class Section4Family(unittest.TestCase):
    def test_pause_poisson_eta(self):
        self.assertEqual(V["lam"], 4)
        self.assertEqual(round(V["eta_pois"], 2), 1.39)


class Section5LogPartition(unittest.TestCase):
    def test_A_at_coffee_shop(self):
        self.assertEqual(round(V["weights"][1], 2), 0.43)
        self.assertEqual(round(V["weights_total"], 2), 1.43)          # slide: log(1.429)
        self.assertEqual(round(V["A"], 3), 0.357)                     # slide: 0.357
        self.assertAlmostEqual(V["A"], V["minus_log_q"])              # = -log 0.7
        self.assertAlmostEqual(V["share_from_weights"], 0.3)

    def test_slope_is_mean_curvature_is_variance(self):
        self.assertAlmostEqual(V["A_prime"], 0.3)
        self.assertAlmostEqual(V["A_second"], V["bern_var"])
        self.assertEqual(round(V["A_second"], 2), 0.21)
        self.assertEqual(round(V["A_slope_num"], 2), 0.30)            # without calculus

    def test_poisson_mean_equals_variance(self):
        self.assertEqual(V["pois_A"], {"A": 4.0, "A_prime": 4.0, "A_second": 4.0})
        self.assertEqual(round(V["sim_mean"], 2), 3.96)
        self.assertEqual(round(V["sim_var"], 2), 3.84)
        self.assertAlmostEqual(V["sim_var"], L03["pois_sim"]["var"])

    def test_log_sum_exp(self):
        self.assertTrue(V["lse_overflows"])
        self.assertEqual(round(V["lse_big"], 2), 1000.31)
        self.assertAlmostEqual(V["lse_big"], 1000 + log(1 + exp(-1)))


class Section6MomentMatching(unittest.TestCase):
    def test_bernoulli(self):
        self.assertEqual(round(V["eta_hat"], 2), -0.71)               # slide: -0.71
        self.assertAlmostEqual(1 / (1 + exp(-V["eta_hat"])), 0.33)

    def test_poisson(self):
        self.assertEqual(round(V["eta_hat_pois"], 2), 1.38)           # slide: log 3.96 = 1.38

    def test_observed_minus_expected(self):
        self.assertAlmostEqual(V["expected_at_true"], 60)
        self.assertAlmostEqual(V["grad_at_true"], 6)

    def test_pause_first_ten_windows(self):
        self.assertEqual(len(V["sim_first"]), 10)
        self.assertEqual(V["sim_first_total"], 33)
        self.assertAlmostEqual(V["sim_first_mean"], 3.3)
        self.assertEqual(round(V["eta_hat_first"], 2), 1.19)


class Section7Sufficiency(unittest.TestCase):
    def test_three_records(self):
        self.assertEqual(set(V["record_totals"].values()), {66})
        self.assertEqual(V["per_morning"] * V["mornings"], 200)
        for r in V["records"].values():
            self.assertLessEqual(max(r), V["per_morning"])
        self.assertEqual(V["records"]["one big day"][0], 20)         # pause: all twenty on day one

    def test_arrangements(self):
        self.assertEqual(len(str(comb(200, 66))), 54)                 # "ellik toʻrt xonali son"
        self.assertEqual(int(V["arrangements_log10"]) + 1, 54)

    def test_given_total_no_p(self):
        vals = list(V["given_total"].values())
        for v in vals:
            self.assertAlmostEqual(v / vals[0], 1.0)
        self.assertAlmostEqual(vals[0] * comb(200, 66), 1.0)

    def test_one_curve(self):
        self.assertEqual(round(V["loglik_hat"], 1), -126.8)


class Section8Gaussian(unittest.TestCase):
    def test_estimates_match_lecture5(self):
        self.assertAlmostEqual(V["xbar"], L05["xbar"])
        self.assertAlmostEqual(V["sigma_hat"], L05["sigma_mle"])
        self.assertAlmostEqual(V["sigma_hat"], V["sigma_direct"])
        self.assertEqual((round(V["xbar"], 2), round(V["sigma_hat"], 2)), (29.88, 1.27))

    def test_two_sums(self):
        self.assertEqual(round(V["sum_x"], 1), 1195.1)
        self.assertEqual(round(V["sum_x2"], 1), 35770.6)

    def test_slide_sums_are_rebuilt_from_rounded_estimates(self):
        # the slide's 1195.2 and 35777.1: noted in the narration header as a slide discrepancy
        self.assertEqual(round(40 * 29.88, 1), 1195.2)
        self.assertEqual(round(40 * (29.88 ** 2 + 1.27 ** 2), 1), 35777.1)
        self.assertGreater(abs(V["sum_x2"] - 35777.1), 6)

    def test_variance_from_sums(self):
        self.assertEqual(round(V["mean_sq"], 2), 894.26)
        self.assertEqual(round(V["xbar_sq"], 2), 892.65)
        self.assertEqual(round(V["var_hat"], 2), 1.61)

    def test_two_spikes_same_sums(self):
        self.assertEqual([round(x, 2) for x in V["spikes"]], [28.61, 31.15])
        self.assertAlmostEqual(V["spikes_sums"][0], V["sum_x"], places=6)
        self.assertAlmostEqual(V["spikes_sums"][1], V["sum_x2"], places=4)

    def test_pause_mean_from_sum(self):
        self.assertEqual(round(round(V["sum_x"], 1) / V["shot_n"], 2), 29.88)


class Section9Conjugacy(unittest.TestCase):
    def test_bus(self):
        b = V["bus"]
        self.assertEqual((b["post"], b["worth"]), ([30, 10], 10))
        self.assertAlmostEqual(b["mean"], 0.75)

    def test_dirichlet(self):
        d = V["dir"]
        self.assertAlmostEqual(d["worth"], 4)
        for got, want in zip(d["post"], (7.8, 23, 13.2)):
            self.assertAlmostEqual(got, want)

    def test_matches_lecture6(self):
        l06 = json.loads((Path(__file__).parent / "raw/l06_numbers.json").read_text())
        self.assertEqual([l06["count30"]["a"], l06["count30"]["b"]], V["bus"]["post"])
        for got, want in zip(l06["dir_post"], V["dir"]["post"]):
            self.assertAlmostEqual(got, want)
        self.assertEqual(l06["walk"]["prior_worth"], 1.0)             # the walk's prior: one timing

    def test_pause(self):
        t = V["pastry_task"]
        self.assertEqual((t["post"], t["worth"]), ([69, 141], 10))
        self.assertEqual(round(t["mean"], 3), 0.329)


class Section10Counters(unittest.TestCase):
    def test_streaming(self):
        self.assertEqual(V["stream_steady"][:3], [[7, 20], [13, 40], [20, 60]])
        self.assertEqual(V["stream_steady"][-1], [66, 200])

    def test_federated(self):
        self.assertEqual((V["halves_big_day"], V["halves_orders"]), ([35, 31], 100))
        self.assertAlmostEqual(V["server_share"], 0.33)

    def test_drift_hidden(self):
        self.assertEqual(V["halves_building"], [18, 48])
        self.assertEqual(V["halves_building_share"], [0.18, 0.48])

    def test_pause(self):
        t = V["stream_task"]
        self.assertEqual((t["total"], t["orders"]), (20, 60))
        self.assertAlmostEqual(t["share"], 1 / 3)


class SavedAndFigure(unittest.TestCase):
    def test_saved_json_is_fresh(self):
        saved = json.loads((Path(__file__).parent / "raw/l08_numbers.json").read_text())
        self.assertEqual(saved, json.loads(json.dumps(V)))

    def test_figure_script_prints_slide_numbers(self):
        out = (Path(__file__).parent / "raw/l08_figures.txt").read_text()
        for s in ("eta = log(p/(1-p)) = -0.8473", "A(eta) = log(1+e^eta) at eta=-0.8473 is 0.356675",
                  "A'(eta) = 0.300000", "p(1-p) = 0.210000", "p_hat = 66/200 = 0.3300",
                  "eta_hat = -0.7082", "eta_hat = 1.3762"):
            self.assertIn(s, out)


if __name__ == "__main__":
    unittest.main()
