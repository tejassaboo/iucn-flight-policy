# Audit notes: iucn-flight-policy (2026-11-25)

This file is under tests/ because stock `nanoagent plugin inspect` rejects extra files at the plugin root.

This is an independent audit of the build at 2e01411, done to `pilot_work/tier_plan/build/WAVE3_AUDIT_BRIEF.md`.
I re-derived every answer from the frozen handbook (`src/plugin/data/policy.txt`, IUCN Travel Policy and
Procedures v2.1) and from what the agent sees: `get_trip` and the pinned `search_flights` output (offer ids, fares,
seats, refundability, segments, flying minutes). I did not use `rules.py` to derive the answers. I then compared
each derived answer with every accept set: decision, offer, cabin, reason, approver and clause.

**Verdict: pass after fixes.** On all 21 non-flag scenarios the key's decision and offer match my reading, and the
3 flags are genuine. Every defect was in trip-record wording or in accept sets that were too narrow. No answer
changed category, and no offer, fare, flight or id changed. `MAX_PASS_ALWAYS_LOWEST` stays **4 -> 4** (amber-tor,
bracken-weir, ivory-garth, quillwort-bend, 17%). `MAX_PASS_ALWAYS_FLAG` stays **1** (vetch-lynn).

## Defects found and fixed

| Scenario(s) | Problem | Fix |
|---|---|---|
| flint-heron, gannet-rill | "Total flying time of over 8 hours" (line 253) could be read as the round trip's total. Two 480-minute legs make 960, which would give premium economy at 480 and erase the twin. The task convention says the return is "not part of this decision", but the record did not rule out adding a return. | Both twins carry the same note: "The return is not yet planned: after the planning week the traveller may go on to field work elsewhere in the region, and that travel will be booked separately." There is no return flight time to add, so only this ticket's 481/480 minutes can be measured. The twin fact is unchanged. |
| kestrel-mire (and twin jasper-wold) | A careful agent could hold the business seat until HR has a renewed certificate, since the trip is six weeks away, instead of taking the request's fallback. | Both twins carry the same note: "The traveller next sees the specialist in March 2027, so Human Resources will receive no newer certificate before this trip." In kestrel-mire nothing can be awaited, so the fallback ("book what the policy allows; I have to be at the meeting") gives economy. In jasper-wold the certificate is still valid (to 2027-04-05). The twin fact is still only the certificate date. |
| hollin-sand (and twin ivory-garth) | REFUSE is defined as "the organisation buys no ticket at all for this request", but on the short-rail side a train ticket is still bought. This is the same doubt as ENISA `quartz-fell`. | Both twins carry the same note: "Any train ticket for this trip is bought separately through the rail desk, not through this flight booking." |
| amber-tor | Lines 246-247 leave the weight of route, cost and convenience "to the traveller's and manager's discretion". The traveller wants the nonstop. The nonstop is overnight and 2.5 h shorter, so a reader could weigh convenience (c) over cost and book it. | The record now says: "The traveller has no work planned on February 15th or 16th, so either flight fits the trip's schedule." With convenience neutral and no special risk, only criteria (a) and (b) have content. Both point to the Miami connection, so no weighting of them favours the nonstop. See the settled item below. |
| egret-moor | The ministry "pays the airline for this ticket itself" could make a literal reader take REFUSE ("the organisation buys no ticket"). | The note now reads: "IUCN books and issues this ticket, and the ministry pays the airline for it directly; ...". |
| teasel-cove | "the TA was not approved" could read as "not yet approved", which would make a hold for the line manager look defensible. Also, the refusal rests partly on the TA, but AUTHORIZATION was not accepted. | The note now says "the line manager declined to approve the TA". The key also accepts AUTHORIZATION as a clause. |
| dapple-rook | LOWEST_FARE was accepted, but the lowest-fare sections (BOOKING 581-582, COST_EFFECTIVENESS 108, CLASS_OF_TRAVEL 251) were not. Lesson 5. | The flexible-fare clauses are now `[*LOW, PLANNING_AND_BUDGET]`. The always-cheapest agent still fails, because it books the 18000-cent saver. |
| umbel-ridge | An agent citing "outside the policy's scope" for a holiday flight would cite section I.1 (lines 76-77, "the policy covers work-related travel"), which was not accepted. | The key accepts PURPOSE beside COMBINED_TRAVEL. |
| yarrow-beck | The budget-holder hold sits under III.1.2. An agent could also cite III.1.1 Planning and Budget (line 552: travel only authorised if funds are available within the appropriate budget). | The key accepts PLANNING_AND_BUDGET beside AUTHORIZATION. |

