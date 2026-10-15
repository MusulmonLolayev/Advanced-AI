"""Helpers shared by the homework number scripts (hwNN/hwNN_numbers.py): LaTeX macros for the sheet's data and the
key's answers. Every number a sheet prints or a key uses is computed in its script and written through these."""
import json
from fractions import Fraction

DIGITS = {"10": "Ten", "30": "Thirty", "0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four", "5": "Five",
          "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine"}


def num(v, nd=2):
    """A number as the sheets print it: integers plain with thin-space thousands, others with nd decimals."""
    if isinstance(v, Fraction) and v.denominator == 1:
        v = v.numerator
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return f"{v:,}".replace(",", "{,}")
    return f"{float(v):,.{nd}f}".replace(",", "{,}")


def frac(v):
    v = Fraction(v)
    return f"\\tfrac{{{v.numerator}}}{{{v.denominator}}}" if v.denominator != 1 else str(v.numerator)


def macro(name, value):
    return f"\\newcommand{{\\{name}}}{{{value}}}\n"


def listing(x):
    return ",\\ ".join(num(v) for v in x)


def tex_name(prefix, key):
    name = prefix + "".join(w.capitalize() for w in key.split("_"))
    for d, w in DIGITS.items():                                   # TeX command names are letters only
        name = name.replace(d, w)
    return name


def show(v, nd=3):
    """An answer for the key: a short fraction with its decimal, a long one as a decimal, lists, yes/no."""
    if isinstance(v, list):
        return listing(v)
    if isinstance(v, Fraction) and v.denominator != 1:
        if v.denominator <= 1000:
            return f"{frac(v)} \\approx {num(v, nd)}"
        return num(v, nd)
    if isinstance(v, float):
        return num(v, nd)
    return num(v)


def jsonable(v):
    if isinstance(v, Fraction):
        return [v.numerator, v.denominator]
    if isinstance(v, list):
        return [jsonable(x) for x in v]
    return v


def write_answers(answers, tex_path, json_path, header):
    tex_path.write_text(f"% {header} -- the answer key's numbers; never commit\n"
                        + "".join(macro(tex_name("ans", k), show(v)) for k, v in answers.items()))
    json_path.write_text(json.dumps({k: jsonable(v) for k, v in answers.items()}, indent=1))
