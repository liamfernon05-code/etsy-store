"""Deterministic 30/60/90-day plan: audit findings + a local-business playbook, ranked by impact x confidence / effort.

Every task that changes something outside our own files is flagged `needs_approval`: the agent only drafts.
"""

from __future__ import annotations

from pydantic import BaseModel

from . import uk
from .markets import market_for
from .models import ClientProfile, Confidence, Finding, Severity
from .verticals import vertical_for

CONF_WEIGHT = {Confidence.OFFICIAL: 1.0, Confidence.EVIDENCE: 0.8, Confidence.HEURISTIC: 0.5, Confidence.VENDOR: 0.5}


class Task(BaseModel):
    id: str
    title: str
    why: str = ""
    how: list[str] = []
    category: str = "playbook"
    impact: int = 3
    effort: int = 2
    confidence: Confidence = Confidence.EVIDENCE
    phase: int = 30  # 30 / 60 / 90
    needs_approval: bool = True
    manual: bool = False
    source: str = "playbook"  # "playbook" or a finding id
    score: float = 0.0


def _score(t: Task) -> float:
    return round(t.impact * CONF_WEIGHT[t.confidence] / t.effort, 2)


def _playbook(profile: ClientProfile) -> list[Task]:
    vert = vertical_for(profile)
    is_uk = market_for(profile).is_uk
    dirs = []
    for name, note, status in vert["directories"]:
        if status in ("defunct", "closing_2026_10"):
            continue  # never recommend a listing on a closed/closing service
        if status == "brand_only_checkatrade_owned":
            continue
        roles = uk.DIRECTORIES.get(name, {}).get("role", "").split(",") if is_uk else []
        if "L" in roles and "F" not in roles:
            continue  # paid lead-gen marketplaces get their own cost/benefit task, not a "claim your listing" step
        dirs.append(name + (" (unverified status)" if status == "unverified" else ""))
    P = Task
    tasks = [
        P(id="pb.gbp-core", title="Claim, verify and fully complete the Google Business Profile",
          why="GBP signals are the largest local-pack factor group in the 2026 expert survey (opinion, not Google's weights) and feed Maps, Gemini and AI Overviews.",
          how=["Pick the most specific PRIMARY category by comparing the top 3 competitors' primary categories.",
               "Use the exact signage name: no keywords added (suspension risk).",
               "Complete hours + special hours, services with descriptions, booking/menu link, attributes, accurate description.",
               "Add real, recent photos regularly. Do not geotag or fake locations."],
          impact=5, effort=2, confidence=Confidence.EVIDENCE, phase=30, manual=True),
        P(id="pb.nap-directories", title="Fix NAP consistency across core directories (claim listings manually)",
          why="Consistent name/address/phone lets machines confirm the entity; Bing Places, Apple Business Connect and Yelp feed other assistants.",
          how=["Use the SAME primary static number everywhere; tracking numbers only as secondary.",
               "Claim/verify: " + ", ".join(dict.fromkeys(dirs)),
               "Do not buy bulk citation blasts; prefer 8-15 accurate, relevant listings."],
          impact=4, effort=3, confidence=Confidence.EVIDENCE, phase=30, manual=True),
        P(id="pb.review-engine", title="Run a compliant review programme: ask EVERY customer, reply to ALL reviews",
          why="Reviews are the second-largest pack factor group and a major input to AI answers (review text, recency, response rate).",
          how=(["Invite ALL recent customers the same neutral way (or an impartial sample, e.g. every nth). Excluding customers with open complaints is not impartial.",
                "No incentives of any kind: lawful in the UK only if prominently disclosed, but banned by Google, Trustpilot, Checkatrade and Yell; this tool never proposes them. No staff quotas or scripts naming staff.",
                "Show on your own site only ratings computed from ALL genuine reviews, naming the source (DMCC Act 2024).",
                "Sending by email/SMS may be direct marketing under PECR: use consent or soft opt-in, identify the sender and include an opt-out. QR codes and in-person asks are lowest risk. [LAWYER] if unsure."]
               if is_uk else
               ["Send the direct Google review link by SMS/email to every customer: no gating, no incentives, no staff-name requests, no on-premises kiosks."]) + [
               "Draft (never auto-post) replies; healthcare/legal replies must not confirm a patient/client relationship.",
               "Track velocity with weekly snapshots (the Places API returns only 5 reviews)."],
          impact=5, effort=3, confidence=Confidence.EVIDENCE, phase=30),
        P(id="pb.homepage-local", title="Make the homepage unmistakably local",
          why="City + primary service in title/H1, visible NAP, tap-to-call, hours and a map are cheap relevance and conversion wins.",
          how=["Title/H1 contain primary service + city.", "Phone as tel: link; hours visible; embed the map.",
               "Link prominently to each core service page."],
          impact=4, effort=1, confidence=Confidence.EVIDENCE, phase=30),
        P(id="pb.analytics", title="Set up measurement: Search Console, Bing Webmaster Tools, GA4 events, AI-referral channel",
          why="You cannot prove results without baselines. Bing Webmaster Tools has the only first-party AI-citation report found.",
          how=["Verify Search Console + Bing Webmaster Tools; enable BigQuery export if available.",
               "GA4 events for calls, form fills, direction clicks; custom 'AI Assistants' channel (many AI visits arrive as Direct).",
               "Call tracking via dynamic number swap without changing the GBP/schema primary number."],
          impact=3, effort=2, confidence=Confidence.OFFICIAL, phase=30, manual=True),
        P(id="pb.ai-baseline", title="Take two AI-visibility baseline waves before changing anything",
          why="Assistant answers vary run to run; a defensible change claim needs >=200 valid runs/platform/period and two baselines.",
          how=["python -m local_seo_agent probe <client> --wave baseline1 / baseline2 (set a budget cap).",
               "Manually sample Google AI Overviews / AI Mode for ~10 queries (not measurable by API)."],
          impact=3, effort=2, confidence=Confidence.OFFICIAL, phase=30, needs_approval=False),
        P(id="pb.service-pages", title="One strong page per core service (and per area only where genuinely distinct)",
          why="Intent-matched pages win organic and give AI assistants something specific to cite. Templated city pages are doorway-page spam.",
          how=["Write from client-supplied facts: pricing ranges, process, credentials, FAQs from real customer questions.",
               "No invented statistics, awards or quotes. Cap near-duplicate location pages; each needs unique, useful content.",
               "Answer-first structure (summary in first paragraph), clear headings, NAP and CTA."],
          impact=4, effort=4, confidence=Confidence.EVIDENCE, phase=60),
        P(id="pb.schema", title="Add LocalBusiness JSON-LD (generated from facts; no aggregateRating)",
          why="Hygiene that confirms entity facts. Controlled tests show no citation uplift by itself.",
          how=["python -m local_seo_agent schema <client>", "Keep values identical to GBP and the visible page."],
          impact=2, effort=1, confidence=Confidence.EVIDENCE, phase=60),
        P(id="pb.local-mentions", title="Earn genuine local mentions and links",
          why="Brand mentions across independent sources correlate with AI visibility (observational, mostly large brands) and prominence.",
          how=["Chamber of commerce, local associations, sponsorships, suppliers/partners, local press and 'best of' lists.",
               "Original local data or a useful local resource others cite. Disclose any paid placement. No link schemes."],
          impact=4, effort=4, confidence=Confidence.EVIDENCE, phase=90),
        P(id="pb.third-party-lists", title="Win inclusion on the third-party lists AI assistants actually cite",
          why="The probe reports which domains are cited for your prompts; those are the pages to earn a place on.",
          how=["Review 'top cited domains' in the AI visibility section; pursue legitimate inclusion (real merits, disclosed).",
               "No astroturfing on Reddit/forums/Wikipedia; participate openly or not at all."],
          impact=4, effort=3, confidence=Confidence.HEURISTIC, phase=90),
    ]
    if is_uk:
        tasks.extend(_uk_playbook(profile, vert))
    age = profile.gbp_age_days()
    if age is not None and 0 <= age < 90:
        tasks.extend(_new_profile_playbook(profile, age))
    if vert.get("key") in ("body_contouring", "cosmetic_surgery"):
        tasks.extend(_contouring_playbook(profile, vert, is_uk))
    if profile.service_area_business or vert["sab_default"]:
        tasks.append(P(id="pb.sab", title="Configure as a service-area business correctly",
                       why="Hidden-address businesses must not publish a fake storefront; proximity works from the service location.",
                       how=["Hide the address on GBP; list up to 20 service areas (about a 2-hour drive).",
                            "Create genuinely useful area pages only where you serve customers.",
                            "Geo-grid rank checks need a paid API; do not scrape Maps."],
                       impact=4, effort=2, confidence=Confidence.OFFICIAL, phase=30, manual=True))
    if profile.locations > 1:
        tasks.append(P(id="pb.multi-location", title="Multi-location: one GBP + one unique indexable page per location",
                       how=["GBP website link points to the location page, not the home page.",
                            "Per-location NAP table; store-locator pages must be crawlable HTML."],
                       impact=4, effort=4, confidence=Confidence.OFFICIAL, phase=60))
    lsa_ok = vert["lsa"] and not (is_uk and vert.get("key") == "lawyer" and (profile.city or "").lower() != "london")
    if lsa_ok:
        tasks.append(P(id="pb.lsa", title="Evaluate Local Services Ads (paid, above the local pack)",
                       why="For this vertical LSAs can sit above the organic pack, which affects what '#1' means.",
                       how=["Check availability/licensing requirements for the vertical and area; compare cost per lead."],
                       impact=3, effort=3, confidence=Confidence.OFFICIAL, phase=60, manual=True))
    if "ymyl" in vert["compliance"]:
        tasks.append(P(id="pb.ymyl", title="Strengthen YMYL trust signals (credentials, licence numbers, reviewed-by)",
                       how=["Show licence/registration numbers, practitioner bios and sources.",
                            "Check professional advertising rules (e.g. bar rules on testimonials; health-claim limits)."],
                       impact=3, effort=2, confidence=Confidence.OFFICIAL, phase=60))
    return tasks


