# Video track — state as of 2026-10-14 (paused)

Paused by the instructor to make a short agent-development course (Module 7) first. Uzbek narration in the
instructor's cloned Navoiy voice; English track on hold.

## Lectures (Module 0, Statistics)

| Lecture | Narration | Video (`out/lectureNN_uz_navoiy/`) | Voice QA |
|---|---|---|---|
| 1 | Draft 4 approved, built in | 33:31, 19:07 buzz muted (`patch_audio.py`) | re-voiced twice; 5 clips fail (letter names), 39 to listen |
| 2 | Draft 2 (depth) approved as written | 17:06, built before depth and before QA | checked only, 22 flagged, not re-voiced |
| 3 | Draft 2 approved as written | 20:28, no depth lines yet | re-voiced twice; 3 fail, 26 to listen |
| 4 | Draft 2 approved as written | 18:34, no depth lines yet | re-voiced twice; all 109 pass, 18 to listen |
| 5 | Draft 2 approved as written | 16:13, built before depth and before QA | checked only, 24 flagged, not re-voiced |
| 6 | Draft 2 approved as written | not built | — |
| 7 | Draft 1 approved as written | not built | — |
| 8–10 | Draft 1, **not approved** | not built | — |

"Approved as written" = the instructor said "Build the videos" for Lectures 2–7 (2026-10-13); their proposed terms are
recorded in the root `CLAUDE.md`. Every `listen_list.md` beside a video lists clips to hear first, with times.

## Half-built work — branch `wip/lecture-depth-builds` (local, not merged)

Six builders were stopped mid-way: Lectures 2–5 had their lettered depth lines partly wired into scenes; Lectures 6
(sections 0–5) and 7 (sections 0–10) had scene files written. Nothing there is rendered at full quality or checked.
Their label drafts are in `video/wip_labels/lNN/*.yaml` on that branch (merge with `labels.write` before a build).
Dev renders: `out/l0{2,3,4,5}depth_uz/`, `out/l0{6,7}dev_uz/`. Resume each lecture by checking which lettered keys
the scenes already say (the narration parser lists them) and finishing the rest.

## Open voice problems (why work stopped)

1. **«z» after «yu» sounds like «zh»** (yuz → yuzsh). Measured: the hiss centre drops to 3–4 kHz («sh» band) where
   «biz» stays ~6 kHz. Same across flow checkpoints, prompts and respellings; it varies by take (seed). An in-place
   spectral reshape of the hiss (2–4.5 kHz down, 5–9.5 kHz up) "partly solved" it by ear — not yet in a tool.
2. **Latin letter names** («kyu», «ay kyu ar», sometimes «eks») come out blurred; four respellings failed both
   recognisers, the spoken terms («birinchi kvartil», «kvartillararo oraliq») passed. Needs the instructor's
   decision: keep letters on screen but say the term?
3. **"Other problems"** the instructor heard and has not yet listed — ask before resuming.

Samples (on disk, gitignored): `out/voice_tests/` — `zfix/` (before→after z repair), `yuz/` (respellings),
`kyu_spellings/`, `z_flow*`/`kyu_flow*` (checkpoints × prompts, script `grid_z.py`). Review files with only the
new lines per lecture: `out/review/l0N_add.txt`.

## Tools

- `voice_check.py` (two ASRs + MMS aligner + DNSMOS) → `voice_check.json`; `revoice.py` (per sentence, `SEEDS=`
  for a second pass); `listen_list.py` → `listen_list.md`; `patch_audio.py at <build> <m:ss>` mutes a buzz in a
  pause in clip and video without re-rendering (`scan` lists candidates only).
- Voice server: `cd ~/navoiy-stack/CosyVoice && echo $$ > ~/navoiy-stack/work/tts_server.shellpid; exec
  .venv/bin/python ../work/tts_server.py 8765` (stop with `kill $(cat ~/navoiy-stack/work/tts_server.shellpid)`).
  Stopped 2026-10-14.
