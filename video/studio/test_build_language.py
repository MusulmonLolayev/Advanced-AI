"""Building a lecture video in a language (phase 2): a single-language narration merged into the kits' lines by id, the
preflight on a fake lecture (what a render would stop on), the registry's fonts and voice guard, the draft watermark
decision (Uzbek is strict), and the build job's steps (outside tools stubbed).

    uv run python -m unittest discover -s studio -p 'test_build_language.py' -t .        (from video/)
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import yaml

import builds as B
import check_lang as CL
import cuescan
import drafts as D
import labels as LB
import languages as LG
import lecture_kit as K
from studio import buildlang as BL
from studio import linestatus as LS
from studio import narration_edit as N
from studio import store as S
from studio import test_languages as TL

HERE = Path(__file__).resolve().parents[1]
RU_ONE = """## Lecture opening
0. **Здравствуйте, друзья.**
### Раздел 1 — Зачем агент?
2. **Начнём с одного вопроса.**
3a. ⏸ ****
- s1a **В компании работают шестьсот человек.** ▸ a picture
### Раздел 2 — Инструменты
4. **Что такое инструмент?**
"""


class Merge(TL.Scratch):
    """narration/<stem>_<lang>.md is merged into the bilingual lines by id; the cue overrides file is read beside it."""
    def setUp(self):
        super().setUp()
        (self.nar / "lecture98_ru.md").write_text(RU_ONE)
        self.old = os.environ.get("NARRATION_DIR")
        os.environ["NARRATION_DIR"] = str(self.nar)

    def tearDown(self):
        if self.old is None:
            os.environ.pop("NARRATION_DIR")
        else:
            os.environ["NARRATION_DIR"] = self.old
        super().tearDown()

    def test_a_single_language_file_is_merged_by_line_id(self):
        lines, heads = K.parse((self.nar / "lecture98.md").read_text())
        before = json.dumps(lines, sort_keys=True), json.dumps(heads, sort_keys=True)
        self.assertTrue(K.add_language(lines, heads, "lecture98", "ru"))
        self.assertEqual(lines["0.0"]["ru"], "Здравствуйте, друзья.")
        self.assertEqual(lines["1.s1a"]["ru"], "В компании работают шестьсот человек.")
        self.assertNotIn("ru", lines["1.3a"])                                    # the empty line is left out, not an error
        self.assertEqual(heads[2]["ru"], "Раздел 2 · Инструменты")
        for k, v in lines.items():                                              # uz and en are as they were
            self.assertEqual({l: v[l] for l in ("uz", "en")}, json.loads(before[0])[k])
        self.assertEqual(heads[1]["uz"], json.loads(before[1])["1"]["uz"])

    def test_no_file_no_merge_and_an_unknown_line_is_an_error(self):
        lines, heads = K.parse((self.nar / "lecture98.md").read_text())
        self.assertFalse(K.add_language(lines, heads, "lecture98", "tr"))
        (self.nar / "lecture98_tr.md").write_text("## Lecture opening\n9. **Merhaba.**\n")
        with self.assertRaisesRegex(AssertionError, "not in the lecture"):
            K.add_language(lines, heads, "lecture98", "tr")

    def test_the_scene_says_a_line_or_names_what_is_missing(self):
        class Scene(K.LectureScene):
            NARRATION = {"1.2": {"uz": "Salom. Dunyo.", "en": "Hello. World."}, "1.3": {"uz": "Faqat uz."}}
            PRIMARY, OVERRIDES = "uz", {"1.2": {"Hello": "x"}}
        s = object.__new__(Scene)
        self.assertEqual(s.line("1.2"), "Hello. World.")
        with self.assertRaisesRegex(K.NoForm, r"no en narration for line 1.3 \(empty or missing in narration/\*_en.md\)"):
            s.line("1.3")
        ref = s.cue_ref("Hello. World.")                                        # found by the text (a line voiced by hand)
        self.assertEqual((ref.key, ref.primary, ref.overrides), ("1.2", "uz", {"Hello": "x"}))
        s._key = "1.2"                                                          # or remembered by say()
        self.assertEqual(s.cue_ref("Hello. World.").texts["uz"], "Salom. Dunyo.")
        self.assertIsNone(s.cue_ref("a line nobody knows"))

    def test_overrides_file_is_read_by_stem_and_language(self):
        (self.nar / "lecture98_ru.cues.yaml").write_text("'1.2': {Bravo: Браво}\n")
        self.assertEqual(K.cue_overrides("lecture98", "ru"), {"1.2": {"Bravo": "Браво"}})
        self.assertEqual(K.cue_overrides("lecture98", "tr"), {})

    def test_the_primary_language(self):
        self.assertEqual((K.primary_language("lecture03"), K.primary_language("m7_lecture01"), K.primary_language("agents_course")),
                         ("uz", "en", "en"))


FAKE_SCENE = '''
from lecture98_kit import *

class S00(Scene):
    def construct(self):
        a = txt(label("fake_word"))
        b = txt(label("fake_has_ru"))
        c = {"en": "Yes", "uz": "Ha"}
        with self.say("1.2") as (tr, t):
            self.cue(tr, t, {"en": "next", "uz": "Keyingi"})
            self.cue(tr, t, {"en": "never said", "uz": "aytilmagan"})
            self.cue(tr, t, 1)
'''
FAKE_BI = """## Lecture opening
0. **Salom.**
   *Hello.*
