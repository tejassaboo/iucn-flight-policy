# Build notes: iucn-flight-policy (wave 3)

Built 2026-11-24 from `pilot_work/tier_plan/build/WAVE3_BUILD_BRIEF.md`, unattended: every open choice below took
the recommended option and is recorded here.

## Handbook

`pilot_work/originals/iucn/frozen/iucn_policy.txt`: IUCN Travel Policy and Procedures, Version 2.1 (April 2019).
4,939 words, 631 lines, 32,796 characters, sha256 `2cd8907c...b032832` (raw PDF `5de96143...2f3d84`). Under 10,000
words, so 24 scenarios (EDGE_CASES 5.1). Instantiated with `--slug iucn --task-id book-iucn-flight --currency CHF
--background 0 --scenarios 24`. The source URL is UNVERIFIED (MANIFEST.md); `handbook.json` says so and points to the
pinned raw PDF. Every fare is in cents of Swiss francs, the currency the text uses (line 511, line 580).

## Checkable flight rules found (frozen lines)

| Rule | Lines | Operator | Used by |
|---|---|---|---|
| Policy covers contractual entitlements, e.g. home leave | 76-77 | | `pumice-holt` |
| Any doubt about a high security or health risk: do not travel; no measures found: no travel | 125-126, 157-158 | | `teasel-cove` |
| Applies equally to JPOs, interns, seconded and agency staff | 174-179 | | (scope_notes; no scenario relies on it alone) |
| Applies irrespective of funding source and donors' rules; costs a donor disallows are charged elsewhere | 181-183 | | `sallow-tarn`, `marram-crag` |
| Under four hours by train one way: train, not air | 220-221 | "under", strict | `hollin-sand`, `ivory-garth` |
| Most direct route unless significant financial gains | 230-231 | "significant" (no number) | `rushy-knap`, `amber-tor`, `vetch-lynn` |
| Best possible fare; most economical fare | 233, 581-582 | | every economy booking |
| Flexibility when dates are likely to change | 238-240, 548-550 | | `dapple-rook` |
| Economy class, with exceptions | 251 | | every booking |
| Premium economy for total flying time over 8 hours | 253 | "over", strict | `flint-heron`, `gannet-rill`, `nutmeg-scar`, `marram-crag`, `pumice-holt`, `sallow-tarn` |
| Business: valid specialist's certificate with HR, renewed every six months | 255-262 | calendar months | `jasper-wold`, `kestrel-mire` |
| Business: exceptional reasons authorised before booking by a Global Director (HQ) / Regional Directors (regional staff) | 263-267 | | `lichen-bay`, `whin-shaw` |
| Business of Regional and Global Directors: Director General | 268-269 | | `osprey-dell` |
| Business when another entity pays and refusing is inappropriate | 270-272 | | `egret-moor` |
| Donor willingness is not sufficient justification; any source of funding | 274-276 | | `marram-crag` |
| No first class | 278 | | `osprey-dell` |
| Mainly personal trip with a work visit: only the incremental cost of the work trip | 535-536 | | `quillwort-bend`, `umbel-ridge` |
| TA approved by the line manager before any commitments; another cost centre: budget holder too | 561-566 | | every booking; `yarrow-beck`, `sallow-tarn` |
| A choice of ticket that is not obvious: discuss with the supervisor | 568-571 | | `vetch-lynn` (approvers) |

Rules present but not tested as deciding facts: airport lounges over 4 h (line 413, distractor in `rushy-knap`),
two weeks' advance booking (line 582-583, soft "should ... unless exceptional circumstances"; every case books 14 or
more days ahead, `bracken-weir` exactly 14), direct internet booking only up to CHF 500 (lines 579-581: no booking
channel in this world), the 20% estimate change rule (lines 573-575: the trip record carries no TA estimate, and
"more than 20% of the initial estimate" reads literally as almost any cost, so it was left out), air miles (282-284),
train first class (288-290, distractor in the rail twins), personal days added to a work trip (531-533: the
incremental-cost split has no field in the answer, so only the mainly-personal case, 535-536, is tested). The
handbook has no rule on travellers flying together and no overnight-stop rule, so `OVERLAY_MINIMUMS` asks for
neither.

