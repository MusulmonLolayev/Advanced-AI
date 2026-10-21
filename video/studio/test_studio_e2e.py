"""End to end: the real studio server on a free port, a synthetic lecture (30 s of test picture, three lines) and a
synthetic voice, recorded over HTTP the way the presenter page does it -- pieces out of order, a retake, a session
cut off without a finish -- then takes, choices, edits, pause cuts and the export, checked against the edit list.

    uv run python -m unittest discover -s studio -p 'test_studio_e2e.py' -t .      (from video/; ~1 min)
"""
import importlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from studio import timeline as T                     # noqa: E402
from studio.test_timeline import session as EVENTS   # noqa: E402   the same session the unit tests reason about

B = "m7_lecture99_en"
SR = 48000
LINES = [[0.0, "Line one is about agents.", [], 0], [10.0, "Line two, the tools.", [], 1],
         [20.0, "Line three ends it.", [], 2]]
NARRATION = """## Lecture opening
0. **Birinchi qator agentlar haqida.**
   *Line one is about agents.*
### 1-boʻlim · Section 1 — Nega agent? · Why an agent?
1. **Ikkinchi qator, vositalar.**
   *Line two, the tools.*
2. **Uchinchi qator tugatadi.**
   *Line three ends it.*
"""
TALK = [(1.2, 11.0), (15.2, 16.8), (18.2, 28.0), (31.2, 40.0)]      # where the synthetic voice speaks


def ff(*a):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *map(str, a)], check=True)


