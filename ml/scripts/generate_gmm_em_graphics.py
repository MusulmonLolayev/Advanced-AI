#!/usr/bin/env python3
"""Generate GMM & EM lecture figures: 2D, K=3, 6-point worked example.

Pipeline: pandas DataFrame → TikZ/pgfplots string → pdflatex → PDF + SVG.

Figures produced
----------------
kmeans_limitation.pdf   – hard k-Means boundary vs GMM soft responsibility
em_init.pdf             – 6-point dataset with initial component positions
em_iter_panels.pdf      – 2×2 grid: iterations 0, 1, 2, 3
covariance_shapes.pdf   – spherical / diagonal / full covariance ellipses
em_convergence.pdf      – log-likelihood convergence across EM iterations
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "gmm_em"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ─── compile helper ───────────────────────────────────────────────────────────

def compile_tikz(content: str, name: str) -> None:
    """Write TikZ content to a .tex file and compile to PDF + SVG."""
    tex_path = OUT_DIR / f"{name}.tex"
    pdf_path = OUT_DIR / f"{name}.pdf"
    tex_path.write_text(content)
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
         "-output-directory", str(OUT_DIR), str(tex_path)],
        capture_output=True, text=True, cwd=str(OUT_DIR),
    )
    if result.returncode == 0:
        print(f"✓ {name}.pdf")
        svg_path = OUT_DIR / f"{name}.svg"
        svg_result = subprocess.run(
            ["dvisvgm", "--pdf", str(pdf_path), "-o", str(svg_path)],
            capture_output=True, text=True, cwd=str(OUT_DIR),
        )
        print(f"✓ {name}.svg" if svg_result.returncode == 0 else f"✗ {name}.svg")
        for ext in [".aux", ".log", ".tex"]:
            (OUT_DIR / f"{name}{ext}").unlink(missing_ok=True)
    else:
        print(f"✗ {name}.pdf  — pdflatex failed")
        print(result.stdout[-2000:] if result.stdout else "")


# ─── dataset ──────────────────────────────────────────────────────────────────

points_df = pd.DataFrame({
    "n":    [1,   2,    3,    4,   5,   6],
    "x1":   [0.,  2.,  10.,   8.,  5.,  5.],
    "x2":   [0.,  0.,   0.,   0.,  9.,  7.],
    "comp": [1,   1,    2,    2,   3,   3],   # true component label
})
X = points_df[["x1", "x2"]].values   # (6, 2)
N, D = X.shape
K = 3
SIGMA = 4.0   # shared isotropic, fixed throughout

MU_INIT = np.array([[0., 0.], [10., 0.], [5., 10.]])
PI = np.ones(K) / K

# ─── EM helpers ───────────────────────────────────────────────────────────────

def log_gaussian(xn: np.ndarray, mu: np.ndarray, sigma: float) -> float:
    """Log N(xn | mu, sigma^2 I)."""
    diff = xn - mu
    return -0.5 * (D * np.log(2 * np.pi * sigma**2) + np.dot(diff, diff) / sigma**2)


def estep(X: np.ndarray, mu: np.ndarray, sigma: float, pi: np.ndarray) -> np.ndarray:
    """E-step: compute (N, K) responsibility matrix."""
    n_pts = X.shape[0]
    log_g = np.array([
        [np.log(pi[k]) + log_gaussian(X[n], mu[k], sigma) for k in range(K)]
        for n in range(n_pts)
    ])
    log_g -= log_g.max(axis=1, keepdims=True)   # numerical stability
    g = np.exp(log_g)
    return g / g.sum(axis=1, keepdims=True)


def mstep(X: np.ndarray, gamma: np.ndarray) -> np.ndarray:
    """M-step: update means (Sigma and pi fixed for this example)."""
    Nk = gamma.sum(axis=0)            # (K,)
    return (gamma.T @ X) / Nk[:, None]  # (K, D)


def log_likelihood(X: np.ndarray, mu: np.ndarray, sigma: float, pi: np.ndarray) -> float:
    ll = 0.0
    for n in range(N):
        comp_ll = [pi[k] * np.exp(log_gaussian(X[n], mu[k], sigma)) for k in range(K)]
        ll += np.log(sum(comp_ll))
    return ll


# Run 4 EM iterations, store trajectory
mu_traj = [MU_INIT.copy()]
gamma_traj: list[np.ndarray] = []
ll_traj = [log_likelihood(X, MU_INIT, SIGMA, PI)]

for _ in range(4):
    g = estep(X, mu_traj[-1], SIGMA, PI)
    gamma_traj.append(g)
    mu_new = mstep(X, g)
    mu_traj.append(mu_new.copy())
    ll_traj.append(log_likelihood(X, mu_new, SIGMA, PI))

# ── print trajectory so slide values can be verified ──────────────────────────
print("=== EM trajectory ===")
for i, (mu, ll) in enumerate(zip(mu_traj, ll_traj)):
    print(f"  iter {i}: μ₁={mu[0].round(2)}, μ₂={mu[1].round(2)}, μ₃={mu[2].round(2)}, LL={ll:.3f}")

print("\n=== Responsibilities after iter-0 E-step ===")
g0 = gamma_traj[0]
for n in range(N):
    print(f"  x{n+1}={X[n]}: γ={g0[n].round(4)}")

# ─── geometry helpers ─────────────────────────────────────────────────────────

def circle_coords(cx: float, cy: float, r: float = SIGMA, n: int = 60) -> str:
    """pgfplots coordinate string for a circle of radius r centred at (cx,cy)."""
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pts = [(cx + r * np.cos(t), cy + r * np.sin(t)) for t in theta]
    return " ".join(f"({x:.2f},{y:.2f})" for x, y in pts)


def covariance_ellipse(cov: np.ndarray, n_std: float = 1.5, n: int = 100) -> tuple[np.ndarray, np.ndarray]:
    eigvals, eigvecs = np.linalg.eigh(cov)
    theta = np.linspace(0, 2 * np.pi, n)
    circle = np.vstack([np.cos(theta), np.sin(theta)])
    pts = n_std * (eigvecs @ np.diag(np.sqrt(eigvals))) @ circle
    return pts[0], pts[1]


# ─── shared colour definitions ────────────────────────────────────────────────

COLOR_DEFS = r"""
\definecolor{comp1}{RGB}{30,80,160}
\definecolor{comp1bg}{RGB}{173,216,230}
\definecolor{comp2}{RGB}{160,30,30}
\definecolor{comp2bg}{RGB}{240,128,128}
\definecolor{comp3}{RGB}{0,120,60}
\definecolor{comp3bg}{RGB}{144,238,144}
"""

COMP_FG = ["comp1", "comp2", "comp3"]
COMP_BG = ["comp1bg", "comp2bg", "comp3bg"]
MARKERS = ["*", "square*", "triangle*"]


# ─── helper: one pgfplots panel for an EM iteration ──────────────────────────

def em_panel(mu: np.ndarray, iter_num: int, width: str = "4.2cm",
             show_labels: bool = False) -> str:
    """Return a complete tikzpicture for one EM iteration panel."""

    circles = "".join(
        f"  \\addplot[{COMP_FG[k]}, densely dashed, line width=0.8, opacity=0.75]"
        f" coordinates {{ {circle_coords(*mu[k])} }} -- cycle;\n"
        for k in range(K)
    )

    means = "".join(
        f"  \\addplot[only marks, mark=+, mark size=5pt, line width=1.5, {COMP_FG[k]}]"
        f" coordinates {{({mu[k][0]:.2f},{mu[k][1]:.2f})}};\n"
        for k in range(K)
    )

    if show_labels:
        for k in range(K):
            cx, cy = mu[k]
            anchor = "south west" if cy >= 5 else "north west"
            means += (
                f"  \\node[{COMP_FG[k]}, font=\\tiny, anchor={anchor}]"
                f" at (axis cs:{cx:.2f},{cy:.2f}) {{$\\mu_{k+1}$}};\n"
            )

    data_pts = "".join(
        f"  \\addplot[only marks, mark={MARKERS[int(r.comp)-1]}, mark size=2.8pt,"
        f" fill={COMP_BG[int(r.comp)-1]}, draw=black, line width=0.4]"
        f" coordinates {{({r.x1:.1f},{r.x2:.1f})}};\n"
        for r in points_df.itertuples()
    )

    if show_labels:
        for r in points_df.itertuples():
            anchor = "south east" if r.x1 <= 5 else "south west"
            data_pts += (
                f"  \\node[font=\\tiny, anchor={anchor}]"
                f" at (axis cs:{r.x1:.1f},{r.x2:.1f}) {{$x_{{{r.n}}}$}};\n"
            )

    return rf"""
