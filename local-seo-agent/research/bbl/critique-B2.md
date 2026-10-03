# Critique of B2 (SEO and new-profile playbook) - Critic B2, 2026-10-03

Method note: WebFetch was blocked for every domain I tried (support.google.com, developers.google.com, brazilianbootylift.co.uk, legislation.gov.uk). All checks below use WebSearch summaries, the same limit as the researcher. "CONFIRMED" means a search summary of the primary source, or several independent sources, agrees. It does not mean I read the page.

## 1. Biggest problem: the client facts are probably wrong or incomplete

Search results I found, which B2 did not:

- The business is probably **"[trading name redacted] (BBL & Beauty Studio)"**. Nextdoor lists it by that name. [owner name redacted] owns "[trading name redacted] beauty studio" and "Brazilian Booty Lift Lanarkshire". [trading name redacted] was a finalist at the Scottish Beauty Industry Awards 2025.
- BBL Lanarkshire is therefore likely a service line or brand inside an existing beauty studio, not a standalone business. The report's whole naming section (section 4) assumes the signage says "Brazilian Booty Lift Lanarkshire". If the shopfront says [trading name redacted], a profile called "brazilian bootlift lanarkshire" fails the "matches real-world signage" test from day one.
- A profile for [trading name redacted] may already exist, with reviews. Check it. The Google guideline on several businesses at one address and the duplicate-profile advice then apply immediately.
- The brand's store page, per search snippets, gives the address as [street address and postcode redacted]. It gives the phone as **[phone redacted]** and the email as **[email redacted]**.
- B2 cites only the landline [phone redacted] (from a third-party profile) and tells the agent to "check the postcode". Two public sources already disagree on the phone. That is a live NAP conflict, not a hypothetical.
- The report treats a personal hotmail as the email problem. The brand page shows an email on a domain ([trading name redacted]), which may be the client's own. If so, "does the client own a domain?" has a partial answer. This is unverified, so the agent must ask.
- "Franchise" is unproven. The Trustpilot snippets show a training, device-supply and lease model (see section 2). The agent should say "licensed or trained stockist, structure unconfirmed".

## 2. Spot-checks (22 claims)

