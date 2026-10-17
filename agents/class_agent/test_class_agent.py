"""Tests for the class agent: the corpus, the tools, the loop, and every fact the Lecture 1 session and slides quote.

No network: the loop is driven by a scripted model, and the recorded runs are replayed.

    python -m unittest test_class_agent          (from agents/class_agent)
"""
import hashlib
import json
import re
import unittest

import agent
import corpus_uk as uk
from corpus import ARTICLES, DATA, fetch_article, search
from llm import TRACES, Model

SOURCE = (DATA.parent / "SOURCE.md").read_text()


def trace(name):
    return json.loads((TRACES / f"{name}.json").read_text())


def cited(text):
    return set(re.findall(r"Art\. (\d+)", text))


def cited_uk(text):
    """Provisions cited, subsections dropped: [WTR 4(6)–(7)] -> 'WTR 4'."""
    return {f"{law} {n}" for law, n in re.findall(r"\b(WTR|NMWA) (\d+[A-Z]?)", text)}


def paragraph(ref, label):
    """One numbered line of a provision: paragraph('WTR 4', '(3)')."""
    return next(line for line in uk.ARTICLES[ref]["text"].splitlines() if line.startswith(label + " "))


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


class UKCorpus(unittest.TestCase):
    """The English version's corpus (corpus_uk.py): the Working Time Regulations 1998 and the NMW Act 1998."""
    def test_the_file_is_the_pinned_one(self):
        self.assertIn(hashlib.sha256(uk.DATA.read_bytes()).hexdigest(), (uk.DATA.parent / "SOURCE_UK.md").read_text())
        self.assertEqual(len(uk.ARTICLES), 118)
        self.assertEqual(sum(k.startswith("WTR ") for k in uk.ARTICLES), 64)

    def test_facts_the_session_quotes(self):
        self.assertIn("an average of 48 hours for each seven days", paragraph("WTR 4", "(1)"))
        self.assertIn("agreement in writing", paragraph("WTR 4", "(1)"))                 # the opt-out is in 4(1)
        self.assertIn("any period of 17 weeks", paragraph("WTR 4", "(b)"))              # 4(3)(b)
        self.assertIn("reference periods", paragraph("WTR 4", "(3)"))
        self.assertNotIn("17 weeks", paragraph("WTR 4", "(2)"))                         # 4(2): the employer's duty
        self.assertNotRegex(paragraph("WTR 5", "(1)"), r"[a-z]")                         # 5(1) is repealed: dots
        self.assertEqual(paragraph("WTR 5A", "(a)"), "(a) eight hours a day, or")
        self.assertEqual(paragraph("WTR 5A", "(b)"), "(b) 40 hours a week.")
        self.assertIn("attained the age of 15 but not the age of 18", uk.fetch_article("WTR 2"))
        self.assertIn("such single hourly rate as the Secretary of State may from time to time prescribe",
                      paragraph("NMWA 1", "(3)"))
        self.assertIn("the hourly rate at which a person is to be regarded", paragraph("NMWA 2", "(1)"))
        self.assertIn("provision for determining the hourly rate in cases where", paragraph("NMWA 2", "(2)"))
        self.assertIn("have not attained the age of 26", paragraph("NMWA 3", "(1)"))
        self.assertIn("an hourly rate for the national minimum wage other than the single hourly rate",
                      uk.ARTICLES["NMWA 3"]["text"])                            # other rates by group: s. 3(2)(b)
        self.assertFalse([k for k, a in uk.ARTICLES.items() if re.search(r"£\s*\d", a["text"])])  # no amount anywhere

    def test_search_and_fetch(self):
        self.assertEqual(uk.search("maximum weekly working time")[0][0], "WTR 4")
        self.assertEqual(uk.search("young workers working time")[0][0], "WTR 5A")
        self.assertEqual(uk.search("national minimum wage")[0][0], "NMWA 1")
        self.assertEqual(uk.search("£"), [])                       # a symbol is not a word: nothing to match
        self.assertEqual(agent.act("search", "£", uk), "no provision contains these words")
        self.assertEqual(uk.fetch_article("wtr reg. 5a"), uk.fetch_article("WTR 5A"))
        self.assertEqual(uk.fetch_article("NMWA s.1"), uk.fetch_article("NMWA 1"))
        self.assertIn("there is no provision WTR 99", agent.act("fetch", "WTR 99", uk))
        self.assertIn("the actions are search, fetch, answer", agent.act("fetch_article", "WTR 4", uk))


