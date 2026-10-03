# Critique 01: Google SEO research report (Critic Agent 1 of 4)

Verification method: WebFetch to developers.google.com was blocked by the egress proxy (EGRESS_BLOCKED), same as the researcher. All checks below used WebSearch (result snippets of vendor sites, SEJ, SERoundtable, plus snippets of Google-hosted pages). So "CONFIRMED" means "multiple independent secondary sources agree", not "read on Google's page". Primary-source re-verification is still required for anything the agent will encode as a hard rule.

## 1. Claim spot-check (15 claims)

| # | Claim | Verdict | Evidence / note |
|---|---|---|---|
| 1 | Dec 2025 core update Dec 11 to Dec 29 (18 days) | CONFIRMED | SEJ, Search Engine Land, gsqi.com ("18 day rollout") |
| 2 | March 2026 spam update Mar 24-25 (<20h) | CONFIRMED | SEJ March core update article; multiple blogs |
| 3 | March 2026 core update Mar 27 to Apr 8 | CONFIRMED | SEJ "Google Confirms March 2026 Core Update Is Complete"; dashboard time 6:12 AM PDT Apr 8 |
| 4 | May 2026 core update May 21 to Jun 2 | CONFIRMED | SERoundtable; 8:43 AM PDT May 21 to 5:40 AM PDT Jun 2 (11d 21h) |
| 5 | Sept 2026 spam update started Sep 24, still rolling | CONFIRMED | SERoundtable "Phase Two hit Sept 30"; Google said "up to two weeks"; expected ~Oct 8. Researcher's "still rolling today" holds. Jun/Aug 2026 spam dates not independently checked (UNVERIFIABLE) |
| 6 | Googlebot 2 MB limit (Feb 3 2026 doc reorg) | CONFIRMED but MISFRAMED | Sources (debugbear, techwyse, ppc.land) agree on Feb 3 2026 and 2 MB for HTML/supported files, 15 MB for other crawlers. Critical nuance the report omits: Google said this is a clarification, not a new restriction; limit is on UNCOMPRESSED bytes; JS/CSS each counted separately at 2 MB. Practical risk for local-business sites is near zero except bloated page-builder pages with inline base64/JSON. Report's "alert >1 MB" is a reasonable heuristic but should be low severity |
| 7 | CWV: LCP 2.5s, INP 200ms, CLS 0.1; 75th percentile | CONFIRMED | Multiple 2026 sources say unchanged since INP launch. One blog claims LCP "good" was lowered to 2.0s; I found no corroboration (treat as noise, but re-check web.dev) |
| 8 | FAQ rich results ended May 7 2026; June report/RRT removal; Aug 2026 API removal | CONFIRMED | SEJ "Google Drops FAQ Rich Results", Bluehost, thefrankagency, others, same three phases |
| 9 | June 2025 retirement of 7 features (Book Actions, Course Info, ClaimReview, Estimated Salary, Learning Video, Special Announcement, Vehicle Listing) | CONFIRMED | Google blog "Simplifying the search results page" (developers.google.com/search/blog/2025/06/simplifying-search-results) surfaced in results; announced June 12 2025. Note: this does NOT affect local-business markup |
| 10 | Q&A: API ended Nov 3 2025, public Q&A removed, Ask Maps replaces | CONFIRMED | BrightLocal, The HOTH, others. Public removal reported as Dec 3 2025 onward, gradual over 1-3 months. Report's "being removed" is fine, but by Oct 2026 it should be stated as "removed" |
| 11 | April 2026 GBP review policy (Apr 16-17): review gating, kiosks, staff-name solicitation, quotas | CONFIRMED (secondary only) | Launchcodex, Birdeye, fsagency, mckinneycv agree: Apr 16 Gemini enforcement, Apr 17 staff-name/quota/kiosk bans, pre-screening banned. Still vendor-sourced; the policy page itself was not read. Also note: "asking staff to name in review" and "kiosk" rules are the least certain details |
| 12 | Whitespark 2026: 47 experts, 187 factors; GBP ~32%, reviews ~20% (from 16%) | CONFIRMED | whitespark.ca snippet + gmbapi.com, w3marketinghub. Report's "on-page 15% vs 19%, links 8% vs 15% conflict" is now resolved: majority sources say on-page 19%, links 15%. Top-3 raw scores (227/225/223), "open now = 5th", "review recency = 11th", behavioural 9%, personalisation 6% remain UNVERIFIABLE. One summary says proximity ~55% of pack decision; treat as unreliable (a derived/misread figure) |
| 13 | AIO CTR: Seer -61% on 5.47M queries; Ahrefs -58% on 300k keywords | PARTLY WRONG / MISCITED | Seer's Sept 2025 study: organic CTR 1.76% to 0.61% (-61%) on 3,119 informational queries, 42 orgs, 25.1M impressions. "5.47M queries" appears to be wrong or from another dataset; fix. Ahrefs: -58% applies to POSITION 1 CTR (Dec 2025 update, 300k keywords), not "sessions". Both are informational-query studies; Seer itself later notes the decline is largely impression inflation, not click collapse. Not applicable to local-intent queries |
| 14 | Search Console API: 25,000 rows/request, 50,000 rows/day/site/search type; 16 months retention | CONFIRMED | developers.google.com/webmaster-tools "all-your-data", Fivetran, Weld. Misleading if read as total: limit is per day of data, so 30 days can return up to 1.5M rows. Report should say that |
| 15 | PSI 25,000/day, 240/min; CrUX 150 QPM; GBP APIs 300 QPM after approval, 0 until approved, ~14-day review | CONFIRMED | developer.chrome.com CrUX API; GBP limits/prereqs pages surfaced. Quota-increase denied unless usage >50% of limit |
| 16 | Generative AI guide May 15 2026, "still SEO", no llms.txt/special markup | CONFIRMED | SEJ, DemandSphere, withsurface; consistent wording. Report's "updated Jun 5" unverified |
| 17 | GSC Generative AI report Jun 3 2026, UK subset, data from May 18, no clicks | CONFIRMED | Multiple (Neil Patel, pragma-code). Click data "later" per Google. Global availability for this client still unknown |
| 18 | Self-serving review schema restriction | CONFIRMED (and report under-states it) | Google blog 2019/09 "Making review rich results more helpful": reviews about entity A placed on entity A's own site (LocalBusiness/Organization, including via embedded third-party widgets) are not eligible for stars. BrightLocal and Whitespark confirm; no manual action, no ranking effect. Report calls it "not re-verified" and omits the widget case and the "no penalty" fact. Nothing found indicating reversal by 2026. Also: aggregateRating on LocalBusiness is still allowed in markup; it just never produces stars |
| 19 | GBP SAB: hide address; up to 20 service areas; ~2h drive radius | CONFIRMED | Google help answer 9157481 surfaced; 750-char description limit not independently verified (UNVERIFIABLE but widely cited and long-standing) |

