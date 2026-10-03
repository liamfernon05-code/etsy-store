"""SSRF-safe, robots-aware, rate-limited fetcher.

The agent reads untrusted URLs (client site, competitor sites), so every hop is validated:
 * http/https only, no userinfo (http://good.com@127.0.0.1), standard ports only
 * hostname is resolved by us (decimal/hex/octal IP forms normalise through getaddrinfo) and EVERY
   resolved address must be public (private, loopback, link-local, metadata, CGNAT 100.64/10, multicast,
   reserved, unspecified and IPv4-mapped IPv6 are all rejected)
 * we then CONNECT TO THE VALIDATED IP (with Host header + SNI/cert check for the real hostname), so DNS
   rebinding between check and connect is impossible
 * redirects are followed manually and each hop is re-validated
 * response size and time are capped; politeness delay per host; robots.txt is honoured by default
"""

from __future__ import annotations

import ipaddress
import os
import socket
import ssl
import time
import urllib.robotparser
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

DEFAULT_UA = "LocalSEOAgent/0.1 (+site-audit; contact: set LSA_CONTACT)"
_CGNAT = ipaddress.ip_network("100.64.0.0/10")
_BLOCKED_NETS = [ipaddress.ip_network(n) for n in ("0.0.0.0/8", "192.0.0.0/24", "198.18.0.0/15", "240.0.0.0/4")]


class BlockedURL(Exception):
    """Raised when a URL fails SSRF validation or robots.txt."""


def is_public_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    if isinstance(ip, ipaddress.IPv6Address) and ip.sixtofour is not None:
        ip = ip.sixtofour
    if (
        ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast
        or ip.is_reserved or ip.is_unspecified
    ):
        return False
    if isinstance(ip, ipaddress.IPv4Address):
        if ip in _CGNAT or any(ip in n for n in _BLOCKED_NETS):
            return False
    return True


def resolve(host: str, port: int) -> list[str]:
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    return sorted({i[4][0].split("%")[0] for i in infos})  # strip IPv6 zone ids


def validate_url(url: str, allow_private: bool = False, allow_ports: tuple[int, ...] = (80, 443)) -> tuple[str, str, int, list[str]]:
    """Return (scheme, host, port, public_ips) or raise BlockedURL."""
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https"):
        raise BlockedURL(f"scheme not allowed: {parts.scheme or 'none'}")
    if "@" in parts.netloc:
        raise BlockedURL("userinfo in URL is not allowed")
    host = parts.hostname
    if not host:
        raise BlockedURL("missing host")
    port = parts.port or (443 if parts.scheme == "https" else 80)
    if not allow_private and port not in allow_ports:
        raise BlockedURL(f"port not allowed: {port}")
    try:
        ips = resolve(host, port)
    except socket.gaierror as e:
        raise BlockedURL(f"cannot resolve {host}: {e}") from e
    if not ips:
        raise BlockedURL(f"no addresses for {host}")
    if not allow_private:
        for ip in ips:
            if not is_public_ip(ipaddress.ip_address(ip)):
                raise BlockedURL(f"{host} resolves to non-public address {ip}")
    return parts.scheme, host, port, ips


@dataclass
class FetchResult:
    url: str
    final_url: str
    status: int
    headers: dict[str, str]
    body: bytes
    truncated: bool = False
    redirect_chain: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class SafeFetcher:
    def __init__(
        self,
        user_agent: str = DEFAULT_UA,
        timeout: float = 15.0,
        max_bytes: int = 3_000_000,
        min_interval: float = 1.0,
        max_redirects: int = 5,
        respect_robots: bool = True,
        allow_private: bool = False,  # tests only; never enable against client-supplied URLs
    ):
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.min_interval = min_interval
        self.max_redirects = max_redirects
        self.respect_robots = respect_robots
        self.allow_private = allow_private
        self._last: dict[str, float] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.requests_made = 0

    @staticmethod
    def _ssl() -> ssl.SSLContext:
        """TLS verification is always on. Corporate/sandbox proxies that re-sign traffic: point LSA_CA_BUNDLE
        (or SSL_CERT_FILE) at their CA bundle instead of disabling verification."""
        cafile = os.environ.get("LSA_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
        return ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()

    # -- robots ---------------------------------------------------------------------------------
    def _robots_for(self, scheme: str, netloc: str) -> urllib.robotparser.RobotFileParser | None:
        key = f"{scheme}://{netloc}"
        if key in self._robots:
            return self._robots[key]
        rp: urllib.robotparser.RobotFileParser | None
        try:
            res = self._get(f"{key}/robots.txt")
            if res.status == 200:
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(res.text.splitlines())
            elif 500 <= res.status < 600:
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(["User-agent: *", "Disallow: /"])  # Google treats 5xx as disallow-all
            else:
                rp = None  # 4xx: no robots.txt, everything allowed
        except (BlockedURL, httpx.HTTPError):
            rp = None
        self._robots[key] = rp
        return rp

    def allowed_by_robots(self, url: str) -> bool:
        p = urlsplit(url)
        rp = self._robots_for(p.scheme, p.netloc)
        return True if rp is None else rp.can_fetch(self.user_agent, url)

    # -- fetch ----------------------------------------------------------------------------------
    def _throttle(self, host: str) -> None:
        wait = self._last.get(host, 0.0) + self.min_interval - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last[host] = time.monotonic()

    def _get(self, url: str) -> FetchResult:
        """Fetch with manual, re-validated redirects. Does not consult robots.txt."""
        chain: list[str] = []
        current = url
        for _ in range(self.max_redirects + 1):
            scheme, host, port, ips = validate_url(current, self.allow_private)
            self._throttle(host)
            parts = urlsplit(current)
            ip = ips[0]
            ip_host = f"[{ip}]" if ":" in ip else ip
            default_port = 443 if scheme == "https" else 80
            netloc = ip_host if port == default_port else f"{ip_host}:{port}"
            target = urlunsplit((scheme, netloc, parts.path or "/", parts.query, ""))
            headers = {
                "Host": parts.netloc.rsplit("@", 1)[-1],
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5",
            }
            ext = {"sni_hostname": host} if scheme == "https" else {}
            body = bytearray()
            truncated = False
            with httpx.Client(timeout=self.timeout, follow_redirects=False, trust_env=False, verify=self._ssl()) as client:
                with client.stream("GET", target, headers=headers, extensions=ext) as r:
                    self.requests_made += 1
                    for chunk in r.iter_bytes():
                        body.extend(chunk)
                        if len(body) > self.max_bytes:
                            truncated = True
                            del body[self.max_bytes:]
                            break
                    status = r.status_code
                    resp_headers = {k.lower(): v for k, v in r.headers.items()}
            if status in (301, 302, 303, 307, 308) and "location" in resp_headers:
                chain.append(current)
                current = urljoin(current, resp_headers["location"])
                continue
            return FetchResult(url, current, status, resp_headers, bytes(body), truncated, chain)
        raise BlockedURL(f"too many redirects from {url}")

    def fetch(self, url: str) -> FetchResult:
        if self.respect_robots and not self.allowed_by_robots(url):
            raise BlockedURL(f"disallowed by robots.txt for {self.user_agent}: {url}")
        return self._get(url)
