"""Market layer: US vs UK (everything else is "OTHER": generic checks only, with a loud warning).

The same pipeline runs for every market; what changes is encoded here: API location parameters, prompt wording,
currency/timezone, and which compliance pack applies. Crown Dependencies (Jersey, Guernsey, Isle of Man) are NOT the UK:
they share +44 numbers and look like UK postcodes, but have their own law and ISO codes, so they resolve to OTHER.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import uk

if TYPE_CHECKING:  # pragma: no cover
    from .models import ClientProfile

_US = {"US", "USA", "UNITED STATES", "UNITED STATES OF AMERICA"}
_UK = {"UK", "GB", "GBR", "UNITED KINGDOM", "GREAT BRITAIN", "ENGLAND", "SCOTLAND", "WALES", "NORTHERN IRELAND"}
_CROWN = {"JE", "JERSEY", "GG", "GY", "GUERNSEY", "IM", "ISLE OF MAN"}


def market_code(jurisdiction: str) -> str:
    j = (jurisdiction or "").strip().upper()
    if j in _UK:
        return "UK"
    if j in _US or not j:
        return "US"
    return "OTHER"


@dataclass(frozen=True)
class Market:
    code: str
    country_iso: str
    currency: str
    timezone: str
    language: str
    currency_symbol: str

    @property
    def is_uk(self) -> bool:
        return self.code == "UK"


MARKETS = {
    "US": Market("US", "US", "USD", "America/Chicago", "en-US", "$"),
    "UK": Market("UK", "GB", "GBP", "Europe/London", "en-GB", "£"),
    "OTHER": Market("OTHER", "", "", "UTC", "en", ""),
}


def market_for(profile: "ClientProfile") -> Market:
    j = (profile.jurisdiction or "").strip().upper()
    if j in _CROWN or uk.postcode_area(profile.address.postal_code) in uk.CROWN_DEPENDENCY_AREAS and j in _UK:
        return MARKETS["OTHER"]
    return MARKETS[market_code(profile.jurisdiction)]


def out_of_scope_note(profile: "ClientProfile") -> str:
    j = (profile.jurisdiction or "").strip().upper()
    if j in _CROWN or (j in _UK and uk.postcode_area(profile.address.postal_code) in uk.CROWN_DEPENDENCY_AREAS):
        return ("Jersey, Guernsey and the Isle of Man are Crown Dependencies, not part of the UK: UK law, regulators and "
                "directories in this tool may not apply. Checks run in generic mode only.")
    if market_code(profile.jurisdiction) == "OTHER":
        return (f"Jurisdiction '{profile.jurisdiction}' has no compliance pack: only generic technical checks apply. "
                "Review, advertising and privacy law must be checked locally.")
    return ""


# ---- API location -----------------------------------------------------------------------------------------------
def location_for(profile: "ClientProfile") -> dict:
    """Approximate user location in the shape every provider adapter needs.

    UK: country 'GB', timezone Europe/London, region = county/council area/nation (free text, loosely matched by
    providers), coordinates from client.toml, a known-city preset, or None (resolve via postcodes.io).
    """
    m = market_for(profile)
    a = profile.address
    city = profile.city
    region = a.region
    lat, lng = profile.latitude, profile.longitude
    if m.is_uk:
        preset = uk.lookup_city(city)
        if preset:
            region = a.council_area or (preset["region"] if not a.region or a.region.lower() in {"england", "scotland", "wales"} else a.region)
            lat = lat if lat is not None else preset["lat"]
            lng = lng if lng is not None else preset["lng"]
        else:
            region = a.council_area or a.county or a.region
    return {"country": m.country_iso or a.country, "city": city, "region": region, "timezone": m.timezone,
            "latitude": lat, "longitude": lng, "language": m.language}


# ---- prompts ---------------------------------------------------------------------------------------------------
US_TEMPLATES = [
    "best {term} in {city}",
    "who is the best {term} near {city}? give me 3 recommendations",
    "I need a {term} in {city}. who should I call?",
]
UK_TEMPLATES = [
    # The term is quoted so any search phrase ("plumber", "Sunday roast", "NHS dentist taking new patients") reads naturally.
    "I live in {city}{area}. Recommend three reputable options for '{term}' nearby, saying why you picked each and naming your sources.",
    "I urgently need help with '{term}' in {city}. Who would you ring, and roughly how much will it cost?",
    "Compare the best-reviewed options for '{term}' in {city}. Are any of them accredited with {body}? Give links.",
    "{term} {district}",
]


def uk_area_clause(profile: "ClientProfile") -> str:
    a = profile.address
    if profile.nation == "ENG" and a.county:
        return f", {a.county}"
    if a.council_area:
        return f", {a.council_area}"
    return ""


def uk_accreditation_phrase(vertical: str) -> str:
    return {"dentist": "the GDC and CQC (or the local regulator)", "lawyer": "the relevant law society or regulator",
            "plumber": "Gas Safe, TrustMark or a trade body", "heating_engineer": "Gas Safe or a trade body",
            "electrician": "NICEIC, NAPIT or SELECT", "restaurant": "a food hygiene rating",
            "salon": "a recognised trade body"}.get(vertical, "a relevant trade body")


_LEAK_US_PATTERNS = [re.compile(r"\b[A-Z]{2}\s\d{5}(?:-\d{4})?\b"), re.compile(r"\$\s?\d"), re.compile(r"\b(?:ZIP|zip code)\b", re.I)]


def localisation_leak(text: str, market: Market) -> bool:
    """True when a UK probe answer shows US context (dollar prices, ZIP/state codes): a localisation failure."""
    if not market.is_uk:
        return False
    return any(p.search(text or "") for p in _LEAK_US_PATTERNS)
