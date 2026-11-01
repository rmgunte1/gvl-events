"""Pushover notification."""
import os
from typing import List

import requests

from config import APP_URL
from models import Event


def send(new_events: List[Event], failures: List[str]) -> None:
    token, user = os.environ.get("PUSHOVER_TOKEN"), os.environ.get("PUSHOVER_USER")
    if not token or not user:
        print("Pushover not configured; skipping notification")
        return
    n = len(new_events)
    if n == 0:
        title = "GVL Events: nothing new today"
        body = "No new events found. Go to Run Club anyway."
    else:
        title = f"GVL Events: {n} new to review"
        top = sorted(new_events, key=lambda e: (-e.social_score, e.start.isoformat() if e.start else "~"))[:5]
        lines = []
        for e in top:
            when = e.recurrence if e.is_series else (e.start.astimezone().strftime("%a %b %-d, %-I:%M %p") if e.start else "")
            lines.append(f"• {e.title[:60]} — {when}")
        body = "\n".join(lines)
        if n > 5:
            body += f"\n…and {n - 5} more"
    if failures:
        body += f"\n({len(failures)} source{'s' if len(failures) != 1 else ''} failed)"
    r = requests.post("https://api.pushover.net/1/messages.json", data={
        "token": token, "user": user, "title": title, "message": body,
        "url": APP_URL, "url_title": "Open GVL Events", "priority": 0,
    }, timeout=30)
    r.raise_for_status()
