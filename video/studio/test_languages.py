"""Languages (languages.yaml, builds.py, studio/linestatus.py, review.py, languages_seed.py): the registry gives the
voices the renders use today; build names round-trip; a language's narration is found (bilingual file, one-language
file) or created as an empty skeleton; a line is empty, draft, approved or "needs update" by the hashes of its text and
of the other languages' texts; labels work the same; the seed approves only Uzbek Lectures 1-5; the review page's actions
write the file through narration_edit and leave the bilingual file's other language alone.

    uv run python -m unittest discover -s studio -p 'test_languages.py' -t .        (from video/)
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

import builds as B
import labels as LB
import languages as LG
from studio import languages_seed as SEED
from studio import linestatus as LS
from studio import narration_edit as N
from studio import review as R
from studio import store as S

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
- s1a **Bu kompaniyada olti yuz kishi ishlaydi.** · *Six hundred people work at this company.* ▸ a picture
### 2-boʻlim · Section 2 — Vositalar · Tools
4. **Vosita nima?**
   *What is a tool?*
"""
EN_ONE = """## Lecture opening
0. **Hello, dear friends (UK).**
### Section 1 — Why an agent?
2. **Let's start with one question (UK).**
2a. **A line only English has.**
### Section 2 — Tools
4. **What is a tool?**
"""


def files(d):
    return {str(p.relative_to(d)): hashlib.sha1(p.read_bytes()).hexdigest() for p in sorted(Path(d).rglob("*")) if p.is_file()}


