"""Unit tests for every Lecture 6 calculation.

Each test recomputes a value with capture_l06.compute() and checks it against what the slides
(statistics/lectures/lecture06_*.tex) and the narration (narration/lecture06.md) say. The saved
JSON the video reads must equal a fresh compute(), and the figure script must still print the
same numbers.
    uv run python -m unittest discover -s statistics -p 'test_l06.py'
"""
import json
import sys
import unittest
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import capture_l06 as C  # noqa: E402

V = C.compute()


class Section1WhyAPrior(unittest.TestCase):
    def test_monday_late(self):
        self.assertFalse(V["day1_on_time"])
        self.assertEqual(V["mle_day1"], 0.0)                         # "never on time"
        self.assertEqual(V["mle_day1_task"], 1.0)                    # hands-on: "always on time"

    def test_prior(self):
        self.assertEqual((V["prior"], V["prior_n"]), ([8, 2], 10))
        self.assertAlmostEqual(V["prior_mean"], 0.8)


class Section2Update(unittest.TestCase):
    def test_one_late_bus(self):
        o = V["one_late"]
        self.assertEqual((o["a"], o["b"]), (8, 3))
        self.assertAlmostEqual(o["mean"], 8 / 11)
        self.assertEqual(round(o["mean"], 3), 0.727)

    def test_hands_on(self):
        o = V["one_on_time"]
        self.assertEqual((o["a"], o["b"]), (9, 2))
        self.assertEqual(round(o["mean"], 3), 0.818)


class Section3Month(unittest.TestCase):
    def test_table(self):
        b = V["bus"]
        self.assertEqual([b[n]["on_time"] for n in ("1", "10", "30", "100")], [0, 6, 22, 68])
        self.assertEqual([round(b[n]["mle"], 3) for n in ("1", "10", "30", "100")], [0.0, 0.6, 0.733, 0.68])
        self.assertEqual([round(b[n]["mean"], 3) for n in ("1", "10", "30", "100")], [0.727, 0.7, 0.75, 0.691])

    def test_hands_on(self):
        r = V["bus"]["10"]
        self.assertEqual((r["a"], r["b"]), (14, 6))
        self.assertAlmostEqual(r["mean"], 14 / 20)

    def test_flat_prior_is_mle(self):
        self.assertEqual(V["three"]["flat"]["prior"], [1, 1])


class Section4CredibleInterval(unittest.TestCase):
    def test_intervals(self):
        self.assertEqual([round(x, 3) for x in V["bus"]["10"]["ci"]], [0.488, 0.874])
        self.assertEqual([round(x, 3) for x in V["bus"]["100"]["ci"]], [0.602, 0.773])
        self.assertEqual(round(V["bus"]["10"]["ci_width"], 2), 0.39)
        self.assertEqual(round(V["bus"]["100"]["ci_width"], 2), 0.17)   # hands-on: 0.773 - 0.602

    def test_shrink(self):
        self.assertEqual(round(V["ci_shrink"], 1), 2.3)
        self.assertGreater(V["ci_shrink"], 2)                            # "narrowed by more than half"


class Section5ThreePriors(unittest.TestCase):
    def test_posteriors(self):
        t = V["three"]
        self.assertEqual([t[k]["worth"] for k in ("flat", "ours", "stubborn")], [2, 10, 100])
        self.assertEqual([round(t[k]["post"]["mean"], 3) for k in ("flat", "ours", "stubborn")], [0.676, 0.691, 0.74])

    def test_hands_on(self):
        s = V["three"]["stubborn"]["post"]
        self.assertEqual((s["a"], s["b"]), (148, 52))
        self.assertAlmostEqual(s["mean"], 148 / 200)
        self.assertAlmostEqual(s["mean"], (V["prior_mean"] + V["bus"]["100"]["mle"]) / 2)   # "moved halfway"


