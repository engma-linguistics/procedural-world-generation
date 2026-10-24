---
id: PW-761
title: "PW-750 measured: drift 2 C (B) and a long-run CO2 reference (D) leave the icehouse median at 46% (pass 39-50% vs ~70%); the gap is the late weatherability trend, and the brightening star (C) overshoots to ice-free worlds"
type: task
status: done
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: v1-finish-6
blocked_by: []
relates: [PW-750, PW-368, PW-240, PW-564, PW-708, PW-558, PW-559]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, docs/review/base-climate/v1-finish-6/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
v1-finish-6 (docs/review/base-climate/v1-finish-6/README.md) measured PW-750's options at L6 on v1-finish-5's 18
seed-draws (8 seeds, offsets 0 / +-0.001), judged on 300-1000 Myr against the owner's bar (icehouse <= 40%, no
always-icebox, no hellhole):

| option | pass | icehouse median | early / late | icebox | never-ice | dT median |
|---|---|---|---|---|---|---|
| base (PW-741) | 5/18 | 46% | 24 / 57 | 2 | 0 | +1.1 |
| B drift 3 -> 2 C | 9/18 | 46% | 31 / 65 | 2 | 0 | +1.5 |
| D source ref = running mean since 100 Myr | 8/18 | 46% | 15 / 57 | 1 | 0 | +1.6 |
| D + B | 7/18 | 47% | 24 / 59 | 2 | 0 | +1.6 |
| probe climate_offset +1.5 C | 10/18 | 36% | 2 / 54 | 0 | 0 | +2.3 |
| C star +0.9%/100 Myr (measurement) | 17/18 | 1% | 0 / 0 | 0 | 16 | +7.4 |

Findings:
- B does not move the mean (an OU drift has mean 0) and gives *more* deep ice (17% of updates below -150 m against
  12%); its 5 -> 9 passes are within the draws' noise (18 draws: sd ~11 points; 2 of its 9 passes are base passes).
  PW-368's expectation of fewer deep icehouses does not hold with the CO2 stock.
- D's premise fails: the 200-300 Myr reference is only ~4% above the source's long-run level, and any causal long-run
  mean is lower (more outgassing in the first 100-200 Myr), so it warms nothing. Only relearning references warm,
  which PW-576 dropped.
- The shape is the problem: early 15-31%, late 54-65% in every config. A uniform +1.5 C empties the early window and
  leaves the late one at 54% (pass 56%). The late cooling is PW-708's weatherability rise (relief, flora) against the
  frozen reference.
- C at the physical rate overshoots: the model's thermostat passes ~half of a sustained forcing, so +1.3 C per
  100 Myr gives dT +7.4 late and ice-free worlds (N1-N4 2/18).

Options (geophysics delegated to the coordinator; owner signs v1 off):
- A. Accept for v1: icehouse median ~46%, ~30-50% of draws at <= 40%, no always-icebox beyond 1-2 per 18, no
  hellholes, no never-ice; ice ages concentrated late, which the showcase picker already handles (warm moment of an
  era). Earth: icehouse roughly a quarter to a third of the Phanerozoic, so ~1.5x Earth, plausible.
- B'. Don't apply climate_drift 2 C (it doesn't help and deepens the ice); close PW-368 as measured.
- C'. PW-564 as a v2 design: the brightening star plus whatever makes the thermostat absorb a Gyr-scale forcing
  (on Earth CO2 fell ~4 doublings over the Phanerozoic against ~5% brightening); measure the absorbed share first.
- E. A warmer balance (PW-708 C, PCO2_BALANCE ~600 ppm, ~the +1.5 C probe): 56% pass, early window near ice-free,
  still short; a calibration knob.
Lean: A for v1 with B' (no change to merge, no showcase remake needed for this), C' as the v2 route to a flatter
history. Remeasuring any option needs >= ~40 draws to tell 30% from 50%.
- [ ] coordinator decision recorded on PW-750

## Updates
- 2026-10-24: Status in-progress -> done. Merged 35bfaff: star_brightening 0.45 x Gough default; L6 16/18, L7 7/8; showcase remade (PW-202). Sign-off and 2 Gyr check on PW-780.
- 2026-10-24: Lane v1-finish-7 (C'): the thermostat is within the literature's range (WEATHER_K 0.09/C = Ea ~63 kJ/mol; WEATHER_CO2 0.4; 3 C per doubling = 5.35 ln ratio at 0.81 C per W/m2; realised global e-folding ~21-38 K, between Walker/GEOCARB 10-20 K and Krissansen-Totton & Catling 2017's ~22-45 K), so not tuned. A Sun-like Gough star on it overshoots (L6 18/18 pass but 16 never-ice, dT +7.8). With the owner's lever, a slower K-type star (star_brightening 0.45, now the default, earth.star_forcing): L6 16/18 pass (89%), icehouse median 20% (early/late 14/16), 3 never-ice; L7 showcase seeds x 2 draws 7/8, median 25% (base 3/8, 45%). docs/review/base-climate/v1-finish-7/; draft-star-brightening-default-signoff.md.
- 2026-10-24: Status needs-decision -> in-progress. Coordinator: one bounded lane on C' (brightening star + a thermostat that absorbs Gyr-long forcing) at L6; fallback A (accept ~46%) needs the owner since it's under the bar.
- 2026-10-24: Created from inbox draft draft-icehouse-bar-late-trend-after-pw750.md (found by v1-finish-6).
