"""Unit tests for every Lecture 7 calculation.

Each test recomputes a value with capture_l07.compute() and checks it against what the slides
(statistics/lectures/lecture07_*.tex) and the narration (narration/lecture07.md) say. The saved
JSON the video reads must equal a fresh compute(), and the figure script must still print the
same numbers.
    uv run python -m unittest discover -s statistics -p 'test_l07.py'
"""
import json
import sys
import unittest
from math import log2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import capture_l07 as C  # noqa: E402

V = C.compute()
F = V["forecasters"]


class Section1WhyEntropy(unittest.TestCase):
    def test_four_equal_need_two_questions(self):              # 1.5, pause 1.9
        self.assertEqual(V["uniform_questions"], 2.0)


class Section2QuestionTree(unittest.TestCase):
    def test_days_and_shares(self):                            # 2.1, 2.2
        self.assertEqual((V["days"], V["n_days"]), ([180, 90, 45, 45], 360))
        self.assertEqual(V["p"], [0.5, 0.25, 0.125, 0.125])

    def test_tree(self):                                       # 2.3-2.5
        self.assertEqual(V["questions"], [1, 2, 3, 3])
        self.assertEqual(V["avg_questions"], 1.75)

    def test_counted_over_the_days(self):                      # 2.6
        self.assertEqual(V["questions_360"], 630)
        self.assertEqual(V["questions_360"] / V["n_days"], 1.75)

    def test_reversed_tree(self):                              # pause 2.10
        self.assertEqual(V["bad_questions"], [3, 3, 2, 1])     # sunny, cloudy, rain, storm
        self.assertEqual(V["avg_bad"], 2.625)
        self.assertEqual(V["bad_extra"], 0.875)
        self.assertLess(V["bad_extra"], 1)                     # "almost a whole question more"


class Section3Entropy(unittest.TestCase):
    def test_surprise(self):                                   # 3.1-3.3
        self.assertEqual(V["surprise"], [1.0, 2.0, 3.0, 3.0])
        self.assertEqual(V["log2_8"], 3.0)

    def test_surprises_add(self):                              # 3.4
        self.assertEqual(V["sunny_then_storm"], {"prob": 1 / 16, "bits": 4.0})

    def test_entropy_is_the_tree_average(self):                # 3.6
        self.assertEqual(V["H"], 1.75)
        self.assertEqual(V["H"], V["avg_questions"])

    def test_extremes(self):                                   # 3.7
        self.assertEqual(V["H_certain"], 0.0)
        self.assertEqual(V["H_uniform"], 2.0)

    def test_climate_is_worth(self):                           # 3.9
        self.assertEqual(V["climate_worth"], 0.25)
        self.assertEqual(V["climate_worth_360"], 90)

    def test_hands_on(self):                                   # pause 3.12
        self.assertEqual(V["H_three"], 1.5)


class Section4BinaryEntropy(unittest.TestCase):
    def test_peak(self):                                       # 4.2
        self.assertEqual(V["binary"]["0.5"], 1.0)

    def test_confidence_either_way(self):                      # 4.3
        self.assertEqual(round(V["binary"]["0.11"], 2), 0.50)
        self.assertEqual(round(V["binary"]["0.89"], 2), 0.50)
        self.assertAlmostEqual(V["binary"]["0.11"], V["binary"]["0.89"])

    def test_steep_ends(self):                                 # 4.4
        b = V["binary"]
        self.assertEqual(round(b["0.4"], 2), 0.97)
        self.assertEqual(round(V["gain_05_04"], 2), 0.03)
        self.assertEqual((round(b["0.1"], 2), round(b["0.01"], 2)), (0.47, 0.08))
        self.assertEqual(round(V["gain_01_001"], 2), 0.39)

    def test_hands_on(self):                                   # pause 4.8
        self.assertEqual(round(V["dry_surprise_quarter"], 3), 0.415)
        self.assertEqual(round(V["binary"]["0.25"], 2), 0.81)
        self.assertAlmostEqual(0.25 * 2 + 0.75 * V["dry_surprise_quarter"], V["binary"]["0.25"])


