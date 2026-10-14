#!/usr/bin/env bash
# join_parts.sh <out_dir> <final.mp4>   joins the scenes listed in <out_dir>/parts.txt into one video.
#
# A manim scene's audio stops with its last voice clip, ~0.6 s before the picture ends (the fade-out).
# A plain `concat -c copy` then leaves a hole in the audio timestamps at every join, and players
# resynchronise there by dropping the frames before the hole: the last syllable of a scene sounds cut off
# (agent course, 3:21). So each scene's audio is first padded with silence to its picture's length
# (audio re-encoded, picture copied; cached in <out_dir>/joined/), and the padded scenes are joined.
# parts.txt keeps pointing at the scene files themselves (listen_list.py reads their subtitles).
set -euo pipefail
OUT="$1"; FINAL="$2"
mkdir -p "$OUT/joined"
: > "$OUT/joined.txt"
while IFS= read -r row; do
  [[ "$row" == file* ]] || continue
  src="${row#file \'}"; src="${src%\'}"
  dst="$PWD/$OUT/joined/$(basename "$src")"
  if [ ! -f "$dst" ] || [ "$src" -nt "$dst" ]; then
    dur=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$src")
    ffmpeg -nostdin -v error -y -i "$src" -map 0:v -map 0:a -c:v copy -af apad -t "$dur" \
           -c:a aac -b:a 192k -ar 48000 -ac 2 "$dst"
  fi
  printf "file '%s'\n" "$dst" >> "$OUT/joined.txt"
done < "$OUT/parts.txt"
ffmpeg -nostdin -v error -y -f concat -safe 0 -i "$OUT/joined.txt" -c copy "$FINAL"
