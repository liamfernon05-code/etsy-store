"""Entity resolution for AI answers. AI output is untrusted text: we only pattern-match it, never act on it."""

from __future__ import annotations

import re
from collections import Counter
from urllib.parse import urlsplit

from ..models import ClientProfile
from ..checks.schema import digits

_LEGAL = re.compile(r"\b(llc|inc|incorporated|ltd|limited|corp|co|pllc|pc|llp|dds|dmd)\b")
_GENERIC = {"dental", "dentist", "family", "plumbing", "plumber", "law", "legal", "salon", "hair", "the", "and", "of",
            "group", "services", "service", "care", "clinic", "office", "offices", "restaurant", "cafe", "studio", "co"}


def norm_name(s: str) -> str:
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("&", " and "))
    s = _LEGAL.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def host(url: str) -> str:
    return (urlsplit(url if "//" in url else "//" + url).hostname or "").lower().removeprefix("www.")


def is_distinctive(name: str) -> bool:
    """Distinctive = at least two non-generic tokens. '<Surname> Plumbing' is NOT (common surname + category word)."""
    toks = norm_name(name).split()
    return sum(1 for t in toks if t not in _GENERIC and len(t) > 2) >= 2


def match_client(text: str, cited_urls: list[str], profile: ClientProfile) -> dict:
    """Return {'verified': bool, 'name_match': bool, 'cited': bool, 'method': str}.

    verified   = client domain cited, OR phone digits present, OR street address present  (hard identifiers)
    name_match = normalised name (or alias) present AND (distinctive name OR the city appears near it)
    cited      = client's domain appears among cited URLs
    """
    client_host = host(profile.website)
    cited = any(host(u) == client_host or host(u).endswith("." + client_host) for u in cited_urls)
    low = text.lower()
    phone = digits(profile.phone)
    phone_hit = bool(phone) and phone in re.sub(r"\D", "", text)
    street = norm_name(profile.address.street)
    street_hit = bool(street) and not profile.service_area_business and street in norm_name(text)
    verified = cited or phone_hit or street_hit

    ntext = norm_name(text)
    name_hit = False
    for n in [profile.name, *profile.brand_aliases]:
        nn = norm_name(n)
        if not nn or nn not in ntext:
            continue
        if is_distinctive(n) or verified:
            name_hit = True
        else:  # generic name: require the city within ~200 chars of the name mention
            i = ntext.find(nn)
            window = ntext[max(0, i - 200): i + len(nn) + 200]
            name_hit = norm_name(profile.city) in window if profile.city else False
        if name_hit:
            break
    method = "domain" if cited else "phone" if phone_hit else "address" if street_hit else "name" if name_hit else "none"
    return {"verified": verified, "name_match": name_hit or verified, "cited": cited, "method": method}


_LIST_ITEM = re.compile(
    r"^\s*(?:\d+[.)]|[-*\u2022])\s*\**\[?([A-Z][^*\n\[\]:\u2013\u2014(]{2,60}?)\**\]?"
    r"(?:\s*(?::|\u2013|\u2014|\()|\s+-\s|\s*$)", re.M)


def extract_listed_entities(text: str) -> list[str]:
    """Heuristic: names from numbered/bulleted list items. Used for share-of-voice among ALL named businesses."""
    names = []
    for m in _LIST_ITEM.finditer(text):
        n = re.sub(r"\s+", " ", m.group(1)).strip(" .-*")
        if 2 < len(n) <= 60:
            names.append(n)
    return names


def top_entities(all_runs: list[list[str]], n: int = 10) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for names in all_runs:
        for name in set(norm_name(x) for x in names if x):
            c[name] += 1
    return c.most_common(n)


def cited_domains(all_urls: list[list[str]], n: int = 15) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for urls in all_urls:
        for d in {host(u) for u in urls if u}:
            if d:
                c[d] += 1
    return c.most_common(n)
