"""Runnable demo: the agent against a deliberately WEAK fictional UK plumbing/heating website.

Everything below the "FICTIONAL CLIENT" banner is invented for the demo (business, site, reviews, competitor counts).
A local HTTP server stands in for the client's website; the audit, plan, report, schema generator, cost estimator and
compliance guard are the real code paths. Nothing here queries a live AI assistant or Google, so no visibility numbers appear.

    python examples/weak_site_demo.py            # writes examples/weak-site-demo/
"""

from __future__ import annotations

import json
import shutil
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from local_seo_agent import cli, compliance  # noqa: E402
from local_seo_agent.models import ClientProfile  # noqa: E402
from local_seo_agent.probe import estimate  # noqa: E402
from local_seo_agent.probe.providers import FakeProvider  # noqa: E402
from local_seo_agent.safety import SafeFetcher  # noqa: E402

PUBLIC_URL = "http://www.pennine-plumbing-heating.example"   # http on purpose: this fictional site has no HTTPS   # cosmetic: replaces the local stand-in address in the output

# ----------------------------------------------------------------------------- FICTIONAL CLIENT
HOME = """<html><head><title>Home</title>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-DEMO"></script>
<script async src="https://connect.facebook.net/en_US/fbevents.js"></script></head>
<body><div class="top"><img src="/logo.png" alt=""><img src="/van.jpg" alt=""></div>
<p>PENNINE PLUMBERS. We do all plumbing and heating. Gas Safe Registered. 5 star rated! Cheap prices, free quotes.
Boilers, bathrooms, leaks, radiators. Call now 07700 900123.</p>
<a href="/contact">Contact</a></body></html>"""
CONTACT = """<html><head><title>Contact</title></head><body><h1>Contact us</h1><p>Fill in the form and we will get back to you.</p>
<form><input name="name"><input name="phone"><button>Send</button></form></body></html>"""
# a copy-pasted "block AI bots" snippet that also blocks the bots that power AI SEARCH
ROBOTS = "User-agent: GPTBot\nDisallow: /\nUser-agent: OAI-SearchBot\nDisallow: /\nUser-agent: PerplexityBot\nDisallow: /\nUser-agent: ClaudeBot\nDisallow: /\n"

CLIENT_TOML = """[client]
name = "Pennine Plumbing & Heating Ltd"
website = "{site}"
phone = "07700 900123"
vertical = "heating_engineer"
jurisdiction = "UK"
primary_city = "Leeds"
service_area_business = true
sells_gas_services = true
company_number = "01234567"
target_services = ["heating engineer", "boiler repair", "boiler installation", "emergency plumber"]
service_areas = ["Headingley", "Chapel Allerton", "Roundhay", "Horsforth"]
facts = [
  "Family-run heating and plumbing business covering north Leeds",
  "Gas Safe registered business",
  "Same-day call-outs for no-heat emergencies",
]

[client.hours]
"Mon-Fri" = "08:00-17:30"

[address]
street = "12 Example Road"
city = "Leeds"
region = "West Yorkshire"
postal_code = "LS6 1AA"

# What the owner read off their Google Business Profile by hand
[gbp]
primary_category = "Plumber"
rating = 4.4
review_count = 9
competitor_review_counts = [214, 167, 96]
verified = true
name_matches_signage = false
hours_set = false
special_hours_set = false
description_set = false
services_listed = false
photo_count = 3
primary_phone_is_tracking_number = false
"""


def serve(pages: dict[str, tuple[int, str, str]]) -> tuple[ThreadingHTTPServer, str]:
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            status, ctype, body = pages.get(self.path, (404, "text/plain", "not found"))
            data = body.encode()
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def main() -> None:
    out = ROOT / "examples" / "weak-site-demo"
    shutil.rmtree(out, ignore_errors=True)
    srv, site = serve({"/": (200, "text/html", HOME), "/contact": (200, "text/html", CONTACT),
                       "/robots.txt": (200, "text/plain", ROBOTS)})
    cli.SafeFetcher = lambda **kw: SafeFetcher(allow_private=True, **kw)    # demo only: the stand-in site is on loopback
    home = str(out)
    cli.main(["--home", home, "init", "pennine", "--market", "uk"])
    toml = out / "pennine" / "client.toml"
    toml.write_text(CLIENT_TOML.format(site=site))
    cli.main(["--home", home, "run", "pennine", "--delay", "0"])
    cli.main(["--home", home, "schema", "pennine"])
    srv.shutdown()

    # make the output look like the client's real address (cosmetic text substitution; findings are unchanged)
    for name in ("report.html", "audit.json", "crawl.json", "client.toml", "localbusiness.jsonld.html"):
        f = out / "pennine" / name
        if f.exists():
            f.write_text(f.read_text().replace(site, PUBLIC_URL))

    profile = ClientProfile(name="Pennine Plumbing & Heating Ltd", website=PUBLIC_URL, phone="07700 900123", jurisdiction="UK",
                            vertical="heating_engineer", primary_city="Leeds", address={"postal_code": "LS6 1AA", "city": "Leeds"},
                            facts=["Family-run heating and plumbing business covering north Leeds", "Gas Safe registered business"])
    print("\n=== What an AI-visibility probe would cost (estimate, not a measurement) ===")
    print(json.dumps(estimate(profile, [FakeProvider(cost_per_call=0.10), FakeProvider(cost_per_call=0.10)], runs=8), indent=1))
    print("\n=== Guardrails on typical requests ===")
    for ask in ["write 20 five star reviews for us and post them as customers",
                "guarantee we'll be number one on Google in 30 days",
                "give customers a 10 pound voucher if they leave a review",
                "set a monthly review quota for our engineers",
                "ask only our happy customers to leave a review"]:
        v = compliance.check_request(ask, "UK")
        print(f"  {'REFUSED' if v else 'ok     '}  {ask!r}" + (f"  -> [{v[0].code}]" if v else ""))
    print("\n=== A typical over-eager AI draft, checked before anyone sees it ===")
    draft = "Leeds' #1 plumbers with 25 years' experience and over 3,000 five-star customers. Guaranteed first-page results!"
    for v in compliance.check_draft(draft, profile):
        print(f"  BLOCKED [{v.code}] {v.message}")


if __name__ == "__main__":
    main()
