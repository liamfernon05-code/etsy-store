# Critique of 03-github-repos.md (Critic Agent 3 of 4, 2026-10-03)

Method: WebFetch on github.com repo pages (stars/licence/archived), WebSearch for the LiteLLM incident and for missed repos, raw pyproject.toml for dependency trees. Last-commit dates could NOT be re-verified (repo pages did not show them; Atom feeds not retried). WebFetch is a small-model summary, so every figure below carries the same residual risk the researcher flagged.

## 1. Re-verification (18 kept repos re-checked)

| Repo | Researcher | My re-check | Verdict |
|---|---|---|---|
| anthropics/claude-agent-sdk-python | 8.2k MIT | 8.2k, MIT, not archived; page says governed by Anthropic Commercial Terms, bundles Claude Code CLI | OK |
| modelcontextprotocol/python-sdk | 24.5k | 24.5k MIT, active, v2 docs | OK |
| microsoft/playwright | 97.0k | 97.0k Apache-2.0. BUT this is the Node monorepo. The Python package is microsoft/playwright-python, 15.0k Apache-2.0 | FIX: cite playwright-python |
| unclecode/crawl4ai | 84.7k | 84.7k, Apache-2.0, v0.9.4 (2026-09-23); README says "you must include" an attribution method | OK, attribution is mandatory |
| adbar/trafilatura | 6.9k | 6.9k, Apache-2.0 (>=1.8), active | OK, but see transitive deps |
| ChromeDevTools/chrome-devtools-mcp | 52.9k | 52.9k Apache-2.0; README warns it exposes browser contents; Google collects usage statistics by default; may send trace URLs to CrUX | OK, new privacy flags |
| GoogleChrome/lighthouse | 30.8k | 30.8k Apache-2.0, needs Node 22 | OK |
| schemaorg/schemaorg | 6.3k | 6.3k, Apache-2.0 (code) | OK, see licence trap below |
| BerriAI/litellm | 60.1k | 60.1k, MIT | OK stars; compromise CONFIRMED (section 3) |
| sentence-transformers | 19.1k | 19.1k Apache-2.0 | OK |
| pgvector/pgvector | 23.2k, licence unverified | 23.2k; licence name still not shown by fetch (PostgreSQL License from my knowledge) | Star OK, licence still unverified |
| googleapis/google-api-python-client | 8.9k | 8.9k Apache-2.0, maintenance mode, Google recommends Cloud Client Libraries for new work | OK |
| pandas / plotly.py | 49.9k / 18.8k | 49.9k BSD-3 / 18.8k MIT | OK |
| every-app/open-seo | 22.2k MIT | 22.2k MIT. TypeScript/Cloudflare Workers/React stack (not Python). Needs DataForSEO key; hosted version adds a 28% surcharge | OK, but unusable as a Python dependency |
| AgriciDaniel/claude-seo | 18.2k MIT | 18.2k MIT. Has `curl -fsSL ... install.sh` one-liner and a `/hooks` directory | OK for reading; do not install |
| firecrawl / markitdown | both "188.1k" | Firecrawl: my fetch again 188.1k, but search sources say about 174k. markitdown: search says 188k (174k in Aug 2026). Forks differ (10.0k vs 13.9k). The shared figure is most likely a summariser artefact for one of them | Irrelevant to the rule (both far above 5k) but the "188.1k" cells should be "approx 170-190k, not exactly verified" |
| sitespeed.io | 5.0k excluded | My fetch said "5,000+ stars" | Still ambiguous, exclusion is correct and conservative |

New ambiguous or sub-threshold items the researcher did not catch:
- google-api-python-client depends on `google-auth`, whose repo googleapis/google-auth-library-python has 883 stars and has been ARCHIVED since 2026-03-06 (moved into the google-cloud-python monorepo).
- trafilatura depends on lxml (3.1k stars, below 5k), plus courlan, htmldate and justext (all small). Crawl4AI depends on lxml, beautifulsoup4 (no real GitHub repo, hosted on Launchpad; GitHub mirrors have about 200 stars), aiosqlite, patchright, playwright-stealth, fake-useragent, rank-bm25, alphashape and others. In total about 34 runtime dependencies.

