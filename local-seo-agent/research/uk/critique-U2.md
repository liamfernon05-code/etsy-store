# Critique of U2 (UK local-search report), Critic Agent 2, 2026-10-03

Method: WebFetch is blocked by the egress proxy (confirmed on lewissilkin.com: EGRESS_BLOCKED). All checks below are WebSearch result summaries, same limitation as the researcher. I mark a claim CONFIRMED where a search returned the specific figure or date from the cited page or a second independent source. I could not read any primary page in full.

## 1. Spot-check table (22 claims)

| # | Claim | Verdict | Evidence / note |
|---|---|---|---|
| 1 | Rated People CVL 16 Sep 2026; Checkatrade bought brand + site 17 Sep | CONFIRMED | bookabuilderuk.com liquidation page, insightdiy.co.uk "Checkatrade acquires selected assets", lewissilkin.com 24 Sep 2026. Nuance: only "selected assets" (brand, website). Trade memberships were NOT transferred. Buyer is Vetted Ltd (Checkatrade Group, Brookfield). |
| 2 | Scoot / Touch Local winding down Oct 2026 | CONFIRMED (own-site only) | scoot.co.uk/about-us and touchlocal.com/about-us both say "winding down in October 2026". No exact date, no press coverage. |
| 3 | Yell active; Thomson Local active | Yell CONFIRMED; Thomson Local UNVERIFIABLE as "active" | Yell: 1,435 staff at 31 May 2026 (Tracxn). Thomson Local: only Wikipedia (2013 administration, print ended 2016). The "195 staff Feb 2026" figure rests on Crunchbase and I could not reproduce it. |
| 4 | Deliveroo -> DoorDash 2 Oct 2025; Just Eat -> Prosus Oct 2025 | CONFIRMED | DoorDash 8-K and press: completed 2 Oct 2025 (180p/share). Prosus offer unconditional, settlement 6 Oct 2025 (90.13%). |
| 5 | Apple Business Connect -> "Apple Business" 14 Apr 2026 | CONFIRMED | Apple Support page "Apple Business Connect is now Apple Business" plus pinmeto, birdeye, intuneirl. Merged with Business Manager and Essentials. Existing claimed locations migrated. |
| 6 | FHRS (E/W/NI, 0-5) vs FHIS (Scotland, Pass / Improvement Required) | CONFIRMED | Multiple council pages (Glasgow, Falkirk, East Lothian). FHIS also has "Exempt" and "Awaiting Inspection". |
| 7 | LSA UK: nationwide trades (~28 categories), Greater London only for legal and estate agents | CONFIRMED | Google LSA UK help page appeared in results; blog.google legal/estate agents post; Sway Digital. London legal list matches. |
| 8 | "Google Verified" replaces Guaranteed / Screened from 20 Oct 2025 | CONFIRMED for UK | UK sources (BPCA, NPTA) repeat it, so it is not only a US change. Sub-claim "claims only for services booked before 7 Dec 2025": **WRONG or unsupported**. Every source I found says claims are only for jobs done before 20 Oct 2025, within 30 days. Drop the 7 Dec date. |
| 9 | GBP Q&A removed Dec 2025 | CONFIRMED with correction | API retired 3 Nov 2025. Public Q&A "began deprecation" 3 Dec 2025 and rolled out over 1-3 months. The report's "disappeared from 3 Dec" overstates it. |
| 10 | Ask Maps UK status unconfirmed | CONFIRMED | Announced 12 Mar 2026, US and India only. A GB News article says UK users miss out on Maps Gemini features. Harri Digital says "coming". The "150+ countries" claim is UNVERIFIABLE; I could not find it. |
| 11 | ccTLD redirect to google.com, Apr 2025 | CONFIRMED | Engadget, gHacks, TechRadar: rollout began 15 Apr 2025, gradual. |
| 12 | AI Mode UK 29 Jul 2025 | CONFIRMED | Press Gazette, Tech.eu, Hello Partner. UK was the third market after US and India. |
| 13 | Search Console Generative AI report: UK subset 3 Jun 2026, worldwide by 31 Aug 2026 | CONFIRMED, but now **stale** | Same dates in multiple trade sources. Newer item the report missed: from 7 Sep 2026 AI Mode and AI Overview impressions are combined, and AI Mode rows can be filtered by user prompt. That contradicts "no queries" and "impressions only". Do not hard-code that limitation. |
| 14 | ChatGPT cites Checkatrade 78/80, MyBuilder 70/80 (Murray Digital) | Figures CONFIRMED; weight LOW | 25 Aug 2026, 8 trades x 10 towns, 80 asks, 405 sources, 71.9% directories, 13.8% own site, 237 map-pack businesses vs 46 named. **Conflicts:** Murray Digital is an SEO/AI-visibility agency. It is a single-day run with one ask per cell, so no repeats and no variance. Prompt wording and ChatGPT login or location state are undisclosed. Checkatrade has an app inside ChatGPT, which confounds "citation" with "integration". Not a basis for a hard rule. |
| 15 | AI Mode own site 90% (Whito) | Figures CONFIRMED; weight LOW | 159 answers, 8 sectors, 20 towns; 90 / 81 / 53 / 45 / 32 / 20 / 0. Whito sells AI-recommendation tooling and reports. Categories overlap, so 98% "rests on own site or Google" is an OR. No repeat runs. Treat as directional. |
| 16 | Yext UK: 600 consumers, 36.7% (EMEA 40.8, global 42.7), 75% use more | CONFIRMED | yext.com blog and itbrief coverage. Yext sells listings, so it has an interest in "AI needs your listings". The "40% start local search on social" figure I could not reproduce. |
| 17 | DMCC Act in force 6 Apr 2025; first CMA fake-review cases Mar 2026 | CONFIRMED, **incomplete** | CMA opened five cases on 27 Mar 2026: **Autotrader, Feefo, Dignity, Just Eat, Pasta Evangelists**. Fines up to 10% of global turnover. The report lists Feefo and Just Eat as neutral platforms and never mentions that they are targets. |
| 18 | SRA transparency rules | CONFIRMED, scope incomplete | In force since 6 Dec 2018. Price info is required for conveyancing, probate, immigration (excl. asylum), employment tribunal (unfair/wrongful dismissal), some motoring offences, business debt recovery up to £100k, and licensing applications. Digital badge and complaints info are also required. The report omits three areas. England and Wales only. |
| 19 | OpenAI / Anthropic / Perplexity `user_location` shapes | CONFIRMED | OpenAI docs example is literally `{"type":"approximate","country":"GB","city":"London","region":"London","timezone":"Europe/London"}`. Anthropic needs at least one field, with `type:"approximate"`. Perplexity `web_search_options.user_location` has country, region, city, latitude, longitude; lat/long must come with country. |
| 20 | Gemini `retrieval_config.lat_lng` + `language_code` for Maps grounding | CONFIRMED | ai.google.dev maps-grounding page. "No location field on Search grounding" remains UNVERIFIABLE. |
| 21 | Community claim: OpenAI web tool assumes US user | UNVERIFIABLE | The thread exists (title matches) but I saw no content. Keep as a reason for the A/B probe, not as fact. Anthropic "unsupported country code returns 400" is also unverified. |
| 22 | MyBuilder "HomeAdvisor-owned since 2021" | **WRONG** | HomeAdvisor acquired MyBuilder 27 Mar 2017. Angi Homeservices increased its stake 1 Apr 2021. Today it is part of Angi Inc. |

