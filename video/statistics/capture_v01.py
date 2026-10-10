"""Capture the real numbers video 1 shows.

The salary population is regenerated with the same seed and formula as
statistics/scripts/generate_data_probability_graphics.py, then asserted against
the figures that script printed. If the script ever changes, these assertions
fail rather than letting the video drift away from the slides.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent / "raw"
OUT.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
n_emp = 600
salary = 22_000 + rng.lognormal(mean=np.log(26_000), sigma=0.55, size=n_emp)
df = pd.DataFrame({"salary": salary})

mean, median = df["salary"].mean(), df["salary"].median()
assert round(mean) == 51613, f"salary mean drifted: {mean}"
assert round(median) == 47697, f"salary median drifted: {median}"

N_DRINKERS = 50
step = n_emp // N_DRINKERS
drinkers = np.sort(salary)[::step][:N_DRINKERS]
BILLIONAIRE = 150_000_000_000.0
after = np.concatenate([drinkers, [BILLIONAIRE]])
assert round(drinkers.mean()) == 50627, f"drinkers mean drifted: {drinkers.mean()}"
assert round(np.median(drinkers)) == 47323, f"drinkers median drifted: {np.median(drinkers)}"
assert round(after.mean()) == 2_941_226_105, f"after mean drifted: {after.mean()}"
assert round(np.median(after)) == 47761, f"after median drifted: {np.median(after)}"

# What the bar animations show: excess above the mean exactly fills the shortfall
# below it, and the median (unlike the mean) does not give back the payroll.
excess = float(np.clip(salary - mean, 0, None).sum())
shortfall = float(np.clip(mean - salary, 0, None).sum())
assert abs(excess - shortfall) < 1e-3, (excess, shortfall)
median_total = median * n_emp
s_drink = np.sort(drinkers)
mid_before = (float(s_drink[N_DRINKERS // 2 - 1]), float(s_drink[N_DRINKERS // 2]))
assert np.isclose(np.mean(mid_before), np.median(drinkers))
assert np.isclose(np.sort(after)[N_DRINKERS // 2], np.median(after))

nine = [31, 38, 42, 45, 47, 49, 52, 61, 88]
below = sum(1 for x in nine if x < sum(nine) / len(nine))

lines = [
    f"employees                 {n_emp}",
    f"payroll mean              ${mean:,.0f}",
    f"payroll median            ${median:,.0f}",
    f"payroll total  mean*n     ${mean * n_emp:,.0f}",
    f"drinkers                  {N_DRINKERS} (every {step}th of the sorted payroll)",
    f"drinkers mean             ${drinkers.mean():,.0f}",
    f"drinkers median           ${np.median(drinkers):,.0f}",
    f"after mean                ${after.mean():,.0f}",
    f"after median              ${np.median(after):,.0f}",
    f"excess above mean         ${excess:,.0f}  (= shortfall below ${shortfall:,.0f})",
    f"median * n                ${median_total:,.0f}  (short by ${mean * n_emp - median_total:,.0f})",
    f"drinkers middle two       ${mid_before[0]:,.2f}, ${mid_before[1]:,.2f}  (25th, 26th of 50)",
    f"hands-on nine (k$)        {nine}",
    f"hands-on sum / mean       {sum(nine)} / {sum(nine)/len(nine):.3f}",
    f"hands-on below the mean   {below} of {len(nine)}",
]
(OUT / "v01_numbers.txt").write_text("\n".join(lines) + "\n")

# Machine-readable copy: the video module reads this and types no number itself.
values = {
    "n_emp": int(n_emp),
    "payroll_mean": float(mean),
    "payroll_median": float(median),
    "payroll_total": float(mean * n_emp),
    "n_drinkers": int(N_DRINKERS),
    "drink_mean": float(drinkers.mean()),
    "drink_median": float(np.median(drinkers)),
    "after_mean": float(after.mean()),
    "after_median": float(np.median(after)),
    "billionaire": float(BILLIONAIRE),
    "excess": excess,
    "median_total": float(median_total),
    "median_short": float(mean * n_emp - median_total),
    "mid_before": list(mid_before),
    "nine": [int(x) for x in nine],
    "nine_sum": int(sum(nine)),
    "nine_mean": float(sum(nine) / len(nine)),
    "nine_below": int(below),
}
(OUT / "v01_numbers.json").write_text(json.dumps(values, indent=2) + "\n")
np.savetxt(OUT / "v01_salaries.txt", np.sort(salary), fmt="%.2f")
np.savetxt(OUT / "v01_drinkers.txt", drinkers, fmt="%.2f")
print("\n".join(lines))
