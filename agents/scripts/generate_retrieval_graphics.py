#!/usr/bin/env python3
"""Generate lecture figures for agents/ Lecture 6 (lecture06_*.tex).

Numbers come from numpy and from a small BM25 implementation in this file --
nothing on the slides is asserted without being computed here first. Rendering
is matplotlib, saved directly as vector PDF (and SVG); see the
pandas-vector-graphics skill. The bi-encoder / cross-encoder / late-interaction
architecture diagrams are schematic and live as inline TikZ in the .tex files.
"""

from pathlib import Path
import math
import re
import unicodedata

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "figures" / "retrieval"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand palette (see agents/theme/rl-theme.tex: RLBlue, RLGreen, RLOrange).
RLBLUE = "#3A35B7"
RLGREEN = "#5FA0A4"
RLORANGE = "#F4BD70"
RLRED = "#D6455D"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#222222",
    "text.color": "#222222",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
})


def save_fig(fig, name):
    fig.savefig(OUT_DIR / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT_DIR / f"{name}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"✓ {name}.pdf")
    print(f"✓ {name}.svg")


# ─── A small BM25, so the slide numbers are computed rather than invented ───
K1_DEFAULT, B_DEFAULT = 1.2, 0.75


def tokenize(text):
    """Unicode-aware word tokens. U+02BB/U+02BC are category Lm (letters), so
    \\w keeps them inside a word -- which is exactly the behaviour that makes an
    ASCII-apostrophe query fail to match a corpus written with U+02BB."""
    return re.findall(r"\w+", text.lower(), re.UNICODE)


def bm25_idf(n_docs, n_containing):
    return math.log((n_docs - n_containing + 0.5) / (n_containing + 0.5) + 1.0)


def bm25_score(query, doc_tokens, corpus_tokens, k1=K1_DEFAULT, b=B_DEFAULT):
    n_docs = len(corpus_tokens)
    avgdl = sum(len(d) for d in corpus_tokens) / n_docs
    dl = len(doc_tokens)
    total = 0.0
    for term in tokenize(query):
        n_q = sum(1 for d in corpus_tokens if term in d)
        if n_q == 0:
            continue
        f = doc_tokens.count(term)
        if f == 0:
            continue
        idf = bm25_idf(n_docs, n_q)
        total += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / avgdl))
    return total


# A tiny stand-in corpus of statute-style provisions. Jurisdiction-neutral
# English, matching how the lectures are written; the running Labor Code
# article is the first entry.
CORPUS = {
    "Art. 182": ("Normal working time may not exceed forty hours per week. "
                 "The employer establishes the working time schedule."),
    "Art. 183": ("Reduced working time is established for certain categories "
                 "of employees without reduction of pay."),
    "Art. 220": ("The employer shall pay wages at least twice a month on the "
                 "days established by the employment contract."),
    "Art. 241": ("Annual basic leave of not less than fifteen working days is "
                 "granted to every employee."),
    "Art. 99":  ("An employment contract is concluded in writing and signed by "
                 "both parties."),
}
CORPUS_TOKENS = {k: tokenize(v) for k, v in CORPUS.items()}
_tok_list = list(CORPUS_TOKENS.values())

print("BM25 worked example -- corpus of", len(CORPUS), "provisions")
print(f"  avgdl = {sum(len(d) for d in _tok_list) / len(_tok_list):.1f} tokens")

for q in ("working time hours per week",
          "how long is the standard workweek"):
    scores = {k: bm25_score(q, t, _tok_list) for k, t in CORPUS_TOKENS.items()}
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    print(f"\n  query: {q!r}")
    for art, s in ranked:
        print(f"    {art:9s} {s:6.3f}")

# The IDF values that make the ranking work, for quoting on the slide.
print("\n  IDF over this corpus (n_docs = 5):")
for term in ("working", "time", "week", "hours", "employer", "employee"):
    n_q = sum(1 for d in _tok_list if term in d)
    print(f"    {term:9s} in {n_q}/5 docs -> idf = {bm25_idf(5, n_q):.3f}")


# ─── Figure 1: term-frequency saturation, the reason BM25 is not just TF-IDF ─
print("\nFigure 1: BM25 term-frequency saturation ...")
f = np.linspace(0, 12, 400)
avg_len_doc = 1.0  # a document of exactly average length, so the b term is 1

fig, ax = plt.subplots(figsize=(4.2, 3.0))
ax.plot(f, f / f.max() * 1.0, color="#999999", linewidth=1.4, linestyle="--")
ax.annotate("raw count", xy=(6.4, 6.4 / 12), xytext=(4, -13),
            textcoords="offset points", fontsize=9, color="#777777",
            ha="left", va="top")
for k1, colour in ((0.5, RLORANGE), (1.2, RLBLUE), (2.0, RLGREEN)):
    sat = (f * (k1 + 1)) / (f + k1 * avg_len_doc)
    ax.plot(f, sat / (k1 + 1), color=colour, linewidth=1.9)
    ax.annotate(f"$k_1={k1}$", xy=(12.2, (12 * (k1 + 1) / (12 + k1)) / (k1 + 1)),
                fontsize=9, color=colour, va="center", ha="left")
    print(f"  k1={k1}: f=1 -> {(1*(k1+1))/(1+k1)/(k1+1):.3f}, "
          f"f=2 -> {(2*(k1+1))/(2+k1)/(k1+1):.3f}, "
          f"f=10 -> {(10*(k1+1))/(10+k1)/(k1+1):.3f}")
