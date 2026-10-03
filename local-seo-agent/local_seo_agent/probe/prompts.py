"""Prompt sets for AI-visibility probes: non-branded local prompts (headline) and branded ones (reputation only)."""

from __future__ import annotations

from dataclasses import dataclass

from .. import uk
from ..markets import UK_TEMPLATES, US_TEMPLATES, market_for, uk_accreditation_phrase, uk_area_clause
from ..models import ClientProfile
from ..verticals import canonical_vertical, vertical_for

TEMPLATES = US_TEMPLATES  # kept for backwards compatibility


@dataclass(frozen=True)
class Prompt:
    id: str
    text: str
    kind: str  # "nonbranded" (headline metric) | "branded" (accuracy/reputation, excluded from headline)
    term: str


def build_prompts(profile: ClientProfile, max_prompts: int = 24, paraphrases: int | None = None) -> list[Prompt]:
    """Non-branded local prompts in the client's market wording (UK English for UK clients)."""
    vert = vertical_for(profile)
    terms = profile.target_services or vert["probe_terms"]
    if not terms:
        raise ValueError("No target_services and no vertical probe terms: add target_services to client.toml")
    city = profile.city
    if not city:
        raise ValueError("A city is required for local prompts (address.city or primary_city)")
    is_uk = market_for(profile).is_uk
    templates = UK_TEMPLATES if is_uk else US_TEMPLATES
    district = uk.postcode_district(profile.address.postal_code) if is_uk else ""
    if is_uk and not district:
        templates = [t for t in templates if "{district}" not in t]
    n = paraphrases if paraphrases is not None else len(templates)
    terms = terms[: max(1, max_prompts // max(n, 1))]  # cap by whole terms so no term is half-covered
    out: list[Prompt] = []
    for t_i, term in enumerate(terms):
        for p_i, tpl in enumerate(templates[:n]):
            text = tpl.format(term=term, city=city, area=uk_area_clause(profile) if is_uk else "",
                              body=uk_accreditation_phrase(canonical_vertical(profile.vertical)) if is_uk else "",
                              district=district)
            out.append(Prompt(f"nb{t_i}-{p_i}", text, "nonbranded", term))
    return out[:max_prompts]


def branded_prompts(profile: ClientProfile) -> list[Prompt]:
    city = profile.city
    return [
        Prompt("br0", f"What do you know about {profile.name} in {city}? Is it a good choice?", "branded", profile.name),
        Prompt("br1", f"{profile.name} {city} reviews and reputation", "branded", profile.name),
    ]
