"""What the editor's web API does, without HTTP (serve_presenter.py routes to these; test_api.py calls them).

Every function takes the studio's output folder (`root`, out/), a build name, and an open database connection.
"""
import hashlib
import json
import shutil
import time
from pathlib import Path

from studio import media as M
from studio import narration_edit as N
from studio import store as S
from studio import timeline as T
from studio import voice_server

ABANDONED = 120              # seconds without a piece: a session still "recording" was cut off (tab closed, crash)
EDIT_KEYS = {"cuts", "trim_in", "trim_out", "nudge", "rejected", "deleted"}


def lines_hash(root, build):
    p = Path(root) / build / "presenter" / "lines.json"
    return hashlib.sha1(p.read_bytes()).hexdigest()[:12] if p.exists() else ""


def usable(root, build, sessions):
    """Sessions recorded against the current line list (a rebuilt video moves every line)."""
    h = lines_hash(root, build)
    return [s for s in sessions if s["lines_hash"] == h]


# ─── recording ────────────────────────────────────────────────────────────
def chunk(root, build, name, seq, data, c):
    n = M.add_chunk(Path(root) / build, name, seq, data)
    S.session_seen(c, build, name, chunks=n, lines_hash=lines_hash(root, build))
    return n


def events(root, build, name, body, c):
    ev = json.loads(body)
    if not isinstance(ev, list) or not all(isinstance(e, list) and len(e) >= 3 for e in ev):
        raise ValueError("events must be a list of [t, kind, position, …]")
    rec = M.recdir(Path(root) / build)
    rec.mkdir(parents=True, exist_ok=True)
    tmp = rec / f"{name}.json.tmp"
    tmp.write_text(json.dumps(ev))
    tmp.replace(rec / f"{name}.json")
    S.session_seen(c, build, name, lines_hash=lines_hash(root, build))


def finish(root, build, name, c):
    """The page says the session ended: it is ready to process. Returns whether it should be processed."""
    S.session_seen(c, build, name, lines_hash=lines_hash(root, build))
    row = c.execute("select state from sessions where build=? and name=?", (build, name)).fetchone()
    if row["state"] in ("processing", "ready"):
        return False
    S.set_session(c, build, name, state="recorded")
    return True


def forget(root, build, name, c):
    """A deleted recording leaves nothing for the editor to list: the session and its edits go, and so do the files
    made from it (pieces, joined audio, cleaned voices, preview, pauses, words). The `<name>.json.<hash>` backups stay:
    they are the history of the remaps."""
    rec = M.recdir(Path(root) / build)
    S.drop_session(c, build, name)
    for d in (rec / f"{name}.chunks", rec / f"{name}.words"):
        shutil.rmtree(d, ignore_errors=True)
    for f in [rec / f"{name}.{x}" for x in ("webm", "json", "mp4", "m4a", "silence.json", "words.json")] + \
            list(rec.glob(f"{name}.*.f32")):
        f.unlink(missing_ok=True)


def abandoned(root, build, c, now=None):
    """Sessions whose pieces stopped coming long ago without a finish: close them, so they get processed."""
    now = now or time.time()
    out = []
    for s in S.sessions(c, build):
        if s["state"] == "recording" and now - s["updated"] > ABANDONED:
            S.set_session(c, build, s["name"], state="recorded")
            out.append(s["name"])
    return out


def import_old(root, build, c):
    """Recordings made before the editor (one upload at the end): register them as sessions. A recording older
    than the current line list belongs to an earlier build of the video and is marked stale."""
    rec = M.recdir(Path(root) / build)
    known = {s["name"] for s in S.sessions(c, build)}
    lj = Path(root) / build / "presenter" / "lines.json"
    out = []
    for w in sorted(rec.glob("*.webm")) if rec.is_dir() else []:
        if w.stem in known or not (rec / f"{w.stem}.json").exists() or (rec / f"{w.stem}.chunks").exists():
            continue
        fresh = lj.exists() and w.stat().st_mtime >= lj.stat().st_mtime
        S.session_seen(c, build, w.stem, lines_hash=lines_hash(root, build) if fresh else "stale")
        S.set_session(c, build, w.stem, state="recorded")
        out.append(w.stem)
    return out


