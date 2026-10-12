"""Lecture 5 — The central limit theorem and maximum likelihood: one video, built like the slides.

    lecture05_s00.py   lecture opening
    lecture05_s01.py … lecture05_s05.py   Part 0 (sections 1-5)
    lecture05_s06.py … lecture05_s10.py   Part 1 (sections 6-10), lecture close

Narration: narration/lecture05.md (approved), read by lecture05_kit.py. Numbers: statistics/raw/l05_numbers.json
(capture_l05.py, unit-tested by test_l05.py).
    ./render.sh lecture05 h                                   # English, edge-tts
    LANG_CODE=uz VOICE_ENGINE=navoiy JOBS=4 ./render.sh lecture05 h
"""
import importlib

SCENES = []
for _n in range(11):
    _m = importlib.import_module(f"lecture05_s{_n:02d}")
    for _s in _m.SCENES:
        # manim only renders classes whose __module__ starts with the name it gave this
        # file, which is built from the file's absolute path; claim the section scenes.
        _cls = getattr(_m, _s)
        _cls.__module__ = __name__
        globals()[_s] = _cls
        SCENES.append(_s)
