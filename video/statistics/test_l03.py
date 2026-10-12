"""Unit tests for every Lecture 3 calculation.

Each test recomputes a value with capture_l03.compute() and checks it against what the slides
(statistics/lectures/lecture03_*.tex) and the narration (narration/lecture03.md) say. The saved
JSON the video reads must equal a fresh compute(), and the figure script must still print the
same numbers.
    uv run python -m unittest discover -s statistics -p 'test_l03.py'
"""
import json
import sys
import unittest
from math import isclose, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import capture_l03 as C  # noqa: E402

V = C.compute()


class Section1Pmf(unittest.TestCase):
    def test_two_dice(self):
        self.assertEqual(sum(V["dice_ways"].values()), V["dice_outcomes"])
        self.assertEqual(V["dice_outcomes"], 36)
        self.assertEqual((V["dice_ways"][2], V["dice_ways"][7]), (1, 6))
        self.assertEqual(V["dice_p7"], [1, 6])                  # 6/36
        self.assertEqual(V["dice_7_vs_2"], 6)                   # six times more likely than 2
        self.assertEqual(V["dice_p11"], [1, 18])                # hands-on: 2/36

    def test_pastries(self):
        self.assertEqual(V["pastry_pmf"], {"0": 0.7, "1": 0.2, "2": 0.1})
        self.assertEqual(V["pastry_sum"], 1.0)


class Section2Expectation(unittest.TestCase):
    def test_pastries(self):
        self.assertAlmostEqual(V["pastry_mean"], 0.4)
        self.assertEqual(V["pastries_per_100"], 40.0)

    def test_raffle(self):
        a = V["raffle_A"]
        self.assertEqual(a["pmf"], {"398": [1, 500], "-2": [499, 500]})
        self.assertAlmostEqual(a["mean"], -1.2)
        self.assertEqual((V["raffle_raised"], V["raffle_kept"]), (1000, 600))
        self.assertAlmostEqual(V["raffle_kept"] / V["raffle_tickets"], -a["mean"])

    def test_die_hands_on(self):
        self.assertEqual(V["die_sum"], 21)
        self.assertEqual(V["die_mean"], 3.5)


class Section3RunningMean(unittest.TestCase):
    def test_runs(self):
        self.assertEqual([r["after_10"] for r in V["runs"]], [4.1, 3.6, 3.9])
        self.assertEqual([r["after_2000"] for r in V["runs"]], [3.539, 3.513, 3.49])
        self.assertEqual([round(r["after_2000"], 2) for r in V["runs"]], [3.54, 3.51, 3.49])
        self.assertAlmostEqual(V["run1_gap"]["after_10"], 0.6)        # hands-on
        self.assertAlmostEqual(V["run1_gap"]["after_2000"], 0.039)
        for r in V["runs"]:                                     # closer to 3.5 at the end than at 10 rolls
            self.assertLess(abs(r["after_2000"] - 3.5), abs(r["after_10"] - 3.5))


class Section4Variance(unittest.TestCase):
    def test_pastries(self):
        self.assertAlmostEqual(V["pastry_e2"], 0.6)
        self.assertAlmostEqual(V["pastry_var"], 0.44)
        self.assertEqual(round(V["pastry_sd"], 2), 0.66)

    def test_two_raffles(self):
        a, b = V["raffle_A"], V["raffle_B"]
        self.assertAlmostEqual(a["mean"], b["mean"])           # identical expectation
        self.assertEqual(b["pmf"], {"6": [1, 10], "-2": [9, 10]})
        self.assertAlmostEqual(a["var"], 319.36)
        self.assertAlmostEqual(b["var"], 5.76)                 # hands-on
        self.assertEqual((round(a["sd"], 2), round(b["sd"], 2)), (17.87, 2.4))


