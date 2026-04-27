#!/usr/bin/env python3
"""Generate DBSCAN teaching graphics with matplotlib."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch


BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "dbscan"

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


def build_formal_setup() -> None:
    dense = np.array(
        [
            [1.0, 1.0],
            [1.2, 1.7],
            [1.8, 1.1],
            [2.0, 1.8],
            [2.4, 1.2],
            [2.7, 1.9],
        ]
    )
    sparse = np.array([[5.6, 5.0], [6.6, 5.8], [7.4, 4.8]])
    data = np.vstack([dense, sparse])
    query = dense[2]
    eps = 1.2

    fig, ax = plt.subplots(figsize=(6.8, 4.4), facecolor="white")
    _style_axes(ax)
    ax.set_title("Local density depends on $\\varepsilon$ and MinPts", fontsize=13, color=DARK)
    ax.set_xlim(0.2, 8.0)
    ax.set_ylim(0.3, 6.6)
    ax.set_aspect("equal", adjustable="box")

    ax.scatter(dense[:, 0], dense[:, 1], s=70, color=BLUE, zorder=3)
    ax.scatter(sparse[:, 0], sparse[:, 1], s=70, color=GRAY, zorder=3)
    ax.scatter(query[0], query[1], s=140, color=ORANGE, edgecolor="white", linewidth=1.1, zorder=4)
    ax.add_patch(Circle(query, radius=eps, fill=False, linestyle=(0, (6, 4)), linewidth=2.0, edgecolor=ORANGE))

    for idx, point in enumerate(data, start=1):
        ax.text(point[0] + 0.08, point[1] + 0.10, rf"$x_{idx}$", fontsize=10, color=DARK)

    ax.text(query[0] - 0.2, query[1] - 0.55, r"$x_i$", fontsize=12, color=ORANGE)
    ax.text(query[0] + 0.95, query[1] + 0.55, r"$\varepsilon$", fontsize=12, color=ORANGE)
    ax.text(5.0, 6.0, r"MinPts = local count threshold", fontsize=11, color=DARK)

    _save(fig, "dbscan_formal_setup")


def build_eps_neighborhood() -> None:
    points = np.array(
        [
            [1.0, 1.1],
            [1.2, 2.0],
            [2.0, 1.4],
            [2.2, 2.2],
            [3.2, 1.2],
            [4.2, 2.4],
        ]
    )
    query = points[2]
    eps = 1.25
    inside = np.linalg.norm(points - query, axis=1) <= eps

    fig, ax = plt.subplots(figsize=(6.6, 4.2), facecolor="white")
    _style_axes(ax)
    ax.set_title(r"The $\varepsilon$-neighborhood $N_\varepsilon(x_i)$", fontsize=13, color=DARK)
    ax.set_xlim(0.4, 4.9)
    ax.set_ylim(0.5, 3.1)
    ax.set_aspect("equal", adjustable="box")

    ax.scatter(points[~inside, 0], points[~inside, 1], s=75, color=GRAY, zorder=3)
    ax.scatter(points[inside, 0], points[inside, 1], s=85, color=BLUE, zorder=3)
    ax.scatter(query[0], query[1], s=145, color=ORANGE, edgecolor="white", linewidth=1.2, zorder=4)
    ax.add_patch(Circle(query, radius=eps, fill=True, facecolor=ORANGE, alpha=0.08, edgecolor=ORANGE, linewidth=1.8))

    for idx, point in enumerate(points, start=1):
        ax.text(point[0] + 0.05, point[1] + 0.08, rf"$x_{idx}$", fontsize=10, color=DARK)

    ax.text(3.15, 2.75, r"inside: $x_j \in N_\varepsilon(x_i)$", fontsize=11, color=BLUE)
    ax.text(3.15, 2.45, r"outside: $\|x_j-x_i\|_2 > \varepsilon$", fontsize=11, color=GRAY)

    _save(fig, "dbscan_eps_neighborhood")


def build_point_types() -> None:
    core = np.array([1.8, 1.9])
    neighbors = np.array([[1.1, 1.4], [1.1, 2.5], [2.0, 1.0], [2.6, 1.4], [2.7, 2.4]])
    border = np.array([4.4, 2.1])
    border_core = np.array([3.5, 2.0])
    noise = np.array([6.8, 1.1])
    eps = 1.0

    fig, axes = plt.subplots(1, 3, figsize=(11.8, 4.0), facecolor="white")
    fig.subplots_adjust(left=0.04, right=0.99, bottom=0.16, top=0.86, wspace=0.18)

    for ax in axes:
        _style_axes(ax)
        ax.set_xlim(0.4, 7.5)
        ax.set_ylim(0.4, 3.4)
        ax.set_aspect("equal", adjustable="box")

    axes[0].set_title("Core point", fontsize=13, color=DARK)
    axes[0].scatter(neighbors[:, 0], neighbors[:, 1], s=70, color=BLUE, zorder=3)
    axes[0].scatter(core[0], core[1], s=145, color=ORANGE, edgecolor="white", linewidth=1.1, zorder=4)
    axes[0].add_patch(Circle(core, radius=eps, fill=True, facecolor=ORANGE, alpha=0.08, edgecolor=ORANGE, linewidth=1.8))
    axes[0].text(0.7, 3.0, r"$|N_\varepsilon(x_i)| \geq \mathrm{MinPts}$", fontsize=11, color=DARK)

    axes[1].set_title("Border point", fontsize=13, color=DARK)
    axes[1].scatter([border_core[0]], [border_core[1]], s=145, color=BLUE, edgecolor="white", linewidth=1.1, zorder=4)
    axes[1].scatter([border[0]], [border[1]], s=110, color=ORANGE, edgecolor="white", linewidth=1.1, zorder=4)
    axes[1].add_patch(Circle(border_core, radius=eps, fill=True, facecolor=BLUE, alpha=0.08, edgecolor=BLUE, linewidth=1.8))
    axes[1].text(3.0, 3.0, r"not core, but near a core point", fontsize=11, color=DARK)

    axes[2].set_title("Noise point", fontsize=13, color=DARK)
    axes[2].scatter([noise[0]], [noise[1]], s=110, color=RED, edgecolor="white", linewidth=1.1, zorder=4)
    axes[2].text(5.0, 3.0, r"neither core nor border", fontsize=11, color=DARK)

    _save(fig, "dbscan_point_types")


def build_direct_reachability() -> None:
    core = np.array([2.0, 2.0])
    border = np.array([3.0, 2.2])
    other = np.array([[1.3, 1.3], [1.2, 2.5], [2.4, 1.3], [2.3, 2.7]])
    eps = 1.2

    fig, ax = plt.subplots(figsize=(6.8, 4.2), facecolor="white")
    _style_axes(ax)
    ax.set_title("Direct density reachability", fontsize=13, color=DARK)
    ax.set_xlim(0.5, 4.1)
    ax.set_ylim(0.7, 3.4)
    ax.set_aspect("equal", adjustable="box")

    ax.scatter(other[:, 0], other[:, 1], s=70, color=BLUE, zorder=3)
    ax.scatter(core[0], core[1], s=150, color=ORANGE, edgecolor="white", linewidth=1.2, zorder=4)
    ax.scatter(border[0], border[1], s=110, color=GREEN, edgecolor="white", linewidth=1.1, zorder=4)
    ax.add_patch(Circle(core, radius=eps, fill=True, facecolor=ORANGE, alpha=0.08, edgecolor=ORANGE, linewidth=1.8))
    ax.add_patch(FancyArrowPatch(core, border, arrowstyle="->", mutation_scale=14, linewidth=2.0, color=PURPLE))

    ax.text(core[0] - 0.22, core[1] - 0.38, r"core $x_i$", fontsize=11, color=ORANGE)
    ax.text(border[0] + 0.05, border[1] + 0.10, r"$x_j$", fontsize=11, color=GREEN)
    ax.text(0.75, 3.0, r"$x_j \in N_\varepsilon(x_i)$ and $x_i$ is core", fontsize=11, color=DARK)

    _save(fig, "dbscan_direct_reachability")


def build_density_connectivity() -> None:
    chain = np.array([[0.9, 1.0], [1.7, 1.6], [2.6, 1.3], [3.5, 1.9], [4.3, 1.4]])
    hub = chain[1]
    eps = 1.15

    fig, ax = plt.subplots(figsize=(7.0, 4.2), facecolor="white")
    _style_axes(ax)
    ax.set_title("Density reachability and density connectivity", fontsize=13, color=DARK)
    ax.set_xlim(0.3, 4.9)
    ax.set_ylim(0.5, 2.8)
    ax.set_aspect("equal", adjustable="box")

    ax.scatter(chain[:, 0], chain[:, 1], s=90, color=BLUE, zorder=3)
    for idx, point in enumerate(chain, start=1):
        ax.text(point[0] + 0.05, point[1] + 0.09, rf"$x_{{{idx}}}$", fontsize=10, color=DARK)
    for left, right in zip(chain[:-1], chain[1:]):
        ax.add_patch(FancyArrowPatch(left, right, arrowstyle="->", mutation_scale=12, linewidth=1.8, color=PURPLE))

    ax.add_patch(Circle(hub, radius=eps, fill=True, facecolor=ORANGE, alpha=0.08, edgecolor=ORANGE, linewidth=1.8))
    ax.scatter(hub[0], hub[1], s=150, color=ORANGE, edgecolor="white", linewidth=1.2, zorder=4)
    ax.text(0.5, 2.45, r"chain: density-reachable", fontsize=11, color=PURPLE)
    ax.text(2.65, 2.45, r"same core support: density-connected", fontsize=11, color=DARK)

    _save(fig, "dbscan_density_connectivity")


def build_cluster_growth() -> None:
    cluster = np.array(
        [
            [1.0, 1.0],
            [1.5, 1.7],
            [2.1, 1.1],
            [2.5, 1.9],
            [3.1, 1.3],
            [3.4, 2.0],
        ]
    )
    noise = np.array([[5.7, 0.9], [6.3, 2.4]])
    eps = 0.95

    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.0), facecolor="white")
    fig.subplots_adjust(left=0.04, right=0.99, bottom=0.16, top=0.86, wspace=0.18)
    titles = ["Step 1: start from one core point", "Step 2: expand from new core points", "Step 3: maximal dense cluster"]

    for ax, title in zip(axes, titles):
        _style_axes(ax)
        ax.set_title(title, fontsize=12, color=DARK)
        ax.set_xlim(0.4, 6.8)
        ax.set_ylim(0.4, 3.1)
        ax.set_aspect("equal", adjustable="box")
        ax.scatter(noise[:, 0], noise[:, 1], s=70, color=GRAY, zorder=2)

    start = cluster[1]
    expand = cluster[3]

    axes[0].scatter(cluster[:, 0], cluster[:, 1], s=70, color=LIGHT, zorder=2)
    axes[0].scatter(start[0], start[1], s=145, color=ORANGE, edgecolor="white", linewidth=1.1, zorder=4)
    axes[0].add_patch(Circle(start, radius=eps, fill=True, facecolor=ORANGE, alpha=0.08, edgecolor=ORANGE, linewidth=1.8))

    axes[1].scatter(cluster[:4, 0], cluster[:4, 1], s=80, color=BLUE, zorder=3)
    axes[1].scatter(start[0], start[1], s=145, color=ORANGE, edgecolor="white", linewidth=1.1, zorder=4)
    axes[1].scatter(expand[0], expand[1], s=145, color=GREEN, edgecolor="white", linewidth=1.1, zorder=4)
    axes[1].add_patch(Circle(expand, radius=eps, fill=True, facecolor=GREEN, alpha=0.08, edgecolor=GREEN, linewidth=1.8))

    axes[2].scatter(cluster[:, 0], cluster[:, 1], s=80, color=BLUE, zorder=3)
    axes[2].scatter(noise[:, 0], noise[:, 1], s=80, color=RED, zorder=3)
    axes[2].text(4.75, 2.65, r"noise", fontsize=11, color=RED)

    _save(fig, "dbscan_cluster_growth")


def main() -> None:
    _configure_mpl()
    build_formal_setup()
    build_eps_neighborhood()
    build_point_types()
    build_direct_reachability()
    build_density_connectivity()
    build_cluster_growth()


if __name__ == "__main__":
    main()
