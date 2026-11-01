"""Generic scraper: schema.org Event objects embedded as JSON-LD, plus a fallback
that hunts through any inline JSON (Next.js __NEXT_DATA__, Nuxt, window.__DATA__)
for event-shaped objects. Covers most venue and calendar sites."""
import json
import re
from typing import List
from urllib.parse import urljoin

from models import Event
from .common import get, parse_dt, clean, jsonld_blocks, walk, addr_parts, first, soup

EVENT_TYPES = {"event", "musicevent", "sportsevent", "socialevent", "festival", "theaterevent",
               "comedyevent", "danceevent", "foodevent", "exhibitionevent", "screeningevent",
               "educationevent", "businessevent", "saleevent", "childrensevent", "literaryevent",
               "visualartsevent"}


def _types(obj: dict) -> set:
    t = obj.get("@type") or obj.get("type") or ""
    if isinstance(t, list):
        return {str(x).lower() for x in t}
    return {str(t).lower()}


def _offers_url(obj: dict) -> str:
    offers = obj.get("offers")
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    if isinstance(offers, dict):
        return offers.get("url", "") or ""
    return ""


def event_from_schema(obj: dict, source: str, base_url: str) -> Event | None:
    name = clean(first(obj.get("name"), obj.get("headline"), obj.get("title")))
    start = parse_dt(first(obj.get("startDate"), obj.get("start_date"), obj.get("dateTime"),
                           obj.get("start"), obj.get("startsAt")))
    if not name or not start:
        return None
    venue, address, city = addr_parts(obj.get("location") or obj.get("venue"))
    url = first(obj.get("url"), obj.get("eventUrl"), obj.get("link"))
    if url:
        url = urljoin(base_url, url)
    reg = _offers_url(obj) or first(obj.get("registrationUrl"), obj.get("ticketUrl"),
                                    obj.get("tickets_url"))
    t = _types(obj)
    cat = "music" if "musicevent" in t else "sports" if "sportsevent" in t else ""
    return Event(title=name, start=start, end=parse_dt(obj.get("endDate")), source=source,
                 url=url, register_url=urljoin(base_url, reg) if reg else "",
                 description=clean(obj.get("description")), venue=venue, address=address, city=city,
                 category=cat)


def events_from_json(payload, source: str, base_url: str) -> List[Event]:
    out = []
    for d in walk(payload):
        if _types(d) & EVENT_TYPES:
            e = event_from_schema(d, source, base_url)
            if e:
                out.append(e)
    return out


def _inline_json_blobs(html: str):
    s = soup(html)
    for tag in s.find_all("script"):
        txt = tag.string or ""
        if not txt or len(txt) < 50:
            continue
        if tag.get("id") == "__NEXT_DATA__" or tag.get("type") == "application/json":
            try:
                yield json.loads(txt)
                continue
            except Exception:
                pass
        m = re.search(r"=\s*(\{.*\})\s*;?\s*$", txt.strip(), re.S)
        if m and ("startDate" in txt or "dateTime" in txt or "start_date" in txt):
            try:
                yield json.loads(m.group(1))
            except Exception:
                continue


def _heuristic_events(payload, source: str, base_url: str) -> List[Event]:
    """Find dicts that look like events even without @type."""
    out = []
    for d in walk(payload):
        if _types(d) & EVENT_TYPES:
            continue
        has_name = any(k in d for k in ("name", "title", "headline"))
        has_start = any(k in d for k in ("startDate", "start_date", "dateTime", "startsAt"))
        if has_name and has_start:
            e = event_from_schema(d, source, base_url)
            if e:
                out.append(e)
    return out


def fetch(src: dict) -> List[Event]:
    url = src["url"]
    html = get(url).text
    events: List[Event] = []
    for block in jsonld_blocks(html):
        events += events_from_json(block, src["name"], url)
    if not events:
        for blob in _inline_json_blobs(html):
            events += events_from_json(blob, src["name"], url)
            if not events:
                events += _heuristic_events(blob, src["name"], url)
    return events
