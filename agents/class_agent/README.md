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

Files: `corpus.py` (the articles and the two tools), `llm.py` (DeepSeek, or record / replay), `agent.py` (the loop),
`traces/` (recorded runs), `test_class_agent.py` (every fact the slides and session plans quote).
