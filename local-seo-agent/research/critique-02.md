# Critique 02: AI-search / GEO research report (02-ai-search-geo.md)

Reviewer: Critic Agent 2 of 4. Date: 2026-10-03.
Method note: WebFetch worked only for the Anthropic support page. developers.openai.com, searchengineland.com, sparktoro.com, ahrefs.com and steadydemand.com were all EGRESS_BLOCKED for me too. Everything else below was checked via WebSearch result summaries, which is the same weakness as the original. "CONFIRMED" means at least two independent outlets or a primary source agree. It does not mean I read the primary page.

## 1. Spot-check table (17 claims)

| # | Claim | Verdict | Evidence / comment |
|---|---|---|---|
| 1 | Claude web search uses Brave | MOSTLY CONFIRMED, but "Brave confirmed" is too strong | Brave is on Anthropic's subprocessor list (Mar 2025), `BraveSearchParams` exists, and TechCrunch reported it ([Yahoo/TechCrunch](https://finance.yahoo.com/news/anthropic-appears-using-brave-power-170703042.html), [Xponent21](https://xponent21.com/insights/claude-web-search-brave-turbopuffer/)). Anthropic has never officially named a provider. The report's "87% overlap" is contradicted by a later re-test at 79.2% (Profound, Jun 2026, ~400 queries, per [shahabpapoon](https://www.shahabpapoon.com/blog/claude-web-search-runs-on-brave)). The report also misses that Anthropic's subprocessor list added a second search-related vendor, TurboPuffer, on 6 May 2026. |
| 2 | ChatGPT-User not bound by robots.txt | CONFIRMED | OpenAI docs changed 9 Dec 2025 to "Because these actions are initiated by a user, robots.txt rules may not apply" ([SEJ](https://www.searchenginejournal.com/openai-says-robots-txt-may-not-apply-to-chatgpts-fetch-bot/585864/), [PPC Land](https://ppc.land/openai-revises-chatgpt-crawler-documentation-with-significant-policy-changes/)). Primary page blocked. |
| 3a | Claude bot roles (ClaudeBot / Claude-User / Claude-SearchBot) | CONFIRMED (read directly) | [Anthropic support](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler). The page I fetched says nothing about IP ranges. A separate source says Anthropic now publishes one combined IPv4 list at claude.com/crawling/bots.json with no per-bot split. The report's "per bot" framing is slightly off. |
| 3b | OAI-SearchBot = search index, GPTBot = training; PerplexityBot = index, Perplexity-User = user fetch that "generally ignores" robots.txt | CONFIRMED via multiple secondary sources | Consistent across SEJ, PPC Land and Perplexity's help-centre excerpt. Primary pages blocked. |
| 4 | Cloudflare default AI-bot blocking, Jul 2025 | CONFIRMED, but scope needs care | 1 Jul 2025, applies to NEW domains, who are asked at onboarding. Existing sites got an opt-in toggle ([MIT Tech Review](https://www.technologyreview.com/2025/07/01/1119498/cloudflare-will-now-by-default-block-ai-bots-from-crawling-its-clients-websites/), [Nieman Lab](https://www.niemanlab.org/2025/07/cloudflare-will-block-ai-scraping-by-default-and-launches-new-pay-per-crawl-marketplace/)). The agent must not assume an older site is blocked, or that a new one is open. |
| 5 | ChatGPT-Yelp deal, 23 Jul 2026 | CONFIRMED | Date, 330M reviews, 8M+ listings, non-exclusive and branding all match ([Search Engine Land](https://searchengineland.com/openai-yelp-deal-483326), [Yahoo Finance](https://finance.yahoo.com/media-advertising/articles/exclusive-yelp-deal-pushes-local-130005436.html)). Request-a-Quote is "set to follow", not live. The report lists it as if live. |
| 6 | Ahrefs brand-mention correlations (0.66 AIO, ~0.71 AI Mode, backlinks 0.22, YouTube 0.74) | CONFIRMED numerically: 0.664, 0.709, 0.218, 0.737 | Reported only via secondary summaries ([Diggity tweet](https://x.com/mattdiggityseo/status/1940303316157936113), [TNW](https://thenextweb.com/news/ahrefs-youtube-mentions-ai-visibility-brand-search)). The 0.664 vs 0.218 result appears to date from Jul 2025, not "Aug and Dec". This is correlation across 75k mostly large brands and is not a local-business finding. |
| 7 | Princeton GEO "~40%" | CONFIRMED, with a bigger caveat than the report gives | The 40% is a relative gain in position-adjusted word count (19.3 to 27.2 for Quotation Addition) in a simulator where 5 sources are already supplied ([arXiv 2311.09735](https://arxiv.org/pdf/2311.09735)). The Perplexity test was small. It measures share of words in an answer, not "being recommended". It says nothing about local entity selection. |
| 8 | Ahrefs schema test shows no uplift | CONFIRMED, but the report drops key facts | 1,885 pages vs 4,000 controls: AIO -4.6% (statistically significant decline), AI Mode +2.4% and ChatGPT +2.2% (both noise). Every test page already had 100+ AIO citations, so it is not generalisable to brand-new local sites ([Ahrefs](https://ahrefs.com/blog/schema-ai-citations/), via summary). The report's "30-day window" and "cited pages 3x likelier to have schema" are UNVERIFIABLE. |
| 9 | Foursquare "70%" debunked | PARTLY CONFIRMED | The SteadyDemand figures match (2,880 prompts, 0.06%, 1 in 4,607, Yelp in 95.83% of runs). It is one local-SEO agency's test. It also found Yelp was in the grounding payload 95.83% of the time but actually cited only ~1.04% of the time. The report omits that, and it matters for how the agent defines "source". The Spanish 50-prompt origin is UNVERIFIABLE. "Matches the Yelp deal" is weak support, since the deal could be new rather than evidence about earlier behaviour. |
| 10 | llms.txt not supported | CONFIRMED for Google (Illyes, Mueller). | UNVERIFIABLE: "300k domains" and "97% got zero traffic" (aggregator blogs only). Coding agents (Cursor, Claude Code) do read llms.txt for docs sites, which is irrelevant to local businesses. |
| 11 | Bing Webmaster Tools AI Performance | CONFIRMED | Public preview 10 Feb 2026 ([Bing blog](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview), [SEJ](https://www.searchenginejournal.com/bing-webmaster-tools-adds-ai-citation-performance-data/566874/)). The 16 Jun 2026 additions were not independently checked. It counts citations only, with no clicks or rankings. |
| 12 | SparkToro reproducibility | CONFIRMED | 2,961 runs, 600 volunteers, 12 prompts, <1/100 same list, ~1/1,000 same order. It covered ChatGPT, Claude AND Google AI (the report names only two). Omitted and important: each prompt ran 60-100 times, and Fishkin concluded that "percent of visibility" is the metric that is real while "ranking position" is "baloney" ([SparkToro](https://sparktoro.com/blog/new-research-ais-are-highly-inconsistent-when-recommending-brands-or-products-marketers-should-take-care-when-tracking-ai-visibility/)). |
| 13 | Microsoft "AI Recommendation Poisoning" | CONFIRMED | Microsoft blog 10 Feb 2026: 50+ prompts, 31 companies, 14 industries, 60 days ([Microsoft](https://www.microsoft.com/en-us/security/blog/2026/02/10/ai-recommendation-poisoning/)). It is about "Summarize with AI" URL prompts that write to assistant memory. The report's "expect de-ranking" is inference, and it blends this with on-page hidden text, which is a different mechanism. |
| 14 | Ahrefs AIO top-10 overlap fell 76% to 38% | CONFIRMED, but misread | Ahrefs itself attributes much of the gap to improved parsing methodology versus Jul 2025 ([DesignRush](https://news.designrush.com/ai-overview-citations-drop-ahrefs)). The report presents it as a real trend ("falling"). |
| 15 | FTC fake-review penalty "~$51,744" | WRONG / STALE | The Jan 2025 adjustment set it at $53,088 per violation, with no further change for 2026 ([Federal Register](https://www.federalregister.gov/documents/2025/01/17/2025-01361/adjustments-to-civil-penalty-amounts)). |
| 16 | Peec "Labrador" result_source (21 May to 21 Jul 2026) | CONFIRMED as a third-party reverse-engineering | Peec/Rudzki, SEL and ALM Corp all agree. Per the summaries, Labrador is a family of vertical indexes including "local", and "Bright" separately scrapes Google Maps for local listings. The report skips this, and it is the most local-relevant detail. |
| 17 | Surfer API-vs-UI 24% brand / 4% source overlap | CONFIRMED as stated | Surfer sells an AI tracker and a UI-scraping product, so there is a conflict of interest, and the method is unpublished. Direction is plausible. |

Net: no claim is fabricated. Two are wrong or overreaching (#14 interpretation, #15 number). Several omit caveats that change the conclusion (#1, #8, #9, #12, #16).

## 2. Overreach, causation, staleness, confidence ratings

- **Section 1 "Brave confirmed" and "high confidence"**: change to "strongly evidenced, never vendor-confirmed". The Maps/Places claim is correctly low confidence. TurboPuffer is unaddressed.
- **Section 3 headline "brand mentions matter more than backlinks"**: observational correlation from Ahrefs' own Brand Radar data, across big brands. Large brands have both more mentions and more AI visibility, so reverse causation and confounding are likely. The playbook's "earn independent mentions" is reasonable. "More than backlinks" must not be quoted as an effect size.
- **Yext (86% brand-managed sources)**: vendor study, categories are retail, finance, health and food, and Yext sells listings management. The report notes this but still builds "first-party site = 44% of citations" into the playbook as a quantity.
- **Whitespark weights** (review 20%, GBP 32%): expert survey of local-pack ranking factors, not AI. Fine as labelled, but the agent must not use these percentages as AI-visibility weights.
- **"GBP basic criteria top-3 72.6% vs 58.5%"**: vendor data, no causal design. Drop or label hypothesis only.
- **Section 5 Perplexity "Yelp in 33%"**: BrightLocal 20 searches x 10 niches. Do not use as a weight.
- **Ratings**: Section 2 "high" is fair for bot roles. Section 3 "medium" should be "low-medium" for the Princeton and vendor studies. Section 6's sample-size rule is the researcher's own inference and is flagged as such, but see below, because it is too weak.

## 3. The proposed tracker: weaknesses and a defensible method

Problems with the design as written:
1. **"5-10 runs per prompt, Wilson interval"** is misleading. With a true rate of 10% and n=10, the Wilson 95% CI is roughly 2% to 40%, which is useless. SparkToro itself used 60-100 runs per prompt for stable visibility numbers.
2. **Runs are not independent across prompts.** Prompts differ enormously in difficulty (competitive "best dentist Austin" vs long-tail). A naive pooled Wilson interval understates uncertainty. You need a prompt-clustered interval.
3. **Cost estimate is tool fees only.** $10-25 per 1k search calls is the fee. Each call also ships 5-20k tokens of retrieved context. My own estimate (unverified) is $0.05-0.15 per call, so 1,600 calls a week is closer to $80-240 per client per week, not $15-25.
4. **No Google AI Overviews / AI Mode coverage.** The report offers Gemini API grounding, but Gemini API grounding is not AI Overviews. For local, Google AIO/AI Mode and Maps packs are the dominant surface. There is no compliant API, so the tool must say "not measured" and use manual samples or a licensed SERP provider flagged as grey-area.
5. **Entity matching**: fuzzy matching on a brand alias list creates false positives for generic names ("Smith Plumbing") and multi-location chains. Needs address, phone or URL confirmation, and a manual review sample.
6. **Competitor set is pre-chosen.** Share-of-voice is wrong if the competitor list is incomplete. Extract all named entities from every answer.
7. **Baseline drift**: models, indexes and result_source routing change weekly. A before/after comparison without a control confounds platform change with client change.

Concrete method to build:
- **Definition.** Call the headline metric **"Mention rate (API-sampled)"**: the share of valid runs, for a defined prompt set, platform, location and date window, in which the client is named and verified by address/phone/URL. Report **Citation rate** (client domain in cited URLs) and **Top-3 inclusion** separately. Never publish "rank" or a single composite "AI visibility score".
- **Prompts.** 20-30 non-branded local prompts, each with 3 paraphrases, plus a separate branded set (reputation/accuracy only, not included in the headline).
- **Runs.** Diagnostic cadence: 8 runs per prompt per platform per wave. Headline claims: at least 200 valid runs per platform per period, pooled across prompts. Run two baseline waves before changes.
- **Interval.** Per-platform Wilson interval for display, plus a prompt-clustered bootstrap (resample prompts, then runs) for any claim of change. Minimum detectable difference at 200 vs 200 runs, 80% power, p~0.3 is about 13 percentage points. Say so in the report.
- **Change attribution.** Track 3-5 competitors and a few non-optimised control prompts. Report change as a difference-in-differences against them. Flag any model-version change as a break in series.
- **Location.** City in prompt text AND `user_location` where supported. Test 2-3 neighbourhood anchors. Gemini Maps grounding takes lat/lng. Label as "approximate, API-supplied location".
- **API vs UI gap.** Run a monthly human spot-check of about 10 prompts in the real consumer apps, logged by hand, shown as a separate "calibration" panel. Footer on every report: "API samples; consumer apps differ (one study found about 24% brand overlap)". Do not scrape consumer UIs.
- **Budget.** Per-client cap, cost logged per run, abort on cap. Use fewer prompts rather than fewer runs.

## 4. Missing for local businesses

- **Non-US markets**: no review-site mix for UK (Trustpilot, Checkatrade, Which? Trusted Trader, Yell), EU (Gelbe Seiten, Pages Jaunes, Treatwell), AU, or other languages and country-specific engines. FTC-only compliance text. UK DMCC Act and EU/AU rules are explicitly unresearched.
- **Voice and Apple**: Apple Maps/Siri and Apple Business Connect are mentioned in one line. Siri's changing model backend, Alexa+, Google Assistant and in-car assistants are absent. I recall Apple and Google announced a Gemini-based Siri deal in early 2026 but did not verify it here.
- **Vertical review sources**: the list names some (Avvo, Healthgrades, Houzz, Angi, TripAdvisor, OpenTable) but gives no vertical-by-vertical mapping or evidence. The agent needs a vertical to source table: dentists (Healthgrades, Zocdoc, RateMDs), law (Avvo, Martindale, Justia), home services (Angi, HomeAdvisor, Thumbtack, BBB), restaurants (TripAdvisor, OpenTable, Eater/local press).
- **Service-area businesses (SABs)**: plumbers often hide their address on GBP. The NAP-diff check in Section 4 would flag intentional differences as errors. Needs a SAB mode.
- **Brand-name disambiguation**: generic or duplicate names, rebrands and multi-location. No guidance on alias handling or verifying that an AI answer is about the right entity.
- **Listicles / third-party "best of" lists**: the report says they help but gives no method for discovering which lists appear in AI answers (the tracker should extract them), nor guidance on paid-placement disclosure.
- **Reddit/community**: assessed with generic Profound data, then discounted using Yext. The tension is unresolved for local. Treat as a hypothesis for the tracker to test per market.
- **Google AIO tracking** (see section 3) and the possibility that ChatGPT local answers draw on scraped Google Maps (finding #16).

## 5. Harm risks and what needs human approval

Highest-risk items an automated agent could do:
- **Fabricating statistics, quotations and "named staff/certifications"** to follow the GEO "add statistics" tactic and the Section 3 "add verifiable facts where thin" check. An LLM will invent them. Every added fact must come from a client-supplied source and be shown for approval.
- **`aggregateRating` / review schema** on a business's own site. Google treats self-serving LocalBusiness/Organization review markup as ineligible and can issue a manual action. The report allows it "if genuine". Default should be: do not add.
- **Replying to reviews** in healthcare (HIPAA, confirming someone is a patient) and law (bar rules on advertising and confidentiality). Never auto-post replies. Draft only.
- **GBP edits** (name, categories, hours, services, address): wrong or keyword-stuffed names, or category changes, can trigger suspension. Human approval for every write.
- **Review solicitation**: Yelp and Google policy limits (the report notes Yelp). Incentives and gating are the main risks. Draft templates only.
- **Robots.txt / WAF / Cloudflare changes**: can break the site or expose it. Propose and diff, never apply.
- **Mass service x location pages**: doorway-page spam. Cap and require review.
- **Reddit/forum posting, Wikidata/Wikipedia edits, paid listicle placements, citation blasting**: no autonomous action. Ban.
- **UA-spoofing curl tests** in Section 2: Cloudflare and other WAFs verify bots by IP, so a spoofed `OAI-SearchBot` string from an arbitrary IP will often be challenged even when the real bot is allowed. Mark as indicative, and prefer server and Cloudflare logs for real bot hits.
- **Hidden-text/prompt-injection scanner** (Section 8) will have false positives (accessibility text, schema, `display:none` menus). Flag for review, never auto-remove.

Needs approval, drafting only: all GBP/Bing/Apple/Yelp edits, review replies and requests, any content publish, robots/WAF/DNS changes, outreach to press or list owners, schema changes. Autonomous and safe: read-only audits, fetches, tracker runs, GA4/Search Console reads, reporting.

## 6. Verdict per section

| Section | Verdict | Why |
|---|---|---|
| 1 Mechanics | FIX | Soften "Brave confirmed", add TurboPuffer, add the Labrador/Google-Maps local-vertical detail, cite the 79% re-test. |
| 2 Crawler access | KEEP, minor fix | Add Cloudflare new-vs-existing nuance, drop "per bot" IP framing, warn about UA-spoof testing. |
| 3 Evidence | FIX | Mark Ahrefs AIO 38% as partly a method change, add the schema test's AIO -4.6% and 100+ citation baseline, downgrade vendor studies, state that none are local. |
| 4 Entity | FIX | Add SAB mode, disambiguation, don't recommend aggregateRating, keep Wikidata low-confidence. |
| 5 Local | FIX | Add Yelp "grounded vs cited" distinction, non-US and vertical tables, Apple/voice, Google AIO surface. |
| 6 Measurement | FIX (substantial) | Replace the run-count and cost guidance with section 3's method. |
| 7 GA4 | KEEP | Low-risk, fine. Verify against client data. |
| 8 Snake oil | KEEP, fix | Update FTC figure ($53,088), add platform and professional-rules risks, add the approval list above. |

## 7. Corrections the builder MUST apply (priority order)

1. Replace the tracker statistics: headline metric named "Mention rate (API-sampled)", at least 200 valid runs per platform per period, prompt-clustered CIs, 2 baseline waves, competitor/control prompts, never "rank".
2. Fix the cost model to include tokens, set per-client budget caps, and re-price before shipping.
3. Add an explicit "Google AI Overviews / AI Mode: not measured by API" notice, and a manual-sample workflow.
4. Add a hard rule: the agent may not invent statistics, quotes, credentials, staff, awards or reviews. Every added fact needs a client-supplied source.
5. Implement an approval gate (draft-only) for every write to GBP, other profiles, reviews, site content, robots/WAF, schema, outreach.
6. Remove default `aggregateRating` markup advice. Add a HIPAA/bar-rules warning for health and legal review replies.
7. Correct the FTC penalty to $53,088. State that non-US rules were not researched and make the jurisdiction a required client input.
8. Soften "Brave confirmed" and add the 79.2% vs 87% conflict.
9. Re-label Ahrefs 38% as partly methodological, and the schema test as "no effect on already-cited large pages, and a significant -4.6% on AIO".
10. Add a service-area-business mode, brand disambiguation (address/phone/URL confirmation), and a vertical-to-source mapping table.
11. Make the UA-spoofing test "indicative only", with server/Cloudflare logs as the authority.
12. Have the tracker extract every named entity and every cited third-party list/listicle domain, not only a preset competitor list.
13. Add a freshness-date stamp and "re-verify before acting" flag to every volatile fact (bot docs, API versions, pricing, Yelp/ChatGPT behaviour), since this domain changes weekly.
