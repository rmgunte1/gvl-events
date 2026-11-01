# Source registry

Dating potential: ★★★ = rooms full of single people your age · ★★ = social, mixed crowd · ★ = good night out.
Method: how the crawler reads it. "Verify on first run" means the page structure was not confirmed live;
the first Actions log will say whether it worked.

## Aggregators
| Source | Method | Dating | Notes |
|---|---|---|---|
| GVLtoday events (6amcity.com) | JSON-LD / inline JSON | ★★ | Curated. Verify on first run. |
| VisitGreenvilleSC.com/events | JSON-LD | ★ | Simpleview CMS, usually has schema.org events. |
| Greenville.com calendar | JSON-LD | ★ | Verify on first run. |
| City of Greenville calendar | RSS (CivicPlus) | ★ | Downtown Alive, Main Street Fridays, festivals. |
| Eventbrite (5 category pages) | JSON-LD → `__SERVER_DATA__` fallback | ★★★ | Singles & speed-dating pages are the key ones. |
| AllEvents.in | JSON-LD | ★ | Noisy; dedupe handles overlap. |
| Ticketmaster Discovery API | API (needs free key) | ★ | Bon Secours Arena, Peace Center, touring acts. Most reliable source in the list. |

## Meetup
| Source | Method | Dating | Notes |
|---|---|---|---|
| 20's & 30's Social Meetup of Greenville | JSON-LD on group events page | ★★★ | |
| Running for Brews (Tue) | JSON-LD | ★★★ | |
| Casual and Refined Social Club | JSON-LD | ★★★ | ~2,000 members, silent discos, mixers. |
| Greenville Experience | JSON-LD | ★★ | ~2,500 members. |
| Bikes & Beers | JSON-LD | ★★ | |
| GNHA Hiking Club | JSON-LD | ★★ | |
| Meetup search (25 mi) | `__NEXT_DATA__` | ★★ | Catch-all; verify on first run. |

## Leagues, YP, alumni, church, volunteering
| Source | Method | Dating | Notes |
|---|---|---|---|
| Greenville Sports Leagues | HTML (LeagueLab) | ★★★ | Shown as registerable series; sign up as a free agent. |
| Greenville Chamber events (GCYP) | JSON-LD | ★★ | GCYP = former Pulse, ages 21–39. |
| Greenville Clemson Club | WordPress Events REST | ★★ | Brewery socials. |
| Upstate International | WordPress Events REST | ★★ | Salsa at Sunset, cultural nights. |
| Fleet Feet (Thu Pub Run) | JSON-LD + curated | ★★ | |
| City of Greenville VolunteerLocal | JSON-LD | ★★ | Festival volunteer shifts. |
| Christ Church Young Adults 23–39 | curated series | ★★ | Third Thursdays at The Commons. |

## Venues & sports
| Source | Method | Dating | Notes |
|---|---|---|---|
| Radio Room | JSON-LD | ★ | |
| Peace Center | JSON-LD | ★ | |
| Bon Secours Wellness Arena | JSON-LD (+Ticketmaster) | ★ | |
| Smiley's Acoustic Café | JSON-LD | ★ | |
| Greenville Drive | MLB Stats API | ★ | Home games only; season Apr–Sep. |
| Swamp Rabbits | JSON-LD | ★ | |
| Greenville Triumph | JSON-LD | ★ | |
| Songkick Greenville | JSON-LD | ★ | Cross-check for every venue. |

## Region
| Source | Method | Dating | Notes |
|---|---|---|---|
| Upcountry SC | WordPress Events REST | ★ | TR / Greer / Pickens festivals. |
| City of Greer | JSON-LD | ★ | |
| Travelers Rest | JSON-LD | ★ | |

## Manual-only (can't be crawled — kept as curated series cards)
Greenville Run Club (Instagram), Single Scene (Instagram), the Facebook singles groups, Tech After Five.
These show up once as a "Weekly / recurring" card with the link to check.

## Excluded on purpose
Spartanburg (all sources), Grace Church, anything tagged kids/family/youth, conferences/summits/webinars/certifications, bridal/wedding, 55+/seniors.
