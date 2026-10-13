"""Capture every number the Lecture 9 video speaks or shows.

Two sources, both computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_regression_graphics.py),
    saved verbatim to raw/l09_figures.txt;
  * the slides' worked examples (hot days and iced coffee, the fitted line and its residuals, R², total drinks,
    Anscombe's quartet, the three-column matrix, the eigenvectors, PCA), computed here from their raw inputs.
    The 300 trading days are the figure script's own (Lecture 4's sample), regenerated from its seed.

`compute()` is pure, so test_l09.py can check every value against what the slides print.
Running this file writes raw/l09_numbers.json, which the video reads; the video types no number.
    uv run python statistics/capture_l09.py
    uv run python -m unittest discover -s statistics -p 'test_l09.py'
"""
import json
import os
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
FIGURE_SCRIPT = REPO / "statistics/scripts/generate_regression_graphics.py"

# ─── raw inputs: the only typed numbers (the figure script's generators, the slides' questions) ───
DAYS_SEED, N_DAYS = 11, 300                     # Lecture 4's 300 trading days
MU, SD_T, SD_C, RHO = (22.0, 40.0), 6.0, 12.0, 0.8
TOTAL_SEED, HOT_SEED = 29, 7                    # total drinks (the U), hot drinks (third column)
F_SCALE = 1.8                                   # one Celsius degree is 1.8 Fahrenheit degrees
WARMER = 3                                      # "tomorrow is forecast 3 degrees warmer"
PREDICT_AT = 25.0                               # "at 25 °C"
EXAMPLE_T = 25.0                                # the residual on the slide: the figure script picks the day nearest 25 °C
TASK_DAY = (25.0, 35.0)                         # section 4's pause: 25 °C, 35 cups
TASK_R = 0.5                                    # section 5's pause: r = 0.5
COLD_BUSY = (15.0, 50.0)                        # section 2's pause: a cold day that sold a lot
PAIRS_K = (3, 5, 10, 100, 1000)                 # pairs among k columns
ANSCOMBE_X = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
ANSCOMBE = {                                    # the published data, as in Lecture 1
    "I": (ANSCOMBE_X, [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
    "II": (ANSCOMBE_X, [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
    "III": (ANSCOMBE_X, [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]),
    "IV": ([8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8], [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]),
}


def days():
    rng = np.random.default_rng(DAYS_SEED)
    cov = np.array([[SD_T ** 2, RHO * SD_T * SD_C], [RHO * SD_T * SD_C, SD_C ** 2]])
    return rng.multivariate_normal(np.array(MU), cov, size=N_DAYS)


def eig_sorted(m):
    vals, vecs = np.linalg.eigh(m)
    o = vals.argsort()[::-1]
    return vals[o], vecs[:, o]


def compute():
    V = {}
    d = days()
    t, c = d[:, 0], d[:, 1]
    n = len(t)
    tb, cb = t.mean(), c.mean()
    st, sc = t.std(ddof=1), c.std(ddof=1)
    S = np.cov(d.T)
    sxy = S[0, 1]
    r = float(np.corrcoef(t, c)[0, 1])
    V.update(n=n, t_mean=tb, c_mean=cb, t_sd=st, c_sd=sc, t_var=S[0, 0], c_var=S[1, 1], cov=sxy, r=r,
             r_from_cov=sxy / (st * sc), r_from_slide=49.6 / (5.65 * 11.33))

    # s1: the units problem
    V["cov_f"] = sxy * F_SCALE                                   # covariance with temperature in Fahrenheit
    V["r_f"] = V["cov_f"] / (st * F_SCALE * sc)
    V["cov_f_slide"] = 49.6 * F_SCALE                            # the slide multiplied the rounded 49.6

    # s2: quadrants, and r as the average product of z-scores
    dt, dc = t - tb, c - cb
    V["quadrants"] = {"warm_busy": int(((dt > 0) & (dc > 0)).sum()), "cold_quiet": int(((dt < 0) & (dc < 0)).sum()),
                      "cold_busy": int(((dt < 0) & (dc > 0)).sum()), "warm_quiet": int(((dt > 0) & (dc < 0)).sum())}
    V["positive_products"] = int((dt * dc > 0).sum())
    V["z_product_mean"] = float(((dt / st) * (dc / sc)).sum() / (n - 1))
    V["cold_busy_task"] = {"dt": COLD_BUSY[0] - tb, "dc": COLD_BUSY[1] - cb,
                           "product": (COLD_BUSY[0] - tb) * (COLD_BUSY[1] - cb)}

    # s3: least squares
    b = sxy / S[0, 0]
    a = cb - b * tb
    V.update(slope=b, intercept=a, slope_from_r=r * sc / st, slope_slide=49.6 / 31.9,
             intercept_slide=39.49 - (49.6 / 31.9) * 21.81)
    V["warmer_cups"] = WARMER * b
    V["pred_25"] = a + b * PREDICT_AT
    V["pred_25_rounded_line"] = 5.6 + 1.55 * PREDICT_AT
    V["pred_at_mean"] = a + b * tb
    V["one_sd_warmer_cups"] = b * st                            # a day one sd warmer sells this many more
    V["one_sd_warmer_in_sd"] = b * st / sc                      # ... which is r standard deviations of cups

    # s4: residuals
    fit = a + b * t
    e = c - fit
    i = int(np.argmin(np.abs(t - EXAMPLE_T)))
    V["example_day"] = {"t": float(t[i]), "cups": float(c[i]), "pred": float(fit[i]), "resid": float(e[i])}
    V["resid_mean"] = float(e.mean())
    V["resid_t_corr"] = float(np.corrcoef(e, t)[0, 1])
    V["resid_sd"] = float(e.std(ddof=2))
    V["task_resid"] = TASK_DAY[1] - (a + b * TASK_DAY[0])

    # s5: R squared
    ss_tot, ss_res = float((dc ** 2).sum()), float((e ** 2).sum())
    V.update(ss_tot=ss_tot, ss_res=ss_res, r2=1 - ss_res / ss_tot, r_squared=r * r)
    V["resid_var"] = ss_res / (n - 2)
    V["resid_var_share"] = V["resid_var"] / S[1, 1]
    V["task_r2"] = TASK_R ** 2

    # s6: least squares is maximum likelihood; the line plus/minus two noise sds
    V["two_sigma"] = 2 * V["resid_sd"]
    V["band_25"] = [V["pred_25"] - V["two_sigma"], V["pred_25"] + V["two_sigma"]]
    V["within_two_sigma"] = float((np.abs(e) < V["two_sigma"]).mean())

    # s7: what r cannot see -- total drinks
    rng4 = np.random.default_rng(TOTAL_SEED)
    total = 55.0 + 0.16 * (t - 21.9) ** 2 + rng4.normal(0.0, 6.0, size=n)
    sst = ((total - total.mean()) ** 2).sum()
    lin, quad = np.polyfit(t, total, 1), np.polyfit(t, total, 2)
    V["total_r"] = float(np.corrcoef(t, total)[0, 1])
    V["total_r2_line"] = float(1 - ((total - np.polyval(lin, t)) ** 2).sum() / sst)
    V["total_r2_curve"] = float(1 - ((total - np.polyval(quad, t)) ** 2).sum() / sst)
    vx = -quad[1] / (2 * quad[0])
    V["total_curve_bottom"] = [float(vx), float(np.polyval(quad, vx))]
    cold = t < tb
    V["total_r_cold"] = float(np.corrcoef(t[cold], total[cold])[0, 1])
    V["total_r_warm"] = float(np.corrcoef(t[~cold], total[~cold])[0, 1])
    V["n_cold"], V["n_warm"] = int(cold.sum()), int((~cold).sum())

    # s7: Anscombe's quartet
    V["anscombe"] = {}
    for name, (x, y) in ANSCOMBE.items():
        x, y = np.array(x, float), np.array(y)
        sl, ic = np.polyfit(x, y, 1)
        res = y - (ic + sl * x)
        k = int(np.argmax(np.abs(res)))
        V["anscombe"][name] = {"r": float(np.corrcoef(x, y)[0, 1]), "slope": float(sl), "intercept": float(ic),
                               "r2": float(np.corrcoef(x, y)[0, 1] ** 2), "max_resid": float(res[k]),
                               "max_resid_point": [float(x[k]), float(y[k])],
                               "resid_far_x": float(res[int(np.argmax(x))]),
                               "resid_signs": [int(np.sign(v)) for v in res[np.argsort(x)]]}

    # s9: three columns
    rng5 = np.random.default_rng(HOT_SEED)
    hot = np.clip(80.0 - 2.2 * t + rng5.normal(0.0, 8.0, size=n), 0.0, None)
    D3 = np.vstack([t, c, hot])
    C3, R3 = np.cov(D3), np.corrcoef(D3)
    V["cov3"], V["corr3"] = C3.tolist(), R3.tolist()
    V["pairs"] = {str(k): k * (k - 1) // 2 for k in PAIRS_K}

    def resid_on_t(y):
        bb = np.cov(t, y)[0, 1] / t.var(ddof=1)
        return y - (y.mean() + bb * (t - tb))
    V["iced_hot_without_temp"] = float(np.corrcoef(resid_on_t(c), resid_on_t(hot))[0, 1])

    # s10: eigenvectors of the temperature-and-iced-coffee block
    vals, vecs = eig_sorted(S)
    v1 = vecs[:, 0] * np.sign(vecs[0, 0])
    v2 = vecs[:, 1] * np.sign(vecs[1, 1])
    V.update(eigvals=vals.tolist(), v1=v1.tolist(), v2=v2.tolist(), v1_dot_v2=float(v1 @ v2),
             eig_sum=float(vals.sum()), trace=float(np.trace(S)), shares=(vals / vals.sum()).tolist(),
             v1_angle=float(np.degrees(np.arctan2(v1[1], v1[0]))), eig_sd=np.sqrt(vals).tolist(),
             arrow_len=(2 * np.sqrt(vals)).tolist())
    V["sigma_v1"] = (S @ v1).tolist()
    V["lambda_v1"] = (vals[0] * v1).tolist()
    pc = (d - [tb, cb]) @ np.column_stack([v1, v2])
    V["pc_score_var"] = [float(pc[:, 0].var(ddof=1)), float(pc[:, 1].var(ddof=1))]
    V["pc_score_corr"] = float(np.corrcoef(pc[:, 0], pc[:, 1])[0, 1])

    # s11: PCA follows the units; standardizing first
    SF = S * np.array([[F_SCALE ** 2, F_SCALE], [F_SCALE, 1.0]])
    vf, _ = eig_sorted(SF)
    V["f_var_factor"] = F_SCALE ** 2
    V["f_shares"] = (vf / vf.sum()).tolist()
    vr, _ = eig_sorted(np.corrcoef(d.T))
    V["std_eigvals"] = vr.tolist()
    V["std_shares"] = (vr / vr.sum()).tolist()
    V["one_plus_r"], V["one_minus_r"] = 1 + r, 1 - r
    v3, _ = eig_sorted(R3)
    V["corr3_shares"] = (v3 / v3.sum()).tolist()
    V["corr3_cum"] = np.cumsum(v3 / v3.sum()).tolist()
    return json.loads(json.dumps(V, default=float))


def figure_output():
    adv_ai = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
    r = subprocess.run([adv_ai, str(FIGURE_SCRIPT)], capture_output=True, text=True, cwd=REPO / "statistics")
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "l09_figures.txt").write_text(figure_output())
    (OUT / "l09_numbers.json").write_text(json.dumps(compute(), indent=1, ensure_ascii=False))
    print("wrote raw/l09_figures.txt and raw/l09_numbers.json")
