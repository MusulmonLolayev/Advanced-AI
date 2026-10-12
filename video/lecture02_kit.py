"""Lecture 2's kit: its approved narration, its numbers (statistics/raw/l02_numbers.json,
written by capture_l02.py and unit-tested by test_l02.py), the shared lecture pieces bound to
them, and the three pictures several sections reuse: the 100-student grid, the tree, the table.
"""
import json

from lecture_kit import *
from lecture_kit import LectureScene as _BaseScene

N = json.loads((RAW / "l02_numbers.json").read_text())

NARRATION, HEADS = narration(2)
assert len(HEADS) == 10 and "0.0" in NARRATION and "6.5" in NARRATION and "10.10" in NARRATION

PARTS = {0: label("part_0_conditional_probability_and_independence"),
         1: label("part_1_bayes_theorem")}

LectureScene, line = bind(_BaseScene, (NARRATION, HEADS), PARTS, {1: 0, 7: 1})

LBLUE = "#8C88F0"                  # course blue is dim on black; use this for blue text
BUS_C, NOBUS_C, OUT_C = RLORANGE, RLGREEN, GREY_D

BIKE, NOBIKE = label("bike"), label("no_bike")
BUS, NOBUS = label("bus", 1), label("no_bus")
TOTAL = label("total")
STUDENTS = label("students")


def dec(x):
    """0.45, 0.6, 0.25 — a probability as the screen shows it."""
    return f"{x:.2f}".rstrip("0").rstrip(".") if x != int(x) else str(int(x))


def ptex(*parts, size=40, color=WHITE):
    """A probability statement in LaTeX; Uzbek words go through Text, so keep these symbolic."""
    return MathTex(*parts, font_size=size, color=color)


# ─── the 100 students ─────────────────────────────────────────────────────
ORDER = [("bike", "bus"), ("bike", "nobus"), ("nobike", "bus"), ("nobike", "nobus")]


def student_grid(side=0.4, gap=0.07):
    """The 100 students as a 10 × 10 grid, ordered by cell so the 60 bike owners fill the first six
    rows (as in the slide's figure). Orange takes the bus, green does not. Returns the grid and,
    per square, its (bike, bus) pair."""
    who = [k for k in ORDER for _ in range(N["cells"][f"{k[0]}_{k[1]}"])]
    assert len(who) == N["n"] == 100
    sq = VGroup()
    for i, (b, u) in enumerate(who):
        r, c = divmod(i, 10)
        sq.add(Square(side, stroke_width=0, fill_color=BUS_C if u == "bus" else NOBUS_C, fill_opacity=1)
               .move_to([c * (side + gap), -r * (side + gap), 0]))
    sq.move_to(ORIGIN)
    return sq, who


def legend(items, size=24):
    """[(colour, label)] as small swatches in a row."""
    g = VGroup(*[VGroup(Square(0.26, stroke_width=0, fill_color=c, fill_opacity=1), txt(t, size=size))
                 .arrange(RIGHT, buff=0.15) for c, t in items])
    return g.arrange(RIGHT, buff=0.6)


# ─── the tree ─────────────────────────────────────────────────────────────
def node(label, color=RLBLUE, size=24):
    """A tree node: a label, or (value, label) for a count such as 100 students."""
    t = tagged(*label, size=size) if isinstance(label, tuple) else txt(label, size=size)
    r = RoundedRectangle(corner_radius=0.1, width=t.width + 0.4, height=t.height + 0.3, stroke_color=color,
                         stroke_width=2.5, fill_color=BLACK, fill_opacity=0.8)
    return VGroup(r, t.move_to(r))


def tree(root, firsts, seconds, x=(-5.6, -2.2, 1.4), dy1=1.6, dy2=0.8, size=24):
    """A two-stage tree. firsts = [(label, p)] * 2; seconds = [[(label, p)] * 2] * 2.
    Returns a dict of mobjects: root, n1[i], e1[i], p1[i], n2[i][j], e2[i][j], p2[i][j], leaf ends."""
    T = {"root": node(root, size=size).move_to([x[0], 0, 0]), "n1": [], "e1": [], "p1": [],
         "n2": [[], []], "e2": [[], []], "p2": [[], []]}
    for i, (lab, p) in enumerate(firsts):
        y = dy1 if i == 0 else -dy1
        n1 = node(lab, size=size).move_to([x[1], y, 0])
        e = Line(T["root"].get_right(), n1.get_left(), color=GREY_B, stroke_width=2.5)
        pl = MathTex(dec(p), font_size=size + 8, color=HILITE).move_to(e.get_center() + (UP if i == 0 else DOWN) * 0.3)
        T["n1"].append(n1), T["e1"].append(e), T["p1"].append(pl)
        for j, (lab2, p2) in enumerate(seconds[i]):
            y2 = y + (dy2 if j == 0 else -dy2)
            n2 = node(lab2, color=GREY_B, size=size).move_to([x[2], y2, 0])
            e2 = Line(n1.get_right(), n2.get_left(), color=GREY_B, stroke_width=2.5)
            pl2 = MathTex(dec(p2), font_size=size + 8, color=HILITE).move_to(
                e2.get_center() + (UP if j == 0 else DOWN) * 0.25)
            T["n2"][i].append(n2), T["e2"][i].append(e2), T["p2"][i].append(pl2)
    return T


