#!/usr/bin/env python3
"""Generate lecture figures for statistics/ Lecture 4
(lecture04_continuous_gaussian.tex, lecture04_gaussian_deep_dive.tex)

Numbers come from pandas/numpy; rendering is matplotlib, saved directly as
vector PDF (and SVG) -- see the pandas-vector-graphics skill for when this
matplotlib path applies vs. the TikZ path used by ml/'s older scripts.

Every figure is authored at roughly the width it occupies on the slide
(~4.2in for a 0.48-column figure), with explicit font sizes, so that its text
survives being scaled into the frame.

The whole lecture runs on one everyday setting -- the coffee shop of Lecture 3,
where customers arrive at 4 per ten minutes and the bakery next door weighs its
croissants.
"""

from pathlib import Path
from math import erf, exp, log, sqrt

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "continuous_gaussian"
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


def Phi(z):
    """Standard normal CDF."""
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))


# The coffee shop of Lecture 3: 4 arrivals per ten minutes, i.e. 0.4 per minute.
RATE = 0.4          # arrivals per minute
MEAN_GAP = 1 / RATE  # 2.5 minutes between customers


# ─── Figure 1: shrinking the bins turns a histogram into a density ─────────
print("Figure 1: histogram bins shrinking toward a density …")
rng1 = np.random.default_rng(4)
gaps = rng1.exponential(MEAN_GAP, size=20_000)
df_gaps = pd.DataFrame({"gap": gaps})
print(f"  n={len(df_gaps)}  mean gap={df_gaps['gap'].mean():.3f} min"
      f"  (theory {MEAN_GAP})")

fig, axes = plt.subplots(2, 1, figsize=(4.2, 3.2), sharex=True)
x_curve = np.linspace(0, 12, 400)
pdf_curve = RATE * np.exp(-RATE * x_curve)

for ax, width, show_curve in ((axes[0], 2.0, False), (axes[1], 0.25, True)):
    edges = np.arange(0, 12 + width, width)
    ax.hist(df_gaps["gap"], bins=edges, density=True, color=RLGREEN,
            alpha=0.75, edgecolor="white",
            linewidth=0.4 if width >= 1 else 0.15)
    if show_curve:
        ax.plot(x_curve, pdf_curve, color=RLBLUE, linewidth=2.0)
    ax.set_title(f"bin width = {width:g} min", fontsize=10, loc="left")
    ax.set_ylabel("density", fontsize=10)
    ax.tick_params(labelsize=9)
    ax.set_xlim(0, 12)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    n_in = int(((df_gaps["gap"] >= 0) & (df_gaps["gap"] < width)).sum())
    print(f"  width={width:g}: first bar holds {n_in} of {len(df_gaps)} gaps"
          f"  -> height {n_in / len(df_gaps) / width:.3f}")

axes[1].set_xlabel("Minutes until the next customer", fontsize=10)
fig.tight_layout()
save_fig(fig, "continuous_histogram_to_density")


# ─── Figure 2: area under the density is probability; the CDF stacks it ────
print("\nFigure 2: area as probability, and the CDF …")
cut = 2.0
p_below = 1 - exp(-RATE * cut)
print(f"  P(gap < {cut} min) = 1 - e^(-{RATE}*{cut}) = {p_below:.4f}")
print(f"  P(gap > 5 min)     = e^(-{RATE * 5})       = {exp(-RATE * 5):.4f}")

fig, axes = plt.subplots(2, 1, figsize=(4.2, 3.3), sharex=True)
shade = x_curve <= cut

axes[0].plot(x_curve, pdf_curve, color=RLBLUE, linewidth=2.0)
axes[0].fill_between(x_curve[shade], 0, pdf_curve[shade], color=RLORANGE,
                     alpha=0.85)
axes[0].annotate(f"area = {p_below:.2f}", xy=(1.1, 0.12), xytext=(3.4, 0.26),
                 fontsize=10, color="#222222",
                 arrowprops=dict(arrowstyle="->", color="#555555",
                                 linewidth=1.0))
axes[0].set_ylabel("density  f(x)", fontsize=10)
axes[0].set_title("the shaded area is the probability", fontsize=10, loc="left")

cdf_curve = 1 - np.exp(-RATE * x_curve)
axes[1].plot(x_curve, cdf_curve, color=RLBLUE, linewidth=2.0)
axes[1].vlines(cut, 0, p_below, color=RLRED, linestyle="--", linewidth=1.3)
axes[1].hlines(p_below, 0, cut, color=RLRED, linestyle="--", linewidth=1.3)
axes[1].plot([cut], [p_below], "o", color=RLRED, markersize=5)
axes[1].annotate(f"F({cut:g}) = {p_below:.2f}", xy=(2.4, 0.30), fontsize=10,
                 color=RLRED)
axes[1].set_ylabel("F(x)", fontsize=10)
axes[1].set_title("the same number, read off the CDF", fontsize=10, loc="left")
axes[1].set_xlabel("Minutes until the next customer", fontsize=10)

