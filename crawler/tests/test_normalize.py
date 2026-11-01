"""Offline tests for filters and dedupe. Run from crawler/: python -m pytest -q"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Event                       # noqa: E402
from normalize import is_excluded, categorize, dedupe, match_existing   # noqa: E402

NOW = datetime.now(timezone.utc)


def ev(title, days=3, **kw):
    return Event(title=title, start=NOW + timedelta(days=days), source=kw.pop("source", "t"), **kw)


def test_excludes_kids_business_and_far_cities():
    assert is_excluded(ev("Kids Maker Day: Ninja Academy")).startswith("keyword")
    assert is_excluded(ev("PIQUE Young Professional Conference")).startswith("keyword")
    assert is_excluded(ev("Hub City Hog Fest", city="Spartanburg")).startswith("city")
    assert is_excluded(ev("Concert", address="580 E Main St, Spartanburg, SC")) == "address:blocked"
    assert is_excluded(ev("Trivia Night", city="Greer")) == ""
    assert is_excluded(ev("Trivia Night", days=40)) == "too-far"
    assert is_excluded(ev("Trivia Night", days=-1)) == "past"


def test_series_without_date_is_allowed():
    s = Event(title="Run Club", start=None, source="curated", is_series=True)
    assert is_excluded(s) == ""


def test_categorize_and_score():
    e = categorize(ev("Tantra Speed Date - Greenville! (Meet Singles Speed Dating)"))
    assert e.category == "social" and e.social_score >= 10
    assert categorize(ev("Futurebirds with Patton Magee - Live in Concert")).category == "music"
    assert categorize(ev("Swamp Rabbits vs Jacksonville Icemen")).category == "sports"


def test_dedupe_merges_same_event_from_two_sources():
    a = ev("Futurebirds w/ Patton Magee", source="Radio Room", register_url="https://tix")
    b = ev("Futurebirds with Patton Magee at Radio Room", source="Songkick", venue="Radio Room")
    c = ev("Completely different show", source="Songkick")
    out = dedupe([a, b, c])
    assert len(out) == 2
    merged = next(x for x in out if "Futurebirds" in x.title)
    assert set(merged.sources) == {"Radio Room", "Songkick"}
    assert merged.register_url == "https://tix" and merged.venue == "Radio Room"


def test_same_title_different_day_is_two_events():
    out = dedupe([ev("Trivia at Southernside", days=2), ev("Trivia at Southernside", days=9)])
    assert len(out) == 2


def test_existing_no_decision_sticks_after_retitle():
    old = ev("Tantra Speed Date - Greenville!", days=5)
    existing = [{"id": old.id, "title": old.title, "start_at": old.start.isoformat(),
                 "venue": "", "is_series": False, "status": "no"}]
    renamed = ev("Tantra Speed Date Greenville (Meet Singles)", days=5)
    assert renamed.id != old.id
    out = match_existing([renamed], existing)
    assert out[0].id == old.id
