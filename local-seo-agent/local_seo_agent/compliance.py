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

from .markets import market_for, out_of_scope_note
from .models import ClientProfile
from .verticals import vertical_for


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
    ("review-incentive", "Incentivised reviews are banned by Google, Trustpilot, Checkatrade and Yell, and are lawful in the UK only if the incentive is prominently disclosed; this tool never proposes them.",
     re.compile(r"\b(discount|gift ?card|coupon|free|cash|reward|prize|raffle)\b.{0,50}\b(for|in exchange for|if they leave)\b.{0,25}\breview", re.I | re.S)),
    ("review-suppression", "Suppressing or removing legitimate negative reviews by deception is prohibited.",
     re.compile(r"\b(suppress|bury|hide|delete)\b.{0,30}\b(negative|bad)\s+reviews?\b", re.I | re.S)),
    ("staff-review-quota", "Staff review quotas, leaderboards and scripts naming staff in reviews are banned by Google (reported 2026-04 policy update: verify).",
     re.compile(r"\b(quota|leaderboard|target|bonus)\b.{0,40}\b(staff|employees?|team)\b.{0,40}\breviews?\b|\b(staff|employees?|team)\b.{0,40}\b(quota|leaderboard|bonus)\b.{0,40}\breviews?\b", re.I | re.S)),
    ("outcome-guarantee", "Outcome guarantees ('we will win your case', guaranteed results) are misleading; regulators (SRA, GDC, ASA) prohibit them.",
     re.compile(r"\bguarantee[sd]?\b.{0,30}\b(win|results?|outcome|approval|cure|success)\b", re.I | re.S)),
    ("pom-advertising", "UK: prescription-only medicines (e.g. Botox/Dysport/Azzalure) cannot be advertised to the public (CAP 12.12). Offer an 'anti-wrinkle consultation' instead.",
     re.compile(r"\b(botox|dysport|azzalure|bocouture|vistabel|botulinum)\b", re.I)),
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
    ("superlative-unsupported", "Unsupported superlative (#1 / best in / award-winning) without a client-supplied fact "
     "(UK: CAP 3.7 and 3.32-3.36 require evidence; US: FTC substantiation).",
     re.compile(r"(#\s*1\b|number one|\bbest in\b|award[- ]winning|top[- ]rated|leading provider|\bleading\b.{0,20}\bin\b|cheapest)", re.I)),
    ("pom-advertising", "UK: Botox/Dysport/Azzalure and other prescription-only medicines cannot be advertised to the public (CAP 12.12).",
     re.compile(r"\b(botox|dysport|azzalure|bocouture|vistabel|botulinum)\b|#botox", re.I)),
    ("outcome-guarantee", "Outcome guarantee (e.g. 'we will win your case', 'guaranteed results').",
     re.compile(r"\bguarantee[sd]?\b.{0,30}\b(win|results?|outcome|approval|cure|success)\b|\bwe(?:'ll| will) win\b", re.I | re.S)),
]

_HEALTH_REPLY = re.compile(
    r"(your (appointment|visit|treatment|procedure|diagnosis|case|consultation|surgery|root canal|filling|implant|"
    r"matter|conveyancing|divorce|claim)|as (our|a) (patient|client)|when you (came|visited) (in )?(for|to)|"
    r"\b\d{1,2}(st|nd|rd|th)? (of )?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b)", re.I)

_NUM = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")


def check_request(text: str, market: str = "US") -> list[Violation]:
    seen: set[str] = set()
    out: list[Violation] = []
    for code, msg, pat in _REQUEST_RULES:
        if code == "pom-advertising" and market != "UK":
            continue  # POM brand advertising is a UK (CAP/MHRA) rule; US rules differ and are not encoded
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
    uk_market = market_for(profile).is_uk
    facts_text = " ".join(profile.facts).lower()
    for code, msg, pat in _DRAFT_RULES:
        m = pat.search(text)
        if not m:
            continue
        if code == "pom-advertising" and not uk_market:
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

    flags = vertical_for(profile)["compliance"]
    if kind == "review-reply" and ({"hipaa_replies", "confidentiality_replies", "confidential_replies"} & set(flags)) \
            and _HEALTH_REPLY.search(text):
        out.append(Violation("confidential-reply", "Reply confirms or discusses a patient/client relationship "
                             "(HIPAA/bar confidentiality risk; UK: GDC/SRA confidentiality). Use a generic reply and take details offline.",
                             _HEALTH_REPLY.search(text).group(0)[:80]))
    return out


def draft_warnings(text: str, profile: ClientProfile, kind: str = "generic") -> list[str]:
    """Non-blocking notes shown next to a draft (a human decides)."""
    notes: list[str] = []
    if kind == "review-request" and market_for(profile).is_uk:
        if not re.search(r"\b(stop|unsubscribe|opt[- ]?out)\b", text, re.I):
            notes.append("UK: a review request sent by email/SMS may count as direct marketing under PECR (ICO position "
                         "unconfirmed). Add sender identity and an opt-out, and confirm consent/soft opt-in before sending.")
    return notes


def jurisdiction_warning(profile: ClientProfile) -> str:
    oos = out_of_scope_note(profile)
    if oos:
        return oos
    m = market_for(profile)
    if m.is_uk:
        return ("UK: guidance reflects research on the DMCC Act 2024, the ASA/CAP Code, UK GDPR/PECR and sector regulators "
                "(see Reference facts); it is not legal advice. Items tagged [LAWYER] need a qualified UK solicitor. "
                "Scotland, Northern Ireland and some sectors (vets, funerals, estate agents, childcare) have rules not "
                "built into this tool.")
    return ""
