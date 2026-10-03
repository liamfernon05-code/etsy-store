"""Command-line interface. State lives in <home>/<client>/ (default ./clients)."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from . import compliance, freshness, plan as plan_mod, uk, uk_data
from .checks import run_all
from .checks.schema import generate_local_business_jsonld, jsonld_script
from .crawl import crawl_site
from .markets import market_for
from .models import ClientProfile, CrawlResult, Finding, Severity, load_profile
from .probe import Budget, BudgetExceeded, compare, estimate, manual, run_probe, summarise
from .probe.providers import make_provider
from .connectors import ApiClient, ConnectorError
from .connectors import dataforseo, google, places
from .probe.store import Store
from .snapshots import Snapshots
from .report import render_report
from .safety import SafeFetcher
from .verticals import VERTICALS

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
TEMPLATE = EXAMPLES / "client.example.toml"
TEMPLATE_UK = EXAMPLES / "client.uk.example.toml"


def _profile(d: Path) -> ClientProfile:
    """client.toml plus anything `resolve` learned (nation, coordinates, council area) without editing the user's file."""
    prof = load_profile(d / "client.toml")
    rp = d / "resolved.json"
    if rp.exists():
        data = json.loads(rp.read_text())
        upd: dict = {}
        if not prof.nation and data.get("nation"):
            upd["nation"] = data["nation"]
        if prof.latitude is None and data.get("latitude") is not None:
            upd.update(latitude=data["latitude"], longitude=data.get("longitude"))
        if upd:
            prof = prof.model_copy(update=upd)
    gp = d / "gbp_live.json"
    if gp.exists():
        live = json.loads(gp.read_text()).get("inputs", {})
        manual = prof.gbp.model_dump(exclude_defaults=True)
        prof = prof.model_copy(update={"gbp": prof.gbp.model_copy(update={k: v for k, v in live.items() if k not in manual and v not in (None, "", [])})})
        if not prof.address.council_area and data.get("council_area"):
            prof = prof.model_copy(update={"address": prof.address.model_copy(update={"council_area": data["council_area"]})})
    return prof


def _home(args) -> Path:
    return Path(args.home or os.environ.get("LSA_HOME", "clients"))


def _dir(args) -> Path:
    d = _home(args) / args.client
    if not (d / "client.toml").exists() and args.cmd != "init":
        raise SystemExit(f"No client.toml in {d}. Run: python -m local_seo_agent init {args.client}")
    return d


def cmd_init(args) -> int:
    d = _home(args) / args.client
    d.mkdir(parents=True, exist_ok=True)
    args.vertical = args.vertical or ("heating_engineer" if args.market == "uk" else "dentist")
    target = d / "client.toml"
    if target.exists():
        raise SystemExit(f"{target} already exists")
    src = TEMPLATE_UK if args.market == "uk" else TEMPLATE
    text = re.sub(r'(?m)^vertical = "[a-z_]+"', f'vertical = "{args.vertical}"', src.read_text(), count=1)
    target.write_text(text)
    print(f"Created {target}\nEdit it (name, website, phone, address, services, facts, gbp), then run: audit {args.client}")
    return 0


def cmd_audit(args) -> int:
    d = _dir(args)
    profile = _profile(d)
    print(f"Crawling {profile.website} (max {args.max_pages} pages, robots.txt honoured, 1 request/second)...")
    fetcher = SafeFetcher(min_interval=args.delay, respect_robots=not args.ignore_robots)
    crawl = crawl_site(profile.website, fetcher, args.max_pages)
    extra: list[Finding] = []
    if args.psi:
        key = os.environ.get("PSI_API_KEY")
        if not key:
            raise SystemExit("--psi needs $PSI_API_KEY (free PageSpeed Insights key)")
        from .psi import fetch_psi, psi_findings

        extra = psi_findings(fetch_psi(profile.website, key))
    extra += _uk_register(profile)
    if (d / "snapshots.sqlite").exists():
        extra += places.competitor_findings(profile, Snapshots(d / "snapshots.sqlite"))
    if getattr(args, "render", False):
        extra += _render_checks(profile, crawl, args)
    findings = run_all(profile, crawl, extra)
    (d / "crawl.json").write_text(crawl.model_dump_json(indent=1))
    (d / "audit.json").write_text(json.dumps([f.model_dump(mode="json") for f in findings], indent=1))
    c = {s: sum(1 for f in findings if f.severity.value == s) for s in ("ERROR", "WARN", "UNKNOWN", "INFO")}
    print(f"{len(crawl.pages)} page(s) crawled, {fetcher.requests_made} request(s). Findings: {c}")
    for f in findings[:10]:
        print(f"  [{f.severity.value:7}] {f.title}")
    print(f"Saved {d/'audit.json'}")
    return 0


