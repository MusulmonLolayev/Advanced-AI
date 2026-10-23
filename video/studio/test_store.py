"""Unit tests for forgetting a deleted recording (studio/store.py drop_session, studio/api.py forget).

    uv run python -m unittest discover -s studio -p 'test_store.py' -t .        (from video/)
"""
import tempfile
import unittest
from pathlib import Path

from studio import api as A
from studio import store as S

B, GONE, KEPT = "m7_lecture99_en", "2026-10-19T14-11-13", "2026-10-19T14-12-00"


class Forget(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.rec = self.root / B / "presenter" / "recordings"
        self.rec.mkdir(parents=True)
        self.c = S.connect(self.root / "studio.sqlite")
        for name in (GONE, KEPT):
            S.session_seen(self.c, B, name)
            S.set_edit(self.c, B, f"{name}@1.39", {"nudge": 0.1})
            S.choose(self.c, B, 0 if name == GONE else 1, f"{name}@1.39")
            for ext in ("webm", "json", "m4a", "yours.m4a", "cloned.json", "cloned.f32", "silence.json", "deepfilter.f32", "off.f32", "json.5ab28c4610a7"):
                (self.rec / f"{name}.{ext}").write_text("x")
            (self.rec / f"{name}.chunks").mkdir()
            (self.rec / f"{name}.chunks" / "000000.part").write_text("x")
            (self.rec / f"{name}.words").mkdir()
            (self.rec / f"{name}.words" / "1.39.json").write_text("{}")

    def tearDown(self):
        self.c.close()
        self.tmp.cleanup()

    def test_store_drops_only_that_sessions_rows(self):
        S.drop_session(self.c, B, GONE)
        self.assertEqual([s["name"] for s in S.sessions(self.c, B)], [KEPT])
        self.assertEqual(list(S.edits(self.c, B)), [f"{KEPT}@1.39"])
        self.assertEqual(S.choices(self.c, B), {1: f"{KEPT}@1.39"})

    def test_forget_removes_the_derived_files_and_keeps_the_remap_history(self):
        A.forget(self.root, B, GONE, self.c)
        left = sorted(p.name for p in self.rec.iterdir() if p.name.startswith(GONE))
        self.assertEqual(left, [f"{GONE}.json.5ab28c4610a7"])
        self.assertEqual(len([p for p in self.rec.iterdir() if p.name.startswith(KEPT)]), 12)
        self.assertEqual([s["name"] for s in S.sessions(self.c, B)], [KEPT])


class ExportProfiles(unittest.TestCase):
    def test_the_profile_an_export_was_made_with_is_listed_and_the_note_is_not(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t) / B / "presenter" / "export"
            d.mkdir(parents=True)
            (d / f"{B}_edited.mp4").write_bytes(b"x" * 10)
            (d / f"{B}_edited.srt").write_text("1")
            (d / "old.mp4").write_bytes(b"y")                                 # an export made before profiles were noted
            A.note_export_profile(t, B, [f"{B}_edited.mp4", f"{B}_edited.srt"], "cloned")
            got = {e["name"]: e["profile"] for e in A.exports(t, B)}
            self.assertEqual(got, {f"{B}_edited.mp4": "cloned", f"{B}_edited.srt": "cloned", "old.mp4": ""})
            A.note_export_profile(t, B, [f"{B}_edited.mp4"], "deepfilter")      # a later export replaces its entry only
            got = {e["name"]: e["profile"] for e in A.exports(t, B)}
            self.assertEqual((got[f"{B}_edited.mp4"], got[f"{B}_edited.srt"]), ("deepfilter", "cloned"))


if __name__ == "__main__":
    unittest.main()
