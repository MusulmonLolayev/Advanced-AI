"""Where a cue falls in a line of narration, in any language (no manim in here: check_lang.py and the tests import it).

A scene times a visual to the words it illustrates with `self.cue(tr, t, k)`; k is a sentence index (0-based), a phrase
that occurs in the line, or a {language: index-or-phrase} dict when the languages split their sentences differently.
English and Uzbek read their own form. Any other language (or a form a dict lacks) is placed from the line's text in
the reference language: the same sentence and share of it, or the same share of the whole line (mapped_offset).
"""
import re

SENTENCE_END = re.compile(r"(?<=[.?!:])\s+")           # the sentence split every cue uses


def sentences(text):
    return [x for x in SENTENCE_END.split(text.strip()) if x]


def spans(text):
    """[(start, end)] of each sentence in `text`, in characters."""
    out, at_, s = [], 0, text.strip()
    lead = len(text) - len(text.lstrip())
    for m in SENTENCE_END.finditer(s):
        out.append((lead + at_, lead + m.start()))
        at_ = m.end()
    return out + ([(lead + at_, lead + len(s))] if s[at_:] else [])


def local_offset(text, k):
    """Characters before cue k in `text`: k is a sentence index (0-based) or a phrase that occurs in the text."""
    if isinstance(k, str):
        i = text.find(k)
        if i < 0:
            raise ValueError(f"cue {k!r} not in narration: {text[:60]!r}")
        return i
    parts = sentences(text)
    if k > len(parts) - 1:
        raise ValueError(f"cue {k} past the last sentence ({len(parts)}) of {text[:60]!r}")
    return sum(len(x) + 1 for x in parts[:k])


class CueRef:
    """What a cue needs to be placed in a language its author did not write it for: the line (its key, and its text in
    each language the lecture has), the lecture's primary language, and the language's overrides ({reference phrase:
    phrase in this language}, per line, from narration/<stem>_<lang>.cues.yaml)."""
    def __init__(self, key, texts, primary, overrides=None):
        self.key, self.texts, self.primary, self.overrides = key, texts, primary, overrides or {}


def reference_language(k, ref, lang):
    """The language a cue is read in: the lecture's primary when the cue (its dict, else the line) has it, else
    English, else the first it has. None when there is none."""
    have = [l for l in (k if isinstance(k, dict) else ref.texts) if l != lang and l in ref.texts]
    return next((l for l in (ref.primary, "en") if l in have), have[0] if have else None)


def mapped_offset(text, k, ref, lang):
    """Characters before a cue in `text` (the line in `lang`) when the cue has no form for `lang`. It is found in the
    line's reference-language text as a sentence and the share of that sentence before it, and put at the same place:
    the same sentence and share when both texts have as many sentences, else the same share of the whole line. An
    override in ref.overrides names the phrase in `text` outright."""
    if ref is None:
        raise ValueError(f"no {lang} form for cue {k!r} and no reference line to place it by")
    rl = reference_language(k, ref, lang)
    if isinstance(k, str):                                  # a phrase of another language: the text that holds it
        rl = next((l for l, t in ref.texts.items() if l != lang and k in t), None)
    if rl is None:
        raise ValueError(f"cue {k!r} of line {ref.key} has no text to be placed by (the line has {sorted(ref.texts)})")
    kk = k[rl] if isinstance(k, dict) else k
    mine = ref.overrides.get(kk)
    if mine is not None:
        i = text.find(mine)
        if i < 0:
            raise ValueError(f"{lang} cue override for line {ref.key}: {mine!r} (for {kk!r}) is not in the {lang} line: "
                             f"{text[:60]!r}")
        return i
    other = ref.texts[rl]
    local_offset(other, kk)                                 # raises when the cue is not in the reference line
    a, b = spans(other), spans(text)
    if isinstance(kk, str):
        i = other.find(kk)
        s = max(n for n, (x, _) in enumerate(a) if x <= i)
        frac = (i - a[s][0]) / max(a[s][1] - a[s][0], 1)
    else:
        s, frac = kk, 0.0
    if len(a) == len(b):
        return b[s][0] + frac * (b[s][1] - b[s][0])
    return len(text) * (a[s][0] + frac * (a[s][1] - a[s][0])) / max(len(other), 1)


def cue_offset(text, k, ref, lang):
    """Characters before cue k in `text`, the line in `lang`. k is a sentence index (0-based),
    a phrase that occurs in the text, or a {lang: index-or-phrase} dict when the languages split their sentences
    differently. English and Uzbek read their own form exactly as always. A language a dict lacks (or an index past
    the line's sentences, or a phrase not in the line) is placed by mapped_offset from the line's reference text."""
    if isinstance(k, dict) and lang in k:
        k = k[lang]
    elif isinstance(k, dict):
        return mapped_offset(text, k, ref, lang)
    if lang in ("uz", "en") or ref is None:
        return local_offset(text, k)
    try:
        return local_offset(text, k)
    except ValueError:
        return mapped_offset(text, k, ref, lang)
