"""Capture every number the Lecture 8 video speaks or shows.

Two sources, both computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_expfamily_graphics.py),
    saved verbatim to raw/l08_figures.txt;
  * the slides' worked examples (the coffee shop's pastry rate and cup shares, Lecture 3's
    simulated arrivals, Lecture 5's 66 of 200 orders and 40 espresso shots, the three ten-morning
    records, Lecture 6's bus), computed here from their raw inputs. Simulated data is regenerated
    from the same generator and seed as the script that first drew it.

`compute()` is pure, so test_l08.py can check every value against what the slides print.
Running this file writes raw/l08_numbers.json, which the video reads; the video types no number.
    uv run python statistics/capture_l08.py
    uv run python -m unittest discover -s statistics -p 'test_l08.py'
"""
import json
import os
import subprocess
from math import comb, exp, log, log10, log1p, sqrt
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
FIGURE_SCRIPT = REPO / "statistics/scripts/generate_expfamily_graphics.py"

# ─── raw inputs: the only typed numbers (all from the slides and earlier lectures) ─────────
PASTRY_NONE = 0.7                       # Lecture 3: an order has no pastry with probability 0.7
CUPS = (0.2, 0.5, 0.3)                  # Lecture 3: small, medium, large
SHIFT = 2                               # the slide: "and so do those three scores plus 2"
K, N = 66, 200                          # Lecture 5: orders with a pastry, orders
LAM = 4                                 # Lecture 3: arrivals per ten minutes
SIM_SEED, SIM_WINDOWS = 21, 3000        # Lecture 3's simulated windows (its figure script's seed)
SHOT_SEED, SHOT_N, SHOT_MU, SHOT_SD = 11, 40, 30.0, 1.5   # Lecture 5's espresso shots
RECORDS = {                             # the figure script's three ten-morning records, 20 orders a morning
    "steady":      [7, 6, 7, 6, 7, 6, 7, 7, 7, 6],
    "one big day": [20, 3, 4, 5, 3, 6, 4, 7, 9, 5],
    "building up": [1, 2, 4, 5, 6, 8, 9, 10, 10, 11],
}
PER_MORNING = 20
BUS_PRIOR, BUS_30 = (8, 2), (22, 8)     # Lecture 6: Beta(8, 2); 22 on time and 8 late in 30 mornings
PASTRY_PRIOR = (3, 7)                   # section 9's pause: "as if 10 orders, 3 with a pastry"
DIR_PRIOR, DIR_COUNTS = (0.8, 2, 1.2), (7, 21, 12)        # Lecture 6, section 8
SURE = (0.99, 0.999)                    # section 2: near-certainty runs off the line
SCORES_BIG = (1000, 999)                # section 5: scores too big for e^x
STEP = 0.01                             # section 5: a numerical slope
SIM_FIRST = 10                          # section 6's pause: the first ten of Lecture 3's windows


def sigmoid(e):
    return 1 / (1 + exp(-e))


def softmax(s):
    w = [exp(x) for x in s]
    return [x / sum(w) for x in w]


def logit(p):
    return log(p / (1 - p))


def bern_A(e):
    return log1p(exp(e))


def sim_counts():
    """Lecture 3's 3000 simulated ten-minute windows (same generator and seed as its figure script)."""
    rng = np.random.default_rng(SIM_SEED)
    gaps = rng.exponential(scale=1.0 / LAM, size=int(LAM * SIM_WINDOWS * 1.6))
    times = np.cumsum(gaps)
    times = times[times < SIM_WINDOWS]
    return np.bincount(times.astype(int), minlength=SIM_WINDOWS)[:SIM_WINDOWS]


