"""The agent course's kit: its approved narration, its numbers, and the visuals every section shares.

Narration: narration/agents_course.md, written in English only (parse(..., single="en")); Korean is added beside it
later, keyed the same way. A spoken line may hold {{agents_course/raw/<file>: <field>}}: a result of a live run. The
kit fills it at bind time from that raw file, through SPOKEN below (one rule per file and field), so the voice says
the captured value and nothing is retyped. The screen shows the same value as digits via raw(file)[field].

Numbers that are not live results come from agents_course/raw/deck_numbers.json (capture_deck.py, test_deck.py) and
capture_deck's own inputs (DECK_IN.PRICE_IN, …); the testbed's tool list and policy from raw/tau2_retail_*.

Shared visuals (see agents_course/BUILDING.md): code_panel, highlight, chat_panel, bubble, schema_card, json_block,
tile, flow_row, bars, stack, bullets, recap, pill / run_pill / shown_pill, captured_tag, pause_card_math.
"""
import importlib.util
import json
import re
import textwrap

from lecture_kit import *
from lecture_kit import LectureScene as _BaseScene

COURSE = HERE / "agents_course"
RAWDIR = COURSE / "raw"
CODE = COURSE / "code"
D = json.loads((RAWDIR / "deck_numbers.json").read_text())

_spec = importlib.util.spec_from_file_location("capture_deck", COURSE / "capture_deck.py")
DECK_IN = importlib.util.module_from_spec(_spec)          # capture_deck's inputs (prices, p, …): the slides' numbers
_spec.loader.exec_module(DECK_IN)

MONO = "DejaVu Sans Mono"
LBLUE = "#8C88F0"                  # course blue is dim on black; use this for blue text
DIM = GREY_C


def raw(name):
    """A captured run, e.g. raw("tau2_retail.json")["pass_1"]."""
    return json.loads((RAWDIR / name).read_text())


# ─── numbers for the ear ──────────────────────────────────────────────────
_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen " \
        "seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def words(n):
    """An integer as spoken English: 72 → 'seventy-two', 1000 → 'one thousand'."""
    n = int(n)
    if n < 0:
        return "minus " + words(-n)
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else "-" + _ONES[n % 10])
    if n < 1000:
        return _ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " and " + words(n % 100))
    if n < 1_000_000:
        return words(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + words(n % 1000))
    raise ValueError(n)


def point(x, places=2):
    """0.7667 → 'zero point seven seven', the way the narration reads a rate (cf. 'zero point five nine')."""
    s = f"{x:.{places}f}".rstrip("0").rstrip(".")
    whole, _, frac = s.partition(".")
    return words(int(whole)) + ("" if not frac else " point " + " ".join(_ONES[int(c)] for c in frac))


def percent(x):
    """0.6 → 'sixty percent'."""
    return words(round(100 * x)) + " percent"


def cents(usd):
    """0.2643 → 'twenty-six cents' (under a dollar)."""
    assert usd < 1, usd
    return words(round(100 * usd)) + " cents"


def _pass_hat_k_spoken(d):
    """{'1': .77, '2': .6, '3': .5} → 'zero point six at two trials, and zero point five at three'."""
    ks = sorted((int(k), v) for k, v in d.items() if int(k) > 1)
    parts = [f"{point(v)} at {words(k)} trials" if i == 0 else f"{point(v)} at {words(k)}" for i, (k, v) in enumerate(ks)]
    return ", and ".join(parts) if len(parts) == 2 else ", ".join(parts)


