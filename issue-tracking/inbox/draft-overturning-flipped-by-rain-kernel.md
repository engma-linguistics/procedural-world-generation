---
title: "PW-458 bisect: PW-015 stage 1's rain kernel (1416523) moved Earth's NH sinking from 11 Sv in the Greenland Sea to 4.9 Sv in Baffin Bay"
type: task
status: todo
parent: null
milestone: v2
subsystem: ocean
effort: m
impact: high
found_by: base-climate-review
blocked_by: []
relates: [PW-458, PW-016, PW-015, PW-038]
refs: [planet/ocean.py, planet/climate.py, docs/review/base-climate-review.md]
---

## Description
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
