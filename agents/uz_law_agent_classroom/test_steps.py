"""Acceptance criteria for Lectures 2-8, as skipped stubs. They document what to build (see STEPS.md) and contain no
solution. When you build a step, replace its stubs with real tests: recompute the number or behaviour from the raw
inputs and assert it, as test_agent.py does.
"""
import unittest


class Lecture2Schemas(unittest.TestCase):
    """Lecture 2: Tool schemas and structured output."""

    @unittest.skip("Lecture 2: Every tool has a JSON schema with typed arguments.")
    def test_every_tool_has_a_json_schema(self):
        pass

    @unittest.skip("Lecture 2: A call with a missing or wrongly typed argument returns an error observation and does not raise.")
    def test_a_malformed_call_is_an_error_observation(self):
        pass

    @unittest.skip("Lecture 2: The final answer is {answer, citations} and every citation is an existing article id.")
    def test_the_answer_is_structured_with_real_citations(self):
        pass

    @unittest.skip("Lecture 2: The regex parser for 'Action:' is removed.")
    def test_the_action_regex_is_gone(self):
        pass


class Lecture3Memory(unittest.TestCase):
    """Lecture 3: Memory."""

    @unittest.skip("Lecture 3: A follow-up question makes fewer tool calls than the same question asked fresh.")
    def test_a_follow_up_reuses_what_was_fetched(self):
        pass

    @unittest.skip("Lecture 3: Memory has a configurable limit and the oldest items go first.")
    def test_memory_is_bounded_and_drops_the_oldest(self):
        pass

    @unittest.skip("Lecture 3: Memory can be saved to and loaded from a file.")
    def test_memory_can_be_saved_and_loaded(self):
        pass


class Lecture4Verifier(unittest.TestCase):
    """Lecture 4: Verifier subagent."""

    @unittest.skip("Lecture 4: For each citation the verifier gets the article text and the claim and returns supported or unsupported.")
    def test_the_verifier_sees_each_cited_article(self):
        pass

    @unittest.skip("Lecture 4: An answer with an unsupported citation is revised or flagged.")
    def test_an_unsupported_citation_is_never_returned_as_is(self):
        pass

    @unittest.skip("Lecture 4: A scripted model gives a wrong citation and the verifier catches it.")
    def test_a_wrong_citation_is_caught(self):
        pass


class Lecture5Chunking(unittest.TestCase):
    """Lecture 5: Chunking."""

    @unittest.skip("Lecture 5: Concatenating the chunks of an article gives back its text.")
    def test_chunks_join_back_to_the_article(self):
        pass

    @unittest.skip("Lecture 5: Every chunk is at most the maximum size and carries article_id and chunk_index.")
    def test_chunks_are_bounded_and_labelled(self):
        pass

    @unittest.skip("Lecture 5: No chunk is empty.")
    def test_no_chunk_is_empty(self):
        pass

    @unittest.skip("Lecture 5: Search results can point to a chunk, not only to an article.")
    def test_search_results_can_point_to_a_chunk(self):
        pass


class Lecture6Retrieval(unittest.TestCase):
    """Lecture 6: BM25 and embeddings."""

    @unittest.skip("Lecture 6: search keeps its interface.")
    def test_search_keeps_its_interface(self):
        pass

    @unittest.skip("Lecture 6: On at least 10 labelled questions the correct article is in the top 5 more often than with the Lecture 1 search; both rates are printed.")
    def test_better_top5_than_word_count_on_labelled_questions(self):
        pass

    @unittest.skip("Lecture 6: Keyboard apostrophes and the corpus's apostrophes still match.")
    def test_apostrophes_still_match(self):
        pass


class Lecture7ANN(unittest.TestCase):
    """Lecture 7: ANN index."""

    @unittest.skip("Lecture 7: For 20 test queries the index returns at least 90 % of an exact search's top 10.")
    def test_recall_at_10_is_at_least_90_percent(self):
        pass

    @unittest.skip("Lecture 7: Building the index is separate from querying it.")
    def test_building_is_separate_from_querying(self):
        pass

    @unittest.skip("Lecture 7: The index can be saved and reloaded.")
    def test_the_index_can_be_saved_and_reloaded(self):
        pass


class Lecture8Evaluation(unittest.TestCase):
    """Lecture 8: Evaluation harness and injection test."""

    @unittest.skip("Lecture 8: evaluate.py prints, per question and in total: answer correct, citation correct, steps used.")
    def test_evaluate_prints_per_question_and_total(self):
        pass

    @unittest.skip("Lecture 8: A planted instruction inside an article does not change the answer or trigger an unrequested tool call.")
    def test_a_planted_instruction_changes_nothing(self):
        pass

    @unittest.skip("Lecture 8: Results are reproducible offline from recorded runs.")
    def test_results_reproduce_offline(self):
        pass


class OptionalUKPort(unittest.TestCase):
    """Optional: port the agent to the UK example corpus (see STEPS.md)."""

    @unittest.skip("Optional: the agent runs over corpus_uk with its own prompt and citations, and the Uzbek agent is unchanged.")
    def test_the_agent_runs_over_the_uk_corpus(self):
        pass

    @unittest.skip("Optional: the maximum weekly working time is answered citing WTR 4 and the 48-hour average read from the file.")
    def test_the_weekly_limit_cites_wtr_4(self):
        pass

    @unittest.skip("Optional: the minimum wage question is answered 'the corpus states no amount', citing NMWA 1.")
    def test_the_minimum_wage_answer_states_no_amount(self):
        pass

    @unittest.skip("Optional: at least two runs are recorded and replay offline with every quoted fact asserted.")
    def test_recorded_runs_replay_offline(self):
        pass


class OptionalAddALaw(unittest.TestCase):
    """Optional: add another Uzbek law as a corpus (see STEPS.md and docs/ADDING_A_LAW.md)."""

    @unittest.skip("Optional: the new law's data file is pinned by a sha256 stated in its SOURCE_<name>.md, with URL, date and licence.")
    def test_the_new_law_is_pinned_and_sourced(self):
        pass

    @unittest.skip("Optional: the data file has unique ids, non-empty text, and the record count the test recomputes.")
    def test_the_new_corpus_loads_with_unique_ids(self):
        pass

    @unittest.skip("Optional: search and fetch_article work on the new corpus; a missing id returns None.")
    def test_search_and_fetch_work_on_the_new_corpus(self):
        pass

    @unittest.skip("Optional: the agent runs over the new corpus and a recorded run replays offline; the Labor Code agent is unchanged.")
    def test_the_agent_runs_over_the_new_corpus(self):
        pass


if __name__ == "__main__":
    unittest.main()
