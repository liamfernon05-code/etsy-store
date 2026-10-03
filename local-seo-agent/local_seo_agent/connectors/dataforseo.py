"""DataForSEO adapters: geo-grid Maps rank tracking and Google AI Overview capture (licensed SERP data, not scraping by us).

Honest caveats: DataForSEO itself collects SERPs for a fee; if your policy forbids third-party SERP collection, don't
use these adapters. Maps live advanced: POST /v3/serp/google/maps/live/advanced, body is a JSON ARRAY of task objects,
location_coordinate = "lat,lng,zoom z" (zoom 3z..21z, default 17z), items[type='maps_search'] carry rank_group,
rating.value/votes_count, place_id, domain, phone. Always check BOTH the envelope status_code and tasks[0].status_code
(20000 = OK): HTTP 200 can carry a task-level error. Live price ~USD 0.002 per SERP (LIKELY): read the response `cost`.
AI Overview: organic live advanced with load_async_ai_overview=true (extra ~USD 0.002, refunded when there is no AIO);
the ai_overview element has markdown, items[] and references[] (domain/url/title). Vendor-collected: treat as a small
directional sample, not a population measure.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

from .. import rank
from ..markets import location_for, market_for
from ..models import ClientProfile
from ..probe.entities import match_client
from ..probe.store import Store
from ..snapshots import Snapshots
from . import ApiClient, ConnectorError

BASE = "https://api.dataforseo.com/v3"
MAPS_PATH = "/serp/google/maps/live/advanced"
ORGANIC_PATH = "/serp/google/organic/live/advanced"


class SerpBudgetExceeded(RuntimeError):
    pass


@dataclass
class DataForSEO:
    api: ApiClient
    login: str
    password: str
    budget_usd: float = 1.0
    spent: float = 0.0

    @classmethod
    def from_env(cls, api: ApiClient | None = None, budget_usd: float = 1.0) -> "DataForSEO":
        login, pw = os.environ.get("DATAFORSEO_LOGIN"), os.environ.get("DATAFORSEO_PASSWORD")
        if not login or not pw:
            raise ConnectorError(401, "Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD (API credentials, not the account login)", "auth")
        return cls(api or ApiClient(), login, pw, budget_usd)

    def _post(self, path: str, task: dict, est_cost: float) -> dict:
        if self.spent + est_cost > self.budget_usd:
            raise SerpBudgetExceeded(f"SERP budget ${self.budget_usd:.2f} reached (spent ${self.spent:.3f})")
        resp = self.api.request("POST", BASE + path, json=[task], auth=(self.login, self.password))
        self.spent += float(resp.get("cost") or est_cost)
        task0 = (resp.get("tasks") or [{}])[0]
        if resp.get("status_code") != 20000 or task0.get("status_code") != 20000:
            raise ConnectorError(200, f"DataForSEO task error {task0.get('status_code')}: {str(task0.get('status_message'))[:120]}")
        return (task0.get("result") or [{}])[0]

    def maps_search(self, keyword: str, lat: float, lng: float, zoom: int = 14, language: str = "en", se_domain: str = "",
                    depth: int = 20) -> list[dict]:
        task = {"keyword": keyword, "location_coordinate": f"{lat:.7f},{lng:.7f},{int(zoom)}z", "language_code": language,
                "device": "desktop", "depth": min(depth, 100), "search_this_area": True}
        if se_domain:
            task["se_domain"] = se_domain
        result = self._post(MAPS_PATH, task, 0.002)
        return [i for i in (result.get("items") or []) if i.get("type") == "maps_search"]

    def organic_with_aio(self, keyword: str, location_name: str, language: str = "en", device: str = "mobile") -> dict:
        task = {"keyword": keyword, "location_name": location_name, "language_code": language, "device": device,
                "depth": 10, "load_async_ai_overview": True}
        return self._post(ORGANIC_PATH, task, 0.004)


def run_geogrid(dfs: DataForSEO, profile: ClientProfile, snaps: Snapshots, keyword: str, wave: str, size: int = 3,
                spacing_km: float = 2.0, client_place_id: str = "") -> dict:
    """Rank of the client at each point of a size x size grid around the business, aggregated to ARP / SoLV / coverage."""
    L = location_for(profile)
    if L["latitude"] is None or L["longitude"] is None:
        raise ValueError("No coordinates: set latitude/longitude in client.toml or run `resolve` (UK)")
    market = market_for(profile)
    hosts = {re.sub(r"^www\.", "", (re.sub(r"^https?://", "", profile.website).split("/")[0]).lower())}
    before = dfs.spent
    points, ranks = [], []
    for pt in rank.grid_points(L["latitude"], L["longitude"], size, spacing_km):
        items = dfs.maps_search(keyword, pt.lat, pt.lng, 14, "en", "google.co.uk" if market.is_uk else "")
        r = rank.find_rank(items, hosts, "".join(ch for ch in profile.phone if ch.isdigit()), client_place_id)
        ranks.append(r)
        points.append({"row": pt.row, "col": pt.col, "lat": pt.lat, "lng": pt.lng, "rank": r})
    agg = rank.aggregate(ranks)
    snaps.add_grid(wave, keyword, "dataforseo", size, spacing_km, points, agg, dfs.spent - before)
    return {**agg, "keyword": keyword, "cost_usd": round(dfs.spent - before, 4), "points": points}


def capture_aio(dfs: DataForSEO, profile: ClientProfile, store: Store, keyword: str, wave: str, location_name: str) -> dict:
    """Record whether an AI Overview appeared for the keyword, whether it names the client, and whether it cites the
    client's domain. Stored as provider 'serp:google_ai_overview' (vendor-collected sample, calibration-grade)."""
    result = dfs.organic_with_aio(keyword, location_name)
    aio = next((i for i in (result.get("items") or []) if i.get("type") == "ai_overview"), None)
    location = f"{profile.city} ({location_name})"
    if not aio:
        store.add(wave=wave, provider="serp:google_ai_overview", model="dataforseo", prompt_id=keyword[:40], prompt_kind="nonbranded",
                  prompt_text=keyword, location=location, ok=1, method="no-aio", response_text="")
        return {"aio_present": False}
    refs = list(aio.get("references") or [])
    for sub in aio.get("items") or []:
        refs += sub.get("references") or []
    urls = [r.get("url") or (f"https://{r['domain']}/" if r.get("domain") else "") for r in refs]
    text = aio.get("markdown") or ""
    m = match_client(text, [u for u in urls if u], profile)
    store.add(wave=wave, provider="serp:google_ai_overview", model="dataforseo", prompt_id=keyword[:40], prompt_kind="nonbranded",
              prompt_text=keyword, location=location, ok=1, verified=int(m["verified"]), name_match=int(m["name_match"]),
              cited=int(m["cited"]), method=m["method"], cited_urls=json.dumps([u for u in urls if u]), response_text=text[:6000])
    return {"aio_present": True, "client_named": m["name_match"], "client_cited": m["cited"], "references": len(refs)}
