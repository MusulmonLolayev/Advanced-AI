"""Our class agent, Lecture 1: a ReAct loop over the Labor Code of Uzbekistan.

The model writes a Thought and one Action as plain text; our code reads the Action, runs the tool, and appends the
result as an Observation. Then the model reads the whole trace again and writes the next Thought. It stops when the
model calls answer[...] or when the step limit is reached.

    python agent.py "What is the maximum normal working week?"
    python agent.py --replay q2_under18                       # a recorded run, no network needed
    python agent.py --record q2_under18 "..."                 # run live and save it

Switches for the session's experiments:
    --no-tools       no loop at all: ask the model once, from memory (what a plain chatbot does)
    --max-steps N    the step limit (default 8); too small, and the loop stops before the answer
    --no-stop        do not cut the model off at "Observation:" (the safety net against a model that writes the
                     tool's result itself; this model did not, see sessions/lecture01.md)
"""
import argparse
import re
import sys

from corpus import fetch_article, search
from llm import Model

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
ACTION = re.compile(r"^Action:\s*(\w+)\[(.*)\]\s*$", re.M | re.S)
STOP = ["Observation:"]          # the model is cut off here, so only our code can write an observation


def act(name, arg):
    """Run one action; the returned text is what the model sees as the Observation."""
    if name == "search":
        hits = search(arg)
        return "\n".join(f"Art. {a}: {title}" for a, title, _ in hits) or "no article contains these words"
    if name == "fetch_article":
        return fetch_article(arg) or f"there is no article {arg}"
    return f"unknown action {name}; the actions are search, fetch_article, answer"


def run(question, model, max_steps=8, stop=True, show=print):
    """The loop. Returns (answer or None, the trace as a list of turns)."""
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    trace = []
    for step in range(1, max_steps + 1):
        text = model.complete(messages, stop=STOP if stop else None).strip()
        messages.append({"role": "assistant", "content": text})
        m = ACTION.search(text)
        if m is None:
            obs = "I could not read an action. Write one line: Action: search[...], fetch_article[...] or answer[...]"
        elif m.group(1) == "answer":
            trace.append({"step": step, "model": text, "observation": None})
            show(f"\n── step {step}\n{text}")
            return m.group(2).strip(), trace
        else:
            obs = act(m.group(1), m.group(2).strip())
        trace.append({"step": step, "model": text, "observation": obs})
        show(f"\n── step {step}\n{text}\nObservation: {obs if len(obs) < 400 else obs[:400] + ' …'}")
        messages.append({"role": "user", "content": f"Observation: {obs}"})
    show(f"\n── stopped: {max_steps} steps without an answer")
    return None, trace


QUESTIONS = {   # the three questions of the Lecture 1 session
    "q1_week": "What is the maximum normal working week?",
    "q2_under18": "What is the maximum normal working week, and does it differ for employees under 18?",
    "q3_min_wage": "What is the minimum monthly wage in Uzbekistan, in soʻm?",
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--record", metavar="NAME")
    ap.add_argument("--replay", metavar="NAME")
    ap.add_argument("--no-stop", action="store_true")
    ap.add_argument("--max-steps", type=int, default=8)
    ap.add_argument("--no-tools", action="store_true")
    a = ap.parse_args()
    name = a.record or a.replay
    question = a.question or QUESTIONS.get(re.sub(r"_(nostop|notools\d*|steps\d+)$", "", name or ""))
    if a.replay:
        import json
        from llm import TRACES
        saved = json.loads((TRACES / f"{a.replay}.json").read_text())
        question, a.max_steps, a.no_stop = saved["question"], saved["max_steps"], not saved["stop"]
        a.no_tools = saved.get("no_tools", False)
    if not question:
        sys.exit("give a question, or --record/--replay one of: " + ", ".join(QUESTIONS))
    model = Model("replay" if a.replay else "record" if a.record else "live", name)
    print(f"Q: {question}")
    if a.no_tools:
        answer = model.complete([{"role": "system", "content": NO_TOOLS}, {"role": "user", "content": question}])
        trace = []
    else:
        answer, trace = run(question, model, max_steps=a.max_steps, stop=not a.no_stop)
    print(f"\nANSWER: {answer}")
    model.save({"question": question, "max_steps": a.max_steps, "stop": not a.no_stop, "no_tools": a.no_tools,
                "answer": answer,
                "trace": trace})
