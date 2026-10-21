"""Can a lecture be built in a language? Everything a render would stop on, listed before it starts.

    python check_lang.py m7_lecture01 ru            # a lecture stem (render.sh's module name) and a language code

It lists, for the lecture's scene files:
  - the language's font and voice (languages.yaml): installed, and an edge voice;
  - narration lines the language's file leaves empty or lacks;
  - screen labels the lecture shows that have no form in the language (narration/labels.yaml and the lecture's draft
    labels, plus $LABEL_DRAFTS);
  - {language: …} dicts that are words on screen or layout choices (not cues) and lack the language: a render would
    stop on them (common.by_lang), never show another language's words;
  - cues that cannot be placed: a reference phrase the line does not have, and narration/<stem>_<lang>.cues.yaml
    overrides whose phrase is not in the line.
Exit status 1 when anything is listed. The studio's "can be built" line and its Build button use preflight().
"""
import os
import sys
from pathlib import Path

import yaml

import builds
import cues
import cuescan
import labels as LB
import languages as LG
from studio import narration_edit as N


def label_forms(stem, extra_dir=None):
    """{key: {language: forms}} the lecture can show: the label files, the lecture's drafts and $LABEL_DRAFTS."""
    book = {k: dict(v) for k, v in LB.book(stem).items()}
    d = extra_dir if extra_dir is not None else os.environ.get("LABEL_DRAFTS")
    for f in sorted(Path(d).glob("*.yaml")) if d else []:
        for k, v in (yaml.safe_load(f.read_text()) or {}).items():
            book.setdefault(k, {}).update(v)
    return book


def line_texts(stem, narration_dir=None):
    """{language: {line key: text}} for every language the lecture has narration in (empty lines too)."""
    out = {}
    for lang in N.languages_of(stem, narration_dir):
        path, single = N.resolve(stem, lang, narration_dir)
        out[lang] = N.texts(path, lang, single)
    return out


def overrides(stem, lang, narration_dir=None):
    """{line key: {reference phrase: phrase in lang}} from narration/<stem>_<lang>.cues.yaml, or {}."""
    path = Path(narration_dir or N.default_dir()) / f"{stem}_{lang}.cues.yaml"
    return {str(k): v for k, v in (yaml.safe_load(path.read_text()) or {}).items()} if path.exists() else {}


def preflight(stem, lang, narration_dir=None, label_drafts=None):
    """{"font": str or None, "narration": [str], "labels": [key], "dicts": [str], "cues": [str], "overrides": [str]}:
    what stands in the way of building `stem` in `lang`; an empty list (and None) is a pass."""
    LG.get(lang)
    texts = line_texts(stem, narration_dir)
    primary = N.primary(stem, narration_dir)
    mine = texts.get(lang)
    out = {"font": LG.build_problem(lang), "narration": [], "labels": [], "dicts": [], "cues": [], "overrides": []}
    if mine is None:
        out["narration"].append(f"there is no {LG.name(lang)} narration for {stem}")
    else:
        ref = texts.get(primary, {})
        # uz and en live in the bilingual file, which may lack a line only the other law's scenes say (M7's UK lines)
        keys = ref if lang not in ("uz", "en") else mine
        out["narration"] = [f"line {k}: " + ("empty" if k in mine else "missing") for k in keys if not mine.get(k, "").strip()]
    # labels
    book = label_forms(stem, label_drafts)
    for key, _ in LB.keys_for(stem):
        forms = book.get(key, {}).get(lang)
        if key in book and not (forms if isinstance(forms, str) else [f for f in forms or [] if f]):
            out["labels"].append(key)
    # dicts that are not cues
    allt = {l: list(t.values()) for l, t in texts.items()}
    for d in cuescan.language_dicts(stem):
        if d["is_cue_arg"] or d["value"] is None or lang in d["value"] or cuescan.is_cue_phrase(d["value"], allt):
            continue
        out["dicts"].append(f"{d['file']}:{d['line']} {d['value']} has no {lang} form")
    # cues, mapped the way a render maps them
    ov = overrides(stem, lang, narration_dir)
    line_ids = {k for t in texts.values() for k in t}
    read_as = {}                                   # {line key: the phrases / indexes its cues are read by in the reference language}
    for c in cuescan.cues(stem):
        k = c["k"]
        if isinstance(k, dict):
            k = k.get(primary, k.get("en", next(iter(k.values()), None)))
        read_as.setdefault(c["key"], set()).add(k)
    for key, mapping in ov.items():
        if key not in line_ids:
            out["overrides"].append(f"{stem}_{lang}.cues.yaml: line {key} is not in the lecture")
            continue
        for ref_phrase, mine_phrase in mapping.items():
            if mine is not None and mine_phrase not in mine.get(key, ""):
                out["overrides"].append(f"{stem}_{lang}.cues.yaml: line {key}: {mine_phrase!r} is not in the {LG.name(lang)} line")
            if ref_phrase not in read_as.get(key, ()):
                out["overrides"].append(f"{stem}_{lang}.cues.yaml: line {key}: no cue of the line is read by {ref_phrase!r} "
                                        f"(cues are read in {primary} first, then English)")
    if mine is not None:
        for c in cuescan.cues(stem):
            tgt = mine.get(c["key"], "")
            if c["k"] is None or not tgt.strip():
                continue
            if lang in ("uz", "en") and not isinstance(c["k"], dict):
                continue                      # a bare phrase or index is read as written there (maybe the other law's branch)
            ref = cues.CueRef(c["key"], {l: t[c["key"]] for l, t in texts.items() if t.get(c["key"], "").strip() and l != lang}
                              | {lang: tgt}, primary, ov.get(c["key"], {}))
            try:
                cues.cue_offset(tgt, c["k"], ref, lang)
            except ValueError as e:
                out["cues"].append(f"{c['file']}:{c['line']} {e}")
    return out


def problems(report):
    """The report as sentences, for the studio and the command line."""
    out = []
    if report["font"]:
        out.append(report["font"])
    out += report["narration"]
    if report["labels"]:
        out.append(f"{len(report['labels'])} labels have no form: " + ", ".join(report["labels"][:8])
                   + (" …" if len(report["labels"]) > 8 else ""))
    out += report["dicts"] + report["cues"] + report["overrides"]
    return out


def summary(report, lang):
    """Short reasons for the lecture page ("34 labels have no Russian form"), one per kind of problem."""
    name, out = LG.name(lang), []
    if report["font"]:
        out.append(report["font"])
    n = len(report["narration"])
    if n:
        out.append(report["narration"][0] if report["narration"][0].startswith("there is no") else
                   f"{n} narration line{'s are' if n != 1 else ' is'} not drafted")
    if report["labels"]:
        n = len(report["labels"])
        out.append(f"{n} labels have no {name} form" if n != 1 else f"1 label has no {name} form")
    for key, what in (("dicts", "words on screen have no {} form"), ("cues", "cues cannot be placed"),
                      ("overrides", "cue overrides do not match")):
        if report[key]:
            out.append(f"{len(report[key])} {what.format(name)}")
    return out


def main(argv):
    if len(argv) != 2 or not builds.STEM.fullmatch(argv[0]):
        print(__doc__)
        return 2
    report = preflight(argv[0], argv[1])
    found = problems(report)
    for p in found:
        print("  " + p)
    print(f"{argv[0]} in {LG.name(argv[1])}: " + (f"{len(found)} problems" if found else "can be built"))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
