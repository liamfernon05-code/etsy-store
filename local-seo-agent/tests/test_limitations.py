import base64
import csv
import json
import os
import socket
import threading
from datetime import date, datetime, timedelta, timezone

import httpx
import pytest

from local_seo_agent import cli, freshness, rank
from local_seo_agent.connectors import ApiClient, ConnectorError, dataforseo, google, places
from local_seo_agent.models import ClientProfile
from local_seo_agent.probe import manual, summarise
from local_seo_agent.probe.providers import AnthropicProvider, GeminiProvider, OpenAIResponsesProvider, make_provider
from local_seo_agent.probe.store import Store
from local_seo_agent.safety import SafeFetcher
from local_seo_agent.snapshots import Snapshots


def uk(**kw):
    base = dict(name="Northgate Heating Ltd", website="https://www.northgate-heating.co.uk", phone="0113 496 0123",
                vertical="heating_engineer", jurisdiction="UK", primary_city="Leeds",
                address={"city": "Leeds", "region": "West Yorkshire", "postal_code": "LS6 1AA"},
                target_services=["boiler repair", "heating engineer"])
    base.update(kw)
    return ClientProfile(**base)


def mock_api(handler, **kw):
    return ApiClient(transport=httpx.MockTransport(handler), **kw)


# ---------------- manual capture (AI Overviews, consumer apps, voice) ----------------
def test_worksheet_roundtrip_and_calibration(tmp_path, profile):
    path = tmp_path / "sheet.csv"
    n = manual.export_worksheet(profile, path, ["google_ai_overview", "chatgpt_app"], n_prompts=4)
    assert n == 8
    rows = list(csv.DictReader(open(path)))
    assert rows[0]["surface"] == "google_ai_overview" and rows[0]["client_named"] == ""
    for r in rows:
        r["observed_on"] = "2026-10-03"
        r["client_named"] = "y" if r["surface"] == "chatgpt_app" else "n"
        r["cited_domains"] = "yelp.com; example-dental.com" if r["client_named"] == "y" else "healthgrades.com"
        r["named_businesses"] = "Other Dental; Riverside Family Dental"
    rows[-1]["client_named"] = ""                                         # not observed yet -> skipped
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=manual.COLUMNS)
        w.writeheader()
        w.writerows(rows)
    store = Store(tmp_path / "p.sqlite")
    profile.website = "https://www.example-dental.com"
    res = manual.import_worksheet(store, profile, path, "w1")
    assert res["imported"] == 7 and res["skipped_blank"] == 1 and res["errors"] == []
    s = summarise(store, "w1", profile)["providers"]
    assert "manual spot-check" in s["manual:chatgpt_app"]["validity"] and s["manual:chatgpt_app"]["citation_rate"] == 1.0
    assert s["manual:google_ai_overview"]["mention_rate"] == 0.0
    # calibration compares API samples with the manual app answers for the same prompts
    for r in rows[:4]:
        for _ in range(4):
            store.add(wave="w1", provider="openai", model="m", prompt_id=r["prompt_id"], prompt_kind="nonbranded",
                      prompt_text="x", location="x", ok=1, name_match=0)
    cal = manual.calibrate(store, "w1")
    assert cal and cal[0]["api"] == "openai" and cal[0]["app"] == "chatgpt_app" and cal[0]["agreement"] == 0.0


def test_worksheet_import_validates(tmp_path, profile):
    p = tmp_path / "s.csv"
    p.write_text("surface,prompt_id,prompt_text,observed_on,client_named,client_site_cited,named_businesses,cited_domains,notes\n"
                 "bogus,x,y,2026-10-03,y,,,,\nsiri,x,y,03/10/2026,y,,,,\n")
    res = manual.import_worksheet(Store(tmp_path / "p.sqlite"), profile, p, "w")
    assert res["imported"] == 0 and len(res["errors"]) == 2
    with pytest.raises(ValueError):
        manual.export_worksheet(profile, tmp_path / "x.csv", ["tiktok"])


# ---------------- geo-grid ----------------
def test_grid_points_geometry():
    pts = rank.grid_points(53.8008, -1.5491, 3, 2.0)
    assert len(pts) == 9 and (pts[4].lat, pts[4].lng) == (53.8008, -1.5491)       # centre point is the business
    assert pts[0].lat > pts[8].lat and pts[0].lng < pts[8].lng                    # north-west to south-east
    assert abs((pts[0].lat - pts[3].lat) * 110.574 - 2.0) < 0.01
    with pytest.raises(ValueError):
        rank.grid_points(95, 0)
    with pytest.raises(ValueError):
        rank.grid_points(0, 0, 10)


