"""Versions of a rewritten scene (studio/versions.py), with the outside tools stubbed: which version a new one grows
from and the texts it holds; the draft narration (the real file stays byte-identical); the voice cache copied in and
merged back without losing an entry; merge order and rollback; stale versions; discard. Plus the two overrides that
make a draft render possible: render.sh's OUT_DIR and the kits' NARRATION_DIR.

    uv run python -m unittest discover -s studio -p 'test_versions.py' -t .        (from video/)
"""
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from studio import media as M
from studio import narration_edit as N
from studio import rewrite as RW
from studio import store as S
from studio import versions as V

HERE = Path(__file__).resolve().parents[1]
B = "m7_lecture99_uz_navoiy"
MODULE = "m7_lecture99"
LINES = [[0.0, "Salom, doʻstlar.", [], 0], [10.0, "Keling, bitta savoldan boshlaymiz.", [], 1],
         [20.0, "Mana shu bilan tugatamiz.", [], 1]]              # lines 2 and 3 (index 1, 2) share the scene S01Q
MD = """## Lecture opening
0. **Salom, doʻstlar.**
   *Hello, friends.*
### 1-boʻlim · Section 1 — Savol · Question
1. **Keling, bitta savoldan boshlaymiz.**
   *Let's start with one question.*
2. **Mana shu bilan tugatamiz.**
   *With this we finish.*
"""
SRT = "1\n00:00:00,500 --> 00:00:03,000\nKeling, bitta savol\n\n2\n00:00:03,100 --> 00:00:04,000\nbilan boshlaymiz.\n\n" \
      "3\n00:00:05,000 --> 00:00:08,000\nMana shu bilan tugatamiz.\n"
OLD_TEXT, NEW_TEXT, TEXT2 = LINES[1][1], "Keling, bitta savol bilan boshlaymiz.", "Mana shu bilan yakunlaymiz."


