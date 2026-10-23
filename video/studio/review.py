"""What the narration review page (/narration), the lecture page's language rows and the editor's language box show:
each language's lines and labels with their status, the checks run on their texts, whether a build is out of date with
its narration, and whether a language can be built (studio/buildlang.py plans it: check_lang's preflight, approval).
"""
import re
from pathlib import Path
from urllib.parse import quote

import builds as B
import languages as LG
from studio import buildlang as BL
from studio import linestatus as LS
from studio import media as M
from studio import narration_edit as N
from studio import store as S

CYR = re.compile(r"[Ѐ-ӿ]")
TURKISH = re.compile(r"[ığşçöü]")
LATIN_WORD = re.compile(r"(?<![A-Za-z0-9_])[a-z]{3,}(?![A-Za-z0-9_])")
TERMS = {"python", "json", "api", "sql", "http", "url", "llm", "gpu", "cpu", "token", "tokens"}   # read as they are, in any language


def checks(lang, text, kind="line"):
    """[(level, message)] for a text, shown beside it and never blocking. level: "warn" (breaks a rule of the repo) or
    "hint" (probably, not surely, wrong)."""
    out = []
    if not text.strip():
        return out
    script = LG.script(lang)
    if script == "latin":
        bad = sorted(set(CYR.findall(text)))
        if bad:
            out.append(("warn", f"Cyrillic letters in a Latin-script text: {' '.join(bad)}"))
    if lang == "uz":
        if TURKISH.search(text):
            out.append(("warn", f"Turkish letters in an Uzbek text: {' '.join(sorted(set(TURKISH.findall(text))))}"))
        if re.search(r"[oOgG]['‘’`ʼ]", text):
            out.append(("warn", "oʻ and gʻ are written with ʻ (U+02BB)"))
        if re.search(r"(?<![oOgG])(?<=[a-zA-Z])['’`](?=[a-zA-Z])", text):
            out.append(("warn", "the tutuq belgisi is ʼ (U+02BC)"))
    if script == "cyrillic":
        words = [w for w in LATIN_WORD.findall(text) if w not in TERMS]
        if words:
            out.append(("hint", f"Latin words in a Cyrillic text (untranslated?): {', '.join(dict.fromkeys(words))}"))
    if kind == "line" and re.search(r"\d", text):
        out.append(("hint", "digits: numbers are spelled out for the ear in narration, the screen shows the digits"))
    return out


def _info(lang):
    e = LG.get(lang)
    return {"code": lang, "name": e["name"], "native": e["native"], "script": e["script"], "rtl": bool(e.get("rtl"))}


# ─── the review page ───
def review(c, stem, lang, narration_dir=None):
    """Everything /narration shows for one language of a lecture."""
    LG.get(lang)
    by_line = LS.line_texts(stem, narration_dir)
    found = N.resolve(stem, lang, narration_dir)
    primary = N.primary(stem, narration_dir)
    out = {"lecture": stem, "lang": lang, "language": _info(lang), "primary": primary, "exists": bool(found),
           "languages": [_info(l) for l in LG.CODES], "have": list(by_line), "lines": [], "sections": {}}
    if found:
        path, single = found
        sts = LS.statuses(c, stem, lang, "line", by_line)
        names = N.titles(path, single, lang)
        out["sections"] = {str(s): f"{LG.section(lang, s)}" + (f" · {names[s]}" if names.get(s) else "")
                           for s in sorted({int(k.split(".")[0]) for k in by_line[lang]})}
        for k, text in by_line[lang].items():
            st = sts[k]
            out["lines"].append({"key": k, "section": int(k.split(".")[0]), "text": text, "state": st["state"],
                                 "changed": st["changed"], "refs": LS.others_of(by_line, lang, k),
                                 "checks": checks(lang, text)})
        out["counts"] = LS.counts(sts)
    else:
        out["counts"] = LS.counts({})
    keys, by_label, lab = LS.label_statuses(c, stem, lang)
    out["labels"] = [{"key": k, "where": w, "text": by_label.get(lang, {}).get(k, ""), "state": lab[k]["state"],
                      "changed": lab[k]["changed"], "refs": LS.others_of(by_label, lang, k),
                      "checks": [x for t in by_label.get(lang, {}).get(k, "").split("\n") for x in checks(lang, t, "label")]}
                     for k, w in keys]
    out["label_counts"] = LS.counts(lab)
    return out


