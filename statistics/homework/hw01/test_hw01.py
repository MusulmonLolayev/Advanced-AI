"""Unit tests for Homework 1's numbers: each answer recomputed independently of hw01_numbers.py.

No expected value is typed here (the tests sit in the shared repo, the answers do not): every check recomputes from
the sheet's data with another method -- Python's statistics module, brute-force counting, a direct product.

    python3 -m unittest discover -s statistics/homework/hw01 -p 'test_hw01.py'
"""
import itertools
import json
import math
import statistics as st
import unittest
from fractions import Fraction
from pathlib import Path

import hw01_numbers as H

A = H.compute()


def lecture_quartiles(x):
    """The lecture's rule, written out again: halves split at the median, the median left out when n is odd."""
    s = sorted(x)
    h = len(s) // 2
    return st.median(s[:h]), st.median(s[-h:])


class Centre(unittest.TestCase):
    def test_rent(self):
        self.assertAlmostEqual(float(A["rent_mean"]), st.mean(H.RENTS))
        self.assertEqual(A["rent_median"], st.median(H.RENTS))
        self.assertEqual(A["rent_mode"], st.multimode(H.RENTS))
        rest = sorted(H.RENTS)[:-1]
        self.assertAlmostEqual(float(A["rent_rest_mean"]), st.mean(rest))
        self.assertEqual(A["rent_rest_median"], st.median(rest))
        self.assertEqual(A["rent_rank_of_mean"], len([r for r in H.RENTS if r < st.mean(H.RENTS)]))

    def test_news_claim_is_the_mean_rounded_up(self):
        pay = [H.STAFF_PAY] * H.STAFF + [H.OWNER_PAY]
        self.assertTrue(st.mean(pay) <= H.news_claim() < st.mean(pay) + 1000)

    def test_story_mean_and_median(self):
        pay = [H.STAFF_PAY] * H.STAFF + [H.OWNER_PAY]
        self.assertAlmostEqual(float(A["pay_mean"]), st.mean(pay))
        self.assertEqual(A["pay_median"], st.median(pay))


class Spread(unittest.TestCase):
    def test_delivery(self):
        for k, x in (("a", H.DELIVERY_A), ("b", H.DELIVERY_B)):
            self.assertEqual(A[f"del_{k}_mean"], st.mean(x))
            self.assertAlmostEqual(float(A[f"del_{k}_var"]), st.variance(x))
            self.assertAlmostEqual(A[f"del_{k}_sd"], st.stdev(x))
            self.assertEqual(sum(A[f"del_{k}_dev"]), 0)                    # deviations sum to zero
        self.assertEqual(st.mean(H.DELIVERY_A), st.mean(H.DELIVERY_B))    # the task's premise: same mean
        self.assertEqual(A["del_sum"], sum(H.DELIVERY_B))
        b = H.DELIVERY_B                                                   # challenge: the shortcut formula
        self.assertEqual(A["del_b_sum_sq"] - len(b) * st.mean(b) ** 2, A["del_b_ss"])

    def test_error_task(self):
        self.assertAlmostEqual(float(A["err_var_by_n"]), st.pvariance(H.ERROR_DATA))
        self.assertAlmostEqual(float(A["err_var_ok"]), st.variance(H.ERROR_DATA))
        self.assertAlmostEqual(float(A["err_ss"]), st.variance(H.ERROR_DATA) * (len(H.ERROR_DATA) - 1))
        self.assertNotEqual(A["err_var_by_n"], A["err_var_ok"])
        self.assertIn(f"= {H.num(A['err_var_by_n'])}$", H.wrong_variance_tex())     # the sheet shows the wrong value


class FiveNumbers(unittest.TestCase):
    def test_summary_and_fences(self):
        q1, q3 = lecture_quartiles(H.SCORES)
        self.assertEqual((A["sc_q1"], A["sc_q3"]), (q1, q3))
        self.assertEqual(A["sc_median"], st.median(H.SCORES))
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        self.assertEqual((float(A["sc_lo_fence"]), float(A["sc_hi_fence"])), (lo, hi))
        self.assertEqual(A["sc_outliers"], [v for v in H.SCORES if not lo <= v <= hi])
        self.assertEqual(len(A["sc_outliers"]), 1)                         # the sheet says one score stands out

    def test_lecture_rule_on_lecture_example(self):
        # the slide's nine salaries give Q1 = 40, Q3 = 56.5: the rule here is the lecture's rule
        self.assertEqual(lecture_quartiles([31, 38, 42, 45, 47, 49, 52, 61, 88]), (40, 56.5))
        self.assertEqual(H.quartiles([31, 38, 42, 45, 47, 49, 52, 61, 88]), (40, Fraction(113, 2)))


