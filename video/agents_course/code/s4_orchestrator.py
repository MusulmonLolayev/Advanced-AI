"""s4 · Orchestrator, worker and verifier — IDEA SNIPPET, not run."""


def handle(request, plan, work, verify, ask_human, max_retries=2):
    """The orchestrator splits the request; each worker sees only its
    subtask and its own tools (least privilege); a verifier checks
    every result against the data before anything is written."""
    results = []
    for subtask in plan(request):  # e.g. order → policy → file return
        for attempt in range(max_retries + 1):
            # a separate LLM call with a narrow tool list
            out = work(subtask, context=results)
            # a second model, or plain code: ids exist? totals add up?
            ok, why = verify(subtask, out)
            if ok:
                results.append(out)
                break
            subtask = f"{subtask}\nThe last attempt was rejected: {why}"
        else:  # fallback: a person decides, with the trail attached
            return ask_human(request, results, why)
    return results
# Each extra agent re-reads context: fewer tokens per call can still
# mean a larger bill overall.
