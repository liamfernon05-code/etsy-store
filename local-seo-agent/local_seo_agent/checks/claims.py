"""Marketing-claim scanner for cosmetic / body-contouring copy (UK ASA/CAP + DMCC context).

Patterns come from the BBL regulation research (research/bbl/B1-regulation.md) AS CORRECTED by its critique (critique-B1.md),
which found the first-draft patterns flagged compliant wording ("non-surgical Brazilian butt lift", "reduce fat intake",
"permanent address") and missed the client's real phrases ("safest and fastest", "reduces the appearance of cellulite").
They are HINTS that route a phrase to a human, not legal findings. Every hit carries the snippet, the rule family and a safer
rewrite, and must be read in context.

Tiers (what the agent will not write / flags hardest):
  REFUSE tier  safest, risk-free, guarantees; erase/remove/reduce cellulite; spot-reduction / inch-loss (CAP 13.9); permanent results;
               fake urgency; false medical or regulatory status.        -> ERROR when found on existing copy
  WARN tier    bare "safe", "painless", "no downtime"; skin tightening/lifting; surgical-equivalence/volume claims; detox/lymphatic;
               medicinal claims; BBL wording without a clarifier; ordinary time-limited offers and % discounts (stricter for surgery/injectables).
CAP rule numbers are quoted only where two sources agree; testimonial-rule numbering differs between sources and editions, so we
cite the topic, not a number.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..models import clean

I = re.I

PATTERNS: dict[str, re.Pattern] = {
    # --- REFUSE tier ---
    "cellulite": re.compile(
        r"\bcellulite\W+(?:\w+\W+){0,2}?(?:reduc\w*|remov\w*|eliminat\w*|smooth\w*|bust\w*|gone|free)\b|"
        r"\b(?:erase|eliminate|remov\w*|banish|smooth\w*|reduc\w*|treat\w*|tackl\w*|target\w*|melt\w*|dissolv\w*|destroy\w*|get\s+rid\s+of|say\s+goodbye\s+to)\s+"
        r"(?:your\s+|the\s+|any\s+)?(?:appearance\s+of\s+|look\s+of\s+)?(?:stubborn\s+)?(?:cellulite|orange[\s-]peel|dimpl\w+)\b", I),
    "fat_inch": re.compile(
        r"\b(?:lose|drop|shed|melt|burn|dissolv\w*|destroy\w*|zap)\w*\s+(?:\w+\s+){0,2}(?:fat|inches|cm)\b|\binch(?:es)?\s+loss\b|\bspot\s+reduction\b|"
        r"\bfat\s+(?:melting|dissolving|destroy\w*|annihilat\w*|loss)\b", I),
    "safest_absolute": re.compile(
        r"\b(?:safest|safer\s+than|(?:100\s?%|completely|totally|perfectly|absolutely)\s+safe|risk[\s-]?free|no\s+risks?|zero\s+(?:risk|side[\s-]effects?|infection)|"
        r"0\s?%\s+(?:infection|complications?)|guarantee[ds]?\s+(?:results?|outcome|satisfaction|to\s+(?:work|lift)))\b", I),
    "permanent": re.compile(
        r"\bpermanent(?:ly)?\s+(?:\w+\s+){0,3}(?:results?|fat|loss|lift|tighten\w*|cellulite|contour\w*)|\b(?:results?|effects?)\s+(?:\w+\s+){0,2}(?:are\s+)?permanent|"
        r"\blast\s+(?:a\s+)?lifetime\b|\bresults?\s+(?:last\s+)?(?:forever|for\s+life)\b", I),
    "fake_urgency": re.compile(
        r"\b(?:last\s+(?:chance|few\s+slots?)|only\s+\d+\s+(?:slots?|spaces?|appointments?)\s+left|offer\s+ends\s+(?:today|tonight|midnight|tomorrow)|hurry|countdown|"
        r"(?:price|prices)\s+(?:rise|increase)\s+(?:on|from|tomorrow|next)|before\s+(?:the\s+)?price\s+(?:increase|rise))\b", I),
    "medical_claim_by_nonmedical": re.compile(
        r"\b(?:clinically\s+proven|medically\s+proven|doctor[\s-]?approved|scientifically\s+proven|fda[\s-]approved|nhs[\s-]approved|cqc[\s-]approved)\b", I),
    # --- WARN tier ---
    "safe_bare": re.compile(r"\bsafe(?:ly)?\b|\bpain[\s-]?free\b|\bpainless\b|\bno\s+down[\s-]?time\b|\bminimal\s+(?:pain|discomfort)\b", I),
    "skin_tighten": re.compile(r"\b(?:tighten\w*|firm\w*|lift\w*)\s+(?:your\s+)?(?:loose\s+|sagging\s+)?skin\b|\bboost\s+your\s+rear\s+appeal\b", I),
    "surg_equiv_volume": re.compile(
        r"\b(?:same|similar|identical|comparable)\s+(?:results?|effects?)\s+(?:as|to)\s+(?:a\s+|the\s+)?(?:surgical\s+)?(?:bbl|brazilian\s+butt\s+lift|surgery|butt\s+lift)|"
        r"\b(?:non[\s-]?surgical\s+)?alternative\s+to\s+(?:a\s+)?(?:bbl|brazilian\s+butt\s+lift|surgery)|"
        r"\b(?:adds?|increas\w*|enlarg\w*|plump\w*)\s+(?:the\s+)?(?:volume|size|fullness)\b|\b(?:bigger|fuller|rounder)\s+(?:bum|butt|booty)\b", I),
    "detox_lymphatic": re.compile(r"\b(?:detox\w*|flush\w*\s+(?:out\s+)?toxins|toxins?|wee\s+it\s+out|drain\w*\s+(?:the\s+)?fat)\b", I),
    "medicinal_claim": re.compile(
        r"\b(?:treat(?:s|ing)?|cure[sd]?|heal(?:s|ing)?)\s+(?:your\s+)?(?:lymphoedema|lymphedema|water\s+retention|varicose\w*|stretch\s+marks|swelling)\b", I),
    "time_pressure": re.compile(
        r"\b(?:offer|deal|price|discount|promo(?:tion)?)s?\s+(?:ends?|expires?|valid)\b|\blimited\s+(?:time|slots?|spaces?|availability|offer)\b|"
        r"\bdon'?t\s+(?:miss|sleep\s+on)\b|\bblack\s+friday\b|\bcyber\s+monday\b|\bflash\s+sale\b|\bbook\s+(?:now|today)\s+(?:and|&)\s+save\b", I),
    "price_inducement": re.compile(
        r"(?<!\w)(?:save\s+(?:up\s+to\s+)?(?:£|\d+\s?%)|\d{1,3}\s?%\s*off|up\s+to\s+\d{1,3}\s?%|(?:£|€)\s?\d+\s*off|(?:buy|book)\s+(?:one|1|two|2)\s+get\s+(?:one|1|two|2)|"
        r"two[\s-]for[\s-]one|2\s?(?:for|4)\s?1|bogof|multi[\s-]?buy|package\s+deal|bundle\s+(?:and|&)\s+save|"
        r"win\s+a\s+(?:free\s+)?(?:treatment|procedure)|prize\s+draw|giveaway)(?!\w)", I),
    "finance_promo": re.compile(
        r"\b(?:from\s+(?:just\s+|only\s+)?£\s?\d+\s*(?:/|a|per)\s*(?:month|mo|week)|(?:£\s?\d+\s*(?:/|a|per)\s*month)|(?:0\s?%|zero)\s+(?:finance|interest|apr)|interest[\s-]free|"
        r"(?:buy\s+now\s+pay\s+later|bnpl|klarna|clearpay|payl8r|deposit\s+from\s+£\s?\d+|pay\s+in\s+(?:3|three|4|four|6|12)\s+(?:instalments|installments)|spread\s+the\s+cost|finance\s+available))\b", I),
    "body_image": re.compile(
        r"\b(?:transform\s+your\s+(?:body|life)|dream\s+body|perfect\s+(?:body|bum|booty|figure|peach\w*)|quick\s+fix|effortless(?:ly)?|exclusive\s+opportunity)\b", I),
    "before_after_cues": re.compile(
        r"\b(?:before\s*(?:/|&|and|\+|-|vs\.?)\s*after|results?\s+gallery|real\s+results?|client\s+results?|transformations?)\b", I),
    "revolutionary_novelty": re.compile(r"\b(?:revolution(?:ary)?|breakthrough|latest\s+technology|cutting[\s-]edge|world[\s-]first)\b", I),
    # surgery-specific
    "surgery_abroad": re.compile(
        r"\b(?:turkey|t[uü]rkiye|istanbul|antalya|izmir|medical\s+tourism|cosmetic\s+tourism|all[\s-]inclusive\s+(?:package|surgery)|vip\s+transfer|hotel\s+(?:stay\s+)?included)\b", I),
}

# BBL wording needs a clarifier nearby (critic B1): flag BBL terms in the page's headline areas without one.
BBL_TERM = re.compile(r"\b(?:brazilian\s+)?(?:butt|booty|bum)[\s-]?lift\b|\bbbl\b", I)
BBL_CLARIFIER = re.compile(r"non[\s-]?surgical|non[\s-]?invasive|no\s+(?:surgery|needles?|injections?|fat\s+transfer)|without\s+surgery", I)
# the word "BBL"/"booty lift" in the brand name itself is unavoidable: we ask for an explicit clarifier near the first mention.

NEGATORS = re.compile(r"(?:\bcannot\b|\bcan'?t\b|\bnever\b|\bdo(?:es)?\s+not\b|\bdon'?t\b|\bdoesn'?t\b|\bno\s+longer\b|\bwithout\b|\bwe\s+won'?t\b|\bnot\b)\s*(?:\w+\s+){0,4}$", I)

REFUSE_TIER = {"cellulite", "fat_inch", "safest_absolute", "permanent", "fake_urgency", "medical_claim_by_nonmedical"}
SURGICAL_ERROR = {"time_pressure", "price_inducement", "body_image", "safe_bare", "surgery_abroad", "finance_promo"}

RULE_REFS = {
    "cellulite": ("ASA/CAP: no convincing evidence that devices or cosmetic treatments treat, remove or reduce cellulite or its appearance (any wording)", "Remove the claim unless you hold product-specific human-trial evidence; describe what the treatment involves, not an outcome."),
    "fat_inch": ("CAP 13.9 and CAP section 13: claims that fat or inches can be lost from specific body parts are not accepted without rigorous human trials", "Remove spot-reduction, fat-melting and inch-loss claims."),
    "safest_absolute": ("CAP 3.1/3.7: 'safest', 'risk-free' and guarantees are absolute or comparative claims needing proof; ASA 2025 rulings held absolute safety claims trivialise risk", "Remove. If you say 'safe', qualify it and tie it to risk screening; never 'the safest'."),
    "permanent": ("CAP 3.7/12.1: permanence of non-invasive results is unlikely to be substantiable", "Remove 'permanent'/'lifetime' result claims; say results vary and may need maintenance."),
    "fake_urgency": ("CAP 1.3 (ASA rulings April 2025 on cosmetic-intervention ads) and DMCC Act unfair practices (false urgency)", "Remove countdowns, 'last slots' and deadline pressure."),
    "medical_claim_by_nonmedical": ("CAP 3.1/12.1: registration, approval and 'proven' claims must be true and evidenced", "Remove unless you can evidence it; never imply NHS/regulator approval."),
    "safe_bare": ("ASA 2025 rulings: 'safe', 'no downtime', 'painless' can trivialise risk; acceptable only as qualified, evidenced statements", "Describe what to expect honestly, including side effects and recovery."),
    "skin_tighten": ("CAP 3.7/12.1: tightening/lifting claims need human-trial evidence for the specific device and body area", "Say what the programme involves; avoid outcome claims without evidence."),
    "surg_equiv_volume": ("CAP 3.1: implying surgical-equivalent results or added volume from a surface device is likely misleading", "State that it is not comparable to surgery and does not add volume; avoid 'alternative to BBL' without a clear qualifier."),
    "detox_lymphatic": ("CAP section 12: detox and medicinal-type claims need evidence", "Remove detox/toxin claims; describe massage or lymphatic techniques factually."),
    "medicinal_claim": ("CAP section 12 (medicinal claims for non-medical products/services)", "Remove claims to treat or cure a condition."),
    "time_pressure": ("CAP 1.3 (documented for liquid-BBL/injectable ads) and consumer law; stricter for surgery and injectables", "Avoid pressure tactics; give people time to decide."),
    "price_inducement": ("CAP 1.3 / GMC guidance on inducements (surgery); DMCC price rules", "Be careful with %-off, multi-buy and prize offers; state the total price clearly. Not for surgery or injectables."),
    "finance_promo": ("CAP price rules; FCA rules on consumer credit and BNPL promotions [LAWYER]", "Lead with the total price; give representative finance terms."),
    "body_image": ("ASA 2025 rulings (e.g. 'perfect peachy look', 'exclusive opportunity'): body-image pressure can be socially irresponsible", "Use neutral, factual language about the service."),
    "before_after_cues": ("ASA/CAP before-and-after guidance; CAP section 3 testimonial rules (numbering differs between editions: verify); UK GDPR for photos", "Hold signed dated consent and unretouched originals; same lighting/pose; state sessions and interval."),
    "revolutionary_novelty": ("CAP 3.7: novelty claims need evidence", "Remove or substantiate."),
    "surgery_abroad": ("CAP 1.3 / GMC guidance; ASA enforcement on surgery packages", "Do not market surgery abroad as a holiday package."),
    "bbl_clarity": ("CAP 3.1: 'BBL'/'Brazilian butt lift' means fat-transfer surgery to most readers, and Scotland's 2026 Act uses 'non-surgical BBL' for filler procedures", "State near the first mention: non-surgical, no injections, no fat transfer, results not comparable to surgery. Avoid 'non-surgical BBL' in titles and descriptions."),
}


@dataclass
class Hit:
    category: str
    snippet: str
    negated: bool
    page: str = ""


def scan_claims(text: str, page: str = "", surgical: bool = False) -> list[Hit]:
    """One hit per (category, matched phrase). `text` should be visible text (HTML stripped). Surgery-only patterns are skipped otherwise."""
    t = text.replace("’", "'").replace("‘", "'")
    hits: list[Hit] = []
    seen: set[tuple[str, str]] = set()
    for cat, pat in PATTERNS.items():
        if cat == "surgery_abroad" and not surgical:
            continue
        for m in pat.finditer(t):
            neg = bool(NEGATORS.search(t[max(0, m.start() - 40): m.start()]))
            key = (cat, m.group(0).lower())
            if key in seen:
                continue
            seen.add(key)
            hits.append(Hit(cat, clean(t[max(0, m.start() - 35): m.end() + 35], 150), neg, page))
    return hits


def bbl_clarity_hits(title: str, h1s: list[str], meta: str, body: str, page: str = "") -> list[Hit]:
    """BBL wording in the headline areas (title / H1 / meta / first 300 body characters) with NO clarifier anywhere in those
    areas. One hit per page at most."""
    areas = [title or "", *(h1s or []), meta or "", (body or "")[:300]]
    if BBL_CLARIFIER.search(" ".join(areas)):
        return []
    for a in areas:
        m = BBL_TERM.search(a)
        if m:
            return [Hit("bbl_clarity", clean(a[max(0, m.start() - 35): m.end() + 35], 150), False, page)]
    return []


def severity_for(category: str, treatment_type: str, negated: bool) -> str:
    """ERROR / WARN / INFO. REFUSE-tier claims are ERROR; surgical and injectable copy is held to the stricter 2025-ruling standard."""
    if negated:
        return "INFO"
    if category in REFUSE_TIER:
        return "ERROR"
    if treatment_type in ("surgical", "injectable") and category in SURGICAL_ERROR:
        return "ERROR"
    if category == "revolutionary_novelty":
        return "INFO"
    return "WARN"
