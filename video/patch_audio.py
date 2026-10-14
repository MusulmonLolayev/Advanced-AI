"""Mute sound that sits in a pause between words, in the voice clips and in the finished video, without re-rendering.

The cloned voice sometimes fills the pause between two sentences with a steady buzz (Lecture 1, 19:06: 0.9 s at
-20 dB after «…topamiz.», before «Kyu uchga…»). It is not a word, so it needs no new take: forced alignment says where
the words are, and a loud stretch between two words is muted with short fades. The same window is muted in the
built video's audio track (the picture is copied as is), at the clip's place found by cross-correlation.

    PY=~/navoiy-stack/CosyVoice/.venv/bin/python
    $PY patch_audio.py at   out/lecture01_uz_navoiy 19:07 [more times]   # mute the noisy pause at a reported time
    $PY patch_audio.py scan out/lecture01_uz_navoiy            # candidates to listen to (writes gaps.json)

`at` touches only a pause between two aligned words, in the clip and in the video; noise inside a word is reported,
not muted (that needs a new take of the sentence). `scan` is only a listening list: a held vowel the aligner squeezed
looks like sound in a pause too (Lecture 1 had 22 such candidates beside the real one), so nothing is muted unheard.

Originals are kept: clips as <build>/patched/<Scene>__<file>, the video as <build>/<name>.before_patch.mp4.
"""
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np

GAP_MIN = 0.30      # a pause between words at least this long is checked
EDGE = 0.06         # leave this much of the pause next to each word untouched
LOUD_DB = -40       # a 50 ms frame louder than this inside a pause is sound, not quiet
LOUD_MIN = 0.20     # this much loud sound inside one pause is muted
FADE = 0.02


def load(path, sr=16000, ss=None, t=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(ss), "-t", str(t)] if ss is not None else []) + \
          ["-i", str(path), "-af", "aresample=async=1:first_pts=0", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


def word_spans(path, text):
    """[(word, start s, end s)] by MMS forced alignment."""
    import torch
    import torchaudio
    import torchaudio.functional as F
    from voice_check import _M
    if "mms" not in _M:
        b = torchaudio.pipelines.MMS_FA
        _M["mms"] = (b.get_model(with_star=False).to("cuda"), b.get_dict(star=None))
    model, d = _M["mms"]
    t = re.sub(r"[ʻʼ'`’‘]", "'", unicodedata.normalize("NFKC", re.sub(r"<[^>]+>", "", text).lower()))
    ws = [w for w in (re.sub(r"[^a-z']", "", w) for w in re.sub(r"[^\w']+", " ", t).split()) if w.strip("'")]
    x = torch.from_numpy(load(path))[None].to("cuda")
    with torch.inference_mode():
        em = torch.log_softmax(model(x)[0], dim=-1)
    ali, sc = F.forced_align(em, torch.tensor([[d[c] for w in ws for c in w]], dtype=torch.int32, device="cuda"), blank=0)
    spans, sec, out, i = F.merge_tokens(ali[0], sc[0].exp()), x.shape[1] / em.shape[1] / 16000, [], 0
    for w in ws:
        sp = spans[i:i + len(w)]; i += len(w)
        out.append((w, sp[0].start * sec, sp[-1].end * sec))
    return out


def noisy_gaps(path, text, spans=None):
    """[(start, end, peak dB, word before, word after)] inside pauses between words where there is sound."""
    x, hop = load(path), 800
    db = 20 * np.log10(np.sqrt(np.add.reduceat(x ** 2, np.arange(0, len(x), hop)) / hop) + 1e-9)
    spans, out = spans or word_spans(path, text), []
    for (w0, _, a), (w1, b, _) in zip(spans, spans[1:]):
        if b - a < GAP_MIN:
            continue
        lo, hi = a + EDGE, b - EDGE
        loud = [k for k in range(int(lo * 20), int(hi * 20)) if k < len(db) and db[k] > LOUD_DB]
        if len(loud) / 20 >= LOUD_MIN:
            out.append((round(lo, 2), round(hi, 2), round(float(db[loud].max()), 1), w0, w1))
    return out


def envelope(n, sr, segs):
    """Gain 1 everywhere except 0 inside each (start, end), with FADE ramps."""
    g, f = np.ones(n, np.float32), int(FADE * sr)
    for a, b in segs:
        i, j = int(a * sr), min(n, int(b * sr))
        if j - i <= 2 * f:
            continue
        g[i:j] = 0
        g[i:i + f] = np.linspace(1, 0, f); g[j - f:j] = np.linspace(0, 1, f)
    return g


def mute_clip(path, segs, backup):
    if not backup.exists():
        shutil.copy2(path, backup)
    x = load(path, 24000)
    y = (x * envelope(len(x), 24000, segs) * 32767).astype(np.int16)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "-", "-b:a", "128k",
                    str(path)], input=y.tobytes(), check=True)


