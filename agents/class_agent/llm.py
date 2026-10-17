"""The model, behind one function: complete(messages, stop) -> the text it writes.

Three modes, so a class demo never depends on the Wi-Fi:
  live     call DeepSeek (OpenAI-compatible API); needs DEEPSEEK_API_KEY in the environment or in .env here
  record   live, and save every reply to traces/<name>.json
  replay   play the saved replies back in order, checking that each prompt is the one that was recorded
"""
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).parent
TRACES = HERE / "traces"
MODEL = "deepseek-flash"             # the module's pinned cheap model (course-map.md, "model and cost baseline")

for line in (HERE / ".env").read_text().splitlines() if (HERE / ".env").exists() else []:
    k, sep, v = line.partition("=")
    if sep and not k.startswith("#") and v.strip():
        os.environ.setdefault(k.strip(), v.strip())


def fingerprint(messages, stop):
    return hashlib.sha256(json.dumps([messages, stop], ensure_ascii=False).encode()).hexdigest()[:16]


class Model:
    def __init__(self, mode="live", name=None):
        self.mode, self.name, self.calls = mode, name, []
        if mode == "replay":
            self.saved = json.loads((TRACES / f"{name}.json").read_text())["calls"]
        else:
            if not os.environ.get("DEEPSEEK_API_KEY"):
                raise SystemExit("no DEEPSEEK_API_KEY: put it in .env here, or replay a recorded run (--replay NAME)")
            from openai import OpenAI
            self.client = OpenAI(base_url="https://api.deepseek.com", api_key=os.environ["DEEPSEEK_API_KEY"])

    def complete(self, messages, stop=None):
        fp = fingerprint(messages, stop)
        if self.mode == "replay":
            n = len(self.calls)
            if n >= len(self.saved) or self.saved[n]["prompt"] != fp:
                raise RuntimeError(f"replay {self.name}: call {n + 1} differs from the recording -- record it again")
            text = self.saved[n]["reply"]
        else:
            r = self.client.chat.completions.create(model=MODEL, messages=messages, stop=stop, temperature=0)
            text = r.choices[0].message.content or ""
        self.calls.append({"prompt": fp, "reply": text})
        return text

    def save(self, extra):
        if self.mode == "record":
            path = TRACES / f"{self.name}.json"           # a name may carry a folder: uk/q1_week
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"model": MODEL, **extra, "calls": self.calls}, ensure_ascii=False, indent=1))
