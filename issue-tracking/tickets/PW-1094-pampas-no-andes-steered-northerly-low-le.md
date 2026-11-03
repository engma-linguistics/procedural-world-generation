---
id: PW-1094
title: "Pampas: no Andes-steered northerly low-level jet, so no Amazon vapour reaches it (Paraguay winter PW 6 vs 25 mm)"
type: task
status: todo
parent: PW-013
milestone: later
subsystem: climate
effort: l
impact: med
found_by: lane26
blocked_by: []
relates: [PW-998, PW-013]
refs: [planet/climate.py, docs/review/base-climate/coasts/README.md]
created: 2026-10-30
updated: 2026-11-03
---

## Description
Split from PW-998 (lane 26, option b). **Mechanism:** east of the Andes, the trades and the South Atlantic high's
western flank are channelled south along the mountains as a northerly low-level jet. It carries Amazon vapour to
Paraguay and the Pampas in both halves.

Numbers, Earth L6 db7a178a. Rain's wind (east, north; m/s), model vs NCEP 850 hPa:

| box, half | model | NCEP 850 hPa |
|---|---|---|
| S Brazil/Paraguay, Apr-Sep | -0.4, +0.9 | 1.4, -3.4 |
| S Brazil/Paraguay, Oct-Mar | -5.9, +1.1 | -0.1, -2.0 |

- Paraguay's vapour, Apr-Sep: 6.1 vs NCEP 24.9 mm.
- Pampas rain, model / GPCC:
  - Apr-Sep: 112 vs 565 mm/yr, PW 5.6 vs 16.5.
  - Oct-Mar: 475 vs 1321 mm/yr, PW 22.2 vs 24.5. The vapour is there, but it rains 0.4x the observed rate per mm.
- Annual: 294 vs 943 mm (31%).
- Lane 26's round 1 (shallow cold domes) doesn't move it (291).

What didn't help:
- Feeling the Andes' blocking 600 km out instead of 250 (`block_km`): no change to the wind, Pampas 308.
- 10x eddy mixing: Pampas 390, but B falls to 24.8.

To do: a mountain-channelled flow, where the part of the wind that `deflect` turns along a range carries on
downstream along it, not only within block_km. It waits until lane 26's rounds 1 and 2 are judged (coordinator).

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Earth-only regional residual; Earth is a test analogue (PW-013 relation added).
- 2026-10-30: Lane 58 (docs/review/base-climate/moisture-budget/README.md): Pampas Oct-Mar vapour is right (23.2 vs 24.5 mm) but rains at 0.51x the observed
  rate per mm (66% showers, weak trigger). 45% of it is SW Atlantic vapour, so more sea rain or no sinking air
  there makes the Pampas drier. Only the drift feeds it (no drift: 401 -> 330). Nothing in PW-1093's five
  candidates helps; the jet stays the mechanism.
- 2026-10-30: Coordinator: moved to v2; regional Earth-fidelity refinement, Earth is a plausibility anchor.
- 2026-10-30: Created from inbox draft draft-pampas-andes-low-level-jet.md (found by lane26).