def build_plan(profile: ClientProfile, findings: list[Finding]) -> list[Task]:
    tasks: list[Task] = []
    for f in findings:
        if f.severity in (Severity.INFO,) and f.impact <= 1:
            continue
        if f.severity == Severity.UNKNOWN:
            t_phase, manual = 30, True
        else:
            t_phase, manual = (30 if f.severity == Severity.ERROR or f.impact >= 4 else 60), False
        tasks.append(Task(id=f"fix.{f.id}", title=f.title, why=f.detail, how=[f.fix] if f.fix else [],
                          category=f.category, impact=f.impact, effort=f.effort, confidence=f.confidence,
                          phase=t_phase if f.severity != Severity.INFO else 90, manual=manual, source=f.id))
    tasks.extend(_playbook(profile))
    for t in tasks:
        t.score = _score(t)
    return sorted(tasks, key=lambda t: (t.phase, -t.score, t.id))


def by_phase(tasks: list[Task]) -> dict[int, list[Task]]:
    out: dict[int, list[Task]] = {30: [], 60: [], 90: []}
    for t in tasks:
        out.setdefault(t.phase, []).append(t)
    return out


def _uk_playbook(profile: ClientProfile, vert: dict) -> list[Task]:
    """UK-only tasks (research/uk). Legal items are flagged [LAWYER]; directory advice respects registry statuses."""
    P = Task
    key = vert.get("key", "generic")
    tasks = [
        P(id="pb.uk-registers", title="Align official registers: Companies House and your regulator/trade-body listings",
          why="Assistants and Google match entities against official records, and AI answers have recommended firms that no longer trade.",
          how=["Companies House: status 'active', registered name, number and registered office match the website footer (the registered office may differ from the trading/GBP address: keep them as separate fields).",
               "Regulator/scheme registers relevant to the vertical (e.g. " + ", ".join(
                   n for n, _, st in vert["directories"] if st != "defunct" and n in (
                       "SRA register", "GDC register", "Gas Safe Register", "NICEIC", "TrustMark", "Food hygiene rating (FHRS/FHIS)",
                       "Law Society of Scotland find-a-solicitor", "Law Society of Northern Ireland")) + "): verify, never just claim a badge.",
               "Run `resolve` (postcodes.io) and set COMPANIES_HOUSE_API_KEY (free) so `audit` checks company status automatically."],
          impact=3, effort=2, confidence=Confidence.EVIDENCE, phase=30, manual=True),
        P(id="pb.uk-identity", title="Show the legally required business details on the website",
          why="Limited companies must show registered name, company number, place of registration and registered office (SI 2015/17); E-Commerce Regulations reg 6 add an email address and VAT number if registered.",
          how=["Footer/legal page with those details, plus a privacy policy and cookie information."],
          impact=3, effort=1, confidence=Confidence.OFFICIAL, phase=30),
        P(id="pb.uk-apple-bing", title="Claim Apple Business (formerly Business Connect) and Bing Places",
          why="Apple Maps/Siri and Bing/Copilot are separate data sources from Google; UK iPhone use is high.",
          how=["Use the same NAP, hours and categories as GBP.", "Add bank-holiday special hours for the right nation (gov.uk/bank-holidays.json has england-and-wales, scotland, northern-ireland)."],
          impact=3, effort=2, confidence=Confidence.EVIDENCE, phase=30, manual=True),
        P(id="pb.uk-consent", title="Check cookie/consent set-up for analytics, ads and call tracking (PECR)",
          why="From 5 Feb 2026 PECR fines can reach GBP 17.5m or 4% of turnover; GA4 in default configuration likely does not meet the statistical exemption; call-tracking scripts set cookies too.",
          how=["Equal-prominence accept/reject; no non-essential tags before consent; privacy policy lists each tag.",
               "Call recording needs a lawful basis and a caller notice."],
          impact=3, effort=2, confidence=Confidence.EVIDENCE, phase=60, manual=True),
        P(id="pb.uk-ai-surfaces", title="Sample Google AI Mode / AI Overviews by hand and read the Search Console AI report",
          why="AI Mode is live in the UK (since 2025-07-29). Search Console's Generative AI report reaches more sites over time; check it is available for your property.",
          how=["Run `sheet-export` for a worksheet, observe on a real phone in the client's area, then `sheet-import`."],
          impact=2, effort=2, confidence=Confidence.VENDOR, phase=60, needs_approval=False),
    ]
    if key in ("plumber", "heating_engineer", "electrician"):
        tasks.append(P(id="pb.uk-trades-directories", title="Decide on Checkatrade / MyBuilder / TrustATrader using YOUR probe data",
                       why="One agency study found ChatGPT citing Checkatrade in 78 of 80 trades answers (and Checkatrade has a ChatGPT app), but another study of Google AI Mode found the business's own site dominates: directional evidence only. Rated People is now a Checkatrade-owned brand and its memberships were not transferred.",
                       how=["Run the probe first: if Checkatrade/MyBuilder appear in the cited domains for your prompts, a paid profile is more defensible.",
                            "Memberships are paid: compare cost per lead; never buy reviews or incentivise reviews on any of them."],
                       impact=3, effort=2, confidence=Confidence.HEURISTIC, phase=60, manual=True))
    if key == "dentist":
        tasks.append(P(id="pb.uk-dental", title="Dental: NHS listing for your nation, GDC numbers, confidential review replies",
                       how=["Keep the NHS listing for your nation accurate (NHS.uk England, NHS inform Scotland, NHS 111 Wales, HSC Northern Ireland).",
                            "Show each clinician's GDC number; say clearly whether you accept new NHS patients.",
                            "Never confirm a reviewer was a patient or mention treatment in public replies (GDC confidentiality)."],
                       impact=3, effort=1, confidence=Confidence.OFFICIAL, phase=30))
    if key == "lawyer":
        tasks.append(P(id="pb.uk-solicitor", title="Solicitors: SRA transparency items (England & Wales) or the right regulator elsewhere",
                       how=["SRA number, 'authorised and regulated by the SRA', clickable digital badge, complaints procedure, and price/service information for the listed areas.",
                            "Scotland / Northern Ireland: Law Society of Scotland / of Northern Ireland rules apply instead (not built into this tool). [LAWYER]"],
                       impact=4, effort=2, confidence=Confidence.OFFICIAL, phase=30))
    if key == "restaurant":
        tasks.append(P(id="pb.uk-food", title="Food hygiene rating and allergen information",
                       how=["Display your FHRS rating (mandatory in Wales and Northern Ireland; voluntary in England); Scotland uses FHIS (Pass / Improvement Required).",
                            "Point menus and online ordering to allergen information."],
                       impact=2, effort=1, confidence=Confidence.OFFICIAL, phase=60))
    if profile.is_aesthetics or key == "salon":
        tasks.append(P(id="pb.uk-aesthetics", title="Aesthetics: no prescription-only medicine brands in public copy; age checks; consented before/afters",
                       how=["Use 'anti-wrinkle consultation', not 'Botox/Dysport' (CAP 12.12), including titles, alt text, GBP text and hashtags.",
                            "Do not target under-18s; keep signed, dated consent for before/after photos and the unretouched originals."],
                       impact=3, effort=1, confidence=Confidence.OFFICIAL, phase=30))
    return tasks