def clip_offsets(build, clip_paths):
    """Where each clip starts in the finished video: its scene's start + its subtitle cue, refined by correlation."""
    from listen_list import duration, norm, srt_starts
    texts = {str(k): v for k, v in clips_text(build).items()}
    parts = [Path(r.split("'")[1]) for r in (build / "parts.txt").read_text().splitlines() if r.startswith("file")]
    start, off = {}, 0.0
    for p in parts:
        start[p.stem] = (off, p); off += duration(p)
    video, out = build / f"{build.name}.mp4", {}
    for f in clip_paths:
        if Path(f).parent.name not in start:
            continue                                   # a stale clip no scene uses any more
        s0, mp4 = start[Path(f).parent.name]
        head = norm(texts[str(f)])[:4]
        cue = next((s0 + ts for ts, ws in srt_starts(mp4.with_suffix(".srt")) if ws[:len(head)] == head), None)
        lo, span = (max(0, cue - 1), 4.5) if cue is not None else (s0, duration(mp4))
        c, v = load(f)[:3 * 16000], load(video, 16000, lo, span)
        k = xcorr_at(c, v)
        seg = v[k:k + len(c)]
        if float(np.dot(seg, c)) / (np.linalg.norm(seg) * np.linalg.norm(c) + 1e-9) > 0.9:
            out[str(f)] = lo + k / 16000                # else an older take of the line, not in this video
    return out


def xcorr_at(c, v):
    """Sample offset in v where c fits best (FFT cross-correlation)."""
    n = 1 << int(np.ceil(np.log2(len(v) + len(c))))
    r = np.fft.irfft(np.fft.rfft(v, n) * np.conj(np.fft.rfft(c, n)), n)[:len(v) - len(c) + 1]
    return int(np.argmax(r))


def clips_text(build):
    from voice_check import clips
    return clips(build)


def patch_video(build, windows):
    """Mute [(start, end)] seconds in the finished video's audio; the picture is copied."""
    video = build / f"{build.name}.mp4"
    before = build / f"{build.name}.before_patch.mp4"
    if not before.exists():
        shutil.copy2(video, before)
    sr = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate",
                             "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip())
    # aresample async fills holes in the audio timestamps with silence; without it the decoded track is shorter
    # than the picture and everything after a hole slides earlier (Lecture 1 drifted 46 s this way)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-af", "aresample=async=1:first_pts=0",
                          "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    x *= envelope(len(x), sr, windows)[:, None]
    tmp = build / "patched_audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "2", "-i", "-", str(tmp)],
                   input=x.tobytes(), check=True)
    out = build / "patched.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(tmp), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(out)], check=True)
    out.replace(video); tmp.unlink()


def stamp(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def secs(s):
    m, _, x = s.rpartition(":")
    return int(m or 0) * 60 + float(x)


def main(cmd, build, *times):
    build = Path(build)
    from listen_list import duration
    texts = clips_text(build)
    if cmd == "scan":
        found = {f: g for f, t in texts.items() if (g := noisy_gaps(f, t))}
        offs = clip_offsets(build, list(found))
        found = {f: g for f, g in found.items() if f in offs}
        (build / "gaps.json").write_text(json.dumps(found, ensure_ascii=False, indent=1))
        for f, g in sorted(found.items(), key=lambda kv: offs[kv[0]]):
            print(f"{Path(f).parent.name:16s} " + ", ".join(
                f"{stamp(offs[f] + a)}-{stamp(offs[f] + b)} ({db} dB, «{w0} … {w1}»)" for a, b, db, w0, w1 in g))
        print(f"{sum(map(len, found.values()))} candidates in {len(found)} clips — listen before muting any")
        return
    parts = [Path(r.split("'")[1]) for r in (build / "parts.txt").read_text().splitlines() if r.startswith("file")]
    windows, work = [], build / "patched"
    work.mkdir(exist_ok=True)
    for tt in times:
        T, off = secs(tt), 0.0
        for p in parts:                                # the scene playing at T
            if off + duration(p) > T:
                break
            off += duration(p)
        cand = [f for f in texts if Path(f).parent.name == p.stem]
        offs = clip_offsets(build, cand)
        f = next((f for f in offs if offs[f] <= T <= offs[f] + duration(f)), None)
        if f is None:
            print(f"{tt}: no voice clip plays here ({p.stem})"); continue
        g = [x for x in noisy_gaps(f, texts[f]) if offs[f] + x[0] - 1.0 <= T <= offs[f] + x[1] + 1.0]
        if not g:
            print(f"{tt}: {p.stem}, «{texts[f][:50]}…» — no sound in a pause near here; the noise is inside a word, "
                  "so that sentence needs a new take"); continue
        mute_clip(Path(f), [(a, b) for a, b, *_ in g], work / f"{Path(f).parent.name}__{Path(f).name}")
        for a, b, db, w0, w1 in g:
            windows.append((offs[f] + a, offs[f] + b))
            print(f"{tt}: muted {stamp(offs[f] + a)}-{stamp(offs[f] + b)} ({b - a:.1f} s, peak {db} dB) between "
                  f"«{w0}» and «{w1}» in {p.stem}")
    if windows:
        patch_video(build, windows)
        print(f"patched {build.name}.mp4 (picture copied; the original is {build.name}.before_patch.mp4)")


if __name__ == "__main__":
    main(*sys.argv[1:])
