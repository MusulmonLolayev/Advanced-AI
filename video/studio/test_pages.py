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
        self.assertEqual(sorted(listed), sorted(str(f.relative_to(static)) for f in (static / "editor").rglob("*.js")))
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

    def test_the_player_seeks_only_when_it_must(self):
        """player.js's seek decision, on fake elements: a voice piece that continues the one before it never seeks, an
        element that is seeking or buffering is never seeked again (the clock runs ahead of it; seeking each frame
        replayed fragments on a slow link), and a jump or a forced seek lands exactly, once."""
        driver = """
const vm = require('vm'), fs = require('fs'), assert = require('assert');
class El { constructor(u){ this.src = u; this.paused = true; this.seeking = false; this.readyState = 4; this.n = 0; this._t = 0; }
  set currentTime(x){ this._t = x; this.n++; } get currentTime(){ return this._t; }
  play(){ this.paused = false; return Promise.resolve(); } pause(){ this.paused = true; } }
const ctx = {performance, Audio: El, Math}; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8') + '; this.Player = Player;', ctx);
const mk = voice => { const v = new El('v'); v.playbackRate = 1;
  const p = new ctx.Player(v, () => ({s: 's.m4a'}), {}); p.audios = {};
  p.load({voice, picture: [[voice.reduce((a, x) => a + x[0], 0), 'hold', 0, null, 1]]}, [], 0); p.playing = true; return p; };
const at = (p, T) => { p.T = T; p.sync(false); };
const run = (name, f) => { try { f(); } catch (e) { console.log(name, e.message); process.exit(1); } };
run('contiguous', () => {                       // before, take, after of one session: one seek (the start), then none
  const p = mk([[2, 's', 100], [20, 's', 102], [2, 's', 122]]), el = p.audios.s.el;
  assert.strictEqual(el.n, 1);
  for (let T = 0; T < 24; T += 0.05){ el._t = 100 + T; at(p, T); }      // the element plays on exactly with the clock
  assert.strictEqual(el.n, 1);
  const q = mk([[2, 's', 100], [20, 's', 102]]), e2 = q.audios.s.el;
  e2._t = 101.8; at(q, 1.9); e2._t = 101.95; at(q, 2.1);     // lagging 0.15-0.2 s across the boundary: within the tolerance
  assert.strictEqual(e2.n, 1); });
run('seeking', () => {                          // behind the clock but still seeking or buffering: never another seek
  const p = mk([[30, 's', 100]]), el = p.audios.s.el;
  el._t = 100; el.seeking = true; for (let T = 1; T < 5; T += 0.1) at(p, T);
  el.seeking = false; el.readyState = 1; for (let T = 5; T < 8; T += 0.1) at(p, T);
  assert.strictEqual(el.n, 1);                  // only the start
  el.readyState = 4; at(p, 8);                  // ready: one exact seek
  assert.strictEqual(el.n, 2); assert.ok(Math.abs(el.currentTime - 108) < 1e-9); });
run('jump', () => {                             // a piece that does not continue seeks once, exactly
  const p = mk([[2, 's', 100], [2, 's', 150]]), el = p.audios.s.el;
  el._t = 100; for (let T = 0; T < 2; T += 0.1){ el._t = 100 + T; at(p, T); }
  const n = el.n; el.seeking = false; at(p, 2.0); assert.strictEqual(el.n, n + 1); assert.ok(Math.abs(el.currentTime - 150) < 1e-9);
  el.seeking = true; at(p, 2.1); at(p, 2.2); assert.strictEqual(el.n, n + 1); });
run('forced', () => {                           // the user moves: seek even if it is seeking
  const p = mk([[30, 's', 100]]), el = p.audios.s.el; el.seeking = true; const n = el.n; p.seek(10);
  assert.strictEqual(el.n, n + 1); });
console.log('ok');
"""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "run.js").write_text(driver)
            r = subprocess.run([NODE, str(Path(d) / "run.js"), str(HERE / "studio" / "static" / "editor" / "player.js")],
                               capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[:1500] + r.stderr[:1500])

    def test_the_editor_has_the_language_switch_and_the_narration_page_its_files(self):
        page = (HERE / "studio" / "editor.html").read_text()
        self.assertIn('id="langsw"', page)
        self.assertIn("__LANGS__", page)
        lines = (HERE / "studio" / "static" / "editor" / "lines.js").read_text()
        for hook in ("function langBanner", "function langBox", "function stillFine", "/api/editor-langs", "/api/narration/fine"):
            self.assertIn(hook, lines)
        review = (HERE / "studio" / "static" / "narration" / "review.js").read_text()
        for hook in ("/api/narration/", "'approve'", "'save'", "'fine'", "#(line|label)="):
            self.assertIn(hook, review)

    def test_presenter_script_parses(self):
        import presenter
        lines = [[0.0, "One.", [[0.0, 1.0, "One."]], 0], [2.0, "Two.", [[2.0, 3.0, "Two."]], 1]]
        with tempfile.TemporaryDirectory() as d:
            silent = Path(d) / "b_silent.mp4"
            silent.write_bytes(b"x")
            page = presenter.render(lines, "b", silent)
        self.assertNotIn("__", "".join(scripts(page)).replace("__proto__", ""))      # every placeholder filled
        for js in scripts(page):
            code, err = node_check(js)
            self.assertEqual(code, 0, err)
        src = (HERE / "presenter.py").read_text()
        self.assertIn('{silent.name}?v={int(silent.stat().st_mtime)}', src)        # the video is versioned: no stale cache
        self.assertRegex(page, r'src="b_silent\.mp4\?v=\d+"')
        self.assertIn('const L = ' + json.dumps(lines, ensure_ascii=False), page)
        self.assertIn("line=(\\d+)", page)                  # the #line=41 pattern reached the page intact

    def test_presenter_loads_the_panel_scripts(self):
        """The presenter page loads the editor's player and level strip, then its own script after the page's: and every
        file it names is there, and parses."""
        import presenter
        page = presenter.PAGE
        static = HERE / "studio" / "static"
        srcs = re.findall(r'<script src="/studio-static/([^"]+)"', page)
        self.assertEqual(srcs, ["editor/player.js", "editor/levels.js", "presenter/takes.js"])
        self.assertLess(page.index("editor/levels.js"), page.index("<script>"))        # the panel's tools first, takes.js last
        self.assertLess(page.index("<script>"), page.index("presenter/takes.js"))
        self.assertIn('href="/studio-static/presenter/takes.css"', page)
        for f in srcs + ["presenter/takes.css"]:
            self.assertTrue((static / f).is_file(), f)
        for k in ("T takes of this line", "L record a take of this line"):          # the help bar lists the new keys
            self.assertIn(k, page)
        self.assertIn("X marks a mistake while recording. Press R to record, or L to record a take of just this line.", page)
        self.assertNotIn("setCursor", (static / "editor" / "player.js").read_text())     # the player knows no page of its own

if __name__ == "__main__":
    unittest.main()
