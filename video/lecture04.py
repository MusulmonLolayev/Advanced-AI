"""Lecture 4 — Continuous random variables and the Gaussian: one video, built like the slides.

    lecture04_s00.py   lecture opening
    lecture04_s01.py … lecture04_s05.py   Part 0 (sections 1-5)
    lecture04_s06.py … lecture04_s10.py   Part 1 (sections 6-10), lecture close

Narration: narration/lecture04.md (approved), read by lecture04_kit.py. Numbers: statistics/raw/l04_numbers.json
(capture_l04.py, unit-tested by test_l04.py).
    ./render.sh lecture04 h                                   # English, edge-tts
    LANG_CODE=uz VOICE_ENGINE=navoiy JOBS=4 ./render.sh lecture04 h
"""
import importlib

SCENES = []
for _n in range(11):
    _m = importlib.import_module(f"lecture04_s{_n:02d}")
    for _s in _m.SCENES:
        # manim only renders classes whose __module__ starts with the name it gave this
        # file, which is built from the file's absolute path; claim the section scenes.
        _cls = getattr(_m, _s)
        _cls.__module__ = __name__
        globals()[_s] = _cls
        SCENES.append(_s)