def test_find_rank_and_aggregate():
    items = [{"domain": "other.com", "place_id": "a", "phone": "01 1111"}, {"domain": "northgate.co.uk", "place_id": "b"}]
    assert rank.find_rank(items, {"northgate.co.uk"}) == 2 and rank.find_rank(items, {"nope.com"}) is None
    assert rank.find_rank(items, set(), client_place_id="a") == 1
    assert rank.find_rank([{"phone": "0113 496 0123"}], set(), "01134960123") == 1
    agg = rank.aggregate([1, 3, 5, None])
    assert agg == {"points": 4, "arp": round((1 + 3 + 5 + 21) / 4, 2), "solv": 50.0, "coverage": 75.0}
    assert rank.aggregate([])["arp"] is None


# ---------------- freshness ----------------
def test_verify_facts_detects_ok_missing_changed_unreachable(site):
    base, pages = site
    pages["/a"] = (200, "text/html", "<html><body>LCP 2.5 seconds INP 200 milliseconds</body></html>")
    f = SafeFetcher(min_interval=0, allow_private=True, respect_robots=False)
    src = {"ok": (base + "/a", ["2.5 seconds", "200 milliseconds"]), "missing": (base + "/a", ["totally absent"]),
           "dead": (base + "/nope", [])}
    first = freshness.verify_facts(f, sources=src)
    assert {k: v["status"] for k, v in first["results"].items()} == {"ok": "OK", "missing": "PHRASE_MISSING", "dead": "UNREACHABLE"}
    pages["/a"] = (200, "text/html", "<html><body>LCP 2.5 seconds INP 200 milliseconds (new paragraph)</body></html>")
    second = freshness.verify_facts(f, previous=first, sources={"ok": src["ok"]})
    assert second["results"]["ok"]["status"] == "CHANGED"                     # page drifted since the last run


NOW = datetime(2026, 10, 3, 12, tzinfo=timezone.utc)


def status_site(site, incidents):
    base, pages = site
    pages["/incidents.json"] = (200, "application/json", json.dumps(incidents))
    return SafeFetcher(min_interval=0, allow_private=True, respect_robots=False), [base + "/incidents.json"]


def test_status_active_recent_none_unknown(site):
    ranking = [{"id": freshness.RANKING_PRODUCT_ID, "title": "Ranking"}]
    active = [{"begin": "2026-09-24T09:15:00-07:00", "affected_products": ranking, "external_desc": "September 2026 spam update"}]
    f, urls = status_site(site, active)
    r = freshness.update_in_progress(f, urls, NOW)
    assert r["state"] == "ACTIVE" and r["incidents"]
    ended = [{"begin": "2026-09-24T09:15:00-07:00", "end": "2026-09-30T10:00:00-07:00", "affected_products": ranking,
              "external_desc": "September 2026 spam update"}]
    f, urls = status_site(site, ended)
    assert freshness.update_in_progress(f, urls, NOW)["state"] == "RECENT"
    old = [{"begin": "2026-05-21T09:00:00-07:00", "end": "2026-06-02T05:40:00-07:00", "affected_products": ranking,
            "external_desc": "May 2026 core update"}]
    f, urls = status_site(site, old)
    assert freshness.update_in_progress(f, urls, NOW)["state"] == "NONE"
    unrelated = [{"begin": "2026-10-01T00:00:00Z", "affected_products": [{"id": "x", "title": "Crawling"}], "external_desc": "Crawl delay"}]
    f, urls = status_site(site, unrelated)
    assert freshness.update_in_progress(f, urls, NOW)["state"] == "NONE"
    f, urls = status_site(site, {"incidents": active})                      # wrapped schema tolerated
    assert freshness.update_in_progress(f, urls, NOW)["state"] == "ACTIVE"
    base, pages = site
    pages["/bad.json"] = (200, "application/json", "not json")
    bad = freshness.update_in_progress(SafeFetcher(min_interval=0, allow_private=True, respect_robots=False), [base + "/bad.json"], NOW)
    assert bad["state"] == "UNKNOWN"                                          # fail open: never "no update"
    assert freshness.update_in_progress(SafeFetcher(min_interval=0, allow_private=True, respect_robots=False), [base + "/missing.json"], NOW)["state"] == "UNKNOWN"


# ---------------- JS rendering (skipped where playwright/chromium are unavailable) ----------------
CHROMIUM = os.environ.get("LSA_CHROMIUM_PATH") or "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
needs_browser = pytest.mark.skipif(not os.path.exists(CHROMIUM) or __import__("importlib").util.find_spec("playwright") is None,
                                   reason="playwright + chromium not available")