class Section6PointEstimates(unittest.TestCase):
    def test_three_answers(self):
        r = V["bus"]["10"]
        self.assertEqual((round(r["mle"], 3), round(r["mean"], 3), round(r["map"], 3)), (0.6, 0.7, 0.722))
        self.assertAlmostEqual(r["map"], 13 / 18)
        self.assertGreater(r["map"], r["mean"])                          # leans left: MAP above the mean
        a, b = r["a"], r["b"]
        self.assertLess(2 * (b - a) * sqrt(a + b + 1) / ((a + b + 2) * sqrt(a * b)), 0)   # tail stretches left

    def test_hands_on(self):
        r = V["bus"]["100"]
        self.assertAlmostEqual(r["map"], 75 / 108)
        self.assertEqual(round(r["map"], 3), 0.694)


class Section7Counting(unittest.TestCase):
    def test_thirty(self):
        self.assertEqual(V["count30"], {"a": 30, "b": 10, "mean": 0.75})

    def test_predictive_is_mean(self):
        self.assertEqual(round(V["predictive_bus"], 3), 0.691)
        r = V["bus"]["100"]
        self.assertEqual((r["a"], r["b"]), (76, 34))                     # hands-on


class Section8Dirichlet(unittest.TestCase):
    def test_update(self):
        self.assertEqual(V["dir_post"], [7.8, 23, 13.2])
        self.assertAlmostEqual(V["dir_post_n"], 44)
        self.assertAlmostEqual(V["dir_prior_n"], 4)
        self.assertEqual(V["dir_n"], 40)
        self.assertEqual([round(s, 3) for s in V["dir_shares"]], [0.177, 0.523, 0.3])

    def test_hands_on(self):
        self.assertEqual(V["dir_task"], [7.8, 23, 14.2])
        self.assertEqual(round(V["dir_task_large"], 2), 0.32)


class Section9Walk(unittest.TestCase):
    def test_update(self):
        w = V["walk"]
        self.assertEqual(w["xbar"], 15)
        self.assertAlmostEqual(w["prec_prior"], 1 / 9)
        self.assertAlmostEqual(w["prec_data"], 4 / 9)
        self.assertAlmostEqual(w["post_mu"], 14.4)
        self.assertAlmostEqual(w["post_var"], 1.8)
        self.assertEqual(round(w["post_sd"], 2), 1.34)

    def test_worth_one_timing(self):
        w = V["walk"]
        self.assertAlmostEqual(w["prior_worth"], 1)
        self.assertAlmostEqual(w["by_counts"], 72 / 5)

    def test_predictive(self):
        self.assertAlmostEqual(V["walk"]["pred_sd"], sqrt(10.8))
        self.assertEqual(round(V["walk"]["pred_sd"], 2), 3.29)

    def test_hands_on(self):
        self.assertAlmostEqual(V["walk_task"]["tau0"] ** 2, 2.25)
        self.assertAlmostEqual(V["walk_task"]["prior_worth"], 4)
        self.assertAlmostEqual(V["walk_task"]["post_mu"], 13.5)


class Section10Penalty(unittest.TestCase):
    def test_coefficients(self):
        self.assertEqual(V["penalty"], {"2.0": 0.125, "1.0": 0.5, "0.5": 2.0})
        self.assertEqual(V["penalty_ratio"], 16)

    def test_hands_on(self):
        self.assertEqual(V["lambda_task"]["lambda"], 4)


class Sources(unittest.TestCase):
    def test_saved_json_is_fresh(self):
        saved = json.loads((C.OUT / "l06_numbers.json").read_text())
        self.assertEqual(saved, json.loads(json.dumps(C.compute())))

    def test_figure_script_agrees(self):
        fig = (C.OUT / "l06_figures.txt").read_text()
        for line in ("day 1 was LATE",
                     "posterior Beta(69,33) mean=0.6765", "posterior Beta(76,34) mean=0.6909",
                     "posterior Beta(148,52) mean=0.7400",
                     "MLE              0.6000", "posterior mean   0.7000", "MAP              0.7222",
                     "95% credible interval [0.488, 0.874]",
                     "posterior mean=14.4000  sd=1.3416",
                     "tau=2.0  penalty coefficient 1/(2 tau^2) = 0.125",
                     "tau=0.5  penalty coefficient 1/(2 tau^2) = 2.000"):
            self.assertIn(line, fig)


if __name__ == "__main__":
    unittest.main()
