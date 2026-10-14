"""s7 · An evaluation harness — IDEA SNIPPET, not run. τ²-bench does exactly this; see raw/tau2_retail.json."""
from math import comb


def run_suite(agent, tasks, trials=3):
    """Grade the end state, not the wording: after the conversation, does the database match the expected one?"""
    results = {t.id: [] for t in tasks}
    for t in tasks:
        for _ in range(trials):
            final_db = agent.run(t.user_scenario, db=t.initial_db.copy())
            results[t.id].append(final_db == t.expected_db)
    return results


def pass_hat_k(results, k):
    """pass^k: the chance that all k independent tries of a task succeed (τ-bench's reliability metric).
    With c successes in n tries, an unbiased estimate is C(c, k) / C(n, k), averaged over tasks."""
    return sum(comb(sum(r), k) / comb(len(r), k) for r in results.values()) / len(results)
# pass^1 is the usual success rate; pass^3 far below it means the agent is right by luck, not by design.
