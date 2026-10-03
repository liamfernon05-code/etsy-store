"""Deterministic on-page / technical checks. Numeric tripwires are heuristics and labelled as such."""

from __future__ import annotations

import re
from collections import Counter
from urllib.parse import urlsplit

from ..facts import VERIFIED
from ..models import ClientProfile, Confidence, CrawlResult, Finding, Severity

CWV_DOC = "https://web.dev/articles/vitals"


GENERIC_TITLES = {"home", "homepage", "home page", "welcome", "untitled", "index", "main", "new page"}
_STOP = {"the", "and", "for", "near", "best", "in", "of", "a", "an"}


def _service_words(term: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", term.lower()) if w not in _STOP and len(w) > 2]


def _mk(id_, sev, title, **kw) -> Finding:
    kw.setdefault("confidence", Confidence.OFFICIAL)
    return Finding(id=id_, category="technical", severity=sev, title=title, verified_on=VERIFIED, **kw)


def check_technical(profile: ClientProfile, crawl: CrawlResult) -> list[Finding]:
    out: list[Finding] = []
    home = crawl.home
    if home is None or home.status != 200:
        return out
    final = urlsplit(home.final_url or home.url)

    if final.scheme != "https":
        out.append(_mk("tech.https", Severity.ERROR, "Site is not served over HTTPS", impact=4, effort=2,
                       fix="Install a certificate and redirect all HTTP URLs to HTTPS."))
    if len(home.redirect_chain) > 2:
        out.append(_mk("tech.redirect-chain", Severity.WARN, "Homepage goes through a long redirect chain",
                       evidence=" -> ".join(home.redirect_chain[:4]), impact=2, effort=2,
                       fix="Redirect straight to the final canonical URL."))
    if not home.viewport:
        out.append(_mk("tech.viewport", Severity.WARN, "No mobile viewport meta tag", impact=4, effort=1,
                       fix='Add <meta name="viewport" content="width=device-width, initial-scale=1">.'))
    if not home.lang:
        out.append(_mk("tech.lang", Severity.INFO, "No lang attribute on <html>", impact=1, effort=1))

    # titles / descriptions / headings
    if not home.title:
        out.append(_mk("tech.title-missing", Severity.ERROR, "Homepage has no <title>", impact=5, effort=1,
                       fix="Add a unique title with primary service + city."))
    elif home.title.strip().lower() in GENERIC_TITLES or len(home.title.split()) < 2:
        out.append(_mk("tech.title-generic", Severity.WARN, "Homepage title is generic or a single word",
                       evidence=home.title, impact=4, effort=1, confidence=Confidence.EVIDENCE,
                       detail="The title is the strongest on-page signal and the headline in search results.",
                       fix="Use a unique title with the primary service, the place and the brand, e.g. 'Heating engineer in Leeds | Brand'."))
    elif len(home.title) > 70:
        out.append(_mk("tech.title-long", Severity.INFO, "Homepage title is long and may be truncated",
                       evidence=f"{len(home.title)} chars", impact=1, effort=1, confidence=Confidence.HEURISTIC,
                       detail="Truncation depends on pixel width (~580px), not a character count."))
    if not home.meta_description:
        out.append(_mk("tech.meta-desc", Severity.WARN, "Homepage has no meta description", impact=2, effort=1,
                       fix="Write a unique, accurate description with city, services and a call to action."))
    if len(home.h1) == 0:
        out.append(_mk("tech.h1-missing", Severity.WARN, "Homepage has no <h1>", impact=3, effort=1))
    elif len(home.h1) > 1:
        out.append(_mk("tech.h1-multiple", Severity.INFO, "Homepage has multiple <h1> elements",
                       evidence=f"{len(home.h1)} found", impact=1, effort=1, confidence=Confidence.HEURISTIC))

    # local relevance signal: city in title/H1
    city = profile.city.lower()
    if city and city not in (home.title + " " + " ".join(home.h1)).lower():
        out.append(_mk("tech.city-in-title", Severity.WARN, f"'{profile.city}' not in homepage title or H1",
                       detail="Local relevance: make the service area explicit where users and crawlers look first.",
                       impact=4, effort=1, confidence=Confidence.EVIDENCE,
                       fix=f"Work '{profile.city}' and the primary service into the title and H1 naturally."))

    # canonical
    if not home.canonical:
        out.append(_mk("tech.canonical-missing", Severity.WARN, "Homepage has no canonical link", impact=2, effort=1,
                       fix='Add <link rel="canonical"> pointing at the preferred URL.'))
    else:
        c = urlsplit(home.canonical)
        if c.hostname and (c.hostname or "").removeprefix("www.") != (final.hostname or "").removeprefix("www."):
            out.append(_mk("tech.canonical-offsite", Severity.ERROR, "Canonical points to a different domain",
                           evidence=home.canonical[:100], impact=5, effort=1,
                           fix="Point the canonical at this site's own preferred URL."))

    # duplicate titles across crawled pages
    titles = Counter(p.title for p in crawl.pages if p.status == 200 and p.title)
    dups = [t for t, n in titles.items() if n > 1]
    if dups:
        out.append(_mk("tech.duplicate-titles", Severity.WARN, f"{len(dups)} duplicated page title(s)",
                       evidence=dups[0], impact=3, effort=2, confidence=Confidence.OFFICIAL,
                       fix="Give each page a unique title."))

    # broken pages found while crawling
    broken = [p for p in crawl.pages if p.status >= 400]
    if broken:
        out.append(_mk("tech.broken-pages", Severity.WARN, f"{len(broken)} crawled page(s) returned errors",
                       evidence=f"{broken[0].url} -> {broken[0].status}", impact=3, effort=2,
                       fix="Fix or redirect broken internal links."))

    # images
    imgs = sum(p.images for p in crawl.pages)
    noalt = sum(p.images_missing_alt for p in crawl.pages)
    if imgs and noalt / imgs > 0.3:
        out.append(_mk("tech.alt-text", Severity.INFO, "Many images lack alt text",
                       evidence=f"{noalt}/{imgs} images", impact=2, effort=2, confidence=Confidence.HEURISTIC))

    # sitemap
    if not crawl.sitemap_urls:
        out.append(_mk("tech.sitemap-missing", Severity.WARN, "No readable XML sitemap found", impact=3, effort=1,
                       fix="Publish /sitemap.xml and reference it from robots.txt."))
    elif crawl.robots_txt is not None and "sitemap:" not in crawl.robots_txt.lower():
        out.append(_mk("tech.sitemap-not-in-robots", Severity.INFO, "Sitemap is not referenced in robots.txt",
                       impact=1, effort=1))

    # Googlebot 2 MB: informational only (uncompressed bytes per resource; Google called it a clarification)
    big = [p for p in crawl.pages if p.bytes > 1_500_000]
    if big:
        out.append(_mk("tech.html-size", Severity.INFO, "Very large HTML document",
                       evidence=f"{big[0].url}: {big[0].bytes} bytes", impact=1, effort=3,
                       detail="Googlebot reads the first 2 MB of uncompressed HTML; rarely an issue unless inline base64/JSON bloats the page."))

    # thin homepage (heuristic: Google denies word-count thresholds, so INFO only)
    if 0 < home.word_count < 150 and not (home.word_count < 50 and home.scripts >= 3):
        out.append(_mk("content.thin-home", Severity.INFO, "Very little text on the homepage", evidence=f"{home.word_count} words",
                       impact=3, effort=3, confidence=Confidence.HEURISTIC,
                       detail="Not a ranking rule, but a page needs enough substance to answer what the business does, where and for whom.",
                       fix="Say what you do, where you work, who it is for, how to book and why to trust you, using real details."))

    # does any crawled page actually target each service? (skip when the crawl hit its page cap: it may have missed some)
    if profile.target_services and len(crawl.pages) < 25:
        blobs = [(p.title + " " + " ".join(p.h1) + " " + urlsplit(p.final_url or p.url).path).lower() for p in crawl.pages if p.status == 200]
        missing = [t for t in profile.target_services if _service_words(t) and
                   not any(all(w in b for w in _service_words(t)) for b in blobs)]
        if missing:
            out.append(_mk("content.service-pages", Severity.WARN, f"No page targets {len(missing)} of {len(profile.target_services)} core services",
                           evidence=", ".join(missing[:4]), impact=4, effort=4, confidence=Confidence.HEURISTIC,
                           detail="Intent-matched pages are how a local business earns organic traffic and gives AI assistants something specific to cite.",
                           fix="Create one useful page per core service (own title, H1, price guidance, process, FAQs, local proof). "
                               "Do not mass-produce near-duplicate area pages."))

    out.append(_mk("tech.cwv-unknown", Severity.UNKNOWN, "Core Web Vitals field data not collected in this run",
                   detail="Run with --psi and a PageSpeed API key to read CrUX field data. Small sites often have no field data.",
                   impact=2, effort=1, source_url=CWV_DOC))
    return out
