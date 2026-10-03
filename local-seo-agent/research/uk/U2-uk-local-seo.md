# U2: UK Local-Search Market Specifics (as of 2026-10-03)

Method note: WebFetch was blocked by the sandbox egress proxy for every primary site tried (support.google.com, blog.google, whitespark.ca, searchenginejournal, ppc.land and others). All findings below come from WebSearch result summaries, which are secondary. Primary-source URLs are listed where the search surfaced them, but I could not open them. Confidence is therefore capped at "med" for anything that rests on a single vendor blog. "From knowledge" means it comes from my own background knowledge and was not re-verified today.

Headline findings for the agent designer:
1. Rated People went into liquidation on 16 Sep 2026 and Checkatrade Group bought the brand and website. Scoot and Touch Local are reported to wind down in October 2026. Check any hard-coded directory list against this.
2. Google Local Services Ads in the UK are nationwide for home-service trades but Greater London only for legal and estate agents. The "Google Guaranteed/Screened" badges were reportedly replaced by "Google Verified" from 20 Oct 2025.
3. Two UK AI-citation studies disagree. For trades, ChatGPT leans heavily on Checkatrade and MyBuilder. Google AI Mode leans on the business's own site and Google reviews. The probe harness must therefore be per-assistant, not one blended "AI" score.
4. Google Q&A was removed in Dec 2025 and replaced by Gemini-powered "Ask Maps". Ask Maps UK availability is not confirmed.
5. DMCC Act (in force 6 Apr 2025) makes fake and incentivised-undisclosed reviews a banned practice, with CMA fines of up to 10% of turnover. This changes what a review-generation module may recommend.

---

## 1. Directories, review platforms and registers

### 1.1 Status check of the platforms you listed

