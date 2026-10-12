"""Capture every number the Lecture 6 video speaks or shows.

Two sources, both computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_bayesian_graphics.py),
    saved verbatim to raw/l06_figures.txt;
  * the slides' worked examples (the 7:40 bus, the coffee-shop Dirichlet, the walk to the station,
    the prior that becomes a penalty), computed here from their raw inputs. The 100 bus mornings are
    the figure script's own, regenerated from its seed.

`compute()` is pure, so test_l06.py can check every value against what the slides print.
Running this file writes raw/l06_numbers.json, which the video reads; the video types no number.
    uv run python statistics/capture_l06.py
    uv run python -m unittest discover -s statistics -p 'test_l06.py'
"""
import json
import os
import subprocess
from math import sqrt
from pathlib import Path

import numpy as np
from scipy.stats import beta as beta_dist, norm

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
FIGURE_SCRIPT = REPO / "statistics/scripts/generate_bayesian_graphics.py"

# ─── raw inputs: the only typed numbers (all from the slides) ─────────────
TRUE_RATE, BUS_SEED, BUS_DAYS = 0.70, 21, 100   # the figure script's simulated mornings
PRIOR = (8, 2)                                  # "as if 8 on time, 2 late"
SHOWN = (1, 10, 30, 100)                        # mornings read off on the slides
CI = 0.95
PRIORS = {"flat": (1, 1), "ours": PRIOR, "stubborn": (80, 20)}
DIR_PRIOR = (0.8, 2, 1.2)                       # Lecture 3: about four orders (small, medium, large)
DIR_COUNTS = (7, 21, 12)                        # the next 40 orders
WALK_MU0, WALK_TAU0, WALK_SIGMA = 12.0, 3.0, 3.0
WALK = (13.0, 14.0, 16.0, 17.0)
TAUS = (2.0, 1.0, 0.5)                          # prior widths on one weight
LAMBDA_TASK = (2.0, 1.0)                        # section 10's pause: sigma, tau
WALK_TAU_TASK = 1.5                             # section 9's pause: a prior worth four timings
COVER_SEED, COVER_REPEATS = 6, 10_000           # draft 2: repeat the hundred mornings, flat-prior intervals
CLOSE = 0.01                                    # draft 2: "within one percentage point of the data"
SMALL_W = 0.1                                   # draft 2: a small weight, L1 vs L2
GRID = np.linspace(0, 1, 601)


def beta_summary(a, b, n=None, k=None):
    lo, hi = beta_dist.ppf([(1 - CI) / 2, (1 + CI) / 2], a, b)
    return {"a": a, "b": b, "mean": a / (a + b), "map": (a - 1) / (a + b - 2),
            "ci": [float(lo), float(hi)], "ci_width": float(hi - lo),
            **({"n": n, "on_time": k, "late": n - k, "mle": k / n} if n else {})}


def curve(a, b, lo=0.0, hi=1.0):
    g = GRID[(GRID >= lo) & (GRID <= hi)]
    return [[float(x), float(y)] for x, y in zip(g, beta_dist.pdf(g, a, b))]


