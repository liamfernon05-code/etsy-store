"""UK-specific helpers: postcodes, nations, phone numbers, location presets, directory registry.

Facts here come from the UK research reports (research/uk/) and their critiques. Directory statuses carry an `as_of`
date and are deliberately conservative: "unverified" means we only saw it in listicles. Re-verify before relying on them.
"""

from __future__ import annotations

import re

AS_OF = "2026-10-03"
NATIONS = {"ENG": "England", "WAL": "Wales", "SCO": "Scotland", "NIR": "Northern Ireland"}
_NATION_ALIASES = {
    "england": "ENG", "eng": "ENG", "wales": "WAL", "cymru": "WAL", "wal": "WAL", "scotland": "SCO", "sco": "SCO",
    "northern ireland": "NIR", "nir": "NIR", "ni": "NIR",
}

# UK postcode (outward + inward). Accepts GIR 0AA. Crown dependencies (JE, GY, IM) match the pattern but are NOT UK.
POSTCODE_RE = re.compile(r"^(GIR ?0AA|[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2})$")
CROWN_DEPENDENCY_AREAS = {"JE": "Jersey", "GY": "Guernsey", "IM": "Isle of Man"}

# Postcode AREA -> nation, only where the area is (almost) entirely in one nation. Border areas are left to resolve via
# postcodes.io or an explicit `nation` in client.toml, never guessed.
_SCOTLAND_AREAS = {"AB", "DD", "DG", "EH", "FK", "G", "HS", "IV", "KA", "KW", "KY", "ML", "PA", "PH", "ZE"}
_WALES_AREAS = {"CF", "LL", "SA", "LD"}
_BORDER_AREAS = {"TD", "CA", "NP", "SY", "CH", "HR", "GL", "SN", "BS", "WS", "DY", "WV", "WR"}  # ambiguous: do not guess


def normalise_postcode(pc: str) -> str:
    pc = re.sub(r"\s+", "", (pc or "").upper())
    return f"{pc[:-3]} {pc[-3:]}" if len(pc) >= 5 else pc


def is_valid_postcode(pc: str) -> bool:
    return bool(POSTCODE_RE.match(normalise_postcode(pc)))


def postcode_area(pc: str) -> str:
    m = re.match(r"^([A-Z]{1,2})", normalise_postcode(pc))
    return m.group(1) if m else ""


def postcode_district(pc: str) -> str:
    return normalise_postcode(pc).split(" ")[0] if pc else ""


def nation_from_nation_text(text: str) -> str:
    return _NATION_ALIASES.get((text or "").strip().lower(), "")


def nation_from_postcode(pc: str) -> str:
    """'ENG' | 'WAL' | 'SCO' | 'NIR' | 'CD' (Crown dependency, out of scope) | '' (ambiguous or invalid)."""
    area = postcode_area(pc)
    if not area or not is_valid_postcode(pc):
        return ""
    if area in CROWN_DEPENDENCY_AREAS:
        return "CD"
    if area == "BT":
        return "NIR"
    if area in _SCOTLAND_AREAS:
        return "SCO"
    if area in _WALES_AREAS:
        return "WAL"
    if area in _BORDER_AREAS:
        return ""
    return "ENG"


def normalise_uk_phone(raw: str) -> str:
    """E.164 (+44...) for a UK number written nationally or internationally; '' if it does not look UK."""
    d = re.sub(r"[^\d+]", "", raw or "")
    if d.startswith("+44"):
        d = d[3:]
    elif d.startswith("0044"):
        d = d[4:]
    elif d.startswith("0"):
        d = d[1:]
    else:
        return ""
    d = d.lstrip("0") if d.startswith("0") else d
    return f"+44{d}" if 9 <= len(d) <= 10 and d[0] in "1235789" else ""


def uk_phone_kind(raw: str) -> str:
    e = normalise_uk_phone(raw)
    if not e:
        return "unknown"
    n = e[3:]
    if n.startswith(("1", "2")):
        return "geographic"
    if n.startswith("3"):
        return "03 (non-geographic, geographic-rate; common for call tracking)"
    if n.startswith("7"):
        return "mobile"
    if n.startswith("800") or n.startswith("808"):
        return "freephone"
    return "other"