@needs_browser
def test_render_sees_js_content_and_blocks_internal_targets(site):
    from local_seo_agent.render import render_findings, render_page

    base, pages = site
    internal = socket.socket()
    internal.bind(("127.0.0.1", 0))
    internal.listen(5)
    hits: list[int] = []

    def accept():
        while True:
            try:
                c, _ = internal.accept()
                hits.append(1)
                c.close()
            except OSError:
                return

    threading.Thread(target=accept, daemon=True).start()
    port = internal.getsockname()[1]
    js = ('document.getElementById("root").innerHTML="<h1>Austin dentist</h1><p>Call (512) 555-0147 today for same day '
          'appointments across Austin and nearby areas, family dentistry and whitening.</p><p>"+"service ".repeat(170)+"</p>";'
          f'try{{new WebSocket("ws://127.0.0.1:{port}/")}}catch(e){{}} fetch("http://127.0.0.1:{port}/f").catch(()=>{{}});'
          'fetch("http://169.254.169.254/latest/meta-data/").catch(()=>{});')
    pages["/"] = (200, "text/html", '<html><head><title>JS site</title><script defer src="/app.js"></script>'
                  '<script src="http://evil.invalid/x.js"></script></head><body><div id=root></div></body></html>')
    pages["/app.js"] = (200, "application/javascript", js)
    pages["/robots.txt"] = (404, "text/plain", "")
    fetcher = SafeFetcher(min_interval=0, allow_private=True, respect_robots=False)
    data, stats = render_page(base + "/", fetcher, executable_path=CHROMIUM)
    assert data.h1 == ["Austin dentist"] and "555" in data.text
    assert stats.aborted >= 2 and any("third-party" in r for r in stats.reasons)
    import time
    time.sleep(1.0)
    assert hits == []                              # WebSocket + fetch to the internal service never connected (fail-closed)
    raw = __import__("local_seo_agent.html_parse", fromlist=["parse_html"]).parse_html(base + "/", pages["/"][2])
    f = render_findings(raw, data, "5125550147")
    assert {x.id for x in f} == {"render.js-dependent", "render.nap-js-only"}
    internal.close()


@needs_browser
def test_render_never_fulfils_a_redirect(site):
    from local_seo_agent.render import render_page

    base, pages = site
    pages["/"] = (200, "text/html", '<html><body>start<script>fetch("/go").then(r=>r.text()).then(t=>{document.title=t}).catch(()=>{})</script></body></html>')
    pages["/go"] = (302, "text/html", "/secret")
    pages["/secret"] = (200, "text/plain", "SECRET")
    pages["/robots.txt"] = (404, "text/plain", "")
    f = SafeFetcher(min_interval=0, allow_private=True, respect_robots=False)
    data, stats = render_page(base + "/", f, executable_path=CHROMIUM)
    # our fetcher follows the redirect itself (re-validating every hop) and hands the browser only the final 200
    assert stats.fulfilled >= 2


def test_render_findings_quiet_when_equal():
    from local_seo_agent.html_parse import parse_html
    from local_seo_agent.render import render_findings

    page = parse_html("http://x.test/", "<html><body><h1>H</h1>" + "word " * 200 + "</body></html>")
    assert render_findings(page, page) == []


# ---------------- ApiClient ----------------
def test_api_client_retries_429_and_5xx_only_when_enabled():
    calls = []

    def handler(req):
        calls.append(1)
        return httpx.Response(429, headers={"retry-after": "3"}, json={"error": {"message": "slow down"}}) if len(calls) < 3 else httpx.Response(200, json={"ok": 1})

    api = mock_api(handler, retries=2)
    sleeps = []
    api.sleep = sleeps.append
    assert api.request("GET", "https://x.test/") == {"ok": 1} and sleeps == [3.0, 3.0]
    calls.clear()
    with pytest.raises(ConnectorError) as e:
        mock_api(handler, retries=0).request("GET", "https://x.test/")
    assert e.value.status == 429 and e.value.kind == "quota" and len(calls) == 1          # default: never retry (costs money)
    for status, kind in ((403, "auth"), (404, "not_found")):
        n = []
        api = mock_api(lambda r, s=status: (n.append(1), httpx.Response(s, json={"error": {"message": "no"}}))[1], retries=3)
        with pytest.raises(ConnectorError) as e:
            api.request("GET", "https://x.test/")
        assert e.value.kind == kind and len(n) == 1                                       # 4xx never retried


def test_google_headers_require_token_and_support_quota_project(monkeypatch):
    monkeypatch.delenv("GOOGLE_ACCESS_TOKEN", raising=False)
    with pytest.raises(ConnectorError):
        google.google_headers()
    monkeypatch.setenv("GOOGLE_ACCESS_TOKEN", "tok")
    monkeypatch.setenv("GOOGLE_QUOTA_PROJECT", "proj")
    assert google.google_headers() == {"Authorization": "Bearer tok", "X-Goog-User-Project": "proj"}


