# GVL Events — Complete Setup Guide

Read this once top to bottom. Every account, every field, every key, every place it gets pasted.
Total time: about 30–40 minutes. Total cost: $4.99 one-time (Pushover). Everything else is free.

---

## 0. What you'll need before starting

| Item | Why |
|---|---|
| A computer with a web browser (Mac or PC) | Uploading the repo folder and pasting keys is far easier than on the phone. The iPhone step at the end takes 1 minute. |
| Your iPhone, with **Safari** | Only Safari can add a web app to the Home Screen. Chrome on iPhone cannot. |
| An email address you control | Used for GitHub, Supabase, Pushover, and as your app login. One address for everything is fine. |
| The unzipped `gvl-events` folder from Claude | This is the code. Keep it somewhere you can find it (Desktop is fine). |
| A password manager or a Notes page | You'll collect 6 keys and 2 passwords. Keep them together. |

### Accounts you will create or use

| Account | Have it? | Cost | Used for |
|---|---|---|---|
| **GitHub** (github.com) | You already have one | Free | Hosts the code, runs the crawler daily, serves the app |
| **Supabase** (supabase.com) | Create in step 2 | Free | Database that stores events and your Yes/No decisions, plus your app login |
| **Pushover** (pushover.net + App Store app) | Create in step 3 | $4.99 one-time (30-day free trial first) | Noon notification to your iPhone |
| **Ticketmaster Developer** (developer.ticketmaster.com) | Optional, step 4 | Free | Arena, Peace Center and touring concerts. Skip it and the crawler just ignores that source. |

### The fill-in sheet

Copy this into Notes and fill it in as you go. Every blank gets used in step 6 or 7.

```
SUPABASE_URL          = https://________________.supabase.co
SUPABASE_ANON_KEY     = eyJ_____________________________________ (public, long)
SUPABASE_SERVICE_KEY  = eyJ_____________________________________ (SECRET, long)
Supabase DB password  = ______________________  (only needed if you ever open the DB directly)
App login email       = ______________________
App login password    = ______________________
PUSHOVER_USER         = u________________________________ (30 chars)
PUSHOVER_TOKEN        = a________________________________ (30 chars)
TICKETMASTER_KEY      = ______________________ (optional)
GitHub username       = ______________________
App URL               = https://<github username>.github.io/gvl-events/
```

---

## 1. Unzip and look at the folder (1 min)

Unzip `gvl-events.zip`. You should see:

```
gvl-events/
  .github/workflows/crawl.yml     ← the noon schedule (hidden folder on Mac; see step 5)
  crawler/                        ← Python crawler
  docs/                           ← the iPhone app
  supabase/schema.sql             ← database setup
  README.md, SETUP.md, SOURCES.md, requirements.txt, .gitignore
```

On a Mac, folders starting with a dot are hidden in Finder. Press **Cmd + Shift + .** (period) in Finder to show them. You need `.github` to get uploaded or the daily schedule will not exist.

---

## 2. Supabase — database and login (10 min)

### 2a. Create the account and project
1. Go to **https://supabase.com** → **Start your project** → **Continue with GitHub** → Authorize.
2. You land on the dashboard. Click **New project**.
3. Fill in:
   - **Organization**: leave the default (your name).
   - **Name**: `gvl-events`
   - **Database Password**: click **Generate a password**, then copy it to your fill-in sheet as *Supabase DB password*.
   - **Region**: **East US (North Virginia)**
   - **Pricing plan**: **Free**
4. Click **Create new project**. It takes 1–3 minutes. Wait until the green "Project is ready" state.

### 2b. Create the tables
1. Left sidebar → **SQL Editor** (icon looks like `>_`).
2. Click **+ New query**.
3. Open `supabase/schema.sql` from the folder in any text editor, select all, copy, paste into the query box.
4. Click **Run** (bottom right, or Cmd/Ctrl + Enter). Expected result: **"Success. No rows returned"**.
5. Confirm: left sidebar → **Table Editor** → you should see tables `events` and `runs`.

