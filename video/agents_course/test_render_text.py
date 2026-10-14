"""The voice says the captured values: every {{placeholder}} in the narration fills from its raw file, and the
filled words are the ones the run produced.

    cd video && uv run python -m unittest discover -s agents_course -p 'test_render_text.py'
"""
import json
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
import agents_course_kit as K  # noqa: E402

MD = (HERE.parent / "narration" / "agents_course.md").read_text()


def raw(name):
    return json.loads((HERE / "raw" / name).read_text())


def said(key):
    return K.NARRATION[key]["en"]


class Words(unittest.TestCase):
    def test_integers(self):
        for n, w in [(0, "zero"), (2, "two"), (11, "eleven"), (26, "twenty-six"), (72, "seventy-two"),
                     (100, "one hundred"), (698, "six hundred and ninety-eight"), (1000, "one thousand"),
                     (34500, "thirty-four thousand five hundred")]:
            self.assertEqual(K.words(n), w)

    def test_rates_and_money(self):
        self.assertEqual(K.point(0.7667), "zero point seven seven")
        self.assertEqual(K.point(0.6), "zero point six")
        self.assertEqual(K.point(0.5), "zero point five")
        self.assertEqual(K.percent(0.6), "sixty percent")
        self.assertEqual(K.cents(0.2643), "twenty-six cents")


class Placeholders(unittest.TestCase):
    def test_every_placeholder_has_a_rule_and_fills(self):
        holes = {f"{f}: {x.strip()}" for f, x in re.findall(r"\{\{agents_course/raw/([^:}]+):\s*([^}]+)\}\}", MD)}
        self.assertTrue(holes)
        self.assertEqual(holes - set(K.SPOKEN), set())
        for key, v in K.NARRATION.items():
            self.assertNotIn("{{", v["en"], key)

    def test_s1_runs(self):
        self.assertEqual(raw("s1_agent_loop.json")["steps"], 2)
        self.assertIn("finished in two tool calls", said("1.11"))
        self.assertEqual(raw("s1_agent_loop_vague.json")["steps"], 3)
        self.assertIn("tried three spellings", said("2.3"))

    def test_s2_runs(self):
        self.assertEqual(len(raw("s2_structured.json")["tries"]), 2)
        self.assertIn("right on try number two.", said("2.10"))
        self.assertEqual(len(raw("s2_structured_unhelpful.json")["tries"]), 3)
        self.assertIn("failed three times in a row", said("2.11"))

    def test_banking(self):
        b = raw("tau2_banking.json")
        self.assertEqual((b["n_tasks"], b["kb_searches"], b["pass_1"]), (5, 72, 0.6))
        self.assertIn("on five banking tasks", said("5.10"))
        self.assertIn("searched the documents seventy-two times", said("5.10"))
        self.assertIn("passed sixty percent of the conversations", said("5.10"))

    def test_trajectory_and_failure(self):
        t, f = raw("tau2_retail_trajectory.json"), raw("tau2_retail_failure.json")
        self.assertEqual((t["task_id"], t["turns"], t["tool_calls"], t["reward"]), ("4", 26, 11, 1.0))
        self.assertIn("task four: twenty-six messages and eleven tool calls", said("8.4"))
        self.assertIn("a reward of one.", said("8.4"))
        self.assertEqual(f["task_id"], "5")
        self.assertIn("task five.", said("8.5"))

    def test_retail_run(self):
        r = raw("tau2_retail.json")
        self.assertEqual((r["n_tasks"], r["n_trials"]), (10, 3))
        self.assertEqual(round(r["pass_1"], 2), 0.77)
        self.assertEqual(r["pass_hat_k"], {"1": 0.7667, "2": 0.6, "3": 0.5})
        self.assertEqual(round(100 * r["cost_usd"]), 26)
        s = said("8.9")
        self.assertIn("on ten tasks, three trials each", s)
        self.assertIn("Pass to the one was zero point seven seven", s)
        self.assertIn("fell to zero point six at two trials, and zero point five at three", s)
        self.assertIn("The whole run cost twenty-six cents.", s)
        self.assertNotIn("dollars", s)


class Parse(unittest.TestCase):
    def test_sections_and_lines(self):
        self.assertEqual(sorted(K.HEADS), list(range(1, 10)))
        self.assertEqual(K.HEADS[1]["en"], "Section 1 · The agent loop")
        self.assertEqual(len(K.NARRATION), len(re.findall(r"^\s*\d+[a-z]?\.\s+(?:⏸\s*)?\*\*", MD, re.M)))


if __name__ == "__main__":
    unittest.main()
