#!/usr/bin/env python3
"""Generate lecture figures for statistics/ Lecture 9
(lecture09_correlation_regression.tex, lecture09_multivariate.tex)

Numbers come from pandas/numpy; rendering is matplotlib, saved directly as
vector PDF (and SVG) -- see the pandas-vector-graphics skill for when this
matplotlib path applies vs. the TikZ path used by ml/'s older scripts.

Every figure is authored at roughly the width it occupies on the slide
(~4.4in for a 0.48-column figure), with explicit font sizes, so that its text
survives being scaled into the frame.

The 300 trading days are the SAME sample Lecture 4 uses for its bivariate
Gaussian (same generator, same seed, same parameters), so the covariance
matrix quoted there -- [[31.9, 49.6], [49.6, 128.4]] -- is the matrix this
lecture regresses on and then diagonalizes.  Nothing is re-rolled.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "regression"
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


# ─── The shared sample: Lecture 4's 300 trading days, re-created exactly ───
rng = np.random.default_rng(11)
MU_VEC = np.array([22.0, 40.0])            # °C, cups of iced coffee
SD_T, SD_C, RHO = 6.0, 12.0, 0.8
COV_TRUE = np.array([[SD_T ** 2, RHO * SD_T * SD_C],
                     [RHO * SD_T * SD_C, SD_C ** 2]])
days = rng.multivariate_normal(MU_VEC, COV_TRUE, size=300)
df = pd.DataFrame(days, columns=["temp", "iced"])

t = df["temp"].to_numpy()
c = df["iced"].to_numpy()
n = len(df)

t_bar, c_bar = t.mean(), c.mean()
s_t, s_c = t.std(ddof=1), c.std(ddof=1)
S = np.cov(days.T)                          # sample covariance matrix
s_tc = S[0, 1]
r = float(np.corrcoef(t, c)[0, 1])

print("Shared sample: 300 trading days (identical to Lecture 4)")
print(f"  mean temp = {t_bar:.2f} °C   mean iced = {c_bar:.2f} cups")
print(f"  sd temp   = {s_t:.2f}        sd iced   = {s_c:.2f}")
print("  sample covariance matrix:")
for row in S:
    print("    [" + "  ".join(f"{v:7.1f}" for v in row) + " ]")
print(f"  covariance = {s_tc:.1f} °C·cups")
print(f"  correlation r = {r:.4f}   (slide: {r:.2f})")
print(f"  check r = cov/(s_t*s_c) = {s_tc / (s_t * s_c):.4f}")
print(f"  check with the SLIDE's rounded numbers: "
      f"49.6/(5.65*11.33) = {49.6 / (5.65 * 11.33):.4f}")

# ─── Ordinary least squares, fitted from the data ─────────────────────────
slope = s_tc / S[0, 0]
intercept = c_bar - slope * t_bar
fitted = intercept + slope * t
resid = c - fitted

ss_tot = float(((c - c_bar) ** 2).sum())
ss_res = float((resid ** 2).sum())
r2 = 1.0 - ss_res / ss_tot

print("\nOrdinary least squares: iced cups on temperature")
print(f"  slope     b = Sxy/Sxx = {s_tc:.1f}/{S[0,0]:.1f} = {slope:.4f} cups per °C")
print(f"  intercept a = ybar - b*xbar = {c_bar:.2f} - {slope:.4f}*{t_bar:.2f} "
      f"= {intercept:.4f}")
print(f"  slide line: y = {intercept:.1f} + {slope:.2f} x")
print(f"  line passes through the mean point ({t_bar:.1f}, {c_bar:.1f}): "
      f"{intercept + slope * t_bar:.2f} cups")
print(f"  prediction at 25 °C: exact {intercept + slope*25:.2f}, "
      f"from slide's rounded line 5.6 + 1.55*25 = {5.6 + 1.55*25:.2f}")
print(f"  SS_tot = {ss_tot:.1f}   SS_res = {ss_res:.1f}")
print(f"  R^2 = 1 - SS_res/SS_tot = {r2:.4f}      r^2 = {r*r:.4f}  "
      f"(identical: {abs(r2 - r*r) < 1e-12})")
print(f"  residual sd = {resid.std(ddof=2):.2f} cups")
print(f"  residual mean = {resid.mean():.2e} (least squares forces this to 0)")

# a concrete residual quoted on the slide
i_demo = int(np.argmin(np.abs(t - 25.0)))
print(f"  example day: {t[i_demo]:.1f} °C, {c[i_demo]:.0f} cups sold, "
      f"line predicts {fitted[i_demo]:.1f}, residual {resid[i_demo]:+.1f}")


# ─── Figure 1: the scatter and what r measures ────────────────────────────
print("\nFigure 1: hot days and iced coffee, with the correlation …")
fig, ax = plt.subplots(figsize=(4.4, 3.1))
ax.scatter(t, c, s=11, color=RLGREEN, alpha=0.65, edgecolors="none", zorder=2)
ax.axvline(t_bar, color=GREY, linewidth=1.2, zorder=1)
ax.axhline(c_bar, color=GREY, linewidth=1.2, zorder=1)
ax.plot([t_bar], [c_bar], "s", color=RLRED, markersize=6, zorder=4)
ax.annotate(f"mean point\n({t_bar:.1f} °C, {c_bar:.1f} cups)", xy=(t_bar, c_bar),
            xytext=(4.0, 66.0), fontsize=9, color=RLRED,
            arrowprops=dict(arrowstyle="->", color=RLRED, linewidth=1.0))
ax.text(0.97, 0.06, f"r = {r:.2f}", transform=ax.transAxes, fontsize=12,
        color=RLBLUE, ha="right", va="bottom", fontweight="bold")
ax.set_xlabel("Daily high temperature (°C)", fontsize=10)
ax.set_ylabel("Iced coffees sold", fontsize=10)
ax.tick_params(labelsize=9)
ax.grid(True, linestyle=":", alpha=0.35)
fig.tight_layout()
save_fig(fig, "regression_scatter_corr")


# ─── Figure 2: the fitted line and its residuals ──────────────────────────
print("\nFigure 2: the fitted line and the residual plot …")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4.4, 3.6), sharex=True,
                               gridspec_kw={"height_ratios": [1.7, 1.0]})
ax1.scatter(t, c, s=10, color=RLGREEN, alpha=0.55, edgecolors="none", zorder=2)
grid_t = np.linspace(t.min() - 0.5, t.max() + 0.5, 100)
ax1.plot(grid_t, intercept + slope * grid_t, color=RLBLUE, linewidth=1.9,
         zorder=4, label=f"$\\hat{{y}}$ = {intercept:.1f} + {slope:.2f}x")
# a handful of residual segments, drawn to the widest-missing days
big = np.argsort(-np.abs(resid))[:12]
for i in big:
    ax1.plot([t[i], t[i]], [c[i], fitted[i]], color=RLRED, linewidth=1.0,
             alpha=0.85, zorder=3)
ax1.legend(loc="upper left", fontsize=8.5, frameon=True, facecolor="white",
           framealpha=0.95, edgecolor="#cccccc")
ax1.set_ylabel("Iced coffees", fontsize=10)
ax1.tick_params(labelsize=9)
ax1.grid(True, linestyle=":", alpha=0.35)

ax2.scatter(t, resid, s=9, color=RLORANGE, alpha=0.8, edgecolors="none", zorder=2)
ax2.axhline(0.0, color=RLBLUE, linewidth=1.5, zorder=3)
ax2.set_xlabel("Daily high temperature (°C)", fontsize=10)
ax2.set_ylabel("Residual", fontsize=10)
ax2.tick_params(labelsize=9)
ax2.grid(True, linestyle=":", alpha=0.35)
fig.tight_layout()
save_fig(fig, "regression_fit_residuals")


# ─── Figure 3: what R^2 compares ──────────────────────────────────────────
print("\nFigure 3: R² as a comparison of two sets of gaps …")
sub = np.argsort(t)[::12]                   # a readable subset, spread over x
fig, (axA, axB) = plt.subplots(2, 1, figsize=(4.4, 3.6), sharex=True,
                               sharey=True)
axA.scatter(t[sub], c[sub], s=16, color=RLGREEN, edgecolors="none", zorder=3)
axA.axhline(c_bar, color="#888888", linewidth=1.6, zorder=2)
for i in sub:
    axA.plot([t[i], t[i]], [c[i], c_bar], color=RLRED, linewidth=1.1,
             alpha=0.9, zorder=1)
axA.set_title(f"gaps from the mean: SS$_{{tot}}$ = {ss_tot:,.0f}"
              f"   ({len(sub)} of {n} days drawn)",
              fontsize=9.5, loc="left")
axA.set_ylabel("Iced coffees", fontsize=10)
axA.tick_params(labelsize=9)
axA.grid(True, linestyle=":", alpha=0.3)

axB.scatter(t[sub], c[sub], s=16, color=RLGREEN, edgecolors="none", zorder=3)
axB.plot(grid_t, intercept + slope * grid_t, color=RLBLUE, linewidth=1.6,
         zorder=2)
for i in sub:
    axB.plot([t[i], t[i]], [c[i], fitted[i]], color=RLRED, linewidth=1.1,
             alpha=0.9, zorder=1)
axB.set_title(f"gaps from the line: SS$_{{res}}$ = {ss_res:,.0f}",
              fontsize=9.5, loc="left")
axB.set_xlabel("Daily high temperature (°C)", fontsize=10)
axB.set_ylabel("Iced coffees", fontsize=10)
axB.tick_params(labelsize=9)
axB.grid(True, linestyle=":", alpha=0.3)
fig.tight_layout()
save_fig(fig, "regression_r_squared")


# ─── Figure 4: what the correlation misses ────────────────────────────────
# Total drinks sold: hot drinks on cold days, iced on hot days, fewest in the
# mild middle.  The U is in the shop's behaviour; r is computed from the data.
print("\nFigure 4: a strong relationship the correlation cannot see …")
rng4 = np.random.default_rng(29)
total = 55.0 + 0.16 * (t - 21.9) ** 2 + rng4.normal(0.0, 6.0, size=n)
r_total = float(np.corrcoef(t, total)[0, 1])
# how well a *curve* does, for the contrast quoted on the slide
quad = np.polyfit(t, total, 2)
quad_fit = np.polyval(quad, t)
r2_quad = 1.0 - ((total - quad_fit) ** 2).sum() / ((total - total.mean()) ** 2).sum()
lin = np.polyfit(t, total, 1)
r2_lin = 1.0 - ((total - np.polyval(lin, t)) ** 2).sum() / \
    ((total - total.mean()) ** 2).sum()
print(f"  Pearson r(temp, total drinks) = {r_total:.4f}  (slide: {r_total:.2f})")
print(f"  straight-line R² = {r2_lin:.4f}   curve R² = {r2_quad:.4f}")
print(f"  total drinks: min={total.min():.0f} max={total.max():.0f} "
      f"mean={total.mean():.1f}")

fig, ax = plt.subplots(figsize=(4.4, 3.1))
ax.scatter(t, total, s=11, color=RLORANGE, alpha=0.75, edgecolors="none",
           zorder=2)
ax.plot(grid_t, np.polyval(lin, grid_t), color=RLBLUE, linewidth=1.8,
        zorder=3, label=f"straight line: $R^2$ = {r2_lin:.2f}")
ax.plot(grid_t, np.polyval(quad, grid_t), color=RLRED, linewidth=1.8,
        linestyle="--", zorder=4, label=f"curve: $R^2$ = {r2_quad:.2f}")
ax.legend(loc="upper center", fontsize=8.5, frameon=True, facecolor="white",
          framealpha=0.95, edgecolor="#cccccc")
ax.text(0.97, 0.06, f"r = {r_total:+.2f}", transform=ax.transAxes, fontsize=12,
        color=RLBLUE, ha="right", va="bottom", fontweight="bold")
ax.set_xlabel("Daily high temperature (°C)", fontsize=10)
ax.set_ylabel("Total drinks sold", fontsize=10)
ax.tick_params(labelsize=9)
ax.grid(True, linestyle=":", alpha=0.35)
fig.tight_layout()
save_fig(fig, "regression_nonlinear")


# ─── Three columns: the correlation matrix ────────────────────────────────
print("\nThree quantities per day: temperature, iced coffees, hot drinks …")
rng5 = np.random.default_rng(7)
hot = 80.0 - 2.2 * t + rng5.normal(0.0, 8.0, size=n)
hot = np.clip(hot, 0.0, None)
df3 = pd.DataFrame({"temp": t, "iced": c, "hot": hot})
C3 = df3.cov().to_numpy()
R3 = df3.corr().to_numpy()
names3 = ["temp (°C)", "iced (cups)", "hot (cups)"]
print("  covariance matrix (units differ, so the entries are not comparable):")
for row in C3:
    print("    [" + "  ".join(f"{v:8.1f}" for v in row) + " ]")
print("  correlation matrix (unit-free):")
for row in R3:
    print("    [" + "  ".join(f"{v:6.2f}" for v in row) + " ]")
print(f"  mean hot drinks = {hot.mean():.1f}  sd = {hot.std(ddof=1):.1f}")

print("\nFigure 5: the correlation matrix …")
fig, ax = plt.subplots(figsize=(4.0, 3.2))
im = ax.imshow(R3, cmap="RdBu_r", vmin=-1.0, vmax=1.0)
for i in range(3):
    for j in range(3):
        ax.text(j, i, f"{R3[i, j]:+.2f}", ha="center", va="center",
                fontsize=11,
                color="white" if abs(R3[i, j]) > 0.55 else "#222222")
ax.set_xticks(range(3))
ax.set_yticks(range(3))
ax.set_xticklabels(names3, fontsize=9)
ax.set_yticklabels(names3, fontsize=9)
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cb.ax.tick_params(labelsize=8)
cb.set_label("correlation", fontsize=9)
ax.set_title("every pair at once", fontsize=10, loc="left")
fig.tight_layout()
save_fig(fig, "regression_corr_matrix")


# ─── Eigendecomposition of the covariance matrix ──────────────────────────
vals, vecs = np.linalg.eigh(S)
order = vals.argsort()[::-1]
vals, vecs = vals[order], vecs[:, order]
# sign convention: point PC1 into the upper-right quadrant
if vecs[0, 0] < 0:
    vecs[:, 0] = -vecs[:, 0]
if vecs[1, 1] < 0:
    vecs[:, 1] = -vecs[:, 1]
shares = vals / vals.sum()

print("\nEigendecomposition of the sample covariance matrix")
print(f"  eigenvalues: {vals[0]:.2f} and {vals[1]:.2f}")
print(f"  sum = {vals.sum():.2f}   trace of Sigma = {np.trace(S):.2f} (equal)")
print(f"  variance shares: {shares[0]*100:.1f}% and {shares[1]*100:.1f}%")
print(f"  PC1 = ({vecs[0,0]:+.3f}, {vecs[1,0]:+.3f})   "
      f"PC2 = ({vecs[0,1]:+.3f}, {vecs[1,1]:+.3f})")
print(f"  PC1 angle = {np.degrees(np.arctan2(vecs[1,0], vecs[0,0])):.1f}° "
      f"from the temperature axis")
print(f"  sd along PC1 = {np.sqrt(vals[0]):.2f}, along PC2 = {np.sqrt(vals[1]):.2f}")
print(f"  orthogonal? PC1·PC2 = {float(vecs[:,0] @ vecs[:,1]):.2e}")

# the same decomposition after standardizing -- i.e. of the correlation matrix
Rmat = np.array([[1.0, r], [r, 1.0]])
vals_r, vecs_r = np.linalg.eigh(Rmat)
order_r = vals_r.argsort()[::-1]
vals_r = vals_r[order_r]
print(f"  on the CORRELATION matrix instead: eigenvalues {vals_r[0]:.4f} "
      f"and {vals_r[1]:.4f} (= 1+r and 1-r)")
print(f"  shares: {vals_r[0]/2*100:.1f}% and {vals_r[1]/2*100:.1f}%")

print("\nFigure 6: the two principal directions …")
fig, ax = plt.subplots(figsize=(4.4, 3.3))
ax.scatter(t, c, s=11, color=RLGREEN, alpha=0.55, edgecolors="none", zorder=2)
mu_hat = np.array([t_bar, c_bar])
for k, (color, label) in enumerate(((RLBLUE, "PC1"), (RLRED, "PC2"))):
    d = vecs[:, k] * 2.0 * np.sqrt(vals[k])
    ax.annotate("", xy=mu_hat + d, xytext=mu_hat,
                arrowprops=dict(arrowstyle="-|>", color=color, linewidth=2.2,
                                mutation_scale=14), zorder=5)
    ax.annotate("", xy=mu_hat - d, xytext=mu_hat,
                arrowprops=dict(arrowstyle="-|>", color=color, linewidth=2.2,
                                mutation_scale=14), zorder=5)
    tip = mu_hat + d * 1.08
    ax.text(tip[0], tip[1], f"{label}: {shares[k]*100:.1f}%", fontsize=9.5,
            color=color, fontweight="bold",
            ha="left" if k == 0 else "right",
            va="bottom" if k == 0 else "top", zorder=6)
ax.plot([t_bar], [c_bar], "s", color="#222222", markersize=5, zorder=6)
ax.set_xlabel("Daily high temperature (°C)", fontsize=10)
ax.set_ylabel("Iced coffees sold", fontsize=10)
ax.tick_params(labelsize=9)
ax.grid(True, linestyle=":", alpha=0.35)
fig.tight_layout()
save_fig(fig, "regression_pca_axes")

print("\nAll Lecture 9 figures written to", OUT_DIR)
