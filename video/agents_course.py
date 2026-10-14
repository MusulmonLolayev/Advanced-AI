"""Building AI Agents — a 30-minute course for software engineers, compressed from Module 7: one video.

    agents_course_s00.py   opening
    agents_course_s01.py … agents_course_s08.py   one section per Module 7 lecture
    agents_course_s09.py   what to build next, close

Narration: narration/agents_course.md (approved, English first), read by agents_course_kit.py, which fills the
live results from agents_course/raw/. Kit API for section builders: agents_course/BUILDING.md.
    ./render.sh agents_course h                      # English, edge-tts (en-US-AndrewNeural)
"""
import importlib

SCENES = []
for _n in range(10):
    try:
        _m = importlib.import_module(f"agents_course_s{_n:02d}")
    except ModuleNotFoundError as e:          # a section still being written
        if e.name != f"agents_course_s{_n:02d}":
            raise
        continue
    for _s in _m.SCENES:
        # manim only renders classes whose __module__ starts with the name it gave this
        # file, which is built from the file's absolute path; claim the section scenes.
        _cls = getattr(_m, _s)
        _cls.__module__ = __name__
        globals()[_s] = _cls
        SCENES.append(_s)