### 1-boʻlim · Section 1 — Bir · One
2. **Birinchi gap. Keyingi gap.**
   *First one. The next one.*
"""
FAKE_RU = """## Lecture opening
0. **Привет.**
### Раздел 1 — Один
2. **Первое предложение. Следующее предложение.**
"""


class Preflight(TL.Scratch):
    """check_lang.preflight on a fake lecture: it lists what a render would stop on."""
    def setUp(self):
        super().setUp()
        self.code = Path(self.tmp.name) / "code"
        self.code.mkdir()
        (self.code / "lecture98_s00.py").write_text(FAKE_SCENE)
        (self.nar / "lecture98.md").write_text(FAKE_BI)
        (self.nar / "lecture98_ru.md").write_text(FAKE_RU)
        (self.nar / "drafts" / "l98").mkdir(parents=True)
        (self.nar / "drafts" / "l98" / "labels.yaml").write_text(
            "fake_word:\n  en: word\n  uz: soʻz\nfake_has_ru:\n  en: has\n  uz: bor\n  ru: есть\n")
        self.patches = [mock.patch.object(cuescan, "HERE", self.code), mock.patch.object(LB, "HERE", self.code),
                        mock.patch.object(LB, "SHARED", ())]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        super().tearDown()

    def test_everything_a_render_would_stop_on_is_listed(self):
        r = CL.preflight("lecture98", "ru", self.nar)
        self.assertIsNone(r["font"])
        self.assertEqual(r["narration"], [])
        self.assertEqual(r["labels"], ["fake_word"])                                     # the one without a ru form
        self.assertEqual(len(r["dicts"]), 1)                                              # the on-screen words, not the cues
        self.assertIn("lecture98_s00.py:", r["dicts"][0])
        self.assertIn("{'en': 'Yes', 'uz': 'Ha'} has no ru form", r["dicts"][0])
        self.assertEqual(len(r["cues"]), 1)                                               # "aytilmagan" is not in the Uzbek line
        self.assertIn("cue 'aytilmagan' not in narration", r["cues"][0])
        sm = CL.summary(r, "ru")
        self.assertEqual(sm, ["1 label has no Russian form", "1 words on screen have no Russian form",
                              "1 cues cannot be placed"])

    def test_the_languages_that_are_complete_pass_apart_from_what_they_lack(self):
        for lang in ("uz", "en"):
            r = CL.preflight("lecture98", lang, self.nar)
            self.assertEqual((r["labels"], r["dicts"]), ([], []), lang)

    def test_empty_missing_and_absent_narration(self):
        (self.nar / "lecture98_ru.md").write_text("## Lecture opening\n0. ****\n### Раздел 1 — Один\n")
        r = CL.preflight("lecture98", "ru", self.nar)
        self.assertEqual(r["narration"], ["line 0.0: empty", "line 1.2: missing"])
        self.assertEqual(r["cues"], [])                                                    # nothing to place them in
        self.assertEqual(CL.preflight("lecture98", "tr", self.nar)["narration"], ["there is no Turkish narration for lecture98"])

    def test_overrides_must_match_and_fix_a_cue(self):
        (self.nar / "lecture98_ru.cues.yaml").write_text(
            "'1.2': {aytilmagan: Следующее, never said: Следующее}\n'9.9': {x: y}\n")
        r = CL.preflight("lecture98", "ru", self.nar)
        self.assertEqual(r["cues"], [])                                                    # the override placed the cue
        self.assertEqual(len(r["overrides"]), 2)                                            # "never said" is in no line; 9.9 does not exist
        self.assertTrue(any("no cue of the line is read by 'never said'" in o for o in r["overrides"]))
        self.assertTrue(any("line 9.9 is not in the lecture" in o for o in r["overrides"]))
        (self.nar / "lecture98_ru.cues.yaml").write_text("'1.2': {aytilmagan: Нигде}\n")
        r = CL.preflight("lecture98", "ru", self.nar)
        self.assertEqual(len(r["overrides"]), 1)
        self.assertIn("'Нигде' is not in the Russian line", r["overrides"][0])

    def test_label_drafts_from_the_environment_count(self):
        d = Path(self.tmp.name) / "scratch_labels"
        d.mkdir()
        (d / "x.yaml").write_text("fake_word:\n  ru: слово\n")
        with mock.patch.dict(os.environ, {"LABEL_DRAFTS": str(d)}):
            self.assertEqual(CL.preflight("lecture98", "ru", self.nar)["labels"], [])

    def test_the_command_line(self):
        env = {k: v for k, v in os.environ.items() if k != "STUDIO_NARRATION"}              # the real narration
        r = subprocess.run([sys.executable, "check_lang.py", "m7_lecture01", "en"], cwd=HERE, capture_output=True, text=True, env=env)
        self.assertEqual((r.returncode, r.stdout.strip().splitlines()[-1]), (0, "m7_lecture01 in English: can be built"), r.stderr[-300:])
        r = subprocess.run([sys.executable, "check_lang.py", "m7_lecture01", "ru"], cwd=HERE, capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stdout, r"there is no Russian narration")
        self.assertEqual(subprocess.run([sys.executable, "check_lang.py", "nonsense", "ru"], cwd=HERE, capture_output=True).returncode, 2)

    def test_every_real_lecture_has_no_stray_language_dict(self):
        """The scene files' {language: …} dicts are all cue phrases: none is a word on screen a new language would lack."""
        for p in self.patches:
            p.stop()
        try:
            for stem in ("lecture01", "lecture02", "lecture03", "lecture04", "lecture05", "m7_lecture01"):
                texts = {l: list(t.values()) for l, t in CL.line_texts(stem, HERE / "narration").items()}
                stray = [d for d in cuescan.language_dicts(stem) if not d["is_cue_arg"] and not cuescan.is_cue_phrase(d["value"], texts)]
                self.assertEqual(stray, [], stem)
        finally:
            for p in self.patches:
                p.start()


