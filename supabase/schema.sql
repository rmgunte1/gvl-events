-- Run this once in Supabase: SQL Editor -> New query -> paste -> Run.

create table if not exists public.events (
  id            text primary key,
  title         text not null,
  description   text default '',
  start_at      timestamptz,
  end_at        timestamptz,
  venue         text default '',
  address       text default '',
  city          text default '',
  url           text default '',
  register_url  text default '',
  source        text default '',
  sources       text[] default '{}',
  category      text default 'other',
  social_score  int default 0,
  is_series     boolean default false,
  recurrence    text default '',
  status        text default 'new' check (status in ('new','yes','no')),
  decided_at    timestamptz,
  first_seen    timestamptz default now(),
  last_seen     timestamptz default now()
);

create index if not exists events_status_idx on public.events (status, start_at);

create table if not exists public.runs (
  id        bigserial primary key,
  ran_at    timestamptz default now(),
  fetched   int,
  kept      int,
  new       int,
  failures  jsonb,
  counts    jsonb
);

-- Row Level Security: only a signed-in user (you) can read/decide.
-- The crawler uses the service-role key, which bypasses RLS.
alter table public.events enable row level security;
alter table public.runs   enable row level security;

drop policy if exists "owner read events"   on public.events;
drop policy if exists "owner decide events" on public.events;
drop policy if exists "owner read runs"     on public.runs;

create policy "owner read events"   on public.events for select to authenticated using (true);
create policy "owner decide events" on public.events for update to authenticated
  using (true) with check (true);
create policy "owner read runs"     on public.runs   for select to authenticated using (true);
