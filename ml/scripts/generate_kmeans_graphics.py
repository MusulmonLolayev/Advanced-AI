#!/usr/bin/env python3
"""Generate k-means teaching graphics with matplotlib."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle


BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "kmeans"

BLUE = "#2b6cb0"
ORANGE = "#dd6b20"
DARK = "#1f2937"
GRAY = "#6b7280"
LIGHT = "#e5e7eb"
GREEN = "#2f855a"


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


def _assign(data: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    d2 = np.sum((data[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
    return np.argmin(d2, axis=1)


def _update(data: np.ndarray, labels: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    updated = centroids.copy()
    for r in range(centroids.shape[0]):
        cluster = data[labels == r]
        if cluster.shape[0] > 0:
            updated[r] = cluster.mean(axis=0)
    return updated


def _run_kmeans(data: np.ndarray, init: np.ndarray, max_iter: int = 40) -> tuple[np.ndarray, np.ndarray, float]:
    centroids = init.astype(float).copy()
    labels = _assign(data, centroids)
    for _ in range(max_iter):
        new_centroids = _update(data, labels, centroids)
        new_labels = _assign(data, new_centroids)
        if np.array_equal(new_labels, labels) and np.allclose(new_centroids, centroids):
            centroids = new_centroids
            labels = new_labels
            break
        centroids = new_centroids
        labels = new_labels
    obj = float(np.sum((data - centroids[labels]) ** 2))
    return labels, centroids, obj


def _style_axes(ax: plt.Axes, xlabel: str = r"$x_1$", ylabel: str = r"$x_2$") -> None:
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, color=LIGHT, linewidth=0.8)
    ax.set_facecolor("white")


def build_iteration_panels() -> None:
    data = np.array([[1.0, 1.0], [1.0, 2.0], [5.0, 4.0], [6.0, 5.0]])
    init = np.array([[1.0, 1.0], [6.0, 5.0]])
    labels = _assign(data, init)
    updated = _update(data, labels, init)
    point_names = [r"$x_1$", r"$x_2$", r"$x_3$", r"$x_4$"]
    cluster_colors = [BLUE, ORANGE]

    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.0), facecolor="white")
    fig.subplots_adjust(left=0.05, right=0.98, bottom=0.15, top=0.86, wspace=0.18)
    titles = ["Step 1: initialize", "Step 2: assign", "Step 3: update"]

    for ax, title in zip(axes, titles):
        ax.set_xlim(0.2, 6.8)
        ax.set_ylim(0.4, 5.6)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(title, fontsize=13, color=DARK)
        _style_axes(ax)

    # Step 1
    axes[0].scatter(data[:, 0], data[:, 1], s=70, color=GRAY, zorder=3)
    for name, point in zip(point_names, data):
        axes[0].text(point[0] + 0.08, point[1] + 0.10, name, fontsize=11, color=DARK)
    for idx, mu in enumerate(init):
        axes[0].scatter(mu[0], mu[1], s=260, marker="X", color=cluster_colors[idx], edgecolor="white", linewidth=1.2, zorder=4)
        axes[0].text(mu[0] + 0.10, mu[1] - 0.22, rf"$\mu_{idx+1}$", fontsize=12, color=cluster_colors[idx])

    # Step 2
    for idx, point in enumerate(data):
        color = cluster_colors[labels[idx]]
        axes[1].scatter(point[0], point[1], s=80, color=color, zorder=3)
        axes[1].text(point[0] + 0.08, point[1] + 0.10, point_names[idx], fontsize=11, color=DARK)
        mu = init[labels[idx]]
        axes[1].plot([point[0], mu[0]], [point[1], mu[1]], linestyle=(0, (4, 4)), color=color, linewidth=1.4, zorder=2)
    for idx, mu in enumerate(init):
        axes[1].scatter(mu[0], mu[1], s=260, marker="X", color=cluster_colors[idx], edgecolor="white", linewidth=1.2, zorder=4)
        circle = Circle(mu, radius=1.15 if idx == 0 else 1.55, fill=False, linestyle=(0, (6, 5)), linewidth=1.3, edgecolor=cluster_colors[idx], alpha=0.55)
        axes[1].add_patch(circle)

    # Step 3
    for r in range(2):
        cluster = data[labels == r]
        axes[2].scatter(cluster[:, 0], cluster[:, 1], s=80, color=cluster_colors[r], zorder=3)
        axes[2].scatter(init[r, 0], init[r, 1], s=160, marker="X", color=LIGHT, edgecolor=GRAY, linewidth=1.0, zorder=3)
        axes[2].scatter(updated[r, 0], updated[r, 1], s=270, marker="X", color=cluster_colors[r], edgecolor="white", linewidth=1.3, zorder=4)
        axes[2].annotate(
            "",
            xy=updated[r],
            xytext=init[r],
            arrowprops=dict(arrowstyle="->", color=cluster_colors[r], lw=1.8),
        )
        axes[2].text(updated[r, 0] + 0.10, updated[r, 1] - 0.22, rf"$\mu_{r+1}'$", fontsize=12, color=cluster_colors[r])
    for name, point in zip(point_names, data):
        axes[2].text(point[0] + 0.08, point[1] + 0.10, name, fontsize=11, color=DARK)

    _save(fig, "kmeans_iteration_panels")


def build_initialization_sensitivity() -> None:
    rng = np.random.default_rng(10)
    c1 = rng.normal(loc=(-2.4, 0.0), scale=(0.45, 0.55), size=(35, 2))
    c2 = rng.normal(loc=(0.3, 2.4), scale=(0.48, 0.45), size=(35, 2))
    c3 = rng.normal(loc=(2.8, -1.3), scale=(0.45, 0.45), size=(35, 2))
    data = np.vstack([c1, c2, c3])

    init_good = np.array([[-2.5, -0.2], [0.1, 2.2], [2.7, -1.5]])
    init_bad = np.array([[-2.8, 0.4], [-1.5, -0.6], [2.5, -1.0]])
    good_labels, good_centroids, good_obj = _run_kmeans(data, init_good)
    bad_labels, bad_centroids, bad_obj = _run_kmeans(data, init_bad)
    colors = [BLUE, GREEN, ORANGE]

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.4), facecolor="white")
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.15, top=0.86, wspace=0.18)
    panels = [
        (axes[0], good_labels, good_centroids, f"Better initialization ($J={good_obj:.1f}$)"),
        (axes[1], bad_labels, bad_centroids, f"Poor initialization ($J={bad_obj:.1f}$)"),
    ]

    for ax, labels, centroids, title in panels:
        ax.set_title(title, fontsize=13, color=DARK)
        _style_axes(ax)
        ax.set_xlim(-4.0, 4.1)
        ax.set_ylim(-3.1, 4.0)
        ax.set_aspect("equal", adjustable="box")
        for r in range(3):
            pts = data[labels == r]
            ax.scatter(pts[:, 0], pts[:, 1], s=28, color=colors[r], alpha=0.85, zorder=3)
            ax.scatter(centroids[r, 0], centroids[r, 1], s=280, marker="X", color=colors[r], edgecolor="white", linewidth=1.4, zorder=4)

    _save(fig, "kmeans_initialization_sensitivity")


def build_scaling_compare() -> None:
    data = np.array(
        [
            [0.8, 120.0],
            [1.0, 280.0],
            [1.2, 500.0],
            [3.8, 140.0],
            [4.0, 300.0],
            [4.2, 520.0],
        ]
    )
    raw_init = np.array([[1.0, 130.0], [4.0, 510.0]])
    raw_labels, raw_centroids, _ = _run_kmeans(data, raw_init)

    mu = data.mean(axis=0)
    sd = data.std(axis=0)
    scaled = (data - mu) / sd
    scaled_init = np.array([scaled[0], scaled[-1]])
    scaled_labels, scaled_centroids, _ = _run_kmeans(scaled, scaled_init)
    colors = [BLUE, ORANGE]

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.3), facecolor="white")
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.86, wspace=0.22)
    panels = [
        (axes[0], data, raw_labels, raw_centroids, "Raw features", r"$x_1$", r"$x_2$"),
        (axes[1], scaled, scaled_labels, scaled_centroids, "After standardization", r"$x_1$ (z-score)", r"$x_2$ (z-score)"),
    ]

    for ax, pts, labels, centroids, title, xlabel, ylabel in panels:
        ax.set_title(title, fontsize=13, color=DARK)
        _style_axes(ax, xlabel=xlabel, ylabel=ylabel)
        for r in range(2):
            cluster = pts[labels == r]
            ax.scatter(cluster[:, 0], cluster[:, 1], s=90, color=colors[r], zorder=3)
            ax.scatter(centroids[r, 0], centroids[r, 1], s=260, marker="X", color=colors[r], edgecolor="white", linewidth=1.3, zorder=4)

    _save(fig, "kmeans_scaling_compare")


def build_elbow_curve() -> None:
    rng = np.random.default_rng(5)
    c1 = rng.normal(loc=(-2.2, -0.6), scale=(0.45, 0.5), size=(45, 2))
    c2 = rng.normal(loc=(0.4, 2.4), scale=(0.42, 0.46), size=(45, 2))
    c3 = rng.normal(loc=(2.6, -1.4), scale=(0.5, 0.44), size=(45, 2))
    data = np.vstack([c1, c2, c3])

    ks = np.arange(1, 7)
    objectives = []
    for k in ks:
        best = float("inf")
        for seed in range(10):
            rng_local = np.random.default_rng(100 + 13 * k + seed)
            init_idx = rng_local.choice(data.shape[0], size=k, replace=False)
            _, _, obj = _run_kmeans(data, data[init_idx], max_iter=50)
            best = min(best, obj)
        objectives.append(best)

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2), facecolor="white")
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.16, top=0.86, wspace=0.22)

    axes[0].set_title("Toy dataset", fontsize=13, color=DARK)
    _style_axes(axes[0])
    axes[0].scatter(c1[:, 0], c1[:, 1], s=26, color=BLUE, alpha=0.85)
    axes[0].scatter(c2[:, 0], c2[:, 1], s=26, color=GREEN, alpha=0.85)
    axes[0].scatter(c3[:, 0], c3[:, 1], s=26, color=ORANGE, alpha=0.85)
    axes[0].set_aspect("equal", adjustable="box")

    axes[1].set_title("Objective versus $k$", fontsize=13, color=DARK)
    _style_axes(axes[1], xlabel=r"Number of clusters $k$", ylabel=r"Within-cluster sum of squares")
    axes[1].plot(ks, objectives, marker="o", color=BLUE, linewidth=2.2, markersize=7)
    axes[1].set_xticks(ks)
    axes[1].annotate(
        "bend near $k=3$",
        xy=(3, objectives[2]),
        xytext=(3.45, objectives[1] + 55.0),
        fontsize=11,
        color=DARK,
        arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.1),
    )

    _save(fig, "kmeans_elbow_curve")


def main() -> None:
    _configure_mpl()
    build_iteration_panels()
    build_initialization_sensitivity()
    build_scaling_compare()
    build_elbow_curve()
    print(f"Saved k-means graphics to {OUT_DIR}")


if __name__ == "__main__":
    main()