def tree(d):
    """{relative path: sha1} of every file under d, to compare two folders byte for byte."""
    return {str(p.relative_to(d)): hashlib.sha1(p.read_bytes()).hexdigest() for p in sorted(Path(d).rglob("*")) if p.is_file()}


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.root, self.nar = d / "out", d / "narration"
        self.b = self.root / B
        (self.b / "presenter" / "recordings").mkdir(parents=True)
        self.nar.mkdir()
        (self.nar / "m7_lecture99.md").write_text(MD)
        self.scenes = self.b / "media" / "videos" / MODULE / "1080p60"
        self.scenes.mkdir(parents=True)
        for s in ("S00Opening", "S01Q"):
            (self.scenes / f"{s}.mp4").write_bytes(b"old " + s.encode())
            (self.scenes / f"{s}.srt").write_text("old srt " + s)
        (self.b / "parts.txt").write_text("".join(f"file '{self.scenes / s}.mp4'\n" for s in ("S00Opening", "S01Q")))
        (self.b / "presenter" / "lines.json").write_text(json.dumps(LINES))
        (self.b / f"{B}.mp4").write_bytes(b"old video")
        cache = self.b / "media" / "voiceovers" / "S01Q"
        cache.mkdir(parents=True)
        (cache / "a.mp3").write_bytes(b"clip a")
        (cache / "cache.json").write_text(json.dumps([self.entry(OLD_TEXT, "a.mp3")]))
        self.db = d / "studio.sqlite"
        os.environ["STUDIO_NARRATION"] = str(self.nar)
        with S.connect(self.db) as c:                       # one recording made against the current lines
            h = hashlib.sha1((self.b / "presenter" / "lines.json").read_bytes()).hexdigest()[:12]
            S.session_seen(c, B, "s1", lines_hash=h)
            S.set_session(c, B, "s1", state="ready")
        (self.b / "presenter" / "recordings" / "s1.json").write_text(json.dumps(
            [[0, "hold", 0, 1], [1, "line", 10.0, 1, 1], [1.05, "play", 10.0, 1], [6, "hold", 15.0, 1],
             [8, "line", 20.0, 1, 2], [8.05, "play", 20.0, 1], [12, "stop", 24.0, 1]]))
        self.calls, self.fail_on = [], None

    def tearDown(self):
        os.environ.pop("STUDIO_NARRATION", None)
        self.tmp.cleanup()

    @staticmethod
    def entry(text, mp3):
        data = {"input_text": text, "service": "navoiy", "voice": "v"}
        return {"input_text": text, "input_data": data, "original_audio": mp3, "final_audio": mp3}

    def connect(self):
        return S.connect(self.db)

    def fake_run(self, cmd, env=None, what=""):
        """The outside tools: records the call, writes what the real tool would."""
        name = Path(cmd[1]).name if cmd[0].endswith("python") else Path(cmd[0]).name
        self.calls.append((name, cmd, {k: env[k] for k in ("ONLY", "OUT_DIR", "NARRATION_DIR", "VOICE_ENGINE") if env and k in env}))
        if self.fail_on and self.fail_on in what:
            raise RuntimeError(f"{what} failed: boom")
        if name == "revoice_line.py":
            job = json.loads(Path(cmd[2]).read_text())
            self.job = job
            cd = Path(job["cache_dir"])
            cd.mkdir(parents=True, exist_ok=True)                           # as revoice_line.py does
            self.cache_seen = sorted(p.name for p in cd.iterdir())          # the copy of the lecture's cache is there
            clip = f"new{len(self.calls)}.mp3"
            (cd / clip).write_bytes(b"clip new")
            es = (json.loads((cd / "cache.json").read_text()) if (cd / "cache.json").exists() else []) + \
                [self.entry(job["text"], clip)]
            (cd / "cache.json").write_text(json.dumps(es))
            vc = Path(job["build"]) / "voice_check.json"
            rows = json.loads(vc.read_text()) if vc.exists() else []              # it appends, as revoice_line.py does
            vc.write_text(json.dumps(rows + [{"file": str(cd / clip), "text": job["text"], "ok": True, "fails": [],
                                       "listen": False, "heard": [job["text"]]}]))
            Path(job["report"]).write_text(json.dumps({"kept": "new", "ok": True, "fails": [], "listen": False}))
        elif name == "render.sh":
            out = Path(env["OUT_DIR"]) / "media" / "videos" / MODULE / "1080p60"
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{env['ONLY']}.mp4").write_bytes(b"version scene")
            (out / f"{env['ONLY']}.srt").write_text(SRT)
        elif name == "presenter.py":
            new = [[0.0] + LINES[0][1:], [10.0, NEW_TEXT, [], 1], [22.0] + LINES[2][1:]]
            (self.b / "presenter" / "lines.json").write_text(json.dumps(new))
        elif name == "join_parts.sh":                                # the lecture is its scenes joined
            old = (self.scenes / "S01Q.mp4").read_bytes() == b"old S01Q"
            (self.b / f"{B}.mp4").write_bytes(b"old video" if old else b"new video")
        return ""

    def patched(self):
        return mock.patch.object(RW, "run", self.fake_run), mock.patch.object(V.voice_server, "up", return_value=True), \
            mock.patch.object(M, "video_end", return_value=30.0)

    def make(self, line=1, text=NEW_TEXT, base=None, build=True):
        """Create a version, and build it (ready) unless build=False. Returns (scene, n)."""
        with self.connect() as c:
            scene, n = V.create(self.root, B, line, text, base, c)
        if build:
            p = self.patched()
            with p[0], p[1], p[2]:
                V.build_version(self.root, B, scene, n, self.connect, progress=lambda m: None, python=Path("/navoiy/python"))
        return scene, n

    def state(self, n, scene="S01Q"):
        with self.connect() as c:
            return S.version(c, B, scene, n)["state"]

    def merge(self, n, scene="S01Q"):
        p = self.patched()
        with p[0], p[1], p[2]:
            return V.merge(self.root, B, scene, n, self.connect, progress=lambda m: None)


