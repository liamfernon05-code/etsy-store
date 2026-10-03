import json

from local_seo_agent.checks import run_all
from local_seo_agent.checks.schema import generate_local_business_jsonld, jsonld_script
from local_seo_agent.crawl import crawl_site
from local_seo_agent.html_parse import parse_html
from local_seo_agent.psi import psi_findings
from local_seo_agent.safety import SafeFetcher

from conftest import ROBOTS_BLOCKING


def _crawl(base, pages=25):
    return crawl_site(base + "/", SafeFetcher(min_interval=0, allow_private=True), pages)


def ids(findings):
    return {f.id for f in findings}


def test_parse_html_extracts_fields():
    p = parse_html("http://x.test/", """<html lang=en><head><title> T  </title><meta name=description content=d>
    <link rel=canonical href="/c"><script type="application/ld+json">{"@type":"Dentist"}</script>
    <script type="application/ld+json">{bad json</script></head><body><h1>H</h1><a href="tel:+15125550147">c</a>
    <a href="/a#frag">a</a><a href="mailto:x@y.z">m</a><img src=a><img src=b alt="ok"><script>var x=1</script></body></html>""")
    assert p.title == "T" and p.meta_description == "d" and p.h1 == ["H"] and p.lang == "en"
    assert p.jsonld == [{"@type": "Dentist"}] and p.jsonld_errors == 1
    assert p.tel_links == ["+15125550147"] and p.internal_links == ["http://x.test/a"]
    assert p.images == 2 and p.images_missing_alt == 1 and "var x" not in p.text


def test_crawl_finds_pages_and_sitemap(site):
    base, _ = site
    c = _crawl(base)
    assert len(c.pages) == 3 and c.sitemap_url_count == 2 and c.robots_status == 200


def test_good_site_has_no_errors_except_unknowns(site, profile):
    base, _ = site
    profile.website = base
    f = run_all(profile, _crawl(base))
    errors = [x for x in f if x.severity.value == "ERROR"]
    assert [e.id for e in errors] == ["tech.https"]         # local test server is plain http; nothing else is an error
    assert "schema.self-serving-reviews" in ids(f)          # WARN, not ERROR
    sev = {x.id: x.severity.value for x in f}
    assert sev["schema.self-serving-reviews"] == "WARN"
    assert "crawl.waf-unknown" in ids(f)                    # honest about what we cannot see


def test_ai_crawler_block_is_error(site, profile):
    base, pages = site
    pages["/robots.txt"] = (200, "text/plain", ROBOTS_BLOCKING)
    profile.website = base
    f = run_all(profile, _crawl(base))
    assert "crawl.blocked.OAI-SearchBot" in ids(f)
    assert "crawl.blocked.Googlebot" not in ids(f)
    gpt = next(x for x in f if x.id == "crawl.training-blocked")
    assert gpt.severity.value == "INFO" and "GPTBot" in gpt.title      # training bots: owner's choice


def test_noindex_and_js_shell(site, profile):
    base, pages = site
    pages["/"] = (200, "text/html", "<html><head><title>x</title><meta name=robots content='noindex'>"
                  "<script src=a></script><script src=b></script><script src=c></script></head><body><div id=root></div></body></html>")
    profile.website = base
    f = ids(run_all(profile, _crawl(base)))
    assert {"crawl.noindex-home", "crawl.js-shell"} <= f


def test_phone_mismatch_in_schema(site, profile):
    base, pages = site
    pages["/"] = (200, "text/html", pages["/"][2].replace("512-555-0147", "737-555-0000"))
    profile.website = base
    assert "schema.phone-mismatch" in ids(run_all(profile, _crawl(base)))


def test_missing_schema_and_nap(site, profile):
    base, pages = site
    pages["/"] = (200, "text/html", "<html lang=en><head><title>Home</title></head><body><h1>Welcome</h1></body></html>")
    pages["/contact"] = (404, "text/html", "no")
    profile.website = base
    f = ids(run_all(profile, _crawl(base)))
    assert {"schema.no-localbusiness", "nap.phone-not-on-site", "nap.address-not-on-site", "tech.city-in-title"} <= f


def test_sab_skips_address_check(site, profile):
    base, pages = site
    pages["/"] = (200, "text/html", "<html lang=en><head><title>Austin plumber</title></head><body><h1>Austin</h1>"
                  "<a href='tel:5125550147'>(512) 555-0147</a> Riverside Family Dental</body></html>")
    profile.website = base
    profile.service_area_business = True
    f = ids(run_all(profile, _crawl(base)))
    assert "nap.address-not-on-site" not in f and "nap.sab-mode" in f


def test_gbp_inputs(profile):
    from local_seo_agent.checks.nap import check_gbp

    profile.gbp = profile.gbp.model_copy(update={"verified": False, "name_matches_signage": False, "review_count": 10,
                                                  "competitor_review_counts": [100, 200, 300]})
    f = {x.id: x for x in check_gbp(profile)}
    assert f["gbp.unverified"].severity.value == "ERROR" and f["gbp.name-stuffed"].severity.value == "ERROR"
    assert f["gbp.review-gap"].severity.value == "WARN"


def test_gbp_no_inputs_is_unknown(profile):
    from local_seo_agent.checks.nap import check_gbp

    assert [x.severity.value for x in check_gbp(profile)] == ["UNKNOWN"]


def test_jsonld_generator_uses_only_supplied_facts(profile):
    node = generate_local_business_jsonld(profile)
    assert node["@type"] == "Dentist" and "aggregateRating" not in node and "review" not in node
    assert "openingHoursSpecification" not in node          # none supplied -> none invented
    profile.service_area_business = True
    assert "streetAddress" not in generate_local_business_jsonld(profile)["address"]
    html = jsonld_script({"name": "</script><script>alert(1)</script>"})
    assert "</script><script>" not in html and json.loads(html.split("\n", 1)[1].rsplit("\n", 1)[0].replace("<\\/", "</"))


def test_psi_unknown_when_no_field_data():
    f = psi_findings({"lighthouseResult": {"categories": {"performance": {"score": 0.5}}}})
    assert {x.id: x.severity.value for x in f}["psi.no-field-data"] == "UNKNOWN"


def test_psi_flags_slow_lcp_and_cls_scaling():
    data = {"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 4000},
                                               "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 5}}}}
    f = {x.id for x in psi_findings(data)}
    assert "psi.lcp" in f and "psi.cls" not in f         # CLS 5 == 0.05 which is good
