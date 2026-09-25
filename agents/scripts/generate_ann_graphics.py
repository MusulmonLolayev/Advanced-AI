#!/usr/bin/env python3
"""Generate lecture figures for agents/ Lecture 7 (lecture07_*.tex)

Numbers come from numpy/scikit-learn; rendering is matplotlib, saved directly
as vector PDF (and SVG) -- see the pandas-vector-graphics skill.

Both charts here are MEASURED, not sketched:

  * the scale wall is timed on this machine with real float32 matrix-vector
    products at three corpus sizes;
  * the recall curves come from an actual IVF index (k-means cells) and an
    actual product-quantization codebook (8-bit k-means per subspace), both
    scored against exhaustive ground truth.

The underlying vectors are synthetic clustered Gaussians, not a public
benchmark, so the slides label them as such. The SHAPE of the trade-off is the
teaching point; the absolute recall of any one index on real embeddings will
differ. Schematic diagrams (IVF cells, the PQ subspace split, HNSW layers) are
inline TikZ in the .tex files instead.
"""

from pathlib import Path
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "ann"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand palette (see agents/theme/rl-theme.tex: RLBlue, RLGreen, RLOrange).
RLBLUE = "#3A35B7"
RLGREEN = "#5FA0A4"
RLORANGE = "#F4BD70"
RLRED = "#D6455D"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#222222",
    "text.color": "#222222",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
})


def save_fig(fig, name):
    pdf_path = OUT_DIR / f"{name}.pdf"
    svg_path = OUT_DIR / f"{name}.svg"
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    fig.savefig(svg_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"✓ {name}.pdf")
    print(f"✓ {name}.svg")


rng = np.random.default_rng(7)

