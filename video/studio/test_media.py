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


class Levels(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.b = Path(self.tmp.name) / "m7_lecture99_en"
        M.recdir(self.b).mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_one_value_per_20_ms_in_whole_db(self):
        x = np.concatenate([tone(1.0, f=250, amp=0.5), np.zeros(M.SR // 2, np.float32), tone(0.51, f=250, amp=0.05)])  # whole cycles per window
        x.tofile(M.recdir(self.b) / "s.off.f32")
        out = M.levels(self.b, "s", "off")
        self.assertEqual(out["step"], 0.02)
        db = out["db"]
        self.assertEqual(len(db), 100)                                # 50 + 25 + 25 whole windows, a part-window dropped
        self.assertTrue(all(v == -9 for v in db[:50]))                # 0.5 / sqrt 2 = 0.3536 -> -9.03 dB
        self.assertTrue(all(v == M.LEVEL_FLOOR for v in db[50:75]))  # digital silence: the floor
        self.assertTrue(all(v == -29 for v in db[75:]))            # 0.05 / sqrt 2 -> -29.03 dB
        self.assertTrue(all(isinstance(v, int) for v in db))

    def test_the_cache_is_reused_until_the_voice_is_newer(self):
        f = M.recdir(self.b) / "s.off.f32"
        tone(0.2, f=250, amp=0.5).tofile(f)
        first = M.levels(self.b, "s", "off")
        cache = M.recdir(self.b) / "s.off.levels.json"
        self.assertTrue(cache.exists())
        c = json.loads(cache.read_text())
        c["db"][0] = -1                                                 # a marker only the cache holds
        cache.write_text(json.dumps(c))
        self.assertEqual(M.levels(self.b, "s", "off")["db"][0], -1)    # served from the cache
        tone(0.2, f=250, amp=0.05).tofile(f)
        import os
        st = f.stat()
        os.utime(f, (st.st_atime, st.st_mtime + 5))                    # the voice was made again
        again = M.levels(self.b, "s", "off")
        self.assertEqual(again["db"][0], -29)
        self.assertNotEqual(again, first)

    def test_a_session_falls_back_to_the_other_cleaned_copy_and_the_original_has_its_own_cache(self):
        tone(0.2, f=250, amp=0.5).tofile(M.recdir(self.b) / "s.deepfilter.f32")
        self.assertEqual(M.levels(self.b, "s", "off")["db"][0], -9)     # no "off" copy: the one there is
        with self.assertRaises(KeyError):
            M.levels(self.b, "nope", "off")
        (self.b / "presenter").mkdir(exist_ok=True)
        (self.b / f"{self.b.name}.mp4").write_bytes(b"x")
        tone(0.2, f=250, amp=0.05).tofile(self.b / "presenter" / "original.f32")
        (self.b / "presenter" / "original.m4a").write_bytes(b"x")
        import os
        os.utime(self.b / f"{self.b.name}.mp4", (0, 0))
        self.assertEqual(M.levels(self.b, T.ORIGINAL, "")["db"][0], -29)
        self.assertTrue((self.b / "presenter" / "original.levels.json").exists())

    def test_a_35_minute_recording_takes_under_2_seconds(self):
        import time
        f = M.recdir(self.b) / "long.off.f32"
        rng = np.random.default_rng(3)
        with open(f, "wb") as out:
            for _ in range(35):                                        # a minute at a time
                (0.1 * rng.standard_normal(60 * M.SR, dtype=np.float32)).tofile(out)
        t0 = time.time()
        db = M.levels(self.b, "long", "off")["db"]
        took = time.time() - t0
        self.assertEqual(len(db), 35 * 60 * 50)
        self.assertTrue(all(v == -20 for v in db[::1000]))             # sigma 0.1 -> -20 dB
        self.assertLess(took, 2.0, f"{took:.2f} s")


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


class Squeezed(unittest.TestCase):
    """A squeezed span is a play piece at up to 4 x the presenter's speed; the export copes with it."""
    def test_frames_and_pieces_of_a_fast_play(self):
        picture = [(1.0, "play", 0.0, 3.6, 3.6), (0.2, "play", 3.6, 4.4, 4.0), (0.5, "hold", 4.4, None, 1)]
        frames = T.frame_counts(picture, M.FPS)
        self.assertEqual(frames, [60, 12, 30])
        self.assertEqual(sum(frames), round(T.length(picture) * M.FPS))
        calls = []
        real, M.ff = M.ff, lambda *a: calls.append([str(x) for x in a])
        try:
            M.picture_piece("src.mp4", picture[1], frames[1], ["-c:v", "x"], "/tmp", 1)
        finally:
            M.ff = real
        args = calls[0]
        self.assertEqual(args[args.index("-vf") + 1], f"setpts=PTS/4.000000,fps={M.FPS}")     # 0.8 s of video in 0.2 s
        self.assertEqual((args[args.index("-ss") + 1], args[args.index("-frames:v") + 1]), ("3.600", "12"))

    def test_a_squeezed_take_exports_the_same_length_in_both_tracks(self):
        tr = {"voice": [(10.0, "s", 0.0)], "picture": [(10.0, "play", 0.0, 9.09, 0.909)]}
        v, p = T.squeeze(tr["voice"], [], [[2.0, 8.0, 1.5]], True), T.squeeze(tr["picture"], [], [[2.0, 8.0, 1.5]], False)
        self.assertEqual(sum(T.frame_counts(T.merge_picture(p), M.FPS)), round(T.length(v) * M.FPS))
        self.assertAlmostEqual(max(x[4] for x in p), 4 * 0.909)


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


class ClonedVoice(unittest.TestCase):
    """The cloned profile's pure part (splitting, fitting, placing), with a fake converter: no GPU."""

    def speech(self):
        # 10 s speech, 2 s pause, 12 s speech, 0.6 s breath, 8 s speech, 3 s pause, 5 s speech, 1.5 s pause at the end
        self.parts = [("v", 10), ("q", 2), ("v", 12), ("q", 0.6), ("v", 8), ("q", 3), ("v", 5), ("q", 1.5)]
        return np.concatenate([tone(d, f=200 + 30 * i) if k == "v" else quiet(d, seed=i)
                               for i, (k, d) in enumerate(self.parts)])

    def test_pieces_are_at_most_25_s_and_cut_in_pauses_where_they_can(self):
        x = self.speech()
        pieces = M.vc_pieces(x)
        for a, b, fi, fo in pieces:
            self.assertLessEqual(b - a, 25 * M.SR)
            self.assertGreaterEqual(a, 0)
            self.assertLessEqual(b, len(x))
        self.assertEqual(len(pieces), 3)                            # 10 s | 12+0.6+8 = 20.6 s | 5 s; the 2 s and 3 s pauses separate
        mid = pieces[1]
        self.assertAlmostEqual(mid[0] / M.SR, 12 - M.VC_PAD, delta=0.05)    # starts a pad before the speech
        self.assertAlmostEqual((mid[1] - mid[0]) / M.SR, 20.6 + 2 * M.VC_PAD, delta=0.06)

    def test_a_long_speech_is_cut_in_its_quietest_frame(self):
        x = np.concatenate([tone(20, f=200), quiet(0.1, amp=0.0), tone(20, f=210)])      # one 40.1 s speech, a 0.1 s dip
        pieces = M.vc_pieces(x)
        self.assertGreaterEqual(len(pieces), 2)
        self.assertTrue(all(b - a <= 25 * M.SR for a, b, _, _ in pieces))
        a0, b0, fi0, fo0 = pieces[0]
        self.assertEqual(fo0, 0)                                    # an inner cut: no fade
        self.assertEqual(pieces[1][2], 0)
        self.assertEqual(pieces[1][0], b0)                          # the next piece starts exactly where it ends
        self.assertAlmostEqual(b0 / M.SR, 20.05, delta=0.05)        # in the dip
        self.assertEqual(pieces[-1][1], len(x))

    def test_output_has_the_input_length_pauses_are_untouched_and_pieces_land_at_their_offsets(self):
        x = self.speech()
        seen = []

        def fake(p):                                                # the "converter": silence-free flat 0.25
            seen.append(len(p))
            return np.full(len(p), 0.25, np.float32)

        y, drifts = M.convert_voice(x, fake)
        self.assertEqual(len(y), len(x))
        self.assertEqual(len(drifts), 3)
        self.assertTrue(all(d == 0 for d in drifts))
        S = M.SR
        same = lambda a, b: np.all(y[int(a * S): int(b * S)] == x[int(a * S): int(b * S)])
        self.assertTrue(same(10.2, 11.8))                           # the 2 s pause between pieces 1 and 2
        self.assertTrue(same(32.8, 35.4))                           # the 3 s pause between pieces 2 and 3
        self.assertTrue(same(40.8, 42.1))                           # the pause at the end
        for a, b in ((1, 9), (13, 23), (24.1, 24.5), (26, 32), (36, 40)):     # speech, and the 0.6 s breath inside a piece
            self.assertTrue(np.allclose(y[int(a * S): int(b * S)], 0.25), (a, b))

    def test_a_converter_returning_a_longer_or_shorter_piece_is_cropped_or_padded(self):
        x = self.speech()
        for delta in (+700, -700):
            y, drifts = M.convert_voice(x, lambda p, d=delta: np.full(len(p) + d, 0.25, np.float32))
            self.assertEqual(len(y), len(x))
            for dr in drifts:
                self.assertAlmostEqual(dr, delta / M.SR, places=6)
        self.assertEqual(len(M.fit(np.ones(10), 4)), 4)
        f = M.fit(np.ones(4), 10)
        self.assertEqual(len(f), 10)
        self.assertTrue(np.all(f[4:] == 0))

    def test_pad_edges_fade_into_the_source(self):
        x = self.speech()
        y, _ = M.convert_voice(x, lambda p: np.full(len(p), 0.25, np.float32))
        a = M.vc_pieces(x)[0]
        self.assertGreater(a[3], 0)
        self.assertAlmostEqual(float(y[a[1] - 1]), float(x[a[1] - 1]), delta=0.01)       # last sample is the source again
        self.assertAlmostEqual(float(y[a[1] - a[3] // 2]), 0.5 * 0.25 + 0.5 * float(x[a[1] - a[3] // 2]), delta=0.01)  # halfway

    def test_cloned_clean_is_cached_and_written_whole(self):
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "m7_lecture99_en"
            rec = M.recdir(b)
            rec.mkdir(parents=True)
            x = self.speech()
            x.tofile(rec / "s.deepfilter.f32")
            (rec / "s.webm").write_bytes(b"x")
            import os
            os.utime(rec / "s.webm", (0, 0))
            real, M.vc_http = M.vc_http, lambda p: np.full(len(p) + 5, 0.25, np.float32)
            try:
                f = M.clean(b, "s", "cloned")
            finally:
                M.vc_http = real
            self.assertEqual(f.name, "s.cloned.f32")
            self.assertEqual(len(M.read_f32(f)), len(x))
            self.assertFalse((rec / "s.cloned.tmp").exists())
            self.assertEqual(len(json.loads((rec / "s.cloned.json").read_text())["drift_s"]), 3)

    def test_an_unreachable_server_is_a_clear_error(self):
        from studio import voice_server
        up, st = voice_server.up, voice_server.start
        voice_server.up = lambda port=8765: False
        voice_server.start = lambda wait=300: (_ for _ in ()).throw(RuntimeError("no stack"))
        try:
            with self.assertRaisesRegex(RuntimeError, "cloned voice: the voice server did not answer"):
                M.vc_http(np.zeros(100, np.float32))
        finally:
            voice_server.up, voice_server.start = up, st


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
