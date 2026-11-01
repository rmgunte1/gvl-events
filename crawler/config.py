"""Central configuration: geography, filters, categories, and the source registry.

Edit this file to add/remove sources or tune filters. Nothing else needs to change.
"""
from datetime import timedelta

TIMEZONE = "America/New_York"
LOOKAHEAD = timedelta(days=21)        # how far ahead to show one-off events
RUN_HOUR_LOCAL = 12                   # only run the full job at noon ET
import os as _os
# App URL is derived automatically from the GitHub repo (owner.github.io/repo).
_repo = _os.environ.get("GITHUB_REPOSITORY", "your_github_username/gvl-events")
APP_URL = _os.environ.get("APP_URL") or f"https://{_repo.split('/')[0]}.github.io/{_repo.split('/')[1]}/"

# Cities within ~25 miles of downtown Greenville (Spartanburg intentionally excluded).
ALLOWED_CITIES = {
    "greenville", "greer", "taylors", "travelers rest", "simpsonville", "mauldin",
    "fountain inn", "easley", "piedmont", "pelzer", "clemson", "central", "pickens",
    "marietta", "landrum", "duncan", "lyman", "wellford", "powdersville", "five forks",
    "berea", "wade hampton", "parker", "sans souci", "tigerville", "slater", "cleveland",
    "liberty", "williamston", "belton", "moore", "reidville", "campobello", "gowensville",
}
BLOCKED_CITIES = {"spartanburg", "anderson", "asheville", "hendersonville", "charlotte",
                  "columbia", "greenwood", "seneca", "walhalla"}

# Anything matching these (case-insensitive, word-ish) is dropped.
EXCLUDE_KEYWORDS = [
    r"\bkids?\b", r"\bchildren'?s?\b", r"\bfamily\b", r"\byouth\b", r"\btoddler", r"\bpreschool",
    r"\bstory ?time\b", r"\bsummer camp\b", r"\bday camp\b", r"\bhomeschool", r"\bparents?\b",
    r"\bconference\b", r"\bsummit\b", r"\bwebinar\b", r"\bcertification\b", r"\bcertified\b",
    r"\bb2b\b", r"\bluncheon\b", r"\bbridal\b", r"\bwedding\b", r"\bseniors?\b", r"\b55\+",
    r"\bsix sigma\b", r"\bpmp\b", r"\bbootcamp\b", r"\bcareer fair\b", r"\bjob fair\b",
    r"\bworship service\b", r"\bbible study\b", r"\bschool board\b", r"\bcity council\b",
    r"\bcouncil meeting\b", r"\bpublic hearing\b", r"\bboard meeting\b", r"\bzoning\b",
]

# Category keywords. First match wins, in this order.
CATEGORY_RULES = [
    ("social", [r"\bsingles?\b", r"speed dat", r"\bmixer\b", r"\btrivia\b", r"\brun club\b",
                r"\bpub run\b", r"running for brews", r"\bmeetup\b", r"young professional",
                r"\bvolunteer", r"\bhappy hour\b", r"\bsocial\b", r"\bkickball\b", r"\bleague\b",
                r"\bbrewery\b", r"\bbrewing\b", r"\btaproom\b", r"\bgame night\b", r"\bbingo\b",
                r"\bkaraoke\b", r"\bsalsa\b", r"\bswing\b", r"\bline danc", r"\bsilent disco\b",
                r"\bhike\b", r"\bhiking\b", r"\bgroup ride\b", r"\bbikes? ?(&|and) beers\b",
                r"\bpaint (&|and) sip\b", r"\bwine tasting\b", r"\bbeer fest", r"\boktoberfest\b",
                r"\bnetworking\b", r"\bclemson club\b", r"\balumni\b", r"\byoung adults?\b"]),
    ("sports", [r"\bvs\.?\b", r"\bswamp rabbits\b", r"\bgreenville drive\b", r"\btriumph\b",
                r"\bfurman\b", r"\bpaladins\b", r"\bclemson tigers\b", r"\bwatch party\b",
                r"\bhome game\b", r"\bhockey\b", r"\bbaseball\b", r"\bsoccer\b", r"\bfootball\b",
                r"\b5k\b", r"\b10k\b", r"\bhalf marathon\b", r"\bmarathon\b", r"\brace\b"]),
    ("music", [r"\bconcert\b", r"\blive music\b", r"\btour\b", r"\bband\b", r"\bw/\b",
               r"\bpresents\b", r"\bdj\b", r"\bjazz\b", r"\bbluegrass\b", r"\bacoustic\b",
               r"\bsymphony\b", r"\bopera\b", r"\balbum\b", r"\bsinger", r"\bsongwriter"]),
    ("festival", [r"\bfestival\b", r"\bfest\b", r"\bfair\b", r"\bmarket\b", r"\bparade\b",
                  r"\bdowntown alive\b", r"\bmain street fridays\b", r"\bartisphere\b",
                  r"\bfall for greenville\b", r"\beuphoria\b", r"\bfood truck"]),
]

