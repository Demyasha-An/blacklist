"""Close an issue whose Telegram ID or email is already in the blacklist.

GitHub Actions runs this on every issue opened from the ban form. The script
reads `blacklist.txt`, takes the address from the "Telegram ID или email"
field, and if it is already listed, leaves a comment with the stored reason and
closes the issue as not planned.

The issue body is untrusted input: it is only compared with the list and never
passed to a shell.

Usage:
    python3 scripts/check_issue.py 42               # act on issue #42
    python3 scripts/check_issue.py 42 --dry-run     # print the decision only
    python3 scripts/check_issue.py --body-file body.md --title "[BAN] x" --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from export_csv import parse as parse_blacklist

ROOT = Path(__file__).resolve().parent.parent
BLACKLIST = ROOT / "blacklist.txt"

MARKER = "<!-- already-listed -->"
HEADING_RE = re.compile(r"^#{1,6}\s*(.+?)\s*$")
ID_RE = re.compile(r"^[0-9]{4,15}$")
EMAIL_RE = re.compile(r"[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)+")

# "Меня добавили ошибочно" — такие обращения не закрываем автоматически,
# даже если адрес в списке: их разбирает человек.
APPEAL_WORDS = ("апеляц", "апелляц", "ошибочн", "разбан", "ложн", "неверн")


def normalize(value: str) -> str | None:
    """Same normalization as the list: integers without leading zeros, lowercase email."""
    v = value.strip().strip("`'\"<>[]()").rstrip(".,;:")
    if not v or v.startswith("@"):
        return None
    if v.isascii() and v.isdigit() and ID_RE.match(v):
        return str(int(v))
    if EMAIL_RE.fullmatch(v.lower()):
        return v.lower()
    return None


def sections(body: str) -> list[tuple[str, list[str]]]:
    """Split an issue-form body into `### label` blocks."""
    out: list[tuple[str, list[str]]] = []
    label: str | None = None
    buf: list[str] = []
    for raw in body.splitlines():
        m = HEADING_RE.match(raw.strip())
        if m:
            if label is not None:
                out.append((label, buf))
            label, buf = m.group(1).lower(), []
        elif label is not None:
            buf.append(raw)
    if label is not None:
        out.append((label, buf))
    return out


def candidate(body: str) -> str | None:
    """Address from the ID/email field, or a line that is nothing but an address."""
    for label, lines in sections(body):
        if any(hint in label for hint in ("telegram", "email", "почт")):
            for line in lines:
                for token in re.split(r"[\s,;]+", line.strip()):
                    value = normalize(token)
                    if value:
                        return value
    for line in body.splitlines():
        value = normalize(line)
        if value:
            return value
    return None


def load_list() -> dict[str, str]:
    """entry -> reason, using the same parser and validation as the csv export."""
    text = BLACKLIST.read_text(encoding="utf-8")
    parse_blacklist(text)  # fails loudly on a broken list

    reasons: dict[str, str] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        token, _, rest = s.partition("#")
        value = normalize(token)
        if value:
            reasons.setdefault(value, rest.strip())
    return reasons


def gh(*args: str, stdin: str | None = None) -> str:
    proc = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"gh {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def is_ban_request(title: str, labels: list[str]) -> bool:
    return title.strip().startswith("[BAN]") or "blacklist" in labels


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("number", nargs="?", help="issue number")
    ap.add_argument("--body-file", help="issue body from a file instead of the API")
    ap.add_argument("--title", default="", help="issue title for --body-file")
    ap.add_argument("--label", action="append", default=[], help="issue label for --body-file")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.body_file:
        body = Path(a.body_file).read_text(encoding="utf-8")
        title, labels, state = a.title, a.label, "open"
        number = a.number or "-"
        comments: list[str] = []
    else:
        if not a.number:
            ap.error("issue number is required unless --body-file is given")
        raw = gh("issue", "view", a.number, "--json", "number,title,body,state,labels,comments")
        issue = json.loads(raw)
        body, title, state = issue["body"] or "", issue["title"] or "", issue["state"]
        labels = [l["name"] for l in issue["labels"]]
        number = str(issue["number"])
        comments = [c["body"] for c in issue["comments"]]

    if state.lower() != "open":
        print(f"issue #{number}: {state}, nothing to do")
        return 0
    if not is_ban_request(title, labels):
        print(f"issue #{number}: not a ban request, skipped")
        return 0
    if any(word in f"{title}\n{body}".lower() for word in APPEAL_WORDS):
        print(f"issue #{number}: looks like an appeal, left for a human")
        return 0

    value = candidate(body)
    if not value:
        print(f"issue #{number}: no Telegram ID or email found, left for a human")
        return 0

    reasons = load_list()
    if value not in reasons:
        print(f"issue #{number}: {value} is not in the list, left open")
        return 0

    reason = reasons[value] or "причина не указана"
    print(f"issue #{number}: {value} is already listed ({reason})")

    if a.dry_run:
        print("dry run: comment and close skipped")
        return 0

    if not any(MARKER in c for c in comments):
        comment = (
            f"{MARKER}\n"
            f"Запись `{value}` уже есть в списке — причина: «{reason}».\n\n"
            "Заявка закрыта автоматически. Если считаете, что запись попала в список "
            "по ошибке, откройте отдельный issue с объяснением — его разберёт человек."
        )
        gh("issue", "comment", number, "--body-file", "-", stdin=comment)
        print(f"issue #{number}: comment added")

    gh("issue", "close", number, "--reason", "not planned")
    print(f"issue #{number}: closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
