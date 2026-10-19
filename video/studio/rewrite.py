"""Rewrite (or just re-voice) one narration line of a built lecture, from the editor:

  1. the new text goes into the narration file (narration_edit; the instructor's edit is their approval)
  2. the cloned voice says it: several seeds per sentence, each take judged by two recognisers, the best kept and
     put in the scene's voice cache (revoice_line.py, Navoiy env); an English build's synthetic voice simply
     voices the new text during the render
  3. only that line's scene is rendered again (render.sh with ONLY=<scene>), and the lecture video joined again
     (join_parts.sh; the previous video is kept as <build>.before_rewrite.mp4)
  4. the presenter page is prepared again (presenter.py), and every recording made against the old line list is
     moved onto the new one (timeline.remap_events; the old events are kept as <name>.json.<old hash>)
If a step fails after the text was saved, the old text is put back, so the narration never disagrees with the video.
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from studio import media as M
from studio import narration_edit as N
from studio import store as S
from studio import timeline as T
from studio import voice_server

HERE = Path(__file__).resolve().parents[1]


def module_of(build):
    """The video module a build renders: lecture01_uz_navoiy -> lecture01, m7_lecture01_en -> m7_lecture01."""
    return build.rsplit("_uz_navoiy", 1)[0] if build.endswith("_uz_navoiy") else build.rsplit("_en", 1)[0]


def render_env(build):
    env = dict(os.environ, JOBS="1")
    m = N.BUILD.fullmatch(build)
    if build.endswith("_uz_navoiy"):
        env.update(LANG_CODE="uz", VOICE_ENGINE="navoiy")
    else:
        env["LANG_CODE"] = "en"
        env.pop("VOICE_ENGINE", None)
    drafts = HERE / "narration" / "drafts" / (f"m{m[1]}_l{m[2]}" if m[1] else f"l{m[2]}")
    if drafts.is_dir():
        env["LABEL_DRAFTS"] = str(drafts.relative_to(HERE))
    return env


def scene_of(build_dir, line):
    if len(M.lines(build_dir)[line]) < 4:
        raise ValueError("this presenter page is older than the editor: press 'Refresh page' in the studio first")
    parts = [Path(r.split("'")[1]).stem for r in (Path(build_dir) / "parts.txt").read_text().splitlines()
             if r.startswith("file")]
    return parts[M.lines(build_dir)[line][3]]


def run(cmd, env=None, what=""):
    r = subprocess.run(cmd, cwd=HERE, env=env, capture_output=True, text=True)
    if r.returncode:
        tail = (r.stdout + r.stderr).strip().splitlines()
        raise RuntimeError(f"{what} failed: " + " | ".join(tail[-3:]))
    return r.stdout


def migrate(root, build, conn, old_lines, old_end, new_lines, new_end, old_hash, new_hash):
    """Move every session recorded against the old line list onto the new one."""
    b = Path(root) / build
    moved = 0
    for s in S.sessions(conn, build):
        if s["lines_hash"] != old_hash:
            continue
        p = M.recdir(b) / f"{s['name']}.json"
        if p.exists():
            ev = json.loads(p.read_text())
            p.with_name(p.name + f".{old_hash}").write_text(json.dumps(ev))
            p.write_text(json.dumps(T.remap_events(ev, [l[0] for l in old_lines], old_end,
                                                   [l[0] for l in new_lines], new_end)))
        S.set_session(conn, build, s["name"], lines_hash=new_hash)
        moved += 1
    return moved


def rewrite(root, build, line, new_text, connect, progress=print, python=M.NAVOIY_PY):
    """Returns a one-line report. `connect()` opens the studio database; `progress(text)` reports each step."""
    b = Path(root) / build
    ls = M.lines(b)
    old_text = ls[line][1]
    scene = scene_of(b, line)
    path, lang, single = N.source(build)
    navoiy = build.endswith("_uz_navoiy")
    text, changed = old_text, False
    if new_text is not None and N.norm(new_text) != N.norm(old_text):
        progress("saving the new text")
        _, text = N.rewrite(path, lang, single, old_text, new_text)
        changed = True
    report = ""
    try:
        if navoiy:
            if not voice_server.up():
                progress("starting the voice server (about a minute)")
                voice_server.start()
            progress("voicing the line: several takes per sentence, each checked by two recognisers")
            with tempfile.TemporaryDirectory() as tmp:
                job = Path(tmp) / "job.json"
                job.write_text(json.dumps({"build": str(b), "cache_dir": str(b / "media" / "voiceovers" / scene),
                                           "text": text, "report": str(Path(tmp) / "report.json")}, ensure_ascii=False))
                run([str(python), str(HERE / "studio" / "revoice_line.py"), str(job)], what="voicing")
                r = json.loads((Path(tmp) / "report.json").read_text())
            report = (f"kept the {'new' if r['kept'] == 'new' else 'old (it scored better)'} take; check: "
                      + ("passes" if r["ok"] else "fails " + ", ".join(r["fails"])) + (" (listen)" if r["listen"] else ""))
        progress(f"rendering {scene}")
        run(["./render.sh", module_of(build), "h"], env=dict(render_env(build), ONLY=scene), what=f"render {scene}")
        progress("joining the lecture video")
        final, backup = b / f"{build}.mp4", b / f"{build}.before_rewrite.mp4"
        if final.exists():
            shutil.copy2(final, backup)
        try:
            run(["./join_parts.sh", os.path.relpath(b, HERE), os.path.relpath(final, HERE)], what="join")  # it prefixes $PWD
        except Exception:
            if backup.exists():
                shutil.copy2(backup, final)            # the lecture keeps a whole video
            raise
    except Exception:
        if changed:                                   # the video still says the old text: so must the narration
            N.rewrite(path, lang, single, text, old_text)
        raise
    progress("preparing the presenter page")
    old_hash = hashlib.sha1((b / "presenter" / "lines.json").read_bytes()).hexdigest()[:12]
    old_end = M.video_end(b)
    run([str(HERE / ".venv" / "bin" / "python"), "presenter.py", str(b)], what="presenter page")
    new_lines = M.lines(b)
    new_hash = hashlib.sha1((b / "presenter" / "lines.json").read_bytes()).hexdigest()[:12]
    moved = 0
    if len(new_lines) == len(ls):
        with connect() as c:
            moved = migrate(root, build, c, ls, old_end, new_lines, M.video_end(b), old_hash, new_hash)
    what = "rewritten" if changed else "re-voiced"
    return f"line {line + 1} {what} in {scene}" + (f"; {report}" if report else "") + \
        (f"; {moved} recording{'s' * (moved != 1)} moved to the new timings" if moved else "")
