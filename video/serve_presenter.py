"""The recording studio: a small web app, served to another computer on the LAN (the server has no screen of its own).

http://localhost:8080/ (through an ssh -L tunnel; the microphone needs a secure origin) lists every built lecture:
prepare its presenter page (presenter.py), open it to present and record (key R), build each recording into a 1080p
video with the instructor's voice, cleaned with the chosen profile of ~/teaching/clean_video.sh (compose_recording.py), watch it in the page, delete it. Recordings and their build
state live in a small SQLite file, out/studio.sqlite; the files stay in <build>/presenter/recordings/. Heavy jobs run
one at a time in the background. Video is served with Range support, so the players can seek. The page is split by
module (a panel on the left, /?m=7): a module's lectures are its builds (lectureNN_uz_navoiy for Module 0,
mK_lectureNN_uz_navoiy for Module K), and its files are whatever is put in (or linked into) out/shared/mK/ -- a
lecture PDF, say -- to open or download.

The editor (/edit?build=…, studio/): the presenter sends each recording in one-second pieces as it is made, with
its line starts and retakes; each session is processed once (joined, cleaned, a seekable preview copy, its pauses),
cut into one take per line, and the editor picks, trims, cuts, nudges and transcribes takes, previews the result in
the browser and exports it (video, subtitles, chapters). Its API is studio/api.py; heavy jobs share the one queue.

    ssh -L 8080:localhost:8080 musulmon@10.0.0.5            # on the instructor's computer
    uv run python serve_presenter.py 8080                    # here; then open http://localhost:8080/
"""
import gzip
import html
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
from urllib.parse import parse_qs, quote, unquote, urlparse

import builds as B
import languages as LG
import presenter
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


def module_of(build):
    return B.module(build)


def lecture_title(build):
    _, lecture, lang, _ = B.parse(build)
    return f"Lecture {lecture:02d} · {LG.name(lang)}"


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


PROFILE = os.environ.get("STUDIO_PROFILE", "deepfilter")      # how a new session's voice is cleaned (tests: off)


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


def lang_switch(build):
    """The editor header's links to the lecture's other languages: their editor when it is built, else their review page."""
    stem = B.stem(build)
    with dbc() as c:
        others = R.editor_langs(c, ROOT, build)["others"]
    return "".join(f'<a class="btn" href="{html.escape("/edit?build=" + o["build"] if o["build"] else o["review"])}" '
                   f'title="{html.escape(o["name"])}: {"the editor" if o["build"] else "narration review (no build yet)"}">'
                   f'{html.escape(o["native"])}{"" if o["build"] else " (review)"}</a> ' for o in others)


def narration_page(stem, lang):
    page = (HERE / "studio" / "narration.html").read_text()
    m = B.parse_stem(stem)
    return (page.replace("__LECTURE__", stem).replace("__LANG__", lang).replace("__MODULE__", str(m[0]))
            .replace("__TITLE__", html.escape(f"Lecture {m[1]:02d} · {LG.name(lang)}")))


def editor(build):
    m = module_of(build)
    page = (HERE / "studio" / "editor.html").read_text()
    return (page.replace("__BUILD__", build).replace("__TITLE__", html.escape(lecture_title(build)))
            .replace("__MODULE__", str(m)).replace("__LANGS__", lang_switch(build)).replace("__CLEAN__", "".join(
                f'<option value="{k}">{k}</option>' for k in sorted(CLEAN, key=lambda k: k != "deepfilter"))))


def presenter_page(build):
    """The build's presenter page, rendered now from presenter.PAGE with its lines.json and silent video (None until
    the page has been prepared once)."""
    d = ROOT / build / "presenter"
    silent = d / f"{build}_silent.mp4"
    if not (d / "lines.json").exists() or not silent.exists():
        return None
    return presenter.render(json.loads((d / "lines.json").read_text()), build, silent)


STATIC = HERE / "studio" / "static"                    # the editor's CSS and scripts, served at /studio-static/
SHARED = ROOT / "shared"


def shared(module):
    """A module's files: everything in out/shared/mK/ (links are followed, so a rebuilt PDF shows up as it is)."""
    d = SHARED / f"m{module}"
    return [f for f in sorted(d.iterdir()) if f.is_file() and not f.name.startswith(".")] if d.is_dir() else []


