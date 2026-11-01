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
        new_events, new_rows, known_rows = [], [], []
        for e in events:
            row = e.to_row()
            row["last_seen"] = now
            if e.id in existing_ids:
                known_rows.append(row)          # no status/first_seen: decisions preserved
            else:
                row["status"] = "new"
                row["first_seen"] = now
                new_rows.append(row)
                new_events.append(e)
        # PostgREST needs every row in a batch to have identical keys, so two batches.
        for rows in (new_rows, known_rows):
            for i in range(0, len(rows), 200):
                r = requests.post(self._rest("events"),
                                  headers={**self.h, "Prefer": "resolution=merge-duplicates"},
                                  json=rows[i:i + 200], timeout=60)
                if not r.ok:
                    raise RuntimeError(f"Supabase {r.status_code}: {r.text[:300]}")
        return new_events

    def log_run(self, summary: dict):
        requests.post(self._rest("runs"), headers=self.h, json=summary, timeout=30)
