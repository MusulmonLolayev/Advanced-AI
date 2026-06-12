#!/usr/bin/env python3
"""Generate vector Random Forests teaching graphics as PDF files.

Uses TikZ to generate vector graphics and compiles them with pdflatex.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "random_forests"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def compile_tikz(content: str, name: str) -> None:
    """Write TikZ content to a .tex file and compile to PDF."""
    tex_path = OUT_DIR / f"{name}.tex"
    pdf_path = OUT_DIR / f"{name}.pdf"

    tex_path.write_text(content)

    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(OUT_DIR), str(tex_path)],
        capture_output=True,
        text=True,
        cwd=str(OUT_DIR),
    )

    if result.returncode == 0:
        print(f"✓ {name}.pdf")
        # Clean up auxiliary files
        for ext in [".aux", ".log", ".tex"]:
            (OUT_DIR / f"{name}{ext}").unlink(missing_ok=True)
    else:
        print(f"✗ {name}.pdf - compilation failed")
        print(result.stdout[-500:] if result.stdout else "")


# ============================================================================
# Figure 1: Bagging diagram
# ============================================================================
bagging_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{shapes, arrows, positioning}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightyellow}{RGB}{255,255,200}
\definecolor{lightgreen}{RGB}{144,238,144}
\definecolor{lightcoral}{RGB}{240,128,128}
\begin{document}
\begin{tikzpicture}
  % Original dataset
  \node[draw, rounded rectangle, fill=lightblue, minimum width=1.6cm, minimum height=2cm] (D) at (0, 1) {$D$};

  % Bootstrap samples -- spread widely
  \foreach \i in {0,1,2} {
    \pgfmathsetmacro{\x}{3.2 + \i * 2.8}
    \node[draw, rounded rectangle, fill=lightyellow, minimum width=1.4cm, minimum height=1.8cm] (D\i) at (\x, 1) {$D^{(\i+1)}$};
  }
  % Arrows from D to each sample, fanned from right
  \draw[-latex] (D.15)  -- (D0.west);
  \draw[-latex] (D.east) -- (D1.west);
  \draw[-latex] (D.-15) -- (D2.west);

  % Trees above
  \foreach \i in {0,1,2} {
    \pgfmathsetmacro{\x}{3.2 + \i * 2.8}
    \node[draw, regular polygon, regular polygon sides=3, fill=lightgreen, minimum size=0.9cm] (T\i) at (\x, 3.2) {T$_{\i+1}$};
    \draw[-latex] (D\i.north) -- (T\i.south);
  }

  % Vote box centered well below
  \node[draw, rounded rectangle, fill=lightcoral, minimum width=2.4cm, minimum height=0.9cm] (vote) at (6, -0.8) {Majority Vote};

  % Arrows from trees to vote -- each takes a separate approach angle
  \draw[-latex] (T0.south) to[out=-90, in=120] (vote.north west);
  \draw[-latex] (T1.south) -- (vote.90);
  \draw[-latex] (T2.south) to[out=-90, in=60]  (vote.north east);

  \node[font=\large\bfseries] at (6, 5.2) {Bagging: Bootstrap Aggregating};
\end{tikzpicture}
\end{document}
"""

compile_tikz(bagging_tex, "bagging_diagram")


# ============================================================================
# Figure 2: Feature subsampling
# ============================================================================
feature_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{shapes, positioning}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightgreen}{RGB}{144,238,144}
\begin{document}
\begin{tikzpicture}[node distance=0.6cm]
  % Left: all features
  \node[anchor=west] at (0, 0) {\textbf{All $d$ features}};
  \foreach \i in {0,1,2,3,4} {
    \node[draw, fill=lightblue, minimum width=3cm, minimum height=0.5cm, anchor=west] at (0, {-0.8-\i*0.6}) {Feature \i+1};
  }

  % Right: subset
  \node[anchor=west] at (5, 0) {\textbf{Random $m$ features ($m = \lfloor\sqrt{d}\rfloor$)}};
  \foreach \i in {0,1,2,3,4} {
    \ifodd\i
      \node[draw, fill=lightgreen, minimum width=3cm, minimum height=0.5cm, anchor=west] at (5, {-0.8-\i*0.6}) {Feature \i+1};
    \else
      \node[draw, fill=gray!30, minimum width=3cm, minimum height=0.5cm, anchor=west, text opacity=0.3] at (5, {-0.8-\i*0.6}) {Feature \i+1};
    \fi
  }

  \node[above] at (2.5, 2) {\large \textbf{Feature Subsampling at Each Split}};
