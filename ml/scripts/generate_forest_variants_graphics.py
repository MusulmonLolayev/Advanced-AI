#!/usr/bin/env python3
"""Generate vector Forest Variants teaching graphics as PDF files.

Uses TikZ to generate vector graphics and compiles them with pdflatex.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "forest_variants"
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
        for ext in [".aux", ".log", ".tex"]:
            (OUT_DIR / f"{name}{ext}").unlink(missing_ok=True)
    else:
        print(f"✗ {name}.pdf - compilation failed")
        print(result.stdout[-1500:] if result.stdout else "")
    pdf_path  # noqa: B018 (referenced for clarity only)


# ============================================================================
# Figure 1: Isolation by random partitioning (anomaly vs normal point)
# ============================================================================
isolation_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightcoral}{RGB}{240,128,128}
\definecolor{darkgreen}{RGB}{0,100,0}
\begin{document}
\begin{tabular}{cc}
\textbf{Anomaly: isolated in 2 cuts} & \textbf{Normal point: isolated in 5 cuts} \\[3pt]
\begin{tikzpicture}
    \draw[draw=black] (0,0) rectangle (5,4);
    \foreach \x/\y in {0.6/1.1, 1.4/0.6, 2.1/1.6, 0.9/2.4, 1.8/0.9, 2.6/2.0, 1.1/1.7, 0.4/0.8, 2.0/0.5, 1.5/1.3} {
      \fill[darkgreen] (\x,\y) circle (2.2pt);
    }
    \fill[lightcoral] (4.4,3.5) circle (3.2pt);
    \draw[thick, red] (3.5,0) -- (3.5,4);
    \draw[thick, red] (3.5,3.0) -- (5,3.0);
    \node[font=\tiny, red] at (4.7,2.8) {cut 2};
    \node[font=\tiny, red] at (3.65,3.85) {cut 1};
\end{tikzpicture}
&
\begin{tikzpicture}
    \draw[draw=black] (0,0) rectangle (5,4);
    \foreach \x/\y in {0.6/1.1, 1.4/0.6, 2.1/1.6, 0.9/2.4, 1.8/0.9, 2.6/2.0, 1.1/1.7, 0.4/0.8, 2.0/0.5, 1.5/1.3} {
      \fill[darkgreen] (\x,\y) circle (2.2pt);
    }
    \fill[lightblue] (1.5,1.3) circle (3.2pt);
    \draw[thick, red] (0,3.0) -- (5,3.0);
    \draw[thick, red] (3.0,0) -- (3.0,3.0);
    \draw[thick, red] (0,1.0) -- (3.0,1.0);
    \draw[thick, red] (1.0,1.0) -- (1.0,3.0);
    \draw[thick, red] (1.0,1.6) -- (3.0,1.6);
\end{tikzpicture}
\end{tabular}
\end{document}
"""

compile_tikz(isolation_tex, "isolation_partition")


# ============================================================================
# Figure 2: Path length comparison (short path vs long path tree)
# ============================================================================
path_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{positioning}
\definecolor{lightcoral}{RGB}{240,128,128}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightyellow}{RGB}{255,255,200}
\begin{document}
\begin{tabular}{cc}
\textbf{Anomaly: short path ($h=2$)} & \textbf{Normal point: long path ($h=5$)} \\[3pt]
\begin{tikzpicture}[
  grow=right,
  level distance=1.15cm,
  level 1/.style={sibling distance=1.1cm},
  level 2/.style={sibling distance=0.8cm},
  every node/.style={draw, circle, fill=lightyellow, minimum size=0.5cm, font=\tiny}
]
  \node {r}
    child { node {} }
    child { node {}
      child { node[fill=lightcoral] {A} }
      child { node {} }
    };
\end{tikzpicture}
&
\begin{tikzpicture}[
  grow=right,
  level distance=1.15cm,
  level 1/.style={sibling distance=1.1cm},
  level 2/.style={sibling distance=0.8cm},
  level 3/.style={sibling distance=0.6cm},
  level 4/.style={sibling distance=0.5cm},
  every node/.style={draw, circle, fill=lightyellow, minimum size=0.5cm, font=\tiny}
]
  \node {r}
    child { node {} }
    child { node {}
      child { node {}
        child { node {}
          child { node[fill=lightblue] {B} }
          child { node {} }
        }
        child { node {} }
      }
      child { node {} }
    };
