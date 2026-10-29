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

## Round 2 design note (lane 26b, 2026-10-29): winter frontal rain as a storm-lifted humidity gate
The large-scale rain runs at ls x min(q/qs / rh_c, 1)^3 with rh_c 0.8. A storm lifts its warm sector's air over the
front, so that air rains as air higher up would. The gate becomes rh_c x exp(-q_k x LAPSE x lift_m x lift) per cell
and season, with lift = storminess (B) times a mask. rh_c is now an [S, n] array in `climate._rain` and in
`tools/moisture_budget._probe` (`test_moisture_budget` checks they match bit for bit). One Earth L6 solve each, on
round 1 (317a7608). Columns: SE USA, Pampas annual; SE USA, NE USA Oct-Mar (GPCC 1334, 932); Arabia; B; BWh; corr;
exact.

| form (mask on B) | lift_m | SE USA | Pampas | SE USA win | NE USA win | Arabia | B | BWh | corr | exact |
|---|---|---|---|---|---|---|---|---|---|---|
| round 1 (none) | 0 | 525 | 291 | 153 | 174 | 198 | 26.4 | 14.7 | 0.704 | 37.1 |
| 1: B everywhere | 1000 / 2000 | 573 / 628 | 305 / 359 | 261 / 334 | 276 / 331 | 234 / 264 | 25.6 / 24.5 | 13.7 / 12.7 | 0.705 / 0.703 | 37.8 / 37.8 |
| 2: over the cold dome (ground below its air mass, /5 C) | 1500 | 527 | 303 | 171 | 223 | 200 | 26.3 | 14.7 | 0.703 | 37.6 |
| 3: in warm advection (-v.grad T, /1 C/day) | 1500 | 550 | 297 | 189 | 210 | 217 | 25.8 | 14.2 | 0.704 | 37.3 |
| 4: land only | 1500 | 624 | 348 | 237 | 261 | 259 | 24.9 | 13.0 | 0.705 | 37.4 |
| **5: not under the subtropics' sinking air, B x (1 - sink) (as clouds' cloud_storm)** | 1000 / **1500** / 2000 | 574 / **601** / 627 | 318 / **330** / 338 | 243 / **288** / 325 | 278 / **313** / 334 | 209 / **214** / 220 | 25.8 / **25.6** / 25.3 | 14.1 / **13.7** / 13.4 | 0.706 / **0.707** / 0.707 | 37.7 / **37.9** / 38.1 |

- **Dropped:** 2 and 3 barely move SE USA's and NE USA's winters (+18-49 mm on 153-174). 1 and 4 wet the deserts
  (Arabia +36-61) for the same gain as 5.
- **Kept: 5 at lift_m 1500 m** (the middle of the design's 1-2 km, unverified; not fitted). SE USA winter 153 -> 288,
  NE USA 174 -> 313, SE USA annual 40% -> 45% of GPCC, Pampas 31% -> 35%, Japan 36% -> 40%, Mediterranean 67% -> 72%,
  corr +0.003, exact +0.8. Winter temperatures move by <= 0.1 C.
- **B falls 26.4 -> 25.6, but mostly by losing wrong B.** `bflip.py lift_form=5 lift_m=1500`, run against lift_m=0 while the probe knobs were in (on the committed code,
`bflip.py lift_m=0` gives the reverse): the land that
  leaves B is 0.32% of land that Kottek calls B and 0.72% that it doesn't; 0.09% / 0.14% joins. So the per-cell match
  gets better while the share moves away from Kottek's 30.1. North America accounts for 0.30% (0.12 / 0.18) of it.
- **Still vapour-limited.** Even at 2000 m SE USA's winter is 25% of GPCC: its vapour is 7.7 mm against NCEP's 17.5.
  The lift fixes the gate, not the supply. SE USA and Pampas can't reach 60% from this round. The rest is the return
  flow's vapour (round 1 went part way) and the Pampas jet.

## Diagnosis gate: the poleward (eddy) vapour transport (lane 26b, 2026-10-29; probes only, `eddy_probes.patch`)
One Earth L6 solve each, on round 2 (4d18c72c). `quick.py --books` prints the northward vapour transport through the
kernel's faces (Sv; `moisture_budget`'s table) against what NCEP E - GPCP P implies.

