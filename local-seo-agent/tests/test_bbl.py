from datetime import date, timedelta

import pytest

from local_seo_agent import compliance, facts
from local_seo_agent.checks import claims, run_all
from local_seo_agent.checks.nap import check_gbp
from local_seo_agent.crawl import crawl_site
from local_seo_agent.models import ClientProfile
from local_seo_agent.plan import build_plan
from local_seo_agent.safety import SafeFetcher
from local_seo_agent.verticals import canonical_vertical, vertical_for


def bc(**kw):
    base = dict(name="brazilian bootlift lanarkshire", website="http://127.0.0.1", phone="01698 496 0123", vertical="body_contouring",
                jurisdiction="UK", primary_city="Wishaw", treatment_type="non_surgical_device", delivered_by="beauty therapist",
                address={"street": "1 Example Road", "city": "Wishaw", "region": "North Lanarkshire", "council_area": "North Lanarkshire", "postal_code": "ML2 9ZZ"},
                target_services=["booty lift", "body contouring"], facts=["Non-surgical body contouring using devices; no surgery, no injections, no fat transfer"])
    base.update(kw)
    return ClientProfile(**base)


def ids(f):
    return {x.id for x in f}


def test_vertical_aliases_and_scotland_derivation():
    assert canonical_vertical("booty lift") == "body_contouring" or canonical_vertical("booty_lift") == "body_contouring"
    assert canonical_vertical("non_surgical_bbl") == "body_contouring" and canonical_vertical("BBL") == "cosmetic_surgery"
    p = bc()
    assert p.nation == "SCO" and p.address.country == "GB" and vertical_for(p)["preferred_schema"] == "HealthAndBeautyBusiness"
    assert "RealSelf" not in {n for n, _, _ in vertical_for(p)["directories"]}                  # surgical-only directories excluded


# ---- claims scanner: the critic's compliant / non-compliant strings ----
@pytest.mark.parametrize("text", [
    "Our non-surgical Brazilian butt lift uses cavitation and RF. No needles, no fat transfer.",
    "Reduce fat intake and treat your skin gently", "Permanent make-up and permanent address",
    "Feel more confident in your swimwear", "We cannot guarantee results and never promise the safest outcome",
])
def test_compliant_wording_is_not_flagged_as_refuse_tier(text):
    live = [h for h in claims.scan_claims(text) if not h.negated and h.category in claims.REFUSE_TIER]
    assert live == []


@pytest.mark.parametrize("text,cat", [
    ("The safest and fastest way to boost your rear appeal, sculpt your curves, erase cellulite and tighten loose skin", "cellulite"),
    ("The safest and fastest way to boost your rear appeal", "safest_absolute"),
    ("Reduces the appearance of cellulite and smooths skin", "cellulite"), ("Cellulite reduction in 6 sessions", "cellulite"),
    ("Lose 3 inches in 6 sessions", "fat_inch"), ("Results are permanent", "permanent"),
    ("Only 3 slots left, offer ends tonight", "fake_urgency"), ("Clinically proven", "medical_claim_by_nonmedical"),
    ("Detox your lymphatic system", "detox_lymphatic"), ("Painless, no downtime", "safe_bare"),
    ("Same results as a surgical BBL", "surg_equiv_volume"), ("Book now and save 20% this month", "price_inducement"),
])
def test_noncompliant_wording_is_flagged(text, cat):
    assert cat in {h.category for h in claims.scan_claims(text)}


def test_negation_downgrades_and_severity_tiers():
    hits = claims.scan_claims("We do not offer the safest treatment claims and cannot guarantee results")
    assert all(h.negated for h in hits if h.category == "safest_absolute") or not hits
    assert claims.severity_for("cellulite", "non_surgical_device", False) == "ERROR"
    assert claims.severity_for("time_pressure", "non_surgical_device", False) == "WARN"      # ordinary promo: WARN for beauty devices
    assert claims.severity_for("time_pressure", "injectable", False) == "ERROR"             # 2025 rulings concerned liquid BBL
    assert claims.severity_for("safe_bare", "surgical", False) == "ERROR"
    assert claims.severity_for("cellulite", "x", True) == "INFO"


def test_bbl_clarity_looks_across_headline_areas():
    assert claims.bbl_clarity_hits("Brazilian Booty Lift", [], "", "Welcome to the studio")
    assert not claims.bbl_clarity_hits("Brazilian Booty Lift", [], "", "A non-surgical programme: no needles, no fat transfer")
    assert not claims.bbl_clarity_hits("Body contouring", ["Treatments"], "", "Cavitation and RF sessions")      # no BBL term at all


