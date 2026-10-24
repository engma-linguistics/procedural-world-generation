---
id: PW-780
title: "Brightening star default star_brightening 0.45 (a K-type star) is a chosen number: owner sign-off, and check 2 Gyr runs and the cold/hothouse recipes on it"
type: task
status: needs-decision
parent: PW-244
milestone: v1
subsystem: climate
effort: s
impact: high
found_by: v1-finish-7
blocked_by: []
relates: [PW-761, PW-750, PW-564, PW-576, PW-708, PW-202]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, docs/review/base-climate/v1-finish-7/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
v1-finish-7 (docs/review/base-climate/v1-finish-7/README.md) made the brightening star the default. The parameters
are `star_brightening` 0.45 x a Sun-like star's rate on Gough's 1981 curve and `star_age` 0, counted against the
run's start (`earth.star_forcing`).

The results:
- L6, 18 seed-draws: pass 16/18, icehouse median 20%, early / late 14 / 16%.
- L7, 4 showcase seeds x 2 draws: pass 7/8, median 25%.
- Base: L6 5/18 and 46%; L7 3/8 and 45%.
- No always-icebox, no hellhole.

The thermostat is within the literature's range and was not changed. Its realised global e-folding is ~21-38 K,
between Walker/GEOCARB's 10-20 K and Krissansen-Totton & Catling 2017's ~22-45 K. A Sun-like star (1.0) on it
warms 1 Gyr runs ice-free: 16/18 never-ice.

So 0.45 is the owner's lever (2026-10-24): a slower-evolving star of ~0.75 solar masses, plausible but chosen. Open
points:
- [ ] Owner / coordinator sign-off that 0.45 (a K star) is the default rather than e.g. 0.3 (12/18, 67%) or a
  Sun-like 1.0 with a cold offset. 18 draws can't separate 0.2-0.3 from each other (sd ~11 points); 0.45 is the only
  rate that flattened the late trend at L6.
- [ ] Late-run warming at L7: early 0-18%, late 34-38%, so the late trend remains at L7, weaker than base's.
- [ ] 2 Gyr runs: the raw forcing is +11.5 C at 2 Gyr (+5.6 at 1 Gyr), ~0.75 of it passing. The water-world
  recipe (2000 Myr) and Earth-like B (1500 Myr) should be checked for hellholes or late ice-free spells.
- [ ] Never-ice: 3/18 L6 draws (the base's warm seeds 583167, 733847, 958504, at 1-5% icehouse) against 0 at
  base. The bar doesn't count it; say whether it should.
- [ ] Recipes: the cold (climate_offset -6) and hothouse (+5) recipes now sit on a planet that warms by a few C
  over the run; re-pick if they read wrong.
- [ ] PW-564's ticket text estimated the model's sensitivity at 0.56-0.6 C per W/m2. The model's own value is
  co2_sensitivity / (5.35 ln 2) = 0.81: 3 C is per doubling, not per e-fold. star_forcing uses 0.81.

## Updates
- 2026-10-24: Created from inbox draft draft-star-brightening-default-signoff.md (found by v1-finish-7).
