"""Listen to every cloned-voice clip of a build and flag the ones that do not say their text.

The cloned voice can garble a phrase into noise while the clip keeps a plausible length (Lecture 3's
first line lost «talaba avtobusda qatnaydi». Lekin koʻp savollar son haqida: to 1.6 s of hiss), so
the length guard in NavoiyService cannot see it. Here two independent Uzbek recognisers transcribe
each clip; a clip fails when even the better of the two misses a run of words or drifts too far
from the approved text.

Runs in the Navoiy stack's env (it has transformers and the GPU):
    ~/navoiy-stack/CosyVoice/.venv/bin/python voice_check.py out/lecture03_uz_navoiy [more builds...]
Writes <build>/voice_check.json and prints the failures.
"""
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

MODELS = ("Kotib/uzbek_stt_v1", "islomov/rubaistt_v2_medium")
MAX_MISSING_RUN = 3      # this many approved words in a row, heard by neither recogniser
MAX_CER = 0.15
MAX_TAIL_DB = -35        # a clip still this loud in its last 50 ms was cut off mid-word


def words(t):
    t = unicodedata.normalize("NFKC", t.lower())
    t = re.sub(r"[ʻʼ'`’‘]", "'", t)
    t = t.replace("o'", "o").replace("g'", "g").replace("'", "")   # recognisers drop or keep these at random
    return re.sub(r"[^\w ]+", " ", t).split()


def cer(a, b):
    a, b = " ".join(a), " ".join(b)
    return 1 - difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def tail_db(path):
    """Loudness of a clip's last 50 ms. Lecture 4's first line stopped inside «olaylik» at -17 dB."""
    import subprocess
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float)[-800:] / 32768
    return float(20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9))


def missing_tail(ref, hyp):
    """Reference words lost at the very end (the voice stopping early), heard by fuzzy match."""
    k = 0
    for w in reversed(ref):
        if any(difflib.SequenceMatcher(None, w, h).ratio() >= 0.7 for h in hyp[-3:]):
            break
        k += 1
    return k


def missing_run(ref, hyp):
    """Longest run of consecutive reference words the transcript does not contain."""
    sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
    hit = [False] * len(ref)
    for b in sm.get_matching_blocks():
        for i in range(b.a, b.a + b.size):
            hit[i] = True
    # a word heard slightly wrong ("ehtimolini" for "ehtimolni") counts as heard
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "replace":
            for i in range(i1, i2):
                if any(difflib.SequenceMatcher(None, ref[i], h).ratio() >= 0.7 for h in hyp[j1:j2]):
                    hit[i] = True
    run = best = 0
    for h in hit:
        run = 0 if h else run + 1
        best = max(best, run)
    return best


def clips(build):
    seen = {}
    for cache in sorted(Path(build, "media", "voiceovers").glob("*/cache.json")):
        for e in json.loads(cache.read_text()):
            f = cache.parent / e["original_audio"]
            if f.exists():
                seen[str(f)] = e["input_text"]
    return seen


def main(builds):
    import torch
    from transformers import pipeline
    asrs = [pipeline("automatic-speech-recognition", model=m, device=0, torch_dtype=torch.float16) for m in MODELS]
    bad = 0
    for build in builds:
        report = []
        for f, text in clips(build).items():
            ref = words(re.sub(r"<[^>]+>", "", text))
            heard = [a(f)["text"] for a in asrs]
            scores = [(missing_run(ref, words(h)), cer(ref, words(h)), missing_tail(ref, words(h))) for h in heard]
            run, c, tail = (min(s[i] for s in scores) for i in range(3))
            end = tail_db(f)
            ok = run < MAX_MISSING_RUN and c <= MAX_CER and tail == 0 and end <= MAX_TAIL_DB
            report.append({"file": f, "text": text, "heard": heard, "missing_run": run, "cer": round(c, 3),
                           "missing_tail": tail, "tail_db": round(end, 1), "ok": ok})
            if not ok:
                bad += 1
                print(f"FAIL {Path(f).parent.name}/{Path(f).name}  missing {run} words, CER {c:.2f}, "
                      f"last {tail} words lost, ends at {end:.0f} dB\n"
                      f"     text:  {text}\n     heard: {heard[0]}\n            {heard[1]}", flush=True)
        Path(build, "voice_check.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
        print(f"{build}: {sum(r['ok'] for r in report)}/{len(report)} clips say their text", flush=True)
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
