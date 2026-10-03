"""UK audit checks (run only for the UK market). Everything a crawler can test with reasonable reliability; where a
legal conclusion would be needed we report what was OBSERVED, never "unlawful". Items needing a human lawyer say so.

Rule sources: research/uk/U1-uk-law.md and critique-U1.md. Law and policy here change often: each finding carries
`verified_on` and the reference facts in facts.py carry their own dates. This is not legal advice.
"""

from __future__ import annotations

import re

from .. import uk
from ..facts import VERIFIED
from ..markets import market_for
from ..models import ClientProfile, Confidence, CrawlResult, Finding, Severity
from ..verticals import canonical_vertical
from .schema import digits

POM_BRANDS = re.compile(r"\b(botox|dysport|azzalure|bocouture|vistabel|botulinum)\b|#botox", re.I)
ANALYTICS_HOSTS = ("googletagmanager.com", "google-analytics.com", "connect.facebook.net", "facebook.net", "hotjar.com",
                   "static.hotjar.com", "clarity.ms", "doubleclick.net", "googleadservices.com", "snap.licdn.com",
                   "analytics.tiktok.com", "tiktok.com", "px.ads.linkedin.com", "callrail.com", "calltrackingmetrics.com")
TRADE_BADGES = {
    "gas safe": ("gas_safe", "Gas Safe"), "trustmark": ("trustmark", "TrustMark"), "niceic": ("niceic", "NICEIC"),
    "napit": ("napit", "NAPIT"), "checkatrade": ("checkatrade", "Checkatrade"),
    "which? trusted trader": ("which_trusted_trader", "Which? Trusted Trader"),
}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
VAT_RE = re.compile(r"VAT\s*(?:reg(?:istration)?\.?\s*)?(?:no|number)?\.?:?\s*(?:GB)?\s?\d{3}\s?\d{4}\s?\d{2}", re.I)
COMPANY_NO_RE = re.compile(r"(company|registered)\s*(?:no|number|reg)\.?[:\s#]*\s*(?:SC|NI|OC|SO|NC|R)?\s?\d{6,8}", re.I)
REGISTERED_IN_RE = re.compile(r"registered in\s+(england and wales|england|wales|scotland|northern ireland)", re.I)
LTD_RE = re.compile(r"\b(ltd|limited|llp|plc)\b\.?", re.I)
STARS_RE = re.compile(r"\b5(?:\.0)?\s*(?:/\s*5|stars?)\b", re.I)


def _mk(id_, sev, title, **kw) -> Finding:
    kw.setdefault("confidence", Confidence.EVIDENCE)
    return Finding(id=f"uk.{id_}", category="uk-compliance", severity=sev, title=title, verified_on=VERIFIED, **kw)


def _text(crawl: CrawlResult, n: int = 15) -> str:
    return " ".join(p.text for p in crawl.pages[:n] if p.status == 200)


def _has_link(crawl: CrawlResult, needle: str) -> bool:
    return any(needle in h for p in crawl.pages for h in p.external_hosts) or any(
        needle in l for p in crawl.pages for l in p.internal_links)