def files(module):
    rows = []
    for f in shared(module):
        st, q = f.stat(), f"m{module}/{quote(f.name)}"
        rows.append(f'<li>{html.escape(f.name)} <span class=dim>· {st.st_size / 1e6:.1f} MB · '
                    f'{time.strftime("%d %b %H:%M", time.localtime(st.st_mtime))}</span> · '
                    f'<a class="btn" href="/shared/{q}" target="_blank">Open</a> '
                    f'<a class="btn" href="/shared/{q}" download>Download</a></li>')
    return f"<section><h2>Files</h2><ul>{''.join(rows) or '<li class=dim>nothing shared yet</li>'}</ul></section>"


def sidebar(module):
    items = []
    for k, title in MODULES.items():
        n_lec = len(R.stems(ROOT, k))
        n_files = len(shared(k))
        count = " · ".join(x for x in (f"{n_lec} lecture{'s' * (n_lec != 1)}" if n_lec else "",
                                        f"{n_files} file{'s' * (n_files != 1)}" if n_files else "") if x)
        items.append(f'<a href="/?m={k}" class="mod{" on" if k == module else ""}{"" if count else " empty"}">'
                     f'<b>Module {k}</b><span>{html.escape(title)}</span><small>{count or "nothing yet"}</small></a>')
    return f'<nav><div class="brand">Recording studio</div>{"".join(items)}</nav>' 


def builds():
    return [d.name for d in sorted(ROOT.iterdir()) if d.is_dir() and B.is_build(d.name)
            and (d / f"{d.name}.mp4").exists() and (d / "joined.txt").exists()]


def when(t):
    return time.strftime("%d %b %H:%M", time.localtime(t))


def counts_line(c, kind):
    """"approved 87 / 91 · 3 need update · 1 empty" for a narration or label count (the parts that are zero are left out)."""
    parts = [f"approved {c['approved']} / {c['total']}"]
    for k, word in (("needs_update", "need update"), ("draft", "draft"), ("empty", "empty")):
        if c[k]:
            parts.append(f'<span class="{"warn" if k == "needs_update" else "dim"}">{c[k]} {word}</span>')
    return f'{kind}: ' + " · ".join(parts)


def build_buttons(b, rows):
    """A built lecture's buttons and its recordings (the studio's original per-build block). Returns (html, busy)."""
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
    pres = (f'<a class="btn" href="/lecture?build={b}">Watch video</a> '
            + (f'<a class="btn" href="/edit?build={b}">Open editor</a> ' if ready else "") + pres)
    recs, busy = [], st == "running"
    for r in (r for r in rows if r["build"] == b):
        n, s = r["name"], r["state"]
        busy |= s in ("queued", "building")
        q = f"build={b}&name={n}"
        act = {"queued": '<span class="busy">queued…</span>', "building": '<span class="busy">building…</span>'}.get(s)
        if act is None:
            act = (f'<a class="btn" href="/watch?{q}">Watch</a> <span class=dim>voice: {html.escape(r["clean"] or "?")}</span> '
                   if s == "built" else "") + \
                  f'<button onclick="build(\'{q}\')">{"Rebuild" if s == "built" else "Build video"}</button> '
            if s == "failed":
                act += f'<span class="bad">failed: {html.escape(r["error"])}</span> '
        act += f'<button class="quiet" onclick="del(\'{q}\')">Delete</button>'
        recs.append(f"<li><span class=mono>{when(r['created'])}</span> · {r['seconds'] / 60:.1f} min · {act}</li>")
    return (f"<p>{pres}</p><ul>{''.join(recs) or '<li class=dim>no recordings yet</li>'}</ul>"), busy