def act(c, stem, lang, action, kind, key, text=None, narration_dir=None):
    """One button of the review page: "approve", "save" (write `text`, then approve) or "fine" (still fine). Returns the
    item as the page shows it, with the counts. Raises KeyError for an item that is not there, ValueError for a
    refusal (the message is shown to the instructor)."""
    LG.get(lang)
    if kind not in ("line", "label"):
        raise ValueError(f"bad kind {kind!r}")
    by = LS.line_texts(stem, narration_dir) if kind == "line" else LS.label_statuses(c, stem, lang)[1]
    if key not in by.get(lang, {}):
        raise KeyError(f"no {kind} {key!r} in {LG.name(lang)}")
    if action == "approve":
        LS.approve(c, stem, lang, kind, key, by)
    elif action == "fine":
        LS.still_fine(c, stem, lang, kind, key, by)
    elif action == "save" and text is not None:
        (LS.save_line(c, stem, lang, key, text, narration_dir) if kind == "line" else LS.save_label(c, stem, lang, key, text))
    else:
        raise ValueError(f"bad action {action!r}")
    r = review(c, stem, lang, narration_dir)
    item = next(x for x in r["lines" if kind == "line" else "labels"] if x["key"] == key)
    return {"item": item, "counts": r["counts"], "label_counts": r["label_counts"]}


def add_language(stem, lang, narration_dir=None):
    """Create the language's skeleton narration (every line empty). Returns the file's name."""
    return N.create_skeleton(stem, lang, narration_dir).name


# ─── the lecture page ───
def stems(root, module, narration_dir=None):
    """The lectures of a module that have a narration file or a build, in lecture order."""
    d = Path(narration_dir or N.default_dir())
    found = set()
    for p in d.glob("*lecture*.md"):
        m = re.match(r"((?:m\d_)?lecture\d\d)(?:_[a-z]{2,3})?\.md$", p.name)
        if m and B.parse_stem(m[1])[0] == module:
            found.add(m[1])
    for p in Path(root).glob("*lecture*"):
        if p.is_dir() and B.is_build(p.name) and B.module(p.name) == module:
            found.add(B.stem(p.name))
    return sorted(found, key=lambda s: B.parse_stem(s)[1])


def builds_of(root, stem):
    """{language: [build names]} of the lecture's builds on disk (a folder with the video in it, or just a folder)."""
    out = {}
    for p in sorted(Path(root).glob(f"{stem}_*")):
        if p.is_dir() and B.is_build(p.name) and B.stem(p.name) == stem and B.lang(p.name) in LG.LANGS:
            out.setdefault(B.lang(p.name), []).append(p.name)
    return out


def lecture_langs(root, stem, narration_dir=None):
    """The languages a lecture shows: the primary language first, then those with narration or a build, in
    languages.yaml's order."""
    have = set(N.languages_of(stem, narration_dir)) | set(builds_of(root, stem))
    first = N.primary(stem, narration_dir)
    return sorted(have, key=lambda l: (l != first, LG.CODES.index(l)))


def lecture_list(c, root, modules, shared_files, narration_dir=None):
    """The project browser's list: every module (`modules`: {number: title}) with its lectures, and for each lecture its
    languages with their approval counts, build state and recorded sessions. The same facts the old module page
    showed (`summary` per language), without the build plan, which is slow: /api/lecture-langs has that for one lecture.
    `shared_files(k)` lists the module's shared files (Paths)."""
    out = []
    for k, title in modules.items():
        lecs = []
        for stem in stems(root, k):
            by_line = LS.line_texts(stem, narration_dir)
            builds = builds_of(root, stem)
            langs = []
            for lang in lecture_langs(root, stem, narration_dir):
                sts = LS.statuses(c, stem, lang, "line", by_line)
                _, _, lab = LS.label_statuses(c, stem, lang)
                built = None
                for b in builds.get(lang, []):
                    mp4 = Path(root) / b / f"{b}.mp4"
                    if mp4.exists() and (Path(root) / b / "joined.txt").exists():
                        built = {"build": b, "when": mp4.stat().st_mtime,
                                 "sessions": c.execute("select count(*) from sessions where build=?", (b,)).fetchone()[0]}
                        break
                langs.append({"lang": lang, "name": LG.name(lang), "native": LG.native(lang), "has_narration": lang in by_line,
                              "lines": LS.counts(sts), "labels": LS.counts(lab), "build": built["build"] if built else None,
                              "built_on": built["when"] if built else None, "sessions": built["sessions"] if built else 0,
                              "build_name": BL.build_name(stem, lang)})
            lecs.append({"stem": stem, "n": B.parse_stem(stem)[1], "langs": langs})
        files = [{"name": f.name, "size": f.stat().st_size, "time": f.stat().st_mtime, "url": f"/shared/m{k}/{quote(f.name)}"}
                 for f in shared_files(k)]
        out.append({"k": k, "title": title, "files": files, "lectures": lecs})
    return out


