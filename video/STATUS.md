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
- Recording studio: `nohup .venv/bin/python serve_presenter.py 8080 > out/serve_presenter.log 2>&1 & echo $! >
  out/serve_presenter.pid` (stop with `kill $(cat out/serve_presenter.pid)`); reach it with `ssh -L 8081:localhost:8080
  hometqqt` → http://localhost:8081/ (the instructor's laptop has its own 8080 taken). Presenter keys: Space pause /
  play, → next line, ← back, N notes below / right / off (words light up at the narration's pace), M microphone, R record;
  the video plays at 1/1.1 speed (logged per recording, the build slows the picture to match). Build cleans the voice: `deepfilter` (default; DeepFilterNet binary in `bin/`, git-ignored, from the
  v0.5.6 release) or the profiles of `~/teaching/clean_video.sh` (voice / mild / strong / off), then one fixed gain
  to −19 LUFS + a peak limiter, picture via NVENC. DNSMOS on the instructor's first recording: raw 1.78, voice 2.17,
  deepfilter 3.16. Listening samples: `out/denoise_compare/` (served at /denoise_compare/). The studio page is split by module (a
  panel on the left, `/?m=7`): Module K's lectures are builds `mK_lectureNN_uz_navoiy` (Module 0: `lectureNN_uz_navoiy`),
  its files whatever is linked into `out/shared/mK/` (e.g. `m7/Module7_Lecture01.pdf` → `agents/lecture01.pdf`).

## Slide discrepancies found by the drafts (slides not edited)

Lecture 8: Σx² 35,777.1 vs 35,770.56 from the data. Lecture 9: Fahrenheit covariance 89.3 vs 89.2; the residual
example day (22.4 °C, 28 cups) is not in the data; eigenvector arrows labelled 2√λ but quoted √λ; Anscombe IV's far
point has residual 0. `statistics/main.tex` line 66: stray "m" after the lecture10_evaluation input.
