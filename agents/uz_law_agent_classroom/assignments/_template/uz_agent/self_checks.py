"""Self-checks for the Lecture N assignment. They run offline (a scripted fake model, recorded runs in traces/).

    python -m uz_agent.self_checks          one PASS / FAIL line per check, exit status 1 if any fails

A check marked @needs(...) exercises code the student writes; until then it fails with NotImplementedError. The
other checks test the code the student is given. tools/verify_assignment.py relies on exactly this split.
"""
import json
import sys
import traceback

from uz_agent import example


def needs(*todo_functions):
    """Mark a check as exercising these TODO functions."""
    def mark(fn):
        fn.needs = todo_functions
        return fn
    return mark


# ---- the code the student is given -----------------------------------------------------------------------------

def check_given_code_example() -> None:
    assert callable(example.double)


# ---- the code the student writes -------------------------------------------------------------------------------

@needs("double")
def check_double() -> None:
    assert example.double(3) == 6
    assert example.double(0) == 0


ALL_CHECKS = [
    check_given_code_example,
    check_double,
]


def run_all_checks(verbose=True):
    """Run every check; return [{"name", "needs", "status": "PASS" or "FAIL", "error", "message"}]."""
    results = []
    for fn in ALL_CHECKS:
        row = {"name": fn.__name__, "needs": list(getattr(fn, "needs", ())), "status": "PASS", "error": None,
               "message": ""}
        try:
            fn()
        except Exception as e:                     # a failing check is a result, not a crash
            row.update(status="FAIL", error=type(e).__name__, message=str(e) or traceback.format_exc(limit=-1))
        results.append(row)
        if verbose:
            detail = "" if row["status"] == "PASS" else f"  {row['error']}: {row['message'].splitlines()[0] if row['message'] else ''}"
            print(f"{row['status']}  {row['name']}{detail}")
    if verbose:
        failed = [r for r in results if r["status"] == "FAIL"]
        print(f"\n{len(results) - len(failed)} of {len(results)} checks passed." if failed
              else f"\nAll {len(results)} self-checks passed.")
    return results


if __name__ == "__main__":
    as_json = "--json" in sys.argv
    outcome = run_all_checks(verbose=not as_json)
    if as_json:
        print(json.dumps(outcome))
    sys.exit(1 if any(r["status"] == "FAIL" for r in outcome) else 0)
