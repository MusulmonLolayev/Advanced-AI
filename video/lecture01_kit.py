"""Lecture 1's kit: its approved narration, its numbers, and the shared lecture pieces
(lecture_kit.py) bound to them. Every number on screen comes from statistics/raw/
(capture_v01.py, capture_l01.py).
"""
import json

import numpy as np
from lecture_kit import *
from lecture_kit import LectureScene as _BaseScene

L = json.loads((RAW / "l01_numbers.json").read_text())
ARR = json.loads((RAW / "l01_arrays.json").read_text())
V1 = json.loads((RAW / "v01_numbers.json").read_text())
SAL = np.sort(np.loadtxt(RAW / "v01_salaries.txt"))

NARRATION, HEADS = narration(1)
assert len(HEADS) == 14 and "0.0" in NARRATION and "4.s3d" in NARRATION and "14.11" in NARRATION

PARTS = {0: label("part_0_data_and_descriptive_statistics"),
         1: label("part_1_probability")}

LectureScene, line = bind(_BaseScene, (NARRATION, HEADS), PARTS, {1: 0, 10: 1})
