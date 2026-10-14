"""Capture every number the agent-course video speaks or shows that does not come from a live run.

Two sources, both computed rather than typed:
  * the Module 7 deck's worked examples (agents/lectures/*.tex) that are not tied to its legal corpus — the bill of a
    trajectory, prefix caching, p^k, the orchestration arithmetic, RRF, the index sizes, the confidence interval —
    recomputed from their raw inputs;
  * the testbed's own facts, read from the τ²-bench clone (video/agents_course/tau2-bench, MIT): how many tasks,
    tools, users and documents its retail and banking_knowledge domains have, and its pass^k formula.
A figure the deck quotes from a paper (DPR's 9-19 points) is kept as a quoted constant, and test_deck.py checks it
still appears in the deck text.

Numbers from the course code's live runs and from τ²-bench runs (video/agents_course/code/) are NOT here: the
narration leaves them as {{placeholders}} until those runs are captured.

`compute()` is pure. Running this file writes raw/deck_numbers.json, which the video reads.
    cd video && uv run python agents_course/capture_deck.py
    cd video && uv run python -m unittest discover -s agents_course -p 'test_deck.py'
"""
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
TAU2 = HERE / "tau2-bench"
RETAIL = TAU2 / "data/tau2/domains/retail"
BANKING = TAU2 / "data/tau2/domains/banking_knowledge"

# ─── raw inputs: the only typed numbers, all from the slides ───────────────
S, A = 1200, 500                     # L1: fixed prefix S and tokens added per step a
STEPS = (3, 10, 20)
PRICE_IN, PRICE_CACHED = 0.15, 0.003  # $ per million input tokens, DeepSeek off-peak (course map, 2026-09-24)
EVAL_QUERIES = 500
P_STEP = 0.95                        # L1: per-step success
P_STEP_LOW = 0.90                    # L1: "cutting ten steps to five at p = 0.90"
Q_FORMAT = 0.98                      # L2: one output is well-formed
SCHEMA_TOKENS = 400                  # L2: schema block
WINDOW, A_UNCAPPED, A_CAPPED = 32_000, 3_000, 500   # L3: context window, observation sizes
SINGLE_STEPS, SUBAGENTS, SUB_STEPS, ORCH_TURNS, A_HANDOFF = 12, 3, 4, 4, 800   # L4
DRAFT_OK, VERIFIER_CATCH = 0.80, 0.90                  # L4: drafter right, verifier catches a bad draft
RRF_K = 60                                             # L5
# L5's worked example (the deck's Art. 258 / 183 / 415 / 182), relabelled: the arithmetic does not depend on the corpus
RRF_LISTS = {"doc_a": (1, None), "doc_b": (2, 3), "doc_c": (3, 1), "doc_d": (4, 2)}
FIRST_STAGE = 50                                       # L5: candidates kept for reranking
BATCH = 64                                             # L6: in-batch negatives
D_EMB = 1024                                           # L7: BGE-M3 dimension, float32
IVF_N, IVF_NLIST, IVF_NPROBE = 10**6, 1_000, 8         # L7
PQ_M, PQ_CENTROIDS, PQ_N = 64, 256, 10**9              # L7
HNSW_M, HNSW_N = 16, 10**6                             # L7
HNSW_LINKS, LINK_BYTES = 33, 4                         # L7: "about 33 links per node, 4 bytes each"
FILTER_KEEP, WANT, OVERFETCH = 0.05, 10, 200           # L7: metadata filter
EXACT_SCAN_LIMIT = 10**5                               # L7: "below roughly 10^5 vectors, scan exhaustively"
HALLU_P, Z95 = 0.20, 1.96                              # L8: CI on a measured rate
EVAL_SIZES = (20, 200)
PASS_K_TRIALS, PASS_K_SUCCESSES = 4, 3                 # a worked pass^k example: one task, four trials, three passes

CITED = {"dpr_gain_points": "9$--$19"}   # quoted from a paper on a slide; test_deck.py finds it in the deck text


def trajectory_tokens(n, s=S, a=A):
    """Total input billed over n steps: n*S + a*n(n-1)/2 (turn t sends S + (t-1)a)."""
    return n * s + a * n * (n - 1) // 2


def first_turn_and_new(n, s=S, a=A):
    """Tokens billed at the full rate under prefix caching: the first turn's whole prompt, then a per turn."""
    return s + (n - 1) * a


def cost(full, cached):
    return (full * PRICE_IN + cached * PRICE_CACHED) / 1e6


