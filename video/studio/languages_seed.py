"""One-time seed of the approvals the instructor already gave: Module 0, Lectures 1-5, Uzbek (STATUS.md: approved,
built). Every Uzbek narration line of those lectures, and every label they show that has an Uzbek form, is approved with
its current text and the other languages' current texts. Idempotent: an item that already has an approval row is left
alone (so a line changed since, or approved again by hand, is not approved by a rerun). English (Module 0's gloss, Module 7's
draft 2) and Module 7's Uzbek are not touched.

    python -m studio.languages_seed [--db out/studio.sqlite] [--dry-run]            (from video/)
"""
import argparse
import os
import sys
from pathlib import Path

import builds as B
from studio import linestatus as LS
from studio import store as S

HERE = Path(__file__).resolve().parents[1]
LECTURES = [B.stem_of(0, n) for n in range(1, 6)]
LANG = "uz"


def seed(c, narration_dir=None, lectures=LECTURES, lang=LANG):
    """Approve what has no approval yet. Returns {(lecture, kind): [newly approved, already had a row, empty]}."""
    out = {}
    for stem in lectures:
        for kind in ("line", "label"):
            by_lang = LS.texts(stem, kind, narration_dir)
            have = S.approvals(c, stem, lang, kind)
            new = old = empty = 0
            for key, text in by_lang.get(lang, {}).items():
                if not text.strip():
                    empty += 1
                elif key in have:
                    old += 1
                else:
                    LS.approve(c, stem, lang, kind, key, by_lang)
                    new += 1
            out[(stem, kind)] = [new, old, empty]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", default=str(Path(os.environ.get("STUDIO_ROOT", HERE / "out")) / "studio.sqlite"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    c = S.connect(a.db)
    with c:
        report = seed(c)
        if a.dry_run:
            c.rollback()
    for (stem, kind), (new, old, empty) in report.items():
        print(f"{stem} uz {kind}s: {new} approved now, {old} already approved, {empty} empty")
    print(f"total: {sum(r[0] for r in report.values())} approved now ({a.db}{', dry run' if a.dry_run else ''})")


if __name__ == "__main__":
    main()
