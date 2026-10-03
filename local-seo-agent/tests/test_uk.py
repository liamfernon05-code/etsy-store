import json

import pytest

from local_seo_agent import cli, compliance, facts, uk, uk_data
from local_seo_agent.checks import run_all
from local_seo_agent.checks.schema import generate_local_business_jsonld
from local_seo_agent.crawl import crawl_site
from local_seo_agent.markets import localisation_leak, location_for, market_code, market_for, MARKETS
from local_seo_agent.models import ClientProfile, Confidence
from local_seo_agent.plan import build_plan
from local_seo_agent.probe.prompts import build_prompts
from local_seo_agent.report import render_report
from local_seo_agent.safety import SafeFetcher
from local_seo_agent.verticals import canonical_vertical, vertical_for


def uk_profile(**kw):
    base = dict(name="Northgate Heating Ltd", website="http://127.0.0.1", phone="0113 496 0123",
                vertical="heating_engineer", jurisdiction="UK", primary_city="Leeds",
                address={"street": "12 Example Road", "city": "Leeds", "region": "West Yorkshire",
                         "county": "West Yorkshire", "postal_code": "ls6 1aa"},
                company_number="01234567", sells_gas_services=True, service_area_business=True,
                facts=["Family-run heating engineers covering north Leeds"])
    base.update(kw)
    return ClientProfile(**base)


# ---------------- helpers ----------------
@pytest.mark.parametrize("pc,ok", [("LS1 4AP", True), ("ls14ap", True), ("EH1 1YZ", True), ("GIR 0AA", True), ("BT1 5GS", True),
                                   ("12345", False), ("SW1A", False), ("LS1 4A", False), ("", False)])
def test_postcode_validity(pc, ok):
    assert uk.is_valid_postcode(pc) is ok


@pytest.mark.parametrize("pc,nation", [("LS1 4AP", "ENG"), ("BT1 5GS", "NIR"), ("EH1 1YZ", "SCO"), ("G1 1AA", "SCO"),
                                       ("CF10 1AA", "WAL"), ("TD1 1AA", ""), ("NP20 1AA", ""),   # border areas never guessed
                                       ("JE2 3AB", "CD"), ("GY1 1AA", "CD"), ("IM1 1AA", "CD"), ("nonsense", "")])
def test_nation_from_postcode(pc, nation):
    assert uk.nation_from_postcode(pc) == nation


def test_postcode_normalisation():
    assert uk.normalise_postcode("ls64ab") == "LS6 4AB" and uk.postcode_district("ls6 4ab") == "LS6"


@pytest.mark.parametrize("raw,e164", [("0113 496 0123", "+441134960123"), ("+44 113 496 0123", "+441134960123"),
                                      ("+44 (0)20 7946 0958", "+442079460958"), ("07700 900123", "+447700900123"),
                                      ("0800 123 4567", "+448001234567"), ("(512) 555-0147", "")])
def test_uk_phone_normalisation(raw, e164):
    assert uk.normalise_uk_phone(raw) == e164


def test_phone_kinds():
    assert uk.uk_phone_kind("0113 496 0123") == "geographic" and uk.uk_phone_kind("07700 900123") == "mobile"
    assert uk.uk_phone_kind("0333 123 4567").startswith("03") and uk.uk_phone_kind("0800 123 4567") == "freephone"


def test_directory_registry_statuses():
    assert uk.DIRECTORIES["Rated People"]["status"] == "brand_only_checkatrade_owned"
    assert uk.DIRECTORIES["Scoot"]["status"] == "closing_2026_10" and uk.DIRECTORIES["Factual"]["status"] == "defunct"
    assert uk.DIRECTORIES["Thomson Local"]["status"] == "unverified"
    assert "Angi" in uk.DIRECTORIES["MyBuilder"]["note"]


def test_city_presets_cover_scotland_with_council_areas():
    e = uk.lookup_city("Edinburgh")
    assert e["region"] == "City of Edinburgh" and e["country_name"] == "Scotland"
    assert uk.lookup_city("Newcastle upon Tyne")["city"] == "Newcastle upon Tyne" and uk.lookup_city("nowhere") is None


