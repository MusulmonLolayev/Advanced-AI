"""The recording studio: a small web app, served to another computer on the LAN (the server has no screen of its own).

http://localhost:8080/ (through an ssh -L tunnel; the microphone needs a secure origin) lists every built lecture:
prepare its presenter page (presenter.py), open it to present and record (key R), build each recording into a 1080p
video with the instructor's voice (compose_recording.py), watch it in the page, delete it. Recordings and their build
state live in a small SQLite file, out/studio.sqlite; the files stay in <build>/presenter/recordings/. Heavy jobs run
one at a time in the background. Video is served with Range support, so the players can seek.

    ssh -L 8080:localhost:8080 musulmon@10.0.0.5            # on the instructor's computer
    uv run python serve_presenter.py 8080                    # here; then open http://localhost:8080/
"""
import html
import os
import re
import sqlite3
import subprocess
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

HERE = Path(__file__).parent
ROOT = HERE / "out"
DB = ROOT / "studio.sqlite"
BUILD = re.compile(r"lecture\d\d_uz_navoiy")          # the statistics lectures
NAME = re.compile(r"[0-9T-]+")                         # a recording's name: its start time
QUEUE = threading.Semaphore(1)                         # one heavy job at a time
PREPARING = {}                                         # build -> "running" | "failed: …"


def db():
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("""create table if not exists recordings (
        build text, name text, seconds real, created real,
        state text default 'recorded',              -- recorded | queued | building | built | failed
        error text default '', primary key (build, name))""")
    return c


def recdir(build):
    return ROOT / build / "presenter" / "recordings"


def sync():
    """Add recordings found on disk (made before the database existed), drop rows whose files are gone."""
    import json
    with db() as c:
        for d in ROOT.glob("lecture*_uz_navoiy/presenter/recordings"):
            for w in d.glob("*.webm"):
                j = d / f"{w.stem}.json"
                if j.exists():
                    ev = json.loads(j.read_text())
                    c.execute("insert or ignore into recordings (build, name, seconds, created, state) values (?,?,?,?,?)",
                              (d.parent.parent.name, w.stem, ev[-1][0] if ev else 0, w.stat().st_mtime,
                               "built" if (d / f"{w.stem}.mp4").exists() else "recorded"))
        for r in c.execute("select build, name from recordings").fetchall():
            if not (recdir(r["build"]) / f"{r['name']}.webm").exists():
                c.execute("delete from recordings where build=? and name=?", (r["build"], r["name"]))
        c.execute("update recordings set state='recorded' where state in ('queued','building')")   # killed jobs


def compose(build, name):
    with db() as c:
        c.execute("update recordings set state='queued', error='' where build=? and name=?", (build, name))
    def work():
        with QUEUE:
            with db() as c:
                c.execute("update recordings set state='building' where build=? and name=?", (build, name))
            r = subprocess.run([sys.executable, "compose_recording.py", f"out/{build}", name], cwd=HERE,
                               capture_output=True, text=True)
            err = "" if r.returncode == 0 else ((r.stdout + r.stderr).strip().splitlines() or ["?"])[-1]
            with db() as c:
                c.execute("update recordings set state=?, error=? where build=? and name=?",
                          ("built" if not err else "failed", err, build, name))
    threading.Thread(target=work, daemon=True).start()


def prepare(build):
    PREPARING[build] = "running"
    def work():
        with QUEUE:
            r = subprocess.run([sys.executable, "presenter.py", f"out/{build}"], cwd=HERE, capture_output=True, text=True)
        if r.returncode == 0:
            PREPARING.pop(build, None)
        else:
            PREPARING[build] = "failed: " + ((r.stdout + r.stderr).strip().splitlines() or ["?"])[-1]
    threading.Thread(target=work, daemon=True).start()


def delete(build, name):
    for ext in ("webm", "json", "mp4"):
        (recdir(build) / f"{name}.{ext}").unlink(missing_ok=True)
    with db() as c:
        c.execute("delete from recordings where build=? and name=?", (build, name))


def builds():
    return [d.name for d in sorted(ROOT.iterdir()) if d.is_dir() and BUILD.fullmatch(d.name)
            and (d / f"{d.name}.mp4").exists() and (d / "joined.txt").exists()]


def studio():
    with db() as c:
        rows = c.execute("select * from recordings order by created desc").fetchall()
    out, busy = [], bool(PREPARING) and any(v == "running" for v in PREPARING.values())
    for b in builds():
        ready = (ROOT / b / "presenter" / "presenter.html").exists()
        st = PREPARING.get(b, "")
        if st == "running":
            pres = '<span class="busy">preparing the presenter page…</span>'
        elif ready:
            pres = (f'<a class="btn" href="/{b}/presenter/presenter.html">Present &amp; record</a> '
                    f'<button class="quiet" onclick="post(\'/api/prepare?build={b}\')">Refresh page</button>')
        else:
            pres = f'<button onclick="post(\'/api/prepare?build={b}\')">Prepare presenter page</button>'
        if st.startswith("failed"):
            pres += f' <span class="bad">{html.escape(st)}</span>'
        recs = []
        for r in (r for r in rows if r["build"] == b):
            n, s = r["name"], r["state"]
            busy |= s in ("queued", "building")
            when = time.strftime("%d %b %H:%M", time.localtime(r["created"]))
            q = f"build={b}&name={n}"
            act = {"queued": '<span class="busy">queued…</span>', "building": '<span class="busy">building…</span>'}.get(s)
            if act is None:
                act = (f'<a class="btn" href="/watch?{q}">Watch</a> ' if s == "built" else "") + \
                      f'<button onclick="post(\'/api/compose?{q}\')">{"Rebuild" if s == "built" else "Build video"}</button> '
                if s == "failed":
                    act += f'<span class="bad">failed: {html.escape(r["error"])}</span> '
            act += f'<button class="quiet" onclick="del(\'{q}\')">Delete</button>'
            recs.append(f"<li><span class=mono>{when}</span> · {r['seconds'] / 60:.1f} min · {act}</li>")
        out.append(f"<section><h2>{b.split('_')[0].replace('lecture', 'Lecture ')}</h2><p>{pres}</p>"
                   f"<ul>{''.join(recs) or '<li class=dim>no recordings yet</li>'}</ul></section>")
    return PAGE.replace("BODY", HELP + "".join(out)).replace("BUSY", "true" if busy else "false")