| # | Claim in B2 | Verdict | Evidence / comment |
|---|---|---|---|
| 1 | GBP APIs need a verified profile active 60+ days, plus a website | CONFIRMED | Search summary of Google's prerequisites page. B2 omits that the profile can be the applicant's own, not the client's. Access is per Cloud project, quota is 0 and every call returns 429 until approval, and review takes up to 14 days. If the operator already has a 60-day-old profile, it can apply now. |
| 2 | Earliest API date is about 2026-12-02 | CONFIRMED arithmetically | Only applies if the client's profile is the qualifying one. Missing: the client's owner or manager must grant OAuth consent before any API call works. |
| 3 | Name must match the real-world name; no extra keywords or locations | CONFIRMED | Google's guidelines page, via search. |
| 4 | "Brand + region" is a defensible franchise pattern | PARTLY | Google's own documentation is internally inconsistent: one section allows a location element, the chains section rejects "Home Depot at Springfield". Signage is the deciding evidence. B2 is right to hedge but does not mention the inconsistency. |
| 5 | Editing the name, address or category can force re-verification or review | CONFIRMED | Google help text, via search: changing the name of a verified profile may require re-verification. B2 attributes this to "vendors" only. That undersells it, because Google says it itself. |
| 6 | Video verification is the default | CONFIRMED (vendor) | Vendors say it became the default for most small businesses from 3 July 2026, requiring 30+ seconds in one take with permanent signage. Moot for this client, who is already verified. The signage in that video is the evidence base. |
| 7 | April 2026 policy: staff quotas and staff-name solicitation banned (17 April) | CONFIRMED | PPC Land and several others. |
| 8 | Gemini screens profile edits (April 2026) | CONFIRMED, tag raised from "vendor med-low" | Google's 16 April announcement reported 79 million blocked edits. The model flags edits that are inconsistent, for example a category swap. |
| 9 | New profiles get reviews filtered more aggressively | UNVERIFIABLE | All sources are vendor blogs. The "20-25% of filtered reviews are legitimate" figure is folklore. "7 days pending means permanently filtered" is also vendor folklore. |
| 10 | Sterling Sky 50 cases: 60% warning, 20% soft suspension, 20% hard | PARTLY | The 60% and 20% soft figures are confirmed. I could not confirm the 20% hard figure. The study is old and mostly law firms. Its main finding was that enforcement is manual and driven by competitor reports. B2's "Google cross-references the name against signage automatically" and its "automated re-review" framing sit awkwardly with that. |
| 11 | Category "Body contouring service" | UNVERIFIABLE, likely not a category | It appeared in none of the category lists in my results. "Body shaping class" and "Body piercing shop" did appear. B2 correctly flags it as weak. |
| 12 | "Cosmetic surgery clinic" cannot be confirmed | UNVERIFIABLE | One vendor summary lists it, others do not. Irrelevant for a non-surgical studio. It should be on the "never use" list. |
| 13 | "Medical spa" is a common vendor recommendation for non-surgical studios | RISKY | UK vendors call it "an American term, the closest available". For a non-medical beauty studio it implies medical oversight. Scotland's HIS regulates clinics where registered clinicians work, and the new Act sharpens this. B2 lists it without a warning. |
| 14 | Weight loss service category | NOT ADDRESSED | B2 never discusses it. It invites efficacy and ASA problems and should not be used. |
| 15 | FAQ rich results "ended in May 2026 and are restricted to authoritative government and health sites" | WRONG | Google removed FAQ rich results for all sites on 7 May 2026, including the government and health sites that had kept them. The sentence is also internally contradictory. FAQ markup is still parsed for understanding. |
| 16 | Apple Business Connect became "Apple Business" in April 2026 | CONFIRMED | Rebrand on 14 April 2026; existing claimed locations carried over. |
| 17 | Scotland Act: Royal Assent 12 May 2026; start Sept 2027 | CONFIRMED | Passed 18 March per the summaries I saw. B2 says 17 March, which is a trivial discrepancy. The date is not load-bearing. |
| 18 | Lower-risk tier (council licence) lists cryolipolysis, HIFU and RF | DOUBTFUL | Search summaries describe the Order as covering procedures that "pierce or penetrate the skin" and need no healthcare professional. Cryolipolysis, HIFU, cavitation and vacuum do not penetrate. B2 says "med", but it may be wrong in the opposite direction: these devices may not be licensable at all. Treat as UNVERIFIED either way. The plan should not claim "you need a licence" or "you are exempt". |
| 19 | Brand Trustpilot (216 reviews, 4.5) is "dominated by training" | PARTLY WRONG | The 216 / 4.5 figures are correct. But snippets also show serious complaints about faulty cavitation and vacuum heads, equipment leasing and contract and termination terms. Branded searches for "Brazilian Booty Lift reviews" may therefore surface supplier-dispute content. B2 missed this reputational point. |
| 20 | Fresha, Booksy and Treatwell list body treatments in Scotland | CONFIRMED | Treatwell shows only about 32 body-treatment venues in Scotland. Treatwell already lists other brand stockists (for example "Brazilian Booty Lift KLW", London). B2 never mentions cost: Treatwell takes about 35% of a new client's first booking, Booksy about 40% plus a £39.99 monthly fee, and Fresha 20% plus per-calendar fees. Calling these the "best-value set" without costs is unsupported. |
| 21 | Google restricts CTAs and offers for regulated goods and services; B2 says unclear for body contouring | PARTLY | The policy covers "health or medical devices" among restricted items. The device point is about selling devices, not treatments, so B2's uncertainty is fair. The safe default is no offers, prices or "book now" CTAs in posts. |
| 22 | AI-assistant studies (94.1% accuracy, 98% / 79% consult quality, arXiv 2609.00319) | UNVERIFIABLE | Plausible but unread. All are US or non-BBL. B2 rates them low and stays honest. They should not be used as decision inputs. |

## 3. Over-claims, folklore and internal contradictions

