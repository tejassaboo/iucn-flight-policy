"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-iucn-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    MOST_DIRECT_ROUTE = "MOST_DIRECT_ROUTE"
    FLEXIBLE_FARE_NEEDED = "FLEXIBLE_FARE_NEEDED"
    EXCEPTIONAL_REASONS_AUTHORISED = "EXCEPTIONAL_REASONS_AUTHORISED"
    THIRD_PARTY_PAYS_TICKET = "THIRD_PARTY_PAYS_TICKET"
    MEDICAL_CERTIFICATE_LAPSED = "MEDICAL_CERTIFICATE_LAPSED"
    DONOR_FUNDING_NOT_SUFFICIENT = "DONOR_FUNDING_NOT_SUFFICIENT"
    FIRST_CLASS_NOT_PERMITTED = "FIRST_CLASS_NOT_PERMITTED"
    TRAVEL_RISK_NOT_MITIGATED = "TRAVEL_RISK_NOT_MITIGATED"
    # Decoys: codes for rules of other handbooks that this one lacks, so the list hints at none of its own rules.
    NEXT_OF_KIN_TRAVEL = "NEXT_OF_KIN_TRAVEL"
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    OPEN_SKIES_AGREEMENT = "OPEN_SKIES_AGREEMENT"
    CREATIVE_TICKETING = "CREATIVE_TICKETING"
    EXTENDED_TRAVEL_SAVINGS = "EXTENDED_TRAVEL_SAVINGS"
    DENIED_BOARDING_NOT_ALLOWED = "DENIED_BOARDING_NOT_ALLOWED"
    CHANCELLOR_WRITTEN_AUTHORIZATION = "CHANCELLOR_WRITTEN_AUTHORIZATION"
    DOUBLE_BOOKING_PROHIBITED = "DOUBLE_BOOKING_PROHIBITED"
    PRIVATE_AIRCRAFT_NOT_APPROVED = "PRIVATE_AIRCRAFT_NOT_APPROVED"
    CANDIDATE_TRIP_NOT_COVERED = "CANDIDATE_TRIP_NOT_COVERED"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: IUCN Travel Policy and Procedures, Version 2.1 (April 2019).
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    AMBER_TOR = "amber-tor"
    BRACKEN_WEIR = "bracken-weir"
    COBBLE_FERN = "cobble-fern"
    DAPPLE_ROOK = "dapple-rook"
    EGRET_MOOR = "egret-moor"
    FLINT_HERON = "flint-heron"
    GANNET_RILL = "gannet-rill"
    HOLLIN_SAND = "hollin-sand"
    IVORY_GARTH = "ivory-garth"
    JASPER_WOLD = "jasper-wold"
    KESTREL_MIRE = "kestrel-mire"
    LICHEN_BAY = "lichen-bay"
    MARRAM_CRAG = "marram-crag"
    NUTMEG_SCAR = "nutmeg-scar"
    OSPREY_DELL = "osprey-dell"
    PUMICE_HOLT = "pumice-holt"
    QUILLWORT_BEND = "quillwort-bend"
    RUSHY_KNAP = "rushy-knap"
    SALLOW_TARN = "sallow-tarn"
    TEASEL_COVE = "teasel-cove"
    UMBEL_RIDGE = "umbel-ridge"
    VETCH_LYNN = "vetch-lynn"
    WHIN_SHAW = "whin-shaw"
    YARROW_BECK = "yarrow-beck"


