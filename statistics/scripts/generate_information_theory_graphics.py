#!/usr/bin/env python3
"""Generate lecture figures for statistics/ Lecture 7
(lecture07_entropy.tex, lecture07_kl_mutual_info.tex)

Numbers come from pandas/numpy; rendering is matplotlib, saved directly as
vector PDF (and SVG) -- see the pandas-vector-graphics skill for when this
matplotlib path applies vs. the TikZ path used by ml/'s older scripts.

Every figure is authored at roughly the width it occupies on the slide
(~4.2in for a 0.48-column figure), with explicit font sizes, so that its text
survives being scaled into the frame.

Nothing here is simulated: every entropy, cross-entropy, KL and mutual
information is computed exactly from the stated distributions, and the
Beta posteriors reuse the 7:40 bus stream established in Lecture 6.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import betaln, digamma
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "information_theory"
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


def entropy_bits(p):
    p = np.asarray(p, dtype=float)
    nz = p > 0
    return float(-(p[nz] * np.log2(p[nz])).sum())


def cross_entropy_bits(p, q):
    p, q = np.asarray(p, dtype=float), np.asarray(q, dtype=float)
    nz = p > 0
    return float(-(p[nz] * np.log2(q[nz])).sum())


def kl_bits(p, q):
    return cross_entropy_bits(p, q) - entropy_bits(p)


# ─── The running example: a year of weather in one town ───────────────────
# Chosen so every probability is a power of one half: the optimal yes/no
# question tree then has an exact integer depth per outcome, and the average
# depth equals the entropy exactly rather than approximately.
LABELS = ["sunny", "cloudy", "rain", "storm"]
P_WEATHER = np.array([0.5, 0.25, 0.125, 0.125])
assert abs(P_WEATHER.sum() - 1) < 1e-12

H_WEATHER = entropy_bits(P_WEATHER)
H_UNIFORM = entropy_bits(np.full(4, 0.25))

print("The running example: a year of weather")
df_w = pd.DataFrame({
    "outcome": LABELS,
    "p": P_WEATHER,
    "days_of_360": (P_WEATHER * 360).astype(int),
    "surprise_bits": -np.log2(P_WEATHER),
    "questions": (-np.log2(P_WEATHER)).astype(int),
})
print(df_w.to_string(index=False))
print(f"  H(p) = {H_WEATHER:.4f} bits   H(uniform over 4) = {H_UNIFORM:.4f} bits")
assert abs(H_WEATHER - 1.75) < 1e-12, "the dyadic example must give exactly 1.75"


# ─── Figure 1: the weather distribution and its surprise per outcome ──────
print("\nFigure 1: weather distribution with surprise per outcome …")
fig, ax = plt.subplots(figsize=(4.2, 3.0))
x = np.arange(4)
bars = ax.bar(x, P_WEATHER, width=0.62, color=RLGREEN, edgecolor="white",
              linewidth=0.8)
for xi, p in zip(x, P_WEATHER):
    n_bits = int(round(-np.log2(p)))
    ax.text(xi, p + 0.018, f"{n_bits} bit" + ("" if n_bits == 1 else "s"),
            ha="center", va="bottom", fontsize=9.5, color=RLBLUE)
ax.set_xticks(x)
ax.set_xticklabels(LABELS, fontsize=10.5)
ax.set_ylabel("Probability", fontsize=11)
ax.set_ylim(0, 0.62)
ax.tick_params(labelsize=10)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
ax.set_title(f"H(p) = {H_WEATHER:.2f} bits  (uniform would be {H_UNIFORM:.0f})",
             fontsize=10, loc="left")
fig.tight_layout()
save_fig(fig, "info_entropy_weather")


# ─── Figure 2: binary entropy -- uncertainty peaks at a fair coin ─────────
print("\nFigure 2: the binary entropy curve …")
pp = np.linspace(1e-6, 1 - 1e-6, 800)
Hb = -(pp * np.log2(pp) + (1 - pp) * np.log2(1 - pp))
for probe in (0.5, 0.25, 0.11, 0.7):
    print(f"  H({probe}) = {entropy_bits([probe, 1 - probe]):.4f} bits")

fig, ax = plt.subplots(figsize=(4.2, 2.9))
ax.plot(pp, Hb, color=RLBLUE, linewidth=2.0)
for probe, col in ((0.5, RLORANGE), (0.11, RLRED)):
    h = entropy_bits([probe, 1 - probe])
    ax.plot([probe], [h], "o", color=col, markersize=7, zorder=3)
    ax.annotate(f"p = {probe}\n{h:.2f} bits", xy=(probe, h),
                xytext=(probe + 0.06, h - 0.28), fontsize=9.5, color=col)
ax.set_xlabel("P(rain tomorrow)", fontsize=11)
ax.set_ylabel("Entropy (bits)", fontsize=11)
ax.set_ylim(0, 1.15)
ax.tick_params(labelsize=10)
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "info_binary_entropy")


# ─── Figure 3: three forecasters, and the floor none of them can beat ─────
print("\nFigure 3: cross-entropy of three forecasters …")
FORECASTERS = {
    "knows the\nclimate": P_WEATHER.copy(),
    "assumes all\nfour equal": np.full(4, 0.25),
    "always\nsays sunny": np.array([0.90, 0.05, 0.04, 0.01]),
}
rows = []
for name, q in FORECASTERS.items():
    assert abs(q.sum() - 1) < 1e-12
    rows.append({
        "forecaster": name.replace("\n", " "),
        "H(p,q)": cross_entropy_bits(P_WEATHER, q),
        "KL(p||q)": kl_bits(P_WEATHER, q),
    })
df_f = pd.DataFrame(rows)
print(df_f.to_string(index=False))

fig, ax = plt.subplots(figsize=(4.4, 3.1))
names = list(FORECASTERS)
ce = [cross_entropy_bits(P_WEATHER, q) for q in FORECASTERS.values()]
cols = [RLGREEN, RLORANGE, RLRED]
xb = np.arange(3)
ax.bar(xb, [H_WEATHER] * 3, width=0.6, color=RLBLUE, edgecolor="white",
       linewidth=0.8, label="H(p): unavoidable")
ax.bar(xb, [c - H_WEATHER for c in ce], bottom=[H_WEATHER] * 3, width=0.6,
       color=cols, edgecolor="white", linewidth=0.8)
for xi, c in zip(xb, ce):
    extra = c - H_WEATHER
    ax.text(xi, c + 0.04, f"{c:.2f}", ha="center", va="bottom", fontsize=10,
            color="#222222")
    if extra > 0.02:
        ax.text(xi, H_WEATHER + extra / 2, f"+{extra:.2f}", ha="center",
                va="center", fontsize=9, color="#222222")
ax.axhline(H_WEATHER, color=RLBLUE, linestyle="--", linewidth=1.2)
ax.set_xticks(xb)
ax.set_xticklabels(names, fontsize=9.5)
ax.set_ylabel("Cross-entropy (bits/day)", fontsize=10.5)
ax.set_ylim(0, 3.0)
ax.tick_params(labelsize=10)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
ax.set_title("coloured part = KL(p‖q), the avoidable waste", fontsize=9.5,
             loc="left")
fig.tight_layout()
save_fig(fig, "info_cross_entropy_forecasters")


# ─── Figure 4: KL(posterior ‖ prior) -- how much the data actually said ───
# Reuses Lecture 6's 7:40 bus: prior Beta(8,2), a route truly on time 70% of
# mornings. The stream is regenerated with Lecture 6's seed and rate so the
# counts match the table on that lecture's slides.
print("\nFigure 4: KL(posterior ‖ prior) for the 7:40 bus …")


def kl_beta_bits(a1, b1, a0, b0):
    """KL( Beta(a1,b1) ‖ Beta(a0,b0) ) converted from nats to bits."""
    nats = (betaln(a0, b0) - betaln(a1, b1)
            + (a1 - a0) * digamma(a1)
            + (b1 - b0) * digamma(b1)
            + (a0 - a1 + b0 - b1) * digamma(a1 + b1))
    return float(nats / np.log(2))


# Identical construction to generate_bayesian_graphics.py (seed 21, rate 0.70)
# so the counts quoted here match the table on Lecture 6's slides exactly.
rng = np.random.default_rng(21)
on_time = rng.random(100) < 0.70
A0, B0 = 8.0, 2.0
assert not on_time[0], "Lecture 6 opens with day 1 being late; streams must match"
assert int(on_time[:10].sum()) == 6, "Lecture 6's table says 6 of the first 10"
assert int(on_time.sum()) == 68, "Lecture 6's posterior mean 0.691 needs 68 of 100"
ns = np.arange(0, 101)
kls = [kl_beta_bits(A0 + on_time[:n].sum(), B0 + n - on_time[:n].sum(), A0, B0)
       for n in ns]
for n in (0, 1, 10, 30, 100):
    k = int(on_time[:n].sum())
    print(f"  n={n:3d}  on time={k:3d}  posterior Beta({A0 + k:.0f},{B0 + n - k:.0f})"
          f"  KL={kls[n]:.3f} bits")
assert abs(kls[0]) < 1e-9, "with no data the posterior is the prior, so KL = 0"

fig, ax = plt.subplots(figsize=(4.2, 2.9))
ax.plot(ns, kls, color=RLBLUE, linewidth=2.0)
# Labels sit in the empty region below the curve, with a leader to the point,
# so neither one crosses the line.
for n, col, txt_xy in ((10, RLGREEN, (17, 0.22)), (100, RLORANGE, (50, 1.97))):
    ax.plot([n], [kls[n]], "o", color=col, markersize=7, zorder=3)
    ax.annotate(f"after {n}: {kls[n]:.2f} bits", xy=(n, kls[n]), xytext=txt_xy,
                fontsize=9.5, color=col,
                arrowprops=dict(arrowstyle="-", color=col, linewidth=0.8,
                                shrinkA=0, shrinkB=4))
ax.set_xlabel("Mornings watched", fontsize=11)
ax.set_ylabel("KL(posterior ‖ prior), bits", fontsize=10.5)
ax.set_ylim(0, max(kls) * 1.35)
ax.tick_params(labelsize=10)
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "info_kl_learning")


# ─── Figure 5: which morning question tells you most about rain? ──────────
# A 2x2 joint distribution per candidate question, built from an honest
# conditional model: P(answer | wet) and P(answer | dry) are stated, and
# every entropy below is computed from the resulting joint, not assigned.
print("\nFigure 5: mutual information of three morning questions …")
P_WET = P_WEATHER[2] + P_WEATHER[3]          # rain or storm
H_WET = entropy_bits([P_WET, 1 - P_WET])
print(f"  P(wet) = {P_WET:.3f}   H(wet) = {H_WET:.4f} bits")

QUESTIONS = {
    "sky is grey\nat 7am": (0.80, 0.20),     # P(yes | wet), P(yes | dry)
    "wind from\nthe west": (0.60, 0.40),
    "date is an\neven number": (0.50, 0.50),
}

mi_rows = []
for name, (p_yes_wet, p_yes_dry) in QUESTIONS.items():
    joint = np.array([
        [P_WET * p_yes_wet, P_WET * (1 - p_yes_wet)],            # wet: yes, no
        [(1 - P_WET) * p_yes_dry, (1 - P_WET) * (1 - p_yes_dry)],  # dry: yes, no
    ])
    assert abs(joint.sum() - 1) < 1e-12
    p_ans = joint.sum(axis=0)                                    # P(yes), P(no)
    h_cond = 0.0
    for j, pa in enumerate(p_ans):
        if pa > 0:
            post_wet = joint[0, j] / pa
            h_cond += pa * entropy_bits([post_wet, 1 - post_wet])
    mi = H_WET - h_cond
    mi_rows.append({
        "question": name.replace("\n", " "),
        "P(yes)": p_ans[0],
        "P(wet|yes)": joint[0, 0] / p_ans[0],
        "P(wet|no)": joint[0, 1] / p_ans[1],
        "H(wet|answer)": h_cond,
        "I(wet;answer)": mi,
    })
df_mi = pd.DataFrame(mi_rows)
print(df_mi.to_string(index=False))
assert abs(df_mi.loc[2, "I(wet;answer)"]) < 1e-12, "a useless question must give exactly 0"

fig, ax = plt.subplots(figsize=(4.4, 3.0))
xq = np.arange(3)
mis = df_mi["I(wet;answer)"].to_numpy()
ax.bar(xq, mis, width=0.6, color=[RLBLUE, RLGREEN, GREY], edgecolor="white",
       linewidth=0.8)
for xi, m in zip(xq, mis):
    ax.text(xi, m + 0.006, f"{m:.3f}", ha="center", va="bottom", fontsize=10,
            color="#222222")
ax.axhline(H_WET, color=RLRED, linestyle="--", linewidth=1.3)
ax.text(2.42, H_WET - 0.035, f"H(wet) = {H_WET:.2f}", ha="right", va="top",
        fontsize=9.5, color=RLRED)
ax.set_xticks(xq)
ax.set_xticklabels(list(QUESTIONS), fontsize=9.5)
ax.set_ylabel("Bits learned about rain", fontsize=10.5)
ax.set_ylim(0, H_WET * 1.25)
ax.tick_params(labelsize=10)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "info_information_gain")


# ─── Numbers quoted on slides that have no figure of their own ────────────
print("\nExtra values quoted in the slide text:")
q_uniform = np.full(4, 0.25)
q_sunny = np.array([0.90, 0.05, 0.04, 0.01])
print(f"  KL(p ‖ uniform)   = {kl_bits(P_WEATHER, q_uniform):.4f} bits")
print(f"  KL(uniform ‖ p)   = {kl_bits(q_uniform, P_WEATHER):.4f} bits  (asymmetric)")
print(f"  KL(p ‖ sunny-ish) = {kl_bits(P_WEATHER, q_sunny):.4f} bits")
print(f"  KL(sunny-ish ‖ p) = {kl_bits(q_sunny, P_WEATHER):.4f} bits")
print(f"  waste vs uniform over 360 days: "
      f"{360 * kl_bits(P_WEATHER, q_uniform):.0f} bits")
print(f"  H(p) in nats = {H_WEATHER * np.log(2):.4f}")

print("\nAll Lecture 7 figures written to", OUT_DIR)
