"""s3 · Memory — IDEA SNIPPET, not run. Keep the context under
budget; keep facts outside it."""


def fit(messages, llm, budget_tokens, count_tokens):
    """In-context memory: when the conversation outgrows the budget,
    fold the oldest turns into a summary. The system prompt and the
    latest turns stay verbatim; tool results are the first thing to
    shrink."""
    system, rest = messages[0], messages[1:]
    while (count_tokens([system, *rest]) > budget_tokens
           and len(rest) > 6):
        old, rest = rest[:4], rest[4:]
        summary = llm("Summarise for later turns, "
                      f"keep ids and decisions:\n{old}")
        rest = [{"role": "user",
                 "content": f"[earlier, summarised] {summary}"}, *rest]
    return [system, *rest]


class Notes:
    """External memory: a key-value store the agent writes with a
    tool and reads back next session."""
    def __init__(self, store):  # a dict, Redis, a database table…
        self.store = store
    def remember(self, user_id, key, value):
        self.store.setdefault(user_id, {})[key] = value
    def recall(self, user_id): return self.store.get(user_id, {})
# At session start, recall(user_id) goes into the system prompt:
# "Known about this customer: …"
