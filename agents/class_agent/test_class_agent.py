"""Tests for the class agent: the corpus, the tools, the loop, and every fact the Lecture 1 session and slides quote.

No network: the loop is driven by a scripted model, and the recorded runs are replayed.

    python -m unittest test_class_agent          (from agents/class_agent)
"""
import hashlib
import json
import re
import unittest

import agent
from corpus import ARTICLES, DATA, fetch_article, search
from llm import TRACES, Model

SOURCE = (DATA.parent / "SOURCE.md").read_text()


def trace(name):
    return json.loads((TRACES / f"{name}.json").read_text())


def cited(text):
    return set(re.findall(r"Art\. (\d+)", text))


class Corpus(unittest.TestCase):
    def test_the_file_is_the_pinned_one(self):
        digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
        self.assertIn(digest, SOURCE)
        self.assertEqual(len(ARTICLES), 581)

    def test_facts_the_session_quotes(self):
        self.assertIn("haftasiga qirq soatdan ortiq", fetch_article("182"))            # 40 hours a week
        a415 = fetch_article("415")
        self.assertIn("oʻn oltidan oʻn sakkiz yoshgacha", a415)                        # ages 16-18 ...
        self.assertIn("haftasiga oʻttiz olti soatdan", a415)                            # ... 36 hours
        self.assertIn("oʻn beshdan oʻn olti yoshgacha", a415)                           # ages 15-16 ...
        self.assertIn("haftasiga yigirma toʻrt soatdan", a415)                          # ... 24 hours
        a183 = fetch_article("183")
        self.assertIn("415-moddasi", a183)                                              # 183 points to 415 ...
        self.assertNotRegex(a183, r"oʻttiz olti|yigirma toʻrt")                          # ... and states no hours
        self.assertIn("eng kam miqdorini belgilash", fetch_article("245"))              # setting the minimum wage
        self.assertIn("Prezidenti tomonidan", fetch_article("245"))                     # ... by the President
        self.assertFalse([k for k, a in ARTICLES.items() if re.search(r"\d\s*soʻm", a["text"])])  # no amount anywhere
        self.assertIn("Ish haqini toʻlash muddatlari", fetch_article("253"))            # wage payment deadlines
        self.assertIn("ishdan chetlashtirish", fetch_article("153"))                    # suspension from work
        self.assertNotIn("oʻn toʻrt", a415)                                             # no 14-year-olds in 415
        self.assertIn("Dam olish kunlarida va ishlanmaydigan bayram kunlarida ishlashni taqiqlash", fetch_article("209"))


class Tools(unittest.TestCase):
    def test_search_finds_the_right_article_first(self):
        self.assertEqual(search("ish vaqtining normal davomiyligi")[0][0], "182")
        self.assertEqual(search("oʻn sakkiz yosh qisqartirilgan ish vaqti")[0][0], "415")
        self.assertEqual(search("mehnatga haq toʻlashning eng kam miqdori")[0][0], "245")

    def test_a_keyboard_apostrophe_finds_the_same_articles(self):
        self.assertEqual(search("o'n sakkiz yosh"), search("oʻn sakkiz yosh"))

    def test_fetch(self):
        self.assertEqual(fetch_article("182-modda"), fetch_article("182"))
        self.assertIsNone(fetch_article("1182"))
        self.assertIn("there is no article 1182", agent.act("fetch_article", "1182"))
        self.assertIn("unknown action", agent.act("calculator", "36/5"))


class Script:
    """A model that says what we tell it to, and remembers what it was asked."""
    def __init__(self, *replies):
        self.replies, self.seen = list(replies), []

    def complete(self, messages, stop=None):
        self.seen.append((list(messages), stop))
        return self.replies.pop(0)


