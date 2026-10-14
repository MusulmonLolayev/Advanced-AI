"""Listen to every cloned-voice clip of a build and flag the ones that do not say their text.

The cloned voice can garble a phrase into noise while the clip keeps a plausible length (Lecture 3's
first line lost «talaba avtobusda qatnaydi». Lekin koʻp savollar son haqida: to 1.6 s of hiss), so
the length guard in NavoiyService cannot see it. Here two independent Uzbek recognisers transcribe
each clip; a clip fails when even the better of the two misses a run of words or drifts too far
from the approved text. Two more listeners back them up:
  * forced alignment (Meta's MMS aligner) lines every approved word up with the audio; a run of words it
    cannot find, or a last word it cannot find, is a garble or a cut-off, located to the word;
  * DNSMOS (Microsoft's P.835 model, ~/navoiy-stack/models/dnsmos/sig_bak_ovr.onnx) scores background noise
    1-5 on 2 s windows; the worst window flags hiss.
  * every word-final «z» is measured: its hiss centred below Z_BAD kHz is heard as «zh» («yuz» -> «yuzsh»);
    revoice.py re-voices that sentence, zfix.py reshapes what stays low.
Calibrated on the defects the instructor reported: every one fails, their fixed takes pass. Lines dense with
spelled numbers trip the aligner on single words, so only runs count. Softer signals put a clip on the
listen list (`listen`) instead of failing it.

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
MAX_NOISE_S = 1.0        # this long loud with no clean voiced frame is hiss, not speech
ALIGN_LOW = 0.1          # a word the aligner finds with less confidence than this is not really there
MAX_ALIGN_RUN = 3        # this many such words in a row is a garble (the 0:18 phrase: 8; normal clips: <= 2)
MIN_BAK = 1.3            # DNSMOS background score below this in any 2 s window is noise (the 6:17 line: 1.15)
LISTEN_BAK = 1.8         # below this, put the clip on the listen list
Z_BAD = 4.0              # a word-final «z» whose hiss is centred below this (kHz) is heard as «zh» (yuz -> yuzsh)
Z_LISTEN = 4.6           # below this, put the clip on the listen list
DNSMOS = Path.home() / "navoiy-stack/models/dnsmos/sig_bak_ovr.onnx"
_M = {}


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


def noise_run(path, win=0.1, flat_min=0.12, loud=-32):
    """Longest stretch (seconds) that is loud but never has a clean voiced 0.1 s frame (spectral flatness stays
    >= 0.12). Speech keeps dipping below that; hiss does not. Lecture 4's 6:17 line opened with 2.3 s of it while
    the recognisers still half-heard the words under it. Across Lectures 3-4 normal clips peak at 0.9 s."""
    import subprocess
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "24000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float) / 32768
    hop, run, best = int(win * 24000), 0, 0
    for i in range(0, len(x) - hop, hop):
        seg = x[i:i + hop]
        rms = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)
        sp = np.abs(np.fft.rfft(seg * np.hanning(hop))) + 1e-9
        run = run + 1 if rms > loud and np.exp(np.log(sp).mean()) / sp.mean() >= flat_min else 0
        best = max(best, run)
    return round(best * win, 1)


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


def _load16(path):
    import subprocess
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def align(path, text):
    """[(word, start s, end s, confidence 0-1)] for every approved word, by forced alignment with MMS."""
    import torch
    import torchaudio
    import torchaudio.functional as F
    if "mms" not in _M:
        b = torchaudio.pipelines.MMS_FA
        _M["mms"] = (b.get_model(with_star=False).to("cuda"), b.get_dict(star=None))
    model, d = _M["mms"]
    t = re.sub(r"[ʻʼ'`’‘]", "'", unicodedata.normalize("NFKC", re.sub(r"<[^>]+>", "", text).lower()))
    ws = [w for w in (re.sub(r"[^a-z']", "", w) for w in re.sub(r"[^\w']+", " ", t).split()) if w.strip("'")]
    x = torch.from_numpy(_load16(path))[None].to("cuda")
    with torch.inference_mode():
        em = torch.log_softmax(model(x)[0], dim=-1)
    toks = torch.tensor([[d[c] for w in ws for c in w]], dtype=torch.int32, device="cuda")
    ali, sc = F.forced_align(em, toks, blank=0)
    spans, out, i = F.merge_tokens(ali[0], sc[0].exp()), [], 0
    sec = x.shape[1] / em.shape[1] / 16000                 # seconds per emission frame
    for w in ws:
        sp = spans[i:i + len(w)]; i += len(w)
        conf = float(sum(z.score * (z.end - z.start) for z in sp) / sum(z.end - z.start for z in sp))
        out.append((w, sp[0].start * sec, sp[-1].end * sec, conf))
    return out


def align_scores(path, text):
    """[(word, confidence 0-1)] for every approved word."""
    return [(w, c) for w, _, _, c in align(path, text)]


def _load24(path):
    import subprocess
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "24000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def z_segment(x, a, b, sr=24000):
    """(start, end) samples of a word-final «z»'s hiss: 10 ms frames in the word's second half and 80 ms after it,
    louder than -45 dB with a spectral centroid above 2.5 kHz; None if there is none."""
    import numpy as np
    hop = sr // 100
    i0, i1 = int((a + (b - a) * 0.5) * sr), min(len(x), int((b + 0.08) * sr))
    fr = [i for i in range(i0, i1 - hop, hop)
          if 20 * np.log10(np.sqrt((x[i:i + hop] ** 2).mean()) + 1e-9) > -45 and centroid(x[i:i + hop], sr) > 2500]
    return (fr[0], fr[-1] + hop) if fr else None


def centroid(seg, sr=24000):
    import numpy as np
    s = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1 / sr)
    return float((s * f).sum() / (s.sum() + 1e-12))


def z_centre(x, seg, sr=24000):
    """Mean centroid (kHz) of the hiss frames: ~6 for a clean «z» («biz»), 3.3-4.5 for «yuz» heard as «yuzsh»."""
    import numpy as np
    hop = sr // 100
    cs = [centroid(x[i:i + hop], sr) for i in range(seg[0], seg[1] - hop + 1, hop)]
    cs = [c for c in cs if c > 2500]
    return round(float(np.mean(cs)) / 1000, 2) if cs else None


def z_words(path, text, spans=None):
    """[(word, index, centre kHz, (start, end) samples at 24 kHz)] for every aligned word ending in «z»."""
    x, out = _load24(path), []
    for k, (w, a, b, _) in enumerate(spans or align(path, text)):
        if w.endswith("z"):
            seg = z_segment(x, a, b)
            c = z_centre(x, seg) if seg else None
            if c is not None:
                out.append((w, k, c, seg))
    return out


def dnsmos_bak(path, win=2.0, hop=0.5):
    """(worst background-noise score 1-5 over 2 s windows, the second it starts)."""
    import numpy as np
    import onnxruntime as ort
    if "dns" not in _M:
        _M["dns"] = ort.InferenceSession(str(DNSMOS), providers=["CPUExecutionProvider"])
    poly = np.poly1d([-0.13166888, 1.60915514, -0.39604546])        # DNSMOS's own calibration for BAK
    x, n, L = _load16(path), int(win * 16000), 144160
    worst = (5.0, 0.0)
    for s0 in range(0, max(1, len(x) - n + 1), int(hop * 16000)):
        seg = x[s0:s0 + n]
        seg = np.tile(seg, L // max(len(seg), 1) + 1)[:L][None].astype(np.float32)
        bak = float(poly(_M["dns"].run(None, {"input_1": seg})[0][0][1]))
        worst = min(worst, (round(bak, 2), round(s0 / 16000, 1)))
    return worst


def judge(f, text, asrs):
    """Every measurement of one clip, and whether it passes (`ok`) or should be heard first (`listen`)."""
    ref = words(re.sub(r"<[^>]+>", "", text))
    heard = [a(str(f))["text"] for a in asrs]
    scores = [(missing_run(ref, words(h)), cer(ref, words(h)), missing_tail(ref, words(h))) for h in heard]
    run, c, tail = (min(s[i] for s in scores) for i in range(3))
    spans = align(f, text)
    al = [(w, c) for w, _, _, c in spans]
    low = [sc < ALIGN_LOW for _, sc in al]
    arun = max((len(r) for r in "".join("x" if b else " " for b in low).split()), default=0)
    bak, bak_at = dnsmos_bak(f)
    r = {"heard": heard, "missing_run": run, "cer": round(c, 3), "missing_tail": tail,
         "tail_db": round(tail_db(f), 1), "noise_s": noise_run(f), "align_run": arun,
         "align_last": round(al[-1][1], 2) if al else 1.0,
         "align_low": [w for (w, _), b in zip(al, low) if b], "bak": bak, "bak_at": bak_at}
    zs = z_words(f, text, spans)
    r["z"] = [(w, c) for w, _, c, _ in zs]
    r["z_min"] = min((c for _, _, c, _ in zs), default=None)
    # The aligner stumbles on dense spelled numbers that both recognisers hear perfectly (Lecture 4's
    # «oltmish sakkiz, toʻqson besh»), so its lost-word run fails a clip only when the recognisers also lose
    # words; on its own it, and an unsure last word, only put the clip on the listen list.
    garble = arun >= MAX_ALIGN_RUN and (run >= 2 or c > 0.10)
    r["fails"] = [k for k, bad in (("words", run >= MAX_MISSING_RUN), ("cer", c > MAX_CER), ("last word", tail > 0),
                                   ("cut off", r["tail_db"] > MAX_TAIL_DB), ("hiss", r["noise_s"] >= MAX_NOISE_S),
                                   ("garble", garble), ("noise", bak < MIN_BAK),
                                   ("z", r["z_min"] is not None and r["z_min"] < Z_BAD)) if bad]
    r["ok"] = not r["fails"]
    # two words missed by the recognisers alone is common on good clips, so it counts only with the aligner
    r["listen"] = r["ok"] and (bak < LISTEN_BAK or arun >= MAX_ALIGN_RUN - 1 or r["align_last"] < ALIGN_LOW
                               or (r["z_min"] is not None and r["z_min"] < Z_LISTEN))
    return r


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
            r = {"file": f, "text": text, **judge(f, text, asrs)}
            report.append(r)
            if not r["ok"]:
                bad += 1
                print(f"FAIL {Path(f).parent.name}/{Path(f).name}  {', '.join(r['fails'])}  (missing {r['missing_run']}, "
                      f"CER {r['cer']:.2f}, aligner lost {r['align_low'][:6]}, noise {r['bak']} at {r['bak_at']} s)\n"
                      f"     text:  {text}\n     heard: {r['heard'][0]}", flush=True)
        Path(build, "voice_check.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
        print(f"{build}: {sum(r['ok'] for r in report)}/{len(report)} clips pass, "
              f"{sum(r['listen'] for r in report)} on the listen list", flush=True)
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
