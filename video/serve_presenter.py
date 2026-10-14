"""Serve the built videos' presenter pages to another computer on the LAN (the server has no screen of its own).

The player seeks to every line, and Python's plain http.server ignores Range requests, so a seek re-downloads the
video from its start; this handler answers them. It serves only video/out/, read-only.

    uv run python serve_presenter.py 8800      # then open http://<this machine>:8800/lecture01_uz_navoiy/presenter/presenter.html
"""
import os
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent / "out"


class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        m = re.match(r"bytes=(\d+)-(\d*)", self.headers.get("Range", ""))
        path = Path(self.translate_path(self.path))
        if not m or not path.is_file():
            return super().send_head()
        size = path.stat().st_size
        start, end = int(m[1]), int(m[2] or size - 1)
        end = min(end, size - 1)
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(str(path)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._left = end - start + 1
        return f

    def copyfile(self, src, dst):
        left = getattr(self, "_left", None)
        if left is None:
            return super().copyfile(src, dst)
        while left > 0:
            chunk = src.read(min(1 << 16, left))
            if not chunk:
                break
            dst.write(chunk)
            left -= len(chunk)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8800
    print(f"serving {ROOT} on port {port} (pid {os.getpid()})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), partial(RangeHandler, directory=str(ROOT))).serve_forever()
