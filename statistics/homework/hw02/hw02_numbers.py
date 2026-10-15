"""Homework 2 (Lecture 2: conditional probability, independence, Bayes): every number the sheet prints and the key uses.

The sheet's data are the inputs here; every answer is computed from them, never typed. Writes
  hw02_data.tex            -- the data the student sheet prints (committed)
  ../keys/hw02_answers.tex -- the answers, as LaTeX macros for the key (git-ignored)
  ../keys/hw02_answers.json

    python3 statistics/homework/hw02/hw02_numbers.py
"""
import itertools
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from hwlib import jsonable, listing, macro, num, write_answers  # noqa: E402

KEYS = HERE.parent / "keys"

# ─── the data printed on the sheet ──────────────────────────────────────────
MACHINES = {"M1": (F(70, 100), F(2, 100)), "M2": (F(30, 100), F(5, 100))}   # share of output, defect rate (2, 6)
ITEMS = 1000                                                                  # task 2: per 1,000 items
RED, BLUE = 5, 3                                                              # task 3: balls in the bag
ATTEND = {"attended": (102, 18), "did not": (44, 36)}                         # task 4: (passed, failed)
SESSION = {"morning": (73, 27), "afternoon": (73, 27)}                        # task 4: (passed, failed)
HOSPITALS = {"A": {"easy": (200, 190), "hard": (50, 30)},                      # task 5: (operations, survived)
             "B": {"easy": (50, 49), "hard": (200, 130)}}
BASE, SENS, FALSE_POS, PEOPLE = F(2, 1000), F(95, 100), F(3, 100), 100_000     # task 6b
SPAM, FREE_SPAM, FREE_HAM = F(40, 100), F(30, 100), F(2, 100)                  # task 6c: P(spam), P("free" | ...)
MATCH = F(1, 1_000_000)                                                       # task 7a
ACCURACY = F(99, 100)                                                         # task 7d
SOCKS_BLACK, SOCKS_WHITE = 6, 4                                               # task 7c and challenge (e)


def compute():
    a = {}
    # task 1: conditioning shrinks the sample space
    die = range(1, 7)
    odd = [d for d in die if d % 2]
    a["p_ge5_given_odd"] = F(sum(d >= 5 for d in odd), len(odd))
    a["p_ge5"] = F(sum(d >= 5 for d in die), 6)
    faces = 12                                                                 # J, Q, K in four suits
    a["p_king_given_face"] = F(4, faces)
    a["p_face_given_king"] = F(4, 4)
    rolls = list(itertools.product(die, repeat=2))
    sum8 = [r for r in rolls if sum(r) == 8]
    first3 = [r for r in rolls if r[0] == 3]
    a["p_sum8_given_first3"] = F(sum(sum(r) == 8 for r in first3), len(first3))
    a["p_first3_given_sum8"] = F(sum(r[0] == 3 for r in sum8), len(sum8))
    a["p_double_given_sum8"] = F(sum(r[0] == r[1] for r in sum8), len(sum8))
    a["n_sum8"] = len(sum8)
    a["p_sum8"] = F(len(sum8), 36)
    # task 2: the tree
    for m, (share, bad) in MACHINES.items():
        k = m.lower()
        a[f"p_{k}_def"] = share * bad
        a[f"p_{k}_ok"] = share * (1 - bad)
        a[f"n_{k}_def"] = share * bad * ITEMS
        a[f"n_{k}_ok"] = share * (1 - bad) * ITEMS
    a["tree_total"] = sum(a[f"p_{m.lower()}_{s}"] for m in MACHINES for s in ("def", "ok"))
    # task 3: without replacement
    n = RED + BLUE
    a["p_rr"] = F(RED, n) * F(RED - 1, n - 1)
    a["p_bb"] = F(BLUE, n) * F(BLUE - 1, n - 1)
    a["p_same"] = a["p_rr"] + a["p_bb"]
    a["p_second_red"] = F(RED, n) * F(RED - 1, n - 1) + F(BLUE, n) * F(RED, n - 1)
    a["p_rr_repl"] = F(RED, n) ** 2
    # task 4: contingency tables
    for name, table in (("att", ATTEND), ("ses", SESSION)):
        rows = list(table.values())
        total = sum(sum(r) for r in rows)
        passed = sum(r[0] for r in rows)
        a[f"{name}_total"], a[f"{name}_passed"] = total, passed
        a[f"{name}_p_pass"] = F(passed, total)
        for (g, (p, f)), k in zip(table.items(), ("one", "two")):
            a[f"{name}_{k}_n"] = p + f
            a[f"{name}_{k}_p_pass"] = F(p, p + f)
            a[f"{name}_{k}_expected"] = F((p + f) * passed, total)
            a[f"{name}_{k}_joint"] = F(p, total)
        a[f"{name}_indep"] = all(F(p, p + f) == F(passed, total) for p, f in rows)
    a["att_p_attended_given_pass"] = F(ATTEND["attended"][0], a["att_passed"])
    # task 5: Simpson
    for h, ops in HOSPITALS.items():
        k = h.lower()
        for kind, (n_ops, ok) in ops.items():
            a[f"h{k}_{kind}"] = F(ok, n_ops)
        a[f"h{k}_ops"] = sum(o for o, _ in ops.values())
        a[f"h{k}_ok"] = sum(s for _, s in ops.values())
        a[f"h{k}_all"] = F(a[f"h{k}_ok"], a[f"h{k}_ops"])
    a["b_better_each"] = all(a[f"hb_{t}"] > a[f"ha_{t}"] for t in ("easy", "hard"))
    a["a_better_pooled"] = a["ha_all"] > a["hb_all"]
    a["ha_hard_share"] = F(HOSPITALS["A"]["hard"][0], a["ha_ops"])
    a["hb_hard_share"] = F(HOSPITALS["B"]["hard"][0], a["hb_ops"])
    # task 6a: which machine made a defective item?
    a["p_def"] = sum(s * b for s, b in MACHINES.values())
    a["p_m2_given_def"] = MACHINES["M2"][0] * MACHINES["M2"][1] / a["p_def"]
    a["p_m1_given_def"] = 1 - a["p_m2_given_def"]
    # task 6b: screening in natural frequencies, then a second independent test
    ill = BASE * PEOPLE
    a["n_ill"], a["n_healthy"] = ill, PEOPLE - ill
    a["n_true_pos"] = SENS * ill
    a["n_false_pos"] = FALSE_POS * (PEOPLE - ill)
    a["n_pos"] = a["n_true_pos"] + a["n_false_pos"]
    a["p_ill_given_pos"] = a["n_true_pos"] / a["n_pos"]
    p = a["p_ill_given_pos"]
    a["p_ill_given_two_pos"] = SENS * p / (SENS * p + FALSE_POS * (1 - p))
    a["lr"] = SENS / FALSE_POS
    a["prior_odds"] = BASE / (1 - BASE)
    a["post_odds_one"] = a["prior_odds"] * a["lr"]
    a["post_odds_two"] = a["prior_odds"] * a["lr"] ** 2
    # task 6c: the spam word
    a["p_free"] = FREE_SPAM * SPAM + FREE_HAM * (1 - SPAM)
    a["p_spam_given_free"] = FREE_SPAM * SPAM / a["p_free"]
    # task 8d: Monty Hall, by enumerating the prize door and the host's choice (you always pick door 1)
    paths = []                                                                # (probability, prize door, opened)
    for prize in (1, 2, 3):
        options = [d for d in (2, 3) if d != prize]                          # the host never opens the prize
        paths += [(F(1, 3) / len(options), prize, d) for d in options]
    opened3 = [(w, prize) for w, prize, d in paths if d == 3]
    a["p_switch_wins"] = sum(w for w, prize in opened3 if prize == 2) / sum(w for w, _ in opened3)
    a["p_stay_wins"] = 1 - a["p_switch_wins"]
    # task 7
    a["err_socks_wrong"] = F(SOCKS_BLACK, SOCKS_BLACK + SOCKS_WHITE) ** 2
    a["err_socks_ok"] = F(SOCKS_BLACK, SOCKS_BLACK + SOCKS_WHITE) * F(SOCKS_BLACK - 1, SOCKS_BLACK + SOCKS_WHITE - 1)
    a["err_total_wrong"] = (a["att_one_p_pass"] + a["att_two_p_pass"]) / 2
    a["err_total_ok"] = a["att_p_pass"]
    a["err_wrong_denominator"] = F(ATTEND["attended"][0], a["att_passed"])        # P(attended | pass), mistaken
    # challenge (e): chain rule, three black socks
    b, t = SOCKS_BLACK, SOCKS_BLACK + SOCKS_WHITE
    a["p_three_black"] = F(b, t) * F(b - 1, t - 1) * F(b - 2, t - 2)
    return a


