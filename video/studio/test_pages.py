"""The offline presenter page (presenter.PAGE, as presenter.main() fills it): its JavaScript parses (node --check) and it
loads nothing from the studio. A syntax error there would only show as a dead page. The studio's own screens are the
React app (studio/app: tsc and the browser test check them).

    uv run python -m unittest discover -s studio -p 'test_pages.py' -t .        (from video/)
"""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


def scripts(page):
    return re.findall(r"<script>(.*?)</script>", page, re.S)


def node_check(js):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(js)
    r = subprocess.run([NODE, "--check", f.name], capture_output=True, text=True)
    Path(f.name).unlink()
    return r.returncode, r.stderr


@unittest.skipUnless(NODE, "node is not installed")
class Pages(unittest.TestCase):
    def render(self):
        import presenter
        lines = [[0.0, "One.", [[0.0, 1.0, "One."]], 0], [2.0, "Two.", [[2.0, 3.0, "Two."]], 1]]
        with tempfile.TemporaryDirectory() as d:
            silent = Path(d) / "b_silent.mp4"
            silent.write_bytes(b"x")
            return lines, presenter.render(lines, "b", silent)

    def test_presenter_script_parses(self):
        lines, page = self.render()
        self.assertNotIn("__", "".join(scripts(page)).replace("__proto__", ""))      # every placeholder filled
        for js in scripts(page):
            code, err = node_check(js)
            self.assertEqual(code, 0, err)
        src = (HERE / "presenter.py").read_text()
        self.assertIn('{silent.name}?v={int(silent.stat().st_mtime)}', src)        # the video is versioned: no stale cache
        self.assertRegex(page, r'src="b_silent\.mp4\?v=\d+"')
        self.assertIn('const L = ' + json.dumps(lines, ensure_ascii=False), page)
        self.assertIn("line=(\\d+)", page)                  # the #line=41 pattern reached the page intact

    def test_the_offline_page_is_standalone(self):
        """It names no file of the studio (those pages are gone): an offline copy works from the disk."""
        _, page = self.render()
        self.assertNotIn("/studio-static/", page)
        self.assertNotIn("Takes", page)
        for k in ("L record a take of this line", "R record", "N notes: below / right / off"):
            self.assertIn(k, page)
        self.assertIn("X marks a mistake while recording. Press R to record, or L to record a take of just this line.", page)


if __name__ == "__main__":
    unittest.main()
