"""AI-visibility probe: run geo-targeted prompts repeatedly, resolve the client entity, report mention rate
with intervals, and capture who else is named and which domains are cited."""

from __future__ import annotations

import json
from dataclasses import dataclass

from ..markets import localisation_leak, market_for
from ..models import ClientProfile
from . import stats
from .entities import cited_domains, extract_listed_entities, match_client, top_entities
from .prompts import Prompt, branded_prompts, build_prompts
from .providers import Provider
from .store import Store

NOT_MEASURED = [
    "Google AI Overviews and AI Mode have no compliant API (Gemini API grounding is a different system): shown only if "
    "someone observed them by hand (sheet-export / sheet-import).",
    "Consumer ChatGPT/Claude/Perplexity apps differ from their APIs (one study found ~24% brand overlap): shown only as "
    "manual calibration samples.",
    "Voice assistants (Siri, Alexa, Google Assistant) are measured only through manual observation.",
]


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Budget:
    cap_usd: float
    spent: float = 0.0

    def check(self, next_cost: float) -> None:
        if self.spent + next_cost > self.cap_usd:
            raise BudgetExceeded(f"budget cap ${self.cap_usd:.2f} reached (spent ${self.spent:.2f})")

    def add(self, c: float) -> None:
        self.spent += c


def estimate(profile: ClientProfile, providers: list[Provider], runs: int, include_branded: bool = False) -> dict:
    n_prompts = len(build_prompts(profile)) + (len(branded_prompts(profile)) if include_branded else 0)
    calls = n_prompts * runs * len(providers)
    cost = sum(n_prompts * runs * p.cost_per_call for p in providers)
    return {"prompts": n_prompts, "runs_per_prompt": runs, "providers": [p.name for p in providers],
            "calls": calls, "estimated_cost_usd": round(cost, 2),
            "note": "Cost per call is an ESTIMATE (search fee + 5-20k retrieved tokens); measure before scaling."}


def run_probe(profile: ClientProfile, providers: list[Provider], store: Store, wave: str, runs: int = 8,
              budget: Budget | None = None, include_branded: bool = False, progress=None) -> dict:
    budget = budget or Budget(5.0)
    prompts: list[Prompt] = build_prompts(profile) + (branded_prompts(profile) if include_branded else [])
    location = f"{profile.city}, {profile.address.region} {profile.address.country}".strip()
    market = market_for(profile)
    done = failed = 0
    halted = ""
    for prov in providers:
        for pr in prompts:
            for _ in range(runs):
                try:
                    budget.check(prov.cost_per_call)
                except BudgetExceeded as e:
                    halted = str(e)
                    break
                try:
                    resp = prov.ask(pr.text, profile)
                except Exception as e:  # noqa: BLE001 - record and continue; invalid runs are excluded from rates
                    store.add(wave=wave, provider=prov.name, model=prov.model, prompt_id=pr.id, prompt_kind=pr.kind,
                              prompt_text=pr.text, location=location, ok=0, error=f"{type(e).__name__}: {e}"[:200])
                    failed += 1
                    continue
                budget.add(resp.cost_estimate)
                m = match_client(resp.text, resp.cited_urls, profile)
                store.add(wave=wave, provider=prov.name, model=resp.model_version or prov.model, prompt_id=pr.id,
                          prompt_kind=pr.kind, prompt_text=pr.text, location=location, ok=1,
                          verified=int(m["verified"]), name_match=int(m["name_match"]), cited=int(m["cited"]),
                          method=m["method"], entities=json.dumps(extract_listed_entities(resp.text)),
                          cited_urls=json.dumps(resp.cited_urls), response_text=resp.text[:6000],
                          cost=resp.cost_estimate, leak=int(localisation_leak(resp.text, market)))
                done += 1
                if progress:
                    progress(done, failed)
            if halted:
                break
        if halted:
            break
    return {"wave": wave, "completed": done, "failed": failed, "spent_usd": round(budget.spent, 2), "halted": halted}


def summarise(store: Store, wave: str, profile: ClientProfile) -> dict:
    """Per-provider mention rates with intervals, share of voice among ALL named entities, cited domains."""
    out: dict = {"wave": wave, "providers": {}, "not_measured": NOT_MEASURED,
                 "metric": "Mention rate (API-sampled): share of valid runs in which the client is named. Not a rank."}
    for prov in sorted({r["provider"] for r in store.rows(wave=wave)}):
        rows = [r for r in store.rows(wave=wave, provider=prov) if r["ok"]]
        n = len(rows)
        if not n:
            continue
        per_prompt: dict[str, list[int]] = {}
        per_prompt_ver: dict[str, list[int]] = {}
        for r in rows:
            a = per_prompt.setdefault(r["prompt_id"], [0, 0])
            a[0] += r["name_match"]
            a[1] += 1
            b = per_prompt_ver.setdefault(r["prompt_id"], [0, 0])
            b[0] += r["verified"]
            b[1] += 1
        k_name = sum(r["name_match"] for r in rows)
        k_ver = sum(r["verified"] for r in rows)
        k_cite = sum(r["cited"] for r in rows)
        cl = stats.clustered_bootstrap({k: tuple(v) for k, v in per_prompt.items()})
        ents = top_entities([json.loads(r["entities"]) for r in rows], 10)
        out["providers"][prov] = {
            "valid_runs": n,
            "failed_runs": len([r for r in store.rows(wave=wave, provider=prov) if not r["ok"]]),
            "validity": ("manual spot-check by a person on a real device (calibration only; not comparable with API samples)"
                         if prov.startswith("manual:") else
                         "vendor-collected SERP sample (directional; not comparable with API samples)"
                         if prov.startswith("serp:") else stats.validity_label(n)),
            "mention_rate": round(k_name / n, 3),
            "mention_rate_ci_wilson": tuple(round(x, 3) for x in stats.wilson(k_name, n)),
            "mention_rate_ci_clustered": tuple(round(x, 3) for x in cl),
            "verified_mention_rate": round(k_ver / n, 3),
            "citation_rate": round(k_cite / n, 3),
            "localisation_leak_rate": round(sum(r["leak"] for r in rows) / n, 3),
            "top_named_entities": ents,
            "top_cited_domains": cited_domains([json.loads(r["cited_urls"]) for r in rows], 10),
            "models_seen": sorted(store.models_seen(prov, wave)),
            "min_detectable_diff_vs_equal_wave": round(stats.min_detectable_diff(n), 3),
        }
        out["providers"][prov]["_per_prompt"] = {k: tuple(v) for k, v in per_prompt.items()}
    return out


def compare(store: Store, wave_a: str, wave_b: str, provider: str) -> dict:
    """Wave-over-wave change per provider; only claims a change when the clustered interval excludes 0.
    Refuses to compare across different model versions (re-baseline instead)."""
    ma, mb = store.models_seen(provider, wave_a), store.models_seen(provider, wave_b)
    if ma != mb:
        return {"verdict": "not comparable: model version changed between waves (re-baseline)",
                "models": {wave_a: sorted(ma), wave_b: sorted(mb)}}

    def pp(w):
        d: dict[str, list[int]] = {}
        for r in store.rows(wave=w, provider=provider):
            if r["ok"]:
                a = d.setdefault(r["prompt_id"], [0, 0])
                a[0] += r["name_match"]
                a[1] += 1
        return {k: tuple(v) for k, v in d.items()}

    return stats.compare_waves(pp(wave_a), pp(wave_b))
