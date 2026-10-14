"""Re-voice the clips voice_check.py failed, sentence by sentence, and keep whichever version says the text.

Each sentence is voiced with the server's usual seed first; if both recognisers still miss words, it
is voiced again with other seeds and the best-heard take is kept. The pieces are joined with a 0.2 s
breath (as NavoiyService does for a line that stops early), the whole clip is checked again, and it
replaces the cached file in place only if it scores better than the old one. The old clip is kept
in <build>/revoiced/. The scenes that use a replaced clip must be re-rendered.

A clip that fails only on «z» (a word-final «z» heard as «zh»: «yuz» -> «yuzsh») keeps its other sentences as they
are: only the sentences holding a low «z» are voiced again, and the take whose lowest «z» is highest among those
that pass every other check replaces that sentence in the original audio. What stays low after this is for
zfix.py, which reshapes the hiss in place.

    ~/navoiy-stack/CosyVoice/.venv/bin/python revoice.py out/lecture03_uz_navoiy
    SEEDS=5,11,99,777,4096,65537 ...revoice.py ...     # second pass on what still fails, with new seeds
"""
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np

from audio_fx import cap_pauses, trim_silence
from voice_check import MODELS, Z_BAD, Z_LISTEN, _load24, align, judge

URL = "http://127.0.0.1:8765/tts"
SEEDS = tuple(int(x) for x in os.environ.get("SEEDS", "1986,7,42,123,2024,31337").split(","))   # a second pass: other seeds
SENT = r"(?<=[.?!:;])\s+"


def synth(text, out, seed):
    req = urllib.request.Request(URL, json.dumps({"text": text, "out": str(Path(out).resolve()), "seed": seed}).encode(),
                                 {"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    if not r.get("ok"):
        raise RuntimeError(r.get("error"))
    trim_silence(out)
    cap_pauses(out)


def non_z(r):
    return [x for x in r["fails"] if x != "z"]


def key(r):
    """Lower is better: the other checks first, as before; a low «z» only after words, garble and noise."""
    z = r.get("z_min")
    return (len(non_z(r)), r["align_run"], r["missing_run"], r["cer"], "z" in r["fails"], -(z if z is not None else 9))


def zkey(r):
    """For a «z» re-take: pass every other check first, then the highest lowest-«z»."""
    z = r.get("z_min")
    return (len(non_z(r)), "z" in r["fails"], -(z if z is not None else 9), r["missing_run"], r["cer"])


def clean(r):
    return not r["fails"] and r["align_run"] == 0 and r["missing_run"] == 0 and r["cer"] <= 0.10


def join(pieces, target):
    gap = Path(target).with_suffix(".gap.mp3")
    listing = Path(target).with_suffix(".parts.txt")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.2",
                    "-b:a", "128k", str(gap)], check=True)
    listing.write_text("".join(f"file '{Path(p).resolve()}'\nfile '{gap.resolve()}'\n" for p in pieces[:-1])
                       + f"file '{Path(pieces[-1]).resolve()}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-ar", "24000", "-ac", "1", "-b:a", "128k", str(target)], check=True)
    gap.unlink(); listing.unlink()


def write_mp3(path, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", "24000", "-ac", "1", "-i", "-",
                    "-b:a", "128k", str(path)], input=np.asarray(x, np.float32).tobytes(), check=True)


def retake_all(asrs, f, text, work):
    """Every sentence voiced again; the best-heard take of each is kept (the original behaviour)."""
    pieces = []
    for k, sent in enumerate(p for p in re.split(SENT, text.strip()) if p):
        best = None
        for seed in SEEDS:
            out = work / f"{f.stem}.s{k}.seed{seed}.mp3"
            synth(sent, out, seed)
            r = judge(out, sent, asrs)
            if best is None or key(r) < key(best[0]):
                best = (r, out)
            if clean(r):
                break
        pieces.append(best[1])
        print(f"   {f.stem[:40]} s{k} {key(best[0])} {best[1].name.split('.')[-2]}", flush=True)
    cand = work / f"{f.stem}.new.mp3"
    join(pieces, cand)
    return cand


