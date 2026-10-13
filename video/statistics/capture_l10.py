"""Capture every number the Lecture 10 video speaks or shows.

Two sources, both computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_evaluation_graphics.py),
    saved verbatim to raw/l10_figures.txt;
  * the slides' worked examples (twenty days of iced-coffee sales, five folds, the bootstrap, two menu layouts,
    many tests at once, two forecasters), computed here from their raw inputs. The sales days, the bootstrap
    resamples, the shuffles and the forecasts are the figure script's own, regenerated from its seeds.

`compute()` is pure, so test_l10.py can check every value against what the slides print.
Running this file writes raw/l10_numbers.json, which the video reads; the video types no number.
    uv run python statistics/capture_l10.py
    uv run python -m unittest discover -s statistics -p 'test_l10.py'
"""
import json
import os
import subprocess
from math import exp, sqrt
from pathlib import Path

import numpy as np
from scipy.stats import norm

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
FIGURE_SCRIPT = REPO / "statistics/scripts/generate_evaluation_graphics.py"

# ─── raw inputs: the only typed numbers (all from the slides and the figure script) ─────────────
SALES_SEED, TEMP_LO, TEMP_HI, NOISE_SD = 10, 16.0, 34.0, 2.5   # the script's simulated days
N_TRAIN, N_TEST = 20, 40
SHOWN = (1, 3, 9)                               # the three fits on the slide
DEGREES = range(1, 11)
K, FOLD_SEED, CV_DEGREE = 5, 5, 3
BOOT_SEED, BOOT_B, CI = 2024, 10_000, 0.95
MENU = {"A": (21, 60), "B": (30, 60)}           # buyers, customers shown the menu
PERM_SEED, PERM_P = 7, 20_000
ALPHA = 0.05
BIG_N, BIG_GAP = 200_000, 0.004                 # "a gap of 0.4 points with 200,000 customers per menu"
ACCURACY = ((0.90, 1000), (0.90, 10_000))       # "0.3 % is not a difference"
ACC_TASK_N = 4000                               # section 6's pause: four times the test set
RIVAL = (0.900, 0.903)
TESTS = (1, 10, 20, 50)
CAL_SEED, PER_BUCKET, SQUASH = 99, 400, 0.55
BUCKETS = (0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95)
RAIN = {"said": 0.70, "days": 100, "honest": 70, "other": 45}   # the everyday forecasters
SCORES, TEMPERATURE = (2.0, 0.0), 2.0           # section 10: two class scores, divided by T
BV_SEED, BV_REPEATS, BV_AT = 11, 2000, (25.0, 30.0)   # section 4: refit on fresh twenty-day samples, read off at 25 and 30 C
SCREEN = {"tested": 10_000, "ill": 100, "false_pos": 495}       # Lecture 2's screening test (raw/l02_numbers.json)
MODULE_MAP = [                                  # "Where Module 0 goes next": (lecture, idea, module, lecture)
    (2, "Bayes formulasi", 3, 6), (5, "maksimal haqiqatga oʻxshashlik", 1, 13), (6, "maksimal aposterior baho", 1, 12),
    (7, "entropiya", 1, 5), (9, "kovariatsiya", 1, 2), (10, "baholash", 1, 14)]


def truth(t):
    """The script's true sales curve: flat while cool, climbing once hot."""
    return 6.0 + 26.0 / (1.0 + np.exp(-(t - 27.0) / 2.0))


def days():
    """The script's twenty training and forty test days, regenerated from its seed in its order."""
    rng = np.random.default_rng(SALES_SEED)

    def make(n):
        t = rng.uniform(TEMP_LO, TEMP_HI, size=n)
        y = truth(t) + rng.normal(0.0, NOISE_SD, size=n)
        return np.sort(t), y[np.argsort(t)]
    return make(N_TRAIN), make(N_TEST)


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def fit(t, y, d):
    return np.polynomial.Polynomial.fit(t, y, d)


def p_two_sided(z):
    return float(2 * (1 - norm.cdf(abs(z))))


