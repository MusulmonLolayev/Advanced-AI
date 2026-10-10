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
- `statistics/screens/figures/` — figures rasterised from the committed PDFs, cached so a video re-renders later.
- `render.sh <module> [l|m|h|k]`, `check_edges.py <mp4>`. `JOBS=N` renders scenes in parallel (keep N <= 4 with
  the Navoiy voice, whose server answers one request at a time); `ONLY="S03Histogram ..."` renders just those scenes.
- Lecture 1: `lecture01.py` collects the scenes of `lecture01_s00.py` ... `lecture01_s14.py` (one file per section;
  `lecture01.py` re-tags their `__module__`, since manim only renders classes whose module name starts with the absolute-path name it gives the file it was handed). `lecture01_kit.py` parses the approved
  `narration/lecture01.md`, so the voice reads the approved words verbatim: never copy narration into Python.

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
- **One video, every language.** Narration and screen words live in the video's `T` table keyed by `LANG_CODE`;
  `common.at()` / `CourseScene.until()` time visuals to sentence starts by character share, since neither voice
  reports word timings.
- **Voice caches are per scene** (`media/voiceovers/<Scene>/`): manim-voiceover appends to its cache index without a
  lock, so parallel scenes sharing one cache would corrupt it.
- **Cues may differ by language.** `self.cue(tr, t, k)` takes a sentence index, a phrase, or `{"en": .., "uz": ..}`;
  sentences split on `. ? ! :`, and the Uzbek and English lines often split differently.
- **Silent cards and transitions stay short** (section card 1.2 s, `clear_all` 0.5 s, 0.15 s after each line): voice clips carry their own
  lead-in and tail, and anything over 2 s of silence that is not a hands-on pause is a defect.
- **Nothing persistent may touch the frame edge.** `check_edges.py` flags bright pixels within 4 px of any border, so the brand mark is inset by `common.SAFE`. A full-width footer strip would flag every frame — branding lives in the opening bumper, the closing card, and that one inset mark.

## Rules carried over from the decks
Uzbek narration follows **Uzbek translation rules** in the repo-root `CLAUDE.md` (berilganlar, tavsiflovchi, native "we" phrasing, approval before voicing).
Numbers on screen come from a saved raw output, never retyped. Narration spells numbers for the ear while the screen shows digits. One concept per section; problem first, concept as the answer; each section ends with the question the next one answers.

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
