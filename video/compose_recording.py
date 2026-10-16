"""Turn a presenter recording into a video: the original 1080p picture, re-timed around the instructor's own voice.

presenter.html (key R) saves <name>.webm (the microphone) and <name>.json (each moment the picture started or held,
as [seconds since recording began, "play"|"hold"|"stop", video position, playback speed]). Between a "play" at
position p and the next event at position q the picture plays p..q, slowed or sped up to the speed it was presented
at (older recordings have no speed: 1); while it holds, the frame at that position stays on screen until the
next event. If the video stalled while playing, the last frame holds for the difference, so the voice never drifts.
The voice is cleaned with one of the instructor's profiles from ~/teaching/clean_video.sh (low cut, FFT noise
reduction, compressor, EQ; "off" for none), or with "deepfilter" (the default): the DeepFilterNet 3 neural
denoiser (bin/deep-filter, the v0.5.6 release binary, sha256 70775e25…; runs on the CPU, ~6x real time) limited to
30 dB of reduction so a faint room tone stays, then the "voice" profile's compressor and EQ. On 60 s of the
instructor's classroom recording DNSMOS rated it 3.11 overall against 2.61 for "voice" and 1.99 raw; on their
first studio recording 3.16 against 2.17 and 1.78. Then levelled to the narration's loudness
(-19 LUFS) by one fixed gain: the cleaned voice is measured first, then raised or lowered by the difference, and a
limiter catches only the short peaks. (loudnorm's one-pass dynamic mode raised the gain in every pause, lifting the
room noise by up to 26 dB; its linear mode falls back to dynamic whenever the gain would push a peak past the
limit, which a quiet microphone always does.) The picture is encoded with that script's NVENC settings on the GPU, or with libx264 when NVENC is not
available.

    uv run python compose_recording.py out/lecture01_uz_navoiy 2026-10-14T13-40-00 [deepfilter|voice|mild|strong|off]
    # -> out/lecture01_uz_navoiy/presenter/recordings/2026-10-14T13-40-00.mp4
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

FPS = 60
NVENC = ["-c:v", "h264_nvenc", "-preset", "p1", "-cq", "30", "-b:v", "0"]          # as in clean_video.sh
X264 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18"]
# the voice-cleaning chains of ~/teaching/clean_video.sh, verbatim
CLEAN = {
    "mild": "highpass=f=80,afftdn=nr=10:nf=-28:tn=1,"
            "acompressor=threshold=0.12:ratio=2.2:attack=20:release=250:makeup=1,"
            "equalizer=f=120:t=h:width=200:g=-2,equalizer=f=2500:t=q:w=1.2:g=2,"
            "equalizer=f=9000:t=h:width=3000:g=1.5,volume=1.5dB",
    "strong": "highpass=f=100,afftdn=nr=14:nf=-32:tn=1,"
              "acompressor=threshold=0.10:ratio=2.8:attack=15:release=220:makeup=1,"
              "equalizer=f=140:t=h:width=220:g=-3,equalizer=f=3000:t=q:w=1.0:g=2.5,"
              "equalizer=f=8500:t=h:width=2800:g=2,volume=2dB",
    "voice": "highpass=f=90,afftdn=nr=12:nf=-30:tn=1,"
             "acompressor=threshold=0.11:ratio=2.5:attack=18:release=240:makeup=1,"
             "equalizer=f=180:t=q:w=1.0:g=-2,equalizer=f=2800:t=q:w=1.1:g=3,"
             "equalizer=f=10000:t=h:width=3500:g=2,volume=1.8dB",
    "off": "highpass=f=80",
    # after DeepFilterNet: the "voice" chain without its FFT denoiser
    "deepfilter": "highpass=f=90,acompressor=threshold=0.11:ratio=2.5:attack=18:release=240:makeup=1,"
                  "equalizer=f=180:t=q:w=1.0:g=-2,equalizer=f=2800:t=q:w=1.1:g=3,"
                  "equalizer=f=10000:t=h:width=3500:g=2",
}
DEEP_FILTER = Path(__file__).parent / "bin" / "deep-filter"
DF_LIMIT = 30                                   # dB: at most this much reduction, so the pauses are not dead silent


def deepfilter(webm, tmp):
    """The voice through DeepFilterNet, as a 48 kHz wav on the recording's own clock (-D: no added delay)."""
    if not DEEP_FILTER.exists():
        sys.exit(f"{DEEP_FILTER} is missing: download deep-filter-0.5.6-x86_64-unknown-linux-musl from "
                 "github.com/Rikorose/DeepFilterNet/releases and chmod +x it")
    wav = tmp / "voice.wav"
    ff("-i", webm, "-af", "aresample=async=1:first_pts=0", "-ac", "1", "-ar", "48000", wav)
    subprocess.run([str(DEEP_FILTER), "-D", "-a", str(DF_LIMIT), "-o", str(tmp / "df"), str(wav)],
                   check=True, capture_output=True)
    return tmp / "df" / "voice.wav"
