"""Capture every number the Lecture 5 video speaks or shows.

Two sources, both computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_clt_mle_graphics.py),
    saved verbatim to raw/l05_figures.txt;
  * the slides' worked examples (pastries per order, office runs, 66 pastries in 200 orders,
    40 espresso shots, mini-batches), computed here from their raw inputs. The sampling
    distributions are exact (convolutions), and the espresso shots are the figure script's own,
    regenerated from its seed.

`compute()` is pure, so test_l05.py can check every value against what the slides print.
Running this file writes raw/l05_numbers.json, which the video reads; the video types no number.
    uv run python statistics/capture_l05.py
    uv run python -m unittest discover -s statistics -p 'test_l05.py'
"""
import json
import os
import subprocess
from math import comb, erf, lgamma, log, log10, pi, sqrt
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
FIGURE_SCRIPT = REPO / "statistics/scripts/generate_clt_mle_graphics.py"

# ─── raw inputs: the only typed numbers (all from the slides) ─────────────
PASTRY = [0.7, 0.2, 0.1]                     # 0, 1, 2 pastries per order (Lecture 3)
NS = (1, 2, 5, 30)                           # sample sizes for the sampling distribution
N_SE = (10, 40, 160)                         # the standard-error curve's read-offs
N_SE_TASK = 640                              # section 2's pause: one more quadrupling
N_CUSTOMERS = 30
OFFICE = {1: 12, 2: 6, 3: 1, 40: 1}          # out of every 20 orders: coffees per order
RUNS_SHOWN = (0, 1, 2, 3)                    # office runs among 30 orders (3 is section 4's pause)
K, N = 66, 200                               # orders with a pastry, orders
P_HYPO = (0.25, 0.30, 0.40)                  # candidate rates compared with p-hat
K_TASK, N_TASK = 45, 150                     # section 8's pause
SHOT_SEED, SHOT_N, SHOT_MU, SHOT_SD = 11, 40, 30.0, 1.5
CANDIDATES = {"low": (28.6, 1.5), "wide": (None, 3.2)}   # None = the MLE centre
BATCH_SMALL, BATCH_BIG = 64, 2048
BATCH_TASK = 256                             # section 5's pause: 64 -> 256
CE_Y, CE_P = 1, 0.9                          # section 10's pause: one example, predicted 0.9


