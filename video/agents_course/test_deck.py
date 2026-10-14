"""Unit tests for every number the agent-course video speaks or shows that is not a live result.

Each test recomputes a value with capture_deck.compute() and checks it against what the slides
(agents/lectures/*.tex) print, what the τ²-bench clone contains, and what the narration
(narration/agents_course.md) says. Quoted paper figures must still appear in the deck text, the saved JSON must
equal a fresh compute(), and every live-run number must still be a {{placeholder}}.
    cd video && uv run python -m unittest discover -s agents_course -p 'test_deck.py'
"""
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import capture_deck as C  # noqa: E402

V = C.compute()
T = V["tau2"]
DECK = "\n".join(p.read_text() for p in sorted((C.REPO / "agents/lectures").glob("*.tex")))
NARR = (C.REPO / "video/narration/agents_course.md").read_text()
SPOKEN = " ".join(re.findall(r"^\s*\d+\.\s+(?:⏸\s*)?\*\*(.+)\*\*\s*$", NARR, re.M))


def said(phrase):
    return phrase in SPOKEN


class Section1Loop(unittest.TestCase):
    def test_bill_table(self):
        self.assertEqual({n: (b["billed"], b["new_only"]) for n, b in V["bill"].items()},
                         {"3": (5100, 2700), "10": (34500, 6200), "20": (119000, 11200)})
        self.assertIn("$34{,}500$", DECK)
        self.assertEqual(V["bill_ratio_20_10"], 3.4)                       # slide: "3.4, not by 2"
        self.assertTrue(said("thirty-four thousand five hundred input tokens"))
        self.assertTrue(said("a hundred and nineteen thousand"))
        self.assertTrue(said("three point four"))

    def test_cache(self):
        c = V["cache10"]
        self.assertEqual((c["full"], c["hit"]), (5700, 28800))
        self.assertEqual((c["cost_cached"], c["cost_uncached"]), (0.00094, 0.00517))
        self.assertEqual((c["ratio"], c["eval_cached"], c["eval_uncached"]), (5.5, 0.47, 2.59))
        self.assertTrue(said("five and a half times cheaper"))
        self.assertTrue(said("forty-seven cents instead of two dollars fifty-nine"))
        self.assertTrue(said("three tenths of a cent per million tokens instead of fifteen cents"))
        self.assertEqual((C.PRICE_CACHED * 100, C.PRICE_IN * 100), (0.3, 15.0))

    def test_compounding(self):
        self.assertEqual(V["p10"], 0.599)
        self.assertEqual((V["p_low_10"], V["p_low_5"]), (0.35, 0.59))
        self.assertTrue(said("Zero point three five becomes zero point five nine"))
        self.assertTrue(said("about six in ten"))


class Section2Schemas(unittest.TestCase):
    def test_format_rate(self):
        self.assertEqual(V["q10"], 0.82)
        self.assertTrue(said("zero point eight two of the time"))

    def test_schema_tokens(self):
        self.assertEqual(V["schema_billed_10"], 4000)                       # deck number; not spoken in draft 2

    def test_cancel_reasons(self):
        self.assertEqual(T["cancel_reasons"], ["no longer needed", "ordered by mistake"])
        self.assertTrue(said('exactly two reasons for a cancellation: "no longer needed" and "ordered by mistake"'))
        policy = (C.RETAIL / "policy.md").read_text()
        self.assertIn("either 'no longer needed' or 'ordered by mistake'", policy)

    def test_tool_refusal_quoted(self):
        src = (C.TAU2 / "src/tau2/domains/retail/tools.py").read_text()
        self.assertIn("Non-pending order cannot be cancelled", src)
        self.assertIn("Non-pending order cannot be cancelled", NARR)
        self.assertIn("ask for explicit user confirmation", src)


class Section3Memory(unittest.TestCase):
    def test_turns(self):
        self.assertEqual((V["turns_uncapped"], V["turns_capped"], V["turns_ratio"]), (11, 62, 5.6))
        self.assertTrue(said("three thousand tokens per call lasts eleven turns"))
        self.assertTrue(said("about five hundred tokens, lasts sixty-two"))
        self.assertTrue(said("five point six times"))

    def test_authenticate_every_time(self):
        policy = (C.RETAIL / "policy.md").read_text()
        self.assertIn("This has to be done even when the user already provides the user id", policy)


