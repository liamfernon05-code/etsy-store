"""Keep the research honest: re-verify quoted facts against their primary sources, and watch Google's status dashboard.

`verify_facts()` is meant to be run from a network that can reach the primary sites (the build sandbox could not).
For each fact with a primary URL it records reachability, whether expected phrases are still present, and a content
hash so later runs flag CHANGED pages. It never edits facts: a person decides.

`update_in_progress()` reads the Google Search Status Dashboard and says whether a ranking/spam/core update is rolling
out, so reports can avoid judging ranking changes mid-rollout. Failure to fetch is UNKNOWN, never "no update".
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .safety import BlockedURL, SafeFetcher

# fact id -> (primary url, phrases that must still appear). Phrases only where we are confident of the wording.
PRIMARY_SOURCES: dict[str, tuple[str, list[str]]] = {
    "cwv": ("https://web.dev/articles/vitals", ["2.5 seconds", "200 milliseconds", "0.1"]),
    "self-serving-reviews": ("https://developers.google.com/search/blog/2019/09/making-review-rich-results-more-helpful", ["self-serving"]),
    "googlebot-2mb": ("https://developers.google.com/search/docs/crawling-indexing/googlebot", ["2 MB"]),
    "gbp-api-access": ("https://developers.google.com/my-business/content/limits", []),
    "ftc-fake-reviews": ("https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465", ["fake"]),
    "whitespark": ("https://whitespark.ca/local-search-ranking-factors/", []),
    "update-freeze": ("https://status.search.google.com/", []),
}

STATUS_URLS = ["https://status.search.google.com/incidents.json"]


def _visible_text(html: str) -> str:
    html = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def verify_facts(fetcher: SafeFetcher, previous: dict | None = None, sources: dict | None = None) -> dict:
    previous = previous or {}
    out: dict = {"checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "results": {}}
    for fid, (url, phrases) in (sources or PRIMARY_SOURCES).items():
        entry: dict = {"url": url}
        try:
            res = fetcher.fetch(url)
        except (BlockedURL, Exception) as e:  # noqa: BLE001
            entry.update(status="UNREACHABLE", detail=f"{type(e).__name__}: {str(e)[:120]}")
            out["results"][fid] = entry
            continue
        if res.status != 200:
            entry.update(status="UNREACHABLE", detail=f"HTTP {res.status}")
            out["results"][fid] = entry
            continue
        text = _visible_text(res.text)
        missing = [p for p in phrases if p.lower() not in text.lower()]
        digest = hashlib.sha256(text.encode()).hexdigest()
        prev = (previous.get("results") or {}).get(fid, {}).get("sha256")
        status = "OK"
        if missing:
            status = "PHRASE_MISSING"
        elif prev and prev != digest:
            status = "CHANGED"  # page changed since last run: re-read before trusting the fact
        entry.update(status=status, sha256=digest, missing=missing)
        out["results"][fid] = entry
    return out


def save_verification(result: dict, path: Path) -> None:
    Path(path).write_text(json.dumps(result, indent=1))


def load_verification(path: Path) -> dict:
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else {}


RANKING_PRODUCT_ID = "rGHU1u87FJnkP6W2GwMi"   # 'Ranking' on status.search.google.com (from a search-result title; LIKELY)
_UPDATE_RE = re.compile(r"(core|spam|helpful content|reviews|local)\s+update", re.I)
VOLATILE_DAYS = 14


def _parse_ts(v) -> datetime | None:
    if not v or not isinstance(v, str):
        return None
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def update_in_progress(fetcher: SafeFetcher, urls: list[str] | None = None, now: datetime | None = None) -> dict:
    """{'state': 'ACTIVE' | 'RECENT' | 'NONE' | 'UNKNOWN', 'incidents': [...]}.

    ACTIVE  = a Ranking-product update/spam/core incident with no end time.
    RECENT  = one began or ended within VOLATILE_DAYS (Google says rollouts can take ~2 weeks and end times are posted late).
    UNKNOWN = the dashboard could not be fetched/parsed. FAIL OPEN: never reported as 'no update'.
    The endpoint and schema are inferred (host blocked during research): first run `status` once and check the output.
    """
    now = now or datetime.now(timezone.utc)
    for url in urls or STATUS_URLS:
        try:
            res = fetcher.fetch(url)
            if res.status != 200:
                continue
            data = json.loads(res.text)
        except (BlockedURL, ValueError, Exception):  # noqa: BLE001
            continue
        incidents = data.get("incidents", []) if isinstance(data, dict) else data
        if not isinstance(incidents, list):
            continue
        active, recent = [], []
        for inc in incidents:
            if not isinstance(inc, dict):
                continue
            products = inc.get("affected_products") or []
            ranking = any(isinstance(p, dict) and (p.get("id") == RANKING_PRODUCT_ID or str(p.get("title", "")).lower() == "ranking")
                          for p in products) or str(inc.get("service_name", "")).lower() == "ranking"
            blob = " ".join(str(inc.get(k, "")) for k in ("external_desc", "service_name", "title"))
            mru = inc.get("most_recent_update")
            blob += " " + (str(mru.get("text", "")) if isinstance(mru, dict) else "")
            if not (ranking or _UPDATE_RE.search(blob)) or not _UPDATE_RE.search(blob):
                continue
            begin, end = _parse_ts(inc.get("begin")), _parse_ts(inc.get("end"))
            item = {"begin": inc.get("begin"), "end": inc.get("end"), "desc": str(inc.get("external_desc", ""))[:160]}
            if not inc.get("end"):
                active.append(item)
            elif (begin and (now - begin).days <= VOLATILE_DAYS) or (end and (now - end).days <= VOLATILE_DAYS):
                recent.append(item)
        state = "ACTIVE" if active else "RECENT" if recent else "NONE"
        return {"state": state, "incidents": active + recent, "source": url}
    return {"state": "UNKNOWN", "incidents": [], "source": ""}
