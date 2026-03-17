#!/usr/bin/env python3
"""Generate vector k-NN teaching graphics as PDF files.

The script uses NumPy to generate deterministic sample data, writes TikZ/PGFPlots
sources, and compiles them with pdflatex into vector PDFs.

Outputs (PDF):
  - figures/knn/knn_classification_k_effect.pdf
  - figures/knn/knn_regression_k_effect.pdf
  - figures/knn/knn_scaling_effect.pdf
  - figures/knn/knn_validation_curve.pdf
  - figures/knn/knn_distance_concentration.pdf
  - figures/knn/knn_indexing_tradeoff.pdf
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "knn"


@dataclass
class ClassificationPanel:
    k: int
    neighbor_idx: np.ndarray
    pred_label: int
    radius: float


@dataclass
class RegressionPanel:
    k: int
    y_pred: np.ndarray


@dataclass
class ScalingPanel:
    title: str
    data: np.ndarray
    query: np.ndarray
    neighbor_idx: np.ndarray


def _coords(points: np.ndarray) -> str:
    return " ".join(f"({p[0]:.5f},{p[1]:.5f})" for p in points)


def _series(x: np.ndarray, y: np.ndarray) -> str:
    return " ".join(f"({xi:.5f},{yi:.5f})" for xi, yi in zip(x, y))


def _nearest_indices(data: np.ndarray, q: np.ndarray, k: int) -> np.ndarray:
    d2 = np.sum((data - q[None, :]) ** 2, axis=1)
    return np.argsort(d2)[:k]


def _knn_regress(train_x: np.ndarray, train_y: np.ndarray, query_x: np.ndarray, k: int) -> np.ndarray:
    d2 = (query_x[:, None] - train_x[None, :]) ** 2
    idx = np.argpartition(d2, kth=k - 1, axis=1)[:, :k]
    return np.mean(train_y[idx], axis=1)


def _knn_classify(train_x: np.ndarray, train_y: np.ndarray, query_x: np.ndarray, k: int) -> np.ndarray:
    d2 = np.sum((query_x[:, None, :] - train_x[None, :, :]) ** 2, axis=2)
    idx = np.argpartition(d2, kth=k - 1, axis=1)[:, :k]
    return (np.mean(train_y[idx], axis=1) >= 0.5).astype(np.int32)


def build_classification_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, list[ClassificationPanel]]:
    rng = np.random.default_rng(7)
    n = 28
    c0 = rng.normal(loc=(-1.3, -1.0), scale=(0.72, 0.72), size=(n, 2))
    c1 = rng.normal(loc=(1.3, 1.0), scale=(0.72, 0.72), size=(n, 2))
    train_x = np.vstack([c0, c1])
    train_y = np.array([0] * n + [1] * n, dtype=np.int32)

    query = np.array([0.25, 0.05])
    ks = [1, 5, 15]
    panels: list[ClassificationPanel] = []

    d2 = np.sum((train_x - query[None, :]) ** 2, axis=1)
    order = np.argsort(d2)

    for k in ks:
        idx = order[:k]
        pred = int(np.mean(train_y[idx]) >= 0.5)
        radius = float(np.sqrt(d2[order[k - 1]]))
        panels.append(ClassificationPanel(k=k, neighbor_idx=idx, pred_label=pred, radius=radius))

    return train_x, train_y, query, panels


def write_classification_tex(path: Path) -> None:
    train_x, train_y, query, panels = build_classification_data()

    class0 = train_x[train_y == 0]
    class1 = train_x[train_y == 1]

    panel_blocks: list[str] = []
    for panel in panels:
        neigh = train_x[panel.neighbor_idx]
        query_color = "red!75!black" if panel.pred_label == 1 else "blue!75!black"
        block = f"""