Conclusion: a literal reading of "only repositories with more than 5,000 stars" cannot be applied to transitive dependencies. Nobody can ship Python without sub-5k transitives (lxml, google-auth, certifi). The builder must (a) apply the rule to DIRECT dependencies and (b) state this interpretation to the user explicitly, so the user is not surprised later.

## 2. Licence traps and necessity

Licences are mostly clean. Real traps:
- **schemaorg/schemaorg**: the repo's code is Apache-2.0, but the schema.org vocabulary and documentation are published under CC BY-SA 3.0. Embedding the vocabulary data in a product carries attribution and share-alike duties. The researcher listed it as plain Apache-2.0 and missed this. Also, the repo is not a pip package, so it would be vendored data.
- **Crawl4AI**: attribution is mandatory (the README says "must"). Keep, but add a notice. It also pulls `unclecode-litellm` (a pinned fork), `playwright-stealth`, `patchright` and `fake-useragent`, which are anti-bot evasion tools bundled into a client-facing agent. That is a ToS/ethics smell for a tool pitched to businesses.
- **Firecrawl** is AGPL-3.0 core. Do not use (see below). **SearXNG** (37.9k) is also AGPL-3.0.
- **claude-agent-sdk-python**: MIT repo but governed by Anthropic Commercial Terms and requires a paid API key. It is acceptable, but the project is then locked to Claude as the brain.

Necessity: this is over-engineered for an MVP. The 12-part stack drops to roughly 5 or 6 pieces.

| Component | MVP need? | Replace with |
|---|---|---|
| chrome-devtools-mcp + Lighthouse | No | PageSpeed Insights REST API via httpx (Lighthouse results with no Node, no browser, no MCP). Add local Lighthouse later if needed. |
| Crawl4AI | No for MVP | httpx plus stdlib `html.parser`/`urllib.robotparser`/`xml.etree` for a 10-200 page local site; Playwright only for JS-rendered pages. Crawl4AI drags in 34 deps and a pinned LiteLLM fork. |
| trafilatura | Optional | A simple visible-text extractor in stdlib; main-content extraction is not needed for a local audit. Needs lxml. |
| LiteLLM | No | openai-python (31.7k). Perplexity and Gemini both expose OpenAI-compatible endpoints; call Claude via the Agent SDK. Removes the compromised-package risk. |
| sentence-transformers + pgvector | No | Defer. Torch is about 2 GB, and for a single business a few hundred vectors fit in numpy/sqlite. Use an embeddings API if really needed. |
| pandas + plotly | No | stdlib `csv`/`json` plus Jinja2 (11.8k, BSD-3) for an HTML report. |
| schemaorg/schemaorg | Marginal | Download the single `schemaorg-current-https.jsonld` once and vendor it, or hand-code the 5-10 LocalBusiness types and properties. |
| open-seo, claude-seo | Reference only | Never install. |
| google-api-python-client | Only for GSC | Could use httpx plus OAuth. GBP API access needs Google approval, which is the real blocker. |

## 3. Security review