def data_tex():
    m1, m2 = MACHINES["M1"], MACHINES["M2"]
    pct = lambda f: num(f * 100)
    rows = []
    for name, table in (("Att", ATTEND), ("Ses", SESSION)):
        for (g, (p, f)), k in zip(table.items(), ("One", "Two")):
            rows += [macro(f"hw{name}{k}Pass", p), macro(f"hw{name}{k}Fail", f)]
    hosp = []
    for h, ops in HOSPITALS.items():
        for kind, (n_ops, ok) in ops.items():
            hosp += [macro(f"hwH{h}{kind.capitalize()}N", n_ops), macro(f"hwH{h}{kind.capitalize()}S", ok)]
    return "% generated by hw02_numbers.py -- do not edit\n" + "".join([
        macro("hwMOneShare", pct(m1[0])), macro("hwMOneDef", pct(m1[1])),
        macro("hwMTwoShare", pct(m2[0])), macro("hwMTwoDef", pct(m2[1])), macro("hwItems", num(ITEMS)),
        macro("hwRed", RED), macro("hwBlue", BLUE), *rows, *hosp,
        macro("hwBaseN", num(BASE * 1000)), macro("hwSens", pct(SENS)), macro("hwFalsePos", pct(FALSE_POS)),
        macro("hwPeople", num(PEOPLE)),
        macro("hwSpam", pct(SPAM)), macro("hwFreeSpam", pct(FREE_SPAM)), macro("hwFreeHam", pct(FREE_HAM)),
        macro("hwMatch", num(1 / MATCH)), macro("hwAccuracy", pct(ACCURACY)),
        macro("hwSockB", SOCKS_BLACK), macro("hwSockW", SOCKS_WHITE), macro("hwSockT", SOCKS_BLACK + SOCKS_WHITE),
        macro("hwErrTotalWrong", num(F(sum(F(p, p + f) for p, f in ATTEND.values()), 2))),
        macro("hwAttOneRate", num(F(ATTEND["attended"][0], sum(ATTEND["attended"])))),
        macro("hwAttTwoRate", num(F(ATTEND["did not"][0], sum(ATTEND["did not"])))),
    ])


def main():
    a = compute()
    (HERE / "hw02_data.tex").write_text(data_tex())
    KEYS.mkdir(exist_ok=True)
    write_answers(a, KEYS / "hw02_answers.tex", KEYS / "hw02_answers.json", "generated by hw02_numbers.py")
    print(f"{len(a)} answers -> {KEYS / 'hw02_answers.tex'}")


if __name__ == "__main__":
    main()
