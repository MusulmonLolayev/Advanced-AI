"""Versions of a rewritten scene: the instructor rewrites a line, watches the result, rewrites again, and merges.

A version is a draft of one scene, made from the lecture's narration plus the texts the version changes, in
out/<build>/versions/<scene>/v<N>/:

  narration/   a copy of the narration file with the version's texts (the real file is not touched before the merge)
  media/       the render (the scene's video and subtitles), and a copy of the scene's voice cache (clips already voiced are
               reused; the lecture's own cache is never written by a draft)
  report.json  the voice check of each line voiced for it
  meta.json    {"line": the line that made it, "base": version it grew from, "scene"}

A version grows from `base` -- the version the instructor said "rewrite again" on, else the newest ready one of the
scene, else the lecture -- and holds its base's texts plus the new one, so two lines of one scene end up in one version.
Building it (build_version): voice the line (Navoiy builds), render the scene with OUT_DIR / NARRATION_DIR pointing at
the version folder. Merging it (merge) is today's rewrite, done on purpose: the texts go in the real narration file,
the clips in the lecture's cache, the scene file is replaced, the lecture joined again, the presenter page prepared
again and the recordings moved to the new timings; any failure puts everything back. The scene's other unmerged
versions were made on the old lecture: they become `stale`.
"""
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

import presenter
from studio import media as M
from studio import narration_edit as N
from studio import rewrite as RW
from studio import store as S
from studio import voice_server

HERE = RW.HERE
SCENE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
MAKING = ("queued", "voicing", "rendering")


def vdir(root, build, scene, n):
    assert SCENE.fullmatch(scene), scene
    return Path(root) / build / "versions" / scene / f"v{int(n)}"


def scene_mp4(root, build, scene, n):
    return vdir(root, build, scene, n) / "media" / "videos" / RW.module_of(build) / "1080p60" / f"{scene}.mp4"


def clean_text(build, text):
    """A line's text as the narration file will hold it (Uzbek apostrophes fixed)."""
    t = N.uz_text(text) if build.endswith("_uz_navoiy") else N.norm(text)
    if not t:
        raise ValueError("the new text is empty")
    if "**" in t:
        raise ValueError("the line may not contain **")
    return t


def choose_base(rows, explicit=None):
    """The number of the version a new one grows from: the one asked for (it must be ready), else the newest ready
    one, else None (the lecture). `rows`: the scene's versions."""
    ready = {r["n"] for r in rows if r["state"] == "ready"}
    if explicit is not None:
        if explicit not in ready:
            raise ValueError(f"v{explicit} is not a ready version of this scene")
        return explicit
    return max(ready, default=None)


def parse_base(arg, scene):
    """'S01Q/v2' -> 2 (the scene must be this one)."""
    if not arg:
        return None
    m = re.fullmatch(r"([A-Za-z_]\w*)/v(\d+)", arg)
    if not m or m[1] != scene:
        raise ValueError(f"bad base {arg!r} for {scene}")
    return int(m[2])


def create(root, build, line, text, base, c):
    """A new version for `line` (text None: re-voice as is). Returns (scene, n); the caller queues build_version."""
    b = Path(root) / build
    ls = M.lines(b)
    if not 0 <= line < len(ls):
        raise ValueError("no such line")
    scene = RW.scene_of(b, line)
    rows = S.versions(c, build, scene)
    busy = [r["n"] for r in rows if r["state"] in MAKING]
    if busy:
        raise ValueError(f"v{busy[0]} of this scene is still being made: wait for it, so the new one grows from it")
    bn = choose_base(rows, parse_base(base, scene))
    texts = dict(next((r["texts"] for r in rows if r["n"] == bn), {}))
    text = texts.get(str(line), ls[line][1]) if text is None else clean_text(build, text)
    texts[str(line)] = text
    n = S.version_add(c, build, scene, bn, texts)
    d = vdir(root, build, scene, n)
    d.mkdir(parents=True, exist_ok=True)
    (d / "meta.json").write_text(json.dumps({"scene": scene, "line": line, "base": bn}))
    return scene, n