# ─── the project, as the editor sees it ───────────────────────────────────
def counts(root, build, c):
    """{line: takes that are not rejected}, from the events alone (before any audio is processed)."""
    b = Path(root) / build
    starts = [l[0] for l in M.lines(b)]
    out = {}
    eds = S.edits(c, build)
    for s in usable(root, build, S.sessions(c, build)):
        for t in T.takes(s["name"], M.session_events(b, s["name"]), starts):
            e = eds.get(t["id"], {})
            if not e.get("rejected", t["rejected"]) and not e.get("deleted"):
                out[t["line"]] = out.get(t["line"], 0) + 1
    return out


def take_view(root, build, t, text, events, silences):
    """One take for the editor: its edit, its edited tracks (to preview it alone), its pauses, its transcript and
    the script check."""
    b = Path(root) / build
    tr = T.edited(t, events, t["edit"])
    raw = T.take_tracks(t, events)
    total = T.length(raw["voice"])
    local = [(max(a, t["t_in"]) - t["t_in"], min(b2, t["t_out"]) - t["t_in"]) for a, b2 in silences
             if b2 > t["t_in"] and a < t["t_out"]]
    w = M.take_words(b, t)
    check = None
    if w:
        missing, extra, changed = T.script_check(text, [tuple(x) for x in w["heard"]])
        weak = [x[0] for x in w["aligned"] if x[3] < 0.1]
        check = {"missing": [m[1] for m in missing], "extra": [[x[1], x[2], x[3]] for x in extra],
                 "changed": [list(x) for x in changed], "weak": weak}
    return {"id": t["id"], "session": t["session"], "line": t["line"], "t_in": t["t_in"], "t_out": t["t_out"],
            "rejected": t["rejected"], "edit": t["edit"], "raw_length": round(total, 3),
            "length": round(T.length(tr["voice"]), 3), "tracks": tr,
            "pauses": [[round(a, 3), round(b2, 3)] for a, b2 in local],
            "proposed": [x for x in T.shrink_silences(local, raw["picture"], total)    # not cut yet
                         if not any(a <= x[0] + 1e-3 and x[1] <= b2 + 1e-3 for a, b2 in t["edit"].get("cuts", []))],
            "words": w, "check": check}


def voice_marks(root, build):
    """{line: the voice check's verdict on its clip} (voice_check.py / revoice_line.py), where there is one."""
    b = Path(root) / build
    p = b / "voice_check.json"
    if not p.exists():
        return {}
    by_text = {N.norm(r["text"]): r for r in json.loads(p.read_text())}
    out = {}
    for k, l in enumerate(M.lines(b)):
        r = by_text.get(N.norm(l[1]))
        if r:
            out[k] = {"ok": r["ok"], "listen": r.get("listen", False), "fails": r["fails"],
                      "heard": (r["heard"][0] if isinstance(r["heard"], list) else r["heard"])}
    return out


def editable(build):
    try:
        path, _, _ = N.source(build)
        return path.exists()
    except ValueError:
        return False


def mtime(path):
    """Whole seconds of a file's age marker, for ?v= (0 when it is not there yet)."""
    try:
        return int(Path(path).stat().st_mtime)
    except OSError:
        return 0


def project(root, build, c):
    b = Path(root) / build
    rec = M.recdir(b)
    ls = M.lines(b)
    sessions = S.sessions(c, build)
    good = usable(root, build, sessions)
    eds, ch, st = S.edits(c, build), S.choices(c, build), S.settings(c, build)
    if st["missing"] == "original":
        try:
            M.original(b)
        except Exception:                          # a video without a soundtrack: nothing to fall back on
            st["missing"] = "silent"
    el, tk = M.project_edit_list(b, good, eds, ch, fallback=st["missing"])
    navoiy = build.endswith("_uz_navoiy")
    takes = {}
    for k, lst in tk.items():
        views = []
        for t in lst:
            if t["edit"].get("deleted"):
                continue
            ev = M.session_events(b, t["session"])
            sil = json.loads((M.recdir(b) / f"{t['session']}.silence.json").read_text()) \
                if (M.recdir(b) / f"{t['session']}.silence.json").exists() else []
            views.append(take_view(root, build, t, ls[k][1], ev, sil))
        takes[k] = views
    used = {tid for _, _, _, tid in el["lines"] if tid}
    stale = {s["name"] for s in sessions} - {s["name"] for s in good}
    return {
        "build": build,
        "video": f"/{build}/presenter/{build}_silent.mp4",
        "video_version": int((b / "presenter" / f"{build}_silent.mp4").stat().st_mtime),
        "lines": [[l[0], l[1]] for l in ls],
        "sessions": [dict(s, stale=s["name"] in stale) for s in sessions],
        "audio": {**{s["name"]: f"/{build}/presenter/recordings/{s['name']}.m4a?v={mtime(rec / (s['name'] + '.m4a'))}"
                     for s in good if s["state"] == "ready"},
                  **({T.ORIGINAL: f"/{build}/presenter/original.m4a?v={mtime(b / 'presenter' / 'original.m4a')}"}
                     if st["missing"] == "original" else {})},
        "settings": st, "voice": voice_marks(root, build), "editable": editable(build),
        "old_page": bool(ls) and len(ls[0]) < 4,      # prepared before lines knew their section: refresh it
        "engine": "navoiy" if navoiy else "edge",
        "voice_server": voice_server.status() if navoiy else None,
        "takes": takes, "choices": ch, "used": sorted(used),
        "edit_list": el,
        "jobs": S.jobs(c, build),
        "exports": exports(root, build),
    }


