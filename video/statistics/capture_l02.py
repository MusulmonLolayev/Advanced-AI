"""Capture every number the Lecture 2 video speaks or shows.

Three sources, all computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_conditional_bayes_graphics.py),
    saved verbatim to raw/l02_figures.txt;
  * the slides' hand-worked examples (die, 100 students, socks, glasses, screening test),
    recomputed here and asserted against what the slides print;
  * Berkeley graduate admissions, autumn 1973, six largest departments, as counts
    (Bickel, Hammel & O'Connell, Science 187, 1975; R's UCBAdmissions dataset). The slide
    shows these as rounded percentages; the counts below reproduce every one of them.
The video reads raw/l02_numbers.json and types no number itself.
"""
import json
import os
import subprocess
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
OUT.mkdir(exist_ok=True)

# ─── the figure script, verbatim ──────────────────────────────────────────
ADV_AI = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
fig = subprocess.run([ADV_AI, str(REPO / "statistics/scripts/generate_conditional_bayes_graphics.py")],
                     capture_output=True, text=True, cwd=REPO / "statistics")
assert fig.returncode == 0, fig.stderr[-2000:]
fig = fig.stdout
(OUT / "l02_figures.txt").write_text(fig)
for must in ("P(bus)=0.45  P(bike)=0.60", "P(bus|bike)=0.25  P(bus|no bike)=0.75",
             "= 27  vs observed 15", "positives = 595", "100/595 = 0.1681",
             "prevalence 0.100%  →  P(disease | positive) = 0.020",
             "prevalence 10.000%  →  P(disease | positive) = 0.690"):
    assert must in fig, f"figure script output changed: {must!r} missing"

V = {}


def frac(x):
    return [x.numerator, x.denominator]


# ─── section 1: the die, then the 100 students ────────────────────────────
V["die_p6"] = frac(F(1, 6))
V["die_p6_given_even"] = frac(F(1, 6) / F(3, 6))
assert F(1, 6) / F(3, 6) == F(1, 3)

CELLS = {("bike", "bus"): 15, ("bike", "nobus"): 45, ("nobike", "bus"): 30, ("nobike", "nobus"): 10}
n = sum(CELLS.values())
bike = CELLS["bike", "bus"] + CELLS["bike", "nobus"]
nobike = n - bike
bus = CELLS["bike", "bus"] + CELLS["nobike", "bus"]
V["cells"] = {f"{a}_{b}": c for (a, b), c in CELLS.items()}
V.update(n=n, bike=bike, nobike=nobike, bus=bus, nobus=n - bus)
V["p_bus"] = bus / n
V["p_bike"] = bike / n
V["p_bus_given_bike"] = CELLS["bike", "bus"] / bike
V["p_bus_given_nobike"] = CELLS["nobike", "bus"] / nobike
assert (V["p_bus"], V["p_bus_given_bike"], V["p_bus_given_nobike"]) == (0.45, 0.25, 0.75)

# ─── section 2: the tree ──────────────────────────────────────────────────
paths = {"bike_bus": F(6, 10) * F(1, 4), "bike_nobus": F(6, 10) * F(3, 4),
         "nobike_bus": F(4, 10) * F(3, 4), "nobike_nobus": F(4, 10) * F(1, 4)}
assert sum(paths.values()) == 1
for k, p in paths.items():
    assert p * n == V["cells"][k], (k, p)
V["tree_paths"] = {k: float(p) for k, p in paths.items()}

# ─── section 3: two socks, 6 black and 4 white ────────────────────────────
b, w_, s = 6, 4, 10
both_black = F(b, s) * F(b - 1, s - 1)
both_white = F(w_, s) * F(w_ - 1, s - 1)
with_repl = F(b, s) ** 2
pair = both_black + both_white
assert both_black == F(1, 3) and float(with_repl) == 0.36 and round(float(pair), 2) == 0.47
V["socks"] = {"black": b, "white": w_, "total": s, "both_black": frac(both_black),
              "both_black_90": [30, 90], "both_white_90": [12, 90], "with_replacement": float(with_repl),
              "pair_90": [42, 90], "pair": round(float(pair), 4)}
assert F(30, 90) == both_black and F(12, 90) == both_white

# ─── section 4: the table — joint, marginal, conditional ──────────────────
V["joint_bike_bus"] = CELLS["bike", "bus"] / n
V["p_bike_given_bus"] = frac(F(CELLS["bike", "bus"], bus))          # hands-on: 15/45 = 1/3
assert F(15, 45) == F(1, 3)

# ─── section 5: independence from the table ───────────────────────────────
GLASSES, GLASSES_BUS = 40, 18
V["glasses"], V["glasses_bus"] = GLASSES, GLASSES_BUS
V["p_bus_given_glasses"] = GLASSES_BUS / GLASSES
assert V["p_bus_given_glasses"] == V["p_bus"]
V["expected_bike_bus"] = bike * bus / n
V["expected_glasses_bus"] = GLASSES * bus / n
V["expected_nobike_bus"] = nobike * bus / n                        # hands-on: 18 expected, 30 observed
assert (V["expected_bike_bus"], V["expected_glasses_bus"], V["expected_nobike_bus"]) == (27, 18, 18)

