#!/usr/bin/env python3
"""Flag frames whose content touches the frame border.

Samples at 4 fps, downscales to 640 px wide, and reports any frame with pixels
brighter than THRESH within MARGIN px of an edge. Catches layouts that exist
for only a few frames, which spot-checking misses.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

FPS, W, MARGIN, THRESH = 4, 640, 4, 70


def frames(path):
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=height,width", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip().split(",")
    w0, h0 = int(probe[0]), int(probe[1])
    h = int(round(W * h0 / w0 / 2)) * 2
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps={FPS},scale={W}:{h}",
         "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(out, np.uint8).reshape(-1, h, W)


def main(paths):
    bad = False
    for p in paths:
        arr = frames(p)
        hits = []
        for i, f in enumerate(arr):
            sides = []
            if (f[:, :MARGIN] > THRESH).any(): sides.append("L")
            if (f[:, -MARGIN:] > THRESH).any(): sides.append("R")
            if (f[:MARGIN, :] > THRESH).any(): sides.append("T")
            if (f[-MARGIN:, :] > THRESH).any(): sides.append("B")
            if sides:
                hits.append((i / FPS, "".join(sides)))
        # merge consecutive hits into ranges
        merged = []
        for t, s in hits:
            if merged and s == merged[-1][2] and t - merged[-1][1] <= 1.0 / FPS + 1e-6:
                merged[-1][1] = t
            else:
                merged.append([t, t, s])
        for a, b, s in merged:
            bad = True
            print(f"EDGE {Path(p).name} {int(a//60)}:{a%60:04.1f}-{int(b//60)}:{b%60:04.1f} {s}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
