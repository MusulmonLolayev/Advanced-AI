"""Does a lecture video in a language carry the draft watermark, or may it not be built at all?

The studio keeps who approved which narration line and screen label (studio/linestatus.py, out/studio.sqlite). A video
is clean when every line and every label of its language is approved. Until then:
  draft    any language but Uzbek: the video is built, every frame carries the "DRAFT" tag (m7_lecture01_kit.Scene7)
  refused  Uzbek: the instructor approves every Uzbek line before it is voiced or built (repo-root CLAUDE.md), so the
           studio's build job refuses; a hand render (render.sh) still tags the frames, as it always has
"""
import os
from pathlib import Path

HERE = Path(__file__).parent


def db_path():
    return Path(os.environ.get("STUDIO_DB", Path(os.environ.get("STUDIO_ROOT", HERE / "out")) / "studio.sqlite"))


def own_lines():
    """{line key: text} the instructor wrote in the studio for this render (env DRAFT_OWN_LINES, JSON), set by
    studio/versions.py build_version: a rewrite in the studio is the instructor's own text, which counts as approved
    (as "save edit" does). Bad or missing JSON: none."""
    import json
    try:
        d = json.loads(os.environ.get("DRAFT_OWN_LINES") or "{}")
        return {str(k): str(t) for k, t in d.items()} if isinstance(d, dict) else {}
    except ValueError:
        return {}


def unapproved(stem, lang, c=None, narration_dir=None, own=None):
    """What stands in the way of a clean video: {"lines": n, "labels": n, "total": n} of the items not approved (an
    empty or changed item counts), from the database `c`, or the studio's file (none there: everything counts).
    "total" is the number of ALL items, approved ones included; the unapproved count is lines + labels.
    `own` ({line key: text}): lines whose text in the narration is exactly this count as approved, nothing else."""
    from studio import linestatus as LS
    from studio import store as S
    if c is None:
        c = S.connect(db_path() if db_path().exists() else ":memory:")
    by_line = LS.line_texts(stem, narration_dir)
    sts = LS.statuses(c, stem, lang, "line", by_line)
    for k, t in (own or {}).items():
        if k in sts and sts[k]["state"] != "empty" and LS.N.norm(by_line.get(lang, {}).get(k, "")) == LS.N.norm(t):
            sts[k] = {"state": "approved", "changed": {}}
    lines = LS.counts(sts)
    labels = LS.counts(LS.label_statuses(c, stem, lang)[2])
    return {"lines": lines["total"] - lines["approved"] if lang in by_line else 1,    # no narration at all: not clean
            "labels": labels["total"] - labels["approved"], "total": lines["total"] + labels["total"]}


def decision(stem, lang, c=None, narration_dir=None, own=None):
    """"clean", "draft" or "refused" (see the module docstring)."""
    u = unapproved(stem, lang, c, narration_dir, own)
    if not u["lines"] and not u["labels"]:
        return "clean"
    return "refused" if lang == "uz" else "draft"


def tagged(stem, lang):
    """Whether a render shows the draft tag: anything but a clean video (a refused one is tagged in a hand render)."""
    try:
        return decision(stem, lang, narration_dir=os.environ.get("NARRATION_DIR"), own=own_lines()) != "clean"
    except Exception:                # no database, a locked one: unknown, so tagged
        return True
