# U3: REST API contracts for local-seo-agent adapters (httpx, no vendor SDKs)

Date of research: 2026-10-03. Author: Research Agent 3.

## 0. Method, evidence tiers and legend

Most vendor doc sites were blocked by the egress proxy (see "Gaps"). I therefore used the strongest primary sources that were reachable:

| Code | Source | Reliability |
|---|---|---|
| **DISC** | Google API Discovery documents fetched live on 2026-10-03 from `https://<svc>.googleapis.com/$discovery/rest?version=<v>` (revisions 20260923 to 20261002). Covers Search Console, GA4 Data, GBP Account Mgmt, Business Info, Performance, Places (New), Gemini (generativelanguage v1beta). | Primary, machine-generated, exact field names and enums |
| **ANTH** | `platform.claude.com/docs/...` pages fetched live (web-search-tool, server-tools, tool-reference, models) | Primary |
| **OAI-SPEC** | `raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml` | Primary (official OpenAPI spec) |
| **PPLX-SDK** | `raw.githubusercontent.com/perplexityai/perplexity-py/main/src/perplexity/types/...` (Stainless-generated from Perplexity's OpenAPI) | Primary-derived |
| **DFS-SDK** | `raw.githubusercontent.com/dataforseo/PythonClient/master/dataforseo_client/models/...` (generated from DataForSEO OpenAPI) | Primary-derived |
| **PW-DOCS** | `raw.githubusercontent.com/microsoft/playwright/main/docs/src/...` | Primary |
| **PW-TEST** | My own empirical tests, Playwright 1.63.0 (Python) + Chromium 141 headless shell and Chromium 1194 build, scripts in the scratchpad `pwtest/` dir | Empirical (this environment) |
| **GCLOUD** | `gcloud` 530.0.0 `--help` run locally | Primary |
| **RSA-TEST** | Stdlib RS256 signer tested byte-for-byte against `openssl dgst -sha256 -sign` | Empirical |
| **WS** | WebSearch result snippets (Google docs pages appear as search results but cannot be fetched) | Secondary; flagged |

Confidence tags: **VERIFIED** (primary source or my own test), **LIKELY** (consistent secondary evidence or strong prior, not seen in a primary source), **UNVERIFIED** (do not hardcode; confirm with a live call).

Global note for every Google adapter: all `*.googleapis.com` hosts respond to unauthenticated probes from this sandbox (401/403 JSON), so the paths below were smoke-tested for existence (VERIFIED, DISC + probe), but no authenticated call could be made.

---

## 1. Google Places API (New): Text Search and Place Details

### 1.1 Endpoints (VERIFIED, DISC `places.v1.json`)

| Op | Method + URL |
|---|---|
| Text Search | `POST https://places.googleapis.com/v1/places:searchText` |
| Place Details | `GET https://places.googleapis.com/v1/places/{PLACE_ID}` (resource name `places/{id}`; optional query `languageCode`, `regionCode`, `sessionToken`) |
| Nearby Search | `POST https://places.googleapis.com/v1/places:searchNearby` |

**Auth headers (VERIFIED by probe + DISC):** `X-Goog-Api-Key: <key>` (or an OAuth bearer token; unauthenticated returns 403 `PERMISSION_DENIED` "Method doesn't allow unregistered callers"). **`X-Goog-FieldMask` is mandatory** (comma list, no spaces; for Text Search each field is prefixed `places.`; include `nextPageToken` if paginating). `Content-Type: application/json`.

### 1.2 Minimal Text Search request (VERIFIED field names, DISC)

```json
{
  "textQuery": "emergency plumber in Leeds",
  "languageCode": "en-GB",
  "regionCode": "GB",
  "pageSize": 20,
  "locationBias": {"circle": {"center": {"latitude": 53.8008, "longitude": -1.5491}, "radius": 5000.0}}
}
```

| Request field | Facts (all VERIFIED, DISC) |
|---|---|
| `textQuery` | required string |
| `languageCode` | BCP-47 (`en`, `en-GB`); unrecognised means any language, English preferred |
| `regionCode` | CLDR 2-letter (`GB`, `US`); 3-digit codes unsupported; affects display and "applicable law" |
| `pageSize` | 1..20 (default 20; above 20 is clamped; negative is `INVALID_ARGUMENT`). `maxResultCount` is deprecated and ignored when `pageSize` is given |
| `pageToken` | from response `nextPageToken`; all other params must match the first call, else `INVALID_ARGUMENT` |
| `locationBias` | `circle{center{latitude,longitude},radius}` or `rectangle{low{...},high{...}}`; radius 0.0..50000.0 m |
| `locationRestriction` | **`rectangle` only** (no circle). Mutually exclusive with `locationBias` |
| `includedType` | single type only; `strictTypeFiltering` boolean |
| `minRating` | 0..5 in 0.5 steps (rounded up); `openNow`; `priceLevels[]`; `rankPreference` (`RELEVANCE`/`DISTANCE`) |
| `includePureServiceAreaBusinesses` | **set `true` for plumbers, cleaners etc.**; otherwise service-area businesses without a storefront are omitted, and when included they have no `location`/address fields |

Response (VERIFIED, DISC): `places[]` (Place objects limited to the mask), `nextPageToken`, `searchUri`, `routingSummaries[]`, `contextualContents[]` (experimental). Empty result returns `{}` (no `places` key): code defensively with `.get("places", [])`.

### 1.3 Place Details request

```
GET https://places.googleapis.com/v1/places/ChIJ...?languageCode=en-GB&regionCode=GB
X-Goog-Api-Key: ...
X-Goog-FieldMask: id,displayName,rating,userRatingCount,reviews,primaryType,types,websiteUri,nationalPhoneNumber,regularOpeningHours,location
```
(no `places.` prefix for Details).

### 1.4 Place fields and JSON paths (VERIFIED, DISC `GoogleMapsPlacesV1Place`)

| Need | Mask token | JSON path in each Place | Type |
|---|---|---|---|
| Place ID | `places.id` | `id` (also `name` = `places/{id}`) | string |
| Name | `places.displayName` | `displayName.text`, `displayName.languageCode` | LocalizedText |
| Rating | `places.rating` | `rating` | number 1.0..5.0 |
| Review count | `places.userRatingCount` | `userRatingCount` | integer (reviews with or without text) |
| Reviews | `places.reviews` | `reviews[].rating`, `.text.text`, `.originalText.text`, `.publishTime`, `.relativePublishTimeDescription`, `.authorAttribution.displayName`, `.googleMapsUri`, `.name` | **max 5**, "sorted by relevance" (DISC text) |
| Primary type | `places.primaryType` | `primaryType` (e.g. `plumber`), `primaryTypeDisplayName.text` | string |
| Types | `places.types` | `types[]` | string[] |
| Website | `places.websiteUri` | `websiteUri` | string |
| Phone | `places.nationalPhoneNumber` (or `internationalPhoneNumber`) | same | string |
| Hours | `places.regularOpeningHours` | `regularOpeningHours.periods[]`, `.weekdayDescriptions[]`, `.openNow` | object |
| Location | `places.location` | `location.latitude`, `location.longitude` | doubles |
| Address / maps link | `places.formattedAddress`, `places.googleMapsUri` | same | string |
| Status | `places.businessStatus` | `businessStatus` (OPERATIONAL / CLOSED_TEMPORARILY / CLOSED_PERMANENTLY; enum values LIKELY) | string |
| AI summaries (avoid) | `places.reviewSummary`, `places.generativeSummary` | | Enterprise+Atmosphere |

### 1.5 SKU / pricing (LIKELY; Google docs seen only as WS snippets of `developers.google.com/maps/documentation/places/web-service/usage-and-billing` and `.../billing-and-pricing/pricing`, corroborated by 3 third-party 2026 pricing pages)

Billing is by the **highest-tier field in the mask** per request; the 2025 model replaced the $200 credit with per-SKU monthly free caps.

| Text Search SKU | Fields that trigger it (from Google's field list) | $/1,000 (US list) | Free cap/month |
|---|---|---|---|
| Essentials (IDs Only) | `places.id`, `places.name`, `nextPageToken`, `places.attributions`, moved-place fields | free (LIKELY unlimited) | n/a |
| **Pro** | `displayName`, `formattedAddress`, `location`, `primaryType`, `primaryTypeDisplayName`, `googleMapsUri`, `businessStatus`, `photos`, `addressComponents`, `shortFormattedAddress`, `postalAddress`, `plusCode`, `pureServiceAreaBusiness`, `googleMapsLinks`, `accessibilityOptions` (`types` is listed with Pro in most references: LIKELY) | 32 | 5,000 |
| **Enterprise** | `rating`, `userRatingCount`, `websiteUri`, `nationalPhoneNumber`, `internationalPhoneNumber`, `regularOpeningHours`, `currentOpeningHours`, `priceLevel`, `priceRange` | 35 | 1,000 |
| **Enterprise + Atmosphere** | `reviews`, `reviewSummary`, `generativeSummary`, `editorialSummary`, `neighborhoodSummary`, dineIn/delivery/parking/payment amenity fields | 40 | 1,000 |

Place Details (LIKELY): Essentials $5 (10k free), Pro $17 (5k), Enterprise $20 (1k), Enterprise+Atmosphere $25 (1k). `types`, `location`, `formattedAddress` are Essentials in Details; `displayName`, `primaryType`, `googleMapsUri` are Pro.

**Practical consequence:** the requested competitor/profile mask `rating,userRatingCount,websiteUri,nationalPhoneNumber,regularOpeningHours` is an **Enterprise** request ($35/1k Text Search; one request returns up to 20 places). Adding `reviews` lifts it to **Enterprise+Atmosphere ($40 or $25 Details)**, and returns only 5 reviews, so use reviews only on Place Details for the client's own place (or GBP v4 reviews, section 4, for the full list). Never send `X-Goog-FieldMask: *` (bills top tier).

### 1.6 Quotas, errors, gotchas

- Default quotas are per method per project (LIKELY; WS: platform FAQ says 6,000 QPM for Places). Over quota gives HTTP 429 `RESOURCE_EXHAUSTED`.
- Errors: 400 `INVALID_ARGUMENT` (missing/invalid field mask, bad pageToken, restriction+bias both set); 403 `PERMISSION_DENIED` (key restricted, "Places API (New)" not enabled: it is a different API from legacy "Places API"; billing not enabled); 404 for unknown place ID on Details.
- Text Search paginates with `nextPageToken` (practical cap about 60 results over 3 pages: LIKELY). Token valid only briefly.
- Place IDs can go stale; handle 404 `NOT_FOUND` and re-search.
- `regularOpeningHours` is absent for many businesses: treat as optional. Service-area businesses omit address/location.
- Review text is user-generated content and a prompt-injection vector: never feed raw review text to an LLM as instructions.
- Google policy limits caching Places content (place IDs may be stored indefinitely; most other content has retention limits). Check ToS before persisting reviews. (LIKELY)

---

## 2. Google Search Console API

### 2.1 Endpoints (VERIFIED, DISC `searchconsole.v1.json`, rev 20260923)

| Op | Method + URL |
|---|---|
| Query | `POST https://searchconsole.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query` |
| List sites | `GET https://searchconsole.googleapis.com/webmasters/v3/sites` -> `{"siteEntry":[{"siteUrl":"sc-domain:example.com","permissionLevel":"SITE_OWNER"}]}` |
| URL Inspection | `POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect` |
| Sitemaps list | `GET .../webmasters/v3/sites/{siteUrl}/sitemaps` |

**OAuth scope (VERIFIED):** `https://www.googleapis.com/auth/webmasters.readonly` (read) or `.../auth/webmasters`. Header `Authorization: Bearer <token>`. No API key access.

**siteUrl encoding (LIKELY; consistent with discovery path template and long-standing behaviour):** percent-encode the whole property id including colon and slashes: domain property `sc-domain:example.com` becomes `sc-domain%3Aexample.com`; URL-prefix property `https://www.example.com/` becomes `https%3A%2F%2Fwww.example.com%2F` (trailing slash must match the registered property). In Python: `urllib.parse.quote(site, safe="")`. With httpx, build the URL string yourself; passing an already-encoded string into `httpx.URL` keeps `%3A`, but do not let a library double-encode `%`.

### 2.2 Request body (VERIFIED, DISC `SearchAnalyticsQueryRequest`)

```json
{
  "startDate": "2026-09-01",
  "endDate": "2026-09-28",
  "dimensions": ["QUERY", "PAGE"],
  "type": "WEB",
  "dataState": "FINAL",
  "rowLimit": 25000,
  "startRow": 0,
  "dimensionFilterGroups": [{"groupType": "AND", "filters": [{"dimension": "QUERY", "operator": "CONTAINS", "expression": "plumber"}]}]
}
```

| Field | Facts |
|---|---|
| `startDate`, `endDate` | required, `YYYY-MM-DD`, **Pacific Time**, inclusive |
| `dimensions` enum | `DATE, QUERY, PAGE, COUNTRY, DEVICE, SEARCH_APPEARANCE, HOUR`; `HOUR` requires `dataState: HOURLY_ALL` (10 days only); COUNTRY returns ISO 3166-1 **alpha-3** (`GBR`, `USA`) |
| `type` / `searchType` | `WEB, IMAGE, VIDEO, NEWS, DISCOVER, GOOGLE_NEWS` (default WEB). **No generative-AI value exists** |
| `dataState` | `FINAL` (default; complete only), `ALL` (includes fresh partial data; response `metadata.firstIncompleteDate`), `HOURLY_ALL` |
| `rowLimit` | 1..25,000 (default 1,000); paginate with `startRow` (zero-based) |
| `aggregationType` | `AUTO` / `BY_PROPERTY` / `BY_PAGE` (cannot use `BY_PROPERTY` when grouping/filtering by PAGE) |
| filter `dimension` enum | `QUERY, PAGE, COUNTRY, DEVICE, SEARCH_APPEARANCE`; `operator` enum: `EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS, INCLUDING_REGEX, EXCLUDING_REGEX` (RE2); `groupType` only `AND` |

Enum casing: discovery lists UPPERCASE; the API has historically also accepted lowercase (`"query"`, `"all"`) (LIKELY). Send uppercase as per the discovery doc.

**Response (VERIFIED):** `{"rows":[{"keys":["leeds plumber","https://..."],"clicks":12.0,"impressions":340.0,"ctr":0.035,"position":6.2}],"responseAggregationType":"BY_PAGE","metadata":{"firstIncompleteDate":"2026-09-27"}}`. `keys[]` order equals `dimensions` order. Metrics are doubles. With no dimensions you get one totals row. An empty period returns no `rows` key.

### 2.3 Limits and errors (LIKELY, WS of `developers.google.com/webmaster-tools/limits`)

- Search Analytics: 1,200 QPM per site, 1,200 QPM per user, 40,000 QPM and 30,000,000 QPD per project; plus short/long-term load quotas. Max about 50,000 rows per day per search type per property that the API can surface. Retention 16 months. Final data lags about 2 to 3 days.
- Errors: 401 token expired/missing; 403 "User does not have sufficient permission for site" (identity is not a user on that property, or the property is `sc-domain:` and you queried the URL-prefix form, or vice versa); 400 on bad dimension combination (e.g. `HOUR` without `HOURLY_ALL`); 404 unknown property; 429 `rateLimitExceeded`.
- Gotcha: a domain property and a URL-prefix property for the same site are separate entries in `sites.list`; pick by `permissionLevel` (not `SITE_UNVERIFIED_USER`, which has no data access) and prefer `sc-domain:`.
- Service accounts work only if the SA email is added as a user in the Search Console property UI.

### 2.4 Generative AI report via API

**Not available via API (VERIFIED by absence + LIKELY from WS).** The Search Generative AI performance report launched 2026-06-03 (UK subset first, worldwide by 2026-08-31, data from 2026-05-18, impressions-only: no clicks, CTR or position) is UI/CSV only. The 2026-09-23 discovery doc exposes no new `searchType`, dimension or method for it; WS sources state "not available in the Search Console API, no BigQuery export as of September 2026". Those impressions are also already counted inside the normal Web search-type data, and cannot be separated via the API. Do not build an adapter for it; document that the user must export CSV manually.

---

## 3. GA4 Data API

### 3.1 Endpoint (VERIFIED, DISC `analyticsdata.v1beta.json`, rev 20260930)

`POST https://analyticsdata.googleapis.com/v1beta/properties/{propertyId}:runReport` (`property` must match `^properties/[^/]+$`; the numeric GA4 property id, not the `G-` measurement id). Scope: `https://www.googleapis.com/auth/analytics.readonly`. Other methods: `:batchRunReports`, `:runRealtimeReport`, `:checkCompatibility`, `GET .../properties/{id}/metadata`.

### 3.2 Request body (VERIFIED field names)

```json
{
  "dateRanges": [{"startDate": "28daysAgo", "endDate": "yesterday"}],
  "dimensions": [{"name": "sessionSource"}, {"name": "sessionDefaultChannelGroup"}, {"name": "landingPagePlusQueryString"}],
  "metrics": [{"name": "sessions"}, {"name": "engagedSessions"}, {"name": "keyEvents"}],
  "dimensionFilter": {"filter": {"fieldName": "sessionSource", "stringFilter": {
      "matchType": "PARTIAL_REGEXP", "caseSensitive": false,
      "value": "chatgpt\\.com|chat\\.openai\\.com|perplexity|gemini\\.google\\.com|claude\\.ai|copilot\\.microsoft\\.com"}}},
  "orderBys": [{"metric": {"metricName": "sessions"}, "desc": true}],
  "limit": "10000",
  "returnPropertyQuota": true
}
```

- `StringFilter.matchType` enum (VERIFIED): `EXACT, BEGINS_WITH, ENDS_WITH, CONTAINS, FULL_REGEXP, PARTIAL_REGEXP`. `FULL_REGEXP` must match the entire value; use `PARTIAL_REGEXP` for domains. Regex dialect is RE2. Escape dots (`\\.` in JSON).
- `limit`/`offset` are int64 **strings**; default 10,000 rows, hard max 250,000. `dateRanges[].startDate` accepts `NdaysAgo`, `yesterday`, `today`.
- Dimension and metric names (`sessionSource`, `sessionMedium`, `sessionSourceMedium`, `sessionDefaultChannelGroup`, `sessions`, `engagedSessions`, `totalUsers`, `newUsers`, `keyEvents`): LIKELY (standard GA4 API schema; names are validated server-side with a 400 listing valid names; verify once with `GET .../metadata`). `keyEvents` replaced `conversions` in 2024 (LIKELY).
- Response (VERIFIED): `dimensionHeaders[].name`, `metricHeaders[].{name,type}`, `rows[].dimensionValues[].value`, `rows[].metricValues[].value` (all **strings**), `rowCount`, `propertyQuota`, `metadata`. Map columns by header order. When there is no data `rows` is absent.

### 3.3 AI-source regex and channel group (LIKELY, WS)

Common regex: `chatgpt\.com|chat\.openai\.com|perplexity|gemini\.google\.com|claude\.ai|copilot\.microsoft\.com` (add `bard\.google\.com`, `you\.com`, `deepseek` as needed). Note that **GA4 added a native "AI Assistant" Default Channel Group on 2026-05-13** (wide availability 2026-06-07; session medium `ai-assistant`), reportedly covering ChatGPT, Gemini, DeepSeek, Copilot and Grok, but **not Perplexity or Claude**, which still land in Referral. Older data is not reclassified. So query both `sessionDefaultChannelGroup` (treat value `AI Assistant` as one bucket) and the source regex. Many AI app clicks arrive with no referrer and are bucketed as `(direct)`; ChatGPT often appends `utm_source=chatgpt.com`. Treat the figure as a lower bound.

### 3.4 Quotas (VERIFIED, DISC `PropertyQuota` descriptions)

Standard property: 200,000 tokens/day; 40,000 tokens/hour; 14,000 tokens/hour per project (35% share); 10 concurrent requests; 10 server errors/hour per project; 120 requests/hour that include potentially thresholded dimensions. 360 properties: 10x tokens, 50 concurrent. Most requests cost under 10 tokens. Error shape: 429 `RESOURCE_EXHAUSTED` with message "Exhausted property tokens for a project per hour". 403 `PERMISSION_DENIED` if the identity lacks Viewer on the property or the Google Analytics Data API is not enabled in the calling project. Set `returnPropertyQuota: true` to monitor.

---

## 4. Google Business Profile (GBP) APIs

### 4.1 Endpoints (VERIFIED, DISC)

| API (enable each in Cloud Console) | Call |
|---|---|
| My Business Account Management (`mybusinessaccountmanagement.googleapis.com`) | `GET https://mybusinessaccountmanagement.googleapis.com/v1/accounts` (page size default and max 20) -> `accounts[].{name:"accounts/123", accountName, type: PERSONAL/LOCATION_GROUP/USER_GROUP/ORGANIZATION, role, verificationState, vettedState}` + `nextPageToken` |
| My Business Business Information (`mybusinessbusinessinformation.googleapis.com`) | `GET https://mybusinessbusinessinformation.googleapis.com/v1/accounts/{accountId}/locations?readMask=name,title,storeCode,websiteUri,phoneNumbers,categories,storefrontAddress,metadata&pageSize=100&pageToken=` -> `locations[]`, `nextPageToken`, `totalSize` (only with `filter`). **`readMask` is required.** Page size default 10, max 100 |
| Business Profile Performance (`businessprofileperformance.googleapis.com`) | `GET https://businessprofileperformance.googleapis.com/v1/locations/{locationId}:fetchMultiDailyMetricsTimeSeries?dailyMetrics=CALL_CLICKS&dailyMetrics=WEBSITE_CLICKS&dailyRange.startDate.year=2026&dailyRange.startDate.month=9&dailyRange.startDate.day=1&dailyRange.endDate.year=2026&dailyRange.endDate.month=9&dailyRange.endDate.day=28` |
| Reviews: legacy "Google My Business API v4" (`mybusiness.googleapis.com`) | `GET https://mybusiness.googleapis.com/v4/accounts/{accountId}/locations/{locationId}/reviews?pageSize=50&orderBy=updateTime%20desc` |

**Scope (LIKELY; discovery docs list no scopes for these services):** `https://www.googleapis.com/auth/business.manage` (one scope covers all four).

**Location resource (VERIFIED):** `name` (`locations/{id}`), `title`, `storeCode`, `websiteUri`, `phoneNumbers.{primaryPhone,additionalPhones}`, `categories.{primaryCategory{name,displayName},additionalCategories[]}`, `storefrontAddress` (PostalAddress: `addressLines[], locality, administrativeArea, postalCode, regionCode`), `latlng`, `regularHours`, `profile.description`, `serviceArea`, `serviceItems`, `metadata.{placeId, mapsUri, newReviewUri, hasVoiceOfMerchant, hasGoogleUpdated, hasPendingEdits}`. **`metadata.placeId` bridges to Places API** (use it to fetch rating/count without GBP quota).

### 4.2 Performance API metrics (VERIFIED enum, DISC `DailyMetric`)

`BUSINESS_IMPRESSIONS_DESKTOP_MAPS`, `BUSINESS_IMPRESSIONS_DESKTOP_SEARCH`, `BUSINESS_IMPRESSIONS_MOBILE_MAPS`, `BUSINESS_IMPRESSIONS_MOBILE_SEARCH` (search impressions are split by surface and device: sum four), `BUSINESS_CONVERSATIONS`, `BUSINESS_DIRECTION_REQUESTS`, `CALL_CLICKS`, `WEBSITE_CLICKS`, `BUSINESS_BOOKINGS`, `BUSINESS_FOOD_ORDERS`, `BUSINESS_FOOD_MENU_CLICKS`. `dailyMetrics` is a repeated query param (repeat the key).

Response (VERIFIED): `multiDailyMetricTimeSeries[].dailyMetricTimeSeries[].{dailyMetric, dailySubEntityType?, timeSeries.datedValues[].{date:{year,month,day}, value}}`. `value` is an int64 **string and is omitted when zero**: default to 0. Daily data only (no hourly); date arguments are split into `year/month/day` query params, not ISO strings. Monthly search terms: `GET .../v1/locations/{id}/searchkeywords/impressions/monthly?monthlyRange.startMonth.year=..&monthlyRange.startMonth.month=..&monthlyRange.endMonth.year=..&monthlyRange.endMonth.month=..` -> `searchKeywordsCounts[].{searchKeyword, insightsValue.{value|threshold}}` (a `threshold` means "below this number").

### 4.3 Reviews v4: status in 2026

**Still available (LIKELY, WS + route probe).** The path `mybusiness.googleapis.com/v4/accounts/x/locations/y/reviews` exists (returns 401 `CREDENTIALS_MISSING` unauthenticated: VERIFIED probe), no discovery document is published for v4 any more (404), and a 2026 changelog snippet lists new review fields shipped on this surface (`reviewReplyState` 2026-04-01, `policyViolation` 2026-07-01, `reviewReplyUrl` 2026-07-24). The legacy `mybusiness.googleapis.com` **Q&A API was shut down 2025-11-03** (my probe of the `mybusinessqanda` discovery doc returned 404): do not build Q&A support. Some blogs wrongly claim v4 reviews died in April 2022: that applied to other v4 endpoints (insights etc.).

Review list response (LIKELY, long-standing docs): `reviews[]` with `reviewId`, `name`, `reviewer.{displayName,profilePhotoUrl,isAnonymous}`, `starRating` (**enum string** `ONE`..`FIVE`, not a number), `comment`, `createTime`, `updateTime`, `reviewReply.{comment,updateTime}`; top level `averageRating`, `totalReviewCount`, `nextPageToken`. `pageSize` max 50; `orderBy` `rating`, `rating desc`, `updateTime desc`.

### 4.4 Access approval and "quota 0" behaviour (LIKELY, WS of Google's "Prerequisites" and several 2026 forum threads)

- A new Cloud project has **quota 0 for all GBP APIs**. Every call fails with HTTP **429 `RESOURCE_EXHAUSTED`** (message contains `Quota exceeded for quota metric ... limit ... per minute` and a limit value of 0), even though the API is enabled and the token is valid. Enabling the API does not fix it.
- Fix: submit the GBP API access request form (`support.google.com/business/contact/api_default`) with project number, business website and use case. Reported prerequisites: a **verified** GBP that is at least **60 days old** and an active website; reviews take days to about 14 days. After approval, default **300 QPM** per project across the APIs.
- Approval is **per Cloud project**: the OAuth client and the API calls must come from the approved project (when using user ADC with a client-id file, quota is billed to that client's project; add `X-Goog-User-Project` if the platform asks).
- `mybusiness.googleapis.com` (v4 reviews) is a separate API to enable and may show a separate "can't be enabled / pending" state (WS forum thread).
- The caller must be an owner/manager of the location (or the SA/agency account must have been invited). Service accounts are impractical for GBP; use user OAuth.
- 403 `PERMISSION_DENIED` `SERVICE_DISABLED` = API not enabled; 403 "does not have permission" = identity is not a manager of the account.
- Design implication: make every GBP adapter optional, detect 429 with quota 0 and report "GBP API access not approved for this project" rather than retrying. Use Places API (section 1) as the zero-approval fallback for rating, count and 5 reviews.

---

## 5. OAuth for a local CLI without google-auth libraries

**Recommendation (ordered by safety and simplicity):**

1. **Bearer token from the environment (default, simplest, SAFE).** Adapter reads `GOOGLE_ACCESS_TOKEN` (and optional `GOOGLE_QUOTA_PROJECT`, sent as `X-Goog-User-Project`). No secrets handled by the agent; tokens last about 1 hour; never write them to disk or logs. Correct gcloud usage (**VERIFIED, local gcloud 530.0.0 help**): `gcloud auth application-default print-access-token --scopes=...` only accepts scopes in `[openid, userinfo.email, cloud-platform, sqlservice.login]` **or those chosen at login**. So the scopes must be granted at login with your own OAuth client:
   ```
   gcloud auth application-default login --client-id-file=client_secret.json \
     --scopes=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/business.manage
   export GOOGLE_ACCESS_TOKEN=$(gcloud auth application-default print-access-token)
   ```
   Without `--client-id-file`, gcloud's built-in client cannot obtain these sensitive non-Cloud scopes (the help text says a custom client ID is needed "for applications outside of Google Cloud Platform"). Plain `gcloud auth print-access-token` has no `--scopes` flag in this version (so the brief's `... print-access-token --scopes=...` only works with the `application-default` variant), and a default-login token carries only cloud-platform scopes, so Search Console/GA4/GBP would return 403 "insufficient authentication scopes".
2. **Refresh-token flow (optional, still stdlib + httpx).** Desktop-app OAuth client, loopback redirect `http://127.0.0.1:<port>` captured with `http.server`, PKCE, exchange at `POST https://oauth2.googleapis.com/token`, store refresh token in a 0600 file, refresh with `grant_type=refresh_token`. Gotchas: a consent screen in "Testing" status expires refresh tokens after 7 days; sensitive scopes need app verification for production use (LIKELY).
3. **Service-account JWT bearer (only for Search Console and GA4).** Build the JWT (`iss`=client_email, `scope`=space-joined scopes, `aud`=`https://oauth2.googleapis.com/token`, `iat`, `exp`<=3600), sign RS256, `POST https://oauth2.googleapis.com/token` form `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=<jwt>` -> `{"access_token","expires_in","token_type"}`. The SA email must be added as a user on the GSC property / GA4 property. Not workable for GBP.

**Can stdlib do RS256? No, not through any supported API:** `hashlib`/`hmac`/`ssl` expose no RSA signing. Options:

| Option | Verdict |
|---|---|
| Pure-stdlib RSA PKCS#1 v1.5 using Python big ints | **Works** (RSA-TEST: matches `openssl` byte-for-byte, 2048-bit). About 35 lines: DER-parse the PKCS#8 key from the SA JSON `private_key`, build EMSA-PKCS1-v1_5 (`SHA256` DigestInfo prefix `3031300d060960864801650304020105000420` + digest), `pow(m, d, n)`. Not constant-time and has no blinding; acceptable for a local single-user CLI signing only its own tokens, but flag it in code comments and never use it on untrusted input |
| `openssl dgst -sha256 -sign key.pem` via `subprocess` | Simple and battle-tested; requires the `openssl` binary (write the key to a 0600 temp file) |
| `cryptography` (pyca) | Cleanest; high star count (UNVERIFIED, check against the >5k rule); PyJWT also needs it for RS256 |
| `google-auth` | Avoid: likely below the star threshold (UNVERIFIED) and pulls transitive deps |

Recommended: ship tier 1 only for v1; add tier 3 behind an optional extra using the tested stdlib signer (reference implementation in `scratchpad/rsatest/rs.py`).

---

## 6. DataForSEO and SerpApi

### 6.1 DataForSEO conventions (VERIFIED from DFS-SDK + WS)

- Base `https://api.dataforseo.com`. Auth: HTTP **Basic** `Authorization: Basic base64(login:password)` (API login/password from dashboard, not the account login). `Content-Type: application/json`.
- **Request body is a JSON array of task objects** `[{...}]`. Live endpoints take one task per request (LIKELY). Response envelope: `{"status_code":20000,"status_message":"Ok.","cost":0.002,"tasks_count":1,"tasks_error":0,"tasks":[{"id","status_code":20000,"cost","result_count","path","data","result":[{...}]}]}` (VERIFIED field names). Always check **both** the top-level and `tasks[0].status_code` (20000 = OK); HTTP 200 can carry task-level errors (error code meanings: UNVERIFIED).
- Rate limit: 2,000 requests/minute general (WS), `X-RateLimit-Limit` response header; Google Ads keyword live endpoints much lower (12/min).

### 6.2 Google Maps SERP live advanced (VERIFIED)

`POST https://api.dataforseo.com/v3/serp/google/maps/live/advanced`

```json
[{
  "keyword": "emergency plumber",
  "location_coordinate": "53.8008,-1.5491,14z",
  "language_code": "en",
  "se_domain": "google.co.uk",
  "device": "desktop",
  "depth": 20,
  "search_this_area": true
}]
```

| Param | Facts (DFS-SDK descriptions) |
|---|---|
| `keyword` | required, up to 700 chars |
| location (one of) | `location_code` (e.g. 2840 US; UK code 2826 is LIKELY), `location_name` (`London,England,United Kingdom`), or `location_coordinate` = `"lat,lng,zoom"` with `z` suffix; zoom 3z..21z, default **17z**; max 7 decimals |
| `language_code` / `language_name` | required one of; `en` |
| `depth` | default 100, max 700; **billed per SERP of up to 100 results** (so `depth` <= 100 costs the same) |
| `device` / `os` | `desktop` (windows/macos) or `mobile` (android/ios); **mobile returns only 20 results** |
| `se_domain` | optional `google.co.uk` |
| `search_this_area` | default true; false lets results spill beyond the viewport |
| `search_places` | default true; set false for local-intent keywords to avoid place-mode interference |

Response path: `tasks[0].result[0]` has `keyword, se_domain, location_code, language_code, check_url, datetime, item_types, se_results_count, items_count, items[]`. Each `items[]` element with `type == "maps_search"` (also `maps_paid_item`) has (VERIFIED):

`rank_group` (int), `rank_absolute` (int), `domain`, `title`, `url`, `rating.value` (float), `rating.votes_count` (int), `rating.rating_max`, `rating_distribution` (`{"1":n,...}`), `address`, `address_info`, `place_id`, `cid` (string; usable with their Reviews API), `feature_id`, `phone`, `category`, `additional_categories[]`, `category_ids[]`, `work_hours`, `latitude`, `longitude`, `is_claimed` (bool), `total_photos`, `main_image`, `snippet`, `price_level`, `local_justifications[]`, `is_directory_item`. Any field may be null: use `.get`. `rating` may be null when no reviews. Match the client by `domain` or `place_id`; position is `rank_group` (rank among `maps_search` items).

Pricing (LIKELY, WS): about **$0.002 per live SERP** ($0.0006 standard queue, $0.0012 priority queue), per 100 results; $50 minimum top-up; check the response `cost` field after each call to reconcile.

### 6.3 Google Organic SERP live advanced with AI Overview (VERIFIED, DFS-SDK)

`POST https://api.dataforseo.com/v3/serp/google/organic/live/advanced`

```json
[{"keyword": "emergency plumber leeds", "location_name": "Leeds,England,United Kingdom", "language_code": "en",
  "device": "mobile", "depth": 10, "load_async_ai_overview": true}]
```

- `load_async_ai_overview: true` is required to get `ai_overview` items that load asynchronously (false returns only cached AIO). **Extra $0.002 per request; refunded automatically when the SERP has no AIO** (DFS-SDK text). `depth` default 10, max 200 (billed per 10 results). `location_coordinate`, `se_domain`, `target`, `stop_crawl_on_match` also exist.
- Response: `tasks[0].result[0].item_types[]` (look for `"ai_overview"`), `items[]`. The AIO element (`type == "ai_overview"`): `rank_group`, `rank_absolute`, `page`, `position` (left/right), `xpath`, `asynchronous_ai_overview` (bool), **`markdown`** (full text), `items[]` (sub-elements `ai_overview_element`: `title`, `text`, `markdown`, `links[]`, `images[]`, `references[]`), and **`references[]`** at element level with `type "ai_overview_reference"`, `source`, `domain`, `url`, `title`, `text`. Citation check: any `references[].domain` equal to the client domain, searching both the top-level `references` and the nested `items[].references`. Organic hits have `type == "organic"` with `rank_group`, `rank_absolute`, `domain`, `url`, `title`. Also present: `knowledge_graph_ai_overview_item` type (do not confuse).
- Base price LIKELY $0.002 per 10-result live SERP (WS).

### 6.4 SerpApi (brief; LIKELY, WS only, `serpapi.com` not fetchable)

- Auth: `api_key` query parameter. Maps: `GET https://serpapi.com/search.json?engine=google_maps&q=emergency+plumber&ll=@53.8008,-1.5491,14z&type=search&hl=en&gl=uk&api_key=KEY` -> `local_results[]` with `position`, `title`, `place_id`, `data_id`, `rating`, `reviews` (count), `type`, `address`, `phone`, `gps_coordinates.{latitude,longitude}` (field names LIKELY; `website` presence UNVERIFIED).
- AI Overview: `engine=google` returns `ai_overview`; sometimes only `{page_token, serpapi_link}`, requiring a follow-up `engine=google_ai_overview&page_token=...` **within 4 minutes**; the follow-up returns `text_blocks[]` and `references[]`. Per-search pricing: UNVERIFIED.

---

## 7. Google Search Status Dashboard

**Machine-readable endpoints: could not fetch (host blocked); the following are LIKELY by analogy with Google's other status dashboards (Cloud/Workspace/Ads share the same engine) and by the page's own "JSON History / JSON Product Catalog / RSS" footer links (WS):**

| Resource | URL (LIKELY) |
|---|---|
| Incident history (JSON) | `https://status.search.google.com/incidents.json` (schema at `.../incidents.schema.json`) |
| Product catalog (JSON) | `https://status.search.google.com/products.json` |
| Atom feed | `https://status.search.google.com/en/feed.atom` |
| Human page | `https://status.search.google.com/summary`; Ranking product history `https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history` (product id VERIFIED from a WS result titled "History for Ranking") |

Schema fields (UNVERIFIED for this host, LIKELY from the Cloud status schema, consistent with the field names in the brief): `id`, `number`, `begin`, `created`, `end` (absent/null while ongoing), `modified`, `external_desc`, `updates[]` (`created`, `modified`, `when`, `text`, `status`), `most_recent_update` (`{when, status, text}`), `status_impact` (values like `SERVICE_INFORMATION`, `SERVICE_DISRUPTION`, `SERVICE_OUTAGE`, `AVAILABLE`), `severity`, `service_key`, `service_name`, `affected_products[]` (`{title, id}`), `uri`. Timestamps are ISO-8601 with offset (PT). The history window is the previous 365 days.

**Detecting an in-progress ranking/spam/core update (robust heuristic that tolerates field uncertainty):** fetch `incidents.json`; keep incidents where (a) any `affected_products[].id == "rGHU1u87FJnkP6W2GwMi"` or title equals `Ranking`; (b) `end` is missing/null/empty **or** `most_recent_update.status` is not a resolved/available value; (c) text of `external_desc` + titles matches `/(core|spam|helpful content|reviews|local)\s+update/i`. Also treat `begin` within the last 14 days as "volatile window" because Google says rollouts take up to about two weeks even after an `end` is posted late. Fail open: if the fetch or parse fails, report "status unknown" instead of "no update". Example for context: the **September 2026 spam update began 2026-09-24 09:15 PDT and was still listed in progress on 2026-09-29** (WS; may still be rolling out on 2026-10-03, so the agent should caveat any rank-change interpretation).

---

## 8. LLM web-search REST contracts

### 8.1 Anthropic Messages API web search (VERIFIED, ANTH)

`POST https://api.anthropic.com/v1/messages`; headers `x-api-key: $ANTHROPIC_API_KEY`, `anthropic-version: 2023-06-01`, `content-type: application/json`. **No beta header needed** for web search.

**Tool type strings (VERIFIED, tool-reference page):** `web_search_20250305` (basic, default caller `direct`, ZDR-eligible), `web_search_20260209` (adds dynamic filtering via code execution; `allowed_callers` defaults to `["code_execution_20260120"]`; not ZDR by default), `web_search_20260318` (adds `response_inclusion`). **Recommendation for a raw-REST adapter: `web_search_20250305`**: simplest response (direct calls only, no code-execution blocks). If you use `_20260209`/`_20260318` set `"allowed_callers": ["direct"]`, else the response includes code_execution blocks and nested `caller` fields.

```json
{
  "model": "claude-sonnet-5-5",
  "max_tokens": 2048,
  "messages": [{"role": "user", "content": "Best emergency plumbers in Leeds right now? Cite sources."}],
  "tools": [{
    "type": "web_search_20250305", "name": "web_search", "max_uses": 5,
    "allowed_domains": ["checkatrade.com", "yell.com"],
    "user_location": {"type": "approximate", "city": "Leeds", "region": "England", "country": "GB", "timezone": "Europe/London"}
  }]
}
```

- `max_uses` int (exceeding yields a result error `max_uses_exceeded`, still HTTP 200). `allowed_domains` **or** `blocked_domains`, never both (400). Bare domains, no scheme; subdomains included; paths allowed for search (`example.com/blog`); wildcards only inside the path; ASCII only (homograph warning). `user_location`: `type` must be `"approximate"`; at least one of `city`, `region`, `country` (ISO 3166-1 alpha-2, **`GB` not `UK`**; unsupported code gives 400), `timezone` (IANA). Org-level restrictions from the Console intersect with request-level lists; if web search is disabled for the org the request fails 400 `invalid_request_error`.
- **Response content blocks (VERIFIED):** `text` (may include preamble), `server_tool_use {id:"srvtoolu_...", name:"web_search", input:{query}}`, `web_search_tool_result {tool_use_id, content:[{type:"web_search_result", url, title, page_age, encrypted_content}]}` (on error `content` is a single `{type:"web_search_tool_result_error", error_code}`: `too_many_requests`, `invalid_tool_input`, `max_uses_exceeded`, `query_too_long`, `request_too_large`, `unavailable`; still HTTP 200, not billed), then `text` blocks with `citations[] {type:"web_search_result_location", url, title, cited_text (<=150 chars), encrypted_index}`. Citation fields do not count toward tokens.
- **Usage (VERIFIED):** `usage.server_tool_use.web_search_requests` (int) alongside `input_tokens`, `output_tokens`, cache fields.
- **Pricing (VERIFIED):** **$10 per 1,000 searches** plus normal token cost; errors not billed; same price in the Batch API.
- `stop_reason: "pause_turn"`: re-send messages with the assistant content appended **unchanged** and the same tools; cap continuations. Multi-turn: echo content blocks back exactly (including `encrypted_content`) or you get 400.
- **Models:** `claude-opus-5-5` is used in the official examples for all three versions (VERIFIED). `claude-sonnet-5-5` (released 2026-09-28): the model page does not list a tools matrix, and dynamic filtering is documented for "Claude 4.6 and later" (so Sonnet 5.5 qualifies); basic web search on Sonnet 5.5 is LIKELY supported (no exclusion documented). Gotchas for both 5.5 models (VERIFIED, model pages): forced tool use returns an error (so do not set `tool_choice` to force `web_search`; use prompt instructions); `temperature`/`top_p`/`top_k` non-default returns 400 on Sonnet 5.5; adaptive thinking is on (Opus 5.5 always) and text between tool calls may arrive inside `thinking` blocks: **extract only `type == "text"` blocks and ignore `thinking`/`server_tool_use`**; set `max_tokens` generously.

### 8.2 OpenAI Responses API (VERIFIED, OAI-SPEC)

`POST https://api.openai.com/v1/responses`, `Authorization: Bearer $OPENAI_API_KEY`.

```json
{"model": "<current model>", "input": "Best emergency plumbers in Leeds?",
 "tools": [{"type": "web_search",
            "user_location": {"type": "approximate", "country": "GB", "city": "Leeds", "region": "England", "timezone": "Europe/London"},
            "search_context_size": "medium",
            "filters": {"allowed_domains": ["yell.com"]}}],
 "include": ["web_search_call.action.sources"]}
```

- Tool type `web_search` (alias `web_search_2025_08_26`); the older `web_search_preview` / `web_search_preview_2025_03_11` still exist. `user_location` fields: `type:"approximate"`, `country` (2-letter), `region`, `city`, `timezone`. **If `user_location` is omitted it defaults to the United States**: always send GB for UK clients. Also `external_web_access` (bool, false = cache-only), `filters.allowed_domains[]` (subdomains allowed), `search_context_size` `low|medium|high`.
- Output walk (no SDK `output_text` helper in raw REST): `output[]` items: `{type:"web_search_call", id, status, action:{type:"search", queries[], query(deprecated), sources:[{type:"url", url}]}}` (sources only if requested via `include`; action may also be `open_page` or `find_in_page`), then `{type:"message", role:"assistant", content:[{type:"output_text", text, annotations:[{type:"url_citation", url, title, start_index, end_index}]}]}`. Concatenate `output_text` blocks; indices are character offsets into that block's `text`.
- Pricing (LIKELY, WS): $10 per 1,000 calls for `web_search` plus search-content tokens at model rates; `web_search_preview` on non-reasoning models $25 per 1,000 calls with free search tokens. Which models support the tool (and effort settings that disable it): UNVERIFIED.

### 8.3 Perplexity Sonar (VERIFIED field names from PPLX-SDK; docs host blocked)

`POST https://api.perplexity.ai/chat/completions` (base URL LIKELY), `Authorization: Bearer pplx-...`. Models `sonar`, `sonar-pro`, `sonar-reasoning-pro`, `sonar-deep-research` (LIKELY).

```json
{"model": "sonar", "messages": [{"role": "user", "content": "Best emergency plumbers in Leeds?"}],
 "web_search_options": {"search_context_size": "low",
   "user_location": {"country": "GB", "region": "England", "city": "Leeds", "latitude": 53.8008, "longitude": -1.5491}},
 "search_domain_filter": ["yell.com"], "search_recency_filter": "month"}
```

- `web_search_options`: `search_context_size` (`low|medium|high`), `search_type` (`fast|pro|auto`), `user_location` `{city, country, latitude, longitude, region}`. WS: latitude/longitude must be accompanied by `country`; `country` is ISO alpha-2. The SDK also exposes older top-level `country`, `latitude`, `longitude`. Other VERIFIED params: `search_domain_filter`, `search_recency_filter` (`hour|day|week|month|year`), `search_mode` (`web|academic|sec`), `disable_search`, `return_images`, `return_related_questions`, `num_search_results`, `search_language_filter`.
- Response (VERIFIED `StreamChunk`/completion): `id, model, created, object`, `choices[0].message.content`, **`citations: [url,...]`** (flat URL list, positional with `[n]` markers in text), **`search_results: [{title, url, date, last_updated, snippet, source}]`**, `usage {prompt_tokens, completion_tokens, total_tokens, citation_tokens, reasoning_tokens, num_search_queries, search_context_size, cost{input_tokens_cost, output_tokens_cost, request_cost, search_queries_cost, total_cost}}`. Prefer `search_results` (richer); `citations` may be deprecated: handle absence.
- Pricing (LIKELY, WS): tokens ($1/$1 per M for Sonar; $3/$15 Sonar Pro) plus a per-request fee of about $5 to $14 per 1,000 requests by context size; read `usage.cost.total_cost` instead of computing.

### 8.4 Gemini API grounding (VERIFIED field names, DISC `generativelanguage.v1beta.json`)

`POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`, header `x-goog-api-key: $GEMINI_API_KEY`. JSON keys are accepted in camelCase and snake_case (docs show `google_search`; discovery uses `googleSearch`).

Search grounding:
```json
{"contents": [{"role": "user", "parts": [{"text": "Best emergency plumbers in Leeds?"}]}], "tools": [{"google_search": {}}]}
```
Maps grounding (location via toolConfig, language optional):
```json
{"contents": [{"role": "user", "parts": [{"text": "Emergency plumbers near me"}]}],
 "tools": [{"google_maps": {}}],
 "toolConfig": {"retrievalConfig": {"latLng": {"latitude": 53.8008, "longitude": -1.5491}, "languageCode": "en-GB"}}}
```
- Answer: `candidates[0].content.parts[].text`. Grounding: **`candidates[0].groundingMetadata`** = `{webSearchQueries[], groundingChunks[], groundingSupports[], searchEntryPoint.renderedContent, googleMapsWidgetContextToken}`.
- `groundingChunks[]` is a union: `{web:{uri, title}}` for search (uri is typically a `vertexaisearch.cloud.google.com/grounding-api-redirect/...` redirect, title usually the source domain: LIKELY; resolve the redirect with a safe GET, no JS, to get the real URL) or `{maps:{uri, title, placeId ("places/{id}"), text, placeAnswerSources.reviewSnippets[{reviewId, googleMapsUri, title}]}}`. `groundingSupports[]`: `{segment:{partIndex, startIndex, endIndex, text}, groundingChunkIndices[], confidenceScores[]}` (indices in **bytes**). `GoogleMaps.enableWidget` optional.
- Pricing (LIKELY, WS of Google pricing page): Gemini 3.x models: 5,000 grounded queries/month free (shared), then **$14 per 1,000 search queries** the model actually runs (Search and Maps); Gemini 2.5: $35 per 1,000 grounded prompts (Search), $25 per 1,000 (Maps). Maps+Search combined only in US and India (WS); UK availability of Maps grounding: UNVERIFIED, test at runtime and degrade gracefully. Model ids change often: make the model configurable (WS shows `gemini-3.5-flash` in a REST example).

---

## 9. Playwright (Python): SSRF-safe rendering

### 9.1 What route interception actually sees (PW-DOCS + PW-TEST, Playwright 1.63.0, Chromium 141; all VERIFIED unless noted)

I ran a local two-server harness (server A public-looking, server B standing in for an internal target) with `context.route("**/*", handler)` that logged every call.

| Request kind | Seen by `context.route`? | Evidence |
|---|---|---|
| Top-level navigation, HTTP | Yes | handler called for `/redir`, `/meta`, `/page` |
| **HTTP 302 redirect hop (document or fetch)** | **NO, and the browser still connects to the redirect target** | Handler fired only for the original URL; server B logged hits to `/secret` and `/secret-fetch-redirect`. PW-DOCS: "a request and its redirects [are] a single unit. The handler is called once". Fulfilling with a 3xx status is also followed without re-routing |
| `<meta refresh>` / JS navigation | Yes (it is a fresh navigation) | handler fired for the target |
| Subresources (img, script, fetch/XHR, iframe document) | Yes | `/img`, `/frame`, `/fetch` logged |
| `data:` and `blob:` fetches | No (no handler call) | `fetch("data:...")` and blob fetch succeeded unseen; harmless by themselves (no network), but a `data:` top-level page's later subresource fetches are routed |
| WebSocket (`ws://`, `wss://`) | **No** via `route`; only `context.route_web_socket()` sees it | `ws://` URL appeared only in the WS handler; without `route_web_socket` assume open |
| Service worker | With `service_workers="allow"` the SW registered and later requests were relayed; PW-DOCS say routes are bypassed for requests handled by an SW; with `"block"` registration is refused ("Service Worker registration blocked by Playwright") | Always set `service_workers="block"` |
| Request headers like Host/Cookie | Not reliably present in handler (set by network stack) | PW-DOCS |

**Conclusion: a route handler alone is not an SSRF control.** Known bypasses: (1) HTTP redirects to loopback/metadata/RFC1918 (confirmed); (2) DNS rebinding / TOCTOU (a hostname that resolves public when you check and private when Chromium connects); (3) WebSocket; (4) service workers; (5) IPv6 and encoded forms (`::ffff:127.0.0.1`, `0x7f.1`, `[::1]`, decimal IPs, trailing-dot hosts), which your validator must normalise through `ipaddress` after `getaddrinfo`; (6) `file:`/`ftp:`/`chrome:` schemes if you pass user URLs straight to `goto`.

### 9.2 Recommended pattern (defence in depth)

1. **Network-layer control (the real boundary).** Launch Chromium with `proxy={"server": "http://127.0.0.1:<port>"}` pointing at a small local forward proxy you control that (a) accepts CONNECT/HTTP only for `80/443`, (b) resolves DNS itself, (c) rejects any address that is not `ipaddress.ip_address(x).is_global` (loopback, private, link-local incl. `169.254.169.254`, CGNAT `100.64/10`, multicast, reserved, IPv4-mapped IPv6), and (d) **connects to the exact IP it validated** (pinning defeats rebinding). Add `--proxy-bypass-list=<-loopback>` so Chromium does not implicitly bypass the proxy for loopback (LIKELY; not tested). In a deployment where an egress firewall exists, also deny RFC1918 and metadata at the firewall.
2. **In-browser guard (catches scheme and redirect issues early):** a catch-all `context.route("**/*", handler)` that allows only `http`/`https`, then **follows redirects itself** with `route.fetch(url=..., max_redirects=0)`, validating each hop (scheme, resolved IPs) up to a cap, and finally `route.fulfill(response=r)`. TESTED: with this pattern server B was never contacted (`BLOCK http://127.0.0.1:<B>/secret`, B's hit log empty). Caveat: `route.fetch` uses Playwright's own client and re-resolves DNS, so it is still subject to rebinding; keep layer 1.
3. `context = browser.new_context(service_workers="block", accept_downloads=False, permissions=[], java_script_enabled=<True only if you need rendering>, bypass_csp=False)`; install a `context.route_web_socket("**/*", handler)` that does not call `connect_to_server()` (this makes the socket a local mock, so nothing leaves the machine; in my run the page saw `ws open` against the mock). One of my first runs hung when the WS handler was an inline lambda calling `ws.close()` in the sync API (cause not isolated), so use a plain `def` handler and test it.
4. Resource limits: per-page `timeout`, cap total requests (count in the handler), cap response bytes (`route.fetch` response `.body()` length), one context per URL, close it afterwards, run Chromium unprivileged and with the default sandbox on (my tests used `--no-sandbox` only because this sandbox is root).
5. Never expose the page content as trusted instructions to an LLM (prompt injection).

### 9.3 Headless Chromium with a custom CA / proxy (PW-TEST, this environment)

- Playwright 1.63 expects browser revision 1243; this box only has Chromium 1194 under `/opt/pw-browsers` (`PLAYWRIGHT_BROWSERS_PATH`), so pass `executable_path=` (or run `playwright install`, which the proxy may block).
- Chromium on Linux does **not** read `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE`. In this sandbox, TLS through the egress proxy failed with `ERR_CERT_AUTHORITY_INVALID` even with the pre-seeded `~/.pki/nssdb` (both the headless shell and full Chromium). **Working recipe (tested; both `raw.githubusercontent.com` and `platform.claude.com` loaded with status 200):**
  ```python
  spki = base64(sha256(DER SubjectPublicKeyInfo of /root/.ccr/agent-proxy-ca.crt))  # openssl x509 -pubkey | openssl pkey -pubin -outform DER | openssl dgst -sha256 -binary | base64
  browser = p.chromium.launch(proxy={"server": os.environ["HTTPS_PROXY"]},
      args=[f"--ignore-certificate-errors-spki-list={spki}", "--disable-background-networking"])
  ```
  This trusts only chains containing that CA key (much narrower than `ignore_https_errors=True`, which disables verification and must not be used). Alternative: import the CA into `$HOME/.pki/nssdb` with `certutil -A` (`certutil` is not installed here; the bundle has 127 certs and must be split, one per import).
- `--disable-background-networking` avoids Chromium's background calls to google.com that the egress policy rejects (and that stalled my first run).
- Do not mix this with the sandbox's `NO_PROXY` list: loopback, `169.254.0.0/16` and RFC1918 are in the proxy's no-proxy set, meaning they are reachable directly from tools that honour it. Another reason the SSRF filter must be explicit.

---

## Gaps / could not verify

Blocked by the egress proxy (WebFetch/curl returned EGRESS_BLOCKED or CONNECT 403): `developers.google.com` (Places, Search Console, GA4, GBP, status-dashboard docs, Search Central blog), `ai.google.dev`, `docs.dataforseo.com`, `dataforseo.com`, `docs.perplexity.ai`, `platform.openai.com`, `status.search.google.com` (incl. `incidents.json`, `feed.atom`, `products.json`), `status.cloud.google.com`, `playwright.dev`, `serpapi.com`, `searchenginejournal.com`, `neilpatel.com`, `openplacesapi.com`, `deepline.com`. Specific gaps:

1. **Places SKU table and prices** are from WS snippets of Google pages plus third-party pages, not fetched. Re-check Text Search `types` SKU (Pro vs Essentials), exact current $ and free caps, and the 60-result pagination cap before showing cost estimates to users.
2. **Search Status Dashboard**: URLs and schema (`status_impact` values, `end` semantics, whether `affected_products[].id` equals the Ranking id) are inferred, not read. First implementation task: do one live fetch and snapshot the schema into a fixture; keep the "fail open: status unknown" behaviour.
3. **GBP**: scope string `business.manage`, v4 review field list/enum casing and the access-form URL/60-day rule come from WS and long-standing docs; no discovery doc exists for v4. Exact quota-0 error text is paraphrased. Whether a given agency account qualifies cannot be checked offline.
4. **GA4**: dimension/metric name list (`keyEvents` etc.) not read from the metadata endpoint; the "AI Assistant" default channel (2026-05-13) and its member list rely on several WS articles.
5. **DataForSEO**: pricing (Maps live $0.002 per 100 results) and error code meanings are from WS; UK `location_code` 2826 and one-task-per-live-request are LIKELY. Request/response field names are from the official generated client and are solid.
6. **SerpApi**: WS only; field lists for `local_results` and pricing UNVERIFIED.
7. **OpenAI**: pricing from WS; supported models and any model restrictions on `web_search` UNVERIFIED. Perplexity: base URL, model names, pricing from WS; field names are solid (SDK).
8. **Anthropic**: Sonnet 5.5 + web search not explicitly stated on its page (Opus 5.5 is in official examples). Rate limits for web search are shown only in the Console.
9. **Gemini**: UK/EEA availability of Maps grounding, exact `web.title` semantics and current model IDs not verified; pricing from WS.
10. **Playwright**: tests used Playwright 1.63.0 with Chromium 141 on Linux only; redirect/ServiceWorker behaviour may differ by version (PW-DOCS state routes may not see SW-handled requests). `<-loopback>` proxy-bypass behaviour and `route_web_socket` default-open semantics were not tested end to end. Stdlib RSA signer was tested for correctness, not side-channel resistance.
11. Dependency star counts (httpx, pyca/cryptography, google-auth) were not checked.

Artifacts produced during research (scratchpad): `disc/*.json` (Google discovery docs), `disc/openai.yaml`, `pwtest/t.py`, `pwtest/t2.py`, `pwtest/t3.py` (Playwright experiments), `rsatest/rs.py` (stdlib RS256 signer).
