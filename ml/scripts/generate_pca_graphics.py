#!/usr/bin/env python3
"""Generate PCA teaching graphics with matplotlib.

The figures are authored once in Python and exported as both SVG and PDF so the
Beamer deck can include vector graphics directly.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch


BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "pca"


def _configure_mpl() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "mathtext.fontset": "dejavusans",
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "axes.linewidth": 0.0,
        }
    )


def _save(fig: plt.Figure, name: str) -> None:
    svg_path = OUT_DIR / f"{name}.svg"
    pdf_path = OUT_DIR / f"{name}.pdf"
    fig.savefig(svg_path, format="svg", bbox_inches="tight", pad_inches=0.08)
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def _new_canvas(width: float, height: float) -> tuple[plt.Figure, plt.Axes]:
    fig = plt.figure(figsize=(width, height), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 920)
    ax.set_ylim(560, 0)
    ax.axis("off")
    return fig, ax


def _arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = "#1f1f1f", lw: float = 2.0, ms: float = 16.0, linestyle: str = "-") -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=ms,
        linewidth=lw,
        color=color,
        linestyle=linestyle,
    )
    ax.add_patch(arrow)


def _line(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = "#1f1f1f", lw: float = 2.0, linestyle: str = "-") -> None:
    ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linewidth=lw, linestyle=linestyle)


def _text(ax: plt.Axes, x: float, y: float, text: str, size: float = 12.0, color: str = "#1f1f1f", ha: str = "left", va: str = "center", weight: str | int = "normal") -> None:
    ax.text(x, y, text, fontsize=size, color=color, ha=ha, va=va, fontweight=weight)


def _projection_point(cx: float, cy: float, angle_deg: float, sample_x: float, sample_y: float) -> tuple[float, float]:
    angle = math.radians(angle_deg)
    dx = sample_x - cx
    dy = sample_y - cy
    dot = dx * math.cos(angle) + dy * (-math.sin(angle))
    px = cx + dot * math.cos(angle)
    py = cy - dot * math.sin(angle)
    return px, py


def build_projection() -> None:
    fig, ax = _new_canvas(9.2, 5.6)

    _arrow(ax, (90, 500), (835, 500), color="#404040", lw=2.4, ms=16)
    _arrow(ax, (90, 500), (90, 70), color="#404040", lw=2.4, ms=16)
    _text(ax, 848, 506, r"$x_1$", size=13)
    _text(ax, 76, 60, r"$x_2$", size=13)

    cx, cy = 430, 280
    angle_deg = 35
    line_len = 285
    dx = math.cos(math.radians(angle_deg)) * line_len
    dy = math.sin(math.radians(angle_deg)) * line_len
    x1, y1 = cx - dx, cy + dy
    x2, y2 = cx + dx, cy - dy
    _line(ax, (x1, y1), (x2, y2), color="#2166ac", lw=4.0)
    _arrow(ax, (x1, y1), (x2, y2), color="#2166ac", lw=4.0, ms=18)
    _text(ax, 650, 185, r"direction $w$", size=13)

    pts = [(250, 390), (320, 355), (360, 330), (450, 290), (540, 245), (610, 210)]
    xs, ys = zip(*pts)
    ax.scatter(xs, ys, s=36, color="#1f4e79", zorder=3)

    sample_x, sample_y = 540, 245
    px, py = _projection_point(cx, cy, angle_deg, sample_x, sample_y)
    ax.scatter([sample_x], [sample_y], s=70, color="#1f4e79", zorder=4)
    ax.scatter([px], [py], s=60, color="#d95f02", zorder=4)
    _line(ax, (sample_x, sample_y), (px, py), color="#8c8c8c", lw=1.8, linestyle=(0, (7, 6)))
    ax.annotate(
        r"$z_i = w^\top x_i$",
        xy=(px, py),
        xytext=(578, 225),
        textcoords="data",
        fontsize=13,
        color="#1f1f1f",
        arrowprops=dict(arrowstyle="->", color="#7f7f7f", lw=1.0),
        ha="left",
        va="center",
    )
    _text(ax, 245, 100, "many points on a line", size=11)
    _text(ax, 550, 252, r"$x_i$", size=11, color="#1f4e79", ha="left", va="bottom")

    _save(fig, "pca_projection")


def build_axes() -> None:
    fig, ax = _new_canvas(9.2, 5.6)

    _arrow(ax, (110, 500), (830, 500), color="#404040", lw=2.2, ms=16)
    _arrow(ax, (110, 500), (110, 70), color="#404040", lw=2.2, ms=16)
    _text(ax, 846, 506, r"$x_1$", size=13)
    _text(ax, 96, 60, r"$x_2$", size=13)

    pts = [
        (390, 270), (430, 250), (470, 236), (510, 220), (550, 205),
        (370, 300), (410, 285), (455, 270), (500, 255), (545, 238),
        (390, 325), (435, 312), (480, 296), (525, 280),
    ]
    xs, ys = zip(*pts)
    ax.scatter(xs, ys, s=20, color="#2c7fb8", zorder=3)

    ellipse = Ellipse((470, 268), width=390, height=164, angle=-34, fill=False, edgecolor="#2c7fb8", linewidth=4.0)
    ax.add_patch(ellipse)
    _arrow(ax, (470, 268), (690, 155), color="#d95f02", lw=4.0, ms=18)
    _arrow(ax, (470, 268), (305, 395), color="#1b9e77", lw=4.0, ms=18)
    _line(ax, (470, 268), (470, 395), color="#7f7f7f", lw=1.8, linestyle=(0, (7, 6)))

    _text(ax, 695, 152, "PC1", size=13)
    _text(ax, 285, 404, "PC2", size=13)
    _text(ax, 488, 398, "orthogonal", size=11, ha="center")
    _text(ax, 196, 120, "spread follows the major axis", size=11)

    _save(fig, "pca_axes")


def _panel_base(ax: plt.Axes) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")


def build_svd_geometry() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.2), facecolor="white")
    fig.subplots_adjust(left=0.02, right=0.985, top=0.90, bottom=0.08, wspace=0.12)

    titles = [
        ("Step 1", "principal coordinates"),
        ("Step 2", "scale each axis"),
        ("Step 3", "output basis"),
    ]
    colors = ["#2166ac", "#d95f02", "#1b9e77"]

    for idx, ax in enumerate(axes):
        _panel_base(ax)
        title, subtitle = titles[idx]
        ax.text(0.5, 0.96, title, ha="center", va="top", fontsize=14, fontweight="bold", color="#1f1f1f", transform=ax.transAxes)
        ax.text(0.5, 0.06, subtitle, ha="center", va="bottom", fontsize=12, color="#1f1f1f", transform=ax.transAxes)

        # Soft background cue without framing boxes.
        ax.add_patch(Ellipse((0.5, 0.5), 0.82, 0.58, angle=0, fill=False, edgecolor="#e3e3e3", linewidth=1.0, transform=ax.transAxes))

        if idx == 0:
            ax.add_patch(Ellipse((0.5, 0.48), 0.38, 0.38, angle=0, fill=False, edgecolor=colors[idx], linewidth=3.5, transform=ax.transAxes))
            ax.plot([0.19, 0.81], [0.48, 0.48], color="#404040", linewidth=1.6, linestyle=(0, (7, 6)), transform=ax.transAxes)
            ax.plot([0.50, 0.50], [0.17, 0.79], color="#404040", linewidth=1.6, linestyle=(0, (7, 6)), transform=ax.transAxes)
            ax.text(0.50, 0.83, r"$V^\top$", ha="center", va="center", fontsize=15, color="#1f1f1f", transform=ax.transAxes)
        elif idx == 1:
            ax.add_patch(Ellipse((0.5, 0.48), 0.60, 0.30, angle=0, fill=False, edgecolor=colors[idx], linewidth=3.5, transform=ax.transAxes))
            ax.plot([0.17, 0.83], [0.48, 0.48], color="#404040", linewidth=1.6, linestyle=(0, (7, 6)), transform=ax.transAxes)
            ax.text(0.50, 0.83, r"$S$", ha="center", va="center", fontsize=15, color="#1f1f1f", transform=ax.transAxes)
            ax.text(0.50, 0.30, "stretch", ha="center", va="center", fontsize=12, color="#1f1f1f", transform=ax.transAxes)
        else:
            ax.add_patch(Ellipse((0.5, 0.48), 0.60, 0.30, angle=-28, fill=False, edgecolor=colors[idx], linewidth=3.5, transform=ax.transAxes))
            ax.plot([0.17, 0.83], [0.55, 0.41], color="#404040", linewidth=1.6, linestyle=(0, (7, 6)), transform=ax.transAxes)
            ax.text(0.50, 0.83, r"$U$", ha="center", va="center", fontsize=15, color="#1f1f1f", transform=ax.transAxes)

    _save(fig, "pca_svd_geometry")


def main() -> None:
    _configure_mpl()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_projection()
    build_axes()
    build_svd_geometry()
    print(f"Saved PCA graphics to {OUT_DIR}")


if __name__ == "__main__":
    main()