TARGET = -19                                   # LUFS, the narration's loudness
PEAK = 10 ** (-2.5 / 20)                        # the limiter's ceiling, -2.5 dBFS (about -2 dB true peak)


def level(voice, chain):
    """One fixed gain to TARGET (measured on the cleaned voice), then a limiter for the peaks it pushes too high."""
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(voice), "-vn", "-af",
                        f"{chain},loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True,
                       check=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    gain = TARGET - float(m["input_i"])
    return f"volume={gain:.2f}dB,alimiter=limit={PEAK:.4f}:level=false:latency=true"


def video_encoder():
    """NVENC if the GPU can encode right now (a one-frame test), else libx264."""
    test = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "color=s=256x256:d=0.1",
                           "-frames:v", "1", *NVENC, "-f", "null", "-"], capture_output=True)
    return (NVENC if test.returncode == 0 else X264) + ["-pix_fmt", "yuv420p", "-r", str(FPS)]


def ff(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *map(str, args)], check=True)


def segments(events):
    """[(kind, start position, end position or None, seconds, speed)]: 'play' runs the picture, 'hold' freezes a frame."""
    out = []
    for (t, kind, pos, *r), (t2, _, pos2, *_) in zip(events, events[1:]):
        span, speed = t2 - t, (r[0] if r else 1)
        if span <= 0.02:
            continue
        if kind == "play" and pos2 > pos:
            run = min(pos2 - pos, span * speed)                    # video seconds shown in this span
            out.append(("play", pos, pos + run, run / speed, speed))
            if span - run / speed > 0.02:
                out.append(("hold", pos + run, None, span - run / speed, 1))
        else:
            out.append(("hold", pos, None, span, 1))
    return out


def main(build, name, clean="deepfilter"):
    if clean not in CLEAN:
        sys.exit(f"unknown cleaning profile {clean!r}: use one of {', '.join(CLEAN)}")
    ENC = video_encoder()
    build = Path(build)
    rec = build / "presenter" / "recordings"
    events = json.loads((rec / f"{name}.json").read_text())
    if events[-1][1] != "stop":                                # the page logs stop just before saving
        events.append([events[-1][0], "stop", events[-1][2], 1])
    src = build / "presenter" / f"{build.name}_silent.mp4"
    segs = segments(sorted(events))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        files = []
        for k, (kind, a, b, dur, speed) in enumerate(segs):
            f = tmp / f"{k:05d}.mp4"
            if kind == "play":
                ff("-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", src, "-an", "-vf", f"setpts=PTS/{speed:.6f}", *ENC, f)
            else:
                png = tmp / f"{k:05d}.png"
                ff("-ss", f"{max(a - 0.02, 0):.3f}", "-i", src, "-frames:v", "1", png)
                ff("-loop", "1", "-i", png, "-t", f"{dur:.3f}", *ENC, f)
            files.append(f)
        (tmp / "list.txt").write_text("".join(f"file '{f}'\n" for f in files))
        ff("-f", "concat", "-safe", "0", "-i", tmp / "list.txt", "-c", "copy", tmp / "picture.mp4")
        out = rec / f"{name}.mp4"
        if clean == "deepfilter":
            voice, chain = deepfilter(rec / f"{name}.webm", tmp), CLEAN[clean]
        else:
            voice, chain = rec / f"{name}.webm", f"aresample=async=1:first_pts=0,{CLEAN[clean]}"
        ff("-i", tmp / "picture.mp4", "-i", voice, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-af", f"{chain},{level(voice, chain)}", "-shortest", out)
    total = sum(s[3] for s in segs)
    print(f"{len(segs)} segments, {total / 60:.1f} min, voice {clean}, {ENC[1]} -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
