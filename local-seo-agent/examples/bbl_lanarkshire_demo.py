"""Demo: the agent for a NEW Google Business Profile of a franchise-branch, NON-SURGICAL body-contouring ("booty lift") studio in
North Lanarkshire, Scotland.

ILLUSTRATIVE, NOT THE CLIENT'S REAL DATA. The live site could not be fetched from the build sandbox. The one sentence marked
"public listing wording" was seen in a public search-result snippet for the business and is quoted so the agent can show how it
would treat it; every other claim, contact detail, review count and Google-profile fact below is INVENTED for the demo.
A local HTTP server stands in for the website. The audit, plan, report, schema generator, claims scanner and compliance guard are
the real code paths. No AI assistant or Google service is queried, so no visibility numbers appear.

    python examples/bbl_lanarkshire_demo.py        # writes examples/bbl-lanarkshire-demo/
"""

from __future__ import annotations

import json
import shutil
import sys
import threading
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from local_seo_agent import cli, compliance  # noqa: E402
from local_seo_agent.models import ClientProfile  # noqa: E402
from local_seo_agent.probe import estimate  # noqa: E402
from local_seo_agent.probe.prompts import build_prompts  # noqa: E402
from local_seo_agent.probe.providers import FakeProvider  # noqa: E402
from local_seo_agent.safety import SafeFetcher  # noqa: E402

CLIENT_NAME = "brazilian bootlift lanarkshire"          # exactly as the user gave it
BRAND_DOMAIN = "www.brazilianbootylift.example"          # fictional stand-in for the franchisor's domain
PAGE_PATH = "/stores/brazilian-bootylift-lanarkshire/"

# ----------------------------------------------------------------------------- ILLUSTRATIVE PAGE
HOME = """<html lang="en"><head><title>Brazilian Bootylift Lanarkshire</title>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-DEMO"></script>
<script async src="https://connect.facebook.net/en_US/fbevents.js"></script></head><body>
<img src="/van.jpg" alt=""><img src="/studio.jpg" alt="">
<h1>Brazilian Booty Lift Lanarkshire</h1>
<p>Brazilian Booty Lift Lanarkshire offers the safest and fastest way to boost your rear appeal, sculpt your curves, erase cellulite and tighten loose skin using the latest non-surgical breakthrough in body contouring.</p>
<p>Painless, no downtime and permanent results. Clinically proven. Detox your lymphatic system and get the same results as a surgical BBL without the risks.</p>
<p>BOOK NOW AND SAVE 20% THIS MONTH. Only 4 slots left, offer ends tonight!</p>
<h2>Real results gallery</h2><p>Before and after photos of our clients.</p>
<p>Call 07700 900123.</p><a href="/contact">Contact</a></body></html>"""
CONTACT = """<html><head><title>Contact</title></head><body><h1>Contact us</h1><p>Use the form to book.</p>
<form><input name="n"><button>Send</button></form></body></html>"""

TOML = """[client]
name = "{name}"
website = "{site}"
phone = "07700 900123"
vertical = "body_contouring"
jurisdiction = "UK"
primary_city = "Wishaw"
treatment_type = "non_surgical_device"
delivered_by = "beauty therapist"
franchise_brand = "Brazilian Booty Lift"
brand_domain = "{brand_host}"
service_area_business = false
target_services = ["booty lift", "body contouring", "cellulite treatment"]
service_areas = ["Wishaw", "Motherwell", "Hamilton", "Airdrie", "Coatbridge", "East Kilbride"]
facts = [
  "Non-surgical body contouring using devices; no surgery, no injections, no fat transfer",
  "Appointments with a trained therapist after a consultation",
]

[client.hours]
"Mon-Fri" = "09:00-17:00"

[address]
street = "1 Example Road"
city = "Wishaw"
region = "North Lanarkshire"
council_area = "North Lanarkshire"
postal_code = "ML2 9ZZ"

# Google Business Profile facts (INVENTED for the demo): profile accepted four days ago, nothing done yet
[gbp]
primary_category = "Beauty salon"
verified = true
verified_on = "{verified_on}"
review_count = 0
hours_set = false
special_hours_set = false
description_set = false
services_listed = false
photo_count = 1
"""


