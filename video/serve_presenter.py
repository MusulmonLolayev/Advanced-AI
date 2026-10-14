"""The recording studio: a small web app, served to another computer on the LAN (the server has no screen of its own).

http://<host>:8080/ lists every built lecture: prepare its presenter page (presenter.py), open it to present and
record (key R), and build each recording into a 1080p video with the instructor's voice (compose_recording.py),
then download it. Jobs run one at a time in the background; the page shows their state.

The player seeks to every line, and Python's plain http.server ignores Range requests, so a seek re-downloads the
video from its start; this handler answers them. It serves video/out/ read-only, and takes one kind of upload: a presenter recording (POST /upload?build=…&name=…&kind=webm|json), saved to
<build>/presenter/recordings/. The microphone works only on a secure origin, so open the page through an ssh tunnel:
    ssh -L 8080:localhost:8080 musulmon@10.0.0.5     # then http://localhost:8080/<build>/presenter/presenter.html

    uv run python serve_presenter.py 8080      # then http://localhost:8080/ (through the tunnel)
"""
import html
import json
import os
import re
import subprocess
import sys
import threading
from functools import partial
from urllib.parse import parse_qs, quote, urlparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE / "out"
BUILD = re.compile(r"lecture\d\d_uz_navoiy")          # the statistics lectures
JOBS, LOCK = {}, threading.Lock()                      # (kind, build, name) -> {"state", "log"}
QUEUE = threading.Semaphore(1)                         # one heavy job at a time


def run_job(key, cmd):
    with LOCK:
        JOBS[key] = {"state": "queued", "log": ""}
    def work():
        with QUEUE:
            JOBS[key]["state"] = "running"
            r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
            JOBS[key].update(state="done" if r.returncode == 0 else "failed",
                             log=(r.stdout + r.stderr).strip().splitlines()[-1:] or [""])
    threading.Thread(target=work, daemon=True).start()


def builds():
    out = []
    for d in sorted(ROOT.iterdir()):
        if d.is_dir() and BUILD.fullmatch(d.name) and (d / f"{d.name}.mp4").exists() and (d / "joined.txt").exists():
            rec = d / "presenter" / "recordings"
            names = sorted({f.stem for f in rec.glob("*.webm") if (rec / f"{f.stem}.json").exists()}, reverse=True) \
                if rec.exists() else []
            out.append((d.name, (d / "presenter" / "presenter.html").exists(), names, rec))
    return out


def studio():
    rows = []
    for b, ready, names, rec in builds():
        job = JOBS.get(("prepare", b, ""), {})
        if ready:
            pres = f'<a class="btn" href="/{b}/presenter/presenter.html">Present &amp; record</a>'
        else:
            pres = f'<button onclick="post(\'/api/prepare?build={b}\')">Prepare presenter page</button>'
        if job.get("state") in ("queued", "running"):
            pres = f'<span class="busy">preparing…</span>'
        recs = []
        for n in names:
            j = JOBS.get(("compose", b, n), {})
            mp4 = rec / f"{n}.mp4"
            dur = json.loads((rec / f"{n}.json").read_text())
            mins = f"{dur[-1][0] / 60:.1f} min" if dur else ""
            if j.get("state") in ("queued", "running"):
                act = f'<span class="busy">{j["state"]}…</span>'
            else:
                act = f'<button onclick="post(\'/api/compose?build={b}&name={n}\')">{"Rebuild" if mp4.exists() else "Build video"}</button>'
                if mp4.exists():
                    act += f' <a class="btn" href="/{b}/presenter/recordings/{quote(n)}.mp4" download>Download</a>'
                if j.get("state") == "failed":
                    act += f' <span class="bad">failed: {html.escape(j["log"][0])}</span>'
            recs.append(f"<li><span class=mono>{n}</span> · {mins} · {act}</li>")
        rows.append(f"<section><h2>{b.split('_')[0].replace('lecture', 'Lecture ')}</h2><p>{pres}</p>"
                    f"<ul>{''.join(recs) or '<li class=dim>no recordings yet</li>'}</ul></section>")
    busy = any(j["state"] in ("queued", "running") for j in JOBS.values())
    return STUDIO.replace("ROWS", "".join(rows)).replace("BUSY", "true" if busy else "false")


STUDIO = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Recording studio</title><style>
:root{--bg:#111;--fg:#eee;--dim:#888;--acc:#8fb8de;--bad:#e5484d}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px}
h1{font-size:24px}h2{font-size:18px;margin:0 0 6px}
section{border:1px solid #2a2a2a;border-radius:10px;padding:14px 16px;margin:12px 0}
ul{margin:6px 0 0;padding-left:18px}li{margin:4px 0}
button,.btn{background:#1f2a36;color:var(--acc);border:1px solid #2f4256;border-radius:6px;padding:4px 10px;
font:inherit;font-size:14px;cursor:pointer;text-decoration:none}
.mono{font-family:ui-monospace,monospace;font-size:14px}.dim{color:var(--dim)}.busy{color:#d7b46a}.bad{color:var(--bad)}
.help{color:var(--dim);font-size:14px}
</style></head><body><main>
<h1>Recording studio</h1>
<p class="help">1. Present &amp; record: Space/→ next line, P pause, ← back, N notes, R start/stop recording.
2. Come back here and press <b>Build video</b> on the recording. 3. Download. The microphone needs this page opened
as <span class="mono">http://localhost:8080</span> (ssh -L tunnel).</p>
ROWS
</main><script>
async function post(u){ const r = await fetch(u, {method:'POST'}); if (!r.ok) alert(await r.text()); location.reload(); }
if (BUSY) setTimeout(() => location.reload(), 3000);
</script></body></html>"""


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

    def do_GET(self):
        if urlparse(self.path).path in ("/", "/index.html"):
            body = studio().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def api(self, u, q):
        b, n = q.get("build", ""), q.get("name", "")
        if not BUILD.fullmatch(b) or not (ROOT / b / f"{b}.mp4").exists():
            return self.send_error(400, "unknown lecture")
        if u.path == "/api/prepare":
            run_job(("prepare", b, ""), [sys.executable, "presenter.py", f"out/{b}"])
        elif u.path == "/api/compose" and re.fullmatch(r"[0-9T-]+", n) \
                and (ROOT / b / "presenter" / "recordings" / f"{n}.webm").exists():
            run_job(("compose", b, n), [sys.executable, "compose_recording.py", f"out/{b}", n])
        else:
            return self.send_error(400, "bad request")
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path.startswith("/api/"):
            return self.api(u, q)
        ok = (u.path == "/upload" and re.fullmatch(r"[a-z0-9_]+", q.get("build", ""))
              and re.fullmatch(r"[0-9T-]+", q.get("name", "")) and q.get("kind") in ("webm", "json")
              and (ROOT / q["build"] / "presenter").is_dir())
        n = int(self.headers.get("Content-Length", 0))
        if not ok or n > 2_000_000_000:
            self.send_error(400, "bad upload")
            return
        out = ROOT / q["build"] / "presenter" / "recordings"
        out.mkdir(exist_ok=True)
        with open(out / f"{q['name']}.{q['kind']}", "wb") as f:
            while n > 0:
                chunk = self.rfile.read(min(1 << 16, n))
                if not chunk:
                    break
                f.write(chunk)
                n -= len(chunk)
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8800
    print(f"serving {ROOT} on port {port} (pid {os.getpid()})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), partial(RangeHandler, directory=str(ROOT))).serve_forever()
