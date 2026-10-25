"""An optional example corpus: two UK laws on work, one regulation or section per record, with the same two tools.

The agent does not use it. Porting the agent to it is an optional assignment (STEPS.md).

The Working Time Regulations 1998 (WTR) and the National Minimum Wage Act 1998 (NMWA), as in force in Great Britain
on 1 October 2026 (data/SOURCE_UK.md). A provision's id is its law and number: "WTR 5A", "NMWA 1".
Same naive search as corpus.py: count the query's word stems that a provision contains, a title word counting twice.
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).parent / "data" / "uk_working_time.jsonl"
ARTICLES = {a["article_id"]: a for a in map(json.loads, DATA.read_text(encoding="utf-8").splitlines())}
ORDER = {k: i for i, k in enumerate(ARTICLES)}

# Words every provision is full of; matching them ranks nothing.
STOP = set("a an and any are as at be by for from has have he his in is it its may of on or shall such that the "
           "their this to under which who with".split())


def words(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower().replace("’", "'")) if w not in STOP]


def stems(text):
    """Crude stems: the first five letters, so work / worker / working and week / weekly meet."""
    return {w[:5] if len(w) > 5 else w.removesuffix("s") for w in words(text)}


STEMS = {k: stems(a["title"] + " " + a["text"]) for k, a in ARTICLES.items()}
TITLE_STEMS = {k: stems(a["title"]) for k, a in ARTICLES.items()}


def search(query, k=5):
    """The k provisions sharing the most word stems with the query, a word in the title counting twice:
    [(id, title, score)]."""
    q = stems(query)
    scored = sorted(((len(q & s) + len(q & TITLE_STEMS[a]), a) for a, s in STEMS.items() if q & s),
                    key=lambda x: (-x[0], ORDER[x[1]]))
    return [(a, ARTICLES[a]["title"], n) for n, a in scored[:k]]


def normalize_id(ref):
    """'wtr 5a', 'WTR reg. 5A', 'NMWA s.1', 'regulation 5A of the WTR' -> 'WTR 5A' / 'NMWA 1'."""
    s = ref.upper()
    law = "NMWA" if "NMWA" in s or "MINIMUM WAGE" in s else "WTR" if "WTR" in s or "WORKING TIME" in s else None
    num = re.search(r"\b(\d+[A-Z]{0,2})\b", s.replace("1998", ""))
    return f"{law} {num[1]}" if law and num else ref.strip()


def fetch_article(ref):
    """The full text of one provision, or None if there is no such provision."""
    a = ARTICLES.get(normalize_id(ref))
    return None if a is None else f"{a['article_id']} ({a['code_title']}, {a['unit']} {a['number']}). {a['title']}\n{a['text']}"