def _new_profile_playbook(profile: ClientProfile, age: int) -> list[Task]:
    """Google Business Profile that has JUST been verified. 'Accepted' means verification passed, NOT that Google endorsed the name,
    categories or content: those stay subject to later automated and manual review (research/bbl B2 + critique)."""
    P = Task
    return [
        P(id="pb.np-freeze-name", title="Days 0-7: freeze the business name and prove it",
          why="Verification does not protect a name that is a service plus a place; competitor reports and automated re-review can still hit it. Google cross-checks the name against signage, website and stationery.",
          how=["Compare the GBP name with the shop-front sign, the website/branch page, Facebook, Instagram, invoices and the booking engine. Check the SPELLING matches everywhere (e.g. bootlift / bootylift / booty lift).",
               "If they differ, do NOT edit the GBP name in a hurry: agree the canonical trading name with the owner and (for a franchise) the franchisor in writing, then make the sign and every profile match.",
               "Check for an existing or duplicate profile for the same premises or under the trading name you actually use BEFORE any edit.",
               "Build a name evidence pack: photos of signage, the franchise licence or permitted trading name, a recent invoice, the lease/rates/utility bill, the HMRC or Companies House record for the trading entity."],
          impact=5, effort=2, confidence=Confidence.EVIDENCE, phase=30, manual=True),
        P(id="pb.np-ownership", title="Days 0-7: lock down ownership, access and contact details",
          why="Profile ownership disputes and recovery problems are expensive. The business, not the franchisor or the agency, should own the profile.",
          how=["Owner = a business-controlled Google account (not a personal mailbox that one person can lose); add the agency/franchisor as managers, not owners; record the recovery email and phone.",
               "Pick ONE primary phone and ONE email per the franchise agreement and use the same details on the website, Facebook, Instagram, citations and the GBP (public listings sometimes show different numbers and emails for the same branch).",
               "Add UTM parameters to the website and booking links so GBP traffic is measurable."],
          impact=4, effort=1, confidence=Confidence.EVIDENCE, phase=30, manual=True),
        P(id="pb.np-completeness", title="Days 8-30: complete the profile accurately (one change at a time)",
          why="The primary category is the most influential single field; accuracy matters more than volume.",
          how=["Primary category: the most specific accurate one from the dashboard list (for a non-medical device studio often 'Beauty salon'). Do not add medical, surgical or weight-loss categories to a non-medical business.",
               "Services with plain descriptions and NO efficacy claims; hours incl. bank holidays; booking link; appointment-only attribute if true; exterior photo with signage (matches the verification evidence), interior, equipment, team.",
               "Before/after photos only with signed dated consent and ASA-compliant presentation (no Google GBP-specific rule was found; the ASA rules apply).",
               "Description about 750 characters, factual, no offers or prices, no outcome promises.",
               "Never change name, address and category together."],
          impact=4, effort=2, confidence=Confidence.EVIDENCE, phase=30, manual=True),
        P(id="pb.np-reviews", title="Days 8-60: build reviews steadily and compliantly",
          why="A new profile starts with none; Google reportedly filters new profiles' reviews more aggressively, and bans staff quotas, incentives, gating and kiosks.",
          how=["Invite every client the same neutral way after treatment (QR code, link): no discounts, no gifts, no 'only happy clients', no staff targets, no asking clients to name a staff member.",
               "Do not ask friends, family or staff to post. Do not post spikes of reviews on one day.",
               "Reply to every review without confirming a person was a client or giving treatment details (privacy)."],
          impact=5, effort=3, confidence=Confidence.EVIDENCE, phase=60),
        P(id="pb.np-api-wait", title="Day 60+: the Business Profile API becomes possible (not before)",
          why="Google's API prerequisites need a verified profile active for 60+ days and a website; access is approved per Cloud project and can take weeks.",
          how=[f"Profile age today: {age} days. Until day 60 use the dashboard, Search Console, and the Places API for competitor and rating data."],
          impact=2, effort=2, confidence=Confidence.OFFICIAL, phase=60, needs_approval=False),
    ]