def _uk_register(profile: ClientProfile) -> list[Finding]:
    """Companies House status (free API key) for UK limited companies; UNKNOWN when it cannot be checked."""
    if not market_for(profile).is_uk or not profile.company_number:
        return []
    key = os.environ.get("COMPANIES_HOUSE_API_KEY")
    if not key:
        return [Finding(id="uk.ch.no-key", category="uk-register", severity=Severity.UNKNOWN,
                        title="Companies House status not checked", impact=2, effort=1,
                        detail="Set COMPANIES_HOUSE_API_KEY (free) so the audit can confirm the company is active.")]
    try:
        return uk_data.company_findings(profile, uk_data.fetch_company(SafeFetcher(min_interval=0), profile.company_number, key))
    except Exception as e:  # noqa: BLE001
        return [Finding(id="uk.ch.error", category="uk-register", severity=Severity.UNKNOWN,
                        title="Companies House lookup failed", detail=f"{type(e).__name__}: {str(e)[:120]}", impact=2, effort=1)]


def _render_checks(profile: ClientProfile, crawl: CrawlResult, args) -> list[Finding]:
    from .models import Confidence
    from .render import render_findings, render_page

    home = crawl.home
    if home is None or home.status != 200:
        return []
    try:
        rendered, st = render_page(profile.website, SafeFetcher(min_interval=0.2, respect_robots=not args.ignore_robots))
    except Exception as e:  # noqa: BLE001 - playwright/chromium missing or page error
        return [Finding(id="render.unavailable", category="crawlability", severity=Severity.UNKNOWN,
                        title="JavaScript rendering check could not run", detail=f"{type(e).__name__}: {str(e)[:140]}",
                        impact=2, effort=1, confidence=Confidence.OFFICIAL,
                        fix="pip install playwright && playwright install chromium (set LSA_CHROMIUM_PATH to use an existing Chromium).")]
    return render_findings(home, rendered, uk.normalise_uk_phone(profile.phone)[-10:] if market_for(profile).is_uk else
                           "".join(ch for ch in profile.phone if ch.isdigit()))


def _load_findings(d: Path) -> list[Finding]:
    p = d / "audit.json"
    return [Finding(**x) for x in json.loads(p.read_text())] if p.exists() else []


def cmd_plan(args) -> int:
    d = _dir(args)
    profile = _profile(d)
    tasks = plan_mod.build_plan(profile, _load_findings(d))
    (d / "plan.json").write_text(json.dumps([t.model_dump(mode="json") for t in tasks], indent=1))
    for phase, items in plan_mod.by_phase(tasks).items():
        print(f"\n== By day {phase} ({len(items)}) ==")
        for t in items[:8]:
            print(f"  {t.score:4}  {t.title}")
    print(f"\nSaved {d/'plan.json'}")
    return 0


