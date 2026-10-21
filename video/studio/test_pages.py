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
    def test_editor_scripts_parse(self):
        page = (HERE / "studio" / "editor.html").read_text()
        page = page.replace("__BUILD__", "m7_lecture01_en").replace("__TITLE__", "t").replace("__MODULE__", "7")
        page = page.replace("__CLEAN__", "<option>off</option>")
        self.assertNotIn("__", "".join(scripts(page)))
        for js in scripts(page):
            code, err = node_check(js)
            self.assertEqual(code, 0, err)
        for f in sorted((HERE / "studio" / "static").rglob("*.js")):         # the split-out scripts
            code, err = node_check(f.read_text())
            self.assertEqual(code, 0, f"{f.name}: {err}")

    def test_template_loads_every_script_in_order(self):
        page = (HERE / "studio" / "editor.html").read_text()
        static = HERE / "studio" / "static"
        listed = re.findall(r'<script src="/studio-static/([^"]+)"', page)
        self.assertEqual(listed, ["editor/player.js", "editor/levels.js", "editor/lines.js", "editor/versions.js", "editor/main.js"])
        self.assertEqual(sorted(listed), sorted(str(f.relative_to(static)) for f in static.rglob("*.js")))
        self.assertIn('href="/studio-static/editor.css"', page)
        for hook in ('id="margin"', 'id="longsil"', 'id="lvc"', 'gotoSilence(1)', 'gotoSilence(-1)', 'id="silcount"'):
            self.assertIn(hook, page)                                  # the header settings, the lecture strip, the buttons
        for f in listed + ["editor.css"]:
            self.assertTrue((static / f).is_file(), f)
        self.assertNotIn("<style>", page)
        self.assertEqual(scripts(page), ['const BUILD = "__BUILD__";'])        # the only inline script

    def test_the_strip_computes_what_the_server_removes(self):
        """levels.js mirrors timeline.plan (the handles show what an edit removes while they are dragged, before the
        server has answered): the same cuts and squeezes, and the same edited time, on random takes and edits."""
        import random
        from studio import api as A, timeline as T
        rnd, cases = random.Random(11), []
        for _ in range(300):
            pic, t = [], 0.0
            for _ in range(rnd.randint(1, 8)):
                d = rnd.choice([0.0004, 0.05, 0.3, 1.0, 3.0])
                pic.append((d, rnd.choice(["play", "hold"]), 0, 1, 1))
                t += d
            e = {}
            for k in ("trim_in", "trim_out"):
                if rnd.random() < 0.7:
                    e[k] = rnd.choice([0.001, 0.1, 0.4, t * 0.3, t * 0.8, t * 1.2])
            if rnd.random() < 0.5:
                e["cuts"] = [sorted([rnd.uniform(0, t), rnd.uniform(0, t)])]
            if rnd.random() < 0.3:
                e["auto_cuts"] = [[rnd.uniform(0, t), rnd.uniform(0, t)] for _ in range(2)]
            if rnd.random() < 0.4:
                a = rnd.uniform(0, t)
                e["squeeze"] = [[a, a + rnd.uniform(0, t), rnd.choice([0.01, 0.2, 1.0])]]
            cuts, sq = T.plan(pic, t, e)
            at = rnd.uniform(0, t)                                         # where a click on the strip lands, edited
            cases.append({"edit": e, "picture": A.picture_spans(pic), "total": t, "cuts": cuts, "sq": sq, "at": at,
                          "edited_at": T.length(T.squeeze([(at, "s", 0.0)], cuts, sq, True))})
        driver = """
const vm = require('vm'), fs = require('fs');
const stub = {addEventListener(){}, getElementById(){ return {addEventListener(){}}; }, documentElement: {}};
const ctx = {window: {addEventListener(){}}, document: stub, localStorage: {}, getComputedStyle(){ return {getPropertyValue(){ return ''; }}; }};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8') + '; this.planOf = planOf; this.editedTime = editedTime;', ctx);
const cases = JSON.parse(fs.readFileSync(process.argv[3], 'utf8')), bad = [];
const close = (a, b) => a.length === b.length && a.every((x, i) => Array.isArray(x) ? close(x, b[i]) : Math.abs(x - b[i]) < 1e-9);
cases.forEach((c, i) => {
  const p = ctx.planOf(c.edit, c.picture, c.total);
  if (!close(p.cuts, c.cuts) || !close(p.sq, c.sq)) bad.push(['plan', i, p, c.cuts, c.sq]);
  else if (Math.abs(ctx.editedTime(p, c.total, c.at) - c.edited_at) > 1e-9) bad.push(['time', i, ctx.editedTime(p, c.total, c.at), c.edited_at]);
});
console.log(JSON.stringify(bad.slice(0, 2)), cases.length);
process.exit(bad.length ? 1 : 0);
"""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "run.js").write_text(driver)
            (Path(d) / "cases.json").write_text(json.dumps(cases))
            r = subprocess.run([NODE, str(Path(d) / "run.js"), str(HERE / "studio" / "static" / "editor" / "levels.js"),
                                str(Path(d) / "cases.json")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[:1500] + r.stderr[:1500])

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
