"""What the editor's web API does, without HTTP (serve_presenter.py routes to these; test_api.py calls them).

Every function takes the studio's output folder (`root`, out/), a build name, and an open database connection.
"""
import hashlib
import json
import shutil
import time
from pathlib import Path

import builds as B
from studio import media as M
from studio import narration_edit as N
from studio import rewrite as RW
from studio import store as S
from studio import timeline as T
from studio import versions as V
from studio import voice_server

ABANDONED = 120              # seconds without a piece: a session still "recording" was cut off (tab closed, crash)
EDIT_KEYS = {"cuts", "auto_cuts", "squeeze", "trim_in", "trim_out", "nudge", "rejected", "deleted"}


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
    for f in [rec / f"{name}.{x}" for x in ("webm", "json", "mp4", "m4a", "yours.m4a", "cloned.json", "silence.json", "words.json")] + \
            list(rec.glob(f"{name}.*.f32")) + list(rec.glob(f"{name}.*.levels.json")):
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


def covered(span, cuts):
    return any(a <= span[0] + 1e-3 and span[1] <= b + 1e-3 for a, b in cuts)


def margin_of(settings):
    """Seconds of silence kept before the first word and after the last, from a lecture's settings."""
    try:
        return float(settings.get("margin", S.DEFAULTS["margin"]))
    except ValueError:
        return float(S.DEFAULTS["margin"])


def by_hand(edit, key):
    """A trim the instructor set (dragged or typed), not the tightening tool."""
    return bool(edit.get(key)) and key not in edit.get("auto", [])


def tightening(t, events, local, total, picture, margin):
    """What the tightening tool would still add to this take, as {pauses, cuts, trim_in, trim_out, start, end, gain}:
    the pause cuts inside the take, and the two trims that leave `margin` seconds around the voice -- each only
    when it is tighter than the trim the take has and was not set by hand -- minus what the edit already holds (so
    a second press finds nothing). start / end: seconds the new trims add; gain: seconds the take would lose."""
    e = t["edit"]
    have = [tuple(x) for x in e.get("cuts", []) + e.get("auto_cuts", [])]
    pauses = [x for x in T.shrink_silences(T.interior(local, total), picture, total) if not covered(x, have)]
    fi, fo = T.fit(local, total, margin)
    ti, to = e.get("trim_in") or 0.0, e.get("trim_out") or 0.0
    new_in = fi if fi > ti + 1e-3 and not by_hand(e, "trim_in") else None
    new_out = fo if fo > to + 1e-3 and not by_hand(e, "trim_out") else None
    now = T.length(T.edited(t, events, e)["voice"])
    after = T.length(T.edited(t, events, dict(e, auto_cuts=T.merge(have + pauses), trim_in=new_in or ti,
                                              trim_out=new_out or to))["voice"])
    return {"pauses": len(pauses), "cuts": [list(x) for x in T.merge(pauses)], "trim_in": new_in, "trim_out": new_out,
            "start": round(new_in - ti, 3) if new_in else 0, "end": round(new_out - to, 3) if new_out else 0,
            "gain": round(now - after, 3)}


def picture_spans(picture):
    """The raw picture as [[from, to, "play" | "hold"]], neighbours of one kind joined (the level strip's band)."""
    out, t = [], 0.0
    for d, kind, *_ in picture:
        if out and out[-1][2] == kind:
            out[-1][1] = round(t + d, 4)
        else:
            out.append([round(t, 4), round(t + d, 4), kind])
        t += d
    return out


def take_view(root, build, t, text, events, silences, margin=0.3):
    """One take for the editor: its edit, its edited tracks (to preview it alone), its pauses, its transcript and
    the script check. lead / tail: the silence before the first word / after the last; fit: the trims that would
    keep `margin` seconds of it; raw_picture: when the picture plays and holds, for the level strip."""
    b = Path(root) / build
    tr = T.edited(t, events, t["edit"])
    raw = T.take_tracks(t, events)
    total = T.length(raw["voice"])
    local = [(max(a, t["t_in"]) - t["t_in"], min(b2, t["t_out"]) - t["t_in"]) for a, b2 in silences
             if b2 > t["t_in"] and a < t["t_out"]]
    tight = tightening(t, events, local, total, raw["picture"], margin)
    lead, tail = T.lead_tail(local, total)
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
            "proposed": tight["cuts"],                       # pauses inside the take, not cut yet
            "tighten": tight,
            "lead": round(lead, 3), "tail": round(tail, 3), "margin": margin,
            "fit": [round(x, 3) for x in T.fit(local, total, margin)], "raw_picture": picture_spans(raw["picture"]),
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


