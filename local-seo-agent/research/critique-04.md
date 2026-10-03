# Critique of 04-strategy-and-architecture.md (Critic 4 of 4, 2026-10-03)

Overall: a strong, honest report. Its confidence labelling is better than most. The problems are (a) a few stale or misattributed facts, (b) an architecture that is described as an MVP but is really a phase-3 system, (c) AI-visibility measurement that is statistically and cost-wise naive, and (d) local-specific blind spots. Details below.

## 1. Spot-checks (14 claims)

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | FTC rule 16 CFR 465 penalty "$51,744 per violation (confirm current)" | WRONG (stale). The Jan 2025 adjustment made it $53,088, and sources say no 2026 adjustment was made (shutdown disrupted CPI data). A Federal Register notice dated 2026-09-15 exists, so recheck once more. | https://www.federalregister.gov/documents/2025/01/17/2025-01361/adjustments-to-civil-penalty-amounts ; https://www.federalregister.gov/documents/2026/09/15/2026-18853/civil-penalty-inflation-adjustments |
| 2 | Model IDs and prices: opus-5-5 $4/$20, sonnet-5-5 $2/$10, haiku-4-5 $1/$5, cache read ~0.1x | CONFIRMED. Sonnet 5.5 launched 2026-09-28, cache read $0.20. One site also lists a "Fable 5.1" tier the report never mentions. | https://benchlm.ai/anthropic/api-pricing ; https://www.eesel.ai/blog/claude-sonnet-5-5-pricing |
| 3 | GBP API: 0 QPM until approved, ~300 QPM after, verified GBP 60+ days with website, ~14-day review | CONFIRMED. The ">50% usage or denied" claim is UNVERIFIABLE. A forum thread reports 6+ weeks with quota still 0, so "~2 weeks" is optimistic. | https://developers.google.com/my-business/content/limits ; https://discuss.google.dev/t/api-gbp-basic-access-quota-still-0-qpm-after-6-weeks-two-case-ids/398811 |
| 4 | PSI: 25,000/day, ~240/min | CONFIRMED (400 per 100 s = 240/min). | https://dev.to/addyosmani/monitoring-performance-with-the-pagespeed-insights-api-33k7 |
| 5 | GSC: 1,200 QPM per site; 40,000 QPM and 30M QPD per project; URL Inspection 2,000 QPD and 600 QPM per site | CONFIRMED. The "50,000 rows/day" figure was not re-verified. | https://developers.google.com/webmaster-tools/limits (search snippets) |
| 6 | GA4: 200,000 tokens/day, 40,000/hour (standard) | CONFIRMED. | https://aelmgren.com/guides/ga4/ga4-limits-reference |
| 7 | DataForSEO $0.60 / $1.20 / $2.00 per 1k SERPs, $50 minimum | CONFIRMED for organic SERP. Maps/local endpoints are priced differently (the report says so but still builds the $0.12/scan budget on the organic rate). | https://dataforseo.com/apis/serp-api |
| 8 | SerpApi $0/250, $25/1k, $75/5k, $150/15k, $275/30k | CONFIRMED. | https://costbench.com/software/web-scraping/serpapi/ |
| 9 | Whitespark 2026: 47 experts, 187 factors; GBP 32%, reviews 20%, on-page 15% | CONFIRMED. The real primary URL exists (https://whitespark.ca/local-search-ranking-factors/) and the builder should cite it. | https://w3marketinghub.com/seo/local-seo-ranking/ |
| 10 | Ahrefs 1.74% (2025) / 5.7% (2017); avg #1 page ~5 years old | CONFIRMED. The report cites "1.7% to 5.7%" as a range, but these are two different years (a trend), not a range. | https://ahrefs.com/blog/how-long-does-it-take-to-rank-in-google-and-how-old-are-top-ranking-pages/ |
| 11 | AI visibility stats 1.2% / 7.4% / 11% vs 35.9% | CONFIRMED but misattributed. The source is SOCi's 2026 Local Visibility Index, not a personal blog. SOCi also says Gemini is grounded in Google Maps, so Gemini's higher rate is structural. | https://www.soci.ai/blog/how-to-rank-in-chatgpt-perplexity-and-google-ai-overview/ |
| 12 | Google Programmable Search / Custom Search JSON API "LOW, unverified" | CONFIRMED as a real hazard. The API is closed to new customers and shuts down 2027-01-01. The report's confidence is too low here. | https://dev.to/nexgendata/google-kills-custom-search-api-on-jan-1-2027-you-have-9-months-1jg1 |
| 13 | Web-search tool costs: OpenAI $10/1k, Gemini 3 5,000 free then $14/1k, Perplexity Sonar $1/$1, Pro $3/$15 | CONFIRMED, but incomplete. Perplexity also charges $5-14 per 1k requests. Gemini 3 bills per query executed, not per prompt. Anthropic's web-search price ($10/1k) is confirmed only for older models, not Sonnet/Opus 5.5. | https://developer.puter.com/tutorials/perplexity-api-pricing/ ; https://ai.google.dev/gemini-api/docs/pricing |
| 14 | Agent SDK: API-key auth only; branding "{Name} Powered by Claude"; not "Claude Code" | CONFIRMED. | https://code.claude.com/docs/en/agent-sdk/overview |
| 15 | Google review policy (gating, incentives banned); "April 2026 update" | Core rules CONFIRMED. April 2026 changes (no staff-name solicitation, no on-premises/shared-device reviews) are reported by several vendors but not verified against Google. | https://launchcodex.com/blog/seo-geo-ai/google-business-profile-review-policy-update/ |

## 2. Overclaims, folklore, contradictions

- **Invented numbers presented as heuristics.** The "<100 reviews or <4.3 rating = winnable" and "500+ reviews = not winnable" thresholds are labelled "my synthesis" but then drive a winnable/stretch/not-yet verdict. The five sub-scores have no weights and no validation. Ship the scorer as "heuristic v0, uncalibrated" and show the client the raw evidence, not a confident label.
- **AI-visibility sampling is statistically weak.** 5 runs per prompt gives a 95% interval of roughly +/-35 points at p=0.2, so week-to-week "trends" are noise. The report says "report CI" but specifies n=5. Require pooled estimates (prompts x runs x weeks) with Wilson intervals, and ban "up/down" language unless the intervals separate.
- **Probe cost is understated by an unknown factor.** The "$4.50/week/client" figure assumes one search per call. Gemini 3 bills per query executed, models fire several searches per answer, and search results are billed as input tokens (often 10-30k tokens). The real figure is plausibly 3-10x higher (my estimate; measure it). The report also adds Opus-class thinking that "cannot be disabled" on the orchestrator and drafter, which makes cost hard to cap. A hard per-run token and spend ceiling must live in the loop, not just in a "budget meter".
- **Probes ignore geography.** For local queries the retrieval location is the whole game. The report never mentions setting `user_location` on web-search tools, or that Gemini/AI Overviews use Maps data. Without this the probe measures "best dentist in [city]" for an IP in a datacentre. This is a MUST fix.
- **Wrong or missing AI data sources for local.** Secondary analyses say ChatGPT's local results lean on Foursquare (an OpenAI partner), Yelp and Bing, while Gemini is grounded in Google Maps (https://www.surfacelocal.com/blog/how-chatgpt-finds-local-businesses ; vendor claims, MED-LOW). The report never names Foursquare. It also says Gemini "leans on the business's own website more", which conflicts with the SOCi Maps-grounding finding. The per-assistant "citation map" is the right idea, but the starting seed list is incomplete.
- **Schema advice risks hallucinated SEO.** The report suggests "Review aggregate where compliant" and FAQPage. Self-serving LocalBusiness review markup is ineligible for rich results under Google's guidelines, and FAQ rich results have been restricted to a small set of authoritative sites since 2023. (From my background knowledge; the builder should confirm in Google's structured-data docs before the schema skill encodes them.) The agent must not promise rich-result gains.
- **Tension on scraping.** "Scraping Google directly violates terms; use a SERP API" is stated as HIGH, yet SERP APIs are scraping vendors. Say so plainly and mark SERP provider as a swappable adapter. Also note Yelp/directory ToS limits on storing competitor review data.
- **Reddit drafting.** "Draft answers for the owner to post" invites astroturfing and platform bans. Drop from MVP (it is already human-only, but the template library should not ship).
- **Confidence inflation.** Items rated HIGH for "Google's three factors" cite a blog; the FTC penalty rated MED was actually wrong. The pattern "HIGH = well-established" is fine for principles, not for numbers. Re-label the numbers as dated, with a "verified-on" field.
- **Internal inconsistency.** B1 recommends "thin custom orchestrator, Client SDK for MVP", but the tables define 8 LLM agents with per-agent models, an Opus orchestrator, a quarantined reader, and a compliance LLM. The repo tree has 7 agent modules. "1,500-2,500 lines, one session" cannot include all of: SSRF-safe fetch with DNS pinning, robots handling, SERP adapter, scorer, extractor, evals, CLI, injection fixtures.