\begin{{tikzpicture}}
\begin{{axis}}[
  width={width}, height={width},
  xmin=-2, xmax=12, ymin=-2, ymax=12,
  title={{\small Iteration {iter_num}}},
  title style={{yshift=-0.4ex}},
  xlabel={{$x^{{(1)}}$}}, ylabel={{$x^{{(2)}}$}},
  xlabel style={{font=\tiny, yshift=0.5ex}},
  ylabel style={{font=\tiny, xshift=0.5ex}},
  tick label style={{font=\tiny}},
  xtick={{0,5,10}}, ytick={{0,5,10}},
  grid=major, grid style={{gray!15}},
]
{circles}{means}{data_pts}
\end{{axis}}
\end{{tikzpicture}}"""


# =============================================================================
# Figure 1: k-Means hard boundary vs GMM soft responsibility
# =============================================================================
# Use 6 working-example points + 1 ambiguous point at (5, 3.5) that is
# approximately equidistant from all three cluster centres.

ambig = np.array([5.0, 3.5])
all_pts_df = pd.concat([
    points_df[["x1","x2","comp"]],
    pd.DataFrame({"x1":[ambig[0]],"x2":[ambig[1]],"comp":[0]}),  # comp=0 = ambiguous
], ignore_index=True)

# k-Means: assign ambiguous point to nearest cluster mean (use post-convergence means)
mu_converged = mu_traj[-1]
dists_ambig = np.array([np.linalg.norm(ambig - mu_converged[k]) for k in range(K)])
kmeans_label = int(np.argmin(dists_ambig))   # 0-indexed

# GMM soft: responsibility of ambiguous point
g_ambig = estep(ambig[None, :], mu_converged, SIGMA, PI)[0]   # (K,)
print(f"\nAmbiguous point (5,3.5) responsibilities: {g_ambig.round(3)}")

# Sector angles for pie in right panel (cumulative, degrees)
angles_deg = np.concatenate([[0], np.cumsum(g_ambig) * 360])
PIE_R = 0.55    # radius of pie glyph in data units


def pie_sector(cx: float, cy: float, a1: float, a2: float, color: str, r: float = PIE_R) -> str:
    """One pie sector in TikZ via addplot fill."""
    theta = np.linspace(np.radians(a1), np.radians(a2), 30)
    pts = [(cx, cy)] + [(cx + r * np.cos(t), cy + r * np.sin(t)) for t in theta]
    coords = " ".join(f"({x:.3f},{y:.3f})" for x, y in pts)
    return (
        f"  \\addplot[fill={color}, draw=black, line width=0.4]"
        f" coordinates {{ {coords} }} -- cycle;\n"
    )


def hard_markers(df: pd.DataFrame) -> str:
    out = ""
    for r in df.itertuples():
        if r.comp == 0:
            # ambiguous point: forced assignment
            k = kmeans_label
            out += (
                f"  \\addplot[only marks, mark={MARKERS[k]}, mark size=3pt,"
                f" fill={COMP_BG[k]}, draw=black, line width=0.5]"
                f" coordinates {{({r.x1},{r.x2})}};\n"
            )
        else:
            k = int(r.comp) - 1
            out += (
                f"  \\addplot[only marks, mark={MARKERS[k]}, mark size=2.8pt,"
                f" fill={COMP_BG[k]}, draw=black, line width=0.4]"
                f" coordinates {{({r.x1},{r.x2})}};\n"
            )
    # forced-label annotation
    out += (
        f"  \\node[font=\\tiny, align=center, text=black] at (axis cs:5,1.8)"
        f" {{forced to\\\\comp. {kmeans_label+1}}};\n"
    )
    return out


def soft_markers(df: pd.DataFrame) -> str:
    out = ""
    for r in df.itertuples():
        if r.comp == 0:
            # pie chart for ambiguous point
            for k in range(K):
                out += pie_sector(r.x1, r.x2, angles_deg[k], angles_deg[k+1], COMP_BG[k])
            out += (
                f"  \\draw[black, line width=0.5] (axis cs:{r.x1},{r.x2})"
                f" circle [radius={PIE_R}];\n"
            )
            out += (
                f"  \\node[font=\\tiny, align=center, text=black] at (axis cs:5,1.8)"
                f" {{soft: {g_ambig[0]:.2f}/{g_ambig[1]:.2f}/{g_ambig[2]:.2f}}};\n"
            )
        else:
            k = int(r.comp) - 1
            out += (
                f"  \\addplot[only marks, mark={MARKERS[k]}, mark size=2.8pt,"
                f" fill={COMP_BG[k]}, draw=black, line width=0.4]"
                f" coordinates {{({r.x1},{r.x2})}};\n"
            )
    return out


AXIS_COMMON = r"""  xmin=-2, xmax=12, ymin=-2, ymax=12,
  width=5.2cm, height=5.2cm,
  xlabel={$x^{(1)}$}, ylabel={$x^{(2)}$},
  xlabel style={font=\small}, ylabel style={font=\small},
  tick label style={font=\tiny},
  xtick={0,5,10}, ytick={0,5,10},
  grid=major, grid style={gray!15},"""

kmeans_limitation_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
"""
    + COLOR_DEFS
    + r"""
\begin{document}
\begin{tabular}{cc}
\textbf{$k$-Means: forced assignment} & \textbf{GMM: soft responsibility} \\[4pt]
\begin{tikzpicture}
\begin{axis}[
"""
    + AXIS_COMMON
    + r"""
  title={\small ambiguous point forced to one cluster},
  title style={font=\footnotesize},
]
"""
    + hard_markers(all_pts_df)
    + r"""
\end{axis}
\end{tikzpicture}
&
\begin{tikzpicture}
\begin{axis}[
"""
    + AXIS_COMMON
    + r"""
  title={\small ambiguous point gets fractional probability},
  title style={font=\footnotesize},
]
"""
    + soft_markers(all_pts_df)
    + r"""
\end{axis}
\end{tikzpicture}
\end{tabular}
\end{document}
"""
)

