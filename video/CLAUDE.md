# Video track — Advanced AI

Narrated Manim videos built from the same material as the slide decks.

## Layout
- `common.py` — speech service, `CourseScene`, style helpers, brand marks.
- **Languages.** `languages.yaml` (loader `languages.py`) is the one list of the course's languages: names, script, edge
  voices / rate / trim (`common.py` reads them from it), section-card word, opening chapter title. `builds.py` is the one
  place that parses a build name (`[mK_]lectureNN_<lang>[_<engine>]`: `lecture01_uz_navoiy`, `m7_lecture01_ru`); never
  test `endswith("_uz_navoiy")` or repeat the regex. A lecture's narration in a language is `narration/<stem>_<lang>.md`
  (one language, same line ids as the primary language) or, for uz and en, the bilingual `<stem>.md`. New languages are
  added in the studio (**+ add language** writes an empty skeleton), drafted by Claude, approved line by line at
  the app's Script & languages screen (`/#mode=script&lecture=<stem>&lang=<code>`); `studio/linestatus.py` keeps who approved what and flags the same line in
  the other languages "needs update" when one changes (`line_status` table, by hash). Studio-side details in `STATUS.md`. Phase 2: `check_lang.py` (preflight), `cues.py` (cue timing in any language),
  `drafts.py` (watermark), `studio/buildlang.py` (the "Build video" job), `voice_check_lang.py` (whisper CER check).
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

## The studio (what the instructor uses)
One address, `http://localhost:8081/` through the ssh tunnel (the server is `serve_presenter.py` on 8080): the React app in
`studio/app` (built into `studio/static/app/`; `cd studio/app && npm run build`). Four screens: **Record** (the booth: picture,
teleprompter, input meter, one take of a line with L or a whole session with R), **Edit** (takes, trims, the timeline, versions of a
rewritten scene), **Script & languages** (lines and labels × languages: approve, edit, still fine, add a language, build a video;
an Uzbek line is never voiced or built until approved), **Export** (voice cleaning, unrecorded lines, queue, finished exports,
watch). Deep links: `/#mode=edit&lecture=lecture01&lang=uz&line=14`. The old pages' addresses (`/?m=7`, `/lecture?build=`,
`/edit?build=`, `/watch`, `/narration`, `<build>/presenter/presenter.html`) redirect into it. The old HTML frontend is gone;
`presenter.py` keeps writing `presenter/lines.json`, the silent video and an offline presenter page. `studio/run_tests.sh [fast]`.
**Voice cleaning profiles** (`compose_recording.CLEAN`; `STUDIO_PROFILE`, `/api/process?clean=`, `/api/export?clean=`): **`cloned`
is the default** for new recordings and for Export, then `deepfilter`, `voice`, `mild`, `strong`, `off`. `cloned` = the
deepfilter voice re-spoken by CosyVoice2 voice conversion (`POST /vc` on the voice server, `~/navoiy-stack/work/tts_server.py`,
port 8765; piece by piece, each piece fitted to its source length, so the file is exactly as long as the deepfilter one;
`studio/media.py` `vc_pieces` / `convert_voice` / `vc_http`). **The voice server must be up** (the process job starts it if
not; otherwise the job fails with "cloned voice: the voice server did not answer"). About 0.2 s of processing per second of
audio. Edit > Recordings: "convert to cloned voice" per recording and "your voice / cloned voice" playback. Details: `STATUS.md`.

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
- **Scenes are joined with `join_parts.sh`, never a bare `concat -c copy`.** A scene's audio stops with its last clip
  ~0.6 s before the picture ends; a copy-join left a hole in the audio timestamps at every join, and players clipped
  the syllable before it (agent course, 3:21). Decoding such a file to raw samples silently closes the holes: that is
  how `patch_audio.py` once slid Lecture 1's audio 46 s early. Check a build with
  `ffprobe -select_streams a:0 -show_entries packet=pts_time` (no step > 50 ms), not by decoding.
- **The agent course** (`agents_course*.py`, `narration/agents_course{,_ko}.md`, `labels_agents_course.yaml`) is English
  and Korean, edge-tts (Andrew; InJoon at +20 % with clip edges trimmed, since it reads ~40 % slower and pads 1.2 s),
  no corner mark (`LectureScene.BRAND = False`). Its testbed and runs live in `agents_course/` (see BUILDING.md).
- **Sound in a pause is muted, not re-voiced.** The cloned voice can fill the pause between two sentences with a
  steady buzz (Lecture 1, 19:06: 0.9 s at -20 dB between «…topamiz.» and «Kyu…»). `patch_audio.py at <build> <m:ss>`
  aligns the clip's words, mutes only sound lying between two words near that time, in the cached clip and in the
  built video's audio track (picture copied, length unchanged), and keeps both originals. Noise inside a word is
  refused. `patch_audio.py scan` only lists candidates: a held vowel the aligner squeezed looks the same, so nothing
  is muted unheard.