def check_uk(profile: ClientProfile, crawl: CrawlResult) -> list[Finding]:
    m = market_for(profile)
    if not m.is_uk:
        return []
    out: list[Finding] = []
    pages = [p for p in crawl.pages if p.status == 200]
    text = _text(crawl)
    low = text.lower()
    vkey = canonical_vertical(profile.vertical)
    nation = profile.nation

    # ---- address / phone / nation hygiene (no crawl needed) ----
    pc = profile.address.postal_code
    if pc and not uk.is_valid_postcode(pc):
        out.append(_mk("postcode-invalid", Severity.WARN, "Client postcode is not a valid UK postcode",
                       evidence=pc, impact=3, effort=1, confidence=Confidence.OFFICIAL,
                       fix="Use the full postcode, e.g. 'LS1 4AP'. Jersey (JE), Guernsey (GY) and Isle of Man (IM) postcodes are not UK."))
    if not nation:
        out.append(_mk("nation-unknown", Severity.UNKNOWN, "UK nation not determined",
                       detail="Regulators and display rules differ across England, Scotland, Wales and Northern Ireland "
                              "(SRA, CQC, FHRS/FHIS). Border postcode areas are never guessed.",
                       impact=3, effort=1, fix="Set `nation` (ENG/WAL/SCO/NIR) in client.toml, or run `resolve` to look it up via postcodes.io."))
    if profile.phone:
        kind = uk.uk_phone_kind(profile.phone)
        if kind == "unknown":
            out.append(_mk("phone-format", Severity.WARN, "Primary phone is not a recognisable UK number",
                           evidence=profile.phone, impact=2, effort=1,
                           fix="Use a UK number (national or +44 format) as the primary on the site, GBP and citations."))
        elif kind == "mobile":
            out.append(_mk("phone-mobile", Severity.INFO, "Primary phone is a mobile (07) number",
                           detail="A local geographic number may read as more local; keep one primary number everywhere.",
                           impact=1, effort=1, confidence=Confidence.HEURISTIC))
        elif kind.startswith("03"):
            out.append(_mk("phone-03", Severity.INFO, "Primary phone is an 03 number",
                           detail="03 numbers are common for call tracking. Google wants a local number as the primary GBP "
                                  "number, with tracking numbers as additional.", impact=1, effort=1,
                           confidence=Confidence.HEURISTIC))

    if not pages:
        return out

    # ---- business identity: UK-ID-01/04 ----
    is_company = bool(profile.company_number) or bool(LTD_RE.search(profile.registered_name or profile.name))
    if is_company:
        if not profile.company_number:
            out.append(_mk("company-number-missing", Severity.UNKNOWN, "Looks like a limited company but no company number supplied",
                           impact=2, effort=1, fix="Add `company_number` to client.toml so identity and status can be checked."))
        else:
            cn = re.sub(r"\s", "", profile.company_number)
            if cn.lower() not in re.sub(r"\s", "", text).lower():
                out.append(_mk("company-number-on-site", Severity.WARN, "Company number not found on the crawled pages",
                               detail="Limited companies must show their registered name, number, place of registration and "
                                      "registered office on the website (SI 2015/17). Image-only footers are not detected.",
                               impact=3, effort=1, confidence=Confidence.OFFICIAL,
                               fix="Add a footer or legal page: registered name, company number, 'Registered in <nation>', registered office."))
            if not REGISTERED_IN_RE.search(text):
                out.append(_mk("registered-in", Severity.INFO, "'Registered in England and Wales / Scotland / Northern Ireland' not found",
                               impact=2, effort=1))
    has_email = any(p.emails for p in pages) or bool(EMAIL_RE.search(text))
    if not has_email:
        out.append(_mk("email-missing", Severity.WARN, "No email address found on the site",
                       detail="E-Commerce Regulations 2002 reg 6: an email address (not just a contact form) should be easily accessible.",
                       impact=2, effort=1, confidence=Confidence.OFFICIAL))
    if profile.vat_number and re.sub(r"\D", "", profile.vat_number)[-9:] not in re.sub(r"\D", "", text):
        out.append(_mk("vat-missing", Severity.WARN, "VAT number (supplied) not found on the site", impact=2, effort=1,
                       confidence=Confidence.OFFICIAL, fix="Show the VAT registration number if the business is VAT-registered."))

    # ---- privacy / cookies (observed, never 'unlawful') ----
    if not any("privacy" in l.lower() for p in pages for l in p.internal_links):
        out.append(_mk("privacy-policy", Severity.WARN, "No privacy policy link found", impact=3, effort=1,
                       confidence=Confidence.OFFICIAL, detail="UK GDPR requires a privacy notice where personal data is collected (forms, calls, tracking)."))
    tags = sorted({h for p in pages for h in p.script_hosts if any(h == a or h.endswith("." + a) for a in ANALYTICS_HOSTS)})
    if tags:
        banner = any(w in low for w in ("cookie", "consent", "manage preferences"))
        out.append(_mk("tracking-tags", Severity.WARN if not banner else Severity.INFO,
                       "Analytics/advertising tags observed" + ("" if banner else " and no cookie/consent wording found"),
                       evidence=", ".join(tags)[:150], impact=3, effort=2, confidence=Confidence.HEURISTIC,
                       detail="PECR (UK): non-essential tags (ads, remarketing, call tracking; GA4 in default configuration "
                              "likely does not meet the statistical exemption) generally need prior opt-in. This crawl cannot "
                              "tell whether tags fire before consent; observed only. [LAWYER] for consent design."))

    # ---- review/rating presentation (DMCC) ----
    if STARS_RE.search(text) and not any(h in ("trustpilot.com", "google.com", "feefo.com", "reviews.io", "checkatrade.com")
                                         for p in pages for h in p.external_hosts):
        out.append(_mk("hardcoded-stars", Severity.WARN, "Star rating shown without a link to the review source",
                       detail="DMCC Act 2024: displayed ratings must come from all genuine reviews and name their source. "
                              "Hard-coded or cherry-picked ratings are risky.", impact=2, effort=1,
                       confidence=Confidence.HEURISTIC, fix="Show the live rating from the named platform, with a link."))

    # ---- aesthetics / prescription-only medicines (CAP 12.12) ----
    if (profile.is_aesthetics or vkey in ("salon", "dentist")) and POM_BRANDS.search(text):
        out.append(_mk("pom-brand", Severity.WARN, "Prescription-only medicine brand named in public website copy",
                       detail="CAP 12.12: prescription-only medicines such as Botox/Dysport/Azzalure cannot be advertised to the "
                              "public, including indirect promotion. Use 'anti-wrinkle consultation'. [LAWYER] for exact limits.",
                       evidence=POM_BRANDS.search(text).group(0), impact=4, effort=1, confidence=Confidence.EVIDENCE))

    # ---- trust marks without supplied registration (CAP 3.50) ----
    for needle, (key, label) in TRADE_BADGES.items():
        if needle in low and not profile.regulator_ids.get(key):
            out.append(_mk(f"badge-{key}", Severity.WARN, f"'{label}' claimed on the site but no registration ID supplied",
                           detail="CAP 3.50: trust marks need authorisation. Verify on the public register; this tool cannot.",
                           impact=3, effort=1, confidence=Confidence.OFFICIAL,
                           fix=f"Add the {label} registration number to client.toml [client.regulator_ids] and show it on the page."))
    if vkey in ("plumber", "heating_engineer") and profile.sells_gas_services:
        gid = profile.regulator_ids.get("gas_safe", "")
        if not gid:
            out.append(_mk("gas-safe-id-missing", Severity.WARN, "Gas work offered but no Gas Safe ID supplied", impact=4, effort=1,
                           confidence=Confidence.OFFICIAL, fix="Gas work must be done by a Gas Safe registered business: supply the ID."))
        elif re.sub(r"\D", "", gid) not in re.sub(r"\D", "", text):
            out.append(_mk("gas-safe-id-on-site", Severity.INFO, "Gas Safe ID not shown on the crawled pages", impact=2, effort=1,
                           confidence=Confidence.HEURISTIC))

    # ---- sector packs ----
    if vkey == "lawyer":
        out += _solicitor(profile, pages, text, low, nation)
    elif vkey == "dentist":
        out += _dentist(profile, pages, text, low, nation)
    elif vkey == "restaurant":
        out += _restaurant(pages, low, nation)
    return out


