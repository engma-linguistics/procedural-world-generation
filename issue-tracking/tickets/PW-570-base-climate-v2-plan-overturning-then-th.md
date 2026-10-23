---
id: PW-570
title: "Base-climate v2 plan: overturning, then the sea's air, then summer heat, then the thermostat (set point and star after it)"
type: task
status: in-progress
parent: PW-470
milestone: v2
subsystem: climate
effort: xs
impact: high
found_by: base-climate-review
blocked_by: []
relates: [PW-458, PW-346, PW-352, PW-457, PW-558, PW-559, PW-564, PW-568, PW-569, PW-555]
refs: [docs/review/base-climate-review.md, tools/climate_bias.py]
created: 2026-10-22
updated: 2026-10-23
---

## Description
The base-climate review (`docs/review/base-climate-review.md`) groups the biases that matter for ice under four
mechanisms and proposes a staged plan (its section 4). Decisions for the owner:

1. **The order.**
   - Lean A:
     1. Stage 1: the overturning (PW-458).
     2. Stage 2: the sea's air and the sea ice (PW-346, broadened).
     3. Stage 3: summer heat from a surface energy split, plus small lands' seasons (PW-352/457).
     4. Then hand the ice lane's honest zoom rules their test (PW-568, `tz_earth`).
     5. Stage 4: the thermostat (the weathering law, then the CO2 stock PW-558), then the set point (PW-559 B), then
        brightening (PW-564).
   - Alternative B: the thermostat first, since it is what makes planets ~60% icehouse. But it doesn't touch the
     zoom's tests, so it doesn't unblock the ice lane, and it needs 10-seed sweeps.
2. **The margins' cold summers stay in the ice lane.**
   - The base climate's bare land on Greenland's rim and in Arctic Canada is 1–3 C too *warm* in summer. The cold
     comes from the ice-surface rules (PW-569, PW-439).
   - Lean: yes. Base-climate fixes won't warm those margins.
3. **The set point and the star come after the thermostat.**
   - With today's feedback of ~0.14 C per C, a default offset would be tuned against a broken brake.
   - Brightening (~1.2 C per 100 Myr) would warm 1 Gyr runs by ~10 C.
   - Lean: yes.
4. **An energy-balance curve (option E)** in place of the fixed Earth latitude curve. Lean: not in v2.
5. **Close enough** (review section 4). Lean: stop when all of these hold:
   - ice-region summers within ±3 C and winters within ±6 C on ≥ 80% of rows;
   - sinking in open polar seas at 8–20 Sv;
   - southern sea ice within ±25%;
   - thermostat feedback 0.4–0.9 C per C;
   - icehouse share 15–45% on ~70% of seeds.

- [ ] the owner picks the order and the stop bars

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: 2026-10-22 checkpoint (lane A10, on the PW-579 base climate): the ice lane's honest zoom rules still fail the L4 endings test (102 of 93.5 m left after 15 kyr); tz_earth interglacial ice 12.4-13.7% (fails either way); dt0 today's ice 1.37x. Points back at the ice-surface air (PW-569/439). Re-run after stage 3.
- 2026-10-22: Status needs-decision -> in-progress. Owner 2026-10-22: plan order approved. Coordinator runs two lanes in parallel: lane A = stages 1-3 serially (overturning PW-458, sea air PW-346, summer heat PW-352/457/573), then the checkpoint; lane B = stage 4 starting with the weathering law (PW-574), then PW-558, PW-559, PW-564.
- 2026-10-22: Created from inbox draft draft-base-climate-plan-order.md (found by base-climate-review).