- **Confidence is too high in section 1.** "The GBP API 60-day rule is real" is fine. "Core-field edits soon after verification are the documented trigger for suspension" rests on vendors. Google documents re-verification; it does not document suspension on edits. Soften the wording.
- **Section 1 item 4 conflates three things.** The 17 April policy change (staff quotas, staff names), vendor claims about review velocity and new-profile filtering, and the DMCC Act are different layers. Only the first is Google policy. The velocity point has no published threshold.
- **Contradiction in section 4.** The report says competitor reports can trigger action, and also describes automated Google cross-referencing. Both exist (manual reports plus the new Gemini edit model), but the report does not say so. The agent will model it incorrectly.
- **"Personal hotmail is not a documented ranking problem."** True but beside the point. The real issue is account recovery, and who owns the profile.
- **"Check-a-Trade-type" and "Scottish Directory Group"** were not verified. The Yell page is cited from its URL alone.
- **Vendor timelines** (appeals 3-14 days, 60-75% success, ranking in 1-3 / 6-12 months) are tagged correctly. They must not appear in client-facing KPIs.
- **Section 12** lists surgical-only directories (HIS, GMC, Doctify, RealSelf, WhatClinic, PHIN, ASPS) at length. None apply to this client. Cut them.

## 4. Scotland and Lanarkshire errors and gaps

- Admin geography is mostly right: Wishaw, Motherwell, Bellshill, Airdrie, Coatbridge and Cumbernauld are North Lanarkshire; Hamilton, East Kilbride and Lanark are South Lanarkshire. "Lanarkshire" is not itself an administrative area and is the NHS board name. One quibble: Clinetix in Bothwell is South Lanarkshire, which is correct as written.
- The report gives **no postcodes at all**. Wishaw is ML2, with [postcode redacted] for this studio. Neighbouring areas: ML1 (Motherwell), ML3 (Hamilton), ML4 (Bellshill), ML5 (Coatbridge), ML6 (Airdrie), G67 and G68 (Cumbernauld), G71 (Viewpark / Tannochside), G72 (Blantyre / Cambuslang). The agent needs these for town-level pages and rank-tracking grids.
- **Locality**: the address is [redacted], not central Wishaw. Locality naming drives distance ranking. Pick one format.
- There is no travel-time analysis for Glasgow. Wishaw to Glasgow is roughly 15 miles. Say "about 25-40 minutes by train or road" only after checking. The report notes that Glasgow-intent searches will favour city-centre addresses, which is sound.
- **Service area versus storefront**: B2 says show the address. That is right for a staffed studio with signage, but only if the studio really has a permanent sign. It is unclear whether this is a shared [trading name redacted] premises.
- Missing Scottish and local sources: Nextdoor (an existing [trading name redacted] page), the Glasglow Girls Club profile (a citation already live), the Scottish Beauty Industry Awards listing, and the North Lanarkshire Council business directory.

## 5. What is missing for a brand-new franchise-branch profile

1. **Name decision tree** ([trading name redacted] versus Brazilian Booty Lift Lanarkshire), signage check, and a duplicate search for an existing [trading name redacted] profile.
2. **Ownership and roles.** Who is the primary owner, the franchisor's possible claim on the location, and what ownership-transfer risk exists if the client leaves the brand. Name a second manager or owner for recovery. Never share the owner login with an agency.
3. **Phone and email.** Choose one number from the two found. The email on [trading name redacted] is a candidate.
4. **Website link, UTM and tracking.** Use UTM on the website link, appointment link and menu link. Check that the brand page allows it. If the brand page is the destination, Search Console cannot be verified without franchisor access.
5. **Attributes, products and services lists, appointment link.** The report covers these only in passing.
6. **Handling brand-level reviews**: Trustpilot lease complaints, and other stockists' Treatwell and Google reviews under similar names. Monitor, do not mix, do not copy rating markup.
7. **Instagram and Facebook alignment.** The Facebook page is "Brazilian Booty Lift Lanarkshire". Instagram handle and category were not checked.
8. **Competing stockist profiles** for the same brand name in nearby areas: a branded-query risk.
9. **Licence readiness** for Sept 2027, in the content roadmap.
10. **Opening-hours and special-hours policy**, and a staffing and appointment-only note (appointment-only studios are allowed but should state it).

## 6. Verdict per section