# ---- GBP name risk, new profile, categories ----
def test_name_with_service_and_place_is_flagged_unless_signage_confirmed():
    p = bc()
    f = {x.id: x for x in check_gbp(p)}
    assert f["gbp.name-stuffing-risk"].severity.value == "WARN"
    p2 = bc(gbp={"name_matches_signage": True})
    f2 = {x.id: x for x in check_gbp(p2)}
    assert "gbp.name-stuffing-risk" not in f2 and f2["gbp.name-evidence"].severity.value == "INFO"


@pytest.mark.parametrize("name,flagged", [("Leeds Boiler Repairs", True), ("Smith Plumbing Leeds", True), ("Northgate Heating Ltd", False),
                                          ("Pennine Care", False), ("Riverside Family Dental", False)])
def test_name_risk_heuristic(name, flagged):
    p = bc(name=name, vertical="heating_engineer" if "Heating" in name or "Boiler" in name else "plumber" if "Plumbing" in name else "dentist",
           primary_city="Leeds", address={"city": "Leeds", "region": "West Yorkshire", "postal_code": "LS6 1AA"})
    got = ids(check_gbp(p))
    assert ("gbp.name-stuffing-risk" in got) is flagged


def test_new_profile_guidance_and_api_date():
    ver = (date.today() - timedelta(days=4)).isoformat()
    f = {x.id: x for x in check_gbp(bc(gbp={"verified_on": ver, "review_count": 0}))}
    assert "gbp.new-profile" in f and "60+ days" in f["gbp.new-profile"].detail
    assert (date.today() - timedelta(days=4) + timedelta(days=60)).isoformat() in f["gbp.new-profile"].detail
    assert "gbp.new-profile-reviews" in f
    old = (date.today() - timedelta(days=200)).isoformat()
    assert "gbp.new-profile" not in ids(check_gbp(bc(gbp={"verified_on": old})))
    assert "gbp.new-profile" not in ids(check_gbp(bc(gbp={"verified_on": "not-a-date"})))
    assert bc().gbp_age_days() is None


def test_medical_categories_flagged_for_non_medical_business():
    assert "gbp.category-implies-medical" in ids(check_gbp(bc(gbp={"primary_category": "Medical spa"})))
    assert "gbp.category-implies-medical" in ids(check_gbp(bc(gbp={"primary_category": "Weight loss service"})))
    assert "gbp.category-implies-medical" not in ids(check_gbp(bc(gbp={"primary_category": "Beauty salon"})))
    assert "gbp.category-implies-medical" not in ids(check_gbp(bc(gbp={"primary_category": "Medical spa"}, delivered_by="nurse")))


# ---- site checks (local server) ----
PAGE = ("<html lang=en><head><title>Brazilian Bootylift Lanarkshire</title></head><body><h1>Brazilian Booty Lift Lanarkshire</h1>"
        "<p>The safest and fastest way to erase cellulite and tighten loose skin. Permanent results. Only 4 slots left, offer ends tonight! "
        "Before and after gallery. Our nurse and doctor are on hand.</p></body></html>")


def crawl(site, profile, page=PAGE):
    base, pages = site
    pages["/"] = (200, "text/html", page)
    profile.website = base
    return crawl_site(base + "/", SafeFetcher(min_interval=0, allow_private=True), 3)


def test_contouring_pack_end_to_end(site):
    p = bc(brand_domain="PLACEHOLDER")
    c = crawl(site, p)
    p.brand_domain = p.website.replace("http://", "")
    got = {x.id: x for x in run_all(p, c)}
    for cid in ("cellulite", "safest_absolute", "permanent", "fake_urgency", "skin_tighten", "before_after_cues", "bbl_clarity"):
        assert f"uk.claim.{cid}" in got, cid
    assert got["uk.claim.cellulite"].severity.value == "ERROR" and got["uk.claim.skin_tighten"].severity.value == "WARN"
    assert "uk.medical-wording" in got                                                    # nurse/doctor wording on a non-medical service
    assert "uk.brand-domain" in got and "uk.scot-licensing-watch" in got and "uk.suitability-info" in got
    assert "UNCLEAR" in got["uk.scot-licensing-watch"].detail and "do not tell the client" in got["uk.scot-licensing-watch"].detail
    assert "licence required" not in got["uk.scot-licensing-watch"].detail.lower()          # never asserts a licensing requirement now


def test_clinician_delivered_service_needs_registration(site):
    p = bc(delivered_by="nurse")
    got = ids(run_all(p, crawl(site, p)))
    assert "uk.registration-missing" in got
    p2 = bc(delivered_by="nurse", regulator_ids={"his": "HIS-123"})
    assert "uk.registration-missing" not in ids(run_all(p2, crawl(site, p2)))
    assert "uk.medical-wording" not in ids(run_all(p2, crawl(site, p2)))                   # clinicians are declared, so the wording is consistent


