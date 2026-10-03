# 03 - Open-source GitHub repositories for the local-business SEO + GEO agent

Research Agent 3 of 4. Date checked: 2026-10-03. Scope (updated by user): the client is a LOCAL business (not ecommerce), so local SEO, GEO, schema/JSON-LD, crawling and audits are prioritised. Hard rule applied: only repos with MORE than 5,000 stars are kept.

## 1. Method and verification caveats (read first)

- The GitHub REST API was not reachable (WebFetch returned HTTP 403 for api.github.com; shields.io and ungh.cc are blocked by the egress proxy). One attempt to call the API through Bash was refused by the permission classifier and I did not retry it.
- Stars, licence and archived status were therefore read from each public repo page (github.com/OWNER/REPO) via WebFetch on 2026-10-03. GitHub abbreviates stars to 0.1k, so figures are "as displayed", not exact integers. Anything displayed as 5.1k or higher is safely over the threshold. A repo displayed as "5.0k" cannot be proven to be above 5,000 and is treated as excluded (sitespeed.io).
- Last-commit dates come from each repo's public commits Atom feed (github.com/OWNER/REPO/commits/HEAD.atom), which gives exact timestamps. This is the "last push to the default branch" proxy. Where I did not pull the feed, the cell says "not checked".
- WebFetch summarises the page with a small model, so there is a residual risk of misreads. One anomaly: firecrawl/firecrawl and microsoft/markitdown both came back as "188.1k" on two separate fetches (forks differed: 10.0k vs 13.9k). Both are far above 5k either way, but treat the exact figures as approximate. Scrapling (85.3k) was re-quoted verbatim and confirmed as displayed.
- Rule: dropped repos are in section 4 ("excluded (<5k)").

## 2. Key finding for a local-business agent

There is almost no >5k open-source tooling that is specific to local SEO (Google Business Profile, citations/NAP, geo-grid rank tracking, review management) or to GEO/AI-visibility tracking. Every purpose-built local or GEO repo I found is under 5k stars (largest: open-seo-mcp-skills 3.3k, GEOFlow 3.7k, geo-optimizer-skill 974, localseoskills 107). The >5k repos are general-purpose building blocks (browsers, crawlers, extractors, auditors, agent frameworks, MCP, data libs) plus two large SEO-specific projects (every-app/open-seo and AgriciDaniel/claude-seo). Consequence: the local and GEO logic (GBP audit, NAP consistency, local schema, citation checks, AI-citation tracking) is something we should build ourselves on top of official APIs and these generic parts.

## 3. Kept repositories (all >5,000 stars)

Complexity: Low = pip/npm install and call; Med = some config, state or hosting; High = significant integration or operational burden.

### 3.1 SEO-specific projects

| Repo | Stars (2026-10-03) | Licence | Last commit | What it does for our agent | Complexity |
|---|---|---|---|---|---|
| every-app/open-seo | 22.2k | MIT | 2026-10-01 | Open-source Semrush/Ahrefs alternative: keyword research, rank tracking, competitor and backlink analysis, site audits, AI-visibility features, MCP server plus agent skills. Requires a paid DataForSEO key (pay-as-you-go). Use as a reference implementation or self-host for the data layer; wrap its MCP server. | Med |
| AgriciDaniel/claude-seo | 18.2k | MIT | 2026-09-29 (v2.4.1, Sept 2026) | Claude Code plugin: 26 sub-skills, 19 sub-agents covering technical SEO, E-E-A-T, schema, GEO/AEO, llms.txt, local SEO (3-layer: GBP signals, NAP consistency, review intelligence), PageSpeed/CrUX/GSC/GA4 integration. Best source of prompts, checklists and agent decomposition to learn from. Not a runtime dependency (a plugin, tied to Claude Code). | Low to read, Med to adopt |
| goenning/google-indexing-script | 7.7k | MIT | 2024-10-10 (stale) | Bulk-submits URLs through the Google Indexing API. The API officially supports only JobPosting and BroadcastEvent pages, so it is largely irrelevant and risky for a local-service site. Do not use. | Low |
| garmeeh/next-seo | 8.5k | MIT | 2026-07-29 | JSON-LD and meta helper for Next.js. Only relevant if the client site is Next.js. | Low |
| schemaorg/schemaorg | 6.3k | Apache-2.0 | 2026-10-01 | The canonical schema.org vocabulary source and release files. Use the vocabulary data to validate that types and properties used in generated LocalBusiness / Service / FAQPage JSON-LD exist and are correctly nested. Note this checks vocabulary validity, not Google rich-result eligibility. | Low |
| gosom/google-maps-scraper | 6.3k | MIT | 2026-09-24 | Scrapes Google Maps listings (name, address, phone, rating, reviews, coordinates). Useful concept for competitor and citation data, but scraping Google Maps violates Google's terms. Prefer the official Places API or a paid SERP/Maps API in production. | Med (legal risk) |