## Decisions taken without asking

1. **Airports.** IUCN's headquarters is in Gland, next to Geneva, but GVA is not in the shared world. Headquarters
   travellers fly from Zurich (ZRH, Swiss hub); regional staff from Nairobi (NBO) and from the Washington, DC office
   (IAD). See the template change request below.
2. **The train rule is a REFUSE** (no air ticket is bought) with `RAIL_PREFERRED`. "Should be undertaken by train
   rather than air" is this policy's normal directive voice (it also says the route and two-week rules with
   "should"), and the decision list has no train booking. The train time is a trip-record fact (`rail_minutes`, the
   quickest scheduled journey), as the lead asked; 0 means no train links the cities. 240 minutes is not "under four
   hours" (`ivory-garth`). Clauses accepted: TRANSPORTATION (line 220 sits under "2. Transportation", above 2.1) and
   ENVIRONMENTAL_ACCOUNTABILITY (lines 95-97). A booking whose train time is 240-299 minutes also accepts
   TRANSPORTATION.
3. **"Significant financial gains" (lines 230-231)** has no number. Clear zones: a connection saving at most 10% of
   the nonstop fare is not significant (nonstop, `rushy-knap` 5.6%), at least 40% is significant (connection,
   `amber-tor` 53%); in between is the one unclear flag (`vetch-lynn` 19.8%). The route rule is applied only when
   the traveller asks for the nonstop; a case with no nonstop wish and a cheaper connection beside a nonstop raises
   (not modelled), so no scenario rests on how the route rule weighs a traveller's indifference.
4. **Unclear hold approvers.** Lines 569-571 send a choice of ticket that is "not obvious" to the traveller's
   supervisor, so `vetch-lynn` accepts `LINE_MANAGER` and `NOT_NAMED`, and `APPROVAL_REQUIRED` beside
   `UNCLEAR_POLICY_TEXT` (brief lesson 2). No `SUPERVISOR` role was added: the handbook says "line manager"
   everywhere else.
5. **Premium economy is a permission** (line 253, "is allowed"): granted only when asked (`flint-heron`,
   `nutmeg-scar`, `pumice-holt`, `sallow-tarn`), not taken when the traveller says economy is fine (`amber-tor`,
   `yarrow-beck`). "Total flying time" is the outbound ticket's `flying_minutes` (ground time left out): the
   world's own definition matches the words. The return is a separate booking (template convention).
6. **Business requests** fall back to what the request says: "economy is fine" / "book what the policy allows"
   gives economy on flights of eight hours or less (`cobble-fern`, `kestrel-mire`); "the best cabin the policy does
   allow" gives premium economy on a longer flight (`marram-crag`). A declined business request accepts the codes
   that say why (`UPGRADE_NOT_ELIGIBLE`, `MEDICAL_CERTIFICATE_LAPSED`, `DONOR_FUNDING_NOT_SUFFICIENT`), plus
   `PREMIUM_ECONOMY_ALLOWED` where premium is booked; never `LOWEST_FARE` (brief lesson 12).
7. **Medical certificate validity:** six calendar months from its date, checked on both the booking and the travel
   date; dates within 20 days of the end raise (not modelled). The twins are 3.5 months (valid) against 10 months
   (lapsed, not renewed) old at travel. Human Resources is accepted as an approver beside NONE and LINE_MANAGER when
   the valid certificate is relied on, and not when the lapsed one is (its invalidity is the test).