def watch(build, name):
    src = f"/{build}/presenter/recordings/{quote(name)}.mp4"
    return PAGE.replace("BODY", f'<p><a href="/">← studio</a> · {build.split("_")[0].replace("lecture", "Lecture ")} · '
                                f'<span class=mono>{name}</span></p><video src="{src}" controls autoplay '
                                f'style="width:100%;background:#000;border-radius:8px"></video>').replace("BUSY", "false")


HELP = """<h1>Recording studio</h1><p class="help">Present &amp; record: Space/→ next line, P pause, ← back, N notes,
R starts and stops recording. Then press <b>Build video</b> here, and <b>Watch</b> when it is built.</p>"""

PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Recording studio</title><style>
:root{--bg:#111;--fg:#eee;--dim:#888;--acc:#8fb8de;--bad:#e5484d}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif}
main{max-width:960px;margin:0 auto;padding:24px 16px}a{color:var(--acc)}
h1{font-size:24px}h2{font-size:18px;margin:0 0 6px}
section{border:1px solid #2a2a2a;border-radius:10px;padding:14px 16px;margin:12px 0}
ul{margin:6px 0 0;padding-left:18px}li{margin:6px 0}
button,.btn{background:#1f2a36;color:var(--acc);border:1px solid #2f4256;border-radius:6px;padding:4px 10px;
font:inherit;font-size:14px;cursor:pointer;text-decoration:none}
button.quiet{background:none;color:var(--dim);border-color:#333}
.mono{font-family:ui-monospace,monospace;font-size:14px}.dim{color:var(--dim)}.busy{color:#d7b46a}.bad{color:var(--bad)}
.help{color:var(--dim);font-size:14px}
</style></head><body><main>BODY</main><script>
async function post(u){ const r = await fetch(u, {method:'POST'}); if (!r.ok) alert(await r.text()); location.reload(); }
function del(q){ if (confirm('Delete this recording and its video?')) post('/api/delete?' + q); }
if (BUSY) setTimeout(() => location.reload(), 3000);
</script></body></html>"""


class Studio(SimpleHTTPRequestHandler):
    def send_head(self):
        m = re.match(r"bytes=(\d+)-(\d*)", self.headers.get("Range", ""))
        path = Path(self.translate_path(self.path))
        if not m or not path.is_file():
            return super().send_head()
        size = path.stat().st_size
        start, end = int(m[1]), min(int(m[2] or size - 1), size - 1)
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(str(path)))
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

    def html(self, text):
        body = text.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def args(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        b, n = q.get("build", ""), q.get("name", "")
        ok_b = BUILD.fullmatch(b) and (ROOT / b / f"{b}.mp4").exists()
        ok_n = NAME.fullmatch(n) is not None
        return u.path, q, b if ok_b else None, n if ok_n else None

    def do_GET(self):
        path, _, b, n = self.args()
        if path in ("/", "/index.html"):
            return self.html(studio())
        if path == "/watch":
            if not (b and n and (recdir(b) / f"{n}.mp4").exists()):
                return self.send_error(404, "no such video")
            return self.html(watch(b, n))
        if path.endswith(".sqlite"):
            return self.send_error(404)
        super().do_GET()

    def ok(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        path, q, b, n = self.args()
        if b is None:
            return self.send_error(400, "unknown lecture")
        if path == "/api/prepare":
            prepare(b)
            return self.ok()
        if n is None:
            return self.send_error(400, "bad recording name")
        if path == "/api/compose" and (recdir(b) / f"{n}.webm").exists():
            compose(b, n)
            return self.ok()
        if path == "/api/delete":
            delete(b, n)
            return self.ok()
        if path == "/upload" and q.get("kind") in ("webm", "json") and (ROOT / b / "presenter").is_dir():
            size = int(self.headers.get("Content-Length", 0))
            if size > 2_000_000_000:
                return self.send_error(400, "too large")
            recdir(b).mkdir(exist_ok=True)
            with open(recdir(b) / f"{n}.{q['kind']}", "wb") as f:
                while size > 0:
                    chunk = self.rfile.read(min(1 << 16, size))
                    if not chunk:
                        break
                    f.write(chunk)
                    size -= len(chunk)
            if q["kind"] == "json":                      # the page sends the audio first, then the events
                sync()
            return self.ok()
        self.send_error(400, "bad request")

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    sync()
    print(f"studio on port {port} (pid {os.getpid()}), recordings in {DB}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), partial(Studio, directory=str(ROOT))).serve_forever()
