# IUCN Flight Policy

**Source of the handbook:** https://iucn.org/sites/default/files/2022-08/iucn_travel_policy_for_staff_v2.1_april2019.pdf. The agent reads it verbatim (bundled at `src/plugin/data/policy.txt`); flights, fares and trips are synthetic.

**No affiliation with IUCN.** The handbook is the International Union for Conservation of Nature's *Travel Policy
and Procedures*, Version 2.1 (April 2019), a published policy of the union, bundled verbatim for research. Its public
source URL was not recorded (the raw PDF under `pilot_work/originals/iucn/` is the pinned copy): confirm the URL
before publishing this plugin.

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under IUCN's real travel policy:
it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and policy section. A deterministic Python verifier,
with no LLM, rebuilds the offers and the policy's answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files (the
JSON files are the truth).

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 4,939 words, 631 lines, 32,796 characters, sha256
`2cd8907c...b032832`, equal to `pilot_work/originals/iucn/frozen/SHA256SUMS`) is never paraphrased, and the task text
restates no rule. The PDF conversion left about ten mid-word stray spaces ("Gl obal", "R egional", "the t ravel") and
interleaved footnotes; they are kept as they are. Under stock NanoAgent the agent does not see the text: the plugin
then runs as the `off` baseline. The `harness.policy` switch of the NanoAgent fork (github.com/tejassaboo/nanoagent,
branch `policy-switch`) adds it to the system prompt: `harness.policy: full` adds all of it, and the selection
methods add parts of it. These plugins are meant to run with `query: instructions+input`, so a selector sees the
traveller's request.

**Size.** At 1.33 tokens a word the policy is about 6,600 tokens (about 8,200 at 4 characters a token). On the
DeepSeek calibration of the paid Thornton and NJC runs (about 0.2 tokens a character of handbook plus 1,800) the
first call under `full` is about 8,400 input tokens, the second about 9,400 (plus the trip record) and the third
9,800 to 11,000 (plus 2 to 6 offers). A 3-call run (`get_trip`, `search_flights`, `submit`) is about 28,000 to
30,000 input tokens, and the final-message call after `submit` starts near 11,500: far under the hosted cap of
65,536.

**Flight duration, as this handbook defines it** (`rules.DURATION_RULES`, `rules.over`). Line 253: "Economy
plus/premium class1 is allowed for total flying time of over 8 hours": the scheduled minutes of every flight of the
ticket added together, ground time left out (the offer's `flying_minutes`), strictly over 480. A nonstop of 481
minutes qualifies, 480 does not; a connection of 50 + 445 minutes qualifies although neither flight does. The train
rule (line 220, "under four hours by train", strict at 240 minutes) is not a flight duration: the trip record gives
the quickest train journey (`rail_minutes`), a trip-record fact only.

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date (every case buys the one-way fare
  out), then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing;
  otherwise the chosen offer's own), `reason_code`, `approver` and `clause`, each from a closed list. The reason
  list is the template's shared list plus eight IUCN codes (`MOST_DIRECT_ROUTE`, `FLEXIBLE_FARE_NEEDED`,
  `EXCEPTIONAL_REASONS_AUTHORISED`, `THIRD_PARTY_PAYS_TICKET`, `MEDICAL_CERTIFICATE_LAPSED`,
  `DONOR_FUNDING_NOT_SUFFICIENT`, `FIRST_CLASS_NOT_PERMITTED`, `TRAVEL_RISK_NOT_MITIGATED`) and decoy codes from
  other handbooks' rules. Fares are in cents of Swiss francs (CHF).