# City presets for API user_location (all coordinates cross-checked by the UK critic to within 0.05 deg).
UK_LOCATIONS: dict[str, dict] = {
    "london": {"city": "London", "region": "Greater London", "country_name": "England", "lat": 51.5074, "lng": -0.1278},
    "manchester": {"city": "Manchester", "region": "Greater Manchester", "country_name": "England", "lat": 53.4808, "lng": -2.2426},
    "birmingham": {"city": "Birmingham", "region": "West Midlands", "country_name": "England", "lat": 52.4862, "lng": -1.8904},
    "leeds": {"city": "Leeds", "region": "West Yorkshire", "country_name": "England", "lat": 53.8008, "lng": -1.5491},
    "sheffield": {"city": "Sheffield", "region": "South Yorkshire", "country_name": "England", "lat": 53.3811, "lng": -1.4701},
    "bristol": {"city": "Bristol", "region": "Bristol", "country_name": "England", "lat": 51.4545, "lng": -2.5879},
    "newcastle": {"city": "Newcastle upon Tyne", "region": "Tyne and Wear", "country_name": "England", "lat": 54.9783, "lng": -1.6178},
    "liverpool": {"city": "Liverpool", "region": "Merseyside", "country_name": "England", "lat": 53.4084, "lng": -2.9916},
    "nottingham": {"city": "Nottingham", "region": "Nottinghamshire", "country_name": "England", "lat": 52.9548, "lng": -1.1581},
    "leicester": {"city": "Leicester", "region": "Leicestershire", "country_name": "England", "lat": 52.6369, "lng": -1.1398},
    "southampton": {"city": "Southampton", "region": "Hampshire", "country_name": "England", "lat": 50.9097, "lng": -1.4044},
    "glasgow": {"city": "Glasgow", "region": "Glasgow City", "country_name": "Scotland", "lat": 55.8642, "lng": -4.2518},
    "edinburgh": {"city": "Edinburgh", "region": "City of Edinburgh", "country_name": "Scotland", "lat": 55.9533, "lng": -3.1883},
    "aberdeen": {"city": "Aberdeen", "region": "Aberdeen City", "country_name": "Scotland", "lat": 57.1497, "lng": -2.0943},
    "inverness": {"city": "Inverness", "region": "Highland", "country_name": "Scotland", "lat": 57.4778, "lng": -4.2247},
    "cardiff": {"city": "Cardiff", "region": "Cardiff", "country_name": "Wales", "lat": 51.4816, "lng": -3.1791},
    "swansea": {"city": "Swansea", "region": "Swansea", "country_name": "Wales", "lat": 51.6214, "lng": -3.9436},
    "belfast": {"city": "Belfast", "region": "Belfast", "country_name": "Northern Ireland", "lat": 54.5973, "lng": -5.9301},
    "derry": {"city": "Derry/Londonderry", "region": "Derry City and Strabane", "country_name": "Northern Ireland", "lat": 54.9966, "lng": -7.3086},
}


def lookup_city(city: str) -> dict | None:
    key = re.sub(r"[^a-z ]", "", (city or "").lower()).strip()
    key = {"newcastle upon tyne": "newcastle", "londonderry": "derry", "derry/londonderry": "derry"}.get(key, key)
    return UK_LOCATIONS.get(key)


