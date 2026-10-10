"""Capture every number the Lecture 1 videos speak or show.

Two sources, both computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_data_probability_graphics.py),
    saved verbatim to raw/l01_figures.txt;
  * the slides' hand-worked examples (five salaries, commute times, nine salaries, cards,
    dice, birthdays), recomputed here and asserted against what the slides print.
The videos read raw/l01_numbers.json and type no number themselves.
"""
import json
import os
import subprocess
from fractions import Fraction
from math import prod
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
OUT.mkdir(exist_ok=True)

# ─── the figure script, verbatim ──────────────────────────────────────────
# The adv_ai env's interpreter, called directly: under `uv run`, PATH puts the uv venv
# first, so `conda run -n adv_ai python3` resolves to the wrong Python.
ADV_AI = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
fig = subprocess.run([ADV_AI, str(REPO / "statistics/scripts/generate_data_probability_graphics.py")],
                     capture_output=True, text=True, cwd=REPO / "statistics")
assert fig.returncode == 0, fig.stderr[-2000:]
fig = fig.stdout
(OUT / "l01_figures.txt").write_text(fig)
for must in ("rejected=11 of 1000", "rejected=210 of 1000", "n=23", "0.5073", "311"):
    assert must in fig, f"figure script output changed: {must!r} missing"

V = {}

# ─── data types (no numbers, but the examples are fixed here) ─────────────
# ─── histogram classes (from the same salaries as video 1) ───────────────
sal = np.loadtxt(OUT / "v01_salaries.txt")
edges = np.arange(20_000, 160_001, 20_000)
counts, _ = np.histogram(sal, bins=edges)
V["hist_edges"] = edges.tolist()
V["hist_counts"] = counts.tolist()
V["sal_min"], V["sal_max"] = float(sal.min()), float(sal.max())
V["sal_range"] = float(sal.max() - sal.min())
V["hist_k"] = 7
V["hist_width_raw"] = V["sal_range"] / 7
assert counts.tolist() == [156, 311, 89, 32, 7, 3, 2], counts

