"""The presenter page in a real (headless) Chromium with a fake microphone, against the real server on a free port and
a scratch root holding a small lecture (four 3-second lines, real picture and sound). The browser is driven by
presenter_browser_check.py in the system Python (the one with Playwright; the project's venv has none): see there for
what is checked.

    uv run python -m unittest discover -s studio -p 'test_presenter_browser.py' -t .        (from video/; ~1 min)
Set PRESENTER_SHOTS=<dir> to also save screenshots of the panel there.
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

B = "m7_lecture96_en"
LINES = [[3.0 * k, f"Line number {k + 1} says something.", [[3.0 * k, 3.0 * k + 2.9, f"Line number {k + 1} says something."]], k]
         for k in range(4)]
CHROME = (glob.glob(str(Path.home() / ".cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell"))
          or glob.glob(str(Path.home() / ".cache/ms-playwright/chromium-*/chrome-linux/chrome")) or [None])[-1]


def ff(*a):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *map(str, a)], check=True)


@unittest.skipUnless(HAS_PLAYWRIGHT and CHROME, "playwright or its Chromium is not installed")
class Browser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = cls.root = Path(cls.tmp.name)
        os.environ["STUDIO_ROOT"], os.environ["STUDIO_PROFILE"] = str(root), "off"
        b = root / B
        (b / "presenter").mkdir(parents=True)
        silent = b / "presenter" / f"{B}_silent.mp4"
        ff("-f", "lavfi", "-i", "testsrc2=s=320x180:r=30:d=12", "-c:v", "libx264", "-preset", "ultrafast", "-g", "10",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", silent)
        ff("-i", silent, "-f", "lavfi", "-i", "sine=f=440:r=48000:d=12", "-c:v", "copy", "-c:a", "aac", "-shortest", b / f"{B}.mp4")
        (b / "joined.txt").write_text("")
        (b / "parts.txt").write_text("".join(f"file '/x/{s}.mp4'\n" for s in ("S00", "S01", "S02", "S03")))
        (b / "presenter" / "lines.json").write_text(json.dumps(LINES))
        import serve_presenter as sp
        cls.sp = importlib.reload(sp)
        cls.sp.Studio.log_message = lambda *a: None
        cls.sp.sync()
        threading.Thread(target=cls.sp._worker, daemon=True).start()
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(cls.sp.Studio, directory=str(root)))
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.tmp.cleanup()

    def test_the_takes_panel_in_a_browser(self):
        cmd = ["python3", str(HERE / "studio" / "presenter_browser_check.py"), self.url, B, CHROME]
        if os.environ.get("PRESENTER_SHOTS"):
            cmd.append(os.environ["PRESENTER_SHOTS"])
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])


if __name__ == "__main__":
    unittest.main()
