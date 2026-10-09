#!/usr/bin/env bash
# render.sh <video_module> [l|m|h|k]   e.g. ./render.sh v01_mean h
set -uo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"
VIDEO="${1:?usage: render.sh <video_module> [quality]}"
Q="${2:-h}"
SUFFIX="${LANG_CODE:+_$LANG_CODE}${VOICE_ENGINE:+_$VOICE_ENGINE}"
OUT="out/$VIDEO$SUFFIX"; LOG="$OUT/render.log"
mkdir -p "$OUT"; : > "$LOG"

mapfile -t SCENES < <(uv run python -c "
import importlib; m = importlib.import_module('$VIDEO')
print('\n'.join(m.SCENES))" 2>/dev/null | grep -E '^[A-Za-z_][A-Za-z0-9_]*$')
[ ${#SCENES[@]} -gt 0 ] || { echo "FAILED: no SCENES in $VIDEO"; exit 1; }

PARTS=()
for S in "${SCENES[@]}"; do
  echo "--- $S ---" | tee -a "$LOG"
  if ! uv run manim -q"$Q" --media_dir "$OUT/media" "$VIDEO.py" "$S" 2>&1 | tee -a "$LOG"; then
    echo "FAILED: scene $S"; exit 1
  fi
  F=$(find "$OUT/media/videos" -name "$S.mp4" -print -quit)
  [ -n "$F" ] || { echo "FAILED: no output for $S"; exit 1; }
  PARTS+=("$F")
done

N=$(grep -c "TERMINAL SCROLLED" "$LOG" || true)
[ "$N" -gt 0 ] && echo "SCROLLED: $N terminal scroll(s) — earlier lines were dropped"

printf "file '%s'\n" "${PARTS[@]/#/$PWD/}" > "$OUT/parts.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$OUT/parts.txt" -c copy "$OUT/$VIDEO$SUFFIX.mp4" || { echo "FAILED: concat"; exit 1; }

uv run python check_edges.py "$OUT/$VIDEO$SUFFIX.mp4"
echo "OK  $OUT/$VIDEO$SUFFIX.mp4  ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$VIDEO$SUFFIX.mp4" | cut -d. -f1)s)"
