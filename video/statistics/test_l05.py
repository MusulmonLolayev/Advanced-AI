"""Unit tests for every Lecture 5 calculation.

Each test recomputes a value with capture_l05.compute() and checks it against what the slides
(statistics/lectures/lecture05_*.tex) and the narration (narration/lecture05.md) say. The saved
JSON the video reads must equal a fresh compute(), and the figure script must still print the
same numbers.
    uv run python -m unittest discover -s statistics -p 'test_l05.py'
"""
import json
import sys
import unittest
from math import log, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import capture_l05 as C  # noqa: E402

V = C.compute()


class Section1SamplingDistribution(unittest.TestCase):
    def test_population(self):
        self.assertAlmostEqual(V["mu"], 0.4)
        self.assertAlmostEqual(V["var"], 0.44)

    def test_two_orders(self):
        self.assertEqual([round(p, 2) for p in V["two"]["probs"]], [0.49, 0.28, 0.18, 0.04, 0.01])
        self.assertEqual(V["two"]["means"], [0.0, 0.5, 1.0, 1.5, 2.0])
        self.assertAlmostEqual(V["two_mean"], 0.4)                   # unbiased
        self.assertAlmostEqual(V["two_e2"], 0.38)
        self.assertAlmostEqual(V["two_var"], 0.22)
        self.assertAlmostEqual(V["two_var"], V["two_formula"])       # sigma^2 / n, checked by hand

    def test_hands_on(self):
        self.assertAlmostEqual(V["two_both_none"], 0.49)


class Section2StandardError(unittest.TestCase):
    def test_values(self):
        se = V["se"]
        self.assertEqual(round(V["sigma"], 3), 0.663)
        self.assertEqual(round(se["30"], 3), 0.121)
        self.assertEqual(round(V["steadier"]), 5)                     # "five times steadier"
        self.assertEqual(round(V["se"]["10"], 3), 0.210)
        self.assertEqual([round(se[k], 3) for k in ("10", "40", "160")], [0.21, 0.105, 0.052])

    def test_quadruple_halves(self):
        self.assertAlmostEqual(V["se"]["40"] / V["se"]["10"], 0.5)
        self.assertAlmostEqual(V["se"]["640"] / V["se"]["160"], 0.5)
        self.assertEqual(round(V["se"]["640"], 3), 0.026)            # hands-on
        self.assertEqual(V["tenfold_error_cost"], 100)


class Section3Clt(unittest.TestCase):
    def test_within_one_se(self):
        w = [V["sampling"][n]["within_1se"] for n in ("1", "2", "5", "30")]
        self.assertEqual([round(x, 2) for x in w], [0.9, 0.77, 0.67, 0.66])
        self.assertEqual(round(V["gauss_1se"], 2), 0.68)

    def test_support(self):
        self.assertEqual([V["sampling"][n]["support"] for n in ("1", "2", "5", "30")], [3, 5, 11, 61])

    def test_hands_on_two_se(self):
        self.assertEqual(round(100 * V["sampling"]["30"]["within_2se"]), 96)
        self.assertEqual(round(100 * V["gauss_2se"]), 95)

    def test_exact_distributions_sum_to_one(self):
        for s in V["sampling"].values():
            self.assertAlmostEqual(sum(s["probs"]), 1.0)


class Section4HeavyTail(unittest.TestCase):
    def test_office(self):
        o = V["office"]
        self.assertEqual(o["per"], 20)
        self.assertAlmostEqual(o["ordinary"], 27 / 19)
        self.assertEqual(round(o["ordinary"], 1), 1.4)
        self.assertAlmostEqual(o["mu"], 3.35)

    def test_islands(self):
        self.assertEqual([round(r["total"]) for r in V["runs"][:3]], [43, 81, 120])
        self.assertEqual([round(r["mean"], 1) for r in V["runs"]], [1.4, 2.7, 4.0, 5.3])   # 3 runs: hands-on
        self.assertEqual(round(V["run_step"], 1), 1.3)

    def test_skew(self):
        self.assertLess(V["skew"]["pastry_mean30"], V["skew"]["office_mean30"])


