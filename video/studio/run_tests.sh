#!/usr/bin/env bash
# studio/run_tests.sh [fast]   every studio test, from video/. "fast" skips the two that take a minute (the end-to-end
#                              server run, and speech recognition on the GPU).
#   test_timeline     takes, tracks, cuts, squeezes, trims, fit by the margin, nudges, pause proposals, the edit list, subtitles, chapters, script check
#   test_store        a deleted recording's session, edits and derived files are forgotten
#   test_media        pieces joined in order, pauses found, voice levels (and their speed), voice sliced sample-exact, chapter titles
#   test_pages        both pages' JavaScript parses (node --check), the editor's split-out scripts all loaded by the template, levels.js's plan equal to timeline.plan
#   test_narration_edit  a line found and rewritten in its narration file (every line of two built lectures found)
#   test_rewrite      the helpers a rewritten scene needs (render environment, scene of a line, running a tool)
#   test_versions     drafts of a rewritten scene: base choice, draft narration, voice cache, merge order and rollback,
#                     stale, discard; render.sh OUT_DIR and the kits' NARRATION_DIR (outside tools stubbed)
#   test_studio_e2e   the real server on a free port: record over HTTP, retake, crash recovery, edits, export
#   test_words        words_worker.py on a real English and a real Uzbek clip (needs the Navoiy env and GPU)
set -uo pipefail
cd "$(dirname "$0")/.."
TESTS=(test_timeline test_store test_media test_pages test_narration_edit test_rewrite test_versions)
[ "${1:-}" = fast ] || TESTS+=(test_studio_e2e test_words)
fail=0
for t in "${TESTS[@]}"; do
  printf '%-18s ' "$t"
  out=$(.venv/bin/python -m unittest discover -s studio -p "$t.py" -t . 2>&1)
  if [ $? -eq 0 ]; then echo "$out" | grep -E "^(Ran|OK)" | tr '\n' ' '; echo
  else echo "FAILED"; echo "$out" | tail -30; fail=1; fi
done
exit $fail
