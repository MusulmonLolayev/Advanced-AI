"""Capture every number the Lecture 4 video speaks or shows.

Two sources, both computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_continuous_gaussian_graphics.py),
    saved verbatim to raw/l04_figures.txt;
  * the slides' worked examples (gaps between customers, the delivery window, the pastry rate,
    croissants and loaves, hot days and iced coffee), computed here from their raw inputs, with the
    figure script's two simulations (20,000 gaps, 300 trading days) regenerated from its seeds.

`compute()` is pure, so test_l04.py can check every value against what the slides print.
Running this file writes raw/l04_numbers.json, which the video reads; the video types no number.
    uv run python statistics/capture_l04.py
    uv run python -m unittest discover -s statistics -p 'test_l04.py'
"""
import json
import os
import subprocess
from math import erf, exp, lgamma, log, pi, sqrt
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
FIGURE_SCRIPT = REPO / "statistics/scripts/generate_continuous_gaussian_graphics.py"

# ─── raw inputs: the only typed numbers (all from the slides) ─────────────
RATE = 0.4                                  # customers per minute (Lecture 3: 4 per ten minutes)
N_GAPS, GAP_SEED = 20_000, 4                # the figure's simulated gaps
BINS = (2.0, 0.25)                          # histogram bin widths, minutes
HIST_MAX = 12                               # minutes shown
EXACT = 2.5                                 # "no stopwatch reads exactly 2.5"
BETWEEN = (2, 3)                            # "between 2 and 3 minutes there are infinitely many answers"
ALERT_Q = 0.99                              # an alert for the slowest one percent of requests
WITHIN = 2                                  # will the next customer arrive within 2 minutes?
LULL = 5                                    # a quiet stretch of 5 minutes or more
WAITED = 3                                  # memoryless: already waited 3 minutes
WINDOW_30S = 0.5                            # a delivery within a 30-second window, minutes
DELIVERY = 10                               # "within ten minutes"
FIRST = 3                                   # lands in the first three minutes
LAST = 2                                    # section 3's pause: lands in the last two minutes
U_HALF, U_TASK = 0.5, 0.9                   # inverse-CDF draws (slide; section 4's pause)
PASTRY_FIRST = (3, 10)                      # 3 of the first 10 orders had a pastry
PASTRY_MORE = (30, 100)                     # 30 of 100
PLAUSIBLE = (0.2, 0.45)                     # shares that "would hardly surprise us" on ten orders
CLICKS = ((12, 15), (800, 1000))            # 12 correct of 15 is not 800 of 1000
MU, SIGMA = 60.0, 2.0                       # croissants, grams
SIGMA_TIGHT = 1.5                           # the tightened process
LABEL_MIN = 55.0                            # "55 g or more"
LIGHT_CROISSANT = 57.0
LOAF_MU, LOAF_SIGMA, LOAF = 500.0, 15.0, 480.0
HEAVY_CROISSANT = 63.0                      # section 8's pause
DAYS, DAY_SEED = 300, 11                    # the figure's simulated trading days
DAY_MU, DAY_SD, DAY_RHO = (22.0, 40.0), (6.0, 12.0), 0.8
ODD_DAY = (28.0, 25.0)                      # 28 °C and only 25 cups
INIT_SD, INIT_BAND = 0.1, 0.2               # section 10's pause: weights N(0, 0.1²), within ±0.2
# draft 2 (depth): the inputs of the added lines
ROUNDED = (2.45, 2.55)                      # a stopwatch reading 2.5 means this range
SHORT = 0.1                                 # the first six seconds, minutes (density × length)
FAR = 10                                    # F(10) on the running total
WAITED_DELIVERY = 8                         # waited 8 of the promised 10 minutes
PRIOR = (1, 1)                              # Beta(1, 1) before any order
DICE = (1, 2, 10)                           # sums of 1, 2 and 10 dice drift toward the bell
MU_UP = 61.0                                # the other lever: raise the mean, sigma stays 2


