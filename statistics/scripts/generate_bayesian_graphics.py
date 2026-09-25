#!/usr/bin/env python3
"""Generate lecture figures for statistics/ Lecture 6
(lecture06_bayesian_inference.tex, lecture06_map_conjugacy.tex)

Numbers come from pandas/numpy; rendering is matplotlib, saved directly as
vector PDF (and SVG) -- see the pandas-vector-graphics skill for when this
matplotlib path applies vs. the TikZ path used by ml/'s older scripts.

Every figure is authored at roughly the width it occupies on the slide
(~4.2in for a 0.48-column figure), with explicit font sizes, so that its text
survives being scaled into the frame.

The running example is the 7:40 bus: each morning it is either on time or
late.  The 100 days are simulated once, from a true on-time rate of 0.70, and
every posterior on every slide is computed from prefixes of that same stream
-- nothing is sketched by hand.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import beta as beta_dist
from scipy.stats import norm

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "bayesian"
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


# ─── The running example: 100 mornings of the 7:40 bus ─────────────────────
TRUE_RATE = 0.70
rng = np.random.default_rng(21)
on_time = rng.random(100) < TRUE_RATE          # True = the bus was on time
PRIOR_A, PRIOR_B = 8.0, 2.0                    # "as if 8 on time, 2 late"

print("The 7:40 bus -- 100 simulated mornings, true on-time rate "
      f"{TRUE_RATE}")
print(f"  day 1 was {'ON TIME' if on_time[0] else 'LATE'}")

rows = []
for n in (1, 10, 30, 100):
    k = int(on_time[:n].sum())
    a, b = PRIOR_A + k, PRIOR_B + (n - k)
    lo, hi = beta_dist.ppf([0.025, 0.975], a, b)
    rows.append({
        "n": n, "on_time": k, "late": n - k,
        "mle": k / n,
        "post_a": a, "post_b": b,
        "post_mean": a / (a + b),
        "post_map": (a - 1) / (a + b - 2),
        "ci_lo": lo, "ci_hi": hi,
    })
bus = pd.DataFrame(rows).set_index("n")
pd.set_option("display.width", 130)
print(bus.round(4).to_string())


# ─── Figure 1: the posterior tightening as evidence arrives ────────────────
print("\nFigure 1: prior and posteriors after 1, 10, 30, 100 mornings …")
grid = np.linspace(0, 1, 601)

fig, ax = plt.subplots(figsize=(4.2, 3.0))
ax.plot(grid, beta_dist.pdf(grid, PRIOR_A, PRIOR_B), color=GREY,
        linewidth=2.2, label="prior (before day 1)")
shades = [RLORANGE, RLGREEN, RLRED, RLBLUE]
for (n, row), colour in zip(bus.iterrows(), shades):
    label = "after 1 morning" if n == 1 else f"after {n} mornings"
    ax.plot(grid, beta_dist.pdf(grid, row["post_a"], row["post_b"]),
            color=colour, linewidth=1.9, label=label)
ax.axvline(TRUE_RATE, color="#666666", linestyle="--", linewidth=1.1)
ax.text(TRUE_RATE + 0.025, ax.get_ylim()[1] * 0.04, "truth",
        ha="left", va="bottom", fontsize=9, color="#666666")
ax.set_xlim(0.2, 1.0)
ax.set_xlabel("on-time rate $\\theta$", fontsize=11)
ax.set_ylabel("density", fontsize=11)
ax.tick_params(labelsize=10)
ax.legend(fontsize=8.5, frameon=True, facecolor="white", framealpha=0.95,
          edgecolor="#cccccc", loc="upper left")
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "bayesian_posterior_updates")


# ─── Figure 2: three priors meet the same 100 mornings ─────────────────────
print("\nFigure 2: three priors, same data …")
k100 = int(on_time.sum())
priors = [
    ("flat: no opinion", 1.0, 1.0, RLORANGE),
    ("ours: 8 on time, 2 late", PRIOR_A, PRIOR_B, RLBLUE),
    ("stubborn: 80 on time, 20 late", 80.0, 20.0, RLRED),
]
fig, axes = plt.subplots(2, 1, figsize=(4.2, 3.15), sharex=True)
for name, a0, b0, colour in priors:
    axes[0].plot(grid, beta_dist.pdf(grid, a0, b0), color=colour,
                 linewidth=1.9, label=name)
    a, b = a0 + k100, b0 + (100 - k100)
    axes[1].plot(grid, beta_dist.pdf(grid, a, b), color=colour, linewidth=1.9)
    print(f"  {name:32s} prior mean={a0/(a0+b0):.3f}  "
          f"posterior Beta({a:.0f},{b:.0f}) mean={a/(a+b):.4f}")
for ax, title in zip(axes, ("before any data", f"after the same {100} mornings")):
    ax.set_title(title, fontsize=10, loc="left")
    ax.set_ylabel("density", fontsize=10.5)
    ax.tick_params(labelsize=9.5)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    ax.axvline(TRUE_RATE, color="#666666", linestyle="--", linewidth=1.0)
axes[0].set_ylim(0, 15.5)          # headroom so the legend clears the curves
axes[0].legend(fontsize=8, frameon=True, facecolor="white", framealpha=0.95,
               edgecolor="#cccccc", loc="upper left")
axes[1].set_xlim(0.3, 1.0)
axes[1].set_xlabel("on-time rate $\\theta$", fontsize=10.5)
fig.tight_layout()
save_fig(fig, "bayesian_three_priors")


# ─── Figure 3: three point estimates on one posterior ──────────────────────
print("\nFigure 3: MLE, MAP and posterior mean after 10 mornings …")
r30 = bus.loc[10]
a30, b30 = r30["post_a"], r30["post_b"]
fig, ax = plt.subplots(figsize=(4.2, 2.9))
dens = beta_dist.pdf(grid, a30, b30)
ax.plot(grid, dens, color=RLBLUE, linewidth=2.0)
inside = (grid >= r30["ci_lo"]) & (grid <= r30["ci_hi"])
ax.fill_between(grid[inside], dens[inside], color=RLBLUE, alpha=0.15)
marks = [
    ("MLE", r30["mle"], RLRED),
    ("posterior mean", r30["post_mean"], RLGREEN),
    ("MAP", r30["post_map"], RLORANGE),
]
ax.set_ylim(0, dens.max() * 1.55)          # clear band above the curve
label_slots = [(0.98, "right"), (0.86, "left"), (0.72, "left")]
for (name, value, colour), (height, side) in zip(marks, label_slots):
    ax.axvline(value, color=colour, linewidth=1.8)
    pad = " " if side == "left" else ""
    ax.text(value, ax.get_ylim()[1] * height,
            f"{pad}{name} {value:.3f}{'' if side == 'left' else ' '}",
            fontsize=9, color=colour, ha=side, va="top")
    print(f"  {name:16s} {value:.4f}")
print(f"  95% credible interval [{r30['ci_lo']:.3f}, {r30['ci_hi']:.3f}]")
ax.set_xlim(0.30, 1.0)
ax.set_xlabel("on-time rate $\\theta$", fontsize=11)
ax.set_ylabel("density", fontsize=11)
ax.tick_params(labelsize=10)
ax.set_title("shaded: central 95% of the posterior", fontsize=9.5, loc="left")
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "bayesian_point_estimates")


# ─── Figure 4: Gaussian prior meets Gaussian data ──────────────────────────
print("\nFigure 4: the walk to the station -- Gaussian update …")
mu0, tau0 = 12.0, 3.0          # hunch: about 12 minutes, give or take 3
sigma = 3.0                    # spread of a single timing
timings = np.array([13.0, 14.0, 16.0, 17.0])
n_t = len(timings)
xbar = timings.mean()
prec_prior, prec_data = 1 / tau0**2, n_t / sigma**2
post_var = 1 / (prec_prior + prec_data)
post_mu = (mu0 * prec_prior + xbar * prec_data) * post_var
print(f"  timings {timings.tolist()}  mean={xbar:.2f}")
print(f"  prior precision={prec_prior:.4f}  data precision={prec_data:.4f}"
      f"  weight on data={prec_data/(prec_prior+prec_data):.3f}")
print(f"  posterior mean={post_mu:.4f}  sd={np.sqrt(post_var):.4f}")

mins = np.linspace(6, 22, 601)
fig, ax = plt.subplots(figsize=(4.2, 2.9))
ax.plot(mins, norm.pdf(mins, mu0, tau0), color=GREY, linewidth=2.2,
        label=f"prior: about {mu0:.0f} min")
ax.plot(mins, norm.pdf(mins, xbar, sigma / np.sqrt(n_t)), color=RLORANGE,
        linewidth=1.9, label=f"{n_t} timings: mean {xbar:.0f} min")
ax.plot(mins, norm.pdf(mins, post_mu, np.sqrt(post_var)), color=RLBLUE,
        linewidth=2.2, label=f"posterior: {post_mu:.1f} min")
ax.set_ylim(0, norm.pdf(post_mu, post_mu, np.sqrt(post_var)) * 1.48)
ax.set_xlabel("walk to the station (minutes)", fontsize=11)
ax.set_ylabel("density", fontsize=11)
ax.tick_params(labelsize=10)
ax.legend(fontsize=8.5, frameon=True, facecolor="white", framealpha=0.95,
          edgecolor="#cccccc", loc="upper left")
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "bayesian_gaussian_update")


# ─── Figure 5: a prior is a penalty ────────────────────────────────────────
print("\nFigure 5: Gaussian prior on a weight, and the penalty it becomes …")
w = np.linspace(-4, 4, 601)
widths = [(2.0, RLORANGE), (1.0, RLBLUE), (0.5, RLRED)]
fig, axes = plt.subplots(1, 2, figsize=(5.2, 2.5))
for tau, colour in widths:
    axes[0].plot(w, norm.pdf(w, 0, tau), color=colour, linewidth=1.9,
                 label=f"$\\tau$ = {tau}")
    axes[1].plot(w, w**2 / (2 * tau**2), color=colour, linewidth=1.9)
    print(f"  tau={tau}  penalty coefficient 1/(2 tau^2) = {1/(2*tau**2):.3f}")
axes[0].set_title("prior $p(w)$", fontsize=10, loc="left")
axes[0].legend(fontsize=8.5, frameon=False, loc="upper left")
axes[1].set_title("penalty $-\\log p(w)$", fontsize=10, loc="left")
axes[1].set_ylim(0, 6)
for ax in axes:
    ax.set_xlabel("weight $w$", fontsize=10.5)
    ax.tick_params(labelsize=9.5)
    ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "bayesian_prior_to_penalty")

print("\nAll Lecture 6 figures written to", OUT_DIR)
