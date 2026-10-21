"""Find, in a lecture's scene files, every cue call and every {language: …} dict, by reading the code (no rendering).

A cue is `self.cue(tr, t, k)` / `self.until(tr, t, k)`; its k is a sentence index, a phrase, or a {language: …} dict.
check_lang.py uses this to name the dicts a new language lacks and to try every cue's mapping; test_cues.py uses it to
prove the cue timing of English and Uzbek did not change.
"""
import ast
import re
from pathlib import Path

import languages

HERE = Path(__file__).parent
CODES = set(languages.CODES)


def scene_files(stem):
    return sorted(p for p in HERE.glob(f"{stem}_*.py") if re.fullmatch(rf"{stem}_(kit|s\d\d)", p.stem))


_TREES = {}


def tree(path):
    """A scene file's syntax tree, parsed again only when the file changed (the lecture page asks for it on every view)."""
    stamp = (path.stat().st_mtime_ns, path.stat().st_size)
    if _TREES.get(path, (None,))[0] != stamp:
        _TREES[path] = (stamp, ast.parse(path.read_text()))
    return _TREES[path][1]


def literal(node):
    """The value of a literal cue argument (int, str, dict of them), or None when it is computed."""
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError):
        return None


def line_key(call, path, names):
    """The narration key a `say("k")` / `line("k")` / local `say("s4b")` call voices, or None. `names`: {variable: key}."""
    if isinstance(call, ast.Name):
        return names.get(call.id)
    if not (isinstance(call, ast.Call) and call.args and isinstance(call.args[0], ast.Constant)):
        return None
    fn = call.func
    arg = call.args[0].value
    if isinstance(fn, ast.Attribute) and fn.attr == "say":
        return arg
    if isinstance(fn, ast.Name) and fn.id == "line":
        return arg
    if isinstance(fn, ast.Name) and fn.id == "say":                  # the section file's own say(): "4." + key
        m = re.search(r"_s(\d\d)$", path.stem)
        return f"{int(m[1])}.{arg}" if m else None
    return None


def cues(stem):
    """[{"file", "line", "call", "key", "k"}] for every cue call: key is the line it voices (None when it is not
    written as a literal), k the literal cue argument (None when computed)."""
    out = []
    for path in scene_files(stem):
        t = tree(path)
        for fn in ast.walk(t):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            assigned = sorted((st.lineno, st.targets[0].id, line_key(st.value, path, {})) for st in ast.walk(fn)
                              if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name)
                              and line_key(st.value, path, {}))
            for w in (n for n in ast.walk(fn) if isinstance(n, ast.With)):
                key = None
                names = {name: k for ln, name, k in assigned if ln < w.lineno}      # t = line("12.4"): t voices 12.4 here
                for item in w.items:
                    c = item.context_expr
                    if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr in ("say", "voiceover"):
                        key = line_key(c, path, names) if c.func.attr == "say" else (
                            line_key(c.args[0], path, names) if c.args else None)
                for call in (n for b in w.body for n in ast.walk(b) if isinstance(n, ast.Call)):
                    if isinstance(call.func, ast.Attribute) and call.func.attr in ("cue", "until") and len(call.args) > 2:
                        out.append({"file": path.name, "line": call.lineno, "call": call.func.attr, "key": key,
                                    "k": literal(call.args[2])})
    seen, uniq = set(), []                                           # nested functions are walked twice
    for c in out:
        if (c["file"], c["line"]) not in seen:
            seen.add((c["file"], c["line"]))
            uniq.append(c)
    return uniq


def language_dicts(stem):
    """[{"file", "line", "value", "is_cue_arg"}] for every dict literal keyed only by language codes (in the stem's
    scene files and kit), with whether it is written directly as a cue's argument."""
    out = []
    for path in scene_files(stem):
        t = tree(path)
        direct = {id(c.args[2]) for c in ast.walk(t) if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                  and c.func.attr in ("cue", "until") and len(c.args) > 2}
        direct |= {id(c.args[2]) for c in ast.walk(t) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                   and c.func.id == "at" and len(c.args) > 2}
        for n in ast.walk(t):
            if isinstance(n, ast.Dict) and n.keys and all(isinstance(k, ast.Constant) and k.value in CODES for k in n.keys):
                v = literal(n)
                out.append({"file": path.name, "line": n.lineno, "value": v, "is_cue_arg": id(n) in direct})
    return out


def is_cue_phrase(value, texts):
    """Whether a {language: …} dict reads like a cue: every value is a sentence index, or a phrase of some narration line
    in that language (`texts`: {language: [line text, …]}). Words shown on screen and layout choices are not."""
    if not isinstance(value, dict) or value is None:
        return False
    for lang, v in value.items():
        if isinstance(v, int):
            continue
        if not isinstance(v, str) or not any(v in t for t in texts.get(lang, [])):
            return False
    return True
