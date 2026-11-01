"""Daily crawl: fetch every source, filter, dedupe, store, notify.

Usage:
  python main.py            # full run (only at noon ET unless FORCE=1)
  DRY_RUN=1 python main.py  # crawl + print, no database writes or notifications
"""
import os
import sys
import traceback
from datetime import datetime
from typing import List

from dateutil import tz

from config import SOURCES, TIMEZONE, RUN_HOUR_LOCAL
from models import Event
from normalize import is_excluded, categorize, dedupe, match_existing
from sources import FETCHERS


def noon_guard() -> bool:
    if os.environ.get("FORCE") == "1":
        return True
    local = datetime.now(tz.gettz(TIMEZONE))
    if local.hour != RUN_HOUR_LOCAL:
        print(f"Local time is {local:%H:%M} ET; this job only runs at {RUN_HOUR_LOCAL}:00. Exiting.")
        return False
    return True


def crawl() -> tuple[List[Event], List[str], dict]:
    all_events: List[Event] = []
    failures: List[str] = []
    counts = {}
    for src in SOURCES:
        fn = FETCHERS.get(src["kind"])
        if not fn:
            failures.append(f"{src['name']}: unknown kind {src['kind']}")
            continue
        try:
            evs = fn(src)
            for e in evs:                       # venue-level defaults from the registry
                e.category = e.category or src.get("category", "")
                e.city = e.city or src.get("city", "")
            counts[src["name"]] = len(evs)
            print(f"[ok]   {src['name']}: {len(evs)} events")
            all_events += evs
        except Exception as ex:  # noqa: BLE001
            counts[src["name"]] = -1
            failures.append(f"{src['name']}: {type(ex).__name__}: {str(ex)[:120]}")
            print(f"[fail] {src['name']}: {type(ex).__name__}: {ex}")
    return all_events, failures, counts


def main() -> int:
    dry = os.environ.get("DRY_RUN") == "1"
    if not dry and not noon_guard():
        return 0

    raw, failures, counts = crawl()
    kept, dropped = [], {}
    for e in raw:
        reason = is_excluded(e)
        if reason:
            dropped[reason.split(":")[0]] = dropped.get(reason.split(":")[0], 0) + 1
            continue
        kept.append(categorize(e))
    events = dedupe(kept)
    print(f"\n{len(raw)} fetched, {len(kept)} after filters, {len(events)} after dedupe. Dropped: {dropped}")

    if dry:
        for e in sorted(events, key=lambda x: (-x.social_score, x.start.isoformat() if x.start else "")):
            when = e.recurrence if e.is_series else e.start.strftime("%a %m/%d %I:%M%p")
            print(f"  [{e.category:8}] {e.social_score:2d}  {e.title[:55]:55} | {when[:30]:30} | {', '.join(e.sources)}")
        if failures:
            print("\nFailures:\n  " + "\n  ".join(failures))
        return 0

    from store import Store
    import notify
    store = Store()
    existing = store.existing()
    events = match_existing(events, existing)
    events = dedupe(events)   # match_existing may have mapped two onto one id
    new = store.upsert(events, {r["id"] for r in existing})
    print(f"{len(new)} new events stored")
    try:
        store.log_run({"ran_at": datetime.utcnow().isoformat(), "fetched": len(raw),
                       "kept": len(events), "new": len(new), "failures": failures, "counts": counts})
    except Exception:
        traceback.print_exc()
    notify.send(new, failures)
    return 0


if __name__ == "__main__":
    sys.exit(main())