ax.set_xlabel("times the term occurs in the article", fontsize=10)
ax.set_ylabel("contribution to the score", fontsize=10)
ax.set_xlim(0, 17.5)
ax.set_ylim(0, 1.05)
ax.set_xticks([0, 2, 4, 6, 8, 10, 12])
ax.tick_params(labelsize=9)
ax.grid(True, linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "retrieval_bm25_saturation")


# ─── Figure 2: forward passes per query -- bi-encoder vs cross-encoder ──────
print("\nFigure 2: encoder cost against corpus size ...")
n = np.logspace(1, 6, 200)
CORPUS_N = 7368  # the capstone corpus: 7,368 articles

fig, ax = plt.subplots(figsize=(4.2, 3.0))
ax.loglog(n, n, color=RLRED, linewidth=2.0)
ax.loglog(n, np.ones_like(n), color=RLBLUE, linewidth=2.0)
ax.axvline(CORPUS_N, color="#999999", linewidth=1.1, linestyle=":")
ax.annotate("cross-encoder:\none pass per article", xy=(1.4e1, 1.6e5), fontsize=9,
            color=RLRED, ha="left", va="center")
ax.annotate("bi-encoder: one pass,\nthen dot products", xy=(15, 2.2), fontsize=9,
            color=RLBLUE, ha="left", va="bottom")
ax.annotate(f"{CORPUS_N:,}\narticles", xy=(CORPUS_N * 1.25, 55), fontsize=8.5,
            color="#666666", ha="left", va="center")
ax.set_xlabel("articles in the corpus", fontsize=10)
ax.set_ylabel("model passes per query", fontsize=10)
ax.set_ylim(0.5, 2e6)
ax.tick_params(labelsize=9)
ax.grid(True, which="major", linestyle=":", alpha=0.4)
fig.tight_layout()
save_fig(fig, "retrieval_encoder_cost")
print(f"  at {CORPUS_N:,} articles: cross-encoder = {CORPUS_N:,} passes, "
      f"bi-encoder = 1 pass + {CORPUS_N:,} dot products")


# ─── Figure 3: the lexical gap BM25 cannot cross ────────────────────────────
# Real lexical indexes drop stopwords. Once they do, a paraphrase that shares
# no content word with the article scores exactly zero everywhere -- the right
# article is not mis-ranked, it is unreachable. That is the honest motivation
# for dense retrieval, and it is computed here rather than asserted.
print("\nFigure 3: lexical overlap vs. paraphrase (stopwords removed) ...")
STOPWORDS = {"the", "a", "an", "is", "are", "of", "to", "in", "for", "on", "by",
             "and", "or", "how", "long", "at", "not", "may", "be", "shall",
             "every", "both", "with", "per", "its"}


def bm25_content(query, doc_tokens):
    content = " ".join(t for t in tokenize(query) if t not in STOPWORDS)
    return bm25_score(content, doc_tokens, _tok_list)


arts = list(CORPUS_TOKENS)
q_kw = "working time hours week"
q_par = "how long is the standard workweek"
kw_scores = [bm25_content(q_kw, CORPUS_TOKENS[a]) for a in arts]
par_scores = [bm25_content(q_par, CORPUS_TOKENS[a]) for a in arts]
print(f"  keyword    {q_kw!r}")
for a, s in zip(arts, kw_scores):
    print(f"    {a:9s} {s:6.3f}")
print(f"  paraphrase {q_par!r}  (content words: "
      f"{[t for t in tokenize(q_par) if t not in STOPWORDS]})")
for a, s in zip(arts, par_scores):
    print(f"    {a:9s} {s:6.3f}")

fig, axes = plt.subplots(1, 2, figsize=(4.4, 2.5), sharey=True)
x = np.arange(len(arts))
for ax, scores, title in (
        (axes[0], kw_scores, "keyword query"),
        (axes[1], par_scores, "paraphrase query")):
    colours = [RLGREEN if a == "Art. 182" else "#C9CDD4" for a in arts]
    ax.bar(x, scores, width=0.66, color=colours)
    ax.set_title(title, fontsize=9.5, loc="left")
    ax.set_xticks(x)
    ax.set_xticklabels([a.replace("Art. ", "") for a in arts], fontsize=8.5)
    ax.set_xlabel("article", fontsize=9)
    ax.tick_params(labelsize=9)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    ax.set_ylim(0, 5.4)
axes[0].set_ylabel("BM25 score", fontsize=10)
axes[0].annotate("4.53", xy=(0, kw_scores[0]), xytext=(0, 3),
                 textcoords="offset points", ha="center", fontsize=9,
                 color=RLGREEN)
axes[1].annotate("every article scores 0", xy=(2, 0.45), fontsize=9,
                 color=RLRED, ha="center", va="bottom")
fig.tight_layout()
save_fig(fig, "retrieval_lexical_gap")


# ─── The orthography trap, verified rather than asserted ───────────────────
print("\nOrthography check (claims that appear on a slide):")
OKINA = "ʻ"
variants = {
    "corpus (U+02BB)": "o" + OKINA + "rtacha",
    "typed (ASCII ')": "o'rtacha",
    "curly (U+2019)": "o’rtacha",
}
for name, w in variants.items():
    nf = {form: unicodedata.normalize(form, w) == variants["corpus (U+02BB)"]
          for form in ("NFC", "NFD", "NFKC", "NFKD")}
    print(f"  {name:17s} {w!r:14s} tokens={tokenize(w)}  "
          f"matches corpus after NFKC={nf['NFKC']}")
print(f"  U+02BB category = {unicodedata.category(OKINA)} "
      f"(a letter, so \\w keeps it inside the word)")
print(f"  U+0027 category = {unicodedata.category(chr(0x27))} "
      f"(punctuation, so \\w splits the word in two)")

print("\nAll Lecture 6 figures written to", OUT_DIR)
