"""Per-vertical configuration: schema type, directories, probe terms, compliance flags.

Directory lists are STARTING POINTS informed by the research (MED-LOW confidence for which sources each
AI assistant uses). The AI probe measures which domains actually get cited, then refines this list.
"""

from __future__ import annotations

CORE_DIRECTORIES = [
    ("Google Business Profile", "Feeds Google Maps/pack, Gemini and AI Overviews. Highest priority."),
    ("Bing Places", "Feeds Bing/Copilot and several other assistants."),
    ("Apple Business Connect", "Feeds Apple Maps and Siri."),
    ("Yelp", "Licensed to ChatGPT (2026-07); frequently in local AI grounding."),
    ("Facebook", "Commonly surfaced in local results."),
]

VERTICALS: dict[str, dict] = {
    "dentist": {
        "label": "Dentist / dental practice",
        "schema_types": ["Dentist", "MedicalBusiness", "LocalBusiness"],
        "preferred_schema": "Dentist",
        "sab_default": False,
        "directories": [("Healthgrades", ""), ("Zocdoc", "Booking marketplace"), ("RateMDs", ""),
                        ("American Dental Association Find-a-Dentist", "US")],
        "probe_terms": ["dentist", "emergency dentist", "family dentist", "teeth whitening", "dental implants"],
        "singular": "dentist",
        "compliance": ["ymyl", "hipaa_replies", "health_claims"],
        "gbp_checks": ["Insurance accepted listed", "New-patient booking link", "Languages spoken"],
        "lsa": False,
    },
    "lawyer": {
        "label": "Law firm / attorney",
        "schema_types": ["LegalService", "Attorney", "LocalBusiness"],
        "preferred_schema": "LegalService",
        "sab_default": False,
        "directories": [("Avvo", ""), ("Justia", ""), ("FindLaw", ""), ("Martindale-Hubbell", ""),
                        ("State bar directory", "Also check bar advertising rules")],
        "probe_terms": ["lawyer", "personal injury lawyer", "family law attorney", "criminal defense attorney"],
        "singular": "lawyer",
        "compliance": ["ymyl", "bar_rules", "confidentiality_replies"],
        "gbp_checks": ["Free consultation noted", "Practice areas as services", "Bar licence on site"],
        "lsa": True,
    },
    "plumber": {
        "label": "Plumber / home services",
        "schema_types": ["Plumber", "HomeAndConstructionBusiness", "LocalBusiness"],
        "preferred_schema": "Plumber",
        "sab_default": True,
        "directories": [("Angi", ""), ("HomeAdvisor", ""), ("Thumbtack", ""), ("Better Business Bureau", ""),
                        ("Nextdoor", "")],
        "probe_terms": ["plumber", "emergency plumber", "water heater repair", "drain cleaning", "leak repair"],
        "singular": "plumber",
        "compliance": ["licensing_display"],
        "gbp_checks": ["Service areas set (max 20)", "Services with descriptions", "24/7 hours accuracy"],
        "lsa": True,
    },
    "restaurant": {
        "label": "Restaurant / cafe",
        "schema_types": ["Restaurant", "FoodEstablishment", "LocalBusiness"],
        "preferred_schema": "Restaurant",
        "sab_default": False,
        "directories": [("TripAdvisor", ""), ("OpenTable", "If reservations"), ("DoorDash/UberEats", "Delivery listings"),
                        ("Local press best-of lists", "Frequently cited by AI answers")],
        "probe_terms": ["restaurant", "best brunch", "date night restaurant", "family restaurant"],
        "singular": "restaurant",
        "compliance": [],
        "gbp_checks": ["Menu link (HTML, not PDF)", "Reservation link", "Dine-in/takeout attributes", "Special hours"],
        "lsa": False,
    },
    "salon": {
        "label": "Hair / beauty salon",
        "schema_types": ["HairSalon", "BeautySalon", "HealthAndBeautyBusiness", "LocalBusiness"],
        "preferred_schema": "HairSalon",
        "sab_default": False,
        "directories": [("Fresha / Booksy / Vagaro", "Booking marketplaces"), ("StyleSeat", ""), ("Instagram", "Portfolio")],
        "probe_terms": ["hair salon", "balayage", "barber", "hair colorist", "bridal hair"],
        "singular": "hair salon",
        "compliance": [],
        "gbp_checks": ["Booking link", "Services and prices", "Staff/portfolio photos"],
        "lsa": False,
    },
    "electrician": {
        "label": "Electrician",
        "schema_types": ["Electrician", "HomeAndConstructionBusiness", "LocalBusiness"],
        "preferred_schema": "Electrician",
        "sab_default": True,
        "directories": [("Angi", ""), ("Thumbtack", ""), ("Better Business Bureau", "")],
        "probe_terms": ["electrician", "emergency electrician", "panel upgrade", "rewiring", "ev charger installation"],
        "singular": "electrician",
        "compliance": ["licensing_display"],
        "gbp_checks": ["Service areas set (max 20)", "Services with descriptions"],
        "lsa": True,
    },
    "heating_engineer": {
        "label": "Heating / HVAC engineer",
        "schema_types": ["HVACBusiness", "HomeAndConstructionBusiness", "LocalBusiness"],
        "preferred_schema": "HVACBusiness",
        "sab_default": True,
        "directories": [("Angi", ""), ("Thumbtack", ""), ("Better Business Bureau", "")],
        "probe_terms": ["hvac contractor", "furnace repair", "ac repair", "water heater installation"],
        "singular": "hvac contractor",
        "compliance": ["licensing_display"],
        "gbp_checks": ["Service areas set (max 20)", "24/7 hours accuracy"],
        "lsa": True,
    },
    "generic": {
        "label": "Local business (generic)",
        "schema_types": ["LocalBusiness"],
        "preferred_schema": "LocalBusiness",
        "sab_default": False,
        "directories": [("Industry-specific directories", "Add 3-5 relevant to the niche"), ("Better Business Bureau", "")],
        "probe_terms": [],
        "singular": "business",
        "compliance": [],
        "gbp_checks": [],
        "lsa": False,
    },
}


