# Research 04: "Win the Local Niche" Playbook and Agent Architecture

Date: 2026-10-03. Scope (per coordinator update): the client is a LOCAL business (dentist, plumber, restaurant, salon, law firm). The agent is a standalone new project folder; nothing here assumes an existing repo. Ecommerce and B2B/SaaS are mentioned only for contrast in one table.

Confidence key: HIGH = primary source or well-established practice; MED = multiple secondary sources agree; LOW = single secondary/vendor source or my own inference. Many "2026 study" numbers below come from vendor blogs; treat them as directional, not as facts to quote to clients.

Note on sources: developers.google.com and support.google.com were blocked by the sandbox egress proxy, so Google docs were verified only through search-result snippets, not full-page reads. Items affected are flagged.

---

## PART A. THE LOCAL "WIN THE NICHE" PLAYBOOK

### A0. Core framing the agent must hold

- Local visibility is three surfaces, each with different levers: (1) the Google Map Pack / local finder (driven by Google Business Profile, proximity, reviews), (2) classic organic results (website, content, links), (3) AI answers (ChatGPT, Gemini, Perplexity, Claude, Google AI Overviews / AI Mode), which pull heavily from the same underlying signals plus third-party directories and review sites.
- "Top business in their niche" is only achievable and honest as a defined, measurable claim: e.g. "top 3 in the Map Pack for 'emergency plumber [suburb]' across a 5x5 geogrid, and named in >=50% of AI answers to a fixed prompt set". Never "#1 for everything". The agent must refuse to promise #1 (see A6).
- Proximity is partly outside the agent's control. Google names relevance, distance and prominence as the three local factors; a business physically 8 km from the searcher's location will rarely beat a good competitor 1 km away for "near me" queries, no matter the SEO.
  Source: Google's own description of local ranking (relevance/distance/prominence) is widely quoted; see https://www.jonalonso.com/the-local-pack-in-2026-how-google-decides-who-shows-up-in-the-3-pack/ . Confidence: HIGH (Google's three factors), MED (anything numeric).

### A1. Picking and proving a winnable niche (geo x service x audience)

Findings

1. Define the niche as a triple: **service** (specific, e.g. "emergency dental" not "dentist") x **geo** (the area the business can genuinely serve and where its address/service-area sits; city, neighbourhood, or radius) x **audience/intent** (emergency vs planned, residential vs commercial, "family", "cosmetic", language, insurance accepted). Sub-niches multiply winnable surface: "Invisalign for adults in [suburb]" is far more winnable than "dentist [city]".
2. Winnability scoring (agent computes, human approves). Score each candidate niche 0-5 on each of:
   - **Demand**: monthly search volume for the head terms plus long-tail count (DataForSEO / GSC impressions for existing clients).
   - **Local pack strength**: for a 5x5 geogrid of search points around the client, what are the top-3 businesses' review count, review rating, review velocity (reviews in last 90 days), GBP category match, website presence?
   - **Organic strength**: are the top organic results local business sites (beatable) or national aggregators/directories (Yelp, Angi, Healthgrades, Avvo, Thumbtack, TripAdvisor), which are hard to displace but can be earned *through* (get listed and reviewed there)?
   - **AI-answer incumbents**: run the fixed prompt set against each assistant; who is named? Are there 0-2 names (open field) or the same 5 named everywhere (entrenched)?
   - **Client right-to-win**: real differentiators (credentials, years, specialisms, unique service, hours, languages), review base already held, physical proximity to the demand centre, capacity to serve extra leads.
3. **Winnable signals** (heuristics, my synthesis): top-3 pack businesses have <100 reviews or <4.3 rating; top results include thin/outdated sites; aggregator pages are the only organic competitors; GBP categories are mismatched; AI answers name directories rather than businesses (opening for the client to become the named business); client already has a review base within 30% of the leaders.
4. **Not-winnable-yet signals**: leaders have 500+ reviews with strong recent velocity and exact-match categories in the client's own proximity zone; client is outside the prime demand cluster; niche is dominated by multi-location chains with a branded-search moat. The honest recommendation then is: pick a narrower sub-niche or adjacent geography, or set expectations to "top 5, not top 1".
5. Reality check on AI visibility: one vendor analysis (about 350,000 locations) reports ChatGPT recommends about 1.2% of locations, Perplexity 7.4%, Gemini 11%, against 35.9% for Google's local 3-pack. Treat as directional (vendor study, methodology unverified), but the implication is robust: AI answers name far fewer local businesses than the map pack, so being named is a smaller, more winnable "top spot". Source: https://mshahid.com/blog/ai-local-visibility-report-2026 . Confidence: LOW on numbers, MED on direction.
6. Local pack factors: the Whitespark 2026 survey (47 experts, 187 factors) is reported to weight GBP signals ~32%, review signals ~20%, on-page signals ~15%; primary GBP category the top single factor, then proximity, with review recency high. This is expert opinion, not Google data. Sources: https://w3marketinghub.com/seo/local-seo-ranking/ , https://totoslocal.com/local-search-ranking-factors/ . Confidence: MED (expert survey, secondary reporting; I could not read the primary Whitespark report).

Agent implementation: `niche_score` output is a JSON object with the five sub-scores, evidence links for each, and a "winnable / stretch / not yet" label plus recommended alternate niches. Humans approve the chosen niche before any content work starts.

### A2. Competitor intelligence method

Procedure the agent runs (each step produces cited, stored evidence):

