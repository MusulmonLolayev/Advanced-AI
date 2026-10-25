# Assignments

One assignment per lecture of Module 7 (the roadmap and the acceptance criteria are in [`../STEPS.md`](../STEPS.md)).
Each is a small self-contained folder in the style of the Stanford CS231n assignments: a Python package in which
the parts the student must write are empty `TODO` blocks with a task description and hints, a handout, a notebook,
self-checks that run offline, and a script that zips the submission. There is no shared package between lectures; a
folder is copied and specialised, like the `ml/assignments/` labs.

| Lecture | Topic | Folder | Status |
|---|---|---|---|
| 1 | ReAct loop | `lecture01_react_loop/` | done |
| 2 | Tool schemas and structured output | | to be built from the same structure |
| 3 | Memory | | to be built from the same structure |
| 4 | Verifier subagent | | to be built from the same structure |
| 5 | Chunking | | to be built from the same structure |
| 6 | BM25 and embeddings | | to be built from the same structure |
| 7 | ANN index | | to be built from the same structure |
| 8 | Evaluation and injection test | | to be built from the same structure |

`_template/` is the empty skeleton of that layout.

## The layout of a folder

```
lectureNN_<topic>/
  README.md                the handout: goal, tasks Q1..Qn, setup, how to check, what to submit
  .env.example  .gitignore  requirements.txt  collectSubmission.sh
  uz_agent/                the package: config.py, llm.py and the lecture's modules; self_checks.py
  data/                    a small pinned data sample + SOURCE.md (source, licence, sha256, count)
  traces/                  recorded model runs, for offline replay
  lectureNN_<topic>.ipynb  a walk-through notebook, stored without outputs
```

## Conventions

- **TODO blocks.** A banner (`# TODO:` with the task, inputs, outputs, required behaviour, hints and pitfalls),
  then the two marker lines `# *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****` and
  `# *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****`. The student version holds only
  `raise NotImplementedError("TODO: <function>")` between them, so an unfinished task fails loudly. The banner
  describes the task; it contains no solution lines, no pseudo-code of the algorithm and no near-copy of the answer.
- **Self-checks.** `python -m uz_agent.self_checks` prints PASS or FAIL per check and exits 1 on a failure. A check
  that exercises student code is marked `@needs("function", ...)`. The grader's visible checks are the same.
- **Offline by default.** Checks use a scripted fake model and recorded runs (`traces/`); a recorded run replays only
  if the student's prompts equal the recorded ones. Only cells and commands marked live need a key.
- **`.env`.** `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`; copied from `.env.example`, never committed or submitted.
- **Numbers.** Every number in a handout or notebook (counts, hashes, article ids, step counts) is computed by a script
  and asserted by a self-check or a tool test.
- **Language.** English only. Uzbek appears only verbatim in the legal data and in recorded traces.

## How the instructor builds a lecture

The working code is written once, in `solutions/lectureNN_<topic>/` (local only, git-ignored, never committed: the
repository is public). The student folder is generated from it:

```bash
# start a new lecture from the skeleton
cp -r assignments/_template solutions/lecture02_<topic>
# ... write the package, wrap each part to fill in the markers, add data, traces, notebook, handout ...

python3 tools/make_student.py solutions/lecture01_react_loop assignments/lecture01_react_loop --replace
python3 tools/verify_assignment.py lecture01_react_loop
python3 -m unittest tools/test_make_student.py
```

`make_student.py` copies the tree (skipping caches, `.venv`, `.env` and anything listed in the solution's
`.studentignore`) and blanks every marked block in the `.py` files. `verify_assignment.py` regenerates the student
folder, runs the self-checks on both versions (the solution must pass them all; the student version must fail exactly
the checks marked `@needs` with `NotImplementedError` and pass the others), looks for solution lines in the student
folder, and compares it with the committed `assignments/<name>/`.

Run these from `agents/uz_law_agent_classroom/`. Only the generated `assignments/<name>/` is committed.
