#!/usr/bin/env python3
"""Generate lecture figures for statistics/ Lecture 3
(lecture03_discrete_rv.tex)

Numbers come from pandas/numpy; rendering is matplotlib, saved directly as
vector PDF (and SVG) -- see the pandas-vector-graphics skill for when this
matplotlib path applies vs. the TikZ path used by ml/'s older scripts.

Every figure is authored at roughly the width it occupies on the slide
(~4.2in for a 0.48-column figure), with explicit font sizes, so that its text
survives being scaled into the frame.
"""

from pathlib import Path
from collections import Counter
from math import comb, exp, factorial

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "discrete_rv"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand palette (see statistics/theme/rl-theme.tex: RLBlue, RLGreen, RLOrange).
RLBLUE = "#3A35B7"
RLGREEN = "#5FA0A4"
RLORANGE = "#F4BD70"
RLRED = "#D6455D"
GREY = "#DCDCDC"

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


# ─── Figure 1: the PMF of a two-dice sum ──────────────────────────────────
# Enumerated exactly -- all 36 equally likely outcomes, nothing simulated.
print("Figure 1: PMF of the sum of two dice …")
counts = Counter(a + b for a in range(1, 7) for b in range(1, 7))
sums = sorted(counts)
n_out = sum(counts.values())
probs = np.array([counts[s] / n_out for s in sums])
df_dice = pd.DataFrame({"sum": sums, "ways": [counts[s] for s in sums], "P": probs})
print(df_dice.to_string(index=False))
mean_sum = float((df_dice["sum"] * df_dice["P"]).sum())
var_sum = float((df_dice["sum"] ** 2 * df_dice["P"]).sum()) - mean_sum ** 2
print(f"  total outcomes={n_out}  E[X]={mean_sum:.3f}  Var(X)={var_sum:.4f}")
assert n_out == 36 and abs(probs.sum() - 1) < 1e-12

fig, ax = plt.subplots(figsize=(4.2, 3.0))
colors = [RLORANGE if s == 7 else RLGREEN for s in sums]
ax.bar(sums, probs, color=colors, edgecolor="white", linewidth=0.6, width=0.82)
for s, p, w in zip(sums, probs, df_dice["ways"]):
    ax.text(s, p + 0.004, str(w), ha="center", va="bottom", fontsize=8.5,
            color="#444444")
# stop the mean line at the bar top so it does not cross the count label
ax.axvline(mean_sum, color=RLRED, linestyle="--", linewidth=1.4, ymax=0.79)
ax.text(2.1, max(probs) * 1.12, f"$E[X] = {mean_sum:.0f}$",
        color=RLRED, fontsize=11, ha="left", va="center")
ax.set_xticks(sums)
ax.set_xlabel("Sum of the two dice", fontsize=11)
ax.set_ylabel("Probability", fontsize=11)
ax.tick_params(labelsize=10)
ax.set_ylim(0, max(probs) * 1.26)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "discrete_rv_two_dice_pmf")


# ─── Figure 2: the sample mean walks towards the expectation ──────────────
print("\nFigure 2: running sample mean of die rolls vs E[X] = 3.5 …")
rng2 = np.random.default_rng(7)
n_rolls = 2000
runs = {}
for label in ("Run 1", "Run 2", "Run 3"):
    rolls = rng2.integers(1, 7, size=n_rolls)
    runs[label] = np.cumsum(rolls) / np.arange(1, n_rolls + 1)
for label, series in runs.items():
    print(f"  {label}: mean after 10 = {series[9]:.3f}, "
          f"after 100 = {series[99]:.3f}, after {n_rolls} = {series[-1]:.3f}")

fig, ax = plt.subplots(figsize=(4.2, 3.0))
for (label, series), color in zip(runs.items(), (RLBLUE, RLGREEN, RLORANGE)):
    ax.plot(np.arange(1, n_rolls + 1), series, color=color, linewidth=1.1,
            label=label)
ax.axhline(3.5, color=RLRED, linestyle="--", linewidth=1.5)
ax.text(n_rolls * 0.95, 2.55, "$E[X] = 3.5$", color=RLRED, fontsize=11,
        ha="right", va="center")
ax.set_xscale("log")
ax.set_xlabel("Number of rolls so far", fontsize=11)
ax.set_ylabel("Sample mean $\\bar{x}$", fontsize=11)
ax.set_ylim(1.0, 6.4)
ax.tick_params(labelsize=10)
ax.legend(fontsize=9.5, frameon=False, loc="upper right")
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "discrete_rv_running_mean")


# ─── Figure 3: Binomial(10, 0.3) ──────────────────────────────────────────
print("\nFigure 3: Binomial(n=10, p=0.3) …")
n_cust, p_pastry = 10, 0.3
ks = np.arange(0, n_cust + 1)
binom = np.array([comb(n_cust, int(k)) * p_pastry ** int(k)
                  * (1 - p_pastry) ** (n_cust - int(k)) for k in ks])
