"""Unit tests for every Lecture 9 calculation.

Each test recomputes a value with capture_l09.compute() and checks it against what the slides
(statistics/lectures/lecture09_*.tex) and the narration (narration/lecture09.md) say. The saved
JSON the video reads must equal a fresh compute(), and the figure script must still print the
same numbers.
    uv run python -m unittest discover -s statistics -p 'test_l09.py'
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import capture_l09 as C  # noqa: E402

V = C.compute()


class Section1WhyCorrelation(unittest.TestCase):
    def test_lecture4_numbers(self):
        self.assertEqual(V["n"], 300)
        self.assertEqual(round(V["cov"], 1), 49.6)
        self.assertEqual((round(V["t_sd"], 2), round(V["c_sd"], 2)), (5.65, 11.33))
        self.assertEqual(round(V["r"], 2), 0.77)
        self.assertAlmostEqual(V["r_from_cov"], V["r"])
        self.assertEqual(round(V["r_from_slide"], 2), 0.77)               # 49.6 / (5.65 × 11.33)

    def test_fahrenheit(self):
        self.assertEqual(round(V["cov_f"], 1), 89.2)                      # spoken; the slide's 89.3 is 49.6 × 1.8
        self.assertEqual(round(V["cov_f_slide"], 1), 89.3)
        self.assertAlmostEqual(V["r_f"], V["r"])                          # hands-on: units cancel


class Section2Quadrants(unittest.TestCase):
    def test_counts(self):
        q = V["quadrants"]
        self.assertEqual((q["warm_busy"], q["cold_quiet"], q["cold_busy"], q["warm_quiet"]), (114, 126, 27, 33))
        self.assertEqual(V["positive_products"], 240)
        self.assertEqual(sum(q.values()), 300)

    def test_mean_point(self):
        self.assertEqual((round(V["t_mean"], 1), round(V["c_mean"], 1)), (21.8, 39.5))

    def test_z_products(self):
        self.assertAlmostEqual(V["z_product_mean"], V["r"])

    def test_hands_on(self):
        h = V["cold_busy_task"]
        self.assertLess(h["dt"], 0)
        self.assertGreater(h["dc"], 0)
        self.assertEqual(round(h["product"], 1), -71.6)


class Section3LeastSquares(unittest.TestCase):
    def test_line(self):
        self.assertEqual(round(V["slope"], 4), 1.5548)
        self.assertEqual(round(V["slope"], 2), 1.55)
        self.assertEqual(round(V["intercept"], 1), 5.6)
        self.assertEqual(round(V["slope_slide"], 2), 1.55)
        self.assertEqual(round(V["intercept_slide"], 1), 5.6)

    def test_through_mean_point(self):
        self.assertAlmostEqual(V["pred_at_mean"], V["c_mean"])

    def test_three_degrees(self):
        self.assertEqual(round(V["warmer_cups"], 1), 4.7)
        self.assertEqual(round(V["warmer_cups"]), 5)

    def test_slope_from_r(self):
        self.assertAlmostEqual(V["slope_from_r"], V["slope"])
        self.assertEqual(round(V["one_sd_warmer_cups"], 1), 8.8)
        self.assertAlmostEqual(V["one_sd_warmer_in_sd"], V["r"])

    def test_hands_on(self):
        self.assertEqual(round(V["pred_25"], 1), 44.4)
        self.assertEqual(round(V["pred_25_rounded_line"]), 44)


class Section4Residuals(unittest.TestCase):
    def test_example_day(self):
        d = V["example_day"]
        self.assertEqual(round(d["t"], 1), 25.0)
        self.assertEqual((round(d["cups"], 1), round(d["cups"])), (31.9, 32))
        self.assertEqual(round(d["pred"], 1), 44.4)
        self.assertEqual(round(d["resid"], 1), -12.5)
        self.assertAlmostEqual(d["cups"] - d["pred"], d["resid"])

    def test_residual_properties(self):
        self.assertAlmostEqual(V["resid_mean"], 0.0, places=10)
        self.assertAlmostEqual(V["resid_t_corr"], 0.0, places=10)
        self.assertEqual(round(V["resid_sd"], 1), 7.2)

    def test_hands_on(self):
        self.assertEqual(round(V["task_resid"], 1), -9.4)


class Section5RSquared(unittest.TestCase):
    def test_sums(self):
        self.assertEqual(round(V["ss_tot"]), 38385)
        self.assertEqual(round(V["ss_res"]), 15348)
        self.assertEqual(round(V["r2"], 2), 0.60)
        self.assertAlmostEqual(V["r2"], V["r_squared"])
        self.assertEqual(round(V["r"], 4), 0.7747)

    def test_through_variances(self):
        self.assertEqual(round(V["resid_var"], 1), 51.5)
        self.assertEqual(round(V["c_var"], 1), 128.4)
        self.assertEqual(round(V["resid_var_share"], 1), 0.4)
        self.assertEqual(round(1 - V["resid_var_share"], 2), 0.60)

    def test_hands_on(self):
        self.assertAlmostEqual(V["task_r2"], 0.25)


class Section6MaximumLikelihood(unittest.TestCase):
    def test_band(self):
        self.assertEqual(round(V["two_sigma"], 1), 14.4)
        self.assertEqual([round(x, 1) for x in V["band_25"]], [30.1, 58.8])
        self.assertEqual(round(100 * V["within_two_sigma"], 1), 95.7)


class Section7WhatRMisses(unittest.TestCase):
    def test_total_drinks(self):
        self.assertEqual(round(V["total_r"], 2), -0.06)
        self.assertEqual(round(V["total_r2_line"], 2), 0.00)
        self.assertEqual(round(V["total_r2_curve"], 2), 0.55)
        x, y = V["total_curve_bottom"]
        self.assertEqual((round(x), round(y)), (22, 55))

    def test_halves(self):
        self.assertEqual(round(V["total_r_cold"], 2), -0.68)
        self.assertEqual(round(V["total_r_warm"], 2), 0.69)
        self.assertEqual(V["n_cold"] + V["n_warm"], 300)

    def test_anscombe(self):
        A = V["anscombe"]
        for s in A.values():
            self.assertAlmostEqual(s["r"], 0.816, delta=0.001)          # "about 0.816" (set IV: 0.8165)
            self.assertEqual(round(s["r2"], 2), 0.67)
            self.assertEqual((round(s["intercept"], 2), round(s["slope"], 2)), (3.0, 0.5))
        # set II: an arc -- negative at both ends, positive in the middle
        signs = A["II"]["resid_signs"]
        self.assertEqual(signs[:2] + signs[-2:], [-1, -1, -1, -1])
        self.assertTrue(all(v == 1 for v in signs[2:-2]))
        # set III: one residual stands apart
        self.assertEqual(round(A["III"]["max_resid"], 2), 3.24)
        self.assertEqual(A["III"]["max_resid_point"], [13.0, 12.74])
        # set IV: the far point decides the line and has residual 0
        self.assertAlmostEqual(A["IV"]["resid_far_x"], 0.0, places=10)

    def test_matches_lecture1(self):
        l01 = json.loads((C.OUT / "l01_numbers.json").read_text())["anscombe"]
        for name, s in V["anscombe"].items():
            self.assertAlmostEqual(s["r"], l01[name]["corr"])


class Section9Matrices(unittest.TestCase):
    def test_pairs(self):
        self.assertEqual(V["pairs"], {"3": 3, "5": 10, "10": 45, "100": 4950, "1000": 499500})

    def test_covariance_matrix(self):
        self.assertEqual([[round(v, 1) for v in row] for row in V["cov3"]],
                         [[31.9, 49.6, -69.5], [49.6, 128.4, -107.4], [-69.5, -107.4, 206.0]])

    def test_correlation_matrix(self):
        R = [[round(v, 2) for v in row] for row in V["corr3"]]
        self.assertEqual(R, [[1.0, 0.77, -0.86], [0.77, 1.0, -0.66], [-0.86, -0.66, 1.0]])

    def test_confounder_removed(self):
        self.assertEqual(round(V["iced_hot_without_temp"], 2), 0.01)


class Section10Eigen(unittest.TestCase):
    def test_values_and_vectors(self):
        self.assertEqual([round(v, 1) for v in V["eigvals"]], [149.3, 11.0])
        self.assertEqual([round(v, 2) for v in V["v1"]], [0.39, 0.92])
        self.assertEqual([round(v, 2) for v in V["v2"]], [-0.92, 0.39])
        self.assertAlmostEqual(V["v1_dot_v2"], 0.0, places=12)

    def test_eigen_equation(self):
        for a, b in zip(V["sigma_v1"], V["lambda_v1"]):
            self.assertAlmostEqual(a, b, places=8)

    def test_conserved(self):
        self.assertEqual(round(V["eig_sum"], 1), 160.3)
        self.assertAlmostEqual(V["eig_sum"], V["trace"])
        self.assertEqual(round(V["t_var"], 1) + round(V["c_var"], 1), 160.3)

    def test_geometry(self):
        self.assertEqual(round(V["v1_angle"]), 67)
        self.assertEqual([round(v, 1) for v in V["eig_sd"]], [12.2, 3.3])      # hands-on: sqrt(lambda)
        self.assertEqual([round(v, 1) for v in V["arrow_len"]], [24.4, 6.6])   # the drawn arrows, 2 sqrt(lambda)
        self.assertEqual(round(V["eig_sd"][0] / V["eig_sd"][1]), 4)
        self.assertEqual([round(100 * s, 1) for s in V["shares"]], [93.2, 6.8])

    def test_projection_variance(self):
        for a, b in zip(V["pc_score_var"], V["eigvals"]):
            self.assertAlmostEqual(a, b, places=8)
        self.assertAlmostEqual(V["pc_score_corr"], 0.0, places=10)


class Section11PCA(unittest.TestCase):
    def test_fahrenheit(self):
        self.assertAlmostEqual(V["f_var_factor"], 3.24)
        self.assertEqual(round(100 * V["f_shares"][0], 1), 88.9)

    def test_standardized(self):
        self.assertEqual([round(v, 2) for v in V["std_eigvals"]], [1.77, 0.23])
        self.assertAlmostEqual(V["std_eigvals"][0], V["one_plus_r"])
        self.assertAlmostEqual(V["std_eigvals"][1], V["one_minus_r"])
        self.assertEqual([round(100 * s, 1) for s in V["std_shares"]], [88.7, 11.3])

    def test_three_columns(self):
        self.assertEqual([round(100 * s, 1) for s in V["corr3_shares"]], [84.4, 11.6, 4.0])
        self.assertEqual([round(100 * s, 1) for s in V["corr3_cum"]], [84.4, 96.0, 100.0])


class Sources(unittest.TestCase):
    def test_saved_json_is_fresh(self):
        saved = json.loads((C.OUT / "l09_numbers.json").read_text())
        self.assertEqual(saved, json.loads(json.dumps(C.compute())))

    def test_figure_script_agrees(self):
        fig = (C.OUT / "l09_figures.txt").read_text()
        for line in ("mean temp = 21.81 °C   mean iced = 39.49 cups",
                     "correlation r = 0.7747",
                     "slope     b = Sxy/Sxx = 49.6/31.9 = 1.5548 cups per °C",
                     "SS_tot = 38385.5   SS_res = 15347.9",
                     "residual sd = 7.18 cups",
                     "example day: 25.0 °C, 32 cups sold, line predicts 44.4, residual -12.5",
                     "Pearson r(temp, total drinks) = -0.0628",
                     "straight-line R² = 0.0039   curve R² = 0.5459",
                     "eigenvalues: 149.29 and 10.96",
                     "variance shares: 93.2% and 6.8%",
                     "PC1 angle = 67.1° from the temperature axis",
                     "shares: 88.7% and 11.3%"):
            self.assertIn(line, fig)


if __name__ == "__main__":
    unittest.main()