class Bases(Fixture):
    def test_choose_base_order(self):
        rows = [{"n": 1, "state": "merged"}, {"n": 2, "state": "ready"}, {"n": 3, "state": "stale"}, {"n": 4, "state": "ready"},
                {"n": 5, "state": "failed"}]
        self.assertEqual(V.choose_base(rows), 4)                      # the newest ready, unmerged one
        self.assertEqual(V.choose_base(rows, 2), 2)                   # "rewrite again" on an older one
        for bad in (1, 3, 5, 9):
            with self.assertRaises(ValueError):
                V.choose_base(rows, bad)
        self.assertIsNone(V.choose_base([{"n": 1, "state": "merged"}, {"n": 2, "state": "stale"}]))   # the lecture
        self.assertEqual(V.parse_base("S01Q/v2", "S01Q"), 2)
        with self.assertRaises(ValueError):
            V.parse_base("S00Opening/v2", "S01Q")

    def test_texts_accumulate_within_a_scene(self):
        scene, n1 = self.make(1, NEW_TEXT)
        self.assertEqual((scene, n1), ("S01Q", 1))
        with self.connect() as c:
            self.assertIsNone(S.version(c, B, scene, 1)["base"])
            self.assertEqual(S.version(c, B, scene, 1)["texts"], {"1": NEW_TEXT})
        _, n2 = self.make(2, TEXT2)                                   # line 3, same scene: grows from v1 (the newest ready)
        with self.connect() as c:
            v2 = S.version(c, B, scene, n2)
        self.assertEqual((v2["base"], v2["texts"]), (1, {"1": NEW_TEXT, "2": TEXT2}))
        _, n3 = self.make(1, None, base="S01Q/v1")   # "re-voice as is" on v1: same text, base v1 asked for
        with self.connect() as c:
            v3 = S.version(c, B, scene, n3)
        self.assertEqual((v3["base"], v3["texts"]), (1, {"1": NEW_TEXT}))
        _, n4 = self.make(2, None)                                    # re-voice line 3 as is: the newest ready is v3
        with self.connect() as c:
            self.assertEqual(S.version(c, B, scene, n4)["texts"], {"1": NEW_TEXT, "2": LINES[2][1]})

    def test_the_first_version_without_a_ready_one_starts_from_the_lecture(self):
        _, n = self.make(2, TEXT2, build=False)                       # v1 only queued, not ready
        with self.connect() as c:
            self.assertEqual(S.version(c, B, "S01Q", n)["texts"], {"2": TEXT2})
            with self.assertRaises(ValueError):                       # a version being made: the next one waits
                V.create(self.root, B, 1, NEW_TEXT, None, c)

    def test_another_scene_has_its_own_numbers(self):
        self.make(1, NEW_TEXT)
        scene, n = self.make(0, "Assalomu alaykum, doʻstlar.")
        self.assertEqual((scene, n), ("S00Opening", 1))

    def test_bad_text_is_refused(self):
        with self.connect() as c:
            for t in ("   ", "a **b** c"):
                with self.assertRaises(ValueError):
                    V.create(self.root, B, 1, t, None, c)
            self.assertEqual(S.versions(c, B), [])
            with self.assertRaises(ValueError):
                V.create(self.root, B, 99, "x", None, c)
            self.assertEqual(V.create(self.root, B, 1, "Keling, o'n savol.", None, c), ("S01Q", 1))
            self.assertEqual(S.version(c, B, "S01Q", 1)["texts"], {"1": "Keling, oʻn savol."})   # apostrophes fixed


