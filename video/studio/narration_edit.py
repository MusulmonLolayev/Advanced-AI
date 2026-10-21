"""Read and rewrite a lecture's narration in any language, from the editor and the review page (the instructor's edit
is their approval).

A lecture's narration in language L (resolve): narration/<stem>_<L>.md when it exists (one language, every line bold,
the same line ids as the lecture's primary language), else narration/<stem>.md, bilingual (each line's Uzbek in bold,
its English in italics under it; only uz and en). A line is found by its key ("4.s3d", "14.11": section, then the id
in the file), or by its text: a presenter line's text is the narration line verbatim (the voice's subtitles are made
from it), checked for every line of two lectures in test_narration_edit.py. An empty line (`3. ****`) is a line not
drafted yet: create_skeleton writes a new language's file that way.
"""
import os
import re
import unicodedata
from pathlib import Path

import builds as B
import languages as LG

HERE = Path(__file__).resolve().parents[1]
LINE = re.compile(r"^(\s*(\d+[a-z]?)\.\s+(?:⏸\s*)?\*\*)(.*)(\*\*\s*)$")
LIST = re.compile(r"^(- (?:\*\*)?(s\d\w*)[^*]*(?:\*\*)?\s*\*\*)([^*]+)(\*\* · \*)([^*]+)(\*.*)$")   # depth lines, bilingual
SLIST = re.compile(r"^(- (s\d\w*)\s+\*\*)(.*?)(\*\*)(\s+▸.*)?\s*$")                                  # depth lines, one language
HEAD_BI = re.compile(r"### (\d+)-boʻlim · Section \d+ — ")
HEAD_BI_FULL = re.compile(r"### (\d+)-boʻlim · Section \d+ — (.+?) · (.+?)(?:\s+\*\(.*)?$")
HEAD_ONE = re.compile(r"### [^\d\n]*(\d+)[^\d\n—–-]*[—–-]")      # "### Section 3 — T", "### Раздел 3 — T", "### 3-boʻlim — T"
OPENINGS = ("## Lecture opening", "## 강의 시작")


def default_dir():
    return Path(os.environ.get("STUDIO_NARRATION", HERE / "narration"))      # tests use a scratch copy


def primary(stem, narration_dir=None):
    """The language a lecture was written in: Uzbek for Module 0, English for the agent module (else the first it has)."""
    have = languages_of(stem, narration_dir)
    want = "uz" if B.parse_stem(stem)[0] == 0 else "en"
    return want if want in have or not have else have[0]


def resolve(stem, lang, narration_dir=None):
    """(path, single-language file?) holding `lang`'s narration of the lecture, or None when it has none."""
    d = Path(narration_dir or default_dir())
    one = d / f"{stem}_{lang}.md"
    if one.exists():
        return one, True
    both = d / f"{stem}.md"
    if lang in ("uz", "en") and both.exists():
        return both, False
    return None


def languages_of(stem, narration_dir=None):
    """The languages with a narration file for the lecture, in languages.yaml's order."""
    return [c for c in LG.CODES if resolve(stem, c, narration_dir)]


def source(build, narration_dir=None):
    """(path, language of the build, single-language file?) for a build's narration."""
    stem, lang = B.stem(build), B.lang(build)
    found = resolve(stem, lang, narration_dir)
    if found:
        return found[0], lang, found[1]
    if lang in ("uz", "en"):                           # no file at all: the bilingual path, as before
        return Path(narration_dir or default_dir()) / f"{stem}.md", lang, False
    raise FileNotFoundError(f"no {LG.name(lang)} narration for {stem} yet")


def norm(t):
    return re.sub(r"\s+", " ", t).strip()


def rows(path, lang, single):
    """[(key, row index, text, form)] for every narrated line, in file order: the row holding `lang`'s text, and
    how it holds it ("bold", "italic": the row under the bold one, "list_uz" / "list_en": a depth line's two parts,
    "list_one": a depth line in a one-language file). An empty line has the text ""."""
    out, sec = [], None
    lines = Path(path).read_text().splitlines()
    for i, row in enumerate(lines):
        if row.startswith(OPENINGS):
            sec = 0
            continue
        h = (HEAD_ONE if single else HEAD_BI).match(row)
        if h:
            sec = int(h[1])
            continue
        m = LINE.match(row)
        if m and sec is not None:
            if single or lang == "uz":
                out.append((f"{sec}.{m[2]}", i, m[3], "bold"))
            elif i + 1 < len(lines):
                en = lines[i + 1].strip()
                if en.startswith("*") and en.endswith("*"):
                    out.append((f"{sec}.{m[2]}", i + 1, en[1:-1], "italic"))
            continue
        m = (SLIST if single else LIST).match(row)
        if m and sec is not None:
            if single:
                out.append((f"{sec}.{m[2]}", i, m[3], "list_one"))
            else:
                out.append((f"{sec}.{m[2]}", i, m[3] if lang == "uz" else m[5], f"list_{lang}"))
    return out


def titles(path, single, lang="en"):
    """{section number: its title} from the headings (a bilingual file has both languages' titles: `lang`'s)."""
    out = {}
    for row in Path(path).read_text().splitlines():
        a = HEAD_BI_FULL.match(row) if not single else None
        h = HEAD_ONE.match(row) if single else None
        if a:
            out[int(a[1])] = a[2] if lang == "uz" else a[3]
        elif h:
            out[int(h[1])] = (re.split(r"\s[—–-]\s", row, maxsplit=1) + [""])[1].strip()
    return out