class Section5Roulette(unittest.TestCase):
    def test_per_bet(self):
        self.assertEqual(V["roulette_mean_frac"], [-1, 37])
        self.assertEqual(round(100 * V["roulette_mean"], 1), -2.7)   # cents per $1

    def test_expected_balance(self):
        self.assertEqual(round(V["roulette"]["1000"]["balance"], 2), -27.03)   # hands-on

    def test_chance_ahead(self):
        p = {n: V["roulette"][n]["p_ahead"] for n in ("100", "1000", "10000")}
        self.assertEqual(round(100 * p["100"]), 36)
        self.assertEqual(round(100 * p["1000"]), 19)
        self.assertEqual(round(100 * p["10000"], 1), 0.3)

    def test_doubling(self):
        m = V["martingale"]
        self.assertEqual((m["losses_covered"], m["lost_after"], m["next_stake"]), (9, 511, 512))
        self.assertEqual(m["lost_after"], sum(2 ** k for k in range(9)))
        self.assertEqual(round(m["one_in"], -2), 400)          # "once every 400 sessions"
        self.assertEqual(round(100 * m["mean"]), -27)          # cents per session


class Section6ShiftScale(unittest.TestCase):
    def test_revenue_and_bill(self):
        self.assertAlmostEqual(V["revenue_mean"], 0.8)
        self.assertEqual(round(V["revenue_sd"], 2), 1.33)
        self.assertAlmostEqual(V["bill_mean"], 3.8)
        self.assertAlmostEqual(V["bill_var"], 1.76)
        self.assertAlmostEqual(V["bill_var"], V["revenue_var"])      # the $3 coffee adds nothing

    def test_hands_on(self):
        self.assertAlmostEqual(V["hands_on_mean"], 1.2)
        self.assertAlmostEqual(V["hands_on_var"], 3.96)
        self.assertEqual(round(V["hands_on_sd"], 2), 1.99)

    def test_standardising(self):
        mu, sd = V["pastry_mean"], V["pastry_sd"]
        z = {(x - mu) / sd: p for x, p in ((0, 0.7), (1, 0.2), (2, 0.1))}
        self.assertAlmostEqual(sum(v * p for v, p in z.items()), V["z_mean"])
        self.assertAlmostEqual(sum(v * v * p for v, p in z.items()), V["z_var"])


class Section7Bernoulli(unittest.TestCase):
    def test_any_pastry(self):
        self.assertAlmostEqual(V["bern_p"], 0.3)
        self.assertAlmostEqual(V["bern_var"], 0.21)

    def test_largest_at_half(self):
        self.assertEqual(max(p * (1 - p) for p in [k / 100 for k in range(101)]), V["bern_max_var"])
        self.assertEqual(round(V["bern_girl_var"], 2), 0.25)          # hands-on: about a quarter


class Section8Binomial(unittest.TestCase):
    def test_pmf(self):
        self.assertAlmostEqual(sum(V["bin_pmf"]), 1.0)
        self.assertEqual(V["bin_mode"], 3)
        self.assertEqual(V["bin_comb3"], 120)
        self.assertEqual(round(V["bin_pmf"][3], 3), 0.267)
        self.assertEqual(round(V["bin_p3_parts"][1], 4), 0.0824)

    def test_moments(self):
        self.assertEqual((V["bin_mean"], round(V["bin_var"], 2), round(V["bin_sd"], 2)), (3.0, 2.1, 1.45))

    def test_tail_and_hands_on(self):
        self.assertEqual(round(V["bin_ge6"], 3), 0.047)
        self.assertEqual(round(V["bin_p0"], 3), 0.028)               # hands-on: nobody buys

    def test_ai_accuracy(self):
        self.assertEqual((V["test_mean"], round(V["test_sd"], 6)), (90.0, 3.0))
        self.assertEqual([round(x) for x in V["test_band"]], [87, 93])


class Section9Categorical(unittest.TestCase):
    def test_cups(self):
        self.assertAlmostEqual(sum(V["cups"].values()), 1.0)
        self.assertEqual(V["cups_expected"], {"small": 2.0, "medium": 5.0, "large": 3.0})
        self.assertEqual(V["cups_expected_hands_on"], {"small": 4.0, "medium": 10.0, "large": 6.0})


