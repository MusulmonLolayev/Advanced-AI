"""The course's languages (languages.yaml): names, scripts, voices, section words. Imported by common.py (voices,
rates, clip trims), lecture_kit.py and labels.py (section cards, label languages) and the studio (narration review).
"""
from pathlib import Path

import yaml

HERE = Path(__file__).parent
LANGS = yaml.safe_load((HERE / "languages.yaml").read_text())     # code -> entry, in the file's order
CODES = list(LANGS)


def get(code):
    if code not in LANGS:
        raise KeyError(f"unknown language {code!r} (languages.yaml has {', '.join(CODES)})")
    return LANGS[code]


def name(code):
    return get(code)["name"]


def native(code):
    return get(code)["native"]


def script(code):
    return get(code)["script"]


def voices(engine="edge"):
    """{language: voice name} for one engine (edge, or navoiy: Uzbek only)."""
    return {c: v["voice"][engine] for c, v in LANGS.items() if engine in v["voice"]}


def rates():
    """{language: edge-tts rate} for the languages that have one."""
    return {c: v["rate"] for c, v in LANGS.items() if "rate" in v}


def trims():
    """{language: (lead, tail)} seconds of silence kept at a clip's ends, for the languages that have one."""
    return {c: tuple(v["trim"]) for c, v in LANGS.items() if "trim" in v}


def section(code, n):
    """The section card's / heading's words for section n: "Section 3", "3-boʻlim", "Раздел 3"."""
    return get(code)["section"].format(n=n)


def opening(code):
    return get(code)["opening"]