### 3.2 Auditing and performance

| Repo | Stars | Licence | Last commit | Role | Complexity |
|---|---|---|---|---|---|
| GoogleChrome/lighthouse | 30.8k | Apache-2.0 | 2026-10-03 | Core technical audit engine: performance, SEO, accessibility, best practices (Node module/CLI). Run per key page, feed JSON to the LLM for prioritised fixes. | Low |
| ChromeDevTools/chrome-devtools-mcp | 52.9k | Apache-2.0 | 2026-10-02 | Official MCP server giving an agent a live Chrome: Lighthouse audits, performance traces, console, network. Fastest way to give the agent audit tools without writing glue. Security note in section 6. | Low |
| GoogleChrome/web-vitals | 8.6k | Apache-2.0 | 2026-10-01 | Real-user Core Web Vitals library. Only needed if we ship a snippet to the client's site for RUM; for lab and field data we can use PageSpeed Insights/CrUX APIs instead. | Low |
| GoogleChrome/lighthouse-ci | 7.1k | Apache-2.0 | 2025-06-26 (stale, ~15 months) | CI regression monitoring for Lighthouse. Stale; for scheduled monitoring we can just run Lighthouse ourselves. Skip. | Med |
| dequelabs/axe-core | 7.6k | MPL-2.0 (file-level copyleft; fine to use unmodified) | 2026-10-02 | Accessibility rules engine. Accessibility is a secondary signal for local sites and is also a legal exposure for the client; cheap to add as an audit module. | Low |
| GoogleChrome/rendertron | 5.9k | Apache-2.0 | ARCHIVED 2022-10-06 | Dynamic rendering proxy. Archived and no longer recommended by Google. Do not use. | n/a |

### 3.3 Crawling, rendering and extraction

