"""Build and lecture names, in one place.

A build is a lecture in one language: `[m<module>_]lecture<NN>_<lang>[_<engine>]` (Module 0 has no prefix). Examples:
lecture01_uz_navoiy (Uzbek, the cloned voice), m7_lecture01_en, m7_lecture01_ru. The *stem* is the lecture without its
language (`m7_lecture01`); narration/<stem>.md and narration/<stem>_<lang>.md hold its narration.
"""
import re

STEM = re.compile(r"(?:m(\d)_)?lecture(\d\d)")
BUILD = re.compile(r"(?:m(\d)_)?lecture(\d\d)_([a-z]{2,3})(?:_([a-z]+))?")


def parse(name):
    """(module, lecture, lang, engine) of a build name; engine is None when the name has none."""
    m = BUILD.fullmatch(name)
    if not m:
        raise ValueError(f"not a lecture build: {name}")
    return int(m[1] or 0), int(m[2]), m[3], m[4]


def stem_of(module, lecture):
    return (f"m{module}_" if module else "") + f"lecture{lecture:02d}"


def name(module, lecture, lang, engine=None):
    return f"{stem_of(module, lecture)}_{lang}" + (f"_{engine}" if engine else "")


def is_build(name):
    return BUILD.fullmatch(name) is not None


def stem(build):
    """The lecture of a build: lecture01_uz_navoiy -> lecture01, m7_lecture01_en -> m7_lecture01."""
    module, lecture, _, _ = parse(build)
    return stem_of(module, lecture)


def lang(build):
    return parse(build)[2]


def engine(build):
    return parse(build)[3]


def module(build):
    return parse(build)[0]


def parse_stem(s):
    """(module, lecture) of a lecture stem."""
    m = STEM.fullmatch(s)
    if not m:
        raise ValueError(f"not a lecture: {s}")
    return int(m[1] or 0), int(m[2])