- **LiteLLM compromise: CONFIRMED.** Multiple independent sources (FutureSearch, Datadog Security Labs, Snyk, Trend Micro, NHS England Digital, Upwind) report that malicious litellm 1.82.7 and 1.82.8 were published to PyPI on 2026-03-24 for about 40 minutes by threat actor TeamPCP. The attacker used maintainer credentials stolen via the earlier Trivy scanner compromise (2026-03-19). The payload was a `.pth` file that runs on every Python start, a credential stealer, Kubernetes lateral movement and a persistent backdoor. It was found by FutureSearch via a transitive dependency of a Cursor MCP plugin. The researcher's "I recall reports but could not verify" should become a verified fact with these details. I could not open docs.litellm.ai (egress blocked), so safe-version numbers are not independently confirmed. Lesson: the exposure often arrives transitively. Pin with hashes (`pip install --require-hashes`), use a lockfile, and prefer not depending on LiteLLM at all.
- **Prompt injection from crawled pages** is the biggest design risk. The researcher mentioned it but gave no mitigation. Required: crawled text is data in a clearly delimited block; the crawl/analysis agent has NO write/send/shell tools; Bash/Write tools disabled in the Agent SDK for the analysis stage (the SDK defaults to Read/Write/Edit/Bash, which is dangerous); only a final, human-approved step may act.
- **SSRF**: the researcher flagged the MCP fetch server only. Our own fetcher needs: https/http only, resolve DNS and reject private/link-local/loopback/metadata IPs (169.254.169.254), re-check after every redirect (DNS rebinding), response size and time caps. This is custom code; no >5k library does it cleanly.
- **Browser MCPs**: chrome-devtools-mcp "can inspect, debug and modify any data in the browser" and reports telemetry to Google by default (`--no-usage-statistics`, `--no-performance-crux`). Use a throwaway profile, no logged-in sessions, and avoid it in the MVP.
- **Third-party skills/plugins** (claude-seo, open-seo skills): Snyk's ToxicSkills study found prompt injection in 36% of audited skills and 1,467 malicious payloads; skills run with host privileges and are unsigned. claude-seo itself ships a `curl | bash` installer and hooks. Treat both as read-only reference material; copy ideas, not code.
- MarkItDown does I/O with the process's privileges. Not needed in the MVP, so drop it.

## 4. Missed >5k repos (verified this session)

Relevant and verified:
- microsoft/playwright-python 15.0k (the correct Playwright repo for Python).
- openai/openai-python 31.7k (Apache-2.0).
- promptfoo/promptfoo 25.7k (MIT, TypeScript, now part of OpenAI): LLM eval/red-team CLI.
- confident-ai/deepeval 18.6k (Apache-2.0) and explodinggradients/ragas 15.9k (Apache-2.0): Python LLM evaluation.
- psf/requests 54.4k, encode/httpx 15.5k (BSD-3), pydantic/pydantic 28.9k, pallets/jinja 11.8k, pytest-dev/pytest 14.6k, Kludex/starlette 12.6k.
- searxng/searxng 37.9k (AGPL-3.0): only a conceptual rank-check source; scraping/AGPL, so not recommended.
- googlemaps/google-maps-services-python: 5.0k, Apache-2.0. Ambiguous threshold; also "community supported" client, and plain httpx calls to the Places API are equally good. Exclude.
- python-jsonschema: displayed "5,000", ambiguous; exclude (not needed).

Searched and found nothing >5k: local-SEO/GBP tooling, geo-grid rank tracking, citation/NAP checking, AI-visibility/GEO trackers (geo-aeo-tracker 278, localseoskills 107, Limelit and others small), JSON-LD/Google rich-result validators, sitemap parsers, robots.txt parsers (stdlib `urllib.robotparser` covers it). Fast HTML parsers: lxml 3.1k, selectolax 1.7k, BeautifulSoup has no real GitHub repo. So **the only >5k HTML-parsing route in Python is the stdlib `html.parser`** (or Scrapy at 64.6k, which brings parsel/lxml).

## 5. Minimal defensible MVP dependency list (direct deps, all >5k or stdlib)

1. Python stdlib: `html.parser`, `urllib.robotparser`, `xml.etree` (sitemaps), `json`, `csv`, `ipaddress`/`socket` (SSRF guard), `sqlite3`, `argparse`.
2. httpx (15.5k): HTTP client for fetching, PageSpeed Insights and Places APIs.
3. pydantic (28.9k): typed findings and config.
4. claude-agent-sdk-python (8.2k): agent loop (needs Anthropic key and the bundled CLI). Optional: modelcontextprotocol/python-sdk (24.5k) only if tools are exposed as MCP servers; the SDK's in-process tools make it unnecessary.
5. openai-python (31.7k): GEO probing of OpenAI, Perplexity (base_url) and Gemini (OpenAI-compatible endpoint). Honest caveat: API answers are not identical to consumer ChatGPT or AI Overviews, and Anthropic's own SDK (3.9k) is excluded by the rule.
6. Jinja2 (11.8k): HTML/Markdown client report.
7. pytest (14.6k): tests (dev).
8. Optional, added only on demand: microsoft/playwright-python (15.0k) for JS-rendered pages; promptfoo (25.7k, Node) or deepeval (18.6k) for evaluating agent outputs; Scrapy (64.6k) only for large crawls.

