# Critique of U1-uk-law.md (UK Critic Agent 1)

Date 2026-10-03. Not legal advice. **Method:** WebFetch is blocked here too (EGRESS_BLOCKED on legislation.gov.uk and asa.org.uk, same as the researcher). Everything below comes from WebSearch result summaries, so my "CONFIRMED" means "two or more independent search summaries agree, ideally one on an official domain". Official-text verification is still outstanding for every item marked [LAWYER].

## 1. Headline verdict

The research is mostly sound on DMCC, DUAA/PECR, platform policy and aesthetics. It has **three errors that would put wrong statements into client output**, one **misleading sector rule**, and **several omissions that matter more than items it did cover**:

1. **WRONG:** UK-ID-01 cites the Companies (Trading Disclosures) Regulations 2008. These were **revoked and replaced from 31 Jan 2015** by the Company, LLP and Business (Names and Trading Disclosures) Regulations 2015, SI 2015/17 (osborneclarke.com "new regime from 31 January 2015"; legislation.gov.uk/uksi/2015/17). The substantive website duty is unchanged, but citing a revoked instrument is the same class of error the researcher warned about for CPRs 2008. Section 10 of the summary repeats it.
2. **MISLEADING:** The CQC reg 20A pack sits under "Dentists". Primary dental care is **exempt from CQC ratings**, so most dental practices have no rating to display (cqc.org.uk "Display your ratings"; aethus.co.uk). A check "CQC rating displayed" would false-fail nearly every dentist. Reg 20A applies to rated providers only (GPs, care homes, hospitals, some independents), England only, and the display is due within 21 days of publication.
3. **WRONG hedge on CAP numbering.** The researcher says testimonials are "3.45-3.48 in one source and 3.47-3.50 in another". The first is right and the second is a miscitation. Settled numbers are in section 3.
4. **Missing and higher priority than anything in section 4.7:** the **CMA veterinary orders** (binding 23 Sep 2026; price lists on websites from Dec 2026 for larger groups and Mar 2027 for smaller ones), the **Funerals Market Investigation Order 2021** (standardised price list on website; Dignity, a funeral firm, is also under CMA fake-review investigation), **estate/lettings agent redress-scheme and fee-display duties**, and the **Botulinum Toxin and Cosmetic Fillers (Children) Act 2021**. These are website-content duties a crawler can check.

## 2. Spot-check table (25 claims)

