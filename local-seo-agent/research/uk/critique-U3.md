# Critique of U3-api-contracts.md (UK Critic Agent 3, 2026-10-03)

Method: I re-fetched the Google Discovery docs (Places, Search Console, GA4 Data, GBP Business Information / Performance / Account Management, Gemini v1beta), the OpenAI OpenAPI YAML, the Perplexity and DataForSEO SDK sources on raw.githubusercontent.com, and the Anthropic web-search / server-tools / models pages (the `.md` variants of platform.claude.com are reachable). I ran three Playwright 1.63.0 experiments against Chromium 1194 (`--no-sandbox`) with local servers on 127.0.0.1. `developers.google.com`, `status.search.google.com` and `docs.perplexity.ai` are still blocked, so I used WebSearch snippets for those.

Overall: the report is accurate on almost everything machine-verifiable. I found no wrong endpoint or field name in the Google, OpenAI, Anthropic, Perplexity or DataForSEO contracts. The errors are one contradicted claim (GA4 channel members), one likely-wrong claim (status-dashboard retention), several omissions that would bite an implementer, and one untested pattern that fails (dead proxy plus `route.fetch`).

## Claim-by-claim spot checks (23 items)

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | Places `POST https://places.googleapis.com/v1/places:searchText`; `X-Goog-FieldMask` required | CONFIRMED | Discovery `v1/places:searchText` POST. Unauthenticated probe gave 403 `PERMISSION_DENIED` "unregistered callers". |
| 2 | `pageSize` 1..20, default 20, >20 clamped, negative is `INVALID_ARGUMENT`; `maxResultCount` deprecated | CONFIRMED | Discovery description is word for word as stated. |
| 3 | `locationBias` takes circle or rectangle; `locationRestriction` takes rectangle only; mutually exclusive | CONFIRMED | `LocationBias` has `rectangle` and `circle`; `LocationRestriction` has `rectangle` only. Radius range 0..50000 not re-checked (the Circle schema only shows `radius: double`). |
| 4 | `includePureServiceAreaBusinesses`: SABs omitted unless true; no `location`, `plus_code` when included | CONFIRMED | Discovery text matches. |
| 5 | `reviews` max 5, "sorted by relevance" | CONFIRMED | Discovery `Place.reviews` text. |
| 6 | Text Search SKU: Pro (`displayName`, `types`...), Enterprise (rating, userRatingCount, websiteUri, phone, hours), Ent+Atmosphere (reviews, generativeSummary...) | CONFIRMED on tiers, UNVERIFIABLE on $ and free caps | The WebSearch snippet of the Google text-search page lists Pro as displayName/formattedAddress/location/types and Enterprise as rating/userRatingCount/websiteUri/nationalPhoneNumber/regularOpeningHours. It says "billed at the highest SKU in the mask". Google Atmosphere fields (e.g. `generativeSummary`, `parkingOptions`) are listed with `reviews` as Enterprise+Atmosphere. Prices are not seen in any primary source. |
| 7 | GSC `POST https://searchconsole.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query` | CONFIRMED | Discovery `rootUrl` is searchconsole.googleapis.com; path as stated. |
| 8 | GSC enums, `rowLimit` 1..25000, `dataState` | CONFIRMED | `dimensions`: DATE, QUERY, PAGE, COUNTRY, DEVICE, SEARCH_APPEARANCE, HOUR. `rowLimit` default 1000, max 25000. `dataState`: FINAL, ALL, HOURLY_ALL (plus `DATA_STATE_UNSPECIFIED`). Filter operators as stated. |
| 9 | No API for the Generative AI report | CONFIRMED (by absence) | `searchType`/`type` enum is only WEB, IMAGE, VIDEO, NEWS, DISCOVER, GOOGLE_NEWS. No AI dimension or method. |
| 10 | GA4 `POST analyticsdata.googleapis.com/v1beta/properties/{id}:runReport`; `PARTIAL_REGEXP`; `limit` is a string, max 250,000 | CONFIRMED | Discovery path `v1beta/{+property}:runReport`; `StringFilter.matchType` includes PARTIAL_REGEXP; `limit` is int64 string. Scopes `analytics` and `analytics.readonly`. |
| 11 | GA4 native "AI Assistant" channel, 2026-05-13 | CONFIRMED on date and existence, WRONG on member list | See correction C2. |
| 12 | GBP Business Information `GET v1/accounts/{id}/locations?readMask=`; page size default 10, max 100 | CONFIRMED | Discovery `accounts.locations.list`: "Default value is 10... maximum page size is 100". `readMask` is documented "Required" (the discovery flag is not set, so omitting it returns 400 at runtime). |
| 13 | Account Management `GET v1/accounts`, page size default and max 20 | CONFIRMED | Discovery text. |
| 14 | Performance `fetchMultiDailyMetricsTimeSeries`: repeated `dailyMetrics`, `dailyRange.startDate.{year,month,day}` | CONFIRMED | All eight query params present as integers; `dailyMetrics` is `repeated: true` with the 11-value enum listed. |
| 15 | v4 reviews still alive, `starRating` enum strings | UNVERIFIABLE (consistent) | v4 has no discovery doc (both URLs 404, as the researcher found). WebSearch confirms the guidance "reviews use `mybusiness.googleapis.com/v4`". The enum strings `ONE`..`FIVE` match long-standing docs. |
| 16 | New project has quota 0, calls fail HTTP 429 until approval | CONFIRMED (secondary) | Multiple community and vendor threads report `quota_limit_value: "0"` and 429. The "60 days verified" rule stays UNVERIFIED. |
| 17 | DataForSEO Maps live advanced path, `location_coordinate` `"lat,lng,zoom z"`, 3z..21z, default 17z | CONFIRMED | SDK request model: "'latitude,longitude,zoom' format... default 17z... min 3z, max 21z, up to 7 decimals". `depth` default 100, max 700, billed per 100. |
| 18 | Maps item fields `rank_group`, `rating.value`, `rating.votes_count`, `place_id`, `domain`, `phone` | CONFIRMED | `SerpApiMapsSearchElementItem` has all of these plus `cid`, `feature_id`, `is_claimed`, `work_hours`, `category`. `RatingInfo` has `value`, `votes_count`, `rating_max`. Envelope has `status_code`, `tasks_count`, `tasks_error`, `cost`. |
| 19 | Organic live advanced `load_async_ai_overview`; AIO item shape | CONFIRMED | Param description matches (extra $0.002, refunded if no AIO). AIO item has `markdown`, `asynchronous_ai_overview`, `items[]`, `references[]`; each reference has `source`, `domain`, `url`, `title`, `text`. |
| 20 | Anthropic tool type strings, `user_location`, `GB` alpha-2, block types, citations, `usage.server_tool_use.web_search_requests`, $10 per 1k, `pause_turn` | CONFIRMED | The fetched web-search-tool page matches all of it. `claude-sonnet-5-5` is a valid API ID (models overview). Sonnet 5.5 page: forced tool use returns an error; non-default `temperature`/`top_p`/`top_k` return 400. |
| 21 | Sonnet 5.5 supports web search | UNVERIFIABLE (downgrade to LIKELY) | Every web-search example uses `claude-opus-5-5`. No Sonnet 5.5 exclusion was found, but no inclusion either. |
| 22 | OpenAI `web_search` tool shape, US default when `user_location` omitted, `url_citation`, `include=["web_search_call.action.sources"]` | CONFIRMED | Spec: "If omitted or null, defaults to the United States". `url_citation` has `start_index`, `end_index`, `title`, `url`. `IncludeEnum` contains `web_search_call.action.sources`. |
| 23 | Perplexity `web_search_options.user_location`, `search_results`/`citations` | CONFIRMED | `WebSearchOptions` has `search_context_size`, `search_type`, `user_location`, `image_results_enhanced_relevance`. `StreamChunk` has `citations: List[str]` and `search_results[{title,url,date,last_updated,snippet,source}]`. Top-level `country`, `latitude`, `longitude` also exist. |
| 24 | Gemini `google_search` / `google_maps`, `toolConfig.retrievalConfig.latLng`, `groundingChunks` union | CONFIRMED but incomplete | `RetrievalConfig {latLng, languageCode}`; `GoogleMaps {enableWidget}`. The `GroundingChunk` union has FOUR members: `web`, `maps`, `image`, `retrievedContext`, not two. |
| 25 | Search Status Dashboard `incidents.json` and schema | UNVERIFIABLE | Host blocked. WebSearch snippets confirm a "JSON History" link and a schema on `status.search.google.com`, but not the exact path or fields. |