for ax in axes:
    ax.set_xlim(0, 12)
    ax.tick_params(labelsize=9)
    ax.grid(True, linestyle=":", alpha=0.4)
axes[1].set_ylim(0, 1.05)
fig.tight_layout()
save_fig(fig, "continuous_density_and_cdf")


# ─── Figure 3: the two shapes -- uniform and exponential ──────────────────
print("\nFigure 3: uniform vs exponential …")
fig, axes = plt.subplots(2, 1, figsize=(4.2, 3.0))

xu = np.linspace(-1, 11, 400)
yu = np.where((xu >= 0) & (xu <= 10), 1 / 10, 0.0)
axes[0].plot(xu, yu, color=RLBLUE, linewidth=2.0)
axes[0].fill_between(xu, 0, yu, color=RLGREEN, alpha=0.45)
axes[0].set_title("Uniform(0, 10): no moment is special", fontsize=10,
                  loc="left")
axes[0].set_xlabel("Minute of the window the delivery lands", fontsize=9.5)
axes[0].set_ylim(0, 0.16)
axes[0].set_yticks([0, 0.1])

axes[1].plot(x_curve, pdf_curve, color=RLBLUE, linewidth=2.0)
axes[1].fill_between(x_curve, 0, pdf_curve, color=RLORANGE, alpha=0.55)
axes[1].set_title("Exponential(0.4): short gaps are commonest", fontsize=10,
                  loc="left")
axes[1].set_xlabel("Minutes until the next customer", fontsize=9.5)
axes[1].set_xlim(0, 12)

for ax in axes:
    ax.set_ylabel("density", fontsize=10)
    ax.tick_params(labelsize=9)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "continuous_uniform_exponential")


# ─── Figure 4: a Beta is a belief about one probability ───────────────────
print("\nFigure 4: Beta beliefs about the pastry rate …")


def beta_pdf(x, a, b):
    from math import lgamma
    logc = lgamma(a + b) - lgamma(a) - lgamma(b)
    return np.exp(logc + (a - 1) * np.log(x) + (b - 1) * np.log1p(-x))


xb = np.linspace(1e-4, 1 - 1e-4, 600)
beliefs = [(4.0, 8.0, "after 10 orders: 3 bought a pastry"),
           (31.0, 71.0, "after 100 orders: 30 bought a pastry")]
fig, axes = plt.subplots(2, 1, figsize=(4.2, 3.1), sharex=True)
for ax, (a, b, label) in zip(axes, beliefs):
    mean = a / (a + b)
    sd = sqrt(a * b / ((a + b) ** 2 * (a + b + 1)))
    print(f"  Beta({a:g}, {b:g}): mean={mean:.4f}  sd={sd:.4f}")
    ax.plot(xb, beta_pdf(xb, a, b), color=RLBLUE, linewidth=2.0)
    ax.fill_between(xb, 0, beta_pdf(xb, a, b), color=RLGREEN, alpha=0.40)
    ax.axvline(mean, color=RLRED, linestyle="--", linewidth=1.2)
    ax.set_title(f"{label}\nBeta({a:g}, {b:g}),  mean {mean:.2f},"
                 f"  spread ±{sd:.2f}", fontsize=9, loc="left")
    ax.set_ylabel("density", fontsize=10)
    ax.tick_params(labelsize=9)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
axes[1].set_xlabel("p, the true pastry-buying rate", fontsize=10)
axes[1].set_xlim(0, 1)
fig.tight_layout()
save_fig(fig, "continuous_beta")


# ─── Figure 5: the 68-95-99.7 rule on croissant weights ───────────────────
print("\nFigure 5: croissant weights and the empirical rule …")
MU, SIGMA = 60.0, 2.0
xn = np.linspace(MU - 4 * SIGMA, MU + 4 * SIGMA, 600)
yn = np.exp(-0.5 * ((xn - MU) / SIGMA) ** 2) / (SIGMA * sqrt(2 * np.pi))

fig, ax = plt.subplots(figsize=(4.4, 2.9))
bands = [(3, "#EAF2F2", "99.7%"), (2, "#C9E0E1", "95%"), (1, "#9CC7C9", "68%")]
for k, colour, label in bands:
    sel = (xn >= MU - k * SIGMA) & (xn <= MU + k * SIGMA)
    ax.fill_between(xn[sel], 0, yn[sel], color=colour, zorder=1)
    exact = Phi(k) - Phi(-k)
    print(f"  within {k} sd: quoted {label}, exact {exact * 100:.2f}%")

ax.plot(xn, yn, color=RLBLUE, linewidth=2.0, zorder=3)

# Spans drawn ABOVE the curve, so each label unambiguously belongs to one band.
for k, _, label in bands:
    y_arrow = yn.max() * (1.10 + 0.155 * (k - 1))
    ax.annotate("", xy=(MU - k * SIGMA, y_arrow), xytext=(MU + k * SIGMA, y_arrow),
                arrowprops=dict(arrowstyle="<->", color=RLBLUE, linewidth=1.1),
                zorder=4)
    ax.annotate(label, xy=(MU, y_arrow + yn.max() * 0.025), ha="center",
                fontsize=9.5, color="#222222", zorder=5)