## 2. Official vs opinion: where the report is loose

- Properly labelled: Whitespark as "expert opinion"; NavBoost as leak/trial-based; keyword density, LSI, llms.txt flagged as folklore. Good.
- Overstated confidence: Section 1 "Confidence: High on update dates and spam-policy definitions" is fine for dates, but the 2 MB item is listed as "High" without the "clarification, not new limit" caveat.
- "Review text with service+location keywords helps relevance" is flagged medium; should be low (folklore-grade; Google has never stated it).
- "Hide address for SABs" and "up to 20 areas" are official; the report mixes them with vendor items without tags.
- "60-70% unique content" and ">70% shingle similarity" are tripwires invented by vendors/the researcher, not Google thresholds. The agent must label output as heuristic, never as "violation".
- Timelines (3-9 months), "10-30 referring domains can win", "4-8 weeks aggregator propagation": low confidence, should not be shown to clients as facts.
- Section 6 "pack ~93% vs AIO ~15%" and "AI local packs show a third as many businesses (7% of keywords)": single vendor, unverified; do not hard-code.
- The "AI assistants pull from Bing/Foursquare/Yelp/Apple" claim is vendor-sourced (my search: Foursquare >70% of ChatGPT local results, Yelp second, Bing catch-all; also single-vendor claims). It is the ONLY AI-assistant content in this report and is thin for a product whose goal includes being recommended by AI assistants. Other research reports should own it; flag as medium-low.

## 3. Self-serving review schema

Status: still in force as of all sources found; since Sept 2019. Applies to LocalBusiness and Organization (and subtypes) when the reviews are about the business itself and hosted on its own domain, including third-party widgets. Consequence: no star snippet, no penalty, no manual action. Agent should WARN-level "no benefit", not ERROR. Third-party-hosted reviews (Google/Yelp) must not be copied into markup either. Product-type markup for actual products is a separate case.