ALIASES = {"solicitor": "lawyer", "attorney": "lawyer", "law_firm": "lawyer", "trades": "plumber", "dental": "dentist",
           "hairdresser": "salon", "barber": "salon", "beauty": "salon", "takeaway": "restaurant", "cafe": "restaurant",
           "hvac": "heating_engineer", "gas_engineer": "heating_engineer"}


def canonical_vertical(key: str) -> str:
    k = (key or "generic").strip().lower().replace(" ", "_")
    return ALIASES.get(k, k if k in VERTICALS else "generic")


def get_vertical(key: str) -> dict:
    return VERTICALS[canonical_vertical(key)]


# UK overlay: UK-English search terms (the critic replaced Americanisms), UK directories by NAME (statuses live in
# uk.DIRECTORIES), compliance packs (see compliance.py / checks/uk_checks.py) and UK-specific GBP checks.
UK_OVERLAY: dict[str, dict] = {
    "dentist": {
        "label": "Dentist / dental practice (UK)",
        "probe_terms": ["NHS dentist", "emergency dentist", "private dentist", "dental implants", "teeth whitening",
                        "Invisalign", "NHS dentist taking new patients", "out of hours dentist"],
        "singular": "dentist",
        "directory_names": ["Google Business Profile", "Bing Places", "Apple Business", "Doctify", "Trustpilot", "Facebook", "Yell"],
        "compliance": ["ymyl", "gdc", "confidential_replies", "asa_cap", "before_after"],
        "gbp_checks": ["Accepting new NHS patients stated (if true)", "Booking link", "Languages spoken", "Opening hours incl. bank holidays"],
        "lsa": False,
    },
    "lawyer": {
        "label": "Solicitor / law firm (UK)",
        "probe_terms": ["solicitor", "conveyancing solicitor", "family law solicitor", "wills and probate solicitor",
                        "employment solicitor", "personal injury solicitor", "immigration solicitor", "divorce solicitor"],
        "singular": "solicitor",
        "directory_names": ["Google Business Profile", "Bing Places", "Apple Business", "Legal 500 / Chambers", "Trustpilot", "Facebook", "Yell"],
        "compliance": ["ymyl", "sra", "confidential_replies", "asa_cap"],
        "gbp_checks": ["Primary category 'Solicitor'", "Practice areas as services", "Fee information visible", "Free initial consultation stated (if true)"],
        "lsa": True,  # London only for legal; handled in plan
    },
    "plumber": {
        "label": "Plumber / heating engineer (UK)",
        "probe_terms": ["plumber", "emergency plumber", "gas safe engineer", "boiler repair", "boiler installation",
                        "central heating engineer", "burst pipe plumber", "tradesperson"],
        "singular": "plumber",
        "directory_names": ["Google Business Profile", "Bing Places", "Apple Business", "Checkatrade", "MyBuilder", "TrustATrader",
                            "Which? Trusted Trader", "TrustMark", "Gas Safe Register", "Trustpilot", "Facebook", "Yell"],
        "compliance": ["trade_badges", "dmcc_pricing", "asa_cap"],
        "gbp_checks": ["Service areas set (max 20)", "Services with descriptions", "24/7 hours accuracy", "Gas Safe ID shown (if gas work)"],
        "lsa": True,
    },
    "heating_engineer": {
        "label": "Heating / gas engineer (UK)",
        "probe_terms": ["heating engineer", "boiler repair", "boiler installation", "gas safe engineer", "boiler service",
                        "central heating engineer", "radiator repair"],
        "singular": "heating engineer",
        "directory_names": ["Google Business Profile", "Bing Places", "Apple Business", "Checkatrade", "TrustATrader",
                            "Which? Trusted Trader", "TrustMark", "Gas Safe Register", "Trustpilot", "Facebook", "Yell"],
        "compliance": ["trade_badges", "dmcc_pricing", "asa_cap"],
        "gbp_checks": ["Service areas set (max 20)", "Gas Safe ID shown", "24/7 hours accuracy"],
        "lsa": True,
    },
    "electrician": {
        "label": "Electrician (UK)",
        "probe_terms": ["electrician", "emergency electrician", "EICR certificate", "fuse board upgrade",
                        "consumer unit replacement", "electrical rewire", "NICEIC electrician", "EV charger installation"],
        "singular": "electrician",
        "directory_names": ["Google Business Profile", "Bing Places", "Apple Business", "Checkatrade", "MyBuilder", "TrustATrader",
                            "Which? Trusted Trader", "TrustMark", "NICEIC", "Trustpilot", "Facebook", "Yell"],
        "compliance": ["trade_badges", "dmcc_pricing", "asa_cap"],
        "gbp_checks": ["Service areas set (max 20)", "Scheme membership (NICEIC/NAPIT/SELECT) shown if true"],
        "lsa": True,
    },
    "restaurant": {
        "label": "Restaurant / cafe / takeaway (UK)",
        "probe_terms": ["restaurant", "Sunday roast", "brunch", "Indian takeaway", "fish and chip shop",
                        "gluten free restaurant", "pub lunch", "gastropub"],
        "singular": "restaurant",
        "directory_names": ["Google Business Profile", "Bing Places", "Apple Business", "TripAdvisor", "TheFork", "OpenTable",
                            "Just Eat", "Deliveroo", "Uber Eats", "Good Food Guide", "Hardens / SquareMeal / CAMRA WhatPub",
                            "Food hygiene rating (FHRS/FHIS)", "Facebook", "Yell"],
        "compliance": ["fhrs", "allergens", "asa_cap"],
        "gbp_checks": ["Menu link (HTML, not PDF)", "Reservation link", "Dine-in/takeaway attributes", "Bank holiday hours"],
        "lsa": False,
    },
    "salon": {
        "label": "Hair / beauty salon (UK)",
        "probe_terms": ["hairdresser", "barber", "balayage", "nail bar", "lash lift", "beauty salon", "waxing",
                        "bridal hair and makeup"],
        "singular": "hairdresser",
        "directory_names": ["Google Business Profile", "Bing Places", "Apple Business", "Treatwell", "Fresha", "Booksy", "Facebook", "Yell"],
        "compliance": ["aesthetics_pom", "before_after", "asa_cap"],
        "gbp_checks": ["Booking link", "Services and prices", "Portfolio photos"],
        "lsa": False,
    },
    "generic": {
        "label": "Local business (UK)",
        "probe_terms": [],
        "singular": "business",
        "directory_names": ["Google Business Profile", "Bing Places", "Apple Business", "Facebook", "Yell", "Trustpilot", "Companies House"],
        "compliance": ["asa_cap"],
        "gbp_checks": [],
        "lsa": False,
    },
}


