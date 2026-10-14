"""Turn τ²-bench result files into the numbers and the two conversations the video shows.

    python3 capture_tau2.py          # reads tau2-bench/data/simulations/*/results.json, writes raw/tau2_*.json
Everything here is computed from the saved runs; test_tau2.py recomputes it.
"""
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIMS = HERE / "tau2-bench/data/simulations"
RAW = HERE / "raw"
JUDGE_NOTE = ("natural-language assertions judged by deepseek/deepseek-v4-flash via run_tau2.py "
              "(the leaderboard uses gpt-4.1), so scores are not leaderboard-comparable")


def load(run):
    return json.loads((SIMS / run / "results.json").read_text())


def pass_hat_k(rewards_by_task, k):
    """τ-bench's pass^k: mean over tasks of C(c, k) / C(n, k), c successes in n trials."""
    usable = {t: r for t, r in rewards_by_task.items() if len(r) >= k}
    return sum(comb(sum(r), k) / comb(len(r), k) for r in usable.values()) / len(usable)


def tokens(sims):
    p = c = 0
    for s in sims:
        for m in s["messages"]:
            u = m.get("usage") or {}
            p += u.get("prompt_tokens") or 0
            c += u.get("completion_tokens") or 0
    return p, c


def summary(run, note=None):
    d = load(run)
    sims = d["simulations"]
    by_task = {}
    for s in sims:
        by_task.setdefault(s["task_id"], []).append(int(s["reward_info"]["reward"] == 1.0))
    trials = max(len(r) for r in by_task.values())
    p, c = tokens(sims)
    out = {"run": run, "tau2_commit": d["info"]["git_commit"], "tau2_tag": "v1.0.1",
           "agent_llm": d["info"]["agent_info"]["llm"], "user_llm": d["info"]["user_info"]["llm"],
           "served_model": next((m["raw_data"]["model"] for s in sims for m in s["messages"] if m.get("raw_data")), None),
           "retrieval_config": d["info"].get("retrieval_config"),
           "n_tasks": len(by_task), "n_trials": trials, "n_simulations": len(sims),
           "rewards_by_task": by_task,
           "pass_1": round(sum(map(sum, by_task.values())) / len(sims), 4),
           "pass_hat_k": {k: round(pass_hat_k(by_task, k), 4) for k in range(1, trials + 1)},
           "cost_usd": round(sum(s["agent_cost"] + s["user_cost"] for s in sims), 4),
           "cost_per_conversation_usd": round(sum(s["agent_cost"] + s["user_cost"] for s in sims) / len(sims), 4),
           "prompt_tokens": p, "completion_tokens": c,
           "terminations": {r: sum(s["termination_reason"] == r for s in sims)
                            for r in sorted({s["termination_reason"] for s in sims})}}
    if note:
        out["note"] = note
    return out, sims


def conversation(s, cut=400):
    """The conversation as the video shows it: who said what, which tool with which arguments, results shortened."""
    rows = []
    for m in s["messages"]:
        row = {"role": m["role"]}
        if m.get("content"):
            row["content"] = m["content"] if m["role"] != "tool" else m["content"][:cut]
        if m.get("tool_calls"):
            row["tool_calls"] = [{"name": t["name"], "arguments": t["arguments"]} for t in m["tool_calls"]]
        rows.append(row)
    return rows


def why_failed(s):
    ri = s["reward_info"]
    missed = [{"name": a["action"]["name"], "arguments": a["action"]["arguments"]}
              for a in ri.get("action_checks") or [] if not a["action_match"]]
    nl = [n for n in ri.get("nl_assertions") or [] if not n.get("met", True)]
    return {"db_match": (ri.get("db_check") or {}).get("db_match"), "expected_actions_not_taken": missed,
            "nl_assertions_failed": nl, "reward_basis": ri.get("reward_basis")}


def n_calls(s):
    return sum(len(m.get("tool_calls") or []) for m in s["messages"])


def main():
    retail, sims = summary("retail10x3", JUDGE_NOTE)
    RAW.joinpath("tau2_retail.json").write_text(json.dumps(retail, indent=1))
    ok = [s for s in sims if s["reward_info"]["reward"] == 1.0]
    bad = [s for s in sims if s["reward_info"]["reward"] != 1.0 and s["termination_reason"] != "infrastructure_error"]
    best = max(ok, key=n_calls)                                  # a success with the most tool calls
    RAW.joinpath("tau2_retail_trajectory.json").write_text(json.dumps(
        {"task_id": best["task_id"], "trial": best["trial"], "reward": best["reward_info"]["reward"],
         "tool_calls": n_calls(best), "turns": len(best["messages"]), "cost_usd": round(best["agent_cost"], 4),
         "messages": conversation(best)}, indent=1, ensure_ascii=False))
    if bad:
        worst = max(bad, key=n_calls)
        RAW.joinpath("tau2_retail_failure.json").write_text(json.dumps(
            {"task_id": worst["task_id"], "trial": worst["trial"], "reward": worst["reward_info"]["reward"],
             "tool_calls": n_calls(worst), "why": why_failed(worst), "messages": conversation(worst)},
            indent=1, ensure_ascii=False))
    banking, bsims = summary("banking5_bm25", "banking ran without run_tau2.py; it needed no gpt-4.1 judge")
    kb = HERE / "tau2-bench/data/tau2/domains/banking_knowledge/documents"
    banking["kb_documents"] = sum(1 for f in kb.rglob("*") if f.is_file())
    banking["kb_searches"] = sum(1 for s in bsims for m in s["messages"] for t in m.get("tool_calls") or []
                                 if t["name"].startswith("KB_search"))
    RAW.joinpath("tau2_banking.json").write_text(json.dumps(banking, indent=1))
    print(json.dumps({k: retail[k] for k in ("pass_1", "pass_hat_k", "cost_usd", "n_simulations", "terminations")}))
    print(json.dumps({k: banking[k] for k in ("pass_1", "cost_usd", "kb_documents", "kb_searches")}))


if __name__ == "__main__":
    main()
