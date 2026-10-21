"""The editor's tables, in the studio's SQLite file (out/studio.sqlite, beside the old `recordings` table).

  sessions  one row per recording session: uploaded chunk count, state (recording -> recorded -> processing ->
            ready | failed), the cleaning profile its audio was prepared with
  edits     one row per take with an edit: {"cuts": [[a, b]], "trim_in", "trim_out", "nudge", "rejected", …};
            "auto" names the trims the tightening tool set (undo takes back those, not a trim set by hand)
  choices   the take chosen for each line (none: the newest take that is not rejected)
  jobs      background work and its state, shown in the editor (process a session, transcribe a take, export)
  versions  drafts of a rewritten scene (studio/versions.py): numbered per scene, built on an earlier version or on the
            lecture, holding {line: text}; queued -> voicing -> rendering -> ready, then merged | stale | discarded
  line_status  the instructor's approval of one narration line or screen label in one language (studio/linestatus.py):
            the hash of the text approved, when, and the other languages' texts at that moment (so a change in one
            of them shows as "needs update"). Keyed by lecture stem (m7_lecture01), not by build.
"""
import json
import sqlite3
import time

SCHEMA = """
create table if not exists sessions (
    build text, name text, created real, updated real, state text default 'recording',
    chunks integer default 0, seconds real default 0, clean text default '', error text default '',
    lines_hash text default '',                 -- the line list it was recorded against (a rebuilt video differs)
    primary key (build, name));
create table if not exists edits (build text, take text, edit text, primary key (build, take));
create table if not exists choices (build text, line integer, take text, primary key (build, line));
create table if not exists settings (build text, key text, value text, primary key (build, key));
create table if not exists jobs (
    build text, kind text, key text, state text, error text default '', updated real, detail text default '',
    primary key (build, kind, key));
create table if not exists versions (
    build text, scene text, n integer, base integer,       -- base: the version it grew from (null: the lecture)
    texts text default '{}',                               -- {line: text} this version says, its base's lines included
    state text default 'queued', error text default '', created real, updated real,
    report text default '{}',                              -- {line: the voice check's result}
    primary key (build, scene, n));
create table if not exists line_status (
    lecture text, lang text, kind text,                     -- kind: line | label
    key text, text_hash text, approved_at real,
    sources text default '{}',                              -- {language: its text when this was approved}
    primary key (lecture, lang, kind, key));
"""


def connect(path):
    c = sqlite3.connect(path, timeout=10)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c


def session_seen(c, build, name, chunks=None, lines_hash=""):
    now = time.time()
    c.execute("insert or ignore into sessions (build, name, created, updated, lines_hash) values (?,?,?,?,?)",
              (build, name, now, now, lines_hash))
    if chunks is not None:
        c.execute("update sessions set chunks=max(chunks, ?), updated=? where build=? and name=?",
                  (chunks, now, build, name))


def set_session(c, build, name, **kw):
    kw["updated"] = time.time()
    c.execute(f"update sessions set {', '.join(f'{k}=?' for k in kw)} where build=? and name=?",
              (*kw.values(), build, name))


def sessions(c, build):
    return [dict(r) for r in c.execute("select * from sessions where build=? order by created", (build,))]


def drop_session(c, build, name):
    """Forget a session: its row, and the edits and choices of its takes (take ids start with `<name>@`)."""
    mine = f"{name}@"
    c.execute("delete from sessions where build=? and name=?", (build, name))
    c.execute("delete from edits where build=? and substr(take, 1, ?)=?", (build, len(mine), mine))
    c.execute("delete from choices where build=? and substr(take, 1, ?)=?", (build, len(mine), mine))


def edit(c, build, take):
    r = c.execute("select edit from edits where build=? and take=?", (build, take)).fetchone()
    return json.loads(r["edit"]) if r else {}


def edits(c, build):
    return {r["take"]: json.loads(r["edit"]) for r in c.execute("select * from edits where build=?", (build,))}


