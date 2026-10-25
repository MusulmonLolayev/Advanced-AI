# Contributing

## Commits

Make small commits, one change each. The message says what changed and why ("Chunk articles at 500 characters so a
search hit points to a passage"), not only the file names. Do not mix a refactor with a new feature.

## Steps and tags

Each lecture is a step. When a step is finished, the maintainers tag it with an annotated tag
`step-NN-<name>`:

| Tag | State |
|---|---|
| `step-01-react-loop` | the starting state: the ReAct loop over the starter corpus (the Labor Code) |
| `step-02-structured-output` | tool schemas and structured output |
| `step-03-memory` | memory |
| `step-04-verifier` | verifier subagent |
| `step-05-chunking` | chunking |
| `step-06-retrieval` | BM25 and embeddings |
| `step-07-ann-index` | ANN index |
| `step-08-evaluation` | evaluation harness and injection test |

In your own fork, tag the end of each of your steps the same way (`git tag -a step-02-structured-output -m "..."`),
so you can return to it.

```bash
git tag -n                          # list the steps
git diff step-01-react-loop         # what changed since a step
git checkout step-01-react-loop     # go back to it (git switch - to return)
```

## Pull requests

Only your own folder: a pull request may change files under `assignments/<your-github-username>/` and nothing else
(maintainers are listed in `MAINTAINERS`). The `pr-scope` workflow checks this; run it yourself with
`python scripts/check_pr_scope.py origin/main <your-github-username>`. Never commit a key: `.env` is git-ignored and
`test_no_secrets.py` fails on one.

## Tests

```bash
uv sync
uv run python -m unittest discover -v
```

Offline, no key. Every number you quote comes from a script and has a test that recomputes it from the raw data.
