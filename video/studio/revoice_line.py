"""Voice one (rewritten) line in the instructor's cloned voice and put the best take in its scene's voice cache.
Runs in the Navoiy env, with the voice server up (studio/voice_server.py starts it), called by studio/rewrite.py:

    ~/navoiy-stack/CosyVoice/.venv/bin/python studio/revoice_line.py job.json

job.json: {"build": out/<build>, "cache_dir": …/voiceovers/<Scene>, "text": the line, "report": result path}.
Each sentence is voiced with several seeds and every take is judged by voice_check.judge (two recognisers, the
aligner, DNSMOS, the «z» check), as revoice.py does for the clips the check fails; the best take of each sentence
is kept and the joined clip judged again. If the line already has a clip (same text: "re-voice as is"), that clip
is judged too, and the new take replaces it only if it scores better. The build's voice_check.json is updated.
"""
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(HERE), str(HERE / "studio")]


def main(job_path):
    import torch
    from transformers import pipeline
    import revoice
    import voicecache
    from voice_check import MODELS, judge
    job = json.loads(Path(job_path).read_text())
    text, cache = " ".join(job["text"].split()), Path(job["cache_dir"])
    cache.mkdir(parents=True, exist_ok=True)
    data = voicecache.navoiy_data(text)
    asrs = [pipeline("automatic-speech-recognition", model=m, device=0, torch_dtype=torch.float16) for m in MODELS]
    work = Path(job["report"]).parent / "takes"
    work.mkdir(parents=True, exist_ok=True)
    name = "rewrite-" + hashlib.sha1(f"{text}{time.time()}".encode()).hexdigest()[:10]
    cand = revoice.retake_all(asrs, work / f"{name}.mp3", text, work)
    new = judge(cand, text, asrs)
    old_path = voicecache.lookup(cache, data)
    old = judge(old_path, text, asrs) if old_path and old_path.exists() else None
    keep_new = old is None or revoice.key(new) < revoice.key(old)
    if keep_new:
        shutil.copy(cand, cache / f"{name}.mp3")
        voicecache.insert(cache, data, f"{name}.mp3")
        final, verdict = cache / f"{name}.mp3", new
    else:
        final, verdict = old_path, old
    report = {"kept": "new" if keep_new else "old", "file": str(final), "ok": verdict["ok"],
              "fails": verdict["fails"], "listen": verdict["listen"], "heard": verdict["heard"][0],
              "old": None if old is None else {"ok": old["ok"], "fails": old["fails"]}}
    vc = Path(job["build"]) / "voice_check.json"
    rows = json.loads(vc.read_text()) if vc.exists() else []
    rel = str(final.relative_to(HERE)) if final.is_relative_to(HERE) else str(final)   # as voice_check.py writes it
    rows = [r for r in rows if r.get("text") != text and r.get("file") != rel]
    rows.append({"file": rel, "text": text, **verdict})
    vc.write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    Path(job["report"]).write_text(json.dumps(report, ensure_ascii=False))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