def set_edit(c, build, take, changes):
    """Merge `changes` into the take's edit (a None value removes that key)."""
    e = edit(c, build, take)
    for k, v in changes.items():
        if v is None:
            e.pop(k, None)
        else:
            e[k] = v
    c.execute("insert or replace into edits values (?,?,?)", (build, take, json.dumps(e)))
    return e


def choices(c, build):
    return {r["line"]: r["take"] for r in c.execute("select * from choices where build=?", (build,))}


def choose(c, build, line, take):
    if take is None:
        c.execute("delete from choices where build=? and line=?", (build, line))
    else:
        c.execute("insert or replace into choices values (?,?,?)", (build, line, take))


def job(c, build, kind, key, state, error="", detail=""):
    c.execute("insert or replace into jobs values (?,?,?,?,?,?,?)", (build, kind, key, state, error, time.time(), detail))


def jobs(c, build):
    return [dict(r) for r in c.execute("select * from jobs where build=? order by updated", (build,))]


def reset_running(c):
    """A server restart kills running jobs: mark them as interrupted, so they can be started again."""
    c.execute("update jobs set state='failed', error='interrupted (server restarted)' where state in ('queued','running')")
    c.execute("update sessions set state='recorded' where state='processing'")
    c.execute("update versions set state='failed', error='interrupted (server restarted)' "
              "where state in ('queued','voicing','rendering')")


# ─── versions of a rewritten scene ───
def _version(r):
    return dict(r, texts=json.loads(r["texts"]), report=json.loads(r["report"]))


def version_add(c, build, scene, base, texts):
    """A new version of `scene`, numbered after the last one (discarded ones keep their number). Returns n."""
    n = (c.execute("select max(n) from versions where build=? and scene=?", (build, scene)).fetchone()[0] or 0) + 1
    now = time.time()
    c.execute("insert into versions (build, scene, n, base, texts, created, updated) values (?,?,?,?,?,?,?)",
              (build, scene, n, base, json.dumps(texts, ensure_ascii=False), now, now))
    return n


def version(c, build, scene, n):
    r = c.execute("select * from versions where build=? and scene=? and n=?", (build, scene, n)).fetchone()
    return _version(r) if r else None


def versions(c, build, scene=None):
    """The build's versions (a scene's, if given), oldest first, without the discarded ones."""
    q, a = "select * from versions where build=? and state!='discarded'", [build]
    if scene:
        q, a = q + " and scene=?", a + [scene]
    return [_version(r) for r in c.execute(q + " order by scene, n", a)]


def set_version(c, build, scene, n, **kw):
    for k in ("texts", "report"):
        if k in kw:
            kw[k] = json.dumps(kw[k], ensure_ascii=False)
    kw["updated"] = time.time()
    c.execute(f"update versions set {', '.join(f'{k}=?' for k in kw)} where build=? and scene=? and n=?",
              (*kw.values(), build, scene, n))


DEFAULTS = {"missing": "original",         # a line nobody recorded keeps the video's own narration
            "margin": "0.3"}              # seconds of silence kept before the first word and after the last


def settings(c, build):
    out = dict(DEFAULTS)
    out.update({r["key"]: r["value"] for r in c.execute("select * from settings where build=?", (build,))})
    return out


def set_setting(c, build, key, value):
    c.execute("insert or replace into settings values (?,?,?)", (build, key, value))


# ─── approvals of narration lines and labels ───
def approvals(c, lecture, lang, kind):
    """{key: {"text_hash", "approved_at", "sources"}} for one language of a lecture."""
    return {r["key"]: {"text_hash": r["text_hash"], "approved_at": r["approved_at"], "sources": json.loads(r["sources"])}
            for r in c.execute("select * from line_status where lecture=? and lang=? and kind=?", (lecture, lang, kind))}


def approve(c, lecture, lang, kind, key, text_hash, sources):
    c.execute("insert or replace into line_status values (?,?,?,?,?,?,?)",
              (lecture, lang, kind, key, text_hash, time.time(), json.dumps(sources, ensure_ascii=False)))