compile_tikz(kmeans_limitation_tex, "kmeans_limitation")


# =============================================================================
# Figure 2: Initial dataset — 6 points + initial component positions
# =============================================================================

init_panel = em_panel(MU_INIT, iter_num=0, width="6.5cm", show_labels=True)

em_init_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
"""
    + COLOR_DEFS
    + r"""
\begin{document}
"""
    + init_panel
    + r"""
\end{document}
"""
)

compile_tikz(em_init_tex, "em_init")


# =============================================================================
# Figure 3: 2×2 grid of EM at iterations 0, 1, 2, 3
# =============================================================================

panels = [em_panel(mu_traj[i], iter_num=i, width="3.1cm") for i in range(4)]

em_iter_panels_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
"""
    + COLOR_DEFS
    + r"""
\begin{document}
\begin{tabular}{cccc}
"""
    + panels[0]
    + r" & "
    + panels[1]
    + r" & "
    + panels[2]
    + r" & "
    + panels[3]
    + r"""
\end{tabular}
\end{document}
"""
)

compile_tikz(em_iter_panels_tex, "em_iter_panels")


# =============================================================================
# Figure 4: Covariance shapes (spherical / diagonal / full)
# =============================================================================

cov_specs = [
    ("spherical ($\\Sigma=\\sigma^2 I$)", np.array([[1.0, 0.0], [0.0, 1.0]])),
    ("diagonal $\\Sigma$",                np.array([[2.2, 0.0], [0.0, 0.5]])),
    ("full $\\Sigma$ (correlated)",       np.array([[2.0, 1.3], [1.3, 1.2]])),
]


