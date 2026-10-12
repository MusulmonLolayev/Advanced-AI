"""Re-voice the clips voice_check.py failed, sentence by sentence, and keep whichever version says the text.

Each sentence is voiced with the server's usual seed first; if both recognisers still miss words, it
is voiced again with other seeds and the best-heard take is kept. The pieces are joined with a 0.2 s
breath (as NavoiyService does for a line that stops early), the whole clip is checked again, and it
replaces the cached file in place only if it scores better than the old one. The old clip is kept
in <build>/revoiced/. The scenes that use a replaced clip must be re-rendered.

    ~/navoiy-stack/CosyVoice/.venv/bin/python revoice.py out/lecture03_uz_navoiy
"""
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

from audio_fx import cap_pauses, trim_silence
from voice_check import MODELS, judge

URL = "http://127.0.0.1:8765/tts"
SEEDS = (1986, 7, 42, 123, 2024, 31337)


def synth(text, out, seed):
    req = urllib.request.Request(URL, json.dumps({"text": text, "out": str(Path(out).resolve()), "seed": seed}).encode(),
                                 {"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    if not r.get("ok"):
        raise RuntimeError(r.get("error"))
    trim_silence(out)
    cap_pauses(out)


def score(asrs, path, text):
    """(number of failed checks, aligner's lost-word run, recognisers' missed-word run, CER), lower is better."""
    r = judge(path, text, asrs)
    return (len(r["fails"]), r["align_run"], r["missing_run"], r["cer"]), r["heard"]


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


def main(build):
    import torch
    from transformers import pipeline
    asrs = [pipeline("automatic-speech-recognition", model=m, device=0, torch_dtype=torch.float16) for m in MODELS]
    report = json.loads(Path(build, "voice_check.json").read_text())
    work = Path(build, "revoiced"); work.mkdir(exist_ok=True)
    replaced = []
    for r in [r for r in report if not r["ok"]]:
        f, text = Path(r["file"]), r["text"]
        old = (len(r["fails"]), r["align_run"], r["missing_run"], r["cer"])
        pieces = []
        for k, sent in enumerate(p for p in re.split(r"(?<=[.?!:;])\s+", text.strip()) if p):
            best = None
            for seed in SEEDS:
                out = work / f"{f.stem}.s{k}.seed{seed}.mp3"
                synth(sent, out, seed)
                s, _ = score(asrs, out, sent)
                if best is None or s < best[0]:
                    best = (s, out)
                if s[0] == 0 and s[1] == 0 and s[2] == 0 and s[3] <= 0.10:
                    break
            pieces.append(best[1])
            print(f"   {f.stem[:40]} s{k} {best[0]} {best[1].name.split('.')[-2]}", flush=True)
        cand = work / f"{f.stem}.new.mp3"
        join(pieces, cand)
        new, heard = score(asrs, cand, text)
        verdict = "REPLACE" if new < old else "keep old"
        print(f"{verdict:8s} {f.parent.name}/{f.name[:50]}  old {old}  new {new}\n         heard: {heard[0]}", flush=True)
        if new < old:
            orig = work / f"{f.parent.name}__{f.name}.orig.mp3"
            if not orig.exists():                      # keep the first original across passes
                shutil.copy2(f, orig)
            shutil.copy2(cand, f)
            replaced.append({"file": str(f), "scene": f.parent.name, "old": old, "new": new,
                             "ok": new[0] == 0})
    log = Path(build, "revoiced.json")
    earlier = json.loads(log.read_text()) if log.exists() else []
    log.write_text(json.dumps(earlier + replaced, indent=1))
    print("scenes to re-render:", " ".join(sorted({x["scene"] for x in replaced})))


if __name__ == "__main__":
    main(sys.argv[1])