| Platform | Operating in 2026? | Role | Confidence / source |
|---|---|---|---|
| Yell (yell.com) | Yes. Active, about 1,400 staff (May 2026). Print Yellow Pages ended Jan 2019. | Consumer directory, reviews, sells ads. Core UK citation. | med-high. https://pitchbook.com/profiles/company/11055-79 ; https://www.biia.com/yellow-pages-end-of-the-print-era-in-the-uk/ |
| Thomson Local | Yes. Active (administration in 2013, then bought by Corporate Media Partners). About 195 staff (Feb 2026). | Legacy directory and citation. | med. https://en.wikipedia.org/wiki/Thomson_Local ; https://www.crunchbase.com/organization/thomsonlocal-com |
| Cylex UK | Listed as active in 2026 citation round-ups. | Free citation with dofollow. Low traffic. | low-med. https://whitehat-seo.co.uk/blog/uk-business-directories-citation-sites |
| FreeIndex | Active per the same round-ups. | Free directory and reviews. Low authority. | low-med. same |
| Scoot and Touch Local | **Winding down in October 2026**; site and listings to go. | Network directory, formerly a Whitespark top-UK citation. | med (the scoot.co.uk snippet says so). https://www.scoot.co.uk/about-us |
| 192.com | Active. Business data is managed via Central Index. | People and business search. | low-med. https://en.wikipedia.org/wiki/192.com |
| Checkatrade | Yes, the market leader. Over 50,000 vetted firms. Has an app inside ChatGPT (booking and fixed price). Group acquired Rated People assets 17 Sep 2026. | Trades lead-gen and vetting. The most-cited source for UK trades in ChatGPT. | high. https://www.installeronline.co.uk/news/checkatrade-app-in-chatgpt-brings-consumers-a-new-way-to-find-vetted-tradespeople/ ; https://www.lewissilkin.com/news/2026/09/24/we-have-advised-checkatrade-group-on-its-acquisition-of-selected-assets-from-rated-people |
| Rated People | **Brand and site still live, but the company entered CVL on 16 Sep 2026**. Trade memberships were closed. Homeowner leads now go to Checkatrade members. | Was pay-per-lead. Now a Checkatrade-owned front end. | med-high (multiple trade-press sources). https://www.ratedpeople.com/blog/rated-people-joins-checkatrade-group ; https://www.bookabuilderuk.com/blog/rated-people-liquidation-what-tradespeople-need-to-know |
| MyBuilder | Active (HomeAdvisor-owned since 2021). Cited 70 of 80 times in one ChatGPT trades study. | Pay-per-lead with verified reviews. | med. https://murraydigital.co.uk/blog/ai-visibility-what-chatgpt-recommends-local-trades/ |
| Bark | Active. Credit-based leads, no vetting. | Lead-gen. Weak trust signal. | med. https://www.swiftlead.co.uk/blog/checkatrade-vs-mybuilder-vs-bark |
| Which? Trusted Trader | A Which? join page shows live offers to Nov 2026, so it is operating. | Vetted-trader scheme (Which? brand). | low-med. https://for-traders.which.co.uk/join |
| TrustATrader | Active. Fixed-fee profile. | Trade directory. | med. https://uk.trustpilot.com/review/www.trustatrader.com |
| TrustMark | Active. Government-endorsed scheme. Joined through scheme providers (NICEIC, Gas Safe, NAPIT, FMB). | Regulator-adjacent trust mark. | high. https://niceic.com/for-the-trades-1/professional-standards/schemes/trustmark/ |
| Trustpilot, Feefo, Reviews.io | All active. | Review platforms feeding Google Seller Ratings and rich snippets (product and company reviews). | high. https://uk.trustpilot.com/review/feefo.com |
| TripAdvisor / TheFork | Active (TheFork is TripAdvisor-owned). | Hospitality reviews and reservations. | med. https://foodhubforbusiness.com/blogs/best-review-sites-for-restaurants-uk/ |
| OpenTable | Active in the UK. | Reservations and verified reviews. | med. same |
| Just Eat | Taken over by Prosus; settled Oct 2025. Brand continues. | Delivery marketplace. Requires an FHRS rating of 3 or better for new restaurants. | high. https://fooddigital.com/news/deliveroo-just-eat-acquisitions-ecommerce |
| Deliveroo | Acquired by DoorDash; completed 2 Oct 2025. | Delivery marketplace. | high. https://deliveroo.co.uk/more/news-articles/doordash-deliveroo-acquisition |
| Uber Eats | Active. | Delivery marketplace. | med |
| Good Food Guide | Digital and app-based since 2022. No longer published by Waitrose. | Editorial accolades. | med. https://www.thegoodfoodguide.co.uk/awards |
| Treatwell, Fresha, Booksy | All active in the UK. Treatwell is about £195/yr plus commission. Booksy is about £40 + VAT/month. Fresha charges commission on new-client bookings. | Booking marketplaces for beauty. | med. https://pabau.com/blog/treatwell-alternatives/ |
| NHS.uk service pages | Active. Public feedback on NHS dental and GP pages. | Official listing, review source and trust signal. | med. https://birdeye.com/blog/dental-review-management-uk/ |
| Doctify | Active. Private, about 186 staff. Closed review system (appointment-confirmed only). | Private-healthcare review platform. | med. https://uk.trustpilot.com/review/www.doctify.com |
| Dentistry.co.uk | Not verified. It is a dental trade publication (from knowledge), not a patient directory. Do not use it as a citation. | n/a | low |
| Law Society Find a Solicitor | Active. Data drawn largely from the SRA register, editable by the firm. | Official directory. | high. https://solicitors.lawsociety.org.uk/about |
| SRA register | Active. Regulator register for England and Wales. | Regulator register. | high. https://www.sra.org.uk/solicitors/standards-regulations/transparency-rules/ |
| Legal 500, Chambers & Partners | Active. Chambers guides are free to read online. | Editorial rankings. | med. https://www.venables.co.uk/listings/legal-directories/ |
| Companies House | Active. Free public register. | Entity and registered-office verification. | high (from knowledge) |
| Gas Safe Register | Active. About 130,000 engineers. Legally required for gas work. | Regulator register. | med. https://sleeplesstradesman.com/guides/approved-trader-schemes-uk |
| NICEIC | Active. Voluntary for electricians, and a TrustMark scheme provider. | Trade body register. | med. same |
| FHRS (food hygiene ratings) | Active in England, Wales and NI (0 to 5). **Scotland uses FHIS (Pass / Improvement Required), not 0 to 5.** | Regulator rating, shown on delivery apps. | med-high. https://www.foodsafetynews.com/2021/01/deliveroo-and-uber-eats-listing-outlets-with-hygiene-ratings-of-2-and-lower/ ; Scotland detail from knowledge |
| Bing Places | Active. Feeds Bing, Copilot and ChatGPT's Bing-based search. | Search and AI data source. | med. https://www.localfalcon.com/blog/chatgpt-local-search-data-sources-where-does-business-info-come-from |
| Apple Business (was Business Connect) | Merged with Manager and Essentials into a single Apple Business platform on 14 Apr 2026. Claimed locations migrated automatically. | Apple Maps and Siri data. | med. https://www.trymaas.com/blog/apple-business-connect-apple-maps-marketers-2026/ |
| Facebook | Active. In UK consumer data, 40% start local search on social, the #2 channel behind Google. | Social discovery and citation. | med. https://www.yext.com/blog/how-uk-consumers-navigate-local-search-in-age-of-ai |
| Yelp UK | Company is registered and active, but weak in the UK. No closure found. | Minor citation. Foursquare and Yelp feed some AI and map data. | low-med. https://find-and-update.company-information.service.gov.uk/company/06762006 |
| Foursquare | Data partner for ChatGPT, Apple Maps and others. One source claims over 70% of ChatGPT local results; I could not verify that figure. | Aggregator. | low-med |

Whitespark's UK top citation list (via search summary; I could not open the page): Google Business Profile, Bing Places, Apple Maps, 118Information, ThePhoneBook.BT.com, Scoot, Thomson Local, Factual, Central Index, Yell, Yelp.co.uk, Facebook, Infobel, FreeIndex, 192.com, TouchLocal, Foursquare, Hotfrog UK, Cylex UK, Tipped. Treat as dated: Scoot and Touch Local are going, Factual is gone (merged into Foursquare in 2020), and I could not confirm 118Information or ThePhoneBook.BT.com are still live. Source: https://whitespark.ca/top-local-citation-sources-by-country/united-kingdom/ (not fetched; confidence low-med). The same results note the UK has no single dominant data aggregator, so direct submission to Google, Bing and Apple matters more.

### 1.2 Per-vertical lists

Role codes: F = feeds or corroborates map and search data; AI = cited by AI assistants in UK studies; T = consumer trust signal; R = regulator or official register; L = lead-gen marketplace.

**Dentist**

