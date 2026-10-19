"""studio/rewrite.py's steps, with the outside tools stubbed: which commands run, in what order, with which
environment; the narration line saved (and put back when a step fails); recordings moved to the new timings.
(The real voice, render and join are exercised by hand on a build: see STATUS.md.)

    uv run python -m unittest discover -s studio -p 'test_rewrite.py' -t .        (from video/)
"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from studio import media as M
from studio import rewrite as RW
from studio import store as S

B = "m7_lecture99_uz_navoiy"
LINES = [[0.0, "Salom, doʻstlar.", [], 0], [10.0, "Keling, bitta savoldan boshlaymiz.", [], 1],
         [20.0, "Mana shu bilan tugatamiz.", [], 2]]
MD = """## Lecture opening
0. **Salom, doʻstlar.**
   *Hello, friends.*
### 1-boʻlim · Section 1 — Savol · Question
1. **Keling, bitta savoldan boshlaymiz.**
   *Let's start with one question.*
### 2-boʻlim · Section 2 — Yakun · End
2. **Mana shu bilan tugatamiz.**
   *With this we finish.*
"""


class Rewrite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.root, self.nar = d / "out", d / "narration"
        self.b = self.root / B
        (self.b / "presenter" / "recordings").mkdir(parents=True)
        self.nar.mkdir()
        (self.nar / "m7_lecture99.md").write_text(MD)
        (self.b / "parts.txt").write_text("".join(f"file '/x/{s}.mp4'\n" for s in ("S00Opening", "S01Q", "S02End")))
        (self.b / "presenter" / "lines.json").write_text(json.dumps(LINES))
        (self.b / f"{B}.mp4").write_bytes(b"old video")
        self.db = d / "studio.sqlite"
        os.environ["STUDIO_NARRATION"] = str(self.nar)
        with S.connect(self.db) as c:                       # one session recorded against the current lines
            import hashlib
            h = hashlib.sha1((self.b / "presenter" / "lines.json").read_bytes()).hexdigest()[:12]
            S.session_seen(c, B, "s1", lines_hash=h)
            S.set_session(c, B, "s1", state="ready")
        (self.b / "presenter" / "recordings" / "s1.json").write_text(json.dumps(
            [[0, "hold", 0, 1], [1, "line", 10.0, 1, 1], [1.05, "play", 10.0, 1], [6, "hold", 15.0, 1],
             [8, "line", 20.0, 1, 2], [8.05, "play", 20.0, 1], [12, "stop", 24.0, 1]]))
        self.calls = []

    def tearDown(self):
        os.environ.pop("STUDIO_NARRATION", None)
        self.tmp.cleanup()

    def fake_run(self, fail_on=None):
        def run(cmd, env=None, what=""):
            self.calls.append((cmd, {k: env[k] for k in ("LANG_CODE", "VOICE_ENGINE", "ONLY") if env and k in env}))
            if fail_on and fail_on in what:
                raise RuntimeError(f"{what} failed: boom")
            if "revoice_line.py" in str(cmd[1] if len(cmd) > 1 else ""):
                job = json.loads(Path(cmd[2]).read_text())
                self.job = job
                Path(job["report"]).write_text(json.dumps({"kept": "new", "ok": True, "fails": [], "listen": False}))
            if len(cmd) > 1 and cmd[1] == "presenter.py":    # the rebuilt video: line 1 grew by 2 s
                new = [[0.0] + LINES[0][1:], [10.0, "Keling, bitta savol bilan boshlaymiz.", [], 1],
                       [22.0] + LINES[2][1:]]
                (self.b / "presenter" / "lines.json").write_text(json.dumps(new))
            if "join_parts.sh" in cmd[0]:
                (self.b / f"{B}.mp4").write_bytes(b"new video")
            return ""
        return run

    def go(self, text, fail_on=None):
        with mock.patch.object(RW, "run", self.fake_run(fail_on)), \
             mock.patch.object(RW.voice_server, "up", return_value=True), \
             mock.patch.object(M, "video_end", return_value=30.0):
            return RW.rewrite(self.root, B, 1, text, lambda: S.connect(self.db), progress=lambda m: None,
                              python=Path("/navoiy/python"))

    def test_the_steps_in_order(self):
        out = self.go("Keling, bitta savol bilan boshlaymiz.")
        self.assertIn("Keling, bitta savol bilan boshlaymiz.", (self.nar / "m7_lecture99.md").read_text())
        self.assertIn("*Let's start with one question.*", (self.nar / "m7_lecture99.md").read_text())
        steps = [Path(c[0][1]).name if c[0][0].endswith("python") else Path(c[0][0]).name for c in self.calls]
        self.assertEqual(steps, ["revoice_line.py", "render.sh", "join_parts.sh", "presenter.py"])
        self.assertEqual(self.job["text"], "Keling, bitta savol bilan boshlaymiz.")
        self.assertTrue(self.job["cache_dir"].endswith("media/voiceovers/S01Q"))
        render = self.calls[1]
        self.assertEqual(render[0][1:], ["m7_lecture99", "h"])
        self.assertEqual(render[1], {"LANG_CODE": "uz", "VOICE_ENGINE": "navoiy", "ONLY": "S01Q"})
        self.assertFalse(Path(self.calls[2][0][1]).is_absolute())        # join_parts.sh prefixes $PWD
        self.assertEqual((self.b / f"{B}.before_rewrite.mp4").read_bytes(), b"old video")
        self.assertIn("1 recording moved", out)

    def test_recordings_follow_the_new_timings(self):
        self.go("Keling, bitta savol bilan boshlaymiz.")
        ev = json.loads((self.b / "presenter" / "recordings" / "s1.json").read_text())
        self.assertEqual([e[2] for e in ev], [0, 10.0, 10.0, 15.0, 22.0, 22.0, 26.0])   # line 2 moved by 2 s
        backups = list((self.b / "presenter" / "recordings").glob("s1.json.*"))
        self.assertEqual(len(backups), 1)
        with S.connect(self.db) as c:
            import hashlib
            h = hashlib.sha1((self.b / "presenter" / "lines.json").read_bytes()).hexdigest()[:12]
            self.assertEqual(S.sessions(c, B)[0]["lines_hash"], h)

    def test_a_failed_render_puts_the_old_text_back(self):
        with self.assertRaises(RuntimeError):
            self.go("Keling, bitta savol bilan boshlaymiz.", fail_on="render")
        self.assertEqual((self.nar / "m7_lecture99.md").read_text(), MD)
        self.assertEqual((self.b / f"{B}.mp4").read_bytes(), b"old video")

    def test_a_failed_join_keeps_the_old_video(self):
        with self.assertRaises(RuntimeError):
            self.go("Keling, bitta savol bilan boshlaymiz.", fail_on="join")
        self.assertEqual((self.b / f"{B}.mp4").read_bytes(), b"old video")
        self.assertEqual((self.nar / "m7_lecture99.md").read_text(), MD)

    def test_revoice_as_is_leaves_the_text(self):
        out = self.go(None)
        self.assertEqual((self.nar / "m7_lecture99.md").read_text(), MD)
        self.assertEqual(self.job["text"], "Keling, bitta savoldan boshlaymiz.")
        self.assertIn("re-voiced", out)

    def test_render_environment_per_build(self):
        self.assertEqual(RW.module_of("lecture03_uz_navoiy"), "lecture03")
        self.assertEqual(RW.module_of("m7_lecture01_en"), "m7_lecture01")
        en = RW.render_env("m7_lecture01_en")
        self.assertEqual((en["LANG_CODE"], "VOICE_ENGINE" in en, en["LABEL_DRAFTS"]), ("en", False, "narration/drafts/m7_l01"))


if __name__ == "__main__":
    unittest.main()
