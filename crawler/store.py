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
                         params={"select": "id,title,start_at,venue,is_series,status", "limit": "5000"}, timeout=30)
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

    def prune_stale_series(self, current_series_ids: set) -> int:
        """Remove curated recurring cards that were deleted from curated_series.json
        (e.g. curated entries that were deleted). Only touches undecided or 'yes'
        rows with is_series = true; one-off events are never deleted."""
        r = requests.get(self._rest("events"), headers=self.h,
                         params={"select": "id", "is_series": "eq.true",
                                 "source": "eq.Curated series"}, timeout=30)
        r.raise_for_status()
        stale = [row["id"] for row in r.json() if row["id"] not in current_series_ids]
        for i in range(0, len(stale), 100):
            ids = ",".join(f'"{x}"' for x in stale[i:i + 100])
            d = requests.delete(self._rest("events"), headers=self.h,
                                params={"id": f"in.({ids})"}, timeout=30)
            d.raise_for_status()
        return len(stale)

    def delete_by_sources(self, sources: list) -> int:
        n = 0
        for src in sources:
            r = requests.delete(self._rest("events"), headers={**self.h, "Prefer": "return=representation"},
                                params={"source": f"eq.{src}"}, timeout=30)
            r.raise_for_status()
            n += len(r.json())
        return n

    def all_rows(self) -> List[dict]:
        r = requests.get(self._rest("events"), headers=self.h,
                         params={"select": "id,title,description,venue,city,address,start_at,is_series,status",
                                 "limit": "5000"}, timeout=30)
        r.raise_for_status()
        return r.json()

    def delete_ids(self, ids: List[str]) -> int:
        for i in range(0, len(ids), 100):
            chunk = ",".join(f'"{x}"' for x in ids[i:i + 100])
            d = requests.delete(self._rest("events"), headers=self.h,
                                params={"id": f"in.({chunk})"}, timeout=30)
            d.raise_for_status()
        return len(ids)

    def log_run(self, summary: dict):
        requests.post(self._rest("runs"), headers=self.h, json=summary, timeout=30)