class Probability(unittest.TestCase):
    def test_cards(self):
        deck = list(itertools.product(range(13), "SHDC"))                # rank 11 = queen; H, D red
        hit = [c for c in deck if c[1] in "HD" or c[0] == 11]
        self.assertEqual(A["p_red_or_queen"], Fraction(len(hit), len(deck)))

    def test_dice(self):
        rolls = list(itertools.product(range(1, 7), repeat=2))
        self.assertEqual(A["p_sum7"], Fraction(sum(a + b == 7 for a, b in rolls), len(rolls)))
        self.assertEqual(A["p_sum_ge10"], Fraction(sum(a + b >= 10 for a, b in rolls), len(rolls)))
        self.assertEqual(A["p_atleast_one6_two"], Fraction(sum(6 in r for r in rolls), len(rolls)))
        self.assertEqual(A["cells_with_six"], len([r for r in rolls if 6 in r]))
        four = list(itertools.product(range(1, 7), repeat=4))
        self.assertEqual(A["p_atleast_one6_four"], Fraction(sum(6 in r for r in four), len(four)))

    def test_independence(self):
        A_ = {2, 4, 6}
        for k, B in (("B", {1, 2, 3}), ("C", {1, 2, 3, 4}), ("D", {1, 3, 5})):
            joint = Fraction(len(A_ & B), 6)
            self.assertEqual(A[f"indep_A{k}"], joint == Fraction(len(A_), 6) * Fraction(len(B), 6))
            self.assertEqual(A[f"excl_A{k}"], not (A_ & B))

    def test_birthday(self):
        for n in H.BIRTHDAY_N:
            direct = 1 - math.prod((365 - k) / 365 for k in range(n))
            self.assertAlmostEqual(float(A[f"p_share_{n}"]), direct, places=12)

    def test_error_task_addition_rule(self):
        deck = list(itertools.product(range(13), "SHDC"))                # rank 12 = king
        hit = [c for c in deck if c[1] == "H" or c[0] == 12]
        self.assertEqual(A["err_p_ok"], Fraction(len(hit), 52))
        self.assertGreater(A["err_p_wrong"], A["err_p_ok"])               # the mistake double-counts


class Extra(unittest.TestCase):
    def test_die_moments(self):
        faces = list(range(1, 7))
        self.assertEqual(A["die_mean"], st.mean(faces))
        self.assertAlmostEqual(float(A["die_var"]), st.pvariance(faces))
        self.assertEqual(A["die_expected"] * 6, H.DIE_ROLLS)

    def test_coins_venn_pin_hearts(self):
        o = list(itertools.product("HT", repeat=H.COINS))
        self.assertEqual(A["coin_outcomes"], 2 ** H.COINS)
        self.assertEqual(A["p_two_heads"], Fraction(sum(x.count("H") == 2 for x in o), len(o)))
        self.assertEqual(A["p_atleast_one_head"], Fraction(sum("H" in x for x in o), len(o)))
        people = (["PR"] * H.BOTH + ["P"] * (H.PYTHON - H.BOTH) + ["R"] * (H.R_LANG - H.BOTH))
        people += [""] * (H.CLASS - len(people))
        self.assertEqual(A["p_python_or_r"], Fraction(sum(bool(x) for x in people), H.CLASS))
        self.assertEqual(A["p_only_python"], Fraction(people.count("P"), H.CLASS))
        pins = list(itertools.product(range(10), repeat=H.PIN_DIGITS))
        self.assertEqual(A["p_pin_distinct"], Fraction(sum(len(set(x)) == H.PIN_DIGITS for x in pins), len(pins)))
        draws = list(itertools.product(range(52), repeat=2))                       # cards 0-12 are hearts
        self.assertEqual(A["p_two_hearts"], Fraction(sum(a < 13 and b < 13 for a, b in draws), len(draws)))

    def test_new_errors(self):
        self.assertEqual(A["err_median_ok"], st.median(H.ERR_MEDIAN_DATA))
        self.assertNotEqual(A["err_median_wrong"], A["err_median_ok"])        # the unsorted middle differs
        rolls = list(itertools.product(range(1, 7), repeat=H.ERR_SIX_ROLLS))
        self.assertEqual(A["err_six_ok"], Fraction(sum(6 in r for r in rolls), len(rolls)))
        self.assertEqual(A["err_six_wrong"], 1)                                  # the claim being refuted
        scores = [m for n, m in H.GROUPS for _ in range(n)]
        self.assertEqual(A["err_group_ok"], st.mean(scores))
        self.assertNotEqual(A["err_group_wrong"], A["err_group_ok"])
        self.assertGreater(H.WAIT_MEAN, H.WAIT_MEDIAN)                          # 8b's premise: a right tail
        for sd, k in zip(H.CLASS_SD, ("a", "b")):
            self.assertAlmostEqual(float(A[f"z_fifty_{k}"]), (H.CLASS_MEAN - 50) / sd)


class Files(unittest.TestCase):
    def test_sheet_data_matches_the_script(self):
        self.assertEqual((H.HERE / "hw01_data.tex").read_text(), H.data_tex(), "rerun hw01_numbers.py")

    def test_key_matches_the_script(self):
        key = H.KEYS / "hw01_answers.json"
        if key.exists():                                                   # the key is local only
            self.assertEqual(json.loads(key.read_text()),
                             {k: H.jsonable(v) for k, v in A.items()}, "rerun hw01_numbers.py")


if __name__ == "__main__":
    unittest.main()
