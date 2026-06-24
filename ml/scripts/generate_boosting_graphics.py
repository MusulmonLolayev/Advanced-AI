#!/usr/bin/env python3
"""Generate vector Boosting teaching graphics as PDF (and SVG) files.

Uses pandas to build the underlying numeric tables (curve points, the
worked-example weight table) and TikZ/pgfplots to render them as vector
graphics, compiled with pdflatex. Each PDF is also converted to SVG via
dvisvgm as a second artifact; the slide deck itself keeps including the
PDFs, matching every other lecture's figures.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "boosting"
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
        svg_path = OUT_DIR / f"{name}.svg"
        svg_result = subprocess.run(
            ["dvisvgm", "--pdf", str(pdf_path), "-o", str(svg_path)],
            capture_output=True,
            text=True,
            cwd=str(OUT_DIR),
        )
        if svg_result.returncode == 0:
            print(f"✓ {name}.svg")
        else:
            print(f"✗ {name}.svg - conversion failed")
            print(svg_result.stderr[-1500:] if svg_result.stderr else "")
        for ext in [".aux", ".log", ".tex"]:
            (OUT_DIR / f"{name}{ext}").unlink(missing_ok=True)
    else:
        print(f"✗ {name}.pdf - compilation failed")
        print(result.stdout[-1500:] if result.stdout else "")


# ============================================================================
# Figure 1: Reweighting after one AdaBoost round (worked-example points)
# ============================================================================
points_df = pd.DataFrame(
    [
        ("P1", 1.0, 1.0, "pos", False),
        ("P2", 1.8, 2.6, "pos", False),
        ("P3", 3.6, 1.3, "neg", False),
        ("P4", 4.2, 2.9, "neg", False),
        ("P5", 1.5, 3.3, "neg", True),
    ],
    columns=["id", "x", "y", "label", "misclassified"],
)
points_df["w_round1"] = 0.2
points_df["w_round2"] = np.where(points_df["misclassified"], 0.5, 0.125)
points_df["r_round1"] = 8.0 * np.sqrt(points_df["w_round1"])
points_df["r_round2"] = 8.0 * np.sqrt(points_df["w_round2"])


def marker(row: pd.Series, radius_col: str) -> str:
    color = "lightblue" if row["label"] == "pos" else "lightcoral"
    shape = "rectangle" if row["label"] == "pos" else "circle"
    r = row[radius_col]
    if shape == "rectangle":
        return f"\\fill[{color}] ({row['x']-r/28:.3f},{row['y']-r/28:.3f}) rectangle ({row['x']+r/28:.3f},{row['y']+r/28:.3f});\n  "
    return f"\\fill[{color}] ({row['x']:.3f},{row['y']:.3f}) circle ({r:.2f}pt);\n  "


round1_marks = "".join(marker(row, "r_round1") for _, row in points_df.iterrows())
round2_marks = "".join(marker(row, "r_round2") for _, row in points_df.iterrows())
miss_row = points_df.loc[points_df["misclassified"]].iloc[0]

reweighting_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightcoral}{RGB}{240,128,128}
\begin{document}
\begin{tabular}{cc}
\textbf{Round 1: weights uniform, $\epsilon_1=0.2$} & \textbf{Round 2: reweighted after round 1} \\[3pt]
\begin{tikzpicture}
    \draw[-latex] (0,0) -- (5,0) node[right, font=\tiny] {$x_1$};
    \draw[dashed, gray, thick] (2.5,0) -- (2.5,4);
    \node[font=\tiny, gray] at (2.5,4.25) {stump: $x_1<2.5\Rightarrow +1$};
"""
    + round1_marks
    + r"""
    \draw[thick, black] ("""
    + f"{miss_row['x']:.3f},{miss_row['y']:.3f}"
    + r""") circle (10pt);
    \node[font=\tiny] at ("""
    + f"{miss_row['x']:.3f},{miss_row['y']+0.55:.3f}"
    + r""") {misclassified};
\end{tikzpicture}
&
\begin{tikzpicture}
    \draw[-latex] (0,0) -- (5,0) node[right, font=\tiny] {$x_1$};
    \draw[dashed, gray!40, thick] (2.5,0) -- (2.5,4);
"""
    + round2_marks
    + r"""
    \node[font=\tiny] at ("""
    + f"{miss_row['x']:.3f},{miss_row['y']+0.55:.3f}"
    + r""") {$5\times$ heavier};
\end{tikzpicture}
\end{tabular}
\end{document}
"""
)