def vertical_for(profile) -> dict:
    """Vertical config merged for the client's market and nation. Same keys as VERTICALS entries plus `directories`
    entries as (name, note, status)."""
    from . import uk
    from .markets import market_for

    key = canonical_vertical(profile.vertical)
    base = dict(VERTICALS[key])
    if not market_for(profile).is_uk:
        base["directories"] = [(n, note, "active") for n, note in [*CORE_DIRECTORIES, *base["directories"]]]
        base["key"] = key
        return base
    ov = UK_OVERLAY.get(key, UK_OVERLAY["generic"])
    base.update({k: v for k, v in ov.items() if k != "directory_names"})
    names = list(ov["directory_names"])
    names += uk.OFFICIAL_BY_NATION.get(key, {}).get(profile.nation or "ENG", [])
    if not profile.nation and key in uk.OFFICIAL_BY_NATION:
        names.append("(nation unknown: set `nation` in client.toml to get the right regulators/listings)")
    dirs = []
    for n in dict.fromkeys(names):
        meta = uk.DIRECTORIES.get(n, {"status": "unverified", "note": ""})
        dirs.append((n, meta.get("note", ""), meta.get("status", "unverified")))
    base["directories"] = dirs
    base["key"] = key
    base["schema_types"] = VERTICALS[key]["schema_types"]
    return base


# Curated LocalBusiness-family @type values (hand-coded; the schema.org vocabulary is CC BY-SA 3.0, so we do
# not vendor it). Extend per client if their vertical is missing.
LOCAL_TYPES = {
    "LocalBusiness", "Dentist", "MedicalBusiness", "Physician", "MedicalClinic", "LegalService", "Attorney",
    "Notary", "Plumber", "Electrician", "HVACBusiness", "RoofingContractor", "GeneralContractor", "Locksmith",
    "HouseCleaning", "MovingCompany", "HomeAndConstructionBusiness", "Restaurant", "FoodEstablishment",
    "CafeOrCoffeeShop", "BarOrPub", "Bakery", "HairSalon", "BeautySalon", "HealthAndBeautyBusiness", "DaySpa",
    "AutoRepair", "AutomotiveBusiness", "AutoDealer", "RealEstateAgent", "AccountingService", "FinancialService",
    "InsuranceAgency", "Store", "ProfessionalService", "VeterinaryCare", "Optician", "ChildCare", "ExerciseGym",
    "SportsActivityLocation", "TravelAgency", "Hotel", "LodgingBusiness", "PhotographyBusiness", "TaxiService",
}
