#!/usr/bin/env python3
"""Generate t-SNE lecture figures for ml/lectures/lecture10_tsne.tex"""

from pathlib import Path
import subprocess
import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR  = BASE_DIR / "figures" / "tsne"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def compile_tikz(content: str, name: str) -> None:
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
        print(f"✓ {name}.svg" if svg_result.returncode == 0 else
              f"✗ {name}.svg - conversion failed")
        for ext in [".aux", ".log", ".tex"]:
            (OUT_DIR / f"{name}{ext}").unlink(missing_ok=True)
    else:
        print(f"✗ {name}.pdf - compilation failed")
        print(result.stdout[-1500:] if result.stdout else "")


# ─── Shared dataset: 3 concentric rings ─────────────────────────────────────
np.random.seed(42)
N_PER = 25

ring_dfs = []
for cls, radius in enumerate([1.5, 3.5, 5.5]):
    angles = np.linspace(0, 2 * np.pi, N_PER, endpoint=False)
    angles += np.random.randn(N_PER) * 0.12
    x = radius * np.cos(angles) + np.random.randn(N_PER) * 0.22
    y = radius * np.sin(angles) + np.random.randn(N_PER) * 0.22
    ring_dfs.append(pd.DataFrame({"x": x, "y": y, "label": cls}))

df_rings = pd.concat(ring_dfs, ignore_index=True)
X_2d    = df_rings[["x", "y"]].values

# Embed in 8D via random linear map + noise — hides the ring structure
np.random.seed(7)
W      = np.random.randn(2, 8)
X_high = X_2d @ W + np.random.randn(len(df_rings), 8) * 0.6
labels = df_rings["label"].values

# Palette (draw, fill)
COLORS = [
    ("blue!80!black",  "blue!35"),
    ("red!80!black",   "red!30"),
    ("green!60!black", "green!35"),
]

def scatter_addplots(df, xcol, ycol, mark_size="1.4pt"):
    """Return pgfplots \addplot blocks for each class."""
    blocks = ""
    for cls, (draw, fill) in enumerate(COLORS):
        sub  = df[df["label"] == cls]
        pts  = " ".join(f"({r[xcol]:.3f},{r[ycol]:.3f})" for _, r in sub.iterrows())
        blocks += (
            f"  \\addplot[only marks, mark=*, mark size={mark_size},\n"
            f"           draw={draw}, fill={fill}]\n"
            f"    coordinates {{ {pts} }};\n"
        )
    return blocks


# ─── Figure 1: PCA vs t-SNE ──────────────────────────────────────────────────
print("Running PCA and t-SNE …")
pca    = PCA(n_components=2)
X_pca  = pca.fit_transform(X_high)
df_rings["pca1"] = X_pca[:, 0]
df_rings["pca2"] = X_pca[:, 1]

tsne_main = TSNE(n_components=2, perplexity=10, random_state=42, max_iter=1000,
                 init="pca", learning_rate="auto")
X_tsne = tsne_main.fit_transform(X_high)
df_rings["t1"] = X_tsne[:, 0]
df_rings["t2"] = X_tsne[:, 1]

print("PCA class ranges on PC1:")
for c in range(3):
    sub = df_rings[df_rings["label"] == c]
    print(f"  Ring {c}: PC1 [{sub.pca1.min():.2f}, {sub.pca1.max():.2f}]")

p1lo, p1hi = df_rings.pca1.min() - 1, df_rings.pca1.max() + 1
p2lo, p2hi = df_rings.pca2.min() - 1, df_rings.pca2.max() + 1
t1lo, t1hi = df_rings.t1.min() - 5, df_rings.t1.max() + 5
t2lo, t2hi = df_rings.t2.min() - 5, df_rings.t2.max() + 5

pca_plots  = scatter_addplots(df_rings, "pca1", "pca2")
tsne_plots = scatter_addplots(df_rings, "t1",   "t2")