| Source | Role | Notes |
|---|---|---|
| Google Business Profile | F, AI, T | Primary. Reviews are the main trust input. |
| NHS.uk (Find a dentist) | F, T, R-ish | Official. The NHS entry needs to match the practice's NAP. NHS practices cannot control it directly (from knowledge). |
| GDC register (olr.gdc-uk.org) | R | UK-wide. Every clinician must be registered. Link to the GDC numbers on team pages. |
| CQC (England), HIW (Wales), Care Inspectorate (Scotland), RQIA (NI) | R | Practice-level regulator. Show the registration. |
| Doctify | T, AI | Private and cosmetic practices. |
| WhatClinic, Dental Fear Central, BDA find-a-dentist | F, T | Named in practitioner guides and by the GDC as a finder. |
| Trustpilot, Facebook | T | Secondary reviews. |
| Yell, Thomson Local, Cylex, FreeIndex | F | Generic citations. |

Sources: https://www.gdc-uk.org/about-us/what-we-do/the-registers ; https://lineup.agency/dental-seo-uk/ (confidence med).

**Solicitor / law firm**

| Source | Role | Notes |
|---|---|---|
| Google Business Profile (category "Solicitor") | F, AI, T | Primary. |
| SRA register | R | England and Wales only. Scotland has the Law Society of Scotland, NI the Law Society of NI (from knowledge). |
| Law Society Find a Solicitor | F, R-ish, T | Mostly SRA-sourced and editable by the firm. |
| Legal 500, Chambers & Partners | T, AI | Editorial authority. |
| Law Society accreditation schemes (Lexcel, CQS conveyancing, Wills & Inheritance) | T | From knowledge. |
| Trustpilot, Review Solicitors | T | Review Solicitors from knowledge, low. |
| Companies House | R | For LLPs and Ltd firms. |
| Yell and generic directories | F | Minor. |

Compliance: the SRA requires the firm's SRA number, the SRA digital badge and complaints information on the website. The price and service transparency rules apply to listed areas such as conveyancing, probate, employment tribunals and immigration. The agent should flag "contact us for a quote" pages and fee information buried several clicks deep as non-compliant. Sources: https://www.sra.org.uk/solicitors/standards-regulations/transparency-rules/ ; https://www.sra.org.uk/solicitors/resources/fees/transparency-price-service/ (confidence high).

**Trades (plumber, heating engineer, electrician)**

| Source | Role | Notes |
|---|---|---|
| Google Business Profile | F, AI, T | Primary. Also the route into Google Local Services Ads. |
| Checkatrade | L, AI, T | Dominant AI citation for UK trades. Tiers: free, Approved (about £30/month + VAT), Growth (about £59/month). Its ChatGPT app can book jobs. |
| MyBuilder | L, AI, T | Cited in 70 of 80 ChatGPT answers in one study. |
| Rated People | L | Now a Checkatrade-owned front end. Do not recommend a fresh membership. |
| TrustATrader, Which? Trusted Trader, Bark | L, T | Second tier. |
| Gas Safe Register | R | Mandatory for gas work. Show the Gas Safe ID. |
| NICEIC / NAPIT (SELECT in Scotland, from knowledge) | R, T | Voluntary for electricians. |
| OFTEC (oil), MCS (solar and heat pumps), WaterSafe | R, T | From knowledge, not verified today. |
| TrustMark | T | Government-endorsed. Joined through a scheme provider. |
| Facebook community groups, Reddit | AI | See section 4. |

Sources: https://sleeplesstradesman.com/guides/approved-trader-schemes-uk ; https://murraydigital.co.uk/blog/ai-visibility-what-chatgpt-recommends-local-trades/ (confidence med).

**Restaurant / cafe / takeaway**

| Source | Role | Notes |
|---|---|---|
| Google Business Profile | F, AI, T | Primary. |
| TripAdvisor and TheFork | F, AI, T | Cited for UK hospitality. |
| OpenTable | F, T | Reservations. |
| Just Eat, Deliveroo, Uber Eats | F, L | Menus, ratings and hygiene ratings are shown. |
| FHRS and FHIS (ratings.food.gov.uk) | R, T | Strongest UK-only trust signal. A rating of 3 or better is needed for Just Eat. |
| Good Food Guide, Michelin Guide, Hardens, Time Out, SquareMeal | T, AI | Editorial "best of". Good Food Guide verified; the rest from knowledge. |
| CAMRA WhatPub (pubs) | F | From knowledge. |
| Facebook and Instagram | T | Heavy UK usage. |
| Bing Places, Apple Business, Yell | F | |

Sources: https://foodhubforbusiness.com/blogs/best-review-sites-for-restaurants-uk/ (confidence med).

**Hair / beauty salon**

| Source | Role | Notes |
|---|---|---|
| Google Business Profile | F, AI, T | Primary. |
| Treatwell | L, T | Largest UK beauty marketplace. |
| Fresha | L, T | London-based. |
| Booksy | L, T | Strong with barbers. |
| Instagram and Facebook | T | Main portfolio and social proof. |
| Local authority special-treatment licensing (piercing, tattooing, some beauty), NHBF / Habia | R, T | From knowledge. Varies by council. |
| Yell, Bing Places, Apple Business | F | |

"Reserve with Google" for beauty in the UK: one vendor blog says it is US-only with the UK "on the 2026 roadmap". I could not verify this (confidence low). Source: https://www.zenoti.com/thecheckin/salon-booking-system-uk

**Generic**

