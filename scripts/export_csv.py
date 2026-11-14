"""Export blacklist.txt into blacklist.csv — a comment-free machine-readable copy.

blacklist.txt stays the single source of truth: entries are added there, with
reason after `#`. blacklist.csv is generated from it, so nothing has to be
duplicated by hand; the workflow `.github/workflows/export.yml` regenerates it
on every change and commits the result.

Usage:
    python3 scripts/export_csv.py           # regenerate blacklist.csv
    python3 scripts/export_csv.py --check   # write nothing, exit 1 if stale

CSV layout: one column `entry` (Telegram ID or email), same order as the txt,
no comments, no BOM, LF line endings.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLACKLIST = ROOT / "blacklist.txt"
CSV_PATH = ROOT / "blacklist.csv"

EMAIL_RE = re.compile(r"[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)+")
HEAD_RE = re.compile(r"[\s#]")


def parse(text: str) -> list[str]:
    """Leading token of every non-comment line; the reason after `#` is dropped."""
    entries: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        value = HEAD_RE.split(s, 1)[0].strip()
        if value.isascii() and value.isdigit():
            entries.append(str(int(value)))
        elif EMAIL_RE.fullmatch(value.lower()):
            entries.append(value.lower())
        else:
            raise SystemExit(f"blacklist.txt:{lineno}: not a Telegram ID or email: {value!r}")
    return entries


def render(entries: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["entry"])
    writer.writerows([e] for e in entries)
    return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    entries = parse(BLACKLIST.read_text(encoding="utf-8"))
    expected = render(entries)
    actual = CSV_PATH.read_text(encoding="utf-8") if CSV_PATH.exists() else ""

    print(f"blacklist.txt: {len(entries)} entries "
          f"(ids: {sum(1 for e in entries if e.isdigit())}, "
          f"emails: {sum(1 for e in entries if not e.isdigit())})")

    if a.check:
        if actual != expected:
            print("DRIFT: blacklist.csv is out of date — run `python3 scripts/export_csv.py`",
                  file=sys.stderr)
            return 1
        print("ok: blacklist.csv is up to date")
        return 0

    if actual == expected:
        print("blacklist.csv: unchanged")
        return 0

    CSV_PATH.write_text(expected, encoding="utf-8", newline="")
    print(f"blacklist.csv: written, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
