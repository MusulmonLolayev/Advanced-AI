"""The editor's logic, pure (no files, no ffmpeg), so every rule is unit-tested (test_timeline.py).

A recording session is one continuous microphone recording with a list of events, each
[seconds since the recording began, kind, video position, playback speed, (line)]:
  play / hold / stop   the picture started, stopped, the recording ended (as compose_recording.py reads them)
  line                 the presenter started narration line k (the 5th field), at video position starts[k]
  retake               the instructor pressed X: the take of the line on screen is a mistake
A take is one line's stretch of a session: from its "line" event to the next "line", "retake" or "stop".

A take becomes two tracks of the same length, cut and nudged together:
  voice    [(seconds, session or None, position in that session)]       None: silence
  picture  [(seconds, "play", from, to, speed) | (seconds, "hold", position, None, 1)]
The lecture's edit list is every line's chosen take, in order; a line with no take shows its own picture with no
voice. The browser preview plays these tracks; media.export renders exactly the same tracks.
"""
import difflib
import re
import unicodedata

MARKERS = ("line", "retake")
EPS = 0.02                                      # spans shorter than this are not worth a play (held, never dropped)
LINE_TOL = 0.08                                 # a "play" this close to a line's start began that line (old recordings)


def segments(events):
    """[(kind, start position, end position or None, seconds, speed)] of the picture between successive events:
    'play' runs it at its speed, 'hold' freezes a frame. Marker events (line, retake) do not change the picture.
    No time is lost: the seconds add up to the last event minus the first (a span of EPS or less is held, not
    dropped, or the picture would run short of the voice)."""
    evs = [e for e in events if e[1] not in MARKERS]
    out = []
    for (t, kind, pos, *r), (t2, _, pos2, *_) in zip(evs, evs[1:]):
        span, speed = t2 - t, (r[0] if r else 1)
        if span <= 0:
            continue
        if span <= EPS:
            out.append(("hold", pos, None, span, 1))
        elif kind == "play" and pos2 > pos:
            run = min(pos2 - pos, span * speed)                    # video seconds shown in this span
            out.append(("play", pos, pos + run, run / speed, speed))
            if span - run / speed > 1e-9:
                out.append(("hold", pos + run, None, span - run / speed, 1))
        else:
            out.append(("hold", pos, None, span, 1))
    return out


def line_events(events, starts):
    """Events with a "line" marker for each line start. New recordings carry them; older ones are given one at
    every "play" that begins at a line's start position."""
    if any(e[1] == "line" for e in events):
        return sorted(events, key=lambda e: e[0])
    out = []
    for e in sorted(events, key=lambda e: e[0]):
        if e[1] == "play":
            k = min(range(len(starts)), key=lambda j: abs(starts[j] - e[2]), default=None)
            if k is not None and abs(starts[k] - e[2]) <= LINE_TOL:
                if not (out and out[-1][1] == "line" and out[-1][4] == k and e[0] - out[-1][0] < 0.5):
                    out.append([e[0], "line", e[2], e[3] if len(e) > 3 else 1, k])
        out.append(list(e))
    return out


def takes(session, events, starts, end=None):
    """[{id, session, line, t_in, t_out, rejected}] for one session. `end` is where the audio stops (a recording
    that crashed has no "stop"); the last take ends there."""
    evs = line_events(events, starts)
    last = max([e[0] for e in evs] + [end or 0])
    out, cur = [], None
    for e in evs:
        if e[1] in ("line", "retake", "stop") and cur is not None:
            cur["t_out"] = e[0]
            cur["rejected"] = e[1] == "retake"
            if cur["t_out"] - cur["t_in"] > EPS:
                out.append(cur)
            cur = None
        if e[1] == "line" and 0 <= e[4] < len(starts):
            cur = {"session": session, "line": e[4], "t_in": e[0], "rejected": False}
    if cur is not None and last - cur["t_in"] > EPS:
        cur.update(t_out=last)
        out.append(cur)
    for t in out:
        t["id"] = take_id(session, t["t_in"])
    return out