## 4. Missing items a local-business agent MUST cover

1. Multi-location handling: per-location GBP, per-location landing page with unique content, consistent URL structure, GBP "website" link pointing to the location page (not home), store-locator pages indexable (no JS-only), bulk verification, and an NAP table per location. Report only mentions location pages in passing.
2. Hybrid vs SAB vs storefront classification and its consequences (address display, verification, 2h radius rule, service-area limit of 20). Partly present; no decision logic.
3. Special/holiday hours, temporary closure status, and hours consistency across GBP/site/schema/Apple/Bing (partly present: "holiday hours"; missing the check logic and "open now" implication).
4. Appointment/booking link, menu/order links (restaurants), and products/services lists with prices; GBP primary-category-specific attributes (e.g., dentists: insurance, languages; restaurants: dine-in/delivery, menu; law: free consultation). Mentioned generically, not by vertical.
5. GBP categories: how to pick (competitor categories) and category-specific features. Present; add "category change risk" caution.
6. Call tracking vs NAP: report notes it in section 7 but gives no concrete rule (primary GBP number = main static number, tracking number only as additional/secondary or on site via dynamic swap without altering schema; changing GBP primary number to a call-tracking number hurts citation consistency).
7. Photos/video: count, recency, categories (exterior, interior, team, work), geotag folklore (do NOT recommend EXIF geotagging).
8. Verticals with special rules: YMYL (dentists, law, medical) need credentials/licence numbers, reviewed-by authorship, and regulator-specific advertising restrictions (e.g., bar association rules on testimonials, healthcare claims). Missing entirely. Restaurants: menu pages as HTML not PDF, reservation integrations. Home services: licensing, LSA (Local Services Ads), "Google Guaranteed" screening.
9. Local Services Ads and paid listings: they sit above the pack for plumbers/locksmiths/lawyers; the report ignores them, which affects "rank first" expectations.
10. Voice/maps: Google Maps, Apple Maps (Apple Business Connect), Waze, Bing Places, Siri/Alexa data sources; voice search relies on GBP + Bing/Apple data. Only a one-sentence mention.
11. Duplicate and legacy listings: detect and merge/remove duplicates; marketing-agency-created listings; "permanently closed" competitors; defensive monitoring for suggested edits by third parties (hijacking).
12. Reviews on other platforms (Yelp, Facebook, industry sites like Healthgrades/Avvo/Houzz/TripAdvisor) and review-response policy; review-gating rules now stricter (see April 2026).
13. Local landing page conversion: click-to-call, hours visible, map embed, schema `areaServed`/`geo`/`hasMap`/`sameAs`, and `Service` markup (low value; defer).
14. Reporting honesty: personalised results; rank tracking from the business location only misrepresents (report does cover geo-grid; good).
15. Legal/regulatory: FTC fake-review rule (US, 2024), UK DMCC Act, GDPR for review/SMS outreach. Mentioned for FTC only.

## 5. Agent-actionable checks: reliability

Reliable and automatable (low false-positive):
- robots.txt/sitemap parsing, HTTP status, canonical presence, redirect chains, noindex detection, HTTPS/mixed content, viewport tag, title/H1/meta presence, duplicate titles.
- JSON-LD parse + type presence + NAP-in-schema vs visible-text match (after normalisation).
- PSI/CrUX field data thresholds (but small sites often have NO CrUX data: handle "insufficient data" explicitly, do not report fail).
- Search Status Dashboard polling (JSON/RSS exists; confirmed by dashboard timestamp coverage).
- GBP API data pulls (if approved).

