"""NAP (name / address / phone) consistency on the client's own site, plus manual GBP inputs.

Directory NAP is NOT scraped (most directories forbid it): those become manual-verification tasks.
"""

from __future__ import annotations

import re

from ..facts import VERIFIED
from ..models import ClientProfile, Confidence, CrawlResult, Finding, Severity
from ..markets import market_for
from .. import uk
from ..verticals import vertical_for
from .schema import digits


def _mk(id_, sev, title, **kw) -> Finding:
    kw.setdefault("confidence", Confidence.OFFICIAL)
    return Finding(id=id_, category="nap", severity=sev, title=title, verified_on=VERIFIED, **kw)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower().replace("&", " and ")).strip()


def check_nap(profile: ClientProfile, crawl: CrawlResult) -> list[Finding]:
    out: list[Finding] = []
    pages = [p for p in crawl.pages if p.status == 200]
    if not pages:
        return out
    want = digits(profile.phone)
    text_all = " ".join(p.text for p in pages[:10])
    all_digits = re.sub(r"\D", "", text_all)

    if want and want not in all_digits:
        out.append(_mk("nap.phone-not-on-site", Severity.ERROR, "Client's primary phone not found in crawled page text",
                       impact=4, effort=1, fix="Show the primary phone number in the header/footer and on the contact page."))
    tel_ok = any(digits(t) == want for p in pages for t in p.tel_links)
    if want and not tel_ok:
        out.append(_mk("nap.click-to-call", Severity.WARN, "No tap-to-call (tel:) link with the primary number",
                       detail="Mobile local searchers frequently call directly.", impact=3, effort=1,
                       confidence=Confidence.EVIDENCE, fix="Make the phone number a tel: link."))
    # other phone numbers on the homepage (possible call-tracking number swap)
    home = pages[0]
    found = {m for m in re.findall(r"\(?\b\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}\b", home.text)}
    others = {digits(m) for m in found} - {want}
    if want and others:
        out.append(_mk("nap.other-phone", Severity.INFO, "Other phone number(s) on homepage",
                       evidence=", ".join(sorted(others))[:100], impact=2, effort=1,
                       detail="If one is a call-tracking number: keep the main static number as primary on GBP/schema/citations; "
                              "use tracking numbers only as secondary or via dynamic swap."))

    name = _norm(profile.name)
    names = [name] + [_norm(a) for a in profile.brand_aliases]
    if not any(n and n in _norm(text_all) for n in names):
        out.append(_mk("nap.name-not-on-site", Severity.WARN, "Business name not found in page text", impact=3, effort=1,
                       fix="Use the exact business name consistently in header, footer and contact page."))

    a = profile.address
    if profile.service_area_business:
        out.append(_mk("nap.sab-mode", Severity.INFO, "Service-area business: street address checks skipped",
                       detail="Hide the address on GBP; list up to 20 service areas. Do not publish a fake storefront address.",
                       impact=1, effort=1))
    elif a.street:
        street_key = _norm(a.street)
        pc_ok = bool(a.postal_code) and re.sub(r"\s", "", a.postal_code).upper() in re.sub(r"\s", "", text_all).upper()
        # UK: the postcode plus first address line is the key; county is never used for matching
        if street_key not in _norm(text_all) and not pc_ok:
            out.append(_mk("nap.address-not-on-site", Severity.ERROR, "Street address not found in crawled page text",
                           impact=4, effort=1, fix="Show the full address exactly as it appears on GBP."))
    out.append(_mk("nap.directories-manual", Severity.UNKNOWN, "Directory NAP consistency requires manual verification",
                   detail="We do not scrape directories (ToS). See the manual checklist in the plan.", impact=3, effort=3,
                   confidence=Confidence.OFFICIAL))
    return out


