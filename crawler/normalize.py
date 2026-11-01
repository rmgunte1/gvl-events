"""Filtering, categorizing, and de-duplicating events."""
import re
from datetime import datetime, timezone
from typing import List, Dict, Iterable

from rapidfuzz import fuzz

from config import (ALLOWED_CITIES, BLOCKED_CITIES, EXCLUDE_KEYWORDS, CATEGORY_RULES,
                    SOCIAL_SCORE_KEYWORDS, LOOKAHEAD)
from models import Event, slug

_EXCLUDE = [re.compile(p, re.I) for p in EXCLUDE_KEYWORDS]
_CATS = [(c, [re.compile(p, re.I) for p in pats]) for c, pats in CATEGORY_RULES]
_SCORES = [(re.compile(p, re.I), w) for p, w in SOCIAL_SCORE_KEYWORDS.items()]


def _text(e: Event) -> str:
    return f"{e.title} {e.description[:400]} {e.venue}"


def is_excluded(e: Event) -> str:
    """Return the reason the event is excluded, or '' if it passes."""
    t = _text(e)
    for rx in _EXCLUDE:
        if rx.search(t):
            return f"keyword:{rx.pattern}"
    city = (e.city or "").strip().lower()
    if city:
        if city in BLOCKED_CITIES:
            return f"city:{city}"
        if city not in ALLOWED_CITIES:
            # unknown city: keep only if the address mentions an allowed one
            addr = (e.address or "").lower()
            if not any(c in addr for c in ALLOWED_CITIES):
                return f"city:{city}"
    else:
        addr = (e.address or "").lower()
        if any(c in addr for c in BLOCKED_CITIES):
            return "address:blocked"
    if not e.is_series:
        if not e.start:
            return "no-date"
        now = datetime.now(timezone.utc)
        if e.start < now:
            return "past"
        if e.start > now + LOOKAHEAD:
            return "too-far"
    return ""


def categorize(e: Event) -> Event:
    t = _text(e)
    if not e.category:
        for cat, rxs in _CATS:
            if any(rx.search(t) for rx in rxs):
                e.category = cat
                break
        else:
            e.category = "other"
    e.social_score = sum(w for rx, w in _SCORES if rx.search(t))
    if e.is_series:
        e.social_score += 2
    return e


def _same_day(a: Event, b: Event) -> bool:
    if a.is_series and b.is_series:
        return True
    if not a.start or not b.start:
        return False
    return a.start.astimezone().date() == b.start.astimezone().date()


def _similar(a: Event, b: Event) -> bool:
    if a.is_series != b.is_series:
        return False
    if not _same_day(a, b):
        return False
    ta, tb = a.title.lower(), b.title.lower()
    score = fuzz.token_set_ratio(ta, tb)
    if score >= 90:
        return True
    if score >= 75 and min(len(ta), len(tb)) >= 15 and fuzz.partial_token_set_ratio(ta, tb) >= 95:
        return True
    if score >= 80:
        va, vb = slug(a.venue), slug(b.venue)
        return bool(va and vb and (va in vb or vb in va))
    return False


def _merge(keep: Event, other: Event) -> Event:
    for f in ("url", "register_url", "description", "venue", "address", "city", "end", "recurrence"):
        if not getattr(keep, f) and getattr(other, f):
            setattr(keep, f, getattr(other, f))
    if len(other.description) > len(keep.description):
        keep.description = other.description
    for s in other.sources:
        if s not in keep.sources:
            keep.sources.append(s)
    return keep


def dedupe(events: Iterable[Event]) -> List[Event]:
    """Collapse events that are the same thing seen from multiple sources."""
    kept: List[Event] = []
    by_id: Dict[str, Event] = {}
    for e in events:
        if e.id in by_id:
            _merge(by_id[e.id], e)
            continue
        match = next((k for k in kept if _similar(k, e)), None)
        if match:
            _merge(match, e)
            continue
        kept.append(e)
        by_id[e.id] = e
    return kept


def match_existing(new_events: List[Event], existing: List[dict]) -> List[Event]:
    """Map new events onto ids already in the database (so a 'no' stays a 'no'
    even if a source re-words the title slightly)."""
    ex_events = []
    for r in existing:
        try:
            st = datetime.fromisoformat(r["start_at"]) if r.get("start_at") else None
        except Exception:
            st = None
        ex_events.append(Event(title=r["title"], start=st, source="db", venue=r.get("venue") or "",
                               is_series=bool(r.get("is_series")), id=r["id"]))
    for e in new_events:
        if any(x.id == e.id for x in ex_events):
            continue
        m = next((x for x in ex_events if _similar(x, e)), None)
        if m:
            e.id = m.id
    return new_events