Automatable but risky (expect false positives; present as "review" not "fail"):
- Raw-vs-rendered diff (dynamic content, cookie banners, A/B tests produce noise).
- Shingle similarity >70% for location pages (legit service pages share boilerplate; tune on body content only; vendor-grade threshold).
- "Thin page <250 words" (arbitrary; Google denies word-count thresholds; local contact/map pages are legitimately short). Drop or heavily downgrade.
- Exact-match anchor >10-15% (invented threshold; needs paid backlink data).
- Keyword-stuffed GBP name detection: legitimate names include category words ("Smith Plumbing"). Needs comparison against signage/legal name supplied by owner; otherwise high false-positive rate.
- Intent-vs-SERP page-type matching (requires SERP API, LLM classification; medium reliability).
- NAP crawling of ~25 directories: most sites block scraping/TOS; Yelp/Facebook/BBB are hostile to bots. Use aggregator APIs (Yext/BrightLocal/Whitespark) or manual attestation. Plan for "unable to verify".
- "Google-Extended only controls training" fact: officially it does not govern Search inclusion, but verify before encoding.
- Geo-grid rank checks: reliable only via paid SERP/Places APIs; scraping google.com/maps violates ToS.
- Competitor "review velocity" from Places API: Places returns only 5 most recent reviews; velocity needs repeated snapshots or paid review APIs. Report glosses this.
- AIO/local-pack presence and citation tracking: SERP-API dependent, unstable, geo-sensitive.

Not automatable: GBP suspension/video verification outcomes, policy-compliance judgments on review solicitation behaviour, "does the page have first-hand experience".

## 6. Verdict per section

| Section | Verdict | Reason |
|---|---|---|
| 1 Ranking reality | KEEP, fix | Dates confirmed. Add the explicit "official vs inferred" tags; drop the navboost.com local-pack claim; remove "(local-market businesses winners)" from firm statements |
| 2 Technical SEO | FIX | Reframe the 2 MB item as a clarification with low practical risk; handle CrUX "no data"; remove "Indexing API" aside (irrelevant) or keep as a "don't" |
| 3 On-page & schema | FIX | Upgrade self-serving-review rule to confirmed (2019, widgets included, no penalty). Add "FAQPage markup harmless, remove optional". "Title >60 chars flag" is a pixel-width heuristic; use ~580px or advisory only |
| 4 Local SEO | KEEP core, FIX | Core relevance/distance/prominence confirmed. Resolve Whitespark percentages (19/15). Mark April 2026 policy rules as "vendor-summarised; verify". Add missing items from section 4 above. Drop "keyword-in-title is #3 factor" from any recommendation (keep as warning only) |
| 5 Off-page | KEEP | Reasonable; label thresholds as heuristic |
| 6 AI | FIX | Correct Seer/Ahrefs citations; scope to informational queries; note local-intent exposure is vendor-thin. Add dedicated ChatGPT/Perplexity/Apple/Bing data-source section from another researcher |
| 7 Measurement | KEEP, fix | Add "50,000 rows per day per search type" nuance, PSI/CrUX confirmed. Places API review-count limitation. Verify DataForSEO pricing at build time |
| 8 Sequence | KEEP | Sensible; timelines labelled low-confidence |
| Gaps list | KEEP | Honest and useful |

## 7. Prioritised corrections the builder MUST apply

1. Never encode review-policy rules (April 2026) as hard errors until read from Google's Maps contributed-content policy; encode as WARN with "source: vendor summary".
2. Self-serving review markup: WARN "no star eligibility, no penalty" (not an error); include third-party widget case.
3. Fix AIO CTR citations (Seer: 61% on informational queries, 3,119 queries; Ahrefs: 58% for position 1) and never apply them to local-intent queries.
4. Resolve Whitespark to GBP 32% / reviews 20% / on-page 19% / links 15% / citations ~6%; do not use proximity 55% or the unverified raw scores; ship as "expert opinion" in the UI.
5. Treat 2 MB as informational severity; compute on uncompressed bytes per resource.
6. Add multi-location, SAB/hybrid classification, special hours, call-tracking/NAP rule, per-vertical attributes and YMYL credential checks, LSA awareness, Apple/Bing listings.
7. Mark all numeric tripwires (70% similarity, 250 words, 10-15% anchors, 60-70% unique) as configurable heuristics, default severity LOW/advisory.
8. Handle "no data" (CrUX, GBP API quota 0, GSC AI report not available) as UNKNOWN, not failure.
9. Do not scrape Google Maps/SERPs directly; require licensed SERP/Places/GBP APIs or user-supplied exports.
10. Build an update-freeze rule that reads the live Status Dashboard (Sept 2026 spam update still active as of Oct 3; expected end ~Oct 8) rather than hard-coding dates.
11. Re-verify primary Google docs (spam policies, structured-data gallery, GBP guidelines, review policy, generative-AI guide) at build time with unrestricted network; store doc URLs and a last-verified date in config.
