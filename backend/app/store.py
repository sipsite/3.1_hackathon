"""Single module: read -> modify -> dump data.json. All writes go through here."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data.json"


def load() -> dict:
    if not DATA_PATH.exists():
        return {"papers": [], "paper_content": {}, "comments": []}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data: dict) -> None:
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
