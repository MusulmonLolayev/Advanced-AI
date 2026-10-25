# uz-law-agent classroom material

This folder holds the classroom material that used to live in the public repository
[uz-law-agent](https://github.com/MusulmonLolayev/uz-law-agent) (an open-source research agent over Uzbek law). It was
moved here so that the public repository stays a general project. It comes from `uz-law-agent` at commit 64f5a9f (on GitHub) plus four local commits that were never pushed (the
ADDING_A_LAW.md guide, wording changes, docstrings and the optional-assignment stubs); where the stubs were newer,
they are the newer versions.

**It is not currently used.** Students submit nothing to a repository for now, so the pull-request flow below has no
active counterpart, and nothing here is wired into this repository's test runs or CI.

| File | What |
|---|---|
| `STEPS.md` | roadmap for Lectures 2-8: what the agent gains, acceptance criteria |
| `test_steps.py` | the acceptance criteria as skipped stub tests |
| `assignments/` | the per-lecture student assignments (CS231n style: TODO blocks) and `_template/`; see its `README.md` |
| `tools/` | `make_student.py` (solution to student folder), `verify_assignment.py`, `build_sample_articles.py` and their tests |
| `solutions/` | the instructor's working code; local only, git-ignored |
| `scripts/check_pr_scope.py`, `test_pr_scope.py`, `MAINTAINERS` | the PR-scope check: a student changes only `assignments/<username>/` |
| `github-workflows/pr-scope.yml` | the GitHub Actions workflow for that check (kept outside `.github/` so it is inactive here) |
| `corpus_uk.py`, `data/uk_working_time.jsonl`, `data/SOURCE_UK.md`, `data/build_uk_corpus.py`, `test_uk_example.py` | the optional UK example corpus (two UK laws, OGL v3.0) and its loader test (the `UKExampleCorpus` test from `test_agent.py`) |
| `CONTRIBUTING_students.md` | the old CONTRIBUTING.md (step tags, per-student folder, PR scope) |

## Running it

The files are meant to be dropped into a checkout of uz-law-agent at the same relative paths (the workflow goes to
`.github/workflows/pr-scope.yml`; `CONTRIBUTING_students.md` back to `CONTRIBUTING.md`). Of the tests:

- `test_steps.py`: all stubs are skipped; it runs anywhere.
- `test_uk_example.py`: needs only `corpus_uk.py` and the two `data/` UK files in the same layout; no other uz-law-agent file.
- `test_pr_scope.py`: needs `scripts/check_pr_scope.py` in the same layout; the unit tests use no git. Only the
  command line of `check_pr_scope.py` needs a git checkout with an `origin/main`, and the workflow needs GitHub.
- `STEPS.md` and the assignment texts refer to `agent.py`, `test_agent.py` and `agent.py --replay q2_under18`, which
  exist only in uz-law-agent.