class Section10Poisson(unittest.TestCase):
    def test_window(self):
        self.assertEqual(round(V["pois_p0"], 3), 0.018)
        self.assertEqual(V["pois_empty_one_in"], 55)
        self.assertEqual(round(V["pois_rush"], 3), 0.051)
        self.assertEqual(round(V["day_rushes"]), 3)
        self.assertEqual(round(V["day_empty"]), 1)                    # hands-on

    def test_mean_equals_variance(self):
        pmf = V["pois_pmf"] + [C.poisson_pmf(k, V["lam"]) for k in range(13, 60)]
        m = sum(k * p for k, p in enumerate(pmf))
        self.assertTrue(isclose(m, V["lam"], rel_tol=1e-9))
        self.assertTrue(isclose(sum(k * k * p for k, p in enumerate(pmf)) - m * m, V["lam"], rel_tol=1e-9))

    def test_simulated_windows(self):
        sim = V["pois_sim"]
        self.assertEqual((sim["windows"], sim["arrivals"]), (3000, 11892))
        self.assertEqual((round(sim["mean"], 2), round(sim["var"], 2)), (3.96, 3.84))
        self.assertAlmostEqual(sum(sim["freq"]), 1.0, delta=0.001)

    def test_binomial_meets_poisson(self):
        self.assertEqual(V["p_second"], [1, 150])
        self.assertLess(V["bin_vs_pois"], 0.001)


class Section11Dirichlet(unittest.TestCase):
    def test_first_orders(self):
        self.assertEqual(V["first_shares"], {"small": 0.25, "medium": 0.5, "large": 0.25})

    def test_alphas(self):
        self.assertEqual(V["alphas"]["4"], [0.8, 2.0, 1.2])
        self.assertEqual(V["alphas"]["40"], [8.0, 20.0, 12.0])
        self.assertEqual(V["alpha_updated"], [0.8, 5.0, 1.2])          # hands-on
        self.assertEqual(round(V["alpha_updated_mean"][1], 2), 0.71)

    def test_draws_add_to_one(self):
        for draws in V["dirichlet_draws"].values():
            for d in draws:
                self.assertAlmostEqual(sum(d), 1.0, delta=0.0015)


class Sources(unittest.TestCase):
    def test_saved_json_is_fresh(self):
        saved = json.loads((C.OUT / "l03_numbers.json").read_text())
        self.assertEqual(saved, json.loads(json.dumps(C.compute())))

    def test_figure_script_agrees(self):
        fig = (C.OUT / "l03_figures.txt").read_text()
        r = V["runs"]
        for line in ("total outcomes=36  E[X]=7.000  Var(X)=5.8333",
                     *[f"Run {i + 1}: mean after 10 = {x['after_10']:.3f}, after 100 = {x['after_100']:.3f}, "
                       f"after 2000 = {x['after_2000']:.3f}" for i, x in enumerate(r)],
                     " 3 0.2668", "E=n*p=3.0  Var=n*p*(1-p)=2.10",
                     "observed mean = 3.964  observed variance = 3.837",
                     "n=   100  E[balance]=$    -2.70  P(ahead)=0.35535",
                     "n=  1000  E[balance]=$   -27.03  P(ahead)=0.18763",
                     "n= 10000  E[balance]=$  -270.27  P(ahead)=0.00333"):
            self.assertIn(line, fig)
        for s, draws in V["dirichlet_draws"].items():                  # the figure's own draws
            for d in draws:
                self.assertIn("[" + " ".join(f"{x:.3f}".rstrip("0").rstrip(".") if x else "0." for x in d), fig.replace("  ", " "))

    def test_figure_dice_and_variance(self):
        self.assertEqual(V["dice_mean"], 7.0)
        self.assertEqual(round(V["dice_var"], 4), 5.8333)
        self.assertEqual(round(sqrt(V["dice_var"]), 2), 2.42)


if __name__ == "__main__":
    unittest.main()
