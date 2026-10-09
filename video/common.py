"""Shared style, speech service and helpers for the Advanced AI course videos.

Colours and the contact strip mirror statistics/theme/rl-theme.tex so the
videos and the slide decks look like one course.
"""
import asyncio
import os
import subprocess
from pathlib import Path

import edge_tts
from mutagen.mp3 import MP3
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService, initialize_speech_service

# ─── identity ─────────────────────────────────────────────────────────────
# One voice per language. LANG picks it; render with LANG=uz ./render.sh ...
VOICES = {
    "en": "en-US-AndrewNeural",
    "uz": "uz-UZ-SardorNeural",     # male; uz-UZ-MadinaNeural is the female option
}
LANG = os.environ.get("LANG_CODE", "en")
VOICE = VOICES[LANG]
# VOICE_ENGINE=navoiy narrates in the instructor's own fine-tuned voice (Uzbek only),
# served by ~/navoiy-stack/work/tts_server.py. Default stays edge-tts.
ENGINE = os.environ.get("VOICE_ENGINE", "edge")
NAVOIY_URL = os.environ.get("NAVOIY_URL", "http://127.0.0.1:8765/tts")
NAVOIY_VOICE_ID = "musulmon-ft-llm1-flow12-phone"
PAUSE_AFTER_VOICEOVER = 0.3

REPO = Path(__file__).resolve().parents[1]
FIGURES = REPO / "statistics" / "figures"

RLBLUE = "#3A35B7"
RLGREEN = "#5FA0A4"
RLORANGE = "#F4BD70"
RLRED = "#D6455D"
GOOD, BAD, HILITE = RLGREEN, RLRED, RLORANGE

BRAND_URL = "tqqt.uz"
BRAND_EMAIL = "musulmon.lolayev.94@gmail.com"
BRAND_TAGLINE = "Contact us for AI/IT solutions, projects, consulting, and hardware"

# check_edges.py flags bright pixels within 4 px of a frame edge, so nothing
# may sit flush against the border. Keep every persistent mark inside this.
SAFE = 0.45


# ─── speech ───────────────────────────────────────────────────────────────
class EdgeTTSService(SpeechService):
    def __init__(self, voice=VOICE, **kwargs):
        initialize_speech_service(self, kwargs)
        self.voice = voice

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = cache_dir or self.cache_dir
        input_text = remove_bookmarks(text)
        input_data = {"input_text": input_text, "service": "edge_tts", "voice": self.voice}
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached
        audio_path = str(path) if path else self.get_audio_basename(input_data) + ".mp3"
        target = str(Path(cache_dir) / audio_path)
        # edge-tts occasionally returns a truncated clip; check against word count.
        min_seconds = len(input_text.split()) / 4.5
        for _ in range(3):
            asyncio.run(edge_tts.Communicate(input_text, self.voice).save(target))
            if MP3(target).info.length >= min_seconds:
                break
        else:
            raise RuntimeError(f"edge-tts returned truncated audio for: {input_text[:60]!r}")
        return {"input_text": text, "input_data": input_data, "original_audio": audio_path}


class NavoiyService(SpeechService):
    """The instructor's cloned voice, via the local Navoiy server. Same cache and
    truncation guard as EdgeTTSService, so a failed clip fails the render."""
    def __init__(self, **kwargs):
        initialize_speech_service(self, kwargs)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        import json, urllib.request
        cache_dir = cache_dir or self.cache_dir
        input_text = remove_bookmarks(text)
        input_data = {"input_text": input_text, "service": "navoiy", "voice": NAVOIY_VOICE_ID}
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached
        audio_path = str(path) if path else self.get_audio_basename(input_data) + ".mp3"
        target = str(Path(cache_dir) / audio_path)
        min_seconds = len(input_text.split()) / 4.5
        req = urllib.request.Request(NAVOIY_URL, data=json.dumps({"text": input_text, "out": str(Path(target).resolve())}).encode(),
                                     headers={"Content-Type": "application/json"})
        resp = json.loads(urllib.request.urlopen(req, timeout=300).read())
        if not resp.get("ok"):
            raise RuntimeError(f"navoiy server failed: {resp.get('error')}")
        if MP3(target).info.length < min_seconds:
            raise RuntimeError(f"navoiy returned truncated audio for: {input_text[:60]!r}")
        return {"input_text": text, "input_data": input_data, "original_audio": audio_path}