## Playwright experiments (claim 10): all observed

(a) CONFIRMED. A catch-all `context.route` that fulfills every request itself still cannot stop redirect hops. A fulfilled response `status=302, Location: http://127.0.0.1:<B>/fulfilled-302` was followed by Chromium. Server B logged the hit, and the page displayed B's body ("SECRET-B"). The same happened for a `fetch(..., {redirect:'follow'})` from the page. The route handler's log showed only the original URLs (`/page`, `/redir`, `/redir-f`), never `/fulfilled-302`. So "fulfil everything from a body" is not a boundary, because a fulfilled 3xx pivots to any host.

(b) CONFIRMED. With no `route_web_socket`, `new WebSocket("ws://127.0.0.1:<port>")` opened, completed the handshake and received a frame; the raw server logged `GET /x`. With `route_web_socket` installed (handler never calling `connect_to_server`), the page saw `open` but the server saw nothing (mock).

(c) CONFIRMED, with a caveat that matters. Launching with `proxy={'server':'http://127.0.0.1:9','bypass':'<-loopback>'}`:
- Fulfilled routes still rendered ("fulfilled").
- The 302 hop to 127.0.0.1 failed with `net::ERR_PROXY_CONNECTION_FAILED`, and B logged zero hits.
- `fetch` of an unrouted/redirected URL failed with `TypeError: Failed to fetch`.
- The WebSocket to the IP literal ended in `error` with no server contact.
- A dead proxy without the bypass key behaved identically in this build, so Chromium did not implicitly bypass loopback here. Still set `<-loopback>` explicitly.
- Caveat 1: with `route_web_socket` installed the same dead-proxy run reports the mock WS as "open" (expected, it is a mock).
- Caveat 2 (new, contradicts the implied design): `route.fetch(max_redirects=0)` inherits the launch proxy. With the dead proxy, `route.fetch` itself failed with `Route.fetch: connect ECONNREFUSED 127.0.0.1:9`. So a "dead proxy" backstop only works for fully offline or fulfilled content; for real rendering the proxy must be a live validating proxy, and the `route.fetch` hop-validation layer is then redundant-but-useful. The report's two-layer recommendation is sound; the "dead/validating proxy" shorthand the brief used is not safe as a combined design.

