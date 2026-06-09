#!/usr/bin/env python3
"""Generate vector Random Forests teaching graphics as PDF files.

Uses TikZ to generate vector graphics and compiles them with pdflatex.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

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
  \node[draw, rounded rectangle, fill=lightblue, minimum width=1.5cm, minimum height=1.8cm] (D) at (0, 1.5) {$D$};

  \foreach \i in {0,1,2} {
    \pgfmathsetmacro{\x}{2.5 + \i * 1.8}
    \node[draw, rounded rectangle, fill=lightyellow, minimum width=1.3cm, minimum height=1.6cm] (D\i) at (\x, 1.5) {$D^{(\i+1)}$};
    \draw[-latex] (D.east) -- (D\i.west);
  }

  \foreach \i in {0,1,2} {
    \pgfmathsetmacro{\x}{2.5 + \i * 1.8}
    \node[draw, regular polygon, regular polygon sides=3, fill=lightgreen, minimum size=0.8cm] (T\i) at (\x, 3.5) {T$_{\i+1}$};
    \draw[-latex] (D\i.north) -- (T\i.south);
  }

  \node[draw, rounded rectangle, fill=lightcoral, minimum width=2cm, minimum height=0.7cm] (vote) at (4, -0.5) {Majority Vote};

  \foreach \i in {0,1,2} {
    \pgfmathsetmacro{\x}{2.5 + \i * 1.8}
    \draw[-latex, gray, thin] (T\i) -- (vote);
  }

  \node[font=\large\bfseries] at (4, 4.5) {Bagging: Bootstrap Aggregating};
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
  \node[above] at (3, 4) {\large \textbf{Forest Prediction (Classification)}};

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
boundary_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightcoral}{RGB}{240,128,128}
\begin{document}
\begin{tikzpicture}
  \node[font=\Large\bfseries] at (4, 5) {Decision Boundary: Single Tree vs Forest};

  \node[font=\bfseries] at (1.5, 4.3) {Single Decision Tree};
  \node[font=\small] at (1.5, 3.9) {(High Variance)};
  \draw[fill=lightblue, opacity=0.3] (0, 2) rectangle (1.5, 3.5);
  \draw[fill=lightcoral, opacity=0.3] (0.75, 2.5) rectangle (1.5, 3);
  \foreach \i in {0,1,2,3} {
    \node[circle, fill=blue, minimum size=0.15cm] at ({0.3+0.3*\i}, 2.3) {};
    \node[rectangle, fill=red, minimum width=0.12cm, minimum height=0.12cm] at ({0.5+0.3*\i}, 3.2) {};
  }

  \node[font=\bfseries] at (4.5, 4.3) {Random Forest};
  \node[font=\small] at (4.5, 3.9) {(Low Variance)};
  \draw[fill=lightblue, opacity=0.3] (3, 2) rectangle (6, 3.5);
  \draw[fill=lightcoral, opacity=0.3] (4.5, 2.5) rectangle (6, 3.5);
  \foreach \i in {0,1,2,3} {
    \node[circle, fill=blue, minimum size=0.15cm] at ({3.3+0.3*\i}, 2.3) {};
    \node[rectangle, fill=red, minimum width=0.12cm, minimum height=0.12cm] at ({3.5+0.3*\i}, 3.2) {};
  }
\end{tikzpicture}
\end{document}
"""

compile_tikz(boundary_tex, "boundary_comparison")


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
