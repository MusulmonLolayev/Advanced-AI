"""The editor's audio and video work: a session's audio, prepared once; the export of the edit list.

A session's files, in <build>/presenter/recordings/:
  <name>.chunks/000000.part …   the pieces the page uploaded while recording (one a second; a crash loses at most
                                the last one or two)
  <name>.webm                   the pieces joined, the microphone as recorded
  <name>.json                   the presenter's events (posted every few seconds, and at the end)
  <name>.<profile>.f32          the voice, cleaned with that profile: 48 kHz mono float32, on the session's clock
  <name>.m4a                    a seekable copy at the narration's loudness, for the browser preview
  <name>.silence.json           [[from, to]] pauses in the session, for the "shorten pauses" proposals
  <name>.words/<t_in>.json      a take's transcript: words heard (with times) and the script aligned to the audio

The export renders the very tracks the preview plays (timeline.edit_list): the picture piece by piece from the
presenter's silent copy of the lecture video, the voice sample-exact from the cleaned sessions, levelled by one gain
to -19 LUFS; then the .srt and the chapters beside it.
"""
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from compose_recording import CLEAN, PEAK, TARGET, deepfilter, video_encoder   # noqa: E402
from studio import timeline as T                                                # noqa: E402

SR = 48000
FPS = 60
NAVOIY_PY = Path.home() / "navoiy-stack/CosyVoice/.venv/bin/python"
BUILD = re.compile(r"(?:m(\d)_)?lecture(\d\d)_(uz_navoiy|en)")


def ff(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *map(str, args)], check=True)


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True, check=True).stdout)


def recdir(build_dir):
    return Path(build_dir) / "presenter" / "recordings"


# ─── a session's audio ────────────────────────────────────────────────────
def add_chunk(build_dir, name, seq, data):
    """Keep one uploaded piece. Idempotent: a piece sent twice (a retry after a lost answer) is written twice."""
    d = recdir(build_dir) / f"{name}.chunks"
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / f"{seq:06d}.tmp"
    tmp.write_bytes(data)
    tmp.replace(d / f"{seq:06d}.part")
    return contiguous(d)


def contiguous(d):
    """How many pieces from 0 on are here without a gap."""
    n = 0
    while (Path(d) / f"{n:06d}.part").exists():
        n += 1
    return n


def assemble(build_dir, name):
    """<name>.webm from its pieces (only the gap-free run from the first: MediaRecorder's pieces are one stream)."""
    rec = recdir(build_dir)
    d = rec / f"{name}.chunks"
    if not d.is_dir():
        return rec / f"{name}.webm"
    n = contiguous(d)
    with open(rec / f"{name}.webm.tmp", "wb") as out:
        for k in range(n):
            out.write((d / f"{k:06d}.part").read_bytes())
    (rec / f"{name}.webm.tmp").replace(rec / f"{name}.webm")
    return rec / f"{name}.webm"


def read_f32(path):
    return np.fromfile(path, dtype=np.float32)


def clean(build_dir, name, profile):
    """The session's voice cleaned with `profile`, as raw 48 kHz mono float32 (cached per profile)."""
    rec = recdir(build_dir)
    out = rec / f"{name}.{profile}.f32"
    webm = rec / f"{name}.webm"
    if out.exists() and out.stat().st_mtime >= webm.stat().st_mtime:
        return out
    with tempfile.TemporaryDirectory() as tmp:
        if profile == "deepfilter":
            src, chain = deepfilter(webm, Path(tmp)), CLEAN[profile]
        else:
            src, chain = webm, f"aresample=async=1:first_pts=0,{CLEAN[profile]}"
        ff("-i", src, "-af", chain, "-ac", "1", "-ar", SR, "-f", "f32le", out.with_suffix(".tmp"))
    out.with_suffix(".tmp").replace(out)
    return out


def loudness(f32):
    """Integrated loudness (LUFS) of raw 48 kHz mono float32."""
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(f32),
                        "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    v = float(m["input_i"])
    return v if np.isfinite(v) else -70.0


def level_chain(f32):
    """One fixed gain to the narration's loudness, and a limiter for the few peaks it pushes too high."""
    return f"volume={TARGET - loudness(f32):.2f}dB,alimiter=limit={PEAK:.4f}:level=false:latency=true"


def preview(build_dir, name, f32):
    out = recdir(build_dir) / f"{name}.m4a"
    ff("-f", "f32le", "-ar", SR, "-ac", "1", "-i", f32, "-af", level_chain(f32), "-c:a", "aac", "-b:a", "128k",
       "-movflags", "+faststart", out)
    return out


