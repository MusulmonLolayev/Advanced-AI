#!/usr/bin/env python3
"""Generate lecture figures for agents/ Lecture 1 (lecture01_what_is_an_agent.tex)

Numbers come from numpy; rendering is matplotlib, saved directly as vector PDF
(and SVG) -- see the pandas-vector-graphics skill. Most of this lecture's
graphics are schematic and are drawn as inline TikZ in the .tex file instead;
only the compounding-error curve is a genuine chart.
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "agent_loop"
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


# --- Figure 1: p^k -- why trajectory length is the dominant variable --------
print("Figure 1: per-step reliability compounded over a trajectory ...")
k = np.arange(1, 21)
levels = [(0.99, RLBLUE), (0.95, RLGREEN), (0.90, RLORANGE), (0.80, RLRED)]

# Authored at roughly the width it occupies on the slide (a 0.50 column),
# so its text is not shrunk into illegibility by \includegraphics.
fig, ax = plt.subplots(figsize=(4.3, 3.1))
for p, colour in levels:
    ax.plot(k, p ** k, color=colour, linewidth=1.9)
    # Label each curve at its right-hand end: clearer than a legend box, which
    # would have to sit on top of one of the curves in a plot this small.
    ax.annotate(f"$p={p:.2f}$", xy=(20.5, max(p ** 20, 0.045)), va="center", ha="left",
                fontsize=9, color=colour)
    print(f"  p={p:.2f}:  k=5 -> {p**5:.3f}   k=10 -> {p**10:.3f}   k=20 -> {p**20:.3f}")

ax.axvline(10, color="#888888", linewidth=1.0, linestyle=":")
ax.annotate("10 steps", xy=(10.4, 0.99), ha="left", va="top",
            fontsize=9, color="#555555")

ax.set_xlabel("steps in the trajectory, $k$", fontsize=10)
ax.set_ylabel("P(all steps correct)", fontsize=10)
ax.set_xlim(1, 25.5)
ax.set_ylim(0, 1.04)
ax.set_xticks([1, 5, 10, 15, 20])
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.tick_params(labelsize=9)
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "agent_loop_compounding")