### 2c. Create your login (the only user the app will ever have)
1. Left sidebar → **Authentication** → **Users**.
2. Click **Add user** → **Create new user**.
3. **Email**: your email. **Password**: choose one (this is your *App login password*). Tick **Auto Confirm User**. Click **Create user**.
4. Now lock the door: left sidebar → **Authentication** → **Sign In / Providers** (may be labeled **Providers**) → click **Email**.
   - Keep **Enable Email provider** ON.
   - Turn **Allow new users to sign up** **OFF**.
   - Click **Save**.
   This means nobody but you can ever create an account, even though the app's URL is public.

### 2d. Copy the three keys
1. Left sidebar (bottom) → **Project Settings** (gear) → **API** (some dashboards show this under **Data API** / **API Keys**).
2. Copy to the fill-in sheet:
   - **Project URL** → `SUPABASE_URL` (looks like `https://abcdefghijkl.supabase.co`)
   - **anon** / **public** key → `SUPABASE_ANON_KEY` (starts with `eyJ`, ~200 chars). Safe to publish.
   - **service_role** / **secret** key → click **Reveal**, copy → `SUPABASE_SERVICE_KEY`. **Never paste this anywhere public.** It only goes into GitHub Secrets.

   If your dashboard shows the newer "Publishable key" / "Secret keys" layout instead: Publishable key = anon key; create a Secret key named `crawler` = service key.

---

## 3. Pushover — iPhone notifications (5 min)

1. On your iPhone, App Store → install **Pushover Notifications** (by Superblock). Free 30-day trial, then a one-time **$4.99** in-app purchase to keep receiving notifications. Nothing recurring.
2. Open the app → **Sign up** with your email and a password. Verify the email if asked.
3. Allow notifications when iOS prompts. (Later check: iPhone **Settings → Notifications → Pushover** → Allow Notifications ON, Banners ON, Sounds ON.)
4. On your computer go to **https://pushover.net** and log in.
5. On the dashboard, copy **Your User Key** (starts with `u`, 30 characters) → `PUSHOVER_USER`.
6. Scroll down → **Your Applications** → **Create an Application/API Token**.
   - **Name**: `GVL Events`
   - **Type**: Application
   - **Description**: anything
   - **URL**: leave blank
   - Tick the agreement box → **Create Application**.
7. On the application page copy **API Token/Key** (starts with `a`, 30 characters) → `PUSHOVER_TOKEN`.

---

## 4. Ticketmaster key — optional (3 min)

Gives you the arena, Peace Center, and touring shows reliably. Skip if you don't care about concerts.

1. **https://developer.ticketmaster.com** → **Get Your API Key** → create an account (email + password).
2. After login: **My Apps** → **Add a New App**. Name `gvl-events`, any description → **Create App**.
3. Copy **Consumer Key** → `TICKETMASTER_KEY`.

---

## 5. GitHub — put the code online (8 min)

### 5a. Create the repository
1. **https://github.com** → top-right **+** → **New repository**.
2. **Repository name**: `gvl-events` (exactly, lowercase; the app URL depends on it).
3. Visibility: **Public**. (GitHub Pages is free only on public repos. The code contains no secrets, and the app itself needs your Supabase login, so public is safe.)
4. Do **not** tick "Add a README". Click **Create repository**.

### 5b. Upload the folder — pick ONE method

**Method A — drag and drop in the browser (no tools needed)**
1. On the new empty repo page, click the link **"uploading an existing file"**.
2. Open the unzipped `gvl-events` folder in Finder/Explorer, select **everything inside it** (including `.github` — show hidden files first with Cmd+Shift+. on Mac), and drag into the browser upload area.
3. Wait for all files to list. Confirm you see `.github/workflows/crawl.yml` in the list. If it is missing, drag the `.github` folder in separately.
4. Commit message: `Initial app` → **Commit changes**.

**Method B — GitHub Desktop (if you have it)**
File → Add Local Repository → choose the `gvl-events` folder → Publish repository → name `gvl-events`, untick "Keep this code private".