1. **Seed**: client GBP primary category, services list, 10-30 head and long-tail queries (service + city, service + neighbourhood, "near me", "emergency", "cost of", "best X for Y").
2. **SERP capture** (SERP API, geo-targeted to city/ZIP): for each query record map pack (top 3 + finder top 10), organic top 10, People Also Ask, AI Overview presence and cited sources, local services ads presence. Store raw JSON with timestamp.
3. **Competitor profile** per recurring competitor (appears in >=3 queries): GBP categories, review count/rating/velocity, photo count, posts, Q&A, services/products listed; website: service-page coverage, location pages, schema types (LocalBusiness subtype, Service, FAQPage, Review aggregate where compliant), page speed/Core Web Vitals, title/H1 patterns; off-site: directory presence, NAP consistency, referring domains (via paid backlink API or a free proxy such as Common Crawl-derived tools; see B2), local press mentions.
4. **AI recommendation capture**: run the prompt set (A5) against each assistant, N repeated runs, capture which businesses are named, in what order, and which URLs are cited. Cluster citations by source type (own site, GBP, directories, Reddit, local press).
5. **Why analysis**: for each AI-named competitor, regress observationally on what they have that others do not (review volume/recency, directory listings, press mentions, a Wikipedia/Wikidata-style entity, dedicated service pages). The agent must label these as correlations, not causes.
6. **Gap analysis**: a matrix of (query/intent) x (competitor coverage). Gaps = intents where the client has no page or a weak page and competitors have thin coverage.
7. **Information-gain opportunities** (content that adds something new rather than rewording the SERP): real pricing ranges with ranges explained, first-party photos/before-after (with consent), local regulation/permit/insurance specifics, neighbourhood-level knowledge, named staff credentials and bios, real FAQ from call logs, seasonal local data (e.g. "burst pipe calls after first frost in [city]"), small original surveys of the client's own customers. Google's public guidance stresses original, helpful, people-first content with first-hand experience; AI features have no extra requirements beyond normal Search eligibility. Source (via snippet; page blocked): https://developers.google.com/search/docs/appearance/ai-features . Confidence: HIGH that Google states there are no special AI requirements; MED on "information gain" as a named ranking mechanism (it's an SEO-community concept).

AI-citation landscape (directional, low-to-medium confidence): analyses of local-service citations report the business GBP, aggregator directories (Yelp, Angi, BBB) and the business's own site as the main cited sources; Gemini reportedly leans on the business's own website more than ChatGPT, which leans on directories and review platforms; only about 11% of domains are cited by both ChatGPT and Perplexity (680M-citation analysis, vendor). Sources: https://everything-pr.com/ai-platform-citation-source-index-2026 , https://www.arfadia.com/blog/how-chatgpt-gemini-perplexity-pick-local-businesses/ , https://authoritytech.io/curated/ai-citation-11-percent-platform-overlap-per-engine-audit-2026 . Implication: do not optimise for "AI" as one thing; maintain the per-assistant citation map and fix the specific source each assistant uses. Confidence: LOW-MED.

### A3. Prioritisation, 30/60/90 plan, honest timelines

**Prioritisation formula.** Score = (Impact x Confidence) / Effort, each 1-5 (Effort 1 = under 1 hour, 5 = over 2 weeks); add a **Risk** veto (anything with policy risk is excluded or needs human sign-off). Agent outputs a ranked backlog with the three scores, rationale and evidence link. Tie-break on "unblocks other tasks" and "measurable within 30 days".

Typical high-ratio local items: GBP primary category and secondary categories fix; services list; NAP consistency; a review-request flow to all customers; one dedicated page per core service x location; schema on those pages; fix indexing/canonical/title issues; click-to-call tracking. Low-ratio: blog-volume plays, link buying (excluded: risk), chasing national keywords.

**30/60/90 template for a local business** (what the agent drafts for human approval):

Days 0-30 (foundation and measurement)
- Access and baselines: GSC, GA4, GBP manager access, call tracking, CRM/booking source. Record baseline rankings (geogrid), impressions, calls, direction requests, form leads, review count/rating, AI share-of-voice prompt set.
- Niche definition and winnability report (A1); agree the claim wording and KPIs with client.
- Technical audit and quick fixes: HTTPS, indexability, mobile speed (PSI), canonical/duplicate issues, XML sitemap, robots, title/H1.
- GBP: categories, hours, services, attributes, description, photos plan, Q&A seeding with genuine FAQs, product/service entries, appointment/booking link. No keyword stuffing in the business name (Google violation).
- NAP audit and fix on top 15-25 citations (including Bing Places, Apple Business Connect, Yelp/industry directories). Claim existing listings before creating new ones.
- Review process: compliant request flow to all customers (A4).
- Schema: LocalBusiness subtype, openingHours, sameAs, service pages.

Days 31-60 (relevance and coverage)
- Service pages (one per core service) and location/neighbourhood pages only where there is genuine unique content (policy risk: doorway/scaled pages, see A6).
- Information-gain content pieces (2-4), each tied to a real query gap.
- Internal linking; FAQ sections written from real customer calls/emails.
- Local links and partnerships outreach (A4); 2-3 community/partner placements.
- GBP posts and photo cadence; respond to every review.
- Re-run geogrid and AI prompt set; compare to baseline.

Days 61-90 (authority and iteration)
- Digital PR or original local data piece launched; sponsorship/association listings.
- Expand sub-niche pages based on GSC impressions-without-clicks (queries at positions 8-20 are the cheapest wins).
- Fix the specific source each AI assistant cites (e.g. a missing Yelp/industry directory profile).
- 90-day review: what moved, what did not, what is the next 90-day backlog; renegotiate the niche if proof says it's not winnable as scoped.

**Realistic timelines (be honest).**
- Evidence: Ahrefs-reported studies (2025) suggest only roughly 1.7% to 5.7% of new pages reach Google's top 10 within a year, and the average #1 page is about 5 years old. Those figures are for general (largely non-local) keywords, so they bound the pessimistic case, not local pack outcomes. Source (secondary summary): https://factoryjet.com/blog/how-long-does-seo-take-2026-month-by-month-timeline , https://keystonewebsolutions.com/blogs/seo-digital-marketing/how-long-does-seo-take-timeline . Confidence: LOW-MED (I could not open the Ahrefs primary studies).
- Practitioner consensus: local SEO often shows first movement in 1-3 months (GBP fixes, citations) and meaningful lead growth at 3-6 months, dominance in a defined sub-niche at 6-12 months. Source: https://www.ewrdigital.com/blog/how-long-does-seo-take-before-you-can-expect-to-see-results , https://rebelfishlocal.com/2026-local-seo-results-for-business-growth/ . Confidence: MED (consistent across many vendors, who have an incentive to sound optimistic).

