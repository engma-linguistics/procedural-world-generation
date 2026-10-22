---
id: PW-458
title: Earth's overturning sinks 4 Sv in Baffin Bay; the Norwegian Sea freezes and Fennoscandia's January is 18 C too cold
type: task
status: done
parent: null
milestone: null
subsystem: ocean
effort: l
impact: high
found_by: pw033
blocked_by: []
relates: [PW-033, PW-018]
refs: [planet/ocean.py, planet/climate.py, docs/review/audit/PW-033-diagnosis.md, docs/review/base-climate-review.md]
created: 2026-10-20
updated: 2026-10-22
---

## Description
In `climate.compute` on Earth L6 today (`scratchpad/pw033/ocean.py`, diagnosis section 7):
- NH sinking is 4.1 Sv (real AMOC ~15-20), and its main sites are at 75 N, 63 W: northern Baffin Bay, not
  the Nordic, Labrador and Irminger seas.
- The overturning's SST warming (`moc_heat`) is +3.0 C in the Irminger Sea, +1.1 in the Labrador Sea, and
  -0.4 in the Norwegian Sea. The Norwegian Sea's SST is 0.5 C annual and -1.8 in January (real ~7-8, ice-free).
  The Barents Sea is frozen all year (real south ~2-5 C). The NAD at 45 N is 11.5 C (real ~13-15).
- On land: Fennoscandia Jul / Jan 9.3 / -26.7 C (obs 14.2 / -8.7), British Isles January -3.4 (obs +4.5),
  Fennoscandia precipitation 459 mm (obs 718). The North Atlantic Drift doesn't reach Norway.
- Labrador's +5.5 C summer bias is NOT from this: its sea is near the observed, and hosing the overturning
  off leaves it at 17.4 C.
- Response: at -3 C the sinking moves to Iceland-Irminger (6.5 Sv), at -6 C it collapses to 0.3 Sv, and
  0.3 Sv of hosing shuts it off.

Why it matters: the time zoom's Eurasian ice (Fennoscandia 1.5 Mkm2, Siberia 4 Mkm2 at the deepest glacial)
is largely this cold bias. On the observed baseline Fennoscandia's ice vanishes. Earth's LGM had warm,
seasonally open Nordic Seas feeding the Fennoscandian sheet (Hebbeln et al. 1994).
What to try: find why the inflow is routed into Baffin Bay (densest water there because of the freezing,
leads and ice export?) and why the surface currents carry no NAD past ~55 N toward the Norwegian Sea. Check
it against generated planets' overturning too.
- [ ] Earth's NH sinking in the Nordic, Labrador and Irminger seas, ~10+ Sv; the Norwegian Sea ice-free in
  winter; Fennoscandia's January within ~5 C of the observed

## Updates
- 2026-10-22: Status todo -> done. 2026-10-22 base-climate lane A stage 1 merged (attempt 3): each hemisphere makes its own deep water; the inflow's deep layer damps the sea's winter (moc_layer_m 500). Earth L6 NH 5.1 -> 9.5 Sv, 71% in open polar seas, Baffin 28%, Norwegian coast open all winter; all 9 generated worlds sink in both hemispheres (7082f5's north 0 -> 14.2). Fennoscandia January still -14.7 C (winds, new ticket). docs/review/base-climate/stages.md.
- 2026-10-22: Merged inbox draft draft-overturning-flipped-by-rain-kernel.md ("PW-458 bisect: PW-015 stage 1's rain kernel (1416523) moved Earth's NH sinking from 11 Sv in the Greenland Sea to 4.9 Sv in Baffin Bay", found by base-climate-review).
  For PW-458 (probably `--merge-into PW-458`).
  
  **The bisect.** Earth L6, dT 0, `climate.compute` alone on the fixed geography (~8 s per revision; the planet/ package
  archived per revision; scratch `bc/bisect_moc.py`):
  
  | revision | NH sinking | site | Norwegian-coast sea air, annual / winter (obs +6.8 / +3.5) | Hudson Bay winter (obs −28) |
  |---|---|---|---|---|
  | e4c341a | 10.2 Sv | 72N 28W | +2.4 / −3.3 | −6.0 |
  | cdd867d (the parent side) | 11.3 Sv | 72N 27W | +3.0 / −2.7 | −6.1 |
  | **1416523** (PW-015 stage 1) | **4.9 Sv** | **67N 51W** | −0.1 / −5.8 | −5.2 |
  | 7fbf3b6, and main 3798b6a | 4.9 Sv | 67N 51W | −0.1 / −5.8 | −5.2 |
  
  **What follows from the flip.**
  - The rain kernel moved the sinking into Baffin Bay.
  - `moc_zonal` then cools the Norwegian coast (moc_heat −0.9 C), and the Nordic and Barents seas freeze. Their winters
    are 9.5 and 8 C too cold.
  - Fennoscandia's January is 18.5 C too cold and its July 5.3 C too cold. Iceland's January is 26.6 C too cold.
  
  **Where to look.**
  - The high-latitude seas get a third of GPCP's rain, so the cause isn't more rain at sea.
  - Suspects: the rivers into the Arctic and Baffin Bay, the ice export and the brine. Together they pick which polar
    sea is densest.
  - Next step: factor-separate the salinity budget between 1416523 and its parent.
  - Even before the flip, the Norwegian coast was ~4 C too cold, because the drift stops at ~55N. That is the older half
    of PW-458.
  - Not a fix: pinning the sites, hosing, or moving `moc_lat`.
  
  - [ ] Earth L6: NH sinking 8–20 Sv, ≥ 70% of it in seas open to the Atlantic north of 55N, none in Baffin Bay
  - [ ] the Norwegian coast ice-free in winter; Fennoscandia's January within 6 C and its July within 3 C
  - [ ] 3 generated L6 worlds: no sinking in a basin smaller than `moc_sea_km2`
- 2026-10-20: Created from inbox draft draft-north-atlantic-drift-missing.md (found by pw033).