class Drafts(Fixture):
    def test_draft_narration_is_in_the_version_and_the_real_file_is_untouched(self):
        real = (self.nar / "m7_lecture99.md").read_bytes()
        cache = tree(self.b / "media" / "voiceovers")
        scene, n = self.make(1, NEW_TEXT)
        self.make(2, TEXT2)
        d = V.vdir(self.root, B, scene, n)
        draft = (d / "narration" / "m7_lecture99.md").read_text()
        self.assertIn(NEW_TEXT, draft)
        self.assertIn("*Let's start with one question.*", draft)                  # the other language is left
        self.assertIn(TEXT2, (V.vdir(self.root, B, scene, 2) / "narration" / "m7_lecture99.md").read_text())
        self.assertNotIn(TEXT2, draft)
        self.assertEqual((self.nar / "m7_lecture99.md").read_bytes(), real)       # byte for byte
        self.assertEqual(tree(self.b / "media" / "voiceovers"), cache)            # the lecture's cache is not written
        self.assertEqual((self.b / f"{B}.mp4").read_bytes(), b"old video")
        self.assertEqual((self.scenes / "S01Q.mp4").read_bytes(), b"old S01Q")

    def test_the_render_and_the_voicing_work_in_the_version_folder(self):
        scene, n = self.make(1, NEW_TEXT)
        d = V.vdir(self.root, B, scene, n)
        voicing, render = self.calls
        self.assertEqual(voicing[0], "revoice_line.py")
        self.assertEqual(self.job["cache_dir"], str(d / "media" / "voiceovers" / scene))
        self.assertEqual(self.job["build"], str(d))                                # voice_check.json is the draft's own
        self.assertEqual(self.job["text"], NEW_TEXT)
        self.assertEqual(self.cache_seen, ["a.mp3", "cache.json"])                # the lecture's clips were copied in
        self.assertEqual(render[0], "render.sh")
        self.assertEqual(render[1][1:], [MODULE, "h"])
        self.assertEqual(render[2], {"ONLY": scene, "OUT_DIR": str(d), "NARRATION_DIR": str(d / "narration"),
                                     "VOICE_ENGINE": "navoiy"})
        self.assertEqual(self.state(n), "ready")
        self.assertTrue(V.scene_mp4(self.root, B, scene, n).exists())
        self.assertEqual(json.loads((d / "report.json").read_text())["1"]["ok"], True)
        self.assertFalse((self.b / "voice_check.json").exists())
        self.assertEqual(json.loads((d / "meta.json").read_text()), {"scene": scene, "line": 1, "base": None})

    def test_a_second_version_voices_only_its_line_and_keeps_the_first_ones_clip(self):
        self.make(1, NEW_TEXT)
        self.calls.clear()
        scene, n = self.make(2, TEXT2)
        self.assertEqual(self.job["text"], TEXT2)
        self.assertEqual(self.cache_seen, ["a.mp3", "cache.json", "new1.mp3"])    # copied from v1, which holds v1's clip
        with self.connect() as c:
            rep = S.version(c, B, scene, n)["report"]
        self.assertEqual(sorted(rep), ["1", "2"])                                # v1's check kept, line 3's added

    def test_a_failed_render_marks_the_version_failed(self):
        self.fail_on = "render"
        with self.connect() as c:
            scene, n = V.create(self.root, B, 1, NEW_TEXT, None, c)
        p = self.patched()
        with p[0], p[1], p[2], self.assertRaises(RuntimeError):
            V.build_version(self.root, B, scene, n, self.connect, progress=lambda m: None)
        with self.connect() as c:
            v = S.version(c, B, scene, n)
        self.assertEqual(v["state"], "failed")
        self.assertIn("boom", v["error"])
        self.assertEqual((self.nar / "m7_lecture99.md").read_text(), MD)

    def test_a_version_no_longer_queued_is_not_built(self):
        scene, n = self.make(1, NEW_TEXT, build=False)
        with self.connect() as c:
            V.discard(self.root, B, scene, n, c)
        p = self.patched()
        with p[0], p[1], p[2]:
            self.assertIn("skipped", V.build_version(self.root, B, scene, n, self.connect))
        self.assertEqual(self.calls, [])


class Cache(Fixture):
    def test_merge_cache_keeps_every_entry_and_clip(self):
        lec, ver = self.b / "media" / "voiceovers" / "S01Q", self.nar / "ver"
        ver.mkdir()
        (lec / "b.mp3").write_bytes(b"clip b")
        (lec / "cache.json").write_text(json.dumps([self.entry(OLD_TEXT, "a.mp3"), self.entry("B", "b.mp3")]))
        V.copy_cache(lec, ver)                                                    # the version starts from a copy
        (ver / "b2.mp3").write_bytes(b"clip b, second take")
        (ver / "c.mp3").write_bytes(b"clip c")
        es = json.loads((ver / "cache.json").read_text())
        es.insert(1, self.entry("B", "b2.mp3"))                                   # the same text, a better take
        es.append(self.entry("C", "c.mp3"))
        (ver / "cache.json").write_text(json.dumps(es))
        before = tree(lec)
        self.assertEqual(V.merge_cache(ver, lec), 2)
        got = json.loads((lec / "cache.json").read_text())
        self.assertEqual([e["final_audio"] for e in got], ["a.mp3", "b2.mp3", "b.mp3", "c.mp3"])   # b2 first: it wins; b stays
        for name, digest in before.items():
            if name != "cache.json":
                self.assertEqual(tree(lec)[name], digest)                         # no clip lost or changed
        self.assertEqual((lec / "b2.mp3").read_bytes(), b"clip b, second take")
        self.assertEqual(V.merge_cache(ver, lec), 0)                              # a second merge adds nothing

    def test_copy_cache_is_a_copy_not_a_link(self):
        lec, ver = self.b / "media" / "voiceovers" / "S01Q", self.nar / "ver"
        V.copy_cache(lec, ver)
        self.assertFalse((ver / "a.mp3").is_symlink())
        (ver / "a.mp3").write_bytes(b"changed in the draft")
        self.assertEqual((lec / "a.mp3").read_bytes(), b"clip a")
        V.copy_cache(self.nar / "nowhere", self.nar / "x")                        # no cache yet: nothing to copy
        self.assertFalse((self.nar / "x").exists())


