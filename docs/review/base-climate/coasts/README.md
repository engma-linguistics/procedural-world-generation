# Lane 26: the dry subtropical coasts (PW-998 with PW-026), 2026-10-29

Status: **diagnosis only, nothing committed under `planet/`.** These are single Earth L6 solves on main db7a178a
(`quick.py`, `winds.py`, `tools/moisture_budget.py`). No candidate reaches the acceptance bar (SE USA and Pampas at
60% of GPCC, B >= ~26%) on its own. The evidence points at more than one mechanism, so I stopped at the gate.

## Which region and season lost the rain (model / GPCC, mm/yr as a half-year rate; PW = column vapour, mm, model / NCEP)
| region | Apr-Sep | Oct-Mar | PW Apr-Sep | PW Oct-Mar | which half failed |
|---|---|---|---|---|---|
| SE USA | 870 / 1323 | **93 / 1334** | 25.0 / 33.5 | **3.7 / 17.5** | winter: no vapour |
| Pampas | **112 / 565** (winter) | **475 / 1321** (summer) | 5.6 / 16.5 | 22.2 / 24.5 | both: no vapour in winter; in summer the vapour is there but rains at 0.4x the observed rate per mm of vapour |
| Japan | **554 / 2075** | **495 / 1268** | 22.2 / 31.7 | 15.3 / 12.3 | both: the rain per mm of vapour is ~0.35x observed (winter vapour is above NCEP) |
| E Australia | **155 / 556** (winter) | 820 / 929 | 9.0 / 15.0 | 28.4 / 25.0 | winter |
| SE China | 1986 / 2131 | **118 / 794** | 34.2 / 41.6 | **5.2 / 21.3** | winter |
| NE USA | 2680 / 1132 | **104 / 932** | 21.5 / 24.0 | **4.0 / 11.1** | winter (the annual figure hides it: the summer is 2.4x too wet) |
| India | **943 / 1916** | 233 / 302 | 26.8 / 39.4 | 11.4 / 20.7 | summer (the monsoon westerly is missing, below) |

- Earth L6 on main: B 27.3 (Kottek 30.1), BWh 14.5 (14.8), exact 36.1, group 70.9, log-rain corr 0.691, land rain 1038 (791).
- PW-026's winter temperatures, coldest month, model / NCEP: W Europe -0.6 / 0.7, Scandinavia (58-70N, 5-30E) -8.5 / -8.2.
  The ticket's figures (-4.2, -22.3) are out of date: the overturning and front_shift have fixed them. What is still
  off: Alaska -29.1 / -19.0, NE China -9.2 / -17.9, Japan 8.6 / 2.0, Quebec -16.2 / -20.2.

## Where the vapour should come from: the rain's wind against NCEP 1991-2020 (`winds.py`; m/s east, north)
| box, half | model | NCEP 850 hPa | NCEP 925 hPa |
|---|---|---|---|
| SE USA, Oct-Mar | 3.8, **-1.6** | 5.6, +0.9 | 2.3, +1.2 |
| Gulf of Mexico, Oct-Mar | -0.4, **-1.6** | 0.7, +1.4 | -2.2, +1.1 |
| W Atlantic 30-37N, Oct-Mar | 6.0, **-1.6** | 6.5, +1.0 | 3.9, +0.7 |
| SE China, Oct-Mar | -1.0, **-3.8** | -0.1, +0.9 | -2.4, -0.8 |
| SE USA, Apr-Sep | 1.6, **+5.0** | 2.7, +1.1 | 1.5, +1.6 |
| Japan, Apr-Sep | 1.2, **+5.4** | 3.7, +1.3 | 1.8, +1.4 |
| S Brazil/Paraguay, Apr-Sep | -0.4, **+0.9** | 1.4, **-3.4** | -1.6, -2.2 |
| S Brazil/Paraguay, Oct-Mar | -5.9, **+1.1** | -0.1, -2.0 | -1.9, -1.5 |
| India, Apr-Sep | **-0.3**, -0.4 | 4.2, -0.9 | 3.5, +0.4 |

- In winter the Gulf, Atlantic and South China Sea coasts have a weak *onshore, poleward* mean flow in NCEP: the
  subtropical highs' western flanks, the return flow. The model blows 1.6-3.8 m/s *offshore*: the cold continent's
  thermal high, at full strength. So the coast's air is the continent's dry air.
