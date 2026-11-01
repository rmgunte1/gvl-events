"""Supabase storage via the PostgREST API (service role key, server-side only)."""
import os
from datetime import datetime, timezone
from typing import List

import requests

from models import Event


class Store:
    def __init__(self):
        self.url = os.environ["SUPABASE_URL"].rstrip("/")
        key = os.environ["SUPABASE_SERVICE_KEY"]
        self.h = {"apikey": key, "Authorization": f"Bearer {key}",
                  "Content-Type": "application/json"}

    def _rest(self, path: str) -> str:
        return f"{self.url}/rest/v1/{path}"

    def existing(self) -> List[dict]:
        r = requests.get(self._rest("events"), headers=self.h,
                         params={"select": "id,title,start_at,venue,is_series,status"}, timeout=30)
        r.raise_for_status()
        return r.json()

    def upsert(self, events: List[Event], existing_ids: set) -> List[Event]:
        """Insert brand-new events; refresh last_seen/sources/urls on known ones.
        Never touches status, so a 'no' stays a 'no'. Returns the new ones."""
        now = datetime.now(timezone.utc).isoformat()
        new, known = [], []
        for e in events:
            row = e.to_row()
            row["last_seen"] = now
            if e.id in existing_ids:
                row.pop("first_seen", None)
                known.append(row)
            else:
                row["status"] = "new"
                row["first_seen"] = now
                new.append(e)
                known.append(row)   # inserted via upsert below
        if known:
            # merge-duplicates updates matching ids and inserts the rest; status is
            # only present on new rows so existing decisions are preserved.
            for i in range(0, len(known), 200):
                r = requests.post(self._rest("events"), headers={**self.h, "Prefer": "resolution=merge-duplicates"},
                                  json=known[i:i + 200], timeout=60)
                r.raise_for_status()
        return new

    def log_run(self, summary: dict):
        requests.post(self._rest("runs"), headers=self.h, json=summary, timeout=30)