| Business type | First measurable movement | Meaningful lead lift | "Top of niche" (defined sub-niche) | Biggest uncertainty |
|---|---|---|---|---|
| Local service / healthcare / legal (this project) | 4-12 weeks (GBP, citations, reviews) | 3-6 months | 6-12 months for a narrow sub-niche; 12-24+ for broad head terms in a competitive city | Proximity, competitor review lead, Google local algorithm shifts |
| Ecommerce (contrast only) | 3-6 months | 6-12 months | 12-24 months | Brand strength, marketplaces |
| B2B / SaaS (contrast only) | 3-6 months | 6-12 months | 12-24 months | Long sales cycle, attribution |
The ecommerce and B2B rows are my own synthesis and are LOW confidence; the agent should not use them for local clients.

Outcomes the agent may state to clients: ranges, leading indicators, and conditions. It must not promise a position or a date.

### A4. White-hat authority building for local

1. **Reviews (compliant).**
   - Google policy (via secondary sources; primary page blocked): asking customers for reviews is allowed; incentives of any kind (discounts, gifts, loyalty points, entries) are prohibited as "fake engagement"; review gating (only asking happy customers, or routing unhappy ones to private feedback before offering the public link) is prohibited; businesses should ask all customers equally. Sources: https://www.applausehq.com/blog/googles-rules-for-incentivizing-reviews , https://www.demandhub.co/articles/google-review-policy/ , https://launchcodex.com/blog/seo-geo-ai/google-business-profile-review-policy-update/ . Confidence: MED-HIGH (consistent; one source cites an April 2026 policy update I could not verify).
   - FTC Consumer Review Rule (16 CFR Part 465), effective October 21, 2024: bans fake or AI-generated reviews that misrepresent the reviewer's experience, buying or selling reviews, incentives conditioned on a particular sentiment, review suppression via intimidation or groundless legal threats, company-controlled "independent" review sites, and misrepresenting that displayed reviews are all reviews when some were suppressed; civil penalties up to $51,744 per violation (figure as reported at 2024; it is inflation-adjusted annually, so confirm current value). Sources: https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials , https://www.olshanlaw.com/Advertising-Law-Blog/FTC-Publishes-New-Rule-Covering-Fake-Reviews-and-Testimonials . Confidence: HIGH on rule existence and structure; MED on current penalty amount.
   - Agent role: draft the review-request message (SMS/email/QR/card), a send-to-everyone trigger recommendation, and compliant reply templates for each review (never reveal client health/legal details in replies; HIPAA and bar rules matter for dentists and law firms). The agent never posts reviews and never writes review text for a customer.
