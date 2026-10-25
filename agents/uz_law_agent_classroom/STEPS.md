# Roadmap: Lectures 2-8

The agent is an open-source research agent over Uzbek law, built step by step; its starter corpus, the Labor Code, is
the one used in the course videos and in the tests. Lecture 1 is done: the starting state, tag `step-01-react-loop`. Each later lecture adds one capability. A step is
finished when its acceptance checks hold; the same checks are skipped stub tests in `test_steps.py`, which say what
to build and contain no solution. Replace a stub with a real test when you build the step.

| Lecture | Topic | What the agent gains | Acceptance criteria (concrete checks) |
|---|---|---|---|
| 1 | ReAct loop | Thought / Action as text; `search`, `fetch_article`, `answer`; a step budget | Done. `python -m unittest test_agent` passes; `python agent.py --replay q2_under18` runs offline. |
| 2 | Tool schemas and structured output | Tools declared with JSON schemas; the model returns a structured tool call instead of text we parse | Every tool has a JSON schema with typed arguments. A malformed call (missing or wrongly typed argument) returns an error observation and does not raise. The final answer is a structured object `{answer, citations}` where every citation is an existing article id. The regex parser for `Action:` is gone. |
| 3 | Memory | The agent keeps what it learned across turns and across questions | A follow-up ("and for employees under 18?") is answered without re-reading what the first turn already fetched: the second run makes fewer tool calls than a fresh run. Memory is bounded (a configurable limit) and the oldest items go first. Memory can be saved to and loaded from a file. |
| 4 | Verifier subagent | A second model call checks the draft answer against the cited articles | For each citation, the verifier receives the cited article text and the claim and returns `supported` or `unsupported`. An answer with an unsupported citation is revised or flagged, never returned as is. A test shows a wrong citation being caught (use a scripted model, as in `test_agent.py`). |
| 5 | Chunking | Articles are split into chunks that keep their article id and position | Concatenating the chunks of an article gives back its text. Every chunk has a maximum size and carries `article_id` and `chunk_index`. No chunk is empty. Search results can point to a chunk, not only an article. |
| 6 | BM25 and embeddings | Real retrieval: BM25 over chunks, embeddings, and a hybrid ranking | `search` keeps its interface. On a small set of labelled questions (at least 10, written by you), the correct article is in the top 5 more often than with the Lecture 1 word-count search; the test prints both rates. Keyboard apostrophes (`o'n`) and the corpus's `oʻn` still match. |
| 7 | ANN index | An approximate nearest-neighbour index for the embeddings | The index returns, for 20 test queries, at least 90 % of the neighbours an exact search returns (recall@10), and the test measures it. Building the index is separate from querying it, and the index can be saved and reloaded. |
| 8 | Evaluation and injection test | An evaluation harness and a prompt-injection test | `python evaluate.py` runs every labelled question and prints, per question and in total: answer correct, citation correct, steps used. A planted instruction inside an article ("ignore previous instructions ...") does not change the answer or trigger a tool call the user did not ask for; the test shows the planted text, the agent's run, and the pass or fail. Results are reproducible offline from recorded runs. |

## Optional: port the agent to the UK corpus (English)

`corpus_uk.py` and `data/uk_working_time.jsonl` (the Working Time Regulations 1998 and the National Minimum Wage
Act 1998, Open Government Licence; see `data/SOURCE_UK.md`) are an example corpus. The repository ships no English
agent: building one is an optional assignment, done in your own folder. Acceptance criteria:

- The agent runs over `corpus_uk` with its own system prompt, tool names and citation format (`[WTR 4]`), without
  changing the Uzbek agent's behaviour: `python -m unittest discover` stays green.
- "What is the maximum weekly working time?" is answered with `WTR 4` cited, and the cited text contains the
  48-hour average that a test asserts from the file.
- "What is the national minimum wage per hour, in pounds?" is answered with "the corpus does not state an amount"
  (no figure appears in any provision), citing `NMWA 1`.
- At least two runs are recorded and replay offline, with a test asserting each fact the answer quotes.

## Optional: add another Uzbek law as a corpus

The agent is meant for Uzbek law in general; today it is wired to the starter corpus, the Labor Code. Following
[docs/ADDING_A_LAW.md](docs/ADDING_A_LAW.md), add one more law, in your own folder. Acceptance criteria:

- The law's text may be reused, and `SOURCE_<name>.md` says so: URL, date retrieved, licence or legal basis, and the
  sha256 of the data file. A test checks that the file's hash appears in the note.
- The data file has one JSON object per line with the fields the loader needs (`article_id`, `title`, `text`), unique
  ids, and no empty text. A test recomputes the record count from the file.
- A loader module provides `search(query, k)` and `fetch_article(ref)` with the interface of `corpus.py`; a test
  finds a known article by a query and fetches its text, and a missing id returns `None`.
- The agent runs over your corpus with its own prompt and citation format, without changing the Labor Code agent:
  `python -m unittest discover` stays green.
- At least one run is recorded and replays offline, with a test asserting each fact the answer quotes.

## Conventions

- One change per commit; tag the end of each step `step-0N-<name>` (see `CONTRIBUTING.md`).
- Do not break the earlier steps: `python -m unittest discover` stays green, with only the later steps skipped.
- Every number you quote in your notes comes from a script and has a test.
