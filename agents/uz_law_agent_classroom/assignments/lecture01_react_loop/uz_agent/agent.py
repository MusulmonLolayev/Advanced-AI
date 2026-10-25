"""Lecture 1: a ReAct loop over the Labor Code of Uzbekistan.

The model writes a Thought and one Action as plain text; our code reads the Action, runs the tool, and appends the
result as an Observation. Then the model reads the whole trace again and writes the next Thought. The loop ends when
the model calls answer[...] or when the step budget is used up.

You fill four functions below (Q1-Q4 in the README). Everything else is given.

    python -m uz_agent.agent --replay q2_under18        # a recorded run, no key and no network needed
    python -m uz_agent.agent "your question"            # live; needs LLM_API_KEY in .env
"""
import argparse
import json
import re
import sys

from uz_agent import config, corpus
from uz_agent.llm import Model

STOP = ["Observation:"]          # the model is cut off here, so only our code can write an observation


def show_turn(show, step, text, obs):
    """GIVEN: print one turn (long observations are shortened on the screen, never in the trace)."""
    shown = "" if obs is None else f"\nObservation: {obs if len(obs) < 400 else obs[:400] + ' …'}"
    show(f"\n── step {step}\n{text}{shown}")


def show_stop(show, max_steps):
    """GIVEN: say that the budget ran out."""
    show(f"\n── stopped: {max_steps} steps without an answer")


def parse_action(text):
    """Read the model's turn: return (name, argument) of its Action line, or None."""
    ##########################################################################
    # TODO:                                                                  #
    # Input: `text`, one turn of the model, e.g. a "Thought: ..." line and   #
    # an "Action: name[argument]" line.                                      #
    # Output: the pair (name, argument) of two strings, the argument without #
    # leading or trailing whitespace; None if the turn has no readable       #
    # action line.                                                           #
    #                                                                        #
    # Required behaviour:                                                    #
    # - an answer may span several lines and may itself contain square       #
    #   brackets (a citation such as [Art. 182]); its argument must come     #
    #   back whole;                                                          #
    # - text that merely mentions the word "Action" somewhere in a sentence  #
    #   is not an action.                                                    #
    #                                                                        #
    # Hints: this is a pattern-matching job for the re module (already       #
    # imported); think about which flags change what ^, $ and . match.       #
    ##########################################################################
    # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
    raise NotImplementedError("TODO: parse_action")
    # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****


def act(name, argument):
    """Run one tool; the returned text is what the model will see after "Observation:"."""
    ##########################################################################
    # TODO:                                                                  #
    # Input: the action's name and argument (both strings).                  #
    # Output: one string, the observation.                                   #
    # - "search": the hits of corpus.search for the argument, one per line,  #
    #   each line the article's citation (corpus.CITE) and its title, as the #
    #   model should read them; corpus.NOT_FOUND when nothing matches.       #
    # - corpus.FETCH: the article's text; corpus.MISSING (with the requested #
    #   id) when the sample has no such article.                             #
    # - any other name: corpus.UNKNOWN (with the name).                      #
    #                                                                        #
    # Hints: look at what corpus.search returns and which parts of it the    #
    # model should see. A recorded run replays only if your observations     #
    # are character for character the recorded ones, so use the corpus      #
    # constants rather than writing the wording yourself.                    #
    # Pitfall: the model is allowed to be wrong. A bad action is answered    #
    # with an observation, never with an exception.                          #
    ##########################################################################
    # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
    raise NotImplementedError("TODO: act")
    # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****


def observe(text):
    """Decide what one model turn means: return (answer, observation)."""
    ##########################################################################
    # TODO:                                                                  #
    # Input: one model turn. Output: a pair (answer, observation), exactly   #
    # one of the two being None.                                             #
    # - the turn holds no readable action: the correction corpus.UNREADABLE  #
    #   is the observation, so the model can fix its format next turn        #
    #   instead of the program stopping;                                     #
    # - the action is "answer": the answer is its argument, there is no      #
    #   observation;                                                         #
    # - any other action: its observation.                                   #
    #                                                                        #
    # Hints: build on parse_action and act above.                            #
    # Pitfall: an empty answer, answer[], is still a finished answer.        #
    ##########################################################################
    # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
    raise NotImplementedError("TODO: observe")
    # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****


def run(question, model, max_steps=config.MAX_STEPS, stop=True, show=print):
    """The ReAct loop. Returns (answer or None, the trace as a list of turns).

    A turn in the trace is {"step": n counted from 1, "model": the model's text, "observation": text or None}.
    """
    messages = [{"role": "system", "content": corpus.SYSTEM}, {"role": "user", "content": question}]
    trace = []
    ##########################################################################
    # TODO:                                                                  #
    # Let the model and the tools take turns until the model answers or      #
    # max_steps turns have been used. Return (answer, trace); the answer is  #
    # None if the budget ran out first.                                      #
    #                                                                        #
    # Required behaviour:                                                    #
    # - the model is called as model.complete(messages, stop=...); pass the  #
    #   list STOP when the argument `stop` is true, else None. Its reply is  #
    #   stripped of surrounding whitespace and kept in `messages` as an      #
    #   "assistant" message;                                                 #
    # - what the tools return goes back to the model as a "user" message     #
    #   that reads "Observation: " followed by the observation. The model    #
    #   sees the whole `messages` list on every call; that is its memory;    #
    # - every turn, also the last one, is added to `trace` as a dict with    #
    #   the keys "step", "model", "observation" (see above) and shown with   #
    #   the given helper show_turn;                                          #
    # - when the budget runs out, report it with the given helper show_stop #
    #   before returning.                                                    #
    #                                                                        #
    # Hints: use observe(). `messages` and `trace` exist already.            #
    # Pitfall: the budget is what stops a model that never answers; the      #
    # checks try it with a model that only searches.                         #
    ##########################################################################
    # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
    raise NotImplementedError("TODO: run")
    # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****


def main():
    """GIVEN: the command line. Replaying a run reads its question and settings from the recording."""
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--record", metavar="NAME", help="run live and save the run to traces/NAME.json")
    ap.add_argument("--replay", metavar="NAME", help="play back traces/NAME.json (no key, no network)")
    ap.add_argument("--no-stop", action="store_true", help="do not cut the model off at \"Observation:\"")
    ap.add_argument("--max-steps", type=int, default=config.MAX_STEPS)
    a = ap.parse_args()
    question, max_steps, stop = a.question or corpus.QUESTIONS.get(a.record or a.replay), a.max_steps, not a.no_stop
    if a.replay:
        saved = json.loads((config.TRACES / f"{a.replay}.json").read_text())
        question, max_steps, stop = saved["question"], saved["max_steps"], saved["stop"]
    if not question:
        sys.exit("give a question, or --replay one of: " + ", ".join(sorted(p.stem for p in config.TRACES.glob("*.json"))))
    model = Model("replay" if a.replay else "record" if a.record else "live", a.record or a.replay)
    print(f"Q: {question}")
    answer, trace = run(question, model, max_steps=max_steps, stop=stop)
    print(f"\nANSWER: {answer}")
    model.save({"question": question, "max_steps": max_steps, "stop": stop, "no_tools": False,
                "answer": answer, "trace": trace})


if __name__ == "__main__":
    main()
