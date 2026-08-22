#!/usr/bin/env python3
"""Generate t-SNE lecture figures for ml/lectures/lecture10_tsne.tex

Numbers come from pandas/numpy/scikit-learn; rendering is matplotlib,
saved directly as vector PDF (and SVG) -- no TikZ/pgfplots/pdflatex in
this script's pipeline. See the pandas-vector-graphics skill for when
this matplotlib path applies vs. the TikZ path used by other lectures.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "tsne"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand palette (see ml/theme/rl-theme.tex: RLBlue, RLGreen, plus a third
# contrasting accent for the 3-class ring dataset).
RLBLUE = "#3A35B7"
RLGREEN = "#5FA0A4"
RLRED = "#D6455D"
CLASS_COLORS = [RLBLUE, RLRED, RLGREEN]

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


def scatter_by_class(ax, df, xcol, ycol, s=26):
    for cls, color in enumerate(CLASS_COLORS):
        sub = df[df["label"] == cls]
        ax.scatter(sub[xcol], sub[ycol], s=s, c=color, edgecolors="black",
                   linewidths=0.5, alpha=0.9, zorder=3)


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
X_2d = df_rings[["x", "y"]].values

np.random.seed(7)
W = np.random.randn(2, 8)
X_high = X_2d @ W + np.random.randn(len(df_rings), 8) * 0.6
labels = df_rings["label"].values


# ─── Figure 1: PCA vs t-SNE ──────────────────────────────────────────────────
print("Running PCA and t-SNE …")
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_high)
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

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.6))
scatter_by_class(ax1, df_rings, "pca1", "pca2")
ax1.set_title("PCA (linear projection)", fontsize=11, fontweight="bold")
ax1.set_xlabel("PC 1")
ax1.set_ylabel("PC 2")
ax1.grid(True, linestyle=":", alpha=0.4)

scatter_by_class(ax2, df_rings, "t1", "t2")
ax2.set_title("t-SNE (non-linear embedding)", fontsize=11, fontweight="bold")
ax2.set_xlabel("Dimension 1")
ax2.set_ylabel("Dimension 2")
ax2.grid(True, linestyle=":", alpha=0.4)

fig.tight_layout()
save_fig(fig, "tsne_pca_comparison")


# ─── Figure 2: Gaussian vs Student-t kernel curves ───────────────────────────
d = np.linspace(0, 4.0, 300)
df_k = pd.DataFrame({
    "d": d,
    "gaussian": np.exp(-d**2),
    "student": 1.0 / (1.0 + d**2),
})

fig, ax = plt.subplots(figsize=(6.2, 4.0))
ax.plot(df_k["d"], df_k["gaussian"], color=RLBLUE, linewidth=2.2,
        label=r"Gaussian $e^{-d^2}$ (used for $P$)")
ax.plot(df_k["d"], df_k["student"], color=RLRED, linewidth=2.2, linestyle="--",
        label=r"Student-$t$ $(1+d^2)^{-1}$ (used for $Q$)")
ax.set_xlabel(r"Distance $d = \|y_i - y_j\|$")
ax.set_ylabel("Similarity")
ax.set_xlim(0, 4)
ax.set_ylim(0, 1.05)
ax.grid(True, linestyle=":", alpha=0.4)
ax.legend(loc="upper right", frameon=False, fontsize=10)
fig.tight_layout()
save_fig(fig, "tsne_similarity_kernels")


# ─── Figure 3: Crowding schematic ────────────────────────────────────────────
n_pts = 6
angles = np.linspace(0, 2 * np.pi, n_pts, endpoint=False)
circ_df = pd.DataFrame({
    "cx": np.cos(angles),
    "cy": np.sin(angles),
    "label": np.arange(n_pts) % 3,
})
circ_df["proj"] = circ_df["cx"]

R = 1.3
PERSONAL_R = 0.38

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.4, 3.4))

ax1.set_xlim(-2.0, 2.0)
ax1.set_ylim(-2.0, 2.0)
ax1.set_aspect("equal")
ax1.axis("off")
ax1.set_title("2D: room for all 6\nneighbours' personal space", fontsize=9.5)
ax1.add_patch(Circle((0, 0), R, fill=False, edgecolor="#999999",
                      linestyle="--", linewidth=1.0))
for _, row in circ_df.iterrows():
    color = CLASS_COLORS[int(row.label)]
    cx, cy = row.cx * R, row.cy * R
    ax1.add_patch(Circle((cx, cy), PERSONAL_R, fill=False,
                          edgecolor=color, alpha=0.5, linewidth=1.0))
    ax1.scatter([cx], [cy], s=55, c=color, edgecolors="black",
                linewidths=0.6, zorder=3)

ax2.set_xlim(-2.0, 2.0)
ax2.set_ylim(-2.0, 2.0)
ax2.set_aspect("equal")
ax2.axis("off")
ax2.set_title("1D: same neighbours —\npersonal spaces overlap", fontsize=9.5)
ax2.plot([-1.7, 1.7], [0, 0], color="#888888", linewidth=1.6, zorder=1)
for _, row in circ_df.iterrows():
    color = CLASS_COLORS[int(row.label)]
    px = row.proj * R
    ax2.add_patch(Circle((px, 0), PERSONAL_R, fill=False,
                          edgecolor=color, alpha=0.5, linewidth=1.0))
    ax2.scatter([px], [0], s=55, c=color, edgecolors="black",
                linewidths=0.6, zorder=3)

fig.tight_layout()
save_fig(fig, "tsne_crowding")


# ─── Figure 4: Perplexity comparison ─────────────────────────────────────────
print("Running t-SNE for perplexity comparison …")
perplexities = [3, 15, 45]
tsne_embeds = {}
for perp in perplexities:
    tsne_p = TSNE(n_components=2, perplexity=perp, random_state=42,
                  max_iter=1000, init="pca", learning_rate="auto")
    emb = tsne_p.fit_transform(X_high)
    tsne_embeds[perp] = emb
    print(f"  perplexity={perp} → KL={tsne_p.kl_divergence_:.3f}")

fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.4))
labels_map = {3: "too local", 15: "good", 45: "too global"}
for ax, perp in zip(axes, perplexities):
    emb = tsne_embeds[perp]
    dfp = df_rings.copy()
    dfp["e1"] = emb[:, 0]
    dfp["e2"] = emb[:, 1]
    scatter_by_class(ax, dfp, "e1", "e2", s=18)
    weight = "bold" if perp == 15 else "normal"
    ax.set_title(f"perplexity = {perp} ({labels_map[perp]})",
                 fontsize=10, fontweight=weight)
    ax.set_xticks([])
    ax.set_yticks([])
fig.tight_layout()
save_fig(fig, "tsne_perplexity")


# ─── Figure 5: KL divergence convergence ─────────────────────────────────────
print("Running t-SNE convergence tracking …")
max_iter_vals = [300, 400, 500, 650, 800, 1000]
kl_rows = []
X_cv = X_high[:20]

for n in max_iter_vals:
    t = TSNE(n_components=2, perplexity=5, max_iter=n, random_state=42,
             init="pca", learning_rate="auto")
    t.fit_transform(X_cv)
    kl_rows.append({"iter": n, "kl": t.kl_divergence_})

df_kl = pd.DataFrame(kl_rows)
df_kl = df_kl[np.isfinite(df_kl["kl"])].reset_index(drop=True)
print("KL trajectory:")
print(df_kl.to_string(index=False))

fig, ax = plt.subplots(figsize=(6.6, 4.0))
ax.plot(df_kl["iter"], df_kl["kl"], color=RLBLUE, linewidth=2.0,
        marker="o", markersize=5, markerfacecolor=RLBLUE,
        markeredgecolor="black", markeredgewidth=0.5)
ax.set_xlabel("Iteration")
ax.set_ylabel(r"KL Divergence $D_{\mathrm{KL}}(P \| Q)$")
ax.set_xlim(0, 1050)
ax.set_ylim(bottom=0)
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "tsne_convergence")


# ─── Figure 6: Worked numerical example — computing P_ij by hand ────────────
print("\nWorked example: 5-point toy dataset …")
toy = pd.DataFrame({
    "x": [0.0, 1.0, 0.0, 5.0, 5.0],
    "y": [0.0, 0.0, 3.0, 5.0, 6.0],
}, index=["x1", "x2", "x3", "x4", "x5"])
X_toy = toy[["x", "y"]].values
n_toy = len(X_toy)

D_toy = np.sqrt(((X_toy[:, None, :] - X_toy[None, :, :]) ** 2).sum(-1))
print("Pairwise distances:")
print(pd.DataFrame(D_toy, index=toy.index, columns=toy.index).round(3))

sigma_toy = 2.0
num = np.exp(-D_toy**2 / (2 * sigma_toy**2))
np.fill_diagonal(num, 0.0)
P_cond = num / num.sum(axis=1, keepdims=True)
P_joint = (P_cond + P_cond.T) / (2 * n_toy)

df_pcond = pd.DataFrame(P_cond, index=toy.index, columns=toy.index)
df_pjoint = pd.DataFrame(P_joint, index=toy.index, columns=toy.index)
print(f"\nConditional p_(j|i), sigma={sigma_toy}:")
print(df_pcond.round(4))
print("\nJoint p_ij (symmetrised):")
print(df_pjoint.round(4))
print(f"\np_(2|1) = {P_cond[0,1]:.4f}   p_(1|2) = {P_cond[1,0]:.4f}")
print(f"p_13 (x1,x3 -- near) = {P_joint[0,2]:.4f}"
      f"   p_14 (x1,x4 -- far) = {P_joint[0,3]:.4f}")

y_toy_1d = np.array([0.0, 0.3, 1.6, 3.6, 3.9])
Dy_toy = np.abs(y_toy_1d[:, None] - y_toy_1d[None, :])
q_num = (1 + Dy_toy**2) ** -1
np.fill_diagonal(q_num, 0.0)
Q_joint = q_num / q_num.sum()
df_qjoint = pd.DataFrame(Q_joint, index=toy.index, columns=toy.index)
print("\nLow-D toy layout y:", dict(zip(toy.index, y_toy_1d)))
print("Joint q_ij (Student-t on the 1D layout above):")
print(df_qjoint.round(4))

with np.errstate(divide="ignore", invalid="ignore"):
    contrib = np.where(P_joint > 0, P_joint * np.log(P_joint / Q_joint), 0.0)
kl_total = contrib[np.triu_indices(n_toy, 1)].sum() * 2
print(f"\nKL(P||Q) for this toy layout = {kl_total:.4f}")
pair_i, pair_j = 0, 2
print(f"Largest single-pair term: p_ij log(p_ij/q_ij) for ({toy.index[pair_i]},"
      f"{toy.index[pair_j]}) = {contrib[pair_i, pair_j]:.4f}")

fig, ax = plt.subplots(figsize=(3.4, 4.0))
ax.scatter(toy["x"], toy["y"], s=90, c=RLBLUE, edgecolors="black",
           linewidths=0.7, zorder=3)
for name, (px, py) in zip(toy.index, X_toy):
    ax.annotate(f"${name}$", (px, py), textcoords="offset points",
                xytext=(7, 6), fontsize=12)
ax.set_xlim(-0.8, 5.8)
ax.set_ylim(-0.8, 6.8)
ax.grid(True, linestyle=":", alpha=0.4)
ax.axhline(0, color="#333333", linewidth=0.8)
ax.axvline(0, color="#333333", linewidth=0.8)
ax.set_aspect("equal")
fig.tight_layout()
save_fig(fig, "tsne_worked_example")


# ─── Shared helpers: Sammon projection & Symmetric SNE ───────────────────────
def pairwise_dist(Y):
    diff = Y[:, None, :] - Y[None, :, :]
    return np.sqrt((diff ** 2).sum(-1) + 1e-12)


def sammon_stress(Dstar, Y, c):
    Dy = pairwise_dist(Y)
    return np.sum(np.triu((Dstar - Dy) ** 2 / np.where(Dstar == 0, 1, Dstar), 1)) / c


def sammon_projection(X, n_iter=300, lr_init=2.0, random_state=0):
    """Minimise Sammon stress (Sammon, 1969) by steepest descent with
    backtracking line search -- plain fixed-step descent on this objective
    converges too slowly to be usable (verified: <2% stress reduction in 400
    steps at a stable step size); line search reaches near-zero stress."""
    n = X.shape[0]
    Dstar = pairwise_dist(X)
    Dstar[Dstar < 1e-6] = 1e-6
    c = Dstar[np.triu_indices(n, 1)].sum()
    rng = np.random.default_rng(random_state)
    Y = rng.normal(scale=0.1, size=(n, 2))
    step = lr_init
    E = sammon_stress(Dstar, Y, c)
    for _ in range(n_iter):
        Dy = pairwise_dist(Y)
        Dy_safe = np.where(Dy < 1e-6, 1e-6, Dy)
        diff = Y[:, None, :] - Y[None, :, :]
        weight = (Dstar - Dy) / (Dstar * Dy_safe)
        np.fill_diagonal(weight, 0.0)
        grad = -(2.0 / c) * (weight[:, :, None] * diff).sum(axis=1)
        while step > 1e-8:
            Y_new = Y - step * grad
            E_new = sammon_stress(Dstar, Y_new, c)
            if E_new < E:
                break
            step *= 0.5
        Y, E = Y_new, E_new
        step *= 1.2
    print(f"  Sammon final stress E = {E:.5f}")
    return Y


def symmetric_sne(P_joint, n_iter=600, lr=20.0, random_state=0):
    """Symmetric SNE: same joint P as t-SNE, but a Gaussian (not Student-t) Q.

    Plain steepest descent on this objective is notoriously unstable (this
    instability is itself part of why t-SNE also introduced momentum/early
    exaggeration) -- so this stand-in uses momentum and gradient clipping to
    reach a readable, converged 2-D layout for the comparison figure.
    """
    n = P_joint.shape[0]
    rng = np.random.default_rng(random_state)
    Y = rng.normal(scale=1e-2, size=(n, 2))
    velocity = np.zeros_like(Y)
    momentum = 0.5
    for it in range(n_iter):
        if it == 250:
            momentum = 0.8
        Dy2 = ((Y[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
        num = np.exp(-Dy2)
        np.fill_diagonal(num, 0.0)
        denom = num.sum()
        Q = num / denom if denom > 0 else num
        Q = np.maximum(Q, 1e-12)
        diff = Y[:, None, :] - Y[None, :, :]
        coeff = (P_joint - Q)
        grad = 4.0 * (coeff[:, :, None] * diff).sum(axis=1)
        grad_norm = np.linalg.norm(grad)
        if grad_norm > 5.0:
            grad = grad * (5.0 / grad_norm)
        velocity = momentum * velocity - lr * grad
        Y = Y + velocity
    return Y


def two_panel_scatter(df, xy_a, xy_b, title_a, title_b, name):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.8))
    for ax, (xc, yc), title in ((ax1, xy_a, title_a), (ax2, xy_b, title_b)):
        scatter_by_class(ax, df, xc, yc, s=24)
        ax.set_title(title, fontsize=10.5, fontweight="bold")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    save_fig(fig, name)


# ─── Figure 7: Sammon projection vs t-SNE on the ring dataset ───────────────
print("\nRunning Sammon projection on the ring dataset …")
Y_sammon = sammon_projection(X_high, n_iter=300, lr_init=2.0, random_state=0)

tsne_small = TSNE(n_components=2, perplexity=10, random_state=42, max_iter=1000,
                   init="pca", learning_rate="auto")
Y_tsne_small = tsne_small.fit_transform(X_high)

df_cmp = pd.DataFrame({
    "sam1": Y_sammon[:, 0], "sam2": Y_sammon[:, 1],
    "t1": Y_tsne_small[:, 0], "t2": Y_tsne_small[:, 1],
    "label": labels,
})
two_panel_scatter(df_cmp, ("sam1", "sam2"), ("t1", "t2"),
                   "Sammon (matches distances)", "t-SNE (matches neighbours)",
                   "tsne_sammon_comparison")


# ─── Figure 8: Symmetric SNE (Gaussian Q) vs t-SNE (Student-t Q) ────────────
# A subsample (not the full 75 points): the crowding effect this figure needs
# to show is much more visible at this density -- verified by comparison,
# the full dataset converges to a much less crowded (less illustrative) layout.
print("\nRunning Symmetric SNE vs t-SNE on the ring dataset …")
X_sne_input = X_high[::2]
labels_sne = labels[::2]
n_sne = len(X_sne_input)
Dh = pairwise_dist(X_sne_input)
sigma_sne = np.median(Dh[Dh > 0])
num_h = np.exp(-Dh**2 / (2 * sigma_sne**2))
np.fill_diagonal(num_h, 0.0)
Pcond_sne = num_h / num_h.sum(axis=1, keepdims=True)
Pjoint_sne = (Pcond_sne + Pcond_sne.T) / (2 * n_sne)

Y_ssne = symmetric_sne(Pjoint_sne, n_iter=400, lr=80.0, random_state=0)

tsne_sne_ref = TSNE(n_components=2, perplexity=8, random_state=42, max_iter=1000,
                     init="pca", learning_rate="auto")
Y_tsne_sne_ref = tsne_sne_ref.fit_transform(X_sne_input)

df_sne = pd.DataFrame({
    "s1": Y_ssne[:, 0], "s2": Y_ssne[:, 1],
    "t1": Y_tsne_sne_ref[:, 0], "t2": Y_tsne_sne_ref[:, 1],
    "label": labels_sne,
})
two_panel_scatter(df_sne, ("s1", "s2"), ("t1", "t2"),
                   "Symmetric SNE (Gaussian Q)", "t-SNE (Student-t Q)",
                   "tsne_sne_comparison")

print("\nAll done.")
