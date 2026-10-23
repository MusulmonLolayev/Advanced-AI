"""A scene's voice cache (media/voiceovers/<Scene>/cache.json, manim-voiceover's format): put a chosen clip in it
for a line's text, so the next render of that scene uses this clip instead of voicing the line again.

manim-voiceover finds a clip by its input_data, exactly: the text (whitespace collapsed, no bookmarks) and, for the
cloned voice, the service and voice id (common.NavoiyService). The first entry that matches wins, so an older entry
for the same text is removed. No manim import: this runs in the Navoiy env too.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def voice_id():
    """common.NAVOIY_VOICE_ID: the cloned voice of the language registry (importing common would load manim)."""
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import languages
    return languages.voices("navoiy")["uz"]


def navoiy_data(text):
    return {"input_text": " ".join(text.split()), "service": "navoiy", "voice": voice_id()}


def lookup(cache_dir, data):
    p = Path(cache_dir) / "cache.json"
    for e in json.loads(p.read_text()) if p.exists() else []:
        if e.get("input_data") == data:
            return Path(cache_dir) / e.get("final_audio", e["original_audio"])
    return None


def insert(cache_dir, data, audio_name):
    """Make `audio_name` (a file already in cache_dir) the clip for `data`."""
    p = Path(cache_dir) / "cache.json"
    entries = [e for e in (json.loads(p.read_text()) if p.exists() else []) if e.get("input_data") != data]
    entries.append({"input_text": data["input_text"], "input_data": data, "original_audio": audio_name,
                    "final_audio": audio_name})
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(entries, ensure_ascii=False, indent=2))
    tmp.replace(p)
