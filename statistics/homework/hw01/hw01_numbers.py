"""Homework 1 (Lecture 1: data, descriptive statistics, probability): every number the sheet prints and the key uses.

The sheet's data are the inputs here; every answer is computed from them, never typed. Writes
  hw01_data.tex            -- the data the student sheet prints (committed)
  ../keys/hw01_answers.tex -- the answers, as LaTeX macros for the key (git-ignored: students never see them)
  ../keys/hw01_answers.json
Conventions follow the lecture: sample variance divides by n - 1; the median is the ((n+1)/2)-th sorted value
(n odd) or the mean of the two middle ones; Q1 / Q3 are the medians of the lower / upper half, leaving the median
out when n is odd; outliers lie beyond Q1 - 1.5 IQR or Q3 + 1.5 IQR.

    python3 statistics/homework/hw01/hw01_numbers.py
"""
import json
import math
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).parent
KEYS = HERE.parent / "keys"

# ─── the data printed on the sheet ──────────────────────────────────────────
RENTS = [510, 450, 1450, 420, 560, 470, 450, 530, 480]          # monthly rent of 9 flats, $ (task 2)
DELIVERY_A = [23, 27, 25, 24, 26]                                # delivery minutes, service A (task 3)
DELIVERY_B = [15, 35, 20, 30, 25]                                # service B
SCORES = [63, 41, 75, 58, 98, 52, 70, 61, 55, 72, 66]            # exam scores of 11 students (task 4)
ERROR_DATA = [2, 4, 6, 8]                                        # the worked solution's data (task 7)
STAFF, STAFF_PAY, OWNER_PAY = 49, 1200, 380000                   # task 8: 49 employees and the owner, $ a month
BIRTHDAY_N = (5, 30)                                             # task 6e


def mean(x):
    return Fraction(sum(x), len(x))


