"""Module 7 Lecture 1: every number the video uses, recomputed another way and checked against the slides.

    uv run python -m unittest discover -s m7 -p 'test_l01.py'      (from video/)
"""
import json
import re
import unittest
from pathlib import Path

import capture_l01 as C

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
SLIDES = (ROOT / "agents/lectures/lecture01_what_is_an_agent.tex").read_text()
N = C.compute()


def slide_number(text):
    return float(text.replace("{,}", "").replace(",", ""))


class Cost(unittest.TestCase):
    def test_billed_tokens_by_summing_every_turn(self):
        for n in C.STEPS:
            self.assertEqual(N[f"billed_{n}"], sum(C.S + (t - 1) * C.A for t in range(1, n + 1)))

    def test_the_table_on_the_slide(self):
        row = re.search(r"Input tokens billed & \$(.*?)\$ & \$(.*?)\$ & \$(.*?)\$", SLIDES).groups()
        self.assertEqual([slide_number(x) for x in row], [N[f"billed_{n}"] for n in C.STEPS])
        row = re.search(r"If you paid only for new text & \$(.*?)\$ & \$(.*?)\$ & \$(.*?)\$", SLIDES).groups()
        self.assertEqual([slide_number(x) for x in row], [N[f"new_only_{n}"] for n in C.STEPS])
        self.assertIn(f"multiplies the bill by ${N['ratio_20_10']}$", SLIDES)

    def test_the_cache(self):
        self.assertEqual(N["fresh_10"] + N["cached_10"], N["billed_10"])
        self.assertIn(f"${N['fresh_10']:,}$ tokens are new".replace(",", "{,}"), SLIDES)
        self.assertIn(f"\\${N['cost_cached_10']} instead of \\${N['cost_full_10']}", SLIDES.replace("0.00517", "0.00517"))
        self.assertIn(f"${N['cache_ratio']}\\times$ cheaper", SLIDES)
        self.assertIn(f"\\${N['eval_cached']} instead of \\${N['eval_full']}", SLIDES)


class Narration(unittest.TestCase):
    def test_turns_and_prices(self):
        self.assertEqual([N["turn_1"], N["turn_2"], N["turn_3"]], [1200, 1700, 2200])
        self.assertEqual(N["billed_5"], 6000 + 5000)
        self.assertEqual((N["cents_per_million"], N["cents_per_million_cached"], N["cache_price_ratio"]), (15.0, 0.3, 50))
        self.assertAlmostEqual(N["p_99_k_20"], 0.818, places=3)


class Compounding(unittest.TestCase):
    def test_p_to_the_k(self):
        p = 1.0
        for _ in range(C.K_LONG):
            p *= C.P_GOOD
        self.assertAlmostEqual(N["p_good_k_long"], p, places=3)
        self.assertIn(f"$0.95^{{10}} = {N['p_good_k_long']}$", SLIDES)
        self.assertIn(f"from ${N['p_lever_k_long']}$ to ${N['p_lever_k_short']}$", SLIDES)


class Files(unittest.TestCase):
    def test_raw_matches(self):
        self.assertEqual(json.loads((HERE / "raw" / "l01_numbers.json").read_text()), N, "rerun capture_l01.py")


if __name__ == "__main__":
    unittest.main()
