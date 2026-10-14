"""Every number the video takes from the testbed and the two runnable examples, recomputed from the saved files.
    cd video/agents_course && python3 -m unittest test_tau2
"""
import json
import unittest
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
SIMS = HERE / "tau2-bench/data/simulations"
DB = HERE / "tau2-bench/data/tau2/domains/retail/db.json"


def raw(name):
    return json.loads((RAW / name).read_text())


def results(run):
    return json.loads((SIMS / run / "results.json").read_text())["simulations"]


class Testbed(unittest.TestCase):
    def test_retail_tools_and_db(self):
        t = raw("tau2_retail_tools.json")
        self.assertEqual(t["tau2_tag"], "v1.0.1")
        self.assertEqual(t["n_tools"], len(t["tools"]))
        self.assertEqual(t["n_tools"], 16)
        kinds = [x["type"] for x in t["tools"]]
        self.assertEqual((kinds.count("READ"), kinds.count("WRITE"), kinds.count("GENERIC")), (7, 7, 2))
        db = json.loads(DB.read_text())
        self.assertEqual((len(db["users"]), len(db["orders"]), len(db["products"])), (500, 1000, 50))

    def check_summary(self, name, run):
        s, sims = raw(name), results(run)
        by_task = {}
        for x in sims:
            by_task.setdefault(x["task_id"], []).append(int(x["reward_info"]["reward"] == 1.0))
        self.assertEqual(s["rewards_by_task"], by_task)
        self.assertEqual(s["n_simulations"], len(sims))
        self.assertAlmostEqual(s["pass_1"], sum(map(sum, by_task.values())) / len(sims), places=4)
        for k, v in s["pass_hat_k"].items():
            k = int(k)
            exp = sum(comb(sum(r), k) / comb(len(r), k) for r in by_task.values()) / len(by_task)
            self.assertAlmostEqual(v, exp, places=4)
        self.assertAlmostEqual(s["cost_usd"], sum(x["agent_cost"] + x["user_cost"] for x in sims), places=4)
        return s

    def test_retail_scores(self):
        s = self.check_summary("tau2_retail.json", "retail10x3")
        self.assertEqual((s["n_tasks"], s["n_trials"]), (10, 3))
        ks = [s["pass_hat_k"][str(k)] for k in (1, 2, 3)]
        self.assertTrue(ks[0] >= ks[1] >= ks[2])                 # reliability can only fall as k grows

    def test_banking_scores(self):
        s = self.check_summary("tau2_banking.json", "banking5_bm25")
        self.assertEqual(s["retrieval_config"], "bm25")
        self.assertGreater(s["kb_searches"], 0)

    def test_trajectories(self):
        t = raw("tau2_retail_trajectory.json")
        self.assertEqual(t["reward"], 1.0)
        self.assertEqual(t["tool_calls"], sum(len(m.get("tool_calls", [])) for m in t["messages"]))
        f = raw("tau2_retail_failure.json")
        self.assertLess(f["reward"], 1.0)
        self.assertTrue(f["why"]["db_match"] is False or f["why"]["expected_actions_not_taken"]
                        or f["why"]["nl_assertions_failed"])


class Examples(unittest.TestCase):
    def test_s1_loop(self):
        good, vague = raw("s1_agent_loop.json"), raw("s1_agent_loop_vague.json")
        self.assertEqual(good["steps"], len(good["tool_calls"]))
        self.assertEqual(good["tool_calls"][0], {"tool": "get_order_details", "args": {"order_id": "#W2611340"}})
        self.assertTrue(all(c["args"]["order_id"] != "#W2611340" for c in vague["tool_calls"]))
        self.assertEqual(vague["steps"], 3)
        db = json.loads(DB.read_text())
        bottle = db["orders"]["#W2611340"]["items"][0]
        self.assertEqual(good["tool_calls"][1]["args"]["product_id"], bottle["product_id"])
        self.assertIn(db["orders"]["#W2611340"]["status"], good["answer"].lower())

    def test_s2_retry(self):
        good, unhelpful = raw("s2_structured.json"), raw("s2_structured_unhelpful.json")
        self.assertTrue(good["invalid_first_try"] and good["recovered"] and good["valid"])
        self.assertEqual(len(good["tries"]), 2)
        db = json.loads(DB.read_text())
        items = {i["item_id"] for i in db["orders"]["#W2611340"]["items"]}
        self.assertTrue(set(good["tries"][-1]["request"]["item_ids"]) <= items)
        self.assertFalse(unhelpful["valid"])
        self.assertEqual(len(unhelpful["tries"]), 3)


if __name__ == "__main__":
    unittest.main()