def _solicitor(profile, pages, text, low, nation) -> list[Finding]:
    out: list[Finding] = []
    if nation in ("SCO", "NIR"):
        out.append(_mk("law-nation", Severity.INFO, "SRA rules do not apply in Scotland / Northern Ireland",
                       detail="Check the Law Society of Scotland / Law Society of Northern Ireland rules instead; not built into this tool. [LAWYER]",
                       impact=2, effort=1, confidence=Confidence.OFFICIAL))
        return out
    if not nation:
        return out
    if "solicitors regulation authority" not in low:
        out.append(_mk("sra-statement", Severity.WARN, "'Authorised and regulated by the Solicitors Regulation Authority' not found",
                       impact=4, effort=1, confidence=Confidence.OFFICIAL, source_url="https://www.sra.org.uk/solicitors/standards-regulations/transparency-rules/"))
    sra = profile.regulator_ids.get("sra", "")
    if not sra:
        out.append(_mk("sra-number-missing", Severity.UNKNOWN, "SRA number not supplied", impact=2, effort=1))
    elif re.sub(r"\D", "", sra) not in re.sub(r"\D", "", text):
        out.append(_mk("sra-number-on-site", Severity.WARN, "SRA number not found on the crawled pages", impact=3, effort=1, confidence=Confidence.OFFICIAL))
    if not _has_link(_Crawl(pages), "sra.org.uk"):
        out.append(_mk("sra-badge", Severity.WARN, "No link to sra.org.uk (SRA digital badge) found", impact=3, effort=1,
                       confidence=Confidence.OFFICIAL, detail="Transparency Rules: show the clickable SRA digital badge."))
    if "complaint" not in low:
        out.append(_mk("sra-complaints", Severity.WARN, "No complaints information found", impact=3, effort=1,
                       confidence=Confidence.OFFICIAL, detail="Transparency Rules: complaints procedure incl. Legal Ombudsman route."))
    if re.search(r"conveyancing|probate|employment tribunal|immigration|licensing", low) and "£" not in text:
        out.append(_mk("sra-price-info", Severity.INFO, "Price/service information not detected for transparency-rule areas",
                       detail="Required areas: conveyancing, probate, immigration (non-asylum), employment tribunal, some motoring "
                              "offences, business debt recovery up to GBP 100k, licensing. Heuristic: no '£' found. [LAWYER]",
                       impact=3, effort=2, confidence=Confidence.HEURISTIC))
    return out