class Merge(Fixture):
    def test_the_steps_in_order_and_what_they_change(self):
        scene, n = self.make(1, NEW_TEXT)
        self.make(2, TEXT2)
        self.calls.clear()
        out = self.merge(2)                                                        # v2 holds both texts
        self.assertEqual([c[0] for c in self.calls], ["join_parts.sh", "presenter.py"])
        self.assertFalse(Path(self.calls[0][1][1]).is_absolute())                 # join_parts.sh prefixes $PWD
        md = (self.nar / "m7_lecture99.md").read_text()
        self.assertIn(NEW_TEXT, md)
        self.assertIn(TEXT2, md)
        self.assertIn("*Let's start with one question.*", md)
        self.assertEqual((self.scenes / "S01Q.mp4").read_bytes(), b"version scene")
        self.assertEqual((self.scenes / "S01Q.srt").read_text(), SRT)
        self.assertEqual((self.scenes / "S01Q.before_merge.mp4").read_bytes(), b"old S01Q")
        self.assertEqual((self.scenes / "S01Q.before_merge.srt").read_text(), "old srt S01Q")
        self.assertEqual((self.scenes / "S00Opening.mp4").read_bytes(), b"old S00Opening")
        self.assertEqual((self.b / f"{B}.before_merge.mp4").read_bytes(), b"old video")
        self.assertEqual((self.b / f"{B}.mp4").read_bytes(), b"new video")
        cache = json.loads((self.b / "media" / "voiceovers" / "S01Q" / "cache.json").read_text())
        self.assertEqual([e["input_text"] for e in cache], [OLD_TEXT, NEW_TEXT, TEXT2])    # nothing dropped
        self.assertTrue((self.b / "media" / "voiceovers" / "S01Q" / "new1.mp3").exists())
        self.assertTrue((self.b / "media" / "voiceovers" / "S01Q" / "new3.mp3").exists())
        vc = json.loads((self.b / "voice_check.json").read_text())                # the checks, pointing at the lecture's clips
        self.assertEqual({r["text"] for r in vc}, {TEXT2, NEW_TEXT})
        self.assertTrue(all(Path(r["file"]).parent == self.b / "media" / "voiceovers" / "S01Q" for r in vc))
        self.assertEqual(self.state(2), "merged")
        self.assertIn("2 lines changed", out)
        self.assertIn("1 recording moved", out)

    def test_recordings_follow_the_new_timings(self):
        self.make(1, NEW_TEXT)
        self.merge(1)
        ev = json.loads((self.b / "presenter" / "recordings" / "s1.json").read_text())
        self.assertEqual([e[2] for e in ev], [0, 10.0, 10.0, 15.0, 22.0, 22.0, 26.0])     # line 3 moved by 2 s
        self.assertEqual(len(list((self.b / "presenter" / "recordings").glob("s1.json.*"))), 1)

    def test_a_failed_join_puts_everything_back(self):
        scene, n = self.make(1, NEW_TEXT)
        self.fail_on = "join"
        before = {"cache": (self.b / "media" / "voiceovers" / "S01Q" / "cache.json").read_bytes()}
        with self.assertRaises(RuntimeError):
            self.merge(n)
        self.assert_untouched(before)

    def test_a_failed_presenter_page_puts_everything_back(self):
        scene, n = self.make(1, NEW_TEXT)
        self.fail_on = "presenter"
        before = {"cache": (self.b / "media" / "voiceovers" / "S01Q" / "cache.json").read_bytes()}
        with self.assertRaises(RuntimeError):
            self.merge(n)
        self.assert_untouched(before)

    def test_a_failure_before_the_backups_leaves_an_earlier_merges_backups_alone(self):
        scene, n = self.make(1, NEW_TEXT)
        (self.b / f"{B}.before_merge.mp4").write_bytes(b"stale video backup")      # left by an EARLIER merge
        (self.scenes / "S01Q.before_merge.mp4").write_bytes(b"stale scene backup")
        (self.scenes / "S01Q.before_merge.srt").write_text("stale srt backup")
        with mock.patch.object(V, "merge_cache", side_effect=RuntimeError("cache boom")), self.assertRaises(RuntimeError):
            self.merge(n)
        self.assertEqual((self.b / f"{B}.mp4").read_bytes(), b"old video")
        self.assertEqual((self.scenes / "S01Q.mp4").read_bytes(), b"old S01Q")
        self.assertEqual((self.scenes / "S01Q.srt").read_text(), "old srt S01Q")
        self.assertEqual((self.nar / "m7_lecture99.md").read_text(), MD)
        self.assertEqual((self.b / f"{B}.before_merge.mp4").read_bytes(), b"stale video backup")   # not used, not changed
        self.assertEqual(self.calls[-1][0] if self.calls else "", "render.sh")                      # no join, no presenter

    def test_a_presenter_failure_runs_presenter_again_after_the_restore(self):
        scene, n = self.make(1, NEW_TEXT)
        self.fail_on = "presenter page"
        seen = []
        real = self.fake_run

        def run(cmd, env=None, what=""):
            if Path(cmd[1]).name == "presenter.py":
                seen.append((what, (self.b / f"{B}.mp4").read_bytes(), (self.scenes / "S01Q.mp4").read_bytes()))
                if what.endswith("(after rollback)"):
                    self.fail_on = None
                    return ""
            return real(cmd, env, what)
        with mock.patch.object(RW, "run", run), mock.patch.object(V.voice_server, "up", return_value=True), \
                mock.patch.object(M, "video_end", return_value=30.0), self.assertRaises(RuntimeError) as cm:
            V.merge(self.root, B, scene, n, self.connect, progress=lambda m: None)
        self.assertIn("presenter page failed", str(cm.exception))                   # the original error, not masked
        self.assertEqual([w for w, _, _ in seen], ["presenter page", "presenter page (after rollback)"])
        self.assertEqual(seen[1][1:], (b"old video", b"old S01Q"))                  # the second run saw the restored files
        self.assertEqual([c[0] for c in self.calls][-2:], ["presenter.py", "join_parts.sh"])  # joined again first
        self.assert_untouched({"cache": (self.b / "media" / "voiceovers" / "S01Q" / "cache.json").read_bytes()})

    def test_a_failing_second_presenter_run_does_not_mask_the_error(self):
        scene, n = self.make(1, NEW_TEXT)
        self.fail_on = "presenter page"                                              # matches both runs
        with self.assertRaises(RuntimeError) as cm:
            self.merge(n)
        self.assertNotIn("after rollback", str(cm.exception))
        self.assertEqual([c[0] for c in self.calls].count("presenter.py"), 2)

    def assert_untouched(self, before):
        self.assertEqual((self.nar / "m7_lecture99.md").read_text(), MD)
        self.assertEqual((self.scenes / "S01Q.mp4").read_bytes(), b"old S01Q")
        self.assertEqual((self.scenes / "S01Q.srt").read_text(), "old srt S01Q")
        self.assertEqual((self.b / f"{B}.mp4").read_bytes(), b"old video")
        self.assertEqual((self.b / "media" / "voiceovers" / "S01Q" / "cache.json").read_bytes(), before["cache"])
        self.assertFalse((self.b / "voice_check.json").exists())
        self.assertEqual(self.state(1), "ready")                                  # it can be merged again

    def test_re_voice_as_is_merges_without_touching_the_narration(self):
        self.make(1, None)
        out = self.merge(1)
        self.assertEqual((self.nar / "m7_lecture99.md").read_text(), MD)
        self.assertIn("0 lines changed", out)

    def test_only_a_ready_version_can_be_merged(self):
        scene, n = self.make(1, NEW_TEXT, build=False)
        with self.assertRaises(ValueError):
            self.merge(n)
        self.assertEqual(self.calls, [])