## 3. Architecture: what breaks in production

1. **Over-engineered for an MVP.** This is a deterministic pipeline (crawl -> parse -> score -> report) with LLM calls at three points (page-level extraction, interpretation, drafting). It does not need a planning orchestrator or subagent hierarchy. Build `audit`, `ai-probe`, `plan`, `report` as plain functions with Pydantic hand-offs; add an LLM judge/compliance pass only on the final artefact.
2. **Prompt injection design has a hole.** The "quarantined reader returns strict JSON" idea is good, but any free-text field (summary, "services offered", "tone") flows downstream into content drafts and reports and carries the payload. Constrain extracted fields to enums, numbers, short length-capped strings, or quote-verified spans; never feed reader free text into a tool-using or drafting prompt. Also scan competitor pages (they are the likeliest source of injection) and AI-probe responses, which are untrusted too.
3. **SSRF checklist is good but misses forms.** Add: decimal/octal/hex IPs, `0.0.0.0`, CGNAT 100.64.0.0/10, IPv6 zone IDs, userinfo in URLs (`http://good.com@127.0.0.1`), non-HTTP redirect schemes, and a connect-time IP check (not just a pre-resolve check). Prefer an egress proxy or container-level network policy over hand-rolled validation. Anthropic's server-side web-search tool executes on Anthropic infrastructure, so SSRF applies only to your own fetcher.
4. **Non-determinism and drift.** No mention of pinning model IDs per run, storing the exact prompt and model version with each probe, or re-baselining when a provider changes the model. Without that, a "ranking drop" in the report may just be an assistant update.
5. **Entity resolution is absent.** The extractor must match "Smith Family Dental" to the client (name+phone+address fuzzy match) and detect hallucinated businesses that do not exist (verify against Places/Maps data). Otherwise share-of-voice is polluted.
6. **JS-rendered sites are excluded without a fallback.** A large share of local sites are built on Wix/Squarespace/Webflow/WordPress page builders. The MVP should at least flag "HTML shell is empty or text-poor" as a finding, because most AI crawlers do not execute JS either.
7. **No auth/consent proof** that the user controls the domain before crawling at 1 req/s with a contact UA; low priority but cheap (DNS TXT or meta tag).