def lang_row(stem, s, rows):
    """One language of a lecture on the lecture page: narration and label counts, the build, its buttons. (html, busy)"""
    lang, busy = s["lang"], False
    review = f'<a class="btn" href="/narration?lecture={stem}&amp;lang={lang}">Review narration</a>'
    native = f' <span class="dim">· {html.escape(s["native"])}</span>' if s["native"] != s["name"] else ""
    out = [f'<div class="lang"><h3>{html.escape(s["name"])}{native}</h3>']
    if s["has_narration"]:
        out.append(f'<p class="stat">{counts_line(s["lines"], "narration")}<br>{counts_line(s["labels"], "labels")}</p>')
    else:
        out.append('<p class="stat dim">no narration yet</p>')
    if s["has_narration"] and s["lines"]["total"] and s["lines"]["empty"] == s["lines"]["total"]:
        out.append(f'<p class="note">skeleton created: ask Claude to draft {html.escape(s["name"])} for this lecture '
                   f'(<span class="mono">narration/{stem}_{lang}.md</span>), then approve it line by line here.</p>')
    out.append(f'<p>{review}</p>')
    built = [b for b in s["builds"] if b["built"] and (ROOT / b["build"] / "joined.txt").exists()]
    for b in s["builds"]:
        if b not in built:
            out.append(f'<p class="stat dim">build {b["build"]}: not built yet</p>')
    for b in built:
        if b["stale"]:
            state = (f'<span class="warn">narration changed since the build</span> '
                     f'<span class="dim">({len(b["stale"])} approved line{"s" * (len(b["stale"]) != 1)} differ from the video)</span>')
        elif b["stale"] is None:
            state = '<span class="dim">(no presenter page to compare the narration with)</span>'
        elif not s["lines"]["approved"] + s["lines"]["needs_update"]:
            state = '<span class="dim">no approved lines to compare with the video yet</span>'
        else:
            state = '<span class="good">narration matches the video</span>'
        btns, bb = build_buttons(b["build"], rows)
        busy |= bb
        out.append(f'<p class="stat">build {b["build"]}: built {when(b["when"])} · {state} · '
                   f'recorded sessions: {b["sessions"]}</p>{btns}')
    p, job = s["plan"], s["job"]
    if not built:
        out.append('<p class="stat">' + ('can be built: <span class="good">yes</span>' if s["ready"] else
                   f'can be built: <span class="bad">no</span> <span class="dim">— {html.escape("; ".join(s["missing"]))}</span>') + '</p>')
        if p["can"]:
            word = "Build draft video" if p["draft"] else "Build video"
            note = (f'<span class="dim">{p["unapproved"]["lines"]} lines and {p["unapproved"]["labels"]} labels are not approved: '
                    f'the frames carry a draft tag</span>') if p["draft"] else ""
            out.append(f'<p><button onclick="buildLang(\'{stem}\', \'{lang}\')">{word}</button> {note}</p>')
    if job and job["state"] in ("queued", "running"):
        busy = True
    if job:
        cls = {"failed": "bad", "done": "good"}.get(job["state"], "dim")
        out.append(f'<p class="stat">build job: <span class="{cls}">{job["state"]}</span> '
                   f'<span class="dim">{html.escape((job["error"] or job["detail"] or "")[:300])}</span></p>')
    out.append("</div>")
    return "".join(out), busy


def add_language_form(stem, have):
    opts = "".join(f'<option value="{c}">{html.escape(LG.name(c))} · {html.escape(LG.native(c))}</option>'
                   for c in LG.CODES if c not in have)
    return (f'<p class="addlang"><select id="add-{stem}">{opts}</select> '
            f'<button onclick="addLang(\'{stem}\')">+ add language</button> '
            f'<span class="dim">creates an empty narration to be drafted by Claude</span></p>')


def studio(module):
    with db() as c:
        rows = c.execute("select * from recordings order by created desc").fetchall()
    out, busy = [], bool(PREPARING) and any(v == "running" for v in PREPARING.values())
    with dbc() as c:
        for stem in R.stems(ROOT, module):
            langs = R.lecture_langs(ROOT, stem)
            body = []
            for lang in langs:
                html_, bb = lang_row(stem, R.summary(c, ROOT, stem, lang), rows)
                body.append(html_)
                busy |= bb
            out.append(f'<section><h2>Lecture {B.parse_stem(stem)[1]:02d}</h2>{"".join(body)}'
                       f'{add_language_form(stem, set(langs))}</section>')
    head = f'<h1>Module {module} · {html.escape(MODULES[module])}</h1>'
    lectures = "".join(out) or '<section><h2>Lectures</h2><p class=dim>no lecture narration or video yet</p></section>'
    return (PAGE.replace("NAV", sidebar(module))
            .replace("BODY", head + files(module) + lectures + HELP)
            .replace("BUSY", "true" if busy else "false").replace("MODULE", str(module)))