## Corrections the builder MUST apply (prioritised)

1. **Playwright/SSRF (C1).** Do not rely on route handlers, fulfilled 3xx bodies or "fulfil everything" as the boundary. Required: (i) a live validating forward proxy that resolves DNS itself, rejects non-global IPs and pins the connect IP; (ii) `proxy={'server': ..., 'bypass': '<-loopback>'}`; (iii) `service_workers='block'`; (iv) `route_web_socket` that never connects; (v) a route handler that uses `route.fetch(max_redirects=0)`, re-validates every `Location`, caps hops, and never fulfils with a 3xx status. Pick layer 1 and 2 together: a dead proxy breaks `route.fetch`.
2. **GA4 AI channel members (C2).** The report says the native channel covers "ChatGPT, Gemini, DeepSeek, Copilot and Grok but not Perplexity or Claude". Multiple 2026 sources (SEO Sherpa, Delante, GA Agency snippets) say ChatGPT, Gemini and Claude ARE recognised, Perplexity is NOT, and Google has not published the full list. Downgrade to LIKELY and drop the member list from code; keep querying both `sessionDefaultChannelGroup = "AI Assistant"` and the source regex (for Perplexity and everything else), and de-duplicate when summing the two.
3. **DataForSEO `url` field (C3).** In `maps_search`, `url` is the "search URL with refinement parameters", NOT the business website. There is no website field. Use `domain` for site matching and `place_id` or `cid` for identity. The report lists `url` among usable fields without this warning.
4. **Gemini chunk union (C4).** Handle `groundingChunks[]` items with `web`, `maps`, `image` or `retrievedContext`; skip unknown keys rather than assuming web or maps.
5. **OpenAI location (C5).** To avoid the US fallback pass a `user_location` with GB fields; if you have no location, send `{"type":"approximate"}` with no fields (the spec says that explicitly avoids the US default). `filters` supports only `allowed_domains` (no blocked list) on `web_search`; `web_search_preview` is a separate tool type.
6. **Anthropic (C6).** Keep `web_search_20250305` for the raw adapter. When echoing the assistant message for `pause_turn`, send ALL blocks back unchanged, including `thinking` blocks, `server_tool_use` and `encrypted_content`. The report's "extract only `text` blocks" applies to reading the answer, not to the echo. Mark Sonnet 5.5 + web search LIKELY, with a configurable model and a startup smoke test; Opus 5.5 is the documented example model.
7. **Status dashboard (C7).** Retention conflict: the report says the history window is 365 days; a search snippet of Google's help page says issues and updates are available for 5 years. Treat the window as unknown, filter by date client-side, and keep the fail-open "status unknown". The report is right that the first task is a live fetch to snapshot a fixture; the path `incidents.json` stays UNVERIFIED.
8. **Search Console body (C8).** Discovery has BOTH `type` and `searchType` on the request (same enum). The report's body uses `type`; Google's historical docs use `searchType`. Send one, add a fixture test, and fall back to the other if the API returns 400.
9. **Places pricing (C9).** Keep tiers as stated (confirmed), but never present $ figures or free caps to users as facts (UNVERIFIED). Read cost from your own request counter, not hard-coded constants.
10. **GBP.** Treat `mybusiness.googleapis.com/v4` reviews as best-effort with no schema contract (no discovery doc); parse defensively and map `ONE..FIVE` with a default for unknown or unspecified values. Send `readMask` every time. `value` omitted for zero (as stated): default to 0.