# ─── Figure 1: the scale wall — measured exact-search latency ──────────────
print("Figure 1: measured brute-force latency …")
D_EMB = 1024                      # BGE-M3 embedding dimension
SIZES = [7_368, 100_000, 1_000_000]
LABELS = ["7,368\n(this corpus)", "100,000", "1,000,000"]
latency_ms = []
for n in SIZES:
    vecs = rng.standard_normal((n, D_EMB), dtype=np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    query = vecs[0].copy()
    timings = []
    for _ in range(5):
        t0 = time.perf_counter()
        scores = vecs @ query
        np.argpartition(-scores, 10)[:10]
        timings.append(time.perf_counter() - t0)
    ms = float(np.median(timings)) * 1000
    latency_ms.append(ms)
    print(f"  N={n:>9,}  {ms:8.2f} ms/query   store={vecs.nbytes / 1e9:.3f} GB")
    del vecs

fig, ax = plt.subplots(figsize=(4.2, 2.9))
xs = np.arange(len(SIZES))
bars = ax.bar(xs, latency_ms, width=0.55, color=[RLGREEN, RLORANGE, RLRED],
              edgecolor="white", linewidth=0.6)
ax.axhline(10, color=RLBLUE, linestyle="--", linewidth=1.4)
ax.text(0.03, 0.40, "10 ms budget", transform=ax.transAxes,
        fontsize=8.5, color=RLBLUE, ha="left", va="bottom")
ax.set_yscale("log")
ax.set_xticks(xs)
ax.set_xticklabels(LABELS, fontsize=9)
ax.set_ylabel("ms per query (log)", fontsize=10)
ax.tick_params(labelsize=9)
for x, ms in zip(xs, latency_ms):
    ax.annotate(f"{ms:.1f} ms", xy=(x, ms * 1.25), ha="center", fontsize=9)
ax.set_ylim(0.5, max(latency_ms) * 6)
ax.grid(True, axis="y", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "ann_scale_wall")


# ─── Figures 2: measured recall/work trade-off for IVF and PQ ──────────────
print("\nFigure 2: measured IVF and PQ recall …")
N, D, N_CLUST, N_QUERY, K = 20_000, 128, 60, 300, 10

centers = rng.standard_normal((N_CLUST, D)).astype(np.float32) * 1.1
X = centers[rng.integers(0, N_CLUST, N)] + rng.standard_normal((N, D)).astype(np.float32)
X /= np.linalg.norm(X, axis=1, keepdims=True)
Q = X[rng.choice(N, N_QUERY, replace=False)] + 0.6 * rng.standard_normal(
    (N_QUERY, D)).astype(np.float32)
Q /= np.linalg.norm(Q, axis=1, keepdims=True)

sims = Q @ X.T
exact = np.argpartition(-sims, K, axis=1)[:, :K]
exact = [set(row[np.argsort(-sims[i, row])].tolist()) for i, row in enumerate(exact)]

# --- IVF: k-means cells, probe the nprobe nearest ---
NLIST = 141                                      # ~sqrt(N)
km = KMeans(n_clusters=NLIST, n_init=3, random_state=0).fit(X)
cents = km.cluster_centers_.astype(np.float32)
buckets = [np.where(km.labels_ == c)[0] for c in range(NLIST)]

ivf_probe, ivf_recall, ivf_frac = [], [], []
for nprobe in (1, 2, 4, 8, 16, 32, 64):
    hits = scanned = 0
    for i in range(N_QUERY):
        cells = np.argsort(-(Q[i] @ cents.T))[:nprobe]
        cand = np.concatenate([buckets[c] for c in cells])
        scanned += len(cand)
        got = cand[np.argsort(-(Q[i] @ X[cand].T))[:K]]
        hits += len(set(got.tolist()) & exact[i])
    recall = hits / (N_QUERY * K)
    frac = scanned / N_QUERY / N
    ivf_probe.append(nprobe); ivf_recall.append(recall); ivf_frac.append(frac)
    print(f"  IVF nprobe={nprobe:>3}  recall@10={recall:6.3f}  "
          f"scanned={100 * frac:5.2f}% of corpus")

# --- PQ: 8-bit k-means codebook per subspace, then exact re-rank ---
M_SUB = 16
sub = D // M_SUB
codes = np.empty((N, M_SUB), dtype=np.uint8)
codebooks = []
for m in range(M_SUB):
    seg = X[:, m * sub:(m + 1) * sub]
    k = KMeans(n_clusters=256, n_init=1, random_state=0).fit(seg)
    codebooks.append(k.cluster_centers_.astype(np.float32))
    codes[:, m] = k.labels_
print(f"  PQ M={M_SUB}: {M_SUB} bytes/vector vs {D * 4} bytes float32 "
      f"= {D * 4 / M_SUB:.0f}x compression")

pq_short, pq_recall, pq_frac = [], [], []
for shortlist in (10, 50, 100, 200, 500, 1000):
    hits = 0
    for i in range(N_QUERY):
        table = np.stack([Q[i, m * sub:(m + 1) * sub] @ codebooks[m].T
                          for m in range(M_SUB)])
        approx = table[np.arange(M_SUB), codes].sum(axis=1)
        short = np.argpartition(-approx, shortlist)[:shortlist]
        got = short[np.argsort(-(Q[i] @ X[short].T))[:K]]
        hits += len(set(got.tolist()) & exact[i])
    recall = hits / (N_QUERY * K)
    pq_short.append(shortlist); pq_recall.append(recall)
    pq_frac.append(shortlist / N)
    print(f"  PQ shortlist={shortlist:>5}  recall@10={recall:6.3f}  "
          f"exact re-ranks={100 * shortlist / N:5.2f}% of corpus")

fig, ax = plt.subplots(figsize=(4.4, 3.0))
ax.plot([100 * f for f in ivf_frac], ivf_recall, "o-", color=RLBLUE,
        linewidth=1.8, markersize=5, label=f"IVF (nlist={NLIST})")
ax.plot([100 * f for f in pq_frac], pq_recall, "s-", color=RLORANGE,
        linewidth=1.8, markersize=5, label=f"PQ {M_SUB}B + exact re-rank")
ax.set_xscale("log")
ax.set_xlabel("% of corpus given exact distances (log)", fontsize=10)
ax.set_ylabel("recall@10", fontsize=10)
ax.set_ylim(0, 1.05)
ax.tick_params(labelsize=9)
ax.legend(loc="lower right", fontsize=8.5, frameon=True, facecolor="white",
          framealpha=0.95, edgecolor="#cccccc")
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "ann_recall_tradeoff")

print("\nAll Lecture 7 figures written to", OUT_DIR)
