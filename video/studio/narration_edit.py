"""Rewrite one narration line in its approved file, from the editor (the instructor's edit is their approval).

A build's narration: narration/<stem>.md, bilingual (each line's Uzbek in bold, its English in italics under it), or
for an English build narration/<stem>_en.md when it exists (one language, bold). The line is found by its text: a
presenter line's text is the narration line verbatim (the voice's subtitles are made from it), checked for every
line of two lectures in test_narration_edit.py.
"""
import os
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def default_dir():
    return Path(os.environ.get("STUDIO_NARRATION", HERE / "narration"))      # tests use a scratch copy
BUILD = re.compile(r"(?:m(\d)_)?lecture(\d\d)_(uz_navoiy|en)")
LINE = re.compile(r"^(\s*(\d+[a-z]?)\.\s+(?:⏸\s*)?\*\*)(.+)(\*\*\s*)$")
LIST = re.compile(r"^(- (?:\*\*)?(s\d\w*)[^*]*(?:\*\*)?\s*\*\*)([^*]+)(\*\* · \*)([^*]+)(\*.*)$")   # depth lines
HEAD_BI = re.compile(r"### (\d+)-boʻlim · Section \d+ — ")
HEAD_ONE = re.compile(r"### Section\s*(\d+)\s*[—–-]")


def source(build, narration_dir=None):
    """(path, language of the build, single-language file?) for a build's narration."""
    narration_dir = narration_dir or default_dir()
    m = BUILD.fullmatch(build)
    if not m:
        raise ValueError(f"not a lecture build: {build}")
    stem = (f"m{m[1]}_" if m[1] else "") + f"lecture{m[2]}"
    lang = "en" if m[3] == "en" else "uz"
    single = Path(narration_dir) / f"{stem}_en.md"
    if lang == "en" and single.exists():
        return single, lang, True
    return Path(narration_dir) / f"{stem}.md", lang, False


def norm(t):
    return re.sub(r"\s+", " ", t).strip()


def rows(path, lang, single):
    """[(key, row index, text, form)] for every narrated line, in file order: the row holding `lang`'s text, and
    how it holds it ("bold", "italic": the row under the bold one, "list_uz" / "list_en": a depth line's two parts)."""
    out, sec = [], None
    lines = Path(path).read_text().splitlines()
    for i, row in enumerate(lines):
        if row.startswith("## Lecture opening") or row.startswith("## 강의 시작"):
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
        m = LIST.match(row)
        if m and sec is not None and not single:
            out.append((f"{sec}.{m[2]}", i, m[3] if lang == "uz" else m[5], f"list_{lang}"))
    return out


def find(path, lang, single, text):
    """The key of the line whose text is `text`."""
    hits = [(k, i, f) for k, i, t, f in rows(path, lang, single) if norm(t) == norm(text)]
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


def rewrite(path, lang, single, old_text, new_text):
    """Replace one line's text in the file. Returns its key. The bilingual file keeps the other language as is."""
    new_text = uz_text(new_text) if lang == "uz" else norm(new_text)
    if not new_text:
        raise ValueError("the new text is empty")
    if "**" in new_text or "\n" in new_text:
        raise ValueError("the line may not contain ** or a line break")
    key, i, form = find(path, lang, single, old_text)
    lines = Path(path).read_text().split("\n")
    if form == "bold":
        m = LINE.match(lines[i])
        lines[i] = m[1] + new_text + m[4]
    elif form.startswith("list"):
        m = LIST.match(lines[i])
        uz, en = (new_text, m[5]) if form == "list_uz" else (m[3], new_text)
        lines[i] = m[1] + uz + m[4] + en + m[6]
    else:
        lead = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
        lines[i] = f"{lead}*{new_text}*"
    Path(path).write_text("\n".join(lines))
    return key, new_text