Google Business Profile, Bing Places, Apple Business, Facebook, Yell, Trustpilot, Companies House (entity and registered office), the local Chamber of Commerce, local council business directory, relevant trade body, Cylex, FreeIndex, Foursquare, Thomson Local. Add 192.com only if Central Index data is needed.

### Agent-actionable (section 1)
- Hard-code a directory registry with a `status` and `as_of` date. Mark Scoot and Touch Local as `closing_2026_10`. Mark Rated People as `brand_only_checkatrade_owned`. Mark Factual as `defunct`.
- Per-vertical citation checklists should use the tables above. Treat NHS.uk, SRA, GDC, Gas Safe, NICEIC, TrustMark and FHRS or FHIS as "verify, don't create" register checks.
- The consumer-facing platform list should rank by AI citation, not by the old citation volume lists.
- Add a UK nations switch: SRA is England and Wales only, FHIS is Scotland only, and CQC is England only.

---

## 2. UK NAP and format conventions

Findings (confidence med unless noted):
- **Phone.** A UK number is +44, an area or network code and a subscriber number. The domestic format has a leading 0 that is dropped after +44. Examples are 020 7946 0958 and +44 20 7946 0958. Mobiles are 07xxx xxxxxx (11 digits). Geographic landlines start 01 or 02. Non-geographic numbers start 03 (charged like geographic calls), 08 and 09. 080 numbers are free to the caller. Source: https://en.wikipedia.org/wiki/Telephone_numbers_in_the_United_Kingdom ; https://callhippo.com/blog/general/uk-phone-number-format
- **Number lengths and spacing vary** (01xxx xxxxxx, 011x xxx xxxx, 01x1 xxx xxxx, 02x xxxx xxxx). Do not validate with a US-style fixed-width regex. Normalise to E.164 internally and display national format. Ofcom reserves drama numbers (020 7946 0xxx, 0161 496 0xxx, 07700 900xxx) for test data (from knowledge, high).
- **Postcode.** Outward and inward code separated by a space, for example LS1 4AP, always upper case. 5 to 7 characters. The postcode is the key element in a UK address. Source: https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom
- **County.** Royal Mail's PAF does not require it. A complete address has a premise, a thoroughfare, a locality or post town, and a postcode. County is optional and usually omitted. Source: https://en.wikipedia.org/wiki/Postcode_Address_File ; https://ideal-postcodes.co.uk/guides/good-addressing-guidelines
- **Town versus county versus region.** England has regions, ceremonial counties, historic counties and defunct postal counties, so users and businesses use them inconsistently. Scotland, Wales and NI are nations. A NAP matcher should treat county as non-significant, match on postcode plus the first address line, and not penalise a missing or different county. (Matching rule is my recommendation.)
- **schema.org.** `addressCountry` should be ISO alpha-2 "GB" (not "UK"). `addressLocality` is the town or city. `addressRegion` is a county or nation. `postalCode` is the full postcode. Source: https://schema.org/PostalAddress (confidence high). Use `priceRange` as free text such as "££" or "£10-£30" (from knowledge; Google treats it as free text). Use `priceCurrency: "GBP"` on Offers. Use `areaServed` with a `City`, `AdministrativeArea` or `GeoCircle`, and name postcode districts in the page copy as well.
- **Opening hours and bank holidays.** Bank holidays differ by nation. The GOV.UK feed at https://www.gov.uk/bank-holidays.json has divisions `england-and-wales`, `scotland` and `northern-ireland`. Scotland has a 2 January holiday and St Andrew's Day. NI has 17 March and 12 July. Publish `openingHoursSpecification` with `validFrom` and `validThrough` for holiday closures, and set the matching special hours in the GBP. Source: https://github.com/alphagov/calendars (confidence high for the feed; holiday specifics from knowledge). Use the Europe/London timezone and 24-hour display.

### Agent-actionable (section 2)
- Normalise phones with a library (libphonenumber, region GB) and store both E.164 and national. Accept 03 and 0800. Warn when a business uses only a 07 mobile as its public number (an unverified recommendation: geographic numbers read as more local).
- Postcode regex: `^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$`. Normalise to upper case with one space.
- When generating JSON-LD, always set `addressCountry: "GB"`, `priceRange` in £, and bank-holiday special hours drawn from the right division.
- Make the NAP consistency check county-insensitive and tolerate "Road/Rd", "Street/St" and unit or flat prefixes.

---

## 3. Google Business Profile UK specifics

### 3.1 Service-area and address rules
- The global rules apply in the UK. A service-area business hides its address and lists the areas it serves, up to 20 named areas. Hiding the address does not make an ineligible business eligible. PO boxes and mail drops are disallowed. Source: https://support.google.com/business/answer/3038177?hl=en-GB (not fetched) and https://www.ollyolly.com/tutorials/how-does-service-area-work-in-google-business-profile/ (confidence med).
- UK-specific risks: many sole traders work from home and must hide their address. Companies House registered-office or accountant addresses are not valid GBP addresses unless the business is staffed there (from knowledge, med).

### 3.2 Category terminology
Google localises category names. The UK uses "Chemist" for the US "Drugstore", "Petrol station" for "Gas station", "Cashpoint" for "ATM" and "Estate agent" for "Real estate agent". "Solicitor" is the UK primary for law firms ("Law firm" also exists). Gas engineers commonly use "Heating contractor", "Gas installation service" and "Boiler repair service" (one UK source). I could not confirm exact category strings for takeaways, so do not hard-code them. Sources: https://nettrackers.co.uk/blog/google-business-profile-categories-uk ; https://www.studiosable.com/post/how-to-optimise-your-google-business-profile-for-uk-trades (confidence med).

