# Local SEO + AI-Visibility Agent (US and UK)

Audits a **local business** (dentist, solicitor, plumber, heating engineer, electrician, restaurant, salon...), builds a
prioritised 30/60/90-day plan, and measures how often AI assistants name the business, so you can work toward being the
first business recommended in its niche on **Google (local pack + organic)** and in **ChatGPT, Claude, Perplexity and
Gemini**. Works for **US and UK** clients: UK law, regulators, directories, wording and postcode/phone handling are built in.

> **Honest limits.** Nobody can guarantee #1 on Google or a first mention in an AI assistant. Results vary by searcher
> location and over time. This tool finds what is holding a business back, ranks the fixes, and measures change with proper
> statistics. It never publishes, posts or messages anything: every outward action is a draft for a human. It is not legal
> advice: legal items are tagged **[LAWYER]**.

Built from research agents each reviewed by an adversarial critic agent: see [`RESEARCH_SUMMARY.md`](RESEARCH_SUMMARY.md),
[`research/`](research/) (US/Google/AI/GitHub/architecture) and [`research/uk/`](research/uk/) (UK law, UK local search, API contracts).

## Quick start

```bash
cd local-seo-agent
pip install -r requirements.txt                 # or: pip install -e ".[probe,draft,render,dev]"

# US client
python -m local_seo_agent init riverside --vertical dentist
# UK client
python -m local_seo_agent init northgate --market uk --vertical heating_engineer

$EDITOR clients/northgate/client.toml           # name, site, phone, address, services, facts, company number, GBP details
python -m local_seo_agent run northgate         # crawl + audit + plan + report
open clients/northgate/report.html
python -m local_seo_agent doctor                # which credentials/packages are available (presence only)
```

UK clients set `jurisdiction = "UK"`; `nation` (ENG/WAL/SCO/NIR) is derived from the postcode when unambiguous (border
postcodes are never guessed: run `resolve`). Verticals: `dentist`, `lawyer` (alias `solicitor`), `plumber`, `heating_engineer`,
`electrician`, `restaurant`, `salon`, `generic`.

## Commands

| Command | What it does | Needs |
|---|---|---|
| `init <client> [--market uk] [--vertical v]` | Template client profile | nothing |
| `audit <client> [--psi] [--render]` | Safe crawl + deterministic checks; `--render` compares raw HTML with the JS-rendered DOM | nothing (`PSI_API_KEY`, playwright optional) |
| `resolve <client>` | UK: nation, council area, coordinates from the postcode (postcodes.io) | network |
| `plan <client>` / `report <client> [--live-status]` | 30/60/90 plan ranked by impact x evidence / effort; HTML report | audit |
| `probe <client> --provider openai\|claude\|perplexity\|gemini\|fake` | Geo-targeted AI-visibility sampling, intervals, entity matching, budget cap | provider key + model id |
| `probe <client> --compare A B --provider p` | Wave-over-wave change; claims a change only if the interval excludes 0 | two waves |
| `sheet-export` / `sheet-import` | Worksheet for MANUAL observation of Google AI Overviews / AI Mode / consumer apps / Siri / Alexa; imported rows become calibration data | a person with a phone |
| `aio-capture <client>` | Google AI Overviews via a licensed SERP API (directional, vendor-collected) | DataForSEO |
| `geogrid <client> --keyword k` | Local rank grid (avg rank, top-3 share, coverage) | DataForSEO |
| `places-snapshot <client>` | Competitor ratings/review counts/categories and review velocity over time | `GOOGLE_PLACES_API_KEY` |
| `gsc` / `ga4` / `gbp` | Search Console summary; AI-assistant traffic in GA4; Business Profile performance/reviews | `GOOGLE_ACCESS_TOKEN` (GBP needs Google approval) |
| `status` / `verify-facts` | Is a Google update rolling out? Re-check quoted facts against primary sources | open network |
| `schema <client>` | LocalBusiness JSON-LD from your facts (no invented ratings/hours) | nothing |
| `draft <client> gbp-description\|review-request\|review-reply\|service-page` | LLM draft, compliance-checked, never posted | `ANTHROPIC_API_KEY` |
| `guard [--market uk] "<request>"` | Check a request against the compliance rules | nothing |

Client state lives in `clients/<client>/` (`client.toml`, `audit.json`, `plan.json`, `probe.sqlite`, `snapshots.sqlite`,
`resolved.json`, `report.html`, `drafts/`). Nothing there is committed (gitignored).

## What it checks