# ---------------- markets / profile ----------------
def test_market_codes_and_crown_dependencies():
    assert market_code("UK") == "UK" and market_code("gb") == "UK" and market_code("US") == "US" and market_code("DE") == "OTHER"
    assert market_for(uk_profile()).code == "UK"
    assert market_for(uk_profile(jurisdiction="Jersey")).code == "OTHER"
    jersey_pc = uk_profile(address={"postal_code": "JE2 3AB", "city": "St Helier"})
    assert market_for(jersey_pc).code == "OTHER"           # looks like a UK postcode but is not the UK


def test_profile_validator_derives_uk_defaults():
    p = uk_profile()
    assert p.address.country == "GB" and p.address.postal_code == "LS6 1AA" and p.nation == "ENG"
    assert uk_profile(address={"postal_code": "G1 1AA", "city": "Glasgow"}).nation == "SCO"
    assert uk_profile(address={"postal_code": "TD1 1AA", "city": "Galashiels"}).nation == ""   # ambiguous: stay blank
    assert uk_profile(nation="scotland").nation == "SCO"
    assert ClientProfile(name="x", website="x.com", phone="1").address.country == "US"        # US default unchanged


def test_location_for_uk_gb_timezone_and_preset():
    L = location_for(uk_profile())
    assert L["country"] == "GB" and L["timezone"] == "Europe/London" and L["city"] == "Leeds"
    assert L["latitude"] == 53.8008 and L["longitude"] == -1.5491
    scot = location_for(uk_profile(primary_city="Edinburgh", address={"postal_code": "EH1 1YZ", "city": "Edinburgh", "region": "Scotland"}))
    assert scot["region"] == "City of Edinburgh"


def test_localisation_leak_detection():
    assert localisation_leak("Call us, from $120 in Austin TX 78701", MARKETS["UK"])
    assert not localisation_leak("From £120 in Leeds LS6", MARKETS["UK"])
    assert not localisation_leak("$120 in Austin TX 78701", MARKETS["US"])


# ---------------- verticals / prompts ----------------
def test_vertical_aliases_and_uk_overlay():
    assert canonical_vertical("Solicitor") == "lawyer" and canonical_vertical("trades") == "plumber"
    v = vertical_for(uk_profile(vertical="solicitor"))
    assert "solicitor" in v["probe_terms"] and v["singular"] == "solicitor"


def test_uk_directories_by_nation_and_statuses():
    eng = {n for n, _, _ in vertical_for(uk_profile(vertical="dentist"))["directories"]}
    assert "NHS.uk (Find a dentist)" in eng and "CQC" in eng
    sco = {n for n, _, _ in vertical_for(uk_profile(vertical="dentist", address={"postal_code": "EH1 1YZ", "city": "Edinburgh"}))["directories"]}
    assert "NHS inform" in sco and "NHS.uk (Find a dentist)" not in sco and "CQC" not in sco
    law = {n for n, _, _ in vertical_for(uk_profile(vertical="lawyer", address={"postal_code": "BT1 5GS", "city": "Belfast"}))["directories"]}
    assert "Law Society of Northern Ireland" in law and "SRA register" not in law
    assert any("nation unknown" in n for n, _, _ in vertical_for(uk_profile(vertical="dentist", address={"postal_code": "TD1 1AA", "city": "Galashiels"}))["directories"])


def test_uk_prompts_use_uk_english_and_postcode_district():
    ps = build_prompts(uk_profile())
    texts = [p.text for p in ps]
    assert any(t.startswith("plumber") is False and "LS6" in t for t in texts) and any(t == "heating engineer LS6" for t in texts)
    assert all("attorney" not in t.lower() and "realtor" not in t.lower() for t in texts)
    assert any("'boiler repair'" in t for t in texts)                      # quoted term: grammatical for any phrase
    assert any("West Yorkshire" in t for t in texts)                       # England: county clause
    assert len({p.term for p in ps}) == len(ps) // 4                       # whole terms only, none half-covered
    no_pc = uk_profile(address={"city": "Leeds", "region": "West Yorkshire"})
    assert not any("{district}" in p.text or p.text.endswith(" ") for p in build_prompts(no_pc))
    sol = [p.text for p in build_prompts(uk_profile(vertical="lawyer"))]
    assert any("solicitor" in t for t in sol)