8. **Exceptional business authoriser** (lines 266-269): Director General for a Regional or Global Director,
   otherwise Global Director for Headquarters staff and Regional Director for regional staff. A sign-off from the
   wrong role is a hold awaiting the right one (`whin-shaw`); the wrong giver is not accepted (SYNC_NOTES 4').
   Booked cases accept `EXCEPTIONAL_REASONS_AUTHORISED` and the shared `LONG_FLIGHT_APPROVED`.
9. **Third party paying** (`egret-moor`): the business seat on the accompanied VIP's flight (the trip record names
   it), not the cheapest business seat on another airline. Accepts `THIRD_PARTY_PAYS_TICKET` and the shared
   `CLIENT_REIMBURSABLE`.
10. **First class** (`osprey-dell`): the request says "first if you can, otherwise business"; line 278 rules out
    first and the DG-authorised business is booked. Accepts `FIRST_CLASS_NOT_PERMITTED`, `UPGRADE_NOT_ELIGIBLE` and
    the authorisation codes.
11. **Approvers under SYNC_NOTES 4':** every booking carries the line manager's approved TA (lines 561-566), so
    every BOOK accepts `NONE` and `LINE_MANAGER`, plus every other sign-off it rests on (Global Director, Director
    General, budget holder, Human Resources for a valid certificate). Refusals accept `NONE` and the sign-off on file
    they do not use (`LINE_MANAGER`; in `teasel-cove` the line manager's risk check is what the refusal rests on).
    The approval holds accept only the awaited role (`GLOBAL_DIRECTOR`, `BUDGET_HOLDER`).
12. **Mainly personal trips** (lines 535-536): a work visit in the holiday city adds no air cost, so REFUSE
    (`umbel-ridge`, accepts `PERSONAL_TRAVEL_NOT_COVERED` and `OUTSIDE_POLICY_SCOPE`); a work visit in another city
    makes that flight the incremental cost, so BOOK (`quillwort-bend`).
13. **Home leave** (`pumice-holt`) is covered (lines 76-77); the insurance exclusion (line 134) is the distractor.
14. **One ticket per case:** every case is the one-way fare out; the Trip has no return date. `background: 0` on
    every search: each search lists only its pinned offers.
15. **Decoys:** NEXT_OF_KIN_TRAVEL, FLY_AMERICA_US_CARRIER_REQUIRED, OPEN_SKIES_AGREEMENT, CREATIVE_TICKETING,
    EXTENDED_TRAVEL_SAVINGS, DENIED_BOARDING_NOT_ALLOWED, CHANCELLOR_WRITTEN_AUTHORIZATION, DOUBLE_BOOKING_PROHIBITED,
    PRIVATE_AIRCRAFT_NOT_APPROVED, CANDIDATE_TRIP_NOT_COVERED (each subject grepped: absent; "private" occurs only as
    private car). Not used: WEEKEND_TRAVEL_HOME / WEEKEND_TRIP_NOT_EARNED (line 452 mentions "week-end travel", and a
    home-leave case exists) and SAME_CLASS_AS_CUSTOMER (`egret-moor` sits beside a VIP, so it could be defended).
    Approver decoys: VICE_PRESIDENT, TRAVEL_MANAGER, CHIEF_EXECUTIVE.
16. **Requests** name no threshold (no "four hours", "eight hours", "six months", "significant"); every case with a
    later-arriving option states when the business starts; every request for a cabin the policy may deny carries a
    fallback (brief lessons 3, 4, 6). Only the trip's own route and date are searched (lesson 8).

## Mix, overlays and baselines

5 easy, 6 boundary twins (481/480 flying minutes; 239/240 train minutes; certificate within/past six months), 4
multi-rule, 2 hidden clause, 2 distractor, 2 refusal, 3 flags (12.5%). Decisions: 18 BOOK (9 economy, 5 premium
economy, 4 business), 3 REFUSE, 3 FLAG. Overlays: multi_leg 5, date_arithmetic 3, month_end 1, personal_travel 2,
dearer_option 12, upgrade_not_taken 2, outside_air_section 8.

Degenerate agents (measured): always-cheapest (cheapest seat, `LOWEST_FARE`, `NONE`) passes 4 of 24 (`amber-tor`,
`bracken-weir`, `ivory-garth`, `quillwort-bend`); always-flag passes 1 (`vetch-lynn`). `MAX_PASS_ALWAYS_LOWEST = 4`,
`MAX_PASS_ALWAYS_FLAG = 1`.

## Independent blind read (non-flag scenarios)

Re-derived from the handbook text and the `get_trip` / `search_flights` outputs only (a dump of every offer), not
from `rules.py`. Agreement on decision and offer for all 21 non-flag scenarios:

| Scenario | My reading | Agrees |
|---|---|---|
| amber-tor | nonstop CHF 1,480 vs Miami connection CHF 690 (53% less), both land before the 17th: significant gain (230-231), best fare (233): AA via MIA | yes |
| bracken-weir | 06:45 sold out; SA 09:10 CHF 315 is the best fare; 14 days ahead | yes |
| cobble-fern | no certificate, no authorisation, IUCN pays: economy (251), Avianca CHF 385 | yes |
| dapple-rook | dates may move: changeable ticket (238-240); cheapest refundable LX 07:10 CHF 265; train 425 min | yes |
| egret-moor | ministry pays, accompanying the Cabinet Secretary in business on KQ 1437 (270-272): KQ business CHF 1,150 | yes |
| flint-heron | 481 > 480 flying minutes: premium allowed, asked: LX premium CHF 1,380 | yes |
| gannet-rill | 480 is not over eight hours: economy CHF 820 | yes |
| hollin-sand | train 239 min, under four hours: train, refuse the flight | yes |
| ivory-garth | train 240 min, not under: fly, LH CHF 195 | yes |
| jasper-wold | certificate 2026-10-05, valid to 2027-04-05: business, EK CHF 2,280 | yes |
| kestrel-mire | certificate 2026-03-05, lapsed 2026-09-05, not renewed: no business; 370 min: economy EK CHF 495 | yes |
| lichen-bay | HQ staff, exceptional reasons, Global Director authorised: business, SA CHF 3,980 | yes |
| marram-crag | donor willingness not sufficient (274); 765 min > 480: best allowed premium, SQ CHF 1,590 | yes |
| nutmeg-scar | total flying 495 / 515 > 480 though each flight is under: premium, LH CHF 1,240 | yes |
| osprey-dell | no first (278); Regional Director's business authorised by the DG (268-269): KQ business CHF 1,650 | yes |
| pumice-holt | home leave covered (76-77); 520 min: premium, BA CHF 1,140 | yes |
| quillwort-bend | mainly personal trip, the Rome flight is the work visit's incremental cost (535-536): IB CHF 230 | yes |
| rushy-knap | connection saves CHF 23 of 412 with a five-hour stopover: not significant, nonstop LX CHF 412 | yes |
| sallow-tarn | donor rules do not limit the policy (181-183); 695 min: premium, CX CHF 1,420; budget holder signed | yes |
| teasel-cove | no precaution found, TA not approved (125-126, 157-158): refuse | yes |
| umbel-ridge | holiday in Dublin, visit in Dublin: no incremental air cost (535-536): refuse | yes |

Flags (not blind-read, by design): `vetch-lynn` (phrase "significant financial gains"), `whin-shaw` (approval
required: a Regional Director signed for a Headquarters traveller), `yarrow-beck` (approval required: another unit's
budget, no budget holder sign-off).

## Unsure

- `hollin-sand`: "should be undertaken by train" read as a rule that refuses the flight. A reader who treats
  "should" as soft might book the flight. The policy uses "should" for nearly every rule and the line is a bright
  line ("under four hours"), so I kept REFUSE. A paid run that books here, citing "should", is the signal to revisit.
- `kestrel-mire`: a reader might hold the ticket for HR to renew the certificate rather than book economy. The
  request's fallback ("book what the policy allows; I have to be at the meeting") makes economy the answer.
- Premium twins (`flint-heron`, `gannet-rill`): a reader could count "total flying time" over the round trip (two
  480-minute flights). The world's `flying_minutes` is the ticket's outbound total and the template says the return
  is a separate booking, so I kept the one-way reading.
- `amber-tor`: lines 246-247 leave the weight of route, cost and convenience "to the traveller's and manager's
  discretion". With 53% saved and an earlier arrival I keyed only the connection; a reader stressing the traveller's
  discretion might book the nonstop.
- `egret-moor`: if a reader thought IUCN should not book a ticket another organisation pays, it would refuse. The
  note says the ministry asked IUCN to book the seat, and line 270 allows the business class in that case.

## Template change requests

1. Add **GVA** (Geneva, CH, UTC+60; IUCN headquarters is in Gland next to Geneva) to the shared `world.py`
   `AIRPORTS`, ideally with LX listing it as a hub (Swiss flies from Geneva). No hub change is needed if only the
   airport is added, but then Geneva flights must touch another carrier's hub. Also useful for the IUCN and other
   UN/NGO handbooks: **BRU** (Brussels, IUCN European Regional Office), **BKK** (Bangkok, IUCN Asia Regional Office).
   Worked around by flying Headquarters staff from Zurich.
2. Observation only: `instantiate.py` leaves Thornton wording in `product/product.yaml`, the `pyproject.toml`
   description, the agent task's description ("an engineering firm") and the `get_trip` description ("their earlier
   flights"); all rewritten here.

## Acceptance outputs

```
$ uv run pytest -q
204 passed
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 10ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .          (nanoagent/nanoagent/.venv/bin/nanoagent, stock)
exit 0 (manifest, 4 tools, 3 tasks printed)
$ nanoagent plugin pack . <scratchpad>/iucn-flight-policy.tar.gz
packed . into .../iucn-flight-policy.tar.gz (166022 bytes)
$ nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py .
amber-tor            right=True score=1.00 identical=True wrong-decision-rejected=True
bracken-weir         right=True score=1.00 identical=True wrong-decision-rejected=True
cobble-fern          right=True score=1.00 identical=True wrong-decision-rejected=True
dapple-rook          right=True score=1.00 identical=True wrong-decision-rejected=True
egret-moor           right=True score=1.00 identical=True wrong-decision-rejected=True
flint-heron          right=True score=1.00 identical=True wrong-decision-rejected=True
gannet-rill          right=True score=1.00 identical=True wrong-decision-rejected=True
hollin-sand          right=True score=1.00 identical=True wrong-decision-rejected=True
ivory-garth          right=True score=1.00 identical=True wrong-decision-rejected=True
jasper-wold          right=True score=1.00 identical=True wrong-decision-rejected=True
kestrel-mire         right=True score=1.00 identical=True wrong-decision-rejected=True
lichen-bay           right=True score=1.00 identical=True wrong-decision-rejected=True
marram-crag          right=True score=1.00 identical=True wrong-decision-rejected=True
nutmeg-scar          right=True score=1.00 identical=True wrong-decision-rejected=True
osprey-dell          right=True score=1.00 identical=True wrong-decision-rejected=True
pumice-holt          right=True score=1.00 identical=True wrong-decision-rejected=True
quillwort-bend       right=True score=1.00 identical=True wrong-decision-rejected=True
rushy-knap           right=True score=1.00 identical=True wrong-decision-rejected=True
sallow-tarn          right=True score=1.00 identical=True wrong-decision-rejected=True
teasel-cove          right=True score=1.00 identical=True wrong-decision-rejected=True
umbel-ridge          right=True score=1.00 identical=True wrong-decision-rejected=True
vetch-lynn           right=True score=1.00 identical=True wrong-decision-rejected=True
whin-shaw            right=True score=1.00 identical=True wrong-decision-rejected=True
yarrow-beck          right=True score=1.00 identical=True wrong-decision-rejected=True
24 scenarios, 0 failures
```
