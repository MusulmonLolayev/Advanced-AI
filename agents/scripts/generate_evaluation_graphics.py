#!/usr/bin/env python3
"""Generate lecture figures for agents/ Lecture 8 (lecture08_agent_evaluation.tex)

Numbers come from numpy; rendering is matplotlib, saved directly as vector PDF
(and SVG) -- see the pandas-vector-graphics skill. Most of this lecture's
graphics are schematic and are drawn as inline TikZ in the .tex files instead;
only these two are genuine charts.

Figure 1 plots the Magesh et al. (2024) result as the *reported range*, against
the vendor claim it contradicts. No per-tool point values are invented: the
paper's headline is a range across three products, and that is what is drawn.

Figure 2 is computed, not illustrative: the half-width of a 95% confidence
interval on a measured rate, as a function of evaluation-set size. It is the
Module 0 Lecture 10 point applied to an agent's hallucination rate.
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "agent_eval"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand palette (see agents/theme/rl-theme.tex: RLBlue, RLGreen, RLOrange).
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


# ─── Figure 1: the claim against the measurement ──────────────────────────
# Magesh, Surani, Dahl, Suzgun, Manning & Ho (2024) hand-scored 202 legal
# queries against three commercial RAG-based legal research tools and report
# hallucination between 17% and 33%. The products were marketed as having
# eliminated hallucination. Only the reported RANGE is drawn -- inventing a
# point value per product would be exactly the dishonesty the lecture warns
# against.
print("Figure 1: vendor claim vs. measured hallucination range …")
LO, HI = 17.0, 33.0
print(f"  vendor claim: 0%   measured range: {LO:.0f}-{HI:.0f}%  (n = 202 queries)")

fig, ax = plt.subplots(figsize=(4.3, 1.9))
ax.axhspan(-0.5, 1.5, color="white")

# the measured band
ax.barh([0.55], [HI - LO], left=[LO], height=0.40, color=RLORANGE,
        edgecolor=RLRED, linewidth=1.2, zorder=3)
ax.text((LO + HI) / 2, 0.55, f"{LO:.0f}–{HI:.0f}%", ha="center", va="center",
        fontsize=11, zorder=4)
ax.text(HI + 1.4, 0.55, "measured\n(202 queries)", ha="left", va="center",
        fontsize=9.5, color=RLRED, zorder=4)

# the claim
ax.plot([0], [0.0], marker="|", markersize=22, color=RLGREEN,
        markeredgewidth=3, zorder=3)
ax.text(1.4, 0.0, "vendor claim:\n“hallucination eliminated”", ha="left",
        va="center", fontsize=9.5, color=RLGREEN, zorder=4)

ax.set_xlim(-1, 46)
ax.set_ylim(-0.45, 1.05)
ax.set_yticks([])
ax.set_xticks([0, 10, 20, 30, 40])
ax.set_xticklabels(["0%", "10%", "20%", "30%", "40%"], fontsize=10)
ax.set_xlabel("Responses containing a hallucination", fontsize=10.5)
for side in ("left", "right", "top"):
    ax.spines[side].set_visible(False)
ax.grid(True, axis="x", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "agent_eval_hallucination_gap")


# ─── Figure 2: how many queries an evaluation set needs ────────────────────
# Normal approximation to the binomial: half-width = 1.96 * sqrt(p(1-p)/n).
# Drawn at p = 0.20, near the middle of the range above, which is also close
# to the worst case for a rate in that region.
print("\nFigure 2: 95% CI half-width vs. evaluation-set size …")
P_HAT = 0.20
sizes = np.array([20, 50, 100, 200, 500, 1000])
half = 1.96 * np.sqrt(P_HAT * (1 - P_HAT) / sizes) * 100
for n, h in zip(sizes, half):
    print(f"  n = {n:5d}   measured {P_HAT:.0%} ± {h:.1f} points"
          f"   → [{P_HAT*100 - h:.1f}%, {P_HAT*100 + h:.1f}%]")

fig, ax = plt.subplots(figsize=(4.3, 2.9))
ax.plot(sizes, half, "o-", color=RLBLUE, linewidth=2.0, markersize=6, zorder=3)
for n, h in ((20, half[0]), (200, half[3])):
    ax.annotate(f"±{h:.1f}", xy=(n, h), xytext=(0, 9),
                textcoords="offset points", ha="center", fontsize=10,
                color=RLBLUE)
ax.axhline(5, color=RLRED, linewidth=1.3, linestyle="--", zorder=2)
ax.text(1000, 5.6, "±5 points", ha="right", va="bottom", fontsize=9.5,
        color=RLRED)
ax.set_ylim(0, half[0] * 1.16)     # headroom so the n=20 label is not clipped
ax.set_xscale("log")
ax.set_xticks(sizes)
ax.set_xticklabels([str(n) for n in sizes], fontsize=10)
ax.minorticks_off()
ax.set_xlabel("Queries in the evaluation set", fontsize=10.5)
ax.set_ylabel("95% CI half-width\n(percentage points)", fontsize=10.5)
ax.tick_params(labelsize=10)
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "agent_eval_sample_size")

print("\nAll Lecture 8 figures written to", OUT_DIR)
