"""Pushover notifications."""
import os
from typing import List

import requests

from config import APP_URL
from models import Event


def push(title: str, body: str, priority: int = 0) -> None:
    token, user = os.environ.get("PUSHOVER_TOKEN"), os.environ.get("PUSHOVER_USER")
    if not token or not user:
        print(f"Pushover not configured; would send: {title}\n{body}")
        return
    r = requests.post("https://api.pushover.net/1/messages.json", data={
        "token": token, "user": user, "title": title, "message": body[:1000],
        "url": APP_URL, "url_title": "Open GVL Events", "priority": priority,
    }, timeout=30)
    r.raise_for_status()


def when_str(e: Event) -> str:
    if e.is_series:
        return e.recurrence
    return e.start.astimezone().strftime("%a %b %-d, %-I:%M %p") if e.start else ""


def lines_for(events: List[Event], n: int = 5) -> str:
    out = [f"• {e.title[:60]} — {when_str(e)}" for e in events[:n]]
    if len(events) > n:
        out.append(f"…and {len(events) - n} more")
    return "\n".join(out)


def send(new_events: List[Event], failures: List[str]) -> None:
    n = len(new_events)
    if n == 0:
        title, body = "GVL Events: nothing new today", "No new events found. Go to Run Club anyway."
    else:
        title = f"GVL Events: {n} new to review"
        body = lines_for(sorted(new_events, key=lambda e: e.start.isoformat() if e.start else "~"))
    if failures:
        body += f"\n({len(failures)} source{'s' if len(failures) != 1 else ''} failed)"
    push(title, body)
