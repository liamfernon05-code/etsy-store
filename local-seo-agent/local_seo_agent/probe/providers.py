"""AI answer-engine providers for visibility probes (official APIs only; never scrape consumer UIs).

Honest limits, repeated in every report:
 * API answers differ from the consumer apps (one study: ~24% brand overlap). Calibrate monthly by hand.
 * Google AI Overviews / AI Mode are NOT measured: Gemini API grounding is a different system.
 * Provider code paths were written against public docs and are exercised in tests with stubs; they have
   not been run against live endpoints in the build environment (no API keys). Run a 1-prompt smoke test first.

Models are deliberately NOT hardcoded: set them via env (LSA_OPENAI_MODEL, LSA_CLAUDE_MODEL, LSA_PERPLEXITY_MODEL,
LSA_GEMINI_MODEL) or --model, because names and prices change.
"""

from __future__ import annotations

import hashlib
import os
import random
import re
from dataclasses import dataclass, field

from ..connectors import ApiClient, ConnectorError
from ..markets import location_for
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
        L = location_for(profile)
        # No US fallback: an empty approximate location is what avoids OpenAI's US default for non-US/unknown markets
        loc = {"type": "approximate", "country": L["country"], "city": L["city"], "region": L["region"],
               "timezone": L["timezone"]}
        resp = self.client.responses.create(
            model=self.model, input=prompt,
            tools=[{"type": "web_search", "user_location": {k: v for k, v in loc.items() if v}}],
            include=["web_search_call.action.sources"],
        )
        urls: list[str] = []
        for item in getattr(resp, "output", []) or []:
            if getattr(item, "type", "") == "web_search_call":
                for src in getattr(getattr(item, "action", None), "sources", None) or []:
                    if getattr(src, "url", ""):
                        urls.append(src.url)
                continue
            if getattr(item, "type", "") != "message":
                continue
            for part in getattr(item, "content", []) or []:
                for ann in getattr(part, "annotations", []) or []:
                    if getattr(ann, "type", "") == "url_citation" and getattr(ann, "url", ""):
                        urls.append(ann.url)
        return ProbeResponse(getattr(resp, "output_text", "") or "", list(dict.fromkeys(urls)),
                             getattr(resp, "model", self.model), self.cost_per_call)


class OpenAICompatProvider(Provider):
    """Perplexity Sonar / Gemini via their OpenAI-compatible chat endpoints."""

    # Gemini is NOT here: the OpenAI-compatible endpoint does not do Google Search grounding (see GeminiProvider).
    BASES = {"perplexity": ("https://api.perplexity.ai", "PERPLEXITY_API_KEY", "LSA_PERPLEXITY_MODEL")}

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
            L = location_for(profile)
            loc = {"country": L["country"], "city": L["city"], "region": L["region"]}
            if L["latitude"] is not None and L["longitude"] is not None:  # lat/long must be sent together with country
                loc.update(latitude=L["latitude"], longitude=L["longitude"])
            kwargs["extra_body"] = {"web_search_options": {"user_location": {k: v for k, v in loc.items() if v not in ("", None)}}}
        resp = self.client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}], **kwargs)
        text = resp.choices[0].message.content or ""
        extra = getattr(resp, "model_extra", None) or {}
        urls = [r.get("url", "") for r in (extra.get("search_results") or []) if isinstance(r, dict)]  # richer; prefer
        urls += list(extra.get("citations") or [])                                                      # may be deprecated
        return ProbeResponse(text, list(dict.fromkeys(u for u in urls if u)), getattr(resp, "model", self.model),
                             self.cost_per_call)