- Recording studio: `nohup .venv/bin/python serve_presenter.py 8080 > out/serve_presenter.log 2>&1 &`, then save
  the PID the log prints (`studio on port 8080 (pid N)`; `$!` is the wrapper shell, not the server) to
  out/serve_presenter.pid (stop with `kill $(cat out/serve_presenter.pid)`); reach it with `ssh -L 8081:localhost:8080
  hometqqt` → http://localhost:8081/ (the instructor's laptop has its own 8080 taken). Presenter keys: Space pause /
  play, → next line, ← back, N notes below / right / off (words light up at the narration's pace), M microphone, R record;
  the video plays at 1/1.1 speed (logged per recording, the build slows the picture to match). Build cleans the voice: `deepfilter` (default; DeepFilterNet binary in `bin/`, git-ignored, from the
  v0.5.6 release) or the profiles of `~/teaching/clean_video.sh` (voice / mild / strong / off), then one fixed gain
  to −19 LUFS + a peak limiter, picture via NVENC. DNSMOS on the instructor's first recording: raw 1.78, voice 2.17,
  deepfilter 3.16. Listening samples: `out/denoise_compare/` (served at /denoise_compare/). The studio page is split by module (a
  panel on the left, `/?m=7`): Module K's lectures are builds `mK_lectureNN_uz_navoiy` (Module 0: `lectureNN_uz_navoiy`),
  its files whatever is linked into `out/shared/mK/` (e.g. `m7/Module7_Lecture01.pdf` → `agents/lecture01.pdf`).
- **Editor** (2026-10-19, `studio/`, "Open editor" on a lecture; `/edit?build=…#open=41`): the presenter uploads each
  recording in one-second pieces (kept in the browser until the server has them; an unsent rest is sent on the next
  visit; a session silent for 2 min is closed and processed anyway), logs each line start, and X marks a mistake (the
  line starts over). Each session is processed once (joined, cleaned with deepfilter, a seekable preview copy, its
  pauses) and cut into one take per line; the editor picks a take per line (default: the newest not marked a
  mistake), trims, cuts (also by clicking words of the transcript), nudges picture against voice, shortens pauses
  over a still picture, transcribes and checks against the approved text (rubaistt for Uzbek, whisper-large-v3-turbo
  for English, MMS alignment: missing / extra / heard differently -- only extra words are offered for cutting), previews
  in the browser with no rebuild, and exports `presenter/export/<build>_edited.{mp4,srt,chapters.txt}` from the same
  edit list. A recording made against an earlier build of the video (another line list) is shown but not used.
  Unrecorded lines keep the video's own narration (the cloned or synthetic voice, as built; or silence, a switch in
  the header), every voice source brought to −19 LUFS, so a few recorded lines can replace just those lines.
  **Rewrite a line as a version** (each line's "narration" box, `studio/versions.py`): "save as new version" voices
  the text (cloned voice: several seeds per sentence, each judged like voice_check.py) and renders that line's
  section into `out/<build>/versions/<Scene>/v<N>/` (render.sh `OUT_DIR`, the kits' `NARRATION_DIR` pointing at a
  draft copy of the narration, the section's voice cache copied in): the narration file and the lecture stay as
  they are. Versions of one section build on each other (rewrite line 120, then 121: the new version has both); each
  can be watched from its line, rewritten again, discarded, or **merged** (the instructor's merge is their approval):
  the texts go into the narration file, the clips into the lecture's voice cache, the section replaces the old one
  (`<Scene>.before_merge.mp4` kept), the lecture is rejoined (`<build>.before_merge.mp4` kept), the presenter page
  prepared again and earlier recordings moved to the new timings; the section's other versions turn stale. A failed
  merge undoes only what it did, joins the lecture again and rebuilds the presenter page. "Re-voice as is" is a
  version with the same text. Red / amber marks on lines and the timeline are voice_check.json's fails / listen
  list. The voice server can be started and stopped from the editor (only the one started there, by its PID file).
  Lecture01's failing line 29 («…eks ikki…») did not improve with any seed (the rule of 2026-10-14: say the term),
  so such a line needs rewriting, not re-voicing.
  **Line ends** (2026-10-21): each open line shows a level strip of its take (voice level in dB over the take, silences of
  0.5 s or more shaded with their length, the picture still/playing as a band, the words, removed spans hatched: red
  cut, blue fast-forwarded) with two draggable handles that set `trim_in` / `trim_out` (snapped to 0.05 s, saved on
  release) and say how much silence they keep ("0.4 s before the first word"). A trim is handled like tightening: cut
  where the picture is still, fast-forwarded (up to 4x, at least 0.15 s, the voice silent there) where an animation
  runs, so it is never cut. "fit start / end / both" set the trims to the lecture's margin ("keep 0.3 s at line ends"
  in the header, `/api/settings?key=margin`); "reset ends" clears them. **Tighten all** (optional) shortens the pauses
  inside each chosen take and fits the ends by the margin; a trim set by hand stays, and `edit["auto"]` names the
  trims the tool set, so "undo tightening" takes back those, the pause cuts and any squeeze, not the hand trims, cuts
  or nudge. Under the timeline a lecture strip shows the voice level of the whole edit list (`/api/levels`, cached as
  `*.levels.json`) with every silence of "long silence >=" seconds (header, default 1.0, kept in the browser) in amber,
  across line boundaries; click one, or use the transport's "next long silence" / back arrow, to jump there and open
  its line. On lecture01_uz_navoiy: 61 silences of 1 s or more, 155 s in all (no recording edited).
  **Takes on the presenter page** (2026-10-21): `presenter.html#line=7` opens with a takes panel (a drawer at the right,
  T shows or hides it, gone while a recording runs) for the line on screen; it follows ← / →. It lists every take of the
  line from every usable session (T1, T2 …, length, time, "used in the video", struck through when a mistake) with ▶ watch
  (the take as the video will have it, on the page's own video with the editor's two-track player, nothing logged),
  ▶ in context (the last 2 s of the line before, the take, the first 2 s of the line after: the edit list's neighbours),
  use this one, mistake, delete, and the editor's level strip with both handles and fit start / end / both. **L** (or
  "● record a take") records one take of that line: new session, the line event, the picture plays the line, and the
  recording stops itself 1 s after the line ends (or at → / L), finishes the session and processes it; the panel shows
  "processing…" and then the take, and L again adds another. The newest take that is not a mistake is the used one unless
  one was picked by hand (a hand pick stays). One call per line: `GET /api/line?build&line=K` (K from 0 like every `line`
  in the API: text, takes as the editor's views, chosen / picked, audio, margin, video, the joins, pending sessions);
  the panel polls it every 3 s while something is processing. X outside a recording now says what it does. The page itself
  is rendered by serve_presenter.py from `presenter.PAGE` (`presenter.render`) with the build's lines.json and the silent
  video's `?v=`, so a change to it reaches every lecture without `presenter.py` (which re-encodes the video); the file
  presenter.py writes is the same page for offline use (no panel there: it needs /studio-static/).
  **Languages** (2026-10-21, phase 1: management, review, approval; rendering a video in a new language is phase 2).
  `languages.yaml` (+ `languages.py`) lists the course's languages (uz, en, ru, ko, tr, de, fr, es, ar, zh): names, script,
  edge voices (all found in `edge_tts --list-voices` on 2026-10-21), rate / trim (Korean only), section-card word,
  opening chapter title; `common.py` takes VOICES / VOICE_RATES / EDGE_TRIM from it (same values for en, uz, ko, asserted).
  `builds.py` parses and makes build names (`[mK_]lectureNN_<lang>[_<engine>]`); no other file holds the pattern. A
  lecture's narration in language L is `narration/<stem>_<L>.md` (one language, bold, the primary language's line ids)
  if it exists, else the bilingual `<stem>.md` (uz bold, en italic). The primary language is Uzbek for Module 0, English for
  Module 7. **+ add language** on the lecture page writes an empty skeleton (`3a. ⏸ ****`; an empty line is "not
  drafted"); Claude drafts it in a coding session, the instructor approves it line by line at
  `/narration?lecture=<stem>&lang=<code>` (a reference language beside the text, checks shown inline and never blocking:
  Cyrillic in a Latin-script text, Uzbek ʻ/ʼ, Latin words in a Cyrillic text, digits; a Labels tab for the screen words,
  written back through `labels.py` to `labels.yaml` or the lecture's draft labels). Table `line_status` (lecture, lang, line
  or label, hash of the approved text, the other languages' texts at that moment): a line is empty / draft / approved /
  **needs update** ("uz changed", old and new side by side) by comparing hashes, so nothing changes by itself; actions are
  approve, save edit (writes the file through `narration_edit`, approves), still fine. A merged version approves its lines
  (the merge is the approval), which flags the same lines in the other languages. The lecture page groups every language of
  a lecture in one block (narration and label counts, build date, "narration changed since the build" = an approved line the
  video's `lines.json` lacks, sessions, "can be built: no — 34 labels have no Russian form; …"); the editor header links to the
  other languages (their editor if built, else their review) and each open line lists the line in the other languages.
  **Seed:** `python -m studio.languages_seed` approves the Uzbek lines and labels of Module 0 Lectures 1-5 (approved and built,
  above); idempotent, never overwrites a row. Run on `out/studio.sqlite` 2026-10-21: 1,752 rows (lines / labels: L1 212 / 295,
  L2 132 / 183, L3 144 / 162, L4 132 / 170, L5 128 / 194). English (Module 0's gloss, Module 7's draft 2) and Module 7's Uzbek (draft 1) are not approved. Lectures 6-7 are
  "approved as written" above but not built, so not seeded.
  **Languages, phase 2: building a video in any language** (2026-10-21; scope per the instructor: the studio's language
  choice works for any language, no module is translated yet, so no narration or label drafts were written).
  `check_lang.py <lecture> <lang>` (e.g. `m7_lecture01 ru`) is the preflight: font installed (registry `font`, `fc-list`;
  zh = AR PL UMing CN, ar = Noto Naskh Arabic, ko = Noto Serif KR, the Latin / Cyrillic languages use the default font),
  narration lines empty or missing, label keys without the language's form (`labels.keys_for` + the lecture's draft labels
  + `$LABEL_DRAFTS`), `{language: ...}` dicts that are words on screen rather than cues (none exist in Lectures 1-5 / M7 L1
  today: all ~580 are cue phrases, asserted in `test_build_language`), cues that cannot be placed, cue overrides that do not
  match. The lecture page's "can be built" line is its `summary`. **Narration:** `lecture_kit.bind()` merges
  `narration/<stem>_<lang>.md` into the kit's lines by id (`add_language`; a line the file lacks says so when voiced:
  `NoForm`); M7 treats every language but Uzbek as the English-law path (`UK = LANG != "uz"`). **Cues** (`cues.py`, light,
  no manim): English and Uzbek read their own form exactly as before (asserted on every real cue pair of Lectures 1-5 and
  M7 L1); any other language is placed from the line's text in the reference language (the lecture's primary, else
  English, else the first the cue has): same sentence and share of it when both lines have as many sentences, else the same
  share of the whole line; a bare index the line has works as written. `narration/<stem>_<lang>.cues.yaml`
  (`{line: {reference phrase: phrase in lang}}`) overrides; a phrase not in the line fails the render and the preflight.
  `common.by_lang(d, what)` and `forms()` raise `NoForm` naming the language: never another language's words.
  **Voice:** the truncation guard is `languages.min_seconds` (words / 5 by default, characters / 6.5 for zh: edge-tts
  reads Chinese at 4.65 characters a second); edge-tts answering nothing (`NoAudioReceived`, seen for ru) is retried.
  **Watermark:** `drafts.py`: clean when every line and label of the language is approved; else a draft (M7 scenes tag
  themselves with the label `m7_draft`; any other lecture in a language but uz / en gets the registry's `draft` word in the
  corner); a hand render of uz still tags, but the studio's job refuses uz with unapproved items. **Studio:** a language row
  with no video shows "Build video" (or "Build draft video") when `studio/buildlang.plan` says so; it queues one job
  (`kind=build`, shown on the row with the step): `render.sh <lecture> h` with `LANG_CODE` (+ `VOICE_ENGINE=navoiy` for uz,
  starting the voice server like a rewritten line does), `join_parts.sh`, `presenter.py`, then the voice check:
  `voice_check.py` for Uzbek, `voice_check_lang.py <lang> <build>` otherwise (whisper-large-v3-turbo, CER, fails over 0.15,
  same `voice_check.json` rows, so the editor's red / amber marks work). A build with a video is never rebuilt over.
  Smoke build (scratch text, deleted): M7 L1 `S00Opening` in Russian at `-ql` rendered with Cyrillic on screen, the ru edge
  voice (mean -23 dB), the draft tag, the cue on «Мы строим небольшого агента» and CER 0.000 on both clips. Arabic is shaped
  and ordered right to left by Pango; `tagged()` (number and words split by index) and `aligned_edge=LEFT` layouts are not
  mirrored, so an Arabic lecture needs its scenes looked at.
  The page is plain files, no build step: `studio/editor.html` + `studio/static/` (served at /studio-static/;
  `editor/player.js` is a `Player` class that drives any video element and audio map, `editor/levels.js` takes its
  take lookup, edit and play from `LV.host`; the presenter's panel is `presenter/takes.js` + `takes.css`).
  Tests: `studio/run_tests.sh` (220; `fast` skips the server run, the browser run and the GPU recognisers). The browser
  run (`test_presenter_browser.py` → `presenter_browser_check.py`) needs Playwright in the system `python3` (the venv has
  none) and drives headless Chromium with a fake microphone through keys, one-take recording, watching and choosing.

## Slide discrepancies found by the drafts (slides not edited)

Lecture 8: Σx² 35,777.1 vs 35,770.56 from the data. Lecture 9: Fahrenheit covariance 89.3 vs 89.2; the residual
example day (22.4 °C, 28 cups) is not in the data; eigenvector arrows labelled 2√λ but quoted √λ; Anscombe IV's far
point has residual 0. `statistics/main.tex` line 66: stray "m" after the lecture10_evaluation input.
