"""Shared by the two runnable examples: the DeepSeek client, the
τ²-bench retail database, and --capture."""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE.parent / "raw"
# τ²-bench v1.0.1, MIT
RETAIL_DB = HERE.parent / "tau2-bench/data/tau2/domains/retail/db.json"

for line in ((HERE / ".env").read_text().splitlines()
             if (HERE / ".env").exists() else []):
    k, sep, v = line.partition("=")  # real env variables win over .env
    if sep and not k.startswith("#") and v.strip():
        os.environ.setdefault(k.strip(), v.strip())

MODEL = os.environ.get("DEEPSEEK_MODEL") or "deepseek-v4-flash"


def client():
    from openai import OpenAI
    if not os.environ.get("DEEPSEEK_API_KEY"):
        sys.exit("Set DEEPSEEK_API_KEY (environment or code/.env).")
    return OpenAI(base_url="https://api.deepseek.com",
                  api_key=os.environ["DEEPSEEK_API_KEY"])


def retail_db():
    return json.loads(RETAIL_DB.read_text())


def capture(name, result):
    """--capture: save the real run so the video shows what actually
    happened."""
    if "--capture" in sys.argv:
        RAW.mkdir(exist_ok=True)
        (RAW / f"{name}.json").write_text(
            json.dumps(result, indent=1, ensure_ascii=False))
        print(f"saved raw/{name}.json")
