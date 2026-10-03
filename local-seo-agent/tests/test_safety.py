import ipaddress

import pytest

from local_seo_agent import safety
from local_seo_agent.safety import BlockedURL, SafeFetcher, is_public_ip, validate_url


@pytest.mark.parametrize("ip", [
    "127.0.0.1", "10.1.2.3", "172.16.0.1", "192.168.1.1", "169.254.169.254", "100.64.0.1", "100.127.255.254",
    "0.0.0.0", "224.0.0.1", "240.0.0.1", "198.18.0.1", "::1", "fe80::1", "fc00::1", "::ffff:127.0.0.1", "::ffff:10.0.0.1",
])
def test_non_public_ips_blocked(ip):
    assert not is_public_ip(ipaddress.ip_address(ip))


@pytest.mark.parametrize("ip", ["8.8.8.8", "93.184.216.34", "2606:4700:4700::1111"])
def test_public_ips_allowed(ip):
    assert is_public_ip(ipaddress.ip_address(ip))


@pytest.mark.parametrize("url", [
    "file:///etc/passwd", "ftp://example.com/", "gopher://example.com/", "javascript:alert(1)",
    "http://good.example@127.0.0.1/", "http://user:pw@example.com/", "http://127.0.0.1/", "http://localhost/",
    "http://2130706433/",          # decimal form of 127.0.0.1
    "http://0x7f.0.0.1/",          # hex form
    "http://0177.0.0.1/",          # octal form
    "http://[::1]/", "http://169.254.169.254/latest/meta-data/", "http://100.64.0.1/",
    "http://example.com:8080/",    # non-standard port
])
def test_validate_url_blocks(url):
    with pytest.raises(BlockedURL):
        validate_url(url)


def test_validate_url_blocks_dns_rebinding_to_private(monkeypatch):
    monkeypatch.setattr(safety, "resolve", lambda host, port: ["93.184.216.34", "10.0.0.5"])  # one bad answer poisons it
    with pytest.raises(BlockedURL):
        validate_url("http://evil.example/")


def test_validate_url_accepts_public(monkeypatch):
    monkeypatch.setattr(safety, "resolve", lambda host, port: ["93.184.216.34"])
    assert validate_url("https://example.com/path")[1] == "example.com"


def test_fetch_blocks_loopback_by_default(site):
    base, _ = site
    with pytest.raises(BlockedURL):
        SafeFetcher(min_interval=0).fetch(base + "/")


def test_fetch_ok_when_private_allowed(site):
    base, _ = site
    r = SafeFetcher(min_interval=0, allow_private=True).fetch(base + "/")
    assert r.status == 200 and b"Riverside" in r.body


def test_redirects_are_revalidated(site):
    base, pages = site
    pages["/go"] = (302, "text/html", "file:///etc/passwd")
    with pytest.raises(BlockedURL):
        SafeFetcher(min_interval=0, allow_private=True, respect_robots=False).fetch(base + "/go")
    pages["/go2"] = (302, "text/html", "http://user@evil.example/")
    with pytest.raises(BlockedURL):
        SafeFetcher(min_interval=0, allow_private=True, respect_robots=False).fetch(base + "/go2")


def test_redirect_loop_capped(site):
    base, pages = site
    pages["/a"] = (302, "text/html", "/b")
    pages["/b"] = (302, "text/html", "/a")
    with pytest.raises(BlockedURL):
        SafeFetcher(min_interval=0, allow_private=True, respect_robots=False, max_redirects=3).fetch(base + "/a")


def test_size_cap(site):
    base, pages = site
    pages["/big"] = (200, "text/html", "x" * 5000)
    r = SafeFetcher(min_interval=0, allow_private=True, respect_robots=False, max_bytes=1000).fetch(base + "/big")
    assert r.truncated and len(r.body) == 1000


def test_robots_enforced(site):
    base, pages = site
    pages["/robots.txt"] = (200, "text/plain", "User-agent: *\nDisallow: /private\n")
    pages["/private/x"] = (200, "text/html", "secret")
    f = SafeFetcher(min_interval=0, allow_private=True)
    assert f.fetch(base + "/").status == 200
    with pytest.raises(BlockedURL):
        f.fetch(base + "/private/x")


def test_robots_5xx_means_disallow(site):
    base, pages = site
    pages["/robots.txt"] = (503, "text/plain", "down")
    with pytest.raises(BlockedURL):
        SafeFetcher(min_interval=0, allow_private=True).fetch(base + "/")