compile_tikz(reweighting_tex, "boosting_reweighting")


# ============================================================================
# Figure 2: alpha(epsilon) = 0.5 ln((1-epsilon)/epsilon)
# ============================================================================
alpha_df = pd.DataFrame({"eps": np.linspace(0.05, 0.95, 91)})
alpha_df["alpha"] = 0.5 * np.log((1.0 - alpha_df["eps"]) / alpha_df["eps"])
alpha_curve_points = " ".join(f"({r.eps:.4f},{r.alpha:.4f})" for r in alpha_df.itertuples())

alpha_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{amsmath}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\definecolor{darkgreen}{RGB}{0,100,0}
\begin{document}
\begin{tikzpicture}
  \begin{axis}[
    width=10cm,
    height=4.6cm,
    xlabel={Weighted error $\epsilon_m$},
    ylabel={$\alpha_m = \tfrac12\ln\frac{1-\epsilon_m}{\epsilon_m}$},
    grid,
    grid style=gray!20,
    xmin=0.05, xmax=0.95,
    ymin=-1.6, ymax=1.6,
  ]
    \addplot[line width=2, color=darkgreen] coordinates {
"""
    + alpha_curve_points
    + r"""
    };
    \addplot[mark=*, mark size=3, only marks, color=red] coordinates {(0.2000, 0.6931)};
    \node[font=\small, red] at (axis cs: 0.30, 0.95) {round 1: $\epsilon_1=0.2$};
    \draw[dashed, gray] (axis cs: 0.05, 0) -- (axis cs: 0.95, 0);
    \node[font=\tiny, gray] at (axis cs: 0.5, -0.25) {$\epsilon=0.5\Rightarrow\alpha=0$};
  \end{axis}
\end{tikzpicture}
\end{document}
"""
)

compile_tikz(alpha_tex, "alpha_vs_error")


# ============================================================================
# Figure 3: Stagewise additive model F_m(x) = F_{m-1}(x) + alpha_m h_m(x)
# ============================================================================
stagewise_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{lightyellow}{RGB}{255,255,200}
\definecolor{lightgreen}{RGB}{144,238,144}
\begin{document}
\begin{tikzpicture}[
  every node/.style={font=\small},
  box/.style={draw, rounded corners, fill=lightyellow, minimum height=0.8cm, minimum width=1.9cm, align=center},
  plus/.style={draw, circle, fill=lightgreen, minimum size=0.55cm}
]
  \node[box] (F0) at (0,4) {$F_0(x)$};
  \node[plus] (plus1) at (2.3,4) {$+$};
  \node[box] (F1) at (4.6,4) {$F_1(x)$};
  \node[box, fill=lightgreen!40] (term1) at (2.3,3.0) {$\alpha_1 h_1(x)$};
  \draw[-latex, thick] (F0) -- (plus1);
  \draw[-latex, thick] (plus1) -- (F1);
  \draw[-latex, thick] (term1) -- (plus1);

  \node[box] (F1b) at (0,2) {$F_1(x)$};
  \node[plus] (plus2) at (2.3,2) {$+$};
  \node[box] (F2) at (4.6,2) {$F_2(x)$};
  \node[box, fill=lightgreen!40] (term2) at (2.3,1.0) {$\alpha_2 h_2(x)$};
  \draw[-latex, thick] (F1b) -- (plus2);
  \draw[-latex, thick] (plus2) -- (F2);
  \draw[-latex, thick] (term2) -- (plus2);

  \node[box] (F2b) at (0,0) {$F_2(x)$};
  \node[plus] (plus3) at (2.3,0) {$+$};
  \node[box] (F3) at (4.6,0) {$F_3(x)$};
  \node[box, fill=lightgreen!40] (term3) at (2.3,-1.0) {$\alpha_3 h_3(x)$};
  \draw[-latex, thick] (F2b) -- (plus3);
  \draw[-latex, thick] (plus3) -- (F3);
  \draw[-latex, thick] (term3) -- (plus3);

  \node[font=\tiny, align=left, anchor=west] at (5.5,0) {final model\\$F_M(x)=\sum_{m=1}^{M}\alpha_m h_m(x)$};
\end{tikzpicture}
\end{document}
"""