class Stale(Fixture):
    def test_a_merge_makes_the_scenes_other_unmerged_versions_stale(self):
        with self.connect() as c:                                                 # three ready versions, two of one scene
            for scene, text in (("S01Q", NEW_TEXT), ("S01Q", TEXT2), ("S00Opening", "Salom.")):
                S.version_add(c, B, scene, None, {"1": text})
        for n, scene in ((1, "S01Q"), (2, "S01Q"), (1, "S00Opening")):
            d = V.vdir(self.root, B, scene, n)
            (d / "narration").mkdir(parents=True)
            out = V.scene_mp4(self.root, B, scene, n).parent
            out.mkdir(parents=True)
            (out / f"{scene}.mp4").write_bytes(b"version scene")
            with self.connect() as c:
                S.set_version(c, B, scene, n, state="ready")
        self.merge(1)
        self.assertEqual((self.state(1), self.state(2), self.state(1, "S00Opening")), ("merged", "stale", "ready"))
        with self.assertRaises(ValueError) as cm:                                 # built on the old lecture
            self.merge(2)
        self.assertIn("before the last merge", str(cm.exception))
        with self.connect() as c:
            self.assertEqual({v["n"] for v in S.versions(c, B, "S01Q")}, {1, 2})  # a stale one stays listed
            V.discard(self.root, B, "S01Q", 2, c)                                  # and can be discarded
        self.assertEqual(self.state(2), "discarded")

    def test_a_new_version_after_a_merge_starts_from_the_new_lecture(self):
        self.make(1, NEW_TEXT)
        self.merge(1)
        with self.connect() as c:
            scene, n = V.create(self.root, B, 2, TEXT2, None, c)
            self.assertIsNone(S.version(c, B, scene, n)["base"])                  # the merged one is no base
            self.assertEqual(S.version(c, B, scene, n)["texts"], {"2": TEXT2})


