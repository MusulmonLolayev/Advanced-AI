"""Build the small pinned article sample the Lecture 1 assignment ships (data/sample_articles.jsonl).

    python tools/build_sample_articles.py

The sample is every article the recorded runs list or fetch (so the recorded prompts replay), the articles the
class tests quote, and filler: the first FILLER articles of the Code not already chosen, in file order. Because a
search scores each article on its own, a subset that holds a search's full top five reproduces that search exactly;
the replay checks in the assignment prove it. Records are copied byte for byte from class_agent's file.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLASS_AGENT = HERE.parents[1] / "class_agent"
FULL = CLASS_AGENT / "data" / "mehnat_kodeksi.jsonl"
TRACES = ["q1_week", "q1_week_nostop", "q2_under18", "q3_min_wage", "q3_min_wage_steps3"]
QUOTED = ["183", "253", "153", "209"]        # cited in class_agent/test_class_agent.py (the no-tools runs)
FILLER = 15
OUT = HERE.parent / "solutions" / "lecture01_react_loop" / "data" / "sample_articles.jsonl"


def needed_ids():
    ids = set(QUOTED)
    for name in TRACES:
        for turn in json.loads((CLASS_AGENT / "traces" / f"{name}.json").read_text())["trace"]:
            ids.update(re.findall(r"^Art\. (\d+):", turn["observation"] or "", re.M))
            ids.update(re.findall(r"fetch_article\[(\d+)\]", turn["model"]))
    return ids


def build():
    lines = FULL.read_text(encoding="utf-8").splitlines()
    by_id = {json.loads(l)["article_id"]: l for l in lines}
    chosen = needed_ids()
    missing = chosen - set(by_id)
    if missing:
        sys.exit(f"not in the Code: {sorted(missing)}")
    filler = [i for i in by_id if i not in chosen][:FILLER]
    keep = chosen | set(filler)
    return [l for l in lines if json.loads(l)["article_id"] in keep]


if __name__ == "__main__":
    rows = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(len(rows), "articles", hashlib.sha256(OUT.read_bytes()).hexdigest())