tex = (
    r"""\documentclass[crop]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
\begin{tikzpicture}
  \begin{axis}[
    name=axPCA,
    width=5.8cm, height=5.8cm,
    title={\small\textbf{PCA} (linear projection)},
    xlabel={\small PC 1},
    ylabel={\small PC 2},
    tick label style={font=\tiny},
    label style={font=\small},
    title style={font=\small},
    grid=both, grid style={dotted,gray!35},
    xmin="""
    + f"{p1lo:.1f}, xmax={p1hi:.1f},"
    + r"""
    ymin="""
    + f"{p2lo:.1f}, ymax={p2hi:.1f},"
    + r"""
    enlargelimits=false,
  ]
"""
    + pca_plots
    + r"""  \end{axis}
  \begin{axis}[
    name=axTSNE,
    at={(axPCA.east)}, anchor=west, xshift=1.0cm,
    width=5.8cm, height=5.8cm,
    title={\small\textbf{t-SNE} (non-linear embedding)},
    xlabel={\small Dimension 1},
    ylabel={\small Dimension 2},
    tick label style={font=\tiny},
    label style={font=\small},
    title style={font=\small},
    grid=both, grid style={dotted,gray!35},
    xmin="""
    + f"{t1lo:.1f}, xmax={t1hi:.1f},"
    + r"""
    ymin="""
    + f"{t2lo:.1f}, ymax={t2hi:.1f},"
    + r"""
    enlargelimits=false,
  ]
"""
    + tsne_plots
    + r"""  \end{axis}
\end{tikzpicture}
\end{document}
"""
)
compile_tikz(tex, "tsne_pca_comparison")


# ─── Figure 2: Gaussian vs Student-t kernel curves ───────────────────────────
d     = np.linspace(0, 4.0, 300)
df_k  = pd.DataFrame({
    "d":        d,
    "gaussian": np.exp(-d**2),
    "student":  1.0 / (1.0 + d**2),
})

gauss_pts   = " ".join(f"({r.d:.4f},{r.gaussian:.5f})" for _, r in df_k.iterrows())
student_pts = " ".join(f"({r.d:.4f},{r.student:.5f})"  for _, r in df_k.iterrows())

tex = (
    r"""\documentclass[crop]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
\begin{tikzpicture}
  \begin{axis}[
    width=8cm, height=5.5cm,
    xlabel={\small Distance $d = \|y_i - y_j\|$},
    ylabel={\small Similarity},
    tick label style={font=\small},
    label style={font=\small},
    xmin=0, xmax=4, ymin=0, ymax=1.05,
    grid=both, grid style={dotted,gray!35},
    legend style={font=\small, at={(0.97,0.97)}, anchor=north east},
    legend cell align=left,
  ]
  \addplot[thick, blue!70!black] coordinates { """
    + gauss_pts
    + r""" };
  \addlegendentry{Gaussian $e^{-d^2}$ (used for $P$)}
  \addplot[thick, red!70!black, dashed] coordinates { """
    + student_pts
    + r""" };
  \addlegendentry{Student-t $(1+d^2)^{-1}$ (used for $Q$)}
  \end{axis}
\end{tikzpicture}
\end{document}
"""
)
compile_tikz(tex, "tsne_similarity_kernels")


# ─── Figure 3: Crowding schematic ────────────────────────────────────────────
# 6 equidistant points on a unit circle — compute coordinates
n_pts   = 6
angles  = np.linspace(0, 2 * np.pi, n_pts, endpoint=False)
circ_df = pd.DataFrame({
    "cx": np.cos(angles),
    "cy": np.sin(angles),
    "label": np.arange(n_pts) % 3,  # 3 colours cycling
})
# The 1D projection onto the x-axis
circ_df["proj"] = circ_df["cx"]

# Build TikZ node positions (scaled up for readability)
R = 1.6  # drawing radius
nodes_2d = ""
for _, row in circ_df.iterrows():
    col = COLORS[int(row.label)][0]
    fill = COLORS[int(row.label)][1]
    cx, cy = row.cx * R, row.cy * R
    nodes_2d += (
        f"  \\node[circle, draw={col}, fill={fill}, "
        f"inner sep=2.2pt] at ({cx:.3f},{cy:.3f}) {{}};\n"
        f"  \\draw[{col}!50, thin] ({cx:.3f},{cy:.3f}) circle (0.38cm);\n"
    )

# 1D projection (y = -3.5): each point at x = proj * R, with overlap circles
nodes_1d = ""
for _, row in circ_df.iterrows():
    col  = COLORS[int(row.label)][0]
    fill = COLORS[int(row.label)][1]
    px   = row.proj * R
    nodes_1d += (
        f"  \\node[circle, draw={col}, fill={fill}, "
        f"inner sep=2.2pt] at ({px:.3f},-3.5) {{}};\n"
        f"  \\draw[{col}!50, thin] ({px:.3f},-3.5) circle (0.38cm);\n"
    )