- **AI-crawler access first**: robots.txt for Googlebot, Bingbot, OAI-SearchBot, Claude-SearchBot, PerplexityBot, Applebot (blocking = ERROR); training bots reported as an owner's choice; noindex; JS-only shells (confirmed by `--render`). CDN/WAF blocking is invisible from outside, so it is reported as UNKNOWN with instructions.
- **Technical/on-page, schema, NAP, GBP facts** (as before), plus **competitor data** from Places snapshots (review gap, rating, category differences, velocity) and **live GBP facts** when approved.
- **UK pack** (`checks/uk_checks.py`): company number / registered name / place of registration on the site (SI 2015/17), email and VAT (E-Commerce Regs reg 6), privacy policy, analytics/ads tags *observed* (never "unlawful"), hard-coded star ratings (DMCC), trust-mark claims without a supplied register ID (CAP 3.50), Botox/Dysport-style brand names in public copy (CAP 12.12), Gas Safe, SRA (England & Wales only), GDC numbers, CQC rating display **only when a rating exists** (primary dental care is usually unrated), food-hygiene rating (mandatory in Wales/NI; Scotland uses FHIS) and allergens, postcode/phone/nation hygiene, Companies House status via `COMPANIES_HOUSE_API_KEY`.

## AI-visibility measurement

- Headline metric: **"Mention rate (API-sampled)"**, never a rank, with a Wilson interval and a prompt-clustered bootstrap interval. Fewer than 200 valid runs per platform is labelled "diagnostic only"; the report states the smallest detectable change.
- Every call carries the client's location (`user_location`: country `GB`/`US`, city, region, timezone; coordinates for Perplexity/Gemini Maps). UK probes also flag **US-context answers** (dollar prices, ZIP codes) as a localisation failure. Provider, model version, prompt, location and timestamp are stored; comparing across model versions is refused.
- Providers: OpenAI Responses (`web_search`), **Claude Messages API (`web_search_20250305`, raw REST)**, Perplexity Sonar, Gemini native `generateContent` with Google Search grounding (the OpenAI-compatible endpoint does not ground). UK prompts use UK English (solicitor, takeaway, postcode districts) and quote the search term so any phrase reads naturally.
- A **hard budget cap** is enforced in code. Cost per call is an estimate you should measure.
- Not measurable by API: Google AI Overviews / AI Mode, consumer apps, voice assistants. They are covered by the manual worksheet (calibration against API answers) and, for AI Overviews, an optional licensed SERP capture (vendor-collected, directional).

## Guardrails (enforced in code, `compliance.py`)

Refuses fake/bought reviews, ranking guarantees, outcome guarantees, hidden text, AI prompt injection, review gating, review
incentives (wording: lawful in the UK only if prominently disclosed, banned by Google/Trustpilot/Checkatrade/Yell, so never
proposed), review suppression, staff review quotas, astroturfing, and (UK) prescription-only-medicine advertising. Drafts are
blocked if they contain guarantees, incentives, directives aimed at AI, unsupported superlatives, POM brand names (UK), or **any
number not in the client's supplied facts**. Health/legal review replies are blocked from confirming a patient/client
relationship. Review-request drafts get a non-blocking PECR note in the UK (ICO position unconfirmed; a human decides).

## Safety