| Repo | Stars | Licence | Last commit | Role | Complexity |
|---|---|---|---|---|---|
| microsoft/playwright | 97.0k | Apache-2.0 | 2026-10-03 | Headless browser for JS-rendered pages, screenshots, mobile emulation, citation-page checks. The foundation of the crawl layer. | Low |
| microsoft/playwright-mcp | 37.8k | Apache-2.0 | 2026-09-28 | Playwright as an MCP server using accessibility snapshots; fastest way to give an LLM a browser. Overlaps with chrome-devtools-mcp; pick one. | Low |
| puppeteer/puppeteer | 95.6k | Apache-2.0 | 2026-10-02 | Alternative to Playwright; no reason to run both. | Low |
| unclecode/crawl4ai | 84.7k | Apache-2.0 plus attribution requirement (badge or text citation) | 2026-09-25 (v0.9.4, 2026-09-23) | LLM-oriented crawler: Playwright-based, outputs clean Markdown, structured extraction, deep-crawl strategies. Best fit for crawling a local-business site (tens to hundreds of pages) into LLM-ready content. | Low to Med |
| scrapy/scrapy | 64.6k | BSD-3-Clause | 2026-10-02 | Industrial crawler for large crawls (robots, throttling, pipelines). Overkill for a typical small local site; useful for directory/citation or competitor crawls at scale. | Med |
| apify/crawlee | 26.0k | Apache-2.0 | 2026-10-02 | Node.js crawler with Playwright/Puppeteer and proxy rotation; the Node equivalent of Scrapy plus Crawl4AI. Use only if the stack is TypeScript. | Med |
| gocolly/colly | 25.5k | Apache-2.0 | 2026-09-28 | Go scraping framework; only if the stack is Go. | Med |
| firecrawl/firecrawl | 188.1k (see caveat) | AGPL-3.0 core, MIT SDKs/UI | 2026-10-03 | Crawl/scrape/search API producing LLM-ready Markdown and structured data. AGPL core is a licence trap if self-hosted and modified; using the hosted API or only the MIT SDKs avoids it. | Low (hosted) / High (self-host) |
| firecrawl/firecrawl-mcp-server | 7.5k | MIT | 2026-10-02 | MCP wrapper around Firecrawl's API (scrape, map, search, crawl). Pairs with the hosted service. | Low |
| adbar/trafilatura | 6.9k | Apache-2.0 (v1.8.0 and later; earlier versions GPLv3+) | 2026-10-02 | Main-content, metadata, comments and sitemap extraction from HTML; strong benchmark results. Use for content-quality analysis, boilerplate removal and sitemap discovery. Pin version at or above 1.8. | Low |
| mozilla/readability | 11.5k | Apache-2.0 | 2026-07-09 | Firefox Reader View algorithm in JS; Node-side alternative to trafilatura. | Low |
| cheeriojs/cheerio | 30.5k | MIT | not checked | jQuery-style HTML parsing for Node. Only if TypeScript stack. | Low |
| jina-ai/reader | 12.1k | Apache-2.0 | 2026-05-22 | URL to Markdown (r.jina.ai) and self-hostable. Useful for quick page-to-LLM conversion; slower update cadence. | Low |
| microsoft/markitdown | ~188k (see caveat) | MIT | 2026-10-03 | Converts PDFs, Office files, images to Markdown. Useful for ingesting client brochures, menus, price lists. | Low |
| D4Vinci/Scrapling | 85.3k | BSD-3-Clause | 2026-09-30 | Adaptive scraping with anti-bot bypass. Capability is a ToS and ethics risk for an agency; for our own client sites we do not need it. | Med |
| ScrapeGraphAI/Scrapegraph-ai | 31.5k | MIT | 2026-09-25 | LLM-driven scraping pipelines. Not needed if Crawl4AI plus Pydantic extraction is used. | Med |
| browser-use/browser-use | 117k | MIT | 2026-09-28 (checked repo header) | Agentic browser control. Only if we need agent-driven interactions (e.g. checking a booking widget); too heavy for plain audits. | Med |
| browserbase/stagehand | 25.5k | MIT | not checked | Natural-language browser automation SDK; overlaps with browser-use. | Med |

### 3.4 Agent frameworks, SDKs and LLM building blocks

