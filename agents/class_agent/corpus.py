"""The Labor Code of Uzbekistan, one article per record, and the two tools the agent may call on it.

Lecture 1 keeps the tools deliberately naive: `search` counts how many of the query's words an article contains.
Lectures 5-7 replace it (chunking, BM25, embeddings, an ANN index); the interface stays the same.
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).parent / "data" / "mehnat_kodeksi.jsonl"
ARTICLES = {a["article_id"]: a for a in map(json.loads, DATA.read_text(encoding="utf-8").splitlines())}

# A keyboard gives ASCII ' or ‘ ’ where the corpus has ʻ (oʻ, gʻ) or ʼ (tutuq belgisi). Both sides are mapped to
# one character before matching, or "o'n sakkiz" would never find "oʻn sakkiz". Lecture 6 is about this line.
APOSTROPHES = str.maketrans({c: "ʻ" for c in "ʼ'‘’`"})


def words(text):
    return re.findall(r"\w+", text.lower().translate(APOSTROPHES))


def stems(text):
    """Crude stems: Uzbek adds suffixes (davomiylik, davomiyligi), so compare the first five letters."""
    return {w[:5] for w in words(text)}


STEMS = {k: stems(a["title"] + " " + a["text"]) for k, a in ARTICLES.items()}
TITLE_STEMS = {k: stems(a["title"]) for k, a in ARTICLES.items()}


def search(query, k=5):
    """The k articles sharing the most word stems with the query, a word in the title counting twice:
    [(article id, title, score)]."""
    q = stems(query)
    scored = sorted(((len(q & s) + len(q & TITLE_STEMS[a]), a) for a, s in STEMS.items() if q & s),
                    key=lambda x: (-x[0], int(x[1])))
    return [(a, ARTICLES[a]["title"], n) for n, a in scored[:k]]


def fetch_article(article_id):
    """The full text of one article, or None if there is no such article."""
    a = ARTICLES.get(str(article_id).strip().removesuffix("-modda").strip())
    return None if a is None else f"{a['article_display']}. {a['title']}\n{a['text']}"


# What the agent is told, and how its actions read (corpus_uk.py defines the same for the UK laws)
FETCH = "fetch_article"
CITE = "Art. {}"
NOT_FOUND = "no article contains these words"
MISSING = "there is no article {}"
SYSTEM = """You answer questions about the Labor Code of Uzbekistan (Mehnat kodeksi, 2022). You do not know its \
text; you can only read it with these actions:

  search[words]          keyword search over the 581 articles. The code is written in Uzbek (Latin script), \
so search with Uzbek words, for example: search[ish vaqtining davomiyligi]
  fetch_article[number]  the full text of one article, for example: fetch_article[182]
  answer[text]           your final answer, in English. Cite every claim as [Art. N]. If the code does not \
answer the question, say so.

Work in turns. In each turn write exactly two lines:
Thought: <your reasoning>
Action: <one action>
Then stop. The result comes back to you as "Observation: ...". Never write an Observation yourself."""

NO_TOOLS = "You answer questions about the Labor Code of Uzbekistan. Cite the article for every claim as [Art. N]."
QUESTIONS = {   # the three questions of the Lecture 1 session
    "q1_week": "What is the maximum normal working week?",
    "q2_under18": "What is the maximum normal working week, and does it differ for employees under 18?",
    "q3_min_wage": "What is the minimum monthly wage in Uzbekistan, in soʻm?",
}
