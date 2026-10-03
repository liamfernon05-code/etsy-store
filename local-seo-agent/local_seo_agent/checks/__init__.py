from __future__ import annotations

from ..models import ClientProfile, CrawlResult, Finding
from .crawlability import check_crawlability
from .nap import check_gbp, check_nap
from .schema import check_schema
from .technical import check_technical


def run_all(profile: ClientProfile, crawl: CrawlResult, extra: list[Finding] | None = None) -> list[Finding]:
    findings = [
        *check_crawlability(crawl),
        *check_technical(profile, crawl),
        *check_schema(profile, crawl),
        *check_nap(profile, crawl),
        *check_gbp(profile),
        *(extra or []),
    ]
    order = {"ERROR": 0, "WARN": 1, "UNKNOWN": 2, "INFO": 3}
    return sorted(findings, key=lambda f: (order[f.severity.value], -f.impact, f.id))
