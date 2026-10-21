"""Listen to every edge-tts clip of a build in any language but Uzbek and flag the ones that do not say their text.

voice_check.py is the Uzbek check (two Uzbek recognisers, aligner, noise); here each clip is transcribed by
openai/whisper-large-v3-turbo in the build's language and compared with the narration by character error rate. A clip
fails over MAX_CER, or when its last 50 ms is still loud (cut off); it goes on the listen list over LISTEN_CER.
The report is voice_check.json, the same rows the editor's red and amber marks read (file, text, heard, cer, fails, ok,
listen), so a build in any language shows the same marks.

Runs in the Navoiy stack's env (transformers and the GPU):
    ~/navoiy-stack/CosyVoice/.venv/bin/python voice_check_lang.py ru out/m7_lecture01_ru [more builds...]
Writes <build>/voice_check.json and prints the failures. Exit 1 when a clip fails.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import languages as LG
from voice_check import MAX_CER, MAX_TAIL_DB, cer, clips, tail_db

MODEL = "openai/whisper-large-v3-turbo"
LISTEN_CER = 0.08        # between this and MAX_CER the clip goes on the listen list


def words(text, lang):
    """The text as compared: lower case, no punctuation, letters unified (ё = е, Arabic marks dropped)."""
    t = unicodedata.normalize("NFKC", re.sub(r"<[^>]+>", "", text).lower())
    if lang == "ru":
        t = t.replace("ё", "е")
    if LG.script(lang) == "arabic":
        t = "".join(ch for ch in unicodedata.normalize("NFKD", t) if not unicodedata.combining(ch))
    return re.sub(r"[^\w ]+", " ", t).split()


def judge(path, text, lang, heard):
    """One clip's row: the transcript, the error rate against the narration, and whether it passes."""
    ref, got = words(text, lang), words(heard, lang)
    c = cer(ref, got)
    r = {"heard": [heard], "cer": round(c, 3), "tail_db": round(tail_db(path), 1)}
    r["fails"] = [k for k, bad in (("cer", c > MAX_CER), ("cut off", r["tail_db"] > MAX_TAIL_DB)) if bad]
    r["ok"] = not r["fails"]
    r["listen"] = r["ok"] and c > LISTEN_CER
    return r


def main(lang, builds):
    import torch
    from transformers import pipeline
    asr = pipeline("automatic-speech-recognition", model=MODEL, device=0, torch_dtype=torch.float16)
    bad = 0
    for build in builds:
        report = []
        for f, text in clips(build).items():
            heard = asr(f, generate_kwargs={"language": LG.whisper(lang), "task": "transcribe"})["text"].strip()
            r = {"file": f, "text": text, **judge(f, text, lang, heard)}
            report.append(r)
            if not r["ok"]:
                bad += 1
                print(f"FAIL {Path(f).parent.name}/{Path(f).name}  {', '.join(r['fails'])}  (CER {r['cer']:.2f})\n"
                      f"     text:  {text}\n     heard: {heard}", flush=True)
        Path(build, "voice_check.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
        worst = max((r["cer"] for r in report), default=0)
        print(f"{build}: {sum(r['ok'] for r in report)}/{len(report)} clips pass, "
              f"{sum(r['listen'] for r in report)} on the listen list, worst CER {worst:.3f}", flush=True)
    return bad


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in LG.LANGS or sys.argv[1] == "uz":
        sys.exit(__doc__)
    sys.exit(1 if main(sys.argv[1], sys.argv[2:]) else 0)