def Phi(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def convolve_n(pmf, n):
    out = np.array([1.0])
    for _ in range(n):
        out = np.convolve(out, pmf)
    return out


def skew(values, probs):
    m = (values * probs).sum()
    v = ((values - m) ** 2 * probs).sum()
    return float(((values - m) ** 3 * probs).sum() / v ** 1.5)


def bern_loglik(p, k=K, n=N):
    return k * log(p) + (n - k) * log(1 - p)


def gauss_loglik(x, mu, sd):
    return float(-len(x) / 2 * log(2 * pi * sd ** 2) - ((x - mu) ** 2).sum() / (2 * sd ** 2))


def compute():
    V = {}
    pmf = np.array(PASTRY)
    vals = np.arange(len(pmf))
    mu = float((vals * pmf).sum())
    var = float((vals ** 2 * pmf).sum() - mu ** 2)
    sd = sqrt(var)
    V["pastry"], V["mu"], V["var"], V["sigma"] = PASTRY, mu, var, sd

    # section 1: the sampling distribution; n = 2 by hand
    two = convolve_n(pmf, 2)
    V["two"] = {"means": [k / 2 for k in range(len(two))], "probs": two.tolist()}
    V["two_mean"] = float(sum(m * p for m, p in zip(V["two"]["means"], two)))
    V["two_e2"] = float(sum(m * m * p for m, p in zip(V["two"]["means"], two)))
    V["two_var"] = V["two_e2"] - V["two_mean"] ** 2
    V["two_formula"] = var / 2
    V["two_both_none"] = PASTRY[0] ** 2                                  # hands-on

    # section 2: the standard error
    V["se"] = {str(n): sd / sqrt(n) for n in (1, *N_SE, N_CUSTOMERS, N_SE_TASK)}
    V["n_se"], V["n_customers"], V["n_se_task"] = list(N_SE), N_CUSTOMERS, N_SE_TASK
    V["steadier"] = sqrt(N_CUSTOMERS)
    V["se_curve"] = [[n, sd / sqrt(n)] for n in range(1, 201)]
    V["tenfold_error_cost"] = 10 ** 2                                    # 1 % -> 0.1 %: 100 x the data

    # section 3: three spikes become a bell (exact)
    V["sampling"] = {}
    for n in NS:
        dist = convolve_n(pmf, n)
        means = np.arange(len(dist)) / n
        se = sd / sqrt(n)
        within = float(dist[np.abs(means - mu) <= se + 1e-12].sum())
        within2 = float(dist[np.abs(means - mu) <= 2 * se + 1e-12].sum())
        V["sampling"][str(n)] = {"means": means.tolist(), "probs": dist.tolist(), "se": se,
                                 "within_1se": within, "within_2se": within2, "support": int(len(dist))}
    V["gauss_1se"], V["gauss_2se"] = 2 * Phi(1) - 1, 2 * Phi(2) - 1

    # section 4: one huge order (office runs)
    total = sum(OFFICE.values())
    ov = np.arange(41)
    office = np.zeros(41)
    for c, k in OFFICE.items():
        office[c] = k / total
    mu_o = float((ov * office).sum())
    var_o = float((ov ** 2 * office).sum() - mu_o ** 2)
    ordinary = sum(c * k for c, k in OFFICE.items() if c != 40) / sum(k for c, k in OFFICE.items() if c != 40)
    V["office"] = {"counts": {str(c): k for c, k in OFFICE.items()}, "per": total, "mu": mu_o, "var": var_o,
                   "sigma": sqrt(var_o), "ordinary": ordinary, "ordinary_frac": [27, 19]}
    V["runs"] = [{"runs": r, "total": (N_CUSTOMERS - r) * ordinary + 40 * r,
                  "mean": ((N_CUSTOMERS - r) * ordinary + 40 * r) / N_CUSTOMERS} for r in RUNS_SHOWN]
    V["run_step"] = (40 - ordinary) / N_CUSTOMERS
    dist30 = convolve_n(office, N_CUSTOMERS)
    keep = dist30 > 1e-6
    V["office30"] = {"means": (np.arange(len(dist30))[keep] / N_CUSTOMERS).tolist(), "probs": dist30[keep].tolist()}
    p30 = convolve_n(pmf, N_CUSTOMERS)
    V["skew"] = {"pastry": skew(vals.astype(float), pmf),
                 "pastry_mean30": skew(np.arange(len(p30)) / N_CUSTOMERS, p30),
                 "office": skew(ov.astype(float), office),
                 "office_mean30": skew(np.arange(len(dist30)) / N_CUSTOMERS, dist30)}

    # section 5: mini-batch gradients
    V["batch_small"], V["batch_big"], V["batch_task"] = BATCH_SMALL, BATCH_BIG, BATCH_TASK
    V["batch_ratio"] = BATCH_BIG // BATCH_SMALL
    V["batch_noise_ratio"] = sqrt(BATCH_BIG / BATCH_SMALL)
    V["batch_task_noise_ratio"] = sqrt(BATCH_TASK / BATCH_SMALL)

    # sections 6-8: the Bernoulli likelihood
    p_hat = K / N
    V["k"], V["n"], V["n_minus_k"], V["p_hat"] = K, N, N - K, p_hat
    V["loglik_hat"] = bern_loglik(p_hat)
    V["log10_lik_hat"] = V["loglik_hat"] / log(10)
    V["lik_hat_mantissa"] = 10 ** (V["log10_lik_hat"] - np.floor(V["log10_lik_hat"]))
    V["lik_hat_exp"] = int(np.floor(V["log10_lik_hat"]))
    V["binom_log10"] = log10(comb(N, K))
    V["p_some_66"] = 10 ** (V["binom_log10"] + V["log10_lik_hat"])
    V["relative"] = {f"{p:.2f}": float(np.exp(bern_loglik(p) - V["loglik_hat"])) for p in P_HYPO}
    V["loglik_at"] = {f"{p:.2f}": bern_loglik(p) for p in (*P_HYPO, p_hat)}
    grid = np.linspace(0.15, 0.55, 241)
    V["lik_curve"] = [[float(p), float(np.exp(bern_loglik(p) - V["loglik_hat"]))] for p in grid]
    V["loglik_curve"] = [[float(p), bern_loglik(p)] for p in grid]
    V["k_task"], V["n_task"], V["p_hat_task"] = K_TASK, N_TASK, K_TASK / N_TASK

    # section 9: which bell curve fits? (same generator and seed as the figure script)
    rng = np.random.default_rng(SHOT_SEED)
    shots = rng.normal(SHOT_MU, SHOT_SD, size=SHOT_N)
    xbar = float(shots.mean())
    s_mle = float(np.sqrt(((shots - xbar) ** 2).mean()))
    s_l1 = float(shots.std(ddof=1))
    V["shots"] = shots.round(4).tolist()
    V["shot_n"], V["xbar"], V["sigma_mle"], V["s_lecture1"] = SHOT_N, xbar, s_mle, s_l1
    V["fits"] = {"mle": {"mu": xbar, "sigma": s_mle, "loglik": gauss_loglik(shots, xbar, s_mle)}}
    for name, (m, s) in CANDIDATES.items():
        m = xbar if m is None else m
        V["fits"][name] = {"mu": m, "sigma": s, "loglik": gauss_loglik(shots, m, s)}
    V["fit_margin"] = V["fits"]["mle"]["loglik"] - max(V["fits"]["low"]["loglik"], V["fits"]["wide"]["loglik"])

    # section 10: cross-entropy of one example
    V["ce_y"], V["ce_p"] = CE_Y, CE_P
    V["ce_loss"] = -(CE_Y * log(CE_P) + (1 - CE_Y) * log(1 - CE_P))
    return V


def figure_output():
    adv_ai = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
    r = subprocess.run([adv_ai, str(FIGURE_SCRIPT)], capture_output=True, text=True, cwd=REPO / "statistics")
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "l05_figures.txt").write_text(figure_output())
    (OUT / "l05_numbers.json").write_text(json.dumps(compute(), indent=1, ensure_ascii=False))
    print("wrote raw/l05_figures.txt and raw/l05_numbers.json")
