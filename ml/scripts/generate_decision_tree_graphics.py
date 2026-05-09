#!/usr/bin/env python3
"""Generate decision tree teaching graphics with matplotlib."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "decision_trees"

BLUE = "#2b6cb0"
ORANGE = "#dd6b20"
GREEN = "#2f855a"
RED = "#c53030"
DARK = "#1f2937"
GRAY = "#6b7280"
LIGHT = "#e5e7eb"
PURPLE = "#6b46c1"


def _configure_mpl() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "mathtext.fontset": "dejavusans",
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.labelcolor": DARK,
            "xtick.color": DARK,
            "ytick.color": DARK,
        }
    )


def _save(fig: plt.Figure, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{name}.svg", format="svg", bbox_inches="tight", pad_inches=0.08)
    fig.savefig(OUT_DIR / f"{name}.pdf", format="pdf", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def _style_axes(ax: plt.Axes, xlabel: str = r"$x_1$", ylabel: str = r"$x_2$") -> None:
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, color=LIGHT, linewidth=0.8)
    ax.set_facecolor("white")


def build_purity_impurity() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.7), facecolor="white")
    fig.subplots_adjust(left=0.06, right=0.98, bottom=0.16, top=0.82, wspace=0.28)

    panels = [
        (axes[0], "Pure node", [BLUE] * 8, r"$p=(1,0)$", r"$I_G=0$"),
        (axes[1], "Mixed node", [BLUE, ORANGE, BLUE, ORANGE, ORANGE, BLUE, ORANGE, BLUE], r"$p=(0.5,0.5)$", r"$I_G=0.5$"),
    ]

    for ax, title, colors, proportion, impurity in panels:
        ax.set_title(title, fontsize=13, color=DARK)
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 3)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")

        xs = [1.25, 1.75, 2.25, 2.75, 1.25, 1.75, 2.25, 2.75]
        ys = [2.0, 2.0, 2.0, 2.0, 1.45, 1.45, 1.45, 1.45]
        for x_pos, y_pos, color in zip(xs, ys, colors):
            marker = "o" if color == BLUE else "s"
            ax.scatter(x_pos, y_pos, s=110, color=color, marker=marker, edgecolor="white", linewidth=0.9, zorder=3)

        ax.add_patch(
            FancyBboxPatch(
                (0.65, 0.75),
                2.7,
                1.8,
                boxstyle="round,pad=0.05,rounding_size=0.08",
                fill=False,
                edgecolor=GRAY,
                linewidth=1.2,
                linestyle=(0, (5, 4)),
            )
        )
        ax.text(2.0, 0.45, proportion, ha="center", fontsize=11, color=DARK)
        ax.text(2.0, 0.15, impurity, ha="center", fontsize=11, color=PURPLE)

    fig.suptitle("Purity means one dominant class; impurity means mixed classes", fontsize=13, color=DARK)
    _save(fig, "decision_tree_purity_impurity")


def _toy_data() -> tuple[np.ndarray, np.ndarray]:
    x = np.array(
        [
            [0.8, 1.1],
            [1.2, 1.7],
            [1.5, 0.8],
            [2.1, 1.3],
            [2.7, 2.2],
            [3.0, 1.0],
            [3.4, 2.8],
            [3.8, 1.7],
            [4.2, 3.1],
            [4.6, 2.3],
            [5.1, 3.4],
            [5.4, 2.6],
        ]
    )
    y = np.array([0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1])
    return x, y


def build_formal_setup() -> None:
    x, y = _toy_data()

    fig, ax = plt.subplots(figsize=(6.8, 4.4), facecolor="white")
    _style_axes(ax)
    ax.set_title("Labeled examples for a supervised tree", fontsize=13, color=DARK)
    ax.set_xlim(0.2, 5.9)
    ax.set_ylim(0.4, 3.8)
    ax.set_aspect("equal", adjustable="box")

    ax.scatter(x[y == 0, 0], x[y == 0, 1], s=85, color=BLUE, edgecolor="white", linewidth=0.9, zorder=3, label=r"$y=0$")
    ax.scatter(x[y == 1, 0], x[y == 1, 1], s=85, color=ORANGE, marker="s", edgecolor="white", linewidth=0.9, zorder=3, label=r"$y=1$")
    ax.legend(frameon=True, facecolor="white", edgecolor=LIGHT, loc="upper left")

    for idx, point in enumerate(x, start=1):
        ax.text(point[0] + 0.06, point[1] + 0.07, rf"$x_{{{idx}}}$", fontsize=9, color=DARK)

    ax.text(3.1, 0.65, r"learn rules from $(x_i,y_i)$", fontsize=12, color=DARK)
    _save(fig, "decision_tree_formal_setup")


def build_split_rule() -> None:
    x, y = _toy_data()
    threshold = 2.4

    fig, ax = plt.subplots(figsize=(6.8, 4.4), facecolor="white")
    _style_axes(ax)
    ax.set_title(r"One candidate split: $x_1 \leq t$", fontsize=13, color=DARK)
    ax.set_xlim(0.2, 5.9)
    ax.set_ylim(0.4, 3.8)
    ax.set_aspect("equal", adjustable="box")

    ax.axvspan(0.2, threshold, color=BLUE, alpha=0.08, zorder=0)
    ax.axvspan(threshold, 5.9, color=ORANGE, alpha=0.08, zorder=0)
    ax.axvline(threshold, color=PURPLE, linewidth=2.0, linestyle=(0, (6, 4)), zorder=2)
    ax.scatter(x[y == 0, 0], x[y == 0, 1], s=85, color=BLUE, edgecolor="white", linewidth=0.9, zorder=3)
    ax.scatter(x[y == 1, 0], x[y == 1, 1], s=85, color=ORANGE, marker="s", edgecolor="white", linewidth=0.9, zorder=3)

    ax.text(0.55, 3.45, r"$D_L=\{x_i:x_{i1}\leq t\}$", fontsize=11, color=BLUE)
    ax.text(3.05, 3.45, r"$D_R=\{x_i:x_{i1}>t\}$", fontsize=11, color=ORANGE)
    ax.text(threshold + 0.08, 0.65, r"$t=2.4$", fontsize=11, color=PURPLE)
    _save(fig, "decision_tree_split_rule")


def build_impurity_curves() -> None:
    p = np.linspace(0.001, 0.999, 300)
    gini = 1.0 - p**2 - (1.0 - p) ** 2
    entropy = -(p * np.log2(p) + (1.0 - p) * np.log2(1.0 - p))

    fig, ax = plt.subplots(figsize=(6.8, 4.3), facecolor="white")
    _style_axes(ax, xlabel=r"class proportion $p$", ylabel="impurity")
    ax.set_title("Impurity is largest when a node is mixed", fontsize=13, color=DARK)
    ax.plot(p, gini, color=BLUE, linewidth=2.4, label="Gini")
    ax.plot(p, entropy, color=ORANGE, linewidth=2.4, label="Entropy")
    ax.axvline(0.5, color=GRAY, linewidth=1.2, linestyle=(0, (4, 4)))
    ax.scatter([0, 1], [0, 0], color=GREEN, s=55, zorder=3)
    ax.text(0.06, 0.12, "pure", fontsize=11, color=GREEN)
    ax.text(0.80, 0.12, "pure", fontsize=11, color=GREEN)
    ax.text(0.53, 0.93, "mixed", fontsize=11, color=GRAY)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.legend(frameon=True, facecolor="white", edgecolor=LIGHT)
    _save(fig, "decision_tree_impurity_curves")


def build_split_gain() -> None:
    x, y = _toy_data()
    thresholds = np.array([1.35, 1.8, 2.4, 2.85, 3.2, 3.6, 4.0, 4.4, 4.85])

    def gini(labels: np.ndarray) -> float:
        if labels.size == 0:
            return 0.0
        p1 = float(np.mean(labels == 1))
        p0 = 1.0 - p1
        return 1.0 - p0**2 - p1**2

    parent = gini(y)
    gains = []
    for t in thresholds:
        left = y[x[:, 0] <= t]
        right = y[x[:, 0] > t]
        weighted = (left.size / y.size) * gini(left) + (right.size / y.size) * gini(right)
        gains.append(parent - weighted)
    gains = np.array(gains)
    best_idx = int(np.argmax(gains))

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2), facecolor="white")
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.16, top=0.86, wspace=0.24)

    ax = axes[0]
    _style_axes(ax)
    ax.set_title("Best split on the toy data", fontsize=13, color=DARK)
    ax.set_xlim(0.2, 5.9)
    ax.set_ylim(0.4, 3.8)
    ax.set_aspect("equal", adjustable="box")
    ax.axvline(thresholds[best_idx], color=PURPLE, linewidth=2.0, linestyle=(0, (6, 4)))
    ax.scatter(x[y == 0, 0], x[y == 0, 1], s=80, color=BLUE, edgecolor="white", linewidth=0.8, zorder=3)
    ax.scatter(x[y == 1, 0], x[y == 1, 1], s=80, color=ORANGE, marker="s", edgecolor="white", linewidth=0.8, zorder=3)
    ax.text(thresholds[best_idx] + 0.08, 0.65, rf"$t={thresholds[best_idx]:.2f}$", fontsize=11, color=PURPLE)

    ax = axes[1]
    _style_axes(ax, xlabel=r"threshold $t$", ylabel=r"impurity decrease $\Delta I$")
    ax.set_title("Search over candidate thresholds", fontsize=13, color=DARK)
    ax.plot(thresholds, gains, color=BLUE, linewidth=2.2, marker="o", markersize=6)
    ax.scatter([thresholds[best_idx]], [gains[best_idx]], s=120, color=PURPLE, zorder=4)
    ax.annotate(
        "choose largest decrease",
        xy=(thresholds[best_idx], gains[best_idx]),
        xytext=(thresholds[best_idx] + 0.45, gains[best_idx] - 0.08),
        fontsize=11,
        color=DARK,
        arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.1),
    )
    ax.set_ylim(0.0, max(gains) + 0.08)
    _save(fig, "decision_tree_split_gain")


def _node(ax: plt.Axes, xy: tuple[float, float], text: str, color: str = LIGHT, width: float = 2.15) -> None:
    x0, y0 = xy
    patch = FancyBboxPatch(
        (x0 - width / 2.0, y0 - 0.27),
        width,
        0.54,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        facecolor=color,
        edgecolor=DARK,
        linewidth=1.0,
    )
    ax.add_patch(patch)
    ax.text(x0, y0, text, ha="center", va="center", fontsize=10.5, color=DARK)


def _arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], label: str) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="->",
            mutation_scale=12,
            linewidth=1.2,
            color=GRAY,
            shrinkA=12,
            shrinkB=12,
        )
    )
    mid = ((start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0)
    ax.text(mid[0], mid[1] + 0.12, label, ha="center", fontsize=9.5, color=GRAY)


def build_tree_prediction() -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.6), facecolor="white")
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    ax.set_title("A tree is a sequence of questions", fontsize=13, color=DARK)

    _node(ax, (4.0, 3.8), r"$x_1 \leq 2.4?$", color="#f1ecff")
    _node(ax, (2.0, 2.4), r"predict $0$", color="#eaf4ff", width=1.55)
    _node(ax, (6.0, 2.4), r"$x_2 \leq 1.4?$", color="#f1ecff")
    _node(ax, (5.0, 1.0), r"predict $0$", color="#eaf4ff", width=1.55)
    _node(ax, (7.0, 1.0), r"predict $1$", color="#fff2df", width=1.55)

    _arrow(ax, (4.0, 3.55), (2.0, 2.67), "yes")
    _arrow(ax, (4.0, 3.55), (6.0, 2.67), "no")
    _arrow(ax, (6.0, 2.15), (5.0, 1.27), "yes")
    _arrow(ax, (6.0, 2.15), (7.0, 1.27), "no")

    _save(fig, "decision_tree_prediction")


def build_regions() -> None:
    x, y = _toy_data()

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2), facecolor="white")
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.16, top=0.86, wspace=0.20)

    for ax in axes:
        _style_axes(ax)
        ax.set_xlim(0.2, 5.9)
        ax.set_ylim(0.4, 3.8)
        ax.set_aspect("equal", adjustable="box")
        ax.scatter(x[y == 0, 0], x[y == 0, 1], s=80, color=BLUE, edgecolor="white", linewidth=0.8, zorder=3)
        ax.scatter(x[y == 1, 0], x[y == 1, 1], s=80, color=ORANGE, marker="s", edgecolor="white", linewidth=0.8, zorder=3)

    axes[0].set_title("Depth 1", fontsize=13, color=DARK)
    axes[0].add_patch(Rectangle((0.2, 0.4), 2.2, 3.4, facecolor=BLUE, alpha=0.08, edgecolor="none", zorder=0))
    axes[0].add_patch(Rectangle((2.4, 0.4), 3.5, 3.4, facecolor=ORANGE, alpha=0.08, edgecolor="none", zorder=0))
    axes[0].axvline(2.4, color=PURPLE, linewidth=2.0, linestyle=(0, (6, 4)))

    axes[1].set_title("Depth 2", fontsize=13, color=DARK)
    axes[1].add_patch(Rectangle((0.2, 0.4), 2.2, 3.4, facecolor=BLUE, alpha=0.08, edgecolor="none", zorder=0))
    axes[1].add_patch(Rectangle((2.4, 0.4), 3.5, 1.0, facecolor=BLUE, alpha=0.08, edgecolor="none", zorder=0))
    axes[1].add_patch(Rectangle((2.4, 1.4), 3.5, 2.4, facecolor=ORANGE, alpha=0.08, edgecolor="none", zorder=0))
    axes[1].axvline(2.4, color=PURPLE, linewidth=2.0, linestyle=(0, (6, 4)))
    axes[1].hlines(1.4, 2.4, 5.9, color=GREEN, linewidth=2.0, linestyle=(0, (6, 4)))

    _save(fig, "decision_tree_regions")


def build_overfitting() -> None:
    rng = np.random.default_rng(11)
    class0 = rng.normal(loc=(1.6, 1.5), scale=(0.45, 0.42), size=(22, 2))
    class1 = rng.normal(loc=(3.8, 2.5), scale=(0.45, 0.42), size=(22, 2))
    noise0 = np.array([[4.1, 1.25], [3.6, 1.0]])
    noise1 = np.array([[1.25, 2.75], [1.8, 2.95]])
    x0 = np.vstack([class0, noise0])
    x1 = np.vstack([class1, noise1])

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2), facecolor="white")
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.16, top=0.86, wspace=0.20)

    for ax, title in zip(axes, ["Controlled depth", "Too much depth"]):
        _style_axes(ax)
        ax.set_title(title, fontsize=13, color=DARK)
        ax.set_xlim(0.4, 5.0)
        ax.set_ylim(0.4, 3.7)
        ax.set_aspect("equal", adjustable="box")
        ax.scatter(x0[:, 0], x0[:, 1], s=55, color=BLUE, edgecolor="white", linewidth=0.7, zorder=3)
        ax.scatter(x1[:, 0], x1[:, 1], s=55, color=ORANGE, marker="s", edgecolor="white", linewidth=0.7, zorder=3)

    axes[0].axvline(2.75, color=PURPLE, linewidth=2.0, linestyle=(0, (6, 4)))
    axes[0].text(2.83, 0.75, "simple rule", fontsize=11, color=PURPLE)

    for xpos in [1.1, 1.55, 2.1, 2.75, 3.2, 3.75, 4.25]:
        axes[1].axvline(xpos, color=GRAY, linewidth=1.0, linestyle=(0, (3, 4)), alpha=0.85)
    for ypos in [1.05, 1.45, 1.9, 2.35, 2.75, 3.1]:
        axes[1].axhline(ypos, color=GRAY, linewidth=1.0, linestyle=(0, (3, 4)), alpha=0.85)
    axes[1].text(2.05, 0.75, "many small regions", fontsize=11, color=GRAY)

    _save(fig, "decision_tree_overfitting")


def main() -> None:
    _configure_mpl()
    build_purity_impurity()
    build_formal_setup()
    build_split_rule()
    build_impurity_curves()
    build_split_gain()
    build_tree_prediction()
    build_regions()
    build_overfitting()


if __name__ == "__main__":
    main()
