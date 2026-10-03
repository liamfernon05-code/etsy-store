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
    {"id": "ftc-fake-reviews", "confidence": Confidence.OFFICIAL,
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
    {"id": "chatgpt-local", "confidence": Confidence.VENDOR,
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
    {"id": "update-freeze", "confidence": Confidence.OFFICIAL,
     "text": "A Google spam update began 2026-09-24 and was still rolling out on 2026-10-03 (expected to end ~2026-10-08). Avoid judging ranking changes during a rollout. Check status.search.google.com for the live state.",
     "source": "https://status.search.google.com/"},
]


def stale(fact_verified_on: str = VERIFIED, today: date | None = None) -> bool:
    today = today or date.today()
    return (today - date.fromisoformat(fact_verified_on)).days > STALE_AFTER_DAYS


def get(fact_id: str) -> dict:
    for f in FACTS:
        if f["id"] == fact_id:
            return {**f, "verified_on": VERIFIED}
    raise KeyError(fact_id)
