# Local SEO + AI-Visibility Agent

Audits a **local business** (dentist, plumber, law firm, restaurant, salon...), builds a prioritised 30/60/90-day plan, and
measures how often AI assistants name the business, so you can work toward being the first business recommended in its
niche on **Google (local pack + organic)** and in **ChatGPT, Claude, Perplexity and Gemini**.

> **Honest limits.** Nobody can guarantee #1 on Google or a first mention in an AI assistant. Results vary by searcher
> location and over time. This tool finds what is holding a business back, ranks the fixes, and measures change with
> proper statistics. It never publishes, posts or messages anything: every outward action is a draft for a human.

Built from 4 research agents, each reviewed by an adversarial critic agent: see [`RESEARCH_SUMMARY.md`](RESEARCH_SUMMARY.md)
and the full reports in [`research/`](research/).

## Quick start

```bash
cd local-seo-agent
pip install -r requirements.txt          # or: pip install -e ".[probe,draft,dev]"

python -m local_seo_agent init riverside --vertical dentist     # creates clients/riverside/client.toml
$EDITOR clients/riverside/client.toml                           # name, site, phone, address, services, facts, GBP details

python -m local_seo_agent run riverside                         # crawl + audit + plan + report
open clients/riverside/report.html
```

| Command | What it does | Needs |
|---|---|---|
| `init <client> [--vertical v]` | Template client profile | nothing |
| `audit <client> [--psi]` | Safe crawl + deterministic checks (AI-crawler access, technical, LocalBusiness schema, NAP, GBP inputs) | nothing (`PSI_API_KEY` for `--psi`) |
| `plan <client>` | 30/60/90 plan ranked by impact x evidence / effort | audit |
| `probe <client> --provider openai\|perplexity\|gemini\|fake` | Geo-targeted AI-visibility sampling with intervals, entity matching, budget cap | provider API key + model id |
| `probe <client> --compare baseline1 after1 --provider openai` | Wave-over-wave change; only claims a change if the interval excludes 0 | two waves |
| `report <client>` | HTML report | audit |
| `schema <client>` | LocalBusiness JSON-LD from your facts (no invented ratings/hours) | nothing |
| `draft <client> gbp-description\|review-request\|review-reply\|service-page` | LLM draft, compliance-checked, never posted | `ANTHROPIC_API_KEY` |
| `guard "<request>"` | Check a request against the compliance rules | nothing |

Client state lives in `clients/<client>/` (`client.toml`, `audit.json`, `plan.json`, `probe.sqlite`, `report.html`, `drafts/`).

## How it works

```
client.toml ─► SafeFetcher (SSRF-safe, robots-aware, 1 req/s) ─► crawl ─► deterministic checks ─► Findings
                                                                                         │
                          playbook (local-business tasks per vertical) ──────────────────┴─► plan (30/60/90, ICE-scored)
AI probe: geo-targeted prompts x N runs x providers ─► entity match ─► mention rate + Wilson / clustered-bootstrap CI ─► report
LLM (optional): drafts from client-supplied facts only ─► compliance validator ─► blocked or saved as a draft
```

The audit and plan are **plain deterministic code**; the LLM is used only for optional drafting, with all built-in
tools disabled. This follows the critique that an orchestrator + subagent tree is over-engineering for an MVP.

### What it checks

- **AI-crawler access first**: robots.txt for Googlebot, Bingbot, OAI-SearchBot, Claude-SearchBot, PerplexityBot, Applebot
  (blocking = ERROR); training bots (GPTBot, ClaudeBot, Google-Extended) reported as an owner's choice; noindex; JS-only shells.
  CDN/WAF blocking can't be seen from outside, so it is reported as UNKNOWN with instructions.
- **Technical/on-page**: HTTPS, viewport, title/meta/H1, city in title/H1, canonical, duplicate titles, broken pages, sitemap, Core Web Vitals via PageSpeed (UNKNOWN when there's no field data).
- **LocalBusiness schema**: type, key properties, phone mismatch, self-serving review markup (WARN: no stars, no penalty), FAQ note.
- **NAP & GBP**: phone/name/address on site, tap-to-call, call-tracking caution, service-area-business mode, manual GBP facts (the GBP API needs Google approval).

### AI-visibility measurement (and its limits)

- Headline metric is **"Mention rate (API-sampled)"**: never a rank. Reported with a Wilson interval and a prompt-clustered bootstrap interval.
- Fewer than **200 valid runs per platform** is labelled "diagnostic only". The report states the smallest change detectable between two waves.
- Every call carries the client's city as `user_location` where the API supports it (OpenAI, Perplexity). Provider, model version, prompt, location and timestamp are stored; comparing across model versions is refused.
- A **hard budget cap** is enforced in code. Cost per call is an estimate you should measure (default $0.10).
- **Not measured**: Google AI Overviews / AI Mode, consumer apps, voice assistants. The report says so.
- Provider code follows public API docs and is tested with stubs; it has **not** been run against live endpoints (no keys in the build environment). Run a 1-prompt smoke test first, and set model names yourself (`LSA_OPENAI_MODEL`, `LSA_PERPLEXITY_MODEL`, `LSA_GEMINI_MODEL`): none are hardcoded.

### Guardrails (enforced in code, `compliance.py`)

Refuses fake/bought reviews, ranking guarantees, hidden text, AI prompt injection, review gating/incentives/suppression and astroturfing.
Drafts are blocked if they contain guarantees, incentives, directives aimed at AI, unsupported superlatives, or **any number not in the client's supplied facts**.
Health/legal review replies are blocked from confirming a patient/client relationship. Non-US clients get an explicit warning: only US rules (FTC 16 CFR 465) were researched.

## Safety notes

- Pages and AI answers are **untrusted**. Findings cap and sanitise text; the LLM never sees raw page text; reports are autoescaped.
- The fetcher validates every hop (public IPs only, incl. CGNAT/metadata/decimal-hex forms, no userinfo, standard ports), connects to the validated IP (DNS-rebinding safe), caps size/time and honours robots.txt. For production, also use an egress proxy or container network policy.
- TLS verification is always on. If your network re-signs TLS, set `LSA_CA_BUNDLE=/path/to/ca.pem`; never disable verification.
- Only crawl sites you have permission to audit. `--ignore-robots` exists for the owner's own site.

## Dependencies: the >5k-star rule

Direct runtime dependencies: **httpx** (15.5k stars), **pydantic** (28.9k), **Jinja2** (11.8k); optional **openai-python** (31.7k) for probes and **claude-agent-sdk-python** (8.2k) for drafting; dev **pytest** (14.6k).
The rule is applied to *direct* dependencies. Transitive ones (e.g. lxml 3.1k, google-auth 883) cannot be avoided in Python. Anthropic's own `anthropic-sdk-python` shows 3.9k stars, so Claude access goes through the Agent SDK. LiteLLM was dropped after a confirmed 2026-03-24 PyPI compromise. Details in `RESEARCH_SUMMARY.md`.
Star counts were read from public repo pages (rounded to 0.1k) because the GitHub API was blocked in the research sandbox; re-check before relying on them.

## Tests

```bash
python -m pytest -q        # 96 tests, offline (local HTTP server stands in for a client site)
```

## Not in this MVP

GBP/GSC/GA4 OAuth (GBP API needs Google approval), JavaScript rendering, backlink analysis, geo-grid rank tracking (needs a
paid Places/SERP API), automatic publishing of anything, Google AI Overview tracking, a live Search Status Dashboard
"update freeze" check, non-US legal guidance, and a multi-agent orchestrator. See the roadmap in `RESEARCH_SUMMARY.md`.
