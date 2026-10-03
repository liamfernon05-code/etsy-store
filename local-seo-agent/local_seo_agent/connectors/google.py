"""Search Console, GA4 and Business Profile connectors (read-only). Auth: GOOGLE_ACCESS_TOKEN env var."""

from __future__ import annotations

import re
from datetime import date, timedelta
from urllib.parse import quote

from ..facts import VERIFIED
from ..models import Confidence, Finding, GBPInputs, Severity
from . import ApiClient, ConnectorError, google_headers

GSC_BASE = "https://searchconsole.googleapis.com/webmasters/v3"
GA4_BASE = "https://analyticsdata.googleapis.com/v1beta"
GBP_ACCOUNTS = "https://mybusinessaccountmanagement.googleapis.com/v1/accounts"
GBP_INFO = "https://mybusinessbusinessinformation.googleapis.com/v1"
GBP_PERF = "https://businessprofileperformance.googleapis.com/v1"
GBP_V4 = "https://mybusiness.googleapis.com/v4"
SCOPES = {
    "gsc": "https://www.googleapis.com/auth/webmasters.readonly",
    "ga4": "https://www.googleapis.com/auth/analytics.readonly",
    "gbp": "https://www.googleapis.com/auth/business.manage",
}
AI_SOURCE_REGEX = r"chatgpt\.com|chat\.openai\.com|perplexity|gemini\.google\.com|claude\.ai|copilot\.microsoft\.com|bard\.google\.com|you\.com|deepseek"
PERF_METRICS = ["BUSINESS_IMPRESSIONS_DESKTOP_MAPS", "BUSINESS_IMPRESSIONS_DESKTOP_SEARCH", "BUSINESS_IMPRESSIONS_MOBILE_MAPS",
                "BUSINESS_IMPRESSIONS_MOBILE_SEARCH", "CALL_CLICKS", "WEBSITE_CLICKS", "BUSINESS_DIRECTION_REQUESTS",
                "BUSINESS_BOOKINGS", "BUSINESS_CONVERSATIONS"]
STAR = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}


# ------------------------------------------------------------ Search Console
def gsc_query(api: ApiClient, site: str, start: str, end: str, dimensions: list[str] | None = None, row_limit: int = 1000,
              data_state: str = "FINAL") -> dict:
    """Search Analytics. `site` is 'sc-domain:example.com' or a URL-prefix property (fully percent-encoded in the path).
    NB: there is no API for the Search Console Generative AI report (UI/CSV only)."""
    body = {"startDate": start, "endDate": end, "dimensions": dimensions or ["QUERY"], "type": "WEB",
            "dataState": data_state, "rowLimit": min(row_limit, 25000), "startRow": 0}
    url = f"{GSC_BASE}/sites/{quote(site, safe='')}/searchAnalytics/query"
    try:
        return api.request("POST", url, headers=google_headers(), json=body)
    except ConnectorError as e:
        if e.status != 400 or "type" not in str(e).lower():
            raise
        body["searchType"] = body.pop("type")  # discovery lists both `type` and `searchType` (same enum): fall back
        return api.request("POST", url, headers=google_headers(), json=body)


def gsc_summary(resp: dict, city: str = "") -> dict:
    rows = resp.get("rows") or []
    clicks = sum(r.get("clicks", 0) for r in rows)
    imps = sum(r.get("impressions", 0) for r in rows)
    top = sorted(rows, key=lambda r: -r.get("impressions", 0))[:10]
    local = [r for r in rows if city and city.lower() in " ".join(r.get("keys", [])).lower()]
    return {
        "clicks": round(clicks), "impressions": round(imps), "ctr": round(clicks / imps, 4) if imps else 0.0,
        "top_queries": [{"keys": r["keys"], "clicks": r.get("clicks", 0), "impressions": r.get("impressions", 0),
                         "position": round(r.get("position", 0), 1)} for r in top],
        "queries_with_city": len(local),
        "note": "Final data lags ~2-3 days. Generative AI impressions are inside Web totals and cannot be separated via the API.",
    }


