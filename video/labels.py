"""Check the label files against the scenes, and tidy them.

Two books: narration/labels.yaml (the statistics lectures and the shared cards, English and Uzbek) and
narration/labels_agents_course.yaml (the agent course, its own languages). A scene may use a key from either book.

narration/labels.yaml holds every on-screen label of every lecture, by key, with its interchangeable
forms in each language (the default first). Scenes show a label with label("key") or label("key", i),
never with text of their own. This script

- checks every label() call names a key that exists, with a form index the key has, and that
  every key is still used;
- checks no label holds a {placeholder}: a label is words only, and the number it goes with comes
  from the data and is drawn beside it (common.tagged) or as math;
- checks the Uzbek forms' spelling (ʻ is U+02BB, ʼ is U+02BC, no Cyrillic or Turkish letters);
- rewrites the file in lecture order, with a comment above each key listing where it is shown.
  Hand edits to the forms are kept; only the order and the comments are regenerated.

    uv run python labels.py           # check and tidy
    uv run python labels.py --check   # check only; exit 1 on a problem
"""
import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).parent
YAML = HERE / "narration" / "labels.yaml"
FILE = re.compile(r"lecture(\d\d)_(kit|s(\d\d))\.py$")
LANGS = ("en", "uz")
AC_YAML = HERE / "narration" / "labels_agents_course.yaml"
AC_FILE = re.compile(r"agents_course_(kit|s(\d\d))\.py$")
# The course's languages: Korean joins as soon as its forms are merged (then every course label needs one, and so
# does every shared labels.yaml key the course shows, e.g. the pause card).
_ac = yaml.safe_load(AC_YAML.read_text()) if AC_YAML.exists() else {}
AC_LANGS = ("en", "ko") if any("ko" in v for v in (_ac or {}).values()) else ("en",)
EXTRA = ("ko",)                                   # a labels.yaml key may also carry these (shared cards the course uses)

HEADER = """\
# On-screen labels for every lecture video. Each label has a key, which the scenes use, and its
# interchangeable forms in English and Uzbek, the default first:
#
#   mean:
#     en: "mean"
#     uz: ["oʻrtacha qiymat", "oʻrtacha"]
#
# A scene shows label("mean") (the first form) or label("mean", 1) (the second); a language with
# fewer forms gives its first. A label is words only: numbers come from the captured data and the
# scene sets them beside the words or as math. To change a word, edit its form here and re-render;
# to allow another word, add it to the list.
# The comment above each key says where it is shown. `uv run python labels.py` checks this file
# against the scenes and regenerates the order and comments; your edits to the forms are kept.
"""


SHARED = ("common.py", "lecture_kit.py")      # cards every lecture shows


def ac_files():
    return sorted((p for p in HERE.glob("agents_course_*.py") if AC_FILE.search(p.name)),
                  key=lambda p: -1 if AC_FILE.search(p.name)[1] == "kit" else int(AC_FILE.search(p.name)[2]))


def scene_files():
    def order(p):
        m = FILE.search(p.name)
        return int(m[1]), -1 if m[2] == "kit" else int(m[3])
    lectures = sorted((p for p in HERE.glob("lecture*.py") if FILE.search(p.name)), key=order)
    return [HERE / f for f in SHARED] + lectures


def where(path):
    if m := AC_FILE.search(path.name):
        return 100, "agent course" if m[1] == "kit" else f"agent course §{int(m[2])}"
    if path.name in SHARED:
        return 0, "all lectures"
    m = FILE.search(path.name)
    lec = int(m[1])
    if m[2] == "kit":
        return lec, f"L{lec} (all)"
    return lec, f"L{lec} opening" if m[3] == "00" else f"L{lec} §{int(m[3])}"


def uses(files=None):
    """[(key, form index, number of keyword args, (lecture, place), 'file:line')] for every label() call."""
    out = []
    for path in files or scene_files():
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "label":
                key = node.args[0].value if node.args and isinstance(node.args[0], ast.Constant) else None
                i = node.args[1].value if len(node.args) > 1 and isinstance(node.args[1], ast.Constant) else 0
                out.append((key, i, len(node.keywords), where(path), f"{path.name}:{node.lineno}"))
    return out


def as_list(f):
    return [f] if isinstance(f, str) else list(f)