def retake_z(asrs, f, text, work):
    """Only the sentences holding a low «z» voiced again, set into the original audio between its own pauses."""
    sents = [p for p in re.split(SENT, text.strip()) if p]
    spans = align(f, text)
    counts = [len([w for w in (re.sub(r"[^a-z']", "", w) for w in re.sub(
        r"[^\w']+", " ", re.sub(r"[ʻʼ'`’‘]", "'", s.lower())).split()) if w.strip("'")]) for s in sents]
    if sum(counts) != len(spans):                     # the sentence split and the aligner disagree: do them all
        return retake_all(asrs, f, text, work)
    x, first, bounds = _load24(f), 0, []
    for c in counts:
        bounds.append((first, first + c - 1)); first += c
    # cut half-way through the pause between two sentences
    cuts = [0] + [int((spans[b][2] + spans[n][1]) / 2 * 24000) for (_, b), (n, _) in zip(bounds, bounds[1:])] + [len(x)]
    from voice_check import z_words
    low = {k for _, k, c, _ in z_words(f, text, spans) if c < Z_BAD}
    out_pieces = []
    for i, (sent, (a, b)) in enumerate(zip(sents, bounds)):
        piece = x[cuts[i]:cuts[i + 1]]
        if not any(a <= k <= b for k in low):
            out_pieces.append(piece)
            continue
        best = None
        for seed in SEEDS:
            out = work / f"{f.stem}.z{i}.seed{seed}.mp3"
            synth(sent, out, seed)
            r = judge(out, sent, asrs)
            if best is None or zkey(r) < zkey(best[0]):
                best = (r, out)
            if not r["fails"] and (r["z_min"] or 9) >= Z_LISTEN:
                break
        print(f"   {f.stem[:40]} z-sentence {i}: lowest «z» {best[0]['z_min']} kHz, fails {best[0]['fails']} "
              f"({best[1].name.split('.')[-2]})", flush=True)
        take = _load24(best[1])
        # keep the original's pause on each side (the take carries 0.12 s of its own)
        lead = max(0, int((spans[a][1] * 24000 - cuts[i])) - 2880)
        tail = max(0, int(cuts[i + 1] - spans[b][2] * 24000) - 2880)
        out_pieces.append(np.concatenate([np.zeros(lead, np.float32), take, np.zeros(tail, np.float32)]))
    cand = work / f"{f.stem}.znew.mp3"
    write_mp3(cand, np.concatenate(out_pieces))
    return cand


def main(build):
    import torch
    from transformers import pipeline
    asrs = [pipeline("automatic-speech-recognition", model=m, device=0, torch_dtype=torch.float16) for m in MODELS]
    report = json.loads(Path(build, "voice_check.json").read_text())
    work = Path(build, "revoiced"); work.mkdir(exist_ok=True)
    replaced = []
    for r in [r for r in report if not r["ok"]]:
        f, text = Path(r["file"]), r["text"]
        only_z = r["fails"] == ["z"]
        cand = retake_z(asrs, f, text, work) if only_z else retake_all(asrs, f, text, work)
        n = judge(cand, text, asrs)
        if only_z:      # nothing else may get worse, and the lowest «z» must rise
            better = len(non_z(n)) == 0 and (n["z_min"] or 9) > (r["z_min"] or 9) + 0.1
        else:
            better = key(n) < key(r)
        print(f"{'REPLACE' if better else 'keep old':8s} {f.parent.name}/{f.name[:50]}  old {key(r)}  new {key(n)}\n"
              f"         heard: {n['heard'][0]}", flush=True)
        if better:
            orig = work / f"{f.parent.name}__{f.name}.orig.mp3"
            if not orig.exists():                      # keep the first original across passes
                shutil.copy2(f, orig)
            shutil.copy2(cand, f)
            replaced.append({"file": str(f), "scene": f.parent.name, "old": key(r), "new": key(n),
                             "ok": not n["fails"], "z": only_z})
    log = Path(build, "revoiced.json")
    earlier = json.loads(log.read_text()) if log.exists() else []
    log.write_text(json.dumps(earlier + replaced, indent=1))
    print("scenes to re-render:", " ".join(sorted({x["scene"] for x in replaced})))


if __name__ == "__main__":
    main(sys.argv[1])