| Section | Verdict | Reason |
|---|---|---|
| 0 Method limits | KEEP | Honest. |
| 1 Executive summary | FIX | Rewrite items 1, 2, 4, 5, 8, 11 (see corrections). |
| 2 Verification and API | FIX | Add the "own profile qualifies" nuance, the OAuth consent step, and a zero quota until approval. |
| 3 30/60/90 plan | FIX | Replace the category table. Add owner, roles, UTM and duplicate check as days 0-7 items. |
| 4 Naming | FIX | Rebuild around the [trading name redacted] question. |
| 5 Reviews | KEEP, trim | Keep policy and DMCC. Mark velocity and filtering numbers as folklore. Drop the GMC and US HHS content (does not apply). |
| 6 Suspension | KEEP | Good. Cut the vendor appeal statistics. |
| 7 NAP and franchise | FIX | Fix contacts, add [trading name redacted] and Nextdoor, correct Trustpilot, add costs. |
| 8 Intent and local | KEEP local half, DROP surgical half | |
| 9 Scotland law | FIX | Dates are fine. Remove the claim that cryolipolysis or HIFU is licensable. |
| 10 BBL ambiguity | KEEP, strengthen | |
| 11 AI assistants | KEEP as hypotheses only | |
| 12 Directories | DROP most | Surgical rows irrelevant. |
| 13 Content and schema | FIX | Remove the FAQ-for-gov/health error. |
| 14 KPIs | KEEP | |
| 15 Gaps | KEEP, extend with the [trading name redacted] finding | |

## 7. MUST-apply corrections, in priority order

1. **Replace the client facts.** "Studio trades as [trading name redacted] (BBL & Beauty Studio) at [street address and postcode redacted]; the brand page shows phone [phone redacted] and email [email redacted]; a third-party profile shows [phone redacted]. Franchise structure unconfirmed."
2. **Add a pre-edit gate.** "Before touching the GBP name, confirm (a) what the permanent shopfront sign says, (b) whether an [trading name redacted] profile already exists at this address, and (c) the exact name on the video-verification clip. The GBP name must match the signage. Do not rename to add 'Lanarkshire' or any service word unless the sign says it."
3. **Fix the category advice.** "Primary: choose from the dashboard list, most likely 'Beauty salon'. Do not use any surgeon, 'Cosmetic surgery clinic', 'Medical spa' (implies medical oversight) or 'Weight loss service' (efficacy claims). Secondary only if true. 'Body contouring service' is unconfirmed; search for it in the dashboard and do not assume it exists."
4. **Fix the FAQ sentence.** "Google ended FAQ rich results for all sites on 7 May 2026. FAQ markup remains harmless but earns no rich result."
5. **Replace the Trustpilot text.** "The brand's Trustpilot page (216 reviews, 4.5) mixes praise for training with complaints about faulty equipment and lease and contract terms. Monitor it, never link to it, never copy its rating."
6. **API wording.** "Access needs a verified profile aged 60+ days (the applicant's own or a client's), a website and an approved Cloud project. Quota is 0 until approved. Calls on the client's profile also need the client's OAuth consent. The client's profile reaches 60 days on 2026-12-02."
7. **Scotland licensing.** "The Order covers procedures that pierce or penetrate the skin without a healthcare professional. Whether cavitation, vacuum, RF or cryolipolysis are included is UNVERIFIED. Ask North Lanarkshire Council and the franchisor before Sept 2027. Do not claim either 'licensable' or 'exempt'."
8. **Avoid "non-surgical BBL" in titles and descriptions.** In the 2026 Act it is the legal label for filler procedures to be restricted. Use "non-surgical body contouring" and say "no surgery, no injections" in the first line.
9. **Directory costs.** Add Treatwell about 35%, Booksy about 40% plus £39.99 a month, Fresha 20% plus per-calendar fees. Recommend Facebook, Instagram, Bing and Apple first; the paid marketplaces are optional.
10. **Cut or demote** all surgical-only content (HIS surgical, GMC, PHIN, RealSelf, Doctify, WhatClinic, US AI-accuracy studies) to an appendix.

## 8. What the plan must NOT promise

- Any ranking, pack position, "top 3" or date.
- A review count or review velocity, or that a review will stay visible.
- Suspension-appeal success or timing.
- AI-assistant mentions, citations or accuracy.
- That any category, including "Body contouring service", exists until it has been seen in the dashboard.
- That the profile name is safe because verification passed.
- Legal certainty on Scottish licensing or on the brand name.
- Revenue, lead numbers or treatment results.
- That the franchisor's page can be edited or that the client controls its domain.