def check(labels, used, langs=LANGS, others=None, unused=True, extra=()):
    """others: keys of the other book, which these scenes may also use."""
    errs, others = [], others or {}
    for key, i, kw, _, at in used:
        if key is None:
            errs.append(f"{at}: label() needs the key as a plain string")
            continue
        if key not in labels and key not in others:
            errs.append(f"{at}: no label {key!r} in labels.yaml")
            continue
        book = labels if key in labels else others
        fs = {lang: as_list(book[key].get(lang, [])) for lang in langs}
        if kw:
            errs.append(f"{at}: label() takes a key and a form index only; set numbers beside the label")
        if i and all(i >= len(fs[lang]) for lang in langs):
            errs.append(f"{at}: {key} has no form {i}")
    for key in (labels.keys() - {u[0] for u in used}) if unused else ():
        errs.append(f"{key}: not shown anywhere (remove it, or use it)")
    for key, v in labels.items():
        if not set(langs) <= set(v) <= set(langs) | set(extra):
            errs.append(f"{key}: needs exactly {' and '.join(langs)}, has {sorted(v)}")
        for s in as_list(v.get("en", [])) + as_list(v.get("uz", [])):
            if re.search(r"\{[^}]*\}", s):
                errs.append(f"{key}: a label holds words only, not a {{placeholder}}: {s!r}")
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
        out.append(f"\n# {note}\n{k}:\n" + "".join(f"  {l}: {scalar(labels[key][l])}\n"
                                                for l in LANGS + EXTRA if l in labels[key]))
    YAML.write_text("".join(out))


def write_ac(labels, used):
    order = list(dict.fromkeys(k for k, *_ in used if k in labels)) + [k for k in labels if k not in {u[0] for u in used}]
    out = [AC_HEADER]
    for key in order:
        places = list(dict.fromkeys(w[1] for k, _, _, w, _ in used if k == key)) or ["not shown"]
        k = key if re.fullmatch(r"[a-z][a-z0-9_]*", key) and yaml.safe_load(f"{key}: 0") == {key: 0} else json.dumps(key)
        out.append(f"\n# {', '.join(places)}\n{k}:\n" + "".join(f"  {l}: {scalar(labels[key][l])}\n" for l in AC_LANGS))
    AC_YAML.write_text("".join(out))


AC_HEADER = """\
# On-screen labels for the agent course (agents_course_*.py), same rules as labels.yaml: a key, its
# interchangeable forms per language (the default first), words only. Its languages are labels.py's AC_LANGS.
# Shared cards (pause, …) stay in labels.yaml. `uv run python labels.py` checks and tidies both files.
"""


def main():
    labels = yaml.safe_load(YAML.read_text())
    ac = yaml.safe_load(AC_YAML.read_text()) if AC_YAML.exists() else {}
    used, ac_used = uses(), uses(ac_files())
    clash = labels.keys() & ac.keys()
    errs = [f"{k}: defined in both label files" for k in sorted(clash)]
    # a shared key the agent course uses counts as used
    errs += check(labels, used + [u for u in ac_used if u[0] in labels], extra=EXTRA)
    for lang in set(AC_LANGS) - set(LANGS):       # shared keys the course shows need its languages too
        errs += [f"{k}: the agent course shows it, so it needs a {lang} form"
                 for k in sorted({u[0] for u in ac_used if u[0] in labels}) if lang not in labels[k]]
    # the course's scenes also pick keys in loops (label(k) for k in ("ac_a", "ac_b")): a key written as a string
    # anywhere in its files counts as used, and such label() calls are allowed there
    lits = {n.value for f in ac_files() for n in ast.walk(ast.parse(f.read_text()))
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value in ac}
    ac_used = [u for u in ac_used if u[0] is not None] + [(k, 0, 0, (100, "agent course"), "literal") for k in lits]
    errs += check(ac, ac_used, AC_LANGS, others=labels)
    if "--check" not in sys.argv:
        write(labels, used + [u for u in ac_used if u[0] in labels])
        assert yaml.safe_load(YAML.read_text()) == labels, "rewriting changed the labels"
        if ac:
            write_ac(ac, ac_used)
            assert yaml.safe_load(AC_YAML.read_text()) == ac, "rewriting changed the agent-course labels"
    many = sum(1 for v in labels.values() if any(len(as_list(v[l])) > 1 for l in LANGS))
    print(f"{YAML.relative_to(HERE)}: {len(labels)} labels ({many} with more than one form), {len(used)} uses; "
          f"{AC_YAML.relative_to(HERE)}: {len(ac)} labels, {len(ac_used)} uses; {len(errs)} problems")
    for e in errs:
        print("  " + e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
