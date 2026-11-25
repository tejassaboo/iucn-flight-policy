# Validation notes: iucn-flight-policy (paid wave 3 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w3_2026-11-25/iucn-flight-policy@w3/`, arm
`full`, DeepSeek V4 Flash (Nebius), temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin
head d07b1e8. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

22/24 valid (91.7%), mean field score 0.958, **easy 5/5**. By category: boundary_twin 6/6, distractor 1/2, easy 5/5, flag 2/3, hidden_clause 2/2, multi_rule 4/4, refusal 2/2.
$0.00131 billed per run, 10,090 prompt tokens per call, 3.96 calls per run;
0 of 24 runs would exceed the hosted 65,536 cap.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| sallow-tarn | distractor | BOOK Cathay economy, DONOR_FUNDING_NOT_SUFFICIENT; key Cathay premium economy | model slip | "the trip is funded by the delta wetlands project grant, whose donor rules allow economy seats only ... the premium economy upgrade is not eligible." It never read lines 181-183: the policy applies "irrespective of donors' own rules", and costs the donor disallows are charged to other funding. 695 minutes is over 8 hours (line 253). |
| vetch-lynn | flag | BOOK Swiss nonstop, MOST_DIRECT_ROUTE; key FLAG | model slip | "The nonstop is the most direct route and is consistent with the travel policy's air-travel criteria". It never weighed whether CHF 85 (20% of the fare) is a "significant financial gain" (lines 230-231), or lines 568-571 (a choice of ticket that is not obvious is discussed with the supervisor). The twins rushy-knap and amber-tor passed. |

## Fixes

None. All 2 failures are model slips; no key was widened and no record changed.

## Q2

Unchanged: the always-cheapest agent passes **4/24 (17%)**.

## Re-score at the head (stored answers)

22/24 (no key changed). No re-run is required.

## Checks (at the notes commit)

`uv run pytest -q` (204 passed), `uv run ruff check .`, `uv lock --check`, `check_shared.py`, byte-identical `rules.py`,
`tools/stock_verify.py` (0 failures), stock `nanoagent plugin inspect .` (exit 0).
