import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from local_seo_agent.models import ClientProfile

GOOD_HOME = """<!doctype html><html lang="en"><head><title>Riverside Family Dental | Dentist in Austin</title>
<meta name="description" content="Family dentist in Austin"><meta name="viewport" content="width=device-width">
<link rel="canonical" href="http://{host}/">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Dentist","name":"Riverside Family Dental",
"url":"http://{host}/","telephone":"+1 512-555-0147","address":{"@type":"PostalAddress","streetAddress":"123 Main St",
"addressLocality":"Austin","postalCode":"78701"},"aggregateRating":{"@type":"AggregateRating","ratingValue":"4.9","reviewCount":"50"}}</script>
</head><body><h1>Dentist in Austin</h1><p>Riverside Family Dental, 123 Main St, Austin TX 78701.
Call <a href="tel:5125550147">(512) 555-0147</a>. Family dentistry, whitening and implants for the whole family in Austin.
We serve patients from across the city and offer same day emergency appointments on weekdays.</p>
<a href="/contact">Contact</a><a href="/services/whitening">Whitening</a></body></html>"""

CONTACT = """<html lang="en"><head><title>Contact | Riverside Family Dental</title></head><body><h1>Contact</h1>
<p>Riverside Family Dental, 123 Main St, Austin TX 78701. Phone (512) 555-0147.</p></body></html>"""

WHITENING = """<html lang="en"><head><title>Teeth whitening Austin</title></head><body><h1>Teeth whitening</h1><p>Info.</p></body></html>"""

ROBOTS_BLOCKING = "User-agent: OAI-SearchBot\nDisallow: /\nUser-agent: GPTBot\nDisallow: /\nUser-agent: *\nAllow: /\n"
SITEMAP = """<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>http://{host}/</loc></url><url><loc>http://{host}/contact</loc></url></urlset>"""


def make_handler(pages: dict[str, tuple[int, str, str]], host_box: list):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):  # silence
            pass

        def do_GET(self):
            status, ctype, body = pages.get(self.path, (404, "text/html", "not found"))
            if status in (301, 302):
                self.send_response(status)
                self.send_header("Location", body)
                self.end_headers()
                return
            data = body.replace("{host}", host_box[0]).encode()
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return H


@pytest.fixture
def site():
    """Start a local 'client site'. Yields (base_url, pages dict) so tests can mutate pages."""
    host_box = [""]
    pages = {
        "/": (200, "text/html; charset=utf-8", GOOD_HOME),
        "/contact": (200, "text/html", CONTACT),
        "/services/whitening": (200, "text/html", WHITENING),
        "/robots.txt": (200, "text/plain", "User-agent: *\nAllow: /\nSitemap: http://{host}/sitemap.xml\n"),
        "/sitemap.xml": (200, "application/xml", SITEMAP),
    }
    srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(pages, host_box))
    host_box[0] = f"127.0.0.1:{srv.server_address[1]}"
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://{host_box[0]}", pages
    srv.shutdown()


@pytest.fixture
def profile():
    return ClientProfile(
        name="Riverside Family Dental", website="http://127.0.0.1", phone="(512) 555-0147", vertical="dentist",
        primary_city="Austin", target_services=["dentist", "emergency dentist"],
        address={"street": "123 Main St", "city": "Austin", "region": "TX", "postal_code": "78701", "country": "US"},
        facts=["Family-owned practice serving Austin since 2011", "Same-day emergency appointments weekdays"],
    )
