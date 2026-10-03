"""Command-line interface. State lives in <home>/<client>/ (default ./clients)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import compliance, plan as plan_mod
from .checks import run_all
from .checks.schema import generate_local_business_jsonld, jsonld_script
from .crawl import crawl_site
from .models import CrawlResult, Finding, load_profile
from .probe import Budget, BudgetExceeded, compare, estimate, run_probe, summarise
from .probe.providers import make_provider
from .probe.store import Store
from .report import render_report
from .safety import SafeFetcher
from .verticals import VERTICALS

TEMPLATE = (Path(__file__).resolve().parent.parent / "examples" / "client.example.toml")


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
    target = d / "client.toml"
    if target.exists():
        raise SystemExit(f"{target} already exists")
    text = TEMPLATE.read_text().replace('vertical = "dentist"', f'vertical = "{args.vertical}"')
    target.write_text(text)
    print(f"Created {target}\nEdit it (name, website, phone, address, services, facts, gbp), then run: audit {args.client}")
    return 0


def cmd_audit(args) -> int:
    d = _dir(args)
    profile = load_profile(d / "client.toml")
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
    findings = run_all(profile, crawl, extra)
    (d / "crawl.json").write_text(crawl.model_dump_json(indent=1))
    (d / "audit.json").write_text(json.dumps([f.model_dump(mode="json") for f in findings], indent=1))
    c = {s: sum(1 for f in findings if f.severity.value == s) for s in ("ERROR", "WARN", "UNKNOWN", "INFO")}
    print(f"{len(crawl.pages)} page(s) crawled, {fetcher.requests_made} request(s). Findings: {c}")
    for f in findings[:10]:
        print(f"  [{f.severity.value:7}] {f.title}")
    print(f"Saved {d/'audit.json'}")
    return 0


def _load_findings(d: Path) -> list[Finding]:
    p = d / "audit.json"
    return [Finding(**x) for x in json.loads(p.read_text())] if p.exists() else []


def cmd_plan(args) -> int:
    d = _dir(args)
    profile = load_profile(d / "client.toml")
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
    profile = load_profile(d / "client.toml")
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
    profile = load_profile(d / "client.toml")
    crawl = CrawlResult.model_validate_json((d / "crawl.json").read_text()) if (d / "crawl.json").exists() else None
    findings = _load_findings(d)
    tasks = plan_mod.build_plan(profile, findings)
    store = Store(d / "probe.sqlite") if (d / "probe.sqlite").exists() else None
    probes = [summarise(store, w, profile) for w in store.waves()] if store else []
    html = render_report(profile, crawl, findings, tasks, probes)
    (d / "report.html").write_text(html)
    print(f"Wrote {d/'report.html'}")
    return 0


def cmd_run(args) -> int:
    cmd_audit(args)
    cmd_plan(args)
    return cmd_report(args)


def cmd_schema(args) -> int:
    d = _dir(args)
    profile = load_profile(d / "client.toml")
    out = jsonld_script(generate_local_business_jsonld(profile))
    (d / "localbusiness.jsonld.html").write_text(out + "\n")
    print(out)
    print("\n(generated only from client.toml facts; no ratings/reviews; paste into the site <head> after review)")
    return 0


def cmd_draft(args) -> int:
    from .llm import draft

    d = _dir(args)
    profile = load_profile(d / "client.toml")
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


def cmd_guard(args) -> int:
    v = compliance.check_request(args.text)
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
    p.add_argument("--vertical", default="dentist", choices=sorted(VERTICALS))
    p.set_defaults(fn=cmd_init)

    for name, fn, helptext in (("audit", cmd_audit, "crawl + deterministic audit"), ("run", cmd_run, "audit + plan + report")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("client")
        p.add_argument("--max-pages", type=int, default=25)
        p.add_argument("--delay", type=float, default=1.0, help="seconds between requests per host")
        p.add_argument("--psi", action="store_true", help="also call PageSpeed Insights ($PSI_API_KEY)")
        p.add_argument("--ignore-robots", action="store_true", help="only for sites you own and have verified")
        p.set_defaults(fn=fn)

    p = sub.add_parser("plan", help="build the 30/60/90 plan from the audit")
    p.add_argument("client")
    p.set_defaults(fn=cmd_plan)

    p = sub.add_parser("probe", help="AI-visibility probe (geo-targeted, repeated, budget-capped)")
    p.add_argument("client")
    p.add_argument("--provider", action="append", default=[], choices=["fake", "openai", "perplexity", "gemini"])
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

    p = sub.add_parser("guard", help="check a request against the compliance rules")
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