print(pd.DataFrame({"k": ks, "P": binom.round(4)}).to_string(index=False))
print(f"  sum={binom.sum():.6f}  E=n*p={n_cust * p_pastry}  "
      f"Var=n*p*(1-p)={n_cust * p_pastry * (1 - p_pastry):.2f}")
assert abs(binom.sum() - 1) < 1e-12

fig, ax = plt.subplots(figsize=(4.2, 3.0))
bar_colors = [RLORANGE if k == 3 else RLGREEN for k in ks]
ax.bar(ks, binom, color=bar_colors, edgecolor="white", linewidth=0.6, width=0.82)
ax.axvline(3.0, color=RLRED, linestyle="--", linewidth=1.4)
ax.text(3.25, max(binom) * 0.93, "$E[X] = 3$", color=RLRED, fontsize=11,
        ha="left", va="center")
ax.set_xticks(ks)
ax.set_xlabel("Customers buying a pastry, out of 10", fontsize=11)
ax.set_ylabel("Probability", fontsize=11)
ax.tick_params(labelsize=10)
ax.set_ylim(0, max(binom) * 1.18)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "discrete_rv_binomial")


# ─── Figure 4: Poisson arrivals, simulated honestly ───────────────────────
# Arrivals are generated as a stream of exponential gaps at rate 4 per window.
# The per-window counts are then simply tallied -- the Poisson shape is not
# imposed, it falls out of the simulation.
print("\nFigure 4: arrivals per 10-minute window …")
rng4 = np.random.default_rng(21)
lam = 4.0
n_windows = 3000
gaps = rng4.exponential(scale=1.0 / lam, size=int(lam * n_windows * 1.6))
times = np.cumsum(gaps)
times = times[times < n_windows]
obs_counts = np.bincount(times.astype(int), minlength=n_windows)[:n_windows]
print(f"  simulated {len(times)} arrivals across {n_windows} windows")
print(f"  observed mean = {obs_counts.mean():.3f}  "
      f"observed variance = {obs_counts.var(ddof=1):.3f}  (Poisson: both = {lam})")

k_max = 12
ks_p = np.arange(0, k_max + 1)
obs_freq = np.array([(obs_counts == k).mean() for k in ks_p])
pois = np.array([exp(-lam) * lam ** int(k) / factorial(int(k)) for k in ks_p])
print(pd.DataFrame({"k": ks_p, "observed": obs_freq.round(4),
                    "Poisson": pois.round(4)}).to_string(index=False))

fig, ax = plt.subplots(figsize=(4.2, 3.0))
ax.bar(ks_p, obs_freq, color=RLGREEN, edgecolor="white", linewidth=0.6,
       width=0.82, label=f"observed ({n_windows} windows)")
ax.plot(ks_p, pois, "o--", color=RLRED, markersize=4.5, linewidth=1.4,
        label="Poisson($\\lambda = 4$)")
ax.set_xticks(ks_p[::2])
ax.set_xlabel("Customers arriving in 10 minutes", fontsize=11)
ax.set_ylabel("Share of windows", fontsize=11)
ax.tick_params(labelsize=10)
ax.legend(fontsize=9.5, frameon=False, loc="upper right")
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "discrete_rv_poisson")


# ─── Figure 5: a Dirichlet is a distribution over bar heights ─────────────
print("\nFigure 5: Dirichlet draws over the three cup sizes …")
rng5 = np.random.default_rng(5)
base = np.array([0.2, 0.5, 0.3])
labels5 = ["small", "medium", "large"]
concentrations = [(4.0, "weak belief — like 4 orders seen"),
                  (40.0, "strong belief — like 40 orders seen")]

# stacked, not side by side, so the figure stays ~4.2in wide for a half column
fig, axes = plt.subplots(2, 1, figsize=(4.2, 3.6), sharex=True, sharey=True)
x5 = np.arange(3)
for ax, (conc, name) in zip(axes, concentrations):
    draws = rng5.dirichlet(base * conc, size=6)
    print(f"  alpha = {conc} * {base}  ({name})")
    for row in draws.round(3):
        print("   ", row)
    for row in draws:
        ax.plot(x5, row, "o-", color=RLGREEN, alpha=0.55, linewidth=1.0,
                markersize=4)
    ax.plot(x5, base, "s-", color=RLBLUE, linewidth=2.0, markersize=6)
    ax.set_xticks(x5)
    ax.set_xticklabels(labels5, fontsize=10.5)
    alpha_txt = ", ".join(f"{a:g}" for a in base * conc)
    ax.set_title(f"{name}\n$\\alpha$ = ({alpha_txt})", fontsize=9.5, loc="left")
    ax.set_ylim(0, 0.85)
    ax.tick_params(labelsize=10)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
for ax in axes:
    ax.set_ylabel("Share", fontsize=11)
fig.tight_layout()
save_fig(fig, "discrete_rv_dirichlet")

print("\nAll Lecture 3 figures written to", OUT_DIR)
