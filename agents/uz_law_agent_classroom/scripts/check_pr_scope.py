"""Fail a pull request that changes anything outside its author's folder, assignments/<author>/.

    python scripts/check_pr_scope.py origin/main alice          # base ref, PR author
    PR_AUTHOR=alice python scripts/check_pr_scope.py origin/main

Maintainers listed in MAINTAINERS (one username per line, # comments allowed) may change anything.
"""
import os
import posixpath
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_maintainers(text):
    """Usernames, lower-cased, from a MAINTAINERS file."""
    lines = (line.split("#", 1)[0].strip() for line in text.splitlines())
    return {line.lower() for line in lines if line}


def outside_scope(paths, author, maintainers=()):
    """The changed paths the author may not touch (empty list: the pull request is fine).

    A path is allowed only if, once normalised, it is a file inside assignments/<author>/ (the folder name is
    compared case-insensitively). `..` is resolved first, so assignments/alice/../bob/x is bob's file.
    """
    if author.lower() in {m.lower() for m in maintainers}:
        return []
    bad = []
    for path in paths:
        parts = posixpath.normpath(path).split("/")
        ok = (len(parts) >= 3 and parts[0] == "assignments" and parts[1].lower() == author.lower()
              and ".." not in parts and not path.startswith("/"))
        if not ok:
            bad.append(path)
    return bad


def changed_files(base):
    out = subprocess.run(["git", "diff", "--name-only", "-z", f"{base}...HEAD"], cwd=ROOT, capture_output=True,
                         check=True).stdout
    return [p for p in out.decode().split("\0") if p]


def main(argv):
    if not argv or not (len(argv) > 1 or os.environ.get("PR_AUTHOR")):
        sys.exit("usage: check_pr_scope.py BASE_REF [AUTHOR]   (or set PR_AUTHOR)")
    base, author = argv[0], argv[1] if len(argv) > 1 else os.environ["PR_AUTHOR"]
    maintainers_file = ROOT / "MAINTAINERS"
    maintainers = read_maintainers(maintainers_file.read_text()) if maintainers_file.exists() else set()
    paths = changed_files(base)
    bad = outside_scope(paths, author, maintainers)
    if bad:
        print(f"{author} may change only files under assignments/{author}/. Outside it:")
        print("\n".join(f"  {p}" for p in bad))
        return 1
    print(f"ok: {len(paths)} changed file(s), all allowed for {author}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
