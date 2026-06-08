"""Refresh the TradeSignal Africa pane in index.html from the public Telegram channel.

Reads https://t.me/s/<channel>, takes the LATEST message, truncates it, and rewrites
the content between the <!-- TSA:START --> / <!-- TSA:END --> markers in index.html.

Fail-safe: on any fetch error or empty result, makes NO change (last committed snapshot
persists) and exits 0 so CI stays green.
"""
from __future__ import annotations

import html
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

INDEX = Path(__file__).resolve().parent.parent / "index.html"
START = "<!-- TSA:START -->"
END = "<!-- TSA:END -->"
MAX_LINES = 12
NOTICE = "… view full signal on Telegram"


def fetch_latest_message(channel: str, *, _html: str | None = None) -> str | None:
    """Return the latest channel message as plain text (with newlines), or None."""
    if _html is None:
        resp = requests.get(
            f"https://t.me/s/{channel}",
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ibenwandu-landing/1.0)"},
        )
        resp.raise_for_status()
        _html = resp.text
    soup = BeautifulSoup(_html, "html.parser")
    blocks = soup.select("div.tgme_widget_message_text")
    if not blocks:
        return None
    latest = blocks[-1]
    for br in latest.find_all("br"):
        br.replace_with("\n")
    text = latest.get_text().strip()
    return text or None


def truncate(text: str, max_lines: int = MAX_LINES) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]) + "\n" + NOTICE


def render_pane(message: str, channel: str, *, now: datetime) -> str:
    body = html.escape(truncate(message)).replace("\n", "<br>")
    stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    return (
        f'<div class="tsa-message">{body}</div>'
        f'<div class="tsa-meta">updated {stamp}</div>'
    )


def rewrite_index(pane_html: str, *, index_path: Path = INDEX) -> bool:
    content = index_path.read_text(encoding="utf-8")
    start_i = content.find(START)
    end_i = content.find(END)
    if start_i == -1 or end_i == -1:
        raise RuntimeError("TSA markers not found in index.html")
    new = content[: start_i + len(START)] + "\n" + pane_html + "\n" + content[end_i:]
    if new == content:
        return False
    index_path.write_text(new, encoding="utf-8")
    return True


def main() -> int:
    channel = os.environ.get("TSA_CHANNEL", "<CHANNEL>")
    try:
        msg = fetch_latest_message(channel)
    except Exception as exc:  # fail-safe — keep last snapshot
        print(f"fetch failed: {exc}; leaving last snapshot", file=sys.stderr)
        return 0
    if not msg:
        print("no message found; leaving last snapshot", file=sys.stderr)
        return 0
    pane = render_pane(msg, channel, now=datetime.now(timezone.utc))
    print("updated" if rewrite_index(pane) else "no change")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
