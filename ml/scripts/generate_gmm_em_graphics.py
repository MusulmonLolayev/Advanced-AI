#!/usr/bin/env python3
"""Generate vector Gaussian Mixture Model / EM teaching graphics as PDF (and SVG) files.

Uses pandas to build the underlying numeric tables (density curves, the
worked-example responsibility table, the synthetic 2D dataset) and TikZ/pgfplots
to render them as vector graphics, compiled with pdflatex. Each PDF is also
converted to SVG via dvisvgm as a second artifact; the slide deck itself keeps
including the PDFs, matching every other lecture's figures.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "gmm_em"
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


def gaussian_pdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    return np.exp(-((x - mu) ** 2) / (2 * sigma**2)) / (sigma * np.sqrt(2 * np.pi))


def responsibility1(x: np.ndarray, mu1: float, mu2: float, sigma: float) -> np.ndarray:
    """Equal-prior, equal-sigma responsibility of component 1 (sigmoid form)."""
    d1sq = (x - mu1) ** 2
    d2sq = (x - mu2) ** 2
    return 1.0 / (1.0 + np.exp(-(d2sq - d1sq) / (2 * sigma**2)))


# ============================================================================
# Figure 0: Intro contrast -- one boundary point, forced choice vs. soft probability
# ============================================================================
intro_df = pd.DataFrame(
    [
        ("A1", 0.6, 0.8, "A"), ("A2", 1.0, 1.3, "A"),
        ("A3", 1.4, 0.6, "A"), ("A4", 0.8, 1.6, "A"),
        ("B1", 4.4, 3.2, "B"), ("B2", 3.8, 3.8, "B"),
        ("B3", 4.0, 2.8, "B"), ("B4", 4.6, 3.6, "B"),
    ],
    columns=["id", "x", "y", "cluster"],
)
intro_cA = intro_df.loc[intro_df["cluster"] == "A", ["x", "y"]].mean()
intro_cB = intro_df.loc[intro_df["cluster"] == "B", ["x", "y"]].mean()
intro_mid = (intro_cA + intro_cB) / 2.0
intro_direction = np.array([intro_cB.x - intro_cA.x, intro_cB.y - intro_cA.y])
intro_perp = np.array([-intro_direction[1], intro_direction[0]])
intro_perp_unit = intro_perp / np.linalg.norm(intro_perp)
intro_boundary_a = intro_mid.values + 2.5 * intro_perp_unit
intro_boundary_b = intro_mid.values - 2.5 * intro_perp_unit
MX, MY, PIE_R = float(intro_mid.x), float(intro_mid.y), 0.30


def intro_marks() -> str:
    out = []
    for _, row in intro_df.iterrows():
        color = "lightblue" if row["cluster"] == "A" else "lightcoral"
        out.append(f"\\fill[{color}, draw=black] ({row['x']:.3f},{row['y']:.3f}) circle (3.0pt);\n    ")
    return "".join(out)


intro_panel_marks = intro_marks()

hard_vs_soft_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightcoral}{RGB}{240,128,128}
\begin{document}
\begin{tabular}{cc}
\textbf{$k$-Means: forced choice} & \textbf{GMM: soft probability} \\[3pt]
\begin{tikzpicture}
  \begin{scope}
    \clip (-0.5,-0.5) rectangle (5.1,4.3);
    \draw[dashed, thick, gray] ("""
    + f"{intro_boundary_a[0]:.3f},{intro_boundary_a[1]:.3f}) -- ({intro_boundary_b[0]:.3f},{intro_boundary_b[1]:.3f}"
    + r""");
  \end{scope}
"""
    + intro_panel_marks
    + r"""\fill[lightblue, draw=black, line width=0.8pt] ("""
    + f"{MX:.3f},{MY:.3f}) circle ({PIE_R:.2f}"
    + r""");
  \node[font=\tiny, align=center] at ("""
    + f"{MX:.3f},{MY - 0.65:.3f}"
    + r""") {forced to cluster $A$\\(despite 50/50 evidence)};
\end{tikzpicture}
&
\begin{tikzpicture}
"""
    + intro_panel_marks
    + r"""\begin{scope}
    \clip ("""
    + f"{MX - PIE_R:.3f},{MY - PIE_R:.3f}) rectangle ({MX:.3f},{MY + PIE_R:.3f}"
    + r""");
    \fill[lightblue] ("""
    + f"{MX:.3f},{MY:.3f}) circle ({PIE_R:.2f}"
    + r""");
  \end{scope}
  \begin{scope}
    \clip ("""
    + f"{MX:.3f},{MY - PIE_R:.3f}) rectangle ({MX + PIE_R:.3f},{MY + PIE_R:.3f}"
    + r""");
    \fill[lightcoral] ("""
    + f"{MX:.3f},{MY:.3f}) circle ({PIE_R:.2f}"
    + r""");
  \end{scope}
  \draw[black, line width=0.8pt] ("""
    + f"{MX:.3f},{MY:.3f}) circle ({PIE_R:.2f}"
    + r""");
  \node[font=\tiny, align=center] at ("""
    + f"{MX:.3f},{MY - 0.65:.3f}"
    + r""") {$p(A)=0.50,\ p(B)=0.50$\\(both kept)};
\end{tikzpicture}
\end{tabular}
\end{document}
"""
)