def ellipse_panel(label: str, cov: np.ndarray) -> str:
    ex, ey = covariance_ellipse(cov)
    outline = " -- ".join(f"({x:.3f},{y:.3f})" for x, y in zip(ex, ey))
    return (
        r"""\begin{tikzpicture}
  \draw[-latex, gray] (-3,0) -- (3,0);
  \draw[-latex, gray] (0,-3) -- (0,3);
  \draw[line width=1.6, comp1, fill=comp1bg, fill opacity=0.35] """
        + outline
        + r""" -- cycle;
  \node[font=\small] at (0,-3.5) {"""
        + label
        + r"""};
\end{tikzpicture}"""
    )


cov_panels = [ellipse_panel(lab, cov) for lab, cov in cov_specs]

covariance_shapes_tex = (
    r"""
\documentclass[crop]{standalone}
\usepackage{xcolor}
\usepackage{tikz}
"""
    + COLOR_DEFS
    + r"""
\begin{document}
\begin{tabular}{ccc}
"""
    + cov_panels[0] + r" & " + cov_panels[1] + r" & " + cov_panels[2]
    + r"""
\end{tabular}
\end{document}
"""
)

compile_tikz(covariance_shapes_tex, "covariance_shapes")


# =============================================================================
# Figure 5: Log-likelihood convergence — actual values from the EM run
# =============================================================================