compile_tikz(stagewise_tex, "stagewise_additive")


# ============================================================================
# Figure 4: Training/test error vs boosting round
# ============================================================================
error_df = pd.DataFrame(
    [
        (0, 0.500, 0.500), (1, 0.380, 0.400), (2, 0.290, 0.330), (3, 0.220, 0.280),
        (4, 0.170, 0.240), (5, 0.130, 0.210), (6, 0.100, 0.190), (7, 0.075, 0.175),
        (8, 0.055, 0.165), (9, 0.040, 0.158), (10, 0.030, 0.155), (12, 0.018, 0.156),
        (14, 0.010, 0.162), (16, 0.006, 0.172), (18, 0.004, 0.185), (20, 0.003, 0.200),
    ],
    columns=["t", "train_err", "test_err"],
)
train_points = " ".join(f"({r.t},{r.train_err:.3f})" for r in error_df.itertuples())
test_points = " ".join(f"({r.t},{r.test_err:.3f})" for r in error_df.itertuples())

error_curve_tex = (
    r"""
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
    height=4.6cm,
    xlabel={Boosting round $t$},
    ylabel={Error},
    grid,
    grid style=gray!20,
    xmin=0, xmax=20,
    ymin=0, ymax=0.55,
    legend pos=north east,
    legend style={font=\tiny},
  ]
    \addplot[line width=2, color=darkgreen] coordinates {
"""
    + train_points
    + r"""
    };
    \addlegendentry{training error}
    \addplot[line width=2, dashed, color=darkred] coordinates {
"""
    + test_points
    + r"""
    };
    \addlegendentry{test error}
  \end{axis}
\end{tikzpicture}
\end{document}
"""
)

compile_tikz(error_curve_tex, "training_error_curve")


# ============================================================================
# Figure 5: Bagging (parallel) vs Boosting (sequential)
# ============================================================================
bagging_boosting_tex = r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightgreen}{RGB}{144,238,144}
\begin{document}
\begin{tikzpicture}[
  every node/.style={font=\small},
  box/.style={draw, rounded corners, fill=lightblue, minimum height=0.7cm, minimum width=1.5cm, align=center}
]
  \node[font=\bfseries] at (1.9,3.0) {Bagging: parallel, independent};
  \node[box] (data) at (1.9,2.1) {data};
  \node[box] (t1) at (0,0.9) {$T_1$};
  \node[box] (t2) at (1.9,0.9) {$T_2$};
  \node[box] (t3) at (3.8,0.9) {$T_3$};
  \node[box, fill=lightgreen] (avg) at (1.9,-0.3) {average / vote};
  \foreach \t in {t1,t2,t3} {
    \draw[-latex, thick] (data) -- (\t);
    \draw[-latex, thick] (\t) -- (avg);
  }

  \begin{scope}[xshift=7.2cm]
    \node[font=\bfseries] at (1.9,3.0) {Boosting: sequential, dependent};
    \node[box] (h1) at (0,1.9) {$h_1$};
    \node[box] (h2) at (1.9,0.9) {$h_2$};
    \node[box] (h3) at (3.8,-0.1) {$h_3$};
    \node[box, fill=lightgreen] (sum) at (3.8,-1.3) {weighted sum};
    \draw[-latex, thick] (h1) -- node[above, font=\tiny] {reweight} (h2);
    \draw[-latex, thick] (h2) -- node[above, font=\tiny] {reweight} (h3);
    \draw[-latex, thick] (h3) -- (sum);
    \draw[-latex, thick] (h1) to[bend left=15] (sum.west);
    \draw[-latex, thick] (h2) to[bend left=8] (sum.west);
  \end{scope}
\end{tikzpicture}
\end{document}
"""

compile_tikz(bagging_boosting_tex, "bagging_vs_boosting")

print("\n✓ All Boosting figures generated successfully!")
