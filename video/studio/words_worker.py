"""Transcribe takes with word times, and align each take's approved text to its audio. Runs in the Navoiy env
(transformers, torchaudio and the GPU), called by studio/media.words():

    ~/navoiy-stack/CosyVoice/.venv/bin/python studio/words_worker.py job.json

job.json: {"lang": "uz" | "en", "items": [{"wav": 16 kHz wav, "text": approved line, "out": result path}]}.
Each result: {"model", "heard": [[word, from, to]], "aligned": [[word, from, to, confidence 0-1]]}.
Uzbek is heard by islomov/rubaistt_v2_medium (one of voice_check.py's two recognisers: a Whisper fine-tune, so it
gives word times), English by openai/whisper-large-v3-turbo; the alignment is voice_check.align (Meta's MMS aligner).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
MODELS = {"uz": "islomov/rubaistt_v2_medium", "en": "openai/whisper-large-v3-turbo"}


def main(job_path):
    import torch
    from transformers import pipeline
    from voice_check import align
    job = json.loads(Path(job_path).read_text())
    name = MODELS[job["lang"]]
    asr = pipeline("automatic-speech-recognition", model=name, device=0, torch_dtype=torch.float16)
    for it in job["items"]:
        r = asr(it["wav"], return_timestamps="word", chunk_length_s=30, batch_size=4,
                generate_kwargs={"language": "uzbek" if job["lang"] == "uz" else "english", "task": "transcribe"})
        heard = []
        for c in r.get("chunks", []):
            w, (a, b) = c["text"].strip(), c["timestamp"]
            if not w:
                continue
            a = a or 0
            b = b if b is not None else a + 0.3
            if heard and w[0] in "'ʻʼ’‘`":            # «boʻladi» comes back as "bo" + "'ladi": one word
                heard[-1][0] += w
                heard[-1][2] = round(b, 3)
            else:
                heard.append([w, round(a, 3), round(b, 3)])
        try:
            aligned = [[w, round(a, 3), round(b, 3), round(c, 3)] for w, a, b, c in align(it["wav"], it["text"])]
        except Exception as e:                     # an empty or silent take: nothing to align
            aligned, heard = [], heard or []
            print(f"align failed for {it['out']}: {e}", file=sys.stderr)
        Path(it["out"]).write_text(json.dumps({"model": name, "heard": heard, "aligned": aligned}, ensure_ascii=False))
        print("done", it["out"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