\\nextgroupplot[
  title={{k={panel.k}}},
  xmin=-3.5,xmax=3.5,
  ymin=-3.2,ymax=3.2,
  axis lines=left,
  xlabel={{Feature 1}}, ylabel={{Feature 2}},
  tick style={{draw=none}},
  xtick=\\empty, ytick=\\empty,
  width=0.32\\textwidth,
  height=0.28\\textwidth,
  clip=false,
]
\\addplot[only marks, mark=*, mark size=0.85pt, draw=blue!70!black, fill=blue!70!black, opacity=0.78] coordinates {{{_coords(class0)}}};
\\addplot[only marks, mark=*, mark size=0.85pt, draw=red!70!black, fill=red!70!black, opacity=0.78] coordinates {{{_coords(class1)}}};
\\addplot[only marks, mark=diamond*, mark size=1.9pt, draw=black, fill=yellow!85!black] coordinates {{{_coords(neigh)}}};
\\addplot[only marks, mark=star, mark size=2.4pt, draw={query_color}, fill={query_color}] coordinates {{({query[0]:.5f},{query[1]:.5f})}};
\\node[anchor=south east, font=\\scriptsize] at (rel axis cs:0.98,1.02) {{Predicted class: {panel.pred_label}}};
"""
        panel_blocks.append(block)

    tex = f"""\\documentclass[tikz,border=2pt]{{standalone}}
\\usepackage{{pgfplots}}
\\usepgfplotslibrary{{groupplots}}
\\pgfplotsset{{compat=1.18}}

\\begin{{document}}
\\begin{{tikzpicture}}
\\begin{{groupplot}}[
  group style={{group size=3 by 1, horizontal sep=1.2cm}},
]
{''.join(panel_blocks)}
\\end{{groupplot}}
\\end{{tikzpicture}}
\\end{{document}}
"""
    path.write_text(tex, encoding="utf-8")


def build_regression_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[RegressionPanel]]:
    rng = np.random.default_rng(19)
    train_x = np.sort(rng.random(44))
    train_y = np.sin(2 * np.pi * train_x) + rng.normal(0.0, 0.18, size=train_x.shape[0])

    xd = np.linspace(0.0, 1.0, 240)
    y_true = np.sin(2 * np.pi * xd)

    panels = []
    for k in [1, 5, 15]:
        panels.append(RegressionPanel(k=k, y_pred=_knn_regress(train_x, train_y, xd, k)))

    return train_x, train_y, xd, y_true, panels


def write_regression_tex(path: Path) -> None:
    train_x, train_y, xd, y_true, panels = build_regression_data()

    panel_blocks: list[str] = []
    for panel in panels:
        block = f"""
\\nextgroupplot[
  title={{k={panel.k}}},
  xmin=0,xmax=1,
  ymin=-1.6,ymax=1.6,
  axis lines=left,
  xlabel={{x}}, ylabel={{y}},
  width=0.32\\textwidth,
  height=0.28\\textwidth,
  tick style={{draw=none}},
]
\\addplot[draw=black!55, densely dashed, line width=0.7pt] coordinates {{{_series(xd, y_true)}}};
\\addplot[draw=blue!75!black, line width=0.95pt] coordinates {{{_series(xd, panel.y_pred)}}};
\\addplot[only marks, mark=*, mark size=0.95pt, draw=black, fill=black] coordinates {{{_series(train_x, train_y)}}};
"""
        panel_blocks.append(block)

    tex = f"""\\documentclass[tikz,border=2pt]{{standalone}}
\\usepackage{{pgfplots}}
\\usepgfplotslibrary{{groupplots}}
\\pgfplotsset{{compat=1.18}}