class Scratch(unittest.TestCase):
    """A scratch narration folder (two small lectures), a scratch database, and label files copied from the real ones."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.nar = d / "narration"
        self.nar.mkdir()
        (self.nar / "lecture98.md").write_text(BI)                      # Module 0 style: bilingual only
        (self.nar / "m7_lecture98.md").write_text(BI)                   # Module 7 style: bilingual uz + a one-language English
        (self.nar / "m7_lecture98_en.md").write_text(EN_ONE)
        self.old_nar = os.environ.get("STUDIO_NARRATION")
        os.environ["STUDIO_NARRATION"] = str(self.nar)
        self.old_labels = LB.NARRATION
        for f in ("labels.yaml", "labels_agents_course.yaml"):
            shutil.copy(HERE / "narration" / f, self.nar / f)
        shutil.copytree(HERE / "narration" / "drafts", self.nar / "drafts")
        LB.use(self.nar)
        self.c = S.connect(d / "studio.sqlite")

    def tearDown(self):
        self.c.close()
        LB.use(self.old_labels)
        if self.old_nar is None:
            os.environ.pop("STUDIO_NARRATION")
        else:
            os.environ["STUDIO_NARRATION"] = self.old_nar
        self.tmp.cleanup()

    def texts(self, stem="lecture98"):
        return LS.line_texts(stem, self.nar)

    def state(self, stem, lang, key, kind="line"):
        by = self.texts(stem) if kind == "line" else LS.label_statuses(self.c, stem, lang)[1]
        return LS.statuses(self.c, stem, lang, kind, by)[key]


class Registry(unittest.TestCase):
    def test_every_language_is_complete(self):
        for code, e in LG.LANGS.items():
            self.assertRegex(code, r"^[a-z]{2,3}$")
            self.assertTrue({"name", "native", "script", "voice", "section", "opening", "font"} <= set(e), code)
            self.assertRegex(e["voice"]["edge"], r"^[a-z]{2}-[A-Z]{2}-\w+Neural$", code)
            self.assertIn(e["script"], ("latin", "cyrillic", "hangul", "arabic", "han"))
            self.assertIn("{n}", e["section"])
        self.assertEqual(LG.CODES[:4], ["uz", "en", "ru", "ko"])
        self.assertTrue({"tr", "de", "fr", "es", "ar", "zh"} <= set(LG.CODES))

    def test_the_voices_rates_and_trims_the_renders_use_today_are_unchanged(self):
        v = LG.voices()
        self.assertEqual({k: v[k] for k in ("en", "uz", "ko")},
                         {"en": "en-US-AndrewNeural", "uz": "uz-UZ-SardorNeural", "ko": "ko-KR-InJoonNeural"})
        self.assertEqual({k: LG.rates().get(k) for k in ("en", "uz", "ko")}, {"en": None, "uz": None, "ko": "+20%"})
        self.assertEqual({k: LG.trims().get(k) for k in ("en", "uz", "ko")}, {"en": None, "uz": None, "ko": (0.15, 0.35)})
        self.assertEqual(LG.voices("navoiy"), {"uz": "musulmon-ft-llm1-flow12-phone"})
        self.assertEqual([LG.section("en", 3), LG.section("uz", 3), LG.section("ko", 3)], ["Section 3", "3-boʻlim", "섹션 3"])
        self.assertEqual((LG.opening("en"), LG.opening("uz")), ("Opening", "Kirish"))

    def test_common_py_takes_them_from_the_registry(self):
        code = ("import json, common as c; print(json.dumps([c.VOICES, c.VOICE_RATES, {k: list(v) for k, v in c.EDGE_TRIM.items()}, "
                "c.NAVOIY_VOICE_ID]))")
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, env=dict(os.environ, LANG_CODE="ko"))
        self.assertEqual(r.returncode, 0, r.stderr[-600:])
        voices, rates, trims, navoiy = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual((voices, rates, navoiy), (LG.voices(), LG.rates(), "musulmon-ft-llm1-flow12-phone"))
        self.assertEqual(trims, {"ko": [0.15, 0.35]})
        self.assertEqual((voices["en"], voices["uz"], voices["ko"], rates), ("en-US-AndrewNeural", "uz-UZ-SardorNeural",
                                                                           "ko-KR-InJoonNeural", {"ko": "+20%"}))


class Builds(unittest.TestCase):
    def test_every_build_on_disk_round_trips(self):
        names = [p.name for p in (HERE / "out").iterdir() if p.is_dir() and B.is_build(p.name)] if (HERE / "out").is_dir() else []
        names += ["lecture01_uz_navoiy", "m7_lecture01_en", "m7_lecture01_uz_navoiy"]
        for n in names:
            self.assertEqual(B.name(*B.parse(n)), n)
            self.assertEqual(B.stem(n) + "_" + B.lang(n) + ("_" + B.engine(n) if B.engine(n) else ""), n)

    def test_new_names(self):
        self.assertEqual(B.parse("m7_lecture01_ru"), (7, 1, "ru", None))
        self.assertEqual(B.parse("lecture03_ko"), (0, 3, "ko", None))
        self.assertEqual(B.parse("lecture01_uz_navoiy"), (0, 1, "uz", "navoiy"))
        self.assertEqual(B.name(7, 1, "ru"), "m7_lecture01_ru")
        self.assertEqual(B.name(0, 3, "ko"), "lecture03_ko")
        self.assertEqual(B.name(0, 1, "uz", "navoiy"), "lecture01_uz_navoiy")
        self.assertEqual((B.stem("m7_lecture01_ru"), B.module("m7_lecture01_ru"), B.parse_stem("m7_lecture01")), ("m7_lecture01", 7, (7, 1)))
        for bad in ("lecture01", "lecture1_en", "out", "lecture01_uz_navoiy.mp4", "m7_lecture01_build.log", "xlecture01_en"):
            self.assertFalse(B.is_build(bad), bad)
            with self.assertRaises(ValueError):
                B.parse(bad)

    def test_the_name_patterns_live_in_builds_py_only(self):
        for f in sorted((HERE / "studio").glob("*.py")) + [HERE / "serve_presenter.py", HERE / "presenter.py"]:
            if f.name.startswith("test_"):
                continue
            src = f.read_text()
            self.assertNotIn("lecture(\\d\\d)", src, f.name)
            self.assertNotRegex(src, r'endswith\("_(uz_navoiy|en)"\)', f.name)


class Resolution(Scratch):
    def test_the_real_narration_files(self):
        nd = HERE / "narration"
        self.assertEqual(N.resolve("lecture01", "uz", nd), (nd / "lecture01.md", False))
        self.assertEqual(N.resolve("lecture01", "en", nd), (nd / "lecture01.md", False))
        self.assertEqual(N.resolve("m7_lecture01", "en", nd), (nd / "m7_lecture01_en.md", True))
        self.assertEqual(N.resolve("m7_lecture01", "uz", nd), (nd / "m7_lecture01.md", False))
        self.assertIsNone(N.resolve("lecture01", "ru", nd))
        self.assertEqual(N.languages_of("lecture01", nd), ["uz", "en"])
        self.assertEqual((N.primary("lecture01", nd), N.primary("m7_lecture01", nd)), ("uz", "en"))

    def test_a_build_finds_its_file(self):
        self.assertEqual(N.source("lecture98_uz_navoiy", self.nar), (self.nar / "lecture98.md", "uz", False))
        self.assertEqual(N.source("lecture98_en", self.nar), (self.nar / "lecture98.md", "en", False))
        self.assertEqual(N.source("m7_lecture98_en", self.nar), (self.nar / "m7_lecture98_en.md", "en", True))
        with self.assertRaises(FileNotFoundError):
            N.source("lecture98_ru", self.nar)

    def test_the_lines_of_each_file(self):
        t = self.texts()
        self.assertEqual(list(t["uz"]), ["0.0", "1.2", "1.3a", "1.s1a", "2.4"])
        self.assertEqual(t["en"]["1.s1a"], "Six hundred people work at this company.")
        self.assertEqual(t["en"]["1.3a"], "Let's pause for a minute.")
        m7 = self.texts("m7_lecture98")
        self.assertEqual(list(m7["en"]), ["0.0", "1.2", "1.2a", "2.4"])           # the one-language file wins for English
        self.assertEqual(m7["en"]["1.2"], "Let's start with one question (UK).")
        self.assertEqual(m7["uz"]["1.2"], "Keling, bitta savoldan boshlaymiz.")

    def test_a_skeleton_from_the_bilingual_file(self):
        path = N.create_skeleton("lecture98", "ru", self.nar)
        self.assertEqual(path, self.nar / "lecture98_ru.md")
        text = path.read_text()
        self.assertIn("### Раздел 1 — Why an agent?", text)
        self.assertIn("3a. ⏸ ****", text)                                         # the pause mark is kept
        self.assertIn("- s1a ****", text)
        rows = N.rows(path, "ru", True)
        self.assertEqual([k for k, *_ in rows], list(self.texts()["uz"]))          # the primary's ids, in its order
        self.assertEqual({t for _, _, t, _ in rows}, {""})                         # every line empty
        self.assertEqual(N.resolve("lecture98", "ru", self.nar), (path, True))
        self.assertEqual(N.languages_of("lecture98", self.nar), ["uz", "en", "ru"])
        self.assertEqual(N.source("lecture98_ru", self.nar), (path, "ru", True))
        with self.assertRaises(ValueError):
            N.create_skeleton("lecture98", "ru", self.nar)                         # no second skeleton over a draft
        with self.assertRaises(ValueError):
            N.create_skeleton("lecture98", "en", self.nar)                         # nor over the English gloss
        with self.assertRaises(KeyError):
            N.create_skeleton("lecture98", "xx", self.nar)

    def test_a_skeleton_from_the_one_language_file_and_the_kit_can_read_the_lines_written_into_it(self):
        path = N.create_skeleton("m7_lecture98", "ru", self.nar)
        self.assertEqual([k for k, *_ in N.rows(path, "ru", True)], ["0.0", "1.2", "1.2a", "2.4"])   # English is the primary
        N.set_line(path, "ru", True, "1.2a", "Строка только для английского.")
        N.set_line(path, "ru", True, "2.4", "Что такое инструмент?")
        N.set_line(path, "ru", True, "0.0", "Здравствуйте.")
        code = ("import json, lecture_kit as k, sys; l, h = k.parse(open(sys.argv[1]).read(), single='ru'); "
                "print(json.dumps([l, h], ensure_ascii=False))")
        r = subprocess.run([sys.executable, "-c", code, str(path)], cwd=HERE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr[-600:])
        lines, heads = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertEqual(lines, {"0.0": {"ru": "Здравствуйте."}, "1.2a": {"ru": "Строка только для английского."},
                                 "2.4": {"ru": "Что такое инструмент?"}})            # the empty line 1.2 is not a line yet
        self.assertEqual(heads["1"], {"ru": "Раздел 1 · Why an agent?"})

    def test_depth_lines_and_pauses_in_a_one_language_file_are_found_and_written(self):
        path = N.create_skeleton("lecture98", "ru", self.nar)
        N.set_line(path, "ru", True, "1.s1a", "В компании работают шестьсот человек.")
        N.set_line(path, "ru", True, "1.3a", "Остановимся на минуту.")
        self.assertIn("- s1a **В компании работают шестьсот человек.**", path.read_text())
        self.assertIn("3a. ⏸ **Остановимся на минуту.**", path.read_text())


class LineStatus(Scratch):
    def test_empty_draft_approved_then_a_text_change_is_a_draft(self):
        N.create_skeleton("lecture98", "ru", self.nar)
        self.assertEqual(self.state("lecture98", "ru", "1.2")["state"], "empty")
        with self.assertRaises(ValueError):
            LS.approve(self.c, "lecture98", "ru", "line", "1.2", self.texts())          # an empty line cannot be approved
        path = self.nar / "lecture98_ru.md"
        N.set_line(path, "ru", True, "1.2", "Начнём с одного вопроса.")
        self.assertEqual(self.state("lecture98", "ru", "1.2")["state"], "draft")       # text, no approval
        LS.approve(self.c, "lecture98", "ru", "line", "1.2", self.texts())
        self.assertEqual(self.state("lecture98", "ru", "1.2")["state"], "approved")
        N.set_line(path, "ru", True, "1.2", "Начнём с одного вопроса!")                # the file changed behind the studio's back
        self.assertEqual(self.state("lecture98", "ru", "1.2")["state"], "draft")
        self.assertEqual(S.approvals(self.c, "lecture98", "ru", "line")["1.2"]["text_hash"], LS.digest("Начнём с одного вопроса."))

    def test_another_languages_change_makes_it_need_an_update_and_still_fine_clears_it(self):
        N.create_skeleton("lecture98", "ru", self.nar)
        path = self.nar / "lecture98_ru.md"
        N.set_line(path, "ru", True, "1.2", "Начнём с одного вопроса.")
        LS.approve(self.c, "lecture98", "ru", "line", "1.2", self.texts())
        old_uz = self.texts()["uz"]["1.2"]
        row = S.approvals(self.c, "lecture98", "ru", "line")["1.2"]
        self.assertEqual(row["sources"], {"uz": old_uz, "en": "Let's start with one question."})     # both sources kept as text
        LS.save_line(self.c, "lecture98", "uz", "1.2", "Keling, bitta savol bilan boshlaymiz.", self.nar)
        st = self.state("lecture98", "ru", "1.2")
        self.assertEqual(st["state"], "needs_update")
        self.assertEqual(st["changed"], {"uz": {"old": old_uz, "new": "Keling, bitta savol bilan boshlaymiz."}})   # the diff to show
        self.assertEqual(self.state("lecture98", "uz", "1.2")["state"], "approved")                  # the line just saved
        LS.still_fine(self.c, "lecture98", "ru", "line", "1.2", self.texts())
        self.assertEqual(self.state("lecture98", "ru", "1.2"), {"state": "approved", "changed": {}})
        with self.assertRaises(ValueError):
            LS.still_fine(self.c, "lecture98", "ru", "line", "1.2", self.texts())                   # nothing left to confirm

    def test_the_other_language_is_not_a_source_until_it_had_text(self):
        """Russian drafted after Uzbek was approved is a translation, not a change to it."""
        LS.approve(self.c, "lecture98", "uz", "line", "1.2", self.texts())
        N.create_skeleton("lecture98", "ru", self.nar)
        N.set_line(self.nar / "lecture98_ru.md", "ru", True, "1.2", "Начнём.")
        self.assertEqual(self.state("lecture98", "uz", "1.2")["state"], "approved")
        N.set_line(self.nar / "lecture98_ru.md", "ru", True, "1.2", "Начнём с вопроса.")
        self.assertEqual(self.state("lecture98", "uz", "1.2")["state"], "approved")

    def test_whitespace_does_not_change_a_hash(self):
        self.assertEqual(LS.digest("a  b\n"), LS.digest(" a b"))
        self.assertNotEqual(LS.digest("a b"), LS.digest("a c"))

    def test_counts(self):
        LS.approve(self.c, "lecture98", "uz", "line", "1.2", self.texts())
        LS.approve(self.c, "lecture98", "uz", "line", "0.0", self.texts())
        LS.save_line(self.c, "lecture98", "en", "0.0", "Hello, everyone.", self.nar)            # flags the Uzbek line 0.0
        sts = LS.statuses(self.c, "lecture98", "uz", "line", self.texts())
        self.assertEqual(LS.counts(sts), {"approved": 1, "needs_update": 1, "draft": 3, "empty": 0, "total": 5})

    def test_save_edit_writes_the_file_through_narration_edit_and_leaves_the_other_language(self):
        before = (self.nar / "lecture98.md").read_text()
        out = R.act(self.c, "lecture98", "uz", "save", "line", "1.2", "Keling, bitta savol bilan o'tamiz.", self.nar)
        self.assertEqual(out["item"]["text"], "Keling, bitta savol bilan oʻtamiz.")             # apostrophe fixed on the way in
        self.assertEqual(out["item"]["state"], "approved")
        after = (self.nar / "lecture98.md").read_text()
        self.assertEqual(after.replace("Keling, bitta savol bilan oʻtamiz.", "Keling, bitta savoldan boshlaymiz."), before)
        self.assertIn("   *Let's start with one question.*", after)                             # its English gloss is as it was
        self.assertEqual(out["counts"]["approved"], 1)
        out = R.act(self.c, "lecture98", "en", "save", "line", "1.2", "Let's begin with a question.", self.nar)
        self.assertIn("**Keling, bitta savol bilan oʻtamiz.**\n   *Let's begin with a question.*", (self.nar / "lecture98.md").read_text())
        uz = R.review(self.c, "lecture98", "uz", self.nar)["lines"][1]
        self.assertEqual((uz["state"], list(uz["changed"])), ("needs_update", ["en"]))          # saving English flagged the Uzbek
        R.act(self.c, "lecture98", "uz", "fine", "line", "1.2", None, self.nar)
        self.assertEqual(R.review(self.c, "lecture98", "uz", self.nar)["lines"][1]["state"], "approved")

    def test_refusals(self):
        with self.assertRaises(KeyError):
            R.act(self.c, "lecture98", "uz", "approve", "line", "9.9", None, self.nar)
        with self.assertRaises(ValueError):
            R.act(self.c, "lecture98", "uz", "save", "line", "1.2", "Келинг", self.nar)         # Cyrillic in Uzbek: not written
        with self.assertRaises(ValueError):
            R.act(self.c, "lecture98", "uz", "save", "line", "1.2", "a ** b", self.nar)
        with self.assertRaises(ValueError):
            R.act(self.c, "lecture98", "uz", "fine", "line", "1.2", None, self.nar)             # not waiting for an update
        with self.assertRaises(ValueError):
            R.act(self.c, "lecture98", "uz", "shout", "line", "1.2", None, self.nar)
        self.assertEqual(self.texts()["uz"]["1.2"], "Keling, bitta savoldan boshlaymiz.")
        with self.assertRaises(FileNotFoundError):
            LS.save_line(self.c, "lecture98", "ru", "1.2", "x", self.nar)                       # a language not added yet


class LabelStatus(Scratch):
    STEM = "lecture04"

    def key(self):
        return LS.label_keys(self.STEM)[0][0]

    def forms(self, key, lang):
        return LB.book(self.STEM)[key].get(lang)

    def test_the_lectures_labels_come_from_the_scenes(self):
        keys = dict(LS.label_keys(self.STEM))
        self.assertGreater(len(keys), 50)
        self.assertEqual(len(keys), len({k for k, _ in LB.keys_for(self.STEM)} & set(LB.book(self.STEM))))
        m7 = dict(LS.label_keys("m7_lecture01"))
        self.assertIn("m7_title", m7)                                        # from the draft labels file
        self.assertEqual(len(m7), 102)

    def test_approve_edit_other_language_still_fine(self):
        key, st = self.key(), lambda lang="uz": LS.label_statuses(self.c, self.STEM, lang)[2]
        old_en = LS.label_text(self.forms(key, "en"))
        self.assertEqual(st()[key]["state"], "draft")
        by = LS.label_statuses(self.c, self.STEM, "uz")[1]
        LS.approve(self.c, self.STEM, "uz", "label", key, by)
        self.assertEqual(st()[key]["state"], "approved")
        self.assertEqual(S.approvals(self.c, self.STEM, "uz", "label")[key]["sources"]["en"], old_en)
        # a Russian form the instructor edits in: written to labels.yaml (the scratch copy), approved
        LS.save_label(self.c, self.STEM, "ru", key, "первая\nвторая")
        self.assertEqual(self.forms(key, "ru"), ["первая", "вторая"])
        self.assertEqual(st("ru")[key]["state"], "approved")
        # the English label changes: the Uzbek and the Russian one need an update
        LS.save_label(self.c, self.STEM, "en", key, old_en + " changed")
        self.assertEqual(self.forms(key, "en"), old_en + " changed" if "\n" not in old_en else self.forms(key, "en"))
        for lang in ("uz", "ru"):
            s = st(lang)[key]
            self.assertEqual((s["state"], list(s["changed"])), ("needs_update", ["en"]), lang)
        self.assertEqual(st("uz")[key]["changed"]["en"], {"old": old_en, "new": old_en + " changed"})
        LS.still_fine(self.c, self.STEM, "uz", "label", key, LS.label_statuses(self.c, self.STEM, "uz")[1])
        self.assertEqual(st("uz")[key]["state"], "approved")
        self.assertEqual(st("ru")[key]["state"], "needs_update")

    def test_saving_a_label_rewrites_labels_yaml_in_order_with_its_comments_and_never_the_real_file(self):
        real = hashlib.sha1((HERE / "narration" / "labels.yaml").read_bytes()).hexdigest()
        key = self.key()
        before = (self.nar / "labels.yaml").read_text()
        LS.save_label(self.c, self.STEM, "ru", key, "слово")
        after = (self.nar / "labels.yaml").read_text()
        self.assertEqual(yaml.safe_load(after)[key]["ru"], "слово")
        a, b = before.splitlines(), after.splitlines()
        self.assertEqual([x for x in b if x != '  ru: "слово"'], a)                         # only that one line was added
        self.assertEqual(hashlib.sha1((HERE / "narration" / "labels.yaml").read_bytes()).hexdigest(), real)

    def test_a_draft_label_is_written_to_the_draft_file_keeping_its_header_and_order(self):
        d = self.nar / "drafts" / "m7_l01" / "labels.yaml"
        before = d.read_text()
        LS.save_label(self.c, "m7_lecture01", "ru", "m7_title", "Модуль 7 · Лекция 1")
        after = d.read_text()
        self.assertTrue(after.startswith(before.split("\nm7_title:")[0]))                   # the header comments
        self.assertEqual(list(yaml.safe_load(after)), list(yaml.safe_load(before)))         # the keys' order
        self.assertEqual(yaml.safe_load(after)["m7_title"]["ru"], "Модуль 7 · Лекция 1")
        self.assertEqual(after.replace('  ru: "Модуль 7 · Лекция 1"\n', ""), before)
        LS.save_label(self.c, "m7_lecture01", "ru", "m7_title", "")                         # no forms: the language is removed
        self.assertEqual(d.read_text(), before)

    def test_label_refusals(self):
        with self.assertRaises(ValueError):
            LS.save_label(self.c, self.STEM, "uz", self.key(), "{n} ta")
        with self.assertRaises(KeyError):
            LS.save_label(self.c, self.STEM, "uz", "no_such_label", "x")

    def test_the_writer_reproduces_the_real_files(self):
        """Writing a label back changes nothing else: the files are what labels.py would have written."""
        main = yaml.safe_load((self.nar / "labels.yaml").read_text())
        before = (self.nar / "labels.yaml").read_text()
        LB.write(main, LB.uses() + [u for u in LB.uses(LB.ac_files()) if u[0] in main])
        self.assertEqual((self.nar / "labels.yaml").read_text(), before)
        d = self.nar / "drafts" / "m7_l01" / "labels.yaml"
        before = d.read_text()
        LB.write_draft(d, yaml.safe_load(before))
        self.assertEqual(d.read_text(), before)


class Checks(unittest.TestCase):
    def kinds(self, lang, text, kind="line"):
        return [m.split(":")[0].split(" in ")[0] for _, m in R.checks(lang, text, kind)]

    def test_latin_script_languages_flag_cyrillic(self):
        self.assertEqual(R.checks("en", "Hello"), [])
        self.assertEqual(R.checks("en", "Hello мир")[0][0], "warn")
        self.assertEqual(R.checks("tr", "Merhaba д")[0][0], "warn")

    def test_uzbek_apostrophes_and_letters(self):
        self.assertEqual(R.checks("uz", "Oʻzbek va maʼlumot"), [])
        self.assertEqual([m for _, m in R.checks("uz", "O'zbek")], ["oʻ and gʻ are written with ʻ (U+02BB)"])
        self.assertEqual([m for _, m in R.checks("uz", "ma'lumot")], ["the tutuq belgisi is ʼ (U+02BC)"])
        self.assertIn("warn", [lv for lv, _ in R.checks("uz", "Қелинг")])
        self.assertTrue(R.checks("uz", "bugün")[0][1].startswith("Turkish letters"))

    def test_cyrillic_script_languages_hint_at_latin_words(self):
        self.assertEqual(R.checks("ru", "Привет, мир"), [])
        hint = R.checks("ru", "Это tool для агента, LLM и ReAct")
        self.assertEqual([lv for lv, _ in hint], ["hint"])
        self.assertIn("tool", hint[0][1])
        self.assertNotIn("LLM", hint[0][1])                                  # technical terms are not flagged

    def test_digits_are_a_hint_for_every_language_but_not_for_labels(self):
        for lang in ("uz", "en", "ru", "ko"):
            self.assertEqual([lv for lv, _ in R.checks(lang, "Bu 12 ta")], ["hint"], lang)
        self.assertEqual(R.checks("en", "Step 2", "label"), [])
        self.assertEqual(R.checks("en", ""), [])


class Seed(Scratch):
    def setUp(self):
        super().setUp()
        for f in HERE.joinpath("narration").glob("lecture*.md"):
            shutil.copy(f, self.nar / f.name)
        shutil.copy(HERE / "narration" / "m7_lecture01.md", self.nar)
        shutil.copy(HERE / "narration" / "m7_lecture01_en.md", self.nar)

    def test_seed_approves_the_uzbek_of_lectures_1_to_5_and_nothing_else_and_twice_changes_nothing(self):
        report = SEED.seed(self.c, self.nar)
        rows = self.c.execute("select lecture, lang, kind, count(*) n from line_status group by 1, 2, 3").fetchall()
        self.assertEqual({(r["lecture"], r["lang"]) for r in rows}, {(f"lecture0{n}", "uz") for n in range(1, 6)})
        self.assertEqual({r["kind"] for r in rows}, {"line", "label"})
        got = {(r["lecture"], r["kind"]): r["n"] for r in rows}
        for n in range(1, 6):
            stem = f"lecture0{n}"
            self.assertEqual(got[(stem, "line")], len(self.texts(stem)["uz"]), stem)       # every Uzbek line
            self.assertEqual(got[(stem, "label")], len(LS.label_keys(stem)), stem)         # every label the lecture shows
            sts = LS.statuses(self.c, stem, "uz", "line", self.texts(stem))
            self.assertEqual(LS.counts(sts)["approved"], len(self.texts(stem)["uz"]))
            en = LS.statuses(self.c, stem, "en", "line", self.texts(stem))
            self.assertEqual(LS.counts(en)["approved"], 0)                                   # the gloss is not approved
        self.assertEqual(sum(r[0] for r in report.values()), sum(got.values()))
        snapshot = [tuple(r) for r in self.c.execute("select * from line_status order by lecture, lang, kind, key")]
        again = SEED.seed(self.c, self.nar)
        self.assertEqual(sum(r[0] for r in again.values()), 0)
        self.assertEqual([tuple(r) for r in self.c.execute("select * from line_status order by lecture, lang, kind, key")], snapshot)

    def test_a_rerun_leaves_a_line_changed_since_alone(self):
        SEED.seed(self.c, self.nar)
        path, lang, single = N.source("lecture01_uz_navoiy", self.nar)
        key = next(iter(N.texts(path, lang, single)))
        N.set_line(path, "uz", single, key, N.texts(path, lang, single)[key] + " Yangi gap.")
        SEED.seed(self.c, self.nar)
        self.assertEqual(self.state("lecture01", "uz", key)["state"], "draft")             # not approved again by a rerun

    def test_seed_flags_the_uzbek_when_the_english_gloss_is_edited_later(self):
        SEED.seed(self.c, self.nar)
        key = "1.2"
        LS.save_line(self.c, "lecture01", "en", key, "A different gloss.", self.nar)
        s = self.state("lecture01", "uz", key)
        self.assertEqual((s["state"], list(s["changed"])), ("needs_update", ["en"]))


class Lectures(Scratch):
    """What the lecture page and the editor show."""
    def test_stems_langs_and_summary(self):
        root = Path(self.tmp.name) / "out"
        (root / "lecture98_uz_navoiy").mkdir(parents=True)
        (root / "lecture98_uz_navoiy" / "lecture98_uz_navoiy.mp4").write_bytes(b"v")
        (root / "m7_lecture98_en").mkdir()
        (root / "lecture01").mkdir()                                                            # not a build
        self.assertEqual(R.stems(root, 0, self.nar), ["lecture98"])
        self.assertEqual(R.stems(root, 7, self.nar), ["m7_lecture98"])
        self.assertEqual(R.lecture_langs(root, "lecture98", self.nar), ["uz", "en"])
        self.assertEqual(R.lecture_langs(root, "m7_lecture98", self.nar), ["en", "uz"])        # the primary language first
        N.create_skeleton("lecture98", "ru", self.nar)
        self.assertEqual(R.lecture_langs(root, "lecture98", self.nar), ["uz", "en", "ru"])
        s = R.summary(self.c, root, "lecture98", "uz", self.nar)
        self.assertEqual((s["lines"]["total"], s["lines"]["draft"], s["builds"][0]["built"]), (5, 5, True))
        self.assertFalse(s["ready"])
        ru = R.summary(self.c, root, "lecture98", "ru", self.nar)
        self.assertEqual((ru["lines"]["empty"], ru["builds"], ru["ready"]), (5, [], False))
        self.assertIn("5 narration lines are not drafted", ru["missing"])

    def test_readiness_counts_the_missing_label_forms(self):
        lines = {"approved": 91, "needs_update": 0, "draft": 0, "empty": 0, "total": 91}
        labels = {"approved": 68, "needs_update": 0, "draft": 0, "empty": 34, "total": 102, "missing": 34}
        ok, why = R.readiness(lines, labels, "ru")
        self.assertFalse(ok)
        self.assertEqual(why, ["34 labels have no Russian form"])
        self.assertEqual(R.readiness(dict(lines, approved=90, draft=1), labels, "ru")[1],
                         ["the narration is not approved (90 of 91 lines)", "34 labels have no Russian form"])
        self.assertEqual(R.readiness(lines, dict(labels, empty=0, missing=0, approved=102), "ru"), (True, []))

    def test_a_build_whose_video_lacks_an_approved_line_is_out_of_date(self):
        root = Path(self.tmp.name) / "out"
        b = root / "lecture98_uz_navoiy" / "presenter"
        b.mkdir(parents=True)
        (b.parent / "lecture98_uz_navoiy.mp4").write_bytes(b"v")
        t = self.texts()["uz"]
        (b / "lines.json").write_text(json.dumps([[float(i), x, [], 0] for i, x in enumerate(t.values())]))
        for k in t:
            LS.approve(self.c, "lecture98", "uz", "line", k, self.texts())
        self.assertEqual(R.summary(self.c, root, "lecture98", "uz", self.nar)["builds"][0]["stale"], [])
        LS.save_line(self.c, "lecture98", "uz", "2.4", "Vosita nimaligini koʻramiz.", self.nar)       # approved, but not in the video
        self.assertEqual(R.summary(self.c, root, "lecture98", "uz", self.nar)["builds"][0]["stale"], ["2.4"])

    def test_the_editors_other_languages_and_per_line_status(self):
        root = Path(self.tmp.name) / "out"
        b = root / "lecture98_uz_navoiy" / "presenter"
        b.mkdir(parents=True)
        t = self.texts()["uz"]
        (b / "lines.json").write_text(json.dumps([[float(i), x, [], 0] for i, x in enumerate(t.values())]))
        N.create_skeleton("lecture98", "ru", self.nar)
        LS.approve(self.c, "lecture98", "uz", "line", "1.2", self.texts())
        LS.save_line(self.c, "lecture98", "en", "1.2", "Let's begin.", self.nar)
        out = R.editor_langs(self.c, root, "lecture98_uz_navoiy", self.nar)
        self.assertEqual([o["lang"] for o in out["others"]], ["en", "ru"])
        self.assertEqual([o["build"] for o in out["others"]], [None, None])                      # neither has an editor: review links
        self.assertEqual(out["others"][1]["review"], "/narration?lecture=lecture98&lang=ru")
        one = out["lines"]["1"]
        self.assertEqual((one["key"], one["state"], list(one["changed"])), ("1.2", "needs_update", ["en"]))
        self.assertEqual([(o["lang"], o["state"]) for o in one["others"]], [("en", "approved")])  # ru is empty: not listed
        self.assertEqual(one["others"][0]["review"], "/narration?lecture=lecture98&lang=en#line=1.2")


NODE = shutil.which("node")


@unittest.skipUnless(NODE, "node is not installed")
class ReviewPage(Scratch):
    """studio/narration.html and static/narration/review.js, run on fake DOM elements against the real payload."""
    DRIVER = """