- In summer the model's land-sea wind is 3-4x too strong on the same coasts (+5 vs +1.5).
- East of the Andes NCEP has the northerly low-level jet (-2 to -3.4 m/s, poleward) bringing Amazon vapour to the
  Pampas. The model has a weak southerly there in both halves, and Paraguay's winter PW is 6.1 against 24.9.
- The global books agree. The model's poleward vapour transport across 30 deg is +0.14 Sv (N) / -0.03 Sv (S),
  against +0.72 / -1.24 Sv implied by NCEP E - GPCP P. The kernel's eddy mixing carries only 0.01-0.04 Sv anywhere.
  (Unverified, from memory: most of the observed transport at 30-40 deg is by transient eddies.)
- (NCEP pressure-level winds: `downloads.psl.noaa.gov/.../pressure/{u,v}wnd.mon.ltm.1991-2020.nc`, read with
  `tools/h5_reader`. They are in my scratchpad only. `winds.py` reads them from there, so re-download them to re-run it.)

## Candidates (each a single Earth L6 solve; the knobs are in `probes.patch`, not committed)
Columns: SE USA / Pampas annual mm (GPCC 1328 / 943), SE USA winter, B %, BWh %, corr, exact %.

| candidate | SE USA | Pampas | SE USA Oct-Mar | B | BWh | corr | exact |
|---|---|---|---|---|---|---|---|
| main | 482 (36%) | 294 (31%) | 93 | 27.3 | 14.5 | 0.691 | 36.1 |
| A: eddy mixing K 5e5 / 1e6 / 2e6 m2/s (now 2e5) | 493 / 521 / 576 | 312 / 340 / 390 | 106 / 135 / 199 | 27.0 / 26.3 / 24.8 | 14.3 / 13.8 / 12.6 | 0.691 / 0.689 / 0.689 | 36.2 / 36.0 / 35.7 |
| B: land-sea wind in the Coriolis-drag balance (1/f poleward of 15 deg) | 144 | 132 | 136 | 31.9 | 19.3 | 0.643 | 39.0 |
| C: shallow winter cold domes (a cold land anomaly fills 0.29 of the column, air_m / fetch_h) | 525 (40%) | 291 | 152 | 26.4 | 14.7 | **0.703** | **37.1** |
| D: dynamic subtropical highs over the oceans, one-sided, amplitude 3 / 6 | 558 / 622 | 292 / 291 | 96 / 100 | 27.1 / 27.1 | 14.4 / 14.4 | 0.694 / 0.695 | 36.2 / 36.3 |
| D two-sided (lows over the continents), amplitude 3 / 10 | 755 / 1030 | 703 / 809 | 116 / 277 | 23.5 / 18.9 | 10.6 / 6.2 | 0.663 / 0.422 | 33.9 / 30.4 |
| E: the Andes' blocking felt 600 km out (now 250) | 477 | 308 | 94 | 27.5 | 14.4 | 0.686 | 35.7 |
| C + A (2e6) | 638 (48%) | 401 (42%) | 299 | 23.9 | 12.8 | 0.701 | 36.8 |
| C + A (2e6) + D (6, one-sided) | 775 (58%) | 399 (42%) | 329 | 23.7 | 12.7 | 0.706 | 37.2 |

- **A, eddy mixing.** For: the books' eddy transport is ~0, and the observed transport needs it. Against: 10x K only
  doubles SE USA's winter rain, and it wets the interiors (Gobi 556 -> 895, Central Asia 227 -> 289), so B falls. Cheap
  to test (a constant), but each 2x costs ~2x in rain-kernel steps (CFL).
- **B, 1/f.** The physics is right, but it takes away the summer southerlies that are SE USA's only source now.
  Dropped.