**Method C — Terminal (Mac)**
```
cd ~/Desktop/gvl-events
git init
git add -A
git commit -m "Initial app"
git branch -M main
git remote add origin https://github.com/<your-username>/gvl-events.git
git push -u origin main
```

### 5c. Verify the upload
On the repo page you should see folders `.github`, `crawler`, `docs`, `supabase` and the `.md` files. If `.github` is missing, go back and add it; nothing will run daily without it.

### 5d. Paste the public keys into the app
1. In the repo, click **docs** → **config.js** → pencil icon (**Edit this file**).
2. Replace `https://YOUR-PROJECT-REF.supabase.co` with your `SUPABASE_URL` and `PASTE-YOUR-ANON-PUBLIC-KEY` with your `SUPABASE_ANON_KEY`. Keep the quotes.
3. **Commit changes** (green button, then confirm).

### 5e. Tell the crawler your app's address
1. Click **crawler** → **config.py** → pencil.
2. Find the line `APP_URL = "https://YOUR_GITHUB_USERNAME.github.io/gvl-events/"` and replace `YOUR_GITHUB_USERNAME` with your GitHub username.
3. **Commit changes**.

---

## 6. GitHub secrets — the private keys (3 min)

1. Repo → **Settings** (tab on the repo, not your profile) → left sidebar **Secrets and variables** → **Actions**.
2. Click **New repository secret** and add these one at a time. Name must match exactly (all caps, underscores):