# ─── section 6: Berkeley 1973 ─────────────────────────────────────────────
BERKELEY = {  # dept: (men applied, men admitted, women applied, women admitted)
    "A": (825, 512, 108, 89), "B": (560, 353, 25, 17), "C": (325, 120, 593, 202),
    "D": (417, 138, 375, 131), "E": (191, 53, 393, 94), "F": (373, 22, 341, 24)}
SLIDE = {"A": (62, 82), "B": (63, 68), "C": (37, 34), "D": (33, 35), "E": (28, 24), "F": (6, 7)}
dept = {}
for d, (ma, mx, wa, wx) in BERKELEY.items():
    m, wo = round(100 * mx / ma), round(100 * wx / wa)
    assert (m, wo) == SLIDE[d], (d, m, wo)
    dept[d] = {"men_applied": ma, "men_rate": mx / ma, "women_applied": wa, "women_rate": wx / wa,
               "all_rate": (mx + wx) / (ma + wa)}
men_app = sum(v[0] for v in BERKELEY.values())
wom_app = sum(v[2] for v in BERKELEY.values())
men_rate = sum(v[1] for v in BERKELEY.values()) / men_app
wom_rate = sum(v[3] for v in BERKELEY.values()) / wom_app
assert (men_app, wom_app, round(100 * men_rate), round(100 * wom_rate)) == (2691, 1835, 45, 30)
women_higher = [d for d, v in dept.items() if v["women_rate"] > v["men_rate"]]
assert women_higher == ["A", "B", "D", "F"]
men_ab = (BERKELEY["A"][0] + BERKELEY["B"][0]) / men_app
wom_cef = sum(BERKELEY[d][2] for d in "CEF") / wom_app
V["berkeley"] = {"dept": dept, "men_applied": men_app, "women_applied": wom_app,
                 "men_rate": men_rate, "women_rate": wom_rate, "women_higher": women_higher,
                 "men_share_AB": men_ab, "women_share_CEF": wom_cef}
# the slide's "accepted about 64% and 63%" (A, B) and "35%, 25% and 7%" (C, E, F), department-wide
all_pct = {d: round(100 * v["all_rate"]) for d, v in dept.items()}
assert (all_pct["A"], all_pct["B"], all_pct["C"], all_pct["E"]) == (64, 63, 35, 25)
V["berkeley"]["all_pct"] = all_pct
print("Berkeley department-wide admission %:", all_pct,
      "(slide says F = 7%; the counts give", all_pct["F"], "%)")

# ─── section 7: total probability ─────────────────────────────────────────
V["total_bus"] = 0.25 * 0.6 + 0.75 * 0.4
V["total_nobus"] = 0.75 * 0.6 + 0.25 * 0.4                          # hands-on: 0.55 = 55/100
assert round(V["total_bus"], 10) == 0.45 and round(V["total_nobus"], 10) == 0.55

# ─── section 8: Bayes on the students ─────────────────────────────────────
V["bayes_bike_given_bus"] = frac(F(1, 4) * F(6, 10) / F(45, 100))
V["bayes_nobike_given_bus"] = frac(F(3, 4) * F(4, 10) / F(45, 100))  # hands-on: 2/3 = 30/45
assert V["bayes_bike_given_bus"] == [1, 3] and V["bayes_nobike_given_bus"] == [2, 3]

# ─── section 9: the screening test ────────────────────────────────────────
def screen(n_tested, prevalence, false_pos=0.05):
    ill = round(n_tested * prevalence)
    fp = round((n_tested - ill) * false_pos)
    return {"tested": n_tested, "ill": ill, "healthy": n_tested - ill, "false_pos": fp,
            "positives": ill + fp, "ppv": ill / (ill + fp)}


V["screen"] = screen(10_000, 0.01)
assert (V["screen"]["false_pos"], V["screen"]["positives"]) == (495, 595)
V["screen_1in10"] = screen(10_000, 0.10)                            # hands-on: 1000 / 1450
assert (V["screen_1in10"]["false_pos"], V["screen_1in10"]["positives"]) == (450, 1450)
V["false_per_real"] = V["screen"]["false_pos"] / V["screen"]["ill"]

# ─── section 10: base rates ───────────────────────────────────────────────
V["screen_1in1000"] = screen(100_000, 0.001)
assert round(V["screen_1in1000"]["ppv"], 2) == 0.02 and round(V["screen_1in10"]["ppv"], 2) == 0.69
V["acc_always_healthy_1in100"] = 0.99
V["acc_always_healthy_1in1000"] = 0.999                             # hands-on
V["base_curve"] = [[p / 1000, (p / 1000) / (p / 1000 + 0.05 * (1 - p / 1000))] for p in range(1, 201)]

(OUT / "l02_numbers.json").write_text(json.dumps(V, indent=1, ensure_ascii=False))
print("wrote", OUT / "l02_numbers.json")
