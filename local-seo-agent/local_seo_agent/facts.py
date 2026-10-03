"""Volatile facts the agent may quote, each with a source, confidence and a verified-on date.

Rule: the agent never quotes a number that is not in this file. This area changes weekly, so every
entry carries `verified_on`; the report prints it and flags entries older than STALE_AFTER_DAYS.
Most sources were verified via search summaries (Google/OpenAI doc pages were blocked in research);
re-verify against primary docs before encoding any of these as a hard rule.
"""

from __future__ import annotations

from datetime import date

from .models import Confidence

STALE_AFTER_DAYS = 90
VERIFIED = "2026-10-03"

FACTS: list[dict] = [
    {"id": "no-guarantee", "confidence": Confidence.OFFICIAL,
     "text": "No one can guarantee a #1 ranking or a first mention in an AI assistant. Results are probabilistic, vary by user location and over time.",
     "source": "Google Search Central: SEO FAQ; SparkToro 2026 AI-recommendation consistency study"},
    {"id": "cwv", "confidence": Confidence.OFFICIAL,
     "text": "Core Web Vitals 'good' thresholds at the 75th percentile: LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1.",
     "source": "https://web.dev/articles/vitals"},
    {"id": "googlebot-2mb", "confidence": Confidence.OFFICIAL,
     "text": "Googlebot processes the first 2 MB of uncompressed bytes of an HTML file; Google called this a documentation clarification. Low practical risk for most local sites.",
     "source": "https://developers.google.com/search/docs/crawling-indexing/googlebot (Feb 2026 reorg)"},
    {"id": "faq-rich-results", "confidence": Confidence.VENDOR,
     "text": "Google ended FAQ rich results on 2026-05-07. FAQPage markup is harmless but earns no rich result.",
     "source": "Search Engine Journal coverage; confirm on Google's structured-data docs"},
    {"id": "self-serving-reviews", "confidence": Confidence.OFFICIAL,
     "text": "Review/aggregateRating markup about a business on its OWN website (LocalBusiness/Organization, including third-party widgets) is not eligible for star rich results. No penalty, just no stars. Do not copy third-party reviews into markup.",
     "source": "https://developers.google.com/search/blog/2019/09/making-review-rich-results-more-helpful"},
    {"id": "local-pack-factors", "confidence": Confidence.EVIDENCE,
     "text": "Google says local ranking = relevance, distance, prominence. Whitespark 2026 expert survey (47 experts): GBP signals ~32%, review signals ~20%, on-page ~19%, links ~15%, citations ~6% of pack weight. This is expert opinion about Google's local pack, NOT an AI-visibility weighting.",
     "source": "https://whitespark.ca/local-search-ranking-factors/"},
    {"id": "gbp-review-policy-2026", "confidence": Confidence.VENDOR,
     "text": "Vendors report April 2026 Google review-policy changes (review gating, kiosk/shared-device reviews, soliciting staff-named reviews). Not read from Google's policy page: treat as WARN and verify.",
     "source": "Vendor summaries (Birdeye, Launchcodex and others)"},
    {"id": "ftc-fake-reviews", "confidence": Confidence.OFFICIAL, "markets": ["US"],
     "text": "US FTC rule 16 CFR 465 (effective 2024-10-21) bans fake or AI-generated reviews, paid-for sentiment and review suppression; civil penalty up to $53,088 per violation (Jan 2025 inflation adjustment; recheck the 2026-09-15 Federal Register notice). Non-US rules (UK DMCC Act, EU, AU) were not researched.",
     "source": "https://www.federalregister.gov/documents/2025/01/17/2025-01361/adjustments-to-civil-penalty-amounts"},
    {"id": "llms-txt", "confidence": Confidence.OFFICIAL,
     "text": "Google does not use llms.txt and says generative-AI optimisation is 'still SEO' (May 2026 guide). No major answer engine is confirmed to honour llms.txt. Optional, not a lever.",
     "source": "Google Search Central generative-AI guide, May 2026"},
    {"id": "schema-ai", "confidence": Confidence.EVIDENCE,
     "text": "Ahrefs' controlled test (1,885 pages) found no citation uplift from adding schema (AI Mode +2.4%/ChatGPT +2.2% were noise; AI Overviews -4.6%, significant), on pages that already had 100+ citations. Schema is hygiene, not a lever.",
     "source": "https://ahrefs.com/blog/schema-ai-citations/ (via summary)"},
    {"id": "ai-bots", "confidence": Confidence.OFFICIAL,
     "text": "Search/answer bots (OAI-SearchBot, Claude-SearchBot, PerplexityBot, Googlebot, Bingbot) drive visibility; training bots (GPTBot, ClaudeBot, Google-Extended) do not affect search inclusion. User-initiated fetchers (ChatGPT-User, Claude-User, Perplexity-User) may ignore robots.txt. Cloudflare blocks AI bots by default on NEW domains (since 2025-07-01).",
     "source": "OpenAI/Anthropic/Perplexity crawler docs; Cloudflare 2025-07-01 announcement"},
    {"id": "claude-search-provider", "confidence": Confidence.VENDOR,
     "text": "Claude's web search is strongly evidenced (not vendor-confirmed) to use Brave Search; results overlap Brave's by roughly 79-87% in third-party tests.",
     "source": "Anthropic subprocessor list; Profound re-test (Jun 2026)"},
    {"id": "chatgpt-local", "confidence": Confidence.VENDOR, "markets": ["US"],
     "text": "ChatGPT local answers blend OpenAI's own index, scraped Google results and licensed data (Yelp deal announced 2026-07-23). The widely quoted 'Foursquare supplies 70% of ChatGPT local results' is not supported by a larger 2,880-prompt re-test (~0.06%). Yelp was in the grounding payload ~96% of the time but cited ~1%.",
     "source": "Search Engine Land; SteadyDemand re-test (single agency, not peer reviewed)"},
    {"id": "gemini-maps", "confidence": Confidence.VENDOR,
     "text": "Gemini and Google AI Overviews/AI Mode draw on Google's index and Google Maps/GBP data, so GBP quality matters most there. Gemini API grounding is NOT the same as AI Overviews.",
     "source": "SOCi 2026 Local Visibility Index; Google docs"},
    {"id": "aio-ctr", "confidence": Confidence.EVIDENCE,
     "text": "AI Overviews cut CTR on INFORMATIONAL queries (Seer: -61% organic CTR on 3,119 queries; Ahrefs: -58% position-1 CTR). Do not apply these to local-intent queries, where the local pack mostly still shows.",
     "source": "Seer Interactive (Sep 2025); Ahrefs (Dec 2025)"},
    {"id": "gbp-api-access", "confidence": Confidence.OFFICIAL,
     "text": "The Google Business Profile APIs have 0 quota until Google approves access (verified GBP 60+ days with a website); approval can take weeks. The Q&A feature/API was discontinued (Nov 2025).",
     "source": "https://developers.google.com/my-business/content/limits"},
    {"id": "custom-search-sunset", "confidence": Confidence.VENDOR,
     "text": "Google's Custom Search JSON API is closed to new customers and scheduled to shut down 2027-01-01. Do not build rank tracking on it.",
     "source": "Vendor/dev-community summaries"},
    # ---------------- UK (research/uk/*; legal items need a human lawyer: lawyer=True) ----------------
    {"id": "uk-dmcc-reviews", "confidence": Confidence.EVIDENCE, "markets": ["UK"], "lawyer": True,
     "text": "UK: fake reviews, reviews that conceal an incentive, publishing reviews misleadingly, and failing to take reasonable and proportionate steps against fake reviews are banned practices under the Digital Markets, Competition and Consumers Act 2024 (Sch 20 para 13), in force 6 Apr 2025 (replacing the CPRs 2008). The CMA can fine directly: for undertakings the higher of GBP 300,000 or 10% of global turnover. An incentivised review is lawful only if the incentive is prominently disclosed, but Google, Trustpilot, Checkatrade and Yell ban them, so this tool never proposes incentives.",
     "source": "CMA guidance CMA208; law-firm summaries (CMS, Pinsent Masons, Browne Jacobson). Statute/guidance text not read directly."},
    {"id": "uk-cma-cases", "confidence": Confidence.EVIDENCE, "markets": ["UK"],
     "text": "The CMA opened its first fake-review investigations on 2026-03-27 (Autotrader, Feefo, Dignity, Just Eat, Pasta Evangelists). Outcomes were not confirmed at the verification date: never describe them as concluded. First substantive DMCC fine: AA Developments Ltd, GBP 4.2m after a 40% settlement discount (drip pricing, 2026-04-15).",
     "source": "gov.uk CMA press release; law-firm summaries"},
    {"id": "uk-cap-claims", "confidence": Confidence.EVIDENCE, "markets": ["UK"], "lawyer": True,
     "text": "UK ASA/CAP Code: objective claims need documentary evidence (3.7); unqualified superlatives are treated as comparisons with all competitors (3.32-3.36); testimonials need documentary evidence they are genuine and contact details (rule numbers differ between sources and editions: verify against the current Code); trust marks need authorisation (3.50); 'guarantee' rules (3.53-3.54); recognisable advertising (2.1-2.4). Prescription-only medicines such as Botox cannot be advertised to the public (12.12); cosmetic-intervention ads must not target under-18s (12.25).",
     "source": "ASA/CAP Code (rule numbers per the UK critic's check; Code amended 2025-04-07): verify against the current edition"},
    {"id": "uk-pecr-fines", "confidence": Confidence.EVIDENCE, "markets": ["UK"], "lawyer": True,
     "text": "UK: PECR maximum fines are GBP 17.5m or 4% of worldwide turnover (from 2026-02-05, Data (Use and Access) Act 2025). New consent exceptions for statistical, functionality and security uses apply from the same date (ICO final guidance 2026-04-29); standard GA4 configurations likely do not meet the statistical exception; advertising/remarketing tags need prior opt-in. The ICO is now the Information Commission (since 2026-09-30) but still branded the ICO.",
     "source": "ICO; law-firm summaries (Bird & Bird, Osborne Clarke). ICO text not read directly."},
    {"id": "uk-review-requests-pecr", "confidence": Confidence.HEURISTIC, "markets": ["UK"], "lawyer": True,
     "text": "UK: whether a 'please review us' email/SMS is direct marketing under PECR is not settled (no ICO statement found). Conservative default: treat it as marketing (consent or soft opt-in, sender identity, opt-out in every message) and have a human decide.",
     "source": "ICO direct-marketing guidance (commentary); researcher inference"},
    {"id": "uk-platform-reviews", "confidence": Confidence.VENDOR, "markets": ["UK", "US"],
     "text": "Google reportedly changed its Maps review policy on 2026-04-16/17: staff review quotas and soliciting reviews that name a staff member are banned; gating, incentives and kiosks remain prohibited. Trustpilot requires inviting all customers or an impartial sample (excluding customers with open complaints is not impartial).",
     "source": "Trade press (ppc.land) and platform guidelines; Google help-centre text not read"},
    {"id": "uk-identity", "confidence": Confidence.EVIDENCE, "markets": ["UK"], "lawyer": True,
     "text": "UK limited companies must show their registered name, registration number, place of registration and registered office on the website (Company, LLP and Business (Names and Trading Disclosures) Regulations 2015, SI 2015/17, which replaced the revoked 2008 regulations). E-Commerce Regulations 2002 reg 6 add an email address and VAT number (if registered). The registered office and the trading/GBP address are separate fields.",
     "source": "legislation.gov.uk/uksi/2015/17 (via summaries); Pinsent Masons"},
    {"id": "uk-sra", "confidence": Confidence.EVIDENCE, "markets": ["UK"], "lawyer": True,
     "text": "England and Wales only: solicitor websites must show price and service information for specified areas (conveyancing, probate, immigration, employment tribunals, some motoring offences, business debt recovery up to GBP 100k, licensing applications), complaints information, the SRA number and the clickable SRA digital badge. Scotland and Northern Ireland have separate regulators (Law Society of Scotland / of Northern Ireland).",
     "source": "https://www.sra.org.uk/solicitors/standards-regulations/transparency-rules/"},
    {"id": "uk-cqc-dental", "confidence": Confidence.EVIDENCE, "markets": ["UK"],
     "text": "CQC regulation 20A (display your rating on your website) applies in England to providers that HAVE a CQC rating. Primary dental care is generally not rated, so the check only runs when the client supplies a rating. Dentists are held to GDC advertising and confidentiality standards (show GDC numbers; never confirm a reviewer was a patient).",
     "source": "CQC 'display your ratings'; GDC guidance"},
    {"id": "uk-fhrs", "confidence": Confidence.EVIDENCE, "markets": ["UK"],
     "text": "Food hygiene rating display is mandatory in Wales and Northern Ireland, voluntary in England; Scotland uses FHIS (Pass / Improvement Required / Exempt / Awaiting Inspection) rather than 0-5.",
     "source": "Food Standards Agency / FSS"},
    {"id": "uk-lsa", "confidence": Confidence.VENDOR, "markets": ["UK"],
     "text": "Google Local Services Ads in the UK: nationwide for home-service trades, Greater London only for legal services and estate agents. Google Guaranteed/Screened were reportedly replaced by 'Google Verified' from 2025-10-20 (claims only for jobs done before that date, within 30 days).",
     "source": "Google LSA UK help/blog; UK trade-body summaries"},
    {"id": "uk-ai-search", "confidence": Confidence.VENDOR, "markets": ["UK"],
     "text": "Google AI Mode launched in the UK on 2025-07-29. The Search Console Generative AI report launched 2026-06-03 to a UK subset and was reported worldwide by 2026-08-31; from 2026-09-07 it reportedly combines AI Mode and AI Overview impressions and lets you filter AI Mode rows by prompt. Ask Maps (Gemini) UK availability is unconfirmed. Google ccTLDs redirect to google.com (from 2025-04-15): localisation relies on location signals, not google.co.uk.",
     "source": "Trade press (Press Gazette, Search Engine Land, 9to5Google); not read from Google"},
    {"id": "uk-ai-citation-studies", "confidence": Confidence.HEURISTIC, "markets": ["UK"],
     "text": "Two small UK AI-citation studies (both published by agencies selling AI visibility, single-run, no variance) point in opposite directions: ChatGPT cited Checkatrade in 78 of 80 trades answers (Checkatrade also has a ChatGPT app), while Google AI Mode cited the business's own site in 90% of 159 answers. Directional only: measure each assistant separately.",
     "source": "Murray Digital (2026-08-25); Whito (2026)"},
    {"id": "uk-consumer-stats", "confidence": Confidence.EVIDENCE, "markets": ["UK"],
     "text": "BrightLocal's 2026 local-review survey is a US panel: do not present its figures as UK data. Yext's UK survey (n=600) found 36.7% had used AI for local search in the past month.",
     "source": "BrightLocal LCRS 2026; Yext UK survey 2026 (vendors)"},
    {"id": "uk-apple", "confidence": Confidence.VENDOR, "markets": ["UK", "US"],
     "text": "Apple Business Connect became 'Apple Business' on 2026-04-14 (existing claimed locations migrated).",
     "source": "Apple Support; vendor summaries"},
    {"id": "uk-scot-nonsurgical-act", "confidence": Confidence.VENDOR, "markets": ["UK"], "lawyer": True,
     "text": "Scotland: the Non-surgical Procedures and Functions of Medical Reviewers (Scotland) Act 2026 passed on 2026-03-17 and received Royal Assent on 2026-05-12; its offences and a council licensing order are reported to start no earlier than 2027-09-06 and NOTHING in them is in force yet. RF and HIFU-type devices used to destroy, tighten or cause scarring to skin tissue, or to destroy fat cells, appear to be inside the licensing order; cavitation, vacuum and LED are not named (unresolved: ask the council and Healthcare Improvement Scotland). The Act uses 'non-surgical BBL' for filler procedures.",
     "source": "Scottish Parliament/legislation summaries via search; legislation.gov.uk text not read"},
    {"id": "uk-asa-cosmetic-rulings", "confidence": Confidence.EVIDENCE, "markets": ["UK"], "lawyer": True,
     "text": "On 2025-04-16 the ASA ruled against six liquid-BBL advertisers: time-limited offers, countdowns and pressure were socially irresponsible (CAP 1.3), and 'safe', '0% infection', 'minimal pain', 'no downtime' and 'sterile clinic' trivialised risk. CAP monitoring (Apr-Dec 2025, published 2026-03) found only 11.5% of 928 liquid-BBL Meta ads compliant. Those rulings concerned liquid (filler) BBL, but the same logic is applied to cosmetic interventions generally. ASA's published position is that there is no convincing evidence that devices or cosmetic treatments treat, remove or reduce cellulite; spot-reduction and inch-loss claims are not accepted (CAP 13.9). No ASA ruling was found on naming a non-surgical treatment 'Brazilian butt lift'.",
     "source": "ASA rulings and advice pages (via search summaries); CAP monitoring report"},
    {"id": "gbp-name-rule", "confidence": Confidence.VENDOR, "markets": ["UK", "US"],
     "text": "Google's profile-name guideline: the name should reflect the real-world name used consistently on signage, website and stationery; marketing taglines, service information, location information and keywords that are not part of the official name are not allowed. 'Accepted/verified' does not mean Google endorsed the name: later automated or manual review, or a competitor report, can still trigger edits or suspension. A 50-case study by Sterling Sky (older, mostly law firms) saw warnings in ~60% and soft suspensions in ~20% of keyword-in-name cases.",
     "source": "Google Business Profile guidelines (via search summaries); Sterling Sky case study"},
    {"id": "update-freeze", "confidence": Confidence.OFFICIAL,
     "text": "A Google spam update began 2026-09-24 and was still rolling out on 2026-10-03 (expected to end ~2026-10-08). Avoid judging ranking changes during a rollout. Check status.search.google.com for the live state.",
     "source": "https://status.search.google.com/"},
]


def stale(fact_verified_on: str = VERIFIED, today: date | None = None) -> bool:
    today = today or date.today()
    return (today - date.fromisoformat(fact_verified_on)).days > STALE_AFTER_DAYS


def for_market(code: str) -> list[dict]:
    """Facts relevant to a market (default: both US and UK)."""
    return [f for f in FACTS if code in f.get("markets", ["US", "UK"]) or code == "OTHER" and "markets" not in f]


def get(fact_id: str) -> dict:
    for f in FACTS:
        if f["id"] == fact_id:
            return {**f, "verified_on": VERIFIED}
    raise KeyError(fact_id)