- **C, shallow cold domes.** For: the winter winds move toward NCEP (SE USA v -1.6 -> +0.4, SE China -3.8 -> -1.3,
  India's winter -5.3 -> -2.6 east). SE USA's winter vapour doubles (3.7 -> 7.7 mm; NCEP 17.5). Corr and exact rise,
  Arabia dries (274 -> 199), and the model's own `air_m` already says the winter air mass is ~1 km deep. Against: SE USA
  gains only +43 mm, Pampas nothing. The vapour arrives at q/qs 0.36, where the large-scale rain runs at
  (0.36/0.8)^3 ~ 0.09 of full, so it barely rains. It also moves the winds the temperatures ride (PW-026): NE China
  +0.7 C, Japan +0.7 C, Quebec +0.9 C (all the wrong way); W Europe and Scandinavia stay within 0.5 C.
- **D, ocean highs.** One-sided, they help SE USA's and Japan's summers (+150-350 mm) but not the winters. Two-sided,
  the continental lows wet every desert. The highs' amplitude has no physical anchor yet.
- **E** doesn't make the low-level jet.

## What the evidence says
1. **The winter error is the wind's sign on the subtropical east coasts.** The continent's cold high is too deep (C),
   and the subtropical highs' western-flank return flow is missing in winter (D can't make it without wetting the
   deserts).
2. **Even with the vapour delivered, the winter coasts don't rain it.** The large-scale rain wants q/qs near 0.8. Real
   winter coastal rain is frontal lifting of Gulf or Kuroshio air over the cold dome, so it rains at a low
   surface-relative humidity. The kernel has no such lifting term. Japan shows this most clearly: its winter vapour is
   *above* NCEP, yet it rains 0.31x the observed rate per mm of vapour, and none of it falls as showers.
3. **The Pampas is its own mechanism:** the Andes-steered low-level jet from the Amazon, in both halves. Neither A nor
   E makes it.

So no single candidate is the fix, and the combinations that come near SE USA's bar break B (23.7 < 26). **I picked
none.** C is the best-supported part (a sound change, the winds move toward NCEP, corr +0.012, exact +1.0), but it
moves SE USA by only +4 points of GPCC and Pampas by 0. By the gate's rule 5 it doesn't count as a fix on its own.

## Options for the coordinator / owner
- (a) C as a first round: shallow cold domes, which improve corr, exact and the winter winds. Then a second mechanism
  for the winter frontal rain (lifting over the cold dome along the storm track, which needs a design). Then the
  Pampas low-level jet (mountain-channelled flow, which also needs a design).
- (b) Treat PW-998's bar as two or three tickets (winter return flow and frontal rain; the Pampas jet; Japan's
  efficiency), with C first.
- (c) Stop here: the bulk exchange is merged, and the coasts wait for v2's moisture-transport proposal
  (docs/proposals/moisture_transport.md).

## Harness (here)
- `quick.py [--level L] [k=v ...]`: Earth summary (regions by half-year, B, BWh, corr, winter T).
- `winds.py [k=v ...]`: the rain's wind and vapour by box against NCEP 850/925 hPa.
- `probes.patch`: the probe knobs (`k_mix`, `lsw_f`, `sub_a`/`sub_one`/`sub_km`/`sub_lat`, `cold_col`) on
  planet/climate.py. Not for merging.
- `tools/moisture_budget.py`: Pampas, Japan, E Australia, Mediterranean, SE Brazil and Mexico N added to the probe
  regions.

## Handoff (2026-10-29, machine restart)
- **Option (b) chosen by the coordinator.** PW-998 is split into three drafts: winter frontal rain, the Pampas jet and
  Japan's rain efficiency.
- **Round 1 (the shallow cold domes) is committed: 261343c5, goldens 317a7608.** Earth L6: B 26.4, BWh 14.7, corr
  0.704, exact 37.1, SE USA 525, Pampas 291. `pytest -m 'not slow'`: 714 passed.
- **The paired judge was killed for the restart, with ~0-2 of 72 runs done.** Re-run it from scratch:
  1. Freeze A = db7a178a and B = 317a7608 with `git archive`.
  2. Run `paired.sh` for each arm with rolls 0.0005 and 0.001.
  3. Run `pjudge.py`.
- **Not yet run for round 1:** `test_envelopes` (slow), earth_check L7, the scorecard.
- **Round 2 (winter frontal rain) is designed but not coded.** The idea is a storm-lifted humidity gate: per cell and
  season, rh_c x exp(-q_k x LAPSE x lift_m x B), with B the storminess. A storm lifts air ~1-2 km (unverified), so
  sub-saturated warm-sector air rains. rh_c becomes an [S, n] array in `climate._rain` and in
  `tools/moisture_budget._probe`, which must match it bit for bit. Then one Earth solve per lift_m, and drop the form
  if SE USA's and NE USA's winters don't move.
- **Next steps:**
  - Message the coordinator before running the round-2 judge.
  - The Andes jet waits until rounds 1 and 2 are judged.