# One rule per placeholder: (how the value is spoken, words after the placeholder that the rule replaces).
SPOKEN = {
    "s1_agent_loop.json: steps": (words, ""),                  # "finished in two tool calls"
    "s1_agent_loop_vague.json: steps": (words, ""),            # "tried three spellings"
    "s2_structured.json: tries": (lambda v: words(len(v)), ""),            # "right on try number two"
    "s2_structured_unhelpful.json: tries": (lambda v: words(len(v)), ""),  # "failed three times in a row"
    "tau2_banking.json: n_tasks": (words, ""),
    "tau2_banking.json: kb_searches": (words, ""),
    "tau2_banking.json: pass_1": (percent, ""),                # "passed sixty percent of the conversations"
    "tau2_retail_trajectory.json: task_id": (words, ""),
    "tau2_retail_trajectory.json: turns": (words, ""),
    "tau2_retail_trajectory.json: tool_calls": (words, ""),
    "tau2_retail_trajectory.json: reward": (words, ""),        # 1.0 → "one"
    "tau2_retail_failure.json: task_id": (words, ""),
    "tau2_retail.json: n_tasks": (words, ""),
    "tau2_retail.json: n_trials": (words, ""),
    "tau2_retail.json: pass_1": (point, ""),                   # "Pass to the one was zero point seven seven"
    "tau2_retail.json: pass_hat_k": (_pass_hat_k_spoken, ""),
    "tau2_retail.json: cost_usd": (cents, " dollars"),         # "{{…cost_usd}} dollars" → "twenty-six cents"
}
_HOLE = re.compile(r"\{\{agents_course/raw/([^:}]+):\s*([^}]+)\}\}")


def resolve(text):
    """Fill every {{agents_course/raw/<file>: <field>}} from its raw file by its SPOKEN rule."""
    def fill(m):
        key = f"{m[1]}: {m[2].strip()}"
        fmt, _ = SPOKEN[key]
        return fmt(raw(m[1])[m[2].strip()])
    for key, (_, tail) in SPOKEN.items():
        if tail:
            f, field = key.split(": ")
            text = re.sub(r"(\{\{agents_course/raw/" + re.escape(f) + r":\s*" + re.escape(field) + r"\}\})"
                          + re.escape(tail), r"\1", text)
    out = _HOLE.sub(fill, text)
    assert "{{" not in out, out
    return out


_LINES, HEADS = parse((HERE / "narration" / "agents_course.md").read_text(), single="en")
NARRATION = {k: {lang: resolve(t) for lang, t in v.items()} for k, v in _LINES.items()}
assert len(HEADS) == 9 and "0.1" in NARRATION and "8.15" in NARRATION and "9.6" in NARRATION

LectureScene, line = bind(_BaseScene, (NARRATION, HEADS), {}, {})
LectureScene.BRAND = False             # presented to other audiences: no tqqt.uz corner mark


# ─── shared visuals ───────────────────────────────────────────────────────
def mono(text, size=22, color=WHITE, weight=NORMAL):
    """Code, ids and JSON as they are: monospace, never a label."""
    return Text(text, font=MONO, font_size=size, color=color, weight=weight, disable_ligatures=True)


def pill(text, color, size=20):
    t = txt(text, size=size, color=color, weight=BOLD)
    r = RoundedRectangle(corner_radius=0.16, width=t.width + 0.4, height=t.height + 0.24, stroke_color=color,
                         stroke_width=2.5)
    return VGroup(r, t.move_to(r))


def run_pill(size=20):
    """Marks code we ran against DeepSeek; what it printed is on screen."""
    return pill(label("ac_run"), GOOD, size)


def shown_pill(size=20):
    """Marks an idea snippet: shown, never run, no output quoted."""
    return pill(label("ac_shown_not_run"), HILITE, size)


def captured_tag(name):
    """'captured: raw/<file>' under a real result, so the viewer knows it is a recording."""
    return VGroup(txt(label("ac_captured"), size=18, color=DIM), mono(f"raw/{name}", size=16, color=DIM)) \
        .arrange(RIGHT, buff=0.15)


def code_lines(fname, start, end=None):
    """(first, last) 1-based line numbers in code/<fname>: from the first line containing `start` to the first
    line after it containing `end` (inclusive), so a panel follows the file if it changes."""
    rows = (CODE / fname).read_text().splitlines()
    a = next(i for i, r in enumerate(rows) if start in r)
    b = a if end is None else next(i for i in range(a, len(rows)) if end in rows[i])
    return a + 1, b + 1


