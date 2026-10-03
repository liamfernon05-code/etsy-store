# Research 01: Google SEO as it works now (as of 2026-10-03), weighted to LOCAL small business

Method note: WebFetch was blocked by the egress proxy for nearly every domain (developers.google.com, status.search.google.com, searchengineland, seroundtable, SEJ and others). Every finding below therefore comes from WebSearch result summaries, not from reading the primary page. Many sources are vendor/agency blogs of mixed reliability. Where Google's own URL surfaced in search results I cite it, but I could not open it. Treat "confidence" accordingly. Items marked [OFFICIAL] are attributed by secondary sources to Google documentation.

Nobody can guarantee #1. Rankings are personalised and location-dependent (especially local), Google changes systems constantly, and competitors act too. The honest goal is: maximise probability of top-3 map-pack and page-1 organic placement for a defined list of money queries in a defined service area, and track it.

---

## 1. Current ranking reality (updates, spam policies, E-E-A-T)

### Findings
**Update timeline (confirmed on Google Search Status Dashboard per press coverage):**
- December 2025 core update: Dec 11 to Dec 29, 2025 (18 days).
- Feb 2026: Discover-only core update (more local relevance, less clickbait). Not a Search ranking update.
- March 2026 spam update: Mar 24-25 (under 20 hours). No new policies; SpamBrain refinement.
- March 2026 core update: Mar 27 to Apr 8, 2026.
- May 2026 core update: May 21 to Jun 2, 2026 (about 12 days, volatile).
- June 2026 spam update: Jun 24-26.
- August 2026 spam update: Aug 18-21.
- September 2026 spam update: began Sep 24, 2026, up to ~2 weeks, so STILL ROLLING OUT as of today. Do not make big site changes or diagnose traffic changes until it completes.
- No August or September 2026 core update was confirmed as of the latest coverage I found (Sept 10). A next core update is plausible in Q4 2026 but unannounced.

**What the core updates reward/punish (analyst consensus, not Google statements):** Google itself says only "create helpful content, nothing special to do." Third-party analyses (e.g. Aleyda Solis on May 2026) report intent match, source type, and originality drove visibility shifts: winners were original sources, specialists, official brand sites, local-market businesses and local domains; losers were aggregators, directories, thin affiliate/AI-generated review content, thin ecommerce pages, and broad "what is X" publishers whose answers AI Overviews now absorb. Small local-service sites showed lower volatility than YMYL/affiliate in the May update. Confidence medium (secondary analyses, no Google winners list).

**Helpful content system** is now part of the core ranking systems (merged March 2024), so there is no separate "HCU" rollout. Google's guidance: people-first content, first-hand experience, a unique point of view.

**Spam policies (codified March 2024, enforced by SpamBrain; 2026 updates refined enforcement rather than adding policies):** scaled content abuse (many pages primarily to manipulate rankings, however produced, AI or human), site reputation abuse (third-party content on a trusted host without close oversight), expired domain abuse, link spam, cloaking, hidden text, doorway pages (explicitly includes many near-identical pages targeting geographic variations), scraped content.

**E-E-A-T:** a framework used in the Search Quality Rater Guidelines (updated Jan 23, 2025 and Sep 11, 2025; the latter widened YMYL to civic/government/elections; added generative-AI definitions and rules for rating AI Overviews; mass-produced unreviewed AI content can be rated Lowest quality). Google's long-standing line: E-E-A-T is not a single ranking factor; raters do not directly change rankings; it informs how systems are evaluated. Practical signal for a local business: visible real people, real addresses, licences/credentials, original photos, genuine reviews, and consistent entity data.

**Evidence tiers (important for an agent deciding where to spend effort):**
- Official/strong: crawlability/indexability, spam policies, Core Web Vitals as a (small) page-experience input, relevance/distance/prominence for local, HTTPS, mobile-friendliness.
- Evidence-backed (DOJ trial testimony 2023-24, May 2024 API leak, reported by many outlets): click/engagement signals via NavBoost (aggregated click data over ~13 months; "clicks are the main signal used by NavBoost" per Google engineer testimony). The leak is a 2024 snapshot of what could be stored, not proof of live weights. A local-SEO site (navboost.com) claims click signals matter in the local pack too; low reliability.
- Folklore / weak: keyword density targets, "LSI keywords", word-count minimums, meta keywords, "freshness by changing dates", schema as a direct ranking boost, domain-authority scores as Google metrics, llms.txt for Google.

### Confidence: High on update dates and spam-policy definitions; medium on "what winners did"; low on exact weights.

