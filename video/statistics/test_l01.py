"""Unit tests for the Lecture 1 numbers the video draws beside its labels.

A label is words only (narration/labels.yaml); every number set next to one comes from
raw/l01_numbers.json or raw/v01_numbers.json, written by capture_l01.py / capture_v01.py. Each test
recomputes the value from the raw inputs where it can, and checks it against what the slides
(statistics/lectures/lecture01_*.tex) and the narration (narration/lecture01.md) say.
    uv run python -m unittest discover -s statistics -p 'test_l01.py'
"""
import json
import unittest
from pathlib import Path

import numpy as np

RAW = Path(__file__).parent / "raw"
L = json.loads((RAW / "l01_numbers.json").read_text())
V1 = json.loads((RAW / "v01_numbers.json").read_text())
A = json.loads((RAW / "l01_arrays.json").read_text())
SAL = np.loadtxt(RAW / "v01_salaries.txt")


class Section1Data(unittest.TestCase):
    def test_height_example(self):
        self.assertEqual(L["height_example"], 172.4)          # read off the ruler, then 172.43


class Section2And3Salaries(unittest.TestCase):
    def test_sample_size(self):
        self.assertEqual(len(SAL), 600)
        self.assertEqual(sum(L["hist_counts"]), len(SAL))

    def test_more_than_half(self):
        counts, _ = np.histogram(SAL, bins=L["hist_edges"])
        self.assertEqual(counts.tolist(), L["hist_counts"])
        self.assertEqual(L["hist_counts"][1], 311)             # $40k-$60k: 311 of 600
        self.assertGreater(2 * L["hist_counts"][1], len(SAL))

    def test_hands_on_edge(self):
        self.assertEqual(L["above_80k_edge"], 80_000.0)
        self.assertEqual(L["above_80k"], int((SAL >= L["above_80k_edge"]).sum()))


class Section4Mean(unittest.TestCase):
    def test_nine_below_mean(self):
        nine = V1["nine"]
        self.assertEqual(V1["nine_below"], sum(x < sum(nine) / len(nine) for x in nine))
        self.assertEqual((V1["nine_below"], len(nine)), (6, 9))    # 6/9 earn less than the mean

    def test_people(self):
        self.assertEqual(V1["n_emp"], len(SAL))


class Section5Typo(unittest.TestCase):
    def test_one_typo(self):
        diff = [(a, b) for a, b in zip(L["five"], L["five_typo"]) if a != b]
        self.assertEqual(diff, [(52, 520)])                    # a dropped decimal point


class Section7Bottles(unittest.TestCase):
    def test_settings(self):
        self.assertEqual((L["bottle_target"], L["bottle_tol"], L["bottles"]), (500.0, 5.0, 1000))
        self.assertEqual(L["bottle_sd"], {"A": 2.0, "B": 4.0})
        self.assertEqual(L["bottle_spread_ratio"], 2.0)

    def test_limits_in_standard_deviations(self):
        for m, want in (("A", 2.5), ("B", 1.25)):
            self.assertEqual(L[f"bottle_{m}_limits_sd"], L["bottle_tol"] / L["bottle_sd"][m])
            self.assertEqual(L[f"bottle_{m}_limits_sd"], want)

    def test_rejected(self):
        lo, hi = L["bottle_target"] - L["bottle_tol"], L["bottle_target"] + L["bottle_tol"]
        for m, want in (("A", 11), ("B", 210)):
            f = np.array(A[f"fills_{m}"])
            self.assertEqual(len(f), L["bottles"])
            self.assertEqual(int(((f < lo) | (f > hi)).sum()), want)
            self.assertEqual(L[f"bottle_{m}_rejected"], want)
        self.assertEqual(L["bottle_ratio"], round(210 / 11))   # waste ×19

    def test_teaser_outlier(self):
        self.assertEqual(V1["nine"][-1], 88)                   # with and without 88


class Section8Quartiles(unittest.TestCase):
    def test_no_low_outlier(self):
        self.assertEqual(L["fence_lo"], L["q1"] - 1.5 * L["iqr"])
        self.assertEqual((min(L["nine"]), L["fence_lo"]), (31, 15.25))
        self.assertGreater(min(L["nine"]), L["fence_lo"])

    def test_branch_c_iqr(self):
        c = L["branches"][2]
        self.assertEqual(c["name"], "C")
        self.assertEqual(round(c["q3x"] - c["q1x"], 1), round(c["iqrx"], 1))
        self.assertEqual(round(c["iqrx"], 1), 19.9)


class Section12Birthdays(unittest.TestCase):
    def test_pairs(self):
        self.assertEqual(L["bday_first_over_half"], 23)
        self.assertEqual(L["bday_pairs_23"], 23 * 22 // 2)
        self.assertEqual(L["bday_first_over_half"] - 1, 22)    # me against the 22 others

    def test_hands_on_class(self):
        self.assertEqual(L["bday_class"], 30)
        self.assertGreater(L["bday"]["30"], 0.5)


class Section14Spam(unittest.TestCase):
    def test_training_share(self):
        s = L["spam_train"]
        self.assertEqual((s["spam"], s["emails"]), (9, 10))
        self.assertEqual(round(100 * s["spam"] / s["emails"]), 90)   # the slide's 90 %


if __name__ == "__main__":
    unittest.main()
