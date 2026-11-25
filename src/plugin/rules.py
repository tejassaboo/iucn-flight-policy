"""The answer key's rules for the IUCN Travel Policy and Procedures, Version 2.1 (April 2019), as exact integer
code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it imports only modules a verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The duration hook. Line 253: "Economy plus/premium class1 is allowed for total flying time of over 8 hours".
The handbook measures the total flying time of the journey: the scheduled minutes of every flight of the
ticket added together, ground time at connections left out (the offer's flying_minutes), and strictly over
480 ("over"). A nonstop of 481 minutes qualifies, one of 480 does not; a connection of 50 + 445 minutes
qualifies although neither flight does. The journey is the ticket being bought (one way out; the return is a
separate booking, guide.CONVENTIONS), so there is no gap value and over() never returns None.

The train rule (line 220, "under four hours by train") is not a flight duration: the trip record gives the
quickest scheduled train journey (rail_minutes), and the rule is strict at 240 minutes.
"""

from contract import (
    Approver,
    Cabin,
    Clause,
    Decision,
    DonorCabinTerms,
    DutyStation,
    Payer,
    PersonalPart,
    Purpose,
    Rank,
    ReasonCode,
    RiskCheck,
    SignOffSubject,
    StaffCategory,
)

from .world import day_number, month_length

HANDBOOK = "IUCN Travel Policy and Procedures, Version 2.1 (April 2019)"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.PURPOSE: "1. Purpose",
    Clause.REQUIREMENT_TO_TRAVEL: "2. Requirement to travel",
    Clause.ENVIRONMENTAL_ACCOUNTABILITY: "3. Environmental accountability",
    Clause.COST_EFFECTIVENESS: "5. Cost effectiveness and fiscal responsibility",
    Clause.HEALTH_SAFETY_SECURITY: "6. Health, Safety and Security",
    Clause.TRAVEL_INSURANCE: "6.1. Travel Insurance",
    Clause.HEALTH_SECURITY_WARNINGS: "6.2. Health and Security Warnings",
    Clause.EQUITABLE_APPLICABILITY: "7. Equitable Applicability",
    Clause.VARIATIONS: "8. Variations",
    Clause.TRANSPORTATION: "2. Transportation",
    Clause.AIR_TRAVEL: "2.1. Air travel",
    Clause.CLASS_OF_TRAVEL: "Class of Travel",
    Clause.AIR_MILES: "Air miles",
    Clause.SURFACE_TRANSPORT: "2.2. Sea, train, bus, and other public transportation",
    Clause.AIRPORT_LOUNGES: "5.6. Airport lounges",
    Clause.CARBON_OFFSETS: "10. Compensation for CO2 emissions",
    Clause.COMBINED_TRAVEL: "11. Combined Travel: Work-related and Personal Travel",
    Clause.PLANNING_AND_BUDGET: "1.1. Planning and Budget",
    Clause.AUTHORIZATION: "1.2. Authorization",
    Clause.BOOKING: "1.3. Booking",
    Clause.EXPENSE_CLAIMS: "2.1. Travel Expense Claims",
}

# The handbook's flight-duration threshold (the per-handbook duration hook; tests/test_duration.py tests both sides).
DURATION_RULES = (
    {"name": "premium-economy", "minutes": 480, "operator": ">", "lines": [253, 253],
     "quote": "Economy plus/premium class1 is allowed for total flying time of over 8 hours"},
)
LIMITS = {rule["name"]: rule["minutes"] for rule in DURATION_RULES}

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Line 220: "When the travel duration in one direction is under four hours by train, travel should be undertaken
# by train rather than air" (strict).
RAIL_MINUTES = 240
# A train journey this little over the limit makes the section part of the answer (it was weighed and passed).
NEAR_RAIL_MINUTES = 60
# Lines 257-260: the medical certificate "should be renewed every six months" (calendar months from its date).
CERTIFICATE_MONTHS = 6
# A certificate whose six months end this close to the booking or travel date is not modelled (no scenario).
CERTIFICATE_MARGIN_DAYS = 20
# Lines 230-231: "normally the most direct route should be taken, unless there are significant financial gains
# from taking an alternative route". The handbook gives no number. Savings of at most 10% of the nonstop fare are
# not significant on any reading, savings of at least 40% are significant on any reading; anything between is
# unclear and held (one scenario).
SMALL_SAVING_PERCENT = 10
LARGE_SAVING_PERCENT = 40
SIGNIFICANT_PHRASE = "significant financial gains"

