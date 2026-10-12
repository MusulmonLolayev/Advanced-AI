# Video track — Advanced AI

Narrated Manim videos built from the same material as the slide decks.

## Layout
- `common.py` — speech service, `CourseScene`, style helpers, brand marks.
- **One video per lecture**, built like the slides: a lecture opening (one greeting), then Part 0, Part 1 … each with a
  part card, and inside each part one section per concept with a short section card. Sections say "keyingi/avvalgi
  boʻlim", never "video"; only the lecture's end points to the next lecture. Narration drafts live in
  `narration/lectureNN.md` and must be approved before building.
- Scenes: one `Scene` class per beat, `SCENES = [...]` giving order; `render.sh` concatenates them into the one lecture video.
- `statistics/raw/` — real stdout captured from the figure scripts. Every number on screen must trace to a file here.
- `statistics/capture_lNN.py` computes a lecture's numbers (`compute()` is pure) and writes `raw/lNN_numbers.json`;
  `statistics/test_lNN.py` unit-tests every one of them against the slides and the narration (`unittest`, no
  pytest): `uv run python -m unittest discover -s statistics -p 'test_l02.py'`. Run by discovery, not by dotted
  path — the folder name `statistics` shadows the standard library module (`test_l01.py` covers the Lecture 1 numbers
  set beside labels; its example inputs — bottle settings, spam share, class of 30 — live in `capture_l01.py`).
  The test caught a narration claim the
  numbers did not support ("the three hardest departments"), so run it after every narration edit.
- `statistics/screens/figures/` — figures rasterised from the committed PDFs, cached so a video re-renders later.
- `render.sh <module> [l|m|h|k]`, `check_edges.py <mp4>`. `JOBS=N` renders scenes in parallel (keep N <= 4 with
  the Navoiy voice, whose server answers one request at a time); `ONLY="S03Histogram ..."` renders just those scenes.
- Lecture N: `lectureNN.py` collects the scenes of `lectureNN_s00.py` … (one file per section; it re-tags their
  `__module__`, since manim only renders classes whose module name starts with the absolute-path name it gives the
  file it was handed). `lecture_kit.py` holds what every lecture shares — the narration parser, `LectureScene`
  (say/cue/section_card/hands_on/clear_all), card/frac/die_face/bars_row — and `lectureNN_kit.py` binds it to that
  lecture's approved `narration/lectureNN.md`, numbers and part layout with `bind()`, so the voice reads the approved
  words verbatim: never copy narration into Python. `lecture02_kit.py` adds the 100-student grid, the tree and the
  contingency table used across Lecture 2's sections.
- **Every on-screen word lives in `narration/labels.yaml`**, one file for all lectures (and the shared cards: pause,
  "Keyingi", "N-maʼruza"). Each label has a key and its interchangeable forms per language, the default first; a scene
  shows `label("mean")` or `label("mean", 1)` and never holds label text itself. Reuse an existing key, or add a form
  to it, before coining a new one. After any label change run `uv run python labels.py`: it checks every `label()`
  call against the file (key, form, unused keys, ʻ/ʼ spelling) and rewrites the file in lecture order with a "where
  shown" comment per key. Narration stays in `narration/lectureNN.md`.