## 4. Local-business tailoring: missing or misweighted

- **AI-crawler access is not mentioned at all.** Check `robots.txt`, WAF/CDN bot-blocking (GPTBot, OAI-SearchBot, PerplexityBot, ClaudeBot, Google-Extended) and noindex headers. This is the cheapest, highest-leverage deterministic check for the "get recommended by AI" goal.
- **Google Places API (New) is absent from the data-source table.** It is the obvious source for competitor rating, review count and categories, and a free GBP-less route for the MVP. Cost and field-mask pricing need checking. This also fills the gap while the GBP API approval is pending.
- **Service-area vs storefront businesses.** Plumbers and many contractors hide their address; the proximity argument and geogrid centre differ. Also missing: GBP suspension and verification risk, categories, hours accuracy, spam competitors (keyword-stuffed names, fake listings) and how to report them.
- **Local Services Ads / Google Guaranteed** is a major lead channel for plumbers, law firms and home services and is mentioned only as a SERP capture field.
- **Vertical specifics are thin.** Restaurants (menu, reservation platforms, delivery apps, TripAdvisor), dentists (insurance, Healthgrades, new-patient booking), law (Avvo/Justia/FindLaw, YMYL, advertising rules), salons (booking links, Instagram). The agent needs a per-vertical config file for directories and compliance flags, not generic text.
- **Review text matters.** Review content (services and place names customers mention) and response rate feed both pack relevance and AI answers; the plan treats reviews mostly as counts.
- **Misweighting:** the plan front-loads schema, blog and information-gain content for a business whose first wins are GBP categories, reviews and NAP. The 30/60/90 is right, but the agent's heavy LLM spend should go to the GBP/review/citation audit, not content drafting.
- **Siri/Apple Maps and Bing Places** are in the citation list but not weighted; for ChatGPT/Copilot/Siri they may matter more than Google-centric advice suggests (MED-LOW, unverified).

