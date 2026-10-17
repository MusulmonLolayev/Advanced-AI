# Lecture 1 in class: the agent loop (about 30 minutes)

Slides: `agents/lectures/lecture01_what_is_an_agent.tex`, the worked trace and the four "Build it in class" frames
before the summary. Everything below runs from `agents/class_agent/`. Each command has a recorded run
(`--replay NAME`, no network, the same output every time); drop `--replay` and pass the question to run it live.

## Before class

```bash
cd agents/class_agent
uv sync                                    # Python 3.11+, one dependency (openai)
echo "DEEPSEEK_API_KEY=..." > .env         # only for live runs; .env is git-ignored
uv run python -m unittest test_class_agent        # 14 tests, no network
```

Print or put on screen the Uzbek text of Articles 182, 183, 415, 245, 153 and 209
(`uv run python -c "from corpus import fetch_article; print(fetch_article('415'))"`). The students check citations against
them in step 1.

## 1. Ask without tools (5 min)

```bash
uv run python agent.py --replay q2_under18_notools
uv run python agent.py --replay q3_min_wage_notools
uv run python agent.py --replay q3_min_wage_notools2
```

The students open each cited article and say whether it supports the claim.

- Under-18 question: the hours are right (36 and 24), but they are cited to Art. 183, which only lists who gets
  shorter hours. The limits are in Art. 415.
- Minimum wage: 1,155,000 soʻm citing Art. 153 (suspension from work); asked again, 1,270,000 soʻm citing Art. 209
  (no work on days off). The code states no amount at all: Art. 245 says the President sets it.

**Point:** a fluent answer with a citation is not a grounded answer. This is why the agent has to *read*.

## 2. Predict, then run (10 min)

```bash
uv run python agent.py --replay q1_week
uv run python agent.py --replay q2_under18
```

Pause after each step and ask: *what will the next Thought and Action be?* Write the guesses on the board.

- Q1 takes 3 steps: search → `fetch_article[182]` → answer. Its first Thought says "likely Article 182" before any
  search: the model remembers the code from training. Ask: why does it still search? (It must cite what it read,
  not what it remembers.)
- Q2 takes 4 steps: search → 182 → 415 → answer. Nobody told it to fetch 415; the search listed it and the Thought
  decided. This is the slide's worked trace.

## 3. The budget (5 min)

```bash
uv run python agent.py --replay q3_min_wage           # 7 steps; the answer: the code states no amount [Art. 245]
uv run python agent.py --replay q3_min_wage_steps3    # the same question with --max-steps 3: no answer at all
```

Discuss: what should the agent return when the budget runs out? Draft the sentence together ("Not found within
3 steps; the last article read was 245").

## 4. Read the loop (5 min)

Open `agent.py`, function `run`: the step budget, the stop at `Observation:`, the three failure replies (unreadable
turn, unknown action, missing article). Each one is an observation, not an exception.

About the stop sequence: Yao et al. cut generation at "Observation:" so the model cannot write the tool's result
itself. In our runs DeepSeek did not try, even with the cut removed (`--replay q1_week_nostop` takes the same three
steps as `q1_week`). In one unrecorded try with the instruction "never write an Observation" also removed, its first
turn still ended after the Action line. Keep the cut anyway: the loop must not depend on the model behaving.

## 5. In pairs: the duplicate-action fix (5 min, or homework)

The "three ways the loop breaks" slide fixes infinite loops with "refuse duplicate actions". Add it to `run`: keep a
set of the actions already taken, and when one repeats, make the observation `already tried: <action>` instead of
running it. Test with the scripted model in `test_class_agent.py` (copy `test_the_step_limit_stops_...`: three
identical searches must give one real observation and two "already tried").

## The recorded runs

Eight runs, 23 model calls on `deepseek-flash`, recorded 2026-10-17 with temperature 0. The model still varies
between runs (the two minimum-wage answers without tools differ), so a live run in class may take a different path
from the recording; that is worth showing, not hiding.