| # | Claim | Verdict | Evidence / correction |
|---|---|---|---|
| 1 | DMCC consumer provisions in force 6 Apr 2025; CPRs 2008 revoked | CONFIRMED | cms.law "consumer elements come into force 6 April 2025"; ASA update on Code changes (7 Apr 2025) |
| 2 | Sch 20 has 32 banned practices | CONFIRMED | Linklaters "unfair commercial practices under the DMCC" |
| 3 | Review ban structure (para 13; "(a)-(d)" lettering) | PARTLY WRONG | Search summaries of legislation.gov.uk Sch 20 para 13: **13(1)** submit/commission fake or concealed-incentivised review; **13(2)** publish reviews/review info in a misleading way; **13(3)** publish without reasonable and proportionate steps to prevent fake/concealed-incentivised reviews. Offering services to produce fake reviews appears in commentary but I could not place its sub-paragraph. Drop the "(a)-(d)" lettering; cite "Sch 20 para 13". |
| 4 | CMA direct fines up to 10% global turnover | CONFIRMED | Pinsent Masons, Ashurst, Shoosmiths. **Correct the cap wording:** the cap is "£300,000 or 10% of global turnover, whichever is higher" for undertakings; individuals who are accessories face up to £300,000. The researcher's "£300k is for individuals per some sources" is muddled. Lower tiers: £30k/£150k or 1%/5% for procedural breaches. |
| 5 | "29 of 32 banned practices are criminal offences" | CONFIRMED (secondary) | Linklaters; Brodies. Keep the [LAWYER] flag. |
| 6 | CMA first fake-review investigations 27 Mar 2026, named firms | CONFIRMED | gov.uk press release; Wiggin; BCLP. Autotrader/Feefo (excluded 1-star), Dignity (staff-written reviews), Just Eat (inflated ratings), Pasta Evangelists (undisclosed discounts). No infringement findings seen. Current status after Sep 2026 unknown. |
| 7 | AA £4.2m drip-pricing fine, 15 Apr 2026 | CONFIRMED | Blake Morgan, Sidley, TLT, gov.uk. Add: first DMCCA substantive fine; £7m reduced by 40% for settlement; £760k refunds to 80,000+ learners; one of eight firms probed from Nov 2025 (more outcomes may exist). |
| 8 | Disclosed incentivised reviews lawful under DMCC | CONFIRMED | CMA208 per CMS, Browne Jacobson, Reed Smith: banned only if the incentive is concealed; must be prominently labelled and the review genuine. |
| 9 | DUAA PECR changes commenced 5 Feb 2026; fines £17.5m/4% | CONFIRMED | SI 2026/31 (legislation.gov.uk); ICO statement Feb 2026; DLA Piper; Clifford Chance. Complaints-procedure duty commenced **19 Jun 2026**, so "about June 2026" can be firmed up. |
| 10 | New cookie exceptions (statistical, appearance, security, updates); ICO final guidance 29 Apr 2026 | CONFIRMED | ico.org.uk "Final storage and access technologies guidance published" (2026/04); Hunton; Osborne Clarke |
| 11 | GA4 does not qualify for the statistical exception | CONFIRMED as commentary; ICO text UNVERIFIED | ICO allows a third-party analytics processor only if data is used solely for the site owner's purposes; commentators say GA defaults let Google reuse data. "Treat as consent-required" is a defensible conservative default, not settled law. Say "likely does not qualify in default configuration". |
| 12 | ICO became Information Commission on 30 Sep 2026 | CONFIRMED | Didlaw; Reed Smith; AberdareOnline 1 Oct 2026. Legal entity is the Information Commission; the office is still branded "ICO". Hard-code neither name; use "the ICO (Information Commission)". |
| 13 | ICO position on review-request messages | UNVERIFIABLE | No ICO text found either way. ICO guidance says genuine surveys are not direct marketing, but promotion or later-marketing use converts them. Practitioner blogs claim a plain review request is a "service message" (the researcher already flagged this). Treat as unsettled; keep WARN, not REFUSE. |
| 14 | SRA Transparency Rules (current version 11 Apr 2025); E&W only | CONFIRMED | sra.org.uk transparency rules; Lexology. Four items: price/service info, complaints info, regulatory statement + clickable digital badge. Scotland and NI excluded. |
| 15 | CQC reg 20A rating display | PARTLY WRONG | See headline item 2. |
| 16 | CAP 12.12 POM ban; Botox is a POM | CONFIRMED | asa.org.uk "Rules for advertising Botox" and enforcement notice |
| 17 | CAP 12.25 under-18 targeting, in force 25 May 2022 | CONFIRMED | ASA "New targeting rules ... come into force today" (announced Nov 2021, in force 25 May 2022) |
| 18 | England aesthetics licensing scheme not yet in force | CONFIRMED | No SI made; consultation response 7 Aug 2025 (red/amber/green; Botox/fillers = amber, local-authority licence); further consultation expected 2026. One site (HealSuite) claims "starts July 2026"; it is contradicted by the others and by lack of an SI. |
| 19 | Google 17 Apr 2026 update (staff names, quotas) | CONFIRMED (trade press) | Two changes on 16 and 17 Apr 2026; kiosks and gating were reinforced, not newly banned. Primary Google text not read. |
| 20 | Trustpilot: invite all or impartial sample; no incentives | CONFIRMED | Trustpilot guidelines (feb-2026, jun-2026 versions exist). The researcher cites the stale "may-2025" URL; link to the versionless page and store a retrieval date. |
| 21 | FHRS display mandatory only in Wales and NI | CONFIRMED | FSA-related summaries. Scotland's FHIS is voluntary. One source says the FSA is "moving toward" mandatory display in England; no legislation found. |
| 22 | ECCTA: IDV from 18 Nov 2025; PO-box registered-office ban | CONFIRMED | CMS, DLA Piper, Freshfields. PO-box/"appropriate address" rule has applied since **4 Mar 2024**; the researcher implies it is part of the Nov 2025 step. |
| 23 | Trading Disclosures Regs 2008 website duty | WRONG instrument | See headline item 1. |
| 24 | E-Commerce Regs 2002 reg 6 (email, VAT number, company no.) | CONFIRMED | Retained UK law post-Brexit (clym.io; SCL; Pinsent Masons). Applies to information society services; brochure sites with online contact are commonly treated as covered, but that is practitioner reading. |
| 25 | PECR B2B (corporate subscribers) | CONFIRMED broadly | ICO B2B page. Sole traders and some partnerships are "individual subscribers"; corporate-subscriber email is lighter but still needs identity and opt-out. |