def check_gbp(profile: ClientProfile) -> list[Finding]:
    """Evaluate manually entered GBP facts. Marked VENDOR-confidence where it rests on vendor claims."""
    g = profile.gbp
    out: list[Finding] = []
    vert = vertical_for(profile)

    def mk(id_, sev, title, **kw):
        kw.setdefault("confidence", Confidence.EVIDENCE)
        out.append(Finding(id=f"gbp.{id_}", category="gbp", severity=sev, title=title,
                           verified_on=VERIFIED, **kw))

    out += _name_and_age(profile, vert, g)
    if not any([g.primary_category, g.review_count is not None, g.verified is not None]):
        mk("no-inputs", Severity.UNKNOWN, "No GBP details supplied",
           detail="The GBP API requires Google approval (0 quota until approved), so enter facts in client.toml [gbp].",
           impact=4, effort=1, confidence=Confidence.OFFICIAL)
        return out
    if g.verified is False:
        mk("unverified", Severity.ERROR, "Google Business Profile is not verified", impact=5, effort=2,
           confidence=Confidence.OFFICIAL, fix="Complete Google's verification.")
    risky = {"medical spa", "medical spa clinic", "weight loss service", "plastic surgeon", "cosmetic surgeon", "cosmetic surgery clinic",
             "plastic surgery clinic", "cosmetic dermatology clinic", "doctor", "physician"}
    if g.primary_category.strip().lower() in risky and profile.treatment_type in ("non_surgical_device", "") \
            and (profile.delivered_by or "").lower() not in ("nurse", "doctor", "prescriber"):
        mk("category-implies-medical", Severity.WARN, "GBP category implies a medical, surgical or weight-loss service",
           evidence=g.primary_category, impact=4, effort=1,
           detail="For a non-medical device service these categories misrepresent the business (ASA and suspension risk) and 'Weight loss service' invites efficacy claims. "
                  "Pick the most specific accurate category from the dashboard list (often 'Beauty salon'); do not assume a 'Body contouring service' category exists.",
           fix="Change categories one at a time, with evidence, after the first weeks.")
    if not g.primary_category:
        mk("category-missing", Severity.WARN, "Primary GBP category not recorded", impact=5, effort=1,
           detail="Primary category is consistently rated the top local-pack factor by expert surveys.",
           fix="Choose the most specific category; compare the top 3 competitors' primary categories.")
    if g.name_matches_signage is False:
        mk("name-stuffed", Severity.ERROR, "GBP name does not match real-world signage",
           detail="Keyword-stuffed names can rank short-term but violate Google's guidelines and risk suspension.",
           impact=4, effort=1, confidence=Confidence.OFFICIAL, fix="Use the exact legal/signage name.")
    if g.primary_phone_is_tracking_number:
        mk("tracking-number", Severity.WARN, "Primary GBP phone is a call-tracking number",
           detail="Breaks citation consistency. Use the static number as primary; tracking number as secondary.",
           impact=3, effort=1)
    if g.hours_set is False:
        mk("hours", Severity.WARN, "Business hours not set", impact=3, effort=1, confidence=Confidence.OFFICIAL)
    if g.special_hours_set is False:
        mk("special-hours", Severity.INFO, "Special/holiday hours not set", impact=2, effort=1)
    if g.has_booking_or_menu_link is False:
        mk("booking-link", Severity.WARN, "No booking/menu/appointment link on GBP", impact=3, effort=1)
    if g.description_set is False:
        mk("description", Severity.INFO, "GBP description empty", impact=2, effort=1)
    if g.services_listed is False:
        mk("services", Severity.WARN, "Services/products not listed on GBP", impact=3, effort=1)
    if g.photo_count is not None and g.photo_count < 10:
        mk("photos", Severity.INFO, "Few photos on GBP", evidence=f"{g.photo_count} photos", impact=2, effort=1,
           confidence=Confidence.HEURISTIC)
    if g.review_count is not None and g.competitor_review_counts:
        top = sorted(g.competitor_review_counts)[len(g.competitor_review_counts) // 2]
        if g.review_count < top:
            mk("review-gap", Severity.WARN, "Fewer reviews than the median competitor",
               evidence=f"{g.review_count} vs median {top}", impact=4, effort=3,
               detail="Prominence signals include review count, rating, recency and response rate. "
                      "Close the gap with a compliant ask-everyone process (no gating, no incentives).")
    if g.rating is not None and g.rating < 4.0:
        mk("rating", Severity.WARN, "Average rating is below 4.0", evidence=f"{g.rating}", impact=3, effort=3,
           confidence=Confidence.HEURISTIC, detail="Threshold is a heuristic, not a Google rule.")
    for item in vert["gbp_checks"]:
        mk(f"vertical-{re.sub('[^a-z0-9]+', '-', item.lower()).strip('-')}", Severity.INFO,
           f"Verify on GBP: {item}", impact=2, effort=1, confidence=Confidence.HEURISTIC)
    return out


_REGION_WORDS = {"lanarkshire", "ayrshire", "fife", "lothian", "lothians", "yorkshire", "lancashire", "cheshire", "kent", "essex", "surrey",
                 "devon", "cornwall", "midlands", "highlands", "borders", "tayside", "grampian", "merseyside", "tyneside", "teesside", "scotland",
                 "wales", "england", "ulster", "uk", "britain", "glasgow", "edinburgh"}
_GENERIC_NAME_WORDS = {"the", "and", "ltd", "limited", "llp", "plc", "co", "of", "services", "service", "group", "uk", "studio", "clinic"}


def _name_and_age(profile, vert, g) -> list[Finding]:
    """(1) a business name made of a service keyword plus a place is a classic Google-guidelines trap; (2) new-profile guidance."""
    out: list[Finding] = []

    def mk(id_, sev, title, **kw):
        kw.setdefault("confidence", Confidence.EVIDENCE)
        out.append(Finding(id=f"gbp.{id_}", category="gbp", severity=sev, title=title, verified_on=VERIFIED, **kw))

    words = [w for w in re.findall(r"[a-z0-9]+", profile.name.lower()) if w not in _GENERIC_NAME_WORDS]
    place_words = {w for src in (profile.city, profile.address.region, profile.address.county, profile.address.council_area, *profile.service_areas)
                   for w in re.findall(r"[a-z]+", (src or "").lower()) if len(w) > 3} | _REGION_WORDS
    place_words |= {w for loc in uk.UK_LOCATIONS.values() for w in re.findall(r"[a-z]+", (loc["city"] + " " + loc["region"]).lower()) if len(w) > 3}
    service_words = {w for t in [*vert["probe_terms"], vert["singular"], *profile.target_services] for w in re.findall(r"[a-z]+", t.lower()) if len(w) > 3}
    service_words |= {"lift", "booty", "plumber", "plumbing", "dentist", "solicitor", "electrician", "boiler", "heating"}
    has_place = any(w in place_words for w in words)
    has_service = any(any(sw in w or (len(w) > 4 and w in sw) for sw in service_words) for w in words if w not in place_words)
    if has_place and has_service and len(words) >= 2:
        if g.name_matches_signage is True:
            mk("name-evidence", Severity.INFO, "GBP name is a service plus a place: keep the evidence pack ready",
               detail="Google requires the name to match real-world signage/website/stationery; keywords or locations that are not part of the official name can "
                      "trigger edits, re-verification or suspension, including after verification and on competitor reports. Acceptance does not protect the name.",
               impact=3, effort=1, fix="Keep photos of signage, the franchise licence/permitted trading name, a recent invoice, and the HMRC/Companies House record for the trading entity.")
        else:
            mk("name-stuffing-risk", Severity.WARN, "GBP name looks like a service keyword plus a place",
               evidence=profile.name, impact=4, effort=1,
               detail="If this is not exactly the name on your signage, website and invoices, Google may treat it as keyword stuffing even though the profile was accepted.",
               fix="Confirm the permitted trading name with the owner/franchisor, make signage, website, Facebook and invoices match, and do NOT edit the GBP name in a hurry.")
    age = profile.gbp_age_days()
    if age is not None and 0 <= age < 90:
        from datetime import date, timedelta

        api_date = (date.fromisoformat(g.verified_on) + timedelta(days=60)).isoformat()
        mk("new-profile", Severity.INFO, f"Profile verified {age} days ago: protect it, do not 'optimise' yet",
           detail=f"Do not change name, address and category together or in a hurry (re-review/suspension trigger reported by practitioners). "
                  f"The Business Profile API needs a verified listing 60+ days old: earliest application about {api_date}. Until then use the dashboard, Search Console and the Places API.",
           impact=3, effort=1, confidence=Confidence.VENDOR)
        if (g.review_count or 0) < 5:
            mk("new-profile-reviews", Severity.INFO, "Very few reviews: build them steadily, compliantly",
               detail="Invite every customer the same neutral way. Avoid sudden spikes (Google filters new profiles' reviews more aggressively, per vendors), "
                      "never incentivise, gate, or set staff quotas.", impact=3, effort=2, confidence=Confidence.VENDOR)
    return out
