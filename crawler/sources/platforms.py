"""Eventbrite, Meetup, LeagueLab, Ticketmaster, MiLB and curated-series sources."""
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

from models import Event
from .common import get, parse_dt, clean, jsonld_blocks, walk, first, soup
from .jsonld import events_from_json, fetch as fetch_jsonld


# ---------------------------------------------------------------- Eventbrite
def fetch_eventbrite(src: dict) -> List[Event]:
    html = get(src["url"]).text
    events: List[Event] = []
    for block in jsonld_blocks(html):
        events += events_from_json(block, src["name"], src["url"])
    if events:
        return events
    # Fallback: Eventbrite embeds window.__SERVER_DATA__ with search results.
    m = re.search(r"window\.__SERVER_DATA__\s*=\s*(\{.*?\});\s*</script>", html, re.S)
    if not m:
        return events
    data = json.loads(m.group(1))
    for d in walk(data):
        if "start_date" in d and ("name" in d) and ("url" in d):
            when = parse_dt(f"{d.get('start_date')} {d.get('start_time', '')}".strip())
            venue = d.get("primary_venue") or {}
            addr = (venue.get("address") or {}) if isinstance(venue, dict) else {}
            events.append(Event(title=clean(d.get("name")), start=when, source=src["name"],
                                url=d.get("url", ""), register_url=first(d.get("tickets_url"), d.get("url")),
                                description=clean(d.get("summary")),
                                venue=clean(venue.get("name")) if isinstance(venue, dict) else "",
                                address=clean(addr.get("localized_address_display")),
                                city=clean(addr.get("city"))))
    return events


# ------------------------------------------------------------------- Meetup
def fetch_meetup(src: dict) -> List[Event]:
    """Group event pages carry JSON-LD; the search page carries __NEXT_DATA__."""
    events = fetch_jsonld(src)
    for e in events:
        e.register_url = e.register_url or e.url
        if not e.city and "greenville" in (e.address or "").lower():
            e.city = "Greenville"
    return events


# ---------------------------------------------------------------- LeagueLab
def fetch_leaguelab(src: dict) -> List[Event]:
    """Greenville Sports Leagues: list open/upcoming leagues as registerable series."""
    html = get(src["url"]).text
    s = soup(html)
    out = []
    for a in s.select("a[href*='/league/']"):
        title = clean(a.get_text())
        if len(title) < 6:
            continue
        href = a.get("href", "")
        url = href if href.startswith("http") else "https://playgreenville.leaguelab.com" + href
        row_text = clean(a.find_parent(["tr", "li", "div"]).get_text(" ")) if a.find_parent(["tr", "li", "div"]) else ""
        m = re.search(r"(Starts?|Start Date)[:\s]*([A-Z][a-z]+,? [A-Z]?[a-z]* ?\d{1,2}(?:,? \d{4})?)", row_text)
        start = parse_dt(m.group(2)) if m else None
        if start and start.year < 2000:
            start = None
        out.append(Event(title=f"GSL: {title}", start=start, source=src["name"], url=url,
                         register_url=url, is_series=True,
                         recurrence=row_text[:140], venue="Greenville Sports Leagues",
                         city="Greenville", category="social",
                         description=row_text))
    # keep only unique titles
    seen, uniq = set(), []
    for e in out:
        if e.title not in seen:
            seen.add(e.title)
            uniq.append(e)
    return uniq


# ------------------------------------------------------------- Ticketmaster
def fetch_ticketmaster(src: dict) -> List[Event]:
    key = os.environ.get("TICKETMASTER_KEY")
    if not key:
        raise RuntimeError("TICKETMASTER_KEY not set (optional source, skipped)")
    now = datetime.now(timezone.utc)
    params = {
        "apikey": key, "latlong": "34.8526,-82.3940", "radius": "25", "unit": "miles",
        "startDateTime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endDateTime": (now + timedelta(days=22)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "size": "200", "sort": "date,asc",
    }
    data = get("https://app.ticketmaster.com/discovery/v2/events.json", params=params).json()
    out = []
    for ev in data.get("_embedded", {}).get("events", []):
        dates = ev.get("dates", {}).get("start", {})
        start = parse_dt(dates.get("dateTime") or dates.get("localDate"))
        venues = ev.get("_embedded", {}).get("venues", [{}])
        v = venues[0] if venues else {}
        city = (v.get("city") or {}).get("name", "")
        out.append(Event(title=clean(ev.get("name")), start=start, source=src["name"],
                         url=ev.get("url", ""), register_url=ev.get("url", ""),
                         description=clean(ev.get("info") or ev.get("pleaseNote")),
                         venue=clean(v.get("name")),
                         address=clean(f"{(v.get('address') or {}).get('line1', '')}, {city}, SC"),
                         city=city))
    return out


# ------------------------------------------------------------------- MiLB
def fetch_milb(src: dict) -> List[Event]:
    now = datetime.now(timezone.utc)
    params = {"sportId": 14, "teamId": src["team_id"],
              "startDate": now.strftime("%Y-%m-%d"),
              "endDate": (now + timedelta(days=22)).strftime("%Y-%m-%d")}
    data = get("https://statsapi.mlb.com/api/v1/schedule", params=params).json()
    out = []
    for day in data.get("dates", []):
        for g in day.get("games", []):
            home = g["teams"]["home"]["team"]
            if home.get("id") != src["team_id"]:
                continue
            away = g["teams"]["away"]["team"]["name"]
            out.append(Event(title=f"Greenville Drive vs {away}", start=parse_dt(g.get("gameDate")),
                             source=src["name"], url="https://www.milb.com/greenville/schedule",
                             register_url="https://www.milb.com/greenville/tickets",
                             venue="Fluor Field", address="945 S Main St, Greenville, SC",
                             city="Greenville", category="sports"))
    return out


# ---------------------------------------------------------------- Curated
def fetch_curated(src: dict) -> List[Event]:
    path = Path(__file__).resolve().parent.parent / src["path"]
    items = json.loads(path.read_text())
    out = []
    for it in items:
        out.append(Event(title=it["title"], start=None, source=src["name"], url=it.get("url", ""),
                         register_url=it.get("register_url", ""), description=it.get("description", ""),
                         venue=it.get("venue", ""), address=it.get("address", ""),
                         city=it.get("city", "Greenville"), is_series=True,
                         recurrence=it.get("recurrence", ""), category=it.get("category", "social")))
    return out


# ---------------------------------------------------------------- RunSignUp
def fetch_runsignup(src: dict) -> List[Event]:
    """Public RunSignUp race search: every 5K/8K/trail run/turkey trot within 25 miles."""
    now = datetime.now(timezone.utc)
    params = {"format": "json", "zipcode": "29601", "radius": 25, "results_per_page": 100,
              "start_date": now.strftime("%Y-%m-%d"),
              "end_date": (now + timedelta(days=45)).strftime("%Y-%m-%d"),
              "only_partner_races": "F", "include_event_days": "T"}
    data = get("https://runsignup.com/Rest/races", params=params,
               headers={"Accept": "application/json"}).json()
    out = []
    for item in data.get("races", []):
        r = item.get("race", item)
        addr = r.get("address") or {}
        city = clean(addr.get("city"))
        start = parse_dt(r.get("next_date"))
        if not start:
            continue
        out.append(Event(title=clean(r.get("name")), start=start, source=src["name"],
                         url=r.get("url", ""), register_url=r.get("url", ""),
                         description=clean(r.get("description"))[:600],
                         venue=clean(addr.get("name")) or city,
                         address=clean(f"{addr.get('street', '')}, {city}, {addr.get('state', '')}"),
                         city=city, category="sports"))
    return out