**The books on round 2** (advection + eddy mixing = total; NCEP implied):

| lat | -40 | -30 | -20 | 20 | 30 | 40 |
|---|---|---|---|---|---|---|
| model | -0.69 | -0.03 | +1.12 | -0.90 | +0.19 | +0.74 |
| of which eddy mixing | -0.01 | -0.02 | -0.03 | +0.03 | +0.01 | +0.01 |
| NCEP implied | -1.39 | -1.24 | -0.50 | +0.08 | +0.72 | +0.83 |

- The deficit isn't a weak source. The model's 20-30N belt gives off +1.09 Sv (NCEP +0.64), but the trades take it all
  equatorward. The model's moisture divide (transport 0) is at ~28N / ~30S. In NCEP it's at ~18N / ~12S. So the
  subtropics export their vapour the wrong way: the poleward export that should feed the subtropical east coasts and
  the mid-latitudes is missing.
- Unverified, from memory: across 30-40 deg the observed transport is mostly transient eddies (v'q'). The warm
  sector's moist air goes poleward and the cold air's dry air comes back, so the flux follows the storms' correlation,
  not the mean vapour gradient at the ground.

| candidate | SE USA | Pampas | SE USA win | Pampas Oct-Mar | Japan | Arabia | Amazon | B | BWh | corr | exact | 30N / 30S Sv | 40N Sv | Japan Tc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| round 2 | 601 | 330 | 288 | 490 | 666 | 214 | 3552 | 25.6 | 13.7 | 0.707 | 37.9 | +0.19 / -0.03 | +0.74 | 9.6 |
| E1: all mixing x5 | 731 | 403 | 446 | 554 | 732 | 250 | 3457 | 23.5 | 12.1 | 0.707 | 37.7 | +0.26 / -0.09 | +0.80 | 9.5 |
| E2: + 4 K_MIX x B (storms only) | 713 | 389 | 433 | 541 | 721 | 243 | 3479 | 24.0 | 12.5 | 0.711 | 37.8 | +0.24 / -0.08 | +0.79 | 9.5 |
| E3: + 4 K_MIX x B, meridional faces only | 682 | 373 | 386 | 551 | 699 | 233 | 3491 | 24.5 | 12.9 | 0.712 | 38.0 | +0.23 / -0.07 | +0.78 | 9.5 |
| E4: v'q' as a poleward drift, 0.5 m/s x B | 610 | 366 | 317 | 567 | 681 | 228 | 3401 | 25.5 | 13.3 | 0.713 | 38.1 | +0.30 / -0.17 | +0.85 | 9.4 |
| E4, 1 m/s x B | 627 | 403 | 355 | 645 | 695 | 242 | 3271 | 25.3 | 12.8 | 0.716 | 38.1 | +0.42 / -0.32 | +0.97 | 9.1 |
| E4, 2 m/s x B | 671 | 473 | 443 | 787 | 721 | 270 | 2989 | 24.8 | 12.1 | 0.718 | 38.3 | +0.65 / -0.61 | +1.21 | 8.7 |
| E4 (i): 1 m/s x the jet's storm tracks only (`track`) | 638 | 402 | 362 | 641 | 703 | 247 | 3237 | 25.1 | 12.7 | 0.718 | 38.1 | +0.41 / -0.31 | +0.96 | 9.2 |
| E4 x (1 - sink), 1 / 2 m/s | 619 / 649 | 239 / 202 | 288 / 299 | 330 / 272 | 639 / 618 | 213 / 216 | 3327 / 3100 | 25.6 / 25.7 | 13.8 / 13.6 | 0.710 / 0.701 | 37.8 / 37.7 | +0.29 / -0.13, +0.38 / -0.23 | +0.91 / +1.07 | 9.1 / 8.7 |

- **E1-E3, more down-gradient mixing: ruled out as the lever.** At 5x the mixing still carries only 0.07-0.15 Sv. The
  vapour gradient at the ground across 30 deg is too weak for diffusion to carry the observed flux. What extra rain it
  makes comes from wetting the land-sea contrast inland: Gobi 583 -> 764-863 (GPCC 157), and B falls 1-2 points.
