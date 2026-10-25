"""Turn an instructor solution folder into a student folder.

    python tools/make_student.py SOLUTION_DIR STUDENT_DIR [--replace]

The solution is written once, with each part the student must fill wrapped in the CS231n markers:

    ##########################################################################
    # TODO: ... what to do, hints ...                                        #
    ##########################################################################
    # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
    <solution lines>
    # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

The copy keeps the banner and both marker lines, drops the solution lines, and puts one line at the marker's
indentation in their place:  raise NotImplementedError("TODO: <function name>")  so an unfinished assignment fails
loudly instead of silently passing. Only .py files are scanned for markers (a handout may quote them in prose).

Skipped when copying: __pycache__, .venv, .env, *.pyc, and anything listed in the solution's `.studentignore`
(one glob per line, matched against the path relative to the solution; `#` starts a comment). Running it again on
the same input gives the same output (--replace is needed to overwrite an existing STUDENT_DIR).
"""
import argparse
import fnmatch
import re
import shutil
import sys
from pathlib import Path

START = "# *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****"
END = "# *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****"
IGNORE_FILE = ".studentignore"
ALWAYS_SKIP = ["__pycache__", ".venv", ".env", "*.pyc", ".git", IGNORE_FILE]
DEF = re.compile(r"^(\s*)(?:async\s+)?def\s+(\w+)")


class MarkerError(ValueError):
    """Unbalanced, nested or stray markers in a solution file."""


def enclosing_function(lines, start_index):
    """Name of the function the block at lines[start_index] sits in: the nearest earlier `def` that is indented
    less than the marker. Falls back to the module for a block outside any function."""
    indent = len(lines[start_index]) - len(lines[start_index].lstrip())
    for j in range(start_index - 1, -1, -1):
        m = DEF.match(lines[j])
        if m and len(m.group(1)) < indent:
            return m.group(2)
    return "module"


def blank_blocks(text, where="<text>"):
    """The student version of one source text (the markers are matched on whole lines, ignoring indentation)."""
    lines = text.split("\n")
    out, inside, start_at = [], False, None
    for i, line in enumerate(lines):
        s = line.strip()
        if s == START:
            if inside:
                raise MarkerError(f"{where}:{i + 1}: START inside the block opened at line {start_at + 1} (nested)")
            inside, start_at = True, i
            out.append(line)
            indent = line[: len(line) - len(line.lstrip())]
            out.append(f'{indent}raise NotImplementedError("TODO: {enclosing_function(lines, i)}")')
        elif s == END:
            if not inside:
                raise MarkerError(f"{where}:{i + 1}: END without a START")
            inside = False
            out.append(line)
        elif not inside:
            out.append(line)
    if inside:
        raise MarkerError(f"{where}:{start_at + 1}: START never closed")
    return "\n".join(out)


def solution_lines(text):
    """The lines inside the blocks, for the leak check: [(function name, line)]."""
    lines, found, inside, name = text.split("\n"), [], False, None
    for i, line in enumerate(lines):
        s = line.strip()
        if s == START:
            inside, name = True, enclosing_function(lines, i)
        elif s == END:
            inside = False
        elif inside:
            found.append((name, line))
    return found


def skipped(rel, patterns):
    parts = rel.parts
    for pat in ALWAYS_SKIP + patterns:
        if any(fnmatch.fnmatch(p, pat) for p in parts) or fnmatch.fnmatch(rel.as_posix(), pat):
            return True
    return False


def make_student(solution, student, replace=False):
    solution, student = Path(solution).resolve(), Path(student).resolve()
    if not solution.is_dir():
        raise SystemExit(f"no such solution folder: {solution}")
    if student == solution or solution in student.parents or student in solution.parents:
        raise SystemExit("the student folder must be separate from the solution folder")
    if student.exists():
        if not replace:
            raise SystemExit(f"{student} exists; pass --replace to overwrite it")
        shutil.rmtree(student)
    ignore_file = solution / IGNORE_FILE
    patterns = [l.strip() for l in ignore_file.read_text().splitlines()
                if l.strip() and not l.lstrip().startswith("#")] if ignore_file.exists() else []
    blocks = 0
    for path in sorted(solution.rglob("*")):
        rel = path.relative_to(solution)
        if path.is_dir() or skipped(rel, patterns):
            continue
        target = student / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".py":
            text = path.read_text(encoding="utf-8")
            new = blank_blocks(text, str(rel))
            blocks += sum(1 for l in text.split("\n") if l.strip() == START)
            target.write_text(new, encoding="utf-8")
            shutil.copymode(path, target)
        else:
            shutil.copy2(path, target)
    return blocks


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution")
    ap.add_argument("student")
    ap.add_argument("--replace", action="store_true", help="overwrite STUDENT_DIR if it exists")
    a = ap.parse_args()
    try:
        n = make_student(a.solution, a.student, a.replace)
    except MarkerError as e:
        sys.exit(f"make_student: {e}")
    print(f"{a.student}: written, {n} block(s) blanked")


if __name__ == "__main__":
    main()
