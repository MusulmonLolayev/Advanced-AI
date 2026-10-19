"""Tests for studio/narration_edit.py: every presenter line is found in its narration file, one line is rewritten
and nothing else moves, Uzbek apostrophes come out as the repo writes them.

    uv run python -m unittest discover -s studio -p 'test_narration_edit.py' -t .        (from video/)
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from studio import narration_edit as N

HERE = Path(__file__).resolve().parents[1]
BI = """# x
## Lecture opening
0. **Assalomu alaykum, aziz doʻstlar.**
   *Hello, dear friends.*
### 1-boʻlim · Section 1 — Nega agent? · Why an agent?
2. **Keling, bitta savoldan boshlaymiz.**
   *Let's start with one question.*
3a. ⏸ **Bir daqiqaga toʻxtaymiz.**
   *Let's pause for a minute.*
- s1a **Bu kompaniyada olti yuz kishi ishlaydi.** · *Six hundred people work at this company.*
"""


class Edit(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        (self.d / "m7_lecture99.md").write_text(BI)
        (self.d / "m7_lecture99_en.md").write_text("## Lecture opening\n0. **Hello, dear friends.**\n"
                                                   "### Section 1 — Why\n2. **Let's start with one question.**\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_the_build_picks_its_file(self):
        self.assertEqual(N.source("m7_lecture99_uz_navoiy", self.d), (self.d / "m7_lecture99.md", "uz", False))
        self.assertEqual(N.source("m7_lecture99_en", self.d), (self.d / "m7_lecture99_en.md", "en", True))
        (self.d / "m7_lecture99_en.md").unlink()
        self.assertEqual(N.source("m7_lecture99_en", self.d), (self.d / "m7_lecture99.md", "en", False))

    def test_one_uzbek_line_changes_and_its_english_stays(self):
        path, lang, single = N.source("m7_lecture99_uz_navoiy", self.d)
        key, text = N.rewrite(path, lang, single, "Bir daqiqaga toʻxtaymiz.", "Bir daqiqa to'xtab olamiz.")
        self.assertEqual((key, text), ("1.3a", "Bir daqiqa toʻxtab olamiz."))
        after = path.read_text()
        self.assertIn("3a. ⏸ **Bir daqiqa toʻxtab olamiz.**\n   *Let's pause for a minute.*", after)
        self.assertEqual(after.replace("Bir daqiqa toʻxtab olamiz.", "Bir daqiqaga toʻxtaymiz."), BI)

    def test_a_depth_line_changes_only_its_own_language(self):
        path = self.d / "m7_lecture99.md"
        N.rewrite(path, "uz", False, "Bu kompaniyada olti yuz kishi ishlaydi.", "Kompaniyada olti yuz kishi bor.")
        N.rewrite(path, "en", False, "Six hundred people work at this company.", "The company has six hundred people.")
        self.assertIn("- s1a **Kompaniyada olti yuz kishi bor.** · *The company has six hundred people.*",
                      path.read_text())

    def test_an_english_line_in_the_bilingual_file_is_its_italic_row(self):
        path = self.d / "m7_lecture99.md"
        N.rewrite(path, "en", False, "Let's start with one question.", "Let's begin with a question.")
        self.assertIn("2. **Keling, bitta savoldan boshlaymiz.**\n   *Let's begin with a question.*", path.read_text())

    def test_the_single_language_file(self):
        path, lang, single = N.source("m7_lecture99_en", self.d)
        self.assertEqual(N.rewrite(path, lang, single, "Let's start with one question.", "  Let's   begin. "),
                         ("1.2", "Let's begin."))

    def test_refusals(self):
        path, lang, single = N.source("m7_lecture99_uz_navoiy", self.d)
        with self.assertRaises(KeyError):
            N.rewrite(path, lang, single, "Not a line.", "x")
        with self.assertRaises(ValueError):
            N.rewrite(path, lang, single, "Keling, bitta savoldan boshlaymiz.", "Келинг")
        with self.assertRaises(ValueError):
            N.rewrite(path, lang, single, "Keling, bitta savoldan boshlaymiz.", "a ** b")

    def test_uzbek_apostrophes(self):
        self.assertEqual(N.uz_text("o'n g‘oya ma'lumot so`z"), "oʻn gʻoya maʼlumot soʻz")


class RealNarration(unittest.TestCase):
    """Every line of the built lectures' presenter pages is found in its narration file, exactly once."""
    def check(self, build):
        lj = HERE / "out" / build / "presenter" / "lines.json"
        if not lj.exists():
            self.skipTest(f"{build} is not built")
        path, lang, single = N.source(build)
        for line in json.loads(lj.read_text()):
            N.find(path, lang, single, line[1])

    def test_module_0_lecture_1(self):
        self.check("lecture01_uz_navoiy")

    def test_module_7_lecture_1_english(self):
        self.check("m7_lecture01_en")


if __name__ == "__main__":
    unittest.main()