def stale_lines(root, build, by_line, lang, sts):
    """The keys of approved lines whose text the built video does not carry (its presenter lines.json), or None when the
    build has no presenter page to compare with."""
    lj = Path(root) / build / "presenter" / "lines.json"
    if not lj.exists():
        return None
    spoken = {N.norm(l[1]) for l in M.lines(Path(root) / build)}
    return [k for k, st in sts.items() if st["state"] in ("approved", "needs_update") and N.norm(by_line[lang][k]) not in spoken]


def summary(c, root, stem, lang, narration_dir=None):
    """One language's row on the lecture page."""
    by_line = LS.line_texts(stem, narration_dir)
    sts = LS.statuses(c, stem, lang, "line", by_line)
    _, _, lab = LS.label_statuses(c, stem, lang)
    lines, labels = LS.counts(sts), LS.counts(lab)
    labels["missing"] = labels["empty"]
    p = BL.plan(c, root, stem, lang, narration_dir)
    rows = []
    for b in builds_of(root, stem).get(lang, []):
        mp4 = Path(root) / b / f"{b}.mp4"
        stale = stale_lines(root, b, by_line, lang, sts) if lang in by_line else None
        n_sessions = c.execute("select count(*) from sessions where build=?", (b,)).fetchone()[0]
        rows.append({"build": b, "built": mp4.exists(), "when": mp4.stat().st_mtime if mp4.exists() else None,
                     "prepared": (Path(root) / b / "presenter" / "lines.json").exists(),
                     "stale": stale, "sessions": n_sessions, "has_page": (Path(root) / b / "presenter" / "presenter.html").exists()})
    return {"lang": lang, **{k: _info(lang)[k] for k in ("name", "native")}, "has_narration": lang in by_line,
            "lines": lines, "labels": labels, "builds": rows, "ready": not p["reasons"], "missing": p["reasons"],
            "plan": p, "job": job(c, p["build"])}


def job(c, build):
    """The newest "build video" job of a build ({state, detail, error, updated}), or None."""
    r = c.execute("select state, detail, error, updated from jobs where build=? and kind='build' order by updated desc",
                  (build,)).fetchone()
    return dict(r) if r else None


# ─── the editor ───
def editor_langs(c, root, build, narration_dir=None):
    """The editor's language switch and, for each presenter line, the same line in the other languages."""
    stem, lang = B.stem(build), B.lang(build)
    by_line = LS.line_texts(stem, narration_dir)
    out = {"lang": lang, "lecture": stem, "others": [], "lines": {}}
    builds = builds_of(root, stem)
    for l in lecture_langs(root, stem, narration_dir):
        if l == lang:
            continue
        sts = LS.statuses(c, stem, l, "line", by_line)
        ed = next((b for b in builds.get(l, []) if (Path(root) / b / "presenter" / "lines.json").exists()), None)
        out["others"].append({"lang": l, "name": LG.name(l), "native": LG.native(l), "build": ed,
                              "review": f"/narration?lecture={stem}&lang={l}", "counts": LS.counts(sts) if l in by_line else None})
    if lang not in by_line:
        return out
    sts = LS.statuses(c, stem, lang, "line", by_line)
    key_of = {}
    for k, t in by_line[lang].items():
        key_of.setdefault(N.norm(t), []).append(k)
    ls = M.lines(Path(root) / build)
    states = {l: LS.statuses(c, stem, l, "line", by_line) for l in by_line if l != lang}
    for i, line in enumerate(ls):
        ks = key_of.get(N.norm(line[1]), [])
        if len(ks) != 1:
            continue
        k = ks[0]
        out["lines"][str(i)] = {
            "key": k, "state": sts[k]["state"], "changed": sts[k]["changed"],
            "others": [{"lang": l, "text": by_line[l][k], "state": states[l][k]["state"],
                        "review": f"/narration?lecture={stem}&lang={l}#line={k}"}
                       for l in states if by_line[l].get(k, "").strip()]}
    return out
