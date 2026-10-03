"""Typed data shared across the pipeline.

Anything derived from untrusted web content (page text, AI answers) is length-capped and stripped of
control characters before it is stored in a Finding, so later LLM steps never see raw payloads.
"""

from __future__ import annotations

import re
import tomllib
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

_CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def clean(text: str, limit: int) -> str:
    """Strip control chars, collapse whitespace, cap length."""
    return re.sub(r"\s+", " ", _CTRL.sub(" ", str(text))).strip()[:limit]


class Severity(str, Enum):
    ERROR = "ERROR"      # blocks visibility or breaks a hard rule
    WARN = "WARN"        # should fix
    INFO = "INFO"        # advisory / FYI
    UNKNOWN = "UNKNOWN"  # could not be determined (no data, blocked, needs API access)


class Confidence(str, Enum):
    OFFICIAL = "official"    # stated by Google/OpenAI/Anthropic/etc. docs
    EVIDENCE = "evidence"    # controlled or large-scale study
    HEURISTIC = "heuristic"  # our own tripwire; configurable, never present as a violation
    VENDOR = "vendor"        # vendor/blog summary, not read from the primary source


class Finding(BaseModel):
    id: str
    category: str
    severity: Severity
    title: str
    detail: str = ""
    evidence: str = ""
    fix: str = ""
    impact: int = Field(3, ge=1, le=5)
    effort: int = Field(2, ge=1, le=5)
    confidence: Confidence = Confidence.OFFICIAL
    source_url: str = ""
    verified_on: str = ""

    @field_validator("title")
    @classmethod
    def _t(cls, v: str) -> str:
        return clean(v, 160)

    @field_validator("detail", "fix")
    @classmethod
    def _d(cls, v: str) -> str:
        return clean(v, 400)

    @field_validator("evidence")
    @classmethod
    def _e(cls, v: str) -> str:
        return clean(v, 160)


class Address(BaseModel):
    street: str = ""
    city: str = ""
    region: str = ""
    postal_code: str = ""
    country: str = "US"


class Competitor(BaseModel):
    name: str
    website: str = ""


class GBPInputs(BaseModel):
    """Manually supplied Google Business Profile facts (the GBP API needs Google approval)."""

    primary_category: str = ""
    additional_categories: list[str] = []
    rating: float | None = None
    review_count: int | None = None
    competitor_review_counts: list[int] = []
    has_booking_or_menu_link: bool | None = None
    hours_set: bool | None = None
    special_hours_set: bool | None = None
    description_set: bool | None = None
    services_listed: bool | None = None
    photo_count: int | None = None
    verified: bool | None = None
    name_matches_signage: bool | None = None
    primary_phone_is_tracking_number: bool | None = None


class ClientProfile(BaseModel):
    name: str
    website: str
    phone: str
    vertical: str = "generic"
    jurisdiction: str = "US"           # required input: compliance notes only cover the US
    address: Address = Address()
    service_area_business: bool = False  # hides street address on GBP
    primary_city: str = ""
    service_areas: list[str] = []
    target_services: list[str] = []
    brand_aliases: list[str] = []
    competitors: list[Competitor] = []
    facts: list[str] = []              # client-supplied, drafting may use ONLY these
    hours: dict[str, str] = {}         # e.g. {"Mon-Fri": "09:00-17:00"}
    same_as: list[str] = []
    locations: int = 1
    gbp: GBPInputs = GBPInputs()

    @field_validator("website")
    @classmethod
    def _site(cls, v: str) -> str:
        v = v.strip()
        return v if v.startswith(("http://", "https://")) else "https://" + v

    @property
    def city(self) -> str:
        return self.primary_city or self.address.city


def load_profile(path: Path) -> ClientProfile:
    data = tomllib.loads(Path(path).read_text())
    client = dict(data.get("client", {}))
    if "address" in data:
        client["address"] = data["address"]
    if "gbp" in data:
        client["gbp"] = data["gbp"]
    if "competitors" in data:
        client["competitors"] = data["competitors"]
    return ClientProfile(**client)


class PageData(BaseModel):
    url: str
    final_url: str = ""
    status: int = 0
    bytes: int = 0
    headers: dict[str, str] = {}
    redirect_chain: list[str] = []
    title: str = ""
    meta_description: str = ""
    h1: list[str] = []
    h2: list[str] = []
    canonical: str = ""
    robots_meta: str = ""
    viewport: bool = False
    lang: str = ""
    jsonld: list[dict] = []
    jsonld_errors: int = 0
    internal_links: list[str] = []
    tel_links: list[str] = []
    images: int = 0
    images_missing_alt: int = 0
    scripts: int = 0
    text: str = ""
    word_count: int = 0
    truncated: bool = False


class CrawlResult(BaseModel):
    start_url: str
    pages: list[PageData] = []
    robots_status: int = 0
    robots_txt: str | None = None
    sitemap_urls: list[str] = []
    sitemap_url_count: int = 0
    errors: list[str] = []

    @property
    def home(self) -> PageData | None:
        return self.pages[0] if self.pages else None