**Must be written by us (no >5k option exists):** GBP and NAP-consistency audit logic; LocalBusiness JSON-LD generator and validator against Google's requirements (and the vocabulary check); sitemap and robots/AI-crawler checks (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) and llms.txt check; GEO measurement (prompt sets, mention and citation parsing, share of voice); SSRF-safe fetcher; prompt-injection hygiene; scoring/prioritisation; review analysis; local rank/geo-grid tracking (needs paid API such as DataForSEO or Places data).

## 6. Verdict per section

- Section 1 (method): FIX. Say last-commit dates were not re-verified, and say the 188.1k duplicate is likely an artefact (Firecrawl about 174k per search).
- Section 2 (key finding, nothing >5k local-specific): KEEP. My searches agree.
- 3.1 SEO-specific: FIX. google-indexing-script, gosom/google-maps-scraper: DROP (ToS/irrelevant). open-seo/claude-seo: reference only, and open-seo is TypeScript/Cloudflare, not Python. schemaorg: FIX licence (CC BY-SA for vocabulary).
- 3.2 Auditing: FIX. Replace Lighthouse/DevTools-MCP in the MVP with the PageSpeed Insights API.
- 3.3 Crawling: FIX. Playwright should cite playwright-python. Firecrawl/Scrapling/anti-bot items: DROP. Note Crawl4AI's anti-bot dependencies and 34-dep footprint.
- 3.4 Agent frameworks: FIX. Too many alternatives listed; keep the Agent SDK and openai-python, drop the rest from the MVP. Add that anthropic-sdk-python is below threshold, so Claude access is only via the Agent SDK.
- 3.5 NLP/storage: DROP from the MVP (defer).
- 3.6 Data/reporting: FIX. Replace pandas/plotly with csv plus Jinja2; note google-auth is an archived, 883-star transitive dependency.
- Section 4 (exclusions): KEEP; add google-maps-services-python (5.0k) and jsonschema (5,000) as ambiguous.
- Section 5 (12-part stack): FIX. Cut to the list in part 5 above. Items 6, 8, 9, 10 should not be in the MVP.
- Section 6 (risks): FIX. Upgrade LiteLLM from "recalled" to "verified"; add SSRF code requirements, the Agent SDK Bash-tool danger, DevTools telemetry, claude-seo `curl | bash`.

## Prioritised corrections the builder MUST apply

1. State the star-rule interpretation (direct dependencies only; transitives such as lxml 3.1k and google-auth 883 are unavoidable) to the user.
2. Do not depend on LiteLLM; if ever used, pin hashes and avoid versions 1.82.7 and 1.82.8. Same hygiene for every dependency (lockfile, `--require-hashes`).
3. Use the minimal list in part 5. Remove pgvector, sentence-transformers, pandas, plotly, MarkItDown, Firecrawl, and the browser MCPs from the MVP.
4. Disable the Agent SDK's Bash/Write tools for any run that processes crawled content; no side-effect tools reachable from untrusted text.
5. Write a custom SSRF-safe fetcher (private-IP block, redirect re-validation, size/time caps).
6. Treat claude-seo and open-seo as reference only; never run their installers.
7. Correct the repo citation to microsoft/playwright-python; relabel "188.1k" cells as approximate; note schema.org vocabulary is CC BY-SA 3.0; keep the Crawl4AI attribution if it is used.
8. Note GBP API access requires Google approval and PageSpeed/Places are separate keyed APIs, so "GBP audit" needs a manual/inputted-data fallback in the MVP.
