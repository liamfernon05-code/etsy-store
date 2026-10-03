"""Deterministic 30/60/90-day plan: audit findings + a local-business playbook, ranked by impact x confidence / effort.

Every task that changes something outside our own files is flagged `needs_approval`: the agent only drafts.
"""

from __future__ import annotations

from pydantic import BaseModel

from .models import ClientProfile, Confidence, Finding, Severity
from .verticals import CORE_DIRECTORIES, get_vertical

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
    vert = get_vertical(profile.vertical)
    dirs = [d for d, _ in CORE_DIRECTORIES] + [d for d, _ in vert["directories"]]
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
          how=["Send the direct Google review link by SMS/email to every customer: no gating, no incentives, no staff-name requests, no on-premises kiosks.",
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
    if vert["lsa"]:
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
