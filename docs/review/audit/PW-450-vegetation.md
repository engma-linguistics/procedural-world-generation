# PW-450: vegetation in the time zoom, and what it contributes to a glacial (2026-10-20, agent pw450)

**Short answer.** The time zoom now grows the run's vegetation on each full climate (`planet/timezoom/plants.py`).
It feeds back through the same couplings as in the run, plus a global albedo term counted from the start.
The coupling works: an LGM-like cooling turns about 60% of the boreal forest into snow-covered tundra.
But the term is small. At the Earth zoom's deepest glacial (-45 m, -1.9 C) it is about 0 (-0.02 C), and even
at a prescribed -6 C it is -0.32 W/m2, against the LGM's -1.1 W/m2 (Köhler et al. 2010). Half of that gap is
the tropics, which turn *greener* as the model cools, the opposite of Earth's glacial drying (inbox draft
`draft-glacial-tropics-green-not-dry.md`). The other half comes from the zoom's shallow glacial (PW-435) and
from forest that ice replaces (counted in the ice albedo). Net effect on the Earth zoom: -42.8 -> -45.1 m,
backstops 1 -> 0, interglacials unchanged. Runtime +11%.

Scripts are in the session scratchpad `pw450/`: `zsum.py` (zoom summary), `probe.py` (prescribed cooling) and
`unforced.py` (the consistency test's moment).

## The model
- At each full climate (every 10 kyr), `vegetation.model` runs in its cheap variant, warm-started from the
  last one: 250 yr of competition, so a biome shift completes within one interval. The CO2 index is the
  source's index plus the zoom's CO2 term divided by the run's `co2_sensitivity`. Under grounded ice the
  climate gets the reference surface (`plants.neutral`, which is what `veg=None` assumes).
- Local feedback, as in the run (`climate.compute(veg=...)`). The climate feels the plants grown on the
  previous full climate. Then the plants grown on it correct its albedo warming straight away
  (`climate.albedo_warming`), so a forest-to-tundra shift doesn't arrive a refresh late. Budyko w still
  waits for the next refresh.
- Global term (`veg=on`): the planet's albedo change from the plants' change since the start, at the
  current snow cover and on the start's land only. The snow's own change is a fast feedback, already in
  the climate's sensitivity. Ice that replaces plants counts as ice albedo, and a shelf the falling sea
  lays bare replaces sea, not bare ground. The formula is -`veg_toa` 0.4 x Δα x the top-of-atmosphere
  sun, x `veg_lambda` 0.8 C per W/m2, lagged `veg_lag` 2 kyr. The 0.4 matches the kernel PW-449 calibrated
  on Köhler's ice forcing: 0.25 W/m2 per W/m2 of sun for a land-to-ice Δα of ~0.55.
- The start: the full model on the start climate, then the climate again with those plants, then the
  cheap model. Ten kyr later an unforced Earth zoom's term is +0.006 W/m2.
- Shared helpers (the run is bit-identical, goldens unchanged): `climate.snow_cover` and
  `climate.surface_albedo` (split out of `albedo_warming`), and `timeline.keyframe_vegetation` (a
  keyframe's warm start, CO2 index and plant groups, now also a run source's `veg`).

## 1. The vegetation term, decomposed

Global terms in C and W/m2 at the top of the atmosphere, change from the start. "Local" is the albedo
warming's change on open land (its C, not in dTg). Belts are each one's contribution to the planet mean.

| | Earth zoom at its deepest (314 kyr, -45 m, dTg -1.93) | Earth zoom, PW-448 'both' knobs (270 kyr, -86 m, dTg -5.9) | Earth today's surface, prescribed -6 C | Earth LGM (literature) |
|---|---|---|---|---|
| global term in dTg | **-0.02 C** (target -0.02..-0.06) | -0.09 C (target -0.10..-0.16) | -0.26 C | -0.9 C |
| forcing, all | **-0.02..-0.07 W/m2** | -0.12..-0.20 | -0.32 | **-1.1** (Köhler et al. 2010) |
| 60-90 N | -0.04..-0.07 | -0.10..-0.14 | -0.24 | most of it: boreal forest to tundra |
| 45-60 N | -0.03..-0.05 | -0.19..-0.22 | -0.34 | |
| 30-45 N | +0.02 | +0.02..+0.03 | +0.05 | brighter: steppe, desert |
| 30 S-30 N | +0.02..+0.03 | +0.10..+0.18 | +0.20 | brighter: forest to savanna and grass, low CO2 |
| south of 30 S | 0 | 0 | 0 | |
| local, open land 45-90 N | -0.05..-0.07 C | -0.20..-0.26 C | -0.29 C | (inside the -0.9) |
| tree cover, open land 45-90 N (start 21.0 Mkm2) | 16.8 | 7.7-9.8 | 8.9 | boreal forest mostly gone or under ice |

(The two zoom columns are the full climates on either side of the minimum, 10 kyr apart.)
- The boreal response is plausible per area: ~0.05 W/m2 of planet-mean forcing per Mkm2 of forest lost,
  which is ~24 W/m2 at the cell, snow masking most of it. It is sizeable at an LGM-like cooling: 45-90 N
  gives -0.58 W/m2 at -6 C, about half of Köhler's total.
- The tropics have the wrong sign. At -6 C they gain 3.9 Mkm2 of trees, mostly where trees are sparse
  today (savanna and dry woodland; 1.45 Mkm2 in the Americas). The model's potential evaporation falls
  faster than its rain as it cools, and the plants' CO2 response is mild. Earth's glacial tropics dried,
  and low CO2 alone pushed trees back toward grass. This is the run's climate and vegetation, out of scope
  here (draft `draft-glacial-tropics-green-not-dry.md`).
- In the zoom itself the glacial is shallow (-1.9 C, PW-435). The high-latitude cooling is weak there
  (PW-448: the Canadian interior's summers are warmer than today's at glacial orbits). Part of the boreal
  belt goes under ice, which the ice albedo counts. So at its deepest the term is almost cancelled. In the
  deep diagnostic variant, vegetation adds 11.5 m to the glacial (-74.8 -> -86.3 m).

## 2. Earth zoom (L6, 600 kyr, default knobs; clean timing, one zoom at a time)

| | min sea level | dTg at min (CO2 / albedo / veg) | iced % of planet | interglacial ice % of land | Laurentide Mkm2 / southmost | Fennoscandia | endings (kyr), backstops | drift, first vs last 100 kyr | runtime (s): total / climate / plants |
|---|---|---|---|---|---|---|---|---|---|
| `veg=off` (= main, 755514) | -42.8 m @ 314 | -1.83 (-0.61 / -1.22 / 0) | 5.96 | 8.7-10.5 | 1.58 / 54.9 N | 1.53 / 54.4 N | 17 (backstop), 43; **1** | -6.7 -> -12.4 | 61.6 / 30.3 / 0 |
| `veg=local` | -43.8 | -1.88 | 6.0 | 8.7-10.5 | 1.58 / 54.9 | 1.48 / 54.4 | 18.5, 43.5; 1 | -7.7 -> -14.8 | |
| **`veg=on`** (saved: **098d5d**) | **-45.1 m @ 314** | -1.93 (-0.66 / -1.25 / -0.02) | 6.09 | **8.7-9.8** | 1.63 / 54.9 N | 1.53 / 54.4 N | 17.5, 43.0; **0** | -7.5 -> -15.1 | 68.5 / 31.4 / 3.8 |

The interglacial ice volume is 28.6 Mkm3 (main 28.1). The second ending stalls at 8.5 m in both.
The Laurentide still doesn't come south of ~55 N. That is PW-033/PW-435, not vegetation.

## 3. Cold run moment (seed 11 @ 400 Myr, source 82fc14, 600 kyr)

| | swing | mean | first vs last 100 kyr | min (dTg; veg term) | endings (kyr), stalled with (m) |
|---|---|---|---|---|---|
| main | 146.6 m | -89.1 | -61.4 -> -78.5 | -146.6 @ 330 (-2.49; 0) | 46.5, 72, 53, 31, 70.5, 74; 20-112 m left |
| `veg=on` | 145.8 | -90.4 | -60.8 -> -76.9 | -145.8 @ 330.5 (-2.37; **+0.11**) | 46, 72.5, 52.5, 32.5, 43, 23.5, 76 (7, 0 backstops); 18-109 m left |

The cold planet has little boreal forest left (2.6 Mkm2 of trees north of 45 N), so its vegetation term at
the glacial maximum is the tropics' darkening: +0.15 W/m2, a warming. The term damps the cycle a little.
Drift and endings are about the same; one long ending splits into two.

## 4. Unforced start (tests/test_timezoom_consistency.py: L5 seed 1 @ 300 Myr, 4 C colder)

The test's sheets are now made on the climate with the run's plants (`vegetation.coupled_climate`, as the
run does) rather than without them. Sea level at 20 kyr: main (old fixture) -13.6 m; `veg=on` on the new
fixture -11.1 m, and -18.1 m at 50 kyr. Its vegetation term stays within ±0.002 W/m2 for 50 kyr, so the
plants start in balance and don't drift.

## Sources
- Köhler et al. 2010, QSR 29: LGM vegetation forcing -1.1 W/m2.
- Qu & Hall 2006, J. Climate 19: planetary vs surface albedo, ~0.3-0.5 outside the tropics.
- Hansen et al. 2008: 0.75 C per W/m2.
- Bonan 1992 and Betts & Ball 1997: snow masking by boreal forest. Betts 2000: its local forcing.
- Prentice et al. 2011, New Phytol. 189; Bragg et al. 2013, Biogeosciences 10; Harrison & Prentice 2003, GCB 9:
  LGM vegetation, and the share of the change that low CO2 explains.
