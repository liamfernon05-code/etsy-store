"""Optional JavaScript rendering (playwright-python, 15k stars) to see what a JS-capable crawler sees.

Why: most AI crawlers do not execute JavaScript, but Googlebot does. Comparing raw HTML with the rendered DOM shows
whether key content (services, NAP, hours) only exists after JS runs, so it may be invisible to AI answer engines.

SSRF design (hardened after the API-contract research found that `context.route` does NOT see HTTP redirect hops,
WebSockets or data:/blob: fetches): the browser NEVER touches the network itself. Every request is intercepted and re-fetched by our own
SafeFetcher (public IPs only, pinned connect, per-hop redirect validation, size/time caps) and fulfilled back into the
page. Consequently DNS rebinding, redirects to internal hosts, and requests the page makes to internal services are all
handled by the same validated code path. The browser is also launched with a DEAD proxy (127.0.0.1:9, bypass '<-loopback>'), so any request route() cannot see
(WebSockets, preconnects) fails closed. Additionally: only GET, only the client's own host (third-party scripts and
trackers are aborted), service workers blocked, downloads off, request/byte budgets, images/media/fonts aborted.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from .html_parse import parse_html
from .models import PageData
from .safety import BlockedURL, SafeFetcher

BLOCKED_TYPES = {"image", "media", "font", "websocket", "eventsource", "manifest", "other"}


@dataclass
class RenderStats:
    fulfilled: int = 0
    aborted: int = 0
    bytes: int = 0
    reasons: list[str] = field(default_factory=list)


def _host(u: str) -> str:
    """Origin key = hostname + effective port (a different port on the same host is a different service)."""
    p = urlsplit(u)
    port = p.port or (443 if p.scheme == "https" else 80)
    return f"{(p.hostname or '').removeprefix('www.').lower()}:{port}"


def render_page(url: str, fetcher: SafeFetcher, max_requests: int = 60, max_total_bytes: int = 8_000_000,
                timeout_ms: int = 15_000, executable_path: str | None = None) -> tuple[PageData, RenderStats]:
    """Render `url` and return the parsed rendered DOM plus stats. Raises RuntimeError if playwright is missing."""
    try:
        from playwright.sync_api import sync_playwright  # lazy: optional dependency
    except ImportError as e:  # pragma: no cover - depends on environment
        raise RuntimeError("JS rendering needs: pip install playwright && playwright install chromium") from e

    stats = RenderStats()
    origin_host = _host(url)
    exe = executable_path or os.environ.get("LSA_CHROMIUM_PATH") or None

    def handler(route):
        req = route.request
        reason = ""
        if req.method != "GET":
            reason = f"method {req.method}"
        elif req.resource_type in BLOCKED_TYPES:
            reason = f"type {req.resource_type}"
        elif urlsplit(req.url).scheme not in ("http", "https"):
            reason = "scheme"
        elif _host(req.url) != origin_host:
            reason = "third-party host"
        elif stats.fulfilled >= max_requests or stats.bytes >= max_total_bytes:
            reason = "budget exceeded"
        if reason:
            stats.aborted += 1
            if len(stats.reasons) < 10:
                stats.reasons.append(f"{reason}: {req.url[:80]}")
            route.abort()
            return
        try:
            res = fetcher._get(req.url) if req.resource_type != "document" else fetcher.fetch(req.url)  # noqa: SLF001
        except BlockedURL as e:
            stats.aborted += 1
            stats.reasons.append(f"blocked: {e}")
            route.abort()
            return
        except Exception as e:  # noqa: BLE001
            stats.aborted += 1
            stats.reasons.append(f"fetch error: {type(e).__name__}")
            route.abort()
            return
        if 300 <= res.status < 400:  # never hand the browser a redirect: Chromium would follow it itself, unseen by route()
            stats.aborted += 1
            stats.reasons.append(f"redirect not fulfilled: {req.url[:80]}")
            route.abort()
            return
        stats.fulfilled += 1
        stats.bytes += len(res.body)
        headers = {"content-type": res.headers.get("content-type", "application/octet-stream")}
        route.fulfill(status=res.status, headers=headers, body=res.body)

    args = ["--disable-background-networking", "--proxy-bypass-list=<-loopback>"]
    if os.geteuid() == 0:
        args += ["--no-sandbox", "--disable-dev-shm-usage"]
    with sync_playwright() as p:
        # FAIL-CLOSED network: Chromium is pointed at a dead proxy. Every request we fulfil in route() never touches the
        # network; anything route() cannot see (WebSockets, preconnects, ...) fails instead of reaching an internal host.
        browser = p.chromium.launch(executable_path=exe, headless=True, args=args,
                                    proxy={"server": "http://127.0.0.1:9", "bypass": "<-loopback>"})
        try:
            ctx = browser.new_context(service_workers="block", accept_downloads=False, java_script_enabled=True,
                                      user_agent=fetcher.user_agent, bypass_csp=False, permissions=[])
            ctx.route("**/*", handler)
            # WebSockets bypass route(). Verified experimentally: with no proxy the page's WebSocket reached a loopback
            # "internal service" (1 TCP connection); with the dead proxy it did not (0). route_web_socket() was avoided on
            # purpose: it hung the sync API in testing. The dead proxy is therefore the boundary for anything route() misses.
            page = ctx.new_page()
            page.set_default_timeout(timeout_ms)
            page.goto(url, wait_until="networkidle")
            html = page.content()
        finally:
            browser.close()
    data = parse_html(url, html, 200)
    return data, stats


def render_findings(raw: PageData, rendered: PageData, phone_digits: str = "") -> list:
    """Findings from comparing the raw HTML with the JS-rendered DOM (what AI crawlers vs Googlebot can see)."""
    from .facts import VERIFIED
    from .models import Confidence, Finding, Severity

    out = []

    def mk(id_, sev, title, **kw):
        out.append(Finding(id=f"render.{id_}", category="crawlability", severity=sev, title=title, verified_on=VERIFIED,
                           confidence=Confidence.EVIDENCE, **kw))

    if rendered.word_count >= max(150, raw.word_count * 3):
        mk("js-dependent", Severity.WARN, "Most page content only appears after JavaScript runs",
           evidence=f"raw {raw.word_count} words vs rendered {rendered.word_count}", impact=4, effort=3,
           detail="Googlebot renders JavaScript, but most AI crawlers do not, so this content may be invisible to them.",
           fix="Server-render the key content (services, NAP, hours) or add it as static HTML.")
    if phone_digits:
        rd = "".join(ch for ch in rendered.text if ch.isdigit())
        wd = "".join(ch for ch in raw.text if ch.isdigit())
        if phone_digits[-10:] in rd and phone_digits[-10:] not in wd:
            mk("nap-js-only", Severity.WARN, "Phone number only appears after JavaScript runs", impact=4, effort=2,
               fix="Put the primary phone number in the static HTML (header/footer and contact page).")
    return out
