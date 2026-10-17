"""Build uk_working_time.jsonl: the Working Time Regulations 1998 and the National Minimum Wage Act 1998, one
regulation or section per record, from legislation.gov.uk's XML (the revised, in-force text).

    python data/build_uk_corpus.py DIR      # DIR holds uksi_1998_1833.xml and ukpga_1998_39.xml (see SOURCE_UK.md)

The output is the pinned file; the site's text changes as the law is amended, so we rebuild only on purpose.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "{http://www.legislation.gov.uk/namespaces/legislation}"
DC = "{http://purl.org/dc/elements/1.1/}"
SOURCES = [   # file, our prefix, what a numbered unit is called
    ("uksi_1998_1833.xml", "WTR", "regulation"),
    ("ukpga_1998_39.xml", "NMWA", "section"),
]
SKIP = {"CommentaryRef", "Commentaries", "Pnumber", "Title"}   # editorial notes; numbers and titles are added by us


def flat(e):
    """The text of an element, editorial markers dropped, whitespace collapsed."""
    def walk(x):
        if x.tag.replace(NS, "") in SKIP:
            return x.tail or ""
        return (x.text or "") + "".join(walk(c) for c in x) + (x.tail or "")
    return re.sub(r"\s+", " ", (e.text or "") + "".join(walk(c) for c in e)).strip()


LEVELS = {"P2": "({})", "P3": "({})", "P4": "({})", "P5": "({})"}
MATH = "{http://www.w3.org/1998/Math/MathML}"


def math(e):
    """MathML as one line: a fraction becomes (top) / (bottom)."""
    tag = e.tag.replace(MATH, "")
    if tag == "mfrac":
        top, bottom = (math(c) for c in e)
        return f"({top}) / ({bottom})"
    if tag in ("mi", "mo", "mn"):
        return f" {e.text.strip()} " if tag == "mo" else e.text.strip()
    return "".join(math(c) for c in e)


def render(p1):
    """A provision as text: each numbered subdivision on its own line, (1), (a), (i) kept."""
    lines = []

    def visit(e):
        tag = e.tag.replace(NS, "")
        if tag in LEVELS:
            num = e.find(f"{NS}Pnumber")
            lines.append([LEVELS[tag].format(flat(num)) if num is not None else "", ""])
        elif tag in ("Text", "Para") and not any(c.tag.replace(NS, "") in ("Text",) for c in e):
            t = flat(e)
            if t:
                if lines and not lines[-1][1]:
                    lines[-1][1] = t
                else:
                    lines.append(["", t])
            return
        elif tag == "Formula":
            m = e.find(f".//{MATH}math")
            lines.append(["", re.sub(r"\s+", " ", math(m)).strip() if m is not None else "[formula]"])
            for c in e.find(f"{NS}Where") if e.find(f"{NS}Where") is not None else []:
                visit(c)
            return
        elif tag in SKIP:
            return
        for c in e:
            visit(c)

    for c in p1.find(f"{NS}P1para") if p1.find(f"{NS}P1para") is not None else []:
        visit(c)
    return "\n".join(" ".join(x for x in pair if x) for pair in lines)


def records(path, prefix, unit):
    root = ET.parse(path).getroot()
    title = root.find(f".//{DC}title").text
    body = root.find(f".//{NS}Body")
    parents = {c: p for p in body.iter() for c in p}
    for group in body.iter(f"{NS}P1group"):
        heading = flat(group.find(f"{NS}Title"))
        part, up, inserted = "", parents.get(group), False
        while up is not None:                    # a provision quoted inside an amendment belongs to another act
            inserted |= up.tag == f"{NS}BlockAmendment"
            up = parents.get(up)
        if inserted:
            continue
        up = parents.get(group)
        while up is not None:
            if up.tag == f"{NS}Pblock" and not part:        # the Act's cross-headings stand in for Parts
                part = flat(up.find(f"{NS}Title"))
            if up.tag == f"{NS}Part":
                part = " ".join(filter(None, (flat(up.find(f"{NS}Number")) if up.find(f"{NS}Number") is not None else "",
                                              flat(up.find(f"{NS}Title")) if up.find(f"{NS}Title") is not None else "")))
                break
            up = parents.get(up)
        for p1 in group.findall(f"{NS}P1"):
            num = flat(p1.find(f"{NS}Pnumber")).rstrip(".")
            text = render(p1)
            if not re.search(r"[A-Za-z]{3}", text):          # repealed: only ". . ." is left
                continue
            yield {"code": prefix, "code_title": title, "article_id": f"{prefix} {num}",
                   "article_display": f"{prefix} {unit} {num}", "unit": unit, "number": num,
                   "title": heading, "part": part, "text": text, "uri": p1.get("DocumentURI"),
                   "valid": root.find(".//{http://purl.org/dc/terms/}valid").text}


def main(src):
    out = []
    for f, prefix, unit in SOURCES:
        out.extend(records(Path(src) / f, prefix, unit))
    for i, r in enumerate(out, 1):
        r["seq"] = i
    dest = Path(__file__).parent / "uk_working_time.jsonl"
    dest.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    print(dest, len(out), "records")


if __name__ == "__main__":
    main(sys.argv[1])