class Section4Orchestration(unittest.TestCase):
    def test_tokens(self):
        o = V["orch"]
        self.assertEqual((o["single_tokens"], o["multi_tokens"], o["fewer_pct"]), (47400, 33000, 30))
        self.assertTrue(said("thirty-three thousand against forty-seven thousand four hundred, thirty percent fewer"))

    def test_caching_inverts(self):
        o = V["orch"]
        self.assertEqual((o["single_full"], o["single_hit"], o["multi_full"], o["multi_hit"]),
                         (6700, 40700, 11700, 21300))
        self.assertEqual((o["single_cost"], o["multi_cost"]), (0.00113, 0.00182))
        self.assertEqual((o["single_eval"], o["multi_eval"], o["bill_ratio"]), (0.56, 0.91, 1.6))
        self.assertTrue(said("one point six times as much"))
        self.assertTrue(said("ninety-one cents per five hundred queries against fifty-six"))

    def test_steps(self):
        o = V["orch"]
        self.assertEqual((o["steps_single"], o["steps_multi"], o["p_single"], o["p_multi"]), (12, 16, 0.54, 0.44))
        self.assertTrue(said("twelve becomes sixteen"))
        self.assertTrue(said("zero point five four drops to zero point four four"))

    def test_verifier(self):
        self.assertEqual(V["verifier"]["with"], 0.94)
        self.assertTrue(said("from zero point eight zero to zero point nine four"))

    def test_write_tools(self):
        self.assertEqual((T["retail_tools"], T["retail_write_tools"], T["retail_read_tools"]), (16, 7, 7))
        self.assertTrue(said("Of the store's sixteen tools, seven write"))
        policy = (C.RETAIL / "policy.md").read_text()
        self.assertIn("obtain explicit user confirmation (yes)", policy)
        self.assertIn("transfer_to_human_agents", policy)


class Section5Rag(unittest.TestCase):
    def test_banking_corpus(self):
        self.assertEqual((T["banking_documents"], T["banking_tasks"]), (698, 97))
        self.assertEqual(round(T["banking_words"], -3), 137000)
        self.assertTrue(said("six hundred and ninety-eight of them, about a hundred and thirty-seven thousand words"))

    def test_rrf(self):
        r = V["rrf"]
        self.assertEqual((r["doc_a"], r["doc_b"], r["doc_c"], r["doc_d"]),
                         (0.0164, 0.032, 0.0323, 0.0318))                   # the deck's 258 / 183 / 415 / 182
        self.assertEqual((V["rrf_order"][0], V["rrf_order"][-1]), ("doc_c", "doc_a"))
        self.assertIn("1/63 + 1/61 = 0.0323", DECK)
        self.assertTrue(said("scores zero point zero one six four"))
        self.assertTrue(said("scores zero point zero three two three, and wins"))

    def test_funnel(self):
        self.assertEqual(V["first_stage"], 50)
        self.assertIn("Retrieve $50$ candidates", DECK)
        self.assertTrue(said("keeps about fifty"))

    def test_configs_exist(self):
        for c in ("no_knowledge", "bm25", "golden_retrieval", "openai_embeddings", "alltools"):
            self.assertIn(c, T["retrieval_configs"])


class Section6Embeddings(unittest.TestCase):
    def test_rare_vs_common(self):
        self.assertEqual(T["docs_with"], {"overdraft": 34, "account": 502})
        self.assertTrue(said('"overdraft" appears in thirty-four of six hundred and ninety-eight, "account" in five hundred and two'))

    def test_cross_encoder_passes(self):
        self.assertTrue(said("six hundred and ninety-eight passes for a single question"))

    def test_batch(self):
        self.assertEqual(V["batch"], {"pairs": 64, "passes": 128, "negatives_each": 63})
        self.assertTrue(said("sixty-four pairs, each question already has sixty-three wrong documents"))
        self.assertIn(C.CITED["dpr_gain_points"], DECK)
        self.assertTrue(said("nine to nineteen points"))


