"""Check an assignment before it goes to students.

    python tools/verify_assignment.py lecture01_react_loop          (a folder name under solutions/, or a path)

1. regenerates the student folder from the solution into a temporary directory (tools/make_student.py);
2. runs `python -m uz_agent.self_checks --json` in the SOLUTION: every check must pass;
3. runs it in the STUDENT version: every check marked @needs(...) must fail with NotImplementedError, every other
   check must pass; every TODO function must be exercised by at least one check;
4. leak check: no distinctive solution line appears anywhere in the student folder;
5. if assignments/<name>/ exists, it must equal the regenerated folder (the committed copy is up to date).

Prints a table and exits non-zero if anything is off.
"""
import filecmp
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import make_student as ms  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MIN_LEAK_LENGTH = 25            # shorter lines (`return None`) legitimately recur in given code


def run_checks(folder):
    p = subprocess.run([sys.executable, "-m", "uz_agent.self_checks", "--json"], cwd=folder,
                       capture_output=True, text=True, timeout=300)
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        raise SystemExit(f"self_checks in {folder} printed no result:\n{p.stdout}\n{p.stderr}")


def todo_functions(folder):
    found = set()
    for path in Path(folder).rglob("*.py"):
        found.update(re.findall(r'raise NotImplementedError\("TODO: (\w+)"\)', path.read_text(encoding="utf-8")))
    return found


def normalized(line):
    """A line without indentation and without the comment frame of a banner (`# text   #`)."""
    return line.strip().strip("#").strip()


def leaks(solution, student):
    """Distinctive solution lines found as whole lines in the student folder (also inside a banner or a
    docstring): [(function, line, file)]."""
    lines = {}
    for p in Path(student).rglob("*"):
        if p.is_file():
            for l in p.read_text(encoding="utf-8", errors="ignore").split("\n"):
                lines.setdefault(normalized(l), set()).add(str(p.relative_to(student)))
    found = []
    for path in Path(solution).rglob("*.py"):
        for name, line in ms.solution_lines(path.read_text(encoding="utf-8")):
            s = normalized(line)
            if len(s) >= MIN_LEAK_LENGTH and s in lines:
                found += [(name, line.strip(), where) for where in sorted(lines[s])]
    return found


def differences(a, b):
    """Paths that differ between two folders (ignoring caches)."""
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__", ".DS_Store"])
    out = [f"only in {a}: {n}" for n in cmp.left_only] + [f"only in {b}: {n}" for n in cmp.right_only]
    out += [f"differs: {n}" for n in cmp.diff_files]
    for sub in cmp.common_dirs:
        out += differences(Path(a) / sub, Path(b) / sub)
    return out


def main(argv):
    if len(argv) != 2:
        raise SystemExit(__doc__)
    arg = Path(argv[1])
    solution = (arg if arg.is_dir() else ROOT / "solutions" / argv[1]).resolve()
    if not solution.is_dir():
        raise SystemExit(f"no solution folder {solution}")
    name = solution.name
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        student = Path(tmp) / name
        ms.make_student(solution, student)
        sol_results, stu_results = run_checks(solution), run_checks(student)
        print(f"{'check':58} {'needs':40} {'solution':9} student")
        for s, t in zip(sol_results, stu_results):
            needs = bool(s["needs"])
            ok_sol = s["status"] == "PASS"
            ok_stu = (t["status"] == "FAIL" and t["error"] == "NotImplementedError") if needs else t["status"] == "PASS"
            expected = "NotImplementedError" if needs else "PASS"
            got = t["status"] if t["status"] == "PASS" else t["error"]
            print(f"{s['name']:58} {','.join(s['needs'])[:40]:40} {s['status']:9} {got}"
                  f"{'' if ok_stu else '   <-- expected ' + expected}")
            if not ok_sol:
                problems.append(f"solution fails {s['name']}: {s['error']}: {s['message']}")
            if not ok_stu:
                problems.append(f"student version of {s['name']}: expected {expected}, got {got}")
        covered = {f for r in sol_results for f in r["needs"]}
        for todo in sorted(todo_functions(student) - covered):
            problems.append(f"TODO {todo} is exercised by no check")
        for todo in sorted(covered - todo_functions(student)):
            problems.append(f"a check needs {todo}, which is not a TODO in the student folder")
        for fn, line, where in leaks(solution, student):
            problems.append(f"solution line of {fn} found in the student folder ({where}): {line}")
        committed = ROOT / "assignments" / name
        if solution.parent == ROOT / "assignments":
            print("\n(a template: no generated copy to compare)")
        elif committed.is_dir():
            diff = differences(student, committed)
            problems += [f"assignments/{name} is stale: {d}" for d in diff]
            print(f"\nassignments/{name}: {'up to date' if not diff else 'STALE'}")
        else:
            print(f"\nassignments/{name}: not generated yet")
        print(f"TODO functions: {', '.join(sorted(todo_functions(student)))}")
    if problems:
        print("\nPROBLEMS")
        print("\n".join(" - " + p for p in problems))
        return 1
    print("\nOK: the solution passes, the student version fails exactly where it should, no solution line leaked.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
