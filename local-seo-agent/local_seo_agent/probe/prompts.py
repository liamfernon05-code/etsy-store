"""Prompt sets for AI-visibility probes: non-branded local prompts (headline) and branded ones (reputation only)."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import ClientProfile
from ..verticals import get_vertical

TEMPLATES = [
    "best {term} in {city}",
    "who is the best {term} near {city}? give me 3 recommendations",
    "I need a {term} in {city}. who should I call?",
]


@dataclass(frozen=True)
class Prompt:
    id: str
    text: str
    kind: str  # "nonbranded" (headline metric) | "branded" (accuracy/reputation, excluded from headline)
    term: str


def build_prompts(profile: ClientProfile, max_prompts: int = 24, paraphrases: int = 3) -> list[Prompt]:
    vert = get_vertical(profile.vertical)
    terms = profile.target_services or vert["probe_terms"]
    if not terms:
        raise ValueError("No target_services and no vertical probe terms: add target_services to client.toml")
    city = profile.city
    if not city:
        raise ValueError("A city is required for local prompts (address.city or primary_city)")
    out: list[Prompt] = []
    for t_i, term in enumerate(terms):
        for p_i, tpl in enumerate(TEMPLATES[:paraphrases]):
            out.append(Prompt(f"nb{t_i}-{p_i}", tpl.format(term=term, city=city), "nonbranded", term))
    return out[:max_prompts]


def branded_prompts(profile: ClientProfile) -> list[Prompt]:
    city = profile.city
    return [
        Prompt("br0", f"What do you know about {profile.name} in {city}? Is it a good choice?", "branded", profile.name),
        Prompt("br1", f"{profile.name} {city} reviews and reputation", "branded", profile.name),
    ]