def pass_hat_k(num_trials, success_count, k):
    """τ²-bench's pass^k (src/tau2/metrics/agent_metrics.py, after Yao et al. 2024): the chance that k trials drawn
    from the n run all succeed."""
    return math.comb(success_count, k) / math.comb(num_trials, k)


def tau2_facts():
    """Counts read from the τ²-bench data and source, so the narration types none of them."""
    tools_src = (TAU2 / "src/tau2/domains/retail/tools.py").read_text()
    kinds = re.findall(r"^\s*@is_tool\(ToolType\.(\w+)\)", tools_src, re.M)   # commented-out tools do not match
    db = json.loads((RETAIL / "db.json").read_text())
    split = json.loads((RETAIL / "split_tasks.json").read_text())
    docs = sorted((BANKING / "documents").glob("*.json"))
    words = sum(len((d := json.loads(p.read_text()))["title"].split()) + len(d["content"].split()) for p in docs)
    knowledge_readme = (TAU2 / "src/tau2/knowledge/README.md").read_text()
    configs = re.findall(r"^\| `([a-z0-9_\-]+)` \| [^|]*\| [^|]*\|$", knowledge_readme.split("## Retrieval Configs")[1]
                         .split("##")[0], re.M)
    reasons = re.search(r"reason not in \{([^}]*)\}", tools_src)[1]
    vocab = [set(re.findall(r"\w+", (d := json.loads(p.read_text()))["title"].lower() + " " + d["content"].lower()))
             for p in docs]
    return {
        "retail_tasks_base": len(split["base"]),
        "retail_tools": len(kinds),
        "retail_write_tools": kinds.count("WRITE"),
        "retail_read_tools": kinds.count("READ"),
        "retail_products": len(db["products"]), "retail_users": len(db["users"]), "retail_orders": len(db["orders"]),
        "cancel_reasons": sorted(re.findall(r'"([^"]+)"', reasons)),
        "banking_documents": len(docs),
        "banking_words": words,
        "docs_with": {w: sum(w in v for v in vocab) for w in ("overdraft", "account")},   # section 6: rare vs common
        "banking_tasks": len(json.loads((BANKING / "tasks.json").read_text())),
        "retrieval_configs": configs,
    }