- Pages, AI answers and reviews are **untrusted**: findings cap and sanitise text; the LLM never sees raw page text; reports are autoescaped.
- The crawler validates every hop (public IPs only incl. CGNAT/metadata/decimal-hex forms, no userinfo, standard ports), connects to the validated IP (DNS-rebinding safe), caps size/time and honours robots.txt. For production also use an egress proxy or container network policy.
- **JS rendering** never lets the browser touch the network: every request is re-fetched through that same validated fetcher (own-origin only, GET only, no redirects handed to the browser). Chromium also runs behind a dead proxy so anything the route handler cannot see fails closed. Verified experimentally in this repo's tests: a page's WebSocket and fetch to a loopback "internal service" made **zero** connections, whereas without the dead proxy a WebSocket did connect (Playwright's `route` does not see WebSockets). `route_web_socket` was avoided because it hung the sync API in testing.
- Connectors read secrets from the environment only, are read-only, treat 429 from the GBP APIs as "access not approved/quota exceeded" (not retried), and retry (opt-in) only idempotent reads. Costly calls (SERP/LLM search) are never retried blindly and have budget caps.
- TLS verification is always on. If your network re-signs TLS, set `LSA_CA_BUNDLE=/path/to/ca.pem`.
- Only crawl sites you have permission to audit. `--ignore-robots` exists for the owner's own site.

## Credentials

`ANTHROPIC_API_KEY` (+ `LSA_CLAUDE_MODEL`), `OPENAI_API_KEY` (+ `LSA_OPENAI_MODEL`), `PERPLEXITY_API_KEY`, `GEMINI_API_KEY`,
`GOOGLE_PLACES_API_KEY` (enable "Places API (New)"), `DATAFORSEO_LOGIN/PASSWORD`, `PSI_API_KEY`, `COMPANIES_HOUSE_API_KEY`
(free). Model names are never hardcoded. For Search Console / GA4 / Business Profile set `GOOGLE_ACCESS_TOKEN` (scopes must have
been granted at login with your own OAuth client):

```bash
gcloud auth application-default login --client-id-file=client_secret.json \
  --scopes=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/business.manage
export GOOGLE_ACCESS_TOKEN=$(gcloud auth application-default print-access-token)
```

## Limitations: what is fixed, and what code cannot fix

| Earlier limitation | Status |
|---|---|
| US-only compliance | **Fixed**: UK pack (DMCC Act, ASA/CAP, PECR/UK GDPR, SRA, GDC/CQC, FHRS/FHIS, Gas Safe/TrustMark, Companies House) + `jurisdiction` routing; other countries get generic checks and a loud warning; Crown Dependencies are not treated as UK. Still needs a lawyer; Scotland/NI law societies, vets, funerals, estate agents, childcare are **not built**. |
| No JavaScript rendering | **Fixed**: `audit --render`, SSRF-hardened (needs `pip install playwright` + a Chromium). |
| No Places / competitor data, no review velocity | **Fixed**: `places-snapshot` (needs a key; velocity needs repeat snapshots). |
| No Search Console / GA4 / Business Profile | **Built** (`gsc`, `ga4`, `gbp`). **GBP cannot be unblocked by code**: new Cloud projects have quota 0 until Google approves access (verified listing 60+ days old); the Places API is the no-approval fallback. Search Console's Generative AI report has no API (UI/CSV only). |
| No local rank tracking | **Fixed**: `geogrid` via DataForSEO (paid; licensed data, no scraping). |
| Claude not probed; Gemini not grounded | **Fixed**: Claude REST provider; Gemini native Search/Maps grounding. |
| Google AI Overviews / AI Mode / consumer apps / voice not measured | **Cannot be fully fixed**: there is no compliant API. Covered by a manual observation worksheet with API-vs-app calibration, plus optional vendor-collected AI Overview capture. |
| "Update freeze" was static | **Fixed**: `status` / `report --live-status` read the Search Status Dashboard (fail-open; schema inferred, take one live fixture first). |
| Research not checked against primary sources | **Tooling fixed, verification not**: `verify-facts` re-reads each primary page, records a content hash and flags drift. It must be run from an open network (the build sandbox blocked those hosts). |
| Provider/connector code never run live | **Not fixable offline**: contracts were verified from Google discovery docs, vendor SDKs and OpenAPI specs and are covered by mock-transport tests, but not run against live services (no credentials, egress blocked). Run each command once with a tiny budget first. |
| Body contouring / BBL vertical, Scotland, brand-new Google profile | **Built**: `body_contouring` and `cosmetic_surgery` verticals (aliases `bbl`, `booty_lift`, `non_surgical_bbl`), an ASA/CAP claims scanner with REFUSE/ERROR/WARN tiers, a GBP name-risk check (service + place), a first-90-days plan for profiles under 60 days old, franchise (brand-domain) checks and a Scottish regime note (Healthcare Improvement Scotland, 2026 non-surgical procedures legislation, licensing not yet in force and **unresolved for cavitation/vacuum devices**). Not legal advice; research in `research/bbl/`. |
| Welsh-language probes | **Not built** (Welsh Language Standards bind public bodies, not private businesses). |
| Orchestrator / subagents | **Deliberately not built** (the critique showed a deterministic pipeline is safer and cheaper). |

## Demo: a new BBL (non-surgical) franchise branch in Scotland

`python examples/bbl_lanarkshire_demo.py` runs the real audit, plan, report, schema and guardrails against an **illustrative** local site
(invented details; one sentence of real public-listing wording is quoted to show how it is treated). Output: `examples/bbl-lanarkshire-demo/`.

## Dependencies: the >5k-star rule

Direct runtime dependencies: **httpx** (15.5k stars), **pydantic** (28.9k), **Jinja2** (11.8k). Optional: **openai-python** (31.7k)
for the OpenAI/Perplexity probes, **claude-agent-sdk-python** (8.2k) for drafting, **playwright-python** (15.0k) for `--render`;
dev **pytest** (14.6k). All connectors (Google, DataForSEO, Claude/Gemini probes, Companies House, postcodes.io) use plain
httpx: no new dependencies. The rule applies to *direct* dependencies; transitive ones (lxml 3.1k, google-auth 883) cannot be
avoided in Python. Anthropic's `anthropic-sdk-python` shows 3.9k stars, so Claude access is via REST/the Agent SDK. LiteLLM was
dropped after a confirmed 2026-03-24 PyPI compromise. Star counts were read from public repo pages (GitHub API blocked): re-check.

## Tests

```bash
python -m pytest -q        # 181 tests, offline (local HTTP server stands in for client sites; mock transports for APIs)
```
The JS-rendering tests need Playwright and a Chromium (`LSA_CHROMIUM_PATH`); they skip otherwise.