compile_tikz(hard_vs_soft_tex, "hard_vs_soft_intro")


# ============================================================================
# Figure 0a: Refresher -- the 1D Gaussian (Normal) distribution
# ============================================================================
REF_MU, REF_SIGMA = 0.0, 1.5
ref_x = np.linspace(-5, 5, 201)
ref_y = gaussian_pdf(ref_x, REF_MU, REF_SIGMA)
ref_curve_pts = " ".join(f"({x:.3f},{y:.5f})" for x, y in zip(ref_x, ref_y))

band_x = np.linspace(REF_MU - REF_SIGMA, REF_MU + REF_SIGMA, 41)
band_y = gaussian_pdf(band_x, REF_MU, REF_SIGMA)
band_pts = " ".join(f"({x:.3f},{y:.5f})" for x, y in zip(band_x, band_y))

peak_y = float(gaussian_pdf(np.array([REF_MU]), REF_MU, REF_SIGMA)[0])
ymax = peak_y * 1.35
mu_line_top = peak_y * 1.05
mu_label_y = peak_y * 1.20
sigma_arrow_y = peak_y * 0.42
sigma_label_y = peak_y * 0.54

gaussian_1d_tex = rf"""
\documentclass[crop]{{standalone}}
\usepackage{{xcolor}}
\usepackage{{amsmath}}
\usepackage{{pgfplots}}
\pgfplotsset{{compat=1.18}}
\definecolor{{darkblue}}{{RGB}}{{0,0,139}}
\definecolor{{lightblue}}{{RGB}}{{173,216,230}}
\begin{{document}}
\begin{{tikzpicture}}
  \begin{{axis}}[
    width=9cm,
    height=5.0cm,
    xlabel={{$x$}},
    ylabel={{density}},
    grid,
    grid style=gray!20,
    xmin=-5, xmax=5,
    ymin=0, ymax={ymax:.4f},
  ]
    \addplot[fill=lightblue, draw=none, opacity=0.6] coordinates {{
{band_pts} ({REF_MU + REF_SIGMA:.3f},0.0) ({REF_MU - REF_SIGMA:.3f},0.0)
    }} \closedcycle;
    \addplot[line width=1.8, color=darkblue] coordinates {{
{ref_curve_pts}
    }};
    \draw[dashed, gray] (axis cs: {REF_MU:.3f},0) -- (axis cs: {REF_MU:.3f},{mu_line_top:.4f});
    \node[font=\small] at (axis cs: {REF_MU:.3f},{mu_label_y:.4f}) {{$\mu$}};
    \draw[latex-latex] (axis cs: {REF_MU - REF_SIGMA:.3f},{sigma_arrow_y:.4f}) -- (axis cs: {REF_MU + REF_SIGMA:.3f},{sigma_arrow_y:.4f});
    \node[font=\small] at (axis cs: {REF_MU:.3f},{sigma_label_y:.4f}) {{$\sigma$}};
  \end{{axis}}
\end{{tikzpicture}}
\end{{document}}
"""