# ------------------------------------------------------------ GA4
def ga4_ai_traffic(api: ApiClient, property_id: str, days: int = 28) -> dict:
    """Sessions from AI assistants: source regex PLUS the native 'AI Assistant' default channel group (GA4, from 2026-05-13).
    Google has not published which assistants the channel covers (sources disagree), so we never rely on its membership;
    the regex catches the rest. Rows are unique per (source, channel), so nothing is double counted. Many AI visits arrive
    as (direct): treat the result as a lower bound."""
    pid = re.sub(r"\D", "", property_id)
    if not pid:
        raise ValueError("GA4 property id must be the numeric id (not the G- measurement id)")
    body = {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "yesterday"}],
        "dimensions": [{"name": "sessionSource"}, {"name": "sessionDefaultChannelGroup"}],
        "metrics": [{"name": "sessions"}, {"name": "engagedSessions"}, {"name": "keyEvents"}],
        "dimensionFilter": {"orFilter": {"expressions": [
            {"filter": {"fieldName": "sessionSource", "stringFilter": {"matchType": "PARTIAL_REGEXP", "caseSensitive": False, "value": AI_SOURCE_REGEX}}},
            {"filter": {"fieldName": "sessionDefaultChannelGroup", "stringFilter": {"matchType": "EXACT", "value": "AI Assistant"}}},
        ]}},
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": "1000", "returnPropertyQuota": True,
    }
    resp = api.request("POST", f"{GA4_BASE}/properties/{pid}:runReport", headers=google_headers(), json=body)
    heads = [h["name"] for h in resp.get("dimensionHeaders", [])] + [h["name"] for h in resp.get("metricHeaders", [])]
    rows = []
    for r in resp.get("rows") or []:
        vals = [v.get("value", "") for v in r.get("dimensionValues", [])] + [v.get("value", "0") for v in r.get("metricValues", [])]
        rows.append(dict(zip(heads, vals)))
    total = sum(int(r.get("sessions", 0)) for r in rows)
    keyev = sum(int(float(r.get("keyEvents", 0))) for r in rows)
    return {"days": days, "ai_sessions": total, "ai_key_events": keyev, "by_source": rows[:20],
            "note": "Lower bound: AI app clicks often arrive without a referrer and land in (direct)."}


# ------------------------------------------------------------ Business Profile
class GBPNotApproved(ConnectorError):
    pass


def _gbp(api: ApiClient, method: str, url: str, **kw) -> dict:
    try:
        return api.request(method, url, headers=google_headers(), **kw)
    except ConnectorError as e:
        if e.status == 429:  # new Cloud projects have quota 0 until Google approves access (also plain throttling)
            raise GBPNotApproved(429, "Business Profile API quota exceeded or access not yet approved for this Cloud project "
                                 "(new projects start at quota 0). Submit Google's GBP API access request; it needs a verified "
                                 "listing 60+ days old with a website. Use the Places API as the no-approval fallback.", "not_approved") from e
        raise


def gbp_accounts(api: ApiClient) -> list[dict]:
    return _gbp(api, "GET", GBP_ACCOUNTS).get("accounts", [])


def gbp_locations(api: ApiClient, account: str, page_size: int = 100) -> list[dict]:
    acc = account if account.startswith("accounts/") else f"accounts/{account}"
    mask = "name,title,storeCode,websiteUri,phoneNumbers,categories,storefrontAddress,regularHours,profile,serviceArea,metadata"
    return _gbp(api, "GET", f"{GBP_INFO}/{acc}/locations", params={"readMask": mask, "pageSize": page_size}).get("locations", [])