- **The voice's «yuz» can end in «zh».** Word-final z after «yu» sometimes has its hiss centred at 3-4 kHz («sh»
  band) instead of ~6 kHz («biz» is always clean). It varies with the take, not the flow checkpoint, prompt or
  spelling (tested 2026-10-13). Latin letter names («kyu», «ay kyu ar») are blurred too: four respellings failed both
  recognisers; the spoken term («birinchi kvartil», «kvartillararo oraliq») passed.
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
- **The cloned voice can garble or cut off a line while the clip keeps a normal length.** Lecture 3's first line lost a
  phrase to 1.6 s of hiss; Lecture 4's stopped inside its last word. About a fifth of the clips in Lectures 1-5 failed.
  After voicing, run `voice_check.py <build>` (two Uzbek recognisers per clip; fails on a run of 3 missed words, CER
  over 0.15, a lost last word, or a clip still loud in its last 50 ms), then `revoice.py <build>`: it re-voices each
  failure sentence by sentence, tries other seeds where a sentence still fails (the server takes an optional `seed`),
  and replaces the cached clip only if the new take scores better; originals stay in `<build>/revoiced/`. Then
  re-render the scenes it lists and concatenate. Both run in the Navoiy env
  (`~/navoiy-stack/CosyVoice/.venv/bin/python`); `audio_fx.py` holds the clip clean-up they share with `common.py`.
  Recognisers stumble on spoken letters and numbers ("ey karra eks"), so a failure is a lead, not a verdict.
  Two more listeners back them up: **forced alignment** (Meta's MMS aligner in torchaudio) scores every approved
  word against the audio and names the lost ones (the 0:18 garble: 8 words at 0.00), and **DNSMOS** (Microsoft's
  P.835 model, `~/navoiy-stack/models/dnsmos/sig_bak_ovr.onnx`) scores background noise per 2 s window (the 6:17
  hiss: 1.15 of 5; clean speech ~3-4). The aligner also stumbles on dense spelled numbers, so its lost-word run
  fails a clip only when the recognisers lose words too. Softer signals put a clip on the **listen list**:
  `uv run python listen_list.py <build>` writes `<build>/listen_list.md`, each flagged line with its time in the
  final video, for the instructor to hear first. Every check is calibrated on the defects the instructor reported.
- **Labels next to a curve get a black backing** (`add_background_rectangle`), or the curve runs through the text.
- **`Indicate` grows a mobject by 20 %**, which pushed a full-width bell curve onto the frame edge; use
  `scale_factor=1.04` on anything near full width.
- **Nothing persistent may touch the frame edge.** `check_edges.py` flags bright pixels within 4 px of any border, so the brand mark is inset by `common.SAFE`. A full-width footer strip would flag every frame — branding lives in the opening bumper, the closing card, and that one inset mark.
- **The editor's server must not queue a job while its request holds a write**: `with dbc() as c:` keeps an open
  transaction, and `enqueue` writes through a second connection, so it waited 10 s on itself and failed with
  "database is locked". `editor_post` collects jobs in `later` and runs them after the request's block commits.
- **A recogniser's "different word" is not an extra word.** rubaistt heard «son emas balki» as «sonimiz va»; cutting
  the mismatch would cut words the instructor said. `timeline.script_check` keeps inserts (cuttable), deletes
  (missing) and replacements (shown, never cut) apart. It also splits «boʻladi» at the apostrophe; words_worker
  joins a piece that starts with one back onto the word before.
- **Rewriting a line re-renders its whole scene**, so every later line of the video moves: recordings made against the
  old line list would point at the wrong picture. Merging a version (`studio/versions.py`) moves them
  (`timeline.remap_events`: each position keeps its offset inside its line) and keeps the old events beside them; a
  failed merge puts back only what it changed (a `before_merge` backup left by an earlier merge is never restored),
  then joins again, since presenter.py reads the line timings from the padded scenes in `joined/`.
- **A picture shorter than its voice broke the whole editor** (2026-10-19): `segments()` dropped spans under 20 ms
  (two presses 8 ms apart) from the picture but not from the voice. No span is dropped now, and `edit_list` pads a
  mismatch instead of asserting.
- **A cue has no word for a new language.** `cues.py` places it from the line's reference-language text (same sentence and
  share, else the same share of the line); en and uz still read their own form, asserted on every real (line, cue) pair
  (`studio/test_cues.py`). A cue that maps badly gets `narration/<stem>_<lang>.cues.yaml`. Run `check_lang.py <lecture> <lang>`
  before a build: it lists labels without the language's form, empty lines, words-on-screen dicts and cues a render would stop on.
- **`label()` / `by_lang()` never fall back to another language** (`NoForm` names the missing one). A `LABEL_DRAFTS` file may add
  a language to an existing key; a form both files hold must match.
- **edge-tts sometimes answers nothing** (`NoAudioReceived`, ru, 2026-10-21: the same text worked a minute later), so
  `EdgeTTSService` retries it; its truncation guard counts words (5 a second) or, for zh, characters (`languages.yaml` `guard`).
- **A draft build is tagged until every line and label of its language is approved** (`drafts.py`); Uzbek is refused by the
  studio's build job instead (the instructor approves every Uzbek line before it is built).
- **join_parts.sh prefixes `$PWD`** to its out-dir: call it with paths relative to video/.

## Rules carried over from the decks
Uzbek narration follows **Uzbek translation rules** in the repo-root `CLAUDE.md` (berilganlar, tavsiflovchi, native "we" phrasing, approval before voicing).
Numbers on screen come from a saved raw output, never retyped. Narration spells numbers for the ear while the screen shows digits. One concept per section; problem first, concept as the answer; each section ends with the question the next one answers.
**Explain from several sides, and recap** (instructor, after watching Lecture 4: "explanations are so short, mostly
from one side"). Each core concept gets more than one angle: the intuition in words, the picture, the formula read
aloud, a worked number, and where it helps a contrast or a common mistake. Before a section leans on an earlier idea
(Beta, likelihood, standard error), recap it in a sentence or two. Longer sections are fine.
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
