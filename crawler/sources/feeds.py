"""iCal, RSS and WordPress 'The Events Calendar' (tribe) REST sources."""
import re
from typing import List
from xml.etree import ElementTree as ET

from icalendar import Calendar

from models import Event
from .common import get, parse_dt, clean, first


def fetch_ical(src: dict) -> List[Event]:
    raw = get(src["url"]).content
    cal = Calendar.from_ical(raw)
    out = []
    for comp in cal.walk("VEVENT"):
        start = comp.get("dtstart")
        if not start:
            continue
        start = parse_dt(start.dt)
        end = parse_dt(comp.get("dtend").dt) if comp.get("dtend") else None
        loc = clean(str(comp.get("location", "")))
        out.append(Event(title=clean(str(comp.get("summary", ""))), start=start, end=end,
                         source=src["name"], url=str(comp.get("url", "") or ""),
                         description=clean(str(comp.get("description", ""))),
                         venue=loc.split(",")[0] if loc else "", address=loc))
    return out


def fetch_rss(src: dict) -> List[Event]:
    """RSS where each item is an event; the date is usually in the title or description
    (CivicPlus puts 'Event date: November 5, 2026' in the description)."""
    root = ET.fromstring(get(src["url"]).content)
    out = []
    for item in root.iter("item"):
        title = clean(item.findtext("title"))
        desc = clean(item.findtext("description"))
        link = (item.findtext("link") or "").strip()
        m = re.search(r"(?:Event date|Date)[:\s]+([A-Z][a-z]+ \d{1,2},? \d{4}(?:[^<\n]{0,20}\d{1,2}:\d{2} ?[AP]M)?)",
                      desc, re.I)
        when = parse_dt(m.group(1)) if m else parse_dt(item.findtext("pubDate"))
        if not title or not when:
            continue
        out.append(Event(title=title, start=when, source=src["name"], url=link, description=desc))
    return out


def fetch_tribe(src: dict) -> List[Event]:
    data = get(src["url"], headers={"Accept": "application/json"}).json()
    out = []
    for ev in data.get("events", []):
        v = ev.get("venue") or {}
        if isinstance(v, list):
            v = v[0] if v else {}
        start = parse_dt(first(ev.get("utc_start_date"), ev.get("start_date")))
        if ev.get("utc_start_date"):
            start = parse_dt(ev["utc_start_date"] + " UTC")
        out.append(Event(title=clean(ev.get("title")), start=start,
                         end=parse_dt(ev.get("utc_end_date") + " UTC") if ev.get("utc_end_date") else None,
                         source=src["name"], url=ev.get("url", ""),
                         register_url=ev.get("website", "") or "",
                         description=clean(ev.get("description") or ev.get("excerpt")),
                         venue=clean(v.get("venue")), address=clean(v.get("address")),
                         city=clean(v.get("city"))))
    return out
