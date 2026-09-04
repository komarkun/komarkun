#!/usr/bin/env python3
"""Refresh the auto-generated blocks in README.md.

Two blocks, delimited by HTML comment markers, are regenerated in place:

    <!-- STATUS:START -->   ... from scripts/status.config.json + the current UTC time
    <!-- ACTIVITY:START --> ... from the public GitHub events API (public data only)

No secrets are read and no private infrastructure is contacted. If the network
call for activity fails, the existing ACTIVITY block is left untouched so the
README never regresses to an error state.

Run locally with:  python scripts/render_readme.py
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
README = ROOT / "README.md"
CONFIG = SCRIPT_DIR / "status.config.json"

RULE = "─" * 56
MAX_ACTIVITY_ROWS = 6
HTTP_TIMEOUT = 20


def box(title: str, lines: list[str]) -> str:
    """Render a titled, terminal-style block wrapped in a text code fence."""
    header = f"─── {title} " + "─" * max(4, len(RULE) - len(title) - 5)
    body = "\n".join(f"  {line}" if line else "" for line in lines)
    return f"```text\n{header}\n\n{body}\n\n{RULE}\n```"


def render_status(cfg: dict, now: datetime) -> str:
    def joined(key: str) -> str:
        return " · ".join(cfg.get(key, []))

    lines = [
        f"ROLE       {cfg.get('role', '')}",
        f"FOCUS      {joined('focus')}",
        f"BUILDING   {joined('building')}",
        f"OPERATING  {joined('operating')}",
        f"LEARNING   {joined('learning')}",
        "",
        f"updated    {now:%Y-%m-%d %H:%M} UTC — auto-refreshed by GitHub Actions",
    ]
    return box("ENGINEERING STATUS", lines)


def fetch_events(user: str) -> list[dict]:
    url = f"https://api.github.com/users/{user}/events/public"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"{user}-profile-bot",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:  # noqa: S310 - fixed https host
        return json.load(resp)


def describe(event: dict) -> str | None:
    """Turn one public event into a short line, or None to skip it."""
    kind = event.get("type", "")
    payload = event.get("payload", {})
    if kind == "PushEvent":
        n = payload.get("size", 0)
        if n < 1:
            return None
        return f"pushed {n} commit{'s' if n != 1 else ''}"
    if kind == "PullRequestEvent":
        action = payload.get("action", "updated")
        if action == "closed" and payload.get("pull_request", {}).get("merged"):
            action = "merged"
        return f"{action} PR #{payload.get('number', '')}"
    if kind == "ReleaseEvent":
        return f"released {payload.get('release', {}).get('tag_name', '')}".rstrip()
    if kind == "CreateEvent" and payload.get("ref_type") in {"tag", "repository"}:
        return f"created {payload.get('ref_type')}"
    if kind == "IssuesEvent" and payload.get("action") in {"opened", "closed"}:
        return f"{payload.get('action')} an issue"
    return None


def render_activity(user: str) -> str | None:
    try:
        events = fetch_events(user)
    except Exception as exc:  # noqa: BLE001 - network/parse failures are non-fatal
        print(f"activity refresh skipped: {exc}", file=sys.stderr)
        return None

    rows: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    for event in events:
        repo = event.get("repo", {}).get("name", "").split("/")[-1]
        date = (event.get("created_at", "") or "")[:10]
        desc = describe(event)
        if not repo or not desc:
            continue
        key = (date, repo, event.get("type", ""))
        if key in seen:
            continue
        seen.add(key)
        rows.append(f"{date}   {repo:<22} {desc}")
        if len(rows) >= MAX_ACTIVITY_ROWS:
            break

    if not rows:
        rows = ["No public activity in the recent window."]
    return box("RECENT PUBLIC ACTIVITY", rows)


def replace_block(text: str, name: str, new_body: str) -> str:
    pattern = re.compile(
        rf"(<!-- {name}:START -->\n).*?(\n<!-- {name}:END -->)",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise SystemExit(f"marker pair '{name}' not found in README.md")
    return pattern.sub(lambda m: m.group(1) + new_body + m.group(2), text)


def main() -> None:
    now = datetime.now(timezone.utc)
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    text = README.read_text(encoding="utf-8")

    text = replace_block(text, "STATUS", render_status(cfg, now))

    activity = render_activity(cfg.get("github_user", "komarkun"))
    if activity is not None:
        text = replace_block(text, "ACTIVITY", activity)

    README.write_text(text, encoding="utf-8")
    print("README.md refreshed")


if __name__ == "__main__":
    main()
