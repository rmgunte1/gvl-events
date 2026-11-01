"""Shared helpers for all scrapers."""
import json
import re
from datetime import datetime, timezone
from typing import Optional, Iterator, Any

import requests
from dateutil import parser as dtparser
from dateutil import tz
from bs4 import BeautifulSoup

from config import TIMEZONE

LOCAL_TZ = tz.gettz(TIMEZONE)
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
session = requests.Session()
session.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})


def get(url: str, **kw) -> requests.Response:
    r = session.get(url, timeout=30, **kw)
    r.raise_for_status()
    return r


def parse_dt(value: Any) -> Optional[datetime]:
    """Parse almost any date string into a tz-aware datetime (local tz if naive)."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    try:
        d = dtparser.parse(str(value), fuzzy=True)
    except Exception:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=LOCAL_TZ)
    return d


def clean(text: Optional[str]) -> str:
    if not text:
        return ""
    text = BeautifulSoup(str(text), "html.parser").get_text(" ")
    return re.sub(r"\s+", " ", text).strip()


def soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def jsonld_blocks(html: str) -> Iterator[Any]:
    """Yield every parsed <script type=application/ld+json> payload."""
    for s in soup(html).find_all("script", attrs={"type": re.compile("ld\\+json", re.I)}):
        raw = s.string or s.get_text() or ""
        raw = raw.strip()
        if not raw:
            continue
        try:
            yield json.loads(raw)
        except json.JSONDecodeError:
            # some sites concatenate objects; try to salvage the first one
            try:
                yield json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
            except Exception:
                continue


def walk(obj: Any) -> Iterator[dict]:
    """Depth-first walk yielding every dict in a nested JSON structure."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def first(*vals):
    for v in vals:
        if v:
            return v
    return ""


def addr_parts(location: Any):
    """Pull (venue, address, city) from a schema.org Place-ish object."""
    venue = address = city = ""
    if isinstance(location, list):
        location = location[0] if location else {}
    if isinstance(location, str):
        return location, "", ""
    if not isinstance(location, dict):
        return venue, address, city
    venue = clean(location.get("name"))
    a = location.get("address")
    if isinstance(a, str):
        address = clean(a)
    elif isinstance(a, dict):
        address = clean(" ".join(str(a.get(k, "")) for k in
                                 ("streetAddress", "addressLocality", "addressRegion", "postalCode")))
        city = clean(a.get("addressLocality"))
    if not city and address:
        m = re.search(r",\s*([A-Za-z .]+?),?\s*SC\b", address)
        if m:
            city = m.group(1).strip()
    return venue, address, city