- **A label is words only, never a value** (instructor's rule). The number comes from the captured data and is set
  beside the words: `tagged(value, words)` when both languages put the words on the same side ("40 talaba",
  "yaroqsiz: 11 / 1000"), as one line split into two objects so they share a baseline. Where the languages order
  them differently ("100 kishidan 1", "9,900 ning 5% i"), show the number as math the languages share
  (`P(kasal) = 1/100`, `5% × 9,900`) with the label beside or under it — never assemble grammar in code. Fixed
  names keep their number ("0-qism", "2-maʼruza", "1-bosqich"). `labels.py` rejects a `{placeholder}` in a label.
- **Building sections in parallel:** each builder keeps its new labels in its own file in a scratch directory and
  renders with `LABEL_DRAFTS=<dir>`; `common.py` merges those files over `labels.yaml` and stops on a key defined two
  ways. Merge them into `labels.yaml` (`labels.write`) before the full build. `label()` takes its key as a plain
  string — for a loop over data keys, build a dict of labels once (`CUP_NAME` in `lecture03_kit.py`) so `labels.py`
  can see every key. Seed the full build's voice cache by copying `out/<dev>/media/voiceovers/*` into
  `out/<lecture>/media/voiceovers/` (file names are relative), so no line is voiced twice.
- A section file renders on its own while it is being written:
  `LANG_CODE=uz uv run --frozen manim -ql --media_dir out/l02dev_uz/media lecture02_s04.py S04Table`.

## Environment
`uv` project (Python 3.12). System deps: `ffmpeg`, `libcairo2-dev`, `libpango1.0-dev`, `pkg-config`.
`uv` itself installed with `pip install --user uv`, not `curl | sh`.
Figures are generated separately by the `adv_ai` conda env — the two never mix.

## Lessons (do not re-learn these)
- **Manim cannot read matplotlib's SVG.** `SVGMobject` dies with `TypeError: object of type 'NoneType' has no len()` on a `<path>` with no `d`. Rasterise the committed PDF with `mutool draw -r 300` instead; `common.figure()` does this and caches the PNG. Video is raster anyway, so nothing is lost.
- **An embedded chart is too small to read at video scale.** A 5.6in matplotlib figure shown 4.6 units tall puts its 8 pt legend at roughly 10 px on a 1080p frame. Use embedded figures only for callbacks; animate the hero chart natively in Manim, driving it from the same numbers in `statistics/raw/`.
- **SoX is missing and that is fine** — `manim-voiceover` only needs it to time-stretch audio, which we never do. The warning is noise.
- **`render.sh` must filter stderr when reading `SCENES`**, or the SoX warning lands in the scene list.
- **The ffmpeg concat list needs absolute paths**, since ffmpeg resolves entries relative to the list file.
- **`render.sh` must take each scene from the folder of the quality it just rendered** (`480p15/`, `1080p60/`...).
  A bare `find -name S.mp4` picked a three-day-old 1080p scene over the fresh 480p one, and the concat silently
  shipped the old video. It also checks the file is newer than the render's start.
- **Text-only scenes are not a video.** Every scene draws the real data: the 600 salaries as a dot histogram, then as
  sorted bars that level to the mean; the mean as a rectangle whose area is the payroll; the 50 drinkers as a sorted
  row whose middle shifts by half a person. Words on screen are labels, not the content.
- **One video, every language.** Narration lives in `narration/lectureNN.md` and screen words in
  `narration/labels.yaml`, both picked by `LANG_CODE`;
  `common.at()` / `CourseScene.until()` time visuals to sentence starts by character share, since neither voice
  reports word timings.
- **Voice caches are per scene** (`media/voiceovers/<Scene>/`): manim-voiceover appends to its cache index without a
  lock, so parallel scenes sharing one cache would corrupt it.
- **Cues may differ by language.** `self.cue(tr, t, k)` takes a sentence index, a phrase, or `{"en": .., "uz": ..}`;
  sentences split on `. ? ! :`, and the Uzbek and English lines often split differently.
- **Silent cards and transitions stay short** (section card 1.0 s, `clear_all` 0.5 s, 0.15 s after each line): voice clips carry their own
  lead-in and tail, and anything over 2 s of silence that is not a hands-on pause is a defect.
- **The cloned voice pads its clips** with up to ~1.2 s of quiet at each end (edge-tts barely does). `NavoiyService`
  trims both ends to 0.12 s (`common.trim_silence`); without it every section boundary in the Uzbek lecture was a
  2.4-3.4 s gap.
- **The cloned voice can stop early on a long run of repeated words** (Lecture 2's line of spelled decimals), and
  its fixed seed repeats the same cut on every retry. `NavoiyService` then voices that line sentence by sentence and
  joins the pieces with a 0.2 s breath; lines that voice whole are untouched.
- **`tagged()` turns ligatures off**: Pango sets "fi" as one glyph, which shifted the split between number and words
  ("1 haqiqiy firibgarlik"). Without ligatures a Text has one submobject per character, spaces included.
- **Never name a local variable `label`**: it shadows the label function for the whole function body
  (`UnboundLocalError`). The move to `labels.yaml` was checked by logging every string each scene hands to
  `Text`/`MathTex` before and after, in both lectures and both languages: identical, so no re-render was needed.
  That probe caught a key reused for two different labels.
- **edge-tts can be refused outright** (HTTP 403 from speech.platform.bing.com on 2026-10-12, version 7.2.8 and the
  latest alike; the clock was right and announcing a newer Edge version did not help). Lines already in a voice cache
  still render; new English lines wait until the service answers again.
- **The cloned voice can also pause too long inside a line** (2.3 s between two sentences of Lecture 5's 10.9).
  `NavoiyService` now runs `common.cap_pauses` on every clip: silences over 0.8 s shrink to under a second, normal
  breaths (~0.4 s) stay. Clips cached before the fix keep their audio; cap one by hand with `cap_pauses(path)`.
- **Labels next to a curve get a black backing** (`add_background_rectangle`), or the curve runs through the text.
- **`Indicate` grows a mobject by 20 %**, which pushed a full-width bell curve onto the frame edge; use
  `scale_factor=1.04` on anything near full width.
- **Nothing persistent may touch the frame edge.** `check_edges.py` flags bright pixels within 4 px of any border, so the brand mark is inset by `common.SAFE`. A full-width footer strip would flag every frame — branding lives in the opening bumper, the closing card, and that one inset mark.

## Rules carried over from the decks
Uzbek narration follows **Uzbek translation rules** in the repo-root `CLAUDE.md` (berilganlar, tavsiflovchi, native "we" phrasing, approval before voicing).
Numbers on screen come from a saved raw output, never retyped. Narration spells numbers for the ear while the screen shows digits. One concept per section; problem first, concept as the answer; each section ends with the question the next one answers.
A pause task may reuse a number the section already showed, the way a teacher repeats a point in class; it does not
have to be new.

## Instructor voice (Navoiy, fine-tuned)
`VOICE_ENGINE=navoiy LANG_CODE=uz JOBS=4 ./render.sh lecture01 h` narrates in the instructor's own voice.
The stack lives **outside the repo** in `~/navoiy-stack/` (CosyVoice @ 074ca6d, Python 3.10, torch 2.3.1+cu121,
Navoiy `emotion_600h_joint.pt`, fine-tuned LLM epoch 1 + flow epoch 12 in `ft/exp/`). Start the server first:
`cd ~/navoiy-stack/CosyVoice && .venv/bin/python ../work/tts_server.py 8765` — it loads the model once; `NavoiyService`
in `common.py` POSTs each line to it. Stop it by PID, never `pkill -f` (the pattern matches your own shell).

Lessons from building it:
- **Instruct mode is the wrong cloning mode.** `inference_instruct2` deletes the prompt's speech tokens, so rhythm and
  intonation come from the model's training speakers. `inference_zero_shot` with the prompt's exact transcript keeps them.
- **The prompt recording matters as much as training.** A phone recording scored 0.60 speaker similarity to the lecture
  voice; a lecture clip scored 0.80 with no training at all. The clone copies mic and room along with the voice.
- **Stock Whisper cannot transcribe spoken Uzbek** ("berenchi qorub" for "birinchi guruh"). Use Kotib/uzbek_stt_v1 and
  islomov/rubaistt_v2_medium, and keep only clips where the two agree (CER <= 0.05).
- **Strip `step`/`epoch` from Navoiy's checkpoint before training** — it carries step 89999, which train.py reads and
  which would put the LR schedule 90k steps in.
- **The LLM overfits fast on ~50 min**: 99.7% train accuracy by epoch 29, dev loss best at epoch 1. Save every epoch and
  choose by dev loss. Flow dev loss is noisy (random t and prompt length per eval) — treat its "best" as approximate.
- **CosyVoice2 flow training needs a patch** for clips not a multiple of 40 ms (25 Hz tokens vs 50 Hz mel). See
  `~/navoiy-stack/CosyVoice/cosyvoice/flow/flow.py` vs `flow.py.orig`.
- The TTS server runs from another directory, so the service must send it **absolute** output paths.
- **English in the instructor's voice (tested 2026-10-12, not yet used; English is on hold by the instructor's
  choice):** the fine-tuned LLM no longer reads English (Whisper heard gibberish), and English respelled in Uzbek
  orthography drops whole sentences. The stock CosyVoice2 LLM with the fine-tuned flow (epoch 12),
  `inference_cross_lingual(text, prompt_wav)`, was word-perfect under Whisper large-v3 with speaker similarity 0.63
  (the Uzbek clips score ~0.67, two real recordings ~0.80). A true English fine-tune would need 30-60 min of the
  instructor reading English.