def texts(path, lang, single):
    """{key: text} of every line of the file (empty ones too), in file order."""
    return {k: t for k, _, t, _ in rows(path, lang, single)}


def find(path, lang, single, text):
    """The key of the line whose text is `text`."""
    hits = [(k, i, f) for k, i, t, f in rows(path, lang, single) if norm(t) and norm(t) == norm(text)]
    if len(hits) != 1:
        raise KeyError(f"{'no' if not hits else len(hits)} narration line{'s' if hits else ''} with this text")
    return hits[0]


def uz_text(text):
    """Uzbek as the repo writes it: oʻ/gʻ with U+02BB, the tutuq belgisi with U+02BC, whatever the keyboard gave."""
    t = norm(unicodedata.normalize("NFC", text))
    t = re.sub(r"([oOgG])['‘’`ʼ]", lambda m: m[1] + "ʻ", t)
    t = re.sub(r"(?<=\w)['‘’`](?=\w)", "ʼ", t)
    bad = re.findall(r"[Ѐ-ӿı]", t)
    if bad:
        raise ValueError(f"Cyrillic or Turkish letters in the Uzbek line: {''.join(sorted(set(bad)))}")
    return t


def clean_text(lang, text, allow_empty=False):
    """A line's text as the file will hold it (Uzbek apostrophes fixed); ValueError for text the file cannot hold."""
    t = uz_text(text) if lang == "uz" else norm(unicodedata.normalize("NFC", text))
    if not t and not allow_empty:
        raise ValueError("the new text is empty")
    if "**" in t or "\n" in t:
        raise ValueError("the line may not contain ** or a line break")
    return t


def put(path, key, new_text, lang, single):
    """Write `new_text` as the text of the line `key` (it is already clean). The bilingual file keeps its other language."""
    hit = next(((i, f) for k, i, _, f in rows(path, lang, single) if k == key), None)
    if hit is None:
        raise KeyError(f"no line {key} in {Path(path).name}")
    i, form = hit
    lines = Path(path).read_text().split("\n")
    if form == "bold":
        m = LINE.match(lines[i])
        lines[i] = m[1] + new_text + m[4]
    elif form == "list_one":
        m = SLIST.match(lines[i])
        lines[i] = m[1] + new_text + m[4] + (m[5] or "")
    elif form.startswith("list"):
        m = LIST.match(lines[i])
        uz, en = (new_text, m[5]) if form == "list_uz" else (m[3], new_text)
        lines[i] = m[1] + uz + m[4] + en + m[6]
    else:
        lead = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
        lines[i] = f"{lead}*{new_text}*"
    Path(path).write_text("\n".join(lines))


def set_line(path, lang, single, key, text):
    """Replace the text of line `key` (an empty line, a draft, an approved one). Returns (key, the text as written)."""
    new_text = clean_text(lang, text)
    put(path, key, new_text, lang, single)
    return key, new_text


def rewrite(path, lang, single, old_text, new_text):
    """Replace one line's text in the file. Returns its key. The bilingual file keeps the other language as is."""
    new_text = clean_text(lang, new_text)
    key, _, _ = find(path, lang, single, old_text)
    put(path, key, new_text, lang, single)
    return key, new_text


# ─── a new language ───
def skeleton_text(stem, lang, narration_dir=None):
    """The text of a new language's narration file: the primary language's headings and line ids, every line empty."""
    d = narration_dir or default_dir()
    src = primary(stem, d)
    found = resolve(stem, src, d)
    if not found:
        raise FileNotFoundError(f"{stem} has no narration to take the line ids from")
    path, single = found
    raw = path.read_text().split("\n")
    names = titles(path, single)
    out = [f"# {stem} — {LG.name(lang)} narration (skeleton)", "",
           f"Line ids and sections follow the {LG.name(src)} narration. Every line is empty: draft its text between the "
           f"bold marks, then approve it line by line in the studio (/narration?lecture={stem}&lang={lang}).", "",
           "## Lecture opening"]
    sec = 0
    for key, i, _, form in rows(path, src, single):
        s, ident = key.split(".", 1)
        if int(s) != sec:
            sec = int(s)
            out += ["", f"### {LG.section(lang, sec)} — {names.get(sec, '')}".rstrip()]
        pause = "⏸ " if "⏸" in raw[i] or (form == "italic" and "⏸" in raw[i - 1]) else ""
        out.append(f"- {ident} ****" if ident.startswith("s") else f"{ident}. {pause}****")
    return "\n".join(out) + "\n"


def create_skeleton(stem, lang, narration_dir=None):
    """narration/<stem>_<lang>.md as an empty skeleton. Refuses a language that already has narration. Returns the path."""
    d = Path(narration_dir or default_dir())
    LG.get(lang)
    if resolve(stem, lang, d):
        raise ValueError(f"{LG.name(lang)} already has narration for {stem}")
    text = skeleton_text(stem, lang, d)
    path = d / f"{stem}_{lang}.md"
    path.write_text(text)
    return path
