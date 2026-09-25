#!/usr/bin/env python3
"""Generate lecture figures for statistics/ Lecture 8
(lecture08_exponential_family.tex, lecture08_sufficient_statistics.tex)

Numbers come from pandas/numpy; rendering is matplotlib, saved directly as
vector PDF (and SVG) -- see the pandas-vector-graphics skill for when this
matplotlib path applies vs. the TikZ path used by ml/'s older scripts.

Every figure is authored at roughly the width it occupies on the slide
(~4.2in for a 0.48-column figure), with explicit font sizes, so that its text
survives being scaled into the frame.

Nothing here is simulated: the logit map, the log-partition function and the
likelihood curves are all evaluated from their formulas, and the sufficiency
demonstration uses three hand-written records that genuinely sum to the same
count.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "expfamily"
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


def sigmoid(eta):
    return 1.0 / (1.0 + np.exp(-eta))


# ─── Figure 1: the logit map, p <-> eta ───────────────────────────────────
# The coffee shop's pastry rate p = 0.3 is the marked point on both panels.
print("Figure 1: the logit map between p and eta …")
P_PASTRY = 0.3
ETA_PASTRY = float(np.log(P_PASTRY / (1 - P_PASTRY)))
print(f"  p = {P_PASTRY}  ->  eta = log(p/(1-p)) = {ETA_PASTRY:.4f}")
print(f"  eta = {ETA_PASTRY:.4f}  ->  sigmoid(eta) = {sigmoid(ETA_PASTRY):.6f}")
assert abs(sigmoid(ETA_PASTRY) - P_PASTRY) < 1e-12

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4.2, 3.4))

p_grid = np.linspace(0.012, 0.988, 400)
ax1.plot(p_grid, np.log(p_grid / (1 - p_grid)), color=RLBLUE, linewidth=2.0)
ax1.axhline(0, color="#999999", linewidth=0.7)
ax1.plot([P_PASTRY], [ETA_PASTRY], "o", color=RLORANGE, markersize=7,
         markeredgecolor="#333333", markeredgewidth=0.7, zorder=5)
ax1.annotate(f"p = 0.3\n$\\eta$ = {ETA_PASTRY:.2f}", xy=(P_PASTRY, ETA_PASTRY),
             xytext=(0.06, 0.9), fontsize=9.5, color="#333333",
             arrowprops=dict(arrowstyle="->", color="#666666", lw=0.9))
ax1.set_title("probability $\\rightarrow$ natural parameter", fontsize=10.5,
              loc="left")
ax1.set_xlabel("$p$", fontsize=11)
ax1.set_ylabel("$\\eta = \\log\\frac{p}{1-p}$", fontsize=10.5)
ax1.set_ylim(-4.6, 4.6)
ax1.tick_params(labelsize=9.5)
ax1.grid(True, linestyle=":", alpha=0.4)

eta_grid = np.linspace(-4.6, 4.6, 400)
ax2.plot(eta_grid, sigmoid(eta_grid), color=RLGREEN, linewidth=2.0)
ax2.axhline(0.5, color="#999999", linewidth=0.7)
ax2.plot([ETA_PASTRY], [P_PASTRY], "o", color=RLORANGE, markersize=7,
         markeredgecolor="#333333", markeredgewidth=0.7, zorder=5)
ax2.annotate(f"$\\eta$ = {ETA_PASTRY:.2f}\np = 0.3", xy=(ETA_PASTRY, P_PASTRY),
             xytext=(1.5, 0.10), fontsize=9.5, color="#333333",
             arrowprops=dict(arrowstyle="->", color="#666666", lw=0.9))
ax2.set_title("natural parameter $\\rightarrow$ probability", fontsize=10.5,
              loc="left")
ax2.set_xlabel("$\\eta$", fontsize=11)
ax2.set_ylabel("$p = \\sigma(\\eta)$", fontsize=10.5)
ax2.set_ylim(-0.05, 1.05)
ax2.tick_params(labelsize=9.5)
ax2.grid(True, linestyle=":", alpha=0.4)

fig.tight_layout()
save_fig(fig, "expfamily_logit_map")


# ─── Figure 2: A(eta) and its slope ───────────────────────────────────────
print("\nFigure 2: the log-partition function and its slope …")
A = lambda e: np.log1p(np.exp(e))
A_prime = sigmoid

a_at = float(A(ETA_PASTRY))
slope_at = float(A_prime(ETA_PASTRY))
print(f"  A(eta) = log(1+e^eta) at eta={ETA_PASTRY:.4f} is {a_at:.6f}")
print(f"  -log(1-p) with p={P_PASTRY} is {-np.log(1 - P_PASTRY):.6f}")
assert abs(a_at + np.log(1 - P_PASTRY)) < 1e-12
print(f"  A'(eta) = {slope_at:.6f}   E[X] = p = {P_PASTRY}")
assert abs(slope_at - P_PASTRY) < 1e-12
# second derivative recovers the variance
h = 1e-5
second = (A(ETA_PASTRY + h) - 2 * A(ETA_PASTRY) + A(ETA_PASTRY - h)) / h ** 2
print(f"  A''(eta) numerically = {second:.6f}   p(1-p) = {P_PASTRY*(1-P_PASTRY):.6f}")
assert abs(second - P_PASTRY * (1 - P_PASTRY)) < 1e-6

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4.2, 3.35), sharex=True)

eta_g = np.linspace(-4.2, 4.2, 400)
ax1.plot(eta_g, A(eta_g), color=RLBLUE, linewidth=2.0)
tan_x = np.linspace(ETA_PASTRY - 1.7, ETA_PASTRY + 1.7, 20)
ax1.plot(tan_x, a_at + slope_at * (tan_x - ETA_PASTRY), color=RLRED,
         linewidth=1.5, linestyle="--")
ax1.plot([ETA_PASTRY], [a_at], "o", color=RLORANGE, markersize=7,
         markeredgecolor="#333333", markeredgewidth=0.7, zorder=5)
# A is convex, so the tangent lies below the curve; annotate from the open
# wedge under the curve on the right, otherwise the arrow has to cross it.
ax1.annotate("slope = 0.30", xy=(ETA_PASTRY + 1.7, a_at + slope_at * 1.7),
             xytext=(1.75, 0.45), fontsize=9.5, color=RLRED,
             arrowprops=dict(arrowstyle="->", color=RLRED, lw=0.9))
ax1.set_title("$A(\\eta) = \\log(1+e^{\\eta})$", fontsize=10.5, loc="left")
ax1.set_ylabel("$A(\\eta)$", fontsize=10.5)
ax1.set_ylim(-0.2, 4.4)
ax1.tick_params(labelsize=9.5)
ax1.grid(True, linestyle=":", alpha=0.4)

ax2.plot(eta_g, A_prime(eta_g), color=RLGREEN, linewidth=2.0)
ax2.plot([ETA_PASTRY], [slope_at], "o", color=RLORANGE, markersize=7,
         markeredgecolor="#333333", markeredgewidth=0.7, zorder=5)
ax2.axhline(P_PASTRY, color="#999999", linewidth=0.8, linestyle=":")
ax2.annotate("$E[X] = 0.30$", xy=(ETA_PASTRY, slope_at), xytext=(0.7, 0.14),
             fontsize=9.5, color="#333333",
             arrowprops=dict(arrowstyle="->", color="#666666", lw=0.9))
ax2.set_title("its slope $A'(\\eta) = E[X]$", fontsize=10.5, loc="left")
ax2.set_xlabel("$\\eta$", fontsize=11)
ax2.set_ylabel("$A'(\\eta)$", fontsize=10.5)
ax2.set_ylim(-0.05, 1.05)
ax2.tick_params(labelsize=9.5)
ax2.grid(True, linestyle=":", alpha=0.4)

fig.tight_layout()
save_fig(fig, "expfamily_log_partition")


# ─── Figure 3: sufficiency -- three records, one likelihood curve ─────────
print("\nFigure 3: three different records with the same sufficient statistic …")
records = {
    "steady":      [7, 6, 7, 6, 7, 6, 7, 7, 7, 6],
    "one big day": [20, 3, 4, 5, 3, 6, 4, 7, 9, 5],
    "building up": [1, 2, 4, 5, 6, 8, 9, 10, 10, 11],
}
ORDERS_PER_MORNING = 20
N_TOTAL = ORDERS_PER_MORNING * 10
df_rec = pd.DataFrame(records, index=[f"m{i+1}" for i in range(10)])
print(df_rec.to_string())
for name, rec in records.items():
    assert sum(rec) == 66, f"{name} sums to {sum(rec)}"
    assert max(rec) <= ORDERS_PER_MORNING
    print(f"  {name:12s} total = {sum(rec)} of {N_TOTAL}")
K_TOTAL = 66

p_g = np.linspace(0.12, 0.60, 400)
loglik = K_TOTAL * np.log(p_g) + (N_TOTAL - K_TOTAL) * np.log(1 - p_g)
p_hat = K_TOTAL / N_TOTAL
print(f"  p_hat = {K_TOTAL}/{N_TOTAL} = {p_hat:.4f}")
print(f"  max log-likelihood = {loglik.max():.4f} at p = {p_g[loglik.argmax()]:.4f}")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4.2, 3.5))

mornings = np.arange(1, 11)
styles = [(RLBLUE, "-", 1.8), (RLORANGE, "-", 1.8), (RLGREEN, "--", 1.8)]
for (name, rec), (col, ls, lw) in zip(records.items(), styles):
    ax1.plot(mornings, rec, ls, color=col, linewidth=lw, marker="o",
             markersize=3.5, label=name)
ax1.set_title("three records, all 66 of 200", fontsize=10.5, loc="left")
ax1.set_xlabel("morning", fontsize=10.5)
ax1.set_ylabel("pastry orders", fontsize=10.5)
ax1.set_xticks(mornings)
ax1.tick_params(labelsize=9)
# upper right: the only corner with no data (the "one big day" spike is at m1)
ax1.legend(fontsize=8.2, frameon=True, facecolor="white", framealpha=0.95,
           edgecolor="#cccccc", loc="upper right", ncol=1)
ax1.set_ylim(-1, 27)
ax1.grid(True, axis="y", linestyle=":", alpha=0.4)

for (name, _), (col, ls, lw) in zip(records.items(), styles):
    ax2.plot(p_g, loglik, ls, color=col, linewidth=lw + 2.2 - 1.1 * list(records).index(name))
ax2.axvline(p_hat, color="#999999", linewidth=0.9, linestyle=":")
ax2.annotate(f"$\\hat p$ = {p_hat:.2f}", xy=(p_hat, loglik.min()),
             xytext=(p_hat + 0.016, loglik.min() + 6), fontsize=9.5,
             color="#333333")
ax2.set_title("one log-likelihood curve", fontsize=10.5, loc="left")
ax2.set_xlabel("$p$", fontsize=11)
ax2.set_ylabel("$\\ell(p)$", fontsize=10.5)
ax2.tick_params(labelsize=9.5)
ax2.grid(True, linestyle=":", alpha=0.4)

fig.tight_layout()
save_fig(fig, "expfamily_sufficiency")


# ─── Figure 4: MLE as moment matching, two different families ─────────────
print("\nFigure 4: MLE as moment matching …")
OBS_P = 66 / 200          # Bernoulli: observed share of pastry orders
OBS_LAM = 3.96            # Poisson: observed mean arrivals per ten minutes
eta_hat_b = float(np.log(OBS_P / (1 - OBS_P)))
eta_hat_p = float(np.log(OBS_LAM))
print(f"  Bernoulli: observed mean {OBS_P:.4f} -> eta_hat = {eta_hat_b:.4f}"
      f"  and sigma(eta_hat) = {sigmoid(eta_hat_b):.4f}")
print(f"  Poisson:   observed mean {OBS_LAM:.4f} -> eta_hat = {eta_hat_p:.4f}"
      f"  and exp(eta_hat) = {np.exp(eta_hat_p):.4f}")
assert abs(sigmoid(eta_hat_b) - OBS_P) < 1e-12
assert abs(np.exp(eta_hat_p) - OBS_LAM) < 1e-12

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4.2, 3.4))

e1 = np.linspace(-3.0, 1.6, 400)
ax1.plot(e1, sigmoid(e1), color=RLGREEN, linewidth=2.0)
ax1.axhline(OBS_P, color=RLRED, linewidth=1.3, linestyle="--")
ax1.plot([eta_hat_b], [OBS_P], "o", color=RLORANGE, markersize=7,
         markeredgecolor="#333333", markeredgewidth=0.7, zorder=5)
ax1.annotate("data average 0.33", xy=(-2.9, OBS_P + 0.035), fontsize=9,
             color=RLRED, ha="left")
ax1.annotate(f"$\\hat\\eta$ = {eta_hat_b:.2f}", xy=(eta_hat_b, OBS_P),
             xytext=(eta_hat_b + 0.18, 0.08), fontsize=9.5, color="#333333",
             arrowprops=dict(arrowstyle="->", color="#666666", lw=0.9))
ax1.set_title("Bernoulli:  $A'(\\eta) = \\sigma(\\eta)$", fontsize=10.5,
              loc="left")
ax1.set_xlabel("$\\eta$", fontsize=11)
ax1.set_ylabel("$E_\\eta[T]$", fontsize=10.5)
ax1.set_ylim(-0.03, 0.85)
ax1.tick_params(labelsize=9.5)
ax1.grid(True, linestyle=":", alpha=0.4)

e2 = np.linspace(0.0, 2.2, 400)
ax2.plot(e2, np.exp(e2), color=RLBLUE, linewidth=2.0)
ax2.axhline(OBS_LAM, color=RLRED, linewidth=1.3, linestyle="--")
ax2.plot([eta_hat_p], [OBS_LAM], "o", color=RLORANGE, markersize=7,
         markeredgecolor="#333333", markeredgewidth=0.7, zorder=5)
ax2.annotate("data average 3.96", xy=(0.03, OBS_LAM + 0.55), fontsize=9,
             color=RLRED, ha="left")
ax2.annotate(f"$\\hat\\eta$ = {eta_hat_p:.2f}", xy=(eta_hat_p, OBS_LAM),
             xytext=(eta_hat_p + 0.12, 1.1), fontsize=9.5, color="#333333",
             arrowprops=dict(arrowstyle="->", color="#666666", lw=0.9))
ax2.set_title("Poisson:  $A'(\\eta) = e^{\\eta}$", fontsize=10.5, loc="left")
ax2.set_xlabel("$\\eta$", fontsize=11)
ax2.set_ylabel("$E_\\eta[T]$", fontsize=10.5)
ax2.set_ylim(0, 9.2)
ax2.tick_params(labelsize=9.5)
ax2.grid(True, linestyle=":", alpha=0.4)

fig.tight_layout()
save_fig(fig, "expfamily_moment_matching")

print("\nAll Lecture 8 figures written to", OUT_DIR)