def compute():
    V = {}
    p = 1 - PASTRY_NONE
    eta = logit(p)

    # section 1: three MLEs, each an average (Lecture 5's share, Lecture 3's arrivals)
    counts = sim_counts()
    V["p"], V["k"], V["n"], V["p_hat"] = p, K, N, K / N
    V["sim_mean"], V["sim_var"] = float(counts.mean()), float(counts.var(ddof=1))
    V["sim_mean_slide"] = round(V["sim_mean"], 2)                    # the slide's 3.96

    # section 2: the logit and the sigmoid
    V["odds"], V["eta"] = p / (1 - p), eta
    V["eta_mirror"] = logit(1 - p)                                   # pause: p = 0.7
    V["eta_sure"] = [logit(q) for q in SURE]
    V["sigmoid_back"] = sigmoid(eta)
    V["sigmoid_zero"] = sigmoid(0.0)

    # section 3: the categorical's scores and the softmax
    scores = [log(c) for c in CUPS]
    V["cups"], V["scores"] = list(CUPS), scores
    V["softmax_scores"] = softmax(scores)
    V["scores_shifted"] = [s + SHIFT for s in scores]
    V["softmax_shifted"] = softmax(V["scores_shifted"])
    V["score_gap_mid_small"] = scores[1] - scores[0]
    V["share_ratio_mid_small"] = CUPS[1] / CUPS[0]
    V["softmax_two"] = softmax([eta, 0.0])[0]                       # two classes: softmax is the sigmoid
    V["softmax_zeros"] = softmax([0.0, 0.0, 0.0])                    # pause: all scores equal

    # section 4: the table; the Poisson's natural parameter
    V["lam"], V["eta_pois"] = LAM, log(LAM)

    # section 5: A(eta), its slope and curvature
    V["weights"] = [1.0, exp(eta)]
    V["weights_total"] = 1 + exp(eta)
    V["A"], V["minus_log_q"] = bern_A(eta), -log(1 - p)
    V["share_from_weights"] = exp(eta) / (1 + exp(eta))
    V["A_slope_num"] = (bern_A(eta + STEP) - bern_A(eta - STEP)) / (2 * STEP)
    V["A_prime"], V["A_second"] = sigmoid(eta), sigmoid(eta) * (1 - sigmoid(eta))
    V["bern_var"] = p * (1 - p)
    V["pois_A"] = {"A": exp(log(LAM)), "A_prime": exp(log(LAM)), "A_second": exp(log(LAM))}
    m = max(SCORES_BIG)
    V["lse_big"] = m + log(sum(exp(s - m) for s in SCORES_BIG))
    with np.errstate(over="ignore"):
        V["lse_overflows"] = bool(np.isinf(np.exp(np.float64(SCORES_BIG[0]))))   # e^1000 in float64

    # section 6: maximum likelihood is moment matching
    V["eta_hat"] = logit(K / N)
    V["eta_hat_pois"] = log(V["sim_mean_slide"])
    V["grad_at_true"] = K - N * p                                    # observed T minus expected T
    V["expected_at_true"] = N * p
    first = counts[:SIM_FIRST]
    V["sim_first"] = first.tolist()
    V["sim_first_total"] = int(first.sum())
    V["sim_first_mean"] = float(first.mean())
    V["eta_hat_first"] = log(float(first.mean()))

    # section 7: three records, one sufficient statistic, one curve
    V["records"] = RECORDS
    V["record_totals"] = {k: sum(r) for k, r in RECORDS.items()}
    V["per_morning"], V["mornings"] = PER_MORNING, len(RECORDS["steady"])
    V["loglik_hat"] = K * log(K / N) + (N - K) * log(1 - K / N)
    V["arrangements_log10"] = log10(comb(N, K))
    # given the total, every arrangement has probability 1 / C(N, K), whatever p is
    V["given_total"] = {str(q): (q ** K * (1 - q) ** (N - K)) / (comb(N, K) * q ** K * (1 - q) ** (N - K))
                        for q in (0.2, 0.33, 0.5)}

    # section 8: the factorization; what a Gaussian needs
    rng = np.random.default_rng(SHOT_SEED)
    shots = rng.normal(SHOT_MU, SHOT_SD, size=SHOT_N)
    s1, s2 = float(shots.sum()), float((shots ** 2).sum())
    xbar = s1 / SHOT_N
    var = s2 / SHOT_N - xbar ** 2
    V["shot_n"], V["sum_x"], V["sum_x2"] = SHOT_N, s1, s2
    V["xbar"], V["sigma_hat"] = xbar, sqrt(var)
    V["mean_sq"], V["xbar_sq"], V["var_hat"] = s2 / SHOT_N, xbar ** 2, var
    V["sigma_direct"] = float(np.sqrt(((shots - shots.mean()) ** 2).mean()))
    # two spikes, half at x̄ - σ̂ and half at x̄ + σ̂: the same two sums, nothing like a bell
    spikes = np.r_[np.full(SHOT_N // 2, xbar - sqrt(var)), np.full(SHOT_N // 2, xbar + sqrt(var))]
    V["spikes"] = [float(xbar - sqrt(var)), float(xbar + sqrt(var))]
    V["spikes_sums"] = [float(spikes.sum()), float((spikes ** 2).sum())]

    # section 9: why conjugacy worked
    a0, b0 = BUS_PRIOR
    s, f = BUS_30
    V["bus"] = {"prior": [a0, b0], "worth": a0 + b0, "data": [s, f], "post": [a0 + s, b0 + f],
                "mean": (a0 + s) / (a0 + b0 + s + f)}
    V["dir"] = {"prior": list(DIR_PRIOR), "worth": sum(DIR_PRIOR), "counts": list(DIR_COUNTS),
                "post": [a + c for a, c in zip(DIR_PRIOR, DIR_COUNTS)]}
    pa, pb = PASTRY_PRIOR
    V["pastry_task"] = {"prior": [pa, pb], "worth": pa + pb, "post": [pa + K, pb + N - K],
                        "mean": (pa + K) / (pa + pb + N)}

    # section 10: a counter instead of a dataset; what the counter cannot see
    big = RECORDS["one big day"]
    V["halves_big_day"] = [sum(big[:5]), sum(big[5:])]
    V["halves_orders"] = 5 * PER_MORNING
    V["server_share"] = sum(big) / (len(big) * PER_MORNING)
    build = RECORDS["building up"]
    V["halves_building"] = [sum(build[:5]), sum(build[5:])]
    V["halves_building_share"] = [sum(build[:5]) / (5 * PER_MORNING), sum(build[5:]) / (5 * PER_MORNING)]
    steady = RECORDS["steady"]
    V["stream_steady"] = [[sum(steady[:i + 1]), (i + 1) * PER_MORNING] for i in range(len(steady))]
    V["stream_task"] = {"total": sum(steady[:3]), "orders": 3 * PER_MORNING,
                        "share": sum(steady[:3]) / (3 * PER_MORNING)}
    return V


def figure_output():
    adv_ai = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
    r = subprocess.run([adv_ai, str(FIGURE_SCRIPT)], capture_output=True, text=True, cwd=REPO / "statistics")
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "l08_figures.txt").write_text(figure_output())
    (OUT / "l08_numbers.json").write_text(json.dumps(compute(), indent=1, ensure_ascii=False))
    print("wrote raw/l08_figures.txt and raw/l08_numbers.json")