\\begin{{document}}
\\begin{{tikzpicture}}
\\begin{{groupplot}}[
  group style={{group size=3 by 1, horizontal sep=1.2cm}},
]
{''.join(panel_blocks)}
\\end{{groupplot}}
\\end{{tikzpicture}}
\\end{{document}}
"""
    path.write_text(tex, encoding="utf-8")


def build_scaling_data() -> tuple[ScalingPanel, ScalingPanel]:
    rng = np.random.default_rng(23)
    n = 65

    f1 = rng.normal(0.5, 0.22, size=n)
    f2 = rng.normal(500.0, 170.0, size=n)
    raw = np.column_stack([f1, f2])
    query_raw = np.array([0.82, 420.0])

    k = 6
    raw_idx = _nearest_indices(raw, query_raw, k)

    mu = raw.mean(axis=0)
    sd = raw.std(axis=0) + 1e-8
    z = (raw - mu) / sd
    query_z = (query_raw - mu) / sd
    z_idx = _nearest_indices(z, query_z, k)

    panel_raw = ScalingPanel(
        title="Without scaling",
        data=raw,
        query=query_raw,
        neighbor_idx=raw_idx,
    )
    panel_z = ScalingPanel(
        title="After standardization",
        data=z,
        query=query_z,
        neighbor_idx=z_idx,
    )
    return panel_raw, panel_z


def write_scaling_tex(path: Path) -> None:
    panel_raw, panel_z = build_scaling_data()

    blocks: list[str] = []
    for idx, panel in enumerate([panel_raw, panel_z]):
        x = panel.data[:, 0]
        y = panel.data[:, 1]
        nbr = panel.data[panel.neighbor_idx]
        xmin = float(np.min(x) - 0.1 * (np.max(x) - np.min(x) + 1e-8))
        xmax = float(np.max(x) + 0.1 * (np.max(x) - np.min(x) + 1e-8))
        ymin = float(np.min(y) - 0.1 * (np.max(y) - np.min(y) + 1e-8))
        ymax = float(np.max(y) + 0.1 * (np.max(y) - np.min(y) + 1e-8))

        xlabel = "Feature 1" if idx == 0 else "Feature 1 (z-score)"
        ylabel = "Feature 2" if idx == 0 else "Feature 2 (z-score)"

        block = f"""
\\nextgroupplot[
  title={{{panel.title}}},
  xmin={xmin:.5f},xmax={xmax:.5f},
  ymin={ymin:.5f},ymax={ymax:.5f},
  axis lines=left,
  xlabel={{{xlabel}}}, ylabel={{{ylabel}}},
  width=0.47\\textwidth,
  height=0.33\\textwidth,
  tick style={{draw=none}},
]
\\addplot[only marks, mark=*, mark size=1.0pt, draw=black!55, fill=black!55] coordinates {{{_coords(panel.data)}}};
\\addplot[only marks, mark=o, mark size=2.9pt, draw=blue!80!black, fill=none, line width=0.7pt] coordinates {{{_coords(nbr)}}};
\\addplot[only marks, mark=star, mark size=2.7pt, draw=red!75!black, fill=red!75!black] coordinates {{({panel.query[0]:.5f},{panel.query[1]:.5f})}};
"""
        blocks.append(block)

    tex = f"""\\documentclass[tikz,border=2pt]{{standalone}}
\\usepackage{{pgfplots}}
\\usepgfplotslibrary{{groupplots}}
\\pgfplotsset{{compat=1.18}}

\\begin{{document}}
\\begin{{tikzpicture}}
\\begin{{groupplot}}[
  group style={{group size=2 by 1, horizontal sep=1.5cm}},
]
{''.join(blocks)}
\\end{{groupplot}}
\\end{{tikzpicture}}
\\end{{document}}
"""
    path.write_text(tex, encoding="utf-8")


def build_validation_curve_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    rng = np.random.default_rng(31)
    n_train = 180
    n_val = 160

    c0_train = rng.normal(loc=(-1.2, -0.9), scale=(0.9, 0.9), size=(n_train // 2, 2))
    c1_train = rng.normal(loc=(1.1, 1.0), scale=(0.9, 0.9), size=(n_train // 2, 2))
    x_train = np.vstack([c0_train, c1_train])
    y_train = np.array([0] * (n_train // 2) + [1] * (n_train // 2), dtype=np.int32)

    c0_val = rng.normal(loc=(-1.2, -0.9), scale=(0.95, 0.95), size=(n_val // 2, 2))
    c1_val = rng.normal(loc=(1.1, 1.0), scale=(0.95, 0.95), size=(n_val // 2, 2))
    x_val = np.vstack([c0_val, c1_val])
    y_val = np.array([0] * (n_val // 2) + [1] * (n_val // 2), dtype=np.int32)

    ks = np.arange(1, 32, 2)
    train_err = np.zeros_like(ks, dtype=np.float64)
    val_err = np.zeros_like(ks, dtype=np.float64)

    for i, k in enumerate(ks):
        pred_train = _knn_classify(x_train, y_train, x_train, int(k))
        pred_val = _knn_classify(x_train, y_train, x_val, int(k))
        train_err[i] = np.mean(pred_train != y_train)
        val_err[i] = np.mean(pred_val != y_val)

    best_idx = int(np.argmin(val_err))
    best_k = int(ks[best_idx])
    return ks, train_err, val_err, best_k


def write_validation_curve_tex(path: Path) -> None:
    ks, train_err, val_err, best_k = build_validation_curve_data()
    train_coords = _series(ks.astype(np.float64), train_err)
    val_coords = _series(ks.astype(np.float64), val_err)
    best_y = float(val_err[np.where(ks == best_k)[0][0]])

    tex = f"""\\documentclass[tikz,border=2pt]{{standalone}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}