\end{tikzpicture}
\end{tabular}
\end{document}
"""

compile_tikz(path_tex, "path_length_tree")


# ============================================================================
# Figure 3: Anomaly score curve s(x,n) = 2^{-E[h(x)]/c(n)}
# ============================================================================
ratio_max = 2.2
curve_points = ""
steps = 60
for i in range(steps + 1):
    r = ratio_max * i / steps
    s = 2 ** (-r)
    curve_points += f"({r:.4f}, {s:.4f}) "

score_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\definecolor{darkgreen}{RGB}{0,100,0}
\definecolor{lightcoral}{RGB}{240,128,128}
\definecolor{lightblue}{RGB}{173,216,230}
\begin{document}
\begin{tikzpicture}
  \begin{axis}[
    width=10cm,
    height=4.6cm,
    xlabel={$E[h(x)] / c(n)$},
    ylabel={Anomaly score $s(x,n)$},
    grid,
    grid style=gray!20,
    xmin=0, xmax=""" + f"{ratio_max}" + r""",
    ymin=0, ymax=1.05,
  ]
    \addplot[line width=2, color=darkgreen] coordinates {
""" + curve_points + r"""
    };
    \addplot[mark=*, mark size=3, only marks, color=red] coordinates {(0.4200, 0.7473)};
    \addplot[mark=square*, mark size=3, only marks, color=blue] coordinates {(1.2601, 0.4176)};
    \node[font=\small, red] at (axis cs: 0.42, 0.86) {anomaly};
    \node[font=\small, blue] at (axis cs: 1.26, 0.30) {normal};
    \draw[dashed, gray] (axis cs: 0, 0.5) -- (axis cs: """ + f"{ratio_max}" + r""", 0.5);
  \end{axis}
\end{tikzpicture}
\end{document}
"""

compile_tikz(score_tex, "anomaly_score_curve")


# ============================================================================
# Figure 4: Random Forest split search vs Extra-Trees random split
# ============================================================================
extra_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{lightgreen}{RGB}{144,238,144}
\definecolor{lightcoral}{RGB}{240,128,128}
\definecolor{lightblue}{RGB}{173,216,230}
\begin{document}
\begin{tikzpicture}
  \node[font=\bfseries, align=center] at (2.5, 1.3) {Random Forest\\\small search all thresholds};
  \draw[-latex, thick] (0,0) -- (5,0);
  \node[below, font=\tiny] at (5,-0.1) {feature value};
  \foreach \x in {0.5,1.1,1.8,2.3,3.0,3.6,4.3} {
    \draw[lightblue, thick] (\x,-0.2) -- (\x,0.2);
  }
  \draw[lightcoral, very thick] (2.3,-0.4) -- (2.3,0.4);
  \node[below, font=\tiny, lightcoral] at (2.3,-0.5) {best $\Delta I$};

  \begin{scope}[xshift=7cm]
    \node[font=\bfseries, align=center] at (2.5, 1.3) {Extra-Trees\\\small one random threshold};
    \draw[-latex, thick] (0,0) -- (5,0);
    \node[below, font=\tiny] at (5,-0.1) {feature value};
    \draw[lightgreen, very thick] (3.1,-0.4) -- (3.1,0.4);
    \node[below, font=\tiny, lightgreen!50!black] at (3.1,-0.5) {random draw};
  \end{scope}
\end{tikzpicture}
\end{document}
"""

compile_tikz(extra_tex, "extra_trees_vs_rf")


# ============================================================================
# Figure 5: Leaf distribution for Quantile Regression Forests
# ============================================================================
bar_heights = [1, 2, 4, 6, 8, 7, 5, 3, 2, 1]
bar_scale = 0.2
bar_step = 0.7
bars = ""
for i, h in enumerate(bar_heights):
    x = i * bar_step
    bars += f"\\fill[lightblue] ({x:.2f},0) rectangle ({x+0.55:.2f},{h*bar_scale:.2f});\n  "

dash_top = max(bar_heights) * bar_scale + 0.15
label_y = dash_top + 0.2
axis_len = len(bar_heights) * bar_step + 0.3

quantile_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{darkred}{RGB}{139,0,0}
\definecolor{darkgreen}{RGB}{0,100,0}
\begin{document}
\begin{tikzpicture}
  \draw[-latex] (0,0) -- (""" + f"{axis_len:.2f}" + r""",0) node[right, font=\small] {$y$};
""" + bars + r"""
  \draw[dashed, darkred, thick] (1.25,0) -- (1.25,""" + f"{dash_top:.2f}" + r""");
  \node[font=\tiny, darkred] at (1.25,""" + f"{label_y:.2f}" + r""") {$\tau=0.1$};
  \draw[dashed, darkgreen, thick] (3.05,0) -- (3.05,""" + f"{dash_top:.2f}" + r""");
  \node[font=\tiny, darkgreen] at (3.05,""" + f"{label_y:.2f}" + r""") {$\tau=0.5$};
  \draw[dashed, darkred, thick] (4.85,0) -- (4.85,""" + f"{dash_top:.2f}" + r""");
  \node[font=\tiny, darkred] at (4.85,""" + f"{label_y:.2f}" + r""") {$\tau=0.9$};
\end{tikzpicture}
\end{document}
"""

compile_tikz(quantile_tex, "quantile_forest_leaf")

print("\n✓ All Forest Variants figures generated successfully!")
