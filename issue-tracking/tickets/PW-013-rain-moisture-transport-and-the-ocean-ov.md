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
refs: [planet/climate.py, planet/ocean.py, tools/earth_check.py]
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
Owner's guidance: use Earth as a test analogue, but never chase 100% parity. Original spec:
`81e1d6b:docs/proposals/ocean_overturning.md` (in git history).

## Updates
- 2026-10-15: From the overturning spec (81e1d6b:docs/proposals/ocean_overturning.md): the overturning's temperature pass does not feed back into rain (one extra temperature pass, no rain recompute) - revisit once moisture transport is fixed. The ocean's extra warmth is added to the 50-70N band (moc_zonal = 0), chosen because the Koppen score preferred it (70.69% vs 70.50% with half taken off the band); recheck if the band changes.
- 2026-10-14: Created from morning decision 3 (owner 2026-10-14: 'spin up its own plan').