tex = (
    r"""\documentclass[crop]{standalone}
\usepackage{tikz}
\usetikzlibrary{arrows.meta}
\begin{document}
\begin{tikzpicture}[>=Stealth]
  % 2D circle of points
  \draw[gray!40, dashed] (0,0) circle (1.6cm);
  \node[font=\small] at (0, 2.2) {\textbf{2D}: 6 neighbours, each with personal space};
"""
    + nodes_2d
    + r"""
  % Arrow
  \draw[->, thick, gray!70] (0,-1.9) -- (0,-2.8)
    node[midway, right, font=\small, text=gray!80] {fit in 1D};
  % 1D line
  \draw[gray!60, thick] (-2.0,-3.5) -- (2.0,-3.5);
  \node[font=\small] at (0, -4.15) {\textbf{1D}: same neighbours — personal spaces \textbf{overlap}};
"""
    + nodes_1d
    + r"""\end{tikzpicture}
\end{document}
"""
)
compile_tikz(tex, "tsne_crowding")


# ─── Figure 4: Perplexity comparison ─────────────────────────────────────────
print("Running t-SNE for perplexity comparison …")
perplexities = [3, 15, 45]
tsne_embeds  = {}
for perp in perplexities:
    tsne_p = TSNE(n_components=2, perplexity=perp, random_state=42,
                  max_iter=1000, init="pca", learning_rate="auto")
    emb = tsne_p.fit_transform(X_high)
    tsne_embeds[perp] = emb
    print(f"  perplexity={perp} → KL={tsne_p.kl_divergence_:.3f}")

# Build per-perplexity dataframes
panel_tex = ""
for idx, perp in enumerate(perplexities):
    emb = tsne_embeds[perp]
    dfp = df_rings.copy()
    dfp["e1"] = emb[:, 0]
    dfp["e2"] = emb[:, 1]
    plots = scatter_addplots(dfp, "e1", "e2", mark_size="1.2pt")
    e1lo = emb[:, 0].min() - 5
    e1hi = emb[:, 0].max() + 5
    e2lo = emb[:, 1].min() - 5
    e2hi = emb[:, 1].max() + 5

    anchor = "" if idx == 0 else (
        f"    at={{(ax{perplexities[idx-1]}.east)}}, anchor=west, xshift=0.6cm,\n"
    )
    label = ("too local" if perp == 3 else
             "\\textbf{good}" if perp == 15 else "too global")
    panel_tex += (
        f"  \\begin{{axis}}[\n"
        f"    name=ax{perp},\n"
        + anchor
        + f"    width=4.2cm, height=4.2cm,\n"
        f"    title={{\\small perplexity $= {perp}$ ({label})}},\n"
        f"    title style={{font=\\small}},\n"
        f"    tick label style={{font=\\tiny}},\n"
        f"    xticklabels={{}}, yticklabels={{}},\n"
        f"    xmin={e1lo:.1f}, xmax={e1hi:.1f},\n"
        f"    ymin={e2lo:.1f}, ymax={e2hi:.1f},\n"
        f"    enlargelimits=false,\n"
        f"  ]\n"
        + plots
        + f"  \\end{{axis}}\n"
    )

tex = (
    r"""\documentclass[crop]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
\begin{tikzpicture}
"""
    + panel_tex
    + r"""\end{tikzpicture}
\end{document}
"""
)
compile_tikz(tex, "tsne_perplexity")


# ─── Figure 5: KL divergence convergence ─────────────────────────────────────
print("Running t-SNE convergence tracking …")
max_iter_vals = [300, 400, 500, 650, 800, 1000]
kl_rows     = []
X_cv        = X_high[:20]   # 20 points — fast to run many times

for n in max_iter_vals:
    t = TSNE(n_components=2, perplexity=5, max_iter=n, random_state=42,
             init="pca", learning_rate="auto")
    t.fit_transform(X_cv)
    kl_rows.append({"iter": n, "kl": t.kl_divergence_})

df_kl  = pd.DataFrame(kl_rows)
df_kl  = df_kl[np.isfinite(df_kl["kl"])].reset_index(drop=True)
kl_pts = " ".join(f"({r.iter:.0f},{r.kl:.4f})" for _, r in df_kl.iterrows())

print("KL trajectory:")
print(df_kl.to_string(index=False))

tex = (
    r"""\documentclass[crop]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
\begin{tikzpicture}
  \begin{axis}[
    width=8.5cm, height=5.5cm,
    xlabel={\small Iteration},
    ylabel={\small KL Divergence $D_{\mathrm{KL}}(P \| Q)$},
    tick label style={font=\small},
    label style={font=\small},
    grid=both, grid style={dotted,gray!35},
    xmin=0, xmax=1050,
    ymin=0,
  ]
  \addplot[thick, blue!70!black, mark=*, mark size=1.8pt] coordinates { """
    + kl_pts
    + r""" };
  \end{axis}
\end{tikzpicture}
\end{document}
"""
)
compile_tikz(tex, "tsne_convergence")

print("\nAll done.")
