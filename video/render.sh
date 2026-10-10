#!/usr/bin/env bash
# render.sh <video_module> [l|m|h|k]   e.g. ./render.sh lecture01 h
#   JOBS=8 ./render.sh ...        render scenes in parallel (default 1; keep <=4 with VOICE_ENGINE=navoiy,
#                                 whose server takes one request at a time)
#   ONLY="S03Histogram" ./render.sh ...   render just these scenes; no concat
set -uo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"
VIDEO="${1:?usage: render.sh <video_module> [quality]}"
Q="${2:-h}"
JOBS="${JOBS:-1}"
SUFFIX="${LANG_CODE:+_$LANG_CODE}${VOICE_ENGINE:+_$VOICE_ENGINE}"
OUT="out/$VIDEO$SUFFIX"; LOG="$OUT/render.log"
# Each quality renders into its own folder; take the scene from this one only,
# or a stale render at another quality gets concatenated instead.
case "$Q" in l) RES=480p15;; m) RES=720p30;; h) RES=1080p60;; k) RES=2160p60;;
  *) echo "FAILED: unknown quality $Q"; exit 1;; esac
mkdir -p "$OUT/logs"; : > "$LOG"; touch "$OUT/render.log.start"

mapfile -t SCENES < <(uv run --frozen python -c "
import importlib; m = importlib.import_module('$VIDEO')
print('\n'.join(m.SCENES))" 2>/dev/null | grep -E '^[A-Za-z_][A-Za-z0-9_]*$')
[ ${#SCENES[@]} -gt 0 ] || { echo "FAILED: no SCENES in $VIDEO"; exit 1; }
[ -n "${ONLY:-}" ] && read -ra SCENES <<< "$ONLY"

render_one() {
  local S=$1 F="$OUT/media/videos/$VIDEO/$RES/$1.mp4" try
  # retries: parallel renders can race on manim's shared Tex/text caches (a rerun reads the finished file)
  for try in 1 2 3; do
    if uv run --frozen manim -q"$Q" --media_dir "$OUT/media" "$VIDEO.py" "$S" > "$OUT/logs/$S.log" 2>&1 \
       && [ -f "$F" ] && [ "$F" -nt "$OUT/render.log.start" ]; then
      echo "done $S"; return 0
    fi
  done
  echo "FAILED: scene $S (see $OUT/logs/$S.log)"; return 1
}
export -f render_one; export Q OUT VIDEO RES
printf '%s\n' "${SCENES[@]}" | xargs -P "$JOBS" -I{} bash -c 'render_one "$1"' _ {} | tee -a "$LOG"
grep -q "^FAILED" "$LOG" && { tail -30 "$OUT/logs/$(grep -m1 '^FAILED' "$LOG" | sed 's/FAILED: scene \([^ ]*\).*/\1/').log"; exit 1; }
for S in "${SCENES[@]}"; do cat "$OUT/logs/$S.log" >> "$LOG"; done

N=$(grep -c "TERMINAL SCROLLED" "$LOG" || true)
[ "$N" -gt 0 ] && echo "SCROLLED: $N terminal scroll(s) — earlier lines were dropped"
[ -n "${ONLY:-}" ] && { echo "OK  rendered: ${SCENES[*]}"; exit 0; }

PARTS=()
for S in "${SCENES[@]}"; do PARTS+=("$OUT/media/videos/$VIDEO/$RES/$S.mp4"); done
printf "file '%s'\n" "${PARTS[@]/#/$PWD/}" > "$OUT/parts.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$OUT/parts.txt" -c copy "$OUT/$VIDEO$SUFFIX.mp4" || { echo "FAILED: concat"; exit 1; }

uv run --frozen python check_edges.py "$OUT/$VIDEO$SUFFIX.mp4"
echo "OK  $OUT/$VIDEO$SUFFIX.mp4  ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$VIDEO$SUFFIX.mp4" | cut -d. -f1)s)"
