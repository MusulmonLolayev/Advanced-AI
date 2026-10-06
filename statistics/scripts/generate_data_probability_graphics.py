#!/usr/bin/env python3
"""Generate lecture figures for statistics/ Lecture 1 (lecture01_data_descriptive.tex)

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


# ─── Figure 1: salary histogram — mean vs. median under skew ──────────────
print("Figure 1: salary histogram (mean vs median) …")
rng = np.random.default_rng(42)
n_emp = 600
# base pay floor plus a right-skewed component, so every salary clears $20k
salary = 22_000 + rng.lognormal(mean=np.log(26_000), sigma=0.55, size=n_emp)
df_pay = pd.DataFrame({"salary": salary})

pay_min = df_pay["salary"].min()
pay_max = df_pay["salary"].max()
pay_mean = df_pay["salary"].mean()
pay_median = df_pay["salary"].median()
print(f"  n={n_emp}  min=${pay_min:,.0f}  max=${pay_max:,.0f}")
print(f"  mean=${pay_mean:,.0f}  median=${pay_median:,.0f}  "
      f"range=${pay_max - pay_min:,.0f}")

# Frequency table used in the "how to build a histogram" slide:
# range/7 rounded up to a convenient width gives 7 classes of $20k.
NUM_CLASSES = 7
CLASS_WIDTH = 20_000
edges = np.arange(20_000, 160_001, CLASS_WIDTH)
counts, _ = np.histogram(df_pay["salary"], bins=edges)
freq_table = pd.DataFrame({
    "class": [f"{lo//1000}-{hi//1000}k" for lo, hi in zip(edges[:-1], edges[1:])],
    "frequency": counts,
})
freq_table["relative %"] = (100 * freq_table["frequency"] / n_emp).round(1)
assert counts.sum() == n_emp, "some salaries fall outside the class limits"
print(f"  suggested width = range/{NUM_CLASSES} = "
      f"${(pay_max - pay_min) / NUM_CLASSES:,.0f} -> rounded to ${CLASS_WIDTH:,}")
print(freq_table.to_string(index=False))

fig, ax = plt.subplots(figsize=(6.6, 4.0))
ax.hist(df_pay["salary"], bins=edges, color=RLBLUE, alpha=0.75,
        edgecolor="white", linewidth=0.8)
ax.axvline(pay_mean, color=RLRED, linewidth=2.0, linestyle="-",
           label=f"mean = \\${pay_mean/1000:.0f}k")
ax.axvline(pay_median, color=RLGREEN, linewidth=2.0, linestyle="--",
           label=f"median = \\${pay_median/1000:.0f}k")
ax.set_xlabel("Annual salary ($1000s)")
ax.set_ylabel("Number of employees")
ax.set_xticks(edges)
ax.set_xticklabels([f"{e//1000}" for e in edges])
ax.legend(loc="upper right", frameon=False, fontsize=10)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "data_probability_salary_histogram")


# ─── Figure 2: "billionaire walks into a bar" — mean vs median ─────────────
# The drinkers are 50 of the same 600 employees from Figure 1, so the video and
# the slides can say "fifty of these people go for a drink" and mean the same
# people. A larger group also puts the mean and the median close together
# before the outlier arrives, which is the whole point of the comparison.
print("\nFigure 2: mean vs median with one extreme outlier …")
N_DRINKERS = 50
step = n_emp // N_DRINKERS                      # evenly spread across the whole payroll
regulars = np.sort(df_pay["salary"].to_numpy())[::step][:N_DRINKERS]
bezos = np.array([150_000_000_000.0])

before = pd.Series(regulars)
after = pd.Series(np.concatenate([regulars, bezos]))
print(f"  drinkers = {N_DRINKERS} of the {n_emp} employees")
print(f"  before: mean=${before.mean():,.0f}  median=${before.median():,.0f}")
print(f"  after:  mean=${after.mean():,.0f}  median=${after.median():,.0f}")

# stacked panels share one x-axis, so the shift of the mean line is read vertically
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.6, 3.9), sharex=True)
for ax, data, title in ((ax1, before, f"{N_DRINKERS} colleagues go for a drink"),
                         (ax2, after, "+ 1 billionaire walks in")):
    ax.set_xscale("log")
    ax.scatter(data, np.zeros_like(data), s=42, c=RLBLUE, edgecolors="black",
               linewidths=0.5, zorder=3, alpha=0.75)
    ax.axvline(data.mean(), color=RLRED, linewidth=2.0,
               label=f"mean = ${data.mean():,.0f}")
    ax.axvline(data.median(), color=RLGREEN, linewidth=2.0, linestyle="--",
               label=f"median = ${data.median():,.0f}")
    ax.set_yticks([])
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    ax.set_xlim(1e4, 3e11)
ax2.set_xlabel("Salary ($, log scale)")
fig.tight_layout()
save_fig(fig, "data_probability_billionaire_bar")


# ─── Figure 3: bottle filling — why variance, not just the mean ───────────
print("\nFigure 3: same mean, different variance (fill limits) …")
rng3 = np.random.default_rng(11)
spec_lo, spec_hi = 495.0, 505.0          # the label allows 500 ml +/- 5 ml
n_bottles = 1000
machines = {
    "A": dict(sd=2.0, color=RLGREEN),
    "B": dict(sd=4.0, color=RLORANGE),
}
# 1 ml bins whose edges land exactly on the limits, so no bar straddles them
bins_fill = np.arange(486.0, 515.0, 1.0)
assert spec_lo in bins_fill and spec_hi in bins_fill

fig, axes = plt.subplots(2, 1, figsize=(6.4, 4.4), sharex=True, sharey=True)
for ax, (name, spec) in zip(axes, machines.items()):
    fills = rng3.normal(500.0, spec["sd"], size=n_bottles)
    rejected = int(((fills < spec_lo) | (fills > spec_hi)).sum())
    spec["rejected"] = rejected
    print(f"  Machine {name}: mean={fills.mean():.2f}ml  std={fills.std(ddof=1):.2f}ml"
          f"  limits at {5.0 / spec['sd']:.2f} std  "
          f"rejected={rejected} of {n_bottles}")

    counts, edges = np.histogram(fills, bins=bins_fill)
    # a bar is a reject if the whole bin lies outside the allowed range
    inside = (edges[:-1] >= spec_lo) & (edges[1:] <= spec_hi)
    ax.bar(edges[:-1][inside], counts[inside], width=1.0, align="edge",
           color=spec["color"], edgecolor="white", linewidth=0.4)
    ax.bar(edges[:-1][~inside], counts[~inside], width=1.0, align="edge",
           color=RLRED, edgecolor="white", linewidth=0.4)
    for limit in (spec_lo, spec_hi):
        ax.axvline(limit, color=RLRED, linewidth=1.4, linestyle="--")
    ax.set_title(f"Machine {name}:  std = {spec['sd']}ml   "
                 f"$\\rightarrow$  {rejected} of {n_bottles} bottles rejected",
                 loc="left", fontsize=10)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)

axes[1].annotate("red bars = outside\nthe allowed range",
                 xy=(0.02, 0.92), xycoords="axes fraction", ha="left", va="top",
                 fontsize=9, color=RLRED)
axes[0].set_ylabel("Bottles")
axes[1].set_ylabel("Bottles")
axes[1].set_xlabel("Bottle contents (ml)")
axes[1].set_xlim(486, 514)
axes[1].set_xticks([490, 495, 500, 505, 510])
fig.tight_layout()
save_fig(fig, "data_probability_variance_bottles")


# ─── Figure 4: box plots — waiting times at three service branches ────────
print("\nFigure 4: box plots across three service branches …")
rng4 = np.random.default_rng(5)
# Waiting times are right-skewed by nature: most customers are served quickly,
# a few wait much longer. A lognormal gives that shape, so the outliers the box
# plot flags come from the tail of the same distribution -- not from a second,
# artificially spliced-in cluster sitting in a gap above the whisker.
branches = {
    "Branch A": dict(median=12.0, sigma=0.16, color=RLBLUE),
    "Branch B": dict(median=18.0, sigma=0.34, color=RLGREEN),
    "Branch C": dict(median=28.0, sigma=0.50, color=RLORANGE),
}
box_data, labels_box, colors_box = [], [], []
for name, spec in branches.items():
    waits = rng4.lognormal(np.log(spec["median"]), spec["sigma"], size=200)
    q1, med, q3 = np.percentile(waits, [25, 50, 75])
    iqr = q3 - q1
    fence = q3 + 1.5 * iqr
    n_out = int((waits > fence).sum())
    print(f"  {name}: median={med:.1f}min  Q1={q1:.1f}  Q3={q3:.1f}  IQR={iqr:.1f}"
          f"  upper fence={fence:.1f}  flagged={n_out}/200")
    box_data.append(waits)
    labels_box.append(name)
    colors_box.append(spec["color"])

fig, ax = plt.subplots(figsize=(6.2, 4.0))
bp = ax.boxplot(box_data, tick_labels=labels_box, patch_artist=True, widths=0.5,
                 flierprops=dict(marker="o", markerfacecolor=RLRED,
                                  markeredgecolor="black", markersize=5, alpha=0.7))
for patch, color in zip(bp["boxes"], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_ylabel("Waiting time (minutes)")
ax.set_ylim(bottom=0)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "data_probability_boxplot_branches")


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