def silences(x, sr=SR, frame=0.02, min_len=0.4):
    """[(from, to)] in seconds where the voice is quiet for at least `min_len`: frames below a threshold set
    between the room's floor (10th percentile) and the voice (95th), a third of the way up, in dB."""
    n = int(sr * frame)
    if len(x) < n:
        return []
    f = x[: len(x) // n * n].reshape(-1, n)
    db = 10 * np.log10(np.mean(f * f, axis=1) + 1e-12)
    floor, voice = np.percentile(db, 10), np.percentile(db, 95)
    quiet = db < floor + (voice - floor) / 3
    out, start = [], None
    for i, q in enumerate(np.append(quiet, False)):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) * frame >= min_len:
                out.append((round(start * frame, 3), round(i * frame, 3)))
            start = None
    return out


def process(build_dir, name, profile="deepfilter"):
    """Everything the editor needs from a session: the joined recording, its cleaned voice, the preview copy,
    its pauses. Returns the session's length in seconds."""
    rec = recdir(build_dir)
    assemble(build_dir, name)
    f32 = clean(build_dir, name, profile)
    preview(build_dir, name, f32)
    x = read_f32(f32)
    (rec / f"{name}.silence.json").write_text(json.dumps(silences(x)))
    return len(x) / SR


def original(build_dir):
    """The lecture video's own narration, for lines nobody recorded: presenter/original.f32 (for the export) and
    presenter/original.m4a (the preview), both remade when the video is newer."""
    b = Path(build_dir)
    video, f32, m4a = b / f"{b.name}.mp4", b / "presenter" / "original.f32", b / "presenter" / "original.m4a"
    if not (f32.exists() and m4a.exists() and f32.stat().st_mtime >= video.stat().st_mtime):
        ff("-i", video, "-vn", "-ac", 1, "-ar", SR, "-f", "f32le", f32.with_suffix(".tmp"))
        f32.with_suffix(".tmp").replace(f32)
        ff("-i", video, "-vn", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", m4a)
    return f32, m4a


def source_f32(build_dir, src, profile):
    return original(build_dir)[0] if src == T.ORIGINAL else clean(build_dir, src, profile)


# ─── the voice level, for the editor's strips ─────────────────────────────
LEVEL_STEP = 0.02                                 # seconds per level value
LEVEL_FLOOR = -80                                 # dB: digital silence reads as this


def level_source(build_dir, src, profile):
    """(the voice file to measure, where its levels are cached). A session: its voice cleaned with `profile`, else
    any other cleaned copy (whatever the editor has to play); the lecture's own narration: presenter/original.f32."""
    b = Path(build_dir)
    if src == T.ORIGINAL:
        return original(b)[0], b / "presenter" / "original.levels.json"
    rec = recdir(b)
    f32 = rec / f"{src}.{profile}.f32"
    if not f32.exists():
        found = sorted(rec.glob(f"{src}.*.f32"))
        if not found:
            raise KeyError(f"no voice for session {src}")
        f32 = found[0]
    return f32, f32.with_suffix(".levels.json")


def level_db(f32, step=LEVEL_STEP, sr=SR, block=1 << 24):
    """The level of a raw float32 file as whole dB, one value per `step` seconds: RMS over each window, 20 log10,
    floored at LEVEL_FLOOR (a trailing part of a window is dropped). Read in blocks, so a 35-minute file stays
    in a few tens of MB."""
    n = round(step * sr)
    x = np.memmap(f32, dtype=np.float32, mode="r")
    out = []
    for a in range(0, len(x) // n * n, block // n * n):
        f = np.asarray(x[a: min(a + block // n * n, len(x) // n * n)]).reshape(-1, n)
        ms = np.einsum("ij,ij->i", f, f, dtype=np.float64) / n
        out.append(np.rint(np.maximum(10 * np.log10(ms + 1e-30), LEVEL_FLOOR)).astype(np.int16))
    return np.concatenate(out) if out else np.zeros(0, np.int16)


def levels(build_dir, src, profile):
    """{step, db}: the level of a voice source, cached beside it as JSON keyed by the file's mtime (remade when the
    source is newer)."""
    f32, cache = level_source(build_dir, src, profile)
    mtime = f32.stat().st_mtime
    if cache.exists():
        try:
            c = json.loads(cache.read_text())
            if c.get("mtime") == mtime and c.get("step") == LEVEL_STEP:
                return {"step": c["step"], "db": c["db"]}
        except ValueError:
            pass
    out = {"step": LEVEL_STEP, "db": level_db(f32).tolist()}
    tmp = cache.with_suffix(".tmp")
    tmp.write_text(json.dumps({**out, "mtime": mtime}, separators=(",", ":")))
    tmp.replace(cache)
    return out


# ─── the project: lines, takes, the edit list ─────────────────────────────
def lines(build_dir):
    return json.loads((Path(build_dir) / "presenter" / "lines.json").read_text())


_ENDS = {}                                       # (path, mtime) -> seconds: ffprobe once per version of the file


def video_end(build_dir):
    b = Path(build_dir)
    p = b / "presenter" / f"{b.name}_silent.mp4"
    key = (str(p), p.stat().st_mtime)
    if key not in _ENDS:
        _ENDS[key] = duration(p)
    return _ENDS[key]


def session_events(build_dir, name):
    p = recdir(build_dir) / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else []


def all_takes(build_dir, sessions, edits):
    """{line: [take, …]} over every processed session (oldest first); each take carries its edit."""
    starts = [l[0] for l in lines(build_dir)]
    out = {}
    for s in sessions:
        if s["state"] != "ready":
            continue
        ev = session_events(build_dir, s["name"])
        for t in T.takes(s["name"], ev, starts, end=s.get("seconds") or None):
            t["edit"] = edits.get(t["id"], {})
            t["rejected"] = t["edit"].get("rejected", t["rejected"])
            out.setdefault(t["line"], []).append(t)
    return out


def chosen_take(takes_of_line, choice):
    """The take the line uses: the chosen one, else the newest that is not rejected."""
    by_id = {t["id"]: t for t in takes_of_line}
    if choice in by_id:
        return by_id[choice]
    ok = [t for t in takes_of_line if not t["rejected"] and not t["edit"].get("deleted")]
    return ok[-1] if ok else None


def project_edit_list(build_dir, sessions, edits, choices, speed=1 / 1.1, fallback="silent"):
    ls = lines(build_dir)
    tk = all_takes(build_dir, sessions, edits)
    events = {s["name"]: session_events(build_dir, s["name"]) for s in sessions}
    chosen = {}
    for k in range(len(ls)):
        t = chosen_take(tk.get(k, []), choices.get(k))
        if t is not None:
            chosen[k] = dict(T.edited(t, events[t["session"]], t["edit"], speed), id=t["id"])
    return T.edit_list([l[0] for l in ls], video_end(build_dir), chosen, speed, fallback), tk


# ─── chapters ─────────────────────────────────────────────────────────────
def section_titles(build_name, narration_dir=HERE / "narration"):
    """{section number: title} from the build's narration headings, in the build's language."""
    m = BUILD.fullmatch(build_name)
    if not m:
        return {}
    stem = (f"m{m[1]}_" if m[1] else "") + f"lecture{m[2]}"
    en = m[3] == "en"
    single = narration_dir / f"{stem}_en.md"
    path = single if en and single.exists() else narration_dir / f"{stem}.md"
    if not path.exists():
        return {}
    out = {}
    for row in path.read_text().splitlines():
        a = re.match(r"### (\d+)-boʻlim · Section \d+ — (.+?) · (.+?)(?:\s+\*\(.*)?$", row)
        b = re.match(r"### Section\s*(\d+)\s*[—–-]\s*(.+?)\s*$", row)
        if a:
            out[int(a[1])] = f"Section {a[1]} · {a[3]}" if en else f"{a[1]}-boʻlim · {a[2]}"
        elif b:
            out[int(b[1])] = f"Section {b[1]} · {b[2]}"
    return out


def line_sections(build_dir):
    """{line: section number} for the first line of each section, from the scene each line belongs to
    (scene classes are named S01…, S02…: the number is the section)."""
    parts = [Path(r.split("'")[1]).stem for r in (Path(build_dir) / "parts.txt").read_text().splitlines()
             if r.startswith("file")]
    out, seen = {}, set()
    for k, l in enumerate(lines(build_dir)):
        scene = l[3] if len(l) > 3 else None
        if scene is None or scene >= len(parts):
            continue
        m = re.match(r"S(\d+)", parts[scene])
        sec = int(m[1]) if m else None
        if sec is not None and sec not in seen:
            seen.add(sec)
            out[k] = sec
    return out


# ─── the export ───────────────────────────────────────────────────────────
def voice_track(build_dir, voice, profile):
    """The edit list's voice as one float32 array: each piece sliced sample-exact from its cleaned session (or the
    video's own narration), every source first brought to the narration's loudness, so the instructor's voice and
    the cloned one sit at one level where they alternate."""
    srcs = {}
    for s in {p[1] for p in voice if p[1]}:
        f = source_f32(build_dir, s, profile)
        srcs[s] = read_f32(f) * np.float32(10 ** ((TARGET - loudness(f)) / 20))
    total = round(T.length(voice) * SR)
    out = np.zeros(total, dtype=np.float32)
    t, done = 0.0, 0
    for d, src, pos in voice:
        t += d
        n = round(t * SR) - done
        if src is not None:
            a = round(pos * SR)
            seg = srcs[src][a: a + n]
            out[done: done + len(seg)] = seg
        done += n
    return out


def picture_piece(src, piece, frames, enc, tmp, k):
    f = Path(tmp) / f"{k:05d}.mp4"
    d, kind, a, b, speed = piece
    if frames <= 0:
        return None
    if kind == "play":
        ff("-ss", f"{a:.3f}", "-i", src, "-an", "-vf", f"setpts=PTS/{speed:.6f},fps={FPS}", "-frames:v", frames, *enc, f)
    else:
        png = Path(tmp) / f"{k:05d}.png"
        ff("-ss", f"{max(a - 0.02, 0):.3f}", "-i", src, "-frames:v", 1, png)
        ff("-loop", 1, "-framerate", FPS, "-i", png, "-frames:v", frames, *enc, f)
    return f


def export(build_dir, sessions, edits, choices, profile="deepfilter", out=None, jobs=3, log=print, fallback="silent"):
    """Render the edit list: <out>.mp4, <out>.srt, <out>.chapters.txt. Returns the paths."""
    b = Path(build_dir)
    el, _ = project_edit_list(b, sessions, edits, choices, fallback=fallback)
    out = Path(out or b / "presenter" / "export" / f"{b.name}_edited")
    out.parent.mkdir(parents=True, exist_ok=True)
    src = b / "presenter" / f"{b.name}_silent.mp4"
    enc = video_encoder()
    picture = T.merge_picture(el["picture"])
    frames = T.frame_counts(picture, FPS)
    log(f"{len(picture)} picture pieces, {T.length(picture) / 60:.1f} min")
    with tempfile.TemporaryDirectory() as tmp:
        with ThreadPoolExecutor(jobs) as pool:
            files = list(pool.map(lambda a: picture_piece(src, a[1][0], a[1][1], enc, tmp, a[0]),
                                  enumerate(zip(picture, frames))))
        lst = Path(tmp) / "list.txt"
        lst.write_text("".join(f"file '{f}'\n" for f in files if f))
        ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", Path(tmp) / "picture.mp4")
        voice = voice_track(b, el["voice"], profile)
        vf = Path(tmp) / "voice.f32"
        voice.tofile(vf)
        ff("-i", Path(tmp) / "picture.mp4", "-f", "f32le", "-ar", SR, "-ac", 1, "-i", vf, "-map", "0:v", "-map", "1:a",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", level_chain(vf), "-shortest",
           out.with_suffix(".mp4"))
    texts = [l[1] for l in lines(b)]
    out.with_suffix(".srt").write_text(T.srt(el["lines"], texts))
    titles, opening = section_titles(b.name), "Opening" if b.name.endswith("_en") else "Kirish"
    secs = {k: opening if s == 0 else titles.get(s, f"Section {s}") for k, s in line_sections(b).items()}
    (out.parent / f"{out.name}.chapters.txt").write_text(T.chapters(el["lines"], secs) + "\n")
    return [out.with_suffix(".mp4"), out.with_suffix(".srt"), out.parent / f"{out.name}.chapters.txt"]


# ─── transcripts ──────────────────────────────────────────────────────────
def words(build_dir, takes, profile, lang, python=NAVOIY_PY):
    """Transcribe takes (words with times) and align their lines' approved text, in one run of words_worker.py.
    takes: [(take, script text)]. Writes <session>.words/<t_in>.json per take."""
    rec = recdir(build_dir)
    with tempfile.TemporaryDirectory() as tmp:
        items = []
        for k, (t, text) in enumerate(takes):
            x = read_f32(clean(build_dir, t["session"], profile))
            seg = x[round(t["t_in"] * SR): round(t["t_out"] * SR)]
            raw = Path(tmp) / f"{k}.f32"
            seg.tofile(raw)
            wav = Path(tmp) / f"{k}.wav"
            ff("-f", "f32le", "-ar", SR, "-ac", 1, "-i", raw, "-ar", 16000, wav)
            dest = rec / f"{t['session']}.words" / f"{t['t_in']:.2f}.json"
            dest.parent.mkdir(exist_ok=True)
            items.append({"wav": str(wav), "text": text, "out": str(dest)})
        job = Path(tmp) / "job.json"
        job.write_text(json.dumps({"lang": lang, "items": items}, ensure_ascii=False))
        r = subprocess.run([str(python), str(HERE / "studio" / "words_worker.py"), str(job)], capture_output=True,
                           text=True, cwd=HERE)
        if r.returncode:
            raise RuntimeError((r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "?")


def take_words(build_dir, take):
    p = recdir(build_dir) / f"{take['session']}.words" / f"{take['t_in']:.2f}.json"
    return json.loads(p.read_text()) if p.exists() else None
