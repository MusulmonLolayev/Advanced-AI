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
        proposed = p["takes"]["0"][0]["proposed"]
        self.assertTrue(proposed, "the 4 s tail pause over a still picture should be proposed")
        self.req(f"/api/shrink?build={B}")
        p = self.get(f"/api/project?build={B}")
        e0 = p["takes"]["0"][0]
        self.assertEqual(e0["edit"]["cuts"], [list(x) for x in proposed])
        self.assertEqual(e0["proposed"], [])                            # nothing left to propose
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

    def test_4_pages(self):
        page = self.get(f"/edit?build={B}").decode()
        self.assertIn(f'const BUILD = "{B}"', page)
        self.assertNotIn("__", page.split("<script>")[1].split("BUILD")[0])  # every placeholder filled
        studio = self.get("/?m=7").decode()
        self.assertIn(f"/edit?build={B}", studio)


if __name__ == "__main__":
    unittest.main()