class Section5MiniBatch(unittest.TestCase):
    def test_noise(self):
        self.assertEqual(V["batch_ratio"], 32)
        self.assertEqual(round(V["batch_noise_ratio"], 1), 5.7)
        self.assertEqual(V["batch_task_noise_ratio"], 2.0)          # hands-on: 64 -> 256


class Section6To8Bernoulli(unittest.TestCase):
    def test_counts(self):
        self.assertEqual((V["k"], V["n"], V["n_minus_k"]), (66, 200, 134))
        self.assertEqual(V["p_hat"], 0.33)

    def test_tiny_likelihood(self):
        self.assertEqual(round(V["loglik_hat"], 2), -126.84)
        self.assertEqual(round(V["log10_lik_hat"]), -55)
        self.assertEqual((round(V["lik_hat_mantissa"]), V["lik_hat_exp"]), (8, -56))
        self.assertEqual(round(V["p_some_66"], 2), 0.06)

    def test_relative(self):
        r = V["relative"]
        self.assertEqual([round(r[p], 2) for p in ("0.30", "0.40", "0.25")], [0.66, 0.12, 0.04])   # 0.25: hands-on

    def test_peak(self):
        best = max(V["loglik_curve"], key=lambda t: t[1])[0]
        self.assertAlmostEqual(best, V["p_hat"], places=2)

    def test_hands_on(self):
        self.assertEqual(V["p_hat_task"], 0.3)


class Section9GaussianFit(unittest.TestCase):
    def test_mle(self):
        f = V["fits"]
        self.assertEqual((round(V["xbar"], 2), round(V["sigma_mle"], 2)), (29.88, 1.27))
        self.assertEqual(round(f["mle"]["loglik"], 1), -66.3)
        self.assertEqual((round(f["low"]["loglik"], 1), round(f["wide"]["loglik"], 1)), (-81.8, -86.4))
        self.assertEqual(round(V["fit_margin"], 1), 15.5)

    def test_n_minus_one(self):                                       # hands-on
        self.assertEqual(round(V["s_lecture1"], 2), 1.29)
        self.assertGreater(V["s_lecture1"], V["sigma_mle"])
        self.assertAlmostEqual(V["s_lecture1"] ** 2 * (V["shot_n"] - 1) / V["shot_n"], V["sigma_mle"] ** 2)


class Section10Losses(unittest.TestCase):
    def test_cross_entropy(self):
        self.assertAlmostEqual(V["ce_loss"], -log(0.9))
        self.assertEqual(round(V["ce_loss"], 3), 0.105)              # hands-on


class Sources(unittest.TestCase):
    def test_saved_json_is_fresh(self):
        saved = json.loads((C.OUT / "l05_numbers.json").read_text())
        self.assertEqual(saved, json.loads(json.dumps(C.compute())))

    def test_figure_script_agrees(self):
        fig = (C.OUT / "l05_figures.txt").read_text()
        for line in ("mu = 0.4000   var = 0.4400   sigma = 0.663325",
                     "n= 1  SE=0.6633  P(mean within 1 SE) = 0.9000  support = 3 values",
                     "n=30  SE=0.1211  P(mean within 1 SE) = 0.6640  support = 61 values",
                     "n= 10  SE = 0.2098", "n=160  SE = 0.0524",
                     "office-order population: mu = 3.3500", "clump spacing = 1.286",
                     "max log-likelihood = -126.8357", "likelihood at p_hat = 10^(-55.08)",
                     "p=0.25  log-lik = -130.0448   relative likelihood = 0.0404",
                     "n = 40   x-bar = 29.8773", "sigma-hat (MLE, /n)      = 1.2696",
                     "s  (Lecture 1, /(n-1))   = 1.2858",
                     "centre too low:  mu=28.60  sigma=1.50   log-lik =   -81.807",
                     "too wide:  mu=29.88  sigma=3.20   log-lik =   -86.432"):
            self.assertIn(line, fig)
        self.assertEqual(round(sqrt(V["batch_ratio"]), 2), 5.66)


if __name__ == "__main__":
    unittest.main()