def audio_alt_urls(root, build, good):
    """{session: URL of its audio before voice conversion}: for a session made with the cloned profile, the same
    recording cleaned only (what the instructor's voice sounds like), to compare with `audio`."""
    rec = M.recdir(Path(root) / build)
    return {s["name"]: f"/{build}/presenter/recordings/{s['name']}.yours.m4a?v={mtime(rec / (s['name'] + '.yours.m4a'))}"
            for s in good if s["state"] == "ready" and s.get("clean") == "cloned" and (rec / f"{s['name']}.yours.m4a").exists()}


def audio_urls(root, build, good, st):
    """{voice source: URL of its audio}: every ready session, and the lecture's own narration when that is the fallback."""
    b = Path(root) / build
    rec = M.recdir(b)
    return {**{s["name"]: f"/{build}/presenter/recordings/{s['name']}.m4a?v={mtime(rec / (s['name'] + '.m4a'))}"
               for s in good if s["state"] == "ready"},
            **({T.ORIGINAL: f"/{build}/presenter/original.m4a?v={mtime(b / 'presenter' / 'original.m4a')}"}
               if st["missing"] == "original" else {})}


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
    navoiy = B.engine(build) == "navoiy"
    takes = {}
    for k, lst in tk.items():
        views = []
        for t in lst:
            if t["edit"].get("deleted"):
                continue
            ev = M.session_events(b, t["session"])
            sil = json.loads((M.recdir(b) / f"{t['session']}.silence.json").read_text()) \
                if (M.recdir(b) / f"{t['session']}.silence.json").exists() else []
            views.append(take_view(root, build, t, ls[k][1], ev, sil, margin_of(st)))
        takes[k] = views
    used = {tid for _, _, _, tid in el["lines"] if tid}
    stale = {s["name"] for s in sessions} - {s["name"] for s in good}
    return {
        "build": build,
        "video": f"/{build}/presenter/{build}_silent.mp4",
        "video_version": int((b / "presenter" / f"{build}_silent.mp4").stat().st_mtime),
        "lines": [[l[0], l[1]] for l in ls],
        "sessions": [dict(s, stale=s["name"] in stale) for s in sessions],
        "audio": audio_urls(root, build, good, st), "audio_alt": audio_alt_urls(root, build, good),
        "settings": st, "voice": voice_marks(root, build), "editable": editable(build),
        "old_page": bool(ls) and len(ls[0]) < 4,      # prepared before lines knew their section: refresh it
        "engine": "navoiy" if navoiy else "edge",
        "voice_server": voice_server.status() if navoiy else None,
        "takes": takes, "choices": ch, "used": sorted(used),
        "edit_list": el,
        "jobs": S.jobs(c, build),
        "scenes": scene_names(b, ls),
        "versions": V.view(root, build, c),
        "exports": exports(root, build),
    }


def line_view(root, build, k, c):
    """One line (k counts from 0, like every line in the API) for the presenter page's takes panel: its text, its takes (the same views the editor gets), the
    take the video uses and the one it would use by default, the audio of every ready session, the margin, the video,
    the neighbours' joins (the last 2 s of the line before, the first 2 s of the line after, as tracks), and the
    recordings of this line that are not processed yet ("pending": recording, waiting, processing or failed)."""
    b = Path(root) / build
    ls = M.lines(b)
    if not 0 <= k < len(ls):
        raise KeyError(f"no line {k}")
    sessions = S.sessions(c, build)
    good = usable(root, build, sessions)
    eds, ch, st = S.edits(c, build), S.choices(c, build), S.settings(c, build)
    if st["missing"] == "original":
        try:
            M.original(b)
        except Exception:                          # a video without a soundtrack: nothing to fall back on
            st["missing"] = "silent"
    tk = M.all_takes(b, good, eds)
    mine = [t for t in tk.get(k, []) if not t["edit"].get("deleted")]
    views = []
    for t in mine:
        sil_p = M.recdir(b) / f"{t['session']}.silence.json"
        sil = json.loads(sil_p.read_text()) if sil_p.exists() else []
        views.append(take_view(root, build, t, ls[k][1], M.session_events(b, t["session"]), sil, margin_of(st)))
    used = M.chosen_take(mine, ch.get(k))
    starts = [l[0] for l in ls]
    pending = []
    for s in good:
        if s["state"] != "ready":
            for t in T.takes(s["name"], M.session_events(b, s["name"]), starts):
                if t["line"] == k:
                    pending.append({"id": t["id"], "session": s["name"], "state": s["state"], "error": s["error"],
                                    "seconds": round(t["t_out"] - t["t_in"], 2)})
    return {"build": build, "line": k, "lines": len(ls), "text": ls[k][1], "starts": [ls[k][0], ls[k + 1][0] if k + 1 < len(ls) else None],
            "video": f"/{build}/presenter/{build}_silent.mp4",
            "video_version": mtime(b / "presenter" / f"{build}_silent.mp4"),
            "takes": views, "chosen": used["id"] if used else None, "picked": ch.get(k),
            "audio": audio_urls(root, build, good, st), "margin": margin_of(st), "settings": st,
            "context": M.neighbourhood(b, k, tk, ch, fallback=st["missing"]), "pending": pending,
            "sessions": [{"name": s["name"], "state": s["state"], "error": s["error"]} for s in good],
            "busy": any(s["state"] in ("recording", "recorded", "processing") for s in good)}