def compute():
    V = {}
    (tt, yt), (te, ye) = days()
    V["n_train"], V["n_test"], V["noise_sd"] = N_TRAIN, N_TEST, NOISE_SD

    # sections 1, 3, 4: fits of every degree, error on the training and the test days
    V["fits"] = {}
    for d in DEGREES:
        m = fit(tt, yt, d)
        V["fits"][str(d)] = {"train": rmse(yt, m(tt)), "test": rmse(ye, m(te))}
    f = V["fits"]
    V["best_degree"] = min(DEGREES, key=lambda d: f[str(d)]["test"])
    V["ratio_9"] = f["9"]["test"] / f["9"]["train"]
    V["gap"] = {str(d): f[str(d)]["test"] - f[str(d)]["train"] for d in SHOWN}
    V["train_falls"] = all(f[str(d + 1)]["train"] <= f[str(d)]["train"] for d in range(1, 10))
    g = np.linspace(tt.min(), tt.max(), 4001)
    m9 = fit(tt, yt, 9)(g)
    V["deg9_min"] = {"temp": float(g[m9.argmin()]), "sales": float(m9.min())}
    V["above_noise_3"] = f["3"]["test"] - NOISE_SD
    V["shown_curves"] = {str(d): [[float(x), float(y)] for x, y in zip(g[::40], fit(tt, yt, d)(g[::40]))] for d in SHOWN}
    V["train_days"] = [[float(x), float(y)] for x, y in zip(tt, yt)]

    # section 4: bias and variance, measured by refitting on fresh twenty-day samples
    rng = np.random.default_rng(BV_SEED)
    at = np.array(BV_AT)
    preds = {d: [] for d in SHOWN}
    for _ in range(BV_REPEATS):
        t = rng.uniform(TEMP_LO, TEMP_HI, N_TRAIN)
        y = truth(t) + rng.normal(0.0, NOISE_SD, N_TRAIN)
        for d in SHOWN:
            preds[d].append(fit(t, y, d)(at))
    V["bv_truth"] = {f"{x:g}": float(truth(x)) for x in BV_AT}
    V["bv"] = {f"{x:g}": {str(d): {"mean": float(np.mean(np.array(p)[:, i])),
                                    "bias": float(np.mean(np.array(p)[:, i]) - truth(x)),
                                    "sd": float(np.std(np.array(p)[:, i]))} for d, p in preds.items()}
               for i, x in enumerate(BV_AT)}

    # section 5: five folds of the twenty training days, degree 3, and the same folds for every degree
    order = np.random.default_rng(FOLD_SEED).permutation(N_TRAIN)
    folds = np.array_split(order, K)

    def cv(d):
        s = []
        for k in range(K):
            tr = np.concatenate([folds[j] for j in range(K) if j != k])
            s.append(rmse(yt[folds[k]], fit(tt[tr], yt[tr], d)(tt[folds[k]])))
        return s
    s3 = cv(CV_DEGREE)
    V["folds"] = s3
    V["cv_mean"], V["cv_sd"] = float(np.mean(s3)), float(np.std(s3, ddof=1))
    V["cv_by_degree"] = {str(d): float(np.mean(cv(d))) for d in DEGREES}
    V["cv_best_degree"] = min(DEGREES, key=lambda d: V["cv_by_degree"][str(d)])
    V["fold_size"], V["times_trained"] = N_TRAIN // K, K - 1
    V["fold_sum_shown"] = round(sum(round(x, 2) for x in V["folds"]), 2)   # section 5's pause, from the rounded folds

    # section 6: the bootstrap on the degree-3 test error, and the standard error of an accuracy
    resid = ye - fit(tt, yt, CV_DEGREE)(te)
    brng = np.random.default_rng(BOOT_SEED)
    boot, distinct = np.empty(BOOT_B), np.empty(BOOT_B)
    for b in range(BOOT_B):
        idx = brng.integers(0, N_TEST, size=N_TEST)
        boot[b] = sqrt(float(np.mean(resid[idx] ** 2)))
        distinct[b] = len(set(idx.tolist()))
    lo, hi = np.percentile(boot, [100 * (1 - CI) / 2, 100 * (1 + CI) / 2])
    sd = float(boot.std(ddof=1))
    V["boot"] = {"point": rmse(ye, ye - resid), "ci": [float(lo), float(hi)], "width": float(hi - lo), "sd": sd,
                 "two_sd": [f["3"]["test"] - 2 * sd, f["3"]["test"] + 2 * sd],
                 "distinct_mean": float(distinct.mean()), "left_out_mean": float(N_TEST - distinct.mean()),
                 "left_out_share": float(1 - distinct.mean() / N_TEST)}
    V["accuracy_se"] = [{"acc": a, "n": n, "se": sqrt(a * (1 - a) / n), "half": 1.96 * sqrt(a * (1 - a) / n)}
                        for a, n in ACCURACY]
    a = ACCURACY[0][0]
    V["l3_recap"] = {"n": 100, "mean": 100 * a, "sd": sqrt(100 * a * (1 - a))}   # Lecture 3: 90 % on 100 examples
    V["accuracy_task"] = {"n": ACC_TASK_N, "half": 1.96 * sqrt(a * (1 - a) / ACC_TASK_N)}
    V["rival_gap_points"] = 100 * (RIVAL[1] - RIVAL[0])

    # sections 7-8: two menu layouts, a permutation test
    (ba, na), (bb, nb) = MENU["A"], MENU["B"]
    V["menu"] = {"A": [ba, na, ba / na], "B": [bb, nb, bb / nb], "gap": bb / nb - ba / na,
                 "pooled": (ba + bb) / (na + nb), "buyers": ba + bb, "customers": na + nb}
    outcomes = np.array([1] * ba + [0] * (na - ba) + [1] * bb + [0] * (nb - bb))
    prng, pool, diffs = np.random.default_rng(PERM_SEED), outcomes.copy(), np.empty(PERM_P)
    for i in range(PERM_P):
        prng.shuffle(pool)
        diffs[i] = pool[na:].mean() - pool[:na].mean()
    gap = V["menu"]["gap"]
    extreme = np.abs(diffs) >= abs(gap) - 1e-12
    V["perm"] = {"shuffles": PERM_P, "p": float(extreme.mean()), "as_extreme": int(extreme.sum()),
                 "one_in": float(1 / extreme.mean()), "sd": float(diffs.std()), "mean": float(diffs.mean()),
                 "gap_in_sd": float(gap / diffs.std())}
    pooled = V["menu"]["pooled"]
    se = sqrt(pooled * (1 - pooled) * (1 / na + 1 / nb))
    V["menu_se"], V["menu_z"] = se, gap / se
    V["n_needed"] = next(n for n in range(60, 1200, 10) if gap / sqrt(pooled * (1 - pooled) * 2 / n) >= 1.96)
    n = V["n_needed"]
    V["z_at_needed"] = gap / sqrt(pooled * (1 - pooled) * 2 / n)
    V["se_shrink_needed"] = sqrt(n / na)
    se_big = sqrt(pooled * (1 - pooled) * 2 / BIG_N)
    V["big"] = {"n": BIG_N, "gap": BIG_GAP, "z": BIG_GAP / se_big, "p": p_two_sided(BIG_GAP / se_big)}

    # section 9: Type I errors in Lecture 2's table, and many tests at once
    sc = SCREEN
    V["screen"] = {**sc, "positives": sc["ill"] + sc["false_pos"],
                   "false_share": sc["false_pos"] / (sc["ill"] + sc["false_pos"])}
    V["many"] = {str(m): 1 - (1 - ALPHA) ** m for m in TESTS}
    V["expected_false_50"] = 50 * ALPHA
    V["no_false_10"] = (1 - ALPHA) ** 10                          # section 9's pause: 0.95 to the tenth

    # section 10: two forecasters, 400 forecasts at each stated level
    crng = np.random.default_rng(CAL_SEED)
    rows = []
    for p in BUCKETS:
        h = int(crng.binomial(PER_BUCKET, p))
        o = int(crng.binomial(PER_BUCKET, 0.5 + SQUASH * (p - 0.5)))
        rows.append({"stated": p, "honest_hits": h, "over_hits": o, "honest": h / PER_BUCKET, "over": o / PER_BUCKET})
    V["cal"] = rows
    V["cal_gap"] = {"honest": float(np.mean([abs(r["honest"] - r["stated"]) for r in rows])),
                    "over": float(np.mean([abs(r["over"] - r["stated"]) for r in rows]))}
    top = rows[-1]
    V["cal_95"] = {"claimed": round(top["stated"] * PER_BUCKET), "honest": top["honest_hits"], "over": top["over_hits"],
                   "over_misses": PER_BUCKET - top["over_hits"], "claimed_misses": PER_BUCKET - round(top["stated"] * PER_BUCKET)}
    V["cal_05_over"] = rows[0]["over"]
    V["per_bucket"] = PER_BUCKET
    V["rain"] = dict(RAIN)
    s1, s0 = SCORES
    V["softmax"] = {"p": 1 / (1 + exp(-(s1 - s0))), "p_T": 1 / (1 + exp(-(s1 - s0) / TEMPERATURE)), "T": TEMPERATURE}
    V["module_map"] = [list(r) for r in MODULE_MAP]
    return V


def figure_output():
    adv_ai = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
    r = subprocess.run([adv_ai, str(FIGURE_SCRIPT)], capture_output=True, text=True, cwd=REPO / "statistics")
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "l10_figures.txt").write_text(figure_output())
    (OUT / "l10_numbers.json").write_text(json.dumps(compute(), indent=1, ensure_ascii=False))
    print("wrote raw/l10_figures.txt and raw/l10_numbers.json")