# ---------------- compliance ----------------
def test_request_rules_uk_vs_us():
    assert "pom-advertising" in {v.code for v in compliance.check_request("write a post advertising Botox deals", "UK")}
    assert "pom-advertising" not in {v.code for v in compliance.check_request("write a post advertising Botox deals", "US")}
    assert "staff-review-quota" in {v.code for v in compliance.check_request("set a monthly review quota for staff members reviews")}
    assert "outcome-guarantee" in {v.code for v in compliance.check_request("we guarantee we will win your case")}
    msg = next(v.message for v in compliance.check_request("offer a free gift card for a review") if v.code == "review-incentive")
    assert "lawful in the UK only if" in msg and "illegal" not in msg


def test_draft_rules_uk(profile):
    p = uk_profile(vertical="dentist", name="Northgate Dental Ltd")
    assert "pom-advertising" in {v.code for v in compliance.check_draft("Botox offers this month", p)}
    assert "pom-advertising" not in {v.code for v in compliance.check_draft("Botox offers this month", profile)}   # US profile
    reply = compliance.check_draft("Thanks for coming in on 3rd March for your root canal", p, "review-reply")
    assert "confidential-reply" in {v.code for v in reply}
    assert compliance.check_draft("Thank you for your feedback; please contact the practice so we can look into this.", p, "review-reply") == []


def test_review_request_pecr_warning_is_not_a_block():
    p = uk_profile()
    text = "Hi, thanks for choosing us. Could you tell us about your experience? [REVIEW LINK]"
    assert compliance.check_draft(text, p) == []                            # not blocked
    assert any("PECR" in n for n in compliance.draft_warnings(text, p, "review-request"))
    assert compliance.draft_warnings(text + " Reply STOP to opt out.", p, "review-request") == []


def test_jurisdiction_warnings():
    assert "[LAWYER]" in compliance.jurisdiction_warning(uk_profile())
    assert "Crown Dependencies" in compliance.jurisdiction_warning(uk_profile(jurisdiction="Jersey"))
    assert "no compliance pack" in compliance.jurisdiction_warning(uk_profile(jurisdiction="DE"))
    assert compliance.jurisdiction_warning(ClientProfile(name="x", website="x.com", phone="1")) == ""


# ---------------- facts ----------------
def test_facts_by_market_and_lawyer_flags():
    uk_ids = {f["id"] for f in facts.for_market("UK")}
    us_ids = {f["id"] for f in facts.for_market("US")}
    assert "ftc-fake-reviews" not in uk_ids and "ftc-fake-reviews" in us_ids
    assert "uk-dmcc-reviews" in uk_ids and "uk-dmcc-reviews" not in us_ids
    d = {f["id"]: f for f in facts.FACTS}
    assert d["uk-dmcc-reviews"]["lawyer"] and "SI 2015/17" in d["uk-identity"]["text"] and "2008" in d["uk-identity"]["text"]
    assert "unconfirmed" in d["uk-cma-cases"]["text"].lower() or "not confirmed" in d["uk-cma-cases"]["text"].lower()
    assert d["uk-ai-citation-studies"]["confidence"] == Confidence.HEURISTIC          # vendor studies are directional only


# ---------------- UK site checks ----------------
UK_HOME = """<html lang="en-GB"><head><title>Heating engineer in Leeds | Northgate Heating Ltd</title>
<meta name="viewport" content="width=device-width"><link rel="canonical" href="http://{host}/">
<script src="https://www.googletagmanager.com/gtag/js?id=G-1"></script></head><body><h1>Heating engineer in Leeds</h1>
<p>Northgate Heating Ltd. Call <a href="tel:01134960123">0113 496 0123</a>. Gas Safe registered boiler repairs across Leeds LS6.
We rate 5.0 stars. Tradespeople you can trust in Leeds.</p><a href="/contact">Contact</a></body></html>"""


