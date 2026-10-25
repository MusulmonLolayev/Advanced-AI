"""The numbers in the Lecture 1 handout, recomputed from the files (run from anywhere: python3 -m unittest <file>)."""
import json
import re
import sys
import unittest
from pathlib import Path

LECTURE = Path(__file__).resolve().parents[1] / "solutions" / "lecture01_react_loop"
sys.path.insert(0, str(LECTURE))


@unittest.skipUnless(LECTURE.is_dir(), "the instructor's solution folder is local only")
class Handout(unittest.TestCase):
    def setUp(self):
        self.readme = (LECTURE / "README.md").read_text(encoding="utf-8")

    def test_article_counts(self):
        from uz_agent import corpus
        self.assertIn(f"holds {len(corpus.ARTICLES)} articles", self.readme)
        full = Path(__file__).resolve().parents[2] / "class_agent" / "data" / "mehnat_kodeksi.jsonl"
        if full.exists():
            self.assertIn(f"({len(full.read_text(encoding='utf-8').splitlines())} in the whole Code)", self.readme)

    def test_check_counts(self):
        from uz_agent import self_checks
        n = len(self_checks.ALL_CHECKS)
        given = sum(1 for f in self_checks.ALL_CHECKS if not getattr(f, "needs", ()))
        self.assertIn(f"There are {n} checks", self.readme)
        self.assertIn(f"the {['zero', 'one', 'two', 'three', 'four', 'five', 'six'][given]} checks of the given code", self.readme)

    def test_four_tasks_in_the_code(self):
        text = (LECTURE / "uz_agent" / "agent.py").read_text(encoding="utf-8")
        self.assertEqual(text.count("START OF YOUR CODE"), 4)
        for q in ("Q1", "Q2", "Q3", "Q4"):
            self.assertIn(f"| {q} |", self.readme)

    def test_the_traces_the_notebook_names_exist(self):
        nb = json.loads((LECTURE / "lecture01_react_loop.ipynb").read_text())
        names = set(re.findall(r"\b(q\d_\w+)", json.dumps(nb)))
        for n in names:
            self.assertTrue((LECTURE / "traces" / f"{n}.json").exists(), n)
        self.assertTrue(all(c.get("outputs", []) == [] for c in nb["cells"]))


if __name__ == "__main__":
    unittest.main()
