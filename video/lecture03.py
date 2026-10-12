"""Lecture 3 — Random variables and key distributions: one video, built like the slides.

    lecture03_s00.py   lecture opening
    lecture03_s01.py … lecture03_s06.py   Part 0 (sections 1-6)
    lecture03_s07.py … lecture03_s11.py   Part 1 (sections 7-11), lecture close

Narration: narration/lecture03.md (approved), read by lecture03_kit.py. Numbers: statistics/raw/l03_numbers.json
(capture_l03.py, unit-tested by test_l03.py).
    ./render.sh lecture03 h                                   # English, edge-tts
    LANG_CODE=uz VOICE_ENGINE=navoiy JOBS=4 ./render.sh lecture03 h
"""
import importlib

SCENES = []
for _n in range(12):
    _m = importlib.import_module(f"lecture03_s{_n:02d}")
    for _s in _m.SCENES:
        # manim only renders classes whose __module__ starts with the name it gave this
        # file, which is built from the file's absolute path; claim the section scenes.
        _cls = getattr(_m, _s)
        _cls.__module__ = __name__
        globals()[_s] = _cls
        SCENES.append(_s)
