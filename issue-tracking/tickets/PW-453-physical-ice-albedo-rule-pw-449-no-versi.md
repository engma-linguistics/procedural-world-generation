---
id: PW-453
title: "Physical ice-albedo rule (PW-449): no version both deepens Earth's time-zoom glacial and keeps the run's cold eras"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: pw449
blocked_by: []
relates: [PW-449, PW-448, PW-438, PW-435, PW-033, PW-450, PW-030, PW-436]
refs: [planet/tectonics/earth.py, planet/timezoom/forcing.py, planet/icemass.py, docs/review/audit/PW-449-snow-season.patch]
created: 2026-10-20
updated: 2026-10-20
---

## Description
PW-449 option A (re-anchor the shared ice-albedo rule on physics). I made 4 attempts. None meets both
done-when bars, so nothing is merged. The code on the branch is main's. The last attempt is in
`docs/review/audit/PW-449-snow-season.patch`.

**The rules tried** (shared by `earth.global_temperature` and `timezoom.Forcing`, in `icemass`):
- **A1, insolation-weighted, no levelling-off.** Cooling = lambda x 0.25 x sum over iced cells of the
  annual-mean top-of-atmosphere sun at the cell's latitude (W/m2, planet mean). lambda = 0.8 C per W/m2.
  Calibration: Earth's real LGM ice (+~25 Mkm2 at ~260 W/m2) gives 2.6 C, about Köhler et al. 2010's
  -3.2 W/m2. Today's ice gives 1.05 C (old rule: 1.4).
- **A2, A1 times the bare ground's snow-free share of that sun.** Each month counts in proportion to
  the bare ground's air temperature at the bed, ramped over +-2.5 C. In months when the ground would be
  under snow anyway, the ice whitens nothing new; that snow is inside the climate sensitivity. Planetary
  albedo contrast 0.4 (snow-free land to ice, Köhler-calibrated). Each model uses its own sensitivity:
  run 0.56 (co2_sensitivity 3 C / 5.35 W/m2 per e-fold), zoom 0.9 (co2_cool 2.5 C / LGM GHG -2.8 W/m2).
  The levelling-off comes from the climate: the colder the planet, the shorter the snow-free season.
- **A3, A2 with the sheets' own air removed** from the bare-ground climate (`bare_ground`: undo the
  SUMMER_DAMP x air_mass summer damping). EARTH_ICE_SUN goes 2.5 -> 3.6 W/m2.
- **A4, A3 plus the zoom counting only ice gained or lost since its start**, both at the current
  climate. Ice that stays counts nothing, whatever the climate. (In A2/A3 the start's Antarctica lost
  forcing as the zoom cooled, which warmed it.) The run is the same as A3.

**Earth time zoom** (L6, 600 kyr, in memory, `scratchpad/pw449/zsum.py`):

| rule | min sea level | dTg at min (CO2 / albedo) | iced % of planet at min | interglacial ice % of land | endings (kyr) | backstops |
|---|---|---|---|---|---|---|
| main (tanh) | -42.8 m @ 314 | -1.83 (-0.61 / -1.22) | 5.96 | 8.7-10.5 | 17, 43 | 1 |
| A1 | **-47.6 @ 107** | **-2.82** (-0.75 / -2.07) | 6.01 | 8.6-10.6 | 44.5, 46, 45 | **0** |
| A2 | -32.6 @ 314 | -1.98 (-0.40 / -1.58) | 5.57 | 8.4-9.9 | 13, 19 | 2 |
| A3 | -32.8 @ 314 | -2.05 (-0.40 / -1.65) | 5.60 | 8.4-9.8 | 13.5, 19 | 2 |
| A4 | -34.9 @ 314 | -2.13 (-0.45 / -1.68) | 5.74 | 8.5-9.2 | 14, 0.5 | 2 |
| PW-448 diagnostic `ice_albedo_max=30` | -70.8 | -4.10 (-1.35 / -2.75) | 6.7 | | 5 endings | 0 |

**Cold run moment** (seed 11 @ 400 Myr, source 82fc14 in the pw030 scratch store, 600 kyr):
swing / mean / first-100 vs last-100 kyr mean / endings, all stalled:

| rule | result |
|---|---|
| main | 147 m / -89 / -61 -> -79 / 6, stalled with 20-112 m left |
| A1 | 160 / -105 / -76 -> -92 / 6, more left (30-125 m) |
| A2 | 141 / -77 / -58 -> -69 / 8, 21-92 m left |
| A3 | 144 / -91 / -66 -> -75 / 6 |
| A4 | 148 / -95 / -68 -> -87 / 6, 23-112 m left |

**The run's cold eras** (L6, 1 Gyr, sea level from ice on 4-Myr samples; worst / % of time below -430 m /
% below -150 m). "Ok" means worst >= ~-450 m and <= 2% of time below -430 m. Main = PW-438's merged
state for the first 4 seeds, plus main runs of 6 more:

