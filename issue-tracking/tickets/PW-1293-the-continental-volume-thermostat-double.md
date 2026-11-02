---
id: PW-1293
title: The continental volume thermostat doubles or triples arc growth late in a run; it stands in for an uncalibrated crust budget
type: task
status: needs-decision
parent: null
milestone: null
subsystem: tectonics
effort: l
impact: med
found_by: lane-100e
blocked_by: []
relates: [PW-1276, PW-046, PW-052, PW-741]
refs: [planet/tectonics/crust.py, docs/review/tectonics/margin/deep-dive.md]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: the model keeps the continents' total volume steady with a thermostat. When they run thin, arcs on
continents grow faster. Late in an L6 run that boost is about 2-3x (the thermostat's integral sits at +0.11 to
+0.26, so e^(4 x ...)). Switched off (`volume_gain=0`, a screen param in lane 100e), the crust thins from 14.2 to
11.6-13.1 km over the surface, land falls from 33-35% to 28-32%, and the worlds run 2-6 C warmer (seeds 1 and 3). So
the arcs' plain rate makes too little crust for what erosion, sediment subduction and subduction erosion take away.
The thermostat is a bookkeeping knob covering that gap. The arc CO2 doesn't see it (PW-741).

Options:
- A. Replace it: set the arc addition rate from a sourced global figure (km3/yr of arc crust per km of trench),
  return part of the subducted sediment to the arc (`crust.accrete` sends half down with the slab), and let the
  volume float. That re-sets calibration, so it needs a full judge.
- B. Keep it, documented as the crust budget's closure.
Lean: B for v1, A for v2. It needs sources first (none read yet).
- [ ] decision A / B

## Updates
- 2026-11-01: Created from inbox draft draft-volume-thermostat-stands-in-for-crust-budget.md (found by lane-100e).