\end{tikzpicture}
\end{document}
"""

compile_tikz(feature_tex, "feature_subsampling")


# ============================================================================
# Figure 3: Forest vote
# ============================================================================
vote_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{shapes, arrows, positioning}
\definecolor{lightyellow}{RGB}{255,255,200}
\definecolor{lightgreen}{RGB}{144,238,144}
\definecolor{lightcoral}{RGB}{240,128,128}
\definecolor{darkgreen}{RGB}{0,100,0}
\begin{document}
\begin{tikzpicture}[node distance=0.8cm]
  \node[above] at (3, 5.2) {\large \textbf{Forest Prediction (Classification)}};

  % Five trees with predictions
  \foreach \i in {0,1,2,3,4} {
    \pgfmathsetmacro{\x}{\i * 1.5}
    \ifodd\i
      \node[draw, regular polygon, regular polygon sides=3, fill=lightyellow, minimum size=0.7cm] at (\x, 3) {};
      \node[draw, fill=lightcoral, circle, minimum size=0.6cm] at (\x, 1.5) {\small B};
    \else
      \node[draw, regular polygon, regular polygon sides=3, fill=lightyellow, minimum size=0.7cm] at (\x, 3) {};
      \node[draw, fill=lightgreen, circle, minimum size=0.6cm] at (\x, 1.5) {\small A};
    \fi
    \draw[-latex] (\x, 2.8) -- (\x, 2.1);
  }

  % Vote result
  \node[draw, fill=darkgreen!30, rounded rectangle, minimum width=3cm, minimum height=0.8cm] at (3, 0) {\textbf{Majority Vote: A (3 vs 2)}};
  \foreach \i in {0,1,2,3,4} {
    \pgfmathsetmacro{\x}{\i * 1.5}
    \draw[-latex, gray, thin] (\x, 1.2) -- (3, 0.8);
  }
\end{tikzpicture}
\end{document}
"""

compile_tikz(vote_tex, "forest_vote")


# ============================================================================
# Figure 4: OOB illustration
# ============================================================================
oob_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightyellow}{RGB}{255,255,200}
\definecolor{lightcoral}{RGB}{240,128,128}
\begin{document}
\begin{tikzpicture}
  \node[font=\bfseries] at (3, 4) {\large Out-of-Bag Error: 2/10 samples (20\%)};

  \node[anchor=west, font=\bfseries] at (0, 3.3) {Original $D$:};
  \foreach \i in {0,1,2,3,4,5,6,7,8,9} {
    \node[draw, fill=lightblue, minimum width=0.4cm, minimum height=0.3cm, font=\tiny] at ({0.5*\i}, 2.9) {\i};
  }

  \node[anchor=west, font=\bfseries] at (0, 2.2) {Bootstrap $D^{(b)}$:};
  \foreach \i in {0,1,3,3,5,6,7,8,8,9} {
    \node[draw, fill=lightyellow, minimum width=0.4cm, minimum height=0.3cm, font=\tiny] at ({0.5*\i}, 1.8) {\i};
  }

  \node[anchor=west, font=\bfseries] at (0, 1.1) {Out-of-bag:};
  \foreach \i/\x in {2/1, 4/2.5} {
    \node[draw, fill=lightcoral, line width=1.5pt, minimum width=0.5cm, minimum height=0.3cm, font=\tiny\bfseries] at (\x, 0.7) {\i};
  }
