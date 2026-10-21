"""Which narration lines and screen labels the instructor approved, in each language, and which need another look.

A line (or a label: kind "label", its forms joined by line breaks) of a lecture in one language is
  empty         no text yet (a skeleton line)
  draft         has text the instructor has not approved: no approval, or the text changed since
  approved      the text hashes to what was approved, and no other language's text of the same line changed since
  needs update  approved, but another language's text of the same line is not what it was at approval time
                ("uz changed": the approval row keeps those texts, so the old and the new can be shown side by side)
Nothing changes by itself: the instructor approves a line, saves an edit (which writes the file and approves), or says
"still fine" (approves again, against the other languages' texts as they are now). A merged version approves the lines
it changed (versions.merge), which makes the same lines in the other languages "needs update".

A language joins a line's sources only when it has text for it at approval time; a language drafted later is a
translation of the approved line, not a change to it.
"""
import hashlib
import unicodedata

import builds as B
import labels as LB
import languages as LG
from studio import narration_edit as N
from studio import store as S

STATES = ("approved", "needs_update", "draft", "empty")


def digest(text):
    return hashlib.sha1(N.norm(unicodedata.normalize("NFC", text)).encode()).hexdigest()[:16]


# ─── the texts, from the files ───
def line_texts(stem, narration_dir=None):
    """{language: {line key: text}} for every language the lecture has narration in, each in file order."""
    out = {}
    for lang in N.languages_of(stem, narration_dir):
        path, single = N.resolve(stem, lang, narration_dir)
        out[lang] = N.texts(path, lang, single)
    return out


def label_keys(stem):
    """[(key, where shown)] of the labels the lecture shows, that exist in a label file (a key used in a loop does not)."""
    book = LB.book(stem)
    return [(k, w) for k, w in LB.keys_for(stem) if k in book]


def label_text(forms):
    """A label's forms in a language as one text: one form per line, the default first."""
    return "\n".join([forms] if isinstance(forms, str) else forms or [])


def label_texts(stem, keys=None):
    """{language: {label key: text}} for every language that has a form of some label the lecture shows."""
    book = LB.book(stem)
    keys = keys or [k for k, _ in label_keys(stem)]
    out = {}
    for lang in LG.CODES:
        t = {k: label_text(book[k].get(lang)) for k in keys}
        if any(t.values()):
            out[lang] = t
    return out


def label_statuses(c, stem, lang):
    """([(key, where shown)], {language: {key: text}}, {key: status}) of the labels the lecture shows, in `lang`."""
    keys = label_keys(stem)
    by_label = label_texts(stem, [k for k, _ in keys])
    by_label[lang] = {k: by_label.get(lang, {}).get(k, "") for k, _ in keys}      # every key, empty ones too
    return keys, by_label, statuses(c, stem, lang, "label", by_label)


def texts(stem, kind, narration_dir=None):
    return line_texts(stem, narration_dir) if kind == "line" else label_texts(stem)


# ─── the status of one item ───
def others_of(by_lang, lang, key):
    """{language: text} of the same item in the other languages (those with text)."""
    return {l: t[key] for l, t in by_lang.items() if l != lang and t.get(key, "").strip()}


def status(text, row, others):
    """{"state", "changed": {language: {"old", "new"}}} of one item: its text, its approval row (or None) and the
    other languages' current texts."""
    if not text.strip():
        return {"state": "empty", "changed": {}}
    if row is None or row["text_hash"] != digest(text):
        return {"state": "draft", "changed": {}}
    changed = {l: {"old": row["sources"][l], "new": t} for l, t in others.items()
               if l in row["sources"] and digest(t) != digest(row["sources"][l])}
    return {"state": "needs_update" if changed else "approved", "changed": changed}


def statuses(c, stem, lang, kind, by_lang):
    """{key: status} for every item of `lang` in `by_lang` ({language: {key: text}})."""
    rows = S.approvals(c, stem, lang, kind)
    mine = by_lang.get(lang, {})
    return {k: status(t, rows.get(k), others_of(by_lang, lang, k)) for k, t in mine.items()}


def counts(sts):
    out = {s: 0 for s in STATES}
    for st in sts.values():
        out[st["state"]] += 1
    out["total"] = len(sts)
    return out


# ─── the actions ───
def approve(c, stem, lang, kind, key, by_lang):
    """Approve the item's current text, with the other languages' texts as they are now."""
    text = by_lang.get(lang, {}).get(key, "")
    if not text.strip():
        raise ValueError("an empty line cannot be approved: draft its text first")
    S.approve(c, stem, lang, kind, key, digest(text), others_of(by_lang, lang, key))


def still_fine(c, stem, lang, kind, key, by_lang):
    """The other language changed and this one is still right: approve it again against the new texts."""
    st = statuses(c, stem, lang, kind, by_lang).get(key)
    if st is None or st["state"] != "needs_update":
        raise ValueError("nothing to confirm: this line is not waiting for an update")
    approve(c, stem, lang, kind, key, by_lang)


def save_line(c, stem, lang, key, text, narration_dir=None):
    """The instructor's edit of a line: written to the narration file (the other language of a bilingual file stays)
    and approved. Returns the text as written."""
    found = N.resolve(stem, lang, narration_dir)
    if not found:
        raise FileNotFoundError(f"no {LG.name(lang)} narration for {stem}: add the language first")
    _, new = N.set_line(found[0], lang, found[1], key, text)
    approve(c, stem, lang, "line", key, line_texts(stem, narration_dir))
    return new


def save_label(c, stem, lang, key, text):
    """The instructor's edit of a label's forms (one per line): written back to its label file and approved."""
    forms = [N.clean_text(lang, f, allow_empty=True) for f in text.split("\n")]
    LB.set_forms(stem, key, lang, forms)
    if any(forms):                                           # removing every form leaves nothing to approve
        approve(c, stem, lang, "label", key, label_texts(stem))
    return label_text([f for f in forms if f])


def approve_written(c, build, pairs, narration_dir=None):
    """A merged version put these lines in the build's language: approve them (`pairs`: [(key, text)])."""
    stem, lang = B.stem(build), B.lang(build)
    by_lang = line_texts(stem, narration_dir)
    for key, text in pairs:
        if N.norm(by_lang.get(lang, {}).get(key, "")) == N.norm(text):
            approve(c, stem, lang, "line", key, by_lang)