class _Crawl:  # tiny adapter so _has_link can run on a page list
    def __init__(self, pages):
        self.pages = pages


def _dentist(profile, pages, text, low, nation) -> list[Finding]:
    out: list[Finding] = []
    if not re.search(r"GDC\s*(?:no|number|reg(?:istration)?)?\.?[:\s#]*\d{6}", text, re.I):
        out.append(_mk("gdc-numbers", Severity.INFO, "No GDC registration numbers detected on team pages",
                       detail="GDC advertising guidance: show each dental professional's GDC number and qualifications.",
                       impact=2, effort=1, confidence=Confidence.EVIDENCE))
    rating = profile.regulator_ids.get("cqc_rating", "")
    if nation == "ENG" and rating:
        shown = rating.lower() in low and _has_link(_Crawl(pages), "cqc.org.uk")
        if not shown:
            out.append(_mk("cqc-display", Severity.WARN, "CQC rating (supplied) not displayed with a link to cqc.org.uk",
                           detail="CQC regulation 20A: rated providers must display their rating on their website (England).",
                           impact=3, effort=1, confidence=Confidence.OFFICIAL))
    else:
        out.append(_mk("cqc-skipped", Severity.INFO, "CQC rating-display check skipped",
                       detail="Reg 20A applies to providers that hold a CQC rating (England). Primary dental care is generally "
                              "not rated: supply `cqc_rating` in regulator_ids only if the CQC register shows one.",
                       impact=1, effort=1))
    return out


def _restaurant(pages, low, nation) -> list[Finding]:
    out: list[Finding] = []
    shows = "food hygiene" in low or any("food.gov.uk" in h for p in pages for h in p.external_hosts)
    if nation in ("WAL", "NIR") and not shows:
        out.append(_mk("fhrs-mandatory", Severity.WARN, "Food hygiene rating not displayed (mandatory in Wales and Northern Ireland)",
                       impact=3, effort=1, confidence=Confidence.OFFICIAL, detail="Display applies at the premises; showing it online is best practice."))
    elif nation in ("ENG", "SCO") and not shows:
        out.append(_mk("fhrs-voluntary", Severity.INFO, "Food hygiene rating not shown online (display is voluntary here)",
                       detail="Scotland uses FHIS (Pass / Improvement Required), not 0-5.", impact=1, effort=1))
    if "allerg" not in low:
        out.append(_mk("allergens", Severity.WARN, "No allergen information or notice found", impact=3, effort=1,
                       confidence=Confidence.OFFICIAL, detail="Menus/online ordering should point to allergen information (14 allergens). Never claim 'allergen-free'."))
    return out
