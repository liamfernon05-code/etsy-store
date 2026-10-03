"""LocalBusiness structured-data checks + a generator built ONLY from client-supplied facts."""

from __future__ import annotations

import json
import re
from typing import Any

from ..facts import VERIFIED
from ..models import ClientProfile, Confidence, CrawlResult, Finding, Severity
from ..markets import market_for
from ..verticals import LOCAL_TYPES, vertical_for

REVIEW_DOC = "https://developers.google.com/search/blog/2019/09/making-review-rich-results-more-helpful"


def _mk(id_, sev, title, **kw) -> Finding:
    kw.setdefault("confidence", Confidence.OFFICIAL)
    return Finding(id=id_, category="schema", severity=sev, title=title, verified_on=VERIFIED, **kw)


def _types(node: dict) -> set[str]:
    t = node.get("@type", [])
    return {t} if isinstance(t, str) else {str(x) for x in t}


def flatten(jsonld: list[dict]) -> list[dict]:
    """Expand @graph containers into a flat list of nodes."""
    nodes: list[dict] = []
    for item in jsonld:
        if isinstance(item.get("@graph"), list):
            nodes.extend(n for n in item["@graph"] if isinstance(n, dict))
        else:
            nodes.append(item)
    return nodes


def digits(s: Any) -> str:
    d = re.sub(r"\D", "", str(s or ""))
    return d[-10:] if len(d) >= 10 else d


def check_schema(profile: ClientProfile, crawl: CrawlResult) -> list[Finding]:
    out: list[Finding] = []
    vert = vertical_for(profile)
    all_nodes: list[dict] = []
    errors = 0
    for p in crawl.pages:
        all_nodes.extend(flatten(p.jsonld))
        errors += p.jsonld_errors
    if errors:
        out.append(_mk("schema.invalid-json", Severity.ERROR, f"{errors} JSON-LD block(s) are not valid JSON",
                       impact=3, effort=1, fix="Validate JSON-LD (trailing commas and unescaped quotes are common)."))
    local = [n for n in all_nodes if _types(n) & LOCAL_TYPES]
    if not local:
        out.append(_mk("schema.no-localbusiness", Severity.WARN, "No LocalBusiness-type structured data found",
                       detail="Structured data is hygiene that helps machines confirm name, address, phone and hours. "
                              "Controlled tests show no citation uplift by itself, so do not expect it to rank you.",
                       impact=3, effort=2, confidence=Confidence.EVIDENCE,
                       fix=f"Add JSON-LD using the most specific type ({vert['preferred_schema']}). "
                           "Run `python -m local_seo_agent schema <client>` to generate it from your facts."))
        return out

    node = local[0]
    types = _types(node)
    if types <= {"LocalBusiness"} and vert["preferred_schema"] != "LocalBusiness":
        out.append(_mk("schema.generic-type", Severity.INFO, "Uses generic LocalBusiness type",
                       detail=f"A more specific subtype exists: {vert['preferred_schema']}.", impact=1, effort=1))

    required = ["name", "telephone", "url", "address"]
    missing = [k for k in required if not node.get(k)]
    if profile.service_area_business and "address" in missing:
        missing.remove("address")
    if missing:
        out.append(_mk("schema.missing-props", Severity.WARN, "LocalBusiness schema is missing key properties",
                       evidence=", ".join(missing), impact=3, effort=1,
                       fix="Add the missing properties with values that match the visible page and your GBP."))
    optional = [k for k in ("openingHoursSpecification", "geo", "sameAs", "image") if not node.get(k)]
    if optional:
        out.append(_mk("schema.missing-optional", Severity.INFO, "Recommended schema properties not present",
                       evidence=", ".join(optional), impact=1, effort=1))

    # NAP consistency inside schema vs profile
    if node.get("telephone") and digits(node["telephone"]) != digits(profile.phone):
        out.append(_mk("schema.phone-mismatch", Severity.ERROR, "Schema phone differs from the client's primary phone",
                       evidence=f"schema {node['telephone']} vs profile {profile.phone}", impact=4, effort=1,
                       detail="NAP inconsistency weakens entity confidence. If a tracking number is used, keep the primary "
                              "static number in schema and on GBP.",
                       fix="Use the same primary number everywhere."))

    # UK: addressCountry should be ISO alpha-2 'GB' (not 'UK')
    if market_for(profile).is_uk and isinstance(node.get("address"), dict):
        ctry = str(node["address"].get("addressCountry", "")).strip()
        if ctry and ctry.upper() not in ("GB", "UNITED KINGDOM"):
            out.append(_mk("schema.country", Severity.WARN, "Schema addressCountry is not 'GB'", evidence=ctry, impact=2, effort=1,
                           fix="Use the ISO 3166-1 alpha-2 code 'GB' (not 'UK')."))

    # self-serving review markup: WARN, never ERROR (no penalty, just no stars)
    if any(("aggregateRating" in n or "review" in n) and (_types(n) & LOCAL_TYPES or "Organization" in _types(n))
           for n in all_nodes):
        out.append(_mk("schema.self-serving-reviews", Severity.WARN,
                       "Review/aggregateRating markup on the business's own site",
                       detail="Google does not show stars for reviews of a business marked up on its own site "
                              "(including third-party widgets). No penalty, no benefit; never copy third-party reviews into markup.",
                       impact=1, effort=1, source_url=REVIEW_DOC,
                       fix="Remove it unless it is for a genuinely eligible item such as a Product."))

    if any("FAQPage" in _types(n) for n in all_nodes):
        out.append(_mk("schema.faq-info", Severity.INFO, "FAQPage markup present",
                       detail="Google ended FAQ rich results on 2026-05-07; harmless but no longer produces a rich result.",
                       confidence=Confidence.VENDOR, impact=1, effort=1))
    return out


def generate_local_business_jsonld(profile: ClientProfile) -> dict:
    """Build JSON-LD only from client-supplied facts. Never adds ratings, awards or invented hours."""
    vert = vertical_for(profile)
    node: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": vert["preferred_schema"],
        "name": profile.name,
        "url": profile.website,
        "telephone": profile.phone,
    }
    a = profile.address
    if a.street and not profile.service_area_business:
        node["address"] = {
            "@type": "PostalAddress", "streetAddress": a.street, "addressLocality": a.city,
            "addressRegion": a.region, "postalCode": a.postal_code, "addressCountry": a.country,
        }
    elif a.city:
        node["address"] = {"@type": "PostalAddress", "addressLocality": a.city,
                           "addressRegion": a.region, "addressCountry": a.country}
    if profile.company_number:
        node["identifier"] = profile.company_number     # Companies House number
    if profile.vat_number:
        node["vatID"] = profile.vat_number
    if profile.service_areas:
        node["areaServed"] = [{"@type": "City", "name": c} for c in profile.service_areas]
    if profile.same_as:
        node["sameAs"] = profile.same_as
    if profile.hours:
        specs = []
        for days, rng in profile.hours.items():
            if "-" in rng and rng.count(":") == 2:
                opens, closes = (x.strip() for x in rng.split("-", 1))
                specs.append({"@type": "OpeningHoursSpecification", "dayOfWeek": days, "opens": opens, "closes": closes})
        if specs:
            node["openingHoursSpecification"] = specs
    return node


def jsonld_script(node: dict) -> str:
    body = json.dumps(node, indent=2, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{body}\n</script>'