### 3.3 Local Services Ads (LSA) in the UK
- Nationwide for home-service trades such as plumbers, electricians, roofers, cleaners and landscapers (about 28 categories). Greater London only for legal services (contract, corporate, criminal, employment, family, immigration, insolvency, IP, litigation, personal injury, probate, property, tax and others) and estate agents. Sources: https://swaydigital.co.uk/insights/google-local-services-ads-uk ; https://blog.google/products/ads-commerce/a-new-way-for-legal-firms-and-estate-agents-to-reach-more-customers/ (confidence med).
- **Badges.** Effective 20 Oct 2025 Google reportedly replaced Google Guaranteed, Google Screened and License Verified with one "Google Verified" badge, and ended the money-back guarantee (claims only for services booked before 7 Dec 2025). Most sources are US-focused, though UK agency guides repeat the change. Confidence med. Sources: https://blog.google/products/ads-commerce/google-verified-august-2025/ ; https://almcorp.com/news/google-local-services-ads-requirements-july-2026/
- **Performance Max migration.** Google is folding LSAs into Performance Max with pay-per-lead goals. Phase 1 started in Aug 2026 for selected US categories. Non-US accounts including the UK are reported for Phase 3 (2027). Confidence low-med (agency reports, one UK source). Source: https://ppcgeeks.co.uk/ppc/local-services-ads-google-ads-uk-ppc-teams/
- LSA specific vetting depends on trade licences, insurance and background checks. A verified GBP is a hard requirement.

### 3.4 Q&A and "Ask Maps"
- GBP Q&A: the API was retired on 3 Nov 2025 and public Q&A threads disappeared from 3 Dec 2025, replaced by a Gemini-powered "Ask" experience. Owners no longer write the answers. Confidence med-high. Source: https://www.northcountydigital.com/marketing-blog/google-business-profile-qa-discontinued ; https://www.respectexperts.co.uk/google-business-profile-questions-and-answers/
- Ask Maps was announced on 12 Mar 2026 (US and India first), with a 6 Aug 2026 update adding more features and one report of expansion to 150+ countries in English. **UK availability is not confirmed.** One UK agency says it is "coming". Confidence low. Sources: https://9to5google.com/2026/08/06/google-ask-maps-global/ ; https://www.harridigital.co.uk/blog/google-ask-maps-is-coming-to-the-uk-heres-how-your-business-can-get-ready
- Ask Maps was reported missing for healthcare and some regulated categories (relevant to dentists). Confidence low-med.

### 3.5 google.co.uk versus google.com
- Google announced on 15 Apr 2025 that country-code domains redirect to google.com. Localisation comes from location signals, `gl` and `hl`, not the domain. Local results have worked this way since 2017. Source: https://9to5google.com/2025/04/15/google-com-search/ (confidence high).
- For SERP tooling, use `gl` for the UK (sources say "gb" is the ISO value, but some SERP APIs historically take "uk"; test against the provider), `hl=en-GB`, and a precise UULE, coordinates or API location. Do not rely on a google.co.uk host. Source: https://cloro.dev/blog/google-search-parameters/ (confidence low-med).
- Review rules: the DMCC Act now bans fake reviews and incentivised reviews that hide the incentive, in force 6 Apr 2025. Businesses must take reasonable steps to prevent or remove them. The CMA opened its first cases in Mar 2026. Source: https://cms.law/en/gbr/legal-updates/no-more-faux-five-stars-the-dmcc-act-bans-fake-reviews ; https://www.eversheds-sutherland.com/en/united-kingdom/insights/fake-reviews-now-expressly-banned-under-new-uk-consumer-law (confidence high).

### Agent-actionable (section 3)
- Pull categories from the Business Profile API `categories.list` with `regionCode=GB` and `languageCode=en-GB` and validate against that list rather than a hard-coded US list.
- LSA eligibility check: trades in all UK, legal and estate agents only if the business is in Greater London. Do not say "Google Guaranteed" or "Google Screened" in client copy. Use "Google Verified" and flag it as med confidence.
- Do not recommend Q&A seeding. Recommend that the website and GBP description cover the likely questions instead.
- Review module: forbid gating, undisclosed incentives and staff-written reviews. Cite the DMCC Act.
- Treat Ask Maps in the UK as "monitor, unconfirmed".

---

## 4. How AI assistants answer UK local queries

