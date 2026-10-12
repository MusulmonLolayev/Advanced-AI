"""Capture every number the Lecture 2 video speaks or shows.

Three sources, all computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_conditional_bayes_graphics.py),
    saved verbatim to raw/l02_figures.txt;
  * the slides' worked examples (die, 100 students, socks, glasses, screening test), computed
    here from their raw counts;
  * Berkeley graduate admissions, autumn 1973, six largest departments, as counts
    (Bickel, Hammel & O'Connell, Science 187, 1975; R's UCBAdmissions dataset).

`compute()` is pure, so test_l02.py can check every value against what the slides print.
Running this file writes raw/l02_numbers.json, which the video reads; the video types no number.
    uv run python statistics/capture_l02.py && uv run python -m unittest statistics/test_l02.py
"""
import json
import math
import os
import subprocess
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
FIGURE_SCRIPT = REPO / "statistics/scripts/generate_conditional_bayes_graphics.py"

# ─── raw inputs: the only typed numbers ───────────────────────────────────
DIE = 6
CELLS = {("bike", "bus"): 15, ("bike", "nobus"): 45, ("nobike", "bus"): 30, ("nobike", "nobus"): 10}
SOCKS = {"black": 6, "white": 4}
GLASSES, GLASSES_BUS = 40, 18
BERKELEY = {  # dept: (men applied, men admitted, women applied, women admitted)
    "A": (825, 512, 108, 89), "B": (560, 353, 25, 17), "C": (325, 120, 593, 202),
    "D": (417, 138, 375, 131), "E": (191, 53, 393, 94), "F": (373, 22, 341, 24)}
FALSE_POS = 0.05            # the test wrongly flags 5 % of healthy people, and never misses a case


def frac(x):
    return [x.numerator, x.denominator]


def screen(n_tested, prevalence, false_pos=FALSE_POS):
    ill = round(n_tested * prevalence)
    fp = round((n_tested - ill) * false_pos)
    return {"tested": n_tested, "ill": ill, "healthy": n_tested - ill, "false_pos": fp,
            "positives": ill + fp, "ppv": ill / (ill + fp)}


def ppv(prevalence, false_pos=FALSE_POS):
    return prevalence / (prevalence + false_pos * (1 - prevalence))


