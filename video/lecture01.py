"""Lecture 1 — Data, descriptive statistics and probability: one video, built like the slides.

    lecture01_s00.py   lecture opening, Part 0 card
    lecture01_s01.py … lecture01_s09.py   Part 0 (sections 1-9)
    lecture01_s10.py … lecture01_s14.py   Part 1 (sections 10-14), lecture close

Narration: narration/lecture01.md (approved), read by lecture01_kit.py. Numbers: statistics/raw/.
    ./render.sh lecture01 h                                   # English, edge-tts
    LANG_CODE=uz VOICE_ENGINE=navoiy JOBS=4 ./render.sh lecture01 h
"""
import importlib

SCENES = []
for _n in range(15):
    _m = importlib.import_module(f"lecture01_s{_n:02d}")
    for _s in _m.SCENES:
        # manim only renders classes whose __module__ starts with the name it gave this
        # file, which is built from the file's absolute path; claim the section scenes.
        _cls = getattr(_m, _s)
        _cls.__module__ = __name__
        globals()[_s] = _cls
        SCENES.append(_s)