## 3. CAP Code numbers (corrected)

Note the Codes were amended on **7 Apr 2025** (post-DMCC, wording changes, mostly stable numbering). Store these as `topic + rule + edition`.

| Topic | Use | Researcher | Status |
|---|---|---|---|
| Misleading | 3.1 (3.3 omission) | same | OK |
| Subjective claims / opinion | **3.6** | cited "3.7 guidance" | fix |
| Substantiation | 3.7 | 3.7 | OK |
| Qualification | 3.9-3.10 | 3.9 | OK |
| Exaggeration | 3.11-3.12 | 3.11 | OK |
| Prices | 3.17 (omission/emphasis), 3.18 (non-optional fees included), 3.19 (incalculable charges), 3.20 (delivery) | 3.17-3.22 | OK |
| Free | 3.23 (3.23-3.26) | 3.23 | OK |
| Comparisons / superlatives | **3.32-3.36** (3.32 not mislead; 3.33 same needs; 3.34 objective, material, verifiable, representative feature; 3.35-3.36 confusion/denigration-type rules). ASA says unqualified superlatives are treated as comparisons with all competitors under 3.32-3.36. | "3.33-3.35 (3.32 start)" | cite the 3.32-3.36 range; do not cite single numbers |
| Testimonials | **3.45** genuine + contact details; **3.46** relates to product; **3.47** factual claims must not mislead; **3.48** permission | "3.45 or 3.47", "3.47-3.50" | drop the alternative numbering |
| Trust marks / approvals | **3.50** | 3.50 | OK. (3.49 is "no reference to CAP/ASA advice"; 3.51 false code-signatory claims; 3.52 Royal Arms.) |
| Guarantees | 3.53 (word "guarantee"), 3.54 (limitations, terms before commitment) | 3.53-3.55 | 3.53/3.54 confirmed; 3.55/3.56 unverified |
| Before/after | no dedicated rule; 3.1, 3.7, 3.45 | same | OK |
| POM | 12.12 | same | OK |
| Cosmetic targeting | 12.25 | same | OK |
| **Recognisability (missing)** | **2.1-2.4** | absent | add |

## 4. Missing legal items (priority order for a UK local-business agent)