def compute():
    V = {}
    # section 1: the die, then the 100 students
    V["die_p6"] = frac(F(1, DIE))
    V["die_p_even"] = frac(F(3, DIE))
    V["die_p6_given_even"] = frac(F(1, DIE) / F(3, DIE))
    n = sum(CELLS.values())
    bike = CELLS["bike", "bus"] + CELLS["bike", "nobus"]
    bus = CELLS["bike", "bus"] + CELLS["nobike", "bus"]
    V["cells"] = {f"{a}_{b}": c for (a, b), c in CELLS.items()}
    V.update(n=n, bike=bike, nobike=n - bike, bus=bus, nobus=n - bus)
    V["p_bus"] = bus / n
    V["p_bike"] = bike / n
    V["p_bus_given_bike"] = CELLS["bike", "bus"] / bike
    V["p_bus_given_nobike"] = CELLS["nobike", "bus"] / (n - bike)

    # section 2: the tree — multiply along each path
    pb, pbb, pbn = F(bike, n), F(CELLS["bike", "bus"], bike), F(CELLS["nobike", "bus"], n - bike)
    paths = {"bike_bus": pb * pbb, "bike_nobus": pb * (1 - pbb),
             "nobike_bus": (1 - pb) * pbn, "nobike_nobus": (1 - pb) * (1 - pbn)}
    V["tree_paths"] = {k: float(p) for k, p in paths.items()}
    V["tree_counts"] = {k: int(p * n) for k, p in paths.items()}
    V["tree_sum"] = float(sum(paths.values()))
    V["tree_reversed"] = {"bus": bus / n, "nobus": (n - bus) / n}            # hands-on

    # section 3: two socks without replacement
    b, w = SOCKS["black"], SOCKS["white"]
    s = b + w
    bb, ww = F(b, s) * F(b - 1, s - 1), F(w, s) * F(w - 1, s - 1)
    V["socks"] = {"black": b, "white": w, "total": s,
                  "p_first_black": frac(F(b, s)), "p_second_black_given": [b - 1, s - 1],
                  "both_black_unreduced": [b * (b - 1), s * (s - 1)], "both_black": frac(bb),
                  "with_replacement": float(F(b, s) ** 2),
                  "both_white_unreduced": [w * (w - 1), s * (s - 1)],
                  "pair_unreduced": [b * (b - 1) + w * (w - 1), s * (s - 1)], "pair": float(bb + ww)}

    # section 4: the table — joint, marginal, conditional
    V["joint_bike_bus"] = CELLS["bike", "bus"] / n
    V["p_bike_given_bus"] = frac(F(CELLS["bike", "bus"], bus))              # hands-on

    # section 5: independence from the table
    V["glasses"], V["glasses_bus"] = GLASSES, GLASSES_BUS
    V["p_bus_given_glasses"] = GLASSES_BUS / GLASSES
    V["expected_bike_bus"] = bike * bus / n
    V["expected_glasses_bus"] = GLASSES * bus / n
    V["expected_nobike_bus"] = (n - bike) * bus / n                          # hands-on

    # section 6: Berkeley 1973
    dept = {}
    for d, (ma, mx, wa, wx) in BERKELEY.items():
        dept[d] = {"men_applied": ma, "men_rate": mx / ma, "women_applied": wa, "women_rate": wx / wa,
                   "all_rate": (mx + wx) / (ma + wa)}
    men_app = sum(v[0] for v in BERKELEY.values())
    wom_app = sum(v[2] for v in BERKELEY.values())
    V["berkeley"] = {
        "dept": dept, "men_applied": men_app, "women_applied": wom_app,
        "men_rate": sum(v[1] for v in BERKELEY.values()) / men_app,
        "women_rate": sum(v[3] for v in BERKELEY.values()) / wom_app,
        "women_higher": [d for d, v in dept.items() if v["women_rate"] > v["men_rate"]],
        "men_share_AB": (BERKELEY["A"][0] + BERKELEY["B"][0]) / men_app,
        "women_share_CEF": sum(BERKELEY[d][2] for d in "CEF") / wom_app,
        "pct": {d: [round(100 * v["men_rate"]), round(100 * v["women_rate"])] for d, v in dept.items()},
        "all_pct": {d: round(100 * v["all_rate"]) for d, v in dept.items()}}

    # section 7: total probability, a weighted average of the group answers
    V["plain_average"] = (V["p_bus_given_bike"] + V["p_bus_given_nobike"]) / 2
    V["total_terms"] = [V["p_bus_given_bike"] * V["p_bike"], V["p_bus_given_nobike"] * (1 - V["p_bike"])]
    V["total_bus"] = sum(V["total_terms"])
    V["total_nobus_terms"] = [(1 - V["p_bus_given_bike"]) * V["p_bike"],
                              (1 - V["p_bus_given_nobike"]) * (1 - V["p_bike"])]
    V["total_nobus"] = sum(V["total_nobus_terms"])                          # hands-on

    # section 8: Bayes on the students
    p_bus = F(bus, n)
    V["bayes_bike_given_bus"] = frac(pbb * pb / p_bus)
    V["bayes_nobike_given_bus"] = frac(pbn * (1 - pb) / p_bus)               # hands-on

    # section 9: the screening test
    V["screen"] = screen(10_000, 0.01)
    V["false_per_real"] = V["screen"]["false_pos"] / V["screen"]["ill"]
    V["healthy_per_ill"] = V["screen"]["healthy"] / V["screen"]["ill"]
    V["screen_1in10"] = screen(10_000, 0.10)                                 # hands-on

    # section 10: base rates
    V["screen_1in1000"] = screen(100_000, 0.001)
    V["base_marks"] = {"0.001": ppv(0.001), "0.01": ppv(0.01), "0.1": ppv(0.1)}
    V["acc_always_healthy"] = {"0.01": 1 - 0.01, "0.001": 1 - 0.001}         # hands-on: 1 in 1000
    V["base_curve"] = [[p / 1000, ppv(p / 1000)] for p in range(1, 201)]

    # narration draft 2: the lines added for depth
    V["die_p_even_given6"] = frac(F(1, DIE) / F(1, DIE))                     # §1 5a: six is always even
    V["p_bus_given_bike_frac"] = frac(F(CELLS["bike", "bus"], bike))         # §1 8a: one in four
    V["p_nobus_given_bike"] = CELLS["bike", "nobus"] / bike                  # §1 9a
    V["bike_quarter"] = int(bike * pbb)                                      # §2 5a: a quarter of sixty
    V["socks_pairs"] = {"all": math.comb(s, 2), "black": math.comb(b, 2),    # §3 4a
                        "share": frac(F(math.comb(b, 2), math.comb(s, 2)))}
    V["socks_big_drawer"] = {"black": 100 * b, "total": 100 * s,             # §3 6a
                             "p": F(100 * b, 100 * s) * F(100 * b - 1, 100 * s - 1)}
    V["socks_big_drawer"]["p"] = float(V["socks_big_drawer"]["p"])
    V["indep_product"] = bike * bus / n ** 2                                 # §5 6a: 0.6 × 0.45
    V["p_glasses"] = GLASSES / n                                             # §5 5a
    V["p_glasses_given_bus"] = GLASSES_BUS / bus
    V["berkeley_weighted"] = {                                               # §7 6a
        "men": sum(v["men_rate"] * v["men_applied"] for v in dept.values()) / men_app,
        "women": sum(v["women_rate"] * v["women_applied"] for v in dept.values()) / wom_app}
    sc = V["screen"]                                                         # §9 6a, 6b
    V["screen_bayes"] = {"joint": sc["ill"] / sc["tested"], "p_pos": sc["positives"] / sc["tested"],
                         "p_pos_total": 1 * 0.01 + FALSE_POS * (1 - 0.01), "sensitivity": 1.0}
    V["screen_bayes"]["ppv"] = V["screen_bayes"]["joint"] / V["screen_bayes"]["p_pos"]
    V["second_test_ppv"] = ppv(sc["ppv"])                                    # §10 4a: the posterior as prior
    V["screen_table"] = {"ill_pos": sc["ill"], "ill_neg": 0, "healthy_pos": sc["false_pos"],   # §10 5a
                         "healthy_neg": sc["healthy"] - sc["false_pos"]}
    return V


def figure_output():
    adv_ai = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
    r = subprocess.run([adv_ai, str(FIGURE_SCRIPT)], capture_output=True, text=True, cwd=REPO / "statistics")
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "l02_figures.txt").write_text(figure_output())
    (OUT / "l02_numbers.json").write_text(json.dumps(compute(), indent=1, ensure_ascii=False))
    print("wrote", OUT / "l02_figures.txt", "and", OUT / "l02_numbers.json")