# ─── what a draft is made of ───
def draft_narration(build, texts, lines, narration_dir):
    """Copy the build's narration file into `narration_dir` and put the version's texts there. Returns the copy."""
    src, lang, single = N.source(build)
    narration_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, narration_dir / src.name)
    path = N.source(build, narration_dir)[0]
    for k, text in sorted(texts.items(), key=lambda x: int(x[0])):
        old = lines[int(k)][1]
        if N.norm(old) != N.norm(text):
            N.rewrite(path, lang, single, old, text)
    return path


def copy_cache(src, dst):
    """The scene's voice cache, copied (never linked: the draft must not write into the source)."""
    if Path(src).is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)


def merge_cache(src, dst):
    """Add to the cache `dst` the entries of `src` it lacks, with their clips. Nothing is removed: an entry for the
    same text goes in front of the old one (manim-voiceover takes the first match), a clip already there stays.
    Returns the number of entries added."""
    src, dst = Path(src), Path(dst)
    if not (src / "cache.json").exists():
        return 0
    mine = json.loads((dst / "cache.json").read_text()) if (dst / "cache.json").exists() else []
    dst.mkdir(parents=True, exist_ok=True)
    added = 0
    for e in json.loads((src / "cache.json").read_text()):
        name = e.get("final_audio", e["original_audio"])
        if any(m.get("input_data") == e["input_data"] and m.get("final_audio", m["original_audio"]) == name for m in mine):
            continue
        for f in {e["original_audio"], name}:
            if (src / f).exists() and not (dst / f).exists():
                shutil.copy2(src / f, dst / f)
        mine.insert(next((i for i, m in enumerate(mine) if m.get("input_data") == e["input_data"]), len(mine)), e)
        added += 1
    tmp = dst / "cache.json.tmp"
    tmp.write_text(json.dumps(mine, ensure_ascii=False, indent=2))
    tmp.replace(dst / "cache.json")
    return added


def merge_voice_check(build_dir, ver_dir, scene):
    """The version's voice-check rows replace the lecture's rows for the same text, pointing at the lecture's clips."""
    vp = Path(ver_dir) / "voice_check.json"
    if not vp.exists():
        return
    lp = Path(build_dir) / "voice_check.json"
    rows = json.loads(lp.read_text()) if lp.exists() else []
    for r in json.loads(vp.read_text()):
        f = Path(build_dir) / "media" / "voiceovers" / scene / Path(r["file"]).name
        rel = str(f.relative_to(HERE)) if f.is_relative_to(HERE) else str(f)       # as voice_check.py writes it
        rows = [x for x in rows if x.get("text") != r["text"] and x.get("file") != rel] + [dict(r, file=rel)]
    lp.write_text(json.dumps(rows, ensure_ascii=False, indent=1))


# ─── building a version (a queued job) ───
def build_version(root, build, scene, n, connect, progress=print, python=M.NAVOIY_PY):
    """Voice the line, render the scene into the version folder. The lecture itself is read, never written."""
    b = Path(root) / build
    with connect() as c:
        row = S.version(c, build, scene, n)
        base = S.version(c, build, scene, row["base"]) if row and row["base"] else None
    if not row or row["state"] != "queued":
        return "skipped (not queued any more)"
    d = vdir(root, build, scene, n)

    def state(st, **kw):
        with connect() as c:
            S.set_version(c, build, scene, n, state=st, **kw)
    try:
        line = json.loads((d / "meta.json").read_text())["line"]
        ls = M.lines(b)
        progress("preparing the draft narration")
        draft_narration(build, row["texts"], ls, d / "narration")
        bd = vdir(root, build, scene, base["n"]) if base else b
        copy_cache(bd / "media" / "voiceovers" / scene, d / "media" / "voiceovers" / scene)
        if (bd / "voice_check.json").exists():
            shutil.copy2(bd / "voice_check.json", d / "voice_check.json")
        report = dict(base["report"]) if base else {}
        if build.endswith("_uz_navoiy"):
            state("voicing")
            if not voice_server.up():
                progress("starting the voice server (about a minute)")
                voice_server.start()
            progress("voicing the line: several takes per sentence, each checked by two recognisers")
            with tempfile.TemporaryDirectory() as tmp:
                job = Path(tmp) / "job.json"
                job.write_text(json.dumps({"build": str(d), "cache_dir": str(d / "media" / "voiceovers" / scene),
                                           "text": row["texts"][str(line)], "report": str(Path(tmp) / "report.json")},
                                          ensure_ascii=False))
                RW.run([str(python), str(HERE / "studio" / "revoice_line.py"), str(job)], what="voicing")
                report[str(line)] = json.loads((Path(tmp) / "report.json").read_text())
        (d / "report.json").write_text(json.dumps(report, ensure_ascii=False))
        state("rendering", report=report)
        progress(f"rendering {scene}")
        RW.run(["./render.sh", RW.module_of(build), "h"],
               env=dict(RW.render_env(build), ONLY=scene, OUT_DIR=str(d), NARRATION_DIR=str(d / "narration")),
               what=f"render {scene}")
        if not scene_mp4(root, build, scene, n).exists():
            raise RuntimeError(f"the render left no {scene}.mp4")
        state("ready")
    except Exception as e:
        state("failed", error=f"{type(e).__name__}: {e}"[-400:])
        raise
    return f"v{n} of {scene} ready"