class UKRecordedRuns(unittest.TestCase):
    """The English version's runs (traces/uk/), and what its slides and video may say about them."""
    def setUp(self):
        self.t = lambda name: trace(f"uk/{name}")

    def actions(self, name):
        """[(action, argument)], (None, None) for a turn with no action; an answer's argument is left out."""
        found = [re.search(r"Action: (\w+)\[(.*)\]", s["model"], re.S) for s in self.t(name)["trace"]]
        return [(m[1], None if m[1] == "answer" else m[2]) if m else (None, None) for m in found]

    def test_every_run_replays_to_its_recorded_answer(self):
        for path in sorted((TRACES / "uk").glob("*.json")):
            t, m = json.loads(path.read_text()), Model("replay", f"uk/{path.stem}")
            if t.get("no_tools"):
                got = m.complete([{"role": "system", "content": uk.NO_TOOLS}, {"role": "user", "content": t["question"]}])
            else:
                got = agent.run(t["question"], m, max_steps=t["max_steps"], stop=t["stop"], show=lambda *_: None,
                                law=uk)[0]
            self.assertEqual(got, t["answer"], path.stem)

    def test_q1_an_empty_turn_gets_the_correction(self):
        self.assertEqual(self.actions("q1_week"), [("search", "maximum weekly working time"), ("fetch", "WTR 4"),
                                                   (None, None), ("fetch", "WTR 5A"), ("answer", None)])
        empty = self.t("q1_week")["trace"][2]
        self.assertEqual(empty["model"], "")
        self.assertIn("could not read an action", empty["observation"])
        self.assertEqual(cited_uk(self.t("q1_week")["answer"]), {"WTR 4", "WTR 5A"})
        self.assertRegex(self.t("q1_week")["answer"], r"average of 48 hours.*17 weeks.*40 hours a week")

    def test_q2_reads_the_definition_too(self):
        fetched = [a for name, a in self.actions("q2_under18") if name == "fetch"]
        self.assertEqual(fetched, ["WTR 4", "WTR 5A", "WTR 2"])
        a = self.t("q2_under18")["answer"]
        self.assertEqual(cited_uk(a), {"WTR 4", "WTR 2", "WTR 5A"})
        for fact in ("average of 48 hours", "17 weeks", "attained the age of 15 but not 18", "8 hours a day or 40 hours a week"):
            self.assertIn(fact, a)

    def test_what_the_english_narration_quotes(self):
        """video/narration/m7_lecture01_en.md, lines 33, 34, 66a, 71, 74a."""
        q2 = self.t("q2_under18")["trace"]
        self.assertNotIn("WTR 2:", q2[3]["observation"])                        # the search did not list WTR 2 ...
        self.assertIn("likely in the interpretation provision", q2[4]["model"])  # ... the thought chose it
        q3 = self.t("q3_min_wage")["trace"]
        self.assertIn("or delegates it to regulations", q3[0]["model"])          # before reading anything
        self.assertIn("No monetary figure appears anywhere", q3[3]["model"])     # after the empty £ search
        self.assertEqual(self.actions("q3_min_wage_steps3")[2], ("search", "pounds per hour"))
        notools = self.t("q3_min_wage_notools")["answer"]
        self.assertIn("From 1 April 2026", notools)
        self.assertIn("**21 and over:** £12.71", notools)
        self.assertIn("does not itself set a pound-per-hour figure", notools)

    def test_q3_says_the_act_has_no_amount(self):
        self.assertEqual([n for n, _ in self.actions("q3_min_wage")], ["search", "fetch", "search", "answer"])
        self.assertEqual(self.actions("q3_min_wage")[2], ("search", "£"))         # a search that cannot match anything
        a = self.t("q3_min_wage")["answer"]
        self.assertIn("does not itself state", a)
        self.assertEqual(cited_uk(a), {"NMWA 1"})
        self.assertIsNone(self.t("q3_min_wage_steps3")["answer"])                # 3 steps are too few
        self.assertEqual(len(self.t("q3_min_wage_steps3")["trace"]), 3)

    def test_without_the_stop_it_still_wrote_no_observation(self):
        self.assertFalse([s for s in self.t("q1_week_nostop")["trace"] if "Observation:" in s["model"]])

    def test_without_tools_the_citations_are_wrong(self):
        q2 = self.t("q2_under18_notools")["answer"]
        self.assertIn("the reference period is **17 weeks** [WTR 4(2)]", q2)   # 17 weeks is 4(3); 4(2) is not it
        self.assertIn("[WTR 5(1)]", q2)                                         # a repealed paragraph
        self.assertNotRegex(q2, r"\b8 hours|eight hours")                       # the daily limit is missing
        q3 = self.t("q3_min_wage_notools")["answer"]
        self.assertIn("£12.71", q3)                                             # from memory; not in the corpus
        self.assertIn("NMW Regulations 2015", q3)
        again = self.t("q3_min_wage_notools2")["answer"]                        # the same question, asked again
        self.assertNotRegex(again, r"£\s*\d")                                  # ... no figure this time
        self.assertIn("[NMWA 2(1)]", again)                                     # the rate is in 1(3), not 2(1)
        self.assertIn("[NMWA 2(2)]", again)                                     # rates by group: 3(2)(b), not 2(2)


if __name__ == "__main__":
    unittest.main()