class Section7Ann(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(V["banking_mb"], 2.9)
        self.assertTrue(V["banking_under_limit"])
        self.assertTrue(said("under three megabytes"))
        self.assertTrue(said("a hundred thousand vectors"))

    def test_ivf(self):
        self.assertEqual(V["ivf"], {"ops": 9000, "saving": 111})             # slide: "about a 110x saving"
        self.assertTrue(said("nine thousand distance computations instead of a million"))

    def test_pq(self):
        p = V["pq"]
        self.assertEqual((p["bytes_before"], p["bytes_after"], p["gb_before"], p["gb_after"]), (4096, 64, 4096, 64))
        self.assertEqual(p["codebook_bytes"], 2 ** 20)                        # slide: 1 MiB
        self.assertTrue(said("Four thousand ninety-six bytes become sixty-four"))
        self.assertTrue(said("sixty-four gigabytes instead of four thousand and ninety-six"))

    def test_hnsw(self):
        h = V["hnsw"]
        self.assertEqual((h["layers"], h["layer1_nodes"]), (4.98, 62500))
        self.assertEqual((h["graph_gb"], h["vectors_gb"], h["overhead_pct"]), (0.13, 4.1, 3))
        self.assertTrue(said("about five layers"))

    def test_filter(self):
        f = V["filter"]
        self.assertEqual((f["post_survive"], f["pre_banking"], f["pre_large"]), (0.5, 35, 50_000_000))
        self.assertTrue(said("half a result survives"))
        self.assertTrue(said("about thirty-five vectors"))
        self.assertTrue(said("fifty million"))


class Section8Evaluation(unittest.TestCase):
    def test_ci(self):
        self.assertEqual(V["ci"], {"20": 17.5, "200": 5.5})
        self.assertEqual(V["ci20_interval"], [2.5, 37.5])
        self.assertTrue(said("plus or minus seventeen and a half points"))
        self.assertTrue(said("bring that to five and a half"))

    def test_demo(self):
        self.assertEqual(V["p10"], 0.599)
        self.assertTrue(said("about three times in five"))

    def test_pass_k(self):
        self.assertEqual(V["pass_k_example"], {"1": 0.75, "2": 0.5, "3": 0.25, "4": 0.0})
        src = (C.TAU2 / "src/tau2/metrics/agent_metrics.py").read_text()
        self.assertIn("math.comb(success_count, k) / math.comb(num_trials, k)", src)
        self.assertTrue(said("Pass to the one is zero point seven five. Pass to the two is zero point five. Pass to the four is zero"))

    def test_graded_by_database(self):
        doc = (C.TAU2 / "docs/evaluation.md").read_text()
        self.assertIn('The default `reward_basis` for the airline, retail, and telecom domains\n  is `["DB", "COMMUNICATE"]`', doc)


RAW = C.OUT
CODE = C.HERE / "code"


@unittest.skipUnless((RAW / "s1_agent_loop.json").exists(), "the s1/s2 runs are not captured yet")
class CapturedRuns(unittest.TestCase):
    """What the narration says about the two real runs, checked against their raw files and the code."""
    def test_s1_question_and_path(self):
        d = json.loads((RAW / "s1_agent_loop.json").read_text())
        self.assertTrue(d["question"].startswith("Order #W2611340"))
        self.assertTrue(said("order W two six one one three four zero"))
        self.assertEqual([c["tool"] for c in d["tool_calls"]], ["get_order_details", "get_product_details"])
        self.assertEqual(d["steps"], len(d["tool_calls"]))
        self.assertIn("water bottle", d["question"])

    def test_s1_step_budget(self):
        src = (CODE / "s1_agent_loop.py").read_text()
        self.assertIn("def run(question, max_steps=6)", src)
        self.assertTrue(said("six turns in ours"))

    def test_s1_vague(self):
        d = json.loads((RAW / "s1_agent_loop_vague.json").read_text())
        ids = [c["args"]["order_id"] for c in d["tool_calls"]]
        self.assertTrue(all(not i.startswith("#") for i in ids))           # "dropped the hash sign"
        self.assertEqual(d["steps"], len(ids))
        self.assertIn("order not found", d["answer"])                       # "never found the order"

    def test_s2_recovered(self):
        d = json.loads((RAW / "s2_structured.json").read_text())
        first, last = d["tries"][0], d["tries"][-1]
        self.assertIn("product", d["message"].lower())                      # the customer quoted a product number
        self.assertTrue(d["invalid_first_try"] and d["recovered"])
        self.assertIn("are not in #W2611340; its items are", first["error"])   # the error lists the real items
        self.assertIsNone(last["error"])
        src = (CODE / "s2_structured.py").read_text()
        self.assertIn('"pattern": "^#W[0-9]{7}$"', src)
        self.assertTrue(said("a hash sign, a W, seven digits"))

    def test_s2_unhelpful(self):
        d = json.loads((RAW / "s2_structured_unhelpful.json").read_text())
        self.assertFalse(d["recovered"])
        self.assertTrue(all(t["error"] for t in d["tries"]))
        self.assertTrue(said('"use item ID, not product ID"'))
        self.assertIn("use item_id, not product_id", d["tries"][0]["error"])


@unittest.skipUnless((RAW / "tau2_retail.json").exists(), "the τ²-bench runs are not captured yet")
class Tau2Runs(unittest.TestCase):
    """Every placeholder names a field that exists, and the words around the τ²-bench results are true."""
    def test_placeholders_resolve(self):
        for h in re.findall(r"\{\{agents_course/raw/(\w+\.json): (\w+)\}\}", NARR):
            d = json.loads((RAW / h[0]).read_text())
            self.assertIn(h[1], d, h)

    def test_retail_run(self):
        d = json.loads((RAW / "tau2_retail.json").read_text())
        self.assertIn("deepseek", d["agent_llm"])
        self.assertIn("deepseek", d["user_llm"])                            # "DeepSeek playing both"
        self.assertIn("not leaderboard-comparable", d["note"])             # the honest caveat
        self.assertTrue(said("these are our numbers, not leaderboard numbers"))
        self.assertEqual(len(d["pass_hat_k"]), d["n_trials"])

    def test_trajectory_and_failure(self):
        ok = json.loads((RAW / "tau2_retail_trajectory.json").read_text())
        self.assertEqual(ok["reward"], 1.0)
        bad = json.loads((RAW / "tau2_retail_failure.json").read_text())
        self.assertNotEqual(bad["reward"], 1.0)
        self.assertIn("why", bad)

    def test_banking_run(self):
        d = json.loads((RAW / "tau2_banking.json").read_text())
        self.assertEqual(d["retrieval_config"], "bm25")
        self.assertEqual(d["kb_documents"], T["banking_documents"])
        self.assertTrue(said("We ran the offline BM25 config"))


class Snippets(unittest.TestCase):
    """The idea snippets the narration describes say what the narration says they say."""
    def test_files(self):
        for f in ("s3_memory", "s4_orchestrator", "s5_rag_hybrid", "s6_vector_index", "s7_eval_harness",
                  "s8_injection_defence"):
            self.assertIn("IDEA SNIPPET, not run", (CODE / f"{f}.py").read_text(), f)

    def test_described_details(self):
        self.assertIn("keep ids and decisions", (CODE / "s3_memory.py").read_text())
        self.assertIn("max_retries=2", (CODE / "s4_orchestrator.py").read_text())
        self.assertTrue(said("after two rejected retries, a human decides"))
        rag = (CODE / "s5_rag_hybrid.py").read_text()
        for bit in ("bm25.search(question, 50)", "top=5", "def rrf(rankings, k=60)", "cite their [ids]"):
            self.assertIn(bit, rag)
        self.assertTrue(said("take fifty candidates from each search"))
        self.assertIn("ef_search=64", (CODE / "s6_vector_index.py").read_text())
        self.assertIn("final_db == t.expected_db", (CODE / "s7_eval_harness.py").read_text())
        guard = (CODE / "s8_injection_defence.py").read_text()
        self.assertIn("refused: acts on another user", guard)
        self.assertIn("refused: user did not confirm", guard)


class Testbed(unittest.TestCase):
    def test_retail_counts(self):
        self.assertEqual((T["retail_tasks_base"], T["retail_products"], T["retail_users"], T["retail_orders"]),
                         (114, 50, 500, 1000))
        self.assertTrue(said("sixteen tools, five hundred customers and a thousand orders"))


class Integrity(unittest.TestCase):
    def test_saved_json_is_fresh(self):
        saved = json.loads((C.OUT / "deck_numbers.json").read_text())
        self.assertEqual(saved, json.loads(json.dumps(V)))

    def test_live_numbers_are_placeholders(self):
        holes = [h for h in re.findall(r"\{\{([^}]*)\}\}", NARR) if h != "placeholders"]
        self.assertEqual(len(holes), 17)                                    # listed in the draft's report
        for h in holes:
            self.assertRegex(h, r"^agents_course/raw/(s1_agent_loop|s1_agent_loop_vague|s2_structured"
                                r"|s2_structured_unhelpful|tau2_retail|tau2_retail_trajectory|tau2_retail_failure"
                                r"|tau2_banking)\.json: \w+$")

    def test_two_pauses(self):
        self.assertEqual(len(re.findall(r"^\s*\d+\.\s+⏸", NARR, re.M)), 2)

    def test_no_legal_corpus_left(self):
        for gone in ("7,368", "seven thousand three hundred", "Article", "Magesh", "under eighteen"):
            self.assertNotIn(gone, SPOKEN)

    def test_shown_snippets_are_marked(self):
        shown = re.findall(r"`s\d_\w+\.py` \(shown, not run\)", NARR)
        self.assertGreaterEqual(len(shown), 7)


if __name__ == "__main__":
    unittest.main()