def code_panel(fname, start, end=None, size=24, width=12.5, tag=None):
    """Lines of the real file code/<fname> (or a path under video/agents_course/), syntax highlighted, with their
    true line numbers and the file name on top. tag: "run" or "shown". At most 18 lines.

    The panel uses the frame: it is as large as fits in `width` units and the frame's height, so short lines get a
    big font (up to ~44 px capitals at 1080p) and only long lines shrink it (at size 24 a capital is 33 px; a
    ~95-character line still gets ~21 px). Centred; move it if the scene needs room beside it.
    Returns a VGroup(title, code); code.code_lines[i] is the i-th shown line (for highlight())."""
    path = CODE / fname if (CODE / fname).exists() else COURSE / fname
    rows = path.read_text().splitlines()
    first, last = code_lines(fname, start, end) if isinstance(start, str) else (start, end or start)
    assert last - first + 1 <= 18, f"{fname}: {last - first + 1} lines is too many for one panel"
    snippet = "\n".join(rows[first - 1:last])
    code = Code(code_string=snippet, language="python", formatter_style="monokai", add_line_numbers=True,
                line_numbers_from=first, background="window",
                background_config={"stroke_color": GREY_D, "fill_color": "#1b1b1f"},
                paragraph_config={"font": MONO, "font_size": size})
    code.scale(min(width / code.width, 6.3 / code.height, 32 / size))
    code.code_lines.set_z_index(2)          # text above a highlight(), which sits above the window
    code.line_numbers.set_z_index(2)
    title = VGroup(mono(fname, size=24, color=GREY_B))
    if tag:
        title.add(run_pill(18) if tag == "run" else shown_pill(18))
        title.arrange(RIGHT, buff=0.3)
    title.next_to(code, UP, buff=0.15, aligned_edge=LEFT)
    g = VGroup(title, code).move_to(DOWN * 0.1)
    g.first_line = first
    return g


def highlight(panel, file_line, color=HILITE, last=None):
    """A box around real line numbers file_line..last of a code_panel: one line pitch tall per line (so it never
    reaches the neighbouring lines), behind the text, a faint fill of `color`."""
    code = panel[1]
    i, j = file_line - panel.first_line, (last or file_line) - panel.first_line
    lines = code.code_lines
    rows = VGroup(*lines[i:j + 1])
    if len(lines) > 1:
        pitch = abs(lines[0].get_center()[1] - lines[1].get_center()[1])
    else:
        pitch = lines[0].height * 1.6
    top = lines[i].get_center()[1] + pitch * 0.47
    bottom = lines[j].get_center()[1] - pitch * 0.47
    left = min(l.get_left()[0] for l in lines if len(l)) - 0.1
    right = rows.get_right()[0] + 0.12
    r = Rectangle(width=right - left, height=top - bottom, stroke_color=color, stroke_width=2.5,
                  fill_color=color, fill_opacity=0.14).move_to([(left + right) / 2, (top + bottom) / 2, 0])
    r.set_z_index(1)
    return r