def gbp_performance(api: ApiClient, location_id: str, start: date, end: date) -> dict:
    loc = re.sub(r"^locations/", "", location_id)
    params: list[tuple[str, str]] = [("dailyMetrics", m) for m in PERF_METRICS] + [
        ("dailyRange.startDate.year", str(start.year)), ("dailyRange.startDate.month", str(start.month)),
        ("dailyRange.startDate.day", str(start.day)), ("dailyRange.endDate.year", str(end.year)),
        ("dailyRange.endDate.month", str(end.month)), ("dailyRange.endDate.day", str(end.day))]
    resp = _gbp(api, "GET", f"{GBP_PERF}/locations/{loc}:fetchMultiDailyMetricsTimeSeries", params=params)
    totals: dict[str, int] = {}
    for multi in resp.get("multiDailyMetricTimeSeries", []):
        for ts in multi.get("dailyMetricTimeSeries", []):
            m = ts.get("dailyMetric", "")
            totals[m] = totals.get(m, 0) + sum(int(v.get("value", 0) or 0) for v in (ts.get("timeSeries", {}).get("datedValues") or []))
    imps = sum(v for k, v in totals.items() if k.startswith("BUSINESS_IMPRESSIONS"))
    return {"impressions": imps, "search_vs_maps": {k: v for k, v in totals.items() if k.startswith("BUSINESS_IMPRESSIONS")},
            "calls": totals.get("CALL_CLICKS", 0), "website_clicks": totals.get("WEBSITE_CLICKS", 0),
            "direction_requests": totals.get("BUSINESS_DIRECTION_REQUESTS", 0), "bookings": totals.get("BUSINESS_BOOKINGS", 0),
            "conversations": totals.get("BUSINESS_CONVERSATIONS", 0)}


def gbp_reviews(api: ApiClient, account: str, location_id: str, page_size: int = 50) -> dict:
    """v4 reviews (still live in 2026, no discovery doc). starRating is an ENUM STRING. Reviewer text is untrusted."""
    acc = account.removeprefix("accounts/")
    loc = location_id.removeprefix("locations/")
    resp = _gbp(api, "GET", f"{GBP_V4}/accounts/{acc}/locations/{loc}/reviews",
                params={"pageSize": min(page_size, 50), "orderBy": "updateTime desc"})
    reviews = resp.get("reviews", [])
    replied = sum(1 for r in reviews if r.get("reviewReply"))
    return {"average_rating": resp.get("averageRating"), "total": resp.get("totalReviewCount"),
            "sampled": len(reviews), "reply_rate": round(replied / len(reviews), 2) if reviews else None,
            "stars": [STAR.get(str(r.get("starRating", "")), 0) for r in reviews],
            "latest": [r.get("updateTime") or r.get("createTime") for r in reviews[:5]]}


def gbp_inputs_from_location(loc: dict, rating: float | None = None, review_count: int | None = None) -> GBPInputs:
    """Map a Business Information location to the manual GBPInputs the checks use (so the audit needs no hand-typing)."""
    cats = loc.get("categories") or {}
    md = loc.get("metadata") or {}
    return GBPInputs(
        primary_category=(cats.get("primaryCategory") or {}).get("displayName", ""),
        additional_categories=[c.get("displayName", "") for c in cats.get("additionalCategories", [])],
        rating=rating, review_count=review_count, verified=md.get("hasVoiceOfMerchant"),
        hours_set=bool((loc.get("regularHours") or {}).get("periods")),
        description_set=bool((loc.get("profile") or {}).get("description")),
        services_listed=bool(loc.get("serviceItems")) if "serviceItems" in loc else None,
    )


def connector_finding(id_: str, title: str, err: Exception) -> Finding:
    sev = Severity.UNKNOWN
    kind = getattr(err, "kind", "error")
    return Finding(id=f"conn.{id_}", category="connector", severity=sev, title=title, verified_on=VERIFIED, impact=2, effort=1,
                   confidence=Confidence.OFFICIAL, detail=f"{kind}: {str(err)[:200]}")
