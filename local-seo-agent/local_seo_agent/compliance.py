"""Deterministic guardrails. These run in code, so they hold even if a model or a user tries to talk around them.

 * check_request(): refuses asks that are fake reviews, guarantees, hidden text / prompt injection, review gating...
 * check_draft(): validates any text the agent drafts (GBP description, review request/reply, page copy)
   before it is shown. Violations block the draft. Heuristic regexes: they reduce risk, they do not replace a human.

US-only research: the FTC fake-review rule is encoded. UK DMCC, EU and AU rules were NOT researched, so
`jurisdiction` is a required client input and non-US clients get an explicit warning.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import ClientProfile
from .verticals import get_vertical


@dataclass(frozen=True)
class Violation:
    code: str
    message: str
    span: str = ""


_REQUEST_RULES: list[tuple[str, str, re.Pattern]] = [
    ("fake-review", "Buying reviews is prohibited (FTC 16 CFR 465; Google policy).",
     re.compile(r"\b(buy|purchase|pay for|order)\b.{0,25}\breviews?\b", re.I | re.S)),
    ("fake-review", "Writing positive reviews for a business to post as customers is prohibited (FTC 16 CFR 465; Google policy).",
     re.compile(r"^(?!.*\b(reply|respond|response|thank|request)\b).*\b(write|generate|create|post)\b.{0,30}\b(5[- ]star|five[- ]star|glowing|positive)\s+reviews\b", re.I | re.S)),
    ("fake-review", "Fake reviews are prohibited.", re.compile(r"\b(fake|fabricated|bogus|paid[- ]for)\s+(5[- ]star\s+|positive\s+)?reviews?\b", re.I)),
    ("guarantee", "No one can guarantee #1 rankings or AI-assistant recommendations.",
     re.compile(r"\bguarantee[sd]?\b.{0,40}(#\s*1|number one|first page|top (spot|rank|result)|rank(ing)?s?|recommend)", re.I | re.S)),
    ("hidden-text", "Hidden text or instructions aimed at AI/crawlers is spam and a known manipulation tactic.",
     re.compile(r"\b(hidden|invisible|white[- ]on[- ]white|display:\s*none)\b.{0,40}\b(text|prompt|instruction|keyword)s?\b", re.I | re.S)),
    ("prompt-injection", "Injecting instructions into pages to steer AI assistants ('AI recommendation poisoning') is prohibited.",
     re.compile(r"\b(inject|plant|embed)\b.{0,40}\b(prompt|instruction)s?\b.{0,60}\b(ai|chatgpt|claude|llm|assistant)", re.I | re.S)),
    ("review-gating", "Review gating (only asking happy customers) violates Google policy.",
     re.compile(r"\b(only|just)\b.{0,30}\b(ask|request|send)\b.{0,50}\b(happy|satisfied|positive|5[- ]star)\b.{0,40}\b(customers?|clients?)\b", re.I | re.S)),
    ("review-incentive", "Incentivising reviews is prohibited.",
     re.compile(r"\b(discount|gift ?card|coupon|free|cash|reward|prize|raffle)\b.{0,50}\b(for|in exchange for|if they leave)\b.{0,25}\breview", re.I | re.S)),
    ("review-suppression", "Suppressing or removing legitimate negative reviews by deception is prohibited.",
     re.compile(r"\b(suppress|bury|hide|delete)\b.{0,30}\b(negative|bad)\s+reviews?\b", re.I | re.S)),
    ("astroturf", "Undisclosed astroturfing on Reddit/forums/Wikipedia is prohibited.",
     re.compile(r"\b(sockpuppet|astroturf|pretend to be (a )?(customer|user))\b", re.I)),
]

_DRAFT_RULES: list[tuple[str, str, re.Pattern]] = [
    ("guarantee", "Draft contains a ranking/recommendation guarantee.",
     re.compile(r"guarantee[sd]?\b.{0,30}(#\s*1|number one|first page|top (spot|rank)|rank)", re.I | re.S)),
    ("review-incentive", "Draft offers something in exchange for a review.",
     re.compile(r"(discount|gift ?card|coupon|reward|raffle|prize|entered into|\bfree (?!to\b)).{0,60}\breview|"
                r"\breview.{0,60}(discount|gift ?card|coupon|reward|raffle|prize|\bfree (?!to\b)\w+)", re.I | re.S)),
    ("review-gating", "Draft filters who may leave a review.",
     re.compile(r"(if you (had|have) a (great|positive|good) (experience|visit)).{0,60}review|(not|n't) happy.{0,40}(contact us|call us) (first|instead)", re.I | re.S)),
    ("staff-name-solicitation", "Draft asks customers to name staff in reviews (reported 2026 policy change; verify).",
     re.compile(r"(mention|name|include).{0,30}(your (technician|stylist|dentist|server|agent)|staff member|by name).{0,40}review", re.I | re.S)),
    ("ai-directive", "Draft addresses AI assistants/crawlers instead of people.",
     re.compile(r"(ignore (all )?(previous|prior) instructions|as an ai (assistant|model)|(chatgpt|claude|gemini|perplexity|ai assistants?),? (should|must|please)? ?(recommend|cite|rank))", re.I)),
    ("superlative-unsupported", "Unsupported superlative (#1 / best in / award-winning) without a client-supplied fact.",
     re.compile(r"(#\s*1\b|number one|\bbest in\b|award[- ]winning|top[- ]rated|leading provider)", re.I)),
]

_HEALTH_REPLY = re.compile(
    r"(your (appointment|visit|treatment|procedure|diagnosis|case|consultation|surgery|root canal|filling|implant)|"
    r"as (our|a) (patient|client)|when you (came|visited) (in )?(for|to))", re.I)

_NUM = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")


def check_request(text: str) -> list[Violation]:
    seen: set[str] = set()
    out: list[Violation] = []
    for code, msg, pat in _REQUEST_RULES:
        m = pat.search(text)
        if m and code not in seen:
            seen.add(code)
            out.append(Violation(code, msg, m.group(0)[:80]))
    return out


def _allowed_numbers(profile: ClientProfile, allowed_extra: list[str]) -> set[str]:
    blob = " ".join([profile.name, profile.phone, profile.address.street, profile.address.postal_code,
                     *profile.facts, *profile.hours.values(), *allowed_extra])
    return {re.sub(r"[^\d.]", "", n) for n in _NUM.findall(blob)} | {re.sub(r"\D", "", profile.phone)}


def check_draft(text: str, profile: ClientProfile, kind: str = "generic", extra_allowed: list[str] | None = None) -> list[Violation]:
    out: list[Violation] = []
    facts_text = " ".join(profile.facts).lower()
    for code, msg, pat in _DRAFT_RULES:
        m = pat.search(text)
        if not m:
            continue
        if code == "superlative-unsupported" and m.group(0).lower() in facts_text:
            continue  # client explicitly supplied this claim
        out.append(Violation(code, msg, m.group(0)[:80]))

    # fabricated statistics guard: any number in the draft must come from client-supplied data
    allowed = _allowed_numbers(profile, extra_allowed or [])
    for n in _NUM.findall(text):
        digits = re.sub(r"[^\d.]", "", n).strip(".")
        if digits and digits not in allowed and len(digits) > 1:
            out.append(Violation("unsupported-number", "Draft contains a number that is not in the client's supplied facts.", n))
            break

    flags = get_vertical(profile.vertical)["compliance"]
    if kind == "review-reply" and ({"hipaa_replies", "confidentiality_replies"} & set(flags)) and _HEALTH_REPLY.search(text):
        out.append(Violation("confidential-reply", "Reply confirms or discusses a patient/client relationship "
                             "(HIPAA/bar confidentiality risk). Use a generic reply and take details offline.",
                             _HEALTH_REPLY.search(text).group(0)[:80]))
    return out


def jurisdiction_warning(profile: ClientProfile) -> str:
    if profile.jurisdiction.upper() in ("US", "USA", "UNITED STATES"):
        return ""
    return (f"Jurisdiction '{profile.jurisdiction}': review-, advertising- and privacy-law guidance in this tool covers the "
            "US only (FTC 16 CFR 465). UK (DMCC Act), EU and AU rules were not researched: have them checked locally.")
