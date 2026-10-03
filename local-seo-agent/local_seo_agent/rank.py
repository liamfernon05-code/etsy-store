"""Local rank tracking via geo-grid: where does the client appear in Google Maps results from points around the business?

Local-pack position depends on the searcher's location, so a single rank from the business address is misleading. We
sample a grid of points and aggregate. Data comes ONLY from a licensed SERP/Places API (adapter below); scraping Google
Maps directly violates Google's terms and is not supported.

Metrics (standard in local-SEO tooling):
  ARP   average rank position across grid points (missing = MISSING_RANK)
  SoLV  share of local voice: % of grid points where the client is in the top 3
  coverage  % of grid points where the client appears at all (top 20)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

MISSING_RANK = 21
KM_PER_DEG_LAT = 110.574
KM_PER_DEG_LNG_EQ = 111.320


@dataclass(frozen=True)
class GridPoint:
    row: int
    col: int
    lat: float
    lng: float


def grid_points(lat: float, lng: float, size: int = 3, spacing_km: float = 2.0) -> list[GridPoint]:
    """size x size grid centred on (lat, lng); odd sizes keep a point on the business itself."""
    if size < 1 or size > 9:
        raise ValueError("grid size must be 1..9")
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise ValueError("invalid coordinates")
    half = (size - 1) / 2
    pts = []
    for r in range(size):
        for c in range(size):
            dlat = (half - r) * spacing_km / KM_PER_DEG_LAT
            dlng = (c - half) * spacing_km / (KM_PER_DEG_LNG_EQ * max(math.cos(math.radians(lat)), 0.01))
            pts.append(GridPoint(r, c, round(lat + dlat, 6), round(lng + dlng, 6)))
    return pts


def find_rank(results: list[dict], client_hosts: set[str], client_phone_digits: str = "", client_place_id: str = "") -> int | None:
    """1-based rank of the client in an ordered list of Maps results, matched by place id, website host or phone."""
    for i, item in enumerate(results, start=1):
        pid = str(item.get("place_id") or "")
        dom = (item.get("domain") or "").lower().removeprefix("www.")
        phone = "".join(ch for ch in str(item.get("phone") or "") if ch.isdigit())[-10:]
        if (client_place_id and pid == client_place_id) or (dom and dom in client_hosts) or \
           (client_phone_digits and phone and phone == client_phone_digits[-10:]):
            return i
    return None


def aggregate(ranks: list[int | None]) -> dict:
    n = len(ranks)
    if n == 0:
        return {"points": 0, "arp": None, "solv": None, "coverage": None}
    eff = [r if r is not None else MISSING_RANK for r in ranks]
    return {
        "points": n,
        "arp": round(sum(eff) / n, 2),
        "solv": round(100 * sum(1 for r in ranks if r is not None and r <= 3) / n, 1),
        "coverage": round(100 * sum(1 for r in ranks if r is not None) / n, 1),
    }