### 4.1 Adoption and rollout
- **AI Mode UK:** launched on 29 Jul 2025 as a tab in mobile and desktop Search and in the Google app. Confidence high. Sources: https://9to5google.com/2025/07/28/google-ai-mode-uk/ ; https://tech.eu/2025/07/29/google-launches-ai-mode-in-uk-search/
- **AI Overviews UK:** one agency source says they appear in about a third of UK searches by mid-2026, with a higher share for local-service queries than in the US. Confidence low (vendor). Source: https://generateleads.online/google-ai-overviews-2026-what-uk-businesses-must-know/
- **Search Console Generative AI report (confirmed UK-first):** launched 3 Jun 2026 to a subset of UK sites, following a CMA publisher conduct requirement. It shows impressions only for AI Overviews, AI Mode and Discover (no clicks, queries or position), with data from 18 May 2026. An opt-out toggle for AI features took effect 17 Jun 2026 and Google said it is not a ranking signal. One source says the reports reached all sites worldwide by 31 Aug 2026, so it is **no longer UK-only**. Confidence med (multiple trade sources, none primary). Sources: https://neilpatel.com/blog/gsc-ai-search-data-generative-ai-report/ ; https://www.sistrix.com/blog/google-must-report-ai-search-data-in-uk-new-regulations-published-by-cma/ ; https://ppc.land/google-reacts-to-uk-order-with-a-search-console-ai-opt-out-toggle/ (not fetched)
- **Consumer behaviour, UK.** Yext surveyed 600 UK consumers in 2026: 36.7% used AI for local search in the past month (EMEA 40.8%, global 42.7%), 75% of UK AI users use it more than a year ago, and 40% start local search on social media. Source: https://www.yext.com/blog/how-uk-consumers-navigate-local-search-in-age-of-ai (confidence med). A secondary source says ChatGPT leads UK AI usage, followed by Gemini and Copilot, with Copilot higher than elsewhere (low).
- **BrightLocal's 2026 survey is a US panel** (1,002 US adults). Its headline figures (45% use AI for local, 31% reject businesses under 4.5 stars) must not be presented to UK clients as UK data. Source: https://www.brightlocal.com/research/local-consumer-review-survey/ ; https://thevalleymarketinggroup.com/blog/brightlocal-2026-review-survey-service-businesses/ (confidence high that it is US-based).
- **Whitespark 2026 Local Search Ranking Factors** added AI visibility as a formal category. Three of the top five AI factors are citation-related: expert "best of" lists, top industry-relevant domains, and unstructured citations such as news, government and association sites. Not UK-specific. Source: https://whitespark.ca/local-search-ranking-factors/ (confidence med).
- ChatGPT local: location sharing launched 26 Mar 2026, and a Maps experience exists. UK availability not confirmed. Source: https://ppc.land/chatgpt-quietly-rolled-out-location-sharing-and-local-search-may-never-be-the-same/ (confidence low-med).

### 4.2 What assistants cite for UK local results
Two small UK studies with opposite emphasis (both vendor-published, small n, confidence low-med):
- **Murray Digital, 25 Aug 2026, ChatGPT.** 80 answers across 8 trades and 10 towns. Checkatrade was cited in 78, MyBuilder in 70, every answer cited at least one trade directory. Trade directories were 71.9% of sources, the business's own site 13.8%. Of 237 map-pack businesses, ChatGPT named 46, and only 2 because of their own site. https://murraydigital.co.uk/blog/ai-visibility-what-chatgpt-recommends-local-trades/
- **Whito, Google AI Mode.** 159 answers across 8 sectors and 20 towns. Own website cited in 90%, Google reviews or profile in 81%, trade directories 53%, regulators and trade bodies 45%, Reddit and Facebook 32%, auto-generated "best of" pages 20%, press 0%. Trustpilot only twice. https://whito.co.uk/research/ai-citation-sources-uk-local-business/
- A third write-up says Trustpilot appeared in 1 of 18 ChatGPT answers and Yell in 0 (July 2026), and that Perplexity almost never cites the business's own site, using comparison articles and roundups instead. https://pressat.co.uk/releases/study-chatgpt-perplexity-gemini-cited-104-sources-in-30-answers-and-cant-agree-on-any-of-them-1e3f27038c139ff0cacef81fa3511f93/
- Whito also published a piece arguing AI keeps recommending closed companies. That is a reason to verify Companies House status. https://whito.co.uk/opinion/are-ai-business-recommendations-reliable/ (low).

Reading across the studies: assistants disagree, so measure each one separately. Yell is rarely cited, so it matters as a data and trust source more than as an AI citation. Checkatrade is the single biggest lever for UK trades in ChatGPT. For other verticals I found no UK citation study.

### 4.3 UK language and query behaviour
Term differences to probe: solicitor (not lawyer or attorney), chemist (not drugstore), takeaway (not takeout), "emergency plumber Leeds" (city-first, no "near me"), "boiler repair", "tradesman", "estate agent", "garage" (car repair), "A&E" versus "urgent care", "NHS dentist", "plasterer", "builder", "gas safe engineer", "pub". "Near me" still occurs but UK trades queries are often "[trade] [town/postcode]". Postcode searches ("dentist LS6") are common. This is mostly from my knowledge, not from a study. Confidence low-med.

### Agent-actionable (section 4)
- Log citations per assistant and per vertical. Flag the share that comes from: own site, Google profile, trade directory, regulator, forum, press.
- For UK trades, make "listed and reviewed on Checkatrade (and MyBuilder)" a top GEO recommendation. For all verticals, recommend confirming Companies House active status because assistants can recommend dead firms.
- Label BrightLocal US figures as US. Prefer Yext UK for UK adoption claims.
- Add a Search Console AI report reader but treat it as impressions-only.

---

## 5. UK probe-prompt vocabulary and API location parameters

### 5.1 Query terms per vertical (about 8 each)

