"""Google Places API (New): competitor snapshots, client rating/count without GBP approval, review-velocity history.

Contract (verified from Google's discovery document): POST places:searchText with X-Goog-Api-Key and a REQUIRED
X-Goog-FieldMask (fields prefixed 'places.'); locationBias.circle radius 0-50000 m (locationRestriction is rectangle
only); pageSize max 20; includePureServiceAreaBusinesses must be true for plumbers etc.; reviews are capped at 5 and
live in a pricier SKU, so competitor scans never request them. Billing is by the highest-tier field in the mask
(rating/userRatingCount/websiteUri/phone/hours = Enterprise ~USD 35 per 1,000: LIKELY, re-check Google's price list).
Never send field mask '*'. Place IDs may be stored; most other Places content has retention limits: this tool keeps only
aggregate competitor metrics, never reviewer names or review text.
"""

from __future__ import annotations

import json
import os
import re
import statistics
from dataclasses import dataclass

from ..checks.schema import digits
from ..facts import VERIFIED
from ..markets import location_for, market_for
from ..models import ClientProfile, Confidence, Finding, Severity
from ..snapshots import Snapshots
from . import ApiClient, ConnectorError

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
DETAILS_URL = "https://places.googleapis.com/v1/places/"
SEARCH_MASK = ",".join(f"places.{f}" for f in ("id", "displayName", "rating", "userRatingCount", "primaryType", "types",
                                               "websiteUri", "nationalPhoneNumber", "regularOpeningHours", "location"))
DETAILS_MASK = "id,displayName,rating,userRatingCount,primaryType,types,websiteUri,nationalPhoneNumber,regularOpeningHours,location,businessStatus"
COST_PER_SEARCH_ENTERPRISE = 0.035  # LIKELY (USD 35 per 1,000): estimate only; read your billing console


class PlacesBudgetExceeded(RuntimeError):
    pass


@dataclass
class PlacesClient:
    api: ApiClient
    api_key: str
    budget_usd: float = 2.0
    spent: float = 0.0

    @classmethod
    def from_env(cls, api: ApiClient | None = None, budget_usd: float = 2.0) -> "PlacesClient":
        key = os.environ.get("GOOGLE_PLACES_API_KEY")
        if not key:
            raise ConnectorError(401, "Set GOOGLE_PLACES_API_KEY (enable 'Places API (New)', a different API from legacy Places)", "auth")
        return cls(api or ApiClient(), key, budget_usd)

    def _spend(self, c: float) -> None:
        if self.spent + c > self.budget_usd:
            raise PlacesBudgetExceeded(f"Places budget ${self.budget_usd:.2f} reached (spent ${self.spent:.2f})")
        self.spent += c

    def _headers(self, mask: str) -> dict:
        return {"X-Goog-Api-Key": self.api_key, "X-Goog-FieldMask": mask, "Content-Type": "application/json"}

    def search_text(self, query: str, lat: float | None, lng: float | None, radius_m: float = 8000.0, country: str = "GB",
                    language: str = "en-GB", page_size: int = 20, include_sab: bool = True) -> list[dict]:
        body: dict = {"textQuery": query, "languageCode": language, "regionCode": country, "pageSize": min(page_size, 20),
                      "includePureServiceAreaBusinesses": include_sab}
        if lat is not None and lng is not None:
            body["locationBias"] = {"circle": {"center": {"latitude": lat, "longitude": lng}, "radius": min(radius_m, 50000.0)}}
        self._spend(COST_PER_SEARCH_ENTERPRISE)
        return self.api.request("POST", SEARCH_URL, headers=self._headers(SEARCH_MASK), json=body).get("places", [])  # {} when empty

    def details(self, place_id: str, country: str = "GB", language: str = "en-GB") -> dict:
        pid = re.sub(r"^places/", "", place_id)
        if not re.fullmatch(r"[A-Za-z0-9_-]{10,200}", pid):
            raise ValueError("invalid place id")
        self._spend(0.020)
        return self.api.request("GET", DETAILS_URL + pid, headers=self._headers(DETAILS_MASK),
                                params={"languageCode": language, "regionCode": country})