def scene_names(b, ls):
    """The scene each line belongs to ("" for all of them when the presenter page predates scenes)."""
    if not ls or len(ls[0]) < 4:
        return [""] * len(ls)
    names = [p.stem for p in RW.scene_files(b)]
    return [names[l[3]] for l in ls]


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
    for k in ("cuts", "auto_cuts"):
        if changes.get(k) is not None:
            changes[k] = [list(x) for x in T.merge([(float(a), float(b)) for a, b in changes[k]])]
    if changes.get("squeeze") is not None:
        changes["squeeze"] = [[float(a), float(b), float(n)] for a, b, n in changes["squeeze"]]
    auto = S.edit(c, build, take).get("auto", [])
    if auto and ("trim_in" in changes or "trim_out" in changes):       # a trim changed by hand is the tool's no more
        changes["auto"] = [k for k in auto if k not in changes] or None
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


def view_of(root, build, t, c):
    b = Path(root) / build
    sil_p = M.recdir(b) / f"{t['session']}.silence.json"
    sil = json.loads(sil_p.read_text()) if sil_p.exists() else []
    return take_view(root, build, t, "", M.session_events(b, t["session"]), sil, margin_of(S.settings(c, build)))


def shrink(root, build, take_ids, c):
    """Tighten each take: the pause cuts inside it (edit["auto_cuts"]) and the trims that leave the margin around
    the voice (edit["trim_in"], edit["trim_out"]), kept apart from the instructor's own work (edit["auto"] names the
    trims the tool set) so they can be taken back. A trim set by hand stays. Pressing it again adds nothing.
    Returns {take id: its edit} and "saved": the seconds the lecture lost."""
    out, saved = {}, 0.0
    for tid in take_ids:
        t = find_take(root, build, tid, c)
        e, tg = t["edit"], view_of(root, build, t, c)["tighten"]
        auto = T.merge([tuple(x) for x in e.get("auto_cuts", [])] + [tuple(x) for x in tg["cuts"]])
        ch, names = {"auto_cuts": [list(x) for x in auto] or None}, list(e.get("auto", []))
        for k in ("trim_in", "trim_out"):
            if tg[k]:
                ch[k] = tg[k]
                names += [k] if k not in names else []
        ch["auto"] = names or None
        out[tid] = S.set_edit(c, build, tid, ch)
        saved += tg["gain"]
    out["saved"] = round(saved, 3)
    return out


def unshrink(root, build, take_id, c):
    """Take back what the tightening tool did: its pause cuts, its squeezes and the trims it set (edit["auto"]).
    The instructor's own cuts, hand-set trims and nudge stay."""
    t = find_take(root, build, take_id, c)
    undo = {"auto_cuts": None, "squeeze": None, "auto": None}
    undo.update({k: None for k in t["edit"].get("auto", [])})
    return S.set_edit(c, build, take_id, undo)


def fit(root, build, take_id, end, c):
    """Set the take's trims so `margin` seconds of silence stay before the first word (end "start"), after the
    last ("end"), or both. Counts as the tool's work (undo tightening takes it back); a fit of 0 clears the trim."""
    if end not in ("start", "end", "both"):
        raise ValueError("end must be start, end or both")
    t = find_take(root, build, take_id, c)
    fi, fo = view_of(root, build, t, c)["fit"]
    ch, names = {}, list(t["edit"].get("auto", []))
    for k, v, on in (("trim_in", fi, end != "end"), ("trim_out", fo, end != "start")):
        if on:
            ch[k] = v or None
            names = [x for x in names if x != k] + ([k] if v else [])
    ch["auto"] = names or None
    return S.set_edit(c, build, take_id, ch)


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
    if key == "margin":                                    # seconds of silence kept at a line's ends
        try:
            m = float(value)
        except ValueError:
            m = -1
        if not 0 <= m <= 5:
            raise ValueError(f"unknown setting {key}={value}")
        return S.set_setting(c, build, key, f"{m:g}")
    allowed = {"missing": ("original", "silent")}
    if key not in allowed or value not in allowed[key]:
        raise ValueError(f"unknown setting {key}={value}")
    S.set_setting(c, build, key, value)


def levels(root, build, src, c):
    """{step, db}: the voice level of a session of this build, or of the lecture's own narration (src ORIGINAL)."""
    b = Path(root) / build
    if src == T.ORIGINAL:
        return M.levels(b, src, "")
    row = next((s for s in S.sessions(c, build) if s["name"] == src), None)
    if row is None:
        raise KeyError(f"no session {src}")
    return M.levels(b, src, row["clean"] or "deepfilter")
