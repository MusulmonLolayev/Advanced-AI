"""Cue timing in every language (cues.py, common.at): English and Uzbek give exactly the seconds they always gave, on
every real (line, cue) pair of the scene files; any other language is placed by the line's reference text (same sentence
and share of it, else the same share of the line); an override wins; a bad override or a missing form stops the render
with a clear message.

    uv run python -m unittest discover -s studio -p 'test_cues.py' -t .        (from video/)
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

import check_lang as CL
import cues
import cuescan
import languages as LG

HERE = Path(__file__).resolve().parents[1]
STEMS = ["lecture01", "lecture02", "lecture03", "lecture04", "lecture05", "m7_lecture01"]


def old_at(text, k, lang):
    """common.at before the languages work (git 2e0d948), as characters before the cue: the reference to compare with."""
    if isinstance(k, dict):
        k = k[lang]
    if isinstance(k, str):
        i = text.find(k)
        if i < 0:
            raise ValueError(f"cue {k!r} not in narration: {text[:60]!r}")
        return i
    parts = [x for x in re.split(r"(?<=[.?!:])\s+", text.strip()) if x]
    if k > len(parts) - 1:
        raise ValueError(f"cue {k} past the last sentence ({len(parts)}) of {text[:60]!r}")
    return sum(len(x) + 1 for x in parts[:k])


class Tracker:
    duration = 7.3


class EnglishAndUzbekAreUnchanged(unittest.TestCase):
    def test_every_real_cue_gives_the_same_seconds_as_before(self):
        n = ok = errors = 0
        for stem in STEMS:
            texts = CL.line_texts(stem)
            primary = "uz" if stem == "lecture01" or not stem.startswith("m7") else "en"
            for c in cuescan.cues(stem):
                if c["k"] is None or c["key"] is None:
                    continue
                for lang in ("en", "uz"):
                    text = texts.get(lang, {}).get(c["key"])
                    if text is None or (isinstance(c["k"], dict) and lang not in c["k"]):
                        continue                              # a dict without the form raised KeyError before
                    ref = cues.CueRef(c["key"], {l: t[c["key"]] for l, t in texts.items() if c["key"] in t}, primary)
                    n += 1
                    try:
                        want = old_at(text, c["k"], lang)
                    except ValueError as e:
                        errors += 1                           # a phrase of the other law's branch: the same message
                        with self.assertRaises(ValueError) as got:
                            cues.cue_offset(text, c["k"], ref, lang)
                        self.assertEqual(str(got.exception), str(e), c)
                        continue
                    self.assertEqual(cues.cue_offset(text, c["k"], ref, lang), want, c)
                    self.assertEqual(cues.cue_offset(text, c["k"], None, lang), want, c)
                    ok += 1
                    # the seconds, as common.at computes them: duration * characters before / length
                    self.assertEqual(Tracker.duration * cues.cue_offset(text, c["k"], ref, lang) / max(len(text), 1),
                                     Tracker.duration * want / max(len(text), 1))
        self.assertGreater(ok, 500, (n, ok, errors))

    def test_common_at_is_cue_offset(self):
        import common
        t = "First sentence here. Second one follows: and a third? Done."
        for k in (0, 2, "Second", {"en": 3, "uz": 0}):
            self.assertEqual(common.at(Tracker, t, k), Tracker.duration * old_at(t, k, common.LANG) / len(t))


REF = "Alpha one is here. Bravo two is next. Charlie three ends."
TGT = "Альфа раз здесь. Браво два дальше. Чарли три конец."


def ref(**kw):
    return cues.CueRef("1.1", {"en": REF, "ru": TGT, **kw.pop("texts", {})}, kw.pop("primary", "en"), kw.pop("overrides", {}))


class OtherLanguagesAreMapped(unittest.TestCase):
    def test_same_sentence_and_share_when_both_have_as_many_sentences(self):
        r = ref()
        self.assertEqual(cues.cue_offset(TGT, {"en": "Bravo two", "uz": "x"}, r, "ru"), TGT.index("Браво"))
        a = REF.index("two")                                   # 6 characters into sentence 1 of 18
        want = TGT.index("Браво") + 6 / 18 * len("Браво два дальше.")
        self.assertAlmostEqual(cues.cue_offset(TGT, {"en": "two"}, r, "ru"), want)
        self.assertEqual(cues.cue_offset(TGT, {"en": 2}, r, "ru"), TGT.index("Чарли"))      # an index: the sentence's start
        self.assertGreater(a, 0)

    def test_the_share_of_the_whole_line_when_the_sentence_counts_differ(self):
        two = "Альфа раз здесь, Браво два дальше. Чарли три конец."
        r = ref(texts={"ru": two})
        want = len(two) * REF.index("Charlie") / len(REF)
        self.assertAlmostEqual(cues.cue_offset(two, {"en": "Charlie"}, r, "ru"), want)
        self.assertAlmostEqual(cues.cue_offset(two, {"en": 2}, r, "ru"), len(two) * REF.index("Charlie") / len(REF))

    def test_a_dict_that_has_the_language_is_read_as_written(self):
        self.assertEqual(cues.cue_offset(TGT, {"en": "Bravo", "ru": "Чарли"}, ref(), "ru"), TGT.index("Чарли"))

    def test_a_bare_index_works_as_before_when_the_line_has_that_sentence(self):
        self.assertEqual(cues.cue_offset(TGT, 1, ref(), "ru"), old_at(TGT, 1, "ru"))
        short = "Один. Два."
        r = cues.CueRef("1.1", {"en": REF, "ru": short}, "en")
        self.assertAlmostEqual(cues.cue_offset(short, 2, r, "ru"), len(short) * REF.index("Charlie") / len(REF))   # past the end: mapped

    def test_a_bare_phrase_of_the_reference_language_is_found_there_and_mapped(self):
        self.assertEqual(cues.cue_offset(TGT, "Bravo two", ref(), "ru"), TGT.index("Браво"))
        self.assertEqual(cues.cue_offset(TGT, "Браво", ref(), "ru"), TGT.index("Браво"))        # in this line: as written

    def test_the_reference_language_is_the_primary_then_english_then_the_first(self):
        r = cues.CueRef("1.1", {"uz": "U1. U2.", "en": "E1. E2.", "ko": "K"}, "uz")
        self.assertEqual(cues.reference_language({"uz": 0, "en": 0}, r, "ru"), "uz")
        self.assertEqual(cues.reference_language({"en": 0, "ko": 0}, r, "ru"), "en")
        self.assertEqual(cues.reference_language({"ko": 0}, r, "ru"), "ko")
        self.assertEqual(cues.reference_language({"ko": 0}, cues.CueRef("1.1", {"uz": "U"}, "en"), "ru"), None)
        self.assertEqual(cues.reference_language({"uz": 0}, cues.CueRef("1.1", {"en": "E"}, "uz"), "ru"), None)

    def test_an_override_wins_over_the_mapping(self):
        r = ref(overrides={"Bravo two": "дальше"})
        self.assertEqual(cues.cue_offset(TGT, {"en": "Bravo two"}, r, "ru"), TGT.index("дальше"))
        self.assertEqual(cues.cue_offset(TGT, "Bravo two", r, "ru"), TGT.index("дальше"))
        self.assertEqual(cues.cue_offset(TGT, {"en": "Bravo two", "ru": "Чарли"}, r, "ru"), TGT.index("Чарли"))   # the scene's own form is first

    def test_a_bad_override_stops_with_a_clear_message(self):
        r = ref(overrides={"Bravo two": "nowhere"})
        with self.assertRaisesRegex(ValueError, "ru cue override for line 1.1: 'nowhere' .* is not in the ru line"):
            cues.cue_offset(TGT, {"en": "Bravo two"}, r, "ru")

    def test_a_cue_the_reference_line_lacks_or_no_reference_stops(self):
        with self.assertRaisesRegex(ValueError, "cue 'Delta' not in narration"):
            cues.cue_offset(TGT, {"en": "Delta"}, ref(), "ru")
        with self.assertRaisesRegex(ValueError, "no ru form for cue .* no reference line"):
            cues.cue_offset(TGT, {"en": "Bravo"}, None, "ru")
        with self.assertRaisesRegex(ValueError, "has no text to be placed by"):
            cues.cue_offset(TGT, {"uz": 1}, ref(), "ru")


class WordsAndLabelsNeverFallBackToAnotherLanguage(unittest.TestCase):
    def run_py(self, code, lang):
        import os
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, env=dict(os.environ, LANG_CODE=lang))
        return r.returncode, (r.stdout + r.stderr)

    def test_by_lang_and_label_say_which_language_is_missing(self):
        code = ("import common\n"
                "print(common.by_lang({'en': 'Yes', 'ru': 'Да'}))\n"
                "for f in (lambda: common.by_lang({'en': 'Yes', 'uz': 'Ha'}, 'the yes button'), lambda: common.label('pause'),\n"
                "          lambda: common.forms('no_such_label_key')):\n"
                "    try: f()\n"
                "    except KeyError as e: print(type(e).__name__, '|', e)\n")
        rc, out = self.run_py(code, "ru")
        self.assertEqual(rc, 0, out[-500:])
        lines = [l for l in out.splitlines() if l.startswith(("Да", "NoForm"))]
        self.assertEqual(lines[0], "Да")
        self.assertRegex(lines[1], r"^NoForm \| no ru form for the yes button \(it has en, uz\); add one before building in ru$")
        self.assertRegex(lines[2], r"^NoForm \| label 'pause' has no ru form \(has en, uz")
        self.assertRegex(lines[3], r"^NoForm \| label 'no_such_label_key' is not in narration/labels.yaml")

    def test_a_label_draft_may_add_a_language_but_not_change_words(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.yaml").write_text("pause:\n  ru: 'Остановите видео'\nzz_new:\n  en: x\n")
            code = "import common; print(common.label('pause'), '|', common.forms('zz_new', 'en'))"
            import os
            r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                               env=dict(os.environ, LANG_CODE="ru", LABEL_DRAFTS=d))
            self.assertEqual(r.stdout.strip().splitlines()[-1].split(" | ")[0], "Остановите видео", r.stderr[-400:])
            (Path(d) / "a.yaml").write_text("pause:\n  en: 'Other words'\n")
            r = subprocess.run([sys.executable, "-c", "import common"], cwd=HERE, capture_output=True, text=True,
                               env=dict(os.environ, LANG_CODE="en", LABEL_DRAFTS=d))
            self.assertIn("already in labels.yaml with other words", r.stderr)


if __name__ == "__main__":
    unittest.main()