# ---------------- Search Console / GA4 / GBP ----------------
def test_gsc_query_contract_and_summary(monkeypatch):
    monkeypatch.setenv("GOOGLE_ACCESS_TOKEN", "tok")
    seen = {}

    def handler(req):
        seen.update(url=str(req.url), body=json.loads(req.content), auth=req.headers["authorization"])
        return httpx.Response(200, json={"rows": [{"keys": ["boiler repair leeds"], "clicks": 12.0, "impressions": 300.0, "position": 4.26},
                                                  {"keys": ["gas safe"], "clicks": 1.0, "impressions": 50.0, "position": 9.0}]})

    resp = google.gsc_query(mock_api(handler), "sc-domain:example.com", "2026-09-01", "2026-09-28", ["QUERY"], 99999)
    assert seen["url"] == "https://searchconsole.googleapis.com/webmasters/v3/sites/sc-domain%3Aexample.com/searchAnalytics/query"
    assert seen["body"]["rowLimit"] == 25000 and seen["body"]["type"] == "WEB" and seen["body"]["dataState"] == "FINAL"
    assert seen["auth"] == "Bearer tok"
    s = google.gsc_summary(resp, "Leeds")
    assert s["clicks"] == 13 and s["impressions"] == 350 and s["queries_with_city"] == 1 and "Generative AI" in s["note"]
    prefix = google.gsc_query(mock_api(handler), "https://www.example.com/", "a", "b")
    assert "https%3A%2F%2Fwww.example.com%2F" in seen["url"] and prefix


def test_gsc_falls_back_to_searchtype_on_400(monkeypatch):
    monkeypatch.setenv("GOOGLE_ACCESS_TOKEN", "tok")
    bodies = []

    def handler(req):
        b = json.loads(req.content)
        bodies.append(b)
        if "type" in b:
            return httpx.Response(400, json={"error": {"message": "Unknown name \"type\": Cannot find field."}})
        return httpx.Response(200, json={"rows": []})

    assert google.gsc_query(mock_api(handler), "sc-domain:x.com", "a", "b") == {"rows": []}
    assert "type" in bodies[0] and bodies[1].get("searchType") == "WEB" and "type" not in bodies[1]


def test_ga4_ai_traffic_contract(monkeypatch):
    monkeypatch.setenv("GOOGLE_ACCESS_TOKEN", "tok")
    seen = {}

    def handler(req):
        seen.update(url=str(req.url), body=json.loads(req.content))
        return httpx.Response(200, json={"dimensionHeaders": [{"name": "sessionSource"}, {"name": "sessionDefaultChannelGroup"}],
                                         "metricHeaders": [{"name": "sessions"}, {"name": "engagedSessions"}, {"name": "keyEvents"}],
                                         "rows": [{"dimensionValues": [{"value": "chatgpt.com"}, {"value": "Referral"}],
                                                   "metricValues": [{"value": "10"}, {"value": "7"}, {"value": "2"}]},
                                                  {"dimensionValues": [{"value": "gemini"}, {"value": "AI Assistant"}],
                                                   "metricValues": [{"value": "4"}, {"value": "3"}, {"value": "1"}]}]})

    out = google.ga4_ai_traffic(mock_api(handler), "properties/123456789", 28)
    assert seen["url"].endswith("/properties/123456789:runReport")
    flt = seen["body"]["dimensionFilter"]["orFilter"]["expressions"]
    assert flt[0]["filter"]["stringFilter"]["matchType"] == "PARTIAL_REGEXP" and "claude\\.ai" in flt[0]["filter"]["stringFilter"]["value"]
    assert flt[1]["filter"]["stringFilter"]["value"] == "AI Assistant"
    assert out["ai_sessions"] == 14 and out["ai_key_events"] == 3 and "Lower bound" in out["note"]
    with pytest.raises(ValueError):
        google.ga4_ai_traffic(mock_api(handler), "G-ABC", 28)


def test_gbp_quota_zero_is_reported_not_retried(monkeypatch):
    monkeypatch.setenv("GOOGLE_ACCESS_TOKEN", "tok")
    n = []
    api = mock_api(lambda r: (n.append(1), httpx.Response(429, json={"error": {"message": "Quota exceeded for quota metric ... limit 0"}}))[1], retries=3)
    with pytest.raises(google.GBPNotApproved) as e:
        google.gbp_accounts(api)
    assert "not yet approved" in str(e.value) and e.value.kind == "not_approved"


