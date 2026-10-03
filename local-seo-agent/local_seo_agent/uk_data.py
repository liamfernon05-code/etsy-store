"""Free UK data adapters (no vendor SDKs): postcodes.io and the Companies House API.

postcodes.io  (no key): postcode -> nation, council area, region, coordinates. Resolves the border-postcode ambiguity
              that nation_from_postcode() refuses to guess, and gives geo-grid / user_location coordinates.
Companies House (free API key, HTTP Basic with the key as username): company status, registered name and office.
              Used because AI assistants have been seen recommending closed companies.

Both calls go through SafeFetcher (public IPs only, size/time caps). Contracts are from the public API docs and were
NOT exercised live in the build sandbox (egress blocked): run `python -m local_seo_agent resolve <client>` as a smoke test.
"""

from __future__ import annotations

import base64
import json
import re
from urllib.parse import quote

from . import uk
from .facts import VERIFIED
from .models import ClientProfile, Confidence, Finding, Severity
from .safety import SafeFetcher

POSTCODES_IO = "https://api.postcodes.io/postcodes/"
COMPANIES_HOUSE = "https://api.company-information.service.gov.uk/company/"


def resolve_postcode(fetcher: SafeFetcher, postcode: str) -> dict:
    """Return {'nation','latitude','longitude','council_area','region'} or {} if unavailable/invalid."""
    pc = uk.normalise_postcode(postcode)
    if not uk.is_valid_postcode(pc):
        return {}
    res = fetcher._get(POSTCODES_IO + quote(pc))  # noqa: SLF001 - fixed trusted host; robots not applicable to an API
    if res.status != 200:
        return {}
    r = (json.loads(res.text) or {}).get("result") or {}
    nation = uk.nation_from_nation_text(r.get("country", ""))
    return {k: v for k, v in {
        "nation": nation, "latitude": r.get("latitude"), "longitude": r.get("longitude"),
        "council_area": r.get("admin_district") or "", "region": r.get("region") or "",
    }.items() if v not in (None, "")}


def fetch_company(fetcher: SafeFetcher, company_number: str, api_key: str) -> dict:
    """Companies House profile JSON, or {} when not found. The key is sent as Basic auth username only."""
    num = re.sub(r"\s", "", company_number).upper()
    if not re.fullmatch(r"[A-Z0-9]{6,8}", num):
        raise ValueError("company number must be 6-8 letters/digits")
    old = fetcher.user_agent
    # SafeFetcher has no auth hook by design (to keep secrets out of crawl paths): build the single request here.
    import httpx  # local import: only needed for the authenticated call

    from .safety import validate_url
    validate_url(COMPANIES_HOUSE + num)
    token = base64.b64encode(f"{api_key}:".encode()).decode()
    r = httpx.get(COMPANIES_HOUSE + num, headers={"Authorization": f"Basic {token}", "User-Agent": old}, timeout=15,
                  follow_redirects=False)
    if r.status_code == 404:
        return {}
    r.raise_for_status()
    return r.json()


def company_findings(profile: ClientProfile, data: dict) -> list[Finding]:
    out: list[Finding] = []

    def mk(id_, sev, title, **kw):
        out.append(Finding(id=f"uk.ch.{id_}", category="uk-register", severity=sev, title=title, verified_on=VERIFIED,
                           confidence=kw.pop("confidence", Confidence.OFFICIAL), **kw))

    if not data:
        mk("not-found", Severity.WARN, "Company number not found at Companies House", evidence=profile.company_number,
           impact=3, effort=1, fix="Check the number; sole traders and partnerships are not on the register.")
        return out
    status = str(data.get("company_status", "")).lower()
    if status and status != "active":
        mk("not-active", Severity.ERROR, f"Companies House status is '{status}'",
           detail="AI assistants and Google can recommend firms that no longer trade; a non-active status is also a legal red flag.",
           impact=5, effort=1, fix="Confirm trading status and update the website, GBP and directories accordingly.")
    reg_name = re.sub(r"[^a-z0-9 ]", "", str(data.get("company_name", "")).lower())
    ours = re.sub(r"[^a-z0-9 ]", "", (profile.registered_name or profile.name).lower())
    if reg_name and ours and reg_name != ours:
        mk("name-differs", Severity.INFO, "Registered company name differs from the name in client.toml",
           evidence=str(data.get("company_name", ""))[:80], impact=1, effort=1,
           detail="Trading names can differ; the website's legal footer must show the registered name.")
    ro = (data.get("registered_office_address") or {}).get("postal_code", "")
    if profile.registered_office and ro and uk.normalise_postcode(ro) not in uk.normalise_postcode(profile.registered_office):
        mk("office-differs", Severity.WARN, "Registered office postcode differs from the one in client.toml",
           evidence=ro, impact=2, effort=1, fix="Show the Companies House registered office in the website's legal footer.")
    jur = str(data.get("jurisdiction", ""))
    if jur:
        mk("jurisdiction", Severity.INFO, f"Registered in: {jur}", impact=1, effort=1,
           detail="The website must state the part of the UK of registration (England and Wales / Scotland / Northern Ireland).")
    return out