class Discard(Fixture):
    def test_a_ready_version_is_deleted_and_hidden(self):
        scene, n = self.make(1, NEW_TEXT)
        d = V.vdir(self.root, B, scene, n)
        self.assertTrue(d.is_dir())
        with self.connect() as c:
            V.discard(self.root, B, scene, n, c)
            self.assertEqual(S.versions(c, B), [])
        self.assertFalse(d.exists())
        self.assertEqual(self.state(n), "discarded")
        with self.connect() as c:
            _, n2 = V.create(self.root, B, 1, NEW_TEXT, None, c)
        self.assertEqual(n2, n + 1)                                               # numbers are not reused

    def test_a_merged_version_cannot_be_discarded(self):
        scene, n = self.make(1, NEW_TEXT)
        self.merge(n)
        d = V.vdir(self.root, B, scene, n)
        with self.connect() as c, self.assertRaises(ValueError):
            V.discard(self.root, B, scene, n, c)
        self.assertTrue(d.is_dir())
        self.assertEqual(self.state(n), "merged")

    def test_one_being_made_or_merged_is_refused(self):
        scene, n = self.make(1, NEW_TEXT)
        with self.connect() as c:
            S.set_version(c, B, scene, n, state="rendering")
            with self.assertRaises(ValueError):
                V.discard(self.root, B, scene, n, c)
            S.set_version(c, B, scene, n, state="ready")
            S.job(c, B, "merge", f"{scene}/v{n}", "running")
            with self.assertRaises(ValueError):
                V.discard(self.root, B, scene, n, c)
            with self.assertRaises(KeyError):
                V.discard(self.root, B, scene, 9, c)


