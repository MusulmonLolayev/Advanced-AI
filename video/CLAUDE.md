# Video track — Advanced AI

Narrated Manim videos built from the same material as the slide decks.

## Layout
- `common.py` — speech service, `CourseScene`, style helpers, brand marks.
- `vNN_topic.py` — one file per video, one `Scene` class per section, `SCENES = [...]` giving order.
- `statistics/raw/` — real stdout captured from the figure scripts. Every number on screen must trace to a file here.
- `statistics/screens/figures/` — figures rasterised from the committed PDFs, cached so a video re-renders later.
- `render.sh <module> [l|m|h|k]`, `check_edges.py <mp4>`.

## Environment
`uv` project (Python 3.12). System deps: `ffmpeg`, `libcairo2-dev`, `libpango1.0-dev`, `pkg-config`.
`uv` itself installed with `pip install --user uv`, not `curl | sh`.
Figures are generated separately by the `adv_ai` conda env — the two never mix.

## Lessons (do not re-learn these)
- **Manim cannot read matplotlib's SVG.** `SVGMobject` dies with `TypeError: object of type 'NoneType' has no len()` on a `<path>` with no `d`. Rasterise the committed PDF with `mutool draw -r 300` instead; `common.figure()` does this and caches the PNG. Video is raster anyway, so nothing is lost.
- **An embedded chart is too small to read at video scale.** A 5.6in matplotlib figure shown 4.6 units tall puts its 8 pt legend at roughly 10 px on a 1080p frame. Use embedded figures only for callbacks; animate the hero chart natively in Manim, driving it from the same numbers in `statistics/raw/`.
- **SoX is missing and that is fine** — `manim-voiceover` only needs it to time-stretch audio, which we never do. The warning is noise.
- **`render.sh` must filter stderr when reading `SCENES`**, or the SoX warning lands in the scene list.
- **The ffmpeg concat list needs absolute paths**, since ffmpeg resolves entries relative to the list file.
- **Nothing persistent may touch the frame edge.** `check_edges.py` flags bright pixels within 4 px of any border, so the brand mark is inset by `common.SAFE`. A full-width footer strip would flag every frame — branding lives in the opening bumper, the closing card, and that one inset mark.

## Rules carried over from the decks
Numbers on screen come from a saved raw output, never retyped. Narration spells numbers for the ear while the screen shows digits. One concept per video; problem first, concept as the answer; each video ends with the problem the next one solves.