def cmd_probe(args) -> int:
    d = _dir(args)
    profile = _profile(d)
    store = Store(d / "probe.sqlite")
    if args.compare:
        a, b = args.compare
        print(json.dumps(compare(store, a, b, args.provider[0]), indent=2, default=str))
        return 0
    providers = [make_provider(p, args.model, args.cost_per_call) for p in args.provider]
    est = estimate(profile, providers, args.runs, args.include_branded)
    print(json.dumps(est, indent=2))
    if args.dry_run:
        return 0
    if est["estimated_cost_usd"] > args.budget:
        print(f"Estimated cost exceeds --budget ${args.budget:.2f}; the run will stop when the cap is reached.")
    res = run_probe(profile, providers, store, args.wave, args.runs, Budget(args.budget), args.include_branded,
                    progress=lambda done, failed: print(f"  runs ok={done} failed={failed}", file=sys.stderr) if done % 25 == 0 else None)
    print("\n" + json.dumps(res, indent=2))
    summ = summarise(store, args.wave, profile)
    (d / f"probe_{args.wave}.json").write_text(json.dumps(summ, indent=1, default=str))
    return 1 if res["halted"] else 0


def cmd_report(args) -> int:
    d = _dir(args)
    profile = _profile(d)
    crawl = CrawlResult.model_validate_json((d / "crawl.json").read_text()) if (d / "crawl.json").exists() else None
    findings = _load_findings(d)
    tasks = plan_mod.build_plan(profile, findings)
    store = Store(d / "probe.sqlite") if (d / "probe.sqlite").exists() else None
    probes = [summarise(store, w, profile) for w in store.waves()] if store else []
    calib = [c for w in (store.waves() if store else []) for c in manual.calibrate(store, w)]
    status = freshness.update_in_progress(SafeFetcher(min_interval=0, respect_robots=False)) if getattr(args, "live_status", False) else None
    extras: dict = {}
    for key in ("gsc", "ga4", "gbp"):
        if (d / f"{key}.json").exists():
            extras[key] = json.loads((d / f"{key}.json").read_text())
    if (d / "snapshots.sqlite").exists():
        extras["geogrid"] = [{"keyword": r["keyword"], "wave": r["wave"], "arp": r["arp"], "solv": r["solv"], "coverage": r["coverage"],
                              "size": r["size"], "spacing_km": r["spacing_km"]} for r in Snapshots(d / "snapshots.sqlite").grids()]
    html = render_report(profile, crawl, findings, tasks, probes, calib, status, extras)
    (d / "report.html").write_text(html)
    print(f"Wrote {d/'report.html'}")
    return 0


def cmd_run(args) -> int:
    cmd_audit(args)
    cmd_plan(args)
    return cmd_report(args)


def cmd_schema(args) -> int:
    d = _dir(args)
    profile = _profile(d)
    out = jsonld_script(generate_local_business_jsonld(profile))
    (d / "localbusiness.jsonld.html").write_text(out + "\n")
    print(out)
    print("\n(generated only from client.toml facts; no ratings/reviews; paste into the site <head> after review)")
    return 0


def cmd_draft(args) -> int:
    from .llm import draft

    d = _dir(args)
    profile = _profile(d)
    bad = compliance.check_request(args.detail or "")
    if bad:
        print("REFUSED:", *[f"\n - {v.code}: {v.message}" for v in bad])
        return 2
    res = draft(profile, args.kind, args.detail or "", args.review or "", args.model)
    out = d / "drafts"
    out.mkdir(exist_ok=True)
    path = out / f"{args.kind}.md"
    note = "" if not res.violations else "\n\n<!-- BLOCKED: " + "; ".join(v.code for v in res.violations) + " -->"
    path.write_text(res.text + note + "\n")
    print(res.text)
    if res.blocked:
        print("\nDRAFT BLOCKED by compliance checks:", *[f"\n - {v.code}: {v.message} ({v.span})" for v in res.violations])
        return 3
    print(f"\nSaved {path} (DRAFT: human review required; nothing was posted)")
    return 0