def median(x):
    s, n = sorted(x), len(x)
    return Fraction(s[n // 2]) if n % 2 else Fraction(s[n // 2 - 1] + s[n // 2], 2)


def quartiles(x):
    s, n = sorted(x), len(x)
    lower, upper = s[: n // 2], s[(n + 1) // 2:]
    return median(lower), median(upper)


def var(x, ddof=1):
    m = mean(x)
    return sum((v - m) ** 2 for v in x) / (len(x) - ddof)


def mode(x):
    counts = {v: x.count(v) for v in x}
    best = max(counts.values())
    return sorted(v for v, c in counts.items() if c == best)


def p_share(n):
    """P(at least two of n people share a birthday), 365 equally likely days."""
    p_diff = Fraction(1)
    for k in range(1, n):
        p_diff *= Fraction(365 - k, 365)
    return 1 - p_diff


def compute():
    a = {}
    # task 2: centre
    a["rent_sorted"] = sorted(RENTS)
    a["rent_sum"] = sum(RENTS)
    a["rent_mean"] = mean(RENTS)
    a["rent_median"] = median(RENTS)
    a["rent_mode"] = mode(RENTS)
    rest = [r for r in RENTS if r != max(RENTS)]
    a["rent_rest_mean"] = mean(rest)
    a["rent_rest_median"] = median(rest)
    a["rent_rank_of_mean"] = sum(r < a["rent_mean"] for r in RENTS)       # flats cheaper than the mean
    # task 3: spread
    for k, x in (("a", DELIVERY_A), ("b", DELIVERY_B)):
        m = mean(x)
        a[f"del_{k}_mean"] = m
        a[f"del_{k}_dev"] = [v - m for v in x]
        a[f"del_{k}_ss"] = sum((v - m) ** 2 for v in x)
        a[f"del_{k}_var"] = var(x)
        a[f"del_{k}_sd"] = math.sqrt(var(x))
    a["del_sum"] = sum(DELIVERY_A)
    a["del_b_sum_sq"] = sum(v * v for v in DELIVERY_B)                     # challenge (b)
    # task 4: five-number summary
    q1, q3 = quartiles(SCORES)
    iqr = q3 - q1
    lo, hi = q1 - Fraction(3, 2) * iqr, q3 + Fraction(3, 2) * iqr
    a["sc_sorted"] = sorted(SCORES)
    a["sc_min"], a["sc_max"] = min(SCORES), max(SCORES)
    a["sc_median"], a["sc_q1"], a["sc_q3"], a["sc_iqr"] = median(SCORES), q1, q3, iqr
    a["sc_lo_fence"], a["sc_hi_fence"] = lo, hi
    a["sc_outliers"] = [v for v in SCORES if v < lo or v > hi]
    inside = [v for v in SCORES if lo <= v <= hi]
    a["sc_whisker_lo"], a["sc_whisker_hi"] = min(inside), max(inside)
    # task 6: probability rules
    a["p_red_or_queen"] = Fraction(26 + 4 - 2, 52)
    dice = [(i, j) for i in range(1, 7) for j in range(1, 7)]
    a["p_sum7"] = Fraction(sum(i + j == 7 for i, j in dice), 36)
    a["p_sum_ge10"] = Fraction(sum(i + j >= 10 for i, j in dice), 36)
    a["cells_with_six"] = sum(6 in d for d in dice)
    a["p_atleast_one6_two"] = Fraction(a["cells_with_six"], 36)
    a["p_atleast_one6_four"] = 1 - Fraction(5, 6) ** 4
    die = range(1, 7)
    ev = {"A": {2, 4, 6}, "B": {1, 2, 3}, "C": {1, 2, 3, 4}, "D": {1, 3, 5}}
    p = {k: Fraction(len(s), 6) for k, s in ev.items()}
    for k in ("B", "C", "D"):
        both = Fraction(len(ev["A"] & ev[k]), 6)
        a[f"p_A{k}"], a[f"pp_A{k}"] = both, p["A"] * p[k]
        a[f"indep_A{k}"] = both == p["A"] * p[k]
        a[f"excl_A{k}"] = both == 0
    assert set(die) == ev["A"] | ev["D"]
    for n in BIRTHDAY_N:
        a[f"p_share_{n}"] = p_share(n)
    # task 7: the worked solution's mistakes
    a["err_ss"] = sum((v - mean(ERROR_DATA)) ** 2 for v in ERROR_DATA)
    a["err_var_by_n"] = var(ERROR_DATA, ddof=0)
    a["err_var_ok"] = var(ERROR_DATA)
    a["err_p_wrong"], a["err_p_ok"] = Fraction(13 + 4, 52), Fraction(13 + 4 - 1, 52)
    # task 8: the salary story
    pay = [STAFF_PAY] * STAFF + [OWNER_PAY]
    a["pay_mean"], a["pay_median"] = mean(pay), median(pay)
    return a


# ─── LaTeX output ───────────────────────────────────────────────────────────
def num(v, nd=2):
    """A number as the key prints it: integers plain, fractions as decimals with nd places."""
    if isinstance(v, Fraction) and v.denominator == 1:
        v = v.numerator
    if isinstance(v, int):
        return f"{v:,}".replace(",", "{,}")
    return f"{float(v):,.{nd}f}".replace(",", "{,}")


def frac(v):
    return f"\\tfrac{{{v.numerator}}}{{{v.denominator}}}" if v.denominator != 1 else str(v.numerator)


def macro(name, value):
    return f"\\newcommand{{\\{name}}}{{{value}}}\n"


def listing(x):
    return ",\\ ".join(num(v) for v in x)


def news_claim():
    """Task 8's headline: the mean pay rounded up to the next thousand ("almost $9,000")."""
    pay = [STAFF_PAY] * STAFF + [OWNER_PAY]
    return math.ceil(sum(pay) / len(pay) / 1000) * 1000


def wrong_variance_tex():
    """Task 7a's worked solution, with its one mistake: it divides by n instead of n - 1."""
    m = mean(ERROR_DATA)
    assert m.denominator == 1
    m = m.numerator
    terms = " + ".join(f"({v}-{m})^2" for v in ERROR_DATA)
    ss = sum((v - m) ** 2 for v in ERROR_DATA)
    n = len(ERROR_DATA)
    return f"mean ${m}$, so $s^2 = \\frac{{{terms}}}{{{n}}} = \\frac{{{ss}}}{{{n}}} = {num(Fraction(ss, n))}$"


def data_tex():
    return "% generated by hw01_numbers.py -- do not edit\n" + "".join([
        macro("hwRents", listing(RENTS)), macro("hwDelA", listing(DELIVERY_A)), macro("hwDelB", listing(DELIVERY_B)),
        macro("hwScores", listing(SCORES)), macro("hwErrData", listing(ERROR_DATA)),
        macro("hwStaff", STAFF), macro("hwStaffPay", num(STAFF_PAY)), macro("hwOwnerPay", num(OWNER_PAY)),
        macro("hwBdayA", BIRTHDAY_N[0]), macro("hwBdayB", BIRTHDAY_N[1]),
        macro("hwNewsClaim", num(news_claim())), macro("hwWrongVar", wrong_variance_tex()),
    ])


DIGITS = {"10": "Ten", "30": "Thirty", "0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four", "5": "Five",
          "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine"}


def answers_tex(a):
    m = []
    for k, v in a.items():
        name = "ans" + "".join(w.capitalize() for w in k.split("_"))
        for d, w in DIGITS.items():                                         # TeX names are letters only
            name = name.replace(d, w)
        if isinstance(v, bool):
            m.append(macro(name, "yes" if v else "no"))
        elif isinstance(v, list):
            m.append(macro(name, listing(v)))
        elif k.startswith("p_share"):                                       # 70-digit fractions: decimals only
            m.append(macro(name, num(v, 4)))
        elif isinstance(v, Fraction) and v.denominator != 1 and k.startswith(("p_", "pp_", "err_p")):
            m.append(macro(name, f"{frac(v)} \\approx {num(v, 3)}"))
        else:
            m.append(macro(name, num(v, 3 if isinstance(v, float) else 2)))
    return "% generated by hw01_numbers.py -- the answer key's numbers; never commit\n" + "".join(m)


def jsonable(v):
    if isinstance(v, Fraction):
        return [v.numerator, v.denominator]
    if isinstance(v, list):
        return [jsonable(x) for x in v]
    return v


def main():
    a = compute()
    (HERE / "hw01_data.tex").write_text(data_tex())
    KEYS.mkdir(exist_ok=True)
    (KEYS / "hw01_answers.tex").write_text(answers_tex(a))
    (KEYS / "hw01_answers.json").write_text(json.dumps({k: jsonable(v) for k, v in a.items()}, indent=1))
    print(f"{len(a)} answers -> {KEYS / 'hw01_answers.tex'}")


if __name__ == "__main__":
    main()