- **E4, the storms' v'q' as a poleward drift of the vapour (u_e x B, poleward, on the faces): the only form that moves
  the books.** 30N goes +0.19 -> +0.42 / +0.65 (NCEP +0.72) and 30S -0.03 -> -0.32 / -0.61 (NCEP -1.24). It's the first
  mechanism that moves the Pampas without the Andes (Oct-Mar 490 -> 645 / 787, GPCC 1321). It dries the Amazon toward
  GPCC (3552 -> 3271 / 2989; GPCC 2335), cools Japan's winter (9.6 -> 9.1 / 8.7; NCEP 2.0) and gives the best corr
  so far (0.716 / 0.718). The physical scale: u_e ~ r x sigma_v x sigma_q / q ~ 0.5 x 6 m/s x 0.3 ~ 1 m/s (all three
  unverified, back of the envelope), so 1 m/s is the anchored value, not a fit (unverified; a source is on docs/references/wishlist.md).
  - **What it breaks:** 40N overshoots (+0.97 / +1.21 vs +0.83). The drift runs on B, whose latitude belt part is
    still ~0.3-0.5 at 50-60 deg. The deserts' poleward edges get wetter (Arabia +28 / +56, Central Asia +13 / +36),
    so B falls 0.3 / 0.8 and BWh 0.9 / 1.6. NE USA's summer, already 2.4x too wet, is unchanged. Tests: none run
    (probe only).
  - Masked by (1 - sink), like round 2: the Pampas collapses (Oct-Mar 330 / 272). The drift *across* the subtropical
    high is what feeds it, so that mask is wrong for transport (it was right for lifting). Dropped.
- **(i), the storm tracks only (coordinator's pick, 1 m/s):** about the same as on B. 30N +0.41, 30S -0.31, corr
  0.718 (+0.002), B 25.1 (-0.2), Pampas 43%, SE USA 48%. It doesn't cure the overshoot: 40N +0.96, 50N +0.65 (NCEP
  +0.83 / +0.52), the same as on B. The tracks themselves peak there. (ii), acting on q minus the zonal-mean q, was
  dropped: transient eddies' q' is the anomaly from the *time* mean, not from the zonal mean, so its only merit
  would be sparing the deserts (coordinator).
- **Round 3 as committed:** (i) at 1 m/s, faded within 15 deg of the equator. The storm tracks run on into the
  tropics (track ~0.3 at the equator), and there the drift has no poleward direction and no eddies to make it. That
  showed as a 2.4 C step in July across the equator in `test_july_stays_july_across_the_equator` (limit 2.0; 1.2
  without the drift). Earth L6: SE USA 636 (48%), Pampas 401 (43%), Japan 42%, Amazon 3383, corr 0.722, exact 38.4,
  B 25.2, BWh 12.7. Books: 30N +0.41, 30S -0.31, 40N +0.96.
- **Open questions for E4's design (before the solves above):** (i) Should it ride the storm tracks only (the `track` part of B), to stop 40-60
  deg overshooting? (ii) Should it act on the vapour's anomaly from the zonal mean (v'q' needs q' ~ q - [q]) rather
  than on q, which would also stop it draining the deserts? (iii) It doesn't conserve dry air. That's fine for a
  vapour tracer, because the return flow is the dry air. A 2 m/s drift through the faces may need RAIN_CFL's dt to
  shrink (not seen: same step count).

## Harness (here)
- `quick.py [--level L] [k=v ...]`: Earth summary (regions by half-year, B, BWh, corr, winter T).
- `winds.py [k=v ...]`: the rain's wind and vapour by box against NCEP 850/925 hPa.
- `quick.py --books`: adds the northward vapour transport table (Sv).
- `eddy_probes.patch`: the eddy-transport probe knobs (`k_all`, `k_storm`, `k_mer`, `k_drift`, `k_drift_sink`) on face_winds. Not for merging.
- `bflip.py [k=v ...]`: which land cells leave or join Koppen B under the overrides, against Kottek, by continent.
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
