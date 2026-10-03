# Research summary (2026-10-03)

Method: 4 research agents (Google SEO, AI-search/GEO, GitHub repos >5k stars, strategy + architecture), each followed by an
adversarial critic agent that re-verified claims and listed must-fix corrections. Full reports and critiques are in
[`research/`](research/). **Caveat on sources:** the sandbox blocked most primary sites (Google, OpenAI, Ahrefs, ...), so most
claims were verified through search-result summaries, not by reading the primary page. `local_seo_agent/facts.py` stamps every
quoted fact with its confidence and verified-on date. Re-verify against primary docs before encoding any rule as a hard fail.

## What matters most for a local business (reconciled across reports)

1. **Be crawlable by search *and* AI answer engines.** Allow Googlebot, Bingbot, OAI-SearchBot, Claude-SearchBot, PerplexityBot, Applebot. Training bots are optional and don't affect search visibility. Cloudflare blocks AI bots by default on domains created since 2025-07-01; WAF blocking can't be seen from outside.
2. **Google Business Profile is the centre of gravity.** It feeds the local pack, Maps, Gemini and AI Overviews. Primary category, completeness, accurate name (no keyword stuffing), hours, services. Whitespark 2026 (expert opinion): GBP ~32%, reviews ~20%, on-page ~19%, links ~15%, citations ~6% of local-pack weight.
3. **Reviews, done compliantly.** Ask everyone; no gating, no incentives, no fake reviews (FTC 16 CFR 465, up to $53,088/violation; Google bans gating/incentives). Reply to all reviews (draft only; health/legal replies must not confirm a relationship).
4. **Consistent NAP and the right directories**, including Bing Places, Apple Business Connect and Yelp (licensed to ChatGPT, 2026-07-23), plus vertical directories.
5. **Genuinely local content**: a page per core service, unique, written from real facts. Templated city pages are doorway spam.
6. **AI mentions come from the same entity strength** (independent mentions, listicles/third-party lists, reviews). Schema and llms.txt are hygiene, not levers (controlled test: no uplift; Google doesn't use llms.txt).
7. **Measure honestly.** Assistants are non-deterministic; report mention rate with intervals from >=200 valid runs/platform and two baselines; never report "rank". Google AI Overviews/AI Mode cannot be measured by API.

## Corrections the critics forced (and where they landed)

| Critic finding | Status |
|---|---|
| FTC penalty stale ($51,744 -> $53,088) | Fixed in `facts.py` (recheck the 2026-09-15 Federal Register notice) |
| AI probes ignored geography | `user_location` + city in every prompt; location stored per run |
| n=5 runs/prompt useless (~±35pts); cost understated | Wilson + prompt-clustered bootstrap; 200-run headline threshold; default cost $0.10/call (est.); hard cap in code |
| No AI-crawler access check | First check in the audit |
| Orchestrator + 8 agents over-engineered | Deterministic pipeline; LLM only for drafting, tools disabled |
| Free-text injection channel | Findings capped/sanitised; LLM sees only client facts; untrusted review text delimited; reports autoescaped |
| SSRF list incomplete | CGNAT, decimal/hex/octal IPs, userinfo, IPv6 zones/mapped, connect-time IP pin, per-hop re-validation (tested) |
| Self-serving review schema = WARN not error; FAQ rich results ended 2026-05-07; don't add aggregateRating | Implemented; generator never emits ratings |
| Seer/Ahrefs AI Overview CTR figures misapplied to local | Scoped to informational queries in `facts.py` |
| "Brave confirmed", Foursquare 70% claims overstated | Downgraded to vendor-confidence with the counter-evidence |
| Invented thresholds (<100 reviews, 250 words, 70% similarity) | Marked HEURISTIC, low severity, or dropped |
| Missing: SAB mode, multi-location, per-vertical config, LSA, call-tracking rule, YMYL | Added (`verticals.py`, plan playbook, NAP checks) |
| Reddit drafting / astroturfing | Dropped; refused by `compliance.check_request` |
| Jurisdiction | Required client field; non-US gets a warning |
| LiteLLM supply-chain compromise | Dropped; not used |
| Wrong Playwright repo, stack bloat | Playwright not needed in MVP; minimal dependency list |

**Deferred (documented, not built):** live Search Status Dashboard "update freeze"; GBP/GSC/GA4 OAuth; JS rendering; geo-grid rank tracking; Places API competitor snapshots; Google AI Overview sampling workflow; non-US compliance; vertical review-source evidence table; prompt-clustered CIs are implemented but power guidance assumes p≈0.3.

## GitHub repositories (>5,000 stars only)

Star counts read from public repo pages on 2026-10-03 (rounded to 0.1k; GitHub API blocked in the sandbox); critic re-verified 18 kept repos.

**Used (direct dependencies)**

| Repo | Stars | Licence | Role |
|---|---|---|---|
| encode/httpx | 15.5k | BSD-3 | HTTP client for the safe fetcher and APIs |
| pydantic/pydantic | 28.9k | MIT | Typed findings/config |
| pallets/jinja | 11.8k | BSD-3 | HTML report |
| openai/openai-python | 31.7k | Apache-2.0 | OpenAI Responses + Perplexity/Gemini compatible endpoints (optional) |
| anthropics/claude-agent-sdk-python | 8.2k | MIT (Anthropic Commercial Terms apply) | LLM drafting with tools disabled (optional) |
| pytest-dev/pytest | 14.6k | MIT | Tests |

**Reference only (read ideas, never install)**: every-app/open-seo (22.2k, MIT, TypeScript/Cloudflare, needs DataForSEO); AgriciDaniel/claude-seo (18.2k, MIT, ships a `curl | bash` installer).

**Excluded**: anthropics/anthropic-sdk-python (3.9k), sitespeed.io (5.0k, can't prove >5,000), unlighthouse 4.9k, geopy 4.9k, pa11y 4.6k (LGPL), KeyBERT 4.2k, lxml 3.1k (transitive only), and every purpose-built local-SEO/GBP/GEO-tracker repo found (all <4k; largest: open-seo-mcp-skills 3.3k, GEOFlow 3.7k). **No >5k-star repo exists for local-SEO/GBP audits, NAP checks, rank/geo-grid tracking, GEO tracking, JSON-LD validation or robots/sitemap parsing, so those parts are written here.**

**Avoided despite high stars**: BerriAI/litellm (60.1k): malicious versions 1.82.7/1.82.8 on PyPI on 2026-03-24 (credential stealer); Firecrawl (AGPL-3.0); Crawl4AI (84.7k, but ~34 deps, bundled anti-bot tooling, mandatory attribution); chrome-devtools-mcp (telemetry, exposes browser data); gosom/google-maps-scraper (ToS).

Rule interpretation: applied to **direct** dependencies; transitive ones (lxml 3.1k, google-auth 883) can't be avoided.

## Roadmap

1. Places API (New) competitor snapshot + weekly review snapshots; DataForSEO adapter for 3x3 geo-grid.
2. Search Console / Bing Webmaster Tools / GA4 read-only connectors (+ GBP API once Google approves access).
3. Status Dashboard update-freeze; scheduled monthly probe waves with automatic wave comparison.
4. Optional orchestrator/subagents only once the deterministic pipeline is validated on real clients.


---

# UK extension and limitation fixes (2026-10-03)

Method: 3 more research agents (UK law and regulation; UK local-search market; exact REST/API contracts) each followed by a
critic agent (reports and critiques in [`research/uk/`](research/uk/)). Again, most primary sites were blocked by the sandbox, so
legal and platform claims come from multiple search summaries; the API contracts were mostly verified from machine-readable sources
(Google discovery documents, vendor SDK source, the OpenAI OpenAPI spec) and, for Playwright, by the researcher's and critic's own tests.

## What the UK critics changed

| Finding | Where it landed |
|---|---|
| Trading-disclosure citation was a **revoked** instrument (2008 regs); correct one is SI 2015/17 | `facts.uk-identity`, `uk.company-number-on-site`; a test fails if the old citation returns |
| CQC regulation 20A check would false-fail almost every dentist (primary dental care is generally not CQC-rated) | Check runs only when a rating is supplied (`regulator_ids.cqc_rating`) and only in England |
| CAP rule numbers: testimonials 3.45-3.48 (not 3.47-3.50), comparisons/superlatives 3.32-3.36, puffery 3.6, recognisable advertising 2.1-2.4 | `facts.uk-cap-claims` |
| "Illegal" wording for incentivised reviews | Reworded everywhere: lawful in the UK only if prominently disclosed, banned by Google/Trustpilot/Checkatrade/Yell, never proposed |
| Review-request emails/SMS: PECR status unsettled (no ICO statement found) | Non-blocking WARN, human decides (`draft_warnings`, plan task) |
| GA4 / tracking tags | Reported as **observed**, never "unlawful"; GA4 default config "likely does not meet" the statistical exemption |
| Fine-cap wording; AA fine was GBP 7m reduced 40% to 4.2m; PO-box ban since 2024-03-04; complaints regime 2026-06-19 | `facts.py` |
| Missing sectors: vets (CMA order), funerals (price lists), estate agents (redress scheme/fees), Children Act 2021, Scotland/NI law societies | **Documented as not built**; flagged [LAWYER] |
| Rated People liquidation (2026-09-16, Checkatrade bought the brand, memberships not transferred); Scoot/Touch Local closing Oct 2026; Factual defunct; Thomson Local/Cylex/FreeIndex/Yelp UK only "unverified" | `uk.DIRECTORIES` statuses; the plan never recommends closed/closing/brand-only services |
| "7 Dec 2025" money-back-guarantee date unsupported; MyBuilder owner is Angi (HomeAdvisor 2017, Angi stake 2021) | Removed / corrected |
| Murray Digital (78/80 Checkatrade) and Whito (90% own site) studies: agencies selling AI visibility, single run, Checkatrade has a ChatGPT app | Facts tagged HEURISTIC "directional"; plan says run your own probe before paying for a directory |
| NHS.uk is England only; law registers E&W only; FHIS in Scotland is not 0-5; Gas Safe covers NI | `OFFICIAL_BY_NATION`, nation-conditional checks |
| Crown Dependencies (JE/GY/IM) look like UK postcodes and use +44 | Resolve to OTHER (generic mode + warning) |
| Search Console AI report is no longer UK-only; from 2026-09-07 combines AI Mode + AI Overview impressions; still no API | `facts.uk-ai-search`; no connector built |
| UK prompts: "plumber near me", "nail salon", "attorney" read American; `{county}` wrong outside England | UK-English terms, quoted search term, council-area clause, postcode-district prompt |

## What the API-contract critic changed

| Finding | Where it landed |
|---|---|
| `context.route` does not see HTTP redirect hops, WebSockets or data:/blob: fetches | Renderer fulfils everything through the validated fetcher, never hands the browser a 3xx; **dead-proxy fail-closed backstop verified** (WebSocket to a loopback service: 1 connection without it, 0 with it) |
| `route_web_socket` hangs the sync API (researcher and our own test) | Not used |
| DataForSEO `maps_search.url` is a search URL, not the website | Match on `domain` / `place_id` / phone only |
| Gemini `groundingChunks` has four members; the OpenAI-compatible Gemini endpoint does not ground | Native `generateContent`; unknown chunk types skipped |
| OpenAI defaults `user_location` to the US when omitted | Always sent; no US fallback for other markets |
| GA4 "AI Assistant" channel membership disputed | Never relied on; both the channel group and the source regex are queried |
| Search Console `type` vs `searchType` | `type` first, fall back to `searchType` on 400 |
| Status Dashboard schema/retention unverified | Fail-open (`UNKNOWN`), date filtering client-side, first run should snapshot a live fixture |
| Places SKU prices are LIKELY, not facts | Constants named as estimates; budget caps; never shown as facts |
| Retry policy | Opt-in exponential backoff on 429/5xx for reads; never for costly calls; GBP 429 is "not approved", never retried |

## Still open after this round

- Nothing was run against live Google, OpenAI, Anthropic, Perplexity, DataForSEO or Companies House services (no credentials; sandbox egress blocked). Mock-transport tests prove request shape and parsing, not live behaviour.
- Legal content is research-based and may be out of date by the time it is used; every legal fact carries a verification date and `[LAWYER]` where a human lawyer is needed. `verify-facts` exists but must be run on an open network.
- The Status Dashboard endpoint and schema are inferred.
- The Business Profile API needs Google approval (verified listing 60+ days old); until then use the Places API.
- Google AI Overviews / AI Mode, consumer apps and voice assistants remain manual or vendor-collected samples.
- Not built: vets / funeral / estate-agent / childcare packs, Law Society of Scotland / Northern Ireland rules, Welsh-language probes, OAuth refresh-token and service-account flows (only a bearer token from the environment), an orchestrator.

## BBL / Scotland round (2 researchers, 2 critics; see `research/bbl/`)

Critics changed the build as follows:
- The first-draft claims patterns flagged compliant text ("non-surgical Brazilian butt lift", "reduce fat intake") and missed real claims; `checks/claims.py` was rewritten with REFUSE/ERROR/WARN tiers and negation handling.
- Disputed CAP rule numbers were removed rather than cited; unresolved items (licensing scope for cavitation/vacuum devices, the "Body contouring service" GBP category) are stated as unverified.
- Scotland is handled as its own regime (Healthcare Improvement Scotland, not CQC); the 2026 non-surgical procedures licensing is described as **not yet in force and of unclear scope**, and the agent never tells a client a service is "licensed".
- A profile accepted a few days ago is treated as new: freeze name/address, ownership, reviews without incentives or gating, and the Business Profile API is not available until the listing is old enough.
- Personal identifiers from public listings in the research (individual name, phone, email, address) are redacted from the repo.
- Everything here was checked only against search summaries; nothing was run against live services and the client's real site could not be fetched.
