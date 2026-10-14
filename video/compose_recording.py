"""Turn a presenter recording into a video: the original 1080p picture, re-timed around the instructor's own voice.

presenter.html (key R) saves <name>.webm (the microphone) and <name>.json (each moment the picture started or held,
as [seconds since recording began, "play"|"hold"|"stop", video position]). Between a "play" at position p and the
next event at position q the picture plays p..q; while it holds, the frame at that position stays on screen until the
next event. If the video stalled while playing, the last frame holds for the difference, so the voice never drifts.
The voice is levelled to the narration's loudness (-19 LUFS) with an 80 Hz low cut against mic rumble.

    uv run python compose_recording.py out/lecture01_uz_navoiy 2026-10-14T13-40-00
    # -> out/lecture01_uz_navoiy/presenter/recordings/2026-10-14T13-40-00.mp4
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

FPS = 60
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def ff(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *map(str, args)], check=True)


def segments(events):
    """[(kind, start position, end position or None, seconds)]: 'play' runs the picture, 'hold' freezes a frame."""
    out = []
    for (t, kind, pos), (t2, _, pos2) in zip(events, events[1:]):
        span = t2 - t
        if span <= 0.02:
            continue
        if kind == "play" and pos2 > pos:
            run = min(pos2 - pos, span)
            out.append(("play", pos, pos + run, run))
            if span - run > 0.02:
                out.append(("hold", pos + run, None, span - run))
        else:
            out.append(("hold", pos, None, span))
    return out


def main(build, name):
    build = Path(build)
    rec = build / "presenter" / "recordings"
    events = json.loads((rec / f"{name}.json").read_text())
    if events[-1][1] != "stop":                                # the page logs stop just before saving
        events.append([events[-1][0], "stop", events[-1][2]])
    src = build / "presenter" / f"{build.name}_silent.mp4"
    segs = segments(sorted(events))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        files = []
        for k, (kind, a, b, dur) in enumerate(segs):
            f = tmp / f"{k:05d}.mp4"
            if kind == "play":
                ff("-ss", f"{a:.3f}", "-i", src, "-t", f"{b - a:.3f}", "-an", *ENC, f)
            else:
                png = tmp / f"{k:05d}.png"
                ff("-ss", f"{max(a - 0.02, 0):.3f}", "-i", src, "-frames:v", "1", png)
                ff("-loop", "1", "-i", png, "-t", f"{dur:.3f}", *ENC, f)
            files.append(f)
        (tmp / "list.txt").write_text("".join(f"file '{f}'\n" for f in files))
        ff("-f", "concat", "-safe", "0", "-i", tmp / "list.txt", "-c", "copy", tmp / "picture.mp4")
        out = rec / f"{name}.mp4"
        ff("-i", tmp / "picture.mp4", "-i", rec / f"{name}.webm", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-af", "aresample=async=1:first_pts=0,highpass=f=80,loudnorm=I=-19:TP=-2:LRA=11", "-shortest", out)
    total = sum(s[3] for s in segs)
    print(f"{len(segs)} segments, {total / 60:.1f} min -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
