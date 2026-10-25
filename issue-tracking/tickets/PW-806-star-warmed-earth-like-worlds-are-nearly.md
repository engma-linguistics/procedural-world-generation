---
id: PW-806
title: Star-warmed Earth-like worlds are nearly treeless (wet tropics at 1-8% trees); the plants' responses to pCO2 below 350 ppm and to warming are too steep
type: task
status: in-progress
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: v1-signoff
blocked_by: []
relates: [PW-644, PW-646, PW-761, PW-780, PW-290, PW-454]
refs: [planet/vegetation.py, "world 6fbc2c", "world a12762", "world 067778", "world 6909cb", "world bdded2", "world 577526", docs/review/base-climate/v1-signoff/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
The L7 Earth-like showcase worlds made on the star default (0.45) have tree cover of 1.7-20% against 20-31% for the
pre-star and Earth worlds. Their wet tropics are the giveaway. Land within 10 degrees of the equator gets a median
2500-3000 mm of rain and has 1-8% trees, against 27-38% on 1df1c3, 3e9e7d, bdded2 and Earth 577526
(`wetbelt.py` in docs/review/base-climate/v1-signoff/).

| world | slice dT | pCO2 at the slice | tree cover | equatorial trees (rain) |
|---|---|---|---|---|
| 6fbc2c | +3.8 | 155 ppm | 2.4% | 1.8% (2548 mm) |
| a12762 | +4.6 | 142 | 1.7 | 1.2 (3010) |
| 067778 | +0.8 (a glacial) | 221 | 9.6 | 3.1 (2471) |
| 6909cb | +6.4 | 349 | 20.0 (boreal) | 8.4 (3015) |
| show-s21 e71172 | +5.5 | 160 | 2.3 | 2.8 (2660) |
| show-s11 2a7385 | +6.5 | 277 | 15.8 | 8.1 (2918) |
| bdded2 (no star) | -2.0 | 350 | 20.7 | 38.0 (2508) |
| Earth 577526 | -0.1 | 350 | 31.4 | 34.1 (2556) |

**It is not a code bug.** It comes from two deliberate changes acting together:
- PW-644/646 (10-23): the plants read the run's real pCO2.
- PW-761 (10-24): the star brightens. At the slice moments it adds +4 to +5.4 C, and the weathering thermostat answers by
  drawing CO2 down. Over 300-1000 Myr the runs' pCO2 is below 180 ppm 3-31% of the time. Over 1000-2000 Myr it is
  below 180 ppm 23-82% of the time (median 87-244 ppm; 13 L6 and 2 L7 2 Gyr draws, `pco2dist.py`).

The plants then get hit from both sides, and their response to each is steep. Rerun offline on Earth's own model
climate (`vegetation.model`, rain held fixed; `vegco2_full.py` and `vegshift.py`; the absolute numbers run about 3x
below the stored ones, so read the ratios):
- **pCO2:** 350 ppm gives 10.0% trees, 221 ppm gives 3.1%, 155 ppm gives 0.4%. Holocene Earth at 280 ppm, which was
  well forested, would lose about half its trees.
- **Warming, with rain held:** -3 / 0 / +3 / +6 C give 27.7 / 12.0 / 5.3 / 2.4% equatorial trees.
- At the same 350 ppm, 6909cb's hot climate (+6.4) gives 1.7% equatorial trees. So its treeless tropics come from the
  warmth, not from the CO2.
- show-s21 (e71172) offline: 0.6% trees at its own 160 ppm, 5.2% at 350 ppm, and 16.6% (29.5% equatorial) at 350 ppm
  and 5 C cooler. Its geography and rain are fine; the CO2 and the warmth explain the gap.

Against the literature:
- The LGM (185 ppm, colder) kept large forests; C4 grasses spread, but the forests did not vanish (Prentice et al. 2011).
- Paleocene-Eocene tropics, +5-10 C, were forested (Jaramillo et al. 2010).

A response this steep reads as off to an amateur ("where is the Amazon?").

Likely amplifiers, to check first:
- The water-use efficiency scales fully with Ca (`potential`: kp[:, 16] *= 2^x).
- The C4 grasses win, and the grass-fire feedback then shuts out trees (savanna-forest bistability).
- PET grows with temperature while the rain is held.

Options:
- A. Recalibrate the plants' CO2 and heat responses against Holocene (280 ppm), LGM (185 ppm) and Eocene
  (warm, wet) tropical forest: a vegetation change.
- B. Keep the physics. Ship v1 with the star default; treeless star-warmed worlds are the K-star planets' character.
  Note it in the presets.
- C. Lower the star default, so slices are less warm and less CO2-starved. That moves the v1 pass rates PW-780 signed off.

Lean A, because the steepness is the fault. B is a fallback for v1 timing only.
- [ ] Earth's climate at 280 ppm keeps at least ~80% of its 350 ppm tree cover (owner to confirm the number)
- [ ] the L7 showcases' wet tropics (> 2000 mm, < 27 C) carry forest again

## Updates
- 2026-10-24: Status todo -> in-progress. Owner: tree cover 15-40% agreed with a geography caveat. Coordinator: global range is a diagnostic; hard check is wet equatorial lowland (>2000 mm) >= ~20% trees where it exists. Plants change only where steeper than the literature (owner: prefer the more correct simulation).
- 2026-10-24: Status needs-decision -> todo. Coordinator ruling: option A (recalibrate the plants' pCO2 and warming responses against Holocene 280 ppm, LGM ~180 ppm and Eocene warm forests). Holocene Earth losing half its forest at 280 ppm is a mechanism fault, whatever the bar. The 15-40% tree-cover range is a threshold: owner question in the feedback doc. Physics lane's v1 task.
- 2026-10-24: Created from inbox draft draft-treeless-tropics-co2-heat.md (found by v1-signoff).
