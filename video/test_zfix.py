"""The «z» reshape changes only its segment, keeps the length, and moves the hiss up.
    uv run python -m unittest test_zfix
"""
import unittest

import numpy as np

from zfix import SR, reshape


def centroid(seg):
    s = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    return (s * f).sum() / s.sum()


class Reshape(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(0)
        t = np.arange(SR) / SR
        self.x = (0.2 * np.sin(2 * np.pi * 180 * t)).astype(np.float32)        # a voiced vowel
        hiss = rng.normal(0, 0.05, SR).astype(np.float32)
        S = np.fft.rfft(hiss); f = np.fft.rfftfreq(SR, 1 / SR)
        S[(f < 2000) | (f > 8000)] = 0                                         # a broad «zh»-like hiss, 2-8 kHz
        self.a, self.b = 9600, 13200                                           # 0.40-0.55 s
        self.x[self.a:self.b] += np.fft.irfft(S, SR)[self.a:self.b].astype(np.float32)
        self.y = reshape(self.x, self.a, self.b)

    def test_length_unchanged(self):
        self.assertEqual(len(self.y), len(self.x))

    def test_outside_untouched(self):
        np.testing.assert_array_equal(self.y[:self.a], self.x[:self.a])
        np.testing.assert_array_equal(self.y[self.b:], self.x[self.b:])

    def test_hiss_moves_up(self):
        m = slice(self.a + 480, self.b - 480)                                  # inside the crossfades
        self.assertGreater(centroid(self.y[m]) - centroid(self.x[m]), 500)


if __name__ == "__main__":
    unittest.main()