def take_id(session, t_in):
    return f"{session}@{t_in:.2f}"


def take_tracks(take, events, speed=1 / 1.1):
    """The take's two tracks, before any edit: the voice runs straight through; the picture is what was on screen."""
    t0, t1 = take["t_in"], take["t_out"]
    evs = [e for e in sorted(events, key=lambda e: e[0]) if e[1] not in MARKERS]
    before = [e for e in evs if e[0] <= t0]
    inside = [e for e in evs if t0 < e[0] < t1]
    state = before[-1] if before else [t0, "hold", 0, speed]
    first = [t0, state[1] if state[1] != "stop" else "hold", state[2], state[3] if len(state) > 3 else 1]
    if state[1] == "play":                       # playing since earlier: where it has got to by t0
        first[2] = min(state[2] + (t0 - state[0]) * first[3], inside[0][2] if inside else 1e9)
    picture = [(d, k, a, b, s) for k, a, b, d, s in segments([first] + inside + [[t1, "stop", 0, 1]])]
    return {"voice": [(t1 - t0, take["session"], t0)], "picture": picture}


def length(track):
    return sum(p[0] for p in track)


def _split(piece, at, voice):
    """A piece cut at local time `at` (0 < at < its length) into two."""
    d = piece[0]
    if voice:
        _, src, pos = piece
        return (at, src, pos), (d - at, src, None if src is None else pos + at)
    _, kind, a, b, s = piece
    if kind == "play":
        m = a + at * s
        return (at, "play", a, m, s), (d - at, "play", m, b, s)
    return (at, "hold", a, None, 1), (d - at, "hold", a, None, 1)


def cut(track, spans, voice):
    """The track with the local-time spans [(from, to)] removed (both tracks get the same spans, so they stay
    in step)."""
    out, t = [], 0.0
    spans = merge(spans)
    for p in track:
        a, b = t, t + p[0]
        t = b
        keep = [(a, b)]
        for x, y in spans:
            keep = [z for (u, v) in keep for z in ((u, min(v, x)), (max(u, y), v)) if z[1] - z[0] > 1e-9]
        for u, v in keep:
            q = p
            if u > a:
                q = _split(q, u - a, voice)[1]
            if v < b:
                q = _split(q, v - u, voice)[0]
            if q[0] > 1e-9:                      # a sliver stays: dropping it from one track only would unsync them
                out.append(q)
    return out


def merge(spans):
    out = []
    for a, b in sorted((min(a, b), max(a, b)) for a, b in spans):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        elif b > a:
            out.append((a, b))
    return out


def nudge(tracks, d):
    """Move the voice against the picture by d seconds: d > 0 starts the picture d s later (its first frame held),
    d < 0 starts the voice |d| s later. The other track is padded at its end, so both keep one length."""
    voice, picture = list(tracks["voice"]), list(tracks["picture"])
    if abs(d) < 1e-3 or not picture:
        return {"voice": voice, "picture": picture}
    first, last = picture[0], picture[-1]
    first_pos = first[2]
    last_pos = last[3] if last[1] == "play" else last[2]
    if d > 0:
        picture.insert(0, (d, "hold", first_pos, None, 1))
        voice.append((d, None, None))
    else:
        voice.insert(0, (-d, None, None))
        picture.append((-d, "hold", last_pos, None, 1))
    return {"voice": voice, "picture": picture}


def edited(take, events, edit, speed=1 / 1.1):
    """A take's tracks with its edit applied: trim in/out, cuts (local seconds), then the nudge."""
    tr = take_tracks(take, events, speed)
    total = length(tr["voice"])
    spans = list(edit.get("cuts", []))
    if edit.get("trim_in"):
        spans.append((0, edit["trim_in"]))
    if edit.get("trim_out"):
        spans.append((total - edit["trim_out"], total))
    tr = {"voice": cut(tr["voice"], spans, True), "picture": cut(tr["picture"], spans, False)}
    return nudge(tr, edit.get("nudge", 0))


