---
id: PW-266
title: Rain kernel recycles 41% of land rain while the water balance evaporates 60%; the freshwater mean hides the gap
type: task
status: in-progress
parent: PW-245
subsystem: climate
effort: s
impact: med
found_by: audit-climate-ocean
blocked_by: []
relates: [PW-013, PW-026, PW-228]
refs: [planet/climate.py, planet/ocean.py, docs/review/audit/climate-ocean.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
The atmosphere and the surface keep separate water budgets.
- `_rain` adds land evaporation as `et × warm × local rain` (climate.py:930-934). That comes to 41% of land rain globally. Budyko's `water_balance` evaporates 60% of it.
- The kernel also takes up vapour over sea ice (13,800 km³/yr). `compute` then zeroes that evaporation (line 1838).
- The difference shows up as a non-zero freshwater mean, which `ocean.freshwater` subtracts uniformly (ocean.py:470-472).

Measured on run a1d3b9 (last frame on L6, km³/yr):
- Kernel land recycling is 65,800; Budyko AET is 95,400.
- P_sea − E_sea + runoff = −16,800 (mean −0.0475 m/yr, removed).
- With `et` = 0.73, land rain rises 22% and the mean flips to +0.074, so the budget closes near et ≈ 0.55–0.6.

Too little recycled moisture over land is a candidate cause for the dry interiors (PW-026, PW-228). It is also what `vapour_mixed` patches for humidity.

Simplest sound fix: give the kernel the water balance's own per-cell evaporation share. Take AET/P from a first `water_balance` on the first-pass temperatures (already computed in `_land_finish`'s inputs), clipped to [0, 1], in place of the uniform `et` (keep vegetation's ±band on top). Then multiply the kernel's sea uptake by the open-water share. The freshwater mean should then come out near 0 by itself. Keep the subtraction, but add an assert or warning if |mean| > 1 cm/yr.
- [ ] |freshwater mean| < 0.01 m/yr on a few L6 seeds and on Earth
- [ ] earth_check and veg_check re-run; regional rain (PW-228) compared before and after

## Updates
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Created from inbox draft draft-audit-climate-ocean-rain-recycling-vs-budyko.md (found by audit-climate-ocean).