| Repo | Stars | Licence | Last commit | Role | Complexity |
|---|---|---|---|---|---|
| anthropics/claude-agent-sdk-python | 8.2k | MIT (SDK); bundles the Claude Code CLI, governed by Anthropic's commercial terms | 2026-10-02 | Run the agent loop with tools, in-process MCP servers and hooks on Claude. Most direct way to build this agent on Claude. | Low to Med |
| modelcontextprotocol/python-sdk | 24.5k | MIT | 2026-10-02 | Build our own MCP servers (GBP, GSC, citation tracker) in Python. | Low |
| modelcontextprotocol/typescript-sdk | 13.5k | Apache-2.0 for new contributions, MIT for existing | not checked (v2, MCP 2026-07-28 spec) | TypeScript equivalent. | Low |
| modelcontextprotocol/servers | 91k | Apache-2.0 new, MIT existing | 2026-09-22 | Reference servers: Fetch, Filesystem, Git, Memory, Time. Described as reference, not production-grade. Many (Brave Search, GitHub, Drive) were moved to an archive repo. | Low |
| anthropics/skills | 179.5k | Apache-2.0 for most; document skills are source-available only | not checked | Skill format and examples; helpful if we package SEO procedures as skills. | Low |
| langchain-ai/langgraph | 42.7k | MIT | 2026-10-02 | Durable stateful agent graphs with human-in-the-loop. Choose if we need long-running audit workflows with approval gates. | Med |
| langchain-ai/langchain | 147.4k | MIT | not checked | Large integration surface; not needed if we keep the stack lean. | Med |
| crewAIInc/crewAI | 59.3k | MIT | 2026-10-03 | Role-based multi-agent crews; fast prototyping, less control than LangGraph or the Claude Agent SDK. | Med |
| openai/openai-agents-python | 29.8k | MIT | 2026-10-02 | Lightweight agent framework with tracing; supports other models via LiteLLM. | Low to Med |
| pydantic/pydantic-ai | 20.4k | MIT | 2026-10-03 | Typed agent framework with structured outputs; good for schema-validated audit findings. | Low |
| google/adk-python | 21.7k | Apache-2.0 | not checked | Google Agent Development Kit. Only if we go Gemini and Vertex native. | Med |
| microsoft/agent-framework | 13.9k | MIT | not checked | Successor to AutoGen. | Med |
| microsoft/autogen | 61.2k | MIT code, CC-BY-4.0 docs | 2026-04-06 (MAINTENANCE MODE) | Superseded by Microsoft Agent Framework; do not start new work on it. | n/a |
| mastra-ai/mastra | 28.5k | Apache-2.0 core, source-available Enterprise License in ee/ | not checked | TypeScript agent framework; licence split needs review. | Med |
| vercel/ai | 27.1k | licence file present (type not shown by my fetch; believed Apache-2.0, unverified) | not checked | TypeScript LLM toolkit; only for a Next.js stack. | Low |
| run-llama/llama_index | 52.4k | MIT | not checked | RAG and document parsing; company focus has shifted to its commercial LlamaParse. | Med |
| stanfordnlp/dspy | 38.5k | MIT | 2026-10-02 | Programmatic prompt optimisation; useful later to tune audit and rewrite prompts against evals. | Med |
| 567-labs/instructor | 14.0k | MIT | 2026-09-11 | Structured outputs via Pydantic across providers. Overlaps with Pydantic AI and native structured outputs. | Low |
| BerriAI/litellm | 60.1k | MIT core; separate commercial licence for enterprise/ folder | 2026-10-03 | Single OpenAI-format interface to 100+ models. Key use: GEO measurement, querying several LLMs and search-enabled models for brand mention and citation. | Low (library) / Med (proxy) |
| ollama/ollama | 182.1k | MIT | not checked | Local LLM runner for cheap bulk classification. Optional. | Low |
| langfuse/langfuse | 35.3k | MIT, ee/ folders under a different licence | 2026-10-02 | LLM tracing, evals, cost tracking. Valuable for auditing agent runs and cost per client. | Med |
| n8n-io/n8n | 206.5k | Sustainable Use License (fair-code, NOT open source) | 2026-10-03 | Workflow automation (scheduled reports, notifications). Licence restricts offering it as a hosted service to others; read before using in an agency product. | Med |

### 3.5 NLP, embeddings and storage

| Repo | Stars | Licence | Last commit | Role | Complexity |
|---|---|---|---|---|---|
| UKPLab/sentence-transformers | 19.1k | Apache-2.0 | 2026-09-21 | Local embeddings for semantic similarity: content gap analysis, page-to-query matching, topic clustering, cannibalisation detection. | Low |
| explosion/spaCy | 33.9k | MIT | 2026-10-01 | Entity recognition, lemmatisation: pull place names, services, entities for local-relevance checks and entity consistency. | Low |
| pgvector/pgvector | 23.2k | PostgreSQL-style licence per LICENSE file (type not shown in my fetch; unverified) | not checked | Vector storage in Postgres for page and chunk embeddings. | Low |

