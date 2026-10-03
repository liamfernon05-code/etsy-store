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


def get_vertical(key: str) -> dict:
    return VERTICALS.get(key, VERTICALS["generic"])


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