class Approver(Enum):
    """Roles that may sign off. NONE: the decision relies on no one's sign-off, given or awaited (one for
    something else may be on file). NOT_NAMED: one is needed, but the handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    LINE_MANAGER = "LINE_MANAGER"
    BUDGET_HOLDER = "BUDGET_HOLDER"
    GLOBAL_DIRECTOR = "GLOBAL_DIRECTOR"
    REGIONAL_DIRECTOR = "REGIONAL_DIRECTOR"
    DIRECTOR_GENERAL = "DIRECTOR_GENERAL"
    HUMAN_RESOURCES = "HUMAN_RESOURCES"
    CHIEF_FINANCIAL_OFFICER = "CHIEF_FINANCIAL_OFFICER"
    FINANCE_OFFICER = "FINANCE_OFFICER"
    VICE_PRESIDENT = "VICE_PRESIDENT"
    TRAVEL_MANAGER = "TRAVEL_MANAGER"
    CHIEF_EXECUTIVE = "CHIEF_EXECUTIVE"


class Clause(Enum):
    """The handbook's sections, by heading."""

    PURPOSE = "PURPOSE"
    REQUIREMENT_TO_TRAVEL = "REQUIREMENT_TO_TRAVEL"
    ENVIRONMENTAL_ACCOUNTABILITY = "ENVIRONMENTAL_ACCOUNTABILITY"
    COST_EFFECTIVENESS = "COST_EFFECTIVENESS"
    HEALTH_SAFETY_SECURITY = "HEALTH_SAFETY_SECURITY"
    TRAVEL_INSURANCE = "TRAVEL_INSURANCE"
    HEALTH_SECURITY_WARNINGS = "HEALTH_SECURITY_WARNINGS"
    EQUITABLE_APPLICABILITY = "EQUITABLE_APPLICABILITY"
    VARIATIONS = "VARIATIONS"
    TRANSPORTATION = "TRANSPORTATION"
    AIR_TRAVEL = "AIR_TRAVEL"
    CLASS_OF_TRAVEL = "CLASS_OF_TRAVEL"
    AIR_MILES = "AIR_MILES"
    SURFACE_TRANSPORT = "SURFACE_TRANSPORT"
    AIRPORT_LOUNGES = "AIRPORT_LOUNGES"
    CARBON_OFFSETS = "CARBON_OFFSETS"
    COMBINED_TRAVEL = "COMBINED_TRAVEL"
    PLANNING_AND_BUDGET = "PLANNING_AND_BUDGET"
    AUTHORIZATION = "AUTHORIZATION"
    BOOKING = "BOOKING"
    EXPENSE_CLAIMS = "EXPENSE_CLAIMS"


class StaffCategory(Enum):
    STAFF_MEMBER = "STAFF_MEMBER"
    JUNIOR_PROFESSIONAL_OFFICER = "JUNIOR_PROFESSIONAL_OFFICER"
    INTERN = "INTERN"
    SECONDED = "SECONDED"
    AGENCY_CONTRACTED = "AGENCY_CONTRACTED"


class DutyStation(Enum):
    HEADQUARTERS = "HEADQUARTERS"
    REGIONAL_OFFICE = "REGIONAL_OFFICE"


class Rank(Enum):
    STAFF = "STAFF"
    REGIONAL_DIRECTOR = "REGIONAL_DIRECTOR"
    GLOBAL_DIRECTOR = "GLOBAL_DIRECTOR"


class Purpose(Enum):
    MEETING = "MEETING"
    WORKSHOP = "WORKSHOP"
    FIELD_MISSION = "FIELD_MISSION"
    CONFERENCE = "CONFERENCE"
    HOME_LEAVE = "HOME_LEAVE"
    PERSONAL = "PERSONAL"


class PersonalPart(Enum):
    NO_PERSONAL_PART = "NO_PERSONAL_PART"
    PERSONAL_DAYS_ADDED = "PERSONAL_DAYS_ADDED"
    WORK_VISIT_ADDED_TO_PERSONAL_TRIP = "WORK_VISIT_ADDED_TO_PERSONAL_TRIP"


class Payer(Enum):
    IUCN = "IUCN"
    ANOTHER_ORGANISATION = "ANOTHER_ORGANISATION"