def tree_group(T):
    return VGroup(T["root"], *T["n1"], *T["e1"], *T["p1"],
                  *[m for i in range(2) for m in (*T["n2"][i], *T["e2"][i], *T["p2"][i])])


# ─── the contingency table ────────────────────────────────────────────────
def table(rows, cols, cells, size=30, cw=2.3, ch=0.72, head_w=2.7, totals=True):
    """A contingency table: row labels, column labels, inner counts and margins.
    cells[r][c] are counts. Returns a dict: grid (all), cell[r][c], rowtot[r], coltot[c], grand,
    rowlab[r], collab[c], and row/col/whole rectangles for highlighting denominators."""
    R, C = len(rows), len(cols)
    rt = [sum(cells[r]) for r in range(R)]
    ct = [sum(cells[r][c] for r in range(R)) for c in range(C)]
    nC = C + (1 if totals else 0)
    nR = R + (1 if totals else 0)

    def pos(r, c):                       # r, c index the body; -1 is the header row/column
        x = -((nC * cw + head_w) / 2) + head_w + (c + 0.5) * cw if c >= 0 else -((nC * cw + head_w) / 2) + head_w / 2
        y = ((nR + 1) * ch) / 2 - (r + 1.5) * ch
        return [x, y, 0]

    T = {"cell": [[None] * C for _ in range(R)], "rowtot": [], "coltot": [], "rowlab": [], "collab": []}
    g = VGroup()
    for c, lab in enumerate(cols + ([TOTAL] if totals else [])):
        m = txt(lab, size=size - 4, color=GREY_B, weight=BOLD).move_to(pos(-1, c))
        (T["collab"] if c < C else T.setdefault("tothead", [])).append(m)
        g.add(m)
    for r, lab in enumerate(rows + ([TOTAL] if totals else [])):
        m = txt(lab, size=size - 4, color=GREY_B, weight=BOLD).move_to(pos(r, -1))
        if m.width > head_w - 0.2:
            m.scale_to_fit_width(head_w - 0.2)
        (T["rowlab"] if r < R else T.setdefault("totlab", [])).append(m)
        g.add(m)
    for r in range(R):
        for c in range(C):
            T["cell"][r][c] = txt(str(cells[r][c]), size=size, weight=BOLD).move_to(pos(r, c))
            g.add(T["cell"][r][c])
    if totals:
        for r in range(R):
            T["rowtot"].append(txt(str(rt[r]), size=size, color=LBLUE, weight=BOLD).move_to(pos(r, C)))
        for c in range(C):
            T["coltot"].append(txt(str(ct[c]), size=size, color=LBLUE, weight=BOLD).move_to(pos(R, c)))
        T["grand"] = txt(str(sum(rt)), size=size, color=LBLUE, weight=BOLD).move_to(pos(R, C))
        g.add(*T["rowtot"], *T["coltot"], T["grand"])
        x0 = pos(0, C)[0] - cw / 2
        y0 = pos(R, 0)[1] + ch / 2
        left = pos(0, -1)[0] - head_w / 2
        top = pos(-1, 0)[1] + ch / 2
        g.add(Line([x0, top, 0], [x0, pos(R, 0)[1] - ch / 2, 0], color=GREY_D, stroke_width=2),
              Line([left, y0, 0], [pos(0, C)[0] + cw / 2, y0, 0], color=GREY_D, stroke_width=2))
    g.add(Line([pos(0, -1)[0] + head_w / 2, pos(-1, 0)[1] + ch / 2, 0],
               [pos(0, -1)[0] + head_w / 2, pos(nR - 1, 0)[1] - ch / 2, 0], color=GREY_D, stroke_width=2),
          Line([pos(0, -1)[0] - head_w / 2, pos(-1, 0)[1] - ch / 2, 0],
               [pos(0, nC - 1)[0] + cw / 2, pos(-1, 0)[1] - ch / 2, 0], color=GREY_D, stroke_width=2))
    T["grid"] = g
    T["pos"] = pos
    T["dims"] = (cw, ch, head_w)

    def row_rect(r, color=HILITE):
        a, b = pos(r, 0), pos(r, nC - 1)
        return Rectangle(width=b[0] - a[0] + cw, height=ch * 0.95, stroke_color=color, stroke_width=4).move_to(
            [(a[0] + b[0]) / 2, a[1], 0])

    def col_rect(c, color=HILITE):
        a, b = pos(0, c), pos(nR - 1, c)
        return Rectangle(width=cw * 0.95, height=a[1] - b[1] + ch, stroke_color=color, stroke_width=4).move_to(
            [a[0], (a[1] + b[1]) / 2, 0])

    def body_rect(color=HILITE):
        a, b = pos(0, 0), pos(R - 1, C - 1)
        return Rectangle(width=b[0] - a[0] + cw, height=a[1] - b[1] + ch, stroke_color=color, stroke_width=4).move_to(
            [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0])

    T["row_rect"], T["col_rect"], T["body_rect"] = row_rect, col_rect, body_rect
    return T


def bike_bus_table(**kw):
    c = N["cells"]
    return table([BIKE, NOBIKE], [BUS, NOBUS],
                 [[c["bike_bus"], c["bike_nobus"]], [c["nobike_bus"], c["nobike_nobus"]]], **kw)