compile_tikz(gaussian_1d_tex, "gaussian_1d_refresher")


# ============================================================================
# Figure 0b: Refresher -- covariance shapes a multivariate Gaussian "blob"
# ============================================================================
def covariance_ellipse(cov: np.ndarray, n_std: float = 1.5, n_points: int = 100) -> tuple[np.ndarray, np.ndarray]:
    """Points on the n_std-sigma contour ellipse of a 2D covariance matrix."""
    eigvals, eigvecs = np.linalg.eigh(cov)
    theta = np.linspace(0, 2 * np.pi, n_points)
    circle = np.vstack([np.cos(theta), np.sin(theta)])
    sqrt_cov = eigvecs @ np.diag(np.sqrt(eigvals))
    pts = n_std * (sqrt_cov @ circle)
    return pts[0], pts[1]


cov_specs = [
    ("spherical (isotropic)", np.array([[1.0, 0.0], [0.0, 1.0]])),
    ("diagonal", np.array([[2.2, 0.0], [0.0, 0.5]])),
    ("full (correlated)", np.array([[2.0, 1.3], [1.3, 1.2]])),
]


def ellipse_panel(label: str, cov: np.ndarray) -> str:
    ex, ey = covariance_ellipse(cov)
    outline = " -- ".join(f"({x:.3f},{y:.3f})" for x, y in zip(ex, ey))
    return (
        r"""\begin{tikzpicture}
  \draw[-latex, gray] (-3,0) -- (3,0);
  \draw[-latex, gray] (0,-3) -- (0,3);
  \draw[line width=1.6, color=darkblue, fill=lightblue, fill opacity=0.35] """
        + outline
        + r""" -- cycle;
  \node[font=\small] at (0,-3.4) {"""
        + label
        + r"""};
\end{tikzpicture}"""
    )


cov_panels = [ellipse_panel(label, cov) for label, cov in cov_specs]

covariance_shapes_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{darkblue}{RGB}{0,0,139}
\definecolor{lightblue}{RGB}{173,216,230}
\begin{document}
\begin{tabular}{ccc}
"""
    + cov_panels[0]
    + r""" &
"""
    + cov_panels[1]
    + r""" &
"""
    + cov_panels[2]
    + r"""
\end{tabular}
\end{document}
"""
)

compile_tikz(covariance_shapes_tex, "covariance_shapes")


# ============================================================================
# Figure 1: 1D mixture density = weighted sum of two Gaussian components
# ============================================================================
MU1, MU2, SIGMA = 0.0, 10.0, 3.0
density_df = pd.DataFrame({"x": np.linspace(-5, 15, 201)})
density_df["comp1"] = 0.5 * gaussian_pdf(density_df["x"], MU1, SIGMA)
density_df["comp2"] = 0.5 * gaussian_pdf(density_df["x"], MU2, SIGMA)
density_df["mixture"] = density_df["comp1"] + density_df["comp2"]

comp1_pts = " ".join(f"({r.x:.3f},{r.comp1:.5f})" for r in density_df.itertuples())
comp2_pts = " ".join(f"({r.x:.3f},{r.comp2:.5f})" for r in density_df.itertuples())
mixture_pts = " ".join(f"({r.x:.3f},{r.mixture:.5f})" for r in density_df.itertuples())

mixture_density_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{amsmath}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\definecolor{darkblue}{RGB}{0,0,139}
\definecolor{darkred}{RGB}{139,0,0}
\definecolor{darkgreen}{RGB}{0,100,0}
\begin{document}
\begin{tikzpicture}
  \begin{axis}[
    width=10cm,
    height=4.0cm,
    xlabel={$x$},
    ylabel={density},
    grid,
    grid style=gray!20,
    xmin=-5, xmax=15,
    ymin=0, ymax=0.09,
    legend pos=north east,
    legend style={font=\tiny},
  ]
    \addplot[line width=1.2, dashed, color=darkblue] coordinates {
"""
    + comp1_pts
    + r"""
    };
    \addlegendentry{$\pi_1\mathcal{N}(x\mid\mu_1,\sigma^2)$}
    \addplot[line width=1.2, dashed, color=darkred] coordinates {
"""
    + comp2_pts
    + r"""
    };
    \addlegendentry{$\pi_2\mathcal{N}(x\mid\mu_2,\sigma^2)$}
    \addplot[line width=2.2, color=darkgreen] coordinates {
"""
    + mixture_pts
    + r"""
    };
    \addlegendentry{mixture $p(x)$}
    \draw[dashed, gray] (axis cs: 0,0) -- (axis cs: 0,0.075);
    \draw[dashed, gray] (axis cs: 10,0) -- (axis cs: 10,0.075);
    \node[font=\tiny, gray] at (axis cs: 0, 0.080) {$\mu_1$};
    \node[font=\tiny, gray] at (axis cs: 10, 0.080) {$\mu_2$};
  \end{axis}
\end{tikzpicture}
\end{document}
"""
)