ll_df = pd.DataFrame({"t": np.arange(len(ll_traj)), "ll": ll_traj})
ll_pts = " ".join(f"({r.t},{r.ll:.4f})" for r in ll_df.itertuples())
ymin_plot = ll_traj[0] - 2
ymax_plot = ll_traj[-1] + 2

em_convergence_tex = rf"""
\documentclass[crop]{{standalone}}
\usepackage{{xcolor}}
\usepackage{{pgfplots}}
\pgfplotsset{{compat=1.18}}
\definecolor{{darkgreen}}{{RGB}}{{0,120,60}}
\begin{{document}}
\begin{{tikzpicture}}
  \begin{{axis}}[
    width=10cm, height=4.6cm,
    xlabel={{EM iteration}},
    ylabel={{log-likelihood $\ell(\theta)$}},
    grid=major, grid style={{gray!20}},
    xmin=0, xmax={len(ll_traj)-1},
    ymin={ymin_plot:.1f}, ymax={ymax_plot:.1f},
    xtick={{{",".join(str(i) for i in range(len(ll_traj)))}}},
    tick label style={{font=\small}},
  ]
    \addplot[line width=2, color=darkgreen, mark=*, mark size=2] coordinates {{
{ll_pts}
    }};
    \draw[dashed, gray] (axis cs:0,{ll_traj[-1]:.4f}) -- (axis cs:{len(ll_traj)-1},{ll_traj[-1]:.4f});
    \node[font=\tiny, gray, anchor=west] at (axis cs:0.2,{ll_traj[-1]+0.8:.2f}) {{plateau}};
  \end{{axis}}
\end{{tikzpicture}}
\end{{document}}
"""

compile_tikz(em_convergence_tex, "em_convergence")

print("\n✓ All GMM & EM figures generated.")