Also confirmed: Which? Trusted Trader is live (Trusted Trader of the Month items through Apr 2026, join offer to 11 Nov 2026). Whitespark's UK list does include Scoot, ThomsonLocal, Factual, 118Information.co.uk and ThePhoneBook.BT.com (the snippet matches; their current liveness is still unknown). Gas Safe covers NI too (replaced CORGI in NI on 1 Apr 2010), so the report's nation switch should not exclude NI for Gas Safe.

## 2. Per-vertical directory tables: faults

1. **NHS.uk is England only.** Scotland uses NHS inform, Wales uses NHS 111 Wales / Health in Wales, NI uses HSC. The dentist table presents NHS.uk as the UK official listing. Fix: make the NHS source a per-nation lookup.
2. **Dentist:** CQC/HIW/Care Inspectorate/RQIA is right. Add Healthwatch and the practice's own NHS Terms of Service wording ("accepting new NHS patients" is the dominant UK query). The "WhatClinic, Dental Fear Central" claim is from a vendor guide and low-value. Dentist ads follow GDC and ASA rules; the report puts that in section 7 only.
3. **Solicitor:** Law Society "Find a Solicitor" and the SRA register are England and Wales only. Scotland has the Law Society of Scotland find-a-solicitor, NI the Law Society of NI. The report notes this only in passing. Add a Scottish row (conveyancing there goes through solicitors' property centres such as ESPC in Edinburgh). Add Which? "Legal services" and Lexcel. "Review Solicitors" is low confidence.
4. **Trades:** Add SNIPEF and SELECT (Scotland), Buy With Confidence (Trading Standards), Federation of Master Builders, NAPIT, Gas Safe, Trustpilot. Facebook community groups and Nextdoor matter, and the table only names Facebook. Checkatrade tier prices (£30 / £59) are unverified vendor numbers; do not hard-code them. MyBuilder ownership is wrong (see above).
5. **Restaurants:** "FHRS 3 or better needed for Just Eat" is unverified and sits oddly next to a CMA fake-review case against Just Eat. FHIS must be a separate branch (Pass / Improvement Required), not a 0-5 value. Add Hardens, SquareMeal and CAMRA WhatPub, which the report lists only as "from knowledge", and Google Maps' own "Dine-in / Takeaway" attributes.
6. **Beauty:** Treatwell cost is incomplete. Capterra summaries put Treatwell at about 35% commission on new clients and Fresha at about 20%, while the report says "£195/yr plus commission" and gives no rate for Fresha. Add Vagaro and Phorest as software rather than directories (low relevance).
7. **Missing everywhere:** a UK-wide `which_regulator` lookup by nation; Companies House appears only in the generic and solicitor tables, but sole traders and partnerships are not on it. Add "Trading Standards / Buy With Confidence" and local council "Trusted Trader" schemes (for example Fife, per Projects Scotland, Sep 2026).
8. **Directory registry:** Yelp UK, Hotfrog, Cylex and FreeIndex are "active" only per listicles. Mark them `status: unverified`, not `active`. 118Information and ThePhoneBook.BT.com are also unverified. Factual defunct is right.

## 3. API location block

Parameter names and shapes are right (see 19-20). Corrections and gaps:
- The OpenAI example region "London" is loose. `region` is free text, so test whether "Greater London" or "England" gives different answers.
- Anthropic web_search has several versions; the builder should read the current version from the SDK, not hard-code the docs URL.
- Perplexity region examples in docs use a state code ("CA"). There is no UK equivalent, so use the county or nation name and test.
- Gemini has no confirmed location field on plain search grounding. Maps grounding with `lat_lng` may not return UK results equally well; the report should say "test with a known UK query and verify the returned place IDs are British".
- Always log the returned citations' domains to detect `.com` US leakage. That is the actual test, not the parameter.

## 4. City coordinates (checked from my own knowledge, all within 0.05 degrees)

London 51.5074, -0.1278 OK. Manchester 53.4808, -2.2426 OK. Birmingham 52.4862, -1.8904 OK. Leeds 53.8008, -1.5491 OK. Sheffield 53.3811, -1.4701 OK. Bristol 51.4545, -2.5879 OK. Newcastle 54.9783, -1.6178 OK. Glasgow 55.8642, -4.2518 OK. Edinburgh 55.9533, -3.1883 OK. Cardiff 51.4816, -3.1791 OK. Belfast 54.5973, -5.9301 OK. No errors in all 11. Region strings: Glasgow and Edinburgh should be "Glasgow City" / "City of Edinburgh" with country "Scotland" as a second field, not "Scotland" alone. Add the missing cities: Liverpool 53.4084, -2.9916; Nottingham 52.9548, -1.1581; Leicester 52.6369, -1.1398; Southampton 50.9097, -1.4044; Aberdeen 57.1497, -2.0943; Swansea 51.6214, -3.9436; Derry/Londonderry 54.9966, -7.3086; Inverness 57.4778, -4.2247. Do not rely on a city-centre point for a service-area business: resolve postcodes through postcodes.io instead.

## 5. Query terms and prompts

Mostly natural. Fixes:
- "dentist accepting new NHS patients" is good, but add "NHS dentist taking new patients" (more common).
- "children's dentist" -> "NHS dentist for kids"/"child dentist". "cafe open now" is fine; "nail salon" -> "nail bar"; "pubs with food" -> "pub lunch" / "gastropub"; "cheap [service]" -> "affordable [service]" or "[service] prices"; "plumber near LS6" is rarer than "plumber LS6".
- Add the UK terms the report lists but omits from tables: "tradesperson", "heating engineer", "chippy", "pub lunch", "Sunday roast", "out of hours dentist", "NHS 111" for urgent care.
- Prompt 2 "how much should I expect to pay in pounds" reads stilted; use "roughly how much will it cost?" and let the £ come back.
- Prompt 1 uses `{county}`. In Scotland, Wales and NI use `{council_area}` or `{nation}`.
- Avoid "attorney", "realtor", "contractor" (generic) and "plumber near me" without a town as the sole template.

## 6. What the report misses

- **Welsh language:** `hl=cy`, bilingual GBP descriptions, Welsh place names (Caerdydd, Abertawe) in queries; Google Maps shows both. Add a `cy` probe variant for Wales.
- **Northern Ireland:** BT postcodes, `028` numbers, +44 28; NI has its own councils and bank holidays (the report has these). Cross-border businesses may use an Irish Eircode and +353, so `addressCountry` GB vs IE matters.
- **Crown dependencies:** Jersey (JE), Guernsey (GY), Isle of Man (IM) are not in the UK, have their own ISO codes and +44 1534 / 1481 / 1624 numbers, and the regex `GB` check would reject them. Scope them out, or add a `market` for them.
- **Phones:** 03 numbers are legal as call-tracking numbers; Google wants the primary GBP number to be a local number, with tracking numbers as additional. 0800/0808 are free; 0845/0870 were withdrawn into 03. Ofcom drama ranges also cover 0113 496, 0121 496, 0131 496, 029 2018 0xxx.
- **Postcode:** the proposed regex rejects `GIR 0AA`; fine for businesses, but note BFPO.
- **Schema/NAP:** `LocalBusiness` should carry `vatID` and `identifier` (Companies House number) where appropriate; registered office vs trading address differ; "Ltd/Limited/LLP" suffix variants break exact NAP match.
- **Regulation:** DMCC also bans drip pricing and "urgency" claims, which affects trades "from £x" pages. The ICO fee note is fine but "PECR" for review emails is from knowledge only.
- **Search Console and Bing:** Bing Webmaster Tools AI performance reporting is not covered.

## 7. Verdicts per section

| Section | Verdict |
|---|---|
| 1.1 Platform status | FIX: Thomson Local activity, MyBuilder ownership, Treatwell/Fresha rates, mark unverified directories, add Just Eat/Feefo CMA flag |
| 1.2 Per-vertical tables | FIX: NHS.uk is England only; add Scotland/NI/Wales regulators and SNIPEF/SELECT, Buy With Confidence |
| 2 NAP formats | KEEP, FIX: add Crown dependencies, NI, call-tracking rule |
| 3 GBP / LSA | FIX: drop "7 Dec 2025"; soften Q&A "disappeared 3 Dec" |
| 3.4 Ask Maps | KEEP as "monitor, unconfirmed" |
| 4 AI assistant behaviour | FIX: update Search Console (prompt filter from 7 Sep 2026); downgrade the two studies to "directional" and disclose conflicts |
| 5 Terms / prompts | FIX: a dozen wording changes above; add Welsh variant |
| 5.3 API location | KEEP (confirmed); add leakage check |
| 5.3 Coordinates | KEEP (all 11 correct); add 8 cities |
| 6 Authority building | KEEP |
| 7 US-vs-UK list | KEEP, add Crown dependencies, Welsh, DMCC drip-pricing |

## 8. MUST-apply corrections (priority order)

1. Remove "claims only for services booked before 7 Dec 2025". Use "jobs done before 20 Oct 2025, claimed within 30 days".
2. Make NHS.uk a per-nation lookup: England NHS.uk, Scotland NHS inform, Wales NHS 111 Wales, NI HSC. Same for law (SRA/Law Society E&W; Law Society of Scotland; Law Society NI) and care regulators.
3. Treat the Murray Digital and Whito studies as vendor-published, single-run, directional. Store `source_conflict: true`. The Checkatrade-in-ChatGPT app is a confounder. Never present 78/80 or 90% as a rule.
4. Add `cma_investigated_2026_03: [Autotrader, Feefo, Dignity, Just Eat, Pasta Evangelists]` to the review-platform registry and warn on incentivised-review nudges.
5. Fix Search Console: UK subset 3 Jun 2026, worldwide 31 Aug 2026, combined AI Mode + AI Overview impressions and prompt filter from 7 Sep 2026. Do not hard-code "impressions only, no queries".
6. Directory statuses: Scoot / Touch Local `closing_2026_10` (date unknown); Rated People `brand_only_checkatrade_owned` (memberships not transferred); Factual `defunct`; Thomson Local, Cylex, FreeIndex, Yelp UK, Hotfrog, 118Information, ThePhoneBook `unverified`. MyBuilder owner is Angi Inc. (HomeAdvisor acquired it in 2017).
7. FHIS branch for Scotland: values `Pass`, `Improvement Required`, `Exempt`, `Awaiting Inspection`; never coerce to 0-5.
8. SRA scope: add motoring offences, business debt recovery up to £100k and licensing applications; flag England and Wales only; require digital badge.
9. Add the 8 cities above; use `postcodes.io` to resolve a client postcode; use council-area region strings for Scotland.
10. Always log citation domains returned and flag `.com` US results as a localisation failure; keep the with/without `user_location` A/B.
11. Add Welsh (`cy`) and NI (BT, 028, IE cross-border) handling, plus a Crown-dependency out-of-scope guard.
12. Reword the prompts per section 5, and make county optional (use `{council_area}` outside England).
13. Do not hard-code Checkatrade tier prices (£30 / £59) or Treatwell "£195/yr". Mark as `last_seen`, with a date.
