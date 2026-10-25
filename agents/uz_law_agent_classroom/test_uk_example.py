"""The UK example corpus loader test, moved out of uz-law-agent's test_agent.py.

Needs corpus_uk.py, data/uk_working_time.jsonl and data/SOURCE_UK.md next to it (all in this folder).

    python -m unittest test_uk_example
"""
import hashlib
import unittest

import corpus_uk


class UKExampleCorpus(unittest.TestCase):
    """The optional UK example corpus (corpus_uk.py) only has to load; the agent does not use it."""
    def test_it_loads_the_pinned_file(self):
        self.assertIn(hashlib.sha256(corpus_uk.DATA.read_bytes()).hexdigest(), (corpus_uk.DATA.parent / "SOURCE_UK.md").read_text())
        lines = corpus_uk.DATA.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(corpus_uk.ARTICLES), len(lines))
        self.assertEqual(len(lines), 118)
        self.assertEqual(sum(k.startswith("WTR ") for k in corpus_uk.ARTICLES), 64)


if __name__ == "__main__":
    unittest.main()