def crawl_uk(site, profile, home=UK_HOME):
    base, pages = site
    pages["/"] = (200, "text/html", home)
    pages["/contact"] = (200, "text/html", "<html><head><title>Contact</title></head><body>Contact Northgate Heating Ltd. Phone 0113 496 0123.</body></html>")
    profile.website = base
    return crawl_site(base + "/", SafeFetcher(min_interval=0, allow_private=True), 5)


def ids(findings):
    return {f.id for f in findings}


def test_uk_checks_identity_privacy_and_badges(site):
    p = uk_profile()
    f = run_all(p, crawl_uk(site, p))
    got = ids(f)
    assert {"uk.company-number-on-site", "uk.email-missing", "uk.privacy-policy", "uk.tracking-tags", "uk.hardcoded-stars",
            "uk.badge-gas_safe"} <= got
    sev = {x.id: x.severity.value for x in f}
    assert sev["uk.tracking-tags"] == "WARN"
    tag = next(x for x in f if x.id == "uk.tracking-tags")
    assert "observed" in tag.detail.lower() and "unlawful" not in tag.detail.lower()   # observed, never "unlawful"
    assert "nap.phone-not-on-site" not in got                                           # UK number matched by last 10 digits


def test_uk_checks_pass_when_compliant(site):
    home = UK_HOME.replace("We rate 5.0 stars.", "").replace(
        "</body>", "<footer>Northgate Heating Ltd, company number 01234567, registered in England and Wales, registered office 1 Example Street, Leeds LS1 4AP. "
        "Email <a href='mailto:hello@northgate.example'>hello@northgate.example</a>. Gas Safe ID 123456. We use cookies: manage your cookie consent. "
        "<a href='/privacy'>Privacy policy</a></footer></body>")
    p = uk_profile(regulator_ids={"gas_safe": "123456"})
    got = ids(run_all(p, crawl_uk(site, p, home)))
    assert not got & {"uk.company-number-on-site", "uk.email-missing", "uk.privacy-policy", "uk.hardcoded-stars",
                      "uk.badge-gas_safe", "uk.gas-safe-id-missing"}
    assert "uk.tracking-tags" in got                                                    # still observed, but INFO because a banner exists


def test_us_profile_gets_no_uk_checks(site, profile):
    base, pages = site
    profile.website = base
    crawl = crawl_site(base + "/", SafeFetcher(min_interval=0, allow_private=True), 3)
    assert not [f for f in run_all(profile, crawl) if f.id.startswith("uk.")]


def test_solicitor_pack_by_nation(site):
    p = uk_profile(vertical="lawyer", name="Smith Solicitors Ltd", regulator_ids={"sra": "654321"})
    got = ids(run_all(p, crawl_uk(site, p)))
    assert {"uk.sra-statement", "uk.sra-number-on-site", "uk.sra-badge", "uk.sra-complaints"} <= got
    sco = uk_profile(vertical="lawyer", address={"postal_code": "EH1 1YZ", "city": "Edinburgh"})
    s_got = ids(run_all(sco, crawl_uk(site, sco)))
    assert "uk.law-nation" in s_got and "uk.sra-statement" not in s_got                # SRA rules do not apply in Scotland


def test_dentist_cqc_check_only_when_rating_supplied(site):
    p = uk_profile(vertical="dentist", name="Northgate Dental Ltd")
    got = ids(run_all(p, crawl_uk(site, p)))
    assert "uk.cqc-skipped" in got and "uk.cqc-display" not in got                      # most dentists have no CQC rating
    p2 = uk_profile(vertical="dentist", name="Northgate Dental Ltd", regulator_ids={"cqc_rating": "Good"})
    assert "uk.cqc-display" in ids(run_all(p2, crawl_uk(site, p2)))
    sco = uk_profile(vertical="dentist", regulator_ids={"cqc_rating": "Good"}, address={"postal_code": "EH1 1YZ", "city": "Edinburgh"})
    assert "uk.cqc-display" not in ids(run_all(sco, crawl_uk(site, sco)))               # CQC is England only