\end{tikzpicture}
\end{document}
"""

compile_tikz(oob_tex, "oob_illustration")


# ============================================================================
# Figure 5: Decision boundary comparison
# ============================================================================
# ============================================================================
# Figure 5: Decision boundary comparison (matplotlib)
# ============================================================================
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def build_boundary_figure() -> None:
    """Plot side-by-side decision boundary: stepped (tree) vs smooth (forest)."""
    rng = np.random.default_rng(42)
    n = 60

    # True diagonal boundary: y = 0.9 + 0.5 * x  (midway between the two classes)
    true_x = np.linspace(0.5, 4.5, 200)
    true_y = 0.9 + 0.5 * true_x

    # Class 0: centered slightly below the true boundary (margin = 0.4)
    # y ≈ 0.5 + 0.5*x, half-width = 0.4 below the boundary
    c0_x = rng.uniform(0.5, 4.5, n)
    c0_y = 0.5 + 0.5 * c0_x + rng.normal(0.0, 0.22, n)
    c0 = np.column_stack([c0_x, c0_y])

    # Class 1: centered slightly above the true boundary
    # y ≈ 1.3 + 0.5*x, half-width = 0.4 above the boundary
    c1_x = rng.uniform(0.5, 4.5, n)
    c1_y = 1.3 + 0.5 * c1_x + rng.normal(0.0, 0.22, n)
    c1 = np.column_stack([c1_x, c1_y])

    # ------ Stepped boundary (decision tree, axis-aligned) ------
    # The step function approximates the diagonal with where="post":
    #   horizontal from (x_k, y_k) to (x_{k+1}, y_k), then vertical to (x_{k+1}, y_{k+1})
    # 5 splits at x = [0.5, 1.3, 2.1, 2.9, 3.7, 4.5]
    # Step y-values follow the true diagonal: y = 0.9 + 0.5*x at the midpoints
    step_x = [0.5, 1.3, 2.1, 2.9, 3.7, 4.5]
    step_y = [1.15, 1.55, 1.95, 2.35, 2.75, 3.15]

    # Expanded path from step(step_x, step_y, where="post"):
    # (0.5,1.15) → (1.3,1.15) → (1.3,1.55) → (2.1,1.55) → (2.1,1.95) →
    # (2.9,1.95) → (2.9,2.35) → (3.7,2.35) → (3.7,2.75) → (4.5,2.75) → (4.5,3.15)

    # Fill polygon below the stepped boundary
    poly_x = [0.5, 0.5, 1.3, 1.3, 2.1, 2.1, 2.9, 2.9, 3.7, 3.7, 4.5, 4.5, 4.5, 0.5]
    poly_y = [0.5, 1.15, 1.15, 1.55, 1.55, 1.95, 1.95, 2.35, 2.35, 2.75, 2.75, 3.15, 0.5, 0.5]

    # Fill polygon above the stepped boundary (blue region)
    poly_x_above = [0.5, 0.5, 1.3, 1.3, 2.1, 2.1, 2.9, 2.9, 3.7, 3.7, 4.5, 4.5, 4.5, 0.5]
    poly_y_above = [4.5, 1.15, 1.15, 1.55, 1.55, 1.95, 1.95, 2.35, 2.35, 2.75, 2.75, 3.15, 4.5, 4.5]

    # ------ Smooth boundary (random forest) ------
    forest_y = 0.905 + 0.5 * true_x  # virtually identical to the true diagonal

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    # ===== LEFT: Single Decision Tree =====
    # Fill above the stepped boundary (blue, class 1 region)
    ax1.fill(poly_x_above, poly_y_above, color="lightblue", alpha=0.3, linewidth=0)
    # Fill below the stepped boundary (red, class 0 region)
    ax1.fill(poly_x, poly_y, color="lightcoral", alpha=0.3, linewidth=0)
    # Stepped boundary line
    ax1.step(step_x, step_y, color="black", linewidth=2.5, where="post")
    # True boundary as dashed reference
    ax1.plot(true_x, true_y, color="gray", linewidth=1.2, linestyle="--", alpha=0.7, label="True boundary")
    # Data points
    ax1.scatter(c0[:, 0], c0[:, 1], c="#2255aa", marker="o", s=22,
                edgecolors="white", linewidth=0.3, zorder=5, label="Class 0 (below)")
    ax1.scatter(c1[:, 0], c1[:, 1], c="#cc3333", marker="s", s=22,
                edgecolors="white", linewidth=0.3, zorder=5, label="Class 1 (above)")
    ax1.set_xlim(0.5, 4.5)
    ax1.set_ylim(0.5, 4.5)
    ax1.set_xlabel("$x_1$")
    ax1.set_ylabel("$x_2$")
    ax1.set_title("Single Decision Tree", fontweight="bold")
    ax1.legend(loc="lower right", fontsize=7)

    # ===== RIGHT: Random Forest =====
    # Fill above the smooth boundary (blue)
    ax2.fill_between(true_x, forest_y, 4.5, color="lightblue", alpha=0.3)
    # Fill below the smooth boundary (red)
    ax2.fill_between(true_x, forest_y, 0.5, color="lightcoral", alpha=0.3)
    # Smooth boundary line
    ax2.plot(true_x, forest_y, color="black", linewidth=2.5)
    # True boundary as dashed reference
    ax2.plot(true_x, true_y, color="gray", linewidth=1.2, linestyle="--", alpha=0.7, label="True boundary")
    # Data points
    ax2.scatter(c0[:, 0], c0[:, 1], c="#2255aa", marker="o", s=22,
                edgecolors="white", linewidth=0.3, zorder=5, label="Class 0 (below)")
    ax2.scatter(c1[:, 0], c1[:, 1], c="#cc3333", marker="s", s=22,
                edgecolors="white", linewidth=0.3, zorder=5, label="Class 1 (above)")
    ax2.set_xlim(0.5, 4.5)
    ax2.set_ylim(0.5, 4.5)
    ax2.set_xlabel("$x_1$")
    ax2.set_ylabel("$x_2$")
    ax2.set_title("Random Forest", fontweight="bold")
    ax2.legend(loc="lower right", fontsize=7)

    fig.suptitle("Decision Boundary: Single Tree vs Random Forest", fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "boundary_comparison.pdf", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("Saved: boundary_comparison.pdf")


build_boundary_figure()


# ============================================================================
# Figure 6: Error vs number of trees
# ============================================================================
import math

error_data_str = ""
for b in range(1, 201, 10):
    oob_err = 0.35 * math.exp(-0.015 * b) + 0.08
    test_err = 0.40 * math.exp(-0.012 * b) + 0.10
    error_data_str += f"OOB: {b} {oob_err:.4f}\n"

error_data_str_test = ""
for b in range(1, 201, 10):
    test_err = 0.40 * math.exp(-0.012 * b) + 0.10
    error_data_str_test += f"TEST: {b} {test_err:.4f}\n"

pgfplots_content = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\definecolor{darkgreen}{RGB}{0,100,0}
\definecolor{darkred}{RGB}{139,0,0}
\begin{document}
\begin{tikzpicture}
  \begin{axis}[
    width=10cm,
    height=6cm,
    xlabel={Number of Trees (B)},
    ylabel={Error},
    legend pos=north east,
    grid,
    grid style=gray!20,
  ]
    \addplot[mark=o, mark size=3, line width=2, color=darkgreen] coordinates {
"""

for b in range(1, 201, 10):
    oob_err = 0.35 * math.exp(-0.015 * b) + 0.08
    pgfplots_content += f"({b}, {oob_err:.4f}) "

pgfplots_content += r"""
    };
    \addlegendentry{OOB Error}

    \addplot[mark=square, mark size=3, line width=2, color=darkred] coordinates {
"""

for b in range(1, 201, 10):
    test_err = 0.40 * math.exp(-0.012 * b) + 0.10
    pgfplots_content += f"({b}, {test_err:.4f}) "

pgfplots_content += r"""
    };
    \addlegendentry{Test Error}
  \end{axis}
\end{tikzpicture}
\end{document}
"""

compile_tikz(pgfplots_content, "error_vs_trees")

print("\n✓ All Random Forest figures generated successfully!")