\\begin{{document}}
\\begin{{tikzpicture}}
\\begin{{axis}}[
  width=0.94\\textwidth,
  height=0.52\\textwidth,
  xlabel={{k (number of neighbors)}},
  ylabel={{Error rate}},
  xmin=1, xmax=31,
  ymin=0, ymax=0.35,
  legend style={{at={{(0.98,0.98)}},anchor=north east,draw=none,fill=none,font=\\footnotesize}},
  grid=major,
  major grid style={{draw=black!8}},
]
\\addplot[draw=blue!75!black, line width=1.1pt, mark=*, mark size=1.5pt] coordinates {{{train_coords}}};
\\addlegendentry{{Training error}}
\\addplot[draw=red!75!black, line width=1.1pt, mark=square*, mark size=1.4pt] coordinates {{{val_coords}}};
\\addlegendentry{{Validation error}}
\\addplot[draw=black!70, densely dashed, line width=0.8pt] coordinates {{({best_k},0) ({best_k},0.35)}};
\\node[anchor=south west, font=\\scriptsize] at (axis cs:{best_k},{best_y:.5f}) {{best k={best_k}}};
\\end{{axis}}
\\end{{tikzpicture}}
\\end{{document}}
"""
    path.write_text(tex, encoding="utf-8")


def build_distance_concentration_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(73)
    dims = np.array([2, 5, 10, 20, 40, 80, 120, 200, 400], dtype=np.int32)
    nearest_farthest = np.zeros_like(dims, dtype=np.float64)
    contrast = np.zeros_like(dims, dtype=np.float64)

    n_points = 450
    repeats = 12
    for i, d in enumerate(dims):
        ratios = []
        contrasts = []
        for _ in range(repeats):
            pts = rng.normal(0.0, 1.0, size=(n_points, int(d)))
            q = rng.normal(0.0, 1.0, size=(int(d),))
            dist = np.sqrt(np.sum((pts - q[None, :]) ** 2, axis=1))
            dmin = float(np.min(dist))
            dmax = float(np.max(dist))
            ratios.append(dmin / (dmax + 1e-12))
            contrasts.append((dmax - dmin) / (dmin + 1e-12))
        nearest_farthest[i] = float(np.mean(ratios))
        contrast[i] = float(np.mean(contrasts))

    return dims.astype(np.float64), nearest_farthest, contrast


def write_distance_concentration_tex(path: Path) -> None:
    dims, ratio, contrast = build_distance_concentration_data()
    ratio_coords = _series(dims, ratio)
    contrast_coords = _series(dims, contrast)

    tex = f"""\\documentclass[tikz,border=2pt]{{standalone}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}