class FontsAndVoices(unittest.TestCase):
    def test_the_registry_names_a_font_only_where_the_default_lacks_the_script(self):
        self.assertEqual({c: LG.font(c) for c in LG.CODES},
                         {"uz": None, "en": None, "ru": None, "ko": "Noto Serif KR", "tr": None, "de": None, "fr": None,
                          "es": None, "ar": "Noto Naskh Arabic", "zh": "AR PL UMing CN"})
        self.assertTrue(LG.rtl("ar") and not LG.rtl("ru"))

    def test_a_language_whose_font_is_not_installed_cannot_be_built(self):
        with mock.patch.object(LG, "_FONTS", {"Noto Sans", "Noto Serif KR"}):
            self.assertIsNone(LG.build_problem("ko"))
            self.assertIsNone(LG.build_problem("ru"))
            self.assertRegex(LG.build_problem("zh"), r"font 'AR PL UMing CN' \(Chinese script\) is not installed")
            self.assertRegex(LG.build_problem("ar"), "Noto Naskh Arabic")
        with mock.patch.object(LG, "_FONTS", set()):                  # fc-list missing: nothing can be said, nothing blocks
            self.assertIsNone(LG.build_problem("zh"))

    def test_the_fonts_the_registry_names_are_installed_here(self):
        if not LG.installed_fonts():
            self.skipTest("fc-list is not available")
        self.assertEqual({c: LG.build_problem(c) for c in LG.CODES}, {c: None for c in LG.CODES})

    def test_common_sets_the_text_font_from_the_registry(self):
        for lang, want in (("ko", "Noto Serif KR"), ("zh", "AR PL UMing CN"), ("ar", "Noto Naskh Arabic"), ("ru", None), ("en", None)):
            r = subprocess.run([sys.executable, "-c", "import common; print(common.TEXT_FONT)"], cwd=HERE, capture_output=True,
                               text=True, env=dict(os.environ, LANG_CODE=lang))
            self.assertEqual(r.stdout.strip().splitlines()[-1], str(want), (lang, r.stderr[-300:]))

    def test_the_truncation_guard_counts_words_or_characters(self):
        self.assertEqual(LG.guard("en"), ("words", 5.0))
        self.assertEqual(LG.guard("zh"), ("chars", 6.5))
        t = "one two three four five six seven eight nine ten"
        self.assertEqual(LG.min_seconds("en", t), len(t.split()) / 5.0)        # exactly what common.py computed before
        self.assertEqual(LG.min_seconds("ko", t), 2.0)                          # the Korean rate and trim are untouched
        zh = "今天的问题很简单：什么是智能体，它和普通程序有什么不同？"                   # 4.65 characters a second measured: 6.5 is a floor
        self.assertAlmostEqual(LG.min_seconds("zh", zh), len(zh) / 6.5)
        self.assertLess(LG.min_seconds("zh", zh), len(zh) / 4.65)
        self.assertEqual((LG.rates()["ko"], LG.trims()["ko"]), ("+20%", (0.15, 0.35)))

    def test_every_language_has_what_the_build_and_its_check_need(self):
        for c in LG.CODES:
            self.assertTrue(LG.whisper(c) and LG.draft_word(c) and LG.voices()[c], c)
        self.assertEqual((LG.whisper("ru"), LG.whisper("zh")), ("russian", "chinese"))