class AnthropicProvider(Provider):
    """Claude via the Messages API (raw REST) with the web_search tool and an approximate user_location.

    Contract (platform docs): POST https://api.anthropic.com/v1/messages, headers x-api-key + anthropic-version
    2023-06-01, no beta header; tool type web_search_20250305 (direct calls only: simplest response shape); country is ISO
    alpha-2 ('GB' not 'UK'); parse only `text` blocks (Opus/Sonnet 5.5 may emit thinking blocks); never force tool_choice
    on the 5.5 models; usage.server_tool_use.web_search_requests counts searches (USD 10 per 1,000); stop_reason
    'pause_turn' means re-send with the assistant content appended UNCHANGED (capped here).
    """

    name = "claude"
    URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, model: str = "", cost_per_call: float = 0.10, api: ApiClient | None = None, max_uses: int = 5):
        super().__init__(_require_model(model, "LSA_CLAUDE_MODEL", "claude"), cost_per_call)
        self.api = api or ApiClient(timeout=120.0)
        self.max_uses = max_uses

    def ask(self, prompt: str, profile: ClientProfile) -> ProbeResponse:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ConnectorError(401, "Set ANTHROPIC_API_KEY", "auth")
        L = location_for(profile)
        loc = {k: v for k, v in {"type": "approximate", "city": L["city"], "region": L["region"],
                                 "country": L["country"], "timezone": L["timezone"]}.items() if v}
        tool = {"type": "web_search_20250305", "name": "web_search", "max_uses": self.max_uses, "user_location": loc}
        messages: list[dict] = [{"role": "user", "content": prompt}]
        text_parts: list[str] = []
        urls: list[str] = []
        searches = 0
        model_v = self.model
        for _ in range(4):  # initial call + up to 3 pause_turn continuations
            resp = self.api.request("POST", self.URL, headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                                               "content-type": "application/json"},
                                    json={"model": self.model, "max_tokens": 2048, "messages": messages, "tools": [tool]})
            model_v = resp.get("model", model_v)
            searches += int(((resp.get("usage") or {}).get("server_tool_use") or {}).get("web_search_requests", 0) or 0)
            for block in resp.get("content", []):
                t = block.get("type")
                if t == "text":
                    text_parts.append(block.get("text", ""))
                    urls += [c.get("url", "") for c in block.get("citations", []) or [] if c.get("url")]
                elif t == "web_search_tool_result" and isinstance(block.get("content"), list):
                    urls += [r.get("url", "") for r in block["content"] if r.get("type") == "web_search_result" and r.get("url")]
            if resp.get("stop_reason") != "pause_turn":
                break
            messages = messages + [{"role": "assistant", "content": resp.get("content", [])}]
        return ProbeResponse("".join(text_parts).strip(), list(dict.fromkeys(urls)), model_v,
                             max(self.cost_per_call, searches * 0.01))


_DOMAIN_RE = re.compile(r"^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")


class GeminiProvider(Provider):
    """Gemini via native generateContent with Google Search (default) or Google Maps grounding.

    POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent, header x-goog-api-key. Search
    grounding has no documented location field, so the town is in the prompt; Maps grounding takes
    toolConfig.retrievalConfig.latLng + languageCode (UK availability UNVERIFIED: test with a known UK query and check the
    returned place ids are British). groundingChunks web.uri is usually a vertexaisearch redirect whose `title` is the source
    domain: we record the domain, never follow the redirect. NB: this is the Gemini API, NOT Google AI Overviews.
    """

    name = "gemini"
    BASE = "https://generativelanguage.googleapis.com/v1beta/models/"

    def __init__(self, model: str = "", cost_per_call: float = 0.10, api: ApiClient | None = None, mode: str = "search"):
        super().__init__(_require_model(model, "LSA_GEMINI_MODEL", "gemini"), cost_per_call)
        self.api = api or ApiClient(timeout=120.0)
        self.mode = mode

    def ask(self, prompt: str, profile: ClientProfile) -> ProbeResponse:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ConnectorError(401, "Set GEMINI_API_KEY", "auth")
        L = location_for(profile)
        body: dict = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        if self.mode == "maps":
            body["tools"] = [{"google_maps": {}}]
            if L["latitude"] is not None and L["longitude"] is not None:
                body["toolConfig"] = {"retrievalConfig": {"latLng": {"latitude": L["latitude"], "longitude": L["longitude"]},
                                                         "languageCode": L["language"]}}
        else:
            body["tools"] = [{"google_search": {}}]
        resp = self.api.request("POST", f"{self.BASE}{self.model}:generateContent", headers={"x-goog-api-key": key}, json=body)
        cand = (resp.get("candidates") or [{}])[0]
        text = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", []))
        urls: list[str] = []
        for ch in (cand.get("groundingMetadata") or {}).get("groundingChunks", []) or []:
            web, maps = ch.get("web") or {}, ch.get("maps") or {}
            if web:
                title = str(web.get("title", ""))
                urls.append(f"https://{title}/" if _DOMAIN_RE.match(title) else web.get("uri", ""))
            if maps:
                urls.append(maps.get("uri", ""))
        return ProbeResponse(text, list(dict.fromkeys(u for u in urls if u)), resp.get("modelVersion", self.model), self.cost_per_call)


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
    if name == "claude":
        return AnthropicProvider(model, cost_per_call)
    if name == "gemini":
        return GeminiProvider(model, cost_per_call)
    raise SystemExit(f"Unknown provider: {name}")
