"""Build a lecture video in a language from the studio: the queued job behind a language row's "Build video" button.

What decides whether it may run (plan):
  - check_lang.preflight passes (font, narration lines, labels, screen-word dicts, cues);
  - drafts.decision is not "refused": Uzbek is built only when every line and label is approved (repo-root CLAUDE.md);
    any other language builds as a draft ("Build draft video") while something is unapproved, and its frames carry
    the draft tag (m7_lecture01_kit.Scene7, lecture_kit.LectureScene);
  - the lecture has no video in the language yet (a build with recordings is never rebuilt over).

The job (build_language), one step after another, each shown in the jobs list:
  render       render.sh <lecture> h with LANG_CODE (and VOICE_ENGINE=navoiy for Uzbek: the voice server must be up,
               the job starts it as a rewritten line does)
  join         join_parts.sh (render.sh joins too; this is the same step the editor's merge runs, so a hand-rendered
               scene folder joins the same way)
  presenter    presenter.py: the presenter page, line timings and subtitles the editor reads
  voice check  voice_check.py (Uzbek) or voice_check_lang.py (whisper, CER) -> voice_check.json; clips that fail do not
               fail the job: the editor shows them red
"""
import os
import time
from pathlib import Path

import builds as B
import check_lang as CL
import drafts as D
import languages as LG
from studio import media as M
from studio import rewrite as RW
from studio import voice_server

HERE = RW.HERE
VENV_PY = HERE / ".venv" / "bin" / "python"
STEPS = ("render", "join", "presenter", "voice check")


def build_name(stem, lang):
    """The build a language of a lecture is made into: Uzbek in the cloned voice, the others in edge-tts."""
    module, lecture = B.parse_stem(stem)
    return B.name(module, lecture, lang, "navoiy" if lang == "uz" else None)


def plan(c, root, stem, lang, narration_dir=None):
    """What the "Build video" button needs: {"build", "can", "draft", "problems": [...], "reasons": [...],
    "unapproved": {...}, "built"}. `problems` is check_lang's full list, `reasons` its short summary; `can` is false
    when the preflight fails, Uzbek has unapproved items, or the video already exists."""
    build = build_name(stem, lang)
    report = CL.preflight(stem, lang, narration_dir)
    reasons = CL.summary(report, lang)
    open_ = D.unapproved(stem, lang, c, narration_dir)
    state = "clean" if not (open_["lines"] or open_["labels"]) else "refused" if lang == "uz" else "draft"
    built = (Path(root) / build / f"{build}.mp4").exists()
    if state == "refused":
        left = open_["lines"] + open_["labels"]
        reasons.append(f"Uzbek is built only when every line and label is approved ({left} left)")
    return {"build": build, "can": not reasons and not built, "draft": state == "draft", "approval": state,
            "problems": CL.problems(report), "reasons": reasons, "unapproved": open_, "built": built}


def steps(root, build):
    """[(name, argv, env)] of the job: pure, so the tests read it without running anything."""
    stem, lang, engine = B.stem(build), B.lang(build), B.engine(build)
    b = Path(root) / build
    env = RW.render_env(build)
    if engine != "navoiy":
        env["JOBS"] = "3"                                   # edge-tts takes parallel requests; the cloned voice does not
    check = [str(M.NAVOIY_PY), "voice_check.py", str(b)] if lang == "uz" else \
            [str(M.NAVOIY_PY), "voice_check_lang.py", lang, str(b)]
    rel = lambda p: os.path.relpath(p, HERE)                # join_parts.sh prefixes $PWD
    return [("render", ["./render.sh", stem, "h"], env),
            ("join", ["./join_parts.sh", rel(b), rel(b / f"{build}.mp4")], None),
            ("presenter", [str(VENV_PY), "presenter.py", str(b)], None),
            ("voice check", check, None)]


def build_language(root, stem, lang, connect, progress=print, run=RW.run, narration_dir=None, server=voice_server):
    """Run the job. `run(cmd, env, what)` runs a command (tests stub it). Returns a one-line report."""
    with connect() as c:
        p = plan(c, root, stem, lang, narration_dir)
    if p["built"]:
        raise ValueError(f"{p['build']} is already built: it has recordings and edits that a rebuild would orphan")
    if not p["can"]:
        raise ValueError("cannot build: " + "; ".join(p["reasons"] or p["problems"]))
    build = p["build"]
    todo = steps(root, build)
    if B.engine(build) == "navoiy" and not server.up():
        progress("starting the voice server (about a minute)")
        server.start()
    note = ""
    for i, (name, argv, env) in enumerate(todo, 1):
        progress(f"step {i} of {len(todo)}: {name}" + (" (a draft: lines or labels are not approved)" if name == "render" and p["draft"] else ""))
        t0 = time.time()
        try:
            run(argv, env=env, what=name)
        except RuntimeError as e:
            report = Path(root) / build / "voice_check.json"
            if name != "voice check" or not (report.exists() and report.stat().st_mtime >= t0 - 2):
                raise
            note = "; some clips failed the voice check (red in the editor)"
    if not (Path(root) / build / f"{build}.mp4").exists():
        raise RuntimeError(f"the build left no {build}.mp4")
    return f"{build} built" + ("; a draft" if p["draft"] else "") + note
