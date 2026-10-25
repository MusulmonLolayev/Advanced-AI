# Lecture 1 assignment: the ReAct loop

## Goal

Build the loop that turns a language model into an agent: the model writes a Thought and one Action as plain text,
your code reads the Action, runs the tool, and feeds the result back as an Observation, until the model answers or the
step budget runs out. The agent answers questions about the Labor Code of Uzbekistan.

## What you will build

Four functions in `uz_agent/agent.py`, each marked by a `TODO` banner:

| Task | Function | In one sentence |
|---|---|---|
| Q1 | `parse_action(text)` | read `(name, argument)` from the model's `Action: name[argument]` line, or `None` |
| Q2 | `act(name, argument)` | run `search` or `fetch_article` and return the observation text; never raise on a bad action |
| Q3 | `observe(text)` | turn one model turn into `(answer, observation)`: answer, tool result, or the correction for an unreadable turn |
| Q4 | `run(question, model, ...)` | the loop: call the model, record the turn, return the answer, stop at the step budget |

The details and the edge cases are in the banner above each function. Everything else is given: `corpus.py` (the
tools over the article sample), `llm.py` (live, record and replay modes), `config.py`, and the command line in
`agent.py`.

## Before you start

This is Lecture 1 of Module 7 (`agents/lectures/` in the course repository); read its ReAct part first.
Python 3.10 or newer (the course machines use 3.13).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # only needed for a live run; the checks and the replays need no key
```

## The data

`data/sample_articles.jsonl` holds 40 articles of the Labor Code (581 in the whole Code), see `data/SOURCE.md`. The
model's prompt still says "581 articles", because the runs in `traces/` were recorded against the whole Code; do not
edit the prompt, or the recorded runs no longer replay. A live question that needs an article outside the sample gets
the observation "there is no article N".

## How to check

```bash
python -m uz_agent.self_checks
```

Each check prints one PASS or FAIL line. There are 17 checks. Until you write the code, the checks of your code fail
with `NotImplementedError: TODO: <function>`; the five checks of the given code pass from the start. A check that
replays a recorded run (`traces/*.json`) compares what your loop sends the model with what was sent when the run was
recorded, so a loop that builds the messages differently fails on the first call that differs.

See a recorded run once your code works: `python -m uz_agent.agent --replay q2_under18`. The notebook
`lecture01_react_loop.ipynb` walks through the same steps.

## Rules for editing

- Edit only what is between the lines `# *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****` and
  `# *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****`. Keep both lines. Delete the `raise
  NotImplementedError` line when you write your code.
- Do not edit `corpus.py`, `llm.py`, `config.py`, `self_checks.py`, the data or the traces.

## What to submit

```bash
./collectSubmission.sh
```

This writes `submission.zip` with `uz_agent/agent.py`, the notebook and `self_check_output.txt` (the output of the
self-checks). No network is used.

## Grading

The self-checks are the same checks the grader runs on your `agent.py`: if they all pass on your machine, the
automatic part of the grade is full. Answers to the free-form questions in the notebook are read by the instructor.

## Academic honesty

Write the four functions yourself. You may discuss the ideas with others and read the lecture; do not copy code from
another student or from a published solution, and do not edit the checks. Say in the notebook if you used an AI
assistant and for what.