### 3.6 Data, reporting and geo

| Repo | Stars | Licence | Last commit | Role | Complexity |
|---|---|---|---|---|---|
| googleapis/google-api-python-client | 8.9k | Apache-2.0 | 2026-07-29 (maintenance mode, security fixes only) | Official client for Search Console, Business Profile and other Google discovery-based APIs. | Low |
| googleapis/google-api-nodejs-client | 12.3k | Apache-2.0 | not checked (maintenance mode) | Node equivalent. | Low |
| pandas-dev/pandas | 49.9k | BSD-3-Clause | not checked | Data wrangling for GSC and rank exports. | Low |
| plotly/plotly.py | 18.8k | MIT | not checked | Interactive charts for client reports. | Low |
| gboeing/osmnx | 5.9k | MIT | 2026-07-31 | OpenStreetMap geodata: build service-area polygons and neighbourhood or competitor radius analysis. Marginal; optional. | Med |

## 4. Excluded (<5k stars, or at-threshold and unverifiable)

Each is a repo I verified and dropped, however good. Stars as displayed on 2026-10-03.

- At or below threshold: sitespeedio/sitespeed.io (5.0k, cannot prove >5,000; displayed "5.0k"), harlan-zw/unlighthouse (4.9k), openvenues/libpostal (4.9k), geopy/geopy (4.9k), pa11y/pa11y (4.6k, LGPL-3.0), osm-search/Nominatim (4.5k, GPL-3.0), MaartenGr/KeyBERT (4.2k), lycheeverse/lychee (4.0k), anthropics/anthropic-sdk-python (3.9k).
- SEO/GEO specific: Ryze-AI-Adgent/open-seo-mcp-skills (3.3k), yaojingang/GEOFlow (3.7k), notfair-plugin (3.9k), aaron-marketing-skills (2.9k), AminForou/mcp-gsc (1.8k), advertools (1.5k), spatie/schema-org (1.5k), LibreCrawl (1.0k), Auriti-Labs/geo-optimizer-skill (974), AgriciDaniel/codex-seo (777), SEOnaut (803), SerpBear (2.1k), cablate/mcp-google-map (467), garrettjsmith/localseoskills (107), Elmo (408), GetCito (445), OneGlanse (198), Gego, local-falcon/mcp (24).
- Libraries: AnswerDotAI/llms-txt (2.6k), anthropics/anthropic-sdk-typescript (2.1k), anthropics/claude-agent-sdk-typescript (1.8k, also Commercial Terms), JustinBeckwith/linkinator (1.3k), google/schema-dts (1.2k), textstat (1.4k), scrapinghub/extruct (972), google/robotstxt (3.5k).

## 5. Recommended shortlist (coherent stack, 12 components)

Principle: lean Python-first stack; the Claude Agent SDK is the brain, MCP is the tool boundary, and everything proprietary to local SEO is ours.