class Section5CrossEntropy(unittest.TestCase):
    def test_uniform_forecaster(self):                         # 5.5
        self.assertEqual(F["uniform"]["cross"], 2.0)

    def test_never_a_bargain(self):                            # 5.6
        for f in F.values():
            self.assertGreaterEqual(f["cross"] + 1e-12, V["H"])
        self.assertEqual(F["climate"]["cross"], V["H"])

    def test_nats(self):                                       # 5.10
        self.assertEqual(round(V["ln2"], 3), 0.693)
        self.assertEqual(round(V["H_nats"], 2), 1.21)

    def test_hands_on(self):                                   # pause 5.13
        self.assertEqual(round(V["one_example"]["bits"], 3), 0.152)
        self.assertEqual(round(V["one_example"]["nats"], 3), 0.105)


class Section6ThreeForecasters(unittest.TestCase):
    def test_bills(self):                                      # 6.1-6.5
        self.assertEqual([round(F[k]["cross"], 2) for k in ("climate", "uniform", "sunny")], [1.75, 2.0, 2.57])
        self.assertEqual([round(F[k]["kl"], 2) for k in ("climate", "uniform", "sunny")], [0.0, 0.25, 0.82])

    def test_over_the_days(self):                              # 6.4
        self.assertEqual((F["climate"]["cross_360"], F["uniform"]["cross_360"]), (630, 720))
        self.assertEqual(V["waste_360_uniform"], V["climate_worth_360"])

    def test_storm_day(self):                                  # 6.6
        self.assertEqual(round(F["sunny"]["surprise"][3], 1), 6.6)
        self.assertEqual(F["climate"]["surprise"][3], 3.0)

    def test_floor_on_noisy_labels(self):                      # 6.8
        self.assertEqual(round(V["floor_noisy"], 2), 0.88)
        self.assertEqual(V["floor_noisy"], V["binary"]["0.7"])

    def test_hands_on(self):                                   # pause 6.11
        s = F["sunny"]["surprise"]
        self.assertEqual(round(s[0], 3), 0.152)
        self.assertLess(s[0], F["climate"]["surprise"][0])     # wins on a sunny day
        self.assertTrue(4 < s[1] < s[2] < s[3] and 6 < s[3] < 7)   # "from over four to over six bits"
        self.assertEqual([round(x, 1) for x in s[1:]], [4.3, 4.6, 6.6])


class Section7KL(unittest.TestCase):
    def test_kl_is_the_cap(self):                              # 7.1-7.4
        for f in F.values():
            self.assertAlmostEqual(f["kl"], f["cross"] - V["H"])
        p, q = V["p"], F["sunny"]["q"]
        self.assertAlmostEqual(F["sunny"]["kl"], sum(a * log2(a / b) for a, b in zip(p, q)))

    def test_hands_on(self):                                   # pause 7.10
        self.assertEqual(V["swap"]["cross"], 1.875)
        self.assertEqual(V["swap"]["kl"], 0.125)


class Section8Mornings(unittest.TestCase):
    def test_posteriors_match_lecture_6(self):                 # 8.2
        b = V["bus_kl"]
        self.assertEqual([b[n]["post"] for n in ("0", "10", "30", "100")], [[8, 2], [14, 6], [30, 10], [76, 34]])
        self.assertEqual(V["bus_prior_worth"], 10)

    def test_learning_measured(self):                          # 8.4, 8.5
        b = V["bus_kl"]
        self.assertEqual(b["0"]["kl"], 0.0)
        self.assertEqual(round(b["10"]["kl"], 2), 0.66)
        self.assertEqual(round(b["100"]["kl"], 2), 1.76)
        self.assertEqual(round(b["30"]["kl"], 2), 0.69)
        self.assertTrue(b["10"]["kl"] < b["30"]["kl"] < b["10"]["kl"] + 0.05)   # "barely more than after ten"

    def test_jagged(self):                                     # 8.5
        path = V["bus_kl_path"]
        self.assertTrue(any(b < a for a, b in zip(path, path[1:])))

    def test_hands_on(self):                                   # pause 8.10
        self.assertEqual(round(V["bus_kl_late_10_100"], 1), 1.1)