def test_restaurant_and_aesthetics_packs(site):
    p = uk_profile(vertical="restaurant", name="Northgate Kitchen Ltd", address={"postal_code": "CF10 1AA", "city": "Cardiff"})
    got = ids(run_all(p, crawl_uk(site, p)))
    assert "uk.fhrs-mandatory" in got and "uk.allergens" in got                         # Wales: display mandatory
    salon = uk_profile(vertical="salon", name="Glow Ltd", is_aesthetics=True)
    home = UK_HOME.replace("Gas Safe registered boiler repairs", "Botox and Dysport anti-wrinkle treatments")
    f = run_all(salon, crawl_uk(site, salon, home))
    assert "uk.pom-brand" in ids(f)


def test_postcode_and_nation_findings():
    from local_seo_agent.checks.uk_checks import check_uk
    from local_seo_agent.models import CrawlResult

    bad = uk_profile(address={"postal_code": "12345", "city": "Leeds"})
    got = ids(check_uk(bad, CrawlResult(start_url="x")))
    assert "uk.postcode-invalid" in got and "uk.nation-unknown" in got
    mob = uk_profile(phone="07700 900123")
    assert "uk.phone-mobile" in ids(check_uk(mob, CrawlResult(start_url="x")))


def test_schema_country_and_generator_uk():
    node = generate_local_business_jsonld(uk_profile(service_area_business=False))
    assert node["address"]["addressCountry"] == "GB" and node["address"]["postalCode"] == "LS6 1AA"
    assert node["identifier"] == "01234567" and "aggregateRating" not in node and "priceRange" not in node


def test_uk_nap_postcode_match_ignores_spaces_and_county(site):
    p = uk_profile(service_area_business=False, address={"street": "99 Different Lane", "city": "Leeds", "county": "Yorkshire", "postal_code": "ls61aa"})
    home = UK_HOME.replace("Leeds LS6.", "Leeds, LS6 1AA.")
    f = run_all(p, crawl_uk(site, p, home))
    assert "nap.address-not-on-site" not in ids(f)


# ---------------- plan / report ----------------
def test_uk_plan_playbook(site):
    p = uk_profile()
    tasks = {t.id: t for t in build_plan(p, [])}
    assert {"pb.uk-registers", "pb.uk-identity", "pb.uk-apple-bing", "pb.uk-consent", "pb.uk-trades-directories", "pb.lsa"} <= set(tasks)
    review = " ".join(tasks["pb.review-engine"].how)
    assert "DMCC" in review and "PECR" in review and "never proposes" in review and "illegal" not in review
    nap = " ".join(tasks["pb.nap-directories"].how)
    assert "Scoot" not in nap and "Rated People" not in nap and "Checkatrade" not in nap      # closed / brand-only / paid marketplaces excluded
    sol = {t.id for t in build_plan(uk_profile(vertical="lawyer", primary_city="Leeds"), [])}
    assert "pb.lsa" not in sol and "pb.uk-solicitor" in sol                                   # legal LSAs: Greater London only
    assert "pb.lsa" in {t.id for t in build_plan(uk_profile(vertical="lawyer", primary_city="London"), [])}


def test_uk_report_renders_banner_facts_and_escapes(site):
    p = uk_profile(name="Northgate <b>Heating</b> Ltd")
    crawl = crawl_uk(site, p)
    f = run_all(p, crawl)
    html = render_report(p, crawl, f, build_plan(p, f))
    assert "[LAWYER]" in html and "Digital Markets, Competition and Consumers Act" in html
    assert "FTC 16 CFR 465" not in html and "<b>Heating</b>" not in html and "&lt;b&gt;" in html


# ---------------- adapters ----------------
class _Res:
    def __init__(self, status, text):
        self.status, self.text = status, text


class _FakeFetcher:
    def __init__(self, status, body):
        self.status, self.body, self.user_agent = status, body, "t"

    def _get(self, url):
        self.url = url
        return _Res(self.status, self.body)


