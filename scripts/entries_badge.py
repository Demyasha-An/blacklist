"""Refresh `badges/entries.json` — the number behind the README badge.

The badge is a shields.io endpoint badge, so the count lives in the repo next to
the data instead of in a hand-edited URL. `.github/workflows/export.yml` runs
this right after the csv export, on pushes to `main` only: a pull request must
not rewrite files.

Usage:
    python3 scripts/entries_badge.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "blacklist.csv"
BADGE_PATH = ROOT / "badges" / "entries.json"


def main() -> int:
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        entries = sum(1 for _ in csv.DictReader(f))

    badge = {
        "schemaVersion": 1,
        "label": "entries",
        "message": f"{entries:,}".replace(",", " "),
        "color": "blue",
    }
    rendered = json.dumps(badge, ensure_ascii=False) + "\n"

    current = BADGE_PATH.read_text(encoding="utf-8") if BADGE_PATH.exists() else ""
    if current == rendered:
        print(f"badges/entries.json: unchanged ({entries} entries)")
        return 0

    BADGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BADGE_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"badges/entries.json: written, {entries} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
