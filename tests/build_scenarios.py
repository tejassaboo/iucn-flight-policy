"""Writes the IUCN scenario JSON files (an authoring aid, not a test; the JSON files are the truth).

    uv run python tests/build_scenarios.py

Flight numbers that a trip record refers to (the flight of the person the traveller accompanies) are read from
the shared world, so they match what search_flights lists. Expected answers are hand-written here;
tests/test_scenarios.py checks them against rules.solve. Every fare is in cents of Swiss francs (CHF).
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from plugin.world import pinned_offers

POLICY = (ROOT / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = ROOT / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def aside(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- clauses -----
HOME_LEAVE = keep(76, 77, None, "the policy covers contractual entitlements such as home leave")
ENVIRONMENT = keep(95, 97, None, "travel in environmentally responsible ways")
COST_EFFECTIVE = keep(108, 110, None, "travel must be cost effective")
DOUBT = keep(125, 126, None, "any doubt about a high security or health risk: do not travel")
NO_MEASURES = keep(157, 158, None, "no measures that reduce the risk to acceptable levels: no travel")
APPLIES = keep(174, 179, None, "the policy applies equally to every category of traveller")
DONOR_RULES = keep(181, 183, None, "the policy applies irrespective of donors' own rules")
TRAIN = keep(220, 221, None, "under four hours by train in one direction: train, not air")
ROUTE = keep(230, 231, None, "the most direct route unless an alternative gives significant financial gains")
BEST_FARE = keep(233, 233, None, "the best possible fare")
FLEXIBILITY = keep(238, 240, None, "dates likely to change: a ticket that can be changed without significant extra cost")
ECONOMY = keep(251, 251, None, "all travel economy, with the exceptions below")
PREMIUM = keep(253, 253, None, "economy plus/premium for total flying time over eight hours")
MEDICAL = keep(255, 262, None, "business with a specialist's certificate held by HR, renewed every six months")
EXCEPTIONAL = keep(263, 267, None, "exceptional business class, authorised before booking by the right director")
DIRECTORS = keep(268, 269, None, "business class of Regional and Global Directors: the Director General")
THIRD_PARTY = keep(270, 272, None, "business when another entity pays and refusing would be inappropriate")
DONOR = keep(274, 274, None, "a donor's willingness to fund business is not sufficient justification")
ANY_FUNDING = keep(276, 276, None, "the business restrictions apply whatever the funding")
NO_FIRST = keep(278, 278, None, "first class travel is not permitted")
ADDED = keep(531, 533, None, "personal travel added with the line manager's agreement; incremental cost borne by the traveller")
PRIMARY_PERSONAL = keep(535, 536, None, "a mainly personal trip: only the work visit's incremental costs are allowable")
CHANGEABLE = keep(548, 550, None, "tickets with options for change when dates are likely to change")
TA = keep(562, 563, "The TA must be approved by the traveller's line manager prior to travel and before any "
          "commitments are made.", "the line manager approves the TA before any commitment")
BUDGET = keep(564, 566, "In cases where travel is funded by a different cost centre than the traveller's own, the t ravel "
              "must also be authorized by the budget holder.", "another unit's budget: its budget holder authorizes too")
NOT_OBVIOUS = keep(568, 571, None, "a choice of ticket that is not obvious is discussed with the supervisor")
ECONOMICAL = keep(581, 582, "alternative proposals should be obtained (different routings, airlines, timings etc.) so as "
                  "to obtain the most economical fare.", "alternative proposals, for the most economical fare")

LOUNGE = aside(413, 413, "The cost of airport lounges is allowed for stopovers exceeding 4 hours.",
               "a long stopover allows a lounge; it does not choose the ticket")
INSURANCE = aside(134, 135, "Please note that Home Leave travel is excluded from the IUCN Global Travel Insurance policy.",
                  "home leave is outside the insurance, not outside the travel policy")
TWO_WEEKS = aside(582, 583, "Air tickets should be booked a minimum of two weeks in advance to avoid premium rates unless "
                  "exceptional circumstances arise.", "fourteen days ahead is two weeks; it decides nothing here")
TRAIN_FIRST = aside(288, 290, "First class travel is authorized on sea, train, bus or other public transportation systems "
                    "for travel durations exceeding two hours", "first class on trains, not on flights")
FOOTNOTE = aside(294, 296, "Economy premium or the equivalent is provided on limited number of airlines",
                 "the footnote describes the cabin; it does not limit the permission")
AIR_MILES = aside(282, 284, "Travellers are, however, encouraged to use such air miles for work-related travel",
                  "air miles may upgrade a ticket; they do not ground a business fare")
TRIP_INSURANCE = aside(536, 538, "IUCN's Global Travel Insurance will only cover the staff member for a personal trip li nked "
                       "to duty travel if they stay in the city where their work will be conducted.",
                       "insurance cover for the personal part, not who buys the flight")
DIRECT_500 = aside(579, 581, "Direct bookings via the internet are only allowed if specified in the applicable Annex I and "
                   "only for air tickets costing CHF 500 or less.", "a booking-channel limit; nothing is booked online here")

# ----- builders -----


def trip(**fields):
    base = {
        "traveller_name": "", "traveller_title": "", "staff_category": "STAFF_MEMBER", "duty_station": "HEADQUARTERS",
        "rank": "STAFF", "origin": "", "destination": "", "travel_date": "", "booking_date": "", "purpose": "",
        "purpose_kind": "MEETING", "personal_part": "NO_PERSONAL_PART", "requested_cabin": "ECONOMY",
        "wants_nonstop": False, "dates_may_change": False, "rail_minutes": 0, "ticket_paid_by": "IUCN",
        "funding": "", "own_cost_centre": True, "donor_cabin_terms": "NOT_STATED", "medical_certificate_date": "",
        "risk_check": "NO_SPECIAL_RISK", "accompanies_flight": "", "sign_offs": [], "notes": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    assert base["funding"], "every trip names its budget"
    return base


def sign(role, name, subject="TRAVEL_AUTHORIZATION"):
    return {"role": role, "name": name, "subject": subject}


def offer(slot, flight, cabin, cents, seats=True, refundable=False):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": cents}
    if not seats:
        data["seats"] = False
    if refundable:
        data["refundable"] = True
    return data


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": slots, "cabins": cabins, "reason_codes": reasons,
            "approvers": approvers, "clauses": clauses, "unclear_phrase": phrase}


def search(origin, destination, date, flights, offers):
    # handbook.json background_offers is 0 and every pinned search lists only its pinned offers, so no filler
    # itinerary can cross a route, cabin or duration test.
    return {"name": "main", "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": 0, "flights": flights, "offers": offers}


def first_flight(scenario_id, search_spec, slot):
    for name, made in pinned_offers(scenario_id, search_spec):
        if name == slot:
            return made.segments[0].flight_number
    raise KeyError(slot)


S = []


def scenario(id, category, overlays, request, trip_, search_spec, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": [search_spec]}, "expected": exp, "must_keep": list(must_keep),
        "distractors": list(distractors), "design_notes": notes,
    })


LOW = ["AIR_TRAVEL", "BOOKING", "CLASS_OF_TRAVEL", "COST_EFFECTIVENESS"]
CLASS = ["AIR_TRAVEL", "CLASS_OF_TRAVEL"]
BOOKED = ["NONE", "LINE_MANAGER"]  # SYNC_NOTES 4': the line manager's TA on file, and NONE
HQ = "Core funds of the traveller's own programme"


def ta(name):
    return [sign("LINE_MANAGER", name)]


# ===== easy (5) =====

scenario(
    "amber-tor", "easy", ["multi_leg", "upgrade_not_taken"],
    "I need to get from Washington Dulles to Sao Paulo on February 15th for the Atlantic Forest restoration workshop, "
    "which opens on the 17th. Economy is fine. I'd like the United nonstop if the policy is OK with it.",
    trip(traveller_name="Daniel Okafor", traveller_title="Senior Programme Officer, Forest Conservation",
         duty_station="REGIONAL_OFFICE", origin="IAD", destination="GRU", travel_date="2027-02-15",
         booking_date="2027-01-11", purpose="Atlantic Forest restoration workshop with Brazilian partners",
         purpose_kind="WORKSHOP", wants_nonstop=True, funding="Core funds of the Washington office's forest programme",
         sign_offs=ta("Rebecca Lindqvist"), notes=["The traveller works in IUCN's Washington, DC office."]),
    search("IAD", "GRU", "2027-02-15", {
        "united": {"carrier": "UA", "depart": "22:10", "minutes": [575]},
        "miami": {"carrier": "AA", "via": ["MIA"], "depart": "07:05", "minutes": [135, 500], "layovers": [85]},
    }, [
        offer("united-economy", "united", "ECONOMY", 148_000),
        offer("miami-economy", "miami", "ECONOMY", 69_000),
    ]),
    expected("BOOK", ["miami-economy"], ["ECONOMY"], ["ALTERNATE_ROUTE_TOO_EXPENSIVE", "COST_SAVINGS", "LOWEST_FARE"],
             BOOKED, ["AIR_TRAVEL", "BOOKING", "COST_EFFECTIVENESS"]),
    [ROUTE, BEST_FARE, ECONOMICAL, TA],
    "The traveller prefers the nonstop, but the Miami connection costs CHF 690 against CHF 1,480: it saves CHF 790, "
    "53% of the nonstop fare, a significant financial gain on any reading of lines 230-231, so the alternative route "
    "and the best possible fare (line 233; line 581, the most economical fare). Both arrive well before the 17th. Total "
    "flying time is over eight hours, so premium economy would be allowed, but economy is what was asked.")

scenario(
    "bracken-weir", "easy", ["date_arithmetic", "month_end"],
    "Nairobi to Johannesburg on December 8th for the transfrontier parks meeting the following day. The cheapest "
    "economy seat, please.",
    trip(traveller_name="Wanjiru Kamau", traveller_title="Programme Officer, Protected Areas",
         duty_station="REGIONAL_OFFICE", origin="NBO", destination="JNB", travel_date="2026-12-08",
         booking_date="2026-11-24", purpose="Transfrontier conservation areas meeting with park authorities",
         funding="Core funds of the Eastern and Southern Africa regional office", sign_offs=ta("Peter Mwangi")),
    search("NBO", "JNB", "2026-12-08", {
        "early": {"carrier": "KQ", "depart": "06:45", "minutes": [240]},
        "morning": {"carrier": "SA", "depart": "09:10", "minutes": [240]},
        "afternoon": {"carrier": "KQ", "depart": "15:30", "minutes": [240]},
    }, [
        offer("early-economy", "early", "ECONOMY", 29_000, seats=False),
        offer("morning-economy", "morning", "ECONOMY", 31_500),
        offer("afternoon-economy", "afternoon", "ECONOMY", 34_200),
    ]),
    expected("BOOK", ["morning-economy"], ["ECONOMY"], ["LOWEST_FARE"], BOOKED, LOW),
    [BEST_FARE, ECONOMY, ECONOMICAL, TA],
    "Economy (line 251) at the best possible fare (line 233): the 06:45 fare is sold out, so South African Airways at "
    "09:10. Booked on November 24th for December 8th: 14 calendar days, two weeks, so the advance-booking line is met "
    "anyway.",
    distractors=[TWO_WEEKS])

scenario(
    "cobble-fern", "easy", [],
    "Please book me Washington Dulles to Bogota on February 3rd for the paramo water-fund workshop the next morning. "
    "I'd like business class if the policy covers it; if not, economy is fine, I have to be there.",
    trip(traveller_name="Laura Mendes", traveller_title="Programme Coordinator, Water and Wetlands",
         duty_station="REGIONAL_OFFICE", origin="IAD", destination="BOG", travel_date="2027-02-03",
         booking_date="2027-01-05", purpose="Water-fund design workshop with Colombian utilities",
         purpose_kind="WORKSHOP", requested_cabin="BUSINESS",
         funding="Core funds of the Washington office's water programme", sign_offs=ta("Rebecca Lindqvist"),
         notes=["The traveller works in IUCN's Washington, DC office."]),
    search("IAD", "BOG", "2027-02-03", {
        "united": {"carrier": "UA", "depart": "08:20", "minutes": [305]},
        "avianca": {"carrier": "AV", "depart": "12:10", "minutes": [305]},
    }, [
        offer("united-economy", "united", "ECONOMY", 41_000),
        offer("united-business", "united", "BUSINESS", 138_000),
        offer("avianca-economy", "avianca", "ECONOMY", 38_500),
        offer("avianca-business", "avianca", "BUSINESS", 124_000),
    ]),
    expected("BOOK", ["avianca-economy"], ["ECONOMY"], ["UPGRADE_NOT_ELIGIBLE"], BOOKED, CLASS),
    [ECONOMY, MEDICAL, EXCEPTIONAL, THIRD_PARTY, TA],
    "All travel is economy (line 251). Business is allowed only with a medical certificate, pre-authorised exceptional "
    "reasons or another entity paying (lines 255-272); none applies, so the cheapest economy fare, Avianca.")

scenario(
    "dapple-rook", "easy", ["dearer_option"],
    "Zurich to Rome on February 9th for the consultation at FAO the next day. The organisers may still move it by a "
    "day or two, so I need a ticket I can change without paying much.",
    trip(traveller_name="Matteo Bianchi", traveller_title="Senior Policy Adviser, Food Systems", origin="ZRH",
         destination="FCO", travel_date="2027-02-09", booking_date="2027-01-12",
         purpose="Consultation on nature-positive food systems at FAO", dates_may_change=True, rail_minutes=425,
         funding=HQ, sign_offs=ta("Ines Moreau"),
         notes=["FAO has said the consultation may move to February 11th or 12th."]),
    search("ZRH", "FCO", "2027-02-09", {
        "early": {"carrier": "LX", "depart": "07:10", "minutes": [80]},
        "midday": {"carrier": "LX", "depart": "12:40", "minutes": [80]},
        "munich": {"carrier": "LH", "via": ["MUC"], "depart": "06:30", "minutes": [50, 80], "layovers": [70]},
    }, [
        offer("early-saver", "early", "ECONOMY", 18_000),
        offer("early-flex", "early", "ECONOMY", 26_500, refundable=True),
        offer("midday-saver", "midday", "ECONOMY", 19_500),
        offer("midday-flex", "midday", "ECONOMY", 27_900, refundable=True),
        offer("munich-flex", "munich", "ECONOMY", 29_000, refundable=True),
    ]),
    expected("BOOK", ["early-flex"], ["ECONOMY"], ["FLEXIBLE_FARE_NEEDED", "LOWEST_FARE"], BOOKED,
             ["AIR_TRAVEL", "PLANNING_AND_BUDGET"]),
    [FLEXIBILITY, CHANGEABLE, BEST_FARE, TA],
    "The dates are likely to change, so the ticket should be changeable without significant extra cost (lines 238-240; "
    "lines 548-549). The cheapest changeable fare is the 07:10 Swiss nonstop at CHF 265; the cheaper saver fares cannot "
    "be changed. The train to Rome takes about seven hours, so flying is fine.")

kenya_cairo = search("NBO", "CAI", "2027-02-22", {
    "kenya": {"carrier": "KQ", "depart": "09:40", "minutes": [285]},
    "egypt": {"carrier": "MS", "depart": "13:20", "minutes": [285]},
}, [
    offer("kenya-economy", "kenya", "ECONOMY", 30_000),
    offer("kenya-business", "kenya", "BUSINESS", 115_000),
    offer("egypt-economy", "egypt", "ECONOMY", 28_000),
    offer("egypt-business", "egypt", "BUSINESS", 99_000),
])
scenario(
    "egret-moor", "easy", ["dearer_option"],
    "I'm travelling with Kenya's Cabinet Secretary for Environment to the African ministerial conference in Cairo on "
    "February 22nd, on the morning Kenya Airways flight. The ministry is paying for my ticket and has booked her in "
    "business; they've asked that I sit with her.",
    trip(traveller_name="Brian Otieno", traveller_title="Regional Programme Coordinator, Drylands",
         duty_station="REGIONAL_OFFICE", origin="NBO", destination="CAI", travel_date="2027-02-22",
         booking_date="2027-01-18", purpose="Accompanying Kenya's Cabinet Secretary for Environment to the African "
         "ministerial conference on the environment", purpose_kind="CONFERENCE", requested_cabin="BUSINESS",
         ticket_paid_by="ANOTHER_ORGANISATION", funding="Paid directly by Kenya's Ministry of Environment",
         accompanies_flight=first_flight("egret-moor", kenya_cairo, "kenya-business"), sign_offs=ta("Peter Mwangi"),
         notes=[("The ministry pays the airline for this ticket itself and has asked IUCN to book the seat beside the "
                "Cabinet Secretary, who flies business class.")]),
    kenya_cairo,
    expected("BOOK", ["kenya-business"], ["BUSINESS"], ["CLIENT_REIMBURSABLE", "THIRD_PARTY_PAYS_TICKET"], BOOKED,
             CLASS),
    [THIRD_PARTY, ECONOMY, TA],
    "Line 270-272: another entity is paying for the ticket and it would not be appropriate to refuse, e.g. when "
    "accompanying a VIP travelling in business class. Business on the Cabinet Secretary's Kenya Airways flight, not "
    "the cheaper EgyptAir business seat on another flight.")

# ===== boundary twins (6): total flying time 481 / 480; train 239 / 240 minutes; certificate within / past six months

NAIROBI_REQUEST = ("Zurich to Nairobi on February 7th for the regional planning week, which starts on the 9th. Premium "
                   "economy if the policy allows it; otherwise economy.")


def nairobi(minutes):
    return search("ZRH", "NBO", "2027-02-07", {
        "swiss": {"carrier": "LX", "depart": "22:30", "minutes": [minutes]},
    }, [
        offer("swiss-economy", "swiss", "ECONOMY", 82_000),
        offer("swiss-premium", "swiss", "PREMIUM_ECONOMY", 138_000),
        offer("swiss-business", "swiss", "BUSINESS", 395_000),
    ])


NAIROBI_TRIP = {"origin": "ZRH", "destination": "NBO", "travel_date": "2027-02-07", "booking_date": "2027-01-08",
                    "purpose": "Regional programme planning week at the Nairobi office", "requested_cabin": "PREMIUM_ECONOMY",
                    "funding": HQ, "sign_offs": ta("Sofia Lindgren")}

scenario(
    "flint-heron", "boundary_twin", ["dearer_option"], NAIROBI_REQUEST,
    trip(traveller_name="Thomas Keller", traveller_title="Programme Officer, Species Survival", **NAIROBI_TRIP),
    nairobi(481),
    expected("BOOK", ["swiss-premium"], ["PREMIUM_ECONOMY"], ["PREMIUM_ECONOMY_ALLOWED"], BOOKED, CLASS),
    [PREMIUM, ECONOMY, TA],
    "Line 253: economy plus/premium is allowed for total flying time of over 8 hours. The nonstop is scheduled at 481 "
    "minutes, over 480: the premium economy fare the traveller asked for.",
    twin_of="gannet-rill", twin_fact="the nonstop is scheduled at 481 or 480 minutes", distractors=[FOOTNOTE])

scenario(
    "gannet-rill", "boundary_twin", [], NAIROBI_REQUEST,
    trip(traveller_name="Thomas Keller", traveller_title="Programme Officer, Species Survival", **NAIROBI_TRIP),
    nairobi(480),
    expected("BOOK", ["swiss-economy"], ["ECONOMY"], ["LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"], BOOKED,
             CLASS),
    [PREMIUM, ECONOMY, TA],
    "Line 253 needs total flying time of over 8 hours; the nonstop is scheduled at exactly 480 minutes, which is not "
    "over eight hours, so economy (line 251), the fallback the traveller gave.",
    twin_of="flint-heron", twin_fact="the nonstop is scheduled at 481 or 480 minutes")

FRANKFURT_REQUEST = ("Please book me a flight from Zurich to Frankfurt on February 4th for the KfW portfolio review, "
                     "which starts at 10:00 the next day.")


def frankfurt():
    return search("ZRH", "FRA", "2027-02-04", {
        "swiss": {"carrier": "LX", "depart": "07:15", "minutes": [50]},
        "lufthansa": {"carrier": "LH", "depart": "09:30", "minutes": [50]},
    }, [
        offer("swiss-economy", "swiss", "ECONOMY", 21_000),
        offer("lufthansa-economy", "lufthansa", "ECONOMY", 19_500),
    ])


FRANKFURT_TRIP = {"traveller_name": "Anna Weber", "traveller_title": "Senior Finance Officer, Donor Relations",
                      "origin": "ZRH", "destination": "FRA", "travel_date": "2027-02-04", "booking_date": "2027-01-07",
                      "purpose": "Portfolio review with KfW Development Bank", "funding": HQ, "sign_offs": ta("Marc Dubois")}

scenario(
    "hollin-sand", "boundary_twin", ["outside_air_section"], FRANKFURT_REQUEST,
    trip(rail_minutes=239, **FRANKFURT_TRIP), frankfurt(),
    expected("REFUSE", [], ["NONE"], ["RAIL_PREFERRED"], BOOKED, ["ENVIRONMENTAL_ACCOUNTABILITY", "TRANSPORTATION"]),
    [TRAIN, ENVIRONMENT],
    "Line 220: when the travel duration in one direction is under four hours by train, travel should be by train "
    "rather than air. The train takes 239 minutes, under 240: no air ticket is bought. The TA on file is not what the "
    "refusal rests on (NONE or LINE_MANAGER).",
    twin_of="ivory-garth", twin_fact="the train takes 239 or 240 minutes", distractors=[TRAIN_FIRST])

scenario(
    "ivory-garth", "boundary_twin", [], FRANKFURT_REQUEST,
    trip(rail_minutes=240, **FRANKFURT_TRIP), frankfurt(),
    expected("BOOK", ["lufthansa-economy"], ["ECONOMY"], ["LOWEST_FARE"], BOOKED, [*LOW, "TRANSPORTATION"]),
    [TRAIN, BEST_FARE, ECONOMY, TA],
    "The train takes exactly 240 minutes, four hours, which is not under four hours (line 220), so the flight is "
    "allowed: economy at the best possible fare, Lufthansa at CHF 195.",
    twin_of="hollin-sand", twin_fact="the train takes 239 or 240 minutes", distractors=[TRAIN_FIRST])

DUBAI_REQUEST = ("Zurich to Dubai on January 18th for the Gulf mangrove partners' meeting the next day. My specialist's "
                 "certificate saying I need to fly business is on file with HR, so business class please. If business "
                 "isn't possible, book what the policy allows; I have to be at the meeting.")


def dubai():
    return search("ZRH", "DXB", "2027-01-18", {
        "swiss": {"carrier": "LX", "depart": "10:15", "minutes": [370]},
        "emirates": {"carrier": "EK", "depart": "14:40", "minutes": [370]},
    }, [
        offer("swiss-economy", "swiss", "ECONOMY", 52_000),
        offer("swiss-business", "swiss", "BUSINESS", 245_000),
        offer("emirates-economy", "emirates", "ECONOMY", 49_500),
        offer("emirates-business", "emirates", "BUSINESS", 228_000),
    ])


DUBAI_TRIP = {"traveller_name": "Claire Fontaine", "traveller_title": "Senior Programme Officer, Marine and Polar",
                  "origin": "ZRH", "destination": "DXB", "travel_date": "2027-01-18", "booking_date": "2026-12-03",
                  "purpose": "Gulf mangrove restoration partners' meeting", "requested_cabin": "BUSINESS", "funding": HQ,
                  "sign_offs": ta("Henrik Larsen")}

scenario(
    "jasper-wold", "boundary_twin", ["date_arithmetic", "dearer_option"], DUBAI_REQUEST,
    trip(medical_certificate_date="2026-10-05", **DUBAI_TRIP), dubai(),
    expected("BOOK", ["emirates-business"], ["BUSINESS"], ["MEDICAL_NEED"], [*BOOKED, "HUMAN_RESOURCES"], CLASS),
    [MEDICAL, ECONOMY, TA],
    "Lines 257-260: business class is allowed when Human Resources holds a valid specialist's certificate, renewed every "
    "six months. The certificate is dated October 5th, 2026; six months run to April 5th, 2027, after both today "
    "(December 3rd) and the flight (January 18th): the cheapest business fare, Emirates.",
    twin_of="kestrel-mire", twin_fact="the certificate is dated 2026-10-05 or 2026-03-05")

scenario(
    "kestrel-mire", "boundary_twin", ["date_arithmetic"], DUBAI_REQUEST,
    trip(medical_certificate_date="2026-03-05", **DUBAI_TRIP), dubai(),
    expected("BOOK", ["emirates-economy"], ["ECONOMY"], ["MEDICAL_CERTIFICATE_LAPSED", "UPGRADE_NOT_ELIGIBLE"], BOOKED,
             CLASS),
    [MEDICAL, ECONOMY, TA],
    "Lines 257-260: the certificate must be renewed every six months. It is dated March 5th, 2026, so its six months "
    "ended on September 5th, 2026, before today (December 3rd); it was not renewed, so it grounds no business seat. No "
    "other exception applies and the flight is under eight hours: economy, the fallback the traveller gave.",
    twin_of="jasper-wold", twin_fact="the certificate is dated 2026-10-05 or 2026-03-05")

# ===== multi-rule (4) =====

JOHANNESBURG_NOTE = ("The traveller returns from field missions in Asia on February 13th and opens the World Heritage "
                     "site managers' workshop in Johannesburg on the morning of the 15th, with no time to recover "
                     "between the two.")


def johannesburg():
    return search("ZRH", "JNB", "2027-02-14", {
        "swiss": {"carrier": "LX", "depart": "21:40", "minutes": [630]},
        "southafrican": {"carrier": "SA", "depart": "20:15", "minutes": [630]},
    }, [
        offer("swiss-economy", "swiss", "ECONOMY", 89_000),
        offer("swiss-premium", "swiss", "PREMIUM_ECONOMY", 145_000),
        offer("swiss-business", "swiss", "BUSINESS", 420_000),
        offer("southafrican-economy", "southafrican", "ECONOMY", 86_000),
        offer("southafrican-premium", "southafrican", "PREMIUM_ECONOMY", 139_000),
        offer("southafrican-business", "southafrican", "BUSINESS", 398_000),
    ])


JOHANNESBURG_TRIP = {"traveller_name": "Elena Petrova", "traveller_title": "Senior Programme Manager, World Heritage",
                         "origin": "ZRH", "destination": "JNB", "travel_date": "2027-02-14", "booking_date": "2027-01-13",
                         "purpose": "World Heritage site managers' workshop for southern Africa", "purpose_kind": "WORKSHOP",
                         "requested_cabin": "BUSINESS", "funding": HQ, "notes": [JOHANNESBURG_NOTE]}

scenario(
    "lichen-bay", "multi_rule", ["dearer_option"],
    "Zurich to Johannesburg on February 14th, overnight. Our Global Director has authorised business class because I "
    "go straight from the Asia missions into the workshop. Please book business; if it needs someone else's sign-off "
    "first, hold it for them.",
    trip(sign_offs=[sign("LINE_MANAGER", "Jonas Berg"), sign("GLOBAL_DIRECTOR", "Amina Haddad", "BUSINESS_CLASS")],
         **JOHANNESBURG_TRIP),
    johannesburg(),
    expected("BOOK", ["southafrican-business"], ["BUSINESS"], ["EXCEPTIONAL_REASONS_AUTHORISED", "LONG_FLIGHT_APPROVED"],
             [*BOOKED, "GLOBAL_DIRECTOR"], CLASS),
    [EXCEPTIONAL, ECONOMY, TA],
    "Lines 263-267: exceptional reasons (back-to-back commitments with no recuperation) allow business class when a "
    "Global Director authorises it before booking for Headquarters staff. The traveller is Headquarters staff and the "
    "Global Director signed: the cheapest business fare, South African Airways.")

scenario(
    "marram-crag", "multi_rule", ["dearer_option", "outside_air_section"],
    "Zurich to Singapore on March 2nd for the ASEAN heritage parks conference, which opens on the 4th. The project's "
    "donor has told us its grant will happily pay for business class, so business please. If business isn't allowed, "
    "put me in the best cabin the policy does allow.",
    trip(traveller_name="Lukas Brunner", traveller_title="Coordinator, Asia Protected Areas Partnership", origin="ZRH",
         destination="SIN", travel_date="2027-03-02", booking_date="2027-01-26",
         purpose="ASEAN heritage parks conference", purpose_kind="CONFERENCE", requested_cabin="BUSINESS",
         funding="The Asia Protected Areas Partnership project grant, held by the traveller's own programme",
         donor_cabin_terms="WILL_PAY_BUSINESS", sign_offs=ta("Mei Tanaka"),
         notes=["The donor has written that its grant may pay for a business-class seat on this trip."]),
    search("ZRH", "SIN", "2027-03-02", {
        "swiss": {"carrier": "LX", "depart": "22:05", "minutes": [765]},
        "singapore": {"carrier": "SQ", "depart": "11:55", "minutes": [765]},
    }, [
        offer("swiss-economy", "swiss", "ECONOMY", 98_000),
        offer("swiss-premium", "swiss", "PREMIUM_ECONOMY", 165_000),
        offer("swiss-business", "swiss", "BUSINESS", 490_000),
        offer("singapore-economy", "singapore", "ECONOMY", 102_000),
        offer("singapore-premium", "singapore", "PREMIUM_ECONOMY", 159_000),
        offer("singapore-business", "singapore", "BUSINESS", 520_000),
    ]),
    expected("BOOK", ["singapore-premium"], ["PREMIUM_ECONOMY"],
             ["DONOR_FUNDING_NOT_SUFFICIENT", "PREMIUM_ECONOMY_ALLOWED", "UPGRADE_NOT_ELIGIBLE"], BOOKED,
             ["AIR_TRAVEL", "CLASS_OF_TRAVEL", "EQUITABLE_APPLICABILITY"]),
    [DONOR, ANY_FUNDING, DONOR_RULES, PREMIUM, TA],
    "Line 274: the willingness of a donor to fund business class is not sufficient justification, and lines 276 and 181 "
    "apply the rules whatever the funding. No other business ground applies. The 765-minute flight is over eight hours, "
    "so the best cabin allowed is economy plus/premium (line 253): the cheapest, Singapore Airlines at CHF 1,590.")

scenario(
    "nutmeg-scar", "multi_rule", ["multi_leg", "dearer_option"],
    "Zurich to Nairobi on March 8th for the UNEP coordination meeting on the 10th. Premium economy if the policy allows "
    "it; otherwise economy.",
    trip(traveller_name="Sara Lindholm", traveller_title="Programme Officer, Ecosystem Management", origin="ZRH",
         destination="NBO", travel_date="2027-03-08", booking_date="2027-02-02",
         purpose="UN Environment Programme coordination meeting", requested_cabin="PREMIUM_ECONOMY", funding=HQ,
         sign_offs=ta("Jonas Berg")),
    search("ZRH", "NBO", "2027-03-08", {
        "frankfurt": {"carrier": "LH", "via": ["FRA"], "depart": "06:50", "minutes": [50, 445], "layovers": [95]},
        "paris": {"carrier": "AF", "via": ["CDG"], "depart": "07:30", "minutes": [65, 450], "layovers": [100]},
    }, [
        offer("frankfurt-economy", "frankfurt", "ECONOMY", 76_000),
        offer("frankfurt-premium", "frankfurt", "PREMIUM_ECONOMY", 124_000),
        offer("paris-economy", "paris", "ECONOMY", 74_500),
        offer("paris-premium", "paris", "PREMIUM_ECONOMY", 131_000),
    ]),
    expected("BOOK", ["frankfurt-premium"], ["PREMIUM_ECONOMY"], ["PREMIUM_ECONOMY_ALLOWED"], BOOKED, CLASS),
    [PREMIUM, ECONOMY, TA],
    "Line 253 counts total flying time: the Frankfurt connection flies 50 + 445 = 495 minutes and the Paris one 65 + "
    "450 = 515, each over 480 although no single flight is, and ground time is not flying time. Premium economy is "
    "allowed: the cheapest premium fare, Lufthansa at CHF 1,240.",
    distractors=[FOOTNOTE])

scenario(
    "osprey-dell", "multi_rule", ["dearer_option"],
    "Nairobi to Dubai on February 26th for the Gulf donors' round table the next morning. The Director General has "
    "authorised business for this trip given my back-to-back schedule. If you can get me first class, do; otherwise "
    "business.",
    trip(traveller_name="Grace Njeri", traveller_title="Regional Director, Eastern and Southern Africa",
         duty_station="REGIONAL_OFFICE", rank="REGIONAL_DIRECTOR", origin="NBO", destination="DXB",
         travel_date="2027-02-26", booking_date="2027-01-25", purpose="Gulf donors' round table on African drylands",
         requested_cabin="FIRST", funding="Core funds of the Eastern and Southern Africa regional office",
         sign_offs=[sign("LINE_MANAGER", "Olivier Laurent"),
                    sign("DIRECTOR_GENERAL", "Helena Strand", "BUSINESS_CLASS")],
         notes=[("The traveller flies in from the African Union summit in Addis Ababa on February 25th and goes "
                "straight on to the round table, with no day between them.")]),
    search("NBO", "DXB", "2027-02-26", {
        "kenya": {"carrier": "KQ", "depart": "08:30", "minutes": [285]},
        "emirates": {"carrier": "EK", "depart": "10:45", "minutes": [285]},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 41_000),
        offer("kenya-business", "kenya", "BUSINESS", 165_000),
        offer("emirates-economy", "emirates", "ECONOMY", 43_000),
        offer("emirates-business", "emirates", "BUSINESS", 172_000),
        offer("emirates-first", "emirates", "FIRST", 390_000),
    ]),
    expected("BOOK", ["kenya-business"], ["BUSINESS"],
             ["EXCEPTIONAL_REASONS_AUTHORISED", "FIRST_CLASS_NOT_PERMITTED", "LONG_FLIGHT_APPROVED",
              "UPGRADE_NOT_ELIGIBLE"], [*BOOKED, "DIRECTOR_GENERAL"], CLASS),
    [NO_FIRST, DIRECTORS, EXCEPTIONAL, TA],
    "Line 278: first class travel is not permitted. Business is: a Regional Director's business class must be "
    "authorised by the Director General (lines 268-269), who did, for exceptional back-to-back reasons (lines "
    "263-265). The cheapest business fare is Kenya Airways at CHF 1,650.")

# ===== hidden clause (2) =====

scenario(
    "pumice-holt", "hidden_clause", ["outside_air_section", "dearer_option"],
    "I'm flying home to London for my home leave on March 12th. Premium economy if I'm entitled to it; otherwise "
    "economy.",
    trip(traveller_name="James Whitfield", traveller_title="Senior Programme Officer, Water",
         duty_station="REGIONAL_OFFICE", origin="NBO", destination="LHR", travel_date="2027-03-12",
         booking_date="2027-02-08", purpose="Home leave under the traveller's expatriate contract",
         purpose_kind="HOME_LEAVE", requested_cabin="PREMIUM_ECONOMY",
         funding="Core funds of the Eastern and Southern Africa regional office", sign_offs=ta("Peter Mwangi"),
         notes=[("The traveller is a British national posted to the Nairobi office; the contract gives home leave "
                "travel every year.")]),
    search("NBO", "LHR", "2027-03-12", {
        "kenya": {"carrier": "KQ", "depart": "08:25", "minutes": [520]},
        "british": {"carrier": "BA", "depart": "09:40", "minutes": [520]},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 69_000),
        offer("kenya-premium", "kenya", "PREMIUM_ECONOMY", 118_000),
        offer("british-economy", "british", "ECONOMY", 72_000),
        offer("british-premium", "british", "PREMIUM_ECONOMY", 114_000),
    ]),
    expected("BOOK", ["british-premium"], ["PREMIUM_ECONOMY"], ["PREMIUM_ECONOMY_ALLOWED"], BOOKED,
             ["AIR_TRAVEL", "CLASS_OF_TRAVEL", "PURPOSE"]),
    [HOME_LEAVE, PREMIUM, TA],
    "Lines 76-77: the policy covers individual travel entitlements under contracts of employment, e.g. home leave for "
    "expatriate staff, so the flight is bought under it. At 520 minutes the flight is over eight hours, so premium "
    "economy is allowed (line 253): the cheapest, British Airways at CHF 1,140. The insurance exclusion for home leave "
    "(line 134) does not take the trip out of the travel policy.",
    distractors=[INSURANCE])

scenario(
    "quillwort-bend", "hidden_clause", ["personal_travel", "multi_leg", "outside_air_section"],
    "I'm on leave in Barcelona, and my manager asked me to attend the FAO meeting in Rome, which starts the morning of "
    "March 3rd. Please book me Barcelona to Rome on March 2nd; I'll get myself back to Barcelona afterwards.",
    trip(traveller_name="Lucia Romero", traveller_title="Senior Programme Officer, Mediterranean Cooperation",
         origin="BCN", destination="FCO", travel_date="2027-03-02", booking_date="2027-02-01",
         purpose="One-day meeting at FAO in Rome, added to the traveller's annual leave in Barcelona",
         personal_part="WORK_VISIT_ADDED_TO_PERSONAL_TRIP", rail_minutes=1140, funding=HQ,
         sign_offs=ta("Ines Moreau"),
         notes=[("The traveller is on annual leave in Barcelona from February 20th to March 7th; the line manager "
                "asked her to attend the Rome meeting during it.")]),
    search("BCN", "FCO", "2027-03-02", {
        "iberia": {"carrier": "IB", "via": ["MAD"], "depart": "07:20", "minutes": [65, 125], "layovers": [70]},
        "swiss": {"carrier": "LX", "via": ["ZRH"], "depart": "10:05", "minutes": [90, 80], "layovers": [60]},
    }, [
        offer("iberia-economy", "iberia", "ECONOMY", 23_000),
        offer("swiss-economy", "swiss", "ECONOMY", 25_500),
    ]),
    expected("BOOK", ["iberia-economy"], ["ECONOMY"], ["LOWEST_FARE"], BOOKED, [*LOW, "COMBINED_TRAVEL"]),
    [PRIMARY_PERSONAL, BEST_FARE, ECONOMY, TA],
    "Lines 535-536: where the primary objective of travel is personal and a work-related visit is added, the allowable "
    "costs are the incremental costs of the work-related trip. The Barcelona-Rome flight exists only for the FAO "
    "meeting, so it is that incremental cost: IUCN buys it, economy at the best fare, Iberia at CHF 230.",
    distractors=[TRIP_INSURANCE])

# ===== distractor (2) =====

scenario(
    "rushy-knap", "distractor", ["multi_leg", "dearer_option"],
    "Zurich to Istanbul on February 17th for the forestry partners' workshop the next morning. I'd rather take the "
    "nonstop if the policy is fine with it.",
    trip(traveller_name="Nora Albrecht", traveller_title="Programme Officer, Business and Biodiversity", origin="ZRH",
         destination="IST", travel_date="2027-02-17", booking_date="2027-01-19",
         purpose="Forest landscape restoration workshop with Turkish partners", purpose_kind="WORKSHOP", wants_nonstop=True,
         funding=HQ, sign_offs=ta("Marc Dubois")),
    search("ZRH", "IST", "2027-02-17", {
        "swiss": {"carrier": "LX", "depart": "08:40", "minutes": [155]},
        "frankfurt": {"carrier": "LH", "via": ["FRA"], "depart": "06:15", "minutes": [50, 160], "layovers": [300]},
    }, [
        offer("swiss-economy", "swiss", "ECONOMY", 41_200),
        offer("frankfurt-economy", "frankfurt", "ECONOMY", 38_900),
    ]),
    expected("BOOK", ["swiss-economy"], ["ECONOMY"], ["ALTERNATE_ROUTE_WITHIN_MARGIN", "MOST_DIRECT_ROUTE"], BOOKED,
             ["AIR_TRAVEL"]),
    [ROUTE, TA],
    "Lines 230-231: normally the most direct route, unless an alternative route brings significant financial gains. "
    "The Frankfurt connection saves CHF 23 of CHF 412 (under 6%), with five hours on the ground: not significant. The "
    "nonstop the traveller asked for. The five-hour stopover would earn a lounge (line 413), which chooses nothing.",
    distractors=[LOUNGE])

scenario(
    "sallow-tarn", "distractor", ["outside_air_section", "dearer_option"],
    "Zurich to Hong Kong on March 15th for the Pearl River delta wetlands workshop on the 17th. Premium economy if the "
    "policy allows it. Heads-up: the project's donor only pays for economy seats.",
    trip(traveller_name="Felix Hartmann", traveller_title="Programme Officer, Global Water Programme", origin="ZRH",
         destination="HKG", travel_date="2027-03-15", booking_date="2027-02-09",
         purpose="Pearl River delta wetlands workshop", purpose_kind="WORKSHOP", requested_cabin="PREMIUM_ECONOMY",
         funding="The delta wetlands project grant, held by the Ecosystem Management Programme",
         own_cost_centre=False, donor_cabin_terms="ECONOMY_ONLY",
         sign_offs=[sign("LINE_MANAGER", "Jonas Berg"), sign("BUDGET_HOLDER", "Sara Lindholm", "BUDGET")],
         notes=["The donor's grant rules allow economy seats only."]),
    search("ZRH", "HKG", "2027-03-15", {
        "swiss": {"carrier": "LX", "depart": "13:10", "minutes": [695]},
        "cathay": {"carrier": "CX", "depart": "22:45", "minutes": [695]},
    }, [
        offer("swiss-economy", "swiss", "ECONOMY", 87_000),
        offer("swiss-premium", "swiss", "PREMIUM_ECONOMY", 149_000),
        offer("cathay-economy", "cathay", "ECONOMY", 84_000),
        offer("cathay-premium", "cathay", "PREMIUM_ECONOMY", 142_000),
    ]),
    expected("BOOK", ["cathay-premium"], ["PREMIUM_ECONOMY"], ["PREMIUM_ECONOMY_ALLOWED"], [*BOOKED, "BUDGET_HOLDER"],
             ["AIR_TRAVEL", "CLASS_OF_TRAVEL", "EQUITABLE_APPLICABILITY"]),
    [DONOR_RULES, PREMIUM, BUDGET, TA],
    "Lines 181-183: the policy applies irrespective of donors' own rules; costs it allows that the donor does not are "
    "charged to other funding. At 695 minutes premium economy is allowed (line 253): the cheapest, Cathay at CHF 1,420. "
    "Another programme's budget pays, and its budget holder has authorized the travel (lines 564-566).")

# ===== refusal (2) =====

scenario(
    "teasel-cove", "refusal", ["outside_air_section"],
    "Please book me Washington Dulles to Mexico City on February 16th for the watershed field visit. I'm happy to go.",
    trip(traveller_name="Carlos Ortega", traveller_title="Programme Officer, Mesoamerica Watersheds",
         duty_station="REGIONAL_OFFICE", origin="IAD", destination="MEX", travel_date="2027-02-16",
         booking_date="2027-01-26", purpose="Field visit to a watershed restoration site", purpose_kind="FIELD_MISSION",
         funding="Core funds of the Washington office's water programme", risk_check="NO_MEASURE_FOUND",
         notes=[("The field site lies in a district where a severe haemorrhagic fever outbreak was declared on January "
                "20th; the health authority has no vaccine or treatment and has asked visitors to stay away."),
                ("The line manager's check on January 25th found no precaution that brings the risk down to an "
                "acceptable level, and the TA was not approved."),
                "The traveller works in IUCN's Washington, DC office."]),
    search("IAD", "MEX", "2027-02-16", {
        "united": {"carrier": "UA", "depart": "09:15", "minutes": [245]},
        "aeromexico": {"carrier": "AM", "depart": "13:30", "minutes": [245]},
    }, [
        offer("united-economy", "united", "ECONOMY", 38_000),
        offer("aeromexico-economy", "aeromexico", "ECONOMY", 35_500),
    ]),
    expected("REFUSE", [], ["NONE"], ["TRAVEL_RISK_NOT_MITIGATED"], BOOKED,
             ["HEALTH_SAFETY_SECURITY", "HEALTH_SECURITY_WARNINGS"]),
    [DOUBT, NO_MEASURES],
    "Lines 125-126: if there is any doubt as to whether staff may be exposed to a high security or health risk, they "
    "should not travel; lines 157-158: where measures to reduce the risks to acceptable levels cannot be found, travel "
    "should not be undertaken. The line manager found none and did not approve the TA: no ticket is bought.")

scenario(
    "umbel-ridge", "refusal", ["personal_travel", "outside_air_section"],
    "I'm taking a week's holiday in Dublin from March 20th, and while I'm there I'll spend an afternoon with our "
    "partners at the Irish Environmental Network. Since it's partly work, can IUCN buy my flight from Zurich to Dublin "
    "on the 20th?",
    trip(traveller_name="Hannah Murphy", traveller_title="Communications Officer", origin="ZRH", destination="DUB",
         travel_date="2027-03-20", booking_date="2027-02-15",
         purpose="A week's holiday in Dublin; during it, an afternoon visit to a partner network in Dublin",
         purpose_kind="PERSONAL", personal_part="WORK_VISIT_ADDED_TO_PERSONAL_TRIP", funding=HQ,
         sign_offs=[sign("LINE_MANAGER", "Marc Dubois", "PERSONAL_DAYS")],
         notes=["The line manager agreed to the partner visit during the holiday."]),
    search("ZRH", "DUB", "2027-03-20", {
        "swiss": {"carrier": "LX", "depart": "09:20", "minutes": [120]},
        "aerlingus": {"carrier": "EI", "depart": "12:05", "minutes": [120]},
    }, [
        offer("swiss-economy", "swiss", "ECONOMY", 26_000),
        offer("aerlingus-economy", "aerlingus", "ECONOMY", 23_500),
    ]),
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"], BOOKED,
             ["COMBINED_TRAVEL"]),
    [PRIMARY_PERSONAL, ADDED],
    "Lines 535-536: where the primary objective of travel is personal and a work-related visit is added, the allowable "
    "costs are the incremental costs of the work-related trip. The visit is in Dublin, where the holiday already takes "
    "the traveller, so it adds no air cost: IUCN buys no ticket.",
    distractors=[TRIP_INSURANCE])

# ===== flag (3) =====

scenario(
    "vetch-lynn", "flag", ["multi_leg", "unclear_phrase"],
    "Zurich to Copenhagen on March 3rd for the Nordic biodiversity strategy meeting on the 4th. I'd rather take the "
    "nonstop if the policy is fine with it.",
    trip(traveller_name="Erik Johansson", traveller_title="Programme Officer, European Biodiversity Policy",
         origin="ZRH", destination="CPH", travel_date="2027-03-03", booking_date="2027-02-01",
         purpose="Nordic Council biodiversity strategy meeting", wants_nonstop=True, rail_minutes=690, funding=HQ,
         sign_offs=ta("Ines Moreau")),
    search("ZRH", "CPH", "2027-03-03", {
        "swiss": {"carrier": "LX", "depart": "07:50", "minutes": [100]},
        "frankfurt": {"carrier": "LH", "via": ["FRA"], "depart": "07:05", "minutes": [50, 80], "layovers": [115]},
    }, [
        offer("swiss-economy", "swiss", "ECONOMY", 43_000),
        offer("frankfurt-economy", "frankfurt", "ECONOMY", 34_500),
    ]),
    expected("FLAG_FOR_APPROVAL", ["frankfurt-economy", "swiss-economy"], ["ECONOMY"],
             ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"], ["LINE_MANAGER", "NOT_NAMED"],
             ["AIR_TRAVEL", "AUTHORIZATION"], phrase="significant financial gains"),
    [ROUTE, BEST_FARE, NOT_OBVIOUS, TA],
    "The Frankfurt connection costs CHF 345 against the nonstop's CHF 430: it saves CHF 85, about 20%, and adds 145 "
    "minutes. Lines 230-231 keep the most direct route 'unless there are significant financial gains from taking an "
    "alternative route', and the handbook gives no measure. Lines 569-571 send a choice of ticket that is not obvious "
    "to the traveller's supervisor: hold either offer.",
    flag_twins=["rushy-knap", "amber-tor"],
    ambiguity={"phrase": "significant financial gains",
               "readings": ["CHF 85, a fifth of the fare, is a significant financial gain: the cheaper connection",
                            ("CHF 85 on a short European trip is not significant beside more than two hours more "
                            "travel: the most direct route, the nonstop")]})

scenario(
    "whin-shaw", "flag", ["approval_required", "dearer_option"],
    "Zurich to Johannesburg on February 14th, overnight. The Regional Director for Southern Africa, whose workshop it "
    "is, has authorised business class because I go straight from the Asia missions into the workshop. Please book "
    "business; if it needs someone else's sign-off first, hold it for them.",
    trip(sign_offs=[sign("LINE_MANAGER", "Jonas Berg"), sign("REGIONAL_DIRECTOR", "Thandiwe Nkosi", "BUSINESS_CLASS")],
         **JOHANNESBURG_TRIP),
    johannesburg(),
    expected("FLAG_FOR_APPROVAL", ["southafrican-business"], ["BUSINESS"], ["APPROVAL_REQUIRED"], ["GLOBAL_DIRECTOR"],
             CLASS),
    [EXCEPTIONAL, TA],
    "Lines 263-267: business class for exceptional reasons must be authorised before booking by a Global Director for "
    "Headquarters staff, and by Regional Directors for regional staff. The traveller is Headquarters staff, and only a "
    "Regional Director signed: hold the cheapest business fare for the Global Director. Approval required, not 'no "
    "compliant offer'.",
    twin_of="lichen-bay", twin_fact="business class authorised by a Global Director or by a Regional Director",
    flag_twins=["lichen-bay", "cobble-fern"],
    ambiguity="none: a sign-off is required and missing; the text is clear")

scenario(
    "yarrow-beck", "flag", ["approval_required", "outside_air_section", "upgrade_not_taken"],
    "Nairobi to Amsterdam on March 9th for the peatlands partners' meeting on the 11th. Economy is fine.",
    trip(traveller_name="Joseph Kiprono", traveller_title="Programme Officer, Peatlands", duty_station="REGIONAL_OFFICE",
         origin="NBO", destination="AMS", travel_date="2027-03-09", booking_date="2027-02-04",
         purpose="Global peatlands partners' meeting", funding="The peatlands project budget of the Ecosystem "
         "Management Programme at Headquarters", own_cost_centre=False, sign_offs=ta("Peter Mwangi"),
         notes=["The trip is charged to a project of another unit, the Ecosystem Management Programme."]),
    search("NBO", "AMS", "2027-03-09", {
        "kenya": {"carrier": "KQ", "depart": "23:55", "minutes": [505]},
        "klm": {"carrier": "KL", "depart": "09:30", "minutes": [505]},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 76_000),
        offer("klm-economy", "klm", "ECONOMY", 73_500),
        offer("klm-premium", "klm", "PREMIUM_ECONOMY", 121_000),
    ]),
    expected("FLAG_FOR_APPROVAL", ["klm-economy"], ["ECONOMY"], ["APPROVAL_REQUIRED"], ["BUDGET_HOLDER"],
             ["AUTHORIZATION"]),
    [BUDGET, TA, BEST_FARE],
    "Lines 562-566: the TA must be approved before any commitments are made, and travel funded by a different cost "
    "centre than the traveller's own must also be authorized by the budget holder. Only the line manager has signed: "
    "hold the ticket the request would get, the cheapest economy fare (KLM), for the budget holder. Premium economy "
    "would be allowed (505 minutes) but economy is what was asked.",
    flag_twins=["sallow-tarn", "bracken-weir"],
    ambiguity="none: a sign-off is required and missing; the text is clear")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
