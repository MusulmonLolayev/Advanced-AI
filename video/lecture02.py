"""Lecture 2 — Conditional probability, independence and Bayes' theorem: one video, built like the slides.

    lecture02_s00.py   lecture opening
    lecture02_s01.py … lecture02_s06.py   Part 0 (sections 1-6)
    lecture02_s07.py … lecture02_s10.py   Part 1 (sections 7-10), lecture close

Narration: narration/lecture02.md (approved), read by lecture02_kit.py. Numbers: statistics/raw/l02_numbers.json
(capture_l02.py, unit-tested by test_l02.py).
    ./render.sh lecture02 h                                   # English, edge-tts
    LANG_CODE=uz VOICE_ENGINE=navoiy JOBS=4 ./render.sh lecture02 h
"""
import importlib

SCENES = []
for _n in range(11):
    _m = importlib.import_module(f"lecture02_s{_n:02d}")
    for _s in _m.SCENES:
        # manim only renders classes whose __module__ starts with the name it gave this
        # file, which is built from the file's absolute path; claim the section scenes.
        _cls = getattr(_m, _s)
        _cls.__module__ = __name__
        globals()[_s] = _cls
        SCENES.append(_s)
