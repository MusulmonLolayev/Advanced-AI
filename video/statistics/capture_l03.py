"""Capture every number the Lecture 3 video speaks or shows.

Two sources, both computed rather than typed:
  * the figure script's own stdout (statistics/scripts/generate_discrete_rv_graphics.py),
    saved verbatim to raw/l03_figures.txt;
  * the slides' worked examples (two dice, pastries per order, the raffles, roulette, cup sizes,
    arrivals), computed here from their raw inputs.

`compute()` is pure, so test_l03.py can check every value against what the slides print.
Running this file writes raw/l03_numbers.json, which the video reads; the video types no number.
    uv run python statistics/capture_l03.py
    uv run python -m unittest discover -s statistics -p 'test_l03.py'
"""
import json
import os
import subprocess
from fractions import Fraction as F
from math import comb, exp, lgamma, log, sqrt
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "raw"
REPO = HERE.parents[1]
FIGURE_SCRIPT = REPO / "statistics/scripts/generate_discrete_rv_graphics.py"

# ─── raw inputs: the only typed numbers (all from the slides) ─────────────
DIE = 6
EXAMPLE_ROLL = (3, 4)                                  # the slide's example outcome: X = 7
MONOPOLY_ORANGE = (6, 9)                               # orange properties: 6 to 9 squares past Jail
HANDS_ON_SUM = 11                                      # section 1's pause
PASTRY = {0: F(7, 10), 1: F(2, 10), 2: F(1, 10)}      # pastries in one order
PASTRY_PRICE, COFFEE_PRICE = 2, 3                      # dollars
HANDS_ON_PRICE = 3                                     # section 6's pause: a $3 pastry
CUSTOMERS = 100
RAFFLE_TICKETS, RAFFLE_PRICE = 500, 2
RAFFLE_A = [(400, 1)]                                  # (prize, how many): one $400 bicycle
RAFFLE_B = [(8, 50)]                                   # fifty $8 prizes
ROULETTE_POCKETS, ROULETTE_RED = 37, 18
ROULETTE_N = (10, 100, 1000, 10000)
BANKROLL = 1000                                        # the doubling system's purse
BERNOULLI_GIRL = 0.49                                  # a newborn being a girl
BERNOULLI_COIN = 0.5                                   # a fair coin
BIN_TAIL_FROM = 6                                      # "six or more buy": the baker's sell-out
BIN_N, BIN_P = 10, F(3, 10)                            # next ten customers, any pastry
CUPS = {"small": F(2, 10), "medium": F(5, 10), "large": F(3, 10)}
CUP_CUSTOMERS, CUP_HANDS_ON = 10, 20
LAM = 4                                                # arrivals per ten minutes
DAY_WINDOWS = 60                                       # a ten-hour day
SIM_WINDOWS = 3000                                     # the figure's simulated windows
SECONDS = 600                                          # ten minutes split into seconds
RUSH = 8                                               # a window with 8 or more arrivals
FIRST_ORDERS = {"small": 1, "medium": 2, "large": 1}
DIRICHLET_SEEN = (4, 40)                               # orders "already seen" by the two priors
MORE_MEDIUM = 3
TEST_N, TEST_ACC = 100, F(9, 10)                       # section 8's AI use: 100 test examples, 90 % accuracy
# draft 2 (depth): the added lines' inputs
LONG_RUN_ROLLS = 36000                                 # §1 7a: two dice rolled this many times
CASINO_STAKES = 1_000_000                              # §5 3a: dollars bet at the table in all
SPREAD_BETS = (100, 10000)                             # §5 4a: expected balance against its spread
SMALL_N, SMALL_K = 3, 2                                # §8 3a: three customers, two buy
ANSWERS_N, ANSWERS_YES = 10, 3                         # §7 2a: ten answers, three yeses
WINDOW_MINUTES = (5, 60)                               # §10 2a: other windows than ten minutes


def frac(x):
    return [x.numerator, x.denominator]


def moments(pmf):
    """E, E[X^2], Var for {value: probability}, exactly."""
    e = sum(x * p for x, p in pmf.items())
    e2 = sum(x * x * p for x, p in pmf.items())
    return e, e2, e2 - e * e


