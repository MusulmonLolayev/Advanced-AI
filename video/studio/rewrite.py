"""The outside-tool helpers a rewritten scene needs, shared by studio/versions.py (a rewrite is a draft version first,
and an explicit merge):

  - which commands render a build's scene (render_env), which scene a line belongs to (scene_of), how a command is
    run (run), and how recordings made against the old line list are moved onto the new one (migrate:
    timeline.remap_events; the old events are kept as <name>.json.<old hash>)
"""
import json
import os
import subprocess
from pathlib import Path

from studio import media as M
from studio import narration_edit as N
from studio import store as S
from studio import timeline as T

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


def scene_files(build_dir):
    """The scene mp4 paths in the order of out/<build>/parts.txt."""
    return [Path(r.split("'")[1]) for r in (Path(build_dir) / "parts.txt").read_text().splitlines() if r.startswith("file")]


def scene_of(build_dir, line):
    if len(M.lines(build_dir)[line]) < 4:
        raise ValueError("this presenter page is older than the editor: press 'Refresh page' in the studio first")
    return scene_files(build_dir)[M.lines(build_dir)[line][3]].stem


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