## Missing items an implementer needs

- **Auth header per API (one table):** Places `X-Goog-Api-Key` + `X-Goog-FieldMask`; GSC/GA4/GBP `Authorization: Bearer` (+ optional `X-Goog-User-Project`); Gemini `x-goog-api-key`; Anthropic `x-api-key` + `anthropic-version: 2023-06-01`; OpenAI and Perplexity `Authorization: Bearer`; DataForSEO HTTP Basic. The report states them scattered; consolidate.
- **Common retry policy:** 429/5xx with exponential backoff and `Retry-After`; no retry on 400/401/403; GBP 429 with quota 0 must NOT retry (the report says this for GBP only). Set explicit httpx timeouts per vendor (LLM search calls need 60-120 s) and cap `pause_turn` continuations.
- **Google error envelope:** `{"error":{"code","message","status","details"}}`; branch on `status` (`RESOURCE_EXHAUSTED`, `PERMISSION_DENIED`, `INVALID_ARGUMENT`) rather than message text.
- **Pagination summary:** Places `nextPageToken` must also be in the field mask; GSC `startRow`; GA4 `offset`+`limit`; GBP `pageToken`; DataForSEO none (live).
- **Cost ledger:** record `usage.server_tool_use.web_search_requests` (Anthropic), `usage.cost.total_cost` (Perplexity), DataForSEO top-level `cost`, and a per-request SKU counter for Places.
- **Gemini grounding redirects:** resolving `vertexaisearch.cloud.google.com/grounding-api-redirect/...` is an outbound fetch; it must go through the same SSRF-safe fetcher.
- **Untrusted content:** Places reviews, search snippets, AIO text and rendered pages are prompt-injection inputs; the report notes it for reviews only.
- **GSC specifics:** the 403 when a property is `sc-domain:` vs URL-prefix is covered; add that dates are Pacific time and the last 2-3 days are partial when `dataState=ALL`.
- **Places ToS:** caching limits are flagged LIKELY; keep that caveat in any persistence code.

## Verdict per section

| Section | Verdict |
|---|---|
| 1 Places (New) | Accurate. Tiers confirmed; prices and the 60-result cap stay LIKELY. |
| 2 Search Console | Accurate. Fix `type` vs `searchType` (C8). |
| 3 GA4 | Accurate on API; WRONG on AI-channel members (C2). |
| 4 GBP | Accurate on three APIs; v4 reviews and 60-day rule remain secondary-sourced. |
| 5 OAuth | Not re-tested (outside brief); no issues spotted. |
| 6 DataForSEO | Accurate; add `url` warning (C3). SerpApi still unverified. |
| 7 Status Dashboard | UNVERIFIABLE; retention claim probably wrong (C7). |
| 8 LLM search | Anthropic, OpenAI, Perplexity accurate; Gemini union incomplete (C4); Sonnet 5.5 support unconfirmed. |
| 9 Playwright | Redirect and WebSocket claims confirmed by my runs; dead-proxy shorthand is unsafe with `route.fetch` (C1). |
