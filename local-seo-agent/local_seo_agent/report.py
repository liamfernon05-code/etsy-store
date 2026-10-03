"""Render the client report (HTML, autoescaped: AI answers and page text are untrusted)."""

from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import facts as facts_mod
from .compliance import jurisdiction_warning
from .models import ClientProfile, CrawlResult, Finding
from .plan import Task, by_phase


def render_report(profile: ClientProfile, crawl: CrawlResult | None, findings: list[Finding], tasks: list[Task],
                  probes: list[dict] | None = None) -> str:
    env = Environment(loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
                      autoescape=select_autoescape(["html", "j2"]))
    counts = Counter(f.severity.value for f in findings)
    facts = [{**f, "verified_on": facts_mod.VERIFIED, "stale": facts_mod.stale()} for f in facts_mod.FACTS]
    from .probe import NOT_MEASURED

    probes = [{k: v for k, v in s.items()} for s in (probes or [])]
    for s in probes:
        for p in s.get("providers", {}).values():
            p.pop("_per_prompt", None)
    return env.get_template("report.html.j2").render(
        profile=profile, findings=findings, phases=by_phase(tasks), probes=probes, facts=facts,
        counts={k: counts.get(k, 0) for k in ("ERROR", "WARN", "UNKNOWN", "INFO")},
        pages=len(crawl.pages) if crawl else 0, generated=date.today().isoformat(),
        jurisdiction_warning=jurisdiction_warning(profile), not_measured=NOT_MEASURED,
        update_note=("A Google spam update that began 2026-09-24 may still be rolling out: avoid judging ranking "
                     "changes until it ends (check status.search.google.com).")
        if date.today() <= date(2026, 10, 15) else "",
    )
