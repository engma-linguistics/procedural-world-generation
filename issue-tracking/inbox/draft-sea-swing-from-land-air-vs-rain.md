---
title: "Sea ice from the land's air works (Hudson Bay -19, southern ice +5%), but the rain kernel is calibrated on the old uniform sea swing and regresses (log-rain 0.617 -> 0.533)"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: base-climate-laneA2
blocked_by: []
relates: [PW-346, PW-570, PW-015, PW-575, PW-017]
refs: [planet/climate.py, docs/review/base-climate/stages.md, docs/review/base-climate/stage2/attempt2.patch, tools/climate_bias.py, tools/earth_check.py]
---

## Description
Lane A stage 2 (PW-346, broadened), Earth L6. The full write-up is in `docs/review/base-climate/stages.md`, "Stage 2".
The code is `docs/review/base-climate/stage2/attempt2.patch` (it applies on b6d707b).

**The mechanism (attempt 2).**
1. The winter air is carried over the sea as well as the land (`_winter_air`):
   - over open water it relaxes toward the water over 300 km;
   - over a frozen sea it relaxes as over land, warmed by the heat conducted up through the ice (k_ice / h against
     the winter air's ~3.5 W/m2/C loss to space) and by the open part of the sea.
2. The sea's seasonal swing is its own (1.9 C × s) plus `continental × land_air`.
   - `land_air` is the share of the air over the sea that came off land within `air_km_w` on the prevailing winds.
   - It correlates at 0.67 with the observed sea-air swing at 35–65 deg: ~±2 C × s over the open Southern Ocean,
     ~6–7 over the northern seas.
   - Main's uniform 6 C × s froze the Southern Ocean at 55–60S as soon as the freeze set the air (attempt 1: southern
     ice +45%).
3. A freezing sea's summer swing loses its winter freezing deficit: the heat goes into melting the ice.

**What it fixes** (model / NCEP, coldest month):

| | main | attempt 2 | NCEP |
|---|---|---|---|
| Hudson Bay | −5.4 | −18.8 | −27.5 |
| Baffin Bay | −11.2 | −23.3 | −30.2 |
| Okhotsk | +1.6 | −9.1 | −9.3 |
| Southern Ocean 60–70S | −5.8 | −18.4 | −14.5 |
| winter sea-ice proxy N / S | 14.2 / 15.0 | 19.7 / 21.2 | 16.8 / 20.2 Mkm2 |

The overturning is fine: Earth NH 11.3 Sv (73% in open polar seas), SH 2.3 → 4.1 Sv, all nine generated worlds sinking
in both hemispheres.

**What it breaks.** The rain:
- log-rain correlation 0.617 → 0.533;
- the summer share of land rain 0.75 → 0.80 (GPCC 0.65);
- Köppen group 71 → 66%; cities exact 32 → 25.

A test with the winds and the rain kernel's half-year SSTs on main's 6 C × s swing brings it back (0.616, 70%). So the
rain kernel (PW-015 stage 1) is tuned to a uniform sea swing that isn't physical.

**Options.**
- A. Land the sea swing together with a re-calibration of the rain kernel to the new half-year SSTs. This is a joint
  stage with the PW-015 lane, so the rain's own guard is checked by its owner.
- B. First find which part of the rain kernel reacts to the SST swing (convection threshold `mse_thr`, evaporation,
  the monsoon winds' land-sea contrast), then decide between A and C.
- C. Keep the uniform swing and look for another way to keep the Southern Ocean open at 55–60S in winter, for
  example deep winter mixing where the column is weakly stratified, as stage 1's `winter_half` does. It is less
  general: the land-air swing also explains why leeward seas swing more.

Lean: B, then A. Giving the air and the rain two different seasonal SSTs for the same sea (tried) recovers the rain,
but it is a split, not a mechanism.

- [ ] the stage-2 bars (stages.md) pass, with earth_check's log-rain correlation and Köppen group not worse than main