class Watermark(TL.Scratch):
    """drafts.decision: clean when every line and label of the language is approved; else a draft, and Uzbek is refused."""
    def approve_all(self, stem, lang):
        by = self.texts(stem)
        for k in by[lang]:
            LS.approve(self.c, stem, lang, "line", k, by)
        keys, by_label, _ = LS.label_statuses(self.c, stem, lang)
        for k, _w in keys:
            if by_label[lang].get(k, "").strip():
                LS.approve(self.c, stem, lang, "label", k, by_label)

    def test_uzbek_is_refused_and_the_others_are_drafts_until_everything_is_approved(self):
        with mock.patch.object(LS, "label_keys", return_value=[]):
            self.assertEqual(D.decision("lecture98", "uz", self.c, self.nar), "refused")
            self.assertEqual(D.decision("lecture98", "en", self.c, self.nar), "draft")
            self.assertEqual(D.decision("lecture98", "ru", self.c, self.nar), "draft")           # no narration at all
            self.assertEqual(D.unapproved("lecture98", "uz", self.c, self.nar)["lines"], 5)
            self.approve_all("lecture98", "uz")
            self.assertEqual(D.decision("lecture98", "uz", self.c, self.nar), "clean")
            self.assertEqual(D.decision("lecture98", "en", self.c, self.nar), "draft")
            # a changed line is unapproved again
            (self.nar / "lecture98.md").write_text((self.nar / "lecture98.md").read_text().replace("Vosita nima?", "Vosita nimadir?"))
            self.assertEqual(D.decision("lecture98", "uz", self.c, self.nar), "refused")

    def test_the_unapproved_count_is_lines_plus_labels_not_total(self):
        with mock.patch.object(LS, "label_keys", return_value=[]):
            self.approve_all("lecture98", "uz")
            u = D.unapproved("lecture98", "uz", self.c, self.nar)
            self.assertEqual((u["lines"], u["labels"]), (0, 0))
            self.assertEqual(u["total"], 5)                          # every item: not what is left to approve

    def test_a_line_the_instructor_wrote_does_not_tag_but_another_unapproved_line_does(self):
        with mock.patch.object(LS, "label_keys", return_value=[]):
            self.approve_all("lecture98", "uz")
            by = self.texts("lecture98")["uz"]
            k1, k2 = list(by)[:2]
            path = self.nar / "lecture98.md"
            path.write_text(path.read_text().replace(by[k1], by[k1] + " Yangi."))     # rewritten in the studio
            path.write_text(path.read_text().replace(by[k2], by[k2] + " Boshqa."))    # changed by hand, nobody approved
            own = {k1: by[k1] + " Yangi."}
            self.assertEqual(D.unapproved("lecture98", "uz", self.c, self.nar)["lines"], 2)
            self.assertEqual(D.unapproved("lecture98", "uz", self.c, self.nar, own)["lines"], 1)   # only k2 is left
            self.assertEqual(D.decision("lecture98", "uz", self.c, self.nar, own), "refused")
            own[k2] = by[k2] + " Boshqa."
            self.assertEqual(D.decision("lecture98", "uz", self.c, self.nar, own), "clean")
            own[k2] = "some other text"                                # text differs from the file: no pass
            self.assertEqual(D.unapproved("lecture98", "uz", self.c, self.nar, own)["lines"], 1)

    def test_tagged_reads_the_own_lines_from_the_environment(self):
        with mock.patch.object(LS, "label_keys", return_value=[]):
            self.approve_all("lecture98", "uz")
            by = self.texts("lecture98")["uz"]
            k1 = list(by)[0]
            path = self.nar / "lecture98.md"
            path.write_text(path.read_text().replace(by[k1], by[k1] + " Yangi."))
            self.c.commit()
            env = {"STUDIO_DB": str(Path(self.tmp.name) / "studio.sqlite"), "NARRATION_DIR": str(self.nar)}
            with mock.patch.dict(os.environ, env):
                self.assertTrue(D.tagged("lecture98", "uz"))
                with mock.patch.dict(os.environ, {"DRAFT_OWN_LINES": json.dumps({k1: by[k1] + " Yangi."})}):
                    self.assertFalse(D.tagged("lecture98", "uz"))
                with mock.patch.dict(os.environ, {"DRAFT_OWN_LINES": "not json"}):
                    self.assertTrue(D.tagged("lecture98", "uz"))

    def test_a_render_tags_every_unclean_build_and_a_missing_database_counts_as_unapproved(self):
        with mock.patch.dict(os.environ, {"STUDIO_DB": str(Path(self.tmp.name) / "nope.sqlite"), "NARRATION_DIR": str(self.nar)}):
            self.assertTrue(D.tagged("lecture98", "uz"))
            self.assertTrue(D.tagged("lecture98", "ru"))
        with mock.patch.object(D, "decision", side_effect=RuntimeError("locked")):
            self.assertTrue(D.tagged("lecture98", "ru"))
        with mock.patch.object(D, "decision", return_value="clean"):
            self.assertFalse(D.tagged("lecture98", "ru"))

    def test_the_m7_scenes_tag_themselves_and_the_base_scene_tags_new_languages_only(self):
        src = (HERE / "m7_lecture01_kit.py").read_text()
        self.assertIn('DRAFT = drafts.tagged("m7_lecture01", LANG)', src)
        self.assertIn("DRAFT_TAG = False", src)                                 # not doubled by the base scene's registry tag
        kit = (HERE / "lecture_kit.py").read_text()
        self.assertIn('LANG not in ("uz", "en") and drafts.tagged(self.STEM, LANG)', kit)    # en and uz render as they always did


