"""Module 7, Lecture 1 — What is an agent? One video, built like the slides (one part, ten sections).

    m7_lecture01_s00.py   lecture opening
    m7_lecture01_s01.py … m7_lecture01_s10.py   sections 1-10, closing

Narration: narration/m7_lecture01.md (DRAFT until approved), read by m7_lecture01_kit.py. Numbers:
m7/raw/l01_numbers.json (m7/capture_l01.py, tested by m7/test_l01.py); agent runs: agents/class_agent/traces/.
    LABEL_DRAFTS=narration/drafts/m7_l01 LANG_CODE=uz VOICE_ENGINE=navoiy JOBS=4 ./render.sh m7_lecture01 m
"""
import importlib

SCENES = []
for _n in range(11):
    _m = importlib.import_module(f"m7_lecture01_s{_n:02d}")
    for _s in _m.SCENES:
        _cls = getattr(_m, _s)
        _cls.__module__ = __name__
        globals()[_s] = _cls
        SCENES.append(_s)