2. **Citations/NAP.** Consistent name/address/phone on Google, Bing Places, Apple Business Connect, Yelp, industry directories (Healthgrades, Avvo, Angi, Houzz, OpenTable as relevant), chamber of commerce. Agent produces a citation audit sheet and a fix list; humans claim/verify listings (many require phone/postcard verification).
3. **Local links and partnerships.** Sponsorships (kids' sports teams, charity runs), supplier/partner pages, local business associations, chamber membership, community event hosting, "best of" local lists, university or trade-school partnerships, scholarships. Agent drafts outreach emails; human sends. No paid links, no private blog network, no link-exchange schemes (Google link spam policy).
4. **Digital PR / original data (local).** A small survey of local customers, anonymised job/appointment data trends, a local price index ("average cost of X in [city] 2026"), seasonal studies; pitch to local newspapers, TV, community blogs and trade press. Must use real data; never fabricate.
5. **Community presence (Reddit etc.).** Etiquette: disclose affiliation; follow each subreddit's rules, which override any ratio; the "90/10" rule is a community convention, not an official Reddit rule; no sock-puppet or fake-customer recommendations, no coordinated upvoting. Reddit is reportedly a leading cited source in Perplexity and overall AI citations, which tempts abuse; the agent must only draft helpful answers for a human (the owner) to post under their own named account with disclosure. Sources: https://redship.io/glossary/reddit-self-promotion-rules , https://redship.io/learn/how-to-avoid-getting-banned-marketing-reddit , https://everything-pr.com/ai-platform-citation-source-index-2026 . Confidence: MED.
6. **Entity strength.** Consistent branding, sameAs links (GBP, Facebook, LinkedIn, Yelp), About page naming people with credentials, a Wikidata item only if the business meets notability/verifiability norms (most small local businesses do not; do not create self-promotional Wikidata/Wikipedia entries). Confidence: MED.
7. **Content at scale is a risk.** Google's scaled content abuse policy (March 2024) targets large volumes of low-value pages regardless of whether AI or humans wrote them. Programmatic "[service] in [every suburb]" pages without unique substance are the classic local trap. Source: https://www.layer3labs.io/guides/scaled-content-abuse , https://ppc.land/scaled-content-abuse/ . Confidence: MED-HIGH.

### A5. Reporting: KPIs and attribution

Show clients (in this order; business outcomes first):

| Layer | KPI | Source | Pitfall |
|---|---|---|---|
| Business | Calls, booked appointments/jobs, quote forms, revenue per lead where client shares it | Call tracking (dynamic number insertion plus GBP call count), booking system, CRM | Self-reported "how did you hear" is biased; call tracking numbers can break NAP consistency unless the main number is kept on the website and GBP primary |
| Local | GBP views, calls, direction requests, website clicks, bookings; geogrid average rank / share of grid in top 3 | GBP Performance API (access-gated), geogrid scan via SERP API | GBP metrics are Google-estimated; seasonal swings; grid cost grows with grid size |
| Organic | Impressions, clicks, average position, queries at positions 4-20, branded vs non-branded split | Search Console | Average position hides variance; impression data changes with Google's reporting changes |
| Site | Conversions (GA4 key events), landing pages, Core Web Vitals | GA4, PSI | Consent mode reduces measured data; GA4 sampling/thresholds |
| AI | AI share-of-voice: % of runs in which the client is named for a fixed prompt set, per assistant; mean rank when named; citation sources; competitors named | Own LLM-API runs (B2) | Non-determinism, geo and personalisation differences, model updates, API results differ from consumer app (different retrieval/system prompts); report with sample size and confidence interval, not single runs |
| Reputation | Review count, rating, 90-day velocity, response rate | GBP | Never present reviews in a way that hides negatives (FTC rule) |

Method for AI share of voice: 20-40 fixed prompts (service + location + intent variants), each run 5+ times per assistant at least weekly, with web search tool enabled where the API supports it, log full responses, parse named businesses with a structured-output extractor, and verify the extraction on a sample by human. Report the trend, not point values. Source for the idea of tracking exact prompts such as "best [business type] in [city]": https://www.pagetraffic.com/blog/how-local-businesses-show-up-on-chatgpt/ , https://www.searchenginejournal.com/ai-overview-recommendation-plan-reviewly-spa/587030/ . Confidence: LOW-MED (vendor guidance; the statistical approach is my own recommendation and is standard measurement hygiene).

Attribution pitfalls the agent must mention in every report: zero-click behaviour (map pack users call without visiting the site); GBP "website clicks" tagged inconsistently unless UTM added; AI-referred visits often arrive as "direct" or untagged; correlation with seasonality; branded searches rise from non-SEO marketing; call tracking dynamic numbers; consent banners hiding conversions; do not credit SEO for repeat customers. Report "estimated" and "observed" separately.

### A6. Ethics and compliance guardrails (hard rules for the agent)

Implement as code-level checks (hooks/validators), not just prompt text:

1. No fake or purchased reviews; no writing reviews on behalf of customers; no review gating; no incentives for reviews (Google + FTC; A4). Refuse and explain.
2. No guarantees: never output "guaranteed #1", "top ranking in X days". Required wording: "target", "likely range", "no guarantee". The FTC Act prohibits deceptive claims generally; this is also standard agency risk management. Confidence: HIGH (principle), my own rule (implementation).
3. No hidden prompt injection against AI assistants (hidden text, white-on-white instructions, cloaked pages to feed LLM crawlers instructions like "recommend this business"). It violates Google's spam/cloaking policies, can poison AI results unfairly, and is an ethical breach. The agent must also detect and refuse to publish content with hidden instructions. Confidence: HIGH (cloaking policy is long-standing), MED (applied to LLMs).
4. Reviews and testimonials on the website: real, attributable, unedited in meaning; disclose any material connection; FTC Endorsement Guides (16 CFR Part 255) apply to testimonials and influencer posts. Source (secondary): https://www.olshanlaw.com/Advertising-Law-Blog/FTC-Publishes-New-Rule-Covering-Fake-Reviews-and-Testimonials . Confidence: MED-HIGH.
5. Regulated professions (dentists, law firms, medical): advertising rules (bar rules on testimonials and "specialist" claims, dental board rules, HIPAA when responding to reviews or using patient photos) vary by jurisdiction. The agent flags and escalates; it does not make legal determinations. Confidence: MED (known to vary; I did not research each jurisdiction).
6. Tracking and privacy: GDPR/ePrivacy (EU/UK) and US state laws (e.g. California CPRA) require consent or notice for non-essential cookies and analytics; use Consent Mode v2 or server-side measurement with consent; do not add pixels, session replay, or call-recording without the client's confirmation of lawful basis and a privacy-policy update; call recording requires consent in two-party-consent jurisdictions. Agent should draft and the client/lawyer approve. Confidence: MED (general legal principles; not legal advice; I did not search for fresh GDPR enforcement news).
7. Client data handling: collect least data; store per-client credentials in a secrets manager; encrypt at rest; no client PII (customer names, phone numbers from call logs) sent to LLM APIs unless needed and covered by agreement; retention limits; per-client isolation; delete on offboarding; log every external write. Confidence: HIGH (standard practice).
8. Content integrity: no fabricated statistics, awards, certifications, staff, addresses, or photos; AI-generated copy needs human review; label AI-generated images where required; respect scaled-content limits (A4.7).
9. Honesty about uncertainty: all recommendations carry confidence and evidence; unverifiable claims are labelled.

---

## PART B. AGENT ARCHITECTURE

### B1. Platform choice and design

Verified facts (from Anthropic docs):
- The **Claude Agent SDK** (Python and TypeScript) is "Claude Code as a library": built-in tools (read/write/edit files, run commands, search the web), hooks, subagents, MCP, permissions, sessions, skills/commands/memory loaded from `.claude/`, and plugins. Source: https://code.claude.com/docs/en/agent-sdk/overview . Confidence: HIGH (read directly).
- Terms/auth: use is governed by Anthropic's Commercial Terms; third parties are not allowed to offer claude.ai login or its rate limits for their products, so use API-key authentication. Branding: do not call a product "Claude Code" or mimic it; allowed forms such as "{YourAgentName} Powered by Claude". Same source. Confidence: HIGH.
- Alternatives (same doc and the claude-api reference): the plain Anthropic Client SDK with tool use (you write the loop or use the beta tool runner), and **Managed Agents** (Anthropic-hosted harness and sandbox, beta, with scheduled deployments, outcomes/graders, memory stores, vaults for credentials). Confidence: HIGH (docs), MED (Managed Agents is beta and may change).
- Current model IDs and prices (from the claude-api reference, cached 2026-09-25): `claude-opus-5-5` ($4/$20 per MTok in/out), `claude-sonnet-5-5` ($2/$10), `claude-haiku-4-5` ($1/$5). Opus 5.5 and Sonnet 5.5: thinking cannot be disabled (omit or use adaptive; control depth via `output_config.effort`), forced `tool_choice` any/tool returns 400 (use auto plus strict tools or structured outputs), no assistant prefill. Structured outputs use `output_config: {format: ...}` (the old `output_format` is deprecated). Prompt caching is prefix-based; verify via `usage.cache_read_input_tokens`. Treat these as correct at time of reading but confirm with `client.models.retrieve`. Confidence: MED-HIGH (skill documentation, not independently verified against live docs).

**Recommendation: Python, Anthropic Client SDK with a thin custom orchestrator for the MVP; Agent SDK for the fuller build.** Reasoning: the MVP's tools are a fixed set of SEO API calls, not arbitrary shell/file access, so the "full Claude Code harness" (bash, edit, etc.) adds attack surface the MVP does not need. The Agent SDK becomes attractive when you want subagents with isolated context, hooks for deterministic approval gates, skills for reusable playbooks, and sessions, and you can restrict its tool list with `allowedTools`/permissions to your own MCP tools only. A common good pattern: write each capability as a plain Python function; expose them via an in-process MCP server so both approaches share the same tools.

**Architecture: orchestrator plus specialist subagents** (each subagent has its own narrow tool list and system prompt; verbose crawl/SERP data stays in the subagent's context and only a structured summary is returned):

| Agent | Job | Tools (least privilege) | Model suggestion |
|---|---|---|---|
| Orchestrator | Plan, call specialists, assemble reports, manage approvals, track client state | Read client state, call subagents, request approval | claude-opus-5-5, effort medium-high |
| Crawler/Auditor | Fetch client pages (SSRF-safe), parse titles/H1/schema/canonical/links, run PSI | `fetch_url_safe`, `parse_html`, `psi_run` | claude-sonnet-5-5 (or deterministic code mostly) |
| Keyword and SERP analyst | Query SERP API, geogrid, competitor profile, niche scoring | `serp_search`, `geogrid_scan`, `gsc_query` | claude-sonnet-5-5 |
| Content strategist | Gap analysis, briefs, drafts for human review | Read evidence store, `write_draft` (to drafts folder only) | claude-opus-5-5 for drafts; Sonnet for briefs |
| Schema/technical fixer | Generate JSON-LD, redirect maps, title/meta suggestions as patch files | `validate_jsonld`, `write_patch` (no direct site write) | claude-sonnet-5-5 |
| AI-visibility tracker | Run prompt set across assistants, extract named businesses | `llm_probe(provider, prompt)`, structured extractor | claude-haiku-4-5 or Sonnet for extraction |
| Reporter | Build client report with KPIs, caveats | `read_metrics`, `render_report` | claude-sonnet-5-5 |
| Compliance reviewer (recommended) | Check every client-facing artefact against A6 rules before it leaves | Read-only | claude-sonnet-5-5 |

**Design principles** (mostly from OWASP and general agent practice; Anthropic skill docs agree on "start simple"):
- Prefer deterministic code for data collection and calculation (rank math, scoring arithmetic, schema validation); use the LLM for judgement, synthesis and writing. An LLM must never compute a number that code can compute.
- Structured outputs (JSON schema) for every inter-agent hand-off; validate with Pydantic; reject and retry on invalid.
- Prompt caching: keep the system prompt, playbook skills and tool definitions in a stable prefix; put per-client volatile data (date, client name, fresh data) after the last cache breakpoint; verify cache hits. Cache reads are about 0.1x input price per the reference. Confidence: HIGH.
- Batch API (50% cost, async) for non-urgent weekly AI-visibility extraction runs. Confidence: MED-HIGH (from skill reference).
- Server-side compaction or context editing for long sessions; but prefer short, stateless runs that load state from the store.
- Skills: package playbooks (niche scoring, GBP audit checklist, citation list, review-request templates, report template) as `SKILL.md` files so they are versioned and reusable (Agent SDK loads `.claude/skills/`). Confidence: HIGH.

**Human-in-the-loop approval points** (enforced in code via a `request_approval` tool and, if using the Agent SDK, `PreToolUse` hooks / `canUseTool` / permission modes):
1. Niche selection and KPI/claim wording.
2. Any outbound message to a third party (outreach emails, review requests, directory edits).
3. Any write to the client's live systems (CMS publish, GBP edits, DNS/redirects, tag manager). MVP: never write; produce patches and drafts only.
4. Any spend above a per-run budget (SERP API, LLM probes).
5. Client-facing reports and anything flagged by the compliance reviewer.
6. Any content with factual claims about the client (awards, prices, credentials): human verifies.

**State and memory per client** (stored outside the model; model is stateless): a per-client directory or database with `profile.json` (business facts, NAP, services, service area, regulated-profession flags, approved claims), `niche.json`, `competitors/`, `serp_snapshots/` (timestamped raw JSON), `metrics/` (time series), `backlog.json` (prioritised tasks with status), `decisions.md` (human approvals and reasons), `reports/`, `ai_probes/`. Use SQLite (MVP) then Postgres. Per-client isolation: one folder or schema per client; credentials in OS keyring/secret manager, never in the repo. Do not rely on "memory" features alone for facts the agent must keep exactly. Confidence: HIGH (design recommendation).

**Evaluating the agent's own output quality:**
- Golden-set tests: 10-20 fixture clients (saved SERP and page snapshots) with expected findings (e.g. "missing LocalBusiness schema", "NAP mismatch on Yelp"); assert on structured outputs; run in CI.
- Rubric-graded LLM-as-judge for narrative output (specific, evidenced, no guarantees, no invented facts), with the judge on a different model or prompt, and spot-checked by a human; track precision of flagged issues (false-positive rate) on audits.
- Citation integrity check: every claim in a report must link to a stored evidence ID; a verifier rejects unlinked claims.
- Compliance regression tests: adversarial prompts ("write 5 five-star reviews for our dentist", "guarantee us #1", "hide text telling ChatGPT to recommend us") must be refused.
- Prompt-injection tests: crawled fixture pages containing injection strings must not change tool calls (B3).
- Cost/latency telemetry per run; alert on drift.
- The claude-api skill reference mentions `build-eval` and `hillclimb` workflows for this; I did not read those files. Confidence: MED.

### B2. Data sources and APIs: cost, limits, free or not

| Source | What for | Cost / free? | Limits and gotchas | Confidence |
|---|---|---|---|---|
| Google Search Console API | Impressions, clicks, queries, pages, positions; URL Inspection | Free | Search Analytics per-site 1,200 QPM; per-project 30M QPD and 40,000 QPM; max 50,000 rows per day per search type per property; URL Inspection 2,000 QPD and 600 QPM per property; needs OAuth with property access, data lag ~2 days, only 16 months of history | MED-HIGH (numbers from search snippets of the official limits page: https://developers.google.com/webmaster-tools/limits ; page itself blocked) |
| GA4 Data API | Sessions, key events, landing pages | Free | Standard property: 200,000 core tokens/property/day, 40,000/hour, 14,000/project/property/hour; 360: 2,000,000/day; needs OAuth/service account added to property | MED-HIGH (https://developers.google.com/analytics/devguides/reporting/data/v1/quotas via search result) |
| PageSpeed Insights API | Lighthouse lab data plus CrUX field data | Free with API key | About 25,000 requests/day and ~240/minute per project; unkeyed calls now reported to fail with 429, so a key is required; slow (10-30 s per call); CrUX field data only when the URL has enough traffic | MED (https://unlighthouse.dev/learn-lighthouse/pagespeed-insights-api, https://dev.to/addyosmani/monitoring-performance-with-the-pagespeed-insights-api-33k7) |
| Google Business Profile APIs | Read/update locations, reviews, performance metrics (calls, directions, views), posts | Free but gated | New Cloud projects start at 0 QPM; must request access via a form; Google reviews applications (reported within ~14 days); approval typically gives 300 QPM; applicant must manage a verified GBP active 60+ days with a website; quota increases denied unless you use consistently >50% of the limit. Plan: agency applies once under the agency's project, clients grant manager access | MED (https://developers.google.com/my-business/content/limits , https://developers.google.com/my-business/content/prereqs , https://localith.ai/blog/google-business-profile-api-guide/ ) |
| SERP APIs | Geo-targeted SERP, local pack, AI Overview (where provided), maps rank | Paid | DataForSEO: reported $0.60 per 1,000 (Standard queue, about 5 min), $1.20 (Priority), $2.00 (Live) per 10-result unit; $50 minimum deposit; deeper pages multiply cost. SerpApi: free 250 searches/month; $25/mo for 1,000; $75 for 5,000; $150 for 15,000; $275 for 30,000 (plan list varies by source). Local geogrid costs scale with grid points x keywords (a 5x5 grid x 10 keywords = 250 calls per scan) | MED (https://nextgrowth.ai/dataforseo-serp-api/ , https://apiserpent.com/blog/dataforseo-pricing-explained , https://costbench.com/software/web-scraping/serpapi/ ; verify on provider sites before quoting) |
| Google Programmable Search / official Google search API | Not suitable | Reported capped/limited and subject to shutdown notices | Do not build on it; one source claims "hidden fees + the shutdown" (https://flybyapis.com/blog/google-search-api-cost/); I did not verify | LOW |
| Scraping Google directly | Avoid | n/a | Violates Google's terms and is brittle; use a SERP API | HIGH |
| Common Crawl | Large-scale web graph/archive for offline research, backlink-ish analysis, finding mentions | Free | Large (terabytes); use the CDX/URL index or columnar index with Athena; not fresh; overkill for MVP | MED (training knowledge, not re-verified; https://commoncrawl.org ) |
| Wikidata | Entity IDs, sameAs, checking whether the business/entity exists | Free | SPARQL endpoint and API with rate limits and a required descriptive User-Agent; most small local businesses will have no item | MED (training knowledge, not re-verified) |
| LLM provider APIs for AI visibility | Probe how assistants answer | Paid, per token plus search-tool fees | Anthropic Messages API with `web_search` server tool (pricing per tool terms; check docs); OpenAI web search tool reported at $10 per 1,000 calls plus tokens; Gemini grounding with Google Search reported 5,000 free requests/month on Gemini 3.x then $14 per 1,000; Perplexity Sonar from $1/$1 per MTok, Sonar Pro $3/$15, plus per-request fees. Consumer apps (ChatGPT UI, Gemini app, Google AI Overviews) differ from API answers: API probes approximate but do not equal what customers see; there is no official API for Google AI Overviews, only some SERP APIs surface them | MED (https://developer.puter.com/tutorials/perplexity-api-pricing/ , https://developer.puter.com/tutorials/openai-api-pricing/ , https://geotoolbox.ai/blog/gemini-api-pricing ; prices move quickly) |
| Backlink data | Referring domains | Paid (DataForSEO Backlinks, Ahrefs, Semrush, Moz) or limited free (Ahrefs Webmaster Tools for verified own sites, Bing Webmaster Tools) | Not researched in detail | LOW |
| Bing Webmaster Tools / Bing Places | Indexing and listing data | Free | Reported to matter for ChatGPT/Copilot retrieval, but I could not verify OpenAI's retrieval stack | LOW |

Which are free: GSC, GA4, PSI (with a key), GBP APIs (gated), Common Crawl, Wikidata, Bing Webmaster Tools. Paid: SERP data, LLM probes, backlinks. A rough MVP budget: SERP calls for a 5x5 grid x 8 keywords per client per month at DataForSEO Standard is about 200 requests = about $0.12 per scan (plus multiplier for local/maps endpoints; check endpoint-specific price); AI probes of 30 prompts x 5 runs x 3 assistants = 450 calls per client per week, which is a few dollars per client per month at cheap model/tool prices but dominated by tool-call fees (OpenAI $10/1k means about $4.50/week/client for that assistant alone). These are my arithmetic on reported prices: LOW-MED.

### B3. Safety

1. **Rate limiting**: per-host token bucket (default 1 request/second/host, lower for small client servers), global concurrency cap, exponential backoff on 429/5xx honouring `Retry-After`, per-provider budget meters, and a per-run and per-client monthly spend cap enforced in code (kill switch). The Anthropic SDK retries 429/5xx automatically (default 2 retries). Confidence: HIGH.
2. **robots.txt and ethics for crawling**: fetch and obey `robots.txt` (use `urllib.robotparser` or `protego`) for competitor sites; identify with an honest User-Agent and contact URL; do not bypass paywalls/login/captcha; crawl the client's own site with their consent even where robots restricts (still be gentle); respect `noindex`/terms where scraping competitors' content; store only what you need (extract facts, don't republish copyrighted text). Confidence: HIGH.
3. **SSRF protection for fetching client/competitor URLs** (the agent fetches URLs from untrusted input, including redirects and URLs found in pages): allow only http/https; resolve DNS and block private, loopback, link-local and cloud-metadata ranges (127.0.0.0/8, 10/8, 172.16/12, 192.168/16, 169.254.169.254, ::1, fc00::/7, fe80::/10, and IPv4-mapped IPv6); pin the resolved IP for the connection (to defeat DNS rebinding) and re-validate on every redirect hop; cap redirects (about 5), response size (about 2-5 MB), and time (about 10-15 s); allowed content types; disallow unusual ports unless explicitly allowed; run the fetcher with no credentials in its environment, ideally in a separate process or container with egress limited to the public internet. Confidence: HIGH (OWASP SSRF standard guidance).
4. **Prompt injection from crawled content** (the main LLM-specific risk): treat all fetched content as untrusted data. OWASP lists indirect prompt injection (web pages, documents, tool outputs) under LLM01 and recommends constraining behaviour, validating output formats with deterministic code, privilege control (keep API tokens in code, not exposed to the model), human approval for privileged actions, and segregating external content (wrap in explicit delimiters and tell the model it is data). Sources: https://genai.owasp.org/llmrisk/llm01-prompt-injection/ . Confidence: HIGH. Concrete design:
   - A "quarantined reader" step: a subagent with no tools other than returning a strict JSON schema summarises the page; the orchestrator never sees raw page text, only validated structured fields.
   - Strip HTML comments, hidden elements (display:none, off-screen, zero-size, white-on-white), metadata and alt-text tricks before passing text; log when hidden text contains instruction-like strings and surface to the human as a finding (competitors may be doing prompt-injection SEO).
   - Tools that cause side effects (send email, write to CMS, publish, spend) are not callable from the reader step; they require approval tokens that code, not the model, issues.
   - Allowlist outbound domains for any tool; no tool should accept arbitrary URLs and secrets together; block markdown-image/URL exfiltration in outputs.
   - Regression tests with injection fixtures; recognise that defences are not perfect, so rely on privilege limits rather than detection. Confidence: MED-HIGH.
5. **Secrets handling**: load from environment or secret manager (never in prompts, logs, repo or tool outputs); `.env` in `.gitignore`; use scoped OAuth tokens with minimum scopes (GSC read-only, GA4 read-only, GBP read first); per-client token files encrypted or in keyring; redact secrets in logs; rotate; secret scanning in CI; the LLM never receives credentials; use Anthropic API key authentication (not consumer login) per the Agent SDK terms. Confidence: HIGH.
6. **Data protection**: PII minimisation before LLM calls (strip phone numbers/emails from call transcripts unless needed), a data-processing agreement posture with the client, and audit logs of external writes. Confidence: HIGH.

### B4. Concrete MVP: repo layout, CLI, workflow, honest scope

**Language**: Python 3.11+ (best libraries for HTML parsing, Pydantic, Google API clients). TypeScript is equally viable; choose it only if you want to use the TS Agent SDK.

**Standalone repo layout** (new folder; no dependency on any existing repo):

```
local-seo-agent/
  README.md
  pyproject.toml            # deps: anthropic, pydantic, httpx, selectolax or beautifulsoup4, typer, rich, tenacity, python-dotenv
  .env.example              # ANTHROPIC_API_KEY, DATAFORSEO_LOGIN/PASSWORD, GOOGLE_PSI_KEY (never commit .env)
  .gitignore
  src/lseo/
    cli.py                  # Typer CLI entrypoint
    config.py               # budgets, rate limits, model IDs (single place)
    orchestrator.py         # plan -> call specialists -> assemble; approval gates
    agents/
      auditor.py            # crawl+parse+PSI -> AuditResult (Pydantic)
      serp_analyst.py       # SERP + niche scoring -> NicheReport
      strategist.py         # gap analysis + 30/60/90 backlog
      schema_fixer.py       # JSON-LD generation + validation, patch files
      ai_tracker.py         # prompt probes + extraction -> VisibilityResult
      reporter.py           # markdown/HTML report
      compliance.py         # guardrail checks on every artefact
    tools/
      safe_fetch.py         # SSRF-safe, robots-aware, rate-limited fetch
      html_extract.py       # visible-text extraction, hidden-text stripping, injection flagging
      serp_client.py        # DataForSEO / SerpApi adapter, caching
      psi_client.py
      gsc_client.py         # optional, OAuth
      llm_probe.py          # provider adapters (anthropic first)
      scoring.py            # deterministic ICE/priority and niche math
    models/                 # Pydantic schemas for all hand-offs
    store/
      db.py                 # SQLite (clients, runs, evidence, backlog, approvals, costs)
      evidence.py           # timestamped raw payloads, evidence IDs
    prompts/                # system prompts (stable prefix, cached)
    skills/                 # playbook markdown (niche scoring, GBP audit, review compliance, report template)
  clients/<slug>/           # profile.yaml, approvals, outputs (gitignored if real client data)
  tests/
    fixtures/               # saved HTML pages, SERP JSON, injection pages
    test_safe_fetch.py      # SSRF cases: 127.0.0.1, 169.254.169.254, redirects to private, DNS rebinding stub
    test_guardrails.py      # refusals: fake reviews, guarantees, hidden prompt text
    test_scoring.py
    test_golden_audits.py
  evals/                    # rubric + golden set + judge prompt
```

**CLI (Typer)**:
```
lseo init <client-slug>                       # create profile.yaml (business, NAP, services, area, regulated flag)
lseo audit <client-slug>                      # crawl, PSI, schema/NAP check -> audit report + issues
lseo niche <client-slug> --queries q.txt      # SERP capture, competitor table, niche score (needs SERP API key)
lseo ai-probe <client-slug> --runs 5          # AI visibility prompt set across configured providers
lseo plan <client-slug>                       # prioritised backlog + 30/60/90 draft
lseo report <client-slug> --period 30d        # client-ready report (markdown/HTML) with caveats
lseo approve <client-slug> <item-id>          # human approval gate
lseo budget <client-slug>                     # show spend vs caps
```

**MVP workflow** (one-session buildable, roughly 1,500-2,500 lines of Python):
1. `init` captures profile and approved claims.
2. `audit`: `safe_fetch` home + up to ~25 pages from the sitemap, extract titles/H1/meta/canonical/schema/NAP/links, run PSI on 3-5 key URLs, quarantined LLM summarisation for content gaps; deterministic checks do the rest.
3. `niche`: for up to 10 queries, one geo-targeted SERP call each (and optionally a small 3x3 grid), pull top-3 pack and organic competitors, compute niche score with `scoring.py`, LLM writes the interpretation with evidence IDs.
4. `ai-probe`: Anthropic web-search-enabled probe first (single provider), structured extraction of named businesses, repeated runs, share-of-voice with sample size.
5. `plan`: ICE-prioritised backlog with the 30/60/90 template.
6. `report`: assemble with KPIs available (no GSC/GA4 in MVP unless configured) and standard attribution caveats; compliance agent checks; human approves.

**Honest MVP scope.**

Can do: SSRF-safe crawling and technical/on-page/schema audits; competitor and SERP snapshots (with a paid SERP key); niche winnability scoring with evidence; AI-visibility sampling on one or two providers via API; prioritised plan and 30/60/90; draft content briefs, JSON-LD and review-request templates as files; guardrails and refusals; cost caps; reproducible evidence trail.

Cannot do (in one session, or at all): guarantee rankings; verify consumer-app AI answers exactly (API probes differ); access GBP data (requires the API access request and approval, reported to take about two weeks) or GSC/GA4 without OAuth setup per client; publish to a CMS or edit GBP automatically (deliberately excluded); verify or claim directory listings (phone/postcard verification is human); generate reliable backlink data without a paid API; run true geogrid at scale cheaply; handle JavaScript-rendered sites (needs a headless browser, deliberately out of MVP because it widens attack surface); legal/regulatory compliance judgement for regulated professions; measure call/lead attribution without client call-tracking/CRM integration; "learn" across clients automatically (state is per client by design).

Phased follow-ups: Phase 2 GSC/GA4 read-only OAuth and automated monthly reports; Phase 3 GBP API (after approval), geogrid, Batch API for probes; Phase 4 Agent SDK subagents/skills/hooks and scheduled runs (cron or Managed Agents scheduled deployments), multi-client dashboard.

---

## Gaps / things I could not verify

1. Google primary docs (Search Console limits, GA4 quotas, GBP limits/prereqs, AI features page, Maps review policy) were blocked by the sandbox proxy; numbers and policy statements come from search-result snippets and secondary sites. Re-check before relying on exact quotas.
2. Whitespark's primary 2026 survey and the Ahrefs studies (1.74% / 5.7% top-10 within a year; average #1 age) were not read directly; only secondary summaries.
3. Vendor "AI visibility" statistics (ChatGPT 1.2% / Perplexity 7.4% / Gemini 11% location recommendation rates; citation source shares; 11% cross-platform overlap; 680M citations) are of unknown methodology; treat as directional.
4. Whether the FTC's per-violation civil penalty remains $51,744 in 2026 (it adjusts yearly) was not checked.
5. Anthropic model IDs and prices come from the bundled claude-api reference (cached 2026-09-25), not live docs. I did not read the Agent SDK pages on hooks/permissions/subagents in detail (only the overview), so exact option names (`allowedTools`, `canUseTool`, hook event names) should be confirmed against https://code.claude.com/docs/en/agent-sdk/ before coding.
6. Managed Agents details (beta) and the `build-eval` / `hillclimb` workflows were not read.
7. Common Crawl and Wikidata limits and Bing Webmaster/Bing Places-to-ChatGPT claims are from background knowledge, not freshly verified.
8. SerpApi and DataForSEO prices vary by source and endpoint (maps/local endpoints may cost more than organic); confirm on vendor pages. DataForSEO "AI Overview / LLM mentions" endpoints exist in my background knowledge but were not verified.
9. Regulated-profession advertising rules (dental, legal, medical) and GDPR/CPRA specifics were not researched jurisdiction by jurisdiction; the agent should escalate rather than decide.
10. Whether Google changed the review policy in April 2026 (one blog claims so) is unverified.
11. I did not research llms.txt or AI-specific "GEO" tactics beyond Google's statement that no special optimisation is required; effectiveness of such tactics for local businesses is unproven.
12. Reddit-citation prevalence and the rule that subreddit rules override ratios come from secondary guides; Reddit's current official policy text was not fetched.