1. **CMA vet orders** (binding 23 Sep 2026; website price lists Dec 2026 / Mar 2027; written estimate at £500+; Rx fee caps). Source: gov.uk/CMA vets final decision 25 Mar 2026 (wired-gov summary; BVA). RCVS rules also apply. Pack needed.
2. **Funerals Market Investigation Order 2021:** standardised price list on website and at premises. Pack needed.
3. **Estate/lettings agents:** mandatory government-approved redress scheme (TPO/PRS) named on website and in offices (Enterprise and Regulatory Reform Act 2013 order, 2014); lettings fees displayed on website (Consumer Rights Act 2015 s.83-84 for England; Tenant Fees Act 2019 and Renters' Rights Act changes); NTSELAT/material information on listings. Source: Zoopla redress page; Shelter; National Trading Standards guidance July 2022.
4. **ASA recognisable advertising (CAP 2.1-2.4), influencer/affiliate disclosure** ("#ad", paid partnership, gifted items, affiliate links): matters for any agent that drafts social posts or partnerships. CMA/ASA updated influencer guidance winter 2025.
5. **Botulinum Toxin and Cosmetic Fillers (Children) Act 2021** (in force 1 Oct 2021): administering to under-18s is an offence, with a duty to verify age. Extent is England and Wales, with a few provisions UK-wide; Scotland and NI treated separately. Add an age-check statement to aesthetics packs and a "do not advise Scotland/NI licensing" caveat.
6. **Consumer Contracts Regulations 2013 / Consumer Rights Act 2015** (cancellation rights, services standards): researcher flagged unresearched. Needed for any e-commerce or booking site checks.
7. **Equality Act 2010 s.20 (website accessibility):** no technical standard in law; WCAG 2.2 AA is the usual benchmark. WARN/CHECK only; never claim "compliant".
8. **Scotland/NI specifics:** Law Society of Scotland practice rules (advertising must be accurate and not misleading; separate from SRA) and Law Society of NI; Scotland's independent clinics regulated by Healthcare Improvement Scotland; Scottish aesthetics bill in progress. Welsh Language Standards bind **public bodies**, not private local businesses; the research should say so rather than leave it as a gap, and recommend a Welsh-language-offer prompt only for Welsh clients.
9. **FCA financial promotion exemptions** (the researcher did not cover them): the agent should not tell a client an exemption applies. [LAWYER].
10. **Childcare (Ofsted/CIW/Care Inspectorate/RQIA)**: grade-display and registration-number claims; low priority, same trust-mark logic as 3.50.
11. Online Safety Act 2023: low relevance to a local-SEO agent unless the client runs user-generated content (reviews/comments/forums). Mention only as a triage item.
12. Aesthetics under-18 and POM rules also interact with **GBP category/attribute choices** (e.g. "Botox clinic" as a category name). Needs a rule: refuse category/service-name text that includes POM brand names.

## 5. Encodable behaviours: false-positive and weakness analysis

**Too aggressive (will block lawful marketing):**
- UK-REV-02 as REFUSE for *any* reward-for-review proposal is fine, but the text must separate "never suggest" from "tell the client it is unlawful". Disclosed incentives are lawful (row 8). The agent must say "platform-banned, and unlawful unless disclosed", not "illegal".
- UK-ADV-01 REFUSE "best/No.1/leading". Not every superlative is unlawful: "best-loved by our customers" or an evidenced "Winner of X award 2026" is fine. Detect, then **WARN and require an evidence field** (source, date, scope, competitor set); REFUSE only when the client supplies no evidence or states "guaranteed #1". Regex: `\b(best|no\.?\s?1|number one|leading|top[- ]rated|cheapest|#1)\b` near `\b(in|of|for)\s+[A-Z][a-z]+` (place). False-positive risk: high (idioms, "best practice"). Treat as a WARN trigger only.
- UK-AES-01 REFUSE brand names: correct for public marketing, but the pattern must not block legitimate **clinician-to-patient** content behind consultation, nor the regulator-facing page of a pharmacy. Regex `\b(botox|dysport|azzalure|bocouture|vistabel|botulinum)\b|#botox`; also catch "wrinkle relaxing injections"? CAP treats indirect references as POM advertising, but the exact line is context-dependent: WARN for indirect, REFUSE for brand names. False-positive risk: low for brand names, medium for generic terms.
- UK-REV-03 REFUSE all selection beyond "all customers" is too tight: Trustpilot allows an impartial sample (the researcher allows it). Keep as written but add that excluding customers with open complaints is **not** impartial (gating by the back door).
- UK-DP-01 (review requests = marketing): an unsettled point; the correct level is WARN, requiring a human decision. Do not auto-refuse sending on the basis of it.

**Too weak / missing:** Doctors/solicitors/dentists replying to reviews (UK-DEN-01, UK-SOL-03) are right as REFUSE. Add "do not confirm the reviewer was a patient/client" detection: a reply draft that echoes names, dates, treatments should be hard-blocked, not just warned. Also add a REFUSE for **ranking guarantees in the agent's own sales copy** (UK-ADV-01 covers it; make it explicit for the agent's reports).

**What a crawler can test reliably:**

| Check | Method | Reliability / false-positive risk |
|---|---|---|
| Company number on site | regex `\b(?:SC|NI|OC|SO|NC|R)?\d{6,8}\b` within 200 chars of `(company|registered)\s*(no|number|reg)` , or `(registered in|registered office)` | Good for limited companies (precision ~high, recall medium: image footers and PDFs missed). Must first learn that the client is a limited company (Companies House lookup). Do not run for sole traders. |
| Place of registration | `registered in (England|Wales|England and Wales|Scotland|Northern Ireland)` | Good |
| Registered office address | match against Companies House record string, normalised | Medium; flag "differs" not "fail" |
| Email address on page (reg 6) | `mailto:` or email regex on contact/footer | Good; forms-only sites are a fail |
| VAT number | `VAT\s*(reg(istration)?\.?\s*)?(no|number)?\.?:?\s*(GB)?\s?\d{9}` | Good if client is VAT registered; do not assert otherwise |
| SRA number/badge | `SRA (number|no)\.?\s*\d{5,6}` + SRA badge script/img from sra.org.uk | Good (E&W firms only; skip if postcode is Scottish/NI) |
| CQC rating | link to cqc.org.uk/location + image/text `(Outstanding|Good|Requires improvement|Inadequate)` | Only for rated providers; **never check dentists** unless the CQC register shows a rating |
| Food hygiene rating | link to ratings.food.gov.uk; compare to FSA API | Reliable via API; display is only *mandatory* in Wales/NI |
| Cookie banner / pre-consent tags | headless load; count requests/cookies before interaction (googletagmanager, facebook, hotjar etc.) | Technically reliable for "tag fired before consent" (high); **legal conclusion** needs a lawyer. Report as "observed", not "unlawful". |
| Review schema vs visible rating | parse JSON-LD `aggregateRating`; compare to the platform API | Medium: self-serving review schema is a Google policy matter, not a DMCC finding. The researcher's UK-REV-05 is correctly marked "inference". |
| Hard-coded "5.0 stars" | regex `\b5(\.0)?\s*(/5|stars?)\b` without a platform link | High false-positive (a real 5.0 with link); WARN only |
| Trust marks | image/alt matches `gas safe|trustmark|niceic|checkatrade|which\? trusted trader` | Detection high; **verification** needs registers (Gas Safe/TrustMark API). Report "unverified" |
| Vet/funeral price list | link text `price list|our fees|standardised price` + PDF | Medium; the CMA format cannot be validated by crawler |
| "Free" with hidden cost | not crawlable | Drop |
| Drip pricing | hard to crawl; check "from £" without fees text | WARN only; high false-positive |