def cmd_resolve(args) -> int:
    d = _dir(args)
    profile = _profile(d)
    if not market_for(profile).is_uk:
        raise SystemExit("resolve is for UK clients (postcodes.io); set jurisdiction = \"UK\".")
    data = uk_data.resolve_postcode(SafeFetcher(min_interval=0, respect_robots=False), profile.address.postal_code)
    if not data:
        raise SystemExit("Could not resolve the postcode (invalid, unknown, or network blocked).")
    (d / "resolved.json").write_text(json.dumps(data, indent=1))
    print(json.dumps(data, indent=1), f"\nSaved {d/'resolved.json'} (client.toml is not modified)")
    return 0


def cmd_sheet_export(args) -> int:
    d = _dir(args)
    out = Path(args.out) if args.out else d / "observation_sheet.csv"
    n = manual.export_worksheet(_profile(d), out, args.surface or None, args.prompts)
    print(f"Wrote {out} ({n} rows). Run each prompt on a real device in the client's area, fill the last columns, then:\n"
          f"  python -m local_seo_agent sheet-import {args.client} --file {out} --wave <wave>")
    return 0


def cmd_sheet_import(args) -> int:
    d = _dir(args)
    res = manual.import_worksheet(Store(d / "probe.sqlite"), _profile(d), Path(args.file), args.wave)
    print(json.dumps(res, indent=2))
    return 1 if res["errors"] else 0


def cmd_verify_facts(args) -> int:
    path = _home(args) / "facts_verification.json"
    prev = freshness.load_verification(path)
    res = freshness.verify_facts(SafeFetcher(min_interval=0.5, respect_robots=False), prev)
    freshness.save_verification(res, path)
    bad = 0
    for fid, r in res["results"].items():
        print(f"  {r['status']:15} {fid}  {r.get('detail', '')}")
        bad += r["status"] != "OK"
    print(f"Saved {path}. Statuses other than OK need a human to re-read the primary page before the fact is trusted.")
    return 1 if bad else 0


def cmd_status(args) -> int:
    res = freshness.update_in_progress(SafeFetcher(min_interval=0, respect_robots=False))
    print(json.dumps(res, indent=2))
    return 0


def _dates(days: int) -> tuple[str, str]:
    from datetime import date, timedelta

    end = date.today() - timedelta(days=3)   # final Search Console data lags ~2-3 days
    return (end - timedelta(days=days)).isoformat(), end.isoformat()


def _conn_fail(name: str, e: Exception) -> int:
    print(f"{name}: {type(e).__name__}: {e}")
    return 2 if getattr(e, "kind", "") in ("auth", "not_approved") else 1


