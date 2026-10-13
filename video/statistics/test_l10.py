"""Unit tests for every Lecture 10 calculation.

Each test recomputes a value with capture_l10.compute() and checks it against what the slides
(statistics/lectures/lecture10_*.tex) and the narration (narration/lecture10.md) say. The saved
JSON the video reads must equal a fresh compute(), and the figure script must still print the
same numbers.
    uv run python -m unittest discover -s statistics -p 'test_l10.py'
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import capture_l10 as C  # noqa: E402

V = C.compute()


def r(x, n=2):
    return round(x, n)


class Section1WhyATestSet(unittest.TestCase):
    def test_degree9_train_and_test(self):                         # 1.4: 1.48 and 27.7
        f = V["fits"]["9"]
        self.assertEqual((r(f["train"]), r(f["test"], 1)), (1.48, 27.7))
        self.assertEqual((V["n_train"], V["n_test"]), (20, 40))

    def test_hands_on(self):                                       # 1.10: about nineteen times
        self.assertEqual(round(V["ratio_9"]), 19)


class Section3TwentyDays(unittest.TestCase):
    def test_three_fits(self):                                     # 3.3-3.5, slide "Real Event"
        f = V["fits"]
        self.assertEqual((r(f["1"]["train"]), r(f["1"]["test"])), (2.84, 3.33))
        self.assertEqual((r(f["3"]["train"]), r(f["3"]["test"])), (2.03, 2.65))
        self.assertEqual((r(f["9"]["train"]), r(f["9"]["test"])), (1.48, 27.74))

    def test_negative_sales_near_21(self):                         # 3.5: about minus two cups near 21 C
        m = V["deg9_min"]
        self.assertEqual((round(m["temp"]), round(m["sales"])), (21, -2))

    def test_hands_on_gaps(self):                                  # 3.10: 0.62 and 26.25
        self.assertEqual((r(V["gap"]["3"]), r(V["gap"]["9"])), (0.62, 26.25))


class Section4BiasVariance(unittest.TestCase):
    def test_truth(self):                                          # 4.4, 4.6: about 13 and 27 cups
        self.assertEqual((round(V["bv_truth"]["25"]), round(V["bv_truth"]["30"])), (13, 27))

    def test_straight_line(self):                                  # 4.5: 16 on average, 3 too many, sd under 1
        b = V["bv"]["25"]["1"]
        self.assertEqual((round(b["mean"]), round(b["bias"])), (16, 3))
        self.assertLess(b["sd"], 1)

    def test_degree9(self):                                        # 4.6: right on 13, sd 24 at 30 C
        b25, b30 = V["bv"]["25"]["9"], V["bv"]["30"]["9"]
        self.assertEqual(round(b25["mean"]), 13)
        self.assertLess(abs(b25["bias"]), 0.1)
        self.assertEqual(round(b30["sd"]), 24)
        self.assertGreater(b30["sd"], 20 * V["bv"]["30"]["1"]["sd"])

    def test_noise(self):                                          # 4.7
        self.assertEqual(V["noise_sd"], 2.5)

    def test_error_curve(self):                                    # 4.10-4.11, slide "Where does the test error turn"
        f = V["fits"]
        self.assertTrue(V["train_falls"])
        self.assertEqual((r(f["1"]["train"]), r(f["10"]["train"])), (2.84, 1.47))
        self.assertEqual(V["best_degree"], 3)
        self.assertEqual(r(f["7"]["test"], 1), 4.8)
        self.assertEqual([round(f[d]["test"]) for d in ("8", "9", "10")], [22, 28, 34])
        tests = [f[str(d)]["test"] for d in range(3, 8)]
        self.assertTrue(any(b < a for a, b in zip(tests, tests[1:])))   # "it wobbles on the way"

    def test_hands_on(self):                                       # 4.15: 0.15 above the noise
        self.assertEqual(r(V["above_noise_3"]), 0.15)


class Section5CrossValidation(unittest.TestCase):
    def test_folds(self):                                          # 5.5-5.7, slide "Five folds by hand"
        self.assertEqual([r(x) for x in V["folds"]], [2.60, 1.57, 2.19, 2.58, 3.66])
        self.assertEqual((r(V["cv_mean"]), r(V["cv_sd"])), (2.52, 0.76))
        self.assertEqual((V["fold_size"], V["times_trained"]), (4, 4))

    def test_cv_picks_degree3(self):                               # 5.8
        self.assertEqual(V["cv_best_degree"], 3)
        self.assertEqual(r(V["cv_by_degree"]["3"]), 2.52)
        self.assertEqual(r(V["cv_by_degree"]["10"]), 8.18)

    def test_hands_on(self):                                       # 5.12: 12.6, then 2.52
        self.assertEqual(V["fold_sum_shown"], 12.6)
        self.assertEqual(r(V["fold_sum_shown"] / 5), 2.52)


class Section6Interval(unittest.TestCase):
    def test_bootstrap(self):                                      # 6.6-6.7, slide "How precise"
        b = V["boot"]
        self.assertEqual(r(b["point"]), 2.65)
        self.assertEqual([r(x) for x in b["ci"]], [2.03, 3.24])
        self.assertGreater(b["width"], 1.0)                        # "more than a cup wide"

    def test_left_out(self):                                       # 6.4: fourteen and a half of forty
        self.assertEqual(round(2 * V["boot"]["left_out_mean"]) / 2, 14.5)

    def test_two_sigma_check(self):                                # 6.8: sd 0.31, 2.03 to 3.26
        b = V["boot"]
        self.assertEqual(r(b["sd"]), 0.31)
        self.assertEqual([r(x) for x in b["two_sd"]], [2.03, 3.26])

    def test_reading(self):                                        # 6.9: "about 2 to 3.2"
        self.assertEqual((round(V["boot"]["ci"][0]), r(V["boot"]["ci"][1], 1)), (2, 3.2))

    def test_lecture3_recap(self):                                 # 6.10: ninety right, sd three
        self.assertEqual((V["l3_recap"]["mean"], r(V["l3_recap"]["sd"], 6)), (90.0, 3.0))

    def test_accuracy_se(self):                                    # 6.11-6.13, slide "0.3 % is not a difference"
        a1, a2 = V["accuracy_se"]
        self.assertEqual(round(a1["se"], 4), 0.0095)
        self.assertEqual(r(100 * a1["half"], 1), 1.9)
        self.assertEqual(r(100 * a2["half"], 1), 0.6)
        self.assertEqual(r(V["rival_gap_points"], 1), 0.3)
        self.assertLess(V["rival_gap_points"], 100 * a1["half"])

    def test_hands_on(self):                                       # 6.16: about 0.9 points, half of 1.9
        self.assertEqual(r(100 * V["accuracy_task"]["half"], 1), 0.9)
        self.assertAlmostEqual(V["accuracy_task"]["half"], V["accuracy_se"][0]["half"] / 2)


class Section7NullAndP(unittest.TestCase):
    def test_menus(self):                                          # 7.2-7.3
        m = V["menu"]
        self.assertEqual((m["A"][:2], m["B"][:2]), ([21, 60], [30, 60]))
        self.assertEqual((m["A"][2], m["B"][2]), (0.35, 0.5))
        self.assertEqual(round(100 * m["gap"]), 15)
        self.assertEqual(m["customers"], 120)

    def test_hands_on(self):                                       # 7.12: 51 of 120, 42.5 %
        self.assertEqual(V["menu"]["buyers"], 51)
        self.assertEqual(100 * V["menu"]["pooled"], 42.5)


class Section8Permutation(unittest.TestCase):
    def test_p_value(self):                                        # 8.5-8.6, slide "Two menu layouts"
        p = V["perm"]
        self.assertEqual((p["shuffles"], p["as_extreme"]), (20_000, 2756))
        self.assertEqual(r(100 * p["p"], 1), 13.8)
        self.assertEqual(r(p["p"]), 0.14)

    def test_spread_as_standard_error(self):                       # 8.7: sd about 0.09, 1.7 of them
        p = V["perm"]
        self.assertEqual(r(p["sd"]), 0.09)
        self.assertEqual(r(p["gap_in_sd"], 1), 1.7)
        self.assertLess(p["gap_in_sd"], 2)
        self.assertAlmostEqual(p["sd"], V["menu_se"], delta=0.002)   # the shuffle's spread is the formula's SE

    def test_one_afternoon_in_seven(self):                         # 8.8
        self.assertEqual(round(V["perm"]["one_in"]), 7)

    def test_ninety_customers(self):                               # 8.9, 8.16
        self.assertEqual(V["n_needed"], 90)
        self.assertEqual(r(V["se_shrink_needed"]), 1.22)
        self.assertEqual(r(V["z_at_needed"]), 2.04)
        self.assertGreater(V["z_at_needed"], 1.96)
        self.assertEqual(r(V["menu_z"], 1), 1.7)                   # 8.15: "about 1.7 standard errors"

    def test_big_sample(self):                                     # 8.12: 200,000 per menu, 0.4 points, p about 0.01
        b = V["big"]
        self.assertEqual((b["n"], 100 * b["gap"]), (200_000, 0.4))
        self.assertEqual(r(b["p"]), 0.01)
        self.assertLess(b["p"], 0.05)


class Section9Errors(unittest.TestCase):
    def test_lecture2_table(self):                                 # 9.3, 9.5: 495 of 595, 83 %
        s = V["screen"]
        self.assertEqual((s["tested"], s["false_pos"], s["positives"]), (10_000, 495, 595))
        self.assertEqual(round(100 * s["false_share"]), 83)
        l02 = json.loads((C.OUT / "l02_numbers.json").read_text())["screen"]
        self.assertEqual((l02["tested"], l02["false_pos"], l02["positives"]), (10_000, 495, 595))

    def test_many_tests(self):                                     # 9.8, slide table
        self.assertEqual([r(V["many"][m]) for m in ("1", "10", "20", "50")], [0.05, 0.40, 0.64, 0.92])
        self.assertEqual(V["expected_false_50"], 2.5)              # 9.9

    def test_hands_on(self):                                       # 9.13: 0.95^10 about 0.6, answer 0.4
        self.assertEqual(r(V["no_false_10"], 1), 0.6)
        self.assertEqual(r(V["many"]["10"], 1), 0.4)


class Section10Calibration(unittest.TestCase):
    def test_everyday_forecasters(self):                           # 10.2
        self.assertEqual(V["rain"], {"said": 0.7, "days": 100, "honest": 70, "other": 45})

    def test_reliability(self):                                    # 10.6-10.8, slide "Two forecasters"
        top, bottom = V["cal"][-1], V["cal"][0]
        self.assertEqual(V["per_bucket"], 400)
        self.assertEqual(round(top["honest"], 3), 0.958)
        self.assertEqual(r(top["over"]), 0.76)
        self.assertEqual(r(bottom["over"]), 0.22)
        self.assertEqual((r(V["cal_gap"]["honest"]), r(V["cal_gap"]["over"])), (0.01, 0.12))

    def test_counts(self):                                         # 10.9, 10.16
        c = V["cal_95"]
        self.assertEqual((c["claimed"], c["claimed_misses"]), (380, 20))
        self.assertEqual((c["honest"], c["over"], c["over_misses"]), (383, 305, 95))
        self.assertEqual(c["claimed"] - c["over"], 75)

    def test_softmax_temperature(self):                            # 10.13: 0.88, then 0.73
        s = V["softmax"]
        self.assertEqual((r(s["p"]), r(s["p_T"]), s["T"]), (0.88, 0.73, 2.0))

    def test_module_map(self):                                     # 10.18-10.20, slide "Where Module 0 goes next"
        self.assertEqual([tuple(x[i] for i in (0, 2, 3)) for x in V["module_map"]],
                         [(2, 3, 6), (5, 1, 13), (6, 1, 12), (7, 1, 5), (9, 1, 2), (10, 1, 14)])


class Sources(unittest.TestCase):
    def test_saved_json_is_fresh(self):
        saved = json.loads((C.OUT / "l10_numbers.json").read_text())
        self.assertEqual(saved, json.loads(json.dumps(C.compute())))

    def test_figure_script_agrees(self):
        fig = (C.OUT / "l10_figures.txt").read_text()
        for line in ("degree 1: train RMSE=2.84  test RMSE=3.33",
                     "degree 3: train RMSE=2.03  test RMSE=2.65",
                     "degree 9: train RMSE=1.48  test RMSE=27.74",
                     "best test RMSE at degree 3: 2.65",
                     "degree 10: train 1.47  test 33.87",
                     "95% bootstrap interval = [2.03, 3.24]  width 1.20",
                     "permutation p-value (two-sided) = 0.1378",
                     "a gap of 0.15 needs about 90 customers per menu",
                     "mean gap  honest 0.011   overconfident 0.121",
                     "at a stated 0.95: honest 0.958, overconfident 0.762",
                     "5-fold RMSE per fold: [2.6, 1.57, 2.19, 2.58, 3.66]",
                     "5-fold mean 2.52  sd 0.76",
                     "accuracy 0.900 on n=1000: SE = 0.0095",
                     "50 independent tests at 0.05: P(at least one false alarm) = 0.923"):
            self.assertIn(line, fig)

    def test_regenerated_days_match_script(self):
        fig = (C.OUT / "l10_figures.txt").read_text()
        (tt, yt), (te, ye) = C.days()
        self.assertIn(f"Training days: n=20  temp {tt.min():.1f}-{tt.max():.1f}  sales {yt.min():.1f}-{yt.max():.1f}",
                      fig)
        self.assertIn(f"Test days:     n=40  temp {te.min():.1f}-{te.max():.1f}  sales {ye.min():.1f}-{ye.max():.1f}",
                      fig)


if __name__ == "__main__":
    unittest.main()
