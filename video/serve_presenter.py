"""The recording studio: a small web server for the React app (studio/app, built into studio/static/app/) and its API.

http://localhost:8080/ (through an ssh -L tunnel; the microphone needs a secure origin) is the app: a project browser
(Module, Lecture, Language) and four screens, Record, Edit, Script & languages and Export. Recordings and their state
live in a small SQLite file, out/studio.sqlite; the files stay in <build>/presenter/recordings/. Heavy jobs run one at a
time in the background. Video is served with Range support, so the players can seek. A module's lectures are its
builds (lectureNN_uz_navoiy for Module 0, mK_lectureNN_uz_navoiy for Module K); its files are whatever is put in (or
linked into) out/shared/mK/, listed in the project browser.

The editor API (studio/api.py): the app sends each recording in one-second pieces as it is made, with its line starts
and retakes; each session is processed once (joined, cleaned, a seekable preview copy, its pauses), cut into one take
per line, and the app picks, trims, cuts, nudges and transcribes takes, previews the result and exports it (video,
subtitles, chapters). Heavy jobs share the one queue.

The old pages' addresses (/?m=N, /lecture, /edit, /watch, /narration, <build>/presenter/presenter.html) answer with a
302 to the same thing in the app (`old_route`).

    ssh -L 8080:localhost:8080 musulmon@10.0.0.5            # on the instructor's computer
    uv run python serve_presenter.py 8080                    # here; then open http://localhost:8080/
"""
import gzip
import io
import json
import os
import queue
import re
import sqlite3
import subprocess
import sys
import threading
import time
import traceback
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlencode, urlparse

import builds as B
import languages as LG
from compose_recording import CLEAN
from studio import api as A
from studio import buildlang as BL
from studio import media as M
from studio import review as R
from studio import store as S
from studio import versions as V
from studio import voice_server

HERE = Path(__file__).parent
ROOT = Path(os.environ.get("STUDIO_ROOT", HERE / "out"))     # tests point this at a scratch folder
DB = ROOT / "studio.sqlite"
MODULES = {0: "Statistics for Advanced AI", 1: "Classical Machine Learning", 2: "Vision / Deep Neural Networks",
           3: "Natural Language Processing", 4: "Graph Neural Networks", 5: "Reinforcement Learning & Alignment",
           6: "Efficient AI & Deployment", 7: "AI Agents, Tool Use & Retrieval"}      # course-map.md


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
    if "clean" not in [r[1] for r in c.execute("pragma table_info(recordings)")]:
        c.execute("alter table recordings add column clean text default ''")     # the voice profile it was built with
    return c


def recdir(build):
    return ROOT / build / "presenter" / "recordings"


def sync():
    """Add recordings found on disk (made before the database existed), drop rows whose files are gone."""
    import json
    with db() as c:
        for d in ROOT.glob("*lecture*/presenter/recordings"):
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


