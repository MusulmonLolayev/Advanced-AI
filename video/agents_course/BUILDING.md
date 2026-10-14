# Building the agent course's sections

One video, `video/agents_course.py`, collects `agents_course_s00.py` … `agents_course_s09.py` (one file per section;
a missing file is skipped while sections are written in parallel). Every scene subclasses the kit's
`LectureScene`: `from agents_course_kit import *`. Model your file on `agents_course_s01.py`.

## Narration and timing
- `with self.say("2.4") as (tr, t):` voices line 2.4 of `narration/agents_course.md` (approved; never copy its
  words into Python). Live results inside a line (`{{agents_course/raw/<file>: <field>}}`) are already filled:
  `agents_course_kit.SPOKEN` holds one rule per file:field; add a rule there (and a test in
  `test_render_text.py`) if a section introduces a new placeholder.
- `self.cue(tr, t, {"en": "a phrase of the line"})` waits until that phrase is spoken. Always use the dict form:
  Korean adds a `"ko"` key later.
- `self.section_card(N)` opens a section ("Section N" + its title from the narration heading).
- A pause line (⏸): show `pause_card_math(tex)` during `self.say(key)`, then `self.hands_on()` (the 3 s gap), then
  fade the card. Only sections 1 and 8 have one. No other silence may reach 2 s.
- `self.clear_all()` between beats; `recap(self, "N.k", [label(...), ...])` voices the section's recap line with
  bullets.

## Numbers
- Live runs: `raw("tau2_retail.json")["pass_1"]` etc. (files in `agents_course/raw/`, tested by `test_tau2.py`).
- Deck numbers: `D[...]` (`raw/deck_numbers.json`) and capture_deck's inputs as `DECK_IN.S`, `DECK_IN.PRICE_IN`, … .
  Never type a number into a scene; digits on screen come from these.
- Spoken helpers if needed: `words(72)`, `point(0.7667)`, `percent(0.6)`, `cents(0.2643)`.

## Visuals (agents_course_kit.py)
| need | helper |
|---|---|
| real code from `agents_course/code/` | `code_panel("s3_memory.py", "def fit", "return", tag="shown")` → `VGroup(title, code)`; start/end are substrings of the first/last line (or line numbers); ≤ 18 lines; `tag="run"` for s1/s2, `"shown"` for the idea snippets. The panel fills the frame (12.5 units wide, as large a font as fits; only long lines shrink it) and comes centred. Show it alone: to put something beside it, fade it out rather than shrink it (a shrunk panel is unreadable) |
| box around code lines | `highlight(panel, code_lines("s3_memory.py", "keep ids")[0], last=None)`: one line pitch tall per line, behind the text, never touching the neighbouring lines |
| a real conversation | `chat_panel(chat_messages(raw("tau2_retail_trajectory.json")["messages"])[i:j])`; one bubble: `bubble(role, text)` with role `user` / `assistant` / `call` / `tool` |
| a τ²-bench tool's schema | `schema_card("cancel_pending_order", show=["order_id", "reason"], mark="explicit user confirmation")`; `tool(name)["type"]` is READ / WRITE / GENERIC |
| JSON as data | `json_block(obj, chars=30)` |
| words in a box / a pipeline | `tile(label(...))`, `flow_row([...])` → `(tiles, arrows)` |
| bars | `bars([(label_or_mobject, value), ...], fmt)` → `(rects, tops, labels, floor)` |
| a stack of layers | `stack([...])` (bottom-up) |
| run / shown markers | `run_pill()`, `shown_pill()`; under a captured result `captured_tag("tau2_retail.json")` |
| monospace ids, tool names, code words | `mono(text)` (data, not labels) |

## Labels
Every on-screen word is a label: `label("ac_…")`, keys prefixed `ac_`, an `en` form only for now (Korean `ko` is added
later). Each builder keeps its new labels in its own file, `scratchpad/agentlabels/sNN.yaml` (the kit's are in
`kit.yaml`, the opening's in `s00.yaml`, section 1's in `s01.yaml`); render with `LABEL_DRAFTS=<that dir>`. Reuse a
key before coining one; `common.py` stops on a key defined two ways. Words only, never values: a number goes beside
the words (`tagged(value, words)`) or as `MathTex`. Merge into `narration/labels.yaml` before the full build.

## Dev render and checks
    cd video && LABEL_DRAFTS=<dir> LANG_CODE=en uv run --frozen manim -ql --media_dir out/agentsdev_en/media agents_course_s03.py S03Window
Parallel renders can race on manim's text cache (`texts/….svg` not found): rerun the scene. Then
`uv run --frozen python check_edges.py <mp4>` (silent = clean), look at frames
(`ffmpeg -ss T -i <mp4> -frames:v 1 f.png`), and `ffmpeg -i <mp4> -af silencedetect=n=-40dB:d=2 -f null -` (only
the pause card may show). Tests: `uv run python -m unittest discover -s agents_course -p 'test_*.py'`.

## Code files stay at 72 columns

The panel's font is set by the longest line shown, so `code/*.py` is wrapped to at most 72 columns (a 113-character
docstring line had shrunk capitals to ~17 px at 1080p; now 26-32 px). Split long strings by implicit concatenation
so the joined text stays byte-identical, and check the AST is unchanged. A statement that wraps needs
`highlight(..., last=...)` to cover its second line, and a panel's end anchor must name its last line. A full
18-line panel reaches the brand mark at the bottom right: place it with `.move_to(UP * 0.3)`.
