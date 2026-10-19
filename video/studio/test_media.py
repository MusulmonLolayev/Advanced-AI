"""Unit tests for studio/media.py: pieces joined in order, pauses found, the voice sliced sample-exact, chapters.

    uv run python -m unittest discover -s studio -p 'test_media.py' -t .        (from video/)
"""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from studio import media as M
from studio import timeline as T


def tone(sec, f=220, sr=M.SR, amp=0.3):
    t = np.arange(round(sec * sr)) / sr
    return (amp * np.sin(2 * np.pi * f * t)).astype(np.float32)


def quiet(sec, sr=M.SR, amp=0.002, seed=0):
    return (amp * np.random.default_rng(seed).standard_normal(round(sec * sr))).astype(np.float32)


class Chunks(unittest.TestCase):
    def test_pieces_join_in_order_and_a_gap_stops_the_join(self):
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "m7_lecture99_en"
            self.assertEqual(M.add_chunk(b, "s", 0, b"AA"), 1)
            self.assertEqual(M.add_chunk(b, "s", 2, b"CC"), 1)       # 1 is late: 2 waits
            self.assertEqual(M.add_chunk(b, "s", 1, b"BB"), 3)
            self.assertEqual(M.add_chunk(b, "s", 1, b"BB"), 3)       # a retry of 1: harmless
            self.assertEqual(M.assemble(b, "s").read_bytes(), b"AABBCC")
            M.add_chunk(b, "s", 4, b"EE")                             # 3 never came: 4 is left out
            self.assertEqual(M.assemble(b, "s").read_bytes(), b"AABBCC")


class Pauses(unittest.TestCase):
    def test_silences_are_found_where_the_voice_stops(self):
        x = np.concatenate([tone(1.0), quiet(1.2), tone(0.5), quiet(0.2), tone(0.8), quiet(0.6)])
        found = M.silences(x)
        self.assertEqual(len(found), 2)                              # the 0.2 s gap is a breath, not a pause
        (a1, b1), (a2, b2) = found
        self.assertAlmostEqual(a1, 1.0, delta=0.03)
        self.assertAlmostEqual(b1, 2.2, delta=0.03)
        self.assertAlmostEqual(a2, 3.7, delta=0.03)
        self.assertAlmostEqual(b2, 4.3, delta=0.03)


class VoiceTrack(unittest.TestCase):
    def test_pieces_are_sliced_sample_exact_and_silence_is_zero(self):
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "m7_lecture99_en"
            rec = M.recdir(b)
            rec.mkdir(parents=True)
            sig = np.arange(10 * M.SR, dtype=np.float32) / M.SR       # value = its own time: easy to check
            sig.tofile(rec / "s.off.f32")
            (rec / "s.webm").write_bytes(b"x")                         # older than the f32: no re-cleaning
            import os
            os.utime(rec / "s.webm", (0, 0))
            loud, M.loudness = M.loudness, lambda f: M.TARGET            # already at the target: gain 1
            try:
                out = M.voice_track(b, [(1.0, "s", 2.0), (0.5, None, None), (1.0, "s", 7.0)], "off")
            finally:
                M.loudness = loud
            self.assertEqual(len(out), round(2.5 * M.SR))
            self.assertAlmostEqual(float(out[0]), 2.0, places=4)
            self.assertAlmostEqual(float(out[M.SR - 1]), 3.0 - 1 / M.SR, places=4)
            self.assertTrue(np.all(out[M.SR: M.SR + M.SR // 2] == 0))
            self.assertAlmostEqual(float(out[int(1.5 * M.SR)]), 7.0, places=4)


class Loudness(unittest.TestCase):
    def test_every_source_is_brought_to_the_narration_loudness(self):
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "m7_lecture99_en"
            rec = M.recdir(b)
            rec.mkdir(parents=True)
            import os
            for name, amp in (("quiet", 0.02), ("loud", 0.4)):
                np.tile(tone(1.0, amp=amp), 20).tofile(rec / f"{name}.off.f32")
                (rec / f"{name}.webm").write_bytes(b"x")
                os.utime(rec / f"{name}.webm", (0, 0))
            out = M.voice_track(b, [(5.0, "quiet", 0.0), (5.0, "loud", 0.0)], "off")
            a, z = out[: 5 * M.SR], out[5 * M.SR:]
            rms = lambda x: float(np.sqrt(np.mean(x ** 2)))           # noqa: E731
            self.assertAlmostEqual(rms(a) / rms(z), 1.0, delta=0.05)   # one level, whichever source


class Chapters(unittest.TestCase):
    def test_titles_come_from_the_narration_headings(self):
        with tempfile.TemporaryDirectory() as d:
            n = Path(d)
            (n / "m7_lecture99_en.md").write_text("## Lecture opening\n### Section 1 — Why agents\n### Section 2 — Tools\n")
            (n / "m7_lecture99.md").write_text("### 1-boʻlim · Section 1 — Nega agent? · Why agents\n")
            self.assertEqual(M.section_titles("m7_lecture99_en", n), {1: "Section 1 · Why agents", 2: "Section 2 · Tools"})
            self.assertEqual(M.section_titles("m7_lecture99_uz_navoiy", n), {1: "1-boʻlim · Nega agent?"})

    def test_the_first_line_of_each_scene_number_starts_a_section(self):
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "m7_lecture99_en"
            (b / "presenter").mkdir(parents=True)
            (b / "parts.txt").write_text("".join(f"file '/x/{s}.mp4'\n" for s in ("S00Opening", "S01Why", "S01More", "S02Tools")))
            ls = [[0, "a", [], 0], [5, "b", [], 1], [9, "c", [], 2], [12, "d", [], 3], [15, "e", [], 3]]
            (b / "presenter" / "lines.json").write_text(json.dumps(ls))
            self.assertEqual(M.line_sections(b), {0: 0, 1: 1, 3: 2})


class RealLecture(unittest.TestCase):
    """The real Module 7 build, when it is there: its line list carries scene numbers and chapters come out."""
    B = Path(__file__).resolve().parents[1] / "out" / "m7_lecture01_en"

    @unittest.skipUnless((B / "presenter" / "lines.json").exists() and (B / "parts.txt").exists(), "no build")
    def test_sections_of_the_english_lecture(self):
        ls = M.lines(self.B)
        if len(ls[0]) < 4:
            self.skipTest("presenter page prepared before lines carried their scene")
        secs = M.line_sections(self.B)
        self.assertEqual(sorted(secs.values()), list(range(0, 11)))
        titles = M.section_titles(self.B.name)
        self.assertEqual(titles[4], "Section 4 · A real trajectory")


if __name__ == "__main__":
    unittest.main()