`src/plugin/rules.py` and `verifier/rules.py` are still byte-identical. The scenario JSON was regenerated with
`tests/build_scenarios.py`.

## The builder's unsure list, settled

- **hollin-sand ("travel should be undertaken by train"): REFUSE kept.**
  - The policy's soft rules carry their own qualifier: the route rule says "normally", the two-week rule says
    "unless exceptional circumstances arise", and the train-first-class rule is a permission. Line 220 has none of
    these. Its only hedge is "should", and that is the same voice as "the best possible fare should be secured"
    (233), which every booking applies.
  - Line 220 is a bright line ("under four hours ... in one direction"), and line 217 adds the environmental test.
  - The record gives no reason against the train. The meeting is at 10:00 the next day, and nothing is pending
    that a hold could await.
  - Booking the flight would also erase the 239/240 twin. A reader who still books here is not following line 220.
    The new rail-desk note removes the one real doubt, which was whether REFUSE fits when a train is bought.
- **kestrel-mire (hold for renewal vs economy): economy kept, and the record now decides.**
  - The certificate lapsed on 2026-09-05, before both the booking date and the travel date.
  - The new note says no newer certificate can reach HR before the trip, so a hold has nothing to wait for.
  - The request's fallback says "book what the policy allows; I have to be at the meeting".
  - FLAG is not accepted.
- **Premium twins (one-way vs round-trip "total flying time"): the record now says which.**
  - The task convention already says the return is booked separately and is not part of this decision.
  - The new note makes the return unknowable, so the only measurable "total" is this ticket's flying minutes. That
    total sums the segments and leaves ground time out, as nutmeg-scar tests.
  - Both twins keep their single-fact difference (481 vs 480).
  - The other cases are unaffected: every other premium case is over 480 one way. kestrel-mire (370 one way) and
    cobble-fern (305) list no premium offer, or ask for economy as the fallback, so a round-trip reading changes
    nothing there.
- **amber-tor (discretion, lines 246-247): connection only, nonstop not accepted.**
  - Discretion sets how much each criterion weighs. It does not change what each criterion says.
  - (a) Route: the direct route is the norm "unless there are significant financial gains". A CHF 790 saving (53%)
    is significant on any reading, so even with full weight, (a) points to the connection.
  - (b) Cost: the best possible fare, reinforced by "Travel must be cost effective" (108) and "the most economical
    fare" (581-582).
  - (c) Convenience is now neutral by the record, (d) does not apply, and (e) has no special risk on file.
  - The traveller's wish is conditional ("if the policy is OK with it"), and the manager has expressed no
    preference.
  - Paying 2.1 times the fare is therefore not a defensible reading. Accepting the nonstop would also leave the case
    testing nothing, since both listed offers would pass.
  - The 10%/40% clear zones and the vetch-lynn flag at 19.8% stay as built.
- **egret-moor (IUCN booking a seat another entity pays for): BOOK kept.**
  - Line 270 allows business exactly here: another entity pays, and the traveller accompanies a VIP who flies
    business.
  - The note now states that IUCN books and issues the ticket.
  - The key's offer is the business seat on the VIP's own flight, KQ 1437, named in `accompanies_flight`. It is not
    the cheaper EgyptAir business seat.

## Other checks

- **Flags:** three, 12.5%.
  - vetch-lynn is genuinely unclear. "Significant financial gains" gets no measure, and the CHF 85 (19.8%) saving
    comes with 145 more minutes. Both offers are held, APPROVAL_REQUIRED is accepted beside UNCLEAR_POLICY_TEXT, and
    the approver accepts LINE_MANAGER or NOT_NAMED, because lines 569-571 name the "supervisor".
  - whin-shaw is a clear approval hold. The traveller is Headquarters staff, so business needs a Global Director's
    authorisation (266-267), and only a Regional Director signed. The awaited role (GLOBAL_DIRECTOR) is the only
    approver accepted.
  - yarrow-beck is a clear approval hold. The trip is charged to another cost centre, and no budget-holder sign-off
    is on file (564-566). BUDGET_HOLDER is the only approver accepted.