# Extra weight for the kinds of events most likely to put you in a room with people.
SOCIAL_SCORE_KEYWORDS = {
    r"\bsingles?\b": 5, r"speed dat": 5, r"\bmixer\b": 4, r"young professional": 4,
    r"\brun club\b": 4, r"\bpub run\b": 4, r"running for brews": 4, r"\btrivia\b": 3,
    r"\bkickball\b": 3, r"\bleague\b": 2, r"\bvolunteer": 3, r"\bsocial\b": 3,
    r"\bsalsa\b": 3, r"\bsilent disco\b": 3, r"\bgame night\b": 3, r"\bhappy hour\b": 2,
    r"\bbrewery\b": 2, r"\bmeetup\b": 2, r"\byoung adults?\b": 3, r"\bnetworking\b": 2,
    r"\bfestival\b": 2, r"\bfest\b": 1, r"\bbeer\b": 1, r"\bwine\b": 1,
}

# ---------------------------------------------------------------------------
# SOURCE REGISTRY
# kind: jsonld | nextdata | ical | rss | tribe | eventbrite | meetup | leaguelab |
#       ticketmaster | milb | curated
# Every source is isolated: a failure is logged and the rest continue.
# ---------------------------------------------------------------------------
SOURCES = [
    # --- Aggregators -------------------------------------------------------
    # Blocked from GitHub's servers (bot protection), so not listed: Eventbrite,
    # Songkick, Peace Center, Upcountry SC, Greenville Chamber. AllEvents mirrors
    # most Eventbrite listings and Ticketmaster covers the arena.
    {"name": "GVLtoday events", "kind": "jsonld",
     "url": "https://6amcity.com/sc/greenville/events"},
    {"name": "VisitGreenvilleSC", "kind": "jsonld",
     "url": "https://www.visitgreenvillesc.com/events/"},
    {"name": "Greenville.com calendar", "kind": "jsonld",
     "url": "https://www.greenville.com/calendar/"},
    {"name": "AllEvents Greenville", "kind": "jsonld",
     "url": "https://allevents.in/greenville-sc/all"},
    {"name": "Ticketmaster (arena, Peace Center, touring)", "kind": "ticketmaster"},

    # --- Meetup groups -------------------------------------------------------
    {"name": "Meetup - 20s & 30s of Greenville", "kind": "meetup",
     "url": "https://www.meetup.com/20sand30sofgreenville/events/"},
    {"name": "Meetup - Running for Brews", "kind": "meetup",
     "url": "https://www.meetup.com/running-for-brews-greenville-5k-beer-running-club/events/"},
    {"name": "Meetup - 30s & 40s of Greenville", "kind": "meetup",
     "url": "https://www.meetup.com/30sand40sofgreenvillesc/events/"},
    {"name": "Meetup - Greer Social Group", "kind": "meetup",
     "url": "https://www.meetup.com/greer-social-group/events/"},
    {"name": "Meetup - Sunday Coffee Lovers", "kind": "meetup",
     "url": "https://www.meetup.com/sunday-coffee-lovers-greenville/events/"},
    {"name": "Meetup - GNHA Hiking Club", "kind": "meetup",
     "url": "https://www.meetup.com/gnha-hiking-club/events/"},
    {"name": "Meetup - Greenville search", "kind": "nextdata",
     "url": "https://www.meetup.com/find/?location=us--sc--greenville&source=EVENTS&distance=twentyFiveMiles"},

    # --- Leagues / YP / alumni / church ----------------------------------------
    {"name": "Greenville Sports Leagues", "kind": "leaguelab",
     "url": "https://playgreenville.leaguelab.com/leagues"},
    {"name": "Clemson Alumni (Greenville Clemson Club)", "kind": "tribe",
     "url": "https://alumni.clemson.edu/wp-json/tribe/events/v1/events?per_page=50&start_date=now"},
    {"name": "Upstate International", "kind": "jsonld",
     "url": "https://upstateinternational.org/calendar", "city": "Greenville"},
    {"name": "Fleet Feet Greenville", "kind": "jsonld",
     "url": "https://www.fleetfeet.com/s/greenville/events", "category": "social", "city": "Greenville"},
    {"name": "City of Greenville VolunteerLocal", "kind": "jsonld",
     "url": "https://cityofgreenville.volunteerlocal.com/volunteer/", "category": "social", "city": "Greenville"},

    # --- Venues / sports ------------------------------------------------------
    {"name": "Greenville Drive (MiLB schedule)", "kind": "milb", "team_id": 428},
    {"name": "Greenville Triumph", "kind": "jsonld",
     "url": "https://www.greenvilletriumph.com/schedule", "category": "sports", "city": "Greenville"},

    # --- Region (TR / Greer / Upcountry) -----------------------------------
    {"name": "City of Greer events", "kind": "jsonld", "url": "https://www.cityofgreer.org/events", "city": "Greer"},
    {"name": "Travelers Rest events", "kind": "jsonld",
     "url": "https://www.travelersrestsc.com/events", "city": "Travelers Rest"},

    # --- Hand-curated recurring series (Instagram/Facebook-only groups) ----
    {"name": "Curated series", "kind": "curated", "path": "curated_series.json"},
]