| Vertical | Natural UK terms |
|---|---|
| Dentist | "NHS dentist near me", "emergency dentist [city]", "private dentist [town]", "dental implants [city] cost", "teeth whitening [town]", "Invisalign [city]", "dentist accepting new NHS patients", "children's dentist [postcode area]" |
| Solicitor | "solicitor [city]", "conveyancing solicitor [town]", "family law solicitor [city]", "wills and probate solicitor near me", "employment solicitor [city]", "personal injury solicitor [city] no win no fee", "immigration solicitor [city]", "divorce solicitor [town] fixed fee" |
| Trades | "emergency plumber [city]", "gas safe engineer [town]", "boiler repair [city]", "boiler installation cost [town]", "electrician [town] NICEIC", "central heating engineer [city]", "burst pipe plumber near me", "EICR certificate [city]" |
| Restaurant / cafe / takeaway | "best restaurants [city]", "Indian takeaway near me", "fish and chip shop [town]", "Sunday roast [town]", "brunch [city]", "gluten free restaurant [city]", "pubs with food [town]", "cafe open now [city]" |
| Hair / beauty | "hairdresser [town]", "barber near me", "balayage [city]", "nail salon [town]", "lash lift [city]", "beauty salon [postcode area]", "waxing [town]", "bridal hair and makeup [city]" |
| Generic | "best [service] in [city]", "[service] open on Sunday [town]", "cheap [service] [city]", "[service] near [postcode]", "who is the best [trade] in [county]", "trusted [service] [town] reviews", "[service] with good reviews [city]", "local [service] recommended" |

### 5.2 Prompt templates in UK English (use for any vertical)
1. "I live in {town}, {county}. Can you recommend three reputable {service_uk_term} nearby? Please say why you picked each and name the sources you used."
2. "My {problem} needs sorting urgently in {city}. Who would you ring tonight, and how much should I expect to pay in pounds?"
3. "Compare the best-reviewed {service_uk_term} in {city}. Are any of them accredited with {regulator_or_body}? Give links."

### 5.3 Setting UK location in each API
Always also state the town in the prompt text. A thread in OpenAI's developer community reports the web tool telling models the user is in the USA, so rely on the explicit parameter plus the prompt, not on either alone. Source: https://community.openai.com/t/models-are-told-the-user-is-in-the-usa-when-using-the-web-tool/1379904 (confidence low-med).

| Provider | Parameter (confirmed from docs summaries) | UK example |
|---|---|---|
| OpenAI Responses `web_search` | `user_location: {type:"approximate", country, city, region, timezone}` (`country` is ISO alpha-2, `city` and `region` free text, `timezone` IANA). OpenAI's own example uses GB and London. https://developers.openai.com/api/docs/guides/tools-web-search | `{"type":"approximate","country":"GB","city":"Leeds","region":"West Yorkshire","timezone":"Europe/London"}` |
| Anthropic `web_search` tool | `user_location: {type:"approximate", city, region, country, timezone}`. At least one field required. Unsupported country codes return a 400. https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/web-search-tool | same shape as above |
| Perplexity API | `web_search_options.user_location: {country, region, city, latitude, longitude}`. Latitude and longitude must be given together with country. City and region improve accuracy. https://docs.perplexity.ai/guides/user-location-filter-guide | `{"country":"GB","region":"West Yorkshire","city":"Leeds","latitude":53.8008,"longitude":-1.5491}` |
| Gemini | Grounding with Google Maps takes `tool_config.retrieval_config.lat_lng` plus optional `language_code`. https://ai.google.dev/gemini-api/docs/generate-content/maps-grounding. I did not find a location field on the plain Google Search grounding tool (confidence low), so include the town and country in the prompt. | `lat_lng: {latitude: 53.8008, longitude: -1.5491}`, `language_code: "en-GB"` |

Region values: for England use the county or ceremonial area (West Yorkshire, Greater Manchester, Greater London). For Scotland, Wales and Northern Ireland use the nation name or the council area. OpenAI's sample uses "London" for both city and region, so exact region strings are loose.

| City | Region to pass | Lat, long |
|---|---|---|
| London | Greater London | 51.5074, -0.1278 |
| Manchester | Greater Manchester | 53.4808, -2.2426 |
| Birmingham | West Midlands | 52.4862, -1.8904 |
| Leeds | West Yorkshire | 53.8008, -1.5491 |
| Sheffield | South Yorkshire | 53.3811, -1.4701 |
| Bristol | Bristol | 51.4545, -2.5879 |
| Newcastle | Tyne and Wear | 54.9783, -1.6178 |
| Glasgow | Scotland | 55.8642, -4.2518 |
| Edinburgh | Scotland | 55.9533, -3.1883 |
| Cardiff | Wales | 51.4816, -3.1791 |
| Belfast | Northern Ireland | 54.5973, -5.9301 |

Coordinates are from my knowledge (city centres), not looked up today. To resolve postcodes to coordinates, a free postcode lookup service such as postcodes.io is the usual route (from knowledge, not verified today).

### Agent-actionable (section 5)
- Store a `uk_locations.json` with city, region, lat, long and timezone as above, and map it onto each provider's parameter shape.
- Run every prompt twice per assistant: with `user_location` and without, and log whether the answer mentions non-UK places. Flag any US-only result as a localisation failure.
- Use UK spelling and UK terms in generated prompts. Make the vocabulary map configurable per vertical.

---

## 6. UK authority-building