class CourseScene(VoiceoverScene):
    def setup(self):
        super().setup()
        self.set_speech_service(NavoiyService() if ENGINE == "navoiy" else EdgeTTSService())

    def wait_for_voiceover(self):
        had = getattr(self, "current_tracker", None) is not None
        super().wait_for_voiceover()
        if had:
            self.wait(PAUSE_AFTER_VOICEOVER)

    def clear_all(self, run_time=0.8):
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)


# ─── helpers ──────────────────────────────────────────────────────────────
def txt(text, size=32, color=WHITE, weight=NORMAL):
    return Text(text, font_size=size, color=color, weight=weight)


def box(label, color=RLBLUE, width=3.2, height=1.1, size=26):
    rect = RoundedRectangle(corner_radius=0.12, width=width, height=height,
                            stroke_color=color, stroke_width=3, fill_opacity=0)
    inner = txt(label, size=size).scale_to_fit_width(min(width - 0.35, 12))
    return VGroup(rect, inner.move_to(rect))


def info(text, size=20):
    """Small note pinned near the bottom, inside the edge-safe margin."""
    t = txt(f"ⓘ  {text}", size=size, color=GREY_B)
    t.to_edge(DOWN, buff=SAFE + 0.15)
    return t


def figure(topic, name, height=4.6, dpi=300):
    """Load a chart the figure scripts already produced.

    The PDF written by generate_*_graphics.py is the single source of truth; we
    rasterise it once at high DPI and cache the PNG in screens/figures/ so a
    video can be re-rendered later even if the script changes. Manim's SVG
    parser rejects matplotlib's SVGs (paths with no "d" attribute), and video is
    a raster medium anyway, so nothing is lost.
    """
    pdf = FIGURES / topic / f"{name}.pdf"
    if not pdf.exists():
        raise FileNotFoundError(f"{pdf} — run the matching generate_*_graphics.py first")
    png = Path(__file__).parent / "statistics" / "screens" / "figures" / f"{name}.png"
    png.parent.mkdir(parents=True, exist_ok=True)
    if not png.exists() or png.stat().st_mtime < pdf.stat().st_mtime:
        subprocess.run(["mutool", "draw", "-o", str(png), "-r", str(dpi), str(pdf), "1"],
                       check=True, capture_output=True)
    img = ImageMobject(str(png))
    img.set_height(height)
    card = SurroundingRectangle(img, buff=0.18, color=GREY_D,
                                stroke_width=2, fill_color=WHITE, fill_opacity=1)
    return Group(card, img)


def title_card(line1, line2=None, color=RLBLUE):
    g = VGroup(txt(line1, size=52, weight=BOLD, color=color))
    if line2:
        g.add(txt(line2, size=34))
        g.arrange(DOWN, buff=0.45)
    return g


def pause_card(steps, note=None):
    head = txt("⏸  Pause the video", size=40, weight=BOLD, color=HILITE)
    items = VGroup(*[txt(f"{i}. {s}", size=28) for i, s in enumerate(steps, 1)])
    items.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
    g = VGroup(head, items).arrange(DOWN, buff=0.55)
    return g if note is None else VGroup(g, info(note))


def next_card(number, title):
    head = txt("Next", size=30, color=GREY_B)
    body = txt(f"Video {number} — {title}", size=40, weight=BOLD, color=RLBLUE)
    return VGroup(head, body).arrange(DOWN, buff=0.35)


def brand_mark():
    """Small persistent mark, inset from the corner to stay edge-safe."""
    t = txt(BRAND_URL, size=20, color=GREY_B)
    t.to_corner(DR, buff=SAFE)
    return t


def brand_outro():
    return VGroup(
        txt("Advanced AI", size=46, weight=BOLD, color=RLBLUE),
        txt(BRAND_TAGLINE, size=24, color=GREY_B),
        txt(f"{BRAND_URL}     {BRAND_EMAIL}", size=26, color=WHITE),
    ).arrange(DOWN, buff=0.45)