## 6. Verdict per section and MUST-fix list

| Section | Verdict |
|---|---|
| 0 Exec summary | FIX (items 5-6 wording; item 10 cites the revoked 2008 regs; item 6 numbering) |
| 1 Reviews / DMCC | KEEP with fixes (para 13 lettering; fine-cap wording; add Dignity is a funeral firm; add "status unconfirmed" flag as the researcher does) |
| 2 Advertising / CAP | FIX (numbers per section 3; add 2.1-2.4; puffery 3.6; comparison range) |
| 3 Data protection | KEEP; soften GA4 and review-request language; add complaints regime date |
| 4 Regulated sectors | FIX (CQC/dental); ADD vets, funerals, estate agents, Children Act; mark childcare etc. "not built" |
| 5 Platforms | KEEP; use versionless URLs |
| 6 Business identity | FIX (2015 Regs); tighten reg 6 applicability |
| 7 Nations | KEEP; add Welsh Language Standards = public bodies only; Children Act extent |
| 8 Lawyer list | KEEP; add vet/funeral/estate-agent price-list formats and the "is this exempt from CQC rating" question |

**Builder MUST apply (priority order):**
1. Replace "Companies (Trading Disclosures) Regulations 2008" with "Company, Limited Liability Partnership and Business (Names and Trading Disclosures) Regulations 2015 (SI 2015/17)" everywhere (UK-ID-01, summary rule 10). Add a lint rule: any citation of SI 2008/495 or CPRs 2008 as live = failure.
2. Make the CQC check conditional: run only when the CQC register shows a rating for the location. Dentists default to "no reg 20A check; verify GDC numbers instead".
3. Use the CAP numbers in section 3; delete the "3.47-3.50" alternative; cite 3.32-3.36 for comparisons/superlatives.
4. Reword the incentivised-review rule: "Lawful only if prominently disclosed; banned by Google, Trustpilot, Checkatrade, Yell; the agent never proposes it." Never output "illegal".
5. Add packs (CHECK-only, marked [LAWYER]): vets (CMA order, dates), funerals (SPL), estate/lettings agents (redress scheme, fees, material information), aesthetics under-18 (Children Act).
6. Set UK-DP-01 (review requests) to WARN-with-human-decision, citing "ICO position not confirmed".
7. Cookie/GA4: output "observed pre-consent tags" and "likely does not meet statistical exception", not "unlawful".
8. Firm the dates: complaints regime 19 Jun 2026; PO-box ban 4 Mar 2024; Google update 16-17 Apr 2026; AA fine £7m reduced 40% to £4.2m.
9. State the exact fine-cap wording (undertakings: higher of £300k and 10% global turnover).
10. Version the Trustpilot, SRA and Google URLs and store a retrieved-on date; add a 90-day staleness flag to every rule.

**Needs a human lawyer before encoding as fact:** exact Sch 20 para 13 wording and offence defences; whether a client displaying a Trustpilot/Google widget is a "publisher" owing the reasonable-steps duty; review-request direct-marketing status; GA4/call-tracking consent design; whether any dentist or aesthetics client falls inside CQC rating or the (future) licensing scheme; FSMA s.21 exemptions; solicitor (Scotland/NI) and healthcare advertising copy; CMA vet and funeral price-list formats; defamation/takedown strategy.
