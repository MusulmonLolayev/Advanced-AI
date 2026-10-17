"""Our class agent, Lecture 1: a ReAct loop over the Labor Code of Uzbekistan (or, with --law uk, two UK laws on
work for the English version: corpus_uk.py).

The model writes a Thought and one Action as plain text; our code reads the Action, runs the tool, and appends the
result as an Observation. Then the model reads the whole trace again and writes the next Thought. It stops when the
model calls answer[...] or when the step limit is reached.

    python agent.py "What is the maximum normal working week?"
    python agent.py --replay q2_under18                       # a recorded run, no network needed
    python agent.py --record q2_under18 "..."                 # run live and save it
    python agent.py --law uk --replay q2_under18              # the English version's run (traces/uk/)

Switches for the session's experiments:
    --no-tools       no loop at all: ask the model once, from memory (what a plain chatbot does)
    --max-steps N    the step limit (default 8); too small, and the loop stops before the answer
    --no-stop        do not cut the model off at "Observation:" (the safety net against a model that writes the
                     tool's result itself; this model did not, see sessions/lecture01.md)
"""
import argparse
import re
import sys

import corpus
import corpus_uk
from corpus import NO_TOOLS, QUESTIONS, SYSTEM  # noqa: F401  the Uzbek law's, as before
from llm import Model

ACTION = re.compile(r"^Action:\s*(\w+)\[(.*)\]\s*$", re.M | re.S)
STOP = ["Observation:"]          # the model is cut off here, so only our code can write an observation

LAWS = {"uz": corpus, "uk": corpus_uk}     # each law: its tools, its prompts, its actions' wording, its questions


def act(name, arg, law=corpus):
    """Run one action; the returned text is what the model sees as the Observation."""
    if name == "search":
        hits = law.search(arg)
        return "\n".join(f"{law.CITE.format(a)}: {title}" for a, title, _ in hits) or law.NOT_FOUND
    if name == law.FETCH:
        return law.fetch_article(arg) or law.MISSING.format(arg)
    return f"unknown action {name}; the actions are search, {law.FETCH}, answer"


def run(question, model, max_steps=8, stop=True, show=print, law=corpus):
    """The loop. Returns (answer or None, the trace as a list of turns)."""
    messages = [{"role": "system", "content": law.SYSTEM}, {"role": "user", "content": question}]
    trace = []
    for step in range(1, max_steps + 1):
        text = model.complete(messages, stop=STOP if stop else None).strip()
        messages.append({"role": "assistant", "content": text})
        m = ACTION.search(text)
        if m is None:
            obs = f"I could not read an action. Write one line: Action: search[...], {law.FETCH}[...] or answer[...]"
        elif m.group(1) == "answer":
            trace.append({"step": step, "model": text, "observation": None})
            show(f"\n── step {step}\n{text}")
            return m.group(2).strip(), trace
        else:
            obs = act(m.group(1), m.group(2).strip(), law)
        trace.append({"step": step, "model": text, "observation": obs})
        show(f"\n── step {step}\n{text}\nObservation: {obs if len(obs) < 400 else obs[:400] + ' …'}")
        messages.append({"role": "user", "content": f"Observation: {obs}"})
    show(f"\n── stopped: {max_steps} steps without an answer")
    return None, trace



if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--record", metavar="NAME")
    ap.add_argument("--replay", metavar="NAME")
    ap.add_argument("--no-stop", action="store_true")
    ap.add_argument("--max-steps", type=int, default=8)
    ap.add_argument("--no-tools", action="store_true")
    ap.add_argument("--law", choices=LAWS, default="uz", help="uz: the Labor Code (default); uk: the UK laws")
    a = ap.parse_args()
    law = LAWS[a.law]
    question = a.question or law.QUESTIONS.get(re.sub(r"_(nostop|notools\d*|steps\d+)$", "", a.record or a.replay or ""))
    name = (a.record or a.replay) and ("uk/" if a.law == "uk" else "") + (a.record or a.replay)
    if a.replay:
        import json
        from llm import TRACES
        saved = json.loads((TRACES / f"{name}.json").read_text())
        question, a.max_steps, a.no_stop = saved["question"], saved["max_steps"], not saved["stop"]
        a.no_tools = saved.get("no_tools", False)
    if not question:
        sys.exit("give a question, or --record/--replay one of: " + ", ".join(QUESTIONS))
    model = Model("replay" if a.replay else "record" if a.record else "live", name)
    print(f"Q: {question}")
    if a.no_tools:
        answer = model.complete([{"role": "system", "content": law.NO_TOOLS}, {"role": "user", "content": question}])
        trace = []
    else:
        answer, trace = run(question, model, max_steps=a.max_steps, stop=not a.no_stop, law=law)
    print(f"\nANSWER: {answer}")
    model.save({"question": question, "max_steps": a.max_steps, "stop": not a.no_stop, "no_tools": a.no_tools,
                "answer": answer,
                "trace": trace})
