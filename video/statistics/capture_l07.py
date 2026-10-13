"""Capture every number the Lecture 7 video speaks or shows.

Two sources, both computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_information_theory_graphics.py),
    saved verbatim to raw/l07_figures.txt;
  * the slides' worked examples (a year of weather in one town, three forecasters, the 7:40 bus of
    Lecture 6, three morning questions about rain), computed here from their raw inputs. The 100 bus
    mornings are Lecture 6's, regenerated from the same seed.

`compute()` is pure, so test_l07.py can check every value against what the slides print.
Running this file writes raw/l07_numbers.json, which the video reads; the video types no number.
    uv run python statistics/capture_l07.py
    uv run python -m unittest discover -s statistics -p 'test_l07.py'
"""
import json
import os
import subprocess
from math import log, log2
from pathlib import Path

import numpy as np
from scipy.special import betaln, digamma

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
FIGURE_SCRIPT = REPO / "statistics/scripts/generate_information_theory_graphics.py"

# ─── raw inputs: the only typed numbers (all from the slides) ─────────────
LABELS = ("sunny", "cloudy", "rain", "storm")
DAYS = (180, 90, 45, 45)                       # 360 logged days
QUESTION_ORDER = (0, 1, 2, 3)                  # the slide's tree asks sunny?, cloudy?, rain?
BAD_ORDER = (3, 2, 1, 0)                       # section 2's pause: storm? first
FORECASTERS = {"climate": None,                # None: the true climate itself
               "uniform": (0.25, 0.25, 0.25, 0.25),
               "sunny": (0.90, 0.05, 0.04, 0.01)}
SWAP = (0.5, 0.125, 0.25, 0.125)               # section 6's pause: cloudy and rain swapped
THREE = (0.5, 0.25, 0.25)                      # section 3's pause
BINARY = (0.5, 0.4, 0.25, 0.11, 0.89, 0.1, 0.01, 0.7)
LABEL_TRUE, MODEL_P = 1, 0.9                   # Lecture 5's one example (section 5's pause)
NOISY_LABELS = 0.7                             # identical pixels, labels 70/30
BUS_SEED, BUS_RATE, BUS_DAYS, BUS_PRIOR = 21, 0.70, 100, (8, 2)   # Lecture 6's 7:40 bus
BUS_SHOWN = (0, 1, 10, 30, 100)
QUESTIONS = {"grey": (0.80, 0.20),             # P(yes | wet), P(yes | dry)
             "wind": (0.60, 0.40),
             "even": (0.50, 0.50)}


def H(p):
    return float(sum(x * log2(1 / x) for x in p if x > 0))


def cross(p, q):
    return float(-sum(a * log2(b) for a, b in zip(p, q) if a > 0))


def kl(p, q):
    return cross(p, q) - H(p)


def kl_beta_bits(a1, b1, a0, b0):
    nats = (betaln(a0, b0) - betaln(a1, b1) + (a1 - a0) * digamma(a1) + (b1 - b0) * digamma(b1)
            + (a0 - a1 + b0 - b1) * digamma(a1 + b1))
    return float(nats / log(2))


def tree_questions(p, order):
    """Questions each outcome costs when the tree asks about the outcomes in `order`, one at a time;
    the last two share the final question."""
    cost = [0] * len(p)
    for depth, i in enumerate(order):
        cost[i] = min(depth + 1, len(p) - 1)
    return cost