compile_tikz(mixture_density_tex, "mixture_density_1d")


# ============================================================================
# Figure 2: E-step responsibilities for the worked example (mu1=0, mu2=10, sigma=3)
# ============================================================================
resp_df = pd.DataFrame({"x": [1.0, 2.0, 8.0, 9.0]})
resp_df["gamma1"] = responsibility1(resp_df["x"], MU1, MU2, SIGMA)
resp_df["gamma2"] = 1.0 - resp_df["gamma1"]

g1_pts = " ".join(f"(x={int(r.x)},{r.gamma1:.4f})" for r in resp_df.itertuples())
g2_pts = " ".join(f"(x={int(r.x)},{r.gamma2:.4f})" for r in resp_df.itertuples())

responsibilities_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{amsmath}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightcoral}{RGB}{240,128,128}
\begin{document}
\begin{tikzpicture}
  \begin{axis}[
    width=8.5cm,
    height=4.0cm,
    ybar stacked,
    bar width=22pt,
    symbolic x coords={x=1,x=2,x=8,x=9},
    xtick=data,
    xlabel={data point},
    ylabel={responsibility},
    ymin=0, ymax=1.18,
    legend pos=north east,
    legend style={font=\tiny},
    enlarge x limits=0.18,
  ]
    \addplot[fill=lightblue, draw=black] coordinates {
"""
    + g1_pts
    + r"""
    };
    \addlegendentry{$\gamma_{n1}$ (component 1)}
    \addplot[fill=lightcoral, draw=black] coordinates {
"""
    + g2_pts
    + r"""
    };
    \addlegendentry{$\gamma_{n2}$ (component 2)}
  \end{axis}
