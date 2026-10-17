"""Module 7, Lecture 1 (What is an agent?): every number the video says or shows.

The inputs are the slides' (agents/lectures/lecture01_what_is_an_agent.tex) and the course's price snapshot
(course-map.md, "Module 7 model and cost baseline", off-peak). The agent runs the video replays are the class agent's
recordings (agents/class_agent/traces/), whose facts agents/class_agent/test_class_agent.py checks.

    uv run python m7/capture_l01.py        (from video/) -> m7/raw/l01_numbers.json
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
S, A = 1200, 500                         # tokens: the fixed prefix, and what one step adds
STEPS = (3, 10, 20)
PRICE_IN, PRICE_CACHED = 0.15, 0.003     # US$ per million input tokens, off-peak
EVAL_RUNS = 500                          # a 500-query evaluation
P_GOOD, K_LONG = 0.95, 10                # errors compound: one step right with p, k steps
P_LEVER, K_SHORT = 0.90, 5               # fewer steps against a better model


def billed(n):
    """Input tokens over an n-step trajectory: turn t re-sends S + (t - 1) A."""
    return n * S + A * n * (n - 1) // 2


def compute():
    c = {}
    for n in STEPS:
        c[f"billed_{n}"] = billed(n)
        c[f"new_only_{n}"] = S + A * n                       # if only the new text were paid for
    c["ratio_20_10"] = round(billed(20) / billed(10), 1)
    n = 10
    fresh = S + A * (n - 1)                                  # the prefix once, then each step's new tokens
    cached = billed(n) - fresh
    c["fresh_10"], c["cached_10"] = fresh, cached
    c["cost_cached_10"] = round((fresh * PRICE_IN + cached * PRICE_CACHED) / 1e6, 5)
    c["cost_full_10"] = round(billed(n) * PRICE_IN / 1e6, 5)
    c["cache_ratio"] = round(c["cost_full_10"] / c["cost_cached_10"], 1)
    c["eval_cached"] = round(EVAL_RUNS * (fresh * PRICE_IN + cached * PRICE_CACHED) / 1e6, 2)
    c["eval_full"] = round(EVAL_RUNS * billed(n) * PRICE_IN / 1e6, 2)
    c["turn_1"], c["turn_2"], c["turn_3"] = (S + (t - 1) * A for t in (1, 2, 3))   # what each turn sends
    c["billed_5"] = billed(5)                                # the pause question in the cost section
    c["cents_per_million"] = round(PRICE_IN * 100, 1)        # 15 cents
    c["cents_per_million_cached"] = round(PRICE_CACHED * 100, 1)
    c["cache_price_ratio"] = round(PRICE_IN / PRICE_CACHED)  # a cached token is this many times cheaper
    c["p_good_k_long"] = round(P_GOOD ** K_LONG, 3)
    c["p_lever_k_long"] = round(P_LEVER ** K_LONG, 2)
    c["p_lever_k_short"] = round(P_LEVER ** K_SHORT, 2)
    c["p_99_k_20"] = round(0.99 ** 20, 3)                    # the pause question in the compounding section
    return c


if __name__ == "__main__":
    (HERE / "raw").mkdir(exist_ok=True)
    out = HERE / "raw" / "l01_numbers.json"
    out.write_text(json.dumps(compute(), indent=1))
    print(out.read_text())
