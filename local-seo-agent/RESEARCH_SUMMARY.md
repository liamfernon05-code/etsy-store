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
