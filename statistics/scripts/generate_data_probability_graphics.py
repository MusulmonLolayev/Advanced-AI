#!/usr/bin/env python3
"""Generate lecture figures for statistics/lectures/lecture01_data_probability.tex

Numbers come from pandas/numpy; rendering is matplotlib, saved directly as
vector PDF (and SVG) -- see the pandas-vector-graphics skill for when this
matplotlib path applies vs. the TikZ path used by ml/'s older scripts.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "data_probability"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand palette (see statistics/theme/rl-theme.tex: RLBlue, RLGreen, RLOrange).
RLBLUE = "#3A35B7"
RLGREEN = "#5FA0A4"
RLORANGE = "#F4BD70"
RLRED = "#D6455D"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#222222",
    "text.color": "#222222",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
})


def save_fig(fig, name):
    pdf_path = OUT_DIR / f"{name}.pdf"
    svg_path = OUT_DIR / f"{name}.svg"
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    fig.savefig(svg_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"✓ {name}.pdf")
    print(f"✓ {name}.svg")


# ─── Figure 1: API latency histogram — mean vs. median under skew ──────────
print("Figure 1: latency histogram (mean vs median) …")
rng = np.random.default_rng(42)
n_req = 600
body = rng.lognormal(mean=np.log(120), sigma=0.35, size=n_req - 20)
tail = rng.uniform(500, 1100, size=20)  # occasional slow/retried requests
latency = np.concatenate([body, tail])
df_lat = pd.DataFrame({"latency_ms": latency})

lat_mean = df_lat["latency_ms"].mean()
lat_median = df_lat["latency_ms"].median()
lat_p95 = df_lat["latency_ms"].quantile(0.95)
lat_p99 = df_lat["latency_ms"].quantile(0.99)
print(f"  mean={lat_mean:.1f}ms  median={lat_median:.1f}ms  "
      f"p95={lat_p95:.1f}ms  p99={lat_p99:.1f}ms")

fig, ax = plt.subplots(figsize=(6.6, 4.0))
ax.hist(df_lat["latency_ms"], bins=40, color=RLBLUE, alpha=0.75,
        edgecolor="white", linewidth=0.4)
ax.axvline(lat_mean, color=RLRED, linewidth=2.0, linestyle="-",
           label=f"mean = {lat_mean:.0f} ms")
ax.axvline(lat_median, color=RLGREEN, linewidth=2.0, linestyle="--",
           label=f"median = {lat_median:.0f} ms")
ax.set_xlabel("Request latency (ms)")
ax.set_ylabel("Number of requests")
ax.legend(loc="upper right", frameon=False, fontsize=10)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "data_probability_latency_histogram")


# ─── Figure 2: "billionaire walks into a bar" — mean vs median ─────────────
print("\nFigure 2: mean vs median with one extreme outlier …")
rng2 = np.random.default_rng(7)
regulars = rng2.uniform(20_000, 150_000, size=9)
bezos = np.array([150_000_000_000.0])

before = pd.Series(regulars)
after = pd.Series(np.concatenate([regulars, bezos]))
print(f"  before: mean=${before.mean():,.0f}  median=${before.median():,.0f}")
print(f"  after:  mean=${after.mean():,.0f}  median=${after.median():,.0f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 3.2),
                                gridspec_kw={"width_ratios": [1, 1]})
for ax, data, title in ((ax1, before, "9 people in a bar"),
                         (ax2, after, "+ 1 billionaire walks in")):
    ax.set_xscale("log")
    ax.scatter(data, np.zeros_like(data), s=70, c=RLBLUE, edgecolors="black",
               linewidths=0.6, zorder=3, alpha=0.85)
    ax.axvline(data.mean(), color=RLRED, linewidth=2.0,
               label=f"mean = ${data.mean():,.0f}")
    ax.axvline(data.median(), color=RLGREEN, linewidth=2.0, linestyle="--",
               label=f"median = ${data.median():,.0f}")
    ax.set_yticks([])
    ax.set_xlabel("Net worth ($, log scale)")
    ax.set_title(title, fontsize=10.5, fontweight="bold")
    ax.legend(loc="upper left", frameon=False, fontsize=8.5)
    ax.set_xlim(1e4, 3e11)
fig.tight_layout()
save_fig(fig, "data_probability_billionaire_bar")


# ─── Figure 3: manufacturing tolerances — why variance, not just mean ──────
print("\nFigure 3: same mean, different variance (spec limits) …")
rng3 = np.random.default_rng(11)
spec_lo, spec_hi = 9.95, 10.05
machine_a = rng3.normal(10.00, 0.010, size=400)
machine_b = rng3.normal(10.00, 0.040, size=400)
df_mfg = pd.DataFrame({"A": machine_a, "B": machine_b})
pct_bad_a = ((df_mfg["A"] < spec_lo) | (df_mfg["A"] > spec_hi)).mean() * 100
pct_bad_b = ((df_mfg["B"] < spec_lo) | (df_mfg["B"] > spec_hi)).mean() * 100
print(f"  Machine A: mean={df_mfg['A'].mean():.4f}  std={df_mfg['A'].std():.4f}"
      f"  out-of-spec={pct_bad_a:.1f}%")
print(f"  Machine B: mean={df_mfg['B'].mean():.4f}  std={df_mfg['B'].std():.4f}"
      f"  out-of-spec={pct_bad_b:.1f}%")

fig, ax = plt.subplots(figsize=(6.8, 4.0))
bins = np.linspace(9.85, 10.15, 60)
ax.hist(df_mfg["A"], bins=bins, color=RLGREEN, alpha=0.7,
        label=f"Machine A: std={df_mfg['A'].std():.3f}mm, {pct_bad_a:.1f}% out-of-spec")
ax.hist(df_mfg["B"], bins=bins, color=RLORANGE, alpha=0.7,
        label=f"Machine B: std={df_mfg['B'].std():.3f}mm, {pct_bad_b:.1f}% out-of-spec")
ax.axvline(spec_lo, color=RLRED, linewidth=1.6, linestyle="--")
ax.axvline(spec_hi, color=RLRED, linewidth=1.6, linestyle="--",
           label="spec limits (9.95-10.05mm)")
ax.set_xlabel("Bolt diameter (mm)")
ax.set_ylabel("Count")
ax.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.95,
          edgecolor="#cccccc", fontsize=8.2)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "data_probability_variance_manufacturing")


# ─── Figure 4: box plots — latency across three data centers ───────────────
print("\nFigure 4: box plots across three data centers …")
rng4 = np.random.default_rng(3)
us_east = rng4.normal(42, 8, size=200)
us_west = np.concatenate([rng4.normal(58, 12, size=190), rng4.uniform(150, 220, size=10)])
eu = np.concatenate([rng4.normal(95, 18, size=190), rng4.uniform(250, 320, size=10)])
box_data = [us_east, us_west, eu]
labels_box = ["US-East", "US-West", "EU"]
for name, d in zip(labels_box, box_data):
    q1, med, q3 = np.percentile(d, [25, 50, 75])
    print(f"  {name}: median={med:.1f}ms  Q1={q1:.1f}  Q3={q3:.1f}  IQR={q3 - q1:.1f}")

fig, ax = plt.subplots(figsize=(6.2, 4.0))
bp = ax.boxplot(box_data, tick_labels=labels_box, patch_artist=True, widths=0.5,
                 flierprops=dict(marker="o", markerfacecolor=RLRED,
                                  markeredgecolor="black", markersize=5, alpha=0.7))
for patch, color in zip(bp["boxes"], [RLBLUE, RLGREEN, RLORANGE]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_ylabel("Request latency (ms)")
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "data_probability_boxplot_datacenters")


# ─── Figure 5: Anscombe's quartet — same summary stats, different shapes ──
print("\nFigure 5: Anscombe's quartet …")
x123 = np.array([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5], dtype=float)
y1 = np.array([8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68])
y2 = np.array([9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74])
y3 = np.array([7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73])
x4 = np.array([8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8], dtype=float)
y4 = np.array([6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89])

quartet = {
    "I": (x123, y1), "II": (x123, y2), "III": (x123, y3), "IV": (x4, y4),
}
rows = []
for name, (x, y) in quartet.items():
    r = np.corrcoef(x, y)[0, 1]
    slope, intercept = np.polyfit(x, y, 1)
    rows.append({"set": name, "mean_x": x.mean(), "mean_y": y.mean(),
                 "var_x": x.var(ddof=1), "var_y": y.var(ddof=1),
                 "corr": r, "slope": slope, "intercept": intercept})
df_ans = pd.DataFrame(rows).set_index("set")
print(df_ans.round(3))

fig, axes = plt.subplots(1, 4, figsize=(11.2, 3.0))
for ax, (name, (x, y)) in zip(axes, quartet.items()):
    ax.scatter(x, y, s=32, c=RLBLUE, edgecolors="black", linewidths=0.5, zorder=3)
    xs = np.linspace(2, 20, 50)
    slope, intercept = df_ans.loc[name, "slope"], df_ans.loc[name, "intercept"]
    ax.plot(xs, slope * xs + intercept, color=RLRED, linewidth=1.4, zorder=2)
    ax.set_title(f"Set {name}", fontsize=10, fontweight="bold")
    ax.set_xlim(2, 20)
    ax.set_ylim(2, 14)
    ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "data_probability_anscombe")


# ─── Figure 6: birthday problem — P(shared birthday) vs. group size ───────
print("\nFigure 6: birthday problem curve …")
ns = np.arange(1, 61)
p_no_share = np.ones_like(ns, dtype=float)
running = 1.0
p_share = []
for n in ns:
    if n == 1:
        running = 1.0
    else:
        running *= (365 - (n - 1)) / 365
    p_share.append(1 - running)
df_bday = pd.DataFrame({"n": ns, "p_share": p_share})
n_cross = df_bday[df_bday["p_share"] > 0.5]["n"].iloc[0]
print(f"  first group size with P(shared birthday) > 0.5: n={n_cross}")
print(f"  P(shared)|n=23 = {df_bday.loc[df_bday.n == 23, 'p_share'].iloc[0]:.4f}")

fig, ax = plt.subplots(figsize=(6.6, 4.0))
ax.plot(df_bday["n"], df_bday["p_share"], color=RLBLUE, linewidth=2.2)
ax.axhline(0.5, color="#999999", linewidth=1.0, linestyle=":")
ax.axvline(n_cross, color=RLRED, linewidth=1.6, linestyle="--")
ax.scatter([n_cross], [df_bday.loc[df_bday.n == n_cross, "p_share"].iloc[0]],
           s=60, c=RLRED, zorder=4,
           label=f"n={n_cross}: P(shared) crosses 50%")
ax.set_xlabel("People in the room (n)")
ax.set_ylabel("P(at least one shared birthday)")
ax.set_xlim(1, 60)
ax.set_ylim(0, 1.02)
ax.legend(loc="lower right", frameon=False, fontsize=9.5)
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "data_probability_birthday_problem")

print("\nAll done.")
