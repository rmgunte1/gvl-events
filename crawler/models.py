from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List
import hashlib
import re


def slug(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


@dataclass
class Event:
    title: str
    start: Optional[datetime]          # tz-aware, or None for a series with no fixed date
    source: str
    url: str = ""
    register_url: str = ""
    end: Optional[datetime] = None
    description: str = ""
    venue: str = ""
    address: str = ""
    city: str = ""
    is_series: bool = False
    recurrence: str = ""               # e.g. "Every Monday 6:45 PM"
    category: str = ""
    social_score: int = 0
    sources: List[str] = field(default_factory=list)
    id: str = ""

    def __post_init__(self):
        self.title = re.sub(r"\s+", " ", (self.title or "")).strip()
        if not self.sources:
            self.sources = [self.source]
        if not self.id:
            self.id = self.make_id()

    def make_id(self) -> str:
        if self.is_series:
            key = "series|" + slug(self.title)[:60]
        else:
            day = self.start.strftime("%Y-%m-%d") if self.start else "nodate"
            key = slug(self.title)[:60] + "|" + day
        return hashlib.sha1(key.encode()).hexdigest()[:16]

    def to_row(self) -> dict:
        d = asdict(self)
        d["start_at"] = self.start.isoformat() if self.start else None
        d["end_at"] = self.end.isoformat() if self.end else None
        d.pop("start"), d.pop("end")
        d["description"] = (d["description"] or "")[:1500]
        return d
