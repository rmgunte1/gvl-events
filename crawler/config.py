"""Central configuration: geography, filters, categories, and the source registry.

Edit this file to add/remove sources or tune filters. Nothing else needs to change.
"""
from datetime import timedelta

TIMEZONE = "America/New_York"
from datetime import date as _date
_today = _date.today()
# Holiday window: Nov 1 – Jan 5 look 6 weeks ahead (parties and NYE tickets go early).
_in_holiday_window = _today.month in (11, 12) or (_today.month == 1 and _today.day <= 5)
LOOKAHEAD = timedelta(days=42 if _in_holiday_window else 21)   # how far ahead to show one-off events

# Holiday "do you have a plan?" checks fire 10 and 3 days before each of these.
HOLIDAYS = [
    ("Thanksgiving", _date(2026, 11, 26)), ("Christmas Eve", _date(2026, 12, 24)),
    ("Christmas Day", _date(2026, 12, 25)), ("New Year's Eve", _date(2026, 12, 31)),
    ("Valentine's Day", _date(2027, 2, 14)), ("July 4th", _date(2027, 7, 4)),
    ("Thanksgiving", _date(2027, 11, 25)), ("Christmas Eve", _date(2027, 12, 24)),
    ("Christmas Day", _date(2027, 12, 25)), ("New Year's Eve", _date(2027, 12, 31)),
]
HOST_PROMPT_EVERY_WEEKS = 3
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
    r"friendsgiving": 5, r"\bthanksgiving\b": 3, r"\borphan": 4, r"\bugly sweater\b": 4,
    r"holiday party": 4, r"christmas party": 4, r"\bnye\b": 4, r"new year'?s eve": 4,
    r"\bimprov\b": 3, r"\bclass\b": 1, r"\bworkshop\b": 1, r"\bclimb": 2, r"\bbouldering\b": 3,
    r"\bsupper club\b": 4, r"\bpotluck\b": 4, r"\btopgolf\b": 2, r"\baxe throwing\b": 2,
}