const vm = require('vm'), fs = require('fs'), assert = require('assert');
const payload = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const els = {};
const el = id => els[id] || (els[id] = {id, innerHTML: '', textContent: '', className: '', style: {}, classList: {toggle(){}, add(){ els[id].target = true; }}, scrollIntoView(){ els[id].scrolled = true; }});
const ctx = {document: {getElementById: el}, location: {hash: process.argv[4] || ''}, localStorage: {getItem: () => null, setItem(){}},
  fetch: async () => ({ok: true, status: 200, json: async () => payload}), setTimeout, clearTimeout, LECTURE: 'lecture98', LANG: 'uz'};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), ctx);
const run = code => vm.runInContext(code, ctx);
(async () => {
  await new Promise(r => setTimeout(r, 20));
  const out = {};
  out.list = els.list.innerHTML; out.counts = els.counts.textContent; out.filters = els.filters.innerHTML; out.ref = els.ref.innerHTML;
  out.langs = els.langs.innerHTML;
  run("setFilter('needs_update')"); out.needs = els.list.innerHTML;
  run("setFilter('empty')"); out.empty = els.list.innerHTML;
  run("setFilter('open')"); out.open = els.list.innerHTML;
  run("setTab('labels')"); out.labels = els.list.innerHTML; out.labelCounts = els.counts.textContent;
  out.diff = run("wordDiff('a b c', 'a x c')");
  out.scrolled = Object.keys(els).filter(k => els[k].scrolled && els[k].target);
  console.log(JSON.stringify(out));
})();
"""

    def run_page(self, lang="uz", stem="lecture98", hash_=""):
        payload = R.review(self.c, stem, lang, self.nar)
        d = Path(self.tmp.name)
        (d / "payload.json").write_text(json.dumps(payload))
        (d / "run.js").write_text(self.DRIVER.replace("'lecture98'", repr(stem)).replace("'uz'", repr(lang)))
        r = subprocess.run([NODE, str(d / "run.js"), str(HERE / "studio/static/narration/review.js"), str(d / "payload.json"), hash_],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])
        return json.loads(r.stdout.strip().splitlines()[-1])

    def test_the_template_is_filled_and_its_files_exist(self):
        page = (HERE / "studio" / "narration.html").read_text()
        for ph in ("__LECTURE__", "__LANG__", "__MODULE__", "__TITLE__"):
            self.assertIn(ph, page)
        page = page.replace("__LECTURE__", "lecture98").replace("__LANG__", "uz").replace("__MODULE__", "0").replace("__TITLE__", "t")
        self.assertNotIn("__", page)
        for f in re.findall(r'(?:src|href)="/studio-static/([^"]+)"', page):
            self.assertTrue((HERE / "studio" / "static" / f).is_file(), f)

    def test_the_page_shows_status_chips_the_diff_counts_and_filters(self):
        LS.approve(self.c, "lecture98", "uz", "line", "1.2", self.texts())
        LS.approve(self.c, "lecture98", "uz", "line", "0.0", self.texts())
        LS.save_line(self.c, "lecture98", "en", "1.2", "Let's begin.", self.nar)
        N.create_skeleton("lecture98", "ru", self.nar)
        o = self.run_page()
        self.assertIn('class="item approved" id="line-0.0"', o["list"])
        self.assertIn('class="item needs_update" id="line-1.2"', o["list"])
        self.assertIn("en changed", o["list"])
        self.assertIn("<del>start</del>", o["list"])                                  # the English diff: old and new words
        self.assertIn("<mark>begin.</mark>", o["list"])
        self.assertIn('class="item draft" id="line-1.s1a"', o["list"])
        self.assertEqual(o["counts"], "approved 1 / 5 · 1 need update · 3 draft")
        self.assertIn("not approved 4", o["filters"])
        self.assertEqual(o["needs"].count('class="item '), 1)                          # the filters
        self.assertEqual(o["empty"], '<p class="dim">nothing here with this filter</p>')
        self.assertEqual(o["open"].count('class="item '), 4)
        self.assertIn("1-boʻlim · Nega agent?", o["list"])                                # the section headings
        self.assertIn('<option value="en" selected>', o["ref"])                                     # the reference languages: not Uzbek itself
        self.assertNotIn('value="uz"', o["ref"])
        self.assertIn("<mark>x</mark>", o["diff"])
        self.assertIn("/narration?lecture=lecture98&lang=ru", o["langs"])               # a tab for the new language

    def test_a_skeleton_language_has_only_empty_lines_and_the_reference_text_beside_them(self):
        N.create_skeleton("lecture98", "ru", self.nar)
        o = self.run_page("ru")
        self.assertEqual(o["list"].count('class="item empty"'), 5)
        self.assertEqual(o["counts"], "approved 0 / 5 · 5 empty")
        self.assertIn("Keling, bitta savoldan boshlaymiz.", o["list"])                 # the reference language (Uzbek, the primary)
        self.assertEqual(o["empty"].count('class="item empty"'), 5)
        self.assertRegex(o["labelCounts"], r"^approved 0 / \d+ · \d+ empty$")

    def test_a_language_with_no_narration_offers_the_skeleton(self):
        o = self.run_page("de")
        self.assertIn("create the empty skeleton", o["list"])

    def test_the_hash_opens_the_line(self):
        o = self.run_page(hash_="#line=1.2")
        self.assertEqual(o["scrolled"], ["line-1.2"])                                      # scrolled to and marked


if __name__ == "__main__":
    unittest.main()
