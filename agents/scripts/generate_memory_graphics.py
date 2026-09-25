#!/usr/bin/env python3
"""Generate lecture figures for agents/ Lecture 3 (memory).

Rendering is matplotlib, saved directly as vector PDF (and SVG) -- see the
pandas-vector-graphics skill. Nearly all of this lecture's graphics are
schematic (memory tiers, the MemGPT paging diagram, context-window occupancy)
and are drawn as inline TikZ in the .tex files instead.

The one chart here is ALSO schematic, and deliberately so: it reproduces the
*shape* Liu et al. (2023) report for accuracy against the position of the
relevant document, not their measured numbers. The curve is generated from an
explicit formula below so that nothing about it can be mistaken for data, and
the slide that uses it says "schematic" on its face.
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "memory"
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


# --- Figure 1: the U-shape (SCHEMATIC, not measured) -----------------------
# Accuracy is highest when the needed passage sits at either end of the
# context and sags in the middle; the whole curve drops as the context grows.
# Formula, stated openly so the figure cannot be read as an experiment:
#
#     acc(u) = base - depth * sin(pi * u)      u = (pos - 1) / (n - 1)
#
# sin(pi*u) is 0 at both ends and 1 in the middle, which is exactly the
# qualitative claim and nothing more.
print("Figure 1: position-in-context effect (schematic) ...")


def u_shape(n_docs, base, depth):
    pos = np.arange(1, n_docs + 1)
    u = (pos - 1) / (n_docs - 1)
    return pos, base - depth * np.sin(np.pi * u)


fig, ax = plt.subplots(figsize=(4.3, 3.0))

for n_docs, base, depth, colour, label in [
    (10, 0.76, 0.18, RLGREEN, "10 passages"),
    (20, 0.70, 0.30, RLBLUE, "20 passages"),
]:
    pos, acc = u_shape(n_docs, base, depth)
    # Plot against relative position so the two context lengths share an axis.
    rel = (pos - 1) / (n_docs - 1)
    ax.plot(rel, acc, color=colour, linewidth=2.0, marker="o", markersize=3.4)
    # Label at the right-hand end, clear of both curves; a legend box would
    # have to sit on top of one of them in a plot this small.
    ax.annotate(label, xy=(1.04, acc[-1]), ha="left", va="center",
                fontsize=9, color=colour)
    print(f"  {label}: ends={acc[0]:.2f}  middle={acc.min():.2f}  "
          f"drop={acc[0] - acc.min():.2f}")

ax.set_xlabel("position of the needed passage", fontsize=10)
ax.set_ylabel("answer accuracy", fontsize=10)
ax.set_xticks([0, 0.5, 1.0])
ax.set_xticklabels(["first", "middle", "last"], fontsize=9.5)
ax.set_xlim(-0.04, 1.36)
ax.set_ylim(0.30, 0.86)
ax.set_yticks([0.4, 0.6, 0.8])
ax.tick_params(labelsize=9)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
ax.set_title("schematic: the shape reported by Liu et al. (2023), not their data",
             loc="left", fontsize=8.2, color="#666666", style="italic", pad=6)
fig.tight_layout()
save_fig(fig, "memory_lost_in_the_middle")

print("\nAll Lecture 3 figures written to", OUT_DIR)
