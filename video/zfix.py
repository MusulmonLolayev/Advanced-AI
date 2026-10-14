"""Reshape the hiss of every word-final «z» that still sounds like «zh» («yuz» -> «yuzsh»), in place.

After revoice.py has tried other takes, a «z» whose hiss is still centred below voice_check.Z_BAD kHz gets its hiss
(only those 10 ms frames, found as voice_check.z_segment finds them) re-weighted: the «sh» band 1.5-4.5 kHz down to
0.35, the «z» band 5-9.5 kHz up 1.8x, with 10 ms crossfades at both ends. Nothing else in the clip changes and its
length stays the same, so the scenes that use a fixed clip only need re-rendering. Instructor, by ear: a partial fix.

    ~/navoiy-stack/CosyVoice/.venv/bin/python zfix.py out/lecture01_uz_navoiy --dry-run   # list what would change
    ~/navoiy-stack/CosyVoice/.venv/bin/python zfix.py out/lecture01_uz_navoiy             # fix; originals in zfixed/
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np

SR = 24000
SH_BAND, SH_GAIN = (1500, 4500), 0.35
Z_BAND, Z_GAIN = (5000, 9500), 1.8
FADE = 0.010


def reshape(x, start, end, sr=SR):
    """x with samples [start, end) re-weighted towards a «z»; outside that range x is returned unchanged."""
    y = np.array(x, dtype=np.float32, copy=True)
    seg = y[start:end]
    n = len(seg)
    if n < 4:
        return y
    S = np.fft.rfft(seg)
    f = np.fft.rfftfreq(n, 1 / sr)
    g = np.ones_like(f)
    g[(f >= SH_BAND[0]) & (f < SH_BAND[1])] = SH_GAIN
    g[(f >= Z_BAND[0]) & (f < Z_BAND[1])] = Z_GAIN
    shaped = np.fft.irfft(S * g, n).astype(np.float32)
    w = min(int(FADE * sr), n // 2)
    mix = np.ones(n, np.float32)
    if w:
        mix[:w] = np.linspace(0, 1, w); mix[-w:] = np.linspace(1, 0, w)
    y[start:end] = seg * (1 - mix) + shaped * mix
    return y


def main(build, dry=False):
    from voice_check import Z_BAD, _load24, clips, z_words
    from revoice import write_mp3
    build = Path(build)
    work = build / "zfixed"
    fixed, scenes, n = [], set(), 0
    for f, text in clips(build).items():
        low = [(w, c, seg) for w, _, c, seg in z_words(f, text) if c < Z_BAD]
        if not low:
            continue
        f = Path(f)
        x = _load24(f)
        y = x
        for _, _, (a, b) in low:
            y = reshape(y, a, b)
        after = [(w, c) for w, _, c, _ in z_words_from(y, f, text)] if not dry else []
        print(f"{'would fix' if dry else 'fixed':9s} {f.parent.name}/{f.name[:44]}  "
              + ", ".join(f"{w} {c:.2f}" for w, c, _ in low) + (f"  ->  {', '.join(f'{w} {c:.2f}' for w, c in after)}"
                                                                if after else ""), flush=True)
        scenes.add(f.parent.name); n += 1
        if dry:
            continue
        work.mkdir(exist_ok=True)
        orig = work / f"{f.parent.name}__{f.name}"
        if not orig.exists():
            shutil.copy2(f, orig)
        write_mp3(f, y)
        fixed.append({"file": str(f), "scene": f.parent.name, "before": [(w, c) for w, c, _ in low], "after": after})
    if not dry:
        log = build / "zfixed.json"
        earlier = json.loads(log.read_text()) if log.exists() else []
        log.write_text(json.dumps(earlier + fixed, ensure_ascii=False, indent=1))
    print(f"{n} clips {'to fix' if dry else 'fixed'}; scenes to re-render:", " ".join(sorted(scenes)))


def z_words_from(y, f, text):
    """The «z» measurements of the reshaped audio (same alignment as the original: lengths are unchanged)."""
    from voice_check import align, z_centre, z_segment
    out = []
    for k, (w, a, b, _) in enumerate(align(f, text)):
        if w.endswith("z"):
            seg = z_segment(y, a, b)
            c = z_centre(y, seg) if seg else None
            if c is not None:
                out.append((w, k, c, seg))
    return out


if __name__ == "__main__":
    main(sys.argv[1], dry="--dry-run" in sys.argv)
