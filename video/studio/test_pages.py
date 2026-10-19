"""The two pages' JavaScript parses (node --check), with every placeholder filled: the editor (studio/editor.html,
as serve_presenter.editor() fills it) and the presenter (presenter.PAGE, as presenter.main() fills it).
A syntax error there would only show as a dead page in the instructor's browser.

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
    def test_editor_script_parses(self):
        page = (HERE / "studio" / "editor.html").read_text()
        page = page.replace("__BUILD__", "m7_lecture01_en").replace("__TITLE__", "t").replace("__MODULE__", "7")
        page = page.replace("__CLEAN__", "<option>off</option>")
        self.assertNotIn("__", "".join(scripts(page)))
        for js in scripts(page):
            code, err = node_check(js)
            self.assertEqual(code, 0, err)

    def test_presenter_script_parses(self):
        import presenter
        lines = [[0.0, "One.", [[0.0, 1.0, "One."]], 0], [2.0, "Two.", [[2.0, 3.0, "Two."]], 1]]
        page = presenter.PAGE.replace("VIDEO", "x.mp4").replace("LINES", json.dumps(lines)).replace("BUILD", "b")
        for js in scripts(page):
            code, err = node_check(js)
            self.assertEqual(code, 0, err)
        src = (HERE / "presenter.py").read_text()
        self.assertIn('{silent.name}?v={int(silent.stat().st_mtime)}', src)        # the video is versioned: no stale cache
        self.assertIn("line=(\\d+)", page)                  # the #line=41 pattern reached the page intact


if __name__ == "__main__":
    unittest.main()