def cmd_gsc(args) -> int:
    d = _dir(args)
    profile = _profile(d)
    start, end = _dates(args.days)
    try:
        resp = google.gsc_query(ApiClient(retries=2), args.site, start, end, ["QUERY"], 5000)
    except ConnectorError as e:
        return _conn_fail("Search Console", e)
    out = {**google.gsc_summary(resp, profile.city), "site": args.site, "start": start, "end": end}
    (d / "gsc.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1)[:1500])
    return 0


def cmd_ga4(args) -> int:
    d = _dir(args)
    try:
        out = google.ga4_ai_traffic(ApiClient(retries=2), args.property, args.days)
    except (ConnectorError, ValueError) as e:
        return _conn_fail("GA4", e)
    (d / "ga4.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1)[:1500])
    return 0


def cmd_gbp(args) -> int:
    from datetime import date, timedelta

    d = _dir(args)
    api = ApiClient()
    try:
        if not args.account:
            for a in google.gbp_accounts(api):
                print(a.get("name"), a.get("accountName"), a.get("type"))
            print("Next: gbp <client> --account accounts/ID   (lists locations)")
            return 0
        if not args.location:
            for loc in google.gbp_locations(api, args.account):
                print(loc.get("name"), "|", loc.get("title"), "|", (loc.get("storefrontAddress") or {}).get("postalCode", ""))
            print("Next: gbp <client> --account accounts/ID --location locations/ID")
            return 0
        loc = next((x for x in google.gbp_locations(api, args.account) if x.get("name", "").endswith(args.location.split("/")[-1])), {})
        end = date.today() - timedelta(days=2)
        perf = google.gbp_performance(api, args.location, end - timedelta(days=args.days), end)
        rev = google.gbp_reviews(api, args.account, args.location)
    except google.GBPNotApproved as e:
        print(f"GBP API: {e}")
        return 2
    except ConnectorError as e:
        return _conn_fail("Business Profile", e)
    inputs = google.gbp_inputs_from_location(loc, rev.get("average_rating"), rev.get("total")).model_dump(exclude_defaults=True)
    out = {"performance": perf, "reviews": rev, "inputs": inputs, "location": args.location}
    (d / "gbp.json").write_text(json.dumps(out, indent=1))
    (d / "gbp_live.json").write_text(json.dumps({"inputs": inputs}, indent=1))
    print(json.dumps(out, indent=1)[:1800])
    return 0


def cmd_places_snapshot(args) -> int:
    d = _dir(args)
    profile = _profile(d)
    try:
        pc = places.PlacesClient.from_env(ApiClient(retries=2), args.budget)
        res = places.snapshot_competitors(pc, profile, Snapshots(d / "snapshots.sqlite"), args.query or None, args.place_id or "")
    except (ConnectorError, places.PlacesBudgetExceeded, ValueError) as e:
        return _conn_fail("Places", e)
    print(json.dumps(res, indent=1), "\nRe-run weekly: review velocity needs >=2 snapshots a day or more apart.")
    return 0


def cmd_geogrid(args) -> int:
    d = _dir(args)
    profile = _profile(d)
    try:
        dfs = dataforseo.DataForSEO.from_env(ApiClient(), args.budget)
        res = dataforseo.run_geogrid(dfs, profile, Snapshots(d / "snapshots.sqlite"), args.keyword, args.wave, args.size,
                                     args.spacing_km, args.place_id or "")
    except (ConnectorError, dataforseo.SerpBudgetExceeded, ValueError) as e:
        return _conn_fail("DataForSEO", e)
    print(json.dumps({k: v for k, v in res.items() if k != "points"}, indent=1))
    return 0


def cmd_aio_capture(args) -> int:
    d = _dir(args)
    profile = _profile(d)
    store = Store(d / "probe.sqlite")
    loc_name = args.location_name or ("Leeds,England,United Kingdom" if market_for(profile).is_uk else f"{profile.city},{profile.address.region},United States")
    kws = args.keyword or [f"{t} {profile.city}" for t in (profile.target_services or [])][:5]
    try:
        dfs = dataforseo.DataForSEO.from_env(ApiClient(), args.budget)
        for kw in kws:
            print(kw, dataforseo.capture_aio(dfs, profile, store, kw, args.wave, loc_name))
    except (ConnectorError, dataforseo.SerpBudgetExceeded) as e:
        return _conn_fail("DataForSEO", e)
    print("Stored as provider 'serp:google_ai_overview' (vendor-collected sample, directional).")
    return 0


def cmd_doctor(args) -> int:
    import importlib.util

    def has(env): return "set" if os.environ.get(env) else "missing"
    print("Credentials (presence only; values are never printed):")
    for name, envs in [("Anthropic (Claude probe + drafting)", ["ANTHROPIC_API_KEY", "LSA_CLAUDE_MODEL"]),
                       ("OpenAI probe", ["OPENAI_API_KEY", "LSA_OPENAI_MODEL"]), ("Perplexity probe", ["PERPLEXITY_API_KEY", "LSA_PERPLEXITY_MODEL"]),
                       ("Gemini probe", ["GEMINI_API_KEY", "LSA_GEMINI_MODEL"]), ("Places API (New)", ["GOOGLE_PLACES_API_KEY"]),
                       ("Search Console / GA4 / GBP", ["GOOGLE_ACCESS_TOKEN"]), ("DataForSEO", ["DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD"]),
                       ("PageSpeed Insights", ["PSI_API_KEY"]), ("Companies House (UK)", ["COMPANIES_HOUSE_API_KEY"])]:
        print(f"  {name:38} " + ", ".join(f"{e}={has(e)}" for e in envs))
    print("Optional packages:")
    for mod, why in [("openai", "OpenAI/Perplexity probes"), ("claude_agent_sdk", "LLM drafting"), ("playwright", "audit --render")]:
        print(f"  {mod:18} {'installed' if importlib.util.find_spec(mod) else 'missing':10} ({why})")
    print("TLS CA bundle override:", os.environ.get("LSA_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE") or "(system default)")
    return 0


def cmd_guard(args) -> int:
    v = compliance.check_request(args.text, args.market.upper())
    if not v:
        print("OK: no prohibited request detected (this is a heuristic check, not legal advice).")
        return 0
    for x in v:
        print(f"REFUSE [{x.code}] {x.message}")
    return 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="local_seo_agent", description="Local-business SEO + AI-visibility agent")
    ap.add_argument("--home", help="clients directory (default ./clients or $LSA_HOME)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="create a client folder with a template client.toml")
    p.add_argument("client")
    p.add_argument("--vertical", default=None, choices=sorted(VERTICALS) + ["solicitor"])
    p.add_argument("--market", default="us", choices=["us", "uk"], help="us (default) or uk")
    p.set_defaults(fn=cmd_init)

    for name, fn, helptext in (("audit", cmd_audit, "crawl + deterministic audit"), ("run", cmd_run, "audit + plan + report")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("client")
        p.add_argument("--max-pages", type=int, default=25)
        p.add_argument("--delay", type=float, default=1.0, help="seconds between requests per host")
        p.add_argument("--psi", action="store_true", help="also call PageSpeed Insights ($PSI_API_KEY)")
        p.add_argument("--ignore-robots", action="store_true", help="only for sites you own and have verified")
        p.add_argument("--render", action="store_true", help="also render the homepage with JavaScript (playwright) and compare")
        p.set_defaults(fn=fn)

    p = sub.add_parser("plan", help="build the 30/60/90 plan from the audit")
    p.add_argument("client")
    p.set_defaults(fn=cmd_plan)

    p = sub.add_parser("probe", help="AI-visibility probe (geo-targeted, repeated, budget-capped)")
    p.add_argument("client")
    p.add_argument("--provider", action="append", default=[], choices=["fake", "openai", "claude", "perplexity", "gemini"])
    p.add_argument("--model", default="", help="model id (or $LSA_<PROVIDER>_MODEL)")
    p.add_argument("--wave", default="baseline1")
    p.add_argument("--runs", type=int, default=8, help="runs per prompt (diagnostic); headline claims need >=200 valid runs/platform")
    p.add_argument("--budget", type=float, default=5.0, help="hard USD cap (estimated)")
    p.add_argument("--cost-per-call", type=float, default=0.10, help="ESTIMATED USD per call incl. retrieved tokens")
    p.add_argument("--include-branded", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="print the estimate and stop")
    p.add_argument("--compare", nargs=2, metavar=("WAVE_A", "WAVE_B"))
    p.set_defaults(fn=cmd_probe)

    p = sub.add_parser("report", help="render report.html")
    p.add_argument("client")
    p.add_argument("--live-status", action="store_true", help="read Google's Search Status Dashboard for a rollout in progress")
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("schema", help="generate LocalBusiness JSON-LD from client facts")
    p.add_argument("client")
    p.set_defaults(fn=cmd_schema)

    p = sub.add_parser("draft", help="LLM draft (needs ANTHROPIC_API_KEY); compliance-checked, never posted")
    p.add_argument("client")
    p.add_argument("kind", choices=["gbp-description", "review-request", "review-reply", "service-page"])
    p.add_argument("--detail", default="", help="e.g. the service name for service-page")
    p.add_argument("--review", default="", help="review text to reply to (treated as untrusted data)")
    p.add_argument("--model", default=None)
    p.set_defaults(fn=cmd_draft)

    p = sub.add_parser("resolve", help="UK: look up nation/coordinates/council area for the postcode (postcodes.io)")
    p.add_argument("client")
    p.set_defaults(fn=cmd_resolve)

    p = sub.add_parser("sheet-export", help="worksheet for MANUAL observation of AI Overviews/AI Mode/consumer apps/voice")
    p.add_argument("client")
    p.add_argument("--surface", action="append", choices=sorted(manual.SURFACES))
    p.add_argument("--prompts", type=int, default=10)
    p.add_argument("--out", default="")
    p.set_defaults(fn=cmd_sheet_export)

    p = sub.add_parser("sheet-import", help="import a filled observation worksheet")
    p.add_argument("client")
    p.add_argument("--file", required=True)
    p.add_argument("--wave", required=True)
    p.set_defaults(fn=cmd_sheet_import)

    p = sub.add_parser("verify-facts", help="re-check quoted facts against their primary sources (needs open network)")
    p.set_defaults(fn=cmd_verify_facts)

    p = sub.add_parser("status", help="is a Google ranking/spam/core update rolling out? (Search Status Dashboard)")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("gsc", help="Search Console summary (GOOGLE_ACCESS_TOKEN)")
    p.add_argument("client")
    p.add_argument("--site", required=True, help="'sc-domain:example.com' or the exact URL-prefix property")
    p.add_argument("--days", type=int, default=28)
    p.set_defaults(fn=cmd_gsc)

    p = sub.add_parser("ga4", help="AI-assistant sessions from GA4 (GOOGLE_ACCESS_TOKEN)")
    p.add_argument("client")
    p.add_argument("--property", required=True, help="numeric GA4 property id (not the G- id)")
    p.add_argument("--days", type=int, default=28)
    p.set_defaults(fn=cmd_ga4)

    p = sub.add_parser("gbp", help="Business Profile accounts/locations/performance/reviews (needs Google API approval)")
    p.add_argument("client")
    p.add_argument("--account", default="")
    p.add_argument("--location", default="")
    p.add_argument("--days", type=int, default=28)
    p.set_defaults(fn=cmd_gbp)

    p = sub.add_parser("places-snapshot", help="competitor snapshot via Places API (New) (GOOGLE_PLACES_API_KEY)")
    p.add_argument("client")
    p.add_argument("--query", action="append")
    p.add_argument("--place-id", default="")
    p.add_argument("--budget", type=float, default=2.0, help="hard USD cap (estimated)")
    p.set_defaults(fn=cmd_places_snapshot)

    p = sub.add_parser("geogrid", help="local rank grid via DataForSEO Maps (DATAFORSEO_LOGIN/PASSWORD)")
    p.add_argument("client")
    p.add_argument("--keyword", required=True)
    p.add_argument("--wave", default="grid1")
    p.add_argument("--size", type=int, default=3)
    p.add_argument("--spacing-km", type=float, default=2.0)
    p.add_argument("--place-id", default="")
    p.add_argument("--budget", type=float, default=1.0)
    p.set_defaults(fn=cmd_geogrid)

    p = sub.add_parser("aio-capture", help="capture Google AI Overviews for keywords via a licensed SERP API (directional)")
    p.add_argument("client")
    p.add_argument("--keyword", action="append")
    p.add_argument("--wave", default="aio1")
    p.add_argument("--location-name", default="")
    p.add_argument("--budget", type=float, default=1.0)
    p.set_defaults(fn=cmd_aio_capture)

    p = sub.add_parser("doctor", help="which credentials/packages are available (presence only)")
    p.set_defaults(fn=cmd_doctor)

    p = sub.add_parser("guard", help="check a request against the compliance rules")
    p.add_argument("--market", default="us", choices=["us", "uk"])
    p.add_argument("text")
    p.set_defaults(fn=cmd_guard)

    args = ap.parse_args(argv)
    if args.cmd == "probe" and not args.provider and not args.compare:
        ap.error("probe needs --provider (openai|perplexity|gemini|fake)")
    try:
        return args.fn(args)
    except BudgetExceeded as e:
        print(e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