class Job(TL.Scratch):
    """The build job's steps, and the job run with every outside tool stubbed."""
    def setUp(self):
        super().setUp()
        self.root = Path(self.tmp.name) / "out"
        self.root.mkdir()
        self.calls, self.said = [], []

    def run_stub(self, make=("render",)):
        def run(argv, env=None, what=""):
            self.calls.append((what, argv, env))
            build = Path(argv[-1]).name if what in ("presenter", "voice check") else None
            if what == "render":
                b = self.root / "m7_lecture01_ru"
                b.mkdir(exist_ok=True)
                (b / "m7_lecture01_ru.mp4").write_bytes(b"v")
        return run

    def clean_plan(self, **kw):
        report = {"font": None, "narration": [], "labels": [], "dicts": [], "cues": [], "overrides": []}
        return mock.patch.multiple(BL, CL=mock.Mock(preflight=mock.Mock(return_value=report), summary=CL.summary, problems=CL.problems),
                                   D=mock.Mock(unapproved=mock.Mock(return_value={"lines": kw.get("lines", 3), "labels": kw.get("labels", 0), "total": 9})))

    def test_the_steps_are_render_join_presenter_and_the_voice_check(self):
        st = BL.steps(self.root, "m7_lecture01_ru")
        self.assertEqual([n for n, _, _ in st], list(BL.STEPS))
        render = st[0]
        self.assertEqual(render[1], ["./render.sh", "m7_lecture01", "h"])
        self.assertEqual((render[2]["LANG_CODE"], render[2].get("VOICE_ENGINE"), render[2]["JOBS"]), ("ru", None, "3"))
        self.assertEqual(st[1][1][:2], ["./join_parts.sh", os.path.relpath(self.root / "m7_lecture01_ru", HERE)])
        self.assertEqual(st[2][1][1:], ["presenter.py", str(self.root / "m7_lecture01_ru")])
        self.assertEqual(st[3][1][1:], ["voice_check_lang.py", "ru", str(self.root / "m7_lecture01_ru")])
        uz = BL.steps(self.root, "lecture01_uz_navoiy")
        self.assertEqual((uz[0][2]["LANG_CODE"], uz[0][2]["VOICE_ENGINE"], uz[0][2]["JOBS"]), ("uz", "navoiy", "1"))
        self.assertEqual(uz[3][1][1:], ["voice_check.py", str(self.root / "lecture01_uz_navoiy")])
        self.assertEqual(BL.build_name("lecture03", "uz"), "lecture03_uz_navoiy")
        self.assertEqual(BL.build_name("m7_lecture01", "ru"), "m7_lecture01_ru")

    def test_a_draft_runs_every_step_in_order_and_says_it_is_a_draft(self):
        with self.clean_plan():
            out = BL.build_language(self.root, "m7_lecture01", "ru", lambda: self.c, self.said.append, self.run_stub(),
                                    server=mock.Mock(up=lambda: True))
        self.assertEqual([c[0] for c in self.calls], list(BL.STEPS))
        self.assertEqual(out, "m7_lecture01_ru built; a draft")
        self.assertIn("step 1 of 4: render (a draft: lines or labels are not approved)", self.said)
        self.assertEqual(self.said[-1], "step 4 of 4: voice check")

    def test_uzbek_with_unapproved_lines_is_refused_and_nothing_runs(self):
        with self.clean_plan():
            with self.assertRaisesRegex(ValueError, "cannot build: Uzbek is built only when every line and label is approved"):
                BL.build_language(self.root, "lecture01", "uz", lambda: self.c, self.said.append, self.run_stub(),
                                  server=mock.Mock(up=lambda: True))
        self.assertEqual(self.calls, [])

    def test_uzbek_with_everything_approved_starts_the_voice_server_first(self):
        server = mock.Mock(up=mock.Mock(return_value=False))
        run = self.run_stub()

        def run_uz(argv, env=None, what=""):
            run(argv, env, what)
            if what == "render":
                (self.root / "lecture01_uz_navoiy").mkdir(exist_ok=True)
                (self.root / "lecture01_uz_navoiy" / "lecture01_uz_navoiy.mp4").write_bytes(b"v")
        with self.clean_plan(lines=0):
            out = BL.build_language(self.root, "lecture01", "uz", lambda: self.c, self.said.append, run_uz, server=server)
        server.start.assert_called_once()
        self.assertEqual(out, "lecture01_uz_navoiy built")
        self.assertEqual(self.calls[0][2]["VOICE_ENGINE"], "navoiy")
        self.assertIn("starting the voice server (about a minute)", self.said[0])

    def test_an_edge_voice_build_never_touches_the_voice_server(self):
        server = mock.Mock(up=mock.Mock(return_value=False))
        with self.clean_plan():
            BL.build_language(self.root, "m7_lecture01", "ru", lambda: self.c, self.said.append, self.run_stub(), server=server)
        server.start.assert_not_called()

    def test_a_failing_voice_check_leaves_the_build_and_marks_the_clips(self):
        run = self.run_stub()

        def run_bad(argv, env=None, what=""):
            run(argv, env, what)
            if what == "voice check":
                (self.root / "m7_lecture01_ru" / "voice_check.json").write_text("[]")
                raise RuntimeError("voice check failed: FAIL")
        with self.clean_plan():
            out = BL.build_language(self.root, "m7_lecture01", "ru", lambda: self.c, self.said.append, run_bad,
                                   server=mock.Mock(up=lambda: True))
        self.assertIn("some clips failed the voice check", out)

    def test_a_crashing_step_and_an_existing_build_fail_the_job(self):
        def run_crash(argv, env=None, what=""):
            if what == "presenter":
                raise RuntimeError("presenter failed: x")
            self.run_stub()(argv, env, what)
        with self.clean_plan():
            with self.assertRaisesRegex(RuntimeError, "presenter failed"):
                BL.build_language(self.root, "m7_lecture01", "ru", lambda: self.c, self.said.append, run_crash,
                                  server=mock.Mock(up=lambda: True))
            with self.assertRaisesRegex(ValueError, "already built"):                      # the video the first run left
                BL.build_language(self.root, "m7_lecture01", "ru", lambda: self.c, self.said.append, self.run_stub(),
                                  server=mock.Mock(up=lambda: True))

    def test_a_voice_check_crash_without_a_fresh_report_fails_the_job(self):
        def run_crash(argv, env=None, what=""):
            self.run_stub()(argv, env, what)
            if what == "voice check":
                raise RuntimeError("voice check failed: Traceback")
        with self.clean_plan():
            with self.assertRaisesRegex(RuntimeError, "Traceback"):
                BL.build_language(self.root, "m7_lecture01", "ru", lambda: self.c, self.said.append, run_crash,
                                  server=mock.Mock(up=lambda: True))

    def test_the_plan_decides_the_button(self):
        report = {"font": None, "narration": [], "labels": ["a"], "dicts": [], "cues": [], "overrides": []}
        with mock.patch.object(BL.CL, "preflight", return_value=report), \
                mock.patch.object(BL.D, "unapproved", return_value={"lines": 2, "labels": 0, "total": 5}):
            p = BL.plan(self.c, self.root, "m7_lecture01", "ru")
            self.assertEqual((p["can"], p["draft"], p["reasons"]), (False, True, ["1 label has no Russian form"]))
        report["labels"] = []
        with mock.patch.object(BL.CL, "preflight", return_value=report), \
                mock.patch.object(BL.D, "unapproved", return_value={"lines": 2, "labels": 0, "total": 5}):
            self.assertEqual([BL.plan(self.c, self.root, "m7_lecture01", l)["can"] for l in ("ru", "uz")], [True, False])
        with mock.patch.object(BL.CL, "preflight", return_value=report), \
                mock.patch.object(BL.D, "unapproved", return_value={"lines": 0, "labels": 0, "total": 5}):
            p = BL.plan(self.c, self.root, "m7_lecture01", "ru")
            self.assertEqual((p["can"], p["draft"], p["approval"]), (True, False, "clean"))
            (self.root / "m7_lecture01_ru").mkdir()
            (self.root / "m7_lecture01_ru" / "m7_lecture01_ru.mp4").write_bytes(b"v")
            self.assertFalse(BL.plan(self.c, self.root, "m7_lecture01", "ru")["can"])         # built: never rebuilt over


class BuildRequest(unittest.TestCase):
    """serve_presenter.build_language: a request for what cannot be built is refused with the reason, else queued."""
    def test_the_build_request_is_refused_for_what_cannot_be_built(self):
        import serve_presenter as SP
        with mock.patch.object(SP.BL, "plan", return_value={"can": False, "reasons": ["3 labels have no Russian form"], "build": "x"}):
            with self.assertRaisesRegex(ValueError, "cannot build: 3 labels have no Russian form"):
                SP.build_language("m7_lecture01", "ru")
        queued = []
        with mock.patch.object(SP.BL, "plan", return_value={"can": True, "reasons": [], "build": "m7_lecture01_ru"}), \
                mock.patch.object(SP, "enqueue", side_effect=lambda *a: queued.append(a[:3])):
            self.assertEqual(SP.build_language("m7_lecture01", "ru"), "m7_lecture01_ru")
        self.assertEqual(queued, [("m7_lecture01_ru", "build", "video")])


if __name__ == "__main__":
    unittest.main()
