"""Nudges beyond the daily digest: empty-weekend alarm, holiday check, host prompts.

All run inside the daily noon job, so they need no extra schedule.
"""
from datetime import datetime, timedelta, date
from typing import List

from dateutil import tz

from config import TIMEZONE, HOLIDAYS, HOST_PROMPT_EVERY_WEEKS
from notify import push

LOCAL = tz.gettz(TIMEZONE)


def _parse(row) -> datetime | None:
    try:
        return datetime.fromisoformat(row["start_at"]).astimezone(LOCAL) if row.get("start_at") else None
    except Exception:
        return None


def _fmt(row) -> str:
    d = _parse(row)
    when = d.strftime("%a %b %-d, %-I:%M %p") if d else ""
    return f"• {row['title'][:60]} — {when}"


def _rows_between(rows: List[dict], start: date, end: date, status: str) -> List[dict]:
    out = []
    for r in rows:
        if r.get("status") != status or r.get("is_series"):
            continue
        d = _parse(r)
        if d and start <= d.date() <= end:
            out.append(r)
    return sorted(out, key=lambda r: r["start_at"])


def empty_weekend_alarm(rows: List[dict], today: date) -> bool:
    """Thursday: if nothing is on the Going list Fri–Sun, push the open options."""
    if today.weekday() != 3:          # Thursday
        return False
    fri, sun = today + timedelta(days=1), today + timedelta(days=3)
    going = _rows_between(rows, fri, sun, "yes")
    if going:
        return False
    options = _rows_between(rows, fri, sun, "new")
    body = "Nothing on your Going list for Fri–Sun."
    if options:
        body += " Still open:\n" + "\n".join(_fmt(r) for r in options[:5])
        if len(options) > 5:
            body += f"\n…and {len(options) - 5} more"
    else:
        body += " The deck is empty too — text someone and make a plan."
    push("Your weekend is empty", body, priority=1)
    return True


def holiday_check(rows: List[dict], today: date) -> bool:
    """Ten days (and again three days) before each holiday: do you have a plan?"""
    sent = False
    for name, hday in HOLIDAYS:
        lead = (hday - today).days
        if lead not in (10, 3):
            continue
        window_start, window_end = hday - timedelta(days=1), hday + timedelta(days=1)
        going = _rows_between(rows, window_start, window_end, "yes")
        if going:
            continue
        options = _rows_between(rows, window_start, window_end, "new")
        body = f"{name} is in {lead} days and you have no plan yet."
        if options:
            body += " Options:\n" + "\n".join(_fmt(r) for r in options[:5])
        else:
            body += " Nothing in the deck for that day — check the Meetup 'orphan' dinners, a volunteer shift, or host something."
        push(f"{name}: no plans yet", body, priority=1)
        sent = True
    return sent


def host_prompt(today: date) -> bool:
    """Every N weeks on Monday: post your own event instead of only attending."""
    if today.weekday() != 0:
        return False
    if today.isocalendar().week % HOST_PROMPT_EVERY_WEEKS != 0:
        return False
    push("Host something this month",
         "It's been a few weeks. Post a committed-date event to the 20s & 30s group: "
         "Catan night at a brewery, a trivia team, a Saturday hike. Hosting beats attending.")
    return True


def run_all(rows: List[dict]) -> None:
    today = datetime.now(LOCAL).date()
    for fn in (empty_weekend_alarm, holiday_check):
        try:
            if fn(rows, today):
                print(f"[reminder] {fn.__name__} sent")
        except Exception as ex:   # noqa: BLE001
            print(f"[reminder] {fn.__name__} failed: {ex}")
    try:
        if host_prompt(today):
            print("[reminder] host_prompt sent")
    except Exception as ex:   # noqa: BLE001
        print(f"[reminder] host_prompt failed: {ex}")