Findings (confidence med, mostly agency commentary):
- **Legit.** Local chamber of commerce membership (British Chambers has about 51 regional chambers, with a listing and link). BID membership (more than 100 BIDs in the UK; many have business directories). Trade-body and accreditation pages (Gas Safe, NICEIC, TrustMark, FMB, Law Society schemes). Council business directories and local-authority "buy local" or supplier lists. Hyperlocal news and community sites, local press features, local charity and community sponsorships that link back, and "best of" lists run by editorial sites. Sources: https://lancaster-chamber.org.uk/business-improvement-district-bid/ ; https://linkbuildingjournal.co.uk/local-link-building-how-to-dominate-your-local-market/
- **Entity signals.** Companies House (company number, registered office, status, filing history) is the authoritative record that AI and Google entity systems can match to. The ICO register shows a business paying its data protection fee and is a minor trust signal. Companies House data is public and free (from knowledge). ICO source: https://ico.org.uk/for-organisations/data-protection-fee/ (not fetched; confidence low-med as an SEO signal, high as a legal register).
- **Whitespark.** Unstructured citations from newspapers, government sites and industry associations, plus "best of" list placements, rank among the top AI visibility factors. See section 4.
- **Spammy or risky.** Bulk citation submission to 100 to 500 directories (agency commentary says marginal value after about 30 to 50 and a risk of NAP inconsistency), paid links and buying "best of" placements, fake or incentivised reviews (DMCC Act), fake local addresses and virtual offices on GBP, and keyword-stuffed business names. Source: https://linkbuildingjournal.co.uk/local-citations-vs-backlinks/

### Agent-actionable (section 6)
- Build an outreach list generator for each client's town: chamber, BID, council directory, trade body, hyperlocal sites. Rank by relevance.
- Offer a Companies House consistency check: trading name, registered name, company number and status against the website footer and GBP. A company website must show its registered name and number (from knowledge, med).
- Cap citation recommendations at the vertical-specific lists in section 1, with the "legit vs spam" rule printed in the output.

---

## 7. Things a US-centric tool would get wrong in 2026

1. **Wrong directory set.** No Yelp-centric workflow. Yell, Checkatrade, Doctify, Treatwell and others matter. Scoot, Touch Local and Rated People have just changed (section 1).
2. **US review statistics presented as UK.** BrightLocal LCRS 2026 is a US panel (section 4).
3. **Terminology.** Solicitor, chemist, takeaway, estate agent, heating engineer, "garage". Also £ and VAT, DD/MM/YYYY, and UK spelling ("organisation", "centre", "licence" as a noun).
4. **Four nations.** Regulators and registers differ: SRA (England and Wales) versus Scotland and NI law societies; FHRS (0 to 5) versus Scotland's FHIS (Pass or Improvement Required); CQC (England only) versus HIW, Care Inspectorate and RQIA; different bank holidays.
5. **Addresses.** No states and no ZIP codes. Postcode format, optional county, flats and building names, and "post town".
6. **Phone.** +44 with the trunk 0 dropped, variable lengths, 03 numbers, 07 mobiles.
7. **LSA.** Not available for most categories outside home services, and legal and estate agents only in Greater London. No assumption of US-style "Google Guaranteed". The Performance Max migration is expected later for UK accounts.
8. **Regulation of claims.** The DMCC Act covers fake and incentivised reviews, with CMA enforcement. The SRA transparency rules govern law-firm websites. GDC and ASA rules govern dental advertising (from knowledge, low-med).
9. **Google localisation.** ccTLD redirect to google.com. UK localisation relies on `gl`, `hl`, UULE or coordinates, not the host.
10. **AI localisation.** Always pass UK `user_location`. Without it, assistants can default to US context. Copilot and Bing matter more in the UK than in the US (low).
11. **Apple Maps.** Apple Business (the rebranded Business Connect, April 2026) is worth claiming. In markets with high iPhone penetration, including the UK, Apple Maps captures a significant share of local searches (low-med, one source: https://www.pinmeto.com/glossary/apple-business/).
12. **Data protection.** UK GDPR and PECR apply to review outreach. Most UK firms processing personal data need to pay the ICO fee (from knowledge for PECR; ICO fee confirmed above).

### Agent-actionable (section 7)
- Add a `market = "UK"` profile object that carries directory registry, terminology map, regulator map per nation, address and phone validators, GBP category source, LSA eligibility rules and API location presets.
- Add a pre-flight warning when a UK client's report cites BrightLocal US figures.

---

## Gaps / could not verify

- Every primary site fetch failed (egress proxy). Nothing above was read from support.google.com, blog.google, whitespark.ca, the CMA or the ICO directly.
- Scoot and Touch Local closure rests on search-snippet text from scoot.co.uk; no news article. Exact shutdown date unknown.
- Cylex UK, FreeIndex, Hotfrog UK, 118Information and ThePhoneBook.BT.com: "active" status comes only from 2026 listicles. Not independently confirmed.
- Whether Google Verified fully replaced Guaranteed and Screened in the UK (sources are US-heavy), and the exact UK Performance Max migration date.
- Whether Ask Maps is live in the UK today; whether Reserve with Google for beauty is available in the UK.
- Exact GBP category strings for UK takeaways and for specific legal specialisms. Use the API list.
- Whether the Search Console Generative AI report reached all sites by 31 Aug 2026 (one source) versus remaining a UK subset.
- No UK-specific study for dentists, restaurants or salons on AI citations. The two trades and cross-sector studies are small and vendor-published.
- Whether the Gemini Google Search grounding tool supports a location field.
- Coordinates and region strings in section 5.3 and the Companies House, Gas Safe, SELECT, OFTEC, MCS, ASA and GDC advertising details came from my own knowledge, not today's searches.
- Which? Trusted Trader and TrustATrader current commercial status beyond "pages live".