## 5. Verdict per section

| Section | Verdict |
|---|---|
| A0 framing (three surfaces, no #1 promise) | KEEP |
| A1 niche scoring | FIX: label thresholds as uncalibrated; add weights; add Places API data |
| A2 competitor method | FIX: add geo-targeted probes, entity resolution, Foursquare/Yelp/Apple/Bing sources |
| A3 prioritisation and 30/60/90, timelines | KEEP (state Ahrefs figures as trend, not range) |
| A4 white-hat authority | KEEP; DROP Reddit drafting from MVP; update FTC penalty |
| A5 KPIs and AI share-of-voice | FIX: n=5 is too small; cost model; Wilson intervals |
| A6 guardrails | KEEP; implement as code validators as stated |
| B1 platform and agents table | FIX: collapse to pipeline; remove Opus orchestrator from MVP |
| B2 data sources | FIX: add Places API, Anthropic search-tool price, Perplexity per-request fees; mark CSE API dead 2027-01-01 |
| B3 safety | KEEP/FIX: close free-text injection channel; extend SSRF list |
| B4 MVP layout/CLI | FIX: shrink scope (below); "one session, 2,500 lines" is optimistic |

## 6. MUST-apply corrections (priority order)

1. Replace the FTC penalty with $53,088 (as of the Jan 2025 adjustment; no 2026 adjustment reported); tell the agent to say "up to ~$53k per violation, adjusted annually" and recheck the 2026-09-15 notice.
2. Add geography to every AI probe (`user_location` where supported, city/ZIP in the prompt) and store provider, model version, prompt, location and timestamp per run.
3. Raise sample size and use Wilson/bootstrap intervals; forbid trend claims when intervals overlap. Re-do the cost model with per-query billing plus search-result tokens and enforce a hard per-run spend cap in code.
4. Add an AI-crawler-access check (robots, WAF, noindex, empty-HTML-shell detection) as the first audit item.
5. Add Google Places API (New) and entity resolution; add Foursquare/Yelp/Apple/Bing Places to the citation seed list per assistant, marked MED-LOW.
6. Close the injection channel: reader outputs are enums/numbers/length-capped strings only; competitor pages and probe outputs are treated as untrusted; no side-effect tools in any LLM step that sees fetched text.
7. Collapse the MVP to a function pipeline with one model (Sonnet 5.5) plus one final compliance pass; drop the Opus orchestrator and the subagent tree until phase 4.
8. Mark scoring thresholds as heuristics; add `verified_on` dates to every number the agent may quote; fix source attribution (SOCi, Whitespark primary).
9. Do not encode FAQ/Review schema rich-result promises; verify against Google structured-data docs before writing the schema skill.
10. Mark SERP provider as an adapter; note CSE API shutdown 2027-01-01; add vertical config files (directories + compliance flags per business type) and a service-area-business mode.

## 7. MVP include / exclude

Include: SSRF-safe, robots-aware crawler; technical, on-page and schema audit (deterministic); AI-crawler access check; NAP and citation audit sheet (human claims listings); Places/SERP-based competitor snapshot for 8-10 queries (small 3x3 grid optional); heuristic niche scorer with evidence links; AI probe on one provider with geo, repeated runs, intervals and entity resolution; GBP checklist (manual input); review-request and review-reply templates; 30/60/90 plan; report with caveats; guardrail refusals (fake reviews, guarantees, hidden prompt text, gating, incentives); cost caps; golden and injection fixtures.

Exclude: orchestrator/subagent hierarchy, Opus drafting, Reddit drafting, GBP/GSC/GA4 OAuth (phase 2-3), backlink analysis, geogrid at scale, multi-provider probes (add one more only after the first is validated), llms.txt/"GEO" tactics, JS rendering, any automatic publish or outbound message, Common Crawl/Wikidata.