def raffle(prizes):
    """The buyer's net gain as a PMF: win a prize having paid the ticket, or lose the ticket."""
    pmf, won = {}, 0
    for prize, k in prizes:
        pmf[prize - RAFFLE_PRICE] = pmf.get(prize - RAFFLE_PRICE, 0) + F(k, RAFFLE_TICKETS)
        won += k
    pmf[-RAFFLE_PRICE] = F(RAFFLE_TICKETS - won, RAFFLE_TICKETS)
    return pmf


def binom_pmf(k, n, p):
    return comb(n, k) * p ** k * (1 - p) ** (n - k)


def binom_tail_above(n, p, k0):
    """P(X > k0) for X ~ Binomial(n, p), summed in logs (n up to 10,000)."""
    lp, lq = log(p), log(1 - p)
    return sum(exp(lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1) + k * lp + (n - k) * lq)
               for k in range(k0 + 1, n + 1))


def poisson_pmf(k, lam):
    return exp(-lam + k * log(lam) - lgamma(k + 1))


def compute():
    V = {}
    # section 1: two dice, and pastries per order
    ways = {s: sum(1 for a in range(1, DIE + 1) for b in range(1, DIE + 1) if a + b == s) for s in range(2, 13)}
    V["dice_ways"] = ways
    V["dice_outcomes"] = DIE * DIE
    V["dice_p7"] = frac(F(ways[7], DIE * DIE))
    V["dice_p2"] = frac(F(ways[2], DIE * DIE))
    V["dice_7_vs_2"] = ways[7] // ways[2]
    V["dice_p11"] = frac(F(ways[HANDS_ON_SUM], DIE * DIE))            # hands-on
    V["hands_on_sum"] = HANDS_ON_SUM
    V["example_roll"], V["example_sum"] = list(EXAMPLE_ROLL), sum(EXAMPLE_ROLL)
    V["monopoly_orange"] = list(MONOPOLY_ORANGE)
    V["monopoly_orange_p"] = float(sum(F(ways[s], DIE * DIE) for s in range(MONOPOLY_ORANGE[0], MONOPOLY_ORANGE[1] + 1)))
    V["dice_mean"], _, dvar = [float(v) for v in moments({s: F(w, DIE * DIE) for s, w in ways.items()})]
    V["dice_var"] = float(F(sum(s * s * w for s, w in ways.items()), DIE * DIE) - 49)
    V["pastry_pmf"] = {str(k): float(p) for k, p in PASTRY.items()}
    V["pastry_sum"] = float(sum(PASTRY.values()))

    # section 2: expectation
    e, e2, var = moments(PASTRY)
    V["pastry_mean"], V["pastry_e2"], V["pastry_var"] = float(e), float(e2), float(var)
    V["pastry_sd"] = sqrt(var)
    V["customers"] = CUSTOMERS
    V["pastries_per_100"] = float(CUSTOMERS * e)
    V["die_sum"] = sum(range(1, DIE + 1))
    V["die_mean"] = float(F(sum(range(1, DIE + 1)), DIE))             # hands-on: 3.5
    for name, prizes in (("A", RAFFLE_A), ("B", RAFFLE_B)):
        pmf = raffle(prizes)
        m, m2, v = moments(pmf)
        V[f"raffle_{name}"] = {"pmf": {str(k): frac(p) for k, p in pmf.items()}, "mean": float(m),
                               "e2": float(m2), "var": float(v), "sd": sqrt(v)}
    V["raffle_tickets"], V["raffle_price"] = RAFFLE_TICKETS, RAFFLE_PRICE
    V["raffle_raised"] = RAFFLE_TICKETS * RAFFLE_PRICE
    V["raffle_kept"] = V["raffle_raised"] - sum(p * k for p, k in RAFFLE_A)
    V["raffle_A_prize"], V["raffle_B_prize"], V["raffle_B_count"] = RAFFLE_A[0][0], RAFFLE_B[0][0], RAFFLE_B[0][1]

    # section 3: the running sample mean (same generator and seed as the figure script)
    rng = np.random.default_rng(7)
    runs = []
    for _ in range(3):
        rolls = rng.integers(1, 7, size=2000)
        m = np.cumsum(rolls) / np.arange(1, 2001)
        runs.append({"after_10": round(float(m[9]), 3), "after_100": round(float(m[99]), 3),
                     "after_2000": round(float(m[-1]), 3), "curve": [round(float(x), 4) for x in m]})
    V["runs"] = runs
    V["run1_gap"] = {"after_10": runs[0]["after_10"] - V["die_mean"], "after_2000": runs[0]["after_2000"] - V["die_mean"]}

    # section 5: roulette, and the doubling system
    p_win = F(ROULETTE_RED, ROULETTE_POCKETS)
    V["roulette_red"], V["roulette_pockets"] = ROULETTE_RED, ROULETTE_POCKETS
    V["roulette_mean"] = float(p_win - (1 - p_win))                   # -1/37 per $1
    V["roulette_mean_frac"] = frac(p_win - (1 - p_win))
    V["roulette"] = {str(n): {"balance": n * V["roulette_mean"],
                              "p_ahead": binom_tail_above(n, float(p_win), n // 2)} for n in ROULETTE_N}
    stake, lost, k = 1, 0, 0
    while lost + stake <= BANKROLL:                                   # losses the purse can cover
        lost, stake, k = lost + stake, stake * 2, k + 1
    q = 1 - p_win
    ruin = q ** k
    V["martingale"] = {"bankroll": BANKROLL, "losses_covered": k, "lost_after": lost, "next_stake": stake,
                       "p_ruin": float(ruin), "one_in": round(1 / float(ruin)),
                       "mean": float((1 - ruin) * 1 - ruin * lost)}

    # section 6: shifting and scaling
    sd = sqrt(var)
    V["price"], V["coffee"] = PASTRY_PRICE, COFFEE_PRICE
    V["revenue_mean"], V["revenue_sd"] = float(PASTRY_PRICE * e), PASTRY_PRICE * sd
    V["revenue_var"] = float(PASTRY_PRICE ** 2 * var)
    V["bill_mean"], V["bill_var"] = float(PASTRY_PRICE * e + COFFEE_PRICE), float(PASTRY_PRICE ** 2 * var)
    V["hands_on_price"] = HANDS_ON_PRICE
    V["hands_on_mean"] = float(HANDS_ON_PRICE * e)
    V["hands_on_var"] = float(HANDS_ON_PRICE ** 2 * var)
    V["hands_on_sd"] = HANDS_ON_PRICE * sd
    V["z_mean"], V["z_var"] = 0.0, 1.0                                # (X - mu) / sigma, checked in the test

    # section 7: Bernoulli
    p_any = PASTRY[1] + PASTRY[2]
    V["bern_p"], V["bern_var"] = float(p_any), float(p_any * (1 - p_any))
    V["bern_max_var"] = 0.25
    V["bern_coin"] = BERNOULLI_COIN
    V["bern_girl"], V["bern_girl_var"] = BERNOULLI_GIRL, BERNOULLI_GIRL * (1 - BERNOULLI_GIRL)

    # section 8: Binomial
    pmf = [binom_pmf(k, BIN_N, BIN_P) for k in range(BIN_N + 1)]
    V["bin_n"], V["bin_p"] = BIN_N, float(BIN_P)
    V["bin_pmf"] = [float(x) for x in pmf]
    V["bin_mode"] = max(range(BIN_N + 1), key=lambda k: pmf[k])
    V["bin_comb3"] = comb(BIN_N, 3)
    V["bin_p3_parts"] = [float(BIN_P ** 3), float((1 - BIN_P) ** 7)]
    V["bin_mean"], V["bin_var"] = float(BIN_N * BIN_P), float(BIN_N * BIN_P * (1 - BIN_P))
    V["bin_sd"] = sqrt(V["bin_var"])
    V["bin_tail_from"] = BIN_TAIL_FROM
    V["bin_ge6"] = float(sum(pmf[BIN_TAIL_FROM:]))
    V["bin_p0"] = float(pmf[0])                                       # hands-on: nobody buys
    V["test_n"], V["test_acc"] = TEST_N, float(TEST_ACC)
    V["test_mean"], V["test_sd"] = float(TEST_N * TEST_ACC), sqrt(TEST_N * TEST_ACC * (1 - TEST_ACC))
    V["test_pmf"] = [binom_pmf(k, TEST_N, float(TEST_ACC)) for k in range(TEST_N + 1)]
    V["test_band"] = [V["test_mean"] - V["test_sd"], V["test_mean"] + V["test_sd"]]

    # section 9: Categorical and Multinomial
    V["cups"] = {k: float(p) for k, p in CUPS.items()}
    V["cup_customers"], V["cup_hands_on"] = CUP_CUSTOMERS, CUP_HANDS_ON
    V["cups_expected"] = {k: float(CUP_CUSTOMERS * p) for k, p in CUPS.items()}
    V["cups_expected_hands_on"] = {k: float(CUP_HANDS_ON * p) for k, p in CUPS.items()}

    # section 10: Poisson
    V["lam"] = LAM
    V["pois_pmf"] = [poisson_pmf(k, LAM) for k in range(13)]
    V["pois_p0"] = poisson_pmf(0, LAM)
    V["pois_empty_one_in"] = round(1 / V["pois_p0"])
    V["rush"] = RUSH
    V["pois_rush"] = 1 - sum(poisson_pmf(k, LAM) for k in range(RUSH))
    V["day_windows"] = DAY_WINDOWS
    V["day_rushes"] = DAY_WINDOWS * V["pois_rush"]
    V["day_empty"] = DAY_WINDOWS * V["pois_p0"]                      # hands-on
    # the figure's 3000 simulated windows (same generator and seed as the figure script)
    rng = np.random.default_rng(21)
    gaps = rng.exponential(scale=1.0 / LAM, size=int(LAM * SIM_WINDOWS * 1.6))
    times = np.cumsum(gaps)
    times = times[times < SIM_WINDOWS]
    counts = np.bincount(times.astype(int), minlength=SIM_WINDOWS)[:SIM_WINDOWS]
    V["pois_sim"] = {"windows": SIM_WINDOWS, "arrivals": int(len(times)), "mean": float(counts.mean()),
                     "var": float(counts.var(ddof=1)), "freq": [float((counts == k).mean()) for k in range(13)]}
    p_sec = F(LAM, SECONDS)
    V["seconds"], V["p_second"] = SECONDS, frac(p_sec)
    V["bin600_pmf"] = [binom_pmf(k, SECONDS, float(p_sec)) for k in range(13)]
    V["bin_vs_pois"] = max(abs(binom_pmf(k, SECONDS, float(p_sec)) - poisson_pmf(k, LAM)) for k in range(SECONDS + 1))

    # section 11: Dirichlet
    total = sum(FIRST_ORDERS.values())
    V["first_orders"] = FIRST_ORDERS
    V["first_shares"] = {k: v / total for k, v in FIRST_ORDERS.items()}
    V["alphas"] = {str(s): [float(s * p) for p in CUPS.values()] for s in DIRICHLET_SEEN}
    a = [float(DIRICHLET_SEEN[0] * p) for p in CUPS.values()]
    a[1] += MORE_MEDIUM
    V["more_medium"] = MORE_MEDIUM
    V["alpha_updated"] = a
    V["alpha_updated_mean"] = [x / sum(a) for x in a]
    rng = np.random.default_rng(5)
    base = np.array([float(p) for p in CUPS.values()])
    V["dirichlet_draws"] = {str(s): np.round(rng.dirichlet(base * s, size=6), 3).tolist() for s in DIRICHLET_SEEN}
    V.update(draft2(V))
    return V


def draft2(V):
    """Numbers of the lines added for depth (narration draft 2)."""
    D = {}
    e, _, var = moments(PASTRY)
    sd = sqrt(var)
    # §1 3a: one roll, several random variables (sum, the larger die, "a six?" as 1/0)
    a, b = EXAMPLE_ROLL
    D["roll_vars"] = {"sum": a + b, "max": max(a, b), "six": int(DIE in (a, b))}
    # §1 7a: a probability read as a long-run share
    D["long_run_rolls"] = LONG_RUN_ROLLS
    D["long_run_sevens"] = float(LONG_RUN_ROLLS * F(V["dice_ways"][7], DIE * DIE))
    D["long_run_twos"] = float(LONG_RUN_ROLLS * F(V["dice_ways"][2], DIE * DIE))
    # §2 3a: one hundred imagined customers in the shares of the PMF
    crowd = {k: int(CUSTOMERS * p) for k, p in PASTRY.items()}
    D["crowd"] = {str(k): n for k, n in crowd.items()}
    D["crowd_pastries"] = sum(k * n for k, n in crowd.items())
    D["crowd_mean"] = D["crowd_pastries"] / CUSTOMERS
    # §2 7a: what the school keeps per ticket
    D["kept_per_ticket"] = V["raffle_kept"] / RAFFLE_TICKETS
    # §4 3a: the variance by its definition, and the two-pastry order's share of it
    parts = {k: float((k - e) ** 2 * p) for k, p in PASTRY.items()}
    D["var_parts"] = {str(k): v for k, v in parts.items()}
    D["var_by_definition"] = sum(parts.values())
    D["var_share_two"] = parts[2] / float(var)
    # §4 6a: how much of the first raffle's variance the one winning ticket carries
    ra = raffle(RAFFLE_A)
    m, _, v = moments(ra)
    win = RAFFLE_A[0][0] - RAFFLE_PRICE
    D["raffle_A_win_share"] = float((win - m) ** 2 * ra[win] / v)
    # §5 1a: red wins 18 of 37, loses 19 of 37
    D["roulette_lose"] = ROULETTE_POCKETS - ROULETTE_RED
    D["roulette_edge_pockets"] = D["roulette_lose"] - ROULETTE_RED
    # §5 3a: the casino's side of a million dollars bet
    D["casino_stakes"] = CASINO_STAKES
    D["casino_keeps"] = CASINO_STAKES / ROULETTE_POCKETS
    # §5 4a: the expected balance grows like n, its spread like the square root of n
    p_win = F(ROULETTE_RED, ROULETTE_POCKETS)
    bet_var = 1 - float(p_win - (1 - p_win)) ** 2                    # E[X^2] = 1 for a +-1 bet
    D["bet_var"] = bet_var
    D["spread"] = {str(n): {"balance": n * V["roulette_mean"], "sd": sqrt(n * bet_var)} for n in SPREAD_BETS}
    # §6 2a: doubling every value quadruples the variance
    D["revenue_var_ratio"] = V["revenue_var"] / float(var)
    # §6 6a: standardized values of the pastry counts
    D["z_pastry"] = {str(k): (k - float(e)) / sd for k in PASTRY}
    # §7 2a: the mean of 0/1 answers is the share of yeses
    answers = [1] * ANSWERS_YES + [0] * (ANSWERS_N - ANSWERS_YES)
    D["answers"] = answers
    D["answers_mean"] = sum(answers) / len(answers)
    # §8 3a: orders of the yeses
    D["small_orders"] = comb(SMALL_N, SMALL_K)
    D["small_n"], D["small_k"] = SMALL_N, SMALL_K
    # §8 5a: the binomial as a sum of ten Bernoullis
    D["bin_sum_mean"] = BIN_N * V["bern_p"]
    D["bin_sum_var"] = BIN_N * V["bern_var"]
    # §9 2a: two answers, medium or not, is a Bernoulli
    D["medium_or_not"] = float(CUPS["medium"])
    # §9 4a: the medium count alone is binomial
    D["medium_count_mean"] = float(CUP_CUSTOMERS * CUPS["medium"])
    # §10 2a: the rate scales with the window
    D["window_minutes"] = list(WINDOW_MINUTES)
    D["window_lam"] = [LAM * w / 10 for w in WINDOW_MINUTES]
    # §10 5a: three and four are the most likely counts, neither common
    D["pois_p3"], D["pois_p4"] = poisson_pmf(3, LAM), poisson_pmf(4, LAM)
    D["pois_p4_one_in"] = round(1 / D["pois_p4"])
    # §11 5a: the Dirichlet's mean is alpha over its total
    D["dirichlet_means"] = {s: [x / sum(al) for x in al] for s, al in V["alphas"].items()}
    D["dirichlet_totals"] = {s: sum(al) for s, al in V["alphas"].items()}
    return D


def figure_output():
    adv_ai = os.environ.get("ADV_AI_PYTHON", str(Path.home() / ".conda/envs/adv_ai/bin/python3"))
    r = subprocess.run([adv_ai, str(FIGURE_SCRIPT)], capture_output=True, text=True, cwd=REPO / "statistics")
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "l03_figures.txt").write_text(figure_output())
    (OUT / "l03_numbers.json").write_text(json.dumps(compute(), indent=1, ensure_ascii=False))
    print("wrote raw/l03_figures.txt and raw/l03_numbers.json")
