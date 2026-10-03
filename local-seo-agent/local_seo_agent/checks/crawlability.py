"""Check 1 (highest leverage): can search engines AND AI answer engines reach the site at all?"""

from __future__ import annotations

import urllib.robotparser

from ..facts import VERIFIED
from ..models import Confidence, CrawlResult, Finding, Severity

# Bots that decide whether you can appear in search / AI answers. Blocking these costs visibility.
SEARCH_BOTS = {
    "Googlebot": "Google Search, AI Overviews, Maps ranking",
    "Bingbot": "Bing, Copilot and assistants that use Bing",
    "OAI-SearchBot": "ChatGPT search index",
    "Claude-SearchBot": "Claude search quality",
    "PerplexityBot": "Perplexity index",
    "Applebot": "Apple/Siri/Spotlight",
}
# Training-only bots: blocking is the owner's business choice and does NOT affect search visibility.
TRAINING_BOTS = ["GPTBot", "ClaudeBot", "Google-Extended", "Applebot-Extended", "CCBot"]
USER_BOTS = ["ChatGPT-User", "Claude-User", "Perplexity-User"]

_DOC = "https://developers.google.com/search/docs/crawling-indexing/robots/intro"


def _mk(id_, sev, title, **kw) -> Finding:
    return Finding(id=id_, category="crawlability", severity=sev, title=title, verified_on=VERIFIED, **kw)


def check_crawlability(crawl: CrawlResult) -> list[Finding]:
    out: list[Finding] = []
    home = crawl.home
    if home is None or home.status == 0:
        return [_mk("crawl.home-unreachable", Severity.ERROR, "Homepage could not be fetched",
                    detail="; ".join(crawl.errors[:3]), impact=5, effort=3,
                    fix="Confirm the URL, SSL certificate and that the site does not block our crawler or robots.txt.")]

    # robots.txt state
    rp: urllib.robotparser.RobotFileParser | None = None
    if crawl.robots_status == 200 and crawl.robots_txt is not None:
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(crawl.robots_txt.splitlines())
    elif 500 <= crawl.robots_status < 600:
        out.append(_mk("crawl.robots-5xx", Severity.ERROR, "robots.txt returns a server error",
                       detail="Google treats a 5xx robots.txt as 'disallow all' until it recovers.",
                       impact=5, effort=2, fix="Fix the server error on /robots.txt."))
    elif crawl.robots_status in (404, 410):
        out.append(_mk("crawl.robots-missing", Severity.INFO, "No robots.txt (everything allowed)",
                       detail="Fine for visibility, but add one that lists your sitemap.", impact=1, effort=1,
                       fix="Add /robots.txt with a Sitemap: line."))

    url = home.final_url or home.url
    if rp is not None:
        blocked = [b for b in SEARCH_BOTS if not rp.can_fetch(b, url)]
        for bot in blocked:
            out.append(_mk(f"crawl.blocked.{bot}", Severity.ERROR,
                           f"robots.txt blocks {bot} ({SEARCH_BOTS[bot]})",
                           detail="Search/answer bots must be allowed to be recommended.",
                           evidence=f"robots.txt disallows {bot} for {url}", impact=5, effort=1,
                           source_url=_DOC, fix=f"Allow {bot} in robots.txt (e.g. 'User-agent: {bot}' / 'Allow: /')."))
        tb = [b for b in TRAINING_BOTS if not rp.can_fetch(b, url)]
        if tb:
            out.append(_mk("crawl.training-blocked", Severity.INFO,
                           "Training-only bots are blocked: " + ", ".join(tb),
                           detail="Owner's choice. Per vendor docs this does not affect search/answer inclusion.",
                           confidence=Confidence.OFFICIAL, impact=1, effort=1))
        ub = [b for b in USER_BOTS if not rp.can_fetch(b, url)]
        if ub:
            out.append(_mk("crawl.user-bots", Severity.INFO,
                           "User-initiated fetchers listed as disallowed: " + ", ".join(ub),
                           detail="These fetch pages when a person asks an assistant about them and may ignore robots.txt anyway.",
                           impact=1, effort=1))

    # noindex on the homepage (meta or header)
    if "noindex" in home.robots_meta or "noindex" in home.headers.get("x-robots-tag", "").lower():
        out.append(_mk("crawl.noindex-home", Severity.ERROR, "Homepage is set to noindex",
                       evidence=(home.robots_meta or home.headers.get("x-robots-tag", ""))[:80],
                       impact=5, effort=1, fix="Remove the noindex directive (meta robots / X-Robots-Tag)."))

    # JS-only shell: most AI crawlers do not execute JavaScript
    if home.word_count < 50 and home.scripts >= 3:
        out.append(_mk("crawl.js-shell", Severity.WARN, "Homepage HTML has almost no text but loads scripts",
                       detail="Most AI crawlers do not run JavaScript; content rendered client-side may be invisible to them.",
                       evidence=f"{home.word_count} words, {home.scripts} scripts", impact=4, effort=3,
                       confidence=Confidence.HEURISTIC,
                       fix="Server-render the key content (services, NAP, hours) or add static HTML."))

    # what we cannot see
    out.append(_mk("crawl.waf-unknown", Severity.UNKNOWN, "CDN/WAF bot blocking cannot be detected from outside",
                   detail="Cloudflare blocks AI bots by default on domains created since 2025-07-01. A spoofed user-agent "
                          "test is unreliable because WAFs verify bots by IP.",
                   impact=4, effort=1, confidence=Confidence.OFFICIAL,
                   fix="Check Cloudflare 'AI Crawl Control' / WAF settings and server logs for real OAI-SearchBot, "
                       "PerplexityBot, Claude-SearchBot hits."))
    return out
