"""The course's languages (languages.yaml): names, scripts, voices, section words. Imported by common.py (voices,
rates, clip trims), lecture_kit.py and labels.py (section cards, label languages) and the studio (narration review).
"""
import subprocess
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


def font(code):
    """The family the video's text is set in, or None for the default font."""
    return get(code).get("font")


def installed_fonts():
    """The font families fontconfig knows (cached; empty when fc-list is missing)."""
    global _FONTS
    if _FONTS is None:
        try:
            out = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            out = ""
        _FONTS = {f.strip() for row in out.splitlines() for f in row.split(",") if f.strip()}
    return _FONTS


_FONTS = None


def guard(code):
    """(unit, per second): how fast the voice can read at most, for the truncation guard. Words at 5 a second unless
    the language says otherwise (a language written without spaces counts characters)."""
    g = get(code).get("guard") or {"words": 5.0}
    unit, per_second = next(iter(g.items()))
    return unit, float(per_second)


def min_seconds(code, text):
    """The shortest a whole clip of `text` can be: a shorter one lost words."""
    unit, per_second = guard(code)
    return (len(text) if unit == "chars" else len(text.split())) / per_second


def build_problem(code):
    """Why a video cannot be built in the language, or None: it needs an edge voice and, when the registry names one,
    that font installed."""
    if "edge" not in get(code)["voice"]:
        return f"{name(code)} has no edge-tts voice in languages.yaml"
    f = font(code)
    if f and installed_fonts() and f not in installed_fonts():
        return f"the font {f!r} ({name(code)} script) is not installed (fc-list)"
    return None


def rtl(code):
    return bool(get(code).get("rtl"))


def whisper(code):
    """The language's name as whisper-large-v3-turbo wants it (voice_check_lang.py)."""
    return get(code)["whisper"]


def draft_word(code):
    """The corner tag of a build whose narration is not approved."""
    return get(code)["draft"]