| Name | Value from fill-in sheet |
|---|---|
| `SUPABASE_URL` | SUPABASE_URL |
| `SUPABASE_SERVICE_KEY` | SUPABASE_SERVICE_KEY (the secret one) |
| `PUSHOVER_TOKEN` | PUSHOVER_TOKEN |
| `PUSHOVER_USER` | PUSHOVER_USER |
| `TICKETMASTER_KEY` | TICKETMASTER_KEY (skip if you didn't do step 4) |

---

## 7. Turn on the app page (GitHub Pages) (2 min)

1. Repo → **Settings** → left sidebar **Pages**.
2. **Source**: **Deploy from a branch**.
3. **Branch**: `main`, folder: **/docs** → **Save**.
4. Wait 1–2 minutes, refresh the page; a box appears: "Your site is live at `https://<username>.github.io/gvl-events/`". That is your *App URL*.
5. Open it on your computer. You should see the dark green **GVL Events** sign-in screen. Sign in with your *App login email/password* from step 2c. It will say "You're caught up" because nothing has been crawled yet.

   If sign-in fails with "Invalid login credentials": re-check step 2c (user exists, auto-confirmed) and that `docs/config.js` has the right URL and anon key.

---

## 8. Run the first crawl (3 min)

1. Repo → **Actions** tab. If it says "Workflows aren't being run on this repository", click **I understand my workflows, go ahead and enable them**.
2. Left sidebar → **Daily event crawl** → right side **Run workflow** → **Run workflow** (green). Manual runs always run regardless of the time of day.
3. Click the run that appears → click **crawl** → expand **Crawl, store, notify**. You'll see one line per source:
   - `[ok]   Source name: 12 events` — working
   - `[fail] Source name: ...` — that site's structure differs from what the scraper expects. Normal for a few of them on the first run. Copy those lines and send them to Claude for a one-line fix.
   - A final line like `18 new events stored`.
4. Within a minute your iPhone should buzz: **"GVL Events: 18 new to review"**. If it doesn't, see Troubleshooting.

From now on it runs by itself every day at **12:00 PM Eastern** (the workflow fires at both 16:00 and 17:00 UTC and the script only proceeds when it is noon in Greenville, so daylight saving is handled).

---

## 9. Put it on your iPhone (1 min)

1. Open **Safari** on your iPhone and go to your App URL.
2. Sign in. (Safari keeps you signed in; you won't be asked again unless you clear site data.)
3. Tap the **Share** button (square with arrow) → scroll → **Add to Home Screen** → **Add**.
4. Open it from the Home Screen. It runs full-screen with no browser bar, like a native app.

Pushover notifications include an **Open GVL Events** button that opens the app directly.

---

## 10. Daily use

- **Noon**: Pushover shows the count and the five most social-looking new events.
- **New tab**: one card at a time. **Swipe right or tap Yes** / **swipe left or tap No**. No = gone forever. Cards are sorted social-first (★ high social = singles, mixers, run clubs, YP events).
- **Register / Tickets** button opens the signup page when one exists; **Details** opens the source page; **＋ Calendar** adds a one-off event to your iPhone Calendar (tap, then **Add**).
- **Going tab**: your yeses grouped by Today / Tomorrow / day name, with the same buttons. **Remove** if plans change.
- **Weekly tab**: recurring things you've said yes to (Run Club, Pub Run, leagues, Third Thursdays). These show once, not every week.

---

## 11. Tuning (no coding required)

All in `crawler/config.py` (edit in GitHub with the pencil, commit, and the next run uses it):
- `SOURCES` — add a line for any site with an events page. Kinds that work with zero new code: `jsonld` (most venue/calendar sites), `ical`, `rss`, `tribe` (WordPress "The Events Calendar" sites: use `https://site.com/wp-json/tribe/events/v1/events`), `eventbrite`, `meetup`.
- `EXCLUDE_KEYWORDS` — add words to block (e.g. `r"\bcomedy\b"`).
- `BLOCKED_CITIES` / `ALLOWED_CITIES` — geography.
- `LOOKAHEAD` — change `days=21` for a longer window.
- `crawler/curated_series.json` — hand-maintained recurring events for Instagram/Facebook-only groups. Add an entry and it appears as one card.

Reset everything (see all events again): Supabase → **Table Editor** → `events` → select all rows → **Delete**. The next run repopulates.

Change your app password: Supabase → **Authentication** → **Users** → your user → **⋯** → **Reset password** / **Send password recovery**.

---

## 12. Troubleshooting

| Symptom | Fix |
|---|---|
| Actions tab shows no workflow | `.github/workflows/crawl.yml` wasn't uploaded. Upload the `.github` folder (show hidden files first). |
| Run fails immediately with `KeyError: 'SUPABASE_URL'` | A secret name is misspelled or missing (step 6). Names are case-sensitive. |
| Run says `401` / `permission denied` writing to Supabase | You pasted the anon key as `SUPABASE_SERVICE_KEY`. Use the **service_role** key. |
| Run says `relation "events" does not exist` | Step 2b didn't run. Re-run `schema.sql` in the SQL Editor. |
| No Pushover notification but run succeeded | Check `PUSHOVER_USER`/`PUSHOVER_TOKEN` secrets; check iPhone Settings → Notifications → Pushover; the 30-day trial may have ended (buy the $4.99 unlock in the app). |
| App shows blank page | `docs/config.js` still has placeholders, or Pages isn't enabled (step 7). Open the URL in a desktop browser and check the console. |
| "Invalid login credentials" | User not auto-confirmed, wrong password, or wrong anon key in `config.js`. |
| App shows events but Yes/No doesn't stick | Row Level Security policies missing: re-run `schema.sql`. |
| Many `[fail]` sources | Expected on day one for scraped sites. Send the fail lines to Claude. Ticketmaster, Eventbrite, Meetup, MiLB and the WordPress calendars are the reliable core. |
| Didn't run at noon | GitHub sometimes delays scheduled runs 5–15 minutes. If it never ran, check the Actions tab for errors; GitHub also disables schedules on repos with no commits for 60 days (any edit re-enables it). |
| Home Screen icon opens but is logged out | iOS cleared site data (happens if unused for a week). Just sign in again; your decisions are in Supabase, not on the phone. |

---

## 13. What stays private and what doesn't

- **Public**: the code on GitHub (no secrets in it) and the app URL. Anyone opening the URL sees only a login screen.
- **Private**: your events and decisions (Supabase, login required), the service key, Pushover keys (GitHub Secrets, never visible after saving).
- The Supabase free tier pauses projects after **7 days with no activity**. The daily crawl counts as activity, so it will not pause as long as the schedule runs. If it ever does, open the Supabase dashboard and click **Restore project**.