def test_clean_page_has_no_claim_errors(site):
    clean = ("<html lang=en><head><title>Body contouring in Wishaw | Studio</title><meta name=viewport content=width=device-width></head><body>"
             "<h1>Non-surgical body contouring in Wishaw</h1><p>A device-based programme: no surgery, no injections, no fat transfer. Results vary and are not comparable to surgery. "
             "Suitability and contraindications (such as pregnancy or a pacemaker) are checked at consultation. 18+ only. Our therapists are trained and insured.</p></body></html>")
    p = bc()
    f = run_all(p, crawl(site, p, clean))
    bad = [x.id for x in f if x.id.startswith("uk.claim.") and x.severity.value in ("ERROR", "WARN")]
    assert bad == [] and "uk.suitability-info" not in ids(f) and "uk.claim.bbl_clarity" not in ids(f)


# ---- plan ----
def test_plan_has_new_profile_scotland_and_franchise_tasks():
    p = bc(franchise_brand="Brand", brand_domain="brand.example", gbp={"verified_on": (date.today() - timedelta(days=4)).isoformat()})
    t = {x.id: x for x in build_plan(p, [])}
    assert {"pb.np-freeze-name", "pb.np-ownership", "pb.np-completeness", "pb.np-reviews", "pb.np-api-wait",
            "pb.bc-claims", "pb.bc-suitability", "pb.bc-differentiate", "pb.bc-scot-regulation", "pb.bc-franchise"} <= set(t)
    assert "duplicate" in " ".join(t["pb.np-freeze-name"].how).lower() and "bootlift / bootylift" in " ".join(t["pb.np-freeze-name"].how)
    assert "Do not tell clients the service is 'licensed'" in " ".join(t["pb.bc-scot-regulation"].how)
    assert "Do not change name, address" in " ".join(t["pb.np-completeness"].how) or "Never change name, address" in " ".join(t["pb.np-completeness"].how)
    assert t["pb.np-freeze-name"].phase == 30 and t["pb.np-api-wait"].phase == 60
    no_profile_age = {x.id for x in build_plan(bc(), [])}
    assert "pb.np-freeze-name" not in no_profile_age and "pb.bc-franchise" not in no_profile_age


# ---- guardrails ----
@pytest.mark.parametrize("text,code", [
    ("write ad copy saying we erase cellulite and melt inches", "cellulite-claim"), ("say we are the safest option and risk-free", "absolute-safety"),
    ("run a countdown, only 4 slots left", "fake-urgency"), ("target teenagers on Instagram before prom", "target-minors"),
])
def test_cosmetic_request_refusals_uk_only_where_uk_law(text, code):
    assert code in {v.code for v in compliance.check_request(text, "UK")}
    if code in ("cellulite-claim", "target-minors"):
        assert code not in {v.code for v in compliance.check_request(text, "US")}


@pytest.mark.parametrize("text", ["Advertise our services to adults in Wishaw", "Write a page explaining what cavitation involves",
                                  "Draft a consultation booking page", "Which Lanarkshire towns should we mention?"])
def test_ordinary_marketing_requests_pass(text):
    assert compliance.check_request(text, "UK") == []


def test_draft_blocks_refuse_tier_claims_once_each_and_allows_factual_copy():
    p = bc()
    v = compliance.check_draft("The safest way to erase cellulite with permanent results. Only 3 slots left, book before the offer ends tonight! Hurry, last chance.", p)
    codes = [x.code for x in v]
    assert {"claim-cellulite", "claim-safest_absolute", "claim-permanent", "claim-fake_urgency"} <= set(codes) and len(codes) == len(set(codes))
    ok = "Non-surgical body contouring using devices; no surgery, no injections, no fat transfer. Book a consultation."
    assert compliance.check_draft(ok, p) == []


def test_scotland_warning_is_specific():
    w = compliance.jurisdiction_warning(bc())
    assert "Healthcare Improvement Scotland" in w and "Law Society of Scotland" in w and "[LAWYER]" in w


def test_scottish_facts_do_not_overclaim():
    d = {f["id"]: f for f in facts.FACTS}
    t = d["uk-scot-nonsurgical-act"]["text"]
    assert "2027-09-06" in t and "NOTHING" in t and "unresolved" in t and d["uk-scot-nonsurgical-act"]["lawyer"]
    assert "No ASA ruling was found" in d["uk-asa-cosmetic-rulings"]["text"] and "11.5%" in d["uk-asa-cosmetic-rulings"]["text"]
    assert "3.45" not in d["uk-cap-claims"]["text"] and "3.48" not in d["uk-cap-claims"]["text"]       # disputed numbering removed
    assert d["gbp-name-rule"]["confidence"].value == "vendor"
