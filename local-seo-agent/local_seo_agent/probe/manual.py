"""Human-observed samples for surfaces no compliant API can measure.

Why: Google AI Overviews / AI Mode have no API (Gemini API grounding is a different system), the consumer ChatGPT /
Claude / Perplexity / Gemini / Copilot apps differ from their APIs (one study: ~24% brand overlap), and voice assistants
(Siri, Alexa, Google Assistant) have none either. We never scrape these. Instead the agent exports a worksheet, a person
runs the prompts on a real device in the client's area, and the results are imported and summarised.

Imported rows are stored as provider "manual:<surface>". They are labelled calibration-only and are never mixed into the
API headline metric. `calibrate()` compares API samples with the manual app samples for the same prompts so the report
can show how far the API numbers are from what real users see.
"""

from __future__ import annotations

import csv
import json
import re
import time
from datetime import date
from pathlib import Path

from ..models import ClientProfile, clean
from .entities import host
from .prompts import build_prompts
from .store import Store

SURFACES = {
    "google_ai_overview": "Google AI Overview (search on a phone, signed out, in the client's area)",
    "google_ai_mode": "Google AI Mode",
    "chatgpt_app": "ChatGPT app/web with search on",
    "claude_app": "Claude app/web with web search on",
    "perplexity_app": "Perplexity app/web",
    "gemini_app": "Gemini app/web",
    "copilot_app": "Microsoft Copilot",
    "siri": "Siri (ask aloud on an iPhone)",
    "alexa": "Alexa (ask aloud)",
    "google_assistant": "Google Assistant / Gemini voice",
}
API_TO_APP = {"openai": "chatgpt_app", "claude": "claude_app", "perplexity": "perplexity_app", "gemini": "gemini_app"}
COLUMNS = ["surface", "prompt_id", "prompt_text", "observed_on", "client_named", "client_site_cited",
           "named_businesses", "cited_domains", "notes"]
YES = {"y", "yes", "true", "1", "x"}
NO = {"n", "no", "false", "0", ""}


def export_worksheet(profile: ClientProfile, path: Path, surfaces: list[str] | None = None, n_prompts: int = 10) -> int:
    surfaces = surfaces or ["google_ai_overview", "google_ai_mode", "chatgpt_app", "claude_app", "perplexity_app"]
    bad = [s for s in surfaces if s not in SURFACES]
    if bad:
        raise ValueError(f"unknown surface(s) {bad}; choose from {sorted(SURFACES)}")
    prompts = build_prompts(profile)[:n_prompts]
    rows = 0
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for s in surfaces:
            for p in prompts:
                w.writerow([s, p.id, p.text, "", "", "", "", "", ""])
                rows += 1
    return rows


def import_worksheet(store: Store, profile: ClientProfile, path: Path, wave: str) -> dict:
    """Validate and import a filled worksheet. Rows without client_named are skipped (not yet observed)."""
    client_host = host(profile.website)
    imported = skipped = 0
    errors: list[str] = []
    location = f"{profile.city}, {profile.address.region} {profile.address.country}".strip()
    with open(path, newline="") as fh:
        for i, row in enumerate(csv.DictReader(fh), start=2):
            surface = (row.get("surface") or "").strip()
            named = (row.get("client_named") or "").strip().lower()
            if surface not in SURFACES:
                errors.append(f"line {i}: unknown surface {surface!r}")
                continue
            if named not in YES and named not in {"n", "no", "false", "0"}:
                skipped += 1  # blank = not observed yet
                continue
            observed = (row.get("observed_on") or "").strip()
            try:
                date.fromisoformat(observed)
            except ValueError:
                errors.append(f"line {i}: observed_on must be YYYY-MM-DD")
                continue
            cited = [d.strip().lower() for d in re.split(r"[;,\s]+", row.get("cited_domains") or "") if d.strip()]
            site_cited = (row.get("client_site_cited") or "").strip().lower() in YES or any(
                d == client_host or d.endswith("." + client_host) for d in cited)
            entities = [clean(x, 60) for x in (row.get("named_businesses") or "").split(";") if x.strip()]
            is_yes = named in YES
            store.add(wave=wave, provider=f"manual:{surface}", model="manual", prompt_id=row.get("prompt_id", ""),
                      prompt_kind="nonbranded", prompt_text=clean(row.get("prompt_text", ""), 300), location=location,
                      ok=1, verified=int(is_yes), name_match=int(is_yes), cited=int(site_cited), method="human",
                      entities=json.dumps(entities), cited_urls=json.dumps([f"https://{d}/" for d in cited]),
                      response_text=clean(row.get("notes", ""), 500), ts=time.time())
            imported += 1
    return {"imported": imported, "skipped_blank": skipped, "errors": errors}


def calibrate(store: Store, wave: str) -> list[dict]:
    """Compare each API provider with its manual consumer-app counterpart on the SAME prompts."""
    out = []
    for api, app in API_TO_APP.items():
        api_rows = [r for r in store.rows(wave=wave, provider=api) if r["ok"]]
        app_rows = [r for r in store.rows(wave=wave, provider=f"manual:{app}") if r["ok"]]
        if not api_rows or not app_rows:
            continue
        per_prompt_api: dict[str, list[int]] = {}
        for r in api_rows:
            a = per_prompt_api.setdefault(r["prompt_id"], [0, 0])
            a[0] += r["name_match"]
            a[1] += 1
        agree = disagree = 0
        details = []
        for r in app_rows:
            a = per_prompt_api.get(r["prompt_id"])
            if not a:
                continue
            api_rate = a[0] / a[1]
            api_says = api_rate >= 0.5
            app_says = bool(r["name_match"])
            agree += api_says == app_says
            disagree += api_says != app_says
            details.append({"prompt_id": r["prompt_id"], "api_mention_rate": round(api_rate, 2), "app_named": app_says})
        n = agree + disagree
        if n:
            out.append({"api": api, "app": app, "prompts_compared": n, "agreement": round(agree / n, 2),
                        "note": "Small manual sample: indicative only. Low agreement means the API numbers do not "
                                "represent what real users see on that app.", "details": details})
    return out