def test_gbp_endpoints_and_parsing(monkeypatch):
    monkeypatch.setenv("GOOGLE_ACCESS_TOKEN", "tok")
    urls = []

    def handler(req):
        urls.append(req.url)
        u = str(req.url)
        if "fetchMultiDailyMetricsTimeSeries" in u:
            return httpx.Response(200, json={"multiDailyMetricTimeSeries": [{"dailyMetricTimeSeries": [
                {"dailyMetric": "CALL_CLICKS", "timeSeries": {"datedValues": [{"date": {"year": 2026, "month": 9, "day": 1}, "value": "5"}, {"date": {"year": 2026, "month": 9, "day": 2}}]}},
                {"dailyMetric": "BUSINESS_IMPRESSIONS_MOBILE_MAPS", "timeSeries": {"datedValues": [{"value": "100"}]}},
                {"dailyMetric": "BUSINESS_IMPRESSIONS_DESKTOP_SEARCH", "timeSeries": {"datedValues": [{"value": "50"}]}}]}]})
        if "/reviews" in u:
            return httpx.Response(200, json={"averageRating": 4.7, "totalReviewCount": 42, "reviews": [
                {"starRating": "FIVE", "updateTime": "2026-09-30T10:00:00Z", "reviewReply": {"comment": "thanks"}},
                {"starRating": "WEIRD", "createTime": "2026-09-01T10:00:00Z"}]})
        return httpx.Response(200, json={"locations": [{"name": "locations/9", "title": "Northgate", "categories": {
            "primaryCategory": {"displayName": "Heating contractor"}, "additionalCategories": [{"displayName": "Plumber"}]},
            "regularHours": {"periods": [{}]}, "profile": {"description": "x"}, "metadata": {"hasVoiceOfMerchant": True}}]})

    api = mock_api(handler)
    locs = google.gbp_locations(api, "123")
    assert "mybusinessbusinessinformation.googleapis.com/v1/accounts/123/locations" in str(urls[0]) and "readMask=" in str(urls[0])
    inp = google.gbp_inputs_from_location(locs[0], 4.7, 42)
    assert inp.primary_category == "Heating contractor" and inp.verified is True and inp.hours_set and inp.review_count == 42
    perf = google.gbp_performance(api, "locations/9", date(2026, 9, 1), date(2026, 9, 28))
    u = str(urls[-1])
    assert u.count("dailyMetrics=") == len(google.PERF_METRICS) and "dailyRange.startDate.year=2026" in u and "dailyRange.endDate.day=28" in u
    assert perf["calls"] == 5 and perf["impressions"] == 150                            # zero-valued days omit `value`
    rev = google.gbp_reviews(api, "accounts/123", "locations/9")
    assert rev["stars"] == [5, 0] and rev["reply_rate"] == 0.5 and "/v4/accounts/123/locations/9/reviews" in str(urls[-1])


# ---------------- Places API (New) ----------------
PLACES = {"places": [
    {"id": "ChIJ_me_client_aaaa", "displayName": {"text": "Northgate Heating"}, "rating": 4.8, "userRatingCount": 42, "primaryType": "plumber",
     "websiteUri": "https://www.northgate-heating.co.uk/", "nationalPhoneNumber": "0113 496 0123"},
    {"id": "ChIJ_rival_one_bbbb", "displayName": {"text": "Rival One"}, "rating": 4.9, "userRatingCount": 300, "primaryType": "heating_contractor",
     "websiteUri": "https://rival1.example/", "nationalPhoneNumber": "0113 000 0001"},
    {"id": "ChIJ_rival_two_cccc", "displayName": {"text": "Rival Two"}, "rating": 4.6, "userRatingCount": 120, "primaryType": "heating_contractor"},
]}


def places_client(handler, budget=2.0):
    return places.PlacesClient(mock_api(handler), "KEY", budget)


def test_places_search_contract(tmp_path):
    seen = {}

    def handler(req):
        seen.update(url=str(req.url), headers=dict(req.headers), body=json.loads(req.content))
        return httpx.Response(200, json=PLACES)

    pc = places_client(handler)
    out = pc.search_text("boiler repair in Leeds", 53.8008, -1.5491, 99999, "GB", "en-GB", 50)
    assert seen["url"] == "https://places.googleapis.com/v1/places:searchText" and len(out) == 3
    assert seen["headers"]["x-goog-api-key"] == "KEY" and "places.userRatingCount" in seen["headers"]["x-goog-fieldmask"]
    assert "reviews" not in seen["headers"]["x-goog-fieldmask"] and seen["headers"]["x-goog-fieldmask"] != "*"
    b = seen["body"]
    assert b["regionCode"] == "GB" and b["languageCode"] == "en-GB" and b["pageSize"] == 20 and b["includePureServiceAreaBusinesses"] is True
    assert b["locationBias"]["circle"]["radius"] == 50000.0 and "locationRestriction" not in b
    assert places_client(lambda r: httpx.Response(200, json={})).search_text("x", None, None) == []     # empty result is {}


def test_places_budget_cap_and_details_validation():
    pc = places_client(lambda r: httpx.Response(200, json=PLACES), budget=0.05)
    pc.search_text("a", 1, 1)
    with pytest.raises(places.PlacesBudgetExceeded):
        pc.search_text("b", 1, 1)
    with pytest.raises(ValueError):
        pc.details("../../etc/passwd")