def duration(p, stream=None):
    args = ["-select_streams", stream] if stream else []
    out = subprocess.run(["ffprobe", "-v", "error", *args, "-show_entries", "format=duration" if not stream else
                          "stream=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout
    return float(out.strip().splitlines()[0])


def voice_webm(path, seconds=43.5):
    t = np.arange(round(seconds * SR)) / SR
    x = (0.002 * np.random.default_rng(1).standard_normal(len(t))).astype(np.float32)
    for a, b in TALK:
        m = (t >= a) & (t < b)
        x[m] += (0.3 * np.sin(2 * np.pi * 220 * t[m])).astype(np.float32)
    raw = path.with_suffix(".f32")
    x.tofile(raw)
    ff("-f", "f32le", "-ar", SR, "-ac", 1, "-i", raw, "-c:a", "libopus", "-b:a", "64k", path)
    return path.read_bytes()


class Studio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        os.environ["STUDIO_ROOT"], os.environ["STUDIO_PROFILE"] = str(root), "off"
        import labels                                                   # the languages test writes narration and labels: scratch copies
        nar = root / "narration"
        nar.mkdir()
        (nar / "m7_lecture99.md").write_text(NARRATION)
        (nar / "labels.yaml").write_text("{}\n")
        cls.old_nar, cls.labels, cls.old_labels = os.environ.get("STUDIO_NARRATION"), labels, labels.NARRATION
        os.environ["STUDIO_NARRATION"] = str(nar)
        labels.use(nar)
        b = root / B
        (b / "presenter").mkdir(parents=True)
        ff("-f", "lavfi", "-i", "testsrc2=s=320x180:r=60:d=30", "-c:v", "libx264", "-preset", "ultrafast",
           "-pix_fmt", "yuv420p", b / "presenter" / f"{B}_silent.mp4")
        ff("-i", b / "presenter" / f"{B}_silent.mp4", "-f", "lavfi", "-i", "sine=f=440:r=48000:d=30", "-c:v", "copy",
           "-c:a", "aac", "-shortest", b / f"{B}.mp4")              # the lecture as built: its own narration is a tone
        (b / "joined.txt").write_text("")
        (b / "parts.txt").write_text("".join(f"file '/x/{s}.mp4'\n" for s in ("S00Opening", "S01Why", "S02Tools")))
        (b / "presenter" / "lines.json").write_text(json.dumps(LINES))
        (b / "presenter" / "presenter.html").write_text("<html></html>")
        cls.webm = voice_webm(root / "voice.webm")
        import serve_presenter as sp
        cls.sp = importlib.reload(sp)
        cls.sp.Studio.log_message = lambda *a: None        # quiet: one line per request
        cls.sp.sync()
        threading.Thread(target=cls.sp._worker, daemon=True).start()
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(cls.sp.Studio, directory=str(root)))
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        cls.root = root

    @classmethod
    def tearDownClass(cls):
        cls.labels.use(cls.old_labels)
        if cls.old_nar is None:
            os.environ.pop("STUDIO_NARRATION", None)
        else:
            os.environ["STUDIO_NARRATION"] = cls.old_nar
        cls.srv.shutdown()
        cls.tmp.cleanup()

    # ─── helpers ───
    def req(self, path, body=None, method="POST"):
        data = body if isinstance(body, bytes) or body is None else json.dumps(body).encode()
        r = urllib.request.Request(self.url + path, data=data, method=method)
        with urllib.request.urlopen(r, timeout=30) as f:
            raw = f.read()
            return json.loads(raw) if raw[:1] in (b"{", b"[") else raw

    def get(self, path):
        return self.req(path, method="GET")

    def record(self, name, events, finish=True, order=None):
        pieces = [self.webm[i:i + 6000] for i in range(0, len(self.webm), 6000)]
        for k in order or range(len(pieces)):
            self.req(f"/api/chunk?build={B}&name={name}&seq={k}", pieces[k])
        self.req(f"/api/events?build={B}&name={name}", events)
        if finish:
            self.req(f"/api/finish?build={B}&name={name}", b"")
        return len(pieces)

    def wait(self, test, what, timeout=120):
        t0 = time.time()
        while time.time() - t0 < timeout:
            p = self.get(f"/api/project?build={B}")
            if test(p):
                return p
            failed = [j for j in p["jobs"] if j["state"] == "failed"]
            if failed:
                self.fail(f"{what}: job failed: {failed}")
            time.sleep(0.5)
        self.fail(f"timed out waiting for {what}")

    def session_ready(self, name):
        return lambda p: any(s["name"] == name and s["state"] == "ready" for s in p["sessions"])

    # ─── the tests (numbered: they share one project) ───
    def test_1_record_take_edit_export(self):
        n = self.record("2026-10-19T10-00-00", EVENTS(), order=None)
        pieces = list(range(n))
        self.assertGreater(len(pieces), 3)
        counts = self.get(f"/api/counts?build={B}")
        self.assertEqual(counts, {"0": 1, "1": 1, "2": 1})            # line 1's retake does not count

        p = self.wait(self.session_ready("2026-10-19T10-00-00"), "processing")
        takes = p["takes"]
        self.assertEqual([len(takes[str(k)]) for k in range(3)], [1, 2, 1])
        self.assertTrue(takes["1"][0]["rejected"])
        used = [tid for _, _, _, tid in p["edit_list"]["lines"]]
        self.assertEqual(used, ["2026-10-19T10-00-00@1.00", "2026-10-19T10-00-00@18.00", "2026-10-19T10-00-00@31.00"])
        el = p["edit_list"]
        self.assertAlmostEqual(T.length(el["voice"]), T.length(el["picture"]), places=6)
        self.assertAlmostEqual(T.length(el["voice"]), 14 + 13 + 12, places=3)    # each take as recorded

        # choose the rejected take for line 1, then go back to the default
        rej = takes["1"][0]["id"]
        self.req(f"/api/choose?build={B}&line=1&take={rej}")
        self.assertEqual(self.get(f"/api/project?build={B}")["edit_list"]["lines"][1][3], rej)
        self.req(f"/api/choose?build={B}&line=1&take=")

        # nudge line 0 and shorten the pauses everywhere: lengths follow
        t0 = takes["0"][0]["id"]
        self.req(f"/api/edit?build={B}&take={t0}", {"nudge": 0.3})
        p = self.get(f"/api/project?build={B}")
        self.assertAlmostEqual(p["takes"]["0"][0]["length"], 14.3, places=3)
        v0 = p["takes"]["0"][0]
        tight = v0["tighten"]
        self.assertAlmostEqual(v0["tail"], 4.0, delta=0.1)               # the voice stops 4 s before the take does
        self.assertAlmostEqual(v0["lead"], 0.2, delta=0.05)            # the quiet before the voice, from the take start
        self.assertEqual(v0["margin"], 0.3)
        self.assertAlmostEqual(tight["trim_out"], v0["tail"] - 0.3, delta=0.01)      # leave the 0.3 s margin
        self.assertIsNone(tight["trim_in"])
        self.assertGreater(tight["gain"], 2.5)
        self.assertEqual(self.req(f"/api/shrink?build={B}")["saved"] > 2.5, True)
        p = self.get(f"/api/project?build={B}")
        e0 = p["takes"]["0"][0]
        self.assertEqual(e0["edit"]["trim_out"], tight["trim_out"])      # the tool's own, apart from the manual cuts
        self.assertEqual(e0["edit"]["auto"], ["trim_out"])
        self.assertNotIn("cuts", e0["edit"])
        self.assertNotIn("squeeze", e0["edit"])
        self.assertEqual((e0["tighten"]["trim_out"], e0["tighten"]["gain"]), (None, 0))     # nothing left to add
        self.assertLess(e0["length"], 14.3 - 2.5)
        total = T.length(p["edit_list"]["voice"])

        # export, and the files match the edit list
        self.req(f"/api/export?build={B}&clean=off")
        p = self.wait(lambda p: any(j["kind"] == "export" and j["state"] == "done" for j in p["jobs"]), "export", 240)
        names = {f["name"] for f in p["exports"]}
        self.assertEqual(names, {f"{B}_edited.mp4", f"{B}_edited.srt", f"{B}_edited.chapters.txt"})
        out = self.root / B / "presenter" / "export"
        self.assertAlmostEqual(duration(out / f"{B}_edited.mp4", "v:0"), total, delta=1 / 60 + 1e-3)
        self.assertAlmostEqual(duration(out / f"{B}_edited.mp4", "a:0"), total, delta=0.05)
        srt = (out / f"{B}_edited.srt").read_text()
        self.assertIn("Line one is about agents.", srt)
        self.assertEqual(srt.count(" --> "), 3)
        self.assertEqual((out / f"{B}_edited.chapters.txt").read_text().splitlines()[0], "0:00 Opening")
        # the voice is where the edit list puts it: loud while line 0 speaks, quiet in its kept tail
        x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(out / f"{B}_edited.mp4"), "-ac", "1",
                                          "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
        rms = lambda a, b: float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))   # noqa: E731
        self.assertGreater(rms(0.3 + 2, 0.3 + 9), 0.05)                # line 0's voice (after the 0.3 s nudge)
        self.assertLess(rms(0.3 + 10.2, 0.3 + 10.4), 0.02)             # the 0.25 s breath kept after it

    def test_1b_tightening_can_be_taken_back_and_keeps_manual_cuts(self):
        t0 = self.get(f"/api/project?build={B}")["takes"]["0"][0]["id"]
        before = self.get(f"/api/project?build={B}")["takes"]["0"][0]["edit"]
        self.req(f"/api/edit?build={B}&take={t0}", {"cuts": [[1.0, 1.2]]})        # the instructor's own cut
        once = self.get(f"/api/project?build={B}")["takes"]["0"][0]["edit"]
        self.req(f"/api/shrink?build={B}&take={t0}")                              # pressed again: nothing new
        self.assertEqual(self.get(f"/api/project?build={B}")["takes"]["0"][0]["edit"], once)
        self.req(f"/api/unshrink?build={B}&take={t0}")
        gone = self.get(f"/api/project?build={B}")["takes"]["0"][0]
        self.assertEqual(before["auto"], ["trim_out"])
        self.assertEqual(gone["edit"], {"nudge": 0.3, "cuts": [[1.0, 1.2]]})        # the trim the tool set is gone
        self.assertGreater(gone["tighten"]["gain"], 2.5)                           # and it can be done again
        self.req(f"/api/shrink?build={B}&take={t0}")
        again = self.get(f"/api/project?build={B}")["takes"]["0"][0]["edit"]
        self.assertEqual((again["cuts"], again["trim_out"], again["auto"]), ([[1.0, 1.2]], once["trim_out"], ["trim_out"]))

    def test_1c_fit_the_handles_and_undo(self):
        """/api/fit sets the trims by the margin; a trim the handles set by hand survives undo, a tool-set one does not."""
        view = lambda: self.get(f"/api/project?build={B}")["takes"]["0"][0]          # noqa: E731
        t0 = view()["id"]
        self.req(f"/api/unshrink?build={B}&take={t0}")
        self.req(f"/api/edit?build={B}&take={t0}", {"nudge": None})
        self.assertEqual(view()["edit"], {"cuts": [[1.0, 1.2]]})
        self.req(f"/api/fit?build={B}&take={t0}&end=end")
        e = view()["edit"]
        self.assertAlmostEqual(e["trim_out"], view()["tail"] - 0.3, delta=0.01)
        self.assertEqual((e["auto"], "trim_in" in e), (["trim_out"], False))
        self.req(f"/api/fit?build={B}&take={t0}&end=start")                         # no silence before the voice: nothing
        self.assertNotIn("trim_in", view()["edit"])
        # the handle dragged by hand: a trim_in the tool did not set; undo takes back the tool's trim only
        self.req(f"/api/edit?build={B}&take={t0}", {"trim_in": 0.15})
        e = view()["edit"]
        self.assertEqual((e["trim_in"], e["auto"]), (0.15, ["trim_out"]))
        self.req(f"/api/unshrink?build={B}&take={t0}")
        self.assertEqual(view()["edit"], {"cuts": [[1.0, 1.2]], "trim_in": 0.15})
        # dragging the end handle over a tool-set trim makes it the instructor's
        self.req(f"/api/fit?build={B}&take={t0}&end=both")
        self.assertEqual(view()["edit"]["auto"], ["trim_out"])                      # (no voice-free start: trim_in cleared)
        self.req(f"/api/edit?build={B}&take={t0}", {"trim_in": 0.15, "trim_out": 2.0})
        e = view()["edit"]
        self.assertEqual((e["trim_in"], e["trim_out"], e.get("auto")), (0.15, 2.0, None))
        self.req(f"/api/shrink?build={B}&take={t0}")                                # tighten all respects it
        self.assertEqual(view()["edit"]["trim_out"], 2.0)
        self.req(f"/api/unshrink?build={B}&take={t0}")
        self.assertEqual(view()["edit"], {"cuts": [[1.0, 1.2]], "trim_in": 0.15, "trim_out": 2.0})
        self.req(f"/api/edit?build={B}&take={t0}", {"trim_in": None, "trim_out": None, "cuts": None, "nudge": 0.3})
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.req(f"/api/fit?build={B}&take={t0}&end=middle")
        self.assertEqual(cm.exception.code, 400)

    def test_1d_levels_of_a_session_and_of_the_original(self):
        p = self.get(f"/api/project?build={B}")
        name = p["sessions"][0]["name"]
        lv = self.get(f"/api/levels?build={B}&src={name}")
        self.assertEqual(lv["step"], 0.02)
        self.assertAlmostEqual(len(lv["db"]) * 0.02, 43.5, delta=0.1)
        db = lv["db"]
        self.assertTrue(-18 <= np.median(db[int(3 / 0.02):int(9 / 0.02)]) <= -9)       # the 220 Hz voice, amp 0.3
        self.assertLess(np.median(db[int(12 / 0.02):int(14 / 0.02)]), -40)             # the gap before line 1
        og = self.get(f"/api/levels?build={B}&src=__original__")
        self.assertAlmostEqual(len(og["db"]) * 0.02, 30.0, delta=0.1)
        self.assertTrue(-26 <= np.median(og["db"]) <= -16)                              # the built video's 440 Hz sine
        self.assertTrue((self.root / B / "presenter" / "original.levels.json").exists())
        for bad in (f"/api/levels?build={B}&src=nope", f"/api/levels?build={B}&src=../../etc/passwd", f"/api/levels?build={B}"):
            with self.assertRaises(urllib.error.HTTPError, msg=bad) as cm:
                self.get(bad)
            self.assertEqual(cm.exception.code, 404, bad)

    def test_1e_the_margin_setting_round_trips_and_moves_the_fit(self):
        self.assertEqual(self.get(f"/api/project?build={B}")["settings"]["margin"], "0.3")       # the default
        t = lambda: self.get(f"/api/project?build={B}")["takes"]["0"][0]                          # noqa: E731
        fit_at_03 = t()["fit"][1]
        self.req(f"/api/settings?build={B}&key=margin&value=0.8")
        p = self.get(f"/api/project?build={B}")
        self.assertEqual((p["settings"]["margin"], p["takes"]["0"][0]["margin"]), ("0.8", 0.8))
        self.assertAlmostEqual(p["takes"]["0"][0]["fit"][1], fit_at_03 - 0.5, delta=0.001)
        for bad in ("abc", "-1", "9"):
            with self.assertRaises(urllib.error.HTTPError, msg=bad) as cm:
                self.req(f"/api/settings?build={B}&key=margin&value={bad}")
            self.assertEqual(cm.exception.code, 400)
        self.req(f"/api/settings?build={B}&key=margin&value=0.3")
        self.assertEqual(self.get(f"/api/project?build={B}")["settings"]["margin"], "0.3")

    def test_2_a_session_cut_off_is_recovered(self):
        name = "2026-10-19T11-00-00"
        ev = [e for e in EVENTS() if e[0] < 20]                          # the tab closed at 20 s: no stop
        self.record(name, ev, finish=False)
        with self.sp.dbc() as c:
            c.execute("update sessions set updated=updated-1000 where name=?", (name,))
        p = self.wait(self.session_ready(name), "recovery")
        lines_of = [t["line"] for k in p["takes"] for t in p["takes"][k] if t["session"] == name]
        self.assertEqual(sorted(lines_of), [0, 1, 1])                   # the last take runs to where the audio ends
        last = max((t for k in p["takes"] for t in p["takes"][k] if t["session"] == name), key=lambda t: t["t_in"])
        self.assertAlmostEqual(last["t_out"], 43.5, delta=0.1)

    def test_2b_one_line_with_takes_from_two_sessions(self):
        """/api/line: the takes of one line from every usable session, the take the video uses, the audio, the joins;
        choose, mistake and delete change it; a recording not yet processed is listed as pending."""
        line = lambda k=1: self.get(f"/api/line?build={B}&line={k}")                 # noqa: E731
        a, b = "2026-10-19T10-00-00", "2026-10-19T11-00-00"
        d = line()
        self.assertEqual((d["line"], d["text"], d["lines"]), (1, LINES[1][1], 3))
        ids = [t["id"] for t in d["takes"]]
        self.assertEqual(ids, [f"{a}@15.00", f"{a}@18.00", f"{b}@15.00", f"{b}@18.00"])     # both sessions, oldest first
        self.assertEqual([t["rejected"] for t in d["takes"]], [True, False, True, False])
        self.assertEqual(d["chosen"], f"{b}@18.00")                                  # the newest that is not a mistake
        self.assertIsNone(d["picked"])
        proj = self.get(f"/api/project?build={B}")
        self.assertEqual(d["chosen"], proj["edit_list"]["lines"][1][3])              # the same one the video uses
        for t in d["takes"]:                                                        # what the editor gets for a take
            self.assertEqual(t, next(x for x in proj["takes"]["1"] if x["id"] == t["id"]))
            self.assertTrue(t["tracks"]["voice"] and t["tracks"]["picture"])
            self.assertIn("raw_picture", t)
            self.assertIn("fit", t)
        self.assertEqual(set(d["audio"]), {a, b, "__original__"})
        self.assertEqual(d["audio"], proj["audio"])
        self.assertEqual((d["margin"], d["video"]), (0.3, f"/{B}/presenter/{B}_silent.mp4"))
        self.assertEqual(d["video_version"], proj["video_version"])
        self.assertEqual((d["pending"], d["busy"]), ([], False))
        # the joins: the last 2 s of line 0 and the first 2 s of line 2, as the video plays them
        c = d["context"]
        self.assertEqual((c["prev"], c["next"]), (proj["edit_list"]["lines"][0][3], proj["edit_list"]["lines"][2][3]))
        for side in ("before", "after"):
            self.assertAlmostEqual(T.length(c[side]["voice"]), 2.0, places=6)
            self.assertAlmostEqual(T.length(c[side]["picture"]), 2.0, places=6)
        el = proj["edit_list"]
        end0 = el["lines"][0][2]
        want = T.window(el, end0 - 2, end0)                                          # cut from the whole lecture's edit list
        got = c["before"]
        self.assertEqual([list(x) for x in got["voice"]], [list(x) for x in want["voice"]])
        self.assertEqual([list(x) for x in got["picture"]], [list(x) for x in want["picture"]])
        a2 = el["lines"][2][1]
        self.assertEqual([list(x) for x in c["after"]["voice"]], [list(x) for x in T.window(el, a2, a2 + 2)["voice"]])
        # the first line has nothing before it; a line that does not exist is a JSON 404
        self.assertEqual(line(0)["context"]["before"], {"voice": [], "picture": []})
        for bad in (f"/api/line?build={B}&line=9", f"/api/line?build={B}&line=x", f"/api/line?build={B}"):
            with self.assertRaises(urllib.error.HTTPError, msg=bad) as cm:
                self.get(bad)
            self.assertEqual(cm.exception.code, 404, bad)
            self.assertIn("error", json.loads(cm.exception.read()))
        # choose, mistake and delete go through the editor's own endpoints and show in the line
        pick = f"{a}@18.00"
        self.req(f"/api/choose?build={B}&line=1&take={pick}")
        self.assertEqual((line()["chosen"], line()["picked"]), (pick, pick))
        self.req(f"/api/edit?build={B}&take={pick}", {"rejected": True})
        self.assertTrue(next(t for t in line()["takes"] if t["id"] == pick)["rejected"])
        self.assertEqual(line()["chosen"], pick)                                      # picked by hand: still used
        self.req(f"/api/choose?build={B}&line=1&take=")
        self.req(f"/api/edit?build={B}&take={pick}", {"rejected": None})
        self.assertEqual(line()["chosen"], f"{b}@18.00")
        self.req(f"/api/edit?build={B}&take={b}@18.00", {"rejected": True})          # the newest is a mistake: the one before
        self.assertEqual(line()["chosen"], f"{a}@18.00")
        self.req(f"/api/edit?build={B}&take={b}@18.00", {"rejected": None})
        self.req(f"/api/edit?build={B}&take={b}@18.00", {"deleted": True})
        d = line()
        self.assertNotIn(f"{b}@18.00", [t["id"] for t in d["takes"]])
        self.assertEqual(d["chosen"], pick)
        self.req(f"/api/edit?build={B}&take={b}@18.00", {"deleted": None})
        self.assertEqual(line()["chosen"], f"{b}@18.00")
        # a recording still going is listed, with the take it will make
        c_name = "2026-10-19T11-30-00"
        self.record(c_name, [e for e in EVENTS() if e[0] < 20], finish=False)
        pend = line()["pending"]
        self.assertEqual([(p["session"], p["state"]) for p in pend], [(c_name, "recording")] * 2)
        self.assertTrue(line()["busy"])
        self.assertEqual(len(line(0)["pending"]), 1)
        self.req(f"/api/finish?build={B}&name={c_name}", b"")
        self.wait(self.session_ready(c_name), "processing")
        d = line()
        self.assertEqual((d["pending"], d["busy"], len(d["takes"])), ([], False, 6))
        self.assertEqual(d["chosen"], f"{c_name}@18.00")                              # the newest take is the used one
        self.req(f"/api/delete?build={B}&name={c_name}")
        self.assertEqual(len(line()["takes"]), 4)

    def test_2c_the_presenter_page_is_rendered_by_the_server(self):
        """presenter.html is made from presenter.PAGE with the build's lines and silent video, whatever the file says."""
        page = self.get(f"/{B}/presenter/presenter.html").decode()
        mtime = int((self.root / B / "presenter" / f"{B}_silent.mp4").stat().st_mtime)
        self.assertIn(f'src="{B}_silent.mp4?v={mtime}"', page)
        self.assertIn("const L = " + json.dumps(LINES, ensure_ascii=False), page)
        self.assertIn(f'BUILD = "{B}"', page)
        self.assertNotIn("__LINES__", page)
        self.assertIn("/studio-static/presenter/takes.js", page)
        import presenter
        self.assertEqual(page, presenter.render(LINES, B, self.root / B / "presenter" / f"{B}_silent.mp4"))
        for name in ("takes.js", "takes.css"):
            self.assertEqual(self.get(f"/studio-static/presenter/{name}"), (HERE / "studio" / "static" / "presenter" / name).read_bytes())
        b = "m7_lecture97_en"                                                          # not prepared: the file on disk, if any
        (self.root / b / "presenter").mkdir(parents=True)
        (self.root / b / f"{b}.mp4").write_bytes(b"x")
        (self.root / b / "presenter" / "presenter.html").write_text("<html>static</html>")
        self.assertEqual(self.get(f"/{b}/presenter/presenter.html"), b"<html>static</html>")

    def test_3_requests_that_are_refused(self):
        for path, body in [(f"/api/edit?build={B}&take=x", {"volume": 3}),          # not an edit field
                           (f"/api/edit?build={B}&take=x", {"nudge": 9}),           # out of range
                           (f"/api/chunk?build={B}&name=../etc&seq=0", b"x"),         # not a session name
                           (f"/api/chunk?build=nope&name=2026-10-19T10-00-00&seq=0", b"x")]:
            with self.assertRaises(urllib.error.HTTPError, msg=path) as cm:
                self.req(path, body)
            self.assertEqual(cm.exception.code, 400, path)

    def test_5_an_unrecorded_line_keeps_the_original_voice_or_is_silent(self):
        p = self.get(f"/api/project?build={B}")
        self.assertEqual(p["settings"]["missing"], "original")
        for t in p["takes"]["2"]:                                       # hide every take of line 2
            self.req(f"/api/edit?build={B}&take={t['id']}", {"deleted": True})
        p = self.get(f"/api/project?build={B}")
        k, a, b, tid = p["edit_list"]["lines"][2]
        self.assertEqual((tid, round(b - a, 3)), (None, 10.0))          # line 2 as built: 10 s at full speed
        self.assertIn("__original__", p["audio"])
        for mode, loud in (("original", True), ("silent", False)):
            self.req(f"/api/settings?build={B}&key=missing&value={mode}")
            self.req(f"/api/export?build={B}&clean=off")
            self.wait(lambda p: all(j["state"] in ("done", "failed") for j in p["jobs"] if j["kind"] == "export"),
                      "export", 240)
            out = self.root / B / "presenter" / "export" / f"{B}_edited.mp4"
            x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-ac", "1", "-ar", str(SR),
                                              "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
            seg = x[int((a + 2) * SR):int((b - 2) * SR)]
            rms = float(np.sqrt(np.mean(seg ** 2)))
            self.assertEqual(rms > 0.05, loud, f"{mode}: rms {rms:.3f}")
        self.req(f"/api/settings?build={B}&key=missing&value=original")
        with self.assertRaises(urllib.error.HTTPError):
            self.req(f"/api/settings?build={B}&key=missing&value=loud")

    def test_6_the_wire(self):
        """Over the slow tunnel: capped open ranges, gzip for text only, caching for media, errors as JSON."""
        def fetch(path, **h):
            r = urllib.request.Request(self.url + path, headers=h)
            with urllib.request.urlopen(r, timeout=30) as f:
                return f.status, dict(f.headers), f.read()
        mp4 = f"/{B}/presenter/{B}_silent.mp4"
        size = (self.root / B / "presenter" / f"{B}_silent.mp4").stat().st_size
        self.sp.RANGE_CAP = 1000
        try:
            st, h, body = fetch(mp4, Range="bytes=0-")
            self.assertEqual((st, len(body), h["Content-Range"]), (206, 1000, f"bytes 0-999/{size}"))
            st, h, body = fetch(mp4 + "?v=1", Range="bytes=500-2999")                 # asked for: given
            self.assertEqual((st, len(body)), (206, 2500))
            st, h, body = fetch(mp4, Range=f"bytes={size - 10}-")
            self.assertEqual(len(body), 10)
        finally:
            self.sp.RANGE_CAP = 4 << 20
        self.assertEqual(h["Accept-Ranges"], "bytes")
        h = fetch(mp4)[1]                                                   # no ?v=: the browser must ask each time
        self.assertEqual(h["Cache-Control"], "no-cache")
        self.assertNotIn("max-age", str(h))
        h = fetch(mp4 + "?v=5", Range="bytes=0-9")[1]
        self.assertEqual(h["Cache-Control"], "private, max-age=86400")
        etag = fetch(mp4)[1]["ETag"]                                        # a validator on 200 and on 206
        self.assertRegex(etag, r'^"[0-9a-f]+-[0-9a-f]+"$')
        self.assertEqual(h["ETag"], etag)
        for extra in ({}, {"Range": "bytes=0-9"}):
            with self.assertRaises(urllib.error.HTTPError) as cm:
                fetch(mp4, **{"If-None-Match": etag}, **extra)
            self.assertEqual(cm.exception.code, 304)
        st, h, body = fetch(mp4, Range="bytes=0-9", **{"If-Range": etag})            # unchanged: the range is honoured
        self.assertEqual((st, len(body)), (206, 10))
        st, h, body = fetch(mp4, Range="bytes=0-9", **{"If-Range": '"old-1"'})       # changed: the whole file, no cap
        self.assertEqual((st, len(body)), (200, size))
        self.assertIn(f"{B}.mp4?v=", self.get(f"/lecture?build={B}").decode())
        with self.assertRaises(urllib.error.HTTPError) as cm:
            fetch(mp4, Range=f"bytes={size}-")
        self.assertEqual(cm.exception.code, 416)
        import gzip
        st, h, body = fetch(f"/api/project?build={B}", **{"Accept-Encoding": "gzip"})
        self.assertEqual(h["Content-Encoding"], "gzip")
        self.assertEqual(h["Cache-Control"], "no-store")
        self.assertEqual(json.loads(gzip.decompress(body))["build"], B)
        self.assertNotIn("Content-Encoding", fetch(f"/api/project?build={B}")[1])
        lines = f"/{B}/presenter/lines.json"
        st, h, body = fetch(lines, **{"Accept-Encoding": "gzip"})
        self.assertEqual((h.get("Content-Encoding"), json.loads(gzip.decompress(body))), ("gzip", LINES))
        self.assertNotIn("Content-Encoding", fetch(mp4, **{"Accept-Encoding": "gzip"})[1])     # media never
        p = self.get(f"/api/project?build={B}")
        for url in p["audio"].values():
            self.assertRegex(url, r"\.m4a\?v=\d+$")
        self.assertEqual(fetch(p["audio"][next(iter(p["audio"]))])[0], 200)           # the query string is ignored

    def test_7_a_build_without_a_presenter_page_is_a_json_404(self):
        b = "m7_lecture98_en"
        (self.root / b).mkdir()
        (self.root / b / f"{b}.mp4").write_bytes(b"x")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.get(f"/api/project?build={b}")
        self.assertEqual(cm.exception.code, 404)
        self.assertEqual(json.loads(cm.exception.read()), {"error": "prepare the presenter page first"})

    def test_8_deleting_a_recording_forgets_its_session(self):
        name = "2026-10-19T12-00-00"
        self.record(name, [e for e in EVENTS() if e[0] < 20])
        self.wait(self.session_ready(name), "processing")
        self.req(f"/api/delete?build={B}&name={name}")
        p = self.get(f"/api/project?build={B}")
        self.assertNotIn(name, [s["name"] for s in p["sessions"]])
        self.assertFalse([f for f in (self.root / B / "presenter" / "recordings").iterdir() if f.name.startswith(name)])

    def test_9_versions_are_created_listed_and_discarded_over_http(self):
        queued, real = [], self.sp.make_version
        self.sp.make_version = lambda build, scene, n: queued.append((build, scene, n))     # the job runner stubbed
        try:
            out = self.req(f"/api/version?build={B}&line=1", {"text": "Line two,  the   tools, rewritten."})
            self.assertEqual(out, {"scene": "S01Why", "n": 1})
            self.assertEqual(queued, [(B, "S01Why", 1)])
            p = self.get(f"/api/project?build={B}")
            self.assertEqual(p["scenes"], ["S00Opening", "S01Why", "S02Tools"])
            v = p["versions"]["S01Why"][0]
            self.assertEqual((v["n"], v["base"], v["state"], v["texts"], v["changed"], v["video"]),
                             (1, None, "queued", {"1": "Line two, the tools, rewritten."}, ["1"], None))
            for bad in (f"/api/version?build={B}&line=1", f"/api/version?build={B}&line=99"):    # one is still being made
                with self.assertRaises(urllib.error.HTTPError) as cm:
                    self.req(bad, {"text": "x"})
                self.assertEqual(cm.exception.code, 400)
            with self.assertRaises(urllib.error.HTTPError) as cm:                      # not ready: nothing to merge
                self.req(f"/api/version/merge?build={B}&scene=S01Why&n=1")
            self.assertEqual(cm.exception.code, 400)
            self.req(f"/api/version/discard?build={B}&scene=S01Why&n=1")
            self.assertEqual(self.get(f"/api/project?build={B}")["versions"], {})
            self.assertFalse((self.root / B / "versions" / "S01Why" / "v1").exists())
            self.req(f"/api/version?build={B}&line=1", {})                              # no text: re-voice as is
            self.assertEqual(self.get(f"/api/project?build={B}")["versions"]["S01Why"][0]["texts"], {"1": LINES[1][1]})
            self.req(f"/api/version/discard?build={B}&scene=S01Why&n=2")
            self.assertEqual(len(queued), 2)
        finally:
            self.sp.make_version = real

    def test_9b_static_files_are_served_with_revalidation_and_stay_inside_static(self):
        r = urllib.request.urlopen(self.url + "/studio-static/editor/main.js")
        self.assertIn("javascript", r.headers["Content-Type"])
        self.assertEqual(r.headers["Cache-Control"], "no-cache")
        self.assertEqual(r.read(), (HERE / "studio" / "static" / "editor" / "main.js").read_bytes())
        self.assertIn("css", urllib.request.urlopen(self.url + "/studio-static/editor.css").headers["Content-Type"])
        lm = r.headers["Last-Modified"]
        with self.assertRaises(urllib.error.HTTPError) as cm:                          # unchanged: not sent again
            urllib.request.urlopen(urllib.request.Request(self.url + "/studio-static/editor/main.js", headers={"If-Modified-Since": lm}))
        self.assertEqual(cm.exception.code, 304)
        for bad in ("/studio-static/../serve_presenter.py", "/studio-static/%2e%2e/serve_presenter.py",
                    "/studio-static/editor/../../editor.html", "/studio-static/nothing.js", "/studio-static/editor"):
            with self.assertRaises(urllib.error.HTTPError, msg=bad) as cm:
                urllib.request.urlopen(self.url + bad)
            self.assertEqual(cm.exception.code, 404, bad)

    def test_9c_languages_are_added_drafted_approved_and_flagged_over_http(self):
        def narr(lang, **q):
            return self.get(f"/api/narration?lecture=m7_lecture99&lang={lang}")

        def post(action, lang, key, body=None, kind="line"):
            return self.req(f"/api/narration/{action}?lecture=m7_lecture99&lang={lang}&kind={kind}&key={key}", body)

        def refused(f, code=400):
            with self.assertRaises(urllib.error.HTTPError) as cm:
                f()
            self.assertEqual(cm.exception.code, code)
            body = cm.exception.read()
            return json.loads(body) if body[:1] == b"{" else {}
        studio = self.get("/?m=7").decode()
        self.assertIn("Lecture 99", studio)
        self.assertIn("+ add language", studio)
        self.assertNotIn("Russian</h3>", studio)
        self.assertEqual(self.req("/api/narration/add?lecture=m7_lecture99&lang=ru"), {"file": "m7_lecture99_ru.md"})
        self.assertIn("ask Claude to draft Russian for this lecture", self.get("/?m=7").decode())
        ru = narr("ru")
        self.assertEqual([(l["key"], l["state"]) for l in ru["lines"]], [("0.0", "empty"), ("1.1", "empty"), ("1.2", "empty")])
        self.assertEqual((ru["primary"], ru["have"]), ("en", ["uz", "en", "ru"]))
        refused(lambda: self.req("/api/narration/add?lecture=m7_lecture99&lang=ru"))                  # a second skeleton
        refused(lambda: post("approve", "ru", "1.1"))                                                 # an empty line
        # draft a line: save writes the file and approves it
        out = post("save", "ru", "1.1", {"text": "Строка вторая, инструменты."})
        self.assertEqual((out["item"]["state"], out["counts"]["approved"], out["counts"]["empty"]), ("approved", 1, 2))
        self.assertIn("1. **Строка вторая, инструменты.**", (self.root / "narration" / "m7_lecture99_ru.md").read_text())
        # the Uzbek line changes (the instructor's edit): the Russian one needs an update, with the diff
        bi = (self.root / "narration" / "m7_lecture99.md").read_text()
        post("save", "uz", "1.1", {"text": "Ikkinchi qator, asboblar."})
        after = (self.root / "narration" / "m7_lecture99.md").read_text()
        self.assertEqual(after, bi.replace("Ikkinchi qator, vositalar.", "Ikkinchi qator, asboblar."))   # the English gloss is as it was
        line = next(l for l in narr("ru")["lines"] if l["key"] == "1.1")
        self.assertEqual(line["state"], "needs_update")
        self.assertEqual(line["changed"], {"uz": {"old": "Ikkinchi qator, vositalar.", "new": "Ikkinchi qator, asboblar."}})
        self.assertIn("1 need update", self.get("/?m=7").decode())
        # the editor knows: its header links to the review page of a language with no build, and the line carries the flag
        page = self.get(f"/edit?build={B}").decode()
        self.assertIn("/narration?lecture=m7_lecture99&amp;lang=ru", page)
        el = self.get(f"/api/editor-langs?build={B}")
        self.assertEqual([(o["lang"], o["build"]) for o in el["others"]], [("uz", None), ("ru", None)])
        self.assertEqual(el["lines"]["1"]["key"], "1.1")
        self.assertEqual({o["lang"] for o in el["lines"]["1"]["others"]}, {"uz", "ru"})
        # still fine clears it; an unknown key or kind is refused, and a lecture that is not there is a 404
        out = post("fine", "ru", "1.1")
        self.assertEqual(out["item"]["state"], "approved")
        refused(lambda: post("fine", "ru", "1.1"))
        refused(lambda: post("approve", "ru", "9.9"))
        refused(lambda: post("approve", "ru", "1.1", kind="thing"))
        refused(lambda: self.req("/api/narration/add?lecture=m7_lecture12&lang=ru"), 404)
        refused(lambda: self.get("/api/narration?lecture=m7_lecture99&lang=xx"), 404)
        self.assertIn("narration review", self.get("/narration?lecture=m7_lecture99&lang=ru").decode())

    def test_4_pages(self):
        page = self.get(f"/edit?build={B}").decode()
        self.assertIn(f'const BUILD = "{B}"', page)
        self.assertNotIn("__", page.split("<script>")[1].split("BUILD")[0])  # every placeholder filled
        studio = self.get("/?m=7").decode()
        self.assertIn(f"/edit?build={B}", studio)


if __name__ == "__main__":
    unittest.main()
