#!/usr/bin/env bash
# studio/run_tests.sh [fast]   every studio test, from video/. "fast" skips the three that take a minute (the end-to-end
#                              server run, the browser run, and speech recognition on the GPU).
#   test_timeline     takes, tracks, cuts, squeezes, trims, fit by the margin, nudges, pause proposals, the edit list, subtitles, chapters, script check
#   test_store        a deleted recording's session, edits and derived files are forgotten
#   test_media        pieces joined in order, pauses found, voice levels (and their speed), voice sliced sample-exact, chapter titles
#   test_pages        the offline presenter page's JavaScript parses (node --check) and names no studio file
#   test_narration_edit  a line found and rewritten in its narration file (every line of two built lectures found)
#   test_rewrite      the helpers a rewritten scene needs (render environment, scene of a line, running a tool)
#   test_versions     drafts of a rewritten scene: base choice, draft narration, voice cache, merge order and rollback,
#                     stale, discard; render.sh OUT_DIR and the kits' NARRATION_DIR (outside tools stubbed)
#   test_languages   the language registry (voices as the renders use them), build names, narration per language and its empty
#                     skeleton, line and label status (empty / draft / approved / needs update), the seed, the review actions and
#                     payload, the language rows, the project browser's lecture list (R.lecture_list), the editor's language data
#   test_cues         cue timing in every language: English and Uzbek give the old seconds on every real (line, cue) pair of the
#                     scene files; other languages are placed by sentence and share, overrides win, a bad one fails; label and
#                     per-language dict errors name the language
#   test_build_language  building a language (phase 2): a single-language narration merged by line id, check_lang's preflight on a
#                     fake lecture, the registry's fonts and truncation guard, the draft watermark (Uzbek strict), the build job's
#                     steps with the tools stubbed, the build request's refusal
#   test_studio_e2e   the real server on a free port: record over HTTP, retake, crash recovery, edits, export
#   test_routes       the front door on a free port: / is the React app (no-cache, hashed assets cached), every old page's address
#                     (/?m=N, /lecture, /edit, /watch, /narration, <build>/presenter/presenter.html) answers 302 with the app's deep
#                     link, /api/lectures lists the project browser's modules, lectures and languages
#   test_app_browser  (full run) the React app in headless Chromium with a fake microphone, on a scratch server built from fixtures:
#                     Edit (play, trim, margin, delete), Record (an L take and a session over HTTP, meter, event shapes), Script
#                     (approve, save, still fine, the Uzbek rule), Export; skipped without Playwright
#   app (react)      (runs first) studio/app: npm run typecheck (tsc --noEmit), npm run build -> static/app/, npm run check (the Export
#                     summary equals the counts the server's fields give)
#   test_words        words_worker.py on a real English and a real Uzbek clip (needs the Navoiy env and GPU)
set -uo pipefail
cd "$(dirname "$0")/.."
TESTS=(test_timeline test_store test_media test_pages test_narration_edit test_rewrite test_versions test_languages test_cues test_build_language test_routes)
[ "${1:-}" = fast ] || TESTS+=(test_studio_e2e test_app_browser test_words)
fail=0
# the app is built first: test_app_browser serves the build (static/app/)
printf '%-18s ' "app (react)"
if [ -d studio/app/node_modules ] || (cd studio/app && npm ci --silent >/dev/null 2>&1); then
  out=$(cd studio/app && npm run typecheck 2>&1 && npm run build 2>&1 && npm run check 2>&1)
  if [ $? -eq 0 ]; then echo "typecheck + build + export numbers check OK"; else echo "FAILED"; echo "$out" | tail -30; fail=1; fi
else echo "FAILED (npm ci)"; fail=1; fi
for t in "${TESTS[@]}"; do
  printf '%-18s ' "$t"
  out=$(.venv/bin/python -m unittest discover -s studio -p "$t.py" -t . 2>&1)
  if [ $? -eq 0 ]; then echo "$out" | grep -E "^(Ran|OK)" | tr '\n' ' '; echo
  else echo "FAILED"; echo "$out" | tail -30; fail=1; fi
done
exit $fail
