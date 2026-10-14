"""Where to listen first: every clip voice_check.py failed or put on its listen list, as a time in the final video.

Each clip is found in its scene's subtitles (manim-voiceover writes <Scene>.srt beside the scene video), and the
scene's start is the sum of the scenes before it in the build's parts.txt.
    uv run python listen_list.py out/lecture04_uz_navoiy        # prints markdown; also writes listen_list.md
"""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path


def norm(t):
    t = unicodedata.normalize("NFKC", t.lower())
    return re.sub(r"[^\w]+", " ", re.sub(r"[ʻʼ'`’‘]", "", t)).split()


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True, check=True).stdout)


def srt_starts(path):
    """[(seconds, words of the cue)] for one scene's subtitles."""
    out = []
    for block in Path(path).read_text().strip().split("\n\n"):
        rows = block.splitlines()
        if len(rows) >= 3:
            h, m, s = rows[1].split(" --> ")[0].replace(",", ".").split(":")
            out.append((int(h) * 3600 + int(m) * 60 + float(s), norm(" ".join(rows[2:]))))
    return out


def stamp(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def main(build):
    build = Path(build)
    report = json.loads((build / "voice_check.json").read_text())
    parts = [Path(r.split("'")[1]) for r in (build / "parts.txt").read_text().splitlines() if r.startswith("file")]
    offset, start = 0.0, {}
    for p in parts:
        start[p.stem] = (offset, p)
        offset += duration(p)
    rows = []
    for r in report:
        if r["ok"] and not r.get("listen"):
            continue
        scene = Path(r["file"]).parent.name
        if scene not in start:
            continue                                   # a stale clip no scene uses any more
        s0, mp4 = start[scene]
        head = norm(r["text"])[:4]
        t = next((s0 + ts for ts, ws in srt_starts(mp4.with_suffix(".srt")) if ws[:len(head)] == head), s0)
        why = ", ".join(r.get("fails", [])) or "listen: " + ", ".join(
            k for k, on in (("noisy?", r["bak"] < 1.8), ("aligner unsure", r["align_run"] >= 2),
                            ("last word unsure", r["align_last"] < 0.1),
                            ("«z» low", (r.get("z_min") or 9) < 4.6))
            if on)
        rows.append((t, scene, why, r["text"][:70]))
    rows.sort()
    md = [f"# Listen list: {build.name}", "", f"{sum(1 for r in report if not r['ok'])} failing, "
          f"{sum(1 for r in report if r['ok'] and r.get('listen'))} to check by ear.", "",
          "| time | scene | why | line begins |", "|---|---|---|---|"]
    md += [f"| {stamp(t)} | {sc} | {why} | {txt}… |" for t, sc, why, txt in rows]
    (build / "listen_list.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main(sys.argv[1])