def compute():
    V = {}
    n = sum(DAYS)
    p = [d / n for d in DAYS]
    V["days"], V["n_days"], V["p"] = list(DAYS), n, p

    # section 1: four equally likely outcomes need two questions every time
    V["uniform_questions"] = log2(4)

    # section 2: the question tree
    q_good = tree_questions(p, QUESTION_ORDER)
    V["questions"] = q_good
    V["avg_questions"] = sum(a * b for a, b in zip(p, q_good))
    q_bad = tree_questions(p, BAD_ORDER)
    V["bad_questions"], V["avg_bad"] = q_bad, sum(a * b for a, b in zip(p, q_bad))
    V["bad_extra"] = V["avg_bad"] - V["avg_questions"]
    V["questions_360"] = sum(d * c for d, c in zip(DAYS, q_good))

    # section 3: surprise and entropy
    V["surprise"] = [log2(1 / x) for x in p]
    V["H"], V["H_uniform"], V["H_certain"] = H(p), H([0.25] * 4), H([1.0])
    V["climate_worth"] = V["H_uniform"] - V["H"]
    V["climate_worth_360"] = n * V["climate_worth"]
    V["log2_8"] = log2(8)
    V["sunny_then_storm"] = {"prob": p[0] * p[3], "bits": log2(1 / (p[0] * p[3]))}
    V["ten_heads"] = {"prob": 0.5 ** 10, "bits": 10 * log2(2)}
    V["H_three"] = H(THREE)

    # section 4: binary entropy
    V["binary"] = {str(x): H([x, 1 - x]) for x in BINARY}
    V["dry_surprise_quarter"] = log2(1 / 0.75)                  # section 4's pause: rain 1/4, dry 3/4
    V["gain_05_04"] = V["binary"]["0.5"] - V["binary"]["0.4"]
    V["gain_01_001"] = V["binary"]["0.1"] - V["binary"]["0.01"]
    V["binary_curve"] = [[float(x), H([x, 1 - x])] for x in np.linspace(0.001, 0.999, 999)]

    # section 5: cross-entropy, three forecasters, nats, the floor
    V["forecasters"] = {}
    for name, q in FORECASTERS.items():
        q = p if q is None else list(q)
        V["forecasters"][name] = {"q": q, "cross": cross(p, q), "kl": kl(p, q), "cross_360": n * cross(p, q),
                                  "surprise": [log2(1 / x) for x in q]}
    V["waste_360_uniform"] = V["forecasters"]["uniform"]["cross_360"] - V["forecasters"]["climate"]["cross_360"]
    V["ln2"] = log(2)
    V["H_nats"] = V["H"] * log(2)
    V["one_example"] = {"bits": -log2(MODEL_P), "nats": -log(MODEL_P)}
    V["floor_noisy"] = H([NOISY_LABELS, 1 - NOISY_LABELS])

    # section 6: KL divergence
    V["swap"] = {"q": list(SWAP), "cross": cross(p, SWAP), "kl": kl(p, SWAP)}
    V["kl_terms_sunny"] = [a * log2(a / b) for a, b in zip(p, FORECASTERS["sunny"])]

    # section 7: how much did the hundred mornings say (Lecture 6's bus)
    rng = np.random.default_rng(BUS_SEED)
    on_time = rng.random(BUS_DAYS) < BUS_RATE
    a0, b0 = BUS_PRIOR
    V["bus_kl"] = {}
    for m in BUS_SHOWN:
        k = int(on_time[:m].sum())
        V["bus_kl"][str(m)] = {"on_time": k, "post": [a0 + k, b0 + m - k],
                               "kl": kl_beta_bits(a0 + k, b0 + m - k, a0, b0)}
    V["bus_kl_path"] = [kl_beta_bits(a0 + int(on_time[:m].sum()), b0 + m - int(on_time[:m].sum()), a0, b0)
                        for m in range(BUS_DAYS + 1)]
    V["bus_kl_late_10_100"] = V["bus_kl"]["100"]["kl"] - V["bus_kl"]["10"]["kl"]
    V["bus_prior_worth"] = a0 + b0

    # section 8: not a distance
    s = list(FORECASTERS["sunny"])
    V["kl_p_sunny"], V["kl_sunny_p"] = kl(p, s), kl(s, p)
    V["kl_p_uniform"], V["kl_uniform_p"] = kl(p, [0.25] * 4), kl([0.25] * 4, p)

    # sections 9-10: mutual information of three morning questions
    wet = p[2] + p[3]
    V["p_wet"], V["H_wet"] = wet, H([wet, 1 - wet])
    V["mi"] = {}
    for name, (yw, yd) in QUESTIONS.items():
        joint = np.array([[wet * yw, wet * (1 - yw)], [(1 - wet) * yd, (1 - wet) * (1 - yd)]])
        ans = joint.sum(axis=0)
        h_cond = sum(a * H([joint[0, j] / a, 1 - joint[0, j] / a]) for j, a in enumerate(ans))
        prod = np.outer(joint.sum(axis=1), ans)
        h_x = H(ans)
        h_x_given_y = sum(r * H(joint[i] / r) for i, r in enumerate(joint.sum(axis=1)))
        V["mi"][name] = {"p_yes": float(ans[0]), "wet_if_yes": float(joint[0, 0] / ans[0]),
                         "wet_if_no": float(joint[0, 1] / ans[1]), "H_cond": float(h_cond),
                         "I": float(V["H_wet"] - h_cond),
                         "I_as_kl": float((joint * np.log2(joint / prod)).sum()),
                         "I_reverse": float(h_x - h_x_given_y),
                         "joint_wet_yes": float(joint[0, 0]), "product_wet_yes": float(prod[0, 0])}
    V["mi_grey_over_wind"] = V["mi"]["grey"]["I"] / V["mi"]["wind"]["I"]
    V["mi_grey_share"] = V["mi"]["grey"]["I"] / V["H_wet"]
    return V


def figure_output():
    adv_ai = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
    r = subprocess.run([adv_ai, str(FIGURE_SCRIPT)], capture_output=True, text=True, cwd=REPO / "statistics")
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "l07_figures.txt").write_text(figure_output())
    (OUT / "l07_numbers.json").write_text(json.dumps(compute(), indent=1, ensure_ascii=False))
    print("wrote raw/l07_figures.txt and raw/l07_numbers.json")
