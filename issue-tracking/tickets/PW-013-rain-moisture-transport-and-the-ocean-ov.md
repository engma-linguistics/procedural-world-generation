---
id: PW-013
title: Rain / moisture transport, and the ocean-overturning follow-up
type: epic
status: todo
parent: null
subsystem: climate
effort: xl
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [docs/proposals/ocean_overturning.md, planet/climate.py, planet/ocean.py, tools/earth_check.py, docs/review/audit/pw305-prototype.md]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Several climate misses share one root: the rain model doesn't move water vapour between basins and
inland the way Earth's does. So the Atlantic isn't saltier than the Pacific (the overturning needs a
spin-up rule), rain is patchy, monsoons are weak, and the Ganges is ~10× too small.

Stories, in order:
1. Diagnose E−P by ocean basin and vapour transport across land bridges vs observations.
2. Fix moisture transport.
3. Remove the overturning spin-up rule; the Atlantic should turn on and the Pacific stay off by
   themselves.
4. Antarctic sinking: Weddell/Ross too fresh; brine from wind-driven sea-ice export.
5. Salinity memory in the time zoom for off-states (Heinrich events, Younger Dryas).

Owner's guidance: use Earth as a test analogue, but never chase 100% parity. Spec and background:
`docs/proposals/ocean_overturning.md`.

## Updates
- 2026-10-15: Owner 2026-10-15: PW-307 (world land = bed > 0 or grounded ice, threaded through climate/hydrology/coast/zoom) is to be scheduled by this ticket: do it before, during or after the rain rework, whichever fits climate.compute's changes.
- 2026-10-15: Coordinator (2026-10-15): now also owns PW-305's problem: after PW-266 closed the fresh-water books, hot dry interiors recycle their own rain (Earth Koppen exact 38.9 -> 33.0%, B share 28.9 -> 20.3% vs obs 30.1; Sahara 328 mm vs 35, Sahel 2007 vs 593, Australia interior 837 vs 291, Gobi 582 vs 157). Tried and not merged: vapour into moved/downwind air (B), a dry-convective mixed layer (E1: exact 34.3%), a deeper layer (dries SE China/SE USA, whose summers run 4-6 C warm). See docs/review/audit/pw305-prototype.md and fixes-climate-ocean.md. Related: PW-304 (kernel transport not mass-conservative), PW-228, PW-026, PW-290. Moved up the V1 order: next after PW-308.
- 2026-10-15: Merged inbox draft draft-gobi-sahel-wet-not-dry-layer.md ("Earth's Gobi (587 mm vs 157) and Sahel (2015 vs 593) are wet for reasons the dry mixed layer (PW-305) doesn't reach", found by pw305-prototype).
  Probed on Earth L6 with the PW-305 prototype (kernel inputs averaged by region and half-year):
  - **Gobi/Mongolia, July half:** P 1152 mm/yr rate, PET 1085, AET 694. So the ground is wet in the model, and the mixed-layer share stays at 1. The showers trigger easily: `mse_t - mse_thr` is only -7.2 C against `LQ·q` = 11.8. The plateau's air (+15 C of height in `mse_t`) is compared with a reference aloft that follows the latitude's cool sea surface. The extra rain came with PW-266 (303 -> 582 mm).
  - **Sahel, July half:** P ~4000 mm/yr rate, q 3.8 of qs 5.7. It is the monsoon's wet season, not a dry interior. It was already 1679 mm before PW-266 (obs 593).
  
  Both need their own look: the reference aloft over high plateaus, and the West African monsoon's reach. Neither is a recycling problem.
- 2026-10-14: Created from morning decision 3 (owner 2026-10-14: 'spin up its own plan').