def compute():
    V = {}
    rng = np.random.default_rng(BUS_SEED)
    on_time = rng.random(BUS_DAYS) < TRUE_RATE
    a0, b0 = PRIOR
    V["true_rate"], V["prior"], V["prior_n"], V["prior_mean"] = TRUE_RATE, list(PRIOR), a0 + b0, a0 / (a0 + b0)
    V["day1_on_time"] = bool(on_time[0])
    V["prior_curve"] = curve(a0, b0)
    V["flat_curve"] = curve(1, 1)

    # section 1-2: one late bus
    V["mle_day1"] = int(on_time[:1].sum()) / 1
    V["mle_day1_task"] = 1 / 1                                   # section 1's pause: Monday on time
    V["one_late"] = beta_summary(a0, b0 + 1)
    V["one_on_time"] = beta_summary(a0 + 1, b0)                  # section 2's pause
    V["lik_late_curve"] = [[float(x), float(1 - x)] for x in GRID]

    # sections 3-4, 6: the month of mornings
    V["bus"] = {}
    for n in SHOWN:
        k = int(on_time[:n].sum())
        V["bus"][str(n)] = beta_summary(a0 + k, b0 + n - k, n, k) | {"curve": curve(a0 + k, b0 + n - k)}
    V["mle_path"] = (np.cumsum(on_time) / np.arange(1, BUS_DAYS + 1)).tolist()
    V["post_path"] = ((a0 + np.cumsum(on_time)) / (a0 + b0 + np.arange(1, BUS_DAYS + 1))).tolist()
    V["ci_shrink"] = V["bus"]["10"]["ci_width"] / V["bus"]["100"]["ci_width"]

    # section 5: three priors, the same 100 mornings
    k100 = int(on_time.sum())
    V["three"] = {}
    for name, (a, b) in PRIORS.items():
        post = beta_summary(a + k100, b + BUS_DAYS - k100)
        V["three"][name] = {"prior": [a, b], "worth": a + b, "prior_mean": a / (a + b), "post": post,
                            "prior_curve": curve(a, b), "post_curve": curve(post["a"], post["b"])}

    # section 7: Beta-Bernoulli is counting; the predictive is the posterior mean
    r30 = V["bus"]["30"]
    V["count30"] = {"a": a0 + r30["on_time"], "b": b0 + r30["late"], "mean": r30["mean"]}
    V["predictive_bus"] = V["bus"]["100"]["mean"]

    # section 8: Dirichlet-categorical
    post = [p + c for p, c in zip(DIR_PRIOR, DIR_COUNTS)]
    V["dir_prior"], V["dir_counts"], V["dir_post"] = list(DIR_PRIOR), list(DIR_COUNTS), post
    V["dir_prior_n"], V["dir_n"], V["dir_post_n"] = sum(DIR_PRIOR), sum(DIR_COUNTS), sum(post)
    V["dir_shares"] = [x / sum(post) for x in post]
    task = post[:2] + [post[2] + 1]                              # section 8's pause: one more large
    V["dir_task"], V["dir_task_large"] = task, task[2] / sum(task)

    # section 9: the walk to the station
    xbar = sum(WALK) / len(WALK)
    pp, pd_ = 1 / WALK_TAU0 ** 2, len(WALK) / WALK_SIGMA ** 2
    pv = 1 / (pp + pd_)
    V["walk"] = {"mu0": WALK_MU0, "tau0": WALK_TAU0, "sigma": WALK_SIGMA, "timings": list(WALK), "n": len(WALK),
                 "xbar": xbar, "prec_prior": pp, "prec_data": pd_, "weight_data": pd_ / (pp + pd_),
                 "post_mu": (WALK_MU0 * pp + xbar * pd_) * pv, "post_var": pv, "post_sd": sqrt(pv),
                 "prior_worth": WALK_SIGMA ** 2 / WALK_TAU0 ** 2,
                 "pred_sd": sqrt(pv + WALK_SIGMA ** 2)}
    V["walk"]["by_counts"] = (V["walk"]["prior_worth"] * WALK_MU0 + len(WALK) * xbar) / (V["walk"]["prior_worth"] + len(WALK))
    pt = 1 / WALK_TAU_TASK ** 2
    V["walk_task"] = {"tau0": WALK_TAU_TASK, "prior_worth": WALK_SIGMA ** 2 / WALK_TAU_TASK ** 2,
                      "post_mu": (WALK_MU0 * pt + xbar * pd_) / (pt + pd_)}

    # section 10: a Gaussian prior is an L2 penalty
    V["penalty"] = {str(t): 1 / (2 * t ** 2) for t in TAUS}
    V["penalty_ratio"] = V["penalty"]["0.5"] / V["penalty"]["2.0"]
    s, t = LAMBDA_TASK
    V["lambda_task"] = {"sigma": s, "tau": t, "lambda": s ** 2 / t ** 2}
    V["depth"] = depth(V, on_time)
    return V


def beta_sd(a, b):
    return sqrt(a * b / ((a + b) ** 2 * (a + b + 1)))


