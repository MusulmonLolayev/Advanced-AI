"""studio/rewrite.py's helpers (the flow itself moved to versions.py: see test_versions.py): the video module and render
environment of each kind of build, the scene a line belongs to, a failing command's message.

    uv run python -m unittest discover -s studio -p 'test_rewrite.py' -t .        (from video/)
"""
import json
import tempfile
import unittest
from pathlib import Path

from studio import rewrite as RW


class Helpers(unittest.TestCase):
    def test_render_environment_per_build(self):
        self.assertEqual(RW.module_of("lecture03_uz_navoiy"), "lecture03")
        self.assertEqual(RW.module_of("m7_lecture01_en"), "m7_lecture01")
        en = RW.render_env("m7_lecture01_en")
        self.assertEqual((en["LANG_CODE"], "VOICE_ENGINE" in en, en["LABEL_DRAFTS"]), ("en", False, "narration/drafts/m7_l01"))
        uz = RW.render_env("m7_lecture01_uz_navoiy")
        self.assertEqual((uz["LANG_CODE"], uz["VOICE_ENGINE"], uz["JOBS"]), ("uz", "navoiy", "1"))

    def test_scene_of_a_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Path(tmp)
            (b / "presenter").mkdir()
            (b / "parts.txt").write_text("".join(f"file '/x/{s}.mp4'\n" for s in ("S00Opening", "S01Q")))
            (b / "presenter" / "lines.json").write_text(json.dumps([[0.0, "a", [], 0], [5.0, "b", [], 1], [9.0, "c", [], 1]]))
            self.assertEqual([RW.scene_of(b, k) for k in range(3)], ["S00Opening", "S01Q", "S01Q"])
            self.assertEqual([p.name for p in RW.scene_files(b)], ["S00Opening.mp4", "S01Q.mp4"])
            (b / "presenter" / "lines.json").write_text(json.dumps([[0.0, "a", []]]))      # a page older than the editor
            with self.assertRaises(ValueError):
                RW.scene_of(b, 0)

    def test_a_failing_command_says_why(self):
        with self.assertRaises(RuntimeError) as cm:
            RW.run(["bash", "-c", "echo oops >&2; exit 3"], what="thing")
        self.assertIn("thing failed", str(cm.exception))
        self.assertIn("oops", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
