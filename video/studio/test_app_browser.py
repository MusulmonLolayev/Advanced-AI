"""The React app (studio/app, built into studio/static/app/) driven in headless Chromium with a fake microphone, against a
scratch server on a free port: a synthetic lecture (30 s of test picture, three lines, a bilingual narration) in a temp
folder built from fixtures, never the real out/. The browser is driven by app_browser_check.py in the system Python (the
one with Playwright; the project's venv has none). One project is shared by its numbered tests, in this order:

  1  the front door: / is the workspace (no tab bar), the project browser starts as the rail; an old address (/edit?build=) lands on its screen; the address is followed when it changes
  2  Record: the meter moves with the microphone; one take of a line (L) goes over HTTP as chunks 0..n, then events, then
     finish, and the take shows up; a whole session with one X mark logs the old page's event shapes; leaving while
     recording asks first
  3  Edit: playing moves the playhead and the picture; a trim handle posts one /api/edit; a click on the level strip plays the
     take from there; a drag on the wave and Delete cut that part (POST /api/edit cuts), the cut is drawn and the take is
     shorter, restore puts it back; the margin is saved; a recording is deleted after the confirm
  4  Script & languages: approve, save an edit (only that line of the narration file changes), still fine (needs update ->
     approved), the Uzbek rule (an unapproved Uzbek is refused, with the reason)
  6  one workspace: no tabs; Record toggles the monitor into the booth (microphone only while on); L from the plain workspace records a
     take; Script & languages is a drawer (Esc, focus trapped), Export a dialog; old mode= links land on the same things
  5  Export (a dialog): cleaning, the unrecorded-lines setting, an export (the job is stubbed) shows in the queue, the lecture video plays

Skipped without Playwright (in the system python3), without its Chromium, or when studio/static/app has not been built
(cd studio/app && npm run build).

    uv run python -m unittest discover -s studio -p 'test_app_browser.py' -t .      (from video/; ~2 min)
Set APP_SHOTS=<dir> to also save screenshots there.
"""
import glob
import importlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

HAS_PLAYWRIGHT = subprocess.run(["python3", "-c", "import playwright"], capture_output=True).returncode == 0
CHROME = (glob.glob(str(Path.home() / ".cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell"))
          or glob.glob(str(Path.home() / ".cache/ms-playwright/chromium-*/chrome-linux/chrome")) or [None])[-1]
APP = HERE / "studio" / "static" / "app" / "index.html"
B = "m7_lecture99_en"
STEM = "m7_lecture99"
SKIP = None if HAS_PLAYWRIGHT and CHROME and APP.exists() else "needs Playwright (system python3), its Chromium and a built app (cd studio/app && npm run build)"


def fixture(root):
    """The synthetic lecture: its video (with a tone as its own narration), the presenter page's files, a bilingual narration."""
    from studio.test_studio_e2e import LINES, NARRATION, ff
    b = root / B
    (b / "presenter").mkdir(parents=True)
    ff("-f", "lavfi", "-i", "testsrc2=s=320x180:r=60:d=30", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", b / "presenter" / f"{B}_silent.mp4")
    ff("-i", b / "presenter" / f"{B}_silent.mp4", "-f", "lavfi", "-i", "sine=f=440:r=48000:d=30", "-c:v", "copy", "-c:a", "aac", "-shortest", b / f"{B}.mp4")
    (b / "joined.txt").write_text("")
    (b / "parts.txt").write_text("".join(f"file '/x/{s}.mp4'\n" for s in ("S00Opening", "S01Why", "S02Tools")))
    (b / "presenter" / "lines.json").write_text(json.dumps(LINES))
    nar = root.parent / "narration"
    nar.mkdir()
    (nar / f"{STEM}.md").write_text(NARRATION)
    (nar / "labels.yaml").write_text("{}\n")
    return nar


@unittest.skipIf(SKIP, SKIP or "")
class Browser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name) / "out"
        cls.root.mkdir()
        cls.nar = fixture(cls.root)
        cls.env = {k: os.environ.get(k) for k in ("STUDIO_ROOT", "STUDIO_NARRATION", "STUDIO_PROFILE")}
        os.environ.update(STUDIO_ROOT=str(cls.root), STUDIO_NARRATION=str(cls.nar), STUDIO_PROFILE="off")
        import labels
        cls.labels, cls.old_labels = labels, labels.NARRATION
        labels.use(cls.nar)
        import serve_presenter as sp
        cls.sp = importlib.reload(sp)
        cls.sp.Studio.log_message = lambda *a: None
        cls.sp.sync()
        threading.Thread(target=cls.sp._worker, daemon=True).start()
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(cls.sp.Studio, directory=str(cls.root)))
        cls.srv.handle_error = lambda *a: None                 # a browser that stops loading a video breaks the pipe: not news
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.labels.use(cls.old_labels)
        for k, v in cls.env.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        cls.tmp.cleanup()

    def test_the_app_in_a_browser(self):
        cmd = ["python3", str(HERE / "studio" / "app_browser_check.py"), self.url, B, STEM, str(self.nar), CHROME]
        if os.environ.get("APP_SHOTS"):
            cmd.append(os.environ["APP_SHOTS"])
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-6000:])


if __name__ == "__main__":
    unittest.main()