\end{tikzpicture}
\end{document}
"""
)

compile_tikz(responsibilities_tex, "em_responsibilities")


# ============================================================================
# Figure 3: One EM iteration -- curves/points before and after the M-step
# ============================================================================
pts_df = resp_df.copy()
MU1_NEW = float((pts_df["gamma1"] * pts_df["x"]).sum() / pts_df["gamma1"].sum())
MU2_NEW = float((pts_df["gamma2"] * pts_df["x"]).sum() / pts_df["gamma2"].sum())
pts_df["gamma1_new"] = responsibility1(pts_df["x"], MU1_NEW, MU2_NEW, SIGMA)
pts_df["gamma2_new"] = 1.0 - pts_df["gamma1_new"]

curve_x = np.linspace(-5, 15, 161)
before1 = gaussian_pdf(curve_x, MU1, SIGMA)
before2 = gaussian_pdf(curve_x, MU2, SIGMA)
after1 = gaussian_pdf(curve_x, MU1_NEW, SIGMA)
after2 = gaussian_pdf(curve_x, MU2_NEW, SIGMA)

before1_pts = " ".join(f"({x:.3f},{y:.5f})" for x, y in zip(curve_x, before1))
before2_pts = " ".join(f"({x:.3f},{y:.5f})" for x, y in zip(curve_x, before2))
after1_pts = " ".join(f"({x:.3f},{y:.5f})" for x, y in zip(curve_x, after1))
after2_pts = " ".join(f"({x:.3f},{y:.5f})" for x, y in zip(curve_x, after2))


def point_marks(df: pd.DataFrame, g1_col: str) -> str:
    out = []
    for _, row in df.iterrows():
        mix = 100.0 * (1.0 - row[g1_col])
        out.append(
            f"\\addplot[only marks, mark=*, mark size=2.6, color=lightblue!{mix:.0f}!lightcoral] "
            f"coordinates {{({row['x']:.3f},0.005)}};\n    "
        )
    return "".join(out)


before_marks = point_marks(pts_df, "gamma1")
after_marks = point_marks(pts_df, "gamma1_new")

em_iterations_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{amsmath}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\definecolor{darkblue}{RGB}{0,0,139}
\definecolor{darkred}{RGB}{139,0,0}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightcoral}{RGB}{240,128,128}
\begin{document}
\begin{tabular}{cc}
"""
    + f"\\textbf{{Before: }} $\\mu_1={MU1:.2f}, \\mu_2={MU2:.2f}$"
    + r""" & """
    + f"\\textbf{{After M-step: }} $\\mu_1={MU1_NEW:.3f}, \\mu_2={MU2_NEW:.3f}$"
    + r"""\\[3pt]
\begin{tikzpicture}
  \begin{axis}[
    width=6.4cm, height=4.6cm,
    xlabel={$x$}, ylabel={density},
    grid, grid style=gray!20,
    xmin=-5, xmax=15, ymin=0, ymax=0.14,
  ]
    \addplot[line width=1.6, color=darkblue] coordinates {
"""
    + before1_pts
    + r"""
    };
    \addplot[line width=1.6, color=darkred] coordinates {
"""
    + before2_pts
    + r"""
    };
"""
    + before_marks
    + r"""
  \end{axis}
\end{tikzpicture}
&
\begin{tikzpicture}
  \begin{axis}[
    width=6.4cm, height=4.6cm,
    xlabel={$x$}, ylabel={density},
    grid, grid style=gray!20,
    xmin=-5, xmax=15, ymin=0, ymax=0.14,
  ]
    \addplot[line width=1.6, color=darkblue] coordinates {
"""
    + after1_pts
    + r"""
    };
    \addplot[line width=1.6, color=darkred] coordinates {
"""
    + after2_pts
    + r"""
    };
"""
    + after_marks
    + r"""
  \end{axis}
\end{tikzpicture}
\end{tabular}
\end{document}
"""
)

compile_tikz(em_iterations_tex, "em_iterations")


# ============================================================================
# Figure 4: Monotonic increase of the log-likelihood across EM iterations
# ============================================================================
ll_df = pd.DataFrame({"t": np.arange(0, 11)})
ll_df["loglik"] = -6.535 - 18.465 * np.exp(-0.4 * ll_df["t"])
ll_pts = " ".join(f"({r.t},{r.loglik:.3f})" for r in ll_df.itertuples())

em_convergence_tex = (
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
    xlabel={EM iteration},
    ylabel={log-likelihood $\ell$},
    grid,
    grid style=gray!20,
    xmin=0, xmax=10,
    ymin=-26, ymax=-4,
  ]
    \addplot[line width=2, color=darkgreen, mark=*, mark size=1.6] coordinates {
"""
    + ll_pts
    + r"""
    };
    \draw[dashed, gray] (axis cs: 0,-6.535) -- (axis cs: 10,-6.535);
    \node[font=\tiny, gray, anchor=east] at (axis cs: 9.8,-5.0) {plateau: $\ell$ stops increasing};
  \end{axis}