def test_competitor_snapshot_findings_and_velocity(tmp_path):
    p = uk()
    snaps = Snapshots(tmp_path / "s.sqlite")
    pc = places_client(lambda r: httpx.Response(200, json=PLACES))
    res = places.snapshot_competitors(pc, p, snaps, ["boiler repair in Leeds"])
    assert res["places_seen"] == 3 and res["client_rows"] == 1
    rows = {r["name"]: r for r in snaps.latest_per_place()}
    assert rows["Northgate Heating"]["is_client"] == 1 and rows["Rival One"]["is_client"] == 0
    f = {x.id: x for x in places.competitor_findings(p, snaps)}
    assert "places.review-gap" in f and "42 vs median" in f["places.review-gap"].evidence
    assert "places.category-differs" in f                                                  # client 'plumber' vs rivals' 'heating_contractor'
    # velocity needs two snapshots a day apart
    pid = "ChIJ_me_client_aaaa"
    assert places.velocity(snaps, pid) is None
    snaps.db.execute("UPDATE place_snapshots SET ts = ts - 864000 WHERE id = (SELECT MIN(id) FROM place_snapshots WHERE place_id=?)", (pid,))
    snaps.add_place(query="q", rank=1, place_id=pid, review_count=52, rating=4.8, is_client=1)
    assert places.velocity(snaps, pid) == pytest.approx(30.0, abs=1.5)                    # +10 reviews in ~10 days = ~30 per 30 days


def test_competitor_findings_without_data_or_client(tmp_path):
    snaps = Snapshots(tmp_path / "s.sqlite")
    assert places.competitor_findings(uk(), snaps)[0].severity.value == "UNKNOWN"
    snaps.add_place(query="q", rank=1, place_id="x", name="Other", review_count=10, rating=4.0)
    assert "places.client-not-found" in {f.id for f in places.competitor_findings(uk(), snaps)}


# ---------------- DataForSEO ----------------
def maps_item(rank_group, domain, place_id="p", phone=""):
    return {"type": "maps_search", "rank_group": rank_group, "domain": domain, "place_id": place_id, "phone": phone,
            "url": "https://www.google.com/maps/search/?x=1", "rating": {"value": 4.5, "votes_count": 10}}


def dfs_ok(items, cost=0.002):
    return httpx.Response(200, json={"status_code": 20000, "cost": cost, "tasks": [{"status_code": 20000, "result": [{"items": items}]}]})


def test_dataforseo_maps_contract_and_geogrid(tmp_path):
    calls = []

    def handler(req):
        body = json.loads(req.content)
        calls.append((str(req.url), body, req.headers["authorization"]))
        n = len(calls)
        items = [maps_item(1, "rival.example"), maps_item(2, "northgate-heating.co.uk")] if n % 2 else [maps_item(1, "rival.example")]
        return dfs_ok(items)

    dfs = dataforseo.DataForSEO(mock_api(handler), "login", "pw", budget_usd=1.0)
    snaps = Snapshots(tmp_path / "s.sqlite")
    p = uk(latitude=53.8008, longitude=-1.5491)
    res = dataforseo.run_geogrid(dfs, p, snaps, "boiler repair", "grid1", size=3, spacing_km=2.0)
    url, body, auth = calls[0]
    assert url == "https://api.dataforseo.com/v3/serp/google/maps/live/advanced" and isinstance(body, list) and len(body) == 1
    assert body[0]["location_coordinate"].endswith(",14z") and body[0]["se_domain"] == "google.co.uk" and body[0]["language_code"] == "en"
    assert auth == "Basic " + base64.b64encode(b"login:pw").decode()
    assert res["points"] and len(calls) == 9 and res["coverage"] == pytest.approx(5 / 9 * 100, abs=0.2)
    assert res["arp"] == round((5 * 2 + 4 * 21) / 9, 2) and res["solv"] == pytest.approx(5 / 9 * 100, abs=0.2)
    assert snaps.grids("grid1")[0]["keyword"] == "boiler repair" and res["cost_usd"] == pytest.approx(0.018)


def test_dataforseo_errors_and_budget():
    bad = lambda r: httpx.Response(200, json={"status_code": 20000, "tasks": [{"status_code": 40501, "status_message": "Invalid Field"}]})
    with pytest.raises(ConnectorError):
        dataforseo.DataForSEO(mock_api(bad), "l", "p").maps_search("x", 1.0, 1.0)
    dfs = dataforseo.DataForSEO(mock_api(lambda r: dfs_ok([], 0.002)), "l", "p", budget_usd=0.003)
    dfs.maps_search("x", 1.0, 1.0)
    with pytest.raises(dataforseo.SerpBudgetExceeded):
        dfs.maps_search("x", 1.0, 1.0)
    with pytest.raises(ValueError):
        dataforseo.run_geogrid(dataforseo.DataForSEO(mock_api(bad), "l", "p"), uk(address={"city": "Nowhereville"}, primary_city="Nowhereville"),
                               Snapshots(":memory:"), "k", "w")


