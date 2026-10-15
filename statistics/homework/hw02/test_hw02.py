"""Unit tests for Homework 2's numbers: each answer recomputed independently of hw02_numbers.py.

No expected value is typed here (the tests sit in the shared repo, the answers do not). Every check recomputes from
the sheet's data another way: enumerating outcomes, building the population person by person, or a second formula.

    python3 -m unittest discover -s statistics/homework/hw02 -p 'test_hw02.py'
"""
import itertools
import json
import unittest
from fractions import Fraction as F

import hw02_numbers as H

A = H.compute()


def p(event, space):
    space = list(space)
    return F(sum(1 for s in space if event(s)), len(space))


class Conditioning(unittest.TestCase):
    def test_die_and_dice(self):
        die = range(1, 7)
        self.assertEqual(A["p_ge5_given_odd"], p(lambda d: d >= 5 and d % 2, die) / p(lambda d: d % 2, die))
        rolls = list(itertools.product(range(1, 7), repeat=2))
        both = p(lambda r: sum(r) == 8 and r[0] == 3, rolls)
        self.assertEqual(A["p_sum8_given_first3"], both / p(lambda r: r[0] == 3, rolls))
        self.assertEqual(A["p_first3_given_sum8"], both / p(lambda r: sum(r) == 8, rolls))
        self.assertNotEqual(A["p_sum8_given_first3"], A["p_first3_given_sum8"])     # the task's point
        self.assertEqual(A["p_double_given_sum8"],
                         p(lambda r: sum(r) == 8 and r[0] == r[1], rolls) / p(lambda r: sum(r) == 8, rolls))

    def test_cards(self):
        deck = list(itertools.product("A23456789TJQK", "SHDC"))
        face = lambda c: c[0] in "JQK"
        king = lambda c: c[0] == "K"
        self.assertEqual(A["p_king_given_face"], p(lambda c: king(c) and face(c), deck) / p(face, deck))
        self.assertEqual(A["p_face_given_king"], p(lambda c: king(c) and face(c), deck) / p(king, deck))


class TreesAndDraws(unittest.TestCase):
    def test_tree_paths_sum_to_one_and_count(self):
        self.assertEqual(A["tree_total"], 1)
        items = []                                                               # 1,000 items, one by one
        for m, (share, bad) in H.MACHINES.items():
            made = int(share * H.ITEMS)
            items += [(m, i < bad * made) for i in range(made)]
        self.assertEqual(len(items), H.ITEMS)
        for m in H.MACHINES:
            self.assertEqual(A[f"n_{m.lower()}_def"], sum(1 for x in items if x == (m, True)))
        defective = [x for x in items if x[1]]
        self.assertEqual(A["p_m2_given_def"], F(sum(1 for x in defective if x[0] == "M2"), len(defective)))
        self.assertEqual(A["p_def"], F(len(defective), len(items)))

    def test_bag(self):
        balls = ["R"] * H.RED + ["B"] * H.BLUE
        pairs = list(itertools.permutations(range(len(balls)), 2))               # ordered, without replacement
        self.assertEqual(A["p_rr"], p(lambda q: balls[q[0]] == balls[q[1]] == "R", pairs))
        self.assertEqual(A["p_same"], p(lambda q: balls[q[0]] == balls[q[1]], pairs))
        self.assertEqual(A["p_second_red"], p(lambda q: balls[q[1]] == "R", pairs))
        self.assertEqual(A["p_second_red"], F(H.RED, H.RED + H.BLUE))           # the symmetry the task asks about
        repl = list(itertools.product(range(len(balls)), repeat=2))
        self.assertEqual(A["p_rr_repl"], p(lambda q: balls[q[0]] == balls[q[1]] == "R", repl))