def json_block(obj, size=20, width=None, color=WHITE, chars=56):
    """A real JSON value (a tool call's arguments, a request) as compact monospace lines of at most `chars`."""
    s = json.dumps(obj, ensure_ascii=False)
    rows = textwrap.wrap(s, chars) or [s]
    g = VGroup(*[mono(r, size=size, color=color) for r in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    if width and g.width > width:
        g.scale_to_fit_width(width)
    return g


def _wrap(text, n):
    out = []
    for para in str(text).replace("**", "").split("\n"):
        out += textwrap.wrap(para, n) or []
    return out


def bubble(role, text, max_chars=46, max_rows=4, size=20):
    """One message of a real conversation. role: 'user' (customer, left), 'assistant' (agent, right),
    'call' (a tool call, monospace), 'tool' (a tool result, monospace, dim). Long text is cut with '…'."""
    rows = _wrap(text, max_chars)
    if len(rows) > max_rows:
        rows = rows[:max_rows]
        rows[-1] = rows[-1][: max_chars - 1] + "…"
    font = MONO if role in ("call", "tool") else None
    color = {"user": WHITE, "assistant": WHITE, "call": HILITE, "tool": GREY_B}[role]
    lines = VGroup(*[Text(r, font=font, font_size=size - (2 if font else 0), color=color, disable_ligatures=True)
                     if font else txt(r, size=size, color=color) for r in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    edge = {"user": GREY_B, "assistant": LBLUE, "call": HILITE, "tool": GREY_D}[role]
    box = RoundedRectangle(corner_radius=0.15, width=lines.width + 0.4, height=lines.height + 0.3,
                           stroke_color=edge, stroke_width=2.5, fill_color=BLACK, fill_opacity=0.7)
    g = VGroup(box, lines.move_to(box))
    g.role = role
    return g


def chat_messages(messages):
    """[(role, text)] for bubble(): a real trajectory's messages, each tool call on its own row."""
    out = []
    for m in messages:
        if m.get("content") and m["role"] in ("user", "assistant"):
            out.append((m["role"], m["content"]))
        for c in m.get("tool_calls") or []:
            out.append(("call", f"{c['name']}({json.dumps(c['arguments'], ensure_ascii=False)})"))
        if m["role"] == "tool":
            out.append(("tool", m["content"]))
    return out


def chat_panel(rows, width=11.5, size=20, max_rows=3, buff=0.18):
    """Bubbles for (role, text) rows, customer on the left, agent and its calls on the right, top to bottom."""
    bs = VGroup(*[bubble(r, t, max_rows=max_rows, size=size) for r, t in rows]).arrange(DOWN, buff=buff)
    for b in bs:
        if b.width > width * 0.8:
            b.scale_to_fit_width(width * 0.8)
        b.align_to(LEFT * width / 2 if b.role == "user" else RIGHT * width / 2, LEFT if b.role == "user" else RIGHT)
    return bs


def tool(name):
    """A τ²-bench retail tool's record: {'name', 'type' (READ/WRITE/GENERIC), 'schema'} from raw/tau2_retail_tools.json."""
    return next(t for t in raw("tau2_retail_tools.json")["tools"] if t["name"] == name)


def schema_card(name, show=None, width=8.6, size=20, mark=None):
    """A τ²-bench tool as its schema says it: name, the description's first sentences, and each argument with its
    type (and enum or pattern). show: argument names to list (default all). mark: a phrase of the description to
    colour (the part the narration points at)."""
    f = tool(name)["schema"]["function"]
    head = mono(f["name"], size=size + 4, color=HILITE, weight=BOLD)
    desc = " ".join(f["description"].split())
    rows = _wrap(desc, 62)[:5]
    body = VGroup(*[txt(r, size=size - 2, color=GREY_A) for r in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    if mark:
        for r, t in zip(rows, body):
            if mark in r:
                t.set_color(HILITE)
    params = f["parameters"]["properties"]
    args = VGroup()
    for p, spec in params.items():
        if show and p not in show:
            continue
        typ = spec.get("type", "")
        extra = f" enum {spec['enum']}" if "enum" in spec else (f" pattern {spec['pattern']}" if "pattern" in spec else "")
        args.add(mono(f"{p}: {typ}{extra}", size=size - 2, color=LBLUE))
    if len(args):
        args.arrange(DOWN, aligned_edge=LEFT, buff=0.1)     # one row per argument, not all on one spot
    g = VGroup(head, body, args).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    box = RoundedRectangle(corner_radius=0.15, width=max(g.width + 0.5, 3), height=g.height + 0.45,
                           stroke_color=GREY_B, stroke_width=2.5, fill_color="#1b1b1f", fill_opacity=1)
    out = VGroup(box, g.move_to(box))
    if out.width > width:
        out.scale_to_fit_width(width)
    return out


def tile(text, color=RLBLUE, width=None, height=0.9, size=26, text_color=WHITE):
    """A labelled box. Unlike common.box(), the words keep their font size (shrunk only if they would not fit),
    so a row of tiles reads as one size; the box grows to the words unless width is given."""
    t = txt(text, size=size, color=text_color)
    w = width or t.width + 0.6
    if t.width > w - 0.3:
        t.scale_to_fit_width(w - 0.3)
    r = RoundedRectangle(corner_radius=0.12, width=w, height=max(height, t.height + 0.3), stroke_color=color,
                         stroke_width=3)
    return VGroup(r, t.move_to(r))


def flow_row(items, color=RLBLUE, size=24, buff=0.7, width=None, height=0.9):
    """Tiles left to right with arrows between: items are label strings (tile()) or ready mobjects."""
    boxes = VGroup(*[tile(i, color=color, width=width, height=height, size=size) if isinstance(i, str) else i
                     for i in items]).arrange(RIGHT, buff=buff)
    arrows = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.08, color=GREY_B, stroke_width=4,
                            max_tip_length_to_length_ratio=0.3) for a, b in zip(boxes, boxes[1:])])
    return boxes, arrows


def bars(pairs, fmt, height=3.2, width=0.9, step=1.6, base=-2.3, color=LBLUE, vmax=None, size=26):
    """[(label mobject or str, value)] as bars on a floor, the value above each (fmt(value)), the label below."""
    vmax = vmax or max(v for _, v in pairs)
    k = height / vmax
    xs = [(i - (len(pairs) - 1) / 2) * step for i in range(len(pairs))]
    rects = VGroup(*[Rectangle(width=width, height=max(v * k, 1e-3), stroke_width=0, fill_color=color,
                               fill_opacity=1).move_to([x, base + v * k / 2, 0]) for x, (_, v) in zip(xs, pairs)])
    tops = VGroup(*[txt(fmt(v), size=size, weight=BOLD).next_to(r, UP, buff=0.12) for r, (_, v) in zip(rects, pairs)])
    labs = VGroup(*[(txt(l, size=size - 4, color=GREY_B) if isinstance(l, str) else l).next_to([x, base, 0], DOWN, buff=0.2)
                    for x, (l, _) in zip(xs, pairs)])
    floor = Line([xs[0] - width, base, 0], [xs[-1] + width, base, 0], color=GREY_B, stroke_width=2)
    return rects, tops, labs, floor


def stack(texts, width=6.4, height=0.62, size=24, colors=None, buff=0.1):
    """Labelled bars stacked bottom-up (texts[0] at the bottom): the course road map, the layers of a system."""
    colors = colors or [RLBLUE] * len(texts)
    words_ = [txt(t, size=size) for t in texts]
    k = min(1, *[(width - 0.4) / w.width for w in words_])          # one font size for every row
    rows = VGroup()
    for w, c in zip(words_, colors):
        r = RoundedRectangle(corner_radius=0.12, width=width, height=height, stroke_color=c, stroke_width=3)
        rows.add(VGroup(r, w.scale(k).move_to(r)))
    rows.arrange(UP, buff=buff)
    return rows


def bullets(texts, size=30, buff=0.35, mark=HILITE):
    """A recap: one line per idea, a small square in front of each."""
    rows = VGroup(*[VGroup(Square(0.16, fill_color=mark, fill_opacity=1, stroke_width=0), txt(t, size=size))
                    .arrange(RIGHT, buff=0.3) for t in texts]).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    return rows


def recap(scene, key, texts, size=30):
    """The section's last line: the recap bullets appear one by one with the line's sentences."""
    rows = bullets(texts, size=size)
    if rows.width > 12:
        rows.scale_to_fit_width(12)
    head = scene.heading(label("ac_recap"), color=HILITE)
    with scene.say(key) as (tr, t):
        scene.play(FadeIn(head), run_time=0.4)
        for r in rows:
            scene.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
    scene.clear_all()


def pause_card_math(tex, size=44):
    """The pause card with its question as math the languages share (numbers from the data)."""
    head = txt(label("pause"), size=40, weight=BOLD, color=HILITE)
    return VGroup(head, MathTex(tex, font_size=size)).arrange(DOWN, buff=0.6)