### Sources
- https://www.searchenginejournal.com/google-confirms-march-2026-core-update-is-complete/571459/
- https://www.seroundtable.com/google-may-2026-core-update-done-41435.html
- https://www.seroundtable.com/google-december-2025-core-update-completed-40671.html
- https://developers.google.com/search/blog/2026/02/discover-core-update
- https://www.seo-kreativ.de/en/blog/google-september-2026-spam-update/
- https://coalitiontechnologies.com/blog/google-june-2026-spam-update
- https://coalitiontechnologies.com/blog/google-august-2026-spam-update
- https://www.aleydasolis.com/en/ai-search/google-may-2026-core-update-analysis-intent-market-fit-and-source-type-drove-the-biggest-visibility-shifts/
- https://webiano.digital/local-domains-gained-as-googles-may-core-update-reset-search-intent/
- https://www.seroundtable.com/google-search-quality-raters-guidelines-update-40092.html
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://www.kopp-online-marketing.com/what-we-can-learn-from-doj-trial-and-api-leak-for-seo
- https://www.szymonslowik.com/navboost/

### Agent-actionable checks
- Poll the Search Status Dashboard (https://status.search.google.com, it has a JSON/RSS feed) for ranking updates; annotate every traffic chart with update start/end dates; freeze major changes during rollouts.
- Scan the site for scaled/duplicate patterns: count URL templates; flag sets of pages with >70% shingle similarity (esp. city + service combos).
- Flag thin pages (<~250 unique words AND no unique data/images) and pages with no author/business identity signals.
- Verify an About/Contact page exists with real address, phone, named people, licences.

---

## 2. Technical SEO checklist

### Findings
- **Crawl size limit:** Google's crawler docs (reorganised Feb 3, 2026) state Googlebot fetches the first 2 MB of an HTML/supported file (including headers); content beyond is not fetched, rendered or indexed. PDFs 64 MB; other Google crawlers default 15 MB. External JS/CSS each have their own counter. Practical: keep HTML lean, put critical content and links early, move inline JS/CSS/base64 images out. Confidence high (multiple reports citing the doc).
- **Core Web Vitals** (75th percentile of real-user CrUX data, 28-day window): LCP <= 2.5 s good (>4.0 s poor); INP <= 200 ms good (>500 ms poor); CLS <= 0.1 good (>0.25 poor). INP replaced FID in March 2024. CWV is a lightweight tie-breaker/page-experience input; do not expect it to beat relevance. Confidence high on thresholds, medium on ranking weight.
- **Mobile-first indexing:** Google indexes the mobile version; content/structured data/meta must be equal on mobile. Most local searches are mobile, so click-to-call and fast load matter for conversions as well.
- **Indexing hygiene:** one canonical URL per page (self-referencing rel=canonical, absolute URLs, consistent http/https, www, trailing slash); 200 status for indexable pages; no accidental noindex; robots.txt must not block CSS/JS or money pages; XML sitemap lists only canonical, indexable 200 URLs, referenced in robots.txt and submitted in Search Console; note robots.txt blocks crawling, not indexing (use noindex, which needs to be crawlable). A page set to noindex in raw HTML cannot be "un-noindexed" by client-side JS reliably.
- **JS rendering:** Google renders JS with an evergreen Chromium but rendering is queued; server-side render or pre-render core content, links as real `<a href>`, avoid fragments/hash routing, avoid content that only loads on interaction.
- **Internal linking and architecture:** shallow structure (money pages within ~3 clicks of home); descriptive anchor text; hub-and-spoke (services hub -> individual service pages -> location variants where genuinely warranted); no orphan pages; breadcrumbs. Confidence medium-high (Google guidance + broad practice).
- **Security/basics:** HTTPS site-wide, no mixed content, no intrusive interstitials, fix soft 404s and redirect chains (keep 301s single-hop).
- **Don't rely on Google's Indexing API** for normal pages (officially limited to job postings/broadcast events).

### Sources
- https://searchengineland.com/google-explains-how-crawling-works-in-2026-473110
- https://www.searchenginejournal.com/google-updates-googlebot-file-size-limit-docs/566485/
- https://www.debugbear.com/blog/googlebot-crawler-file-size-limit
- https://dev.to/nayankyada/why-core-web-vitals-matter-and-how-i-improve-them-pj3
- https://nitropack.io/blog/most-important-core-web-vitals-metrics/
- Google canonical/robots/sitemap/JS docs under https://developers.google.com/search/docs (not fetched; blocked)

### Agent-actionable checks
- Fetch homepage + key pages as Googlebot-smartphone UA; assert HTTP 200, HTML size < 2 MB (alert > 1 MB), title/H1/main content/links present in raw HTML (diff raw vs rendered via headless Chromium).
- Parse robots.txt: confirm no Disallow on money pages/CSS/JS, Sitemap line present.
- Parse sitemap(s): every URL returns 200, is self-canonical, not noindex; compare against crawl to find orphan/missing pages.
- Check canonical tag presence/consistency, http->https and www redirect single-hop, one `<h1>` per page, `<meta name=viewport>`.
- PageSpeed Insights API (field data from CrUX + Lighthouse lab) for mobile: LCP/INP/CLS vs thresholds; CrUX API for origin-level 75th percentile.
- Search Console URL Inspection API: indexed vs "Discovered/Crawled - not indexed", user vs Google canonical mismatch.
- Detect broken internal links, redirect chains >1 hop, mixed content, pages with zero inlinks.

---

## 3. On-page and content (incl. schema)

### Findings
- **Search-intent matching is the first filter.** Look at the live SERP for each target query: if Google shows a map pack + service pages, the query is local-commercial and needs a service page (not a blog post); if it shows "how to" articles and AI Overviews, it is informational. Match page type to what ranks.
- **Local-business page set that works:** homepage (entity, primary service + area), one page per core service (unique copy, pricing/process, FAQs from real calls, original photos, proof/case studies, reviews, clear CTA and phone), a location page per physical location (see section 4), About/team, Contact, and supporting content that answers real customer questions (costs, timelines, comparisons) written by someone with first-hand experience.
- **Titles/meta/headings:** title ~50-60 chars (display is pixel-based), primary keyword + modifier (service + city) + brand; unique per page. Google rewrites titles when they mismatch content (H1/title divergence increases rewrites) and rewrites meta descriptions the majority of the time (Portent study of 70k URLs: ~62%), so write descriptions for CTR but expect substitution. One H1 aligned with title; logical H2/H3.
- **Content depth** is about completeness vs. the intent, not a word count. Pages that merely summarise the top 10 without original data, experience, or perspective are consistent core-update losers (analyst consensus). For local: original photos of real jobs, named staff, specific neighbourhood details, pricing ranges, and real customer stories are differentiators competitors and AI cannot copy.
- **Freshness:** matters for time-sensitive queries; for evergreen service pages, genuine updates (new projects, prices, reviews) not date-bumping.
- **Images:** descriptive file names/alt text, compressed WebP/AVIF, explicit width/height (prevents CLS), original not stock where possible.
- **Structured data (JSON-LD is the only format Google recommends):**
  - Still produce Google rich results: Organization, LocalBusiness (most specific subtype, e.g. Plumber/Dentist/Electrician; name+address required, recommended: telephone, url, geo, openingHoursSpecification, priceRange, image, sameAs), BreadcrumbList, Article, Product snippets/merchant listings (keep minimal for this client), Review snippet, Video, Event, JobPosting, etc.
  - **Self-serving reviews caveat:** Google does not show review stars for LocalBusiness/Organization markup that reviews the business itself on its own site (long-standing policy; I could not re-verify in 2026 docs). Do not mark up your own testimonials expecting stars.
  - **Deprecated/removed:** HowTo rich results (2023); FAQ rich results fully ended May 7, 2026 (restricted to gov/health since Aug 2023; FAQ report/filter/Rich Results Test support removed June 2026; Search Console API support ended August 2026); in June 2025 Google retired seven other displays: Book Actions, Course Info, ClaimReview, Estimated Salary, Learning Video, Special Announcement, Vehicle Listing. FAQPage markup may be left in place harmlessly but earns no Google rich result. (Sitelinks search box was also retired in 2024.)
  - Google's May 2026 generative-AI guide says no special structured data is needed for AI features. Schema helps entity understanding and consistency with GBP; it is not a ranking lever by itself.

### Confidence: High on FAQ/HowTo deprecations and JSON-LD recommendation; medium on title/meta stats and content-depth heuristics; medium on LocalBusiness property specifics (secondary sources).

### Sources
- https://www.searchenginejournal.com/google-drops-faq-rich-results-from-search/574429/
- https://almcorp.com/blog/google-faq-rich-results-no-longer-supported/
- https://developers.google.com/search/docs/appearance/structured-data/search-gallery
- https://www.searchenginejournal.com/google-is-not-diminishing-the-use-of-structured-data-in-2026/560516/
- https://www.getpassionfruit.com/blog/what-changed-with-google-drops-faq-rich-results-and-what-to-do-now
- https://dev.to/saltalash/sal-talash-localbusiness-structured-data-done-right-the-json-ld-google-reads-and-the-rules-that-5e3o
- https://seranking.com/blog/title-tags-and-meta-descriptions-in-seo/

### Agent-actionable checks
- Extract JSON-LD from every page; validate JSON; check LocalBusiness subtype is specific; name/address/telephone/openingHours EXACTLY match GBP and visible page text; flag deprecated types being relied on (FAQPage/HowTo expecting rich results) and self-review markup on LocalBusiness.
- Per page: title length (flag >60 chars / duplicates / missing), meta description presence and uniqueness, exactly one H1, H1 contains primary term, images with alt and dimensions, internal links count.
- Compute near-duplicate similarity across service/location pages; flag >70% overlap.
- Compare each money page's target query against live SERP features (use a SERP API) to confirm page type matches intent.
- Check each page has a phone number as a `tel:` link and a visible NAP block on mobile.

---

## 4. Local SEO (highest priority for this client)

### Findings
**Google's official local ranking model [OFFICIAL, support.google.com/business/answer/7091]:** relevance (how well the profile matches the query), distance (to searcher or searched location), prominence (how well known: reviews, links, citations, web presence). Distance cannot be optimised after the address is chosen, so the controllable levers are relevance and prominence.

**Whitespark 2026 Local Search Ranking Factors (survey of 47 experts, published Nov 2025, 187 factors; the best structured public source, but it is expert opinion, not Google data):**
- Local pack/Maps top three: primary GBP category (score ~227), proximity to searcher (~225), keywords in GBP business title (~223).
- "Business is open at time of search" reported as 5th most important pack factor; review recency ranked about 11th; engagement quality and in-store-visit signals rose; social signals newly appear.
- Category weights reported in secondary summaries: GBP signals ~32%, reviews ~20% (up from ~16% in 2023), citations ~6-7%, behavioural ~9%, personalization ~6%. On-page and links figures conflict between summaries (on-page 15% vs 19%, links 8% vs 15%), so do not rely on those two; check whitespark.ca directly.
- Practical reading: GBP completeness/category accuracy + a steady stream of fresh genuine reviews + a strong, locally relevant website are the core. Citations are a hygiene factor (confirm NAP, reduce conflicts) not a growth lever.

**GBP optimisation checklist (consistent across sources):**
- Verified profile; most specific PRIMARY category (single biggest lever) plus relevant secondary categories; do not add categories you do not genuinely offer.
- Business name = real-world name only. Keyword-stuffing the title is the top-ranked factor but is a policy violation and a major suspension trigger. Never recommend it.
- Complete: hours (incl. holiday hours; "open now" matters), services list with descriptions, products if relevant, service areas (limit to areas you really serve; up to 20 areas), description (750 chars max; influences CTR/relevance rather than directly ranking), attributes, appointment/booking link, website URL pointing to the correct landing page, 10+ original photos plus regular new uploads, posts/updates and offers.
- Hide address for pure service-area businesses (SABs) per Google guidelines; use a real address for storefronts. Virtual offices/PO boxes are suspension risks.
- Q&A feature was discontinued: API ended Nov 3, 2025 and public Q&A is being removed; Gemini-powered "Ask Maps" now answers questions from profile, reviews, photos and website. Implication: put FAQs, policies, parking, pricing hints into website content, GBP description/services, and reviews, because that's what Ask Maps draws from. Customers can also suggest edits conversationally.

**Reviews:**
- April 2026 policy changes (Apr 16-17 per vendor coverage): bans on review gating (filtering by sentiment), pressuring customers on premises, review kiosks/shared in-store tablets, asking customers to name staff in reviews; stronger pre-publication detection of coordinated fake review campaigns; visible warnings on profiles with fake-review activity; repeat violators restricted or suspended. Confidence medium (vendor blogs summarising Google's policy pages; verify against Google's Maps user-contributed content policy before encoding rules).
- Approach: ask every customer (not only happy ones) via a direct Google review link by SMS/email after service; respond to every review (thank positives, address negatives factually and politely); aim for steady velocity and recency rather than bursts; never buy, swap or incentivise reviews. FTC rules on fake reviews also apply (US).
- Review text containing service + location keywords appears to help relevance (industry belief, medium confidence).

**Suspensions:** a wave of "Deceptive Content" suspensions around Apr 27, 2026 hit legitimate profiles (reported by agencies). Recovery usually involves video verification showing the premises, signage, equipment and ownership proof. Video verification does not give immunity. Keep documentation (licences, utility bill, signage photos) ready; avoid edits to name/address/category without need; do not create duplicate profiles.

**Citations/NAP:** keep Name, Address, Phone identical on GBP, website, schema and listings. Priority: Apple Business Connect, Bing Places, Facebook, Yelp (where relevant), BBB, data aggregators (Data Axle, Foursquare; Neustar/Localeze) and 5-10 industry-specific directories. Aggregator corrections propagate in ~4-8 weeks (vendor claim). Low-authority bulk citations are discounted; spam directories risk link-spam flags.

**Service-area and location pages (doorway risk):**
- Google's spam policy flags many similar pages targeting geographic variations as doorway pages. Create a location page only when there is a real place (office/branch), or a genuinely distinct service area with distinct content (local projects done there, local team, local pricing/regulations, local testimonials, embedded map, unique photos). One broad "areas we serve" page plus a handful of strong, unique city pages beats 100 templated pages.
- Vendor rule of thumb "60-70% unique content per page" is folklore-grade but a sensible tripwire.
- Use LocalBusiness/Service schema with areaServed consistent with the GBP service areas.

**"Near me" and local-intent queries:** simple "near me"/"[service] [city]" queries trigger the local pack for most searches (one source: pack ~93% vs AI Overview ~15%); the pack is driven by GBP, not by the website title. Do not stuff "near me" into pages; ensure location is in titles, H1, NAP, and GBP service areas. Google determines location from device signals.

**AI local packs:** reports (early 2026) of AI-generated local packs showing about a third as many unique businesses as the traditional 3-pack on some queries (about 7% of tracked keywords). Medium-low confidence (vendor research); implies being #1-2 matters even more, and reviews/GBP content feed the AI summaries.

### Confidence: High on relevance/distance/prominence and GBP basics; medium on the Whitespark weights (survey) and 2026 policy details (secondary); low-medium on AI local pack figures.

### Sources
- https://support.google.com/business/answer/7091?hl=en
- https://whitespark.ca/local-search-ranking-factors/
- https://sambretzmann.com/2026-local-seo-ranking-factors-overview/
- https://gmbapi.com/news/local-ranking-factors-comparison-2026-2023/
- https://launchcodex.com/blog/seo-geo-ai/google-business-profile-review-policy-update/
- https://birdeye.com/blog/google-review-policy/
- https://www.jcerme.com/news/google-business-profile-mass-suspension-wave-april-2026
- https://www.reinstatelabs.com/blogs/google-business-profile-video-verification
- https://www.impactmarketing.net/blog/google-business-profile-qa/
- https://www.excitecs.com/8494/goodbye-qa-hello-ask-maps-what-googles-latest-update-means-for-your-business/
- https://splinternetmarketing.com/digital-strategy/city-pages-doorway-risk-and-site-reputation-abuse-in-2026/
- https://www.webmoves.net/how-many-service-area-pages-should-you-have/
- https://onpurposemedia.com/ai-overview-local-packs-impacting-visibility/
- https://thestacc.com/blog/ai-overviews-local-search-impact/
- https://www.w3era.com/blog/local-seo/local-seo-citations-usa/
- https://direction.com/resources/local-citation-aggregators/

### Agent-actionable checks
- GBP audit via Business Profile APIs (needs approval, see section 7) or manual export: primary category vs top-3 map-pack competitors' categories (scrape/Places API), missing secondary categories, hours/holiday hours set, services populated, photo count and last upload date, description present, website URL correct, address hidden for SAB, name equals legal/signage name (flag keyword-stuffed names).
- Reviews: count, average, velocity (reviews/month over last 90 days), % with owner reply, median reply latency, days since last review versus competitors.
- NAP consistency: crawl website footer/contact/schema/GBP and a defined list of ~25 directories; normalise (phone E.164, address abbreviations) and report mismatches/duplicates.
- Local rank grid: run geo-grid map-pack rank checks (e.g. 5x5 or 7x7 around the business) for 5-20 money keywords monthly; record share of grid in top 3.
- Location pages: detect templated duplicates, require unique elements (local project, photo, review, map embed); check each has NAP, LocalBusiness schema, internal links from the hub page.
- Run a competitor benchmark for the top 3 map-pack businesses per keyword: category, review count/rating/velocity, photo count, GBP name, website page that GBP links to, referring domains.

---

## 5. Off-page: links, PR, mentions

### Findings
- Links remain a significant prominence/authority signal (Google's local prominence definition explicitly includes links to the business); Whitespark shows links as a meaningful but non-dominant local factor.
- **White hat (editorial, publisher's discretion):** local press and community news, sponsorships (local clubs/charities/events) that credit you, supplier/manufacturer/partner pages, chamber of commerce and trade-association memberships, local business associations, university/college partnerships, data-led local studies (original local stats journalists cite), useful local resources/tools, expert quotes for local reporters, unlinked-mention reclamation, genuinely useful guest content on relevant local sites.
- **Penalised / ignored (Google link spam policy):** buying or selling links that pass ranking credit (use rel=sponsored/nofollow), excessive link exchanges, automated link creation, low-quality directory spam, keyword-rich anchor text in guest posts/press releases at scale, PBNs, hacked-site links, expired-domain abuse. SpamBrain neutralises most spam links algorithmically, and the 2026 spam updates continue refining this; manual actions are still possible. Disavow is generally unnecessary unless there was a manual action or a clear paid-link history.
- **Brand mentions:** unlinked mentions and brand search volume are useful correlates and feed AI answers; Google's 2026 AI guide specifically warns against seeking "inauthentic mentions across the web" (secondary report). Pursue real PR, not mention seeding.
- Realistic small-business benchmark: 10-30 genuinely relevant local referring domains can beat competitors in non-competitive niches; compare against the top 3 competitors' referring-domain counts (a requirement for knowing whether links are your gap).

### Confidence: High on what is spam (Google policies); medium on tactic effectiveness (practitioner consensus).

### Sources
- https://bluetree.digital/google-backlink-policy/
- https://www.relevantaudience.com/seo/link-building-guide-2026/
- https://tocayo.me/resources/white-hat-link-building-small-business-2026
- https://www.igniteseo.co.uk/how-to-build-white-hat-backlinks-in-2026/
- https://www.searchenginejournal.com/googles-new-ai-search-guide-calls-aeo-and-geo-still-seo/575026/
- Google link spam policy: https://developers.google.com/search/docs/essentials/spam-policies (not fetched)

### Agent-actionable checks
- Pull the backlink profile (Search Console Links report export; Ahrefs/Semrush/DataForSEO Backlinks if budgeted); flag exact-match anchor over-concentration (>~10-15% commercial anchors), links from known link-farm patterns, and sponsored links without rel attributes on the client's own outbound links.
- Check Search Console Security & Manual Actions report for manual actions.
- Build a prospect list of local linkable entities (chamber, suppliers, associations, sponsored events) and diff against competitors' linking domains.
- Monitor new brand mentions (Google Alerts-equivalent via search API) for reclamation.

---

## 6. AI Overviews / AI Mode

### Findings
- **Google's official position (May 15, 2026 guide, updated Jun 5):** optimising for generative AI search is "still SEO." No llms.txt, no special AI markup, no content chunking or AI-specific rewrites needed; AI features use RAG and query fan-out over the Search index; don't create pages for every query variation; don't seek inauthentic mentions. Doing the same fundamentals (crawlable, indexable, helpful, unique POV, good page experience, media) is the recommendation. Confidence high that this is the stated position (several outlets: SEJ, Semrush, SEO Strategy Ltd).
- **Traffic impact (third-party studies, 2025-26):** where an AI Overview appears, organic CTR falls substantially (Seer: ~61% reduction across 5.47M queries; Ahrefs: ~58% lower CTR for the top result on 300k keywords; sessions with AIO see fewer clicks on any result), but pages cited in the Overview get materially more clicks than uncited ones. AIO prevalence on informational queries is high (some datasets 48% of queries); on local-intent queries it is much lower, with the map pack dominating. Confidence medium: figures from vendors with differing methodologies; direction is consistent.
- **Implication for a local business:** informational blog traffic is the part most at risk; bottom-funnel local/commercial queries (service + city, "near me", emergency) are the most protected and are where leads come from. Prioritise those, and make informational content original (cost data, process, local specifics) so it gets cited.
- **Measurement now exists:** Search Console Generative AI performance reports launched Jun 3, 2026 (initially a subset of UK sites; impressions, pages, countries, devices, dates; no clicks/CTR/queries; data from May 18, 2026, no backfill). Web multimodal (image-driven search) reporting began rolling out globally Sep 24, 2026. Check whether the client's property has these reports and whether API access exists.
- **Local specifics:** AI-generated local packs and Gemini "Ask Maps" draw on GBP data, reviews, photos and website content, so GBP/review quality doubles as AI visibility. Other assistants (ChatGPT, Perplexity, Apple Maps) pull from Bing/Foursquare/Yelp/Apple data, which is another reason to keep Bing Places, Apple Business Connect and major directories accurate (note this multi-platform point is vendor-sourced).
- "GEO/AEO" vendor claims (e.g. "FAQ schema makes you 3.2x more likely in AI Overviews") are correlational vendor statistics; do not treat as causal.

### Sources
- https://www.searchenginejournal.com/googles-new-ai-search-guide-calls-aeo-and-geo-still-seo/575026/
- https://www.semrush.com/blog/google-publishes-generative-ai-search-guide/
- https://www.seostrategy.co.uk/llm-optimisation/google-ai-optimisation-guide-2026/
- https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-2026-update
- https://www.relevantaudience.com/seo/ai-overview-impact-on-organic-search-2026/
- https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports
- https://neilpatel.com/blog/gsc-ai-search-data-generative-ai-report/
- https://developers.google.com/search/blog/2026/09/web-multimodal-in-sc
- https://searchengineland.com/guide/how-ai-is-impacting-local-search

### Agent-actionable checks
- For each target keyword, record via SERP API whether an AI Overview and a local pack appear, and whether the client is cited in/under the AIO.
- Verify Googlebot is not blocked by robots.txt/WAF/CDN bot rules (Google-Extended only controls training use, not Search inclusion); check for nosnippet/max-snippet restrictions that would limit AI usage.
- Pull Search Console Generative AI report data if the property has it; log impressions by page.
- Confirm answer-worthy facts (services, prices/ranges, hours, areas, policies) exist as plain crawlable text on the site.

---

## 7. Measurement and data sources an agent can use

### Findings
- **Search Console (free):** Search Analytics API (up to 25,000 rows per request, 50,000 rows/day/site/search type exposed; 16 months of retention; bulk export to BigQuery has no row limits but only goes forward from setup, so enable it on day one), URL Inspection API, Sitemaps API, Links report (UI export). FAQ rich result API support ended Aug 2026.
- **GA4:** Data API (free quotas); track organic landing-page sessions, plus key events: calls (tel: clicks), form submits, direction clicks, booking clicks. For local businesses, calls are the real KPI; consider call tracking (dynamic numbers must not change the NAP on the site: use a static main NAP and swap only in GA/ads contexts).
- **GBP data:** Business Profile Performance API (search keyword impressions, calls, direction requests, website clicks, messages) and Reviews API need Google approval (basic API access request form; quota 0 until approved, 300 QPM once approved; Google says reviews within ~14 days, forum reports vary). Fallback: manual dashboard export or paid tools.
- **Free/cheap APIs:** PageSpeed Insights API (25,000/day, 240/min), CrUX API (150 QPM), Google Places API (competitor ratings/review counts; paid per request beyond free tiers, check current pricing), Google Trends (unofficial), Keyword Planner (needs Google Ads account), Google autocomplete/People Also Ask scraping (respect ToS).
- **Rank tracking:** Search Console avg position is an impression-weighted average, not a rank. For local use geo-grid tracking: Local Falcon, BrightLocal, Local Viking (~$20/mo), free grid tools (e.g. Grid My Business) or build on a SERP API; DataForSEO pay-as-you-go (reported ~$0.0006 standard queue to $0.002 live per SERP, $50 minimum deposit; verify current rates; it has a Local Pack/Maps SERP endpoint). Always check rank at the true service locations (lat/long), mobile, logged-out.
- **Third-party backlink/keyword data** has no meaningful free API (Ahrefs/Semrush paid; Ahrefs Webmaster Tools gives free data for verified own site).
- **Cadence:** baseline in week 0; weekly technical/GSC checks; monthly grid rank + review velocity + competitor benchmark; annotate algorithm updates.

### Confidence: High on GSC/PSI/CrUX limits (multiple sources); medium on GBP API approval specifics and DataForSEO pricing (vendor sources, may change).

### Sources
- https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data
- https://www.searchcans.com/blog/google-search-console-api-limits-explained/
- https://getdadseo.com/blog/gsc-data-retention-explained
- https://unlighthouse.dev/learn-lighthouse/pagespeed-insights-api
- https://developers.google.com/my-business/content/limits
- https://developers.google.com/my-business/content/prereqs
- https://localith.ai/blog/google-business-profile-api-guide/
- https://www.mapsleads.co/blog/google-business-profile-api-quotas-limits
- https://www.sitepoint.com/5-best-data-for-seo-alternatives-a-senior-expert-breakdown/
- https://www.flento.io/blog/best-local-falcon-alternative-2026
- https://ahrefs.com/blog/google-seo-tools-explained/

### Agent-actionable checks
- Verify the client owns/has delegated access to Search Console (domain property), GA4, and GBP before starting; verify BigQuery export is on.
- Confirm GA4 key events for calls/forms/directions are firing (test with real events) and are marked as key events.
- Smoke-test API credentials (PSI key, GSC OAuth service account added as user, GBP API quota not 0).
- Store a dated baseline snapshot (queries, pages, positions, review stats, grid ranks) so the effect of each change is attributable.

---

## 8. Step-by-step sequence: how to become #1 in a niche

Reality check first: "#1" must be defined as (a) a set of ~10-30 specific money keywords, (b) in specific locations (grid points), (c) in the map pack and organic, on mobile. A business with the wrong location or a thin footprint cannot always beat entrenched competitors near the searcher (distance is un-optimisable). Typical timelines: GBP/review fixes can move the pack in weeks; competitive organic positions usually take 3-9+ months; nothing is guaranteed.

1. **Define business, offer, margins, service area.** List services by profit, capacity and real service radius. Confirm GBP eligibility (storefront vs service-area business) and address legitimacy.
2. **Technical/health baseline (week 1).** Run the section 2 checklist; fix indexing blockers, canonical/redirect issues, mobile and CWV failures first; they gate everything else.
3. **Keyword/niche selection (week 1-2).** Build the seed list from: services x modifiers (emergency, cost, near me, best, repair/installation), neighbourhood names, GSC queries already showing impressions (positions 5-30 are the cheapest wins), GBP search-keyword data, Google autocomplete/PAA, competitor titles/categories. Classify intent (local-commercial, informational, navigational). Record volume (Keyword Planner ranges), SERP type (pack present? aggregators dominating?), and difficulty proxy (competitor review counts, referring domains).
4. **Competitor gap analysis (week 2).** For each target keyword, take the top 3 pack businesses and top 5 organic results and tabulate: GBP primary/secondary categories, review count/rating/recency, photo count, GBP posts, service pages present, content depth, schema, referring domains, citations count/consistency, page speed. Gaps = rows where the client trails. Flag aggregator-dominated SERPs (Yelp, Angi etc.) as lower-probability for organic but still winnable in the pack.
5. **Prioritise by impact x effort x confidence** (rough order for a local business):
   1. Fix GBP: correct primary category, complete all fields, services, photos, hours, link to the right page (low effort, high impact in the pack).
   2. Launch a compliant review-generation process and reply workflow (medium effort, high impact; compounding).
   3. Fix website basics: service pages with unique content for each money service, title/H1 alignment, NAP/schema, click-to-call, speed (medium effort, high impact).
   4. Citation/NAP cleanup on top ~25 sources and aggregators (low-medium effort, hygiene).
   5. Build a small number of genuine location/area pages (only where real).
   6. Local link building and digital PR (high effort, high long-term impact).
   7. Informational/supporting content (original data, costs, process) for the topic cluster and AI citation (medium-high effort, medium impact; deprioritise generic "what is" posts that AIO absorbs).
   Defer: schema tinkering, meta description rewriting, llms.txt/GEO tricks (low expected impact).
6. **Execute in 30/60/90-day sprints**, one measurable change cluster at a time; avoid changing everything simultaneously so effects can be attributed; avoid big changes during an active update rollout.
7. **Measure and iterate monthly:** geo-grid pack share, organic positions/clicks (GSC), calls/forms (GA4/call tracking), review velocity/rating, referring domains, AI Overview presence/citation. Double down on what moves leads, not just rank.
8. **Guardrails (what not to do):** no review gating/buying, no keyword-stuffed GBP name, no fake addresses/virtual offices, no templated city-page farms, no mass AI content without human original input, no paid links without rel=sponsored, no cloaking. These are the fastest routes to suspension or demotion.

### Confidence: Medium-high on the framework (standard practice consistent with Google's guidance); timelines are experience-based estimates (low-medium).

### Agent-actionable checks
- Produce a prioritised backlog automatically: score = (estimated impact 1-5 x confidence 1-5) / effort 1-5, using gap-table severity.
- Track target list and "state of #1": for each keyword x grid point, store pack rank and organic rank; report share-of-grid-in-top-3 and organic rank trend.
- Alert triggers: GBP status change/suspension, sudden review drop, indexing drops in GSC, CWV regression, NAP mismatch introduced, a competitor's review velocity spiking.

---

## Gaps / things I could not verify

1. Primary Google documentation could not be opened (developers.google.com, status.search.google.com blocked), so spam policy wording, structured data gallery contents, the May 2026 generative-AI guide wording, GBP guideline text and the GBP review policy were verified only via secondary summaries. An agent with unrestricted access should re-read: Google's spam policies, the Search Status Dashboard, the generative-AI features doc, GBP guidelines and the Maps contributed-content (reviews) policy.
2. Exact April 2026 GBP review-policy change details (dates, kiosk ban, staff-name ban) come from vendor blogs; confirm against Google's policy pages before encoding rules in an agent.
3. Whitespark 2026 category percentages conflict across summaries (on-page 15% vs 19%; links 8% vs 15%); only the top-3 pack factors and the GBP 32% / reviews 20% figures were consistent. The original report at whitespark.ca was not read.
4. Whether the Search Console Generative AI report has reached non-UK properties/the client's property: unknown (June launch was a UK subset; global multimodal reporting was Sep 24).
5. Whether the self-serving review-schema restriction and the "no review stars for LocalBusiness" rule remain unchanged in 2026 docs: not re-verified.
6. Whether a new core update is scheduled: no announcement found; the September 2026 spam update is mid-rollout (started Sep 24), so end date unconfirmed.
7. Click/CTR figures for AI Overviews vary widely across vendors (58-67% drops); methodology differences not assessed. Local-specific AIO data is thin and vendor-sourced.
8. Current pricing/quotas for Places API, DataForSEO and Local Falcon, and the real-world turnaround time for GBP API approval, were not verified at the source.
9. No independent evidence found on exact ranking weights of CWV/INP for local sites, nor of NavBoost in the local pack (only a vendor claim).
10. Not covered in depth (by scope instruction): ecommerce/Merchant Center, international/hreflang, video SEO, and Bing/other engines.