class Section9NotADistance(unittest.TestCase):
    def test_asymmetric_pair(self):                            # 9.2
        self.assertEqual((round(V["kl_p_sunny"], 2), round(V["kl_sunny_p"], 2)), (0.82, 0.54))

    def test_hands_on_equal_pair(self):                        # pause 9.9
        self.assertAlmostEqual(V["kl_p_uniform"], 0.25)
        self.assertAlmostEqual(V["kl_uniform_p"], 0.25)


class Section10MutualInformation(unittest.TestCase):
    def test_wet(self):                                        # 10.6
        self.assertEqual(V["p_wet"], 0.25)
        self.assertEqual(round(V["H_wet"], 2), 0.81)
        self.assertEqual(V["H_wet"], V["binary"]["0.25"])

    def test_grey_sky(self):                                   # 10.7, 10.8
        g = V["mi"]["grey"]
        self.assertEqual((round(g["joint_wet_yes"], 2), round(g["p_yes"], 2)), (0.2, 0.35))
        self.assertEqual((round(g["wet_if_yes"], 2), round(g["wet_if_no"], 2)), (0.57, 0.08))
        self.assertEqual(round(g["H_cond"], 2), 0.60)
        self.assertEqual(round(g["I"], 3), 0.212)
        self.assertEqual(round(4 * V["mi_grey_share"]), 1)      # "about a quarter"

    def test_symmetric(self):                                  # 10.9
        for m in V["mi"].values():
            self.assertAlmostEqual(m["I"], m["I_reverse"])

    def test_mi_is_a_kl(self):                                 # 10.10
        g = V["mi"]["grey"]
        self.assertAlmostEqual(g["I"], g["I_as_kl"])
        self.assertEqual(round(g["product_wet_yes"], 2), 0.09)

    def test_hands_on(self):                                   # pause 10.13
        e = V["mi"]["even"]
        self.assertEqual((e["wet_if_yes"], e["wet_if_no"]), (0.25, 0.25))
        self.assertAlmostEqual(e["I"], 0.0)
        self.assertEqual(e["joint_wet_yes"], 0.125)


class Section11WhichQuestion(unittest.TestCase):
    def test_ranking(self):                                    # 11.2
        m = V["mi"]
        self.assertEqual([round(m[k]["I"], 3) for k in ("grey", "wind", "even")], [0.212, 0.022, 0.0])
        self.assertEqual(round(m["wind"]["wet_if_yes"], 2), 0.33)
        self.assertEqual(round(V["mi_grey_over_wind"]), 10)   # "about ten times less useful"

    def test_hands_on(self):                                   # pause 11.9
        w = V["mi"]["wind"]
        self.assertEqual(round(w["H_cond"], 2), 0.79)
        self.assertEqual(round(V["H_wet"] - w["H_cond"], 2), 0.02)


class Sources(unittest.TestCase):
    def test_saved_json_is_fresh(self):
        saved = json.loads((C.OUT / "l07_numbers.json").read_text())
        self.assertEqual(saved, json.loads(json.dumps(C.compute())))

    def test_figure_script_agrees(self):
        fig = (C.OUT / "l07_figures.txt").read_text()
        for line in ("H(p) = 1.7500 bits   H(uniform over 4) = 2.0000 bits",
                     "H(0.11) = 0.4999 bits", "H(0.7) = 0.8813 bits",
                     "always says sunny 2.567448  0.817448",
                     "posterior Beta(14,6)  KL=0.664 bits", "posterior Beta(76,34)  KL=1.760 bits",
                     "posterior Beta(30,10)  KL=0.690 bits",
                     "P(wet) = 0.250   H(wet) = 0.8113 bits",
                     "KL(sunny-ish ‖ p) = 0.5449 bits",
                     "waste vs uniform over 360 days: 90 bits",
                     "H(p) in nats = 1.2130"):
            self.assertIn(line, fig)
        for q, i in (("sky is grey at 7am", "0.212140"), ("wind from the west", "0.021824")):
            row = next(r for r in fig.splitlines() if q in r)
            self.assertTrue(row.rstrip().endswith(i), row)


if __name__ == "__main__":
    unittest.main()