| # | Component | Repo | Why |
|---|---|---|---|
| 1 | Agent runtime | anthropics/claude-agent-sdk-python (8.2k) | Native Claude loop, hooks, in-process MCP tools. Alternative if we want model-agnostic graphs: LangGraph (42.7k). |
| 2 | Tool protocol | modelcontextprotocol/python-sdk (24.5k) | Expose our own tools (GBP, GSC, citations, schema validator) as MCP servers. |
| 3 | Rendering | microsoft/playwright (97.0k) | Rendered DOM, screenshots, mobile views; one browser engine for everything. |
| 4 | Site crawl to Markdown | unclecode/crawl4ai (84.7k) | LLM-ready content of a 10 to 500 page local site. Add Scrapy only if we need large crawls. |
| 5 | Main-content and sitemap extraction | adbar/trafilatura (6.9k) | Boilerplate stripping, metadata, sitemap parsing, text for content scoring. |
| 6 | Technical audits | GoogleChrome/lighthouse (30.8k) via ChromeDevTools/chrome-devtools-mcp (52.9k) | Perf, SEO, a11y, CWV scoring with no custom audit engine. |
| 7 | Schema vocabulary | schemaorg/schemaorg (6.3k) | Source of truth for validating LocalBusiness subtypes, properties and nesting. |
| 8 | Multi-model GEO probing | BerriAI/litellm (60.1k) | Query several LLM and search-enabled models for prompts like "best plumber in X" and parse citations. |
| 9 | Embeddings | UKPLab/sentence-transformers (19.1k) with pgvector (23.2k) | Semantic gap analysis, service-page to query matching. |
| 10 | Reporting data | pandas (49.9k) with plotly.py (18.8k) | Client-facing reports and charts. |
| 11 | Google data | googleapis/google-api-python-client (8.9k) | Search Console and Business Profile API access. |
| 12 | Reference, not dependency | every-app/open-seo (22.2k) and AgriciDaniel/claude-seo (18.2k) | Learn their local-SEO decomposition and prompts; optionally wrap open-seo's MCP for DataForSEO-backed keyword and rank data. |

Optional additions: Langfuse (35.3k) for tracing and cost per client; Pydantic AI (20.4k) or native structured outputs for typed findings; axe-core (7.6k) for an accessibility module.

### Build ourselves vs reuse

Reuse (commodity, well maintained): browser automation (Playwright), crawl and extraction (Crawl4AI, trafilatura), Lighthouse audits, schema.org vocabulary, embeddings, LLM routing, MCP plumbing, Google API clients, charts.

Build ourselves (our differentiation and where no >5k repo exists):
1. Local SEO audit logic: GBP completeness, NAP consistency across the site and citations, service-area pages, review velocity and response, local landing-page quality, map-pack factors.
2. LocalBusiness JSON-LD generator and validator tuned to Google's rich-result requirements (the vocabulary alone does not tell you what Google needs).
3. GEO measurement: prompt sets per business and city, running through LiteLLM, brand-mention and citation extraction, share-of-voice over time. No >5k tracker exists; the small OSS ones (Elmo, Gego) can be read for ideas.
4. llms.txt and AI-crawler readiness checks (robots.txt rules for GPTBot, ClaudeBot, PerplexityBot, Google-Extended). The llms-txt spec repo is only 2.6k stars, and the check is a small amount of code anyway.
5. Prioritisation, scoring and client-friendly reporting; the agent's judgement layer.
6. Guardrails: URL allow-listing, SSRF protection, prompt-injection hygiene on crawled content (section 6).

## 6. Risks, licence traps and maintenance flags

Licence traps for a commercial agency:
- Firecrawl is AGPL-3.0 at its core. Running a modified copy as a network service for others triggers source-disclosure obligations. Safer: use the hosted API plus MIT SDKs, or choose Crawl4AI (Apache-2.0).
- Crawl4AI is Apache-2.0 but its README requires an attribution badge or text citation when used. Cheap, but must be honoured.
- n8n uses the Sustainable Use License (fair-code, not OSI open source): internal use is fine, but offering it as a service or product to clients is restricted. Legal review before building a client-facing product on it.
- Mixed licences: LiteLLM (enterprise/ folder), Langfuse (ee/), Mastra (ee/), anthropics/skills (document skills source-available), trafilatura (v1.8.0 and later only is Apache-2.0; earlier is GPLv3+), axe-core (MPL-2.0 file-level copyleft). Claude Agent SDK repo is MIT but ships the Claude Code CLI under Anthropic's commercial terms.
- Excluded for licence anyway: Nominatim (GPL-3.0), pa11y (LGPL-3.0).

