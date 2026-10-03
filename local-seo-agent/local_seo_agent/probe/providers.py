"""AI answer-engine providers for visibility probes (official APIs only; never scrape consumer UIs).

Honest limits, repeated in every report:
 * API answers differ from the consumer apps (one study: ~24% brand overlap). Calibrate monthly by hand.
 * Google AI Overviews / AI Mode are NOT measured: Gemini API grounding is a different system.
 * Provider code paths were written against public docs and are exercised in tests with stubs; they have
   not been run against live endpoints in the build environment (no API keys). Run a 1-prompt smoke test first.

Models are deliberately NOT hardcoded: set them via env (LSA_OPENAI_MODEL, LSA_PERPLEXITY_MODEL,
LSA_GEMINI_MODEL) or --model, because names and prices change.
"""

from __future__ import annotations

import hashlib
import os
import random
from dataclasses import dataclass, field

from ..models import ClientProfile


@dataclass
class ProbeResponse:
    text: str
    cited_urls: list[str] = field(default_factory=list)
    model_version: str = ""
    cost_estimate: float = 0.0


class Provider:
    name = "base"

    def __init__(self, model: str = "", cost_per_call: float = 0.10):
        self.model = model
        self.cost_per_call = cost_per_call

    def ask(self, prompt: str, profile: ClientProfile) -> ProbeResponse:  # pragma: no cover - interface
        raise NotImplementedError


def _require_model(model: str, env: str, provider: str) -> str:
    model = model or os.environ.get(env, "")
    if not model:
        raise SystemExit(f"Set a model for {provider}: --model or ${env} (model names change; none is hardcoded).")
    return model


class OpenAIResponsesProvider(Provider):
    """OpenAI Responses API with the web_search tool and an approximate user_location."""

    name = "openai"

    def __init__(self, model: str = "", cost_per_call: float = 0.10, client=None):
        super().__init__(_require_model(model, "LSA_OPENAI_MODEL", "openai"), cost_per_call)
        if client is None:
            from openai import OpenAI  # lazy: optional dependency

            client = OpenAI()
        self.client = client

    def ask(self, prompt: str, profile: ClientProfile) -> ProbeResponse:
        loc = {"type": "approximate", "country": profile.address.country or "US",
               "city": profile.city, "region": profile.address.region}
        resp = self.client.responses.create(
            model=self.model, input=prompt,
            tools=[{"type": "web_search", "user_location": {k: v for k, v in loc.items() if v}}],
        )
        urls: list[str] = []
        for item in getattr(resp, "output", []) or []:
            if getattr(item, "type", "") != "message":
                continue
            for part in getattr(item, "content", []) or []:
                for ann in getattr(part, "annotations", []) or []:
                    if getattr(ann, "type", "") == "url_citation" and getattr(ann, "url", ""):
                        urls.append(ann.url)
        return ProbeResponse(getattr(resp, "output_text", "") or "", urls, getattr(resp, "model", self.model),
                             self.cost_per_call)


class OpenAICompatProvider(Provider):
    """Perplexity Sonar / Gemini via their OpenAI-compatible chat endpoints."""

    BASES = {
        "perplexity": ("https://api.perplexity.ai", "PERPLEXITY_API_KEY", "LSA_PERPLEXITY_MODEL"),
        "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY", "LSA_GEMINI_MODEL"),
    }

    def __init__(self, name: str, model: str = "", cost_per_call: float = 0.10, client=None):
        base, key_env, model_env = self.BASES[name]
        super().__init__(_require_model(model, model_env, name), cost_per_call)
        self.name = name
        if client is None:
            from openai import OpenAI

            key = os.environ.get(key_env)
            if not key:
                raise SystemExit(f"Set ${key_env} for the {name} provider.")
            client = OpenAI(base_url=base, api_key=key)
        self.client = client

    def ask(self, prompt: str, profile: ClientProfile) -> ProbeResponse:
        kwargs = {}
        if self.name == "perplexity":  # Perplexity supports an approximate user location
            loc = {"country": profile.address.country or "US", "city": profile.city, "region": profile.address.region}
            kwargs["extra_body"] = {"web_search_options": {"user_location": {k: v for k, v in loc.items() if v}}}
        resp = self.client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}], **kwargs)
        text = resp.choices[0].message.content or ""
        extra = getattr(resp, "model_extra", None) or {}
        urls = list(extra.get("citations") or [])
        urls += [r.get("url", "") for r in (extra.get("search_results") or []) if isinstance(r, dict)]
        return ProbeResponse(text, [u for u in urls if u], getattr(resp, "model", self.model), self.cost_per_call)


class FakeProvider(Provider):
    """Deterministic offline provider for tests, demos and --dry-run style smoke tests."""

    name = "fake"

    def __init__(self, model: str = "fake-1", cost_per_call: float = 0.0, p_mention: float = 0.3, seed: int = 1):
        super().__init__(model, cost_per_call)
        self.p = p_mention
        self.seed = seed

    def ask(self, prompt: str, profile: ClientProfile) -> ProbeResponse:
        self._n = getattr(self, "_n", 0) + 1
        h = int(hashlib.sha256(f"{self.seed}|{prompt}|{self._n}".encode()).hexdigest(), 16)
        rng = random.Random(h)
        rivals = ["Maple Grove Care", "Downtown Experts", "City Pros Group", "Elm Street Specialists"]
        rng.shuffle(rivals)
        picks = rivals[:3]
        if rng.random() < self.p:
            picks[rng.randrange(3)] = profile.name
        lines = [f"{i}. **{n}** - highly rated in {profile.city}." for i, n in enumerate(picks, 1)]
        cited = ["https://www.yelp.com/biz/example", "https://www.healthgrades.com/example"]
        if profile.name in picks and rng.random() < 0.5:
            cited.append(profile.website)
        return ProbeResponse("\n".join(lines), cited, self.model, self.cost_per_call)


def make_provider(name: str, model: str = "", cost_per_call: float = 0.10) -> Provider:
    if name == "fake":
        return FakeProvider(model or "fake-1", 0.0)
    if name == "openai":
        return OpenAIResponsesProvider(model, cost_per_call)
    if name in OpenAICompatProvider.BASES:
        return OpenAICompatProvider(name, model, cost_per_call)
    raise SystemExit(f"Unknown provider: {name}")