\\begin{{document}}
\\begin{{tikzpicture}}
\\begin{{axis}}[
  width=0.94\\textwidth,
  height=0.52\\textwidth,
  xlabel={{Dimension d}},
  ylabel={{Value}},
  xmin=0, xmax=410,
  ymin=0, ymax=2.8,
  legend style={{at={{(0.98,0.98)}},anchor=north east,draw=none,fill=none,font=\\footnotesize}},
  grid=major,
  major grid style={{draw=black!8}},
]
\\addplot[draw=blue!75!black, line width=1.1pt, mark=*, mark size=1.6pt] coordinates {{{ratio_coords}}};
\\addlegendentry{{$d_{{min}}/d_{{max}}$ (higher means less contrast)}}
\\addplot[draw=orange!85!black, line width=1.1pt, mark=triangle*, mark size=1.7pt] coordinates {{{contrast_coords}}};
\\addlegendentry{{$(d_{{max}}-d_{{min}})/d_{{min}}$}}
\\end{{axis}}
\\end{{tikzpicture}}
\\end{{document}}
"""
    path.write_text(tex, encoding="utf-8")


def build_indexing_tradeoff_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = np.array([1_000, 3_000, 10_000, 30_000, 100_000, 300_000, 1_000_000], dtype=np.float64)
    brute = n
    kd_tree = 45.0 * np.log2(n)
    ann = 250.0 + 10.0 * np.log2(n)
    return n, brute, kd_tree, ann


def write_indexing_tradeoff_tex(path: Path) -> None:
    n, brute, kd_tree, ann = build_indexing_tradeoff_data()
    brute_coords = _series(n, brute)
    kd_coords = _series(n, kd_tree)
    ann_coords = _series(n, ann)

    tex = f"""\\documentclass[tikz,border=2pt]{{standalone}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}

\\begin{{document}}
\\begin{{tikzpicture}}
\\begin{{axis}}[
  width=0.94\\textwidth,
  height=0.54\\textwidth,
  xmode=log,
  ymode=log,
  xlabel={{Dataset size $n$}},
  ylabel={{Candidate comparisons per query (illustrative)}},
  xmin=900, xmax=1200000,
  ymin=120, ymax=1500000,
  legend style={{at={{(0.02,0.98)}},anchor=north west,draw=none,fill=none,font=\\footnotesize}},
  grid=major,
  major grid style={{draw=black!8}},
]
\\addplot[draw=red!75!black, line width=1.1pt, mark=square*, mark size=1.5pt] coordinates {{{brute_coords}}};
\\addlegendentry{{Brute-force}}
\\addplot[draw=blue!75!black, line width=1.1pt, mark=*, mark size=1.5pt] coordinates {{{kd_coords}}};
\\addlegendentry{{KD/Ball-tree (idealized)}}
\\addplot[draw=green!55!black, line width=1.1pt, mark=triangle*, mark size=1.7pt] coordinates {{{ann_coords}}};
\\addlegendentry{{ANN search}}
\\end{{axis}}
\\end{{tikzpicture}}
\\end{{document}}
"""
    path.write_text(tex, encoding="utf-8")


def _compile_tex(tex_path: Path) -> None:
    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        tex_path.name,
    ]
    result = subprocess.run(
        cmd,
        cwd=tex_path.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to compile {tex_path.name}\n"
            f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    class_tex = OUT_DIR / "knn_classification_k_effect.tex"
    reg_tex = OUT_DIR / "knn_regression_k_effect.tex"
    scale_tex = OUT_DIR / "knn_scaling_effect.tex"
    val_curve_tex = OUT_DIR / "knn_validation_curve.tex"
    dist_conc_tex = OUT_DIR / "knn_distance_concentration.tex"
    index_tradeoff_tex = OUT_DIR / "knn_indexing_tradeoff.tex"

    write_classification_tex(class_tex)
    write_regression_tex(reg_tex)
    write_scaling_tex(scale_tex)
    write_validation_curve_tex(val_curve_tex)
    write_distance_concentration_tex(dist_conc_tex)
    write_indexing_tradeoff_tex(index_tradeoff_tex)

    _compile_tex(class_tex)
    _compile_tex(reg_tex)
    _compile_tex(scale_tex)
    _compile_tex(val_curve_tex)
    _compile_tex(dist_conc_tex)
    _compile_tex(index_tradeoff_tex)

    print(f"Saved vector k-NN graphics to: {OUT_DIR}")


if __name__ == "__main__":
    main()