# ---------------------------------------------------------------------------
# SOURCE REGISTRY
# kind: jsonld | nextdata | ical | rss | tribe | eventbrite | meetup | leaguelab |
#       ticketmaster | milb | curated
# Every source is isolated: a failure is logged and the rest continue.
# Events already stored from these sources are deleted on the next run.
REMOVED_SOURCES = ["Meetup - Greer Social Group"]
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

    # --- Meetup category pages (wide net) ------------------------------------
    {"name": "Meetup - social activities", "kind": "nextdata",
     "url": "https://www.meetup.com/find/us--sc--greenville/social-activities/"},
    {"name": "Meetup - outdoors", "kind": "nextdata",
     "url": "https://www.meetup.com/find/us--sc--greenville/outdoor-activities/"},
    {"name": "Meetup - sports & fitness", "kind": "nextdata",
     "url": "https://www.meetup.com/find/us--sc--greenville/sports-fitness/"},
    {"name": "Meetup - games", "kind": "nextdata",
     "url": "https://www.meetup.com/find/us--sc--greenville/games/"},
    {"name": "Meetup - dancing", "kind": "nextdata",
     "url": "https://www.meetup.com/find/us--sc--greenville/dancing/"},
    {"name": "Meetup - food & drink", "kind": "nextdata",
     "url": "https://www.meetup.com/find/us--sc--greenville/food-and-drink/"},
    {"name": "Meetup - West Coast Swing Dance Club", "kind": "meetup",
     "url": "https://www.meetup.com/greenville-west-coast-swing-dance-club/events/"},

    # --- Fitness-social / dance / veterans ----------------------------------
    {"name": "SweatPals Greenville", "kind": "jsonld",
     "url": "https://sweatpals.com/s/greenville/social-events", "category": "social", "city": "Greenville"},
    {"name": "Salsa Greenville (SalsaVida)", "kind": "jsonld",
     "url": "https://www.salsavida.com/guides/south-carolina/greenville", "category": "social", "city": "Greenville"},
    {"name": "Team RWB Greenville", "kind": "jsonld",
     "url": "https://members.teamrwb.org/events?chapter=greenville-sc", "category": "social", "city": "Greenville"},

    # --- Breweries (trivia, bingo, markets, releases) -------------------------
    {"name": "Fireforge Crafted Beer", "kind": "jsonld", "url": "https://fireforge.beer/events", "category": "social", "city": "Greenville"},
    {"name": "Birds Fly South Ale Project", "kind": "jsonld", "url": "https://www.bfsbeer.com/events", "category": "social", "city": "Greenville"},
    {"name": "Liability Brewing", "kind": "jsonld", "url": "https://www.liabilitybrewing.co/events", "category": "social", "city": "Greenville"},
    {"name": "Carolina Bauernhaus", "kind": "jsonld", "url": "https://www.carolinabauernhaus.com/events", "category": "social", "city": "Greenville"},
    {"name": "Thomas Creek Brewery", "kind": "jsonld", "url": "https://www.thomascreekbeer.com/events", "category": "social", "city": "Greenville"},
    {"name": "Double Stamp Brewery", "kind": "jsonld", "url": "https://www.doublestampbrewery.com/events", "category": "social", "city": "Greenville"},
    {"name": "13 Stripes Brewery", "kind": "jsonld", "url": "https://www.13stripesbrewery.com/events", "category": "social", "city": "Taylors"},
    {"name": "Swamp Rabbit Brewery (TR)", "kind": "jsonld", "url": "https://www.theswamprabbitbrewery.com/events", "category": "social", "city": "Travelers Rest"},
    {"name": "Southernside Brewing", "kind": "jsonld", "url": "https://www.southernsidebrewing.com/events", "category": "social", "city": "Greenville"},

    # --- Sports / volunteering / library -------------------------------------
    {"name": "Furman Athletics (iCal)", "kind": "ical",
     "url": "https://furmanpaladins.com/calendar.ashx/calendar.ics", "category": "sports", "city": "Greenville"},
    {"name": "United Way Greenville volunteer calendar", "kind": "jsonld",
     "url": "https://ps0311.handsonconnect.org/opportunities", "category": "social", "city": "Greenville"},
    {"name": "Habitat for Humanity Greenville events", "kind": "jsonld",
     "url": "https://www.habitatgreenville.org/events/", "category": "social", "city": "Greenville"},
    {"name": "Greenville County Library events", "kind": "jsonld",
     "url": "https://www.greenvillelibrary.org/events", "city": "Greenville"},

    # --- AllEvents category pages --------------------------------------------
    {"name": "AllEvents - parties & nightlife", "kind": "jsonld", "url": "https://allevents.in/greenville-sc/parties"},
    {"name": "AllEvents - music", "kind": "jsonld", "url": "https://allevents.in/greenville-sc/music"},
    {"name": "AllEvents - meetups", "kind": "jsonld", "url": "https://allevents.in/greenville-sc/meetups"},
    {"name": "AllEvents - sports", "kind": "jsonld", "url": "https://allevents.in/greenville-sc/sports"},

    # --- Holiday-specific nets (Meetup keyword searches, AllEvents holiday pages) --
    {"name": "Meetup - friendsgiving/thanksgiving", "kind": "nextdata",
     "url": "https://www.meetup.com/find/?keywords=thanksgiving&location=us--sc--greenville&source=EVENTS&distance=twentyFiveMiles"},
    {"name": "Meetup - christmas/holiday", "kind": "nextdata",
     "url": "https://www.meetup.com/find/?keywords=christmas&location=us--sc--greenville&source=EVENTS&distance=twentyFiveMiles"},
    {"name": "Meetup - new year's eve", "kind": "nextdata",
     "url": "https://www.meetup.com/find/?keywords=new%20years&location=us--sc--greenville&source=EVENTS&distance=twentyFiveMiles"},
    {"name": "Meetup - singles", "kind": "nextdata",
     "url": "https://www.meetup.com/find/?keywords=singles&location=us--sc--greenville&source=EVENTS&distance=twentyFiveMiles"},
    {"name": "AllEvents - christmas", "kind": "jsonld", "url": "https://allevents.in/greenville-sc/christmas"},
    {"name": "AllEvents - thanksgiving", "kind": "jsonld", "url": "https://allevents.in/greenville-sc/thanksgiving"},
    {"name": "AllEvents - new year", "kind": "jsonld", "url": "https://allevents.in/greenville-sc/new-year"},

    # --- Races (RunSignUp public API: every 5K/8K/turkey trot in 25 mi) ----------
    {"name": "RunSignUp races", "kind": "runsignup"},

    # --- Repeat-exposure classes & venues ---------------------------------------
    {"name": "Alchemy Comedy Theatre", "kind": "jsonld", "url": "https://www.alchemycomedy.com/shows", "category": "social", "city": "Greenville"},
    {"name": "BlocHaven climbing", "kind": "jsonld", "url": "https://www.blochaven.com/events", "category": "social", "city": "Greenville"},
    {"name": "Greenville Center for Creative Arts", "kind": "jsonld", "url": "https://artcentergreenville.org/events/", "city": "Greenville"},
    {"name": "The Community Tap", "kind": "jsonld", "url": "https://www.thecommunitytap.com/events", "category": "social", "city": "Greenville"},
    {"name": "Northampton Wines", "kind": "jsonld", "url": "https://www.northamptonwines.com/events", "category": "social", "city": "Greenville"},
    {"name": "Greenville Little Theatre", "kind": "jsonld", "url": "https://www.greenvillelittletheatre.org/", "city": "Greenville"},
    {"name": "Topgolf Greenville", "kind": "jsonld", "url": "https://topgolf.com/us/greenville/events/", "category": "social", "city": "Greenville"},

    # --- Holiday volunteering -----------------------------------------------------
    {"name": "Meals on Wheels Greenville", "kind": "jsonld", "url": "https://www.mowgvl.org/events/", "category": "social", "city": "Greenville"},
    {"name": "Harvest Hope Food Bank", "kind": "jsonld", "url": "https://www.harvesthope.org/events/", "category": "social", "city": "Greenville"},
    {"name": "Roper Mountain Holiday Lights", "kind": "jsonld", "url": "https://www.ropermountainholidaylights.com/", "city": "Greenville"},
    {"name": "Salvation Army Greenville", "kind": "jsonld", "url": "https://southernusa.salvationarmy.org/greenville/events/", "category": "social", "city": "Greenville"},

    # --- Hand-curated recurring series (Instagram/Facebook-only groups) ----
    {"name": "Curated series", "kind": "curated", "path": "curated_series.json"},
]