def _host(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", (url or "").lower()).split("/")[0]


def is_client(place: dict, profile: ClientProfile, client_place_id: str = "") -> bool:
    if client_place_id and place.get("id") == client_place_id:
        return True
    if _host(place.get("websiteUri", "")) and _host(place.get("websiteUri", "")) == _host(profile.website):
        return True
    ph = digits(place.get("nationalPhoneNumber", ""))
    return bool(ph) and ph == digits(profile.phone)


def snapshot_competitors(client: PlacesClient, profile: ClientProfile, snaps: Snapshots, queries: list[str] | None = None,
                         client_place_id: str = "", radius_m: float = 8000.0) -> dict:
    """Run each query around the client's location; store rank, rating, review count and types for every place returned."""
    L = location_for(profile)
    market = market_for(profile)
    queries = queries or [f"{t} in {profile.city}" for t in (profile.target_services or [])][:6]
    if not queries:
        raise ValueError("No queries: set target_services or pass queries")
    seen = found_client = 0
    for q in queries:
        places = client.search_text(q, L["latitude"], L["longitude"], radius_m, market.country_iso or "US",
                                    "en-GB" if market.is_uk else "en-US", include_sab=True)
        for rank, p in enumerate(places, start=1):
            c = is_client(p, profile, client_place_id)
            found_client += c
            snaps.add_place(query=q, rank=rank, place_id=p.get("id", ""), name=(p.get("displayName") or {}).get("text", "")[:120],
                            rating=p.get("rating"), review_count=p.get("userRatingCount"), primary_type=p.get("primaryType", ""),
                            types=json.dumps(p.get("types", [])), website=p.get("websiteUri", ""),
                            phone=p.get("nationalPhoneNumber", ""), is_client=int(c))
            seen += 1
    return {"queries": len(queries), "places_seen": seen, "client_rows": found_client, "spent_usd": round(client.spent, 3)}


def velocity(snaps: Snapshots, place_id: str) -> float | None:
    """New reviews per 30 days from the first and last snapshot (needs >=2 snapshots >=1 day apart)."""
    h = [r for r in snaps.history(place_id) if r["review_count"] is not None]
    if len(h) < 2 or h[-1]["ts"] - h[0]["ts"] < 86400:
        return None
    return round((h[-1]["review_count"] - h[0]["review_count"]) / ((h[-1]["ts"] - h[0]["ts"]) / 86400) * 30, 1)


def competitor_findings(profile: ClientProfile, snaps: Snapshots) -> list[Finding]:
    rows = snaps.latest_per_place()
    me = [r for r in rows if r["is_client"]]
    others = [r for r in rows if not r["is_client"] and r["review_count"] is not None]
    out: list[Finding] = []

    def mk(id_, sev, title, **kw):
        out.append(Finding(id=f"places.{id_}", category="competitors", severity=sev, title=title, verified_on=VERIFIED,
                           confidence=kw.pop("confidence", Confidence.EVIDENCE), **kw))

    if not others:
        mk("no-data", Severity.UNKNOWN, "No competitor snapshot yet", impact=2, effort=1,
           detail="Run `places-snapshot` (needs GOOGLE_PLACES_API_KEY).")
        return out
    top = sorted(others, key=lambda r: (r["rank"] or 99))[:10]
    med = statistics.median(r["review_count"] for r in top)
    if not me:
        mk("client-not-found", Severity.WARN, "Client not found in the Maps results for the target queries",
           detail="Either the match failed (check website/phone) or the business does not appear for these queries in this area.",
           impact=5, effort=3)
    else:
        mine = me[0]
        if mine["review_count"] is not None and mine["review_count"] < med:
            mk("review-gap", Severity.WARN, "Fewer reviews than the median of the top competitors",
               evidence=f"{mine['review_count']} vs median {med:g} (top {len(top)})", impact=4, effort=3,
               fix="Close the gap with a compliant ask-everyone process (no gating, no incentives).")
        ratings = [r["rating"] for r in top if r["rating"]]
        if mine["rating"] and ratings and mine["rating"] < statistics.median(ratings) - 0.2:
            mk("rating-gap", Severity.INFO, "Rating below the competitor median",
               evidence=f"{mine['rating']} vs {statistics.median(ratings):.1f}", impact=2, effort=3, confidence=Confidence.HEURISTIC)
        v = velocity(snaps, mine["place_id"])
        vc = [x for x in (velocity(snaps, r["place_id"]) for r in top[:5]) if x is not None]
        if v is not None and vc and v < statistics.median(vc):
            mk("velocity-gap", Severity.INFO, "New-review velocity below top competitors",
               evidence=f"{v}/30d vs median {statistics.median(vc)}/30d", impact=3, effort=3, confidence=Confidence.HEURISTIC)
    # category comparison: what do the top 3 use as primary type that we don't?
    top3 = [r["primary_type"] for r in sorted(others, key=lambda r: (r["rank"] or 99))[:3] if r["primary_type"]]
    if me and top3 and me[0]["primary_type"] and me[0]["primary_type"] not in top3:
        mk("category-differs", Severity.INFO, "Client's primary type differs from the top competitors'",
           evidence=f"client {me[0]['primary_type']} vs {', '.join(dict.fromkeys(top3))}", impact=3, effort=1,
           detail="Primary category is a top local-pack factor in expert surveys; confirm yours is the most specific accurate one.")
    return out