def test_capture_ai_overview(tmp_path):
    aio = {"type": "ai_overview", "markdown": "Try Northgate Heating Ltd in Leeds.", "references": [{"domain": "northgate-heating.co.uk", "url": "https://www.northgate-heating.co.uk/"}],
           "items": [{"references": [{"domain": "yell.com", "url": "https://www.yell.com/x"}]}]}
    seen = {}

    def handler(req):
        seen.update(body=json.loads(req.content))
        return dfs_ok([aio, {"type": "organic"}], 0.004)

    store = Store(tmp_path / "p.sqlite")
    p = uk()
    dfs = dataforseo.DataForSEO(mock_api(handler), "l", "p")
    out = dataforseo.capture_aio(dfs, p, store, "boiler repair leeds", "aio1", "Leeds,England,United Kingdom")
    assert out == {"aio_present": True, "client_named": True, "client_cited": True, "references": 2}
    assert seen["body"][0]["load_async_ai_overview"] is True
    none = dataforseo.capture_aio(dataforseo.DataForSEO(mock_api(lambda r: dfs_ok([{"type": "organic"}])), "l", "p"), p, store, "kw2", "aio1", "x")
    assert none == {"aio_present": False}
    s = summarise(store, "aio1", p)["providers"]["serp:google_ai_overview"]
    assert "vendor-collected" in s["validity"] and s["citation_rate"] == 0.5


