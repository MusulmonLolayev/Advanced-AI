#!/usr/bin/env python3
"""Generate lecture figures for statistics/ Lecture 10
(lecture10_evaluation.tex, lecture10_hypothesis_testing.tex)

Numbers come from pandas/numpy; rendering is matplotlib, saved directly as
vector PDF (and SVG) -- see the pandas-vector-graphics skill for when this
matplotlib path applies vs. the TikZ path used by ml/'s older scripts.

Every figure is authored at roughly the width it occupies on the slide
(~4.2in for a 0.48-column figure), with explicit font sizes, so that its text
survives being scaled into the frame.

Nothing here is sketched. The polynomial fits are least-squares fits, the
bias-variance curve is measured at every degree, the bootstrap interval is
resampled, and the permutation null is produced by actually permuting labels.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "evaluation"
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


# ═══════════════════════════════════════════════════════════════════════════
# The running example: the coffee shop of Lectures 3-5 predicts how many iced
# coffees it will sell from the day's high temperature. Lecture 4 already
# showed these two quantities move together; here we try to fit that link and
# then ask how well the fit will do on a day we have not seen.
# ═══════════════════════════════════════════════════════════════════════════

rng = np.random.default_rng(10)

TEMP_LO, TEMP_HI = 16.0, 34.0
NOISE_SD = 2.5


def true_sales(temp):
    """The truth: sales stay flat while it is cool, then climb once it is hot
    and level off again. A straight line cannot follow that shape, which is
    what gives the low-capacity fits genuine bias."""
    return 6.0 + 26.0 / (1.0 + np.exp(-(temp - 27.0) / 2.0))


def make_days(n):
    t = rng.uniform(TEMP_LO, TEMP_HI, size=n)
    y = true_sales(t) + rng.normal(0.0, NOISE_SD, size=n)
    return np.sort(t), y[np.argsort(t)]


N_TRAIN, N_TEST = 20, 40
t_train, y_train = make_days(N_TRAIN)
t_test, y_test = make_days(N_TEST)

df_train = pd.DataFrame({"temp": t_train, "sales": y_train})
df_test = pd.DataFrame({"temp": t_test, "sales": y_test})
print(f"Training days: n={N_TRAIN}  temp {t_train.min():.1f}-{t_train.max():.1f}"
      f"  sales {y_train.min():.1f}-{y_train.max():.1f}")
print(f"Test days:     n={N_TEST}  temp {t_test.min():.1f}-{t_test.max():.1f}"
      f"  sales {y_test.min():.1f}-{y_test.max():.1f}")


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def fit_poly(degree):
    """Least-squares polynomial fit on the training days."""
    return np.polynomial.Polynomial.fit(t_train, y_train, degree)


# ─── Figure 1: three fits of different capacity ────────────────────────────
print("\nFigure 1: three polynomial fits …")
SHOWN = [(1, RLBLUE, "degree 1 (a straight line)"),
         (3, RLGREEN, "degree 3"),
         (9, RLRED, "degree 9")]
# only draw each fit across the range it was actually fitted on -- showing
# extrapolation beyond the training days would be a different lesson
grid = np.linspace(t_train.min(), t_train.max(), 400)

fig, ax = plt.subplots(figsize=(4.3, 3.1))
ax.scatter(t_train, y_train, s=26, color="#555555", zorder=4,
           label="20 training days")
for deg, colour, label in SHOWN:
    model = fit_poly(deg)
    tr = rmse(y_train, model(t_train))
    te = rmse(y_test, model(t_test))
    print(f"  degree {deg}: train RMSE={tr:.2f}  test RMSE={te:.2f}")
    ax.plot(grid, model(grid), color=colour, linewidth=1.8, label=label)
ax.set_xlabel("Day's high temperature (°C)", fontsize=10.5)
ax.set_ylabel("Iced coffees sold", fontsize=10.5)
# room below zero: the degree-9 fit dips to about -2 cups near 21 C, which is
# the most vivid symptom of overfitting on the slide, so it must be visible
ax.axhline(0.0, color="#999999", linewidth=0.9)
ax.set_ylim(-6, 40)
ax.tick_params(labelsize=9.5)
ax.legend(fontsize=8.2, loc="upper left", frameon=True, facecolor="white",
          framealpha=0.95, edgecolor="#cccccc")
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "evaluation_polynomial_fits")


# ─── Figure 2: the bias-variance curve, measured ───────────────────────────
print("\nFigure 2: train vs test error against capacity …")
DEGREES = list(range(1, 11))
rows = []
for deg in DEGREES:
    model = fit_poly(deg)
    rows.append({"degree": deg,
                 "train": rmse(y_train, model(t_train)),
                 "test": rmse(y_test, model(t_test))})
df_bv = pd.DataFrame(rows).set_index("degree")
print(df_bv.round(2).to_string())
best_deg = int(df_bv["test"].idxmin())
best_test = float(df_bv["test"].min())
print(f"  best test RMSE at degree {best_deg}: {best_test:.2f}")
print(f"  degree 1: train {df_bv.loc[1, 'train']:.2f}  test {df_bv.loc[1, 'test']:.2f}")
print(f"  degree 10: train {df_bv.loc[10, 'train']:.2f}  test {df_bv.loc[10, 'test']:.2f}")

Y_TOP = 6.0
off_scale = df_bv[df_bv["test"] > Y_TOP]
print("  off the chart:", {int(d): round(v, 1)
                           for d, v in off_scale["test"].items()})

fig, ax = plt.subplots(figsize=(4.3, 3.1))
ax.plot(df_bv.index, df_bv["train"], "o-", color=RLGREEN, linewidth=1.8,
        markersize=5, label="training error")
ax.plot(df_bv.index, df_bv["test"], "s-", color=RLRED, linewidth=1.8,
        markersize=5, label="test error")
ax.axvline(best_deg, color="#777777", linestyle="--", linewidth=1.2)
ax.annotate(f"best: degree {best_deg}", xy=(best_deg + 0.2, 0.28),
            fontsize=9, color="#444444")
for deg, val in off_scale["test"].items():
    ax.annotate(f"↑{val:.0f}", xy=(deg, Y_TOP - 0.35), ha="center",
                va="center", fontsize=8.6, color=RLRED)
ax.set_xlabel("Degree of the fitted curve (capacity)", fontsize=10.5)
ax.set_ylabel("Error (RMSE, cups)", fontsize=10.5)
ax.set_ylim(0, Y_TOP)
ax.set_xticks([1, 2, 4, 6, 8, 10])
ax.tick_params(labelsize=9.5)
ax.legend(fontsize=9, loc="upper left", frameon=True, facecolor="white",
          framealpha=0.95, edgecolor="#cccccc")
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "evaluation_bias_variance")


# ─── Figure 3: bootstrap interval on the test error ────────────────────────
print("\nFigure 3: bootstrapping the test error …")
chosen = fit_poly(best_deg)
resid_test = y_test - chosen(t_test)
point_rmse = rmse(y_test, chosen(t_test))

B = 10_000
boot_rng = np.random.default_rng(2024)
boot = np.empty(B)
for b in range(B):
    idx = boot_rng.integers(0, N_TEST, size=N_TEST)
    boot[b] = float(np.sqrt(np.mean(resid_test[idx] ** 2)))
lo, hi = np.percentile(boot, [2.5, 97.5])
print(f"  point estimate RMSE = {point_rmse:.2f} cups")
print(f"  95% bootstrap interval = [{lo:.2f}, {hi:.2f}]  width {hi - lo:.2f}")
print(f"  bootstrap mean {boot.mean():.2f}  sd {boot.std(ddof=1):.2f}")

fig, ax = plt.subplots(figsize=(4.3, 3.0))
ax.hist(boot, bins=45, color=RLGREEN, alpha=0.75, edgecolor="white",
        linewidth=0.4)
ax.axvline(point_rmse, color=RLBLUE, linewidth=2.0,
           label=f"measured: {point_rmse:.2f}")
for edge in (lo, hi):
    ax.axvline(edge, color=RLRED, linestyle="--", linewidth=1.5)
ax.axvline(hi, color=RLRED, linestyle="--", linewidth=1.5,
           label=f"95%: [{lo:.2f}, {hi:.2f}]")
ax.set_xlabel("Test RMSE from a resampled test set", fontsize=10.5)
ax.set_ylabel("Resamples", fontsize=10.5)
ax.set_ylim(0, np.histogram(boot, bins=45)[0].max() * 1.32)
ax.tick_params(labelsize=9.5)
ax.legend(fontsize=8.6, loc="upper right", frameon=True, facecolor="white",
          framealpha=0.95, edgecolor="#cccccc")
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "evaluation_bootstrap")


# ─── Figure 4: the permutation test, actually permuted ─────────────────────
print("\nFigure 4: permutation test on two menu layouts …")
N_A = N_B = 60
BUY_A, BUY_B = 21, 30
labels = np.array([0] * N_A + [1] * N_B)
outcomes = np.array([1] * BUY_A + [0] * (N_A - BUY_A) +
                    [1] * BUY_B + [0] * (N_B - BUY_B))
rate_a = BUY_A / N_A
rate_b = BUY_B / N_B
observed = rate_b - rate_a
print(f"  menu A: {BUY_A}/{N_A} = {rate_a:.3f}")
print(f"  menu B: {BUY_B}/{N_B} = {rate_b:.3f}")
print(f"  observed difference = {observed:.3f}")

P = 20_000
perm_rng = np.random.default_rng(7)
diffs = np.empty(P)
pool = outcomes.copy()
for i in range(P):
    perm_rng.shuffle(pool)
    diffs[i] = pool[N_A:].mean() - pool[:N_A].mean()
p_two_sided = float(np.mean(np.abs(diffs) >= abs(observed) - 1e-12))
print(f"  permutation p-value (two-sided) = {p_two_sided:.4f}")

# the normal-approximation check, for the slide's cross-check
pooled = (BUY_A + BUY_B) / (N_A + N_B)
se_pool = np.sqrt(pooled * (1 - pooled) * (1 / N_A + 1 / N_B))
z_stat = observed / se_pool
from math import erf, sqrt as msqrt
p_normal = 2 * (1 - 0.5 * (1 + erf(abs(z_stat) / msqrt(2))))
print(f"  pooled rate {pooled:.4f}  SE {se_pool:.4f}  z {z_stat:.3f}"
      f"  normal p {p_normal:.4f}")

# how many customers per menu would be needed to detect this gap at p<0.05?
for n_each in range(60, 1200, 10):
    se_n = np.sqrt(pooled * (1 - pooled) * (2 / n_each))
    if abs(observed) / se_n >= 1.96:
        print(f"  a gap of {observed:.2f} needs about {n_each} customers per menu")
        needed = n_each
        break

fig, ax = plt.subplots(figsize=(4.3, 3.0))
# the difference can only land on a discrete grid (both groups have 60
# customers and 51 buys are shared out), so put one bin on each possible value
step = 2.0 / N_A
edges = np.arange(diffs.min() - step / 2, diffs.max() + step, step)
ax.hist(diffs, bins=edges, color=GREY, edgecolor="white", linewidth=0.4,
        label="if the menus were identical")
extreme = np.abs(diffs) >= abs(observed) - 1e-12
ax.hist(diffs[extreme], bins=edges, color=RLORANGE, edgecolor="white",
        linewidth=0.4, label=f"as extreme: {100 * p_two_sided:.1f}%")
ax.axvline(observed, color=RLRED, linewidth=2.0,
           label=f"observed: {observed:+.2f}")
ax.axvline(-observed, color=RLRED, linewidth=1.0, linestyle=":")
ax.set_xlabel("Difference in buy rate after shuffling labels", fontsize=10.5)
ax.set_ylabel("Shuffles", fontsize=10.5)
ax.set_ylim(0, np.histogram(diffs, bins=edges)[0].max() * 1.38)
ax.tick_params(labelsize=9.5)
ax.legend(fontsize=8.2, loc="upper left", frameon=True, facecolor="white",
          framealpha=0.95, edgecolor="#cccccc")
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "evaluation_permutation")


# ─── Figure 5: reliability diagram ─────────────────────────────────────────
print("\nFigure 5: reliability diagram for two forecasters …")
cal_rng = np.random.default_rng(99)
BUCKETS = np.array([0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95])
PER_BUCKET = 400

# Forecaster H is honest: when she says 0.7, it happens 70% of the time.
# Forecaster O is overconfident: he pushes every claim away from 0.5, so his
# stated 0.9 only happens about 0.74 of the time. Both are *simulated from a
# stated true rate*, so the diagram measures a real frequency.
def squash(p, strength=0.55):
    """Pull a stated probability back toward 0.5 to get the true rate."""
    return 0.5 + strength * (p - 0.5)


rows = []
for p in BUCKETS:
    hits_h = cal_rng.binomial(PER_BUCKET, p)
    hits_o = cal_rng.binomial(PER_BUCKET, squash(p))
    rows.append({"stated": p,
                 "honest": hits_h / PER_BUCKET,
                 "overconfident": hits_o / PER_BUCKET})
df_cal = pd.DataFrame(rows)
print(df_cal.round(3).to_string(index=False))

ece_h = float(np.mean(np.abs(df_cal["honest"] - df_cal["stated"])))
ece_o = float(np.mean(np.abs(df_cal["overconfident"] - df_cal["stated"])))
print(f"  mean gap  honest {ece_h:.3f}   overconfident {ece_o:.3f}")
row95 = df_cal[np.isclose(df_cal["stated"], 0.95)].iloc[0]
print(f"  at a stated 0.95: honest {row95['honest']:.3f},"
      f" overconfident {row95['overconfident']:.3f}")

fig, ax = plt.subplots(figsize=(4.0, 3.4))
ax.plot([0, 1], [0, 1], color="#888888", linestyle="--", linewidth=1.3,
        label="perfect calibration")
ax.plot(df_cal["stated"], df_cal["honest"], "o-", color=RLGREEN,
        linewidth=1.8, markersize=5, label=f"honest (gap {ece_h:.02f})")
ax.plot(df_cal["stated"], df_cal["overconfident"], "s-", color=RLRED,
        linewidth=1.8, markersize=5, label=f"overconfident (gap {ece_o:.02f})")
ax.set_xlabel("Probability the forecaster stated", fontsize=10.5)
ax.set_ylabel("How often it happened", fontsize=10.5)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect("equal")
ax.tick_params(labelsize=9.5)
ax.legend(fontsize=8.4, loc="upper left", frameon=True, facecolor="white",
          framealpha=0.95, edgecolor="#cccccc")
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "evaluation_reliability")


# ─── Numbers quoted on slides that are not themselves figures ──────────────
print("\nSlide numbers (no figure):")

# 5-fold cross-validation on the 20 training days, degree 3
K = 5
fold_rng = np.random.default_rng(5)
order = fold_rng.permutation(N_TRAIN)
folds = np.array_split(order, K)
cv_scores = []
for k in range(K):
    val_idx = folds[k]
    tr_idx = np.concatenate([folds[j] for j in range(K) if j != k])
    m = np.polynomial.Polynomial.fit(t_train[tr_idx], y_train[tr_idx], 3)
    cv_scores.append(rmse(y_train[val_idx], m(t_train[val_idx])))
cv_scores = np.array(cv_scores)
print(f"  5-fold RMSE per fold: {np.round(cv_scores, 2).tolist()}")
print(f"  5-fold mean {cv_scores.mean():.2f}  sd {cv_scores.std(ddof=1):.2f}")

# standard error on a reported accuracy, for the "0.3% is not a difference" slide
for acc, n in ((0.90, 1000), (0.903, 1000), (0.90, 10000)):
    se = np.sqrt(acc * (1 - acc) / n)
    print(f"  accuracy {acc:.3f} on n={n}: SE = {se:.4f}"
          f"  (95% half-width {1.96 * se:.4f})")

# multiple comparisons: chance of at least one false alarm
for m in (1, 10, 20, 50):
    print(f"  {m} independent tests at 0.05: P(at least one false alarm)"
          f" = {1 - 0.95 ** m:.3f}")

print("\nAll Lecture 10 figures written to", OUT_DIR)
