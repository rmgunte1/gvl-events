from . import jsonld, feeds, platforms

FETCHERS = {
    "jsonld": jsonld.fetch,
    "nextdata": jsonld.fetch,
    "ical": feeds.fetch_ical,
    "rss": feeds.fetch_rss,
    "tribe": feeds.fetch_tribe,
    "eventbrite": platforms.fetch_eventbrite,
    "meetup": platforms.fetch_meetup,
    "leaguelab": platforms.fetch_leaguelab,
    "ticketmaster": platforms.fetch_ticketmaster,
    "milb": platforms.fetch_milb,
    "curated": platforms.fetch_curated,
}