class Loop(unittest.TestCase):
    def test_observations_go_back_and_answer_ends_the_loop(self):
        m = Script("Thought: look\nAction: fetch_article[182]", "Thought: done\nAction: answer[40 hours [Art. 182]]")
        answer, steps = agent.run("q", m, show=lambda *_: None)
        self.assertEqual(answer, "40 hours [Art. 182]")
        self.assertEqual(len(steps), 2)
        second_prompt = m.seen[1][0]
        self.assertTrue(second_prompt[-1]["content"].startswith("Observation: 182-modda"))
        self.assertEqual(m.seen[0][1], agent.STOP)                                     # cut off at "Observation:"

    def test_the_step_limit_stops_a_loop_that_never_answers(self):
        m = Script(*["Thought: again\nAction: search[ish vaqti]"] * 3)
        answer, steps = agent.run("q", m, max_steps=3, show=lambda *_: None)
        self.assertIsNone(answer)
        self.assertEqual(len(steps), 3)

    def test_an_unreadable_turn_gets_a_correction_not_a_crash(self):
        m = Script("I think it is 40 hours.", "Thought: format\nAction: answer[40 hours]")
        answer, steps = agent.run("q", m, show=lambda *_: None)
        self.assertEqual(answer, "40 hours")
        self.assertIn("could not read an action", steps[0]["observation"])

    def test_a_multi_line_answer_is_read_whole(self):
        m = Script("Thought: ok\nAction: answer[line one\nline two]")
        self.assertEqual(agent.run("q", m, show=lambda *_: None)[0], "line one\nline two")


class RecordedRuns(unittest.TestCase):
    """The runs the session replays, and what the slides say about them."""
    def test_every_run_replays_to_its_recorded_answer(self):
        for path in sorted(TRACES.glob("*.json")):
            t, m = json.loads(path.read_text()), Model("replay", path.stem)
            if t.get("no_tools"):
                got = m.complete([{"role": "system", "content": agent.NO_TOOLS},
                                  {"role": "user", "content": t["question"]}])
            else:
                got = agent.run(t["question"], m, max_steps=t["max_steps"], stop=t["stop"], show=lambda *_: None)[0]
            self.assertEqual(got, t["answer"], path.stem)

    def test_q1_one_search_one_fetch(self):
        t = trace("q1_week")
        self.assertEqual([re.search(r"Action: (\w+)", s["model"])[1] for s in t["trace"]],
                         ["search", "fetch_article", "answer"])
        self.assertEqual(cited(t["answer"]), {"182"})

    def test_q2_the_second_lookup_finds_415(self):
        t = trace("q2_under18")
        fetched = [re.search(r"fetch_article\[(\d+)\]", s["model"])[1] for s in t["trace"] if "fetch_article[" in s["model"]]
        self.assertEqual(fetched, ["182", "415"])
        self.assertEqual(cited(t["answer"]), {"182", "415"})
        self.assertRegex(t["answer"], r"forty hours")
        self.assertRegex(t["answer"], r"thirty-six hours.*twenty-four hours")

    def test_q3_says_the_code_has_no_amount(self):
        t = trace("q3_min_wage")
        self.assertEqual([re.search(r"Action: (\w+)\[(\d*)", s["model"]).groups() for s in t["trace"]],
                         [("search", ""), ("search", ""), ("fetch_article", "245"), ("search", ""),
                          ("fetch_article", "243"), ("search", ""), ("answer", "")])          # the slide's order
        self.assertIn("245", cited(t["answer"]))
        self.assertIn("does not", t["answer"])
        self.assertIsNone(trace("q3_min_wage_steps3")["answer"])                         # 3 steps are too few

    def test_without_tools_the_citations_are_wrong(self):
        q2 = trace("q2_under18_notools")["answer"]
        self.assertIn("36 hours", q2)
        self.assertEqual(cited(q2), {"182", "183"})            # the limits are in 415, which it never cites
        q3 = trace("q3_min_wage_notools")["answer"]
        self.assertIn("1,155,000", q3)                         # a figure the code does not contain
        self.assertIn("153", cited(q3))                        # 153 is about suspension from work
        again = trace("q3_min_wage_notools2")["answer"]          # the same question, asked again
        self.assertIn("1,270,000", again)                      # ... a different figure
        self.assertEqual(cited(again), {"209"})                # 209 forbids work on days off


if __name__ == "__main__":
    unittest.main()