# ─── merging ───
def check_merge(c, build, scene, n):
    row = S.version(c, build, scene, n)
    if row is None:
        raise KeyError("no such version")
    if row["state"] == "stale":
        raise ValueError("this version was made before the last merge: rewrite the line again from the lecture")
    if row["state"] != "ready":
        raise ValueError(f"only a ready version can be merged (this one is {row['state']})")
    return row


def merge(root, build, scene, n, connect, progress=print):
    """Put version n of `scene` into the lecture. Returns a one-line report. Any failure after the narration was
    changed puts the old narration, the scene file, the cache and the video back."""
    b = Path(root) / build
    with connect() as c:
        row = check_merge(c, build, scene, n)
    d = vdir(root, build, scene, n)
    ls = M.lines(b)
    path, lang, single = N.source(build)
    target = next(p for p in RW.scene_files(b) if p.stem == scene)
    cache = b / "media" / "voiceovers" / scene
    final = b / f"{build}.mp4"
    keep = {"narration": path, "cache": cache / "cache.json", "voice": b / "voice_check.json"}
    saved = {k: (p.read_bytes() if p.exists() else None) for k, p in keep.items()}
    backs = {target: target.with_name(f"{scene}.before_merge.mp4"),
             target.with_suffix(".srt"): target.with_name(f"{scene}.before_merge.srt")}
    video_back = b / f"{build}.before_merge.mp4"
    changed = [k for k, t in row["texts"].items() if N.norm(ls[int(k)][1]) != N.norm(t)]
    backed, video_saved, presenting = [], False, False       # what THIS run backed up or started: only that is undone
    try:
        progress("saving the new texts to the narration file")
        for k in sorted(changed, key=int):
            N.rewrite(path, lang, single, ls[int(k)][1], row["texts"][k])
        progress("adding the voice clips to the lecture's cache")
        merge_cache(d / "media" / "voiceovers" / scene, cache)
        merge_voice_check(b, d, scene)
        progress(f"replacing {scene}")
        src = scene_mp4(root, build, scene, n)
        for dst, back in backs.items():
            if dst.exists():
                shutil.copy2(dst, back)
                backed.append((dst, back))
        for dst in backs:
            if src.with_suffix(dst.suffix).exists():
                shutil.copy(src.with_suffix(dst.suffix), dst)      # a fresh mtime: join_parts.sh pads it again
        progress("joining the lecture video")
        if final.exists():
            shutil.copy2(final, video_back)
            video_saved = True
        RW.run(["./join_parts.sh", os.path.relpath(b, HERE), os.path.relpath(final, HERE)], what="join")   # it prefixes $PWD
        progress("preparing the presenter page")
        old_hash = _hash(b)
        old_end = M.video_end(b)
        presenting = True
        RW.run([str(HERE / ".venv" / "bin" / "python"), "presenter.py", str(b)], what="presenter page")
    except Exception:
        for k, p in keep.items():
            if saved[k] is None:
                p.unlink(missing_ok=True)
            else:
                p.write_bytes(saved[k])
        for dst, back in backed:
            shutil.copy(back, dst)
        if video_saved:
            shutil.copy2(video_back, final)
            try:                        # joined/ holds the new scene padded, and presenter.py reads its timings
                RW.run(["./join_parts.sh", os.path.relpath(b, HERE), os.path.relpath(final, HERE)],
                       what="join (after rollback)")       # the restored scene is newer: padded again
            except Exception as e:
                print(f"merge rollback: lecture not joined again: {e}", flush=True)
                shutil.copy2(video_back, final)
        if presenting:                  # the page may be half rebuilt: make it again from the restored video
            try:
                RW.run([str(HERE / ".venv" / "bin" / "python"), "presenter.py", str(b)], what="presenter page (after rollback)")
            except Exception as e:
                print(f"merge rollback: presenter page not rebuilt: {e}", flush=True)
        raise
    new_lines = M.lines(b)
    moved = 0
    if len(new_lines) == len(ls):
        with connect() as c:
            moved = RW.migrate(root, build, c, ls, old_end, new_lines, M.video_end(b), old_hash, _hash(b))
    with connect() as c:
        S.set_version(c, build, scene, n, state="merged")
        for r in S.versions(c, build, scene):
            if r["n"] != n and r["state"] in ("queued", "ready", "failed"):
                S.set_version(c, build, scene, r["n"], state="stale")
    return (f"v{n} of {scene} merged: {len(changed)} line{'s' * (len(changed) != 1)} changed" +
            (f"; {moved} recording{'s' * (moved != 1)} moved to the new timings" if moved else ""))


