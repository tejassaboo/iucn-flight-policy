"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "iucn" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 24-scenario row).
MIX = {"easy": 5, "boundary_twin": 6, "multi_rule": 4, "hidden_clause": 2, "distractor": 2, "refusal": 2, "flag": 3}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has. It has no rule on travellers
# flying together and no overnight-stop rule for booking, so neither overlay is required.
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "date_arithmetic": 2, "month_end": 1, "personal_travel": 1, "dearer_option": 2,
    "upgrade_not_taken": 2, "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "train", "rail", "railway", "station", "donor", "grant", "medical", "doctor", "certificate", "lounge", "premium",
    "plus", "first", "business", "economy", "home", "leave", "holiday", "minister", "vip", "host", "director",
    "general", "global", "regional", "manager", "line", "budget", "holder", "nonstop", "direct", "route",
    "connection", "stopover", "significant", "savings", "flexible", "change", "risk", "security", "health",
    "epidemic", "personal", "intern", "seconded", "staff", "miles", "weeks", "fortnight", "advance", "flying",
    "time", "cost", "centre", "agent", "online", "carbon",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.StaffCategory, contract.DutyStation, contract.Rank, contract.Purpose,
                     contract.PersonalPart, contract.Payer, contract.DonorCabinTerms, contract.RiskCheck,
                     contract.SignOffSubject]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section and approver NONE).
MAX_PASS_ALWAYS_FLAG = 1  # vetch-lynn, the one hold over unclear words
MAX_PASS_ALWAYS_LOWEST = 4  # amber-tor, bracken-weir, ivory-garth, quillwort-bend

# Hand-built duration cases beyond the automatic both-sides tests: (rule, outbound scheduled minutes per
# flight, layovers, expected True / False / None for unclear).
DURATION_CASES = [
    ("premium-economy", [481], [], True),
    ("premium-economy", [480], [], False),
    ("premium-economy", [50, 445], [95], True),  # neither flight is over, the total flying time is
    ("premium-economy", [240, 240], [300], False),  # ground time is not flying time: 480 in the air
    ("premium-economy", [200, 200, 81], [60, 60], True),
    ("premium-economy", [100, 300], [200], False),
]