def stamp(path):
    """?v= for a video the pages play: its mtime, so a rebuilt file is never served from the browser's cache."""
    try:
        return int(Path(path).stat().st_mtime)
    except OSError:
        return 0


def lecture(build):
    """The built lecture video itself (the narrated Manim video), to watch before presenting it."""
    m = module_of(build)
    src = f"/{build}/{build}.mp4?v={stamp(ROOT / build / (build + '.mp4'))}"
    return (PAGE.replace("NAV", sidebar(m))
            .replace("BODY", f'<p><a href="/?m={m}">← Module {m}</a> · {lecture_title(build)} · the narrated video</p>'
                             f'<video src="{src}" controls autoplay style="width:100%;background:#000;border-radius:8px">'
                             f'</video>')
            .replace("BUSY", "false").replace("MODULE", str(m)))


def watch(build, name):
    src = f"/{build}/presenter/recordings/{quote(name)}.mp4?v={stamp(recdir(build) / (name + '.mp4'))}"
    m = module_of(build)
    return (PAGE.replace("NAV", sidebar(m))
            .replace("BODY", f'<p><a href="/?m={m}">← Module {m}</a> · {lecture_title(build)} · '
                             f'<span class=mono>{name}</span></p><video src="{src}" controls autoplay '
                             f'style="width:100%;background:#000;border-radius:8px"></video>')
            .replace("BUSY", "false").replace("MODULE", str(m)))


HELP = ("""<h2 class="sub">How it works</h2><p class="help">Present &amp; record: Space pause / play, → next line, ← back,
N notes (below / right / off), M microphone, R starts and stops recording, X marks a mistake (the line starts over).
Then <b>Open editor</b>: pick each line's take, cut, preview, export. (<b>Build video</b> below still builds a whole
recording as it was made.)</p><p>Voice cleaning when building: <select id="clean">"""
        + "".join(f'<option value="{k}">{k}</option>' for k in sorted(CLEAN, key=lambda k: k != "deepfilter"))
        + """</select> <span class="help">deepfilter (default): neural denoiser,
the cleanest (DNSMOS 3.2 vs 2.2 for voice on your first recording; ~5 min per 30 min) · voice: tuned for speech · mild: lighter · strong: a noisy
room · off: low cut only. Rebuild to try another.</span></p>""")

PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Recording studio</title><style>
:root{--bg:#111;--fg:#eee;--dim:#888;--acc:#8fb8de;--bad:#e5484d}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif}
.wrap{display:flex;min-height:100vh}
nav{width:250px;flex:none;border-right:1px solid #2a2a2a;padding:16px 10px;box-sizing:border-box;
  position:sticky;top:0;height:100vh;overflow-y:auto;background:#151515}
nav .brand{font-weight:600;padding:4px 10px 12px;color:var(--fg)}
nav a.mod{display:block;padding:8px 10px;border-radius:8px;color:var(--fg);text-decoration:none;margin:2px 0}
nav a.mod span{display:block;font-size:14px;line-height:1.3}
nav a.mod small{display:block;font-size:12px;color:var(--dim)}
nav a.mod:hover{background:#1d1d1d}nav a.mod.on{background:#1f2a36}nav a.mod.on b{color:var(--acc)}
nav a.mod.empty{opacity:.55}
main{flex:1;min-width:0;max-width:960px;margin:0 auto;padding:24px 16px}a{color:var(--acc)}
h2.sub{margin-top:24px}
@media (max-width:720px){.wrap{flex-direction:column}
  nav{width:auto;height:auto;position:static;display:flex;overflow-x:auto;gap:6px;border-right:0;
    border-bottom:1px solid #2a2a2a;padding:8px}
  nav .brand{display:none}nav a.mod{flex:none;width:170px}}
h1{font-size:24px}h2{font-size:18px;margin:0 0 6px}
section{border:1px solid #2a2a2a;border-radius:10px;padding:14px 16px;margin:12px 0}
ul{margin:6px 0 0;padding-left:18px}li{margin:6px 0}
button,.btn{background:#1f2a36;color:var(--acc);border:1px solid #2f4256;border-radius:6px;padding:4px 10px;
font:inherit;font-size:14px;cursor:pointer;text-decoration:none}
button.quiet{background:none;color:var(--dim);border-color:#333}
.mono{font-family:ui-monospace,monospace;font-size:14px}.dim{color:var(--dim)}.busy{color:#d7b46a}.bad{color:var(--bad)}
.help{color:var(--dim);font-size:14px}.good{color:#5fa0a4}.warn{color:#d7b46a}
.lang{border-top:1px solid #2a2a2a;margin-top:10px;padding-top:6px}.lang:first-of-type{border-top:0;margin-top:0}
.lang h3{font-size:16px;margin:4px 0}.stat{margin:4px 0;font-size:14px}.note{margin:4px 0;font-size:14px;color:#d7b46a}
.addlang{margin:12px 0 0;padding-top:8px;border-top:1px dashed #2a2a2a}select{background:#1f2a36;color:var(--acc);border:1px solid #2f4256;border-radius:6px;padding:4px 8px;font:inherit;font-size:14px}
</style></head><body><div class="wrap">NAV<main>BODY</main></div><script>
// the module last opened is remembered: "/" without ?m= goes back to it
const MOD = "MODULE", asked = new URLSearchParams(location.search).get('m');
try { if (location.pathname === '/' && asked === null && (localStorage.getItem('studioModule') || MOD) !== MOD)
        location.replace('/?m=' + localStorage.getItem('studioModule'));
      else if (location.pathname === '/') localStorage.setItem('studioModule', MOD); } catch (e) {}
document.querySelector('nav a.mod.on')?.scrollIntoView({inline: 'center', block: 'nearest'});   // on a phone, a strip
async function post(u){ const r = await fetch(u, {method:'POST'}); if (!r.ok) alert(await r.text()); location.reload(); }
const clean = document.getElementById('clean');
if (clean){ try { clean.value = localStorage.getItem('studioClean') || 'deepfilter'; } catch (e) { clean.value = 'deepfilter'; }
  clean.onchange = () => { try { localStorage.setItem('studioClean', clean.value); } catch (e) {} }; }
async function addLang(stem){ const l = document.getElementById('add-' + stem).value; if (!l) return;
  const r = await fetch('/api/narration/add?lecture=' + stem + '&lang=' + l, {method:'POST'});
  if (!r.ok) alert(await r.text()); location.reload(); }
async function buildLang(stem, lang){ const r = await fetch('/api/narration/build?lecture=' + stem + '&lang=' + lang, {method:'POST'});
  if (!r.ok) alert((await r.json()).error); location.reload(); }
function build(q){ post('/api/compose?' + q + '&clean=' + (clean ? clean.value : 'deepfilter')); }
function del(q){ if (confirm('Delete this recording and its video?')) post('/api/delete?' + q); }
if (BUSY) setTimeout(() => location.reload(), 10000);
</script></body></html>"""


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
        zipped = self.gzips() and len(body) > 1024
        if self.headers.get("If-Modified-Since") == mtime:
            self.send_response(304)
            self.send_header("Last-Modified", mtime)
            self.send_header("Cache-Control", "no-cache")
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
        self.send_header("Cache-Control", "no-cache")
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
        if path == "/narration":
            return self.html(narration_page(*a))
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

    def do_GET(self):
        path, q, b, n = self.args()
        if path in ("/narration", "/api/narration"):
            return self.narration_get(path, q)
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
        if path in ("/", "/index.html"):
            m = q.get("m", "0")
            return self.html(studio(int(m) if m.isdigit() and int(m) in MODULES else 0))
        if path == "/lecture":
            if not b:
                return self.send_error(404, "no such lecture")
            return self.html(lecture(b))
        if path == "/watch":
            if not (b and n and (recdir(b) / f"{n}.mp4").exists()):
                return self.send_error(404, "no such video")
            return self.html(watch(b, n))
        if path == "/edit":
            if not (b and (ROOT / b / "presenter" / "lines.json").exists()):
                return self.send_error(404, "prepare the presenter page first")
            return self.html(editor(b))
        m = re.fullmatch(r"/([\w-]+)/presenter/presenter\.html", path)
        if m and B.is_build(m[1]):                         # rendered from presenter.PAGE: a page fix reaches every lecture
            page = presenter_page(m[1])
            if page:
                return self.html(page)
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
                return self.json({"error": "prepare the presenter page first"}, 404)
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
                later.append(lambda: export(b, q.get("clean") if q.get("clean") in CLEAN else "deepfilter"))
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
