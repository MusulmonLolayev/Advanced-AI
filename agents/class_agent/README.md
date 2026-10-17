# The class agent

The agent we build together in Module 7, one step per lecture, over the Labor Code of Uzbekistan (581 articles,
`data/`, CC0; see `data/SOURCE.md`). Each lecture's session plan is in `sessions/`.

| Lecture | What the agent gains | Status |
|---|---|---|
| 1 | a ReAct loop: Thought / Action as text, three actions (`search`, `fetch_article`, `answer`), a step budget | done |
| 2 | tool schemas and structured output instead of parsing text | |
| 3 | memory | |
| 4 | a verifier subagent | |
| 5–7 | real retrieval: chunking, BM25 and embeddings, an ANN index | |
| 8 | an evaluation harness and an injection test | |

```bash
uv sync
uv run python agent.py --replay q2_under18                 # a recorded run: no key, no network
echo "DEEPSEEK_API_KEY=..." > .env                   # git-ignored; for live runs
uv run python agent.py "How many days of annual leave does an employee get?"
uv run python agent.py --record NAME "question"             # run live and save it to traces/NAME.json
uv run python -m unittest test_class_agent                  # no network
```

**English version:** the same agent over two UK laws on work, the Working Time Regulations 1998 and the National
Minimum Wage Act 1998 (118 provisions, `data/uk_working_time.jsonl`, Open Government Licence; see
`data/SOURCE_UK.md`). Add `--law uk`; its runs are in `traces/uk/`, under the same names as the Uzbek ones:

```bash
uv run python agent.py --law uk --replay q2_under18       # WTR 4 -> 5A -> the definition in WTR 2: 48 h average; 40 h under 18
uv run python agent.py --law uk --replay q3_min_wage      # the Act states no amount; s. 1(3) leaves it to a minister [NMWA 1]
```

Files: `corpus.py` (the articles and the two tools; `corpus_uk.py` for the UK laws), `llm.py` (DeepSeek, or record / replay), `agent.py` (the loop),
`traces/` (recorded runs), `test_class_agent.py` (every fact the slides and session plans quote).