class View(Fixture):
    def test_line_starts_come_from_the_versions_subtitles(self):
        scene, n = self.make(1, NEW_TEXT)
        with self.connect() as c:
            v = V.view(self.root, B, c)[scene][0]
        self.assertEqual(v["line_starts"], {"1": 0.5, "2": 5.0})                  # the two lines of S01Q, as presenter.py groups them
        self.assertEqual(v["video"].split("?")[0], f"/{B}/versions/{scene}/v{n}/media/videos/{MODULE}/1080p60/{scene}.mp4")
        self.assertRegex(v["video"], r"\?v=\d+$")
        self.assertEqual((v["state"], v["changed"], v["texts"]), ("ready", ["1"], {"1": NEW_TEXT}))
        self.assertEqual(sorted(v["report"]), ["1"])

    def test_a_version_still_being_made_has_no_video(self):
        self.make(1, NEW_TEXT, build=False)
        with self.connect() as c:
            v = V.view(self.root, B, c)["S01Q"][0]
        self.assertEqual((v["state"], v["video"], v["line_starts"]), ("queued", None, {}))

    def test_a_restart_fails_the_versions_that_were_running(self):
        scene, n = self.make(1, NEW_TEXT, build=False)
        with self.connect() as c:
            S.reset_running(c)
        self.assertEqual(self.state(n), "failed")


class Overrides(unittest.TestCase):
    def test_render_sh_honours_OUT_DIR(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            bin_ = tmp / "home" / ".local" / "bin"
            bin_.mkdir(parents=True)
            fake = bin_ / "uv"                       # render.sh puts $HOME/.local/bin first: a stand-in for `uv run manim`
            fake.write_text('''#!/usr/bin/env bash
if [ "$3" = python ]; then echo S01Q; exit 0; fi
while [ $# -gt 0 ]; do case "$1" in --media_dir) M="$2"; shift;; *.py) F="${1%.py}";; esac; S="$1"; shift; done
mkdir -p "$M/videos/$F/1080p60"; echo scene > "$M/videos/$F/1080p60/$S.mp4"
''')
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            out = tmp / "draft"
            env = dict(os.environ, HOME=str(tmp / "home"), OUT_DIR=str(out), ONLY="S01Q", JOBS="1")
            for k in ("LANG_CODE", "VOICE_ENGINE"):
                env.pop(k, None)
            r = subprocess.run(["./render.sh", "fakevideo99", "h"], cwd=HERE, env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue((out / "media" / "videos" / "fakevideo99" / "1080p60" / "S01Q.mp4").exists())
            self.assertTrue((out / "render.log").exists())
            self.assertFalse((HERE / "out" / "fakevideo99").exists())               # nothing in the lecture's folder

    def test_kits_read_narration_from_NARRATION_DIR(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            src = HERE / "narration" / "lecture01.md"
            (tmp / "lecture01.md").write_text(src.read_text())
            path, lang, single = N.source("lecture01_uz_navoiy", tmp)
            key, i, form = N.rows(path, lang, single)[0][:3]
            text = N.rows(path, lang, single)[0][2]
            N.rewrite(path, lang, single, text, text + " Bu oʻzgargan matn.")
            code = "import json, lecture_kit as k; l, h = k.narration(1); print(json.dumps(l[%r]['uz'], ensure_ascii=False))" % key
            env = dict(os.environ, NARRATION_DIR=str(tmp))
            got = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True)
            self.assertEqual(got.returncode, 0, got.stderr[-600:])
            self.assertEqual(json.loads(got.stdout.strip().splitlines()[-1]), text + " Bu oʻzgargan matn.")
            env.pop("NARRATION_DIR")
            plain = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True)
            self.assertEqual(json.loads(plain.stdout.strip().splitlines()[-1]), text)       # unset: the real file

    def test_no_kit_reads_a_narration_file_around_narration_dir(self):
        import re
        for f in ("lecture_kit.py", "m7_lecture01_kit.py"):
            self.assertIsNone(re.search(r'HERE / "narration" / ', (HERE / f).read_text()), f)     # only labels.yaml may
        self.assertIn("narration_dir()", (HERE / "m7_lecture01_kit.py").read_text())
        self.assertIn('"NARRATION_DIR"', (HERE / "lecture_kit.py").read_text())


if __name__ == "__main__":
    unittest.main()
