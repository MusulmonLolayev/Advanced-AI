"""Self-checks for the Lecture 1 assignment. They run offline: a scripted fake model and the recorded runs.

    python -m uz_agent.self_checks          one PASS / FAIL line per check, exit status 1 if any fails

The grader's visible checks are these same functions. A check marked @needs(...) exercises code you write; until
you do, it fails with NotImplementedError ("TODO: <function>"). The other checks test the code you are given.
"""
import hashlib
import json
import re
import sys
import traceback
from pathlib import Path

from uz_agent import agent, config, corpus
from uz_agent.llm import Model


def needs(*todo_functions):
    """Mark a check as exercising these TODO functions (used by the table the instructor's tool prints)."""
    def mark(fn):
        fn.needs = todo_functions
        return fn
    return mark


class Script:
    """A model that says what we tell it to, and remembers what it was asked."""
    def __init__(self, *replies):
        self.replies, self.seen = list(replies), []

    def complete(self, messages, stop=None):
        self.seen.append((list(messages), stop))
        return self.replies.pop(0)


def quiet(*_):
    pass


def saved(name):
    return json.loads((config.TRACES / f"{name}.json").read_text(encoding="utf-8"))


def actions(name):
    """The (action, argument) of each recorded turn; an answer's argument is left out."""
    found = [re.search(r"Action: (\w+)\[(.*)\]", t["model"], re.S) for t in saved(name)["trace"]]
    return [(m[1], None if m[1] == "answer" else m[2]) for m in found]


def cited(text):
    return set(re.findall(r"Art\. (\d+)", text))


# ---- the code you are given ------------------------------------------------------------------------------------

def check_sample_is_pinned() -> None:
    note = (config.DATA.parent / "SOURCE.md").read_text(encoding="utf-8")
    assert hashlib.sha256(config.DATA.read_bytes()).hexdigest() in note, "data/SOURCE.md names another file"
    assert len(corpus.ARTICLES) == 40, f"the sample has {len(corpus.ARTICLES)} articles, not 40"
    assert "40 articles" in note


def check_search_and_fetch() -> None:
    assert corpus.search("ish vaqtining normal davomiyligi")[0][0] == "182"
    assert corpus.search("oʻn sakkiz yosh qisqartirilgan ish vaqti")[0][0] == "415"
    assert corpus.search("mehnatga haq toʻlashning eng kam miqdori")[0][0] == "245"
    assert corpus.search("o'n sakkiz yosh") == corpus.search("oʻn sakkiz yosh"), "keyboard apostrophe"
    assert corpus.fetch_article("182-modda") == corpus.fetch_article("182")
    assert corpus.fetch_article("1182") is None
    assert "haftasiga qirq soatdan ortiq" in corpus.fetch_article("182")
    assert "oʻn oltidan oʻn sakkiz yoshgacha" in corpus.fetch_article("415")


def check_recorded_runs_have_the_expected_shape() -> None:
    assert [a for a, _ in actions("q1_week")] == ["search", "fetch_article", "answer"]
    assert cited(saved("q1_week")["answer"]) == {"182"}
    fetched = [arg for name, arg in actions("q2_under18") if name == "fetch_article"]
    assert fetched == ["182", "415"], fetched
    assert len(saved("q3_min_wage")["trace"]) == 7
    assert saved("q3_min_wage_steps3")["max_steps"] == 3 and saved("q3_min_wage_steps3")["answer"] is None
    assert saved("q1_week_nostop")["stop"] is False and saved("q1_week")["stop"] is True


def check_replay_rejects_a_changed_prompt() -> None:
    model = Model("replay", "q1_week")
    try:
        model.complete([{"role": "system", "content": "not the recorded prompt"}], stop=agent.STOP)
    except RuntimeError as e:
        assert "differs from the recording" in str(e)
    else:
        raise AssertionError("a prompt that is not the recorded one was accepted")


def check_constants_for_the_model() -> None:
    assert corpus.UNREADABLE.startswith("I could not read an action.")
    assert "fetch_article[number]" in corpus.SYSTEM and "answer[text]" in corpus.SYSTEM
    assert agent.STOP == ["Observation:"]


# ---- Q1-Q4: the code you write ---------------------------------------------------------------------------------

@needs("parse_action")
def check_parse_action() -> None:
    assert agent.parse_action("Thought: look\nAction: search[ish vaqti]") == ("search", "ish vaqti")
    assert agent.parse_action("Thought: x\nAction:   fetch_article[ 182 ]  ") == ("fetch_article", "182")
    assert agent.parse_action("Thought: x\nAction: answer[40 hours [Art. 182]]") == ("answer", "40 hours [Art. 182]")
    assert agent.parse_action("Action: answer[line one\nline two]") == ("answer", "line one\nline two")
    assert agent.parse_action("I think it is 40 hours.") is None
    assert agent.parse_action("") is None
    assert agent.parse_action("I will take an Action: later, maybe search[x] too") is None, "Action must start a line"


@needs("act")
def check_act() -> None:
    hits = corpus.search("ish vaqtining normal davomiyligi")
    expected = "\n".join(f"Art. {a}: {title}" for a, title, _ in hits)
    assert agent.act("search", "ish vaqtining normal davomiyligi") == expected
    assert agent.act("search", "zzzz qqqq") == corpus.NOT_FOUND
    assert agent.act("fetch_article", "182") == corpus.fetch_article("182")
    assert agent.act("fetch_article", "1182") == "there is no article 1182"
    assert agent.act("calculator", "36/5") == "unknown action calculator; the actions are search, fetch_article, answer"


