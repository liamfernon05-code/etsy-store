"""PageSpeed Insights API (free, needs a key). Missing field data is UNKNOWN, never a failure."""

from __future__ import annotations

import httpx

from .facts import VERIFIED
from .models import Confidence, Finding, Severity

ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
THRESHOLDS = {  # metric key -> (label, good, unit divisor)
    "LARGEST_CONTENTFUL_PAINT_MS": ("LCP", 2500, "ms"),
    "INTERACTION_TO_NEXT_PAINT": ("INP", 200, "ms"),
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": ("CLS", 10, "x0.01"),  # API reports CLS scaled by 100: 10 == 0.10
}


def fetch_psi(url: str, api_key: str, strategy: str = "mobile", timeout: float = 90.0) -> dict:
    r = httpx.get(ENDPOINT, params={"url": url, "key": api_key, "strategy": strategy, "category": "PERFORMANCE"},
                  timeout=timeout)
    r.raise_for_status()
    return r.json()


def psi_findings(data: dict) -> list[Finding]:
    out: list[Finding] = []
    metrics = (data.get("loadingExperience") or {}).get("metrics") or {}

    def mk(id_, sev, title, **kw):
        out.append(Finding(id=f"psi.{id_}", category="performance", severity=sev, title=title, verified_on=VERIFIED,
                           source_url="https://web.dev/articles/vitals", **kw))

    if not metrics:
        mk("no-field-data", Severity.UNKNOWN, "No Core Web Vitals field data for this URL (too little traffic)",
           impact=2, effort=1, confidence=Confidence.OFFICIAL)
    for key, (label, good, _) in THRESHOLDS.items():
        m = metrics.get(key)
        if not m or "percentile" not in m:
            continue
        p = m["percentile"]
        shown = f"{p / 100:.2f}" if key.startswith("CUMULATIVE") else f"{p}ms"
        limit = f"{good / 100:.2f}" if key.startswith("CUMULATIVE") else f"{good}ms"
        if p > good:
            mk(label.lower(), Severity.WARN, f"{label} is above the 'good' threshold (75th percentile)",
               evidence=f"{shown} vs {limit}", impact=3, effort=3, confidence=Confidence.OFFICIAL,
               fix=f"Improve {label}: compress/resize hero images, defer third-party scripts, reserve layout space.")
    score = (((data.get("lighthouseResult") or {}).get("categories") or {}).get("performance") or {}).get("score")
    if score is not None:
        mk("lab-score", Severity.INFO, "Lighthouse lab performance score (single synthetic run)",
           evidence=f"{round(score * 100)}/100", impact=1, effort=1, confidence=Confidence.HEURISTIC)
    return out