def serve(pages: dict[str, tuple[int, str, str]]):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            status, ctype, body = pages.get(self.path.split("?")[0], (404, "text/plain", "not found"))
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
    out = ROOT / "examples" / "bbl-lanarkshire-demo"
    shutil.rmtree(out, ignore_errors=True)
    srv, site = serve({PAGE_PATH: (200, "text/html", HOME), "/contact": (200, "text/html", CONTACT),
                       "/robots.txt": (200, "text/plain", "User-agent: *\nAllow: /\n")})
    cli.SafeFetcher = lambda **kw: SafeFetcher(allow_private=True, **kw)      # demo only: the stand-in site is on loopback
    home = str(out)
    cli.main(["--home", home, "init", "lanarkshire", "--market", "uk", "--vertical", "body_contouring"])
    host = site.replace("http://", "")
    (out / "lanarkshire" / "client.toml").write_text(TOML.format(
        name=CLIENT_NAME, site=site + PAGE_PATH, brand_host=host, verified_on=(date.today() - timedelta(days=4)).isoformat()))
    cli.main(["--home", home, "run", "lanarkshire", "--delay", "0"])
    # The stand-in server is plain http, so the audit reports "not served over HTTPS". That is an artifact of THIS DEMO HARNESS, not a
    # statement about the client's real site, so that single finding is removed and the plan/report regenerated.
    audit = out / "lanarkshire" / "audit.json"
    audit.write_text(json.dumps([f for f in json.loads(audit.read_text()) if f["id"] != "tech.https"], indent=1))
    cli.main(["--home", home, "plan", "lanarkshire"])
    cli.main(["--home", home, "report", "lanarkshire"])
    cli.main(["--home", home, "schema", "lanarkshire"])
    srv.shutdown()
    for name in ("report.html", "audit.json", "crawl.json", "client.toml", "plan.json", "localbusiness.jsonld.html"):
        f = out / "lanarkshire" / name
        if f.exists():                                                     # cosmetic: show a franchise-style address instead of the loopback stand-in
            f.write_text(f.read_text().replace(site, "https://" + BRAND_DOMAIN).replace(host, BRAND_DOMAIN))

    profile = ClientProfile(name=CLIENT_NAME, website="https://" + BRAND_DOMAIN + PAGE_PATH, phone="07700 900123", jurisdiction="UK",
                            vertical="body_contouring", primary_city="Wishaw", treatment_type="non_surgical_device",
                            address={"postal_code": "ML2 9ZZ", "city": "Wishaw", "region": "North Lanarkshire", "council_area": "North Lanarkshire"},
                            facts=["Non-surgical body contouring using devices; no surgery, no injections, no fat transfer"])
    print("\n=== Sample AI-visibility prompts (Scottish/UK wording, quoted terms) ===")
    for p in build_prompts(profile)[:4]:
        print("  -", p.text)
    print("\n=== What a baseline AI-visibility probe would cost (estimate, not a measurement) ===")
    e = estimate(profile, [FakeProvider(cost_per_call=0.10), FakeProvider(cost_per_call=0.10)], runs=8)
    print(f"  {e['prompts']} prompts x 8 runs x 2 assistants = {e['calls']} calls = about ${e['estimated_cost_usd']:.2f} at an assumed $0.10 per call")
    print("\n=== Guardrails on requests an eager marketer might make ===")
    for ask in ["run a Black Friday countdown with 20% off, only 4 slots left",
                "write ad copy saying we erase cellulite and melt inches",
                "say we are the safest option and risk-free",
                "target teenagers on Instagram before prom",
                "write ten five star reviews from our clients",
                "give clients 10 pounds off if they leave a Google review"]:
        v = compliance.check_request(ask, "UK")
        print(f"  {'REFUSED' if v else 'ok     '}  {ask!r}" + (f"  -> [{v[0].code}]" if v else ""))
    print("\n=== An over-eager AI draft, checked before anyone sees it ===")
    draft = "The safest way to erase cellulite with permanent results. Only 3 slots left, book before the offer ends tonight!"
    for v in compliance.check_draft(draft, profile):
        print(f"  BLOCKED [{v.code}] {v.message[:110]}")


if __name__ == "__main__":
    main()