# ---- directory registry ------------------------------------------------------------------------------------------
# status: active | unverified | closing_2026_10 | brand_only_checkatrade_owned | defunct
# role codes: F feeds/corroborates map+search data, AI cited by assistants in UK studies (directional), T trust signal,
#             R regulator/official register, L lead-gen marketplace
DIRECTORIES: dict[str, dict] = {
    "Google Business Profile": {"status": "active", "role": "F,AI,T", "note": "Primary for every vertical."},
    "Bing Places": {"status": "active", "role": "F,AI", "note": "Feeds Bing/Copilot and assistants that use Bing."},
    "Apple Business": {"status": "active", "role": "F", "note": "Renamed from Apple Business Connect on 2026-04-14; Apple Maps/Siri."},
    "Facebook": {"status": "active", "role": "T,F", "note": "Heavy UK local-discovery use."},
    "Yell": {"status": "active", "role": "F", "note": "Rarely cited by assistants; matters as data/trust source."},
    "Trustpilot": {"status": "active", "role": "T", "note": "Invite all customers or an impartial sample."},
    "Companies House": {"status": "active", "role": "R", "note": "Free register; verify company status. Sole traders/partnerships are not on it."},
    "Checkatrade": {"status": "active", "role": "L,AI,T", "note": "Most-cited UK trades source in ONE vendor ChatGPT study (directional; has a ChatGPT app)."},
    "MyBuilder": {"status": "active", "role": "L,AI,T", "note": "Owned by Angi Inc. Cited in the same single-vendor study."},
    "Rated People": {"status": "brand_only_checkatrade_owned", "role": "L", "note": "Company entered liquidation 2026-09-16; Checkatrade bought brand/site; trade memberships not transferred. Do not recommend a new membership."},
    "TrustATrader": {"status": "active", "role": "L,T", "note": ""},
    "Which? Trusted Trader": {"status": "active", "role": "T", "note": ""},
    "Bark": {"status": "active", "role": "L", "note": "Credit-based leads; weak trust signal."},
    "TrustMark": {"status": "active", "role": "T,R", "note": "Government-endorsed; joined via a scheme provider."},
    "Buy With Confidence": {"status": "unverified", "role": "T", "note": "Trading Standards scheme; confirm local availability."},
    "Gas Safe Register": {"status": "active", "role": "R", "note": "Covers GB, Northern Ireland, Isle of Man and Guernsey."},
    "NICEIC": {"status": "active", "role": "R,T", "note": ""},
    "NAPIT": {"status": "unverified", "role": "R,T", "note": ""},
    "SELECT": {"status": "unverified", "role": "R,T", "note": "Scotland electrical trade body."},
    "SNIPEF": {"status": "unverified", "role": "R,T", "note": "Scotland plumbing/heating trade body."},
    "Federation of Master Builders": {"status": "unverified", "role": "T", "note": ""},
    "TripAdvisor": {"status": "active", "role": "F,AI,T", "note": ""},
    "TheFork": {"status": "active", "role": "F,T", "note": "TripAdvisor-owned reservations."},
    "OpenTable": {"status": "active", "role": "F,T", "note": ""},
    "Just Eat": {"status": "active", "role": "F,L", "note": "Prosus-owned (Oct 2025). Subject of a CMA fake-review investigation opened 2026-03-27."},
    "Deliveroo": {"status": "active", "role": "F,L", "note": "DoorDash-owned (completed 2025-10-02)."},
    "Uber Eats": {"status": "active", "role": "F,L", "note": ""},
    "Good Food Guide": {"status": "active", "role": "T", "note": "Digital since 2022."},
    "Hardens / SquareMeal / CAMRA WhatPub": {"status": "unverified", "role": "T", "note": "Editorial 'best of' / pub guides."},
    "Food hygiene rating (FHRS/FHIS)": {"status": "active", "role": "R,T", "note": "FHRS 0-5 in England/Wales/NI; Scotland uses FHIS (Pass / Improvement Required / Exempt / Awaiting Inspection)."},
    "Treatwell": {"status": "active", "role": "L,T", "note": "Marketplace: vendors report ~35% of a first booking (last seen 2026; verify the current terms before relying on it)."},
    "Fresha": {"status": "active", "role": "L,T", "note": "Marketplace: vendors report ~20% on new-client bookings (verify)."},
    "Booksy": {"status": "active", "role": "L,T", "note": "Strong with barbers; vendors report a monthly fee plus a percentage on new clients (verify)."},
    "Doctify": {"status": "active", "role": "T,AI", "note": "Private/cosmetic healthcare; appointment-verified reviews."},
    "Law Society Find a Solicitor": {"status": "active", "role": "F,R,T", "note": "England & Wales."},
    "SRA register": {"status": "active", "role": "R", "note": "England & Wales only."},
    "Law Society of Scotland find-a-solicitor": {"status": "unverified", "role": "F,R,T", "note": "Scotland."},
    "Law Society of Northern Ireland": {"status": "unverified", "role": "F,R,T", "note": "Northern Ireland."},
    "Legal 500 / Chambers": {"status": "active", "role": "T,AI", "note": "Editorial rankings."},
    "GDC register": {"status": "active", "role": "R", "note": "UK-wide; clinician registration numbers."},
    "Instagram": {"status": "active", "role": "T,F", "note": "Main portfolio channel for beauty studios; keep the name identical to GBP/signage."},
    "Healthcare Improvement Scotland register": {"status": "active", "role": "R", "note": "Scotland: independent healthcare services (clinician-delivered); check whether the service is registrable."},
    "Thomson Local": {"status": "unverified", "role": "F", "note": "Only weak evidence it is still operating."},
    "Cylex UK": {"status": "unverified", "role": "F", "note": "Listicle evidence only."},
    "FreeIndex": {"status": "unverified", "role": "F", "note": "Listicle evidence only."},
    "Hotfrog UK": {"status": "unverified", "role": "F", "note": ""},
    "118Information / ThePhoneBook": {"status": "unverified", "role": "F", "note": ""},
    "Yelp UK": {"status": "unverified", "role": "F", "note": "Weak in the UK; licensed to ChatGPT (US-led, 2026-07)."},
    "Scoot": {"status": "closing_2026_10", "role": "F", "note": "Own site says it is winding down in October 2026."},
    "Touch Local": {"status": "closing_2026_10", "role": "F", "note": "Own site says it is winding down in October 2026."},
    "Factual": {"status": "defunct", "role": "F", "note": "Merged into Foursquare in 2020."},
}

# Nation-specific official listings / regulators, by vertical key -> nation -> names
OFFICIAL_BY_NATION: dict[str, dict[str, list[str]]] = {
    "dentist": {
        "ENG": ["NHS.uk (Find a dentist)", "CQC", "GDC register"],
        "WAL": ["NHS 111 Wales", "Healthcare Inspectorate Wales (HIW)", "GDC register"],
        "SCO": ["NHS inform", "Care Inspectorate / Healthcare Improvement Scotland", "GDC register"],
        "NIR": ["HSC / nidirect", "RQIA", "GDC register"],
    },
    "lawyer": {
        "ENG": ["SRA register", "Law Society Find a Solicitor"],
        "WAL": ["SRA register", "Law Society Find a Solicitor"],
        "SCO": ["Law Society of Scotland find-a-solicitor"],
        "NIR": ["Law Society of Northern Ireland"],
    },
    "restaurant": {
        "ENG": ["Food hygiene rating (FHRS)"], "WAL": ["Food hygiene rating (FHRS)"],
        "NIR": ["Food hygiene rating (FHRS)"], "SCO": ["Food hygiene rating (FHIS)"],
    },
}
