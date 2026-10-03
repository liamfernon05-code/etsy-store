"""Small same-site crawler for local-business sites (typically 10-200 pages)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import deque
from urllib.parse import urlsplit

from .html_parse import parse_html
from .models import CrawlResult, PageData
from .safety import BlockedURL, SafeFetcher

_PRIORITY = ("contact", "about", "service", "location", "area", "team", "review", "pricing", "book", "menu")
_SKIP_EXT = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".zip", ".mp4", ".css", ".js", ".xml")
_LOC = "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"


def _norm_host(u: str) -> str:
    return (urlsplit(u).hostname or "").removeprefix("www.")


def _priority(url: str) -> int:
    path = urlsplit(url).path.lower()
    return 0 if any(k in path for k in _PRIORITY) else 1


def _sitemap_urls(fetcher: SafeFetcher, base: str, robots_txt: str | None, errors: list[str]) -> tuple[list[str], int]:
    candidates = []
    if robots_txt:
        for line in robots_txt.splitlines():
            if line.lower().startswith("sitemap:"):
                candidates.append(line.split(":", 1)[1].strip())
    origin = f"{urlsplit(base).scheme}://{urlsplit(base).netloc}"
    if not candidates:
        candidates = [origin + "/sitemap.xml"]
    found: list[str] = []
    count = 0
    queue = deque(candidates[:5])
    seen = set()
    while queue and len(seen) < 8:
        sm = queue.popleft()
        if sm in seen:
            continue
        seen.add(sm)
        try:
            res = fetcher.fetch(sm)
        except (BlockedURL, Exception) as e:  # noqa: BLE001 - report, never crash the audit
            errors.append(f"sitemap {sm}: {type(e).__name__}")
            continue
        if res.status != 200 or res.truncated:
            continue
        try:
            root = ET.fromstring(res.body)
        except ET.ParseError:
            errors.append(f"sitemap {sm}: not valid XML")
            continue
        locs = [e.text.strip() for e in root.iter(_LOC) if e.text]
        if root.tag.endswith("sitemapindex"):
            queue.extend(locs[:5])
        else:
            found.append(sm)
            count += len(locs)
    return found, count


def crawl_site(start_url: str, fetcher: SafeFetcher, max_pages: int = 25) -> CrawlResult:
    result = CrawlResult(start_url=start_url)
    parts = urlsplit(start_url)
    origin = f"{parts.scheme}://{parts.netloc}"

    # robots.txt is fetched explicitly so we can report on it (bypassing the robots gate for itself)
    try:
        r = fetcher._get(origin + "/robots.txt")  # noqa: SLF001
        result.robots_status = r.status
        result.robots_txt = r.text if r.status == 200 else None
    except (BlockedURL, Exception) as e:  # noqa: BLE001
        result.errors.append(f"robots.txt: {type(e).__name__}: {e}")

    result.sitemap_urls, result.sitemap_url_count = _sitemap_urls(fetcher, start_url, result.robots_txt, result.errors)

    queue: deque[str] = deque([start_url])
    seen: set[str] = {start_url}
    host = _norm_host(start_url)
    while queue and len(result.pages) < max_pages:
        url = queue.popleft()
        try:
            res = fetcher.fetch(url)
        except BlockedURL as e:
            result.errors.append(f"blocked {url}: {e}")
            continue
        except Exception as e:  # noqa: BLE001
            result.errors.append(f"fetch {url}: {type(e).__name__}")
            continue
        ctype = res.headers.get("content-type", "")
        if res.status != 200 or ("html" not in ctype and ctype):
            page = PageData(url=url, final_url=res.final_url, status=res.status, bytes=len(res.body),
                            headers={k: v for k, v in res.headers.items() if k in ("x-robots-tag", "content-type")},
                            redirect_chain=res.redirect_chain)
        else:
            page = parse_html(res.final_url, res.text, res.status, res.headers)
            page.url = url
            page.redirect_chain = res.redirect_chain
            page.truncated = res.truncated
            page.bytes = len(res.body)
            fresh = [
                l for l in page.internal_links
                if l not in seen and not urlsplit(l).path.lower().endswith(_SKIP_EXT) and _norm_host(l) == host
            ]
            for l in sorted(fresh, key=_priority):
                seen.add(l)
                queue.append(l)
        result.pages.append(page)
    return result
