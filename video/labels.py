"""Check narration/labels.yaml against the scenes, and tidy it.

narration/labels.yaml holds every on-screen label of every lecture, by key, with its interchangeable
forms in each language (the default first). Scenes show a label with label("key") or label("key", i),
never with text of their own. This script

- checks every label() call names a key that exists, with a form index the key has and the
  {placeholders} its forms need, and that every key is still used;
- checks the Uzbek forms' spelling (ʻ is U+02BB, ʼ is U+02BC, no Cyrillic or Turkish letters);
- rewrites the file in lecture order, with a comment above each key listing where it is shown.
  Hand edits to the forms are kept; only the order and the comments are regenerated.

    uv run python labels.py           # check and tidy
    uv run python labels.py --check   # check only; exit 1 on a problem
"""
import ast
import json
import re
import string
import sys
from collections import defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).parent
YAML = HERE / "narration" / "labels.yaml"
FILE = re.compile(r"lecture(\d\d)_(kit|s(\d\d))\.py$")
LANGS = ("en", "uz")

HEADER = """\
# On-screen labels for every lecture video. Each label has a key, which the scenes use, and its
# interchangeable forms in English and Uzbek, the default first:
#
#   mean:
#     en: "mean"
#     uz: ["oʻrtacha qiymat", "oʻrtacha"]
#
# A scene shows label("mean") (the first form) or label("mean", 1) (the second); a language with
# fewer forms gives its first. {n} is filled in from the lecture's captured numbers. To change
# a word, edit its form here and re-render; to allow another word, add it to the list.
# The comment above each key says where it is shown. `uv run python labels.py` checks this file
# against the scenes and regenerates the order and comments; your edits to the forms are kept.
"""


SHARED = ("common.py", "lecture_kit.py")      # cards every lecture shows


def scene_files():
    def order(p):
        m = FILE.search(p.name)
        return int(m[1]), -1 if m[2] == "kit" else int(m[3])
    lectures = sorted((p for p in HERE.glob("lecture*.py") if FILE.search(p.name)), key=order)
    return [HERE / f for f in SHARED] + lectures


def where(path):
    if path.name in SHARED:
        return 0, "all lectures"
    m = FILE.search(path.name)
    lec = int(m[1])
    if m[2] == "kit":
        return lec, f"L{lec} (all)"
    return lec, f"L{lec} opening" if m[3] == "00" else f"L{lec} §{int(m[3])}"


def uses():
    """[(key, form index, {kwarg names}, (lecture, place), 'file:line')] for every label() call."""
    out = []
    for path in scene_files():
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "label":
                key = node.args[0].value if node.args and isinstance(node.args[0], ast.Constant) else None
                i = node.args[1].value if len(node.args) > 1 and isinstance(node.args[1], ast.Constant) else 0
                out.append((key, i, {k.arg for k in node.keywords}, where(path), f"{path.name}:{node.lineno}"))
    return out


def as_list(f):
    return [f] if isinstance(f, str) else list(f)


def fields(s):
    return {f.split(".")[0].split("[")[0] for _, f, _, _ in string.Formatter().parse(s) if f}


def check(labels, used):
    errs = []
    for key, i, kw, _, at in used:
        if key is None:
            errs.append(f"{at}: label() needs the key as a plain string")
            continue
        if key not in labels:
            errs.append(f"{at}: no label {key!r} in labels.yaml")
            continue
        fs = {lang: as_list(labels[key].get(lang, [])) for lang in LANGS}
        for lang in LANGS:
            if not fs[lang]:
                errs.append(f"{key}: no {lang} form")
                continue
            s = fs[lang][i] if i < len(fs[lang]) else fs[lang][0]
            if kw and fields(s) - kw:
                errs.append(f"{at}: {key} [{lang}] needs {sorted(fields(s) - kw)}")
        if i and all(i >= len(fs[lang]) for lang in LANGS):
            errs.append(f"{at}: {key} has no form {i}")
    for key in labels.keys() - {u[0] for u in used}:
        errs.append(f"{key}: not shown anywhere (remove it, or use it)")
    for key, v in labels.items():
        if set(v) != set(LANGS):
            errs.append(f"{key}: needs exactly en and uz, has {sorted(v)}")
        for s in as_list(v.get("uz", [])):
            if re.search(r"[Ѐ-ӿığşçöü]", s):
                errs.append(f"{key}: Cyrillic or Turkish letter in {s!r}")
            if re.search(r"[oOgG]['‘’`ʼ]", s):
                errs.append(f"{key}: oʻ/gʻ must use ʻ (U+02BB) in {s!r}")
            if re.search(r"(?<=[a-zA-Z])['’`](?=[a-zA-Z])", s):
                errs.append(f"{key}: the tutuq belgisi is ʼ (U+02BC) in {s!r}")
    return errs


def scalar(f):
    f = as_list(f)
    q = [json.dumps(s, ensure_ascii=False) for s in f]
    return q[0] if len(q) == 1 else "[" + ", ".join(q) + "]"


def write(labels, used):
    seen = defaultdict(list)                      # key -> [(lecture, place)] in first-use order
    for key, _, _, w, _ in used:
        if key in labels and w not in seen[key]:
            seen[key].append(w)
    order = list(seen) + [k for k in labels if k not in seen]
    out, lec = [HEADER], None
    for key in order:
        ws = seen.get(key, [])
        if ws and ws[0][0] != lec:
            lec = ws[0][0]
            head = f"Lecture {lec}" if lec else "Every lecture"
            out.append(f"\n# ══ {head} " + "═" * (70 - len(head)) + "\n")
        places, last = [], None
        for l, p in ws:
            places.append(p if l != last or not l else p.split(" ", 1)[1])
            last = l
        note = re.sub(r", (L\d)", r"; \1", ", ".join(places)) or "not shown"
        # quote a key YAML would read as something else ("no" is false, "1_in_10" could be a number)
        k = key if re.fullmatch(r"[a-z][a-z0-9_]*", key) and yaml.safe_load(f"{key}: 0") == {key: 0} else json.dumps(key)
        out.append(f"\n# {note}\n{k}:\n  en: {scalar(labels[key]['en'])}\n  uz: {scalar(labels[key]['uz'])}\n")
    YAML.write_text("".join(out))


def main():
    labels = yaml.safe_load(YAML.read_text())
    used = uses()
    errs = check(labels, used)
    if "--check" not in sys.argv:
        write(labels, used)
        assert yaml.safe_load(YAML.read_text()) == labels, "rewriting changed the labels"
    many = sum(1 for v in labels.values() if any(len(as_list(v[l])) > 1 for l in LANGS))
    print(f"{YAML.relative_to(HERE)}: {len(labels)} labels ({many} with more than one form), "
          f"{len(used)} uses, {len(errs)} problems")
    for e in errs:
        print("  " + e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