def Phi(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def expo_cdf(x, lam=RATE):
    return 1 - exp(-lam * x)


def beta_mean_sd(a, b):
    return a / (a + b), sqrt(a * b / ((a + b) ** 2 * (a + b + 1)))


def beta_pdf(x, a, b):
    if x <= 0 or x >= 1:
        return 0.0
    return exp(lgamma(a + b) - lgamma(a) - lgamma(b) + (a - 1) * log(x) + (b - 1) * log(1 - x))


def compute():
    V = {}
    # section 1: from bars to a density
    rng = np.random.default_rng(GAP_SEED)
    gaps = rng.exponential(1 / RATE, size=N_GAPS)
    V["rate"], V["mean_gap"] = RATE, 1 / RATE
    V["n_gaps"], V["gaps_mean"] = N_GAPS, float(gaps.mean())
    V["hist"] = {}
    for w in BINS:
        edges = np.arange(0, HIST_MAX + w, w)
        dens, _ = np.histogram(gaps, bins=edges, density=False)
        V["hist"][str(w)] = {"width": w, "edges": edges.tolist(), "counts": dens.tolist(),
                             "heights": (dens / (N_GAPS * w)).tolist(), "bars": len(edges) - 1}
    V["exact"], V["between"] = EXACT, list(BETWEEN)
    V["window_30s"], V["window_density"] = WINDOW_30S, 1 / WINDOW_30S
    V["pdf_curve"] = [[x, RATE * exp(-RATE * x)] for x in np.linspace(0, HIST_MAX, 241).tolist()]

    # section 2: area, and the CDF
    V["within"], V["p_within"] = WITHIN, expo_cdf(WITHIN)
    V["lull"], V["p_lull"] = LULL, 1 - expo_cdf(LULL)
    V["F_lull"], V["F_within"] = expo_cdf(LULL), expo_cdf(WITHIN)
    V["p_between"] = expo_cdf(LULL) - expo_cdf(WITHIN)
    V["alert_q"], V["alert_x"] = ALERT_Q, -log(1 - ALERT_Q) / RATE

    # section 3: uniform and exponential, memorylessness
    V["delivery"], V["delivery_density"] = DELIVERY, 1 / DELIVERY
    V["first"], V["p_first"] = FIRST, FIRST / DELIVERY
    V["last"], V["p_last"] = LAST, LAST / DELIVERY
    V["waited"] = WAITED
    V["p_more_given"] = (1 - expo_cdf(LULL)) / (1 - expo_cdf(WAITED))
    V["p_more_than_2"] = 1 - expo_cdf(LULL - WAITED)

    # section 4: every random number starts uniform
    V["u_half"], V["x_half"] = U_HALF, -log(1 - U_HALF) / RATE
    V["u_task"], V["x_task"] = U_TASK, -log(1 - U_TASK) / RATE
    V["median_gap_check"] = float(np.mean(gaps < V["x_half"]))

    # section 5: Beta
    V["beta"] = {}
    for k, (s, n) in (("first", PASTRY_FIRST), ("more", PASTRY_MORE)):
        a, b = s + 1, n - s + 1
        m, sd = beta_mean_sd(a, b)
        V["beta"][k] = {"successes": s, "n": n, "a": a, "b": b, "mean": m, "sd": sd,
                        "curve": [[x, beta_pdf(x, a, b)] for x in np.linspace(0, 1, 201).tolist()]}
    V["beta_plausible"] = list(PLAUSIBLE)
    grid = np.linspace(0, 1, 401).tolist()
    a, b = V["beta"]["first"]["a"] + 1, V["beta"]["first"]["b"]
    V["beta_next"] = {"a": a, "b": b, "mean": a / (a + b), "curve": [[x, beta_pdf(x, a, b)] for x in grid]}
    V["clicks"] = [{"correct": c, "n": n, "a": c + 1, "b": n - c + 1, "sd": beta_mean_sd(c + 1, n - c + 1)[1],
                    "curve": [[x, beta_pdf(x, c + 1, n - c + 1)] for x in grid]} for c, n in CLICKS]

    # section 6: the normal distribution, 68-95-99.7
    V["mu"], V["sigma"] = MU, SIGMA
    V["rule"] = {str(k): 2 * Phi(k) - 1 for k in (1, 2, 3)}
    V["rule_ranges"] = {str(k): [MU - k * SIGMA, MU + k * SIGMA] for k in (1, 2, 3)}
    V["normal_curve"] = [[x, exp(-(x - MU) ** 2 / (2 * SIGMA ** 2)) / (SIGMA * sqrt(2 * pi))]
                         for x in np.linspace(MU - 4 * SIGMA, MU + 4 * SIGMA, 241).tolist()]

    # section 7: the label's promise
    V["label_min"] = LABEL_MIN
    V["label_z"] = (LABEL_MIN - MU) / SIGMA
    V["label_short"] = Phi(V["label_z"])
    V["label_per_1000"] = 1000 * V["label_short"]
    V["sigma_tight"] = SIGMA_TIGHT
    V["tight_z"] = (LABEL_MIN - MU) / SIGMA_TIGHT
    V["tight_short"] = Phi(V["tight_z"])
    V["tight_per_10000"] = 10_000 * V["tight_short"]
    V["three_sigma_outside"] = 1 - V["rule"]["3"]

    # section 8: z-scores
    V["light"], V["z_light"], V["p_light"] = LIGHT_CROISSANT, (LIGHT_CROISSANT - MU) / SIGMA, Phi((LIGHT_CROISSANT - MU) / SIGMA)
    V["loaf_mu"], V["loaf_sigma"], V["loaf"] = LOAF_MU, LOAF_SIGMA, LOAF
    V["z_loaf"], V["p_loaf"] = (LOAF - LOAF_MU) / LOAF_SIGMA, Phi((LOAF - LOAF_MU) / LOAF_SIGMA)
    V["heavy"], V["z_heavy"] = HEAVY_CROISSANT, (HEAVY_CROISSANT - MU) / SIGMA

    # section 9: hot days and iced coffee (same generator and seed as the figure script)
    rng = np.random.default_rng(DAY_SEED)
    sd_t, sd_c = DAY_SD
    cov = np.array([[sd_t ** 2, DAY_RHO * sd_t * sd_c], [DAY_RHO * sd_t * sd_c, sd_c ** 2]])
    days = rng.multivariate_normal(np.array(DAY_MU), cov, size=DAYS)
    mu_hat, cov_hat = days.mean(axis=0), np.cov(days.T)
    sds = np.sqrt(np.diag(cov_hat))
    V["days"] = days.round(3).tolist()
    V["n_days"] = DAYS
    V["day_mean"] = mu_hat.tolist()
    V["day_cov"] = cov_hat.tolist()
    V["day_sd"] = sds.tolist()
    V["day_corr"] = float(cov_hat[0, 1] / (sds[0] * sds[1]))
    vals, vecs = np.linalg.eigh(cov_hat)
    order = vals.argsort()[::-1]
    V["day_axes"] = {"vals": vals[order].tolist(), "vecs": vecs[:, order].T.tolist()}
    d = np.array(ODD_DAY) - mu_hat
    V["odd_day"] = list(ODD_DAY)
    V["odd_z"] = (d / sds).tolist()
    V["odd_mahalanobis"] = float(sqrt(d @ np.linalg.inv(cov_hat) @ d))

    # section 10: weights drawn from N(0, sd²)
    V["init_sd"], V["init_band"] = INIT_SD, INIT_BAND
    V["init_within"] = 2 * Phi(INIT_BAND / INIT_SD) - 1

    # draft 2: the added angles
    D = V["depth"] = {}
    D["rounded"], D["p_rounded"] = list(ROUNDED), expo_cdf(ROUNDED[1]) - expo_cdf(ROUNDED[0])
    first = V["hist"]["2.0"]
    D["first_bar_count"], D["first_bar_share"] = first["counts"][0], first["counts"][0] / N_GAPS
    D["first_bar_height"] = D["first_bar_share"] / first["width"]
    D["short"], D["short_estimate"], D["short_exact"] = SHORT, RATE * SHORT, expo_cdf(SHORT)
    D["far"], D["F_far"] = FAR, expo_cdf(FAR)
    D["uniform_mean"] = DELIVERY / 2
    D["waited_delivery"] = WAITED_DELIVERY
    D["p_rest_given_waited"] = (DELIVERY - WAITED_DELIVERY) / (DELIVERY - WAITED_DELIVERY)
    D["median_gap"], D["mean_gap"] = V["x_half"], 1 / RATE
    D["prior"] = list(PRIOR)
    D["beta_sd_ratio"] = V["beta"]["first"]["sd"] / V["beta"]["more"]["sd"]
    D["data_ratio"] = PASTRY_MORE[1] / PASTRY_FIRST[1]
    D["clicks_share"] = [c / n for c, n in CLICKS]
    D["clicks_sd_ratio"] = V["clicks"][0]["sd"] / V["clicks"][1]["sd"]
    D["dice"] = {}
    for k in DICE:
        pmf = np.array([1.0])
        for _ in range(k):
            pmf = np.convolve(pmf, np.full(6, 1 / 6))
        D["dice"][str(k)] = {"sums": list(range(k, 6 * k + 1)), "pmf": pmf.tolist(),
                             "mode": k + int(pmf.argmax()), "p_mode": float(pmf.max())}
    D["one_in_outside"] = {str(k): 1 / (1 - V["rule"][str(k)]) for k in (1, 2, 3)}
    D["mu_up"], D["mu_up_z"] = MU_UP, (LABEL_MIN - MU_UP) / SIGMA
    D["mu_up_per_10000"] = 10_000 * Phi(D["mu_up_z"])
    D["ruler"] = {"croissant": [MU + k * SIGMA for k in range(-2, 3)],
                  "loaf": [LOAF_MU + k * LOAF_SIGMA for k in range(-2, 3)]}
    prod = (days[:, 0] - mu_hat[0]) * (days[:, 1] - mu_hat[1])
    D["cov_positive_days"] = int((prod > 0).sum())
    D["cov_from_products"] = float(prod.sum() / (DAYS - 1))
    D["expected_cups_at_28"] = float(mu_hat[1] + cov_hat[0, 1] / cov_hat[0, 0] * (ODD_DAY[0] - mu_hat[0]))
    D["cups_short"] = D["expected_cups_at_28"] - ODD_DAY[1]
    D["pca_share"] = float(V["day_axes"]["vals"][0] / sum(V["day_axes"]["vals"]))
    return V


def figure_output():
    adv_ai = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
    r = subprocess.run([adv_ai, str(FIGURE_SCRIPT)], capture_output=True, text=True, cwd=REPO / "statistics")
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "l04_figures.txt").write_text(figure_output())
    (OUT / "l04_numbers.json").write_text(json.dumps(compute(), indent=1, ensure_ascii=False))
    print("wrote raw/l04_figures.txt and raw/l04_numbers.json")
