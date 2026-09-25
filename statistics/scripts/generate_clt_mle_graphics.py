#!/usr/bin/env python3
"""Generate lecture figures for statistics/ Lecture 5
(lecture05_clt.tex, lecture05_mle.tex)

Numbers come from numpy/pandas; rendering is matplotlib, saved directly as
vector PDF (and SVG) -- see the pandas-vector-graphics skill for when this
matplotlib path applies vs. the TikZ path used by ml/'s older scripts.

Every figure is authored at roughly the width it occupies on the slide
(~4.2in for a 0.48-column figure), with explicit font sizes, so that its text
survives being scaled into the frame.

The sampling distributions are computed by EXACT convolution of the
population PMF, not by simulation: the bell shape has to emerge from the
arithmetic, it is never drawn on top of a claim.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "clt_mle"
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


def normal_pdf(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


def convolve_n(pmf, n):
    """Exact PMF of the sum of n iid copies, by repeated convolution."""
    out = np.array([1.0])
    for _ in range(n):
        out = np.convolve(out, pmf)
    return out


# ══════════════════════════════════════════════════════════════════════════
# The running population: pastries per order at the Lecture 3 coffee shop.
#   P(0) = 0.7, P(1) = 0.2, P(2) = 0.1
# ══════════════════════════════════════════════════════════════════════════
PASTRY = np.array([0.7, 0.2, 0.1])
values = np.arange(3)
MU = float((values * PASTRY).sum())
VAR = float((values**2 * PASTRY).sum() - MU**2)
SIGMA = float(np.sqrt(VAR))
print("Population: pastries per order")
print(f"  mu = {MU:.4f}   var = {VAR:.4f}   sigma = {SIGMA:.6f}")


# ─── Figure 1: three spikes become a bell ─────────────────────────────────
print("\nFigure 1: sampling distribution of the mean, n = 1, 2, 5, 30 …")
fig, axes = plt.subplots(2, 2, figsize=(4.4, 3.5))
for ax, n in zip(axes.ravel(), (1, 2, 5, 30)):
    pmf_n = convolve_n(PASTRY, n)
    totals = np.arange(len(pmf_n))
    means = totals / n
    se = SIGMA / np.sqrt(n)
    # bars of width 1/n, so bar height = probability / width = probability * n
    ax.bar(means, pmf_n * n, width=0.9 / n, color=RLGREEN, alpha=0.85,
           edgecolor="none")
    grid = np.linspace(MU - 4 * se, MU + 4 * se, 400)
    ax.plot(grid, normal_pdf(grid, MU, se), color=RLBLUE, linewidth=1.6)
    ax.set_xlim(MU - 4 * se, MU + 4 * se)
    ax.set_title(f"n = {n},  SE = {se:.3f}", fontsize=9, loc="left", pad=3)
    ax.tick_params(labelsize=8)
    ax.set_yticks([])
    # report the three numbers the slide quotes
    lo, hi = MU - se, MU + se
    inside = pmf_n[(means >= lo - 1e-12) & (means <= hi + 1e-12)].sum()
    print(f"  n={n:2d}  SE={se:.4f}  P(mean within 1 SE) = {inside:.4f}"
          f"  support = {len(pmf_n)} values")
fig.supxlabel("Sample mean (pastries per order)", fontsize=9)
fig.tight_layout()
save_fig(fig, "clt_mle_sampling_distribution")


# ─── Figure 2: the square-root law ────────────────────────────────────────
print("\nFigure 2: standard error against sample size …")
ns = np.arange(1, 201)
ses = SIGMA / np.sqrt(ns)
marks = [10, 40, 160]
fig, ax = plt.subplots(figsize=(4.2, 2.9))
ax.plot(ns, ses, color=RLBLUE, linewidth=2.0)
for m in marks:
    se_m = SIGMA / np.sqrt(m)
    ax.plot([m], [se_m], "o", color=RLRED, markersize=6, zorder=3)
    ax.annotate(f"n={m}\nSE={se_m:.3f}", xy=(m, se_m), xytext=(m + 8, se_m + 0.045),
                fontsize=8.5, color=RLRED)
ax.set_xlabel("Sample size n", fontsize=10)
ax.set_ylabel("Standard error", fontsize=10)
ax.tick_params(labelsize=9)
ax.grid(True, linestyle=":", alpha=0.45)
ax.set_ylim(0, 0.72)
fig.tight_layout()
save_fig(fig, "clt_mle_standard_error")
for m in [1] + marks:
    print(f"  n={m:3d}  SE = {SIGMA / np.sqrt(m):.4f}")


# ─── Figure 3: when the CLT is slow ───────────────────────────────────────
# Everyday heavy tail: most customers buy 1-3 coffees, but 1 in 20 is an
# office run of 40.
print("\nFigure 3: a heavy tail slows the CLT down …")
office = np.zeros(41)
office[1], office[2], office[3], office[40] = 0.6, 0.3, 0.05, 0.05
ov = np.arange(41)
mu_o = float((ov * office).sum())
var_o = float((ov**2 * office).sum() - mu_o**2)
sd_o = float(np.sqrt(var_o))
print(f"  office-order population: mu = {mu_o:.4f}  var = {var_o:.4f}  sigma = {sd_o:.4f}")

N_CMP = 30
fig, axes = plt.subplots(2, 1, figsize=(4.2, 3.6))
for ax, (pmf, mu_p, sd_p, name) in zip(
        axes,
        [(PASTRY, MU, SIGMA, "Pastries per order (no heavy tail)"),
         (office, mu_o, sd_o, "Coffees per order (1 in 20 is an office run)")]):
    pmf_n = convolve_n(pmf, N_CMP)
    means = np.arange(len(pmf_n)) / N_CMP
    se = sd_p / np.sqrt(N_CMP)
    ax.bar(means, pmf_n * N_CMP, width=0.9 / N_CMP, color=RLORANGE,
           alpha=0.9, edgecolor="none")
    grid = np.linspace(mu_p - 4 * se, mu_p + 4 * se, 500)
    ax.plot(grid, normal_pdf(grid, mu_p, se), color=RLBLUE, linewidth=1.6)
    ax.set_xlim(mu_p - 4 * se, mu_p + 4 * se)
    ax.set_title(f"{name}\nn = {N_CMP}, SE = {se:.3f}", fontsize=8.5,
                 loc="left", pad=3)
    ax.set_yticks([])
    ax.tick_params(labelsize=8.5)
    # Skewness is the honest diagnostic here: a normal has skew 0, and the
    # skew of a sample mean is skew(X)/sqrt(n). (A CDF distance would mostly
    # measure the staircase of a discrete distribution, not the departure
    # from normality.)
    vals_p = np.arange(len(pmf))
    skew_x = float(((vals_p - mu_p) ** 3 * pmf).sum() / sd_p**3)
    print(f"  {name}: skew(X) = {skew_x:.4f},"
          f"  skew of mean at n={N_CMP} = {skew_x / np.sqrt(N_CMP):.4f}")
axes[1].set_xlabel("Sample mean", fontsize=9.5)
fig.tight_layout()
save_fig(fig, "clt_mle_heavy_tail")


# ══════════════════════════════════════════════════════════════════════════
# Part 1: maximum likelihood
# ══════════════════════════════════════════════════════════════════════════

# ─── Figure 4: the Bernoulli likelihood ───────────────────────────────────
print("\nFigure 4: Bernoulli likelihood from 200 orders …")
N_ORD, K_PASTRY = 200, 66
p_hat = K_PASTRY / N_ORD
ps = np.linspace(0.001, 0.999, 2000)
loglik = K_PASTRY * np.log(ps) + (N_ORD - K_PASTRY) * np.log(1 - ps)
lik_scaled = np.exp(loglik - loglik.max())
ll_hat = K_PASTRY * np.log(p_hat) + (N_ORD - K_PASTRY) * np.log(1 - p_hat)
print(f"  p_hat = {p_hat:.4f}")
print(f"  max log-likelihood = {ll_hat:.4f}")
print(f"  likelihood at p_hat = 10^({ll_hat / np.log(10):.2f})")
for p_try in (0.25, 0.30, 0.33, 0.40):
    llv = K_PASTRY * np.log(p_try) + (N_ORD - K_PASTRY) * np.log(1 - p_try)
    print(f"    p={p_try:.2f}  log-lik = {llv:9.4f}   relative likelihood"
          f" = {np.exp(llv - ll_hat):.4f}")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4.2, 3.5), sharex=True)
ax1.plot(ps, lik_scaled, color=RLGREEN, linewidth=2.0)
ax1.axvline(p_hat, color=RLRED, linestyle="--", linewidth=1.4)
ax1.set_ylabel("Likelihood\n(scaled to peak)", fontsize=9)
ax1.tick_params(labelsize=8.5)
ax1.set_yticks([0, 0.5, 1])
ax1.grid(True, linestyle=":", alpha=0.4)
ax2.plot(ps, loglik, color=RLBLUE, linewidth=2.0)
ax2.axvline(p_hat, color=RLRED, linestyle="--", linewidth=1.4)
ax2.annotate(f"$\\hat{{p}}$ = {p_hat:.2f}", xy=(p_hat, ll_hat),
             xytext=(p_hat + 0.07, ll_hat - 90), fontsize=9, color=RLRED)
ax2.set_ylabel("Log-likelihood", fontsize=9)
ax2.set_xlabel("p  (chance an order contains a pastry)", fontsize=9.5)
ax2.set_ylim(ll_hat - 200, ll_hat + 25)
ax2.tick_params(labelsize=8.5)
ax2.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "clt_mle_bernoulli_likelihood")


# ─── Figure 5: which bell curve fits? ─────────────────────────────────────
print("\nFigure 5: Gaussian MLE on espresso shot volumes …")
rng = np.random.default_rng(11)
shots = rng.normal(30.0, 1.5, size=40)
df_shots = pd.DataFrame({"ml": shots})
xbar = float(df_shots["ml"].mean())
sigma_mle = float(np.sqrt(((df_shots["ml"] - xbar) ** 2).mean()))   # divides by n
s_lect1 = float(df_shots["ml"].std(ddof=1))                          # divides by n-1
print(f"  n = {len(shots)}   x-bar = {xbar:.4f}")
print(f"  sigma-hat (MLE, /n)      = {sigma_mle:.4f}")
print(f"  s  (Lecture 1, /(n-1))   = {s_lect1:.4f}")


def gauss_loglik(data, mu, sigma):
    return float((-0.5 * np.log(2 * np.pi * sigma**2)
                  - (data - mu) ** 2 / (2 * sigma**2)).sum())


candidates = [
    (xbar, sigma_mle, RLBLUE, "MLE fit"),
    (28.6, 1.5, RLORANGE, "centre too low"),
    (xbar, 3.2, RLGREEN, "too wide"),
]
lls = []
for mu_c, sd_c, _, name in candidates:
    ll = gauss_loglik(df_shots["ml"].to_numpy(), mu_c, sd_c)
    lls.append(ll)
    print(f"  {name:>15s}:  mu={mu_c:.2f}  sigma={sd_c:.2f}   log-lik = {ll:9.3f}")
assert lls[0] == max(lls), "the MLE must have the highest log-likelihood"
print(f"  MLE beats the next best by {max(lls) - sorted(lls)[-2]:.2f} in log-likelihood")

fig, ax = plt.subplots(figsize=(4.3, 2.9))
ax.hist(df_shots["ml"], bins=10, density=True, color=GREY, edgecolor="white")
grid = np.linspace(shots.min() - 3, shots.max() + 3, 400)
for (mu_c, sd_c, colour, name), ll in zip(candidates, lls):
    ax.plot(grid, normal_pdf(grid, mu_c, sd_c), color=colour, linewidth=1.9,
            label=f"{name}: {ll:.0f}")
ax.plot(shots, np.full_like(shots, -0.012), "|", color="#444444", markersize=7)
ax.set_xlabel("Espresso shot volume (ml)", fontsize=9.5)
ax.set_ylabel("Density", fontsize=9.5)
ax.legend(title="log-likelihood", fontsize=8, title_fontsize=8.5,
          loc="upper left", frameon=True, facecolor="white", framealpha=0.95,
          edgecolor="#cccccc")
ax.tick_params(labelsize=8.5)
ax.set_ylim(-0.03, 0.55)          # headroom so the legend clears the bars
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "clt_mle_gaussian_fit")

print("\nAll Lecture 5 figures written to", OUT_DIR)
