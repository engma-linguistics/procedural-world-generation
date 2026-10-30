---
id: PW-780
title: "Brightening star default star_brightening 0.45 (a K-type star) is a chosen number: owner sign-off, and check 2 Gyr runs and the cold/hothouse recipes on it"
type: task
status: done
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
updated: 2026-10-29
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
- 2026-10-29: Removed docs/review/base-climate/v1-finish-7/ in cleanup; last present at 9861e2df.
- 2026-10-24: Status needs-decision -> done. Owner 2026-10-24: 0.45 is fine as the base rate; the star thermostat (PW-791) handles the long run.
- 2026-10-24: Sign-off page docs/review/base-climate/v1-signoff/README.md. Coordinator: v1 bar is 1 Gyr (13/18 L6, 7/8 L7); the 2 Gyr late window (4/13, one hellhole) goes with PW-791 after v1.
- 2026-10-24: v1 sign-off summary docs/review/base-climate/v1-signoff/README.md (Earth-like only). Strict: L6 1 Gyr 13/18, L7 1 Gyr 7/8 (unchanged code since v1-finish-8); L6 2 Gyr whole run 10/13 with 6 new draws, but the 1500-2000 window only 4/13 (6 ice-free, 1 hellhole: 957317 +0.001 at +10.5 / 15.5); one new L7 2 Gyr draw stopped at 1500 Myr (warm, ~15% icehouse samples). Main open question: the star-warmed L7 showcases are nearly treeless (1.7-20%, wet tropics 1-8%): low pCO2 plus warmth on too-steep plant responses; draft-treeless-tropics-co2-heat.md.
- 2026-10-24: v1-finish-8 merged 2b2299e. Strict bar: L6 13/18 (72%), L7 7/8. Awaiting owner's final sign-off on 0.45; then v1 closes.
- 2026-10-24: Owner 2026-10-24: for Earth-like worlds NO ice ages is a fail too. The star's brightening is the accepted per-world lever (slower/none for never-ice, faster for icy). Physics lane measuring.
- 2026-10-24: Owner 2026-10-24 (phone, provisional): 'probably' - happy to have ice ages set via this external variable; hasn't reviewed fully. Treat 0.45 as the working default.
- 2026-10-24: Lane v1-finish-8 (docs/review/base-climate/v1-finish-8/README.md).
  - 2 Gyr: no hothouse. L6 Earth-like 6/7 on 300-2000 (never-ice 0, hellhole 0, late dT med +4..+8). L7 2 draws are
    warmer late: 1500-2000 ice-free in both, dT +9.1 / +7.4; seed 12 never-ice overall.
  - Water world: always-icebox with or without the star (the outgassing falls 3x; draft-water-world-recipe-icebox.md).
  - Cold recipe kept. Hothouse preset climate_offset 5 -> 3 (at 5 with the star, dT med +12.9 / +10.9 crossed the
    hellhole line).
  - Strict reading (never-ice fails): L6 13/18, L7 7/8. A lower rate cools the warm draws by 2-4 C, but the share per
    seed is chaotic (583167: 0 / 60 / 12 / 11% at 0.45 / 0.2 / 0.1 / 0). star_age can't help (it warms).
    Per-world lever: draft-star-brightening-per-world-lever.md.
  - PW-564's text corrected.
- 2026-10-24: Created from inbox draft draft-star-brightening-default-signoff.md (found by v1-finish-7).