- **Success:** every field is one the answer key accepts. Score = fields right / 6.
- **Reasons on a declined request.** The task instructions say that when the booking is not what the traveller
  asked for, the reason code gives why the request is declined. Such a booking accepts only the codes that name the
  policy's ground, not `LOWEST_FARE`: business declined (`cobble-fern`, `kestrel-mire`, `marram-crag`), premium
  economy declined (`gannet-rill`), first class declined (`osprey-dell`). The nonstop declined because the
  cheaper connection passes the route test (lines 230-231, `amber-tor`) accepts `LOWEST_FARE` beside the specific
  codes (lead's decision, the same in every plugin).
- **No hidden facts:** no `answer_key_inputs`. The trip record carries what a booking tool would not show by itself:
  the traveller's post and duty station, the quickest train journey, who pays and from which budget, what the donor
  says about cabins, the date of a medical certificate held by Human Resources, the line manager's risk check, the
  flight of a person accompanied, personal travel linked to the trip, sign-offs on file and notes.

| Scenario | Category | Expected decision (offer; cabin) | Reason | Approver | Clause (frozen lines of must_keep) |
|---|---|---|---|---|---|
| `cypress-ember` | easy | BOOK (midday-economy; ECONOMY) | BUSINESS_REASON_MISSING or LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or DEFINITIONS or POLICY or PROCEDURE (122, 126-127, 117-118, 47-49, 17-19, 34-37) |
| `heron-gable` | easy | BOOK (morning-economy; ECONOMY) | LOWEST_FARE or REQUESTED_TIME_WINDOW | DEAN or NONE or SUPERVISOR | AIR_TRAVEL or DEFINITIONS or POLICY or PROCEDURE (115-116, 117-118, 17-19, 34-37) |
| `mangrove-lute` | easy | BOOK (american-premium; PREMIUM_ECONOMY) | FARE_WITHIN_TOLERANCE or PREMIUM_ECONOMY_ALLOWED or UPGRADE_WITHIN_FARE_MARGIN | DEAN or FACULTY_AFFAIRS or NONE or SUPERVISOR | AIR_TRAVEL or PROCEDURE (121, 126-127, 123, 128-129, 17-19, 34-37) |
| `pelican-arch` | easy | BOOK (atlanta-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or DEFINITIONS or POLICY or PROCEDURE (149-150, 117-118, 47-49, 17-19, 34-37) |
| `sawgrass-loom` | easy | BOOK (iberia-economy; ECONOMY) | LOWEST_FARE | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or DEFINITIONS or INTERNATIONAL_TRAVEL or POLICY or PROCEDURE (117-118, 47-49, 233-235, 17-19, 34-37) |
| `egret-sable` | boundary_twin | BOOK (atlanta-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | DEAN or NONE or SUPERVISOR | AIR_TRAVEL or DEFINITIONS or POLICY or PROCEDURE (149-150, 120, 126-127, 128-129, 117-118, 17-19, 34-37) |
| `ibis-quarry` | boundary_twin | BOOK (united-premium; PREMIUM_ECONOMY) | FARE_WITHIN_TOLERANCE or PREMIUM_ECONOMY_ALLOWED or UPGRADE_WITHIN_FARE_MARGIN | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or PROCEDURE (121, 126-127, 123, 128-129, 17-19, 34-37) |
| `manatee-reed` | boundary_twin | BOOK (latam-economy; ECONOMY) | BUSINESS_REASON_MISSING or LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or DEFINITIONS or INTERNATIONAL_TRAVEL or POLICY or PROCEDURE (122, 126-127, 117-118, 47-49, 233-235, 17-19, 34-37) |
| `osprey-quill` | boundary_twin | BOOK (united-economy; ECONOMY) | BUSINESS_REASON_MISSING or LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or DEFINITIONS or POLICY or PROCEDURE (121, 126-127, 117-118, 47-49, 17-19, 34-37) |
| `snook-larder` | boundary_twin | BOOK (nonstop-economy; ECONOMY) | ALTERNATE_ROUTE_WITHIN_MARGIN or FARE_WITHIN_TOLERANCE or LOWEST_FARE | DEAN or NONE or SUPERVISOR | AIR_TRAVEL or DEFINITIONS or POLICY or PROCEDURE (149-150, 123, 128-129, 117-118, 17-19, 34-37) |
| `tarpon-mesa` | boundary_twin | BOOK (american-business; BUSINESS) | FARE_WITHIN_TOLERANCE or INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED or UPGRADE_WITHIN_FARE_MARGIN | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or INTERNATIONAL_TRAVEL or PROCEDURE (122, 126-127, 123, 128-129, 233-235, 17-19, 34-37) |
| `anhinga-dell` | multi_rule | BOOK (atlanta-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or DEFINITIONS or POLICY or PROCEDURE (149-150, 120, 126-127, 128-129, 117-118, 17-19, 34-37) |
| `gannet-wold` | multi_rule | BOOK (atlanta-economy or nonstop-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or CONNECTION_TOO_LONG or COST_SAVINGS or LOWEST_FARE | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or DEFINITIONS or POLICY or PROCEDURE (149-150, 120, 126-127, 117-118, 17-19, 34-37) |
| `kestrel-isle` | multi_rule | BOOK (late-morning-business; BUSINESS) | BUSINESS_REASON_DOCUMENTED or LOWEST_FARE or NO_ECONOMY_SEATS_URGENT | DEAN or FACULTY_AFFAIRS or NONE or SUPERVISOR | AIR_TRAVEL or PROCEDURE (122, 126-127, 117-118, 17-19, 34-37) |
| `lumen-bay` | multi_rule | BOOK (late-morning-economy; ECONOMY) | COMPANION_UNIVERSITY_ROLE or LOWEST_FARE or REQUESTED_TIME_WINDOW | DEAN or NONE or SUPERVISOR | AIR_TRAVEL or BOOKING_FOR_OTHERS or DEFINITIONS or POLICY or PROCEDURE (269-272, 115-116, 117-118, 17-19, 34-37) |
| `brine-lattice` | hidden_clause | BOOK (midday-economy; ECONOMY) | LOWEST_FARE | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or DEFINITIONS or INTERNATIONAL_TRAVEL or POLICY or PROCEDURE (74-76, 233-235, 117-118, 47-49, 17-19, 34-37) |
| `pompano-ridge` | hidden_clause | BOOK (american-economy; ECONOMY) | FLY_AMERICA_US_CARRIER_REQUIRED or NATIONAL_CARRIER_REQUIRED or OPEN_SKIES_AGREEMENT | DEAN or FACULTY_AFFAIRS or NONE or SUPERVISOR | DEFINITIONS or INTERNATIONAL_TRAVEL or POLICY (58-59, 233-235, 17-19, 34-37) |
| `marlin-cove` | distractor | BOOK (delta-economy; ECONOMY) | BUSINESS_REASON_MISSING or LOWEST_FARE or LOYALTY_PROGRAM_PREFERENCE | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or DEFINITIONS or POLICY or PROCEDURE (120, 126-127, 128-129, 123, 117-118, 17-19, 34-37) |
| `saffron-key` | distractor | BOOK (friday-jetblue; ECONOMY) | LOWEST_FARE or PERSONAL_EXTENSION_COMPARISON or PERSONAL_TRAVEL_NOT_COVERED | NONE or SUPERVISOR or VICE_PRESIDENT | AIR_TRAVEL or PROCEDURE (139-144, 135-136, 17-19, 34-37) |
| `ochre-fen` | refusal | REFUSE (none; NONE) | OUTSIDE_POLICY_SCOPE or PERSONAL_TRAVEL_NOT_COVERED | NONE | DEFINITIONS or POLICY or PURPOSE or SCOPE (26-31, 68-70, 106-107) |
| `wren-hollow` | refusal | REFUSE (none; NONE) | COMPANION_NOT_COVERED or PERSONAL_TRAVEL_NOT_COVERED | DEAN or NONE or SUPERVISOR | BOOKING_FOR_OTHERS or DEFINITIONS (269-272, 71-72) |
| `jasmine-shoal` | flag | FLAG_FOR_APPROVAL (atlanta-economy or atlanta-premium; ECONOMY or PREMIUM_ECONOMY) | APPROVAL_REQUIRED or UNCLEAR_POLICY_TEXT | EXECUTIVE_VICE_PRESIDENT or NOT_NAMED or TRAVEL_MANAGEMENT | AIR_TRAVEL or PROCEDURE (121, 126-127, 123, 102-104, 62-63, 17-19, 34-37) |
| `thistle-pier` | flag | FLAG_FOR_APPROVAL (american-economy; ECONOMY) | APPROVAL_REQUIRED | FACULTY_AFFAIRS | POLICY or PURPOSE or SCOPE (17-19, 34-37, 117-118) |
| `vesper-tide` | flag | FLAG_FOR_APPROVAL (united-business or united-economy; BUSINESS or ECONOMY) | APPROVAL_REQUIRED or UNCLEAR_POLICY_TEXT | EXECUTIVE_VICE_PRESIDENT or NOT_NAMED or SUPERVISOR or TRAVEL_MANAGEMENT | AIR_TRAVEL or PROCEDURE (122, 126-127, 102-104, 62-63, 17-19, 34-37) |

Mix (EDGE_CASES.md 5.2, 24 row): 5 easy, 6 boundary twins, 4 multi-rule, 2 hidden clause, 2 distractor, 2 refusal,
3 flags (12.5%; the cap is 3). Decisions: 18 BOOK (9 economy, 5 premium economy, 4 business), 3 REFUSE, 3
FLAG_FOR_APPROVAL. Twin pairs: a nonstop of 481 or 480 scheduled minutes (`flint-heron`, `gannet-rill`); a train
journey of 239 or 240 minutes (`hollin-sand`, `ivory-garth`); a medical certificate dated 2026-10-05 or 2026-03-05
against six months (`jasper-wold`, `kestrel-mire`); and, against the approval flag, business authorised by a Global
or by a Regional Director for a Headquarters traveller (`lichen-bay`, `whin-shaw`).

Flags, each with clear twins on both sides:

- `vetch-lynn` (unclear): the traveller prefers the nonstop; the connection saves CHF 85 of CHF 430 (about 20%) and
  adds 145 minutes. Lines 230-231 keep the most direct route "unless there are significant financial gains from
  taking an alternative route", with no measure. Twins `rushy-knap` (under 6% saved: nonstop) and `amber-tor` (53%
  saved: connection). Either held offer is accepted; lines 569-571 send a choice of ticket that is not obvious to the
  traveller's supervisor, so `LINE_MANAGER` and `NOT_NAMED` are accepted, and `APPROVAL_REQUIRED` beside
  `UNCLEAR_POLICY_TEXT`.
- `whin-shaw` (approval required): a Headquarters traveller's exceptional business class is authorised by a Regional
  Director, but lines 266-267 need a Global Director. Twins `lichen-bay` (Global Director: business booked) and
  `cobble-fern` (no ground: economy). Only `GLOBAL_DIRECTOR` is accepted as the approver.
- `yarrow-beck` (approval required): the trip is charged to another unit's budget and only the line manager signed;
  lines 564-566 need the budget holder too. Twins `sallow-tarn` (budget holder signed: booked) and `bracken-weir`
  (own budget: booked). Only `BUDGET_HOLDER` is accepted.

Approvers (template SYNC_NOTES 4'): every booked trip has the line manager's approved Travel Authorization (lines
561-566). A BOOK accepts `NONE`, `LINE_MANAGER` and every other sign-off it rests on (the Global Director, the
Director General, the budget holder; Human Resources for the medical certificate); a refusal accepts `NONE` and the
sign-off on file it does not use; the approval holds accept only the awaited role. The Regional Director in
`whin-shaw` and Human Resources in `kestrel-mire` (a lapsed certificate) are not accepted, because their invalidity
is what the case tests. Degenerate agents (`tests/test_verifier.py`): always holding the right offer as unclear passes
1 case (`vetch-lynn`); always booking the cheapest seat with `LOWEST_FARE` and `NONE` passes 4 (`amber-tor`,
`bracken-weir`, `ivory-garth`, `quillwort-bend`).

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, post and duty station, route, date, purpose, requested cabin and routing, train time, payer, budget, donor terms, medical certificate, risk check, accompanied flight, sign-offs, notes | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date: the pinned scenario offers only (no background offers in this plugin); a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-iucn-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this policy's scenario ids, approvers, sections, eight reason
  codes, decoys and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this
  policy's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this policy's settings.
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).
- `tests/BUILD_NOTES.md`: design decisions, the blind read and the acceptance outputs.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/iucn-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