@needs("observe", "parse_action", "act")
def check_observe() -> None:
    assert agent.observe("Thought: x\nAction: answer[40 hours]") == ("40 hours", None)
    assert agent.observe("Action: answer[]") == ("", None), "an empty answer is still an answer"
    assert agent.observe("Thought: x\nAction: fetch_article[182]") == (None, corpus.fetch_article("182"))
    assert agent.observe("I think it is 40 hours.") == (None, corpus.UNREADABLE)
    assert agent.observe("") == (None, corpus.UNREADABLE)


@needs("run", "observe", "parse_action", "act")
def check_observations_go_back_and_answer_ends_the_loop() -> None:
    model = Script("Thought: look\nAction: fetch_article[182]", "Thought: done\nAction: answer[40 hours [Art. 182]]")
    answer, trace = agent.run("q", model, show=quiet)
    assert answer == "40 hours [Art. 182]"
    assert len(trace) == 2 and [t["step"] for t in trace] == [1, 2]
    assert trace[0]["observation"] == corpus.fetch_article("182") and trace[1]["observation"] is None
    second_prompt = model.seen[1][0]
    assert [m["role"] for m in second_prompt] == ["system", "user", "assistant", "user"]
    assert second_prompt[-1]["content"] == "Observation: " + corpus.fetch_article("182")
    assert model.seen[0][1] == agent.STOP, "the model must be cut off at Observation:"
    unstopped = Script("Action: answer[x]")
    agent.run("q", unstopped, stop=False, show=quiet)
    assert unstopped.seen[0][1] is None


@needs("run", "observe", "parse_action", "act")
def check_step_budget() -> None:
    model = Script(*["Thought: again\nAction: search[ish vaqti]"] * 3)
    shown = []
    answer, trace = agent.run("q", model, max_steps=3, show=shown.append)
    assert answer is None and len(trace) == 3 and model.replies == []
    assert any("stopped: 3 steps" in line for line in shown), "say that the budget ran out"


@needs("run", "observe", "parse_action", "act")
def check_unreadable_turn_gets_a_correction_not_a_crash() -> None:
    model = Script("I think it is 40 hours.", "Thought: format\nAction: answer[40 hours]")
    answer, trace = agent.run("q", model, show=quiet)
    assert answer == "40 hours"
    assert trace[0]["observation"] == corpus.UNREADABLE
    assert model.seen[1][0][-1]["content"] == "Observation: " + corpus.UNREADABLE


@needs("run", "observe", "parse_action", "act")
def check_multi_line_answer_is_read_whole() -> None:
    model = Script("Thought: ok\nAction: answer[line one\nline two]")
    assert agent.run("q", model, show=quiet)[0] == "line one\nline two"


def replay(name):
    """Run a recorded question through your loop, on the model's recorded replies."""
    want, model = saved(name), Model("replay", name)
    answer, trace = agent.run(want["question"], model, max_steps=want["max_steps"], stop=want["stop"], show=quiet)
    assert answer == want["answer"], f"{name}: answer differs"
    assert trace == want["trace"], f"{name}: the trace differs from the recorded one"
    assert len(model.calls) == len(want["calls"]), f"{name}: the model was called {len(model.calls)} times"


@needs("run", "observe", "parse_action", "act")
def check_replay_q1_week() -> None:
    replay("q1_week")


@needs("run", "observe", "parse_action", "act")
def check_replay_q2_under18() -> None:
    replay("q2_under18")
    assert cited(saved("q2_under18")["answer"]) == {"182", "415"}


@needs("run", "observe", "parse_action", "act")
def check_replay_q3_min_wage() -> None:
    replay("q3_min_wage")


@needs("run", "observe", "parse_action", "act")
def check_replay_with_a_budget_too_small() -> None:
    replay("q3_min_wage_steps3")


@needs("run", "observe", "parse_action", "act")
def check_replay_without_the_stop() -> None:
    replay("q1_week_nostop")


ALL_CHECKS = [
    check_sample_is_pinned,
    check_search_and_fetch,
    check_recorded_runs_have_the_expected_shape,
    check_replay_rejects_a_changed_prompt,
    check_constants_for_the_model,
    check_parse_action,
    check_act,
    check_observe,
    check_observations_go_back_and_answer_ends_the_loop,
    check_step_budget,
    check_unreadable_turn_gets_a_correction_not_a_crash,
    check_multi_line_answer_is_read_whole,
    check_replay_q1_week,
    check_replay_q2_under18,
    check_replay_q3_min_wage,
    check_replay_with_a_budget_too_small,
    check_replay_without_the_stop,
]


def run_all_checks(verbose=True):
    """Run every check; return [{"name", "needs", "status": "PASS" or "FAIL", "error", "message"}]."""
    results = []
    for fn in ALL_CHECKS:
        row = {"name": fn.__name__, "needs": list(getattr(fn, "needs", ())), "status": "PASS", "error": None,
               "message": ""}
        try:
            fn()
        except Exception as e:                     # a failing check is a result, not a crash
            row.update(status="FAIL", error=type(e).__name__, message=str(e) or traceback.format_exc(limit=-1))
        results.append(row)
        if verbose:
            detail = "" if row["status"] == "PASS" else f"  {row['error']}: {row['message'].splitlines()[0] if row['message'] else ''}"
            print(f"{row['status']}  {row['name']}{detail}")
    if verbose:
        failed = [r for r in results if r["status"] == "FAIL"]
        print(f"\n{len(results) - len(failed)} of {len(results)} checks passed." if failed
              else f"\nAll {len(results)} Lecture 1 self-checks passed.")
    return results


if __name__ == "__main__":
    as_json = "--json" in sys.argv
    outcome = run_all_checks(verbose=not as_json)
    if as_json:
        print(json.dumps(outcome))
    sys.exit(1 if any(r["status"] == "FAIL" for r in outcome) else 0)