# ─── five salaries: notation, mean, median ────────────────────────────────
five = [31, 45, 47, 52, 88]
V["five"] = five
V["five_sum"] = sum(five)
V["five_mean"] = sum(five) / len(five)
V["five_median"] = sorted(five)[len(five) // 2]
four = five[:-1]
V["four"] = four
V["four_median"] = (four[1] + four[2]) / 2
V["five_above_mean"] = sum(x < V["five_mean"] for x in five)
assert (V["five_sum"], V["five_mean"], V["five_median"], V["four_median"]) == (263, 52.6, 47, 46.0)
assert V["five_above_mean"] == 4
V["x2"], V["x1_plus_x5"] = five[1], five[0] + five[4]
V["above_80k"] = int(counts[3:].sum())
assert (V["x2"], V["x1_plus_x5"], V["above_80k"]) == (45, 119, 44)

# ─── commute: same mean, different variance ───────────────────────────────
bus, car = [30, 29, 31, 30, 30], [18, 42, 25, 35, 30]
for name, xs in (("bus", bus), ("car", car)):
    m = sum(xs) / len(xs)
    dev = [x - m for x in xs]
    sq = [d * d for d in dev]
    V[name] = xs
    V[f"{name}_mean"] = m
    V[f"{name}_dev"] = dev
    V[f"{name}_sq"] = sq
    V[f"{name}_ss"] = sum(sq)
    V[f"{name}_var"] = sum(sq) / (len(xs) - 1)
    V[f"{name}_std"] = float(np.sqrt(V[f"{name}_var"]))
V["car_worst_late"] = max(car) - V["car_mean"]
assert (V["bus_mean"], V["car_mean"], V["bus_ss"], V["car_ss"]) == (30, 30, 2, 338)
assert (V["bus_var"], V["car_var"], V["car_worst_late"]) == (0.5, 84.5, 12)

# ─── bottles (parsed from the figure script) ──────────────────────────────
import re
rej = dict(re.findall(r"Machine (\w): .*?rejected=(\d+) of 1000", fig))
V["bottle_A_rejected"], V["bottle_B_rejected"] = int(rej["A"]), int(rej["B"])
V["bottle_ratio"] = round(V["bottle_B_rejected"] / V["bottle_A_rejected"])
V["branches"] = [dict(zip(("name", "median", "q1", "q3", "iqr"), (m[0], *map(float, m[1:]))))
                 for m in re.findall(r"Branch (\w): median=([\d.]+)min\s+Q1=([\d.]+)\s+Q3=([\d.]+)\s+IQR=([\d.]+)", fig)]
assert [b["name"] for b in V["branches"]] == ["A", "B", "C"]
assert V["bottle_ratio"] == 19

# ─── nine salaries: quartiles, IQR, fences ────────────────────────────────
nine = [31, 38, 42, 45, 47, 49, 52, 61, 88]
lo, hi = nine[:4], nine[5:]
V["nine"] = nine
V["q1"] = (lo[1] + lo[2]) / 2
V["q2"] = nine[4]
V["q3"] = (hi[1] + hi[2]) / 2
V["iqr"] = V["q3"] - V["q1"]
V["fence_lo"] = V["q1"] - 1.5 * V["iqr"]
V["fence_hi"] = V["q3"] + 1.5 * V["iqr"]
V["outliers"] = [x for x in nine if x > V["fence_hi"] or x < V["fence_lo"]]
assert (V["q1"], V["q2"], V["q3"], V["iqr"], V["fence_hi"]) == (40, 47, 56.5, 16.5, 81.25)
assert V["outliers"] == [88]

# ─── probability: die, cards, birthdays ───────────────────────────────────
omega = set(range(1, 7))
even, gt4 = {2, 4, 6}, {5, 6}
V["p_even"] = str(Fraction(len(even), 6))
V["p_gt4"] = str(Fraction(len(gt4), 6))
V["p_even_and_gt4"] = str(Fraction(len(even & gt4), 6))
assert Fraction(len(even & gt4), 6) == Fraction(len(even), 6) * Fraction(len(gt4), 6)
hearts, kings, both = 13, 4, 1
V["cards"] = {"hearts": hearts, "kings": kings, "both": both, "union": hearts + kings - both}
assert V["cards"]["union"] == 16
# multiplication rule on the king of hearts, and the complement of "heart or king"
V["p_heart"], V["p_king_given_heart"] = str(Fraction(13, 52)), str(Fraction(1, 13))
V["p_king_of_hearts"] = str(Fraction(13, 52) * Fraction(1, 13))
assert Fraction(13, 52) * Fraction(1, 13) == Fraction(1, 52)
V["neither"] = 52 - V["cards"]["union"]
assert V["neither"] == 36
# even vs odd: exclusive, so dependent; even vs "less than 3": independent
odd, lt3 = {1, 3, 5}, {1, 2}
V["p_even_times_odd"] = str(Fraction(3, 6) * Fraction(3, 6))
V["p_even_and_odd"] = str(Fraction(len(even & odd), 6))
V["p_lt3"] = str(Fraction(len(lt3), 6))
V["p_even_and_lt3"] = str(Fraction(len(even & lt3), 6))
assert Fraction(len(even & lt3), 6) == Fraction(1, 2) * Fraction(1, 3)
assert (V["p_even_times_odd"], V["p_even_and_odd"]) == ("1/4", "0")
# empirical probability on our own salaries
V["p_40_60k"] = counts[1] / len(sal)
assert round(V["p_40_60k"], 3) == 0.518

bday = {n: 1 - prod((365 - k) / 365 for k in range(n)) for n in (10, 23, 30, 50, 70)}
V["bday"] = {str(n): p for n, p in bday.items()}
assert round(bday[23], 4) == 0.5073
V["bday_first_over_half"] = next(n for n in range(1, 366)
                                 if 1 - prod((365 - k) / 365 for k in range(n)) > 0.5)
assert V["bday_first_over_half"] == 23
V["bday_pairs_23"] = 23 * 22 // 2

# ─── arrays the pictures are drawn from (regenerated with the figure script's seeds) ──
# Same generators, same order of draws as generate_data_probability_graphics.py, then
# checked against the stdout it printed, so the video draws the slides' own data.
A = {}
rng3 = np.random.default_rng(11)
for name, sd in (("A", 2.0), ("B", 4.0)):
    f = rng3.normal(500.0, sd, size=1000)
    A[f"fills_{name}"] = f.tolist()
    bad = (f < 495) | (f > 505)
    assert int(bad.sum()) == V[f"bottle_{name}_rejected"]
    V[f"bottle_{name}_mean"] = float(f.mean())
    V[f"bottle_{name}_std"] = float(f.std(ddof=1))
    V[f"bottle_{name}_limits_sd"] = 5.0 / sd
assert f"mean={V['bottle_B_mean']:.2f}ml  std={V['bottle_B_std']:.2f}ml" in fig
# machine B with its mean moved off-centre: every shift rejects more bottles
fB = np.array(A["fills_B"])
V["bottle_B_shift"] = {str(d): int(((fB + d < 495) | (fB + d > 505)).sum()) for d in range(-3, 4)}
assert min(V["bottle_B_shift"].values()) == V["bottle_B_shift"]["0"] == 210

rng4 = np.random.default_rng(5)
for b, (med, sig) in zip(V["branches"], ((12.0, 0.16), (18.0, 0.34), (28.0, 0.50))):
    w = rng4.lognormal(np.log(med), sig, size=200)
    q1, q2, q3 = np.percentile(w, [25, 50, 75])
    iqr = q3 - q1
    assert (round(q1, 1), round(q2, 1), round(q3, 1)) == (b["q1"], b["median"], b["q3"]), b
    lo_f, hi_f = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    b.update(q1x=q1, medx=q2, q3x=q3, iqrx=iqr,
             wlo=float(w[w >= lo_f].min()), whi=float(w[w <= hi_f].max()),
             fliers=sorted(float(v) for v in w[(w < lo_f) | (w > hi_f)]))
    A[f"waits_{b['name']}"] = w.tolist()
assert [len(b["fliers"]) for b in V["branches"]] == [2, 3, 3]

# Anscombe's quartet: the published data, as in the figure script
x123 = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
quartet = {
    "I": (x123, [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
    "II": (x123, [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
    "III": (x123, [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]),
    "IV": ([8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8], [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]),
}
V["anscombe"] = {}
for name, (x, y) in quartet.items():
    x, y = np.array(x, float), np.array(y)
    slope, icept = np.polyfit(x, y, 1)
    st = dict(x=x.tolist(), y=y.tolist(), mean_x=x.mean(), mean_y=y.mean(), var_x=x.var(ddof=1),
              corr=float(np.corrcoef(x, y)[0, 1]), slope=float(slope), intercept=float(icept))
    row = re.search(rf"^{name}\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+[\d.]+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$", fig, re.M)
    assert row and tuple(map(float, row.groups())) == tuple(round(st[k], 3) for k in
            ("mean_x", "mean_y", "var_x", "corr", "slope", "intercept")), name
    V["anscombe"][name] = st

# birthday curve, one point per group size
V["bday_curve"] = [1 - prod((365 - k) / 365 for k in range(n)) for n in range(1, 71)]
assert abs(V["bday_curve"][22] - V["bday"]["23"]) < 1e-12

# section 3: a continuous variable never repeats; section 5: one typo (52 -> 520)
assert len(np.unique(sal)) == len(sal)
V["five_typo"] = [31, 45, 47, 520, 88]
V["five_typo_mean"] = sum(V["five_typo"]) / 5
V["five_typo_median"] = sorted(V["five_typo"])[2]
assert (V["five_typo_mean"], V["five_typo_median"]) == (146.2, 47)
V["sal_median"] = float(np.median(sal))
V["sal_mean"] = float(sal.mean())
# section 7's closing question: how much one extreme value moves the variance
V["nine_var"] = float(np.var(nine, ddof=1))
V["eight_var"] = float(np.var(nine[:-1], ddof=1))
(OUT / "l01_arrays.json").write_text(json.dumps(A) + "\n")

(OUT / "l01_numbers.json").write_text(json.dumps(V, indent=2) + "\n")
for k, v in V.items():
    print(f"{k:22s} {v}")