- **Twins:** each pair differs in one fact.
  - 481/480 flying minutes, with the arrival a minute apart.
  - 239/240 rail minutes.
  - Certificate dated 2026-10-05 or 2026-03-05.
  - lichen-bay/whin-shaw: which director signed.
  - The new notes are identical within each pair.
- **Requests:**
  - None uses threshold or rule wording. No request says "four hours", "eight hours", "six months" or
    "significant".
  - Every request that asks for a cabin the policy may deny carries a fallback.
  - Every case where arrival time could matter states when the business starts.
  - Only the trip's own route and date are searched.
- **Instructions:** the decline sentence follows the conventions line in `nanoagent.yaml`.
- **Declined requests:** no declining BOOK accepts LOWEST_FARE. That covers cobble-fern, gannet-rill, kestrel-mire,
  marram-crag and osprey-dell. The exception is amber-tor, where the nonstop is declined on the route/savings test,
  so it accepts LOWEST_FARE together with ALTERNATE_ROUTE_TOO_EXPENSIVE and COST_SAVINGS (lesson 12).
- **Approvers (SYNC_NOTES 4'):**
  - Every BOOK accepts NONE and LINE_MANAGER, plus each sign-off it relies on: HR (jasper-wold), Global Director
    (lichen-bay), Director General (osprey-dell) and budget holder (sallow-tarn).
  - The refusals accept NONE and LINE_MANAGER.
- **Constraints on keyed bookings:** I checked every keyed booking against every stated constraint:
  - the cabin rules (251-278);
  - the best fare (233);
  - the route (230-231);
  - flexibility (238-240);
  - the TA approved before commitment (561-566);
  - the train rule (220);
  - two weeks' advance (582-583): every case books 14 or more days ahead;
  - the incremental cost (535-536);
  - risk (125-126, 157-158).

## Re-derivation (all agree with the key after the fixes)

- **Easy:**
  - amber-tor: AA via MIA, CHF 690 (53% under the nonstop).
  - bracken-weir: SA 09:10, CHF 315 (the 06:45 is sold out; 14 days ahead).
  - cobble-fern: Avianca economy, CHF 385 (no business ground).
  - dapple-rook: LX 07:10 flex, CHF 265 (cheapest changeable; the train takes 425 min).
  - egret-moor: KQ 1437 business, CHF 1,150.
- **Boundary twins:**
  - flint-heron: LX premium (481 > 480).
  - gannet-rill: LX economy (480 is not over 480).
  - hollin-sand: REFUSE (239 < 240).
  - ivory-garth: LH CHF 195 (240 is not under 240).
  - jasper-wold: EK business CHF 2,280 (the certificate is valid to 2027-04-05).
  - kestrel-mire: EK economy CHF 495 (the certificate lapsed 2026-09-05; 370 min).
- **Multi-rule:**
  - lichen-bay: SA business CHF 3,980 (HQ staff, Global Director signed).
  - marram-crag: SQ premium CHF 1,590 (donor willingness is not enough; 765 min).
  - nutmeg-scar: LH premium CHF 1,240 (total flying 495/515 > 480).
  - osprey-dell: KQ business CHF 1,650 (no first class; the DG authorised a Regional Director).
- **Hidden clause:**
  - pumice-holt: BA premium CHF 1,140 (home leave is covered, 76-77; 520 min).
  - quillwort-bend: IB CHF 230 (the work visit's incremental flight).
- **Distractor:**
  - rushy-knap: LX nonstop CHF 412 (5.6% saving; the lounge clause decides nothing).
  - sallow-tarn: CX premium CHF 1,420 (donor rules do not limit the policy; the budget holder signed).
- **Refusal:**
  - teasel-cove: no measure was found and the TA was declined.
  - umbel-ridge: the holiday flight has no incremental work cost.
- **Flags:** vetch-lynn, whin-shaw, yarrow-beck (above).

## Acceptance (after the fixes)

```
uv run pytest -q                                   204 passed
uv run ruff check .                                All checks passed!
uv lock --check                                    Resolved 42 packages
python3 ../_template/check_shared.py .             : ok
<stock venv>/bin/python ../_template/tools/stock_verify.py .   24 scenarios, 0 failures
<stock venv>/bin/nanoagent plugin inspect .        exit 0
```