Legal and ToS risk:
- gosom/google-maps-scraper and Scrapling (anti-bot bypass) conflict with Google's terms and site ToS. Use official Places and Business Profile APIs for production data.
- google-indexing-script abuses the Indexing API for non-eligible page types and has not had a commit since 2024-10-10.

Maintenance flags:
- Archived: GoogleChrome/rendertron (2022). Maintenance mode: microsoft/autogen (use Microsoft Agent Framework), google-api-python-client and google-api-nodejs-client (security fixes only; still fine and stable).
- Stale: GoogleChrome/lighthouse-ci (last commit 2025-06-26), goenning/google-indexing-script (2024-10-10), jina-ai/reader (2026-05-22, slow cadence), mozilla/readability (2026-07-09).
- Fast-moving APIs: Claude Agent SDK bumps its bundled CLI almost daily (2.1.287 and 2.1.288 on 2026-10-01 and 10-02); MCP TypeScript SDK is now v2 against the 2026-07-28 spec; Playwright MCP is still 0.0.x. Pin versions and add contract tests.

Security risks:
- Prompt injection from crawled pages: an SEO agent reads arbitrary third-party HTML. Treat all fetched content as untrusted data, strip or sandbox it, and never let page text trigger tool calls with side effects.
- Browser-control MCPs (chrome-devtools-mcp, Playwright MCP) expose the browser's contents and sessions to the model. Run them in an isolated profile with no logged-in sessions.
- The MCP reference "fetch" server can request internal URLs (SSRF risk). Add allow/deny lists and block private IP ranges.
- Third-party Claude plugins and skills (claude-seo, open-seo skills) execute with the agent's privileges. Review code, pin to a commit, and do not auto-update.
- Supply chain: LiteLLM, MarkItDown and similar widely deployed Python packages are attractive targets. I recall reports of a PyPI compromise affecting LiteLLM earlier in 2026, but I could not verify this during the session. Pin hashes and verify before installing.
- MarkItDown's own README warns it performs I/O with the privileges of the process: sanitise inputs and run it in a sandbox.

## 7. Gaps / things I could not verify

- Exact star integers: the GitHub API and shields endpoints were blocked, so counts are the abbreviated figures shown on repo pages (0.1k resolution). sitespeed.io (5.0k) and any other near-threshold repo cannot be proven above or below 5,000.
- The page summariser may misread values. The identical "188.1k" for firecrawl/firecrawl and microsoft/markitdown is unusual (confirmed twice for each, forks differ) but I could not cross-check against the API.
- Last-commit dates were pulled for about 45 of the kept repos; rows marked "not checked" lack one (langchain, llama_index, ADK, Mastra, vercel/ai, anthropics/skills, TS MCP SDK, Cheerio, Stagehand, Ollama, pgvector, pandas, plotly, Node Google client, Agent Framework).
- Licences not clearly shown by my fetch: vercel/ai (LICENSE file present, type unseen) and pgvector (LICENSE file present, type unseen). I believe Apache-2.0 and the PostgreSQL licence respectively, but this is from memory, not verified.
- Releases and version dates were mostly not shown on the repo pages; only Crawl4AI (v0.9.4, 2026-09-23), claude-seo (v2.4.1, Sept 2026), and the Agent SDK's bundled CLI bumps were seen.
- I did not read any repo in depth via add_repo; capability descriptions come from README summaries. I did not test installation, performance or output quality of any tool.
- I could not confirm that no >5k local-SEO or GEO repo exists; I searched GitHub topics (seo, seo-tools, seo-audit, seo-analysis, seo-crawler, ai-seo, generative-engine-optimization, geo-optimization, llms-txt, google-business-profile, local-seo) sorted by stars plus web searches, and all relevant hits beyond open-seo and claude-seo were under 4k. Unindexed or oddly-tagged repos may exist.
- The LiteLLM supply-chain concern above is from memory only.
