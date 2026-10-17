# Module 7, Lecture 1 — What is an agent? — English narration (draft 2, UK law, for approval)

**The English version runs on UK law, not the Labor Code of Uzbekistan** (the instructor's decision, 2026-10-17).
The Uzbek version stays on the Labor Code (`m7_lecture01.md`, its own approval). The lecture, its sections and its
line numbers are the same in both, so the scenes are shared; a line added here carries a letter (32a, 66a, 74a).

**The agent on screen is our class agent with `--law uk`** (`agents/class_agent/corpus_uk.py`) on two UK laws on
work: the Working Time Regulations 1998 (WTR) and the National Minimum Wage Act 1998 (NMWA), the text in force in
Great Britain on 1 October 2026, 118 provisions (`data/SOURCE_UK.md`). Every run shown is a recording in
`agents/class_agent/traces/uk/`, and every fact quoted from a run or a provision is asserted in
`test_class_agent.py` (classes `UKCorpus`, `UKRecordedRuns`). Cost and reliability numbers are the lecture's own
(`video/m7/raw/l01_numbers.json`), unchanged. The narration spells numbers; the screen shows digits.

**What changed from draft 1** (lines not listed keep draft 1's English, with "article" → "provision"):
- 1, 2, 4, 11, 14, 27–45 (the real runs), 64, 66–67, 70–72: the UK laws and the UK runs.
- 32a (new): the UK run takes six steps, not four: it also reads the definition of a young worker.
- 34: the "it remembers" example is now the minimum-wage run's first thought (the UK week run has no such hint).
- 40–43: without tools the model's wage figures are *right* (the April 2026 rates, as on GOV.UK), but from memory,
  not from the laws, and asked again it gives none. The lesson becomes "memory can be right, and we still cannot
  check it", instead of draft 1's invented figure.
- 66a (new): a real failure reply: in the week run, the model's third turn came back empty.
- 74a (new): a real bad step: the minimum-wage run searched for "£", which our search cannot match, and took
  "nothing found" as proof.

**Voice:** "we", never "you"; only the pause cards address the viewer.

**Outside fact (line 41):** the April 2026 rates the model gave from memory match the government's announcement,
<https://www.gov.uk/government/news/national-living-wage-increases-to-1271-per-hour> (£12.71 at 21 and over, £10.85 at
18–20, £8.00 at 16–17 and for apprentices), checked 2026-10-17. The narration says only that they match; the
screen shows the model's own answer.

---

## Lecture opening
▸ title card "Module 7 · Lecture 1" → "What is an agent?"
0. **Hello, dear friends, and welcome to the first lecture of module seven. In this module we work with agents: programs in which a language model makes its own decisions and calls tools.**
1. **Today's question is simple: what is an agent, and how is it different from an ordinary program? We find the answer not in theory but in a real example. We build a small agent on two UK laws about work, and look at every step it takes.**
   ▸ the two titles "The Working Time Regulations 1998" and "National Minimum Wage Act 1998"; 118 provision tiles fill the screen

### Section 1 — Why do we need an agent?
2. **Let's start with one question: at most, how many hours a week may a person work? One search is enough for it. We find the right provision in the law, read it, and answer.**
   ▸ a row of boxes: question → search → answer
3. **We call such a fixed sequence a pipeline. The programmer wrote the order of the steps in advance: first search, then answer. The number of steps is known in advance too.**
4. **Now let's change the question a little: is that limit different for workers under eighteen? Now one search is not enough. We find the general rule, read it, see that it says nothing about young workers, and search again.**
5. **How many times will we search? Nobody knows in advance. The next step depends on what the previous step returned.**
6. **An agent is exactly the answer to this problem. In an agent, the model, not the programmer, chooses the next step. The model itself decides that one more search is needed, and a third one if it must.**
   ▸ the row re-forms: the arrow out of "tool" bends back into "model"
7. **Let's put the two diagrams side by side. Both have a model and a tool. The difference is one arrow: in the agent, the arrow goes back. The model decides how many times to go round the loop.**
   ▸ pipeline above, agent below; the back arrow pulses
8. **Let's pause for a minute. Take two questions: how much annual leave does a worker get? And how many hours a day and a week may a seventeen-year-old work? Which one needs one search, and which needs several?**
   ▸ pause card
9. **So an agent works inside a loop. Now let's name the parts of that loop.**

### Section 2 — Tool, action, trajectory
10. **The first concept is a tool. A tool is a function the model can ask for by name. The model knows it only from its description in text.**
11. **Our agent has three actions. Search finds provisions by words. Fetch returns the full text of one provision. Answer ends the run, and every claim in it is cited by its regulation or section number.**
    ▸ three cards: `search[…]` · `fetch[…]` · `answer[…]`
12. **All the actions available at one step are called the action space. Ours has three.**
13. **The whole sequence of thoughts, actions and observations for one task is called a trajectory. In lecture eight we grade an agent by its whole trajectory, not only by its last answer.**
14. **The most important point is this: the model never executes anything itself. It only writes a request: "fetch this provision". Our code decides whether to carry it out.**
    ▸ the model box writes a slip `fetch[WTR 4]`; a code box takes it, runs the tool, hands back the text
15. **That is why the security boundary sits exactly here, between the request and the execution. All the defences in lecture eight are built on this boundary.**
16. **Let's pause for a minute. We want to give our agent a fourth tool, a calculator. Let's write its description in one sentence. Which words tell the model when to call it?**
    ▸ pause card
17. **Now let's see how the model takes turns between thinking and acting.**

### Section 3 — ReAct
18. **There are two obvious ways to build an agent, and each fails in its own way.**
19. **The first way is thinking only. The model makes a fine plan but checks nothing. A wrong premise travels all the way to the final answer.**
    ▸ a chain of thought bubbles, the first one red, the red carried to the end
20. **The second way is acting only. The model keeps calling tools with no plan. When a result is surprising, it has nowhere to write down that the plan must change.**
21. **Yao and colleagues proposed a third way in twenty twenty-three: ReAct. The model writes in turns: a thought, an action, and the observation the tool returned. Each step is added to the trajectory.**
    ▸ the loop: Thought → Action → Observation → back to Thought; an exit to Answer
22. **The thought is exactly the place where the model can write: "that search gave nothing useful; I will narrow the query".**
23. **Every turn the model re-reads the whole text written so far and writes the next thought. Nothing else is remembered.**
24. **In Yao and colleagues' experiments, the mixed loop beat both simple ways, on question answering and on interactive tasks.**
25. **Let's stop and think: where could an act-only agent go wrong on the under-eighteen question?**
    ▸ pause card
26. **Now let's run this loop in a real agent.**

### Section 4 — A real trajectory
27. **Our agent works on two laws: the Working Time Regulations of nineteen ninety-eight, and the National Minimum Wage Act of the same year, as they stand in Great Britain today. Together, one hundred and eighteen provisions. At the start the agent has seen none of them. It reads only by acting.**
    ▸ the two titles, "118 provisions"; "a real recorded run"
28. **Our question: what is the maximum weekly working time, and does it differ for workers under eighteen?**
29. **Step one. Thought: I need the provisions on maximum weekly working time, and the special rules for young workers. Action: search, "maximum weekly working time". Observation: regulation four, maximum weekly working time; and regulation five A, maximum working time for young workers, is on the list too.**
    ▸ the trace builds line by line from `traces/uk/q2_under18.json`; the search result list appears, WTR 4 and WTR 5A lit
30. **Step two. The model fetches regulation four. It says: a worker's working time, including overtime, shall not exceed an average of forty-eight hours for each seven days, unless the worker has agreed in writing. The average is taken over seventeen weeks.**
    ▸ the provision's text, «an average of 48 hours for each seven days» highlighted
31. **Step three. Thought: now I need the young workers' provision, to see whether it differs. The model fetches regulation five A: a young worker's working time shall not exceed eight hours a day, or forty hours a week.**
32. **Steps four and five. Thought: I should confirm who counts as a young worker. The model searches for "young worker", then fetches regulation two, the definitions: a young worker has reached fifteen, but not eighteen, and is over school age.**
    ▸ steps 4–5 in the left column: `search[young worker]`, `fetch[WTR 2]`; the definition, «attained the age of 15 but not the age of 18» highlighted
32a. **Step six, the answer: an average of forty-eight hours a week over seventeen weeks, regulation four; under eighteen, eight hours a day and forty a week, regulation five A; and who counts as under eighteen, regulation two.**
33. **Notice: nobody told it to read the definitions. The search for "young worker" did not even list regulation two. Its thought says the meaning is likely in the interpretation provision, the part where a law defines its words: the model knew how laws are built, and decided itself to check. That is exactly the difference from a pipeline.**
    ▸ the left column's step 5 lit; the search list of step 4 beside it, with no WTR 2 in it
34. **There is one more interesting thing. On our minimum-wage question, the model's very first thought, before it had read anything, was: I need to see whether the Act specifies an hourly rate, or delegates it to regulations. The model remembers this law from its training. So why does it still read? Because it must cite what it read, not what it remembers.**
    ▸ `traces/uk/q3_min_wage.json`, the first Thought, «or delegates it to regulations» underlined
35. **Let's stop and guess in advance: how many hours a day may a seventeen-year-old work, and which provisions must the agent read to say so?**
    ▸ pause card
36. **The agent answered correctly. And without tools? That is what we check in the next section.**

### Section 5 — An answer without tools
37. **Now we give the same model the same question, but with no tools. No loop, no search: we ask once, like an ordinary chatbot.**
38. **The answer sounds sure: forty-eight hours on average, over seventeen weeks, and forty hours a week for young workers. The numbers are right. But look at where it says the seventeen weeks come from: regulation four, paragraph two.**
    ▸ `traces/uk/q2_under18_notools.json`, the citation [WTR 4(2)] boxed
39. **We open regulation four. Paragraph two is the employer's duty to keep to the limit and to keep records; the seventeen weeks are in paragraph three. The written agreement is cited to regulation five, paragraph one, and that paragraph has been repealed: only dots are left. And the limit of eight hours a day is missing altogether.**
    ▸ each citation opened to its real paragraph: 4(2) the employer's duty, 5(1) ". . .", 5A(1)(a) "eight hours a day" with nothing pointing to it
40. **The second question is even more interesting: what is the national minimum wage per hour, in pounds? Without tools, the model says the Act itself sets no figure, and then lists the rates from April twenty twenty-six: twelve pounds seventy-one an hour from the age of twenty-one, and lower rates for younger workers.**
    ▸ `traces/uk/q3_min_wage_notools.json`: the rates list, "NMW Regulations 2015" boxed
41. **These figures are in fact right: they match the rates the government published. But nothing we gave the model contains them. They come from memory, so we cannot check them against its sources, and next April they change while the memory does not. We asked the same question once more: this time no figure at all, and section two cited for rules that are in sections one and three.**
    ▸ the two answers side by side; the second one's [NMWA 2(1)] and [NMWA 2(2)] opened to their real text
42. **The Act contains no amount at all. Section one says the national minimum wage shall be such single hourly rate as the Secretary of State may from time to time prescribe. Our agent reached exactly this answer in four steps: the Act states no amount; the minister sets it by regulations.**
    ▸ NMWA 1(3), «such single hourly rate as the Secretary of State may from time to time prescribe» highlighted
43. **So a fluent, confident answer, even one with a citation, even one that happens to be right, is not a grounded answer. A grounded answer is one we can check against what the agent read. An agent has to read, not remember.**
44. **Let's stop for an exercise: next to each claim in the answer without tools, we write "in the law" or "not in the law". Which ones could not be checked?**
    ▸ pause card
45. **An agent reads, and reading is not free. In the next section we work out the cost.**

### Section 6 — The scratchpad and the bill
46. **An agent's scratchpad is not stored anywhere special. Every thought, action and observation is joined together and sent to the model again, whole, on the next turn. The scratchpad is the context window itself.**
47. **Let's count. The system prompt and the tool descriptions are a fixed part, say twelve hundred tokens. Each step adds another five hundred.**
    ▸ a prompt bar: a fixed block (S = 1200), then one 500-token block per step
48. **The first turn sends twelve hundred tokens. The second, seventeen hundred. The third, twenty-two hundred. Each turn is longer than the one before.**
49. **For three steps we pay for five thousand one hundred tokens in all. For ten steps, thirty-four thousand five hundred. For twenty steps, one hundred and nineteen thousand.**
    ▸ bars for 3 / 10 / 20 steps, split into the fixed part and the re-read part
50. **We doubled the steps, from ten to twenty. The bill grew not two times but three point four times. The reason: every step is re-read by every step after it, and that part grows like the square of the number of steps.**
    ▸ the formula n·S + a·n(n−1)/2, the second term lit
51. **If we paid only for the new text, twenty steps would be just eleven thousand two hundred tokens.**
    ▸ beside each bar, a thin bar for the new text only: 2,700 / 6,200 / 11,200
52. **Let's stop and count: how many tokens in all do we pay for in a five-step trajectory?**
    ▸ pause card
53. **There is a way to bring this bill down. We see it in the next section.**

### Section 7 — The cache
54. **To write each new token, the model computes over every token before it. But that computation depends only on the earlier text. A server can do it once and keep it. We call this a cache.**
55. **An agent loop is the ideal case for a cache: each turn begins with exactly the previous turn's text. Only the tokens added last are new.**
    ▸ the turn-2 bar slides under the turn-1 bar: the shared prefix turns grey ("cached")
56. **For our model a cached token is fifty times cheaper: a million ordinary tokens cost fifteen cents, cached ones three tenths of a cent.**
57. **In a ten-step trajectory, five thousand seven hundred tokens are new and twenty-eight thousand eight hundred come from the cache. One run becomes five and a half times cheaper.**
58. **Across a five-hundred-question evaluation, that means forty-seven cents instead of two dollars fifty-nine.**
59. **But the cache works on one condition: the beginning of the text must not change. If we put the time or date into the system prompt, or swap the order of the tools, the cache is lost from that point on.**
60. **Let's stop and think: what happens if we put today's date at the start of our agent's system prompt?**
    ▸ pause card
61. **Now from the bill back to the tools themselves: how do we choose them?**

### Section 8 — Designing the action space
62. **The action space is the model's only vocabulary. Sizing it wrong hurts in both directions.**
63. **Too large: search, look up, find provision, query corpus, four near-identical tools. The model is forced to guess which one we meant.**
64. **Too coarse: with a single search tool, the model cannot say "search only the Working Time Regulations". It stuffs extra words into the query and hopes.**
65. **The rule is: every tool should be describable in one sentence, and no two tools should ever both fit the same need.**
66. **And every tool needs a failure reply. In our agent, "there is no such provision" or "unknown action" does not stop the program. It goes back to the model as an observation, and the model picks the next step.**
    ▸ `fetch[WTR 99]` → Observation: there is no provision WTR 99; `calculator[36/5]` → unknown action
66a. **This happened in one of our real runs. On the weekly-hours question, the model's third turn came back empty. Our code answered: "I could not read an action". On the next turn the model carried on, fetched regulation five A, and answered.**
    ▸ `traces/uk/q1_week.json`: step 3, an empty turn and the correction under it; step 4 `fetch[WTR 5A]`
67. **Let's pause: which of our three actions would gain from one more argument? For example, which of the two laws to search?**
    ▸ pause card
68. **Even with failure replies, the loop can still break. How, we see in the next section.**

### Section 9 — How the loop breaks
69. **The loop breaks in three ways. The first is an endless loop. The model repeats the same action again and again, because the observation changed nothing in its thinking.**
70. **The cure is a step limit. Ours is eight steps. The minimum-wage question took four: a search, section one of the Act, one more search, and the answer.**
    ▸ `traces/uk/q3_min_wage.json` as four step tiles under an 8-step ruler
71. **What if we lower the limit to three steps? In that run the agent searched, read section one, searched again for "pounds per hour", and stopped. No answer at all. The loop ended safely, but the user learned nothing.**
    ▸ `traces/uk/q3_min_wage_steps3.json`: three tiles, then a wall
72. **So when it hits the limit, the agent should not go silent but say honestly: not found within the limit; the last provision read was section one of the Act. A guess is not honest.**
73. **The second way is calling a tool that does not exist, or giving it a wrong argument. The cure is to hand the error back as an observation, and in the next lecture, to make a wrong call impossible altogether.**
74. **The third way is compounding errors. Every step rests on all the steps before it, so one bad observation spoils everything after it. There is no cure for this, only arithmetic.**
74a. **Our own minimum-wage run shows a bad step slipping through. At step three, the model searched for the pound sign. Our search reads only words, so it could never find anything, and the model took "no provision contains these words" as proof that the Act states no figure. The conclusion was true this time: a test checks every provision. But that step proved nothing.**
    ▸ `traces/uk/q3_min_wage.json` step 3: `search[£]` → "no provision contains these words"; the next Thought, «No monetary figure appears anywhere» underlined
75. **Let's stop and think: if the model writes the same search a second time, what observation should our code give back?**
    ▸ pause card
76. **Now let's turn to the arithmetic.**

### Section 10 — Errors compound
77. **Let's recall lecture two of module zero: the probability that independent events all happen is the product of their probabilities.**
78. **Suppose each step of an agent is right with the same probability. Then the chance that all ten steps are right is that probability multiplied by itself ten times.**
    ▸ p · p · … · p = pᵏ, the ten factors drawn as tiles
79. **Each step is right ninety-five times in a hundred. That is excellent. But after ten steps the whole trajectory is right with probability about zero point five nine nine, roughly six times in ten.**
    ▸ the curve pᵏ for p = 0.95 and p = 0.90, k from 1 to 20; k = 10 marked
80. **In reality it is even worse, because the steps depend on each other: one bad search makes the next thought worse too.**
81. **An important lesson follows: shortening the trajectory is often worth more than improving the model. At ninety in a hundred per step, ten steps give zero point three five, and five steps give zero point five nine.**
82. **There are three levers, usually paying off in this order: fewer steps, better steps, and noticing a failure and trying again.**
83. **Let's stop and count: if each step is right ninety-nine times in a hundred, how reliable is a twenty-step trajectory?**
    ▸ pause card
84. **That is exactly why, in lecture eight, we grade the whole trajectory and not only the last answer.**

## Closing
85. **With this we finish our first lecture. An agent is a program in which the model chooses the next step; the arrow that goes back is its only new idea. ReAct takes turns between thought, action and observation. The scratchpad is the context window, so a long trajectory is expensive. And reliability multiplies.**
86. **In the next lecture we see exactly how a model calls a tool: tool schemas, structured outputs, and ways to make a wrong call impossible. See you!**
    ▸ closing card "Lecture 2 · Calling tools"