class DonorCabinTerms(Enum):
    NOT_STATED = "NOT_STATED"
    ECONOMY_ONLY = "ECONOMY_ONLY"
    WILL_PAY_BUSINESS = "WILL_PAY_BUSINESS"


class RiskCheck(Enum):
    NO_SPECIAL_RISK = "NO_SPECIAL_RISK"
    MEASURES_AGREED = "MEASURES_AGREED"
    NO_MEASURE_FOUND = "NO_MEASURE_FOUND"


class SignOffSubject(Enum):
    TRAVEL_AUTHORIZATION = "TRAVEL_AUTHORIZATION"
    BUSINESS_CLASS = "BUSINESS_CLASS"
    BUDGET = "BUDGET"
    PERSONAL_DAYS = "PERSONAL_DAYS"


@dataclass
class SignOff(Output):
    role: Annotated[Approver, "The signer's role"]
    name: Annotated[str, "Their name"]
    subject: Annotated[
        SignOffSubject,
        "What they signed: the trip's Travel Authorization (TA), a business-class seat, the charge to their "
        "budget, or personal days or a work visit linked to the trip",
    ]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "Who flies"]
    traveller_title: Annotated[str, "Their job title"]
    staff_category: Annotated[StaffCategory, "How the traveller is engaged by IUCN"]
    duty_station: Annotated[DutyStation, "Whether the traveller works at Headquarters or in a regional office"]
    rank: Annotated[Rank, "STAFF, or the traveller's director post when they hold one"]
    origin: Annotated[Airport, "Where the flight leaves from"]
    destination: Annotated[Airport, "Where it goes"]
    travel_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    booking_date: Annotated[str, "Today in this world, the day the request is made and the ticket bought, YYYY-MM-DD"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    purpose_kind: Annotated[Purpose, "The kind of trip"]
    personal_part: Annotated[
        PersonalPart,
        "Personal travel linked to the trip: none, personal days the traveller adds to a work trip, or a work "
        "visit added to a trip made mainly for personal reasons",
    ]
    requested_cabin: Annotated[Cabin, "The cabin the traveller asks for"]
    wants_nonstop: Annotated[bool, "Whether the traveller asks for a flight with no connection"]
    dates_may_change: Annotated[bool, "Whether the trip's dates may still move after the ticket is bought"]
    rail_minutes: Annotated[
        int,
        "The quickest scheduled train journey from the origin city to the destination city, one way, in "
        "minutes; zero when no train links them",
    ]
    ticket_paid_by: Annotated[Payer, "Who pays for this ticket: IUCN, or another organisation paying it directly"]
    funding: Annotated[str, "The budget the trip is charged to, in plain words"]
    own_cost_centre: Annotated[bool, "Whether the cost centre charged is the one the traveller belongs to"]
    donor_cabin_terms: Annotated[
        DonorCabinTerms,
        "What the donor whose grant funds the trip says about the cabin: nothing, economy only, or that it "
        "will pay for business class",
    ]
    medical_certificate_date: Annotated[
        str,
        "The date of the specialist's certificate held by Human Resources saying the traveller needs a "
        "business-class seat, YYYY-MM-DD; empty when none is held",
    ]
    risk_check: Annotated[
        RiskCheck,
        "The line manager's check of the trip's risks to the traveller: no special risk, precautions agreed, "
        "or no precaution found that brings the risk down to an acceptable level",
    ]
    accompanies_flight: Annotated[
        str,
        "The flight number of the person the traveller accompanies on duty, as search_flights shows it; "
        "empty when none",
    ]
    sign_offs: Annotated[list[SignOff], "Sign-offs on file for this trip, each given before today"]
    notes: Annotated[list[str], "Other facts on file about the trip, in plain words; empty when none"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from, and a word when this case lists none for the search"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the organisation buys no ticket at all for this request. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on, whether already on file or still awaited; NONE when "
        "this decision relies on no one's sign-off, even if a sign-off for something else is on file; NOT_NAMED "
        "when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