def _contouring_playbook(profile: ClientProfile, vert: dict, is_uk: bool) -> list[Task]:
    P = Task
    tt = profile.treatment_type
    tasks = [
        P(id="pb.bc-claims", title="Audit and rewrite every efficacy and safety claim before promoting anything",
          why="UK advertising rules are the biggest risk for this service. ASA's published position is that there is no convincing evidence devices treat or remove cellulite, and absolute safety claims were ruled against as trivialising risk. SEO traffic to a page with non-compliant claims is a liability, not an asset.",
          how=["Replace outcome claims ('erase cellulite', 'tighten loose skin', 'safest', 'permanent', 'instant') with factual descriptions of what the programme involves, unless the client holds product-specific human-trial evidence for the device and body area.",
               "Keep an evidence file: trials for each claim, signed dated consent and unretouched originals for before/after images, proof testimonials are genuine.",
               "Say plainly near the first mention: non-surgical, no injections, no fat transfer, results not comparable to surgery. Avoid 'non-surgical BBL' in titles and descriptions."],
          impact=5, effort=2, confidence=Confidence.EVIDENCE, phase=30),
        P(id="pb.bc-suitability", title="Add suitability, contraindication, session and complaints information",
          why="Honest information protects clients and is what a trustworthy page looks like to both people and AI assistants.",
          how=["Who should NOT have the treatment (e.g. pregnancy, pacemakers or metal implants, clotting disorders): have a clinician confirm the list.",
               "Number of sessions, what results are and are not expected, patch/consultation steps, practitioner training and insurance, complaints route, 18+ statement."],
          impact=4, effort=2, confidence=Confidence.HEURISTIC, phase=30),
        P(id="pb.bc-differentiate", title="Make the page match what people actually search (and not mislead them)",
          why="'BBL' usually means fat-transfer surgery and 'non-surgical BBL' is used by regulators for filler procedures. People searching those terms are often researching surgery.",
          how=["Target honest terms: 'body contouring', 'booty lift treatment', 'cellulite treatment' (describe, don't promise), plus town names across Lanarkshire.",
               "Add an explanatory section: how this differs from surgical BBL and from filler procedures, and what it can't do."],
          impact=4, effort=3, confidence=Confidence.EVIDENCE, phase=60),
    ]
    if is_uk and profile.nation == "SCO":
        tasks.append(P(id="pb.bc-scot-regulation", title="Scotland: ask the regulators in writing and keep the answers",
                       why="Scotland's 2026 non-surgical procedures legislation and council licensing are phased in from no earlier than 2027-09-06; the scope for skin-surface devices is unclear.",
                       how=["Ask Healthcare Improvement Scotland whether any part of the service is registrable (especially if a nurse or doctor is involved).",
                            "Ask the local council (e.g. North Lanarkshire licensing) what licences or premises standards apply now and from 2027; keep insurance specific to the devices used.",
                            "Do not tell clients the service is 'licensed', 'approved' or 'exempt' unless you hold a document that says so. [LAWYER]"],
                       impact=3, effort=1, confidence=Confidence.VENDOR, phase=30, manual=True))
    if profile.franchise_brand or profile.brand_domain:
        tasks.append(P(id="pb.bc-franchise", title="Franchise: agree in writing who controls the page, the claims and the profile",
                       why="A branch page on the brand's domain is a shared asset: branches share templates (near-duplicate content), you cannot fix its claims, and the ASA looks at who is responsible for content.",
                       how=["Ask the franchisor for the permitted trading name, written permission to run your own Google profile (and check whether they created one), and whether you may run your own domain.",
                            "Audit the brand pages your local page links to as well as your own; do not copy brand claims you cannot evidence.",
                            "Do not mark up the brand's Trustpilot score as the branch's rating; brand-level reviews are not local reviews."],
                       impact=3, effort=2, confidence=Confidence.HEURISTIC, phase=60, manual=True))
    if tt in ("surgical", "injectable") or (profile.delivered_by or "").lower() in ("nurse", "doctor", "prescriber"):
        tasks.append(P(id="pb.bc-registration", title="Regulated service: registration, named practitioners and risk information first",
                       how=["Registration number (HIS in Scotland / CQC in England) on file and shown; named clinicians with GMC/NMC numbers verifiable on the register.",
                            "No time-limited offers, prizes, multi-buy or deadline pricing for cosmetic surgery or injectables; people need time to reflect. [LAWYER]"],
                       impact=5, effort=2, confidence=Confidence.OFFICIAL, phase=30, manual=True))
    return tasks