\end{tikzpicture}
\end{document}
"""
)

compile_tikz(em_convergence_tex, "em_convergence")


# ============================================================================
# Figure 5: Hard k-means partition vs. soft GMM responsibilities (2D)
# ============================================================================
cluster_df = pd.DataFrame(
    [
        ("A1", 0.6, 0.8, "A"), ("A2", 1.0, 1.3, "A"), ("A3", 1.4, 0.6, "A"),
        ("A4", 0.8, 1.6, "A"), ("A5", 1.6, 1.1, "A"),
        ("B1", 4.4, 3.2, "B"), ("B2", 3.8, 3.8, "B"), ("B3", 4.0, 2.8, "B"),
        ("B4", 4.6, 3.6, "B"), ("B5", 3.6, 3.1, "B"),
        ("M1", 2.4, 2.0, "?"), ("M2", 2.8, 2.6, "?"),
    ],
    columns=["id", "x", "y", "seed_label"],
)
centroids = cluster_df.loc[cluster_df["seed_label"] != "?"].groupby("seed_label")[["x", "y"]].mean()
cA = centroids.loc["A"]
cB = centroids.loc["B"]
GMM_SIGMA_2D = 1.15

cluster_df["d1sq"] = (cluster_df["x"] - cA.x) ** 2 + (cluster_df["y"] - cA.y) ** 2
cluster_df["d2sq"] = (cluster_df["x"] - cB.x) ** 2 + (cluster_df["y"] - cB.y) ** 2
cluster_df["gammaB"] = 1.0 / (1.0 + np.exp(-(cluster_df["d1sq"] - cluster_df["d2sq"]) / (2 * GMM_SIGMA_2D**2)))
cluster_df["hard_is_B"] = cluster_df["d2sq"] < cluster_df["d1sq"]

mid = (cA + cB) / 2.0
direction = np.array([cB.x - cA.x, cB.y - cA.y])
perp = np.array([-direction[1], direction[0]])
perp_unit = perp / np.linalg.norm(perp)
boundary_a = mid.values + 3.0 * perp_unit
boundary_b = mid.values - 3.0 * perp_unit


def hard_marks(df: pd.DataFrame) -> str:
    out = []
    for _, row in df.iterrows():
        color = "lightcoral" if row["hard_is_B"] else "lightblue"
        out.append(f"\\fill[{color}, draw=black] ({row['x']:.3f},{row['y']:.3f}) circle (3.2pt);\n    ")
    return "".join(out)


def soft_marks(df: pd.DataFrame) -> str:
    out = []
    for _, row in df.iterrows():
        mix = 100.0 * (1.0 - row["gammaB"])
        out.append(
            f"\\fill[lightblue!{mix:.0f}!lightcoral, draw=black] "
            f"({row['x']:.3f},{row['y']:.3f}) circle (3.2pt);\n    "
        )
    return "".join(out)


hard_panel_marks = hard_marks(cluster_df)
soft_panel_marks = soft_marks(cluster_df)

gmm_vs_kmeans_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
\definecolor{lightblue}{RGB}{173,216,230}
\definecolor{lightcoral}{RGB}{240,128,128}
\begin{document}
\begin{tabular}{cc}
\textbf{k-Means: hard assignment} & \textbf{GMM: soft responsibility} \\[3pt]
\begin{tikzpicture}
  \begin{scope}
    \clip (-0.5,-0.5) rectangle (5.5,4.5);
    \draw[dashed, thick, gray] ("""
    + f"{boundary_a[0]:.3f},{boundary_a[1]:.3f}) -- ({boundary_b[0]:.3f},{boundary_b[1]:.3f}"
    + r""");
  \end{scope}
  \draw[-latex] (-0.5,0) -- (5.5,0) node[right, font=\tiny] {$x_1$};
  \draw[-latex] (0,-0.5) -- (0,4.5) node[above, font=\tiny] {$x_2$};
"""
    + hard_panel_marks
    + r"""
  \node[font=\tiny] at (1.0,-0.3) {cluster $A$};
  \node[font=\tiny] at (4.0,-0.3) {cluster $B$};
\end{tikzpicture}
&
\begin{tikzpicture}
  \draw[-latex] (-0.5,0) -- (5.5,0) node[right, font=\tiny] {$x_1$};
  \draw[-latex] (0,-0.5) -- (0,4.5) node[above, font=\tiny] {$x_2$};
"""
    + soft_panel_marks
    + r"""
  \node[font=\tiny, align=center] at (2.6,4.2) {blended color $=$\\mixed responsibility};
\end{tikzpicture}
\end{tabular}
\end{document}
"""
)

compile_tikz(gmm_vs_kmeans_tex, "gmm_vs_kmeans")

print("\n✓ All GMM & EM figures generated successfully!")