def holds(picture):
    """Local-time spans where the picture holds still."""
    out, t = [], 0.0
    for d, kind, *_ in picture:
        if kind == "hold":
            out.append((t, t + d))
        t += d
    return merge(out)


def shrink_silences(silences, picture, total, keep=0.5, keep_end=0.25, min_cut=0.3):
    """Cuts that shorten each silence to `keep` seconds (`keep_end` at the take's end), only where the picture holds
    still: a silence over a running animation is the animation's time, not a gap to remove."""
    still = holds(picture)
    out = []
    for a, b in silences:
        for x, y in still:
            u, v = max(a, x), min(b, y)
            if v - u <= 0:
                continue
            if v >= total - 1e-6:                # the take's tail: keep a short breath after the last word
                lo, hi = u + keep_end, v
            else:                                # inside: keep half the pause on each side
                lo, hi = u + keep / 2, v - keep / 2
            if hi - lo >= min_cut:
                out.append((round(lo, 3), round(hi, 3)))
    return merge(out)


ORIGINAL = "__original__"                        # the lecture video's own narration, as a voice source


def edit_list(starts, video_end, chosen, speed=1 / 1.1, fallback="silent"):
    """The lecture's two tracks and where each line sits in them.
    chosen: {line: tracks of its chosen take} (edited). A line without a take shows its own picture with
    fallback "silent": no voice, at the presenter's speed; or "original": the video's own narration (the cloned or
    synthetic voice), picture and voice as built, at full speed -- so a few recorded lines replace just those lines.
    Returns {"voice": [...], "picture": [...], "lines": [(line, from, to, take id or None)]}."""
    voice, picture, spans, t = [], [], [], 0.0
    own = fallback == "original"
    rate = 1.0 if own else speed
    if starts and starts[0] > EPS:
        d = starts[0] / rate
        voice.append((d, ORIGINAL, 0.0) if own else (d, None, None))
        picture.append((d, "play", 0.0, starts[0], rate))
        t = d
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else video_end
        tr = chosen.get(k)
        if tr is None:
            d = (e - s) / rate
            voice.append((d, ORIGINAL, s) if own else (d, None, None))
            picture.append((d, "play", s, e, rate))
            spans.append((k, t, t + d, None))
            t += d
            continue
        d = length(tr["voice"])
        v, p = list(tr["voice"]), list(tr["picture"])
        gap = d - length(p)
        if abs(gap) > 1e-6:                      # never take the page down over a mismatch: pad the shorter track
            if gap < 0:
                v.append((-gap, None, None))
            else:
                at = (p[-1][3] if p[-1][1] == "play" else p[-1][2]) if p else 0.0
                p.append((gap, "hold", at, None, 1))
        d = length(v)
        voice += v
        picture += p
        spans.append((k, t, t + d, tr.get("id")))
        t += d
    return {"voice": voice, "picture": picture, "lines": spans}


def remap_events(events, old_starts, old_end, new_starts, new_end):
    """A session's events moved onto a rebuilt video whose lines kept their order and number but not their timings
    (one section re-rendered after a line was rewritten): a position inside old line k keeps its offset from that
    line's start, clipped to the new line's length. Wall-clock times do not change, so the voice stays where it was."""
    if len(old_starts) != len(new_starts):
        raise ValueError("the line count changed: these recordings cannot follow")
    olds, news = list(old_starts) + [old_end], list(new_starts) + [new_end]

    def move(pos):
        k = max(0, min(len(old_starts) - 1, sum(1 for s in old_starts if s <= pos + 1e-6) - 1))
        off = pos - olds[k]
        return round(news[k] + max(0.0, min(off, news[k + 1] - news[k] - 0.04)), 4)
    return [[e[0], e[1], move(e[2]), *e[3:]] for e in events]


def placed(track):
    """[(start, piece)] on the track's own clock."""
    out, t = [], 0.0
    for p in track:
        out.append((round(t, 6), p))
        t += p[0]
    return out