LOW = [Clause.AIR_TRAVEL, Clause.BOOKING, Clause.CLASS_OF_TRAVEL, Clause.COST_EFFECTIVENESS]
CLASS = [Clause.AIR_TRAVEL, Clause.CLASS_OF_TRAVEL]
DIRECTORS = (Rank.REGIONAL_DIRECTOR, Rank.GLOBAL_DIRECTOR)


def over(rule, offer):
    """True or False: whether ``offer``'s total flying time out is over the handbook's ``rule`` (line 253)."""
    if rule != "premium-economy":
        raise ValueError(f"unknown duration rule {rule!r}")
    return offer.flying_minutes > LIMITS[rule]


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def signed(trip, subject, roles=None):
    return [record for record in trip.sign_offs if record.subject == subject and (roles is None or record.role in roles)]


def nonstop(offer):
    return not offer.layover_minutes


def francs(cents):
    return f"CHF {cents // 100:,}"


def months_later(date, months):
    """The YYYY-MM-DD date ``months`` calendar months after ``date`` (the day clamped to the month's length)."""
    year, month, day = int(date[:4]), int(date[5:7]), int(date[8:])
    month += months
    year += (month - 1) // 12
    month = (month - 1) % 12 + 1
    return f"{year:04d}-{month:02d}-{min(day, month_length(year, month)):02d}"


def certificate_valid(trip):
    """True or False: whether the medical certificate on file is within its six months on the booking and travel
    dates (lines 257-260); None when there is none."""
    if not trip.medical_certificate_date:
        return None
    ends = day_number(months_later(trip.medical_certificate_date, CERTIFICATE_MONTHS))
    days = [day_number(trip.booking_date), day_number(trip.travel_date)]
    if any(abs(ends - day) < CERTIFICATE_MARGIN_DAYS for day in days) or len({ends > day for day in days}) != 1:
        raise ValueError("a certificate expiring near the booking or travel date is not modelled")
    return ends > days[1]


