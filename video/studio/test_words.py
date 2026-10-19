"""words_worker.py on real speech: a cached English narration clip of Module 7 Lecture 1 and its approved text.
Needs the Navoiy env (transformers, torchaudio, the GPU) and the build's voice cache; skipped without them.

    uv run python -m unittest discover -s studio -p 'test_words.py' -t .        (from video/; ~30 s)
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from studio import media as M
from studio import timeline as T

HERE = Path(__file__).resolve().parents[1]
CACHE = HERE / "out" / "m7_lecture01_en" / "media" / "voiceovers" / "S02Tools"


def clip():
    for c in json.loads((CACHE / "cache.json").read_text()):
        if c["input_text"].startswith("The first concept is a tool."):
            return CACHE / c["final_audio"], c["input_text"]
    return None, None


@unittest.skipUnless(M.NAVOIY_PY.exists() and (CACHE / "cache.json").exists(), "no Navoiy env or no voice cache")
class Words(unittest.TestCase):
    def test_a_clean_take_is_heard_and_aligned_word_for_word(self):
        mp3, text = clip()
        self.assertIsNotNone(mp3)
        with tempfile.TemporaryDirectory() as d:
            wav, out, job = Path(d) / "c.wav", Path(d) / "c.json", Path(d) / "job.json"
            subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-ac", "1", "-ar", "16000", str(wav)], check=True)
            job.write_text(json.dumps({"lang": "en", "items": [{"wav": str(wav), "text": text, "out": str(out)}]}))
            r = subprocess.run([str(M.NAVOIY_PY), str(HERE / "studio" / "words_worker.py"), str(job)],
                               capture_output=True, text=True, cwd=HERE)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            w = json.loads(out.read_text())
        heard = [tuple(x) for x in w["heard"]]
        missing, extra, changed = T.script_check(text, heard)
        self.assertLessEqual(len(missing), 1, missing)            # the recogniser hears the clean voice
        self.assertLessEqual(len(extra), 1, extra)
        self.assertLessEqual(len(changed), 1, changed)
        self.assertEqual(len(w["aligned"]), len(T.norm_words(text)))
        times = [a for _, a, _ in heard]
        self.assertEqual(times, sorted(times))                    # word times run forward
        self.assertGreater(sum(c for *_, c in w["aligned"]) / len(w["aligned"]), 0.5)


UZ = HERE / "out" / "lecture01_uz_navoiy" / "media" / "voiceovers"


@unittest.skipUnless(M.NAVOIY_PY.exists() and UZ.is_dir(), "no Navoiy env or no Uzbek voice cache")
class UzbekWords(unittest.TestCase):
    def test_apostrophe_words_stay_whole_and_every_script_word_is_aligned(self):
        clip = None
        for c in sorted(UZ.glob("*/cache.json")):
            for x in json.loads(c.read_text()):
                if x["input_text"].startswith("Demak, ayrim berilganlar son emas"):
                    clip, text = c.parent / x["final_audio"], x["input_text"]
        if clip is None:
            self.skipTest("the clip is not in this cache")
        with tempfile.TemporaryDirectory() as d:
            wav, out, job = Path(d) / "c.wav", Path(d) / "c.json", Path(d) / "job.json"
            subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-ac", "1", "-ar", "16000", str(wav)], check=True)
            job.write_text(json.dumps({"lang": "uz", "items": [{"wav": str(wav), "text": text, "out": str(out)}]},
                                      ensure_ascii=False))
            r = subprocess.run([str(M.NAVOIY_PY), str(HERE / "studio" / "words_worker.py"), str(job)],
                               capture_output=True, text=True, cwd=HERE)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            w = json.loads(out.read_text())
        self.assertFalse([h for h in w["heard"] if h[0][0] in "'ʻʼ’‘`"])          # no "'ladi." on its own
        self.assertEqual(len(w["aligned"]), len(T.norm_words(text)))
        _, extra, _ = T.script_check(text, [tuple(x) for x in w["heard"]])
        self.assertEqual(extra, [])           # mishearings are "changed", never offered for cutting


if __name__ == "__main__":
    unittest.main()