def _hash(b):
    import hashlib
    return hashlib.sha1((Path(b) / "presenter" / "lines.json").read_bytes()).hexdigest()[:12]


def discard(root, build, scene, n, c):
    """Delete a version's folder and mark it discarded. A merged one is part of the lecture; one being made waits."""
    row = S.version(c, build, scene, n)
    if row is None:
        raise KeyError("no such version")
    if row["state"] == "merged":
        raise ValueError("a merged version is part of the lecture: it cannot be discarded")
    if row["state"] in ("voicing", "rendering"):
        raise ValueError("it is being made: wait until it is ready")
    if c.execute("select 1 from jobs where build=? and kind='merge' and key=? and state in ('queued','running')",
                 (build, f"{scene}/v{n}")).fetchone():
        raise ValueError("it is being merged")
    shutil.rmtree(vdir(root, build, scene, n), ignore_errors=True)
    for parent in (vdir(root, build, scene, n).parent, Path(root) / build / "versions"):
        try:
            parent.rmdir()                                    # the scene's folder, then versions/: only if now empty
        except OSError:
            pass
    S.set_version(c, build, scene, n, state="discarded")


# ─── what the editor shows ───
def view(root, build, c):
    """{scene: [version, …]} for /api/project: texts, state, voice check, and for a version with a render its video
    and where each line of the scene starts in it (from the render's subtitles, grouped as presenter.py does)."""
    b = Path(root) / build
    rows = S.versions(c, build)
    if not rows:
        return {}
    ls = M.lines(b)
    names = [p.stem for p in RW.scene_files(b)]
    out = {}
    for r in rows:
        scene, n = r["scene"], r["n"]
        mp4 = scene_mp4(root, build, scene, n)
        v = {"n": n, "base": r["base"], "texts": r["texts"], "state": r["state"], "error": r["error"],
             "created": r["created"], "report": r["report"],
             "changed": sorted((k for k, t in r["texts"].items() if int(k) < len(ls) and N.norm(ls[int(k)][1]) != N.norm(t)), key=int),
             "video": None, "line_starts": {}}
        if r["state"] in ("ready", "stale", "merged") and mp4.exists() and scene in names and len(ls[0]) >= 4:
            sl = presenter.scene_lines(mp4.with_suffix(".srt"))
            mine = [k for k, l in enumerate(ls) if l[3] == names.index(scene)]
            v["line_starts"] = {str(k): round(sl[i][0], 3) for i, k in enumerate(mine) if i < len(sl)}
            v["video"] = f"/{build}/versions/{scene}/v{n}/media/videos/{RW.module_of(build)}/1080p60/{scene}.mp4" \
                         f"?v={int(mp4.stat().st_mtime)}"
        out.setdefault(scene, []).append(v)
    return out