| seed | main | A1 | A2 | A3 (= A4's run) |
|---|---|---|---|---|
| 3199 | -386 / 0 / 31 ok | -403 / 0 / 49 ok | -371 / 0 / 14 ok | -446 / 1.2 / 13 ok |
| 11 | -569 / 5.2 / 37 FAIL | -576 / 10.0 / 14 FAIL | -540 / 11.6 / 27 FAIL | -822 / 12.7 / 20 FAIL |
| 2 | -404 / 0 / 22 ok | -550 / 6.0 / 48 FAIL | -338 / 0 / 32 ok | -514 / 8.4 / 28 FAIL |
| 21 | -393 / 0 / 11 ok | -357 / 0 / 12 ok | -364 / 0 / 16 ok | -292 / 0 / 18 ok |
| 1 | -260 / 0 / 13 ok | -481 / 3.2 / 46 FAIL | -206 / 0 / 8 ok | -600 / 4.8 / 42 FAIL |
| 5 | -215 / 0 / 16 ok | -446 / 2.8 / 12 FAIL | -299 / 0 / 6 ok | -280 / 0 / 11 ok |
| 7 | -362 / 0 / 14 ok | -497 / 11.6 / 30 FAIL | -333 / 0 / 24 ok | -545 / 2.0 / 6 FAIL |
| 13 | -372 / 0 / 44 ok | -555 / 6.0 / 51 FAIL | -447 / 2.0 / 32 ok | -378 / 0 / 50 ok |
| 42 | -364 / 0 / 27 ok | -264 / 0 / 32 ok | -311 / 0 / 33 ok | -216 / 0 / 10 ok |
| 99 | -450 / 3.2 / 60 FAIL | -353 / 0 / 61 ok | -422 / 0 / 45 ok | -468 / 4.0 / 33 FAIL |
| **seeds ok** | **8/10** | **4/10** | **9/10** | **5/10** |

**What this shows**
1. A rule calibrated on physics (A1 reproduces the LGM's real ice-albedo forcing) does not take the
   Earth zoom to ~-70 m. The PW-448 diagnostic got there with ~50 C per unit of iced planet share
   everywhere. Physics gives 0.2 x the annual sun: ~36-40 at 70-80 N, where the model's Earth ice
   grows (Siberia, Alaska, the Arctic islands, PW-033), and ~55 at 50 N, where the Laurentide never
   forms in the model (PW-448). The depth is a geography and mass-balance problem (PW-435, PW-033),
   plus the LGM's missing vegetation and dust (PW-450). The rule's anchoring is a smaller part than
   PW-449 assumed. The old tanh's marginal slope is ~40 per unit share at today's ice and ~21 at 6%, so
   A1 (36-55) is a bit stronger at the zoom's glacial and gets -48 m.
2. Without the snow season (A1), the run's cold eras run away (4/10): their ice sits at 30-45 deg
   under strong sun (s400's thickest ice is at 32 N), and nothing levels the forcing off.
3. With the snow season (A2-A4), the run levels off physically (A2 9/10, but A3 5/10 after a modest
   strengthening). The 10-seed share is noisy and chaotic per seed, so A2 vs A3 is within the run's
   chaos. But the Earth zoom gets shallower (-33..-35 m, 2 backstops): a margin cell that freshly
   glaciates in a -2 C world has a short snow-free season, so it adds less than the tanh's
   small-extent slope.
4. Either way the albedo per metre of sea level at the glacial maximum is about the same (0.039-0.048
   C/m in all variants). The depth differs by the build's path, which shows how close to gain 1 the
   Earth zoom is.

**Options**
- **(a) Keep main's tanh** and take the Earth depth to PW-435 / PW-033 / PW-450 (the geography and
  forcing gaps above). Nothing changes. Lean.
- **(b) A2 for both run and zoom**: physically better, levels off by the climate, run 9/10 (noisy),
  Earth zoom -43 -> -33 m with 2 backstops. Needs another 10-seed check (A3 got 5/10 with a small
  change).
- **(c) A1 for both**: Earth zoom -48 m, 0 backstops, run 8/10 -> 4/10. No.
- **(d) A1 in the zoom only, A2 in the run**: breaks PW-030's consistency. No.

- [ ] decide

Notes: in the A-variants, `tests/test_timezoom.py::test_start_anchor_leaves_with_the_ice` failed on a
marine cell: a held ice cell with bed -258 m has the sea's climate. Restricting `held` to land fixes it
(in the patch). earth_check doesn't depend on this rule (dT = 0). Main's baseline is Koppen group 71% /
exact 31%. The main scorecard (commit e02d7e2) has Earth group 70.6 / exact 30.9, seed 1 ice 1.1%,
seed 2 ice 10.6%.

## Updates
- 2026-10-20: Status needs-decision -> todo. Coordinator decision 2026-10-20: option (a). Keep main's rule; revisit (b), the snow-season rule A2 for both run and zoom (9/10 seeds), after PW-450, PW-435 and PW-033. The missing depth is where the ice grows plus the missing vegetation and dust, not the cap.
- 2026-10-20: Created from inbox draft draft-ice-albedo-physical-rule-run-vs-zoom.md (found by pw449).