def compute():
    v = {"cited": CITED}

    # ── Section 1: the loop and its bill ───────────────────────────────
    v["bill"] = {str(n): {"billed": trajectory_tokens(n), "new_only": S + n * A} for n in STEPS}
    v["bill_ratio_20_10"] = round(trajectory_tokens(20) / trajectory_tokens(10), 1)
    full10 = first_turn_and_new(10)
    hit10 = trajectory_tokens(10) - full10
    v["cache10"] = {"full": full10, "hit": hit10,
                    "cost_cached": round(cost(full10, hit10), 5),
                    "cost_uncached": round(cost(trajectory_tokens(10), 0), 5),
                    "ratio": round(cost(trajectory_tokens(10), 0) / cost(full10, hit10), 1),
                    "eval_cached": round(EVAL_QUERIES * cost(full10, hit10), 2),
                    "eval_uncached": round(EVAL_QUERIES * cost(trajectory_tokens(10), 0), 2)}
    v["p_step"] = P_STEP
    v["p10"] = round(P_STEP ** 10, 3)
    v["p_low_10"] = round(P_STEP_LOW ** 10, 2)
    v["p_low_5"] = round(P_STEP_LOW ** 5, 2)

    # ── Section 2: schemas and structured output ──────────────────────
    v["q_format"] = Q_FORMAT
    v["q10"] = round(Q_FORMAT ** 10, 2)
    v["schema_billed_10"] = SCHEMA_TOKENS * 10

    # ── Section 3: memory ────────────────────────────────────────────
    v["turns_uncapped"] = math.floor((WINDOW - S) / A_UNCAPPED) + 1
    v["turns_capped"] = math.floor((WINDOW - S) / A_CAPPED) + 1
    v["turns_ratio"] = round(v["turns_capped"] / v["turns_uncapped"], 1)

    # ── Section 4: orchestration ─────────────────────────────────────
    single = trajectory_tokens(SINGLE_STEPS)
    multi = SUBAGENTS * trajectory_tokens(SUB_STEPS) + trajectory_tokens(ORCH_TURNS, a=A_HANDOFF)
    s_full = first_turn_and_new(SINGLE_STEPS)
    m_full = SUBAGENTS * first_turn_and_new(SUB_STEPS) + first_turn_and_new(ORCH_TURNS, a=A_HANDOFF)
    v["orch"] = {"single_tokens": single, "multi_tokens": multi,
                 "fewer_pct": round(100 * (1 - multi / single)),
                 "single_full": s_full, "single_hit": single - s_full,
                 "multi_full": m_full, "multi_hit": multi - m_full,
                 "single_cost": round(cost(s_full, single - s_full), 5),
                 "multi_cost": round(cost(m_full, multi - m_full), 5),
                 "single_eval": round(EVAL_QUERIES * cost(s_full, single - s_full), 2),
                 "multi_eval": round(EVAL_QUERIES * cost(m_full, multi - m_full), 2),
                 "bill_ratio": round(cost(m_full, multi - m_full) / cost(s_full, single - s_full), 1),
                 "steps_single": SINGLE_STEPS, "steps_multi": SUBAGENTS * SUB_STEPS + ORCH_TURNS,
                 "p_single": round(P_STEP ** SINGLE_STEPS, 2),
                 "p_multi": round(P_STEP ** (SUBAGENTS * SUB_STEPS + ORCH_TURNS), 2)}
    v["verifier"] = {"draft": DRAFT_OK, "catch": VERIFIER_CATCH,
                     "with": round(DRAFT_OK + (1 - DRAFT_OK) * VERIFIER_CATCH * DRAFT_OK, 2)}

    # ── Section 5: RAG ───────────────────────────────────────────────
    rrf = {d: sum(1 / (RRF_K + r) for r in ranks if r is not None) for d, ranks in RRF_LISTS.items()}
    v["rrf"] = {d: round(s, 4) for d, s in rrf.items()}
    v["rrf_order"] = sorted(rrf, key=lambda d: -rrf[d])
    v["first_stage"] = FIRST_STAGE

    # ── Section 6: embeddings ────────────────────────────────────────
    v["batch"] = {"pairs": BATCH, "passes": 2 * BATCH, "negatives_each": BATCH - 1}

    # ── Section 7: ANN and vector databases ─────────────────────────
    ivf_ops = IVF_NLIST + IVF_NPROBE * IVF_N // IVF_NLIST
    v["ivf"] = {"ops": ivf_ops, "saving": round(IVF_N / ivf_ops)}
    v["pq"] = {"bytes_before": D_EMB * 4, "bytes_after": PQ_M, "reduction": D_EMB * 4 // PQ_M,
               "gb_before": D_EMB * 4 * PQ_N // 10**9, "gb_after": PQ_M * PQ_N // 10**9,
               "codebook_bytes": PQ_M * PQ_CENTROIDS * (D_EMB // PQ_M) * 4}
    v["hnsw"] = {"layers": round(math.log(HNSW_N) / math.log(HNSW_M), 2),
                 "layer1_nodes": HNSW_N // HNSW_M,
                 "graph_gb": round(HNSW_N * HNSW_LINKS * LINK_BYTES / 1e9, 2),
                 "vectors_gb": round(HNSW_N * D_EMB * 4 / 1e9, 2),
                 "overhead_pct": round(100 * HNSW_LINKS * LINK_BYTES / (D_EMB * 4))}
    v["filter"] = {"post_survive": WANT * FILTER_KEEP, "pre_large": int(10**9 * FILTER_KEEP)}

    # ── Section 8: evaluation ────────────────────────────────────────
    v["ci"] = {str(n): round(100 * Z95 * math.sqrt(HALLU_P * (1 - HALLU_P) / n), 1) for n in EVAL_SIZES}
    v["ci20_interval"] = [round(100 * HALLU_P - v["ci"]["20"], 1), round(100 * HALLU_P + v["ci"]["20"], 1)]
    v["pass_k_example"] = {str(k): pass_hat_k(PASS_K_TRIALS, PASS_K_SUCCESSES, k)
                           for k in range(1, PASS_K_TRIALS + 1)}

    # ── the testbed ──────────────────────────────────────────────────
    t = v["tau2"] = tau2_facts()
    v["banking_mb"] = round(t["banking_documents"] * D_EMB * 4 / 1e6, 1)
    v["banking_under_limit"] = t["banking_documents"] < EXACT_SCAN_LIMIT
    v["filter"]["pre_banking"] = round(t["banking_documents"] * FILTER_KEEP)
    return v


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "deck_numbers.json").write_text(json.dumps(compute(), indent=1, ensure_ascii=False))
    print("wrote", OUT / "deck_numbers.json")
