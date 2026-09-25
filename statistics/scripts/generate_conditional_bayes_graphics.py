#!/usr/bin/env python3
"""Generate lecture figures for statistics/ Lecture 2
(lecture02_conditional_independence.tex, lecture02_bayes_theorem.tex)

Numbers come from pandas/numpy; rendering is matplotlib, saved directly as
vector PDF (and SVG) -- see the pandas-vector-graphics skill for when this
matplotlib path applies vs. the TikZ path used by ml/'s older scripts.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "conditional_bayes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand palette (see statistics/theme/rl-theme.tex: RLBlue, RLGreen, RLOrange).
RLBLUE = "#3A35B7"
RLGREEN = "#5FA0A4"
RLORANGE = "#F4BD70"
RLRED = "#D6455D"
GREY = "#DCDCDC"

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


# ─── The running example: one year group of 100 students ──────────────────
# Two everyday facts recorded about each student. The four cell counts are the
# data; every probability below is derived from them, nothing is asserted.
CELLS = [
    ("bike", "bus", 15),
    ("bike", "no bus", 45),
    ("no bike", "bus", 30),
    ("no bike", "no bus", 10),
]
people = []
for bike, bus, count in CELLS:
    people.extend([(bike, bus)] * count)
students = pd.DataFrame(people, columns=["bike", "bus"])

n_stu = len(students)
n_bike = int((students["bike"] == "bike").sum())
n_bus = int((students["bus"] == "bus").sum())
n_bike_bus = int(((students["bike"] == "bike") & (students["bus"] == "bus")).sum())
p_bus = n_bus / n_stu
p_bike = n_bike / n_stu
p_bus_given_bike = n_bike_bus / n_bike
p_bus_given_nobike = (n_bus - n_bike_bus) / (n_stu - n_bike)

print("Running example: 100 students")
print(pd.crosstab(students["bike"], students["bus"], margins=True))
print(f"  P(bus)={p_bus:.2f}  P(bike)={p_bike:.2f}")
print(f"  P(bus|bike)={p_bus_given_bike:.2f}  P(bus|no bike)={p_bus_given_nobike:.2f}")
print(f"  independence check: P(bike)*P(bus)*n = {p_bike * p_bus * n_stu:.0f}"
      f"  vs observed {n_bike_bus}")


# ─── Figure 1: conditioning restricts the sample space ────────────────────
print("\nFigure 1: restricting the sample space …")
NCOL = 10
# Draw the 100 students ordered by cell, so the 60 bike owners form the first
# six complete rows and the conditioned group is a contiguous block.
order = students.sort_values(
    ["bike", "bus"], key=lambda s: s.map({"bike": 0, "no bike": 1, "bus": 0, "no bus": 1})
).reset_index(drop=True)
bus_colour = [RLORANGE if b == "bus" else RLGREEN for b in order["bus"]]
in_group = [b == "bike" for b in order["bike"]]
print(f"  first {sum(in_group)} icons are the bike owners "
      f"({NCOL} per row → {sum(in_group) // NCOL} full rows)")


def icon_grid(ax, colours):
    for i, fc in enumerate(colours):
        r, c = divmod(i, NCOL)
        ax.add_patch(Rectangle((c, -r), 0.86, 0.86, facecolor=fc,
                               edgecolor="white", linewidth=0.7))
    ax.set_xlim(-0.35, NCOL + 0.05)
    ax.set_ylim(-(len(colours) - 1) // NCOL - 0.5, 1.05)
    ax.set_aspect("equal")
    ax.axis("off")


fig, axes = plt.subplots(1, 2, figsize=(6.2, 3.0))
icon_grid(axes[0], bus_colour)
axes[0].set_title(f"All {n_stu} students\n{n_bus} take the bus"
                  f"   $\\rightarrow$   $P$(bus) $= {p_bus:.2f}$", fontsize=9.5)

faded = [c if g else GREY for c, g in zip(bus_colour, in_group)]
icon_grid(axes[1], faded)
n_rows_group = sum(in_group) // NCOL
axes[1].add_patch(Rectangle((-0.16, -n_rows_group + 0.84), NCOL + 0.02,
                            n_rows_group + 0.18, facecolor="none",
                            edgecolor=RLBLUE, linewidth=1.6))
axes[1].set_title(f"Given “owns a bike” ({n_bike} students)\n"
                  f"{n_bike_bus} of them take the bus"
                  f"   $\\rightarrow$   $P$(bus | bike) $= {p_bus_given_bike:.2f}$",
                  fontsize=9.5)

handles = [Rectangle((0, 0), 1, 1, facecolor=RLORANGE, edgecolor="white"),
           Rectangle((0, 0), 1, 1, facecolor=RLGREEN, edgecolor="white"),
           Rectangle((0, 0), 1, 1, facecolor=GREY, edgecolor="white")]
fig.legend(handles, ["takes the bus", "does not take the bus", "ruled out by what we know"],
           loc="lower center", ncol=3, frameon=False, fontsize=9,
           bbox_to_anchor=(0.5, -0.015))
fig.tight_layout(rect=(0, 0.06, 1, 1))
save_fig(fig, "conditional_bayes_restrict_space")


# ─── Figure 2: the law of total probability as a weighted average ─────────
print("\nFigure 2: law of total probability …")
groups = [("owns a bike", 0, n_bike, p_bus_given_bike),
          ("no bike", n_bike, n_stu, p_bus_given_nobike)]
total_riders = sum((x1 - x0) * p for _, x0, x1, p in groups)
print(f"  weighted average = "
      + " + ".join(f"{p:.2f}×{(x1 - x0) / n_stu:.1f}" for _, x0, x1, p in groups)
      + f" = {total_riders / n_stu:.2f}  (table says {p_bus:.2f})")
assert abs(total_riders - n_bus) < 1e-9

fig, ax = plt.subplots(figsize=(5.8, 3.4))
for label, x0, x1, p in groups:
    w = x1 - x0
    ax.add_patch(Rectangle((x0, 0), w, p, facecolor=RLORANGE, edgecolor="white",
                           linewidth=1.2))
    ax.add_patch(Rectangle((x0, p), w, 1 - p, facecolor=RLGREEN, edgecolor="white",
                           linewidth=1.2))
    ax.text(x0 + w / 2, p / 2, f"{int(round(p * w))} take\nthe bus",
            ha="center", va="center", fontsize=9.5)
    ax.text(x0 + w / 2, p + (1 - p) / 2, f"{int(round((1 - p) * w))} do not",
            ha="center", va="center", fontsize=9.5)

ax.axhline(p_bus, color=RLBLUE, linewidth=1.8, linestyle="--")
ax.text(2.5, p_bus + 0.015, f"overall $P$(bus) $= {p_bus:.2f}$",
        ha="left", va="bottom", fontsize=9.5, color=RLBLUE,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.5))
ax.set_xlim(0, n_stu)
ax.set_ylim(0, 1)
ax.set_xticks([n_bike / 2, (n_bike + n_stu) / 2])
ax.set_xticklabels([f"owns a bike\n{n_bike} students\n$P$(bus | bike) $= {p_bus_given_bike:.2f}$",
                    f"no bike\n{n_stu - n_bike} students\n"
                    f"$P$(bus | no bike) $= {p_bus_given_nobike:.2f}$"], fontsize=9.5)
ax.tick_params(axis="x", length=0)
ax.set_ylabel("share of the group\nwho take the bus")
ax.set_xlabel("bar width = how big the group is", fontsize=9.5, labelpad=8)
fig.tight_layout()
save_fig(fig, "conditional_bayes_total_probability")


# ─── Figure 3: a screening test — where the positives come from ───────────
print("\nFigure 3: screening test …")
N_TESTED = 10_000
PREVALENCE = 0.01          # 1 person in 100 has the disease
SENSITIVITY = 1.00         # assume the test never misses a real case
FALSE_POS = 0.05           # it wrongly flags 5% of healthy people

n_ill = int(round(N_TESTED * PREVALENCE))
n_well = N_TESTED - n_ill
true_pos = int(round(n_ill * SENSITIVITY))
false_neg = n_ill - true_pos
false_pos = int(round(n_well * FALSE_POS))
true_neg = n_well - false_pos
n_positive = true_pos + false_pos
ppv = true_pos / n_positive
screen = pd.DataFrame({"positive": [true_pos, false_pos], "negative": [false_neg, true_neg]},
                      index=["has the disease", "healthy"])
print(screen)
print(f"  positives = {n_positive}   P(disease | positive) = "
      f"{true_pos}/{n_positive} = {ppv:.4f}")

# Two bars. The top one is the whole tested population at true scale, with the
# people who test positive gathered at the left end; the bottom one magnifies
# just that sliver. Connector lines make the change of scale explicit rather
# than leaving the reader to infer it from the titles.
fig, axes = plt.subplots(2, 1, figsize=(4.8, 3.1))
BAR_H = 0.5

top, bot = axes
frac_pos = n_positive / N_TESTED
for ax in axes:
    ax.set_xlim(0, 1)
    ax.axis("off")
top.set_ylim(-0.95, 0.45)
bot.set_ylim(-0.95, 0.45)

# --- top bar: all 10,000, positives first so they form one block ---
segments = [(true_pos, RLRED), (false_pos, RLORANGE),
            (false_neg, "#9E9E9E"), (true_neg, RLGREEN)]
left = 0.0
for width, colour in segments:
    top.barh(0, width / N_TESTED, left=left, height=BAR_H, color=colour,
             edgecolor="white", linewidth=0.8)
    left += width / N_TESTED
top.text(0.5 * (frac_pos + 1), 0, f"{true_neg + false_neg:,} test negative",
         ha="center", va="center", fontsize=11)
top.set_title(f"{N_TESTED:,} people tested", fontsize=11.5, loc="left")
# bracket under the positive sliver
top.plot([0, frac_pos], [-BAR_H / 2 - 0.10] * 2, color="#555555", linewidth=1.0)
top.text(frac_pos + 0.10, -0.55, f"{n_positive} test positive",
         fontsize=11, ha="left", va="center",
         bbox=dict(facecolor="white", edgecolor="none", pad=1.8))

# --- bottom bar: the same 594 people, magnified to full width ---
left = 0.0
for width, colour, label in [(true_pos, RLRED, f"{true_pos}\ntruly ill"),
                             (false_pos, RLORANGE, f"{false_pos} false alarms")]:
    frac = width / n_positive
    bot.barh(0, frac, left=left, height=BAR_H, color=colour,
             edgecolor="white", linewidth=0.8)
    bot.text(left + frac / 2, 0, label, ha="center", va="center", fontsize=11)
    left += frac
bot.text(0.5, -0.58, f"the same {n_positive} people, magnified",
         ha="center", va="center", fontsize=11, color="#555555")

# connectors showing the magnification
for x_top, x_bot in ((0.0, 0.0), (frac_pos, 1.0)):
    con = matplotlib.patches.ConnectionPatch(
        xyA=(x_top, -BAR_H / 2), coordsA=top.transData,
        xyB=(x_bot, BAR_H / 2 + 0.02), coordsB=bot.transData,
        color="#999999", linewidth=0.9, linestyle=(0, (3, 3)))
    fig.add_artist(con)

fig.tight_layout()
fig.subplots_adjust(hspace=0.05)
save_fig(fig, "conditional_bayes_screening")


# ─── Figure 4: the same test, different base rates ────────────────────────
print("\nFigure 4: base rate vs. P(disease | positive) …")
prev = np.linspace(0.0005, 0.20, 500)
post = SENSITIVITY * prev / (SENSITIVITY * prev + FALSE_POS * (1 - prev))
df_base = pd.DataFrame({"prevalence": prev, "ppv": post})
for p in (0.001, 0.01, 0.05, 0.10, 0.20):
    v = SENSITIVITY * p / (SENSITIVITY * p + FALSE_POS * (1 - p))
    print(f"  prevalence {p:6.3%}  →  P(disease | positive) = {v:.3f}")

fig, ax = plt.subplots(figsize=(4.2, 3.2))
ax.plot(df_base["prevalence"] * 100, df_base["ppv"] * 100, color=RLBLUE, linewidth=2.4)
ax.scatter([PREVALENCE * 100], [ppv * 100], s=80, c=RLRED, zorder=4)
ax.annotate(f"1 in 100\n$\\rightarrow$ {ppv * 100:.0f}%",
            xy=(PREVALENCE * 100, ppv * 100), xytext=(4.0, 10),
            fontsize=11, color=RLRED,
            arrowprops=dict(arrowstyle="->", color=RLRED, linewidth=1.3))
ax.set_xlabel("How common the disease is (%)", fontsize=11)
ax.set_ylabel("$P$(disease | positive), %", fontsize=11)
ax.set_xlim(0, 20)
ax.set_ylim(0, 100)
ax.set_xticks([0, 5, 10, 15, 20])
ax.set_yticks([0, 25, 50, 75, 100])
ax.tick_params(labelsize=10.5)
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "conditional_bayes_base_rate")

print("\nAll done.")