def test_resolve_postcode_parses_postcodes_io():
    body = json.dumps({"status": 200, "result": {"country": "Scotland", "latitude": 55.95, "longitude": -3.19,
                                                  "admin_district": "City of Edinburgh", "region": None}})
    f = _FakeFetcher(200, body)
    out = uk_data.resolve_postcode(f, "eh11yz")
    assert out == {"nation": "SCO", "latitude": 55.95, "longitude": -3.19, "council_area": "City of Edinburgh"}
    assert f.url.endswith("EH1%201YZ")
    assert uk_data.resolve_postcode(_FakeFetcher(404, "{}"), "EH1 1YZ") == {} and uk_data.resolve_postcode(f, "bad") == {}


def test_company_findings():
    p = uk_profile(registered_office="1 Example Street, Leeds, LS1 4AP")
    ok = {"company_name": "NORTHGATE HEATING LTD", "company_status": "active", "jurisdiction": "england-wales",
          "registered_office_address": {"postal_code": "LS1 4AP"}}
    assert [f.id for f in uk_data.company_findings(p, ok)] == ["uk.ch.jurisdiction"]
    dead = {**ok, "company_status": "dissolved"}
    f = {x.id: x for x in uk_data.company_findings(p, dead)}
    assert f["uk.ch.not-active"].severity.value == "ERROR"
    moved = {**ok, "registered_office_address": {"postal_code": "M1 1AA"}}
    assert "uk.ch.office-differs" in {x.id for x in uk_data.company_findings(p, moved)}
    assert uk_data.company_findings(p, {})[0].id == "uk.ch.not-found"


def test_fetch_company_uses_basic_auth_and_validates(monkeypatch):
    seen = {}

    class R:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"company_status": "active"}

    import httpx
    from local_seo_agent import safety

    monkeypatch.setattr(safety, "validate_url", lambda url, *a, **k: ("https", "x", 443, ["93.184.216.34"]))
    monkeypatch.setattr(httpx, "get", lambda url, **kw: (seen.update(url=url, **kw), R())[1])
    out = uk_data.fetch_company(SafeFetcher(min_interval=0), "01234567", "KEY123")
    assert out == {"company_status": "active"} and seen["url"].endswith("/01234567")
    import base64
    assert seen["headers"]["Authorization"] == "Basic " + base64.b64encode(b"KEY123:").decode()
    with pytest.raises(ValueError):
        uk_data.fetch_company(SafeFetcher(min_interval=0), "../../etc", "K")


# ---------------- CLI ----------------
def test_cli_uk_end_to_end(site, tmp_path, monkeypatch, capsys):
    base, pages = site
    pages["/"] = (200, "text/html", UK_HOME)
    monkeypatch.setattr(cli, "SafeFetcher", lambda **kw: SafeFetcher(allow_private=True, **kw))
    monkeypatch.setattr(uk_data, "resolve_postcode", lambda f, pc: {"nation": "ENG", "latitude": 53.81, "longitude": -1.56, "council_area": "Leeds"})
    home = str(tmp_path)
    assert cli.main(["--home", home, "init", "uk1", "--market", "uk"]) == 0
    toml = tmp_path / "uk1" / "client.toml"
    text = toml.read_text().replace("https://www.example-heating.co.uk", base)
    assert 'jurisdiction = "UK"' in text and 'vertical = "heating_engineer"' in text
    toml.write_text(text)
    assert cli.main(["--home", home, "resolve", "uk1"]) == 0
    assert json.loads((tmp_path / "uk1" / "resolved.json").read_text())["council_area"] == "Leeds"
    assert cli.main(["--home", home, "audit", "uk1", "--delay", "0", "--max-pages", "3"]) == 0
    assert any(x["id"].startswith("uk.") for x in json.loads((tmp_path / "uk1" / "audit.json").read_text()))
    assert cli.main(["--home", home, "probe", "uk1", "--provider", "fake", "--runs", "2", "--wave", "w1", "--budget", "1"]) == 0
    assert cli.main(["--home", home, "plan", "uk1"]) == 0 and cli.main(["--home", home, "report", "uk1"]) == 0
    html = (tmp_path / "uk1" / "report.html").read_text()
    assert "UK:" in html and "US-context answers" in html
    assert cli.main(["--home", home, "guard", "--market", "uk", "advertise botox offers"]) == 2
    assert cli.main(["--home", home, "guard", "--market", "us", "advertise botox offers"]) == 0
