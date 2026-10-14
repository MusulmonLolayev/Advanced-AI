# Agent course — code

The course's testbed is **τ²-bench** (Sierra Research, MIT; pinned at tag `v1.0.1`): simulated customers talk to
an agent that must follow a written policy and use tools on a database; a run is graded by the database it leaves
behind. We use its **retail** domain (16 tools, 500 users, 1,000 orders) and its **banking_knowledge** domain
(the same idea plus a document knowledge base to search).

## Two examples that run (DeepSeek, OpenAI-compatible API)

| file | idea | captured run |
|---|---|---|
| `s1_agent_loop.py` | the loop: model → tool call → result → … → answer, with a step limit | `raw/s1_agent_loop.json`, and `raw/s1_agent_loop_vague.json` (same loop with a vague tool description: the model dropped the `#` from the order id three times) |
| `s2_structured.py` | a JSON-Schema tool, validated in code, errors sent back for a retry | `raw/s2_structured.json`, and `raw/s2_structured_unhelpful.json` (the error named the problem but not the valid ids: three failed tries) |

Both read τ²-bench's retail `db.json`, so clone it first (see below). Then:

```bash
cp .env.example .env    # or create .env with DEEPSEEK_API_KEY=...  (never commit it)
uv run python s1_agent_loop.py            # add --capture to save the run in ../raw/
uv run python s2_structured.py
```

## Idea snippets (not run — read them)

`s3_memory.py` (summarise to a budget; an external note store) · `s4_orchestrator.py` (orchestrator, worker,
verifier, human fallback) · `s5_rag_hybrid.py` (BM25 + dense fused by reciprocal rank fusion, then rerank, answer
with citations) · `s6_vector_index.py` (HNSW in FAISS, the `efSearch` knob) · `s7_eval_harness.py` (grade the end
state; pass^k) · `s8_injection_defence.py` (tool text is data; writes need confirmation, enforced in code).

## The testbed runs

```bash
git clone --branch v1.0.1 https://github.com/sierra-research/tau2-bench ../tau2-bench
cd ../tau2-bench && uv sync --extra knowledge
echo "DEEPSEEK_API_KEY=..." > .env
M=deepseek/deepseek-v4-flash
uv run python ../run_tau2.py run --domain retail --agent-llm $M --user-llm $M --num-trials 3 --num-tasks 10 --save-to retail10x3
uv run tau2 run --domain banking_knowledge --retrieval-config bm25 --agent-llm $M --user-llm $M --num-tasks 5 --save-to banking5_bm25
cd .. && python3 capture_tau2.py && python3 -m unittest test_tau2
```

`run_tau2.py` exists because τ²-bench judges some tasks with `gpt-4.1` and has no flag to change it; it switches the
judge to DeepSeek, so our scores are not comparable with the public leaderboard. `--retrieval-config bm25` is the
offline option; the dense-embedding configs need an OpenAI or OpenRouter key (DeepSeek has no embeddings API).