def frame_counts(track, fps=60):
    """Frames per piece, rounded on the running total, so a hundred pieces never drift a frame from the voice."""
    out, t, done = [], 0.0, 0
    for p in track:
        t += p[0]
        n = round(t * fps) - done
        out.append(n)
        done += n
    return out


def merge_picture(track):
    """Adjacent pieces that continue each other (a play running on at one speed; one held frame) as one piece."""
    out = []
    for p in track:
        if out:
            q = out[-1]
            if p[1] == q[1] == "hold" and abs(p[2] - q[2]) < 1e-6:
                out[-1] = (q[0] + p[0], "hold", q[2], None, 1)
                continue
            if p[1] == q[1] == "play" and abs(p[4] - q[4]) < 1e-9 and abs(p[2] - q[3]) < 1e-3:
                out[-1] = (q[0] + p[0], "play", q[2], p[3], q[4])
                continue
        out.append(p)
    return out


def stamp(t, sep=","):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}"


def srt(spans, texts, width=42):
    """Subtitles: each line's approved text over its place in the final video, two rows at most per card (a long
    line is split into cards at sentence or comma breaks, each shown for its share of the characters)."""
    out, n = [], 0
    for k, a, b, _ in spans:
        cards = cards_of(texts[k], width)
        total = sum(len(c) for c in cards) or 1
        t = a
        for c in cards:
            d = (b - a) * len(c) / total
            n += 1
            out.append(f"{n}\n{stamp(t)} --> {stamp(t + d)}\n{wrap2(c, width)}\n")
            t += d
    return "\n".join(out)


def cards_of(text, width):
    parts = [p for p in re.split(r"(?<=[.?!:;])\s+", text.strip()) if p]
    out = []
    for p in parts:
        while len(p) > 2 * width:
            cut_at = p.rfind(", ", 0, 2 * width)
            cut_at = cut_at + 1 if cut_at > width // 2 else p.rfind(" ", 0, 2 * width)
            out.append(p[:cut_at].strip())
            p = p[cut_at:].strip()
        out.append(p)
    return out


def wrap2(text, width):
    if len(text) <= width:
        return text
    mid = len(text) // 2
    left, right = text.rfind(" ", 0, mid + 1), text.find(" ", mid)
    i = left if right < 0 or (left >= 0 and mid - left <= right - mid) else right
    return text[:i] + "\n" + text[i + 1:] if i > 0 else text


def chapters(spans, sections):
    """YouTube chapters: 'm:ss Title' at the first line of each section ({line: title}); the first is at 0:00."""
    out = []
    for k, a, _, _ in spans:
        if k in sections:
            t = 0 if not out else a
            out.append(f"{int(t // 60)}:{int(t % 60):02d} {sections[k]}")
    return "\n".join(out)


def norm_words(text):
    t = unicodedata.normalize("NFKC", text.lower())
    t = re.sub(r"[ʻʼ'`’‘]", "", t)
    return re.sub(r"[^\w ]+", " ", t).split()


def script_check(script, heard):
    """The approved text against what was heard ([(word, start, end)]). Returns three lists:
      missing  script words with nothing heard in their place          [(index, word)]
      extra    words heard between script words: an "um", a repeat    [(index, word, start, end)]  (safe to cut)
      changed  script words heard as something else                   [(script words, heard words, start, end)]
    A recogniser mishears; a word it heard differently is shown, never cut: only `extra` is offered for cutting."""
    s = norm_words(script)
    h = [(w2, a, b) for w, a, b in heard for w2 in norm_words(w)[:1]]
    sm = difflib.SequenceMatcher(None, s, [w for w, _, _ in h], autojunk=False)
    missing, extra, changed = [], [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "delete":
            missing += [(i, s[i]) for i in range(i1, i2)]
        elif op == "insert":
            extra += [(j, h[j][0], h[j][1], h[j][2]) for j in range(j1, j2)]
        elif op == "replace":
            changed.append((" ".join(s[i1:i2]), " ".join(w for w, _, _ in h[j1:j2]), h[j1][1], h[j2 - 1][2]))
    return missing, extra, changed
