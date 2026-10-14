"""s5 · Retrieval-augmented answers with hybrid search — IDEA SNIPPET, not run.
τ²-bench's banking_knowledge domain ships this as tools: KB_search_bm25 and KB_search_dense."""


def rrf(rankings, k=60):
    """Reciprocal rank fusion: merge ranked lists without comparing their scores."""
    score = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, 1):
            score[doc_id] = score.get(doc_id, 0) + 1 / (k + rank)
    return sorted(score, key=score.get, reverse=True)


def answer(question, bm25, dense, rerank, llm, top=5):
    candidates = rrf([bm25.search(question, 50), dense.search(question, 50)])   # wide and cheap
    passages = rerank(question, candidates[:30])[:top]                          # narrow and precise
    context = "\n\n".join(f"[{p.id}] {p.text}" for p in passages)
    return llm(f"Answer only from these passages and cite their [ids]. "
               f"If they do not contain the answer, say so.\n\n{context}\n\nQuestion: {question}")