ax.set_xticks([MU + k * SIGMA for k in (-3, -2, -1, 0, 1, 2, 3)])
ax.set_xlabel("Croissant weight (g)", fontsize=10)
ax.set_ylabel("density", fontsize=10)
ax.tick_params(labelsize=9)
ax.set_ylim(0, yn.max() * 1.58)
fig.tight_layout()
save_fig(fig, "gaussian_empirical_rule")

z_croissant = (57 - MU) / SIGMA
print(f"  a 57 g croissant: z = {z_croissant:.2f},"
      f"  P(X < 57) = {Phi(z_croissant):.4f}")
z_loaf = (480 - 500) / 15
print(f"  a 480 g loaf   : z = {z_loaf:.3f},"
      f"  P(X < 480) = {Phi(z_loaf):.4f}")
print(f"  P(croissant < 55 g) = {Phi((55 - MU) / SIGMA):.5f}"
      f"  -> {Phi((55 - MU) / SIGMA) * 1000:.1f} per 1000")


# ─── Figure 6: a bivariate Gaussian, its ellipses and its covariance ──────
print("\nFigure 6: hot days and iced coffee …")
rng6 = np.random.default_rng(11)
mu_vec = np.array([22.0, 40.0])          # °C, cups of iced coffee
sd_t, sd_c, rho = 6.0, 12.0, 0.8
cov = np.array([[sd_t ** 2, rho * sd_t * sd_c],
                [rho * sd_t * sd_c, sd_c ** 2]])
days = rng6.multivariate_normal(mu_vec, cov, size=300)
df_days = pd.DataFrame(days, columns=["temp", "cups"])
print(f"  n={len(df_days)}  mean temp={df_days['temp'].mean():.2f}°C"
      f"  mean cups={df_days['cups'].mean():.1f}")
print(f"  sample sd: temp={df_days['temp'].std(ddof=1):.2f}"
      f"  cups={df_days['cups'].std(ddof=1):.2f}")
print(f"  sample cov={np.cov(days.T)[0, 1]:.1f} (theory {cov[0, 1]:.1f})"
      f"  corr={df_days['temp'].corr(df_days['cups']):.3f} (theory {rho})")
print("  sample covariance matrix:")
for row in np.cov(days.T):
    print("    [" + "  ".join(f"{v:7.1f}" for v in row) + " ]")

fig, ax = plt.subplots(figsize=(4.4, 3.1))
ax.scatter(df_days["temp"], df_days["cups"], s=11, color=RLGREEN, alpha=0.65,
           edgecolors="none", zorder=2)

# Ellipses are drawn from the SAMPLE mean and covariance -- the same numbers
# the slide quotes -- so the picture and the matrix on the slide agree exactly.
mu_hat = days.mean(axis=0)
cov_hat = np.cov(days.T)
vals, vecs = np.linalg.eigh(cov_hat)
order = vals.argsort()[::-1]
vals, vecs = vals[order], vecs[:, order]
angle = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
from matplotlib.patches import Ellipse
for k in (1, 2):
    ax.add_patch(Ellipse(mu_hat, 2 * k * sqrt(vals[0]), 2 * k * sqrt(vals[1]),
                         angle=angle, fill=False, edgecolor=RLBLUE,
                         linewidth=1.6, zorder=3))
ax.plot([mu_hat[0]], [mu_hat[1]], "s", color=RLRED, markersize=6, zorder=4)
ax.annotate(f"mean vector\n({mu_hat[0]:.1f} °C, {mu_hat[1]:.1f} cups)",
            xy=mu_hat, xytext=(3.5, 63.0), fontsize=9, color=RLRED,
            arrowprops=dict(arrowstyle="->", color=RLRED, linewidth=1.0))

# The joint outlier quoted on the slide: ordinary on each axis, strange as a pair.
odd = np.array([28.0, 25.0])
diff = odd - mu_hat
maha = sqrt(float(diff @ np.linalg.inv(cov_hat) @ diff))
sd_t_hat, sd_c_hat = sqrt(cov_hat[0, 0]), sqrt(cov_hat[1, 1])
print(f"  odd day (28 °C, 25 cups): z_temp={diff[0] / sd_t_hat:+.2f}"
      f"  z_cups={diff[1] / sd_c_hat:+.2f}  Mahalanobis={maha:.2f} sd")
ax.plot([odd[0]], [odd[1]], "*", color=RLRED, markersize=13, zorder=5)
ax.annotate("28 °C, 25 cups", xy=odd, xytext=(29.0, 17.0), fontsize=9,
            color=RLRED, ha="center",
            arrowprops=dict(arrowstyle="->", color=RLRED, linewidth=1.0))
ax.set_xlabel("Daily high temperature (°C)", fontsize=10)
ax.set_ylabel("Iced coffees sold", fontsize=10)
ax.tick_params(labelsize=9)
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "gaussian_bivariate")

print("\nAll Lecture 4 figures written to", OUT_DIR)
