# GVL Events

Private, one-person app that crawls Greenville, SC event sources every day at noon ET,
de-duplicates them, pushes a Pushover notification to your iPhone, and shows each event once
as a Yes/No card. "No" hides it forever; "Yes" goes on your Going list (or Weekly list for
recurring things) with a one-tap register link and Add-to-Calendar.

```
crawler/      Python crawler (GitHub Actions runs it daily)
  config.py   geography, filters, categories, SOURCE REGISTRY  ← edit this to tune
  curated_series.json  recurring groups that live on Instagram/Facebook
docs/         the iPhone PWA (served by GitHub Pages)
supabase/     database schema + Row Level Security
.github/      the noon schedule
SETUP.md      step-by-step setup (start here)
SOURCES.md    what each source is and how it's read
```

Stack: GitHub Actions → Python → Supabase (Postgres + auth) → static PWA on GitHub Pages → Pushover.
Cost: $0/month (Pushover is a $4.99 one-time purchase).