def compose(build, name, clean):
    with db() as c:
        c.execute("update recordings set state='queued', error='', clean=? where build=? and name=?", (clean, build, name))
    def work():
        with QUEUE:
            with db() as c:
                c.execute("update recordings set state='building' where build=? and name=?", (build, name))
            r = subprocess.run([sys.executable, "compose_recording.py", f"out/{build}", name, clean], cwd=HERE,
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
    """Forget a recording: its files, its old `recordings` row, and (studio/api.py forget) its editor session."""
    for ext in ("webm", "json", "mp4"):
        (recdir(build) / f"{name}.{ext}").unlink(missing_ok=True)
    with db() as c:
        c.execute("delete from recordings where build=? and name=?", (build, name))
    with dbc() as c:
        A.forget(ROOT, build, name, c)


# ─── the editor's background jobs: one at a time, sharing QUEUE with the builds above ─────────────────────────
JOBS = queue.Queue()


def dbc():
    return S.connect(DB)


def _worker():
    while True:
        JOBS.get()()


def enqueue(build, kind, key, fn):
    with dbc() as c:
        S.job(c, build, kind, key, "queued")

    def run():
        with QUEUE:
            with dbc() as c:
                S.job(c, build, kind, key, "running")
            try:
                detail = fn()
                with dbc() as c:
                    S.job(c, build, kind, key, "done", detail=str(detail or ""))
            except Exception as e:                            # shown in the editor; the queue carries on
                with dbc() as c:
                    S.job(c, build, kind, key, "failed", error=f"{type(e).__name__}: {e}"[-400:])
    JOBS.put(run)


PROFILE = os.environ.get("STUDIO_PROFILE", "cloned")      # how a new session's voice is cleaned (tests: off); cloned needs the voice server


def process(build, name, profile=None):
    profile = profile or PROFILE
    def fn():
        with dbc() as c:
            S.set_session(c, build, name, state="processing", error="")
        try:
            secs = M.process(ROOT / build, name, profile)
        except Exception as e:
            with dbc() as c:
                S.set_session(c, build, name, state="failed", error=str(e)[-300:])
            raise
        with dbc() as c:
            S.set_session(c, build, name, state="ready", seconds=secs, clean=profile)
        sync()                                                # the old whole-recording build sees it too
        return f"{secs / 60:.1f} min"
    enqueue(build, "process", name, fn)


def transcribe(build, take_ids):
    def fn():
        with dbc() as c:
            ts = [A.find_take(ROOT, build, t, c) for t in take_ids]
        ls = M.lines(ROOT / build)
        with dbc() as c:
            prof = {s["name"]: s["clean"] or PROFILE for s in S.sessions(c, build)}
        M.words(ROOT / build, [(t, ls[t["line"]][1]) for t in ts], prof[ts[0]["session"]] if ts else "deepfilter",
                B.lang(build))
        return f"{len(ts)} takes"
    enqueue(build, "words", ",".join(take_ids)[:200] if len(take_ids) < 4 else f"{len(take_ids)} takes", fn)


def export(build, profile):
    def fn():
        with dbc() as c:
            sessions = A.usable(ROOT, build, S.sessions(c, build))
            eds, ch, st = S.edits(c, build), S.choices(c, build), S.settings(c, build)
        paths = M.export(ROOT / build, sessions, eds, ch, profile, fallback=st["missing"])
        A.note_export_profile(ROOT, build, [p.name for p in paths], profile)
        return paths[0].name
    enqueue(build, "export", "export", fn)


def progress_to(build, kind, key):
    def progress(msg):
        with dbc() as c:
            S.job(c, build, kind, key, "running", detail=msg)
    return progress


def make_version(build, scene, n):
    """Build a draft version of a scene (voice the line, render the scene): the lecture is not touched."""
    key = f"{scene}/v{n}"
    enqueue(build, "version", key, lambda: V.build_version(ROOT, build, scene, n, dbc, progress_to(build, "version", key)))


def merge_version(build, scene, n):
    """Put a ready version into the lecture: narration, cache, scene, joined video, presenter page, recordings."""
    key = f"{scene}/v{n}"
    enqueue(build, "merge", key, lambda: V.merge(ROOT, build, scene, n, dbc, progress_to(build, "merge", key)))


def voice_server_action(action):
    def go():
        try:
            (voice_server.start if action == "start" else voice_server.stop)()
        except Exception as e:                                # shown as the server's state in the editor
            print("voice server:", e, flush=True)
    threading.Thread(target=go, daemon=True).start()


def build_language(stem, lang):
    """Queue a lecture video in a language (studio/buildlang.py). Refused with a message when it cannot be built."""
    with dbc() as c:
        p = BL.plan(c, ROOT, stem, lang)
    if not p["can"]:
        raise ValueError("cannot build: " + "; ".join(p["reasons"] or ["it is already built"]))
    build = p["build"]
    enqueue(build, "build", "video", lambda: BL.build_language(ROOT, stem, lang, dbc, progress_to(build, "build", "video")))
    return build


STATIC = HERE / "studio" / "static"                    # the editor's CSS and scripts, served at /studio-static/
SHARED = ROOT / "shared"


def shared(module):
    """A module's files: everything in out/shared/mK/ (links are followed, so a rebuilt PDF shows up as it is)."""
    d = SHARED / f"m{module}"
    return [f for f in sorted(d.iterdir()) if f.is_file() and not f.name.startswith(".")] if d.is_dir() else []


def old_route(path, q):
    """Where the address of an old page goes in the app (the Location of a 302), or None for any other address.
    The app reads its deep link from the query (`/?mode=edit&lecture=lecture01&lang=uz`) as well as the hash, so a
    fragment the browser keeps across the redirect (presenter.html#line=41 -> line 41) still reaches it."""
    def app(mode, build, **more):
        p = {"mode": mode, "lecture": B.stem(build), "lang": B.lang(build), **more}
        return "/?" + urlencode({k: v for k, v in p.items() if v})
    build = q.get("build", "")
    if path in ("/", "/index.html"):
        m = q.get("m", "")
        if not m:
            return None
        stems = R.stems(ROOT, int(m)) if m.isdigit() and int(m) in MODULES else []
        return "/?" + urlencode({"lecture": stems[0]}) if stems else "/"
    if path in ("/lecture", "/edit", "/watch") and B.is_build(build) and (ROOT / build).is_dir():
        if path == "/lecture":
            return app("export", build, watch="lecture")                 # the narrated video, playing in Export
        if path == "/edit":
            return app("edit", build)
        return app("export", build, watch=q["name"]) if NAME.fullmatch(q.get("name", "")) else app("export", build)
    if path == "/narration":
        stem, lang = q.get("lecture", ""), q.get("lang", "")
        if B.STEM.fullmatch(stem) and lang in LG.LANGS:
            return "/?" + urlencode({"mode": "script", "lecture": stem, "lang": lang})
        return None
    m = re.fullmatch(r"/([\w-]+)/presenter/presenter\.html", path)
    if m and B.is_build(m[1]) and (ROOT / m[1]).is_dir():
        return app("record", m[1])
    return None


RANGE_CAP = 4 << 20                                    # an open-ended Range gets this much, not the rest of the file
MEDIA = (".mp4", ".m4a")
ZIPPED = (".json", ".html", ".js", ".css")                     # static files worth gzipping (media never is)


class Counted:
    """The response stream, counting the bytes written (for the log)."""
    def __init__(self, f):
        self.f, self.n = f, 0

    def write(self, data):
        self.n += len(data)
        return self.f.write(data)

    def __getattr__(self, name):
        return getattr(self.f, name)


class HeadOnly:
    """The response stream of a HEAD request: the status line and headers go out (the first write), the body does not."""
    def __init__(self, f):
        self.f, self.sent = f, False

    def write(self, data):
        if not self.sent:
            self.sent = True
            return self.f.write(data)
        return len(data)

    def __getattr__(self, name):
        return getattr(self.f, name)


class Studio(SimpleHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.wfile = Counted(self.wfile)
        self._code, self._left = "-", None

    def parse_request(self):
        self._t0 = time.time()
        return super().parse_request()

    def handle_one_request(self):
        try:
            super().handle_one_request()
        finally:
            if getattr(self, "requestline", ""):
                ms = (time.time() - getattr(self, "_t0", time.time())) * 1000
                self.log_message('"%s" %s - %dms %dB', self.requestline, self._code, ms, self.wfile.n)
                self.wfile.n = 0

    def log_request(self, code="-", size="-"):
        self._code = code                              # logged once, at the end of the request, with time and bytes

    def gzips(self):
        return "gzip" in self.headers.get("Accept-Encoding", "")

    def send_head(self):
        self._left = self._etag = None
        m = re.match(r"bytes=(\d+)-(\d*)", self.headers.get("Range", ""))
        path = Path(self.translate_path(self.path))
        if not path.is_file():
            return super().send_head()
        if path.suffix in MEDIA:
            st = path.stat()
            self._etag = f'"{st.st_mtime_ns:x}-{st.st_size:x}"'          # strong: a remux changes the size, not the mtime
            if self.headers.get("If-None-Match") == self._etag:
                self.send_response(304)
                self.end_headers()
                return None
            if m and self.headers.get("If-Range", self._etag) != self._etag:
                m = None                                                  # the file changed: the whole of it, no cap
        if not m:
            if path.suffix in MEDIA:
                return super().send_head()
            if path.suffix in ZIPPED and self.gzips():
                body = gzip.compress(path.read_bytes(), 6)
                self.send_response(200)
                self.send_header("Content-Type", self.guess_type(str(path)))
                self.send_header("Content-Encoding", "gzip")
                self.send_header("Vary", "Accept-Encoding")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Last-Modified", self.date_time_string(path.stat().st_mtime))
                self.end_headers()
                return io.BytesIO(body)
            return super().send_head()
        size = path.stat().st_size
        start = int(m[1])
        if start >= size:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        end = min(int(m[2]), size - 1) if m[2] else min(size - 1, start + RANGE_CAP - 1)
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
        left = self._left
        if left is None:
            return super().copyfile(src, dst)
        while left > 0:
            chunk = src.read(min(1 << 16, left))
            if not chunk:
                break
            dst.write(chunk)
            left -= len(chunk)

    def send_text(self, body, ctype, code=200):
        """A page or an API answer: never cached, gzipped when the browser takes it (the tunnel is the slow part)."""
        if self.gzips() and len(body) > 1024:
            body = gzip.compress(body, 6)
            zipped = True
        else:
            zipped = False
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        if zipped:
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def static(self, rel):
        """/studio-static/<path>: a file under studio/static/, revalidated on every load (no-cache + Last-Modified),
        so an edit shows on refresh."""
        p = (STATIC / unquote(rel)).resolve()
        if not (p.is_relative_to(STATIC.resolve()) and p.is_file()):
            return self.send_error(404)
        mtime = self.date_time_string(p.stat().st_mtime)
        body = p.read_bytes()
        hashed = rel.startswith("app/assets/")
        zipped = self.gzips() and len(body) > 1024
        if self.headers.get("If-Modified-Since") == mtime:
            self.send_response(304)
            self.send_header("Last-Modified", mtime)
            self.send_header("Cache-Control", "public, max-age=31536000, immutable" if hashed else "no-cache")
            return self.end_headers()
        if zipped:
            body = gzip.compress(body, 6)
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(str(p)))
        if zipped:
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Last-Modified", mtime)
        # the app's assets are named by their content hash: a new build has new names, so the old ones never change
        self.send_header("Cache-Control", "public, max-age=31536000, immutable" if rel.startswith("app/assets/") else "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def html(self, text):
        self.send_text(text.encode(), "text/html; charset=utf-8")

    def json(self, obj, code=200):
        self.send_text(json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8", code)

    def body(self, limit=50_000_000):
        size = int(self.headers.get("Content-Length", 0))
        if size > limit:
            raise ValueError("too large")
        return self.rfile.read(size)

    def args(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        b, n = q.get("build", ""), q.get("name", "")
        ok_b = B.is_build(b) and (ROOT / b / f"{b}.mp4").exists()
        ok_n = NAME.fullmatch(n) is not None
        return u.path, q, b if ok_b else None, n if ok_n else None

    def narration_args(self, q):
        """(lecture stem, language) of a narration request, or None: the lecture must have narration or a build."""
        stem, lang = q.get("lecture", ""), q.get("lang", "")
        if not B.STEM.fullmatch(stem) or lang not in LG.LANGS or stem not in R.stems(ROOT, B.parse_stem(stem)[0]):
            return None
        return stem, lang

    def narration_get(self, path, q):
        a = self.narration_args(q)
        if a is None:
            return self.send_error(404, "no such lecture or language")
        try:
            with dbc() as c:
                return self.json(R.review(c, *a))
        except Exception as e:
            traceback.print_exc()
            return self.json({"error": f"{type(e).__name__}: {e}"[:500]}, 500)

    def narration_post(self, path, q):
        """/api/narration/{approve,save,fine}?lecture&lang&kind&key (save: {"text"} in the body) and /add?lecture&lang."""
        a = self.narration_args(q)
        if a is None:
            return self.send_error(404, "no such lecture or language")
        action = path.rsplit("/", 1)[1]
        try:
            if action == "add":
                return self.json({"file": R.add_language(a[0], a[1])})
            if action == "build":
                return self.json({"build": build_language(*a)})
            if action not in ("approve", "save", "fine"):
                return self.send_error(404)
            text = json.loads(self.body() or b"{}").get("text") if action == "save" else None
            with dbc() as c:
                return self.json(R.act(c, *a, action, q.get("kind", "line"), q.get("key", ""), text))
        except (ValueError, KeyError, FileNotFoundError) as e:
            return self.json({"error": str(e.args[0] if e.args else e)[:300]}, 400)

    def do_HEAD(self):                                      # the same answer as GET, without the body (curl -I)
        real, self.wfile = self.wfile, HeadOnly(self.wfile)
        try:
            self.do_GET()
        finally:
            self.wfile = real

    def do_GET(self):
        path, q, b, n = self.args()
        to = old_route(path, q)
        if to:                                              # an old page's address: the same thing in the app
            self.send_response(302)
            self.send_header("Location", to)
            self.send_header("Content-Length", "0")
            self.send_header("Cache-Control", "no-store")
            return self.end_headers()
        if path == "/api/narration":
            return self.narration_get(path, q)
        if path == "/api/lectures":                         # the project browser: modules, lectures, languages (studio/review.py lecture_list)
            try:
                with dbc() as c:
                    return self.json({"modules": R.lecture_list(c, ROOT, MODULES, shared)})
            except Exception as e:
                traceback.print_exc()
                return self.json({"error": f"{type(e).__name__}: {e}"[:500]}, 500)
        if path == "/api/lecture-langs":                   # the lecture page's language rows as JSON (the React app's Script and Export)
            stem = q.get("lecture", "")
            if not B.STEM.fullmatch(stem) or stem not in R.stems(ROOT, B.parse_stem(stem)[0]):
                return self.send_error(404, "no such lecture")
            try:
                with dbc() as c:
                    langs = R.lecture_langs(ROOT, stem)
                    out = {"lecture": stem, "primary": langs[0] if langs else None,
                           "langs": [R.summary(c, ROOT, stem, l) for l in langs],
                           "addable": [{"code": l, "name": LG.name(l), "native": LG.native(l)} for l in LG.CODES if l not in langs]}
                return self.json(out)
            except Exception as e:
                traceback.print_exc()
                return self.json({"error": f"{type(e).__name__}: {e}"[:500]}, 500)
        if path == "/api/editor-langs":
            if not b or not (ROOT / b / "presenter" / "lines.json").exists():
                return self.send_error(404, "no such lecture")
            try:
                with dbc() as c:
                    return self.json(R.editor_langs(c, ROOT, b))
            except Exception as e:
                traceback.print_exc()
                return self.json({"error": f"{type(e).__name__}: {e}"[:500]}, 500)
        if path in ("/", "/index.html"):                   # the React app (studio/app, built into static/app/)
            return self.static("app/index.html")
        if path == "/api/line":
            if not b:
                return self.send_error(404, "no such lecture")
            if not (ROOT / b / "presenter" / "lines.json").exists():
                return self.json({"error": "prepare the presenter page first"}, 404)
            try:
                with dbc() as c:
                    cut_off = A.abandoned(ROOT, b, c)
                for name in cut_off:
                    process(b, name)
                with dbc() as c:
                    return self.json(A.line_view(ROOT, b, int(q["line"]) if q.get("line", "").isdigit() else -1, c))
            except KeyError as e:
                return self.json({"error": str(e.args[0])[:200]}, 404)
            except Exception as e:
                traceback.print_exc()
                return self.json({"error": f"{type(e).__name__}: {e}"[:500]}, 500)
        if path in ("/api/project", "/api/counts"):
            if not b:
                return self.send_error(404, "no such lecture")
            if not (ROOT / b / "presenter" / "lines.json").exists():
                return self.json({"error": "prepare the presenter page first", "preparing": PREPARING.get(b, "")}, 404)
            try:
                with dbc() as c:
                    cut_off = A.abandoned(ROOT, b, c)         # cut off without a finish: process what came
                for name in cut_off:
                    process(b, name)
                with dbc() as c:
                    out = A.project(ROOT, b, c) if path == "/api/project" else A.counts(ROOT, b, c)
            except Exception as e:                            # say why, instead of dropping the connection
                traceback.print_exc()
                return self.json({"error": f"{type(e).__name__}: {e}"[:500]}, 500)
            return self.json(out)
        if path == "/api/levels":
            if not b:
                return self.send_error(404, "no such lecture")
            try:
                with dbc() as c:
                    return self.json(A.levels(ROOT, b, q.get("src", ""), c))
            except KeyError as e:
                return self.json({"error": str(e.args[0])[:200]}, 404)
            except Exception as e:
                traceback.print_exc()
                return self.json({"error": f"{type(e).__name__}: {e}"[:500]}, 500)
        if path.startswith("/studio-static/"):
            return self.static(path[len("/studio-static/"):])
        if path.endswith(".sqlite"):
            return self.send_error(404)
        super().do_GET()

    def ok(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        path, q, b, n = self.args()
        if path.startswith("/api/narration/"):
            return self.narration_post(path, q)
        if b is None:
            return self.send_error(400, "unknown lecture")
        try:
            if self.editor_post(path, q, b, n):
                return
        except (ValueError, KeyError) as e:
            return self.send_error(400, str(e)[:200])
        if path == "/api/prepare":
            prepare(b)
            return self.ok()
        if n is None:
            return self.send_error(400, "bad recording name")
        if path == "/api/compose" and (recdir(b) / f"{n}.webm").exists():
            clean = q.get("clean", "deepfilter")
            if clean not in CLEAN:
                return self.send_error(400, "unknown cleaning profile")
            compose(b, n, clean)
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

    def editor_post(self, path, q, b, n):
        """The editor's API (studio/api.py). Returns True when the request was one of them. Jobs are queued only
        after this request's changes are committed (queueing writes through its own connection)."""
        later = []
        with dbc() as c:
            if path == "/api/chunk" and n is not None and q.get("seq", "").isdigit():
                A.chunk(ROOT, b, n, int(q["seq"]), self.body(), c)
            elif path == "/api/events" and n is not None:
                A.events(ROOT, b, n, self.body(), c)
            elif path == "/api/finish" and n is not None:
                if A.finish(ROOT, b, n, c):
                    later.append(lambda: process(b, n))
            elif path == "/api/edit" and q.get("take"):
                out = A.set_edit(ROOT, b, q["take"], json.loads(self.body() or b"{}"), c)
                later.append(lambda: self.json(out))
            elif path == "/api/choose" and q.get("line", "").isdigit():
                A.choose(ROOT, b, q["line"], q.get("take"), c)
            elif path == "/api/shrink":
                ids = [q["take"]] if q.get("take") else A.chosen_ids(ROOT, b, c)
                out = A.shrink(ROOT, b, ids, c)
                later.append(lambda: self.json({"saved": out["saved"]}))
            elif path == "/api/fit" and q.get("take"):
                A.fit(ROOT, b, q["take"], q.get("end", "both"), c)
            elif path == "/api/unshrink" and q.get("take"):
                A.unshrink(ROOT, b, q["take"], c)
            elif path == "/api/cut-extras" and q.get("take"):
                A.cut_extras(ROOT, b, q["take"], c)
            elif path == "/api/words":
                ids = [q["take"]] if q.get("take") else A.chosen_ids(ROOT, b, c)
                later.append(lambda: transcribe(b, ids))
            elif path == "/api/import":
                names = A.import_old(ROOT, b, c)
                later += [lambda name=name: process(b, name) for name in names]
            elif path == "/api/process" and n is not None:
                later.append(lambda: process(b, n, q.get("clean") if q.get("clean") in CLEAN else None))
            elif path == "/api/version" and q.get("line", "").isdigit():
                body = json.loads(self.body() or b"{}")
                scene, num = V.create(ROOT, b, int(q["line"]), body.get("text"), q.get("base") or body.get("base"), c)
                later.append(lambda: make_version(b, scene, num))
                later.append(lambda: self.json({"scene": scene, "n": num}))
            elif path in ("/api/version/merge", "/api/version/discard") and q.get("scene") and q.get("n", "").isdigit():
                num = int(q["n"])
                if path.endswith("merge"):
                    V.check_merge(c, b, q["scene"], num)
                    later.append(lambda: merge_version(b, q["scene"], num))
                else:
                    V.discard(ROOT, b, q["scene"], num, c)
            elif path == "/api/settings" and q.get("key"):
                A.set_setting(ROOT, b, q["key"], q.get("value", ""), c)
            elif path == "/api/voice-server" and q.get("action") in ("start", "stop"):
                later.append(lambda: voice_server_action(q["action"]))
            elif path == "/api/export":
                later.append(lambda: export(b, q.get("clean") if q.get("clean") in CLEAN else "cloned"))
            else:
                return False
        for f in later:
            f()
        if path not in ("/api/edit", "/api/shrink", "/api/version"):
            self.ok()
        return True

    def send_response(self, code, message=None):
        self._status = code
        super().send_response(code, message)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        if getattr(self, "_status", 0) in (200, 206, 304) and getattr(self, "_etag", None):
            self.send_header("ETag", self._etag)
            versioned = "v" in parse_qs(urlparse(self.path).query)          # ?v=<mtime> names one version of the file
            self.send_header("Cache-Control", "private, max-age=86400" if versioned else "no-cache")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    sync()
    with dbc() as c:
        S.reset_running(c)
    threading.Thread(target=_worker, daemon=True).start()
    print(f"studio on port {port} (pid {os.getpid()}), recordings in {DB}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), partial(Studio, directory=str(ROOT))).serve_forever()