def exports(root, build):
    d = Path(root) / build / "presenter" / "export"
    return [{"name": f.name, "url": f"/{build}/presenter/export/{f.name}", "size": f.stat().st_size,
             "time": f.stat().st_mtime} for f in sorted(d.iterdir())] if d.is_dir() else []


# ─── edits ────────────────────────────────────────────────────────────────
def set_edit(root, build, take, changes, c):
    bad = set(changes) - EDIT_KEYS
    if bad:
        raise ValueError(f"unknown edit fields: {', '.join(sorted(bad))}")
    for k in ("trim_in", "trim_out", "nudge"):
        if changes.get(k) is not None:
            changes[k] = float(changes[k])
            lim = (-3, 3) if k == "nudge" else (0, 600)
            if not lim[0] <= changes[k] <= lim[1]:
                raise ValueError(f"{k} out of range")
    if changes.get("cuts") is not None:
        changes["cuts"] = [list(x) for x in T.merge([(float(a), float(b)) for a, b in changes["cuts"]])]
    return S.set_edit(c, build, take, changes)


def choose(root, build, line, take, c):
    S.choose(c, build, int(line), take or None)


def find_take(root, build, take_id, c):
    b = Path(root) / build
    tk = M.all_takes(b, usable(root, build, S.sessions(c, build)), S.edits(c, build))
    for lst in tk.values():
        for t in lst:
            if t["id"] == take_id:
                return t
    raise KeyError(f"no take {take_id}")


def shrink(root, build, take_ids, c):
    """Add the proposed pause cuts to each take (pauses over a still picture, shortened)."""
    b = Path(root) / build
    out = {}
    for tid in take_ids:
        t = find_take(root, build, tid, c)
        sil_p = M.recdir(b) / f"{t['session']}.silence.json"
        sil = json.loads(sil_p.read_text()) if sil_p.exists() else []
        v = take_view(root, build, t, "", M.session_events(b, t["session"]), sil)
        cuts = T.merge([tuple(x) for x in t["edit"].get("cuts", [])] + [tuple(x) for x in v["proposed"]])
        out[tid] = S.set_edit(c, build, tid, {"cuts": [list(x) for x in cuts]})
    return out


def cut_extras(root, build, take_id, c, pad=0.03):
    """Cut every word heard that is not in the approved text (an "um", a false start, a repeated word)."""
    b = Path(root) / build
    t = find_take(root, build, take_id, c)
    w = M.take_words(b, t)
    if not w:
        raise ValueError("transcribe this take first")
    text = M.lines(b)[t["line"]][1]
    _, extra, _ = T.script_check(text, [tuple(x) for x in w["heard"]])
    cuts = T.merge([tuple(x) for x in t["edit"].get("cuts", [])] +
                   [(max(0, a - pad), b2 + pad) for _, _, a, b2 in extra])
    return S.set_edit(c, build, take_id, {"cuts": [list(x) for x in cuts]})


def chosen_ids(root, build, c):
    b = Path(root) / build
    el, _ = M.project_edit_list(b, usable(root, build, S.sessions(c, build)), S.edits(c, build), S.choices(c, build),
                                fallback=S.settings(c, build)["missing"])
    return [tid for _, _, _, tid in el["lines"] if tid]


def set_setting(root, build, key, value, c):
    allowed = {"missing": ("original", "silent")}
    if key not in allowed or value not in allowed[key]:
        raise ValueError(f"unknown setting {key}={value}")
    S.set_setting(c, build, key, value)