def business_authoriser(trip):
    """Lines 266-269: exceptional business class is authorised by a Global Director for Headquarters staff, by
    Regional Directors for regional staff, and by the Director General for Regional and Global Directors."""
    if trip.rank in DIRECTORS:
        return Approver.DIRECTOR_GENERAL
    if trip.duty_station == DutyStation.HEADQUARTERS:
        return Approver.GLOBAL_DIRECTOR
    return Approver.REGIONAL_DIRECTOR


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers on its route and date: the decision, and every accepted
    offer id, cabin, reason, approver and section. ``hidden`` (answer_key_inputs) is unused by this handbook."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if any(offer.return_segments for offer in offers):
        raise ValueError("round-trip fares are not modelled: every case buys the one-way fare out")
    on_file = [record.role for record in trip.sign_offs]
    authorization = signed(trip, SignOffSubject.TRAVEL_AUTHORIZATION, [Approver.LINE_MANAGER])
    if trip.purpose_kind == Purpose.PERSONAL:
        if trip.personal_part != PersonalPart.WORK_VISIT_ADDED_TO_PERSONAL_TRIP or authorization:
            raise ValueError("a personal trip other than a work visit added to a holiday is not modelled")
        # SYNC_NOTES 4(b): the line manager's agreement on file is not what the refusal rests on.
        return answer(Decision.REFUSE, [], [ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      [Approver.NONE, *on_file], [Clause.COMBINED_TRAVEL],
                      "Lines 535-536: where the primary objective of travel is personal travel and a work-related "
                      "visit is added, the allowable costs are the incremental costs of the work-related trip. The "
                      "flight goes to the holiday destination, where the visit also takes place, so the visit adds no "
                      "air cost: IUCN buys no ticket.")
    if trip.risk_check == RiskCheck.NO_MEASURE_FOUND:
        if authorization:
            raise ValueError("an approved TA with no precaution found is not modelled")
        return answer(Decision.REFUSE, [], [ReasonCode.TRAVEL_RISK_NOT_MITIGATED], [Approver.NONE, Approver.LINE_MANAGER],
                      [Clause.HEALTH_SAFETY_SECURITY, Clause.HEALTH_SECURITY_WARNINGS],
                      "Lines 125-126: if there is any doubt as to whether staff may be exposed to a high security or "
                      "health risk, they should not travel; lines 157-158: where measures to reduce the risks to "
                      "acceptable levels cannot be found, travel should not be undertaken. The line manager's check "
                      "found none, and the TA is not approved: no ticket is bought.")
    if 0 < trip.rail_minutes < RAIL_MINUTES:
        if not authorization:
            raise ValueError("a train-distance trip without an approved TA is not modelled")
        return answer(Decision.REFUSE, [], [ReasonCode.RAIL_PREFERRED], [Approver.NONE, *on_file],
                      [Clause.TRANSPORTATION, Clause.ENVIRONMENTAL_ACCOUNTABILITY],
                      f"Line 220: the journey takes {trip.rail_minutes} minutes by train, under four hours one way, so "
                      "travel should be by train rather than air (lines 95-97: travel in environmentally responsible "
                      "ways). No air ticket is bought.")
    if len(authorization) != 1:
        raise ValueError("every booked trip carries the line manager's approved TA (lines 561-566)")
    if trip.risk_check == RiskCheck.MEASURES_AGREED:
        raise ValueError("a trip with agreed precautions is not modelled")
    seated = [offer for offer in offers if offer.seats_available]
    decision, chosen, reasons, relied, clauses, notes, phrase = choose(trip, seated)
    if RAIL_MINUTES <= trip.rail_minutes < RAIL_MINUTES + NEAR_RAIL_MINUTES:
        clauses.append(Clause.TRANSPORTATION)
        notes.append(f"line 220: the train takes {trip.rail_minutes} minutes, not under four hours, so flying is allowed")
    if not trip.own_cost_centre:
        budget = signed(trip, SignOffSubject.BUDGET, [Approver.BUDGET_HOLDER])
        if not budget:
            if decision != Decision.BOOK:
                raise ValueError("a missing budget holder's sign-off on a hold is not modelled")
            return answer(Decision.FLAG_FOR_APPROVAL, chosen, [ReasonCode.APPROVAL_REQUIRED], [Approver.BUDGET_HOLDER],
                          [Clause.AUTHORIZATION],
                          "Lines 564-566: travel funded by a different cost centre than the traveller's own must also "
                          "be authorized by the budget holder, and the TA must be approved before any commitments are "
                          f"made (line 563). Only the line manager has signed: hold the ticket the request would "
                          f"otherwise get ({'; '.join(notes)}).")
        relied.append(Approver.BUDGET_HOLDER)
        notes.append("lines 564-566: another unit's budget pays, and its budget holder has authorized the travel")
    elif signed(trip, SignOffSubject.BUDGET):
        raise ValueError("a budget sign-off on the traveller's own cost centre is not modelled")
    if decision == Decision.FLAG_FOR_APPROVAL:
        approvers = relied
    else:
        # SYNC_NOTES 4': a BOOK whose sign-offs are already on file accepts those roles and NONE; 4(b): an unused one
        # is accepted too.
        approvers = [Approver.NONE, Approver.LINE_MANAGER, *relied, *on_file]
    notes.append("lines 561-563: the line manager approved the TA before booking")
    return answer(decision, chosen, reasons, approvers, clauses, "; ".join(notes) + ".", phrase)


def choose(trip, seated):
    """(decision, offers, reasons, roles relied on beyond the TA, clauses, notes, unclear phrase)."""
    if trip.ticket_paid_by != Payer.IUCN and trip.requested_cabin != Cabin.BUSINESS:
        raise ValueError("another organisation paying for a cabin other than business is not modelled")
    if trip.requested_cabin == Cabin.ECONOMY:
        return economy(trip, seated)
    if trip.wants_nonstop or trip.dates_may_change:
        raise ValueError("a premium-cabin request with a routing or flexibility wish is not modelled")
    if trip.requested_cabin == Cabin.PREMIUM_ECONOMY:
        return premium(trip, seated)
    if trip.requested_cabin in (Cabin.BUSINESS, Cabin.FIRST):
        return business(trip, seated)
    raise ValueError(f"a {trip.requested_cabin.value} request is not modelled")


def scope_notes(trip, clauses, notes):
    """Sections that bring the traveller or the trip within the rules (lines 76-77, 174-183, 535-536)."""
    if trip.purpose_kind == Purpose.HOME_LEAVE:
        clauses.append(Clause.PURPOSE)
        notes.append("lines 76-77: the policy covers travel entitlements under contracts of employment, e.g. home leave")
    if trip.staff_category != StaffCategory.STAFF_MEMBER:
        clauses.append(Clause.EQUITABLE_APPLICABILITY)
        notes.append("lines 174-179: the policy applies equally to this category of traveller")
    if trip.donor_cabin_terms == DonorCabinTerms.ECONOMY_ONLY:
        clauses.append(Clause.EQUITABLE_APPLICABILITY)
        notes.append("lines 181-183: the policy applies irrespective of donors' own rules; costs the donor disallows "
                     "are charged to other funding")
    if trip.personal_part == PersonalPart.WORK_VISIT_ADDED_TO_PERSONAL_TRIP:
        clauses.append(Clause.COMBINED_TRAVEL)
        notes.append("lines 535-536: the work-related visit's incremental cost, this flight, is allowable")
    elif trip.personal_part != PersonalPart.NO_PERSONAL_PART:
        raise ValueError("personal days added to a work trip are not modelled")


def lowest_route(offers):
    """The cheapest offer, checked against line 230: a connection may only be the answer here when no nonstop
    competes (routes with both go through route())."""
    lowest = cheapest(offers)
    if not lowest:
        raise ValueError("no offer that can be bought")
    if any(not nonstop(offer) for offer in lowest) and any(nonstop(offer) for offer in offers):
        raise ValueError("a cheaper connection beside a nonstop, with no nonstop wish, is not modelled")
    return lowest


def economy(trip, seated):
    """An economy request: the best possible fare (line 233; line 581, the most economical fare), a changeable
    one when dates may move (lines 238-240), and the most direct route when the traveller asks for the nonstop
    (lines 230-231)."""
    pool = [offer for offer in seated if offer.cabin == Cabin.ECONOMY]
    reasons, clauses, notes = [ReasonCode.LOWEST_FARE], list(LOW), []
    if trip.dates_may_change:
        pool = [offer for offer in pool if offer.refundable]
        reasons.append(ReasonCode.FLEXIBLE_FARE_NEEDED)
        clauses = [Clause.AIR_TRAVEL, Clause.PLANNING_AND_BUDGET]
        notes.append("lines 238-240 and 548-549: the dates are likely to change, so the ticket must be changeable "
                     "without significant extra cost: the cheapest changeable fare")
    if trip.donor_cabin_terms != DonorCabinTerms.NOT_STATED:
        raise ValueError("donor cabin terms on an economy request are not modelled")
    relied = []
    if trip.wants_nonstop:
        if trip.dates_may_change:
            raise ValueError("a nonstop wish with changeable dates is not modelled")
        decision, chosen, reasons, clauses, phrase, note = route(pool)
        notes.append(note)
        if decision == Decision.FLAG_FOR_APPROVAL:
            # Lines 569-571 name the supervisor (the line manager) for a choice of ticket that is not obvious.
            relied = [Approver.NOT_NAMED, Approver.LINE_MANAGER]
    else:
        decision, chosen, phrase = Decision.BOOK, lowest_route(pool), ""
        notes.append("line 233: the best possible fare")
    scope_notes(trip, clauses, notes)
    return decision, chosen, reasons, relied, clauses, notes, phrase


def route(pool):
    """Lines 230-231: the most direct route unless an alternative route brings significant financial gains."""
    direct = cheapest([offer for offer in pool if nonstop(offer)])
    connection = cheapest([offer for offer in pool if not nonstop(offer)])
    if not direct or not connection or connection[0].fare_cents >= direct[0].fare_cents:
        raise ValueError("a nonstop wish needs a nonstop and a cheaper connection")
    saving = direct[0].fare_cents - connection[0].fare_cents
    base = direct[0].fare_cents
    said = f"the connection saves {francs(saving)} of the nonstop's {francs(base)}"
    if saving * 100 <= SMALL_SAVING_PERCENT * base:
        return (Decision.BOOK, direct, [ReasonCode.MOST_DIRECT_ROUTE, ReasonCode.ALTERNATE_ROUTE_WITHIN_MARGIN],
                [Clause.AIR_TRAVEL], "",
                f"lines 230-231: {said}, not a significant financial gain, so the most direct route: the nonstop")
    if saving * 100 >= LARGE_SAVING_PERCENT * base:
        # The nonstop is declined because the cheaper connection passes the route test, which is part of the
        # best-fare rule, so LOWEST_FARE is accepted beside the specific codes (lead's decision, every plugin).
        return (Decision.BOOK, connection, [ReasonCode.ALTERNATE_ROUTE_TOO_EXPENSIVE, ReasonCode.COST_SAVINGS,
                                            ReasonCode.LOWEST_FARE],
                [Clause.AIR_TRAVEL, Clause.BOOKING, Clause.COST_EFFECTIVENESS], "",
                f"lines 230-233 and 581: {said}, a significant financial gain: the cheaper route")
    # Lines 569-571: the choice of ticket that is not obvious is discussed with the traveller's supervisor.
    return (Decision.FLAG_FOR_APPROVAL, direct + connection, [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED],
            [Clause.AIR_TRAVEL, Clause.AUTHORIZATION], SIGNIFICANT_PHRASE,
            (f"lines 230-231: {said}; whether that is a 'significant financial gain' the handbook does not say. Hold "
            "either offer; lines 569-571 send a choice of ticket that is not obvious to the traveller's supervisor"))


def verdict_of(offers):
    verdicts = {over("premium-economy", offer) for offer in offers}
    if len(verdicts) != 1:
        raise ValueError("offers on different sides of the premium-economy limit are not modelled")
    return verdicts.pop()


def premium(trip, seated):
    """Line 253: economy plus/premium is allowed for total flying time over eight hours (a permission the traveller
    asked to use); otherwise economy (line 251)."""
    if trip.donor_cabin_terms == DonorCabinTerms.WILL_PAY_BUSINESS:
        raise ValueError("a donor's business offer on a premium-economy request is not modelled")
    clauses, notes = list(CLASS), []
    if verdict_of(seated):
        chosen = lowest_route([offer for offer in seated if offer.cabin == Cabin.PREMIUM_ECONOMY])
        reasons = [ReasonCode.PREMIUM_ECONOMY_ALLOWED]
        notes.append(f"line 253: total flying time {chosen[0].flying_minutes} minutes, over eight hours (ground time "
                     "left out): economy plus/premium is allowed, the cheapest premium fare")
    else:
        chosen = lowest_route([offer for offer in seated if offer.cabin == Cabin.ECONOMY])
        # The reason names why premium economy is declined (line 253's condition), not LOWEST_FARE.
        reasons = [ReasonCode.UPGRADE_NOT_ELIGIBLE, ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET]
        notes.append(f"lines 251-253: total flying time {chosen[0].flying_minutes} minutes, not over eight hours: "
                     "economy class")
    scope_notes(trip, clauses, notes)
    return Decision.BOOK, chosen, reasons, [], clauses, notes, ""


def business(trip, seated):
    """Lines 255-278: business only with a valid medical certificate, exceptional reasons authorised before booking
    by the right director, or another entity paying for the ticket; a donor's willingness is not enough; no first
    class. A declined business request falls back to the best cabin the policy allows."""
    first = trip.requested_cabin == Cabin.FIRST
    clauses, notes, relied = list(CLASS), [], []
    reasons = [ReasonCode.FIRST_CLASS_NOT_PERMITTED, ReasonCode.UPGRADE_NOT_ELIGIBLE] if first else []
    if first:
        notes.append("line 278: first class travel is not permitted")
    valid = certificate_valid(trip)
    authorised = signed(trip, SignOffSubject.BUSINESS_CLASS)
    business_offers = [offer for offer in seated if offer.cabin == Cabin.BUSINESS]
    ground = None
    if valid:
        ground = "medical"
        chosen = lowest_route(business_offers)
        reasons.append(ReasonCode.MEDICAL_NEED)
        relied.append(Approver.HUMAN_RESOURCES)
        notes.append("lines 257-260: a specialist's certificate held by Human Resources, within its six months: "
                     "business class, the cheapest business fare")
    if authorised:
        if ground or len(authorised) != 1:
            raise ValueError("several business grounds or authorisations are not modelled")
        ground = "authorised"
        needed = business_authoriser(trip)
        given = authorised[0].role
        chosen = lowest_route(business_offers)
        if given != needed:
            if first:
                raise ValueError("a wrongly authorised first-class request is not modelled")
            # The authorisation on file is from the wrong role, which is what the case tests: its giver is not
            # accepted, only the role that must sign.
            return (Decision.FLAG_FOR_APPROVAL, chosen, [ReasonCode.APPROVAL_REQUIRED], [needed], list(CLASS),
                    [(f"lines 263-269: business class for exceptional reasons must be authorised before booking by the "
                     f"{needed.value} for this traveller; only a {given.value} signed. Hold the cheapest business "
                     "fare for that authorisation")], "")
        reasons += [ReasonCode.EXCEPTIONAL_REASONS_AUTHORISED, ReasonCode.LONG_FLIGHT_APPROVED]
        relied.append(given)
        notes.append(f"lines 263-269: exceptional reasons, authorised before booking by the {given.value}, the role "
                     "this traveller needs: business class, the cheapest business fare")
    if trip.ticket_paid_by == Payer.ANOTHER_ORGANISATION:
        if ground or not trip.accompanies_flight:
            raise ValueError("another organisation paying without an accompanied flight is not modelled")
        ground = "third party"
        chosen = cheapest([offer for offer in business_offers
                           if offer.segments[0].flight_number == trip.accompanies_flight])
        if not chosen:
            raise ValueError("no business seat on the accompanied flight")
        reasons += [ReasonCode.THIRD_PARTY_PAYS_TICKET, ReasonCode.CLIENT_REIMBURSABLE]
        notes.append("lines 270-272: another entity pays for the ticket and it would not be appropriate to refuse, "
                     "as when accompanying a VIP who travels in business class: business on that flight")
    elif trip.accompanies_flight:
        raise ValueError("an accompanied flight paid by IUCN is not modelled")
    if ground:
        if trip.donor_cabin_terms != DonorCabinTerms.NOT_STATED:
            raise ValueError("donor terms beside a business ground are not modelled")
        scope_notes(trip, clauses, notes)
        return Decision.BOOK, chosen, reasons, relied, clauses, notes, ""
    if first:
        raise ValueError("a first-class request with no business ground is not modelled")
    # No ground: the request's fallback, the best cabin the policy allows. The reasons name why business is declined.
    reasons.append(ReasonCode.UPGRADE_NOT_ELIGIBLE)
    if valid is False:
        reasons.append(ReasonCode.MEDICAL_CERTIFICATE_LAPSED)
        notes.append("lines 257-260: the certificate is more than six months old and was not renewed, so it does not "
                     "ground business class")
    if trip.donor_cabin_terms == DonorCabinTerms.WILL_PAY_BUSINESS:
        reasons.append(ReasonCode.DONOR_FUNDING_NOT_SUFFICIENT)
        clauses.append(Clause.EQUITABLE_APPLICABILITY)
        notes.append("lines 274-276: a donor's willingness to fund business class is not sufficient justification, "
                     "whatever the source of funding (line 181)")
    elif trip.donor_cabin_terms != DonorCabinTerms.NOT_STATED:
        raise ValueError("other donor terms on a business request are not modelled")
    if verdict_of(seated):
        chosen = lowest_route([offer for offer in seated if offer.cabin == Cabin.PREMIUM_ECONOMY])
        reasons.append(ReasonCode.PREMIUM_ECONOMY_ALLOWED)
        notes.append(f"line 253: total flying time {chosen[0].flying_minutes} minutes, over eight hours: the best cabin "
                     "allowed is economy plus/premium, the cheapest premium fare")
    else:
        chosen = lowest_route([offer for offer in seated if offer.cabin == Cabin.ECONOMY])
        notes.append("line 251: no exception applies, so economy class, the cheapest economy fare")
    scope_notes(trip, clauses, notes)
    return Decision.BOOK, chosen, reasons, [], clauses, notes, ""