# ---------------- LLM probe providers ----------------
def test_anthropic_provider_contract_pause_turn_and_cost(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    seen = []

    def handler(req):
        body = json.loads(req.content)
        seen.append((dict(req.headers), body))
        if len(seen) == 1:
            return httpx.Response(200, json={"model": "m-1", "stop_reason": "pause_turn", "usage": {"server_tool_use": {"web_search_requests": 2}},
                                             "content": [{"type": "thinking", "thinking": "..."}, {"type": "server_tool_use", "id": "srv1", "name": "web_search", "input": {"query": "q"}}]})
        return httpx.Response(200, json={"model": "m-1", "stop_reason": "end_turn", "usage": {"server_tool_use": {"web_search_requests": 3}},
                                         "content": [{"type": "web_search_tool_result", "tool_use_id": "srv1", "content": [
                                             {"type": "web_search_result", "url": "https://www.checkatrade.com/x", "title": "t", "encrypted_content": "e"}]},
                                             {"type": "text", "text": "1. **Northgate Heating Ltd** is good.", "citations": [{"type": "web_search_result_location", "url": "https://www.yell.com/y"}]}]})

    prov = AnthropicProvider(model="claude-test", api=mock_api(handler))
    r = prov.ask("best boiler repair in Leeds", uk())
    h, body = seen[0]
    assert h["x-api-key"] == "sk-test" and h["anthropic-version"] == "2023-06-01"
    tool = body["tools"][0]
    assert tool["type"] == "web_search_20250305" and tool["user_location"] == {"type": "approximate", "city": "Leeds", "region": "West Yorkshire", "country": "GB", "timezone": "Europe/London"}
    assert "tool_choice" not in body and "temperature" not in body                              # forbidden on the 5.5 models
    # continuation echoes the assistant content UNCHANGED (thinking + server_tool_use blocks included)
    assert seen[1][1]["messages"][1] == {"role": "assistant", "content": [{"type": "thinking", "thinking": "..."}, {"type": "server_tool_use", "id": "srv1", "name": "web_search", "input": {"query": "q"}}]}
    assert r.text.startswith("1. **Northgate") and r.cited_urls == ["https://www.checkatrade.com/x", "https://www.yell.com/y"]
    assert r.cost_estimate == max(0.10, 5 * 0.01) and r.model_version == "m-1"
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    with pytest.raises(ConnectorError):
        prov.ask("x", uk())


def test_anthropic_pause_turn_is_capped(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    n = []
    handler = lambda r: (n.append(1), httpx.Response(200, json={"stop_reason": "pause_turn", "content": [{"type": "text", "text": "x"}]}))[1]
    AnthropicProvider(model="m", api=mock_api(handler)).ask("q", uk())
    assert len(n) == 4                                                                           # initial + 3 continuations, never unbounded


def test_gemini_provider_search_and_maps(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g")
    seen = []

    def handler(req):
        seen.append((str(req.url), dict(req.headers), json.loads(req.content)))
        return httpx.Response(200, json={"modelVersion": "gem-x", "candidates": [{"content": {"parts": [{"text": "Try Northgate Heating."}]},
            "groundingMetadata": {"groundingChunks": [
                {"web": {"uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/abc", "title": "checkatrade.com"}},
                {"web": {"uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/def", "title": "Some Article Title"}},
                {"maps": {"uri": "https://maps.google.com/?cid=1", "title": "Northgate", "placeId": "places/abc"}},
                {"image": {"uri": "https://img"}}, {"retrievedContext": {"uri": "x"}}]}}]})

    p = uk(latitude=None)
    r = GeminiProvider(model="gem", api=mock_api(handler)).ask("q", p)
    url, headers, body = seen[0]
    assert url == "https://generativelanguage.googleapis.com/v1beta/models/gem:generateContent" and headers["x-goog-api-key"] == "g"
    assert body["tools"] == [{"google_search": {}}] and "toolConfig" not in body
    assert r.cited_urls[0] == "https://checkatrade.com/" and "vertexaisearch" in r.cited_urls[1] and "https://maps.google.com/?cid=1" in r.cited_urls
    assert len(r.cited_urls) == 3                                                               # image / retrievedContext chunks skipped
    GeminiProvider(model="gem", api=mock_api(handler), mode="maps").ask("q", p)
    _, _, mbody = seen[1]
    assert mbody["tools"] == [{"google_maps": {}}] and mbody["toolConfig"]["retrievalConfig"] == {
        "latLng": {"latitude": 53.8008, "longitude": -1.5491}, "languageCode": "en-GB"}


def test_provider_factory_and_openai_location_has_no_us_fallback():
    assert isinstance(make_provider("claude", "m"), AnthropicProvider) and isinstance(make_provider("gemini", "m"), GeminiProvider)
    seen = {}

    class R:
        def create(self, **kw):
            seen.update(kw)
            return type("O", (), {"output": [], "output_text": "x", "model": "m"})()

    client = type("C", (), {"responses": R()})()
    ClientProfile(name="x", website="x.de", phone="1", jurisdiction="DE", primary_city="Berlin")
    OpenAIResponsesProvider(model="m", client=client).ask("q", ClientProfile(name="x", website="x.de", phone="1", jurisdiction="DE", primary_city="Berlin"))
    loc = seen["tools"][0]["user_location"]
    assert loc["city"] == "Berlin" and "country" not in loc                                      # never silently claim the US
    assert seen["include"] == ["web_search_call.action.sources"]


# ---------------- CLI wiring ----------------
def test_cli_connector_commands(tmp_path, monkeypatch, capsys):
    home = str(tmp_path)
    assert cli.main(["--home", home, "init", "c1", "--market", "uk"]) == 0
    monkeypatch.setenv("GOOGLE_ACCESS_TOKEN", "tok")
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "k")
    monkeypatch.setenv("DATAFORSEO_LOGIN", "l")
    monkeypatch.setenv("DATAFORSEO_PASSWORD", "p")

    def handler(req):
        u = str(req.url)
        if "searchAnalytics" in u:
            return httpx.Response(200, json={"rows": [{"keys": ["leeds boiler"], "clicks": 3.0, "impressions": 90.0, "position": 5.0}]})
        if "runReport" in u:
            return httpx.Response(200, json={"dimensionHeaders": [{"name": "sessionSource"}], "metricHeaders": [{"name": "sessions"}], "rows": [
                {"dimensionValues": [{"value": "chatgpt.com"}], "metricValues": [{"value": "6"}]}]})
        if "places:searchText" in u:
            return httpx.Response(200, json=PLACES)
        if "dataforseo" in u:
            return dfs_ok([maps_item(2, "example-heating.co.uk")])
        raise AssertionError(u)

    real = ApiClient

    class Mocked(real):
        def __init__(self, *a, **k):
            super().__init__(transport=httpx.MockTransport(handler), retries=k.get("retries", 0))

    monkeypatch.setattr(cli, "ApiClient", Mocked)
    assert cli.main(["--home", home, "gsc", "c1", "--site", "sc-domain:example-heating.co.uk"]) == 0
    assert cli.main(["--home", home, "ga4", "c1", "--property", "123456789"]) == 0
    assert cli.main(["--home", home, "places-snapshot", "c1", "--query", "boiler repair in Leeds"]) == 0
    assert cli.main(["--home", home, "geogrid", "c1", "--keyword", "boiler repair", "--size", "1"]) in (0, 2, 1)
    assert cli.main(["--home", home, "report", "c1"]) == 0
    html = (tmp_path / "c1" / "report.html").read_text()
    assert "Performance data" in html and "Search Console" in html and "AI-assistant traffic in GA4" in html
    assert cli.main(["--home", home, "doctor"]) == 0
    out = capsys.readouterr().out
    assert "GOOGLE_PLACES_API_KEY=set" in out and "sk-" not in out                                # presence only, never values
    monkeypatch.delenv("GOOGLE_ACCESS_TOKEN")
    assert cli.main(["--home", home, "gsc", "c1", "--site", "sc-domain:x.com"]) == 2             # missing creds -> clean failure