def depth(V, on_time):
    """Numbers of draft 2's added lines (several angles per idea, recaps of Lectures 1-5)."""
    D = {}
    a0, b0 = PRIOR
    n0 = a0 + b0
    # s1: same mean, different certainty
    D["sd_prior"], D["sd_stubborn"] = beta_sd(a0, b0), beta_sd(*PRIORS["stubborn"])
    # s2: one late bus as a likelihood ratio between two thetas; the mean as a weighted average
    D["late_if_08"], D["late_if_05"] = 1 - 0.8, 1 - 0.5
    D["late_ratio"] = D["late_if_05"] / D["late_if_08"]
    D["blend_day1"] = (n0 * V["prior_mean"] + 1 * V["mle_day1"]) / (n0 + 1)
    # s3: the MLE swings early, the posterior mean does not; the hundred mornings as a weighted average
    m, p = np.array(V["mle_path"][:10]), np.array(V["post_path"][:10])
    D["first10_mle"], D["first10_post"] = [float(m.min()), float(m.max())], [float(p.min()), float(p.max())]
    r = V["bus"]["100"]
    D["blend_100"] = (n0 * V["prior_mean"] + r["n"] * r["mle"]) / (n0 + r["n"])
    D["data_weight_100"] = r["n"] / (n0 + r["n"])
    # s4: the normal approximation (Lecture 4's two-sigma rule); the 1/sqrt(n) narrowing (Lecture 5)
    sd = beta_sd(r["a"], r["b"])
    D["sd_100"], D["two_sd_100"] = sd, [r["mean"] - 2 * sd, r["mean"] + 2 * sd]
    D["count_ratio"] = (r["a"] + r["b"]) / (V["bus"]["10"]["a"] + V["bus"]["10"]["b"])
    D["sqrt_count_ratio"] = sqrt(D["count_ratio"])
    # s5: how many mornings (at the data's rate) until each prior's mean is within CLOSE of it
    rate = r["mle"]
    D["mornings_to_close"] = {name: next(n for n in range(1, 100_000)
                                         if abs((a + rate * n) / (a + b + n) - rate) <= CLOSE + 1e-12)
                              for name, (a, b) in PRIORS.items()}
    # s5: a flat-prior 95 % interval, rebuilt on many repeats of the hundred mornings
    rng = np.random.default_rng(COVER_SEED)
    k = rng.binomial(BUS_DAYS, TRUE_RATE, COVER_REPEATS)
    lo, hi = beta_dist.ppf((1 - CI) / 2, 1 + k, 1 + BUS_DAYS - k), beta_dist.ppf((1 + CI) / 2, 1 + k, 1 + BUS_DAYS - k)
    D["coverage"] = float(((lo <= TRUE_RATE) & (TRUE_RATE <= hi)).mean())
    # s6: flat prior's MAP is the MLE; after Monday it is the absurd zero again, the mean is a third
    k100 = r["on_time"]
    D["flat_map_100"] = ((1 + k100) - 1) / ((1 + k100) + (1 + BUS_DAYS - k100) - 2)
    D["flat_day1"] = beta_summary(1, 2)
    # s7: one morning at a time ends where thirty at once does
    a, b = a0, b0
    for x in on_time[:30]:
        a, b = a + int(x), b + int(not x)
    D["seq30"] = [a, b]
    # s8: shares from the counts alone; a cup never seen
    D["dir_raw_shares"] = [c / sum(DIR_COUNTS) for c in DIR_COUNTS]
    D["dir_unseen"] = DIR_PRIOR[0] / (sum(DIR_PRIOR) + sum(DIR_COUNTS))
    # s9: the prior as 12 +- 3 (Lecture 4's 68 %); four timings' standard error (Lecture 5)
    D["walk_band"] = [WALK_MU0 - WALK_TAU0, WALK_MU0 + WALK_TAU0]
    D["one_sd_share"] = float(2 * norm.cdf(1) - 1)
    D["walk_se_var"] = WALK_SIGMA ** 2 / len(WALK)
    D["walk_se"] = sqrt(D["walk_se_var"])
    # s10: lambda is the walk's "worth" formula; a small weight under L2 and L1
    D["lambda_as_worth"] = WALK_SIGMA ** 2 / WALK_TAU0 ** 2
    D["l2_small"], D["l1_small"] = SMALL_W ** 2, abs(SMALL_W)
    D["l1_over_l2_small"] = D["l1_small"] / D["l2_small"]
    return D


def figure_output():
    adv_ai = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
    r = subprocess.run([adv_ai, str(FIGURE_SCRIPT)], capture_output=True, text=True, cwd=REPO / "statistics")
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "l06_figures.txt").write_text(figure_output())
    (OUT / "l06_numbers.json").write_text(json.dumps(compute(), indent=1, ensure_ascii=False))
    print("wrote raw/l06_figures.txt and raw/l06_numbers.json")