class Tables(unittest.TestCase):
    def test_contingency(self):
        for name, table in (("att", H.ATTEND), ("ses", H.SESSION)):
            people = [(g, ok) for g, (ps, fl) in table.items() for ok in [True] * ps + [False] * fl]
            self.assertEqual(A[f"{name}_p_pass"], p(lambda x: x[1], people))
            for (g, _), k in zip(table.items(), ("one", "two")):
                grp = [x for x in people if x[0] == g]
                self.assertEqual(A[f"{name}_{k}_p_pass"], p(lambda x: x[1], grp))
                expected = F(len(grp)) * sum(x[1] for x in people) / len(people)
                self.assertEqual(A[f"{name}_{k}_expected"], expected)
            cond = [p(lambda x: x[1], [x for x in people if x[0] == g]) for g in table]
            self.assertEqual(A[f"{name}_indep"], len(set(cond)) == 1)
        self.assertFalse(A["att_indep"])                                          # one table dependent
        self.assertTrue(A["ses_indep"])                                           # one exactly independent

    def test_simpson(self):
        for h, ops in H.HOSPITALS.items():
            patients = [(kind, ok) for kind, (n, s) in ops.items() for ok in [True] * s + [False] * (n - s)]
            self.assertEqual(A[f"h{h.lower()}_all"], p(lambda x: x[1], patients))
        self.assertTrue(A["b_better_each"])                                       # the paradox's premise ...
        self.assertTrue(A["a_better_pooled"])                                     # ... and its reversal


class Bayes(unittest.TestCase):
    def test_screening_counts_and_formula(self):
        ill = H.BASE * H.PEOPLE
        true_pos = H.SENS * ill
        false_pos = H.FALSE_POS * (H.PEOPLE - ill)
        bayes = H.SENS * H.BASE / (H.SENS * H.BASE + H.FALSE_POS * (1 - H.BASE))
        self.assertEqual(A["p_ill_given_pos"], true_pos / (true_pos + false_pos))
        self.assertEqual(A["p_ill_given_pos"], bayes)                            # counts = formula
        odds = A["post_odds_two"]
        self.assertEqual(A["p_ill_given_two_pos"], odds / (1 + odds))           # odds form = sequential Bayes
        self.assertLess(A["p_ill_given_pos"], F(1, 10))                          # the base-rate surprise

    def test_spam(self):
        emails = 1000                                                            # a population of emails
        spam = H.SPAM * emails
        free_spam, free_ham = H.FREE_SPAM * spam, H.FREE_HAM * (emails - spam)
        self.assertEqual(A["p_spam_given_free"], free_spam / (free_spam + free_ham))

    def test_errors_and_chain_rule(self):
        socks = ["B"] * H.SOCKS_BLACK + ["W"] * H.SOCKS_WHITE
        pairs = list(itertools.permutations(range(len(socks)), 2))
        self.assertEqual(A["err_socks_ok"], p(lambda q: socks[q[0]] == socks[q[1]] == "B", pairs))
        self.assertNotEqual(A["err_socks_wrong"], A["err_socks_ok"])
        triples = list(itertools.permutations(range(len(socks)), 3))
        self.assertEqual(A["p_three_black"], p(lambda q: all(socks[i] == "B" for i in q), triples))
        self.assertNotEqual(A["err_total_wrong"], A["err_total_ok"])            # unweighted average is off


class MontyHall(unittest.TestCase):
    def test_by_counting_equally_likely_games(self):
        games = []                                                           # 6 games: prize door x coin for the host
        for prize in (1, 2, 3):
            for coin in (0, 1):
                opened = [d for d in (2, 3) if d != prize][coin % len([d for d in (2, 3) if d != prize])]
                games.append((prize, opened))
        seen = [g for g in games if g[1] == 3]
        self.assertEqual(A["p_switch_wins"], F(sum(1 for g in seen if g[0] == 2), len(seen)))


class Files(unittest.TestCase):
    def test_sheet_data_matches_the_script(self):
        self.assertEqual((H.HERE / "hw02_data.tex").read_text(), H.data_tex(), "rerun hw02_numbers.py")

    def test_key_matches_the_script(self):
        key = H.KEYS / "hw02_answers.json"
        if key.exists():
            self.assertEqual(json.loads(key.read_text()), {k: H.jsonable(v) for k, v in A.items()})


if __name__ == "__main__":
    unittest.main()
