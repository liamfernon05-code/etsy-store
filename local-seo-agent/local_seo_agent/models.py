"""Typed data shared across the pipeline.

Anything derived from untrusted web content (page text, AI answers) is length-capped and stripped of
control characters before it is stored in a Finding, so later LLM steps never see raw payloads.
"""

from __future__ import annotations

import re
import tomllib
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator

from . import uk

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
    region: str = ""        # US state, or UK county / council area / nation
    postal_code: str = ""   # ZIP or UK postcode
    country: str = ""       # ISO alpha-2 ("US", "GB"); derived from `jurisdiction` when empty
    county: str = ""        # UK, optional (never used for NAP matching)
    council_area: str = ""  # UK, Scotland/Wales/NI


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
    verified_on: str = ""            # ISO date the profile was verified/accepted (drives the "new profile" playbook)
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
    # --- UK / identity (all optional) ---
    nation: str = ""                    # ENG | WAL | SCO | NIR (derived from the postcode when unambiguous)
    company_number: str = ""            # Companies House number (limited companies / LLPs)
    registered_name: str = ""           # legal name if different from the trading name
    registered_office: str = ""         # registered office address (may differ from the trading address)
    vat_number: str = ""
    regulator_ids: dict[str, str] = {}  # e.g. {"sra": "123456", "gdc": "...", "gas_safe": "...", "cqc": "..."}
    latitude: float | None = None       # used for geo-grid and user_location; resolved from the postcode if unset
    longitude: float | None = None
    language: str = "en"
    is_aesthetics: bool = False         # clinic/salon offering injectables etc. (UK CAP 12.12 checks)
    treatment_type: str = ""            # "non_surgical_device" | "injectable" | "surgical" | "" (sets which regulatory regime applies)
    delivered_by: str = ""              # e.g. "beauty therapist", "nurse", "doctor": clinicians change the regime
    franchise_brand: str = ""           # e.g. the franchisor's brand name
    brand_domain: str = ""              # franchisor's website domain when the local page lives there
    sells_gas_services: bool = False

    @field_validator("website")
    @classmethod
    def _site(cls, v: str) -> str:
        v = v.strip()
        return v if v.startswith(("http://", "https://")) else "https://" + v

    @model_validator(mode="after")
    def _market_defaults(self) -> "ClientProfile":
        from .markets import market_code  # local import: markets imports uk, not models

        code = market_code(self.jurisdiction)
        if not self.address.country:
            self.address.country = {"UK": "GB", "US": "US"}.get(code, "")
        if code == "UK":
            if self.address.postal_code:
                self.address.postal_code = uk.normalise_postcode(self.address.postal_code)
            if not self.nation:
                self.nation = (uk.nation_from_nation_text(self.address.region) or uk.nation_from_nation_text(
                    self.address.council_area) or "")
                pc_nation = uk.nation_from_postcode(self.address.postal_code)
                if not self.nation and pc_nation in uk.NATIONS:
                    self.nation = pc_nation
            else:
                self.nation = uk.nation_from_nation_text(self.nation) or self.nation.upper()
        return self

    @property
    def city(self) -> str:
        return self.primary_city or self.address.city

    def gbp_age_days(self, today=None) -> int | None:
        """Days since the Google Business Profile was verified (None if unknown/invalid)."""
        from datetime import date

        try:
            return ((today or date.today()) - date.fromisoformat(self.gbp.verified_on)).days
        except ValueError:
            return None


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
    external_hosts: list[str] = []   # unique hostnames this page links to
    script_hosts: list[str] = []     # unique hostnames of external <script src> (analytics/ads/tag managers)
    emails: list[str] = []           # mailto: addresses
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
