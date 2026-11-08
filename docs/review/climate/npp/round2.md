# Wet-forest NPP, round 2 (lane 181, 2026-11-04): scout 173's KN_RESP lever on D47 main

**In plain words.** Scout 173 found that the model's rainforest grows too little because every leaf, even deep in the
shade, is charged the upkeep of a sunlit leaf, so the forests stop adding leaves early (leaf area index about 3 where real
rainforest is about 5). The lever makes leaf upkeep fall with depth in the canopy, using one constant (KN_RESP = 0.4).
Lane 181 put the lever onto current main (after D47) and judged it.
- On Earth's real climate, rainforest growth rises from 628 to 831 g C/m2/yr (field plots: about 1160).
- The whole land's growth rises 8%, from 59.6 to 64.4 Pg C/yr (observed: about 56). It is not unchanged: the total stays
  flat only if lane 123's grass fix ships with the lever.
- Because D47 made rock weathering read how much ground plants cover, not how fast they grow, the climate barely
  notices.
- On all 36 test planets: no planet freezes, boils, loses its ocean or crashes its CO2. Soft passes are 31 against
  main's 30. Every planet's late climate stays inside -6..+5 C of today's Earth, and the spread between planets stays
  narrow (sd 1.25 C against 1.73).
- The rainforests are denser on 33 of the 36 planets. Nothing else moves beyond chance.

Baselines: "main" is current main 38073e05. Its physics (planet/tectonics, climate, vegetation) is identical to
ca715232, so the paired baseline arm is lane 170b's `cand` arm (36 runs of ca715232, round3.md), re-used rather than
re-run. "Today's Earth" is the climate model's dT = 0.

## The change
`planet/vegetation.py`: `KN_RESP = 0.4`, column 20 of `_KP` (0 for herbs), and in `_year` a stand's leaf respiration
becomes (1 - exp(-KN L)) / KN per unit of LAI L instead of L. This is scout 173's commit 19512a3a, cherry-picked with no
conflict against D47. `docs/review/vegetation/npp-check/npp_check.py` gains `--kn` and now finds its own checkout
(it had a hard-coded path to lane 123's worktree).

KN 0.4 is still a scout value. Lloyd et al. 2010 and Bonan et al. 2011 were not read this session, so the value is not
yet checked against a measured profile.

## 1. Earth NPP check (Earth L6 world 506694, observed climate, soils on)
`npp_check.py --kn 0` (main) against `--kn 0.4`. NPP in g C/m2/yr, area-weighted. The yardsticks are those lane 123
read (MOD17A3; Miami; Malhi et al. 2011 for the field figure).

| box | main | KN 0.4 | MOD17 | Miami | field |
|---|---|---|---|---|---|
| T 18-32 C, P 2500+ mm (wet tropics) | 628 | **831** | 1011 | 1099 | ~1160 |
| T 18-32 C, P 1500-2500 | 647 | 784 | 920 | 961 | |
| T 10-18 C, P 1000-1500 (wet temperate) | 788 | 889 | 741 | 734 | |
| T 18-32 C, P 750-1000 (savanna) | 799 | 803 | 476 | 593 | |
| T 0-10 C, P 500-750 (boreal-ish) | 451 | 488 | 469 | 392 | |
| forest/woodland group (potveg) | 513 | 583 | 634 | 576 | |
| savanna group | 692 | 714 | 501 | 583 | |
| grassland group | 489 | 509 | 292 | 338 | |
| shrubland / tundra / desert | 406 / 185 / 93 | 411 / 190 / 93 | 211 / 123 / 82 | 280 / 120 / 68 | |

| whole land | main | KN 0.4 |
|---|---|---|
| land NPP, Pg C/yr | 59.6 | **64.4** (observed about 56) |
| potveg agreement | 61.7% | 62.2% |
| forest / savanna / desert, Mkm2 | 43.7 / 21.6 / 26.8 | 45.5 / 20.5 / 26.7 |
| burned, Mkm2/yr | 5.67 | 5.66 |
| vegetation carbon, Pg | 493 | 580 |

- The wet tropics come up from 628 to 831 g C/m2/yr, as the scout found (833): 0.54x to 0.72x of the field median. The
  forest group as a whole moves from 0.81x to 0.92x of MOD17.
- **Global land NPP is not unchanged.** It rises 8% (59.6 to 64.4 Pg C/yr). "About unchanged" (59.9) needs lane 123's
  herb-root fix C1 alongside, as scout 173's table shows. KN alone also pushes wet temperate forest further above MOD17
  (+6% to +20%) and boreal-ish cells from 0.96x to 1.04x of MOD17.
- Vegetation carbon rises 18% (deeper canopies hold more leaf and wood).

### Interaction with D47 C (weathering reads rooted cover)
`cover_kn.py` (scratchpad): rooted cover (`vegetation.rooted_cover`, which the weathering's plant factor reads) on the same
Earth run, KN 0 against KN 0.4:

| cells | KN 0 | KN 0.4 | change |
|---|---|---|---|
| all land | 0.864 | 0.867 | +0.002 |
| wet tropics T 18-32, P 2500+ | 0.905 | 0.925 | +0.021 |
| tropics P 1500-2500 | 0.916 | 0.930 | +0.013 |
| savanna, wet temperate, boreal, dry, cold | | | within +-0.002 |

Per cell, the 1st/99th percentile change is -0.015/+0.050. So the lever's +8% NPP barely reaches the weathering. Cover is
already near 0.9 where the forests are, and it saturates, which is what D47 C was built for. Under the old NPP-based
factor, the wet tropics (already above NPP_WEATHER 500) would not have moved either. The +8% elsewhere would have moved it.

## 2. Paired screen (12 of the 36 L6 draws, tails)
I picked main's 5 coldest draws (late dT -3.39 to +0.18, including the one with 26% land ice at the end), 2 draws whose
land-ice peak was over 30%, and main's 5 warmest draws (+2.71 to +4.80). The kn arm ran exactly as paired.sh runs a
draw (`screen.sh`: `tools/ice_diag.py`, 1 Gyr, star_brightening 1.0, the same offsets), with 1 thread each and 4 at once.
Read-outs: `ana.py` (per draw and regional), `tools/judge.py paired`.

| draw | late dT main | late dT KN | KN - main | peak land ice main / KN | end land ice main / KN |
|---|---|---|---|---|---|
| r0.001 l6c_m 53669 | -3.39 | +2.70 | +6.09 | 33.5 / 4.8 | 25.4 / 3.9 |
| r0.001 l6c_0 53669 | -1.78 | -0.10 | +1.68 | 22.4 / 17.1 | 12.1 / 17.1 |
| r0.0005 l6fix 619496 | -1.52 | -0.64 | +0.88 | 30.2 / 27.2 | 13.1 / 24.9 |
| r0.001 l6c_p 819014 | -1.11 | +2.61 | +3.72 | 19.7 / 6.3 | 9.0 / 5.6 |
| r0.001 l6c_p 958504 | +0.18 | +0.58 | +0.40 | 27.6 / 18.6 | 26.2 / 16.6 |
| r0.0005 l6fix 957317 | +0.54 | +1.20 | +0.66 | 30.7 / 9.1 | 9.8 / 8.3 |
| r0.0005 l6c_p 958504 | +2.71 | +2.39 | -0.32 | 30.3 / 3.8 | 4.5 / 2.4 |
| r0.001 l6c_0 819014 | +3.17 | +1.15 | -2.03 | 13.2 / 35.2 | 11.0 / 34.6 |
| r0.001 l6c_p 639472 | +3.35 | +0.69 | -2.67 | 2.8 / 9.2 | 2.2 / 5.8 |
| r0.001 l6c_p 53669 | +3.42 | +2.02 | -1.40 | 5.7 / 21.6 | 4.5 / 20.2 |
| r0.001 l6c_p 733847 | +4.18 | +4.33 | +0.15 | 20.0 / 5.9 | 18.0 / 5.3 |
| r0.0005 l6c_p 639472 | +4.80 | +1.08 | -3.71 | 4.0 / 10.6 | 1.5 / 4.2 |

- **Hard failures: none.** No world ends frozen over (the most land ice at the end is 34.6%). None boils, none goes
  past 40% land ice at any moment, and every draw's late dT is inside -6..+5 C (-0.64..+4.33).
- **Both tails come in,** as expected when a set of draws is picked on main's own chaos: the cold five warm by +0.4 to
  +6.1 C and the warm five cool by up to -3.7. The paired median is +0.10 C (95% CI -1.46..+1.43), split 6 up and 6
  down. The sd of KN - main is 2.7 C, the same as twice the 1.4-1.8 C re-run chaos (round3.md). So the screen cannot see
  any effect on the climate's centre, and it shows no sign of a push one way.
- Soft pass: main 8/12, KN 10/12 (McNemar p 0.69).
- Regional read-outs (late means, median of the paired differences over the 12 draws): **tree cover in the wet
  equatorial cells +2.8 points, higher in 11 of 12 draws.** This is the one consistent signal, and it is the lever's
  own target. Land trees +1.4 points (7/12). The ice edge (the lowest latitude with land ice) moves poleward by 2.4
  degrees (6/12). Frozen sea +0.01, arid land +0.8 points, hot desert +0.4, land rain +10 mm, pCO2 -95 ppm (4/12 up).
  The weathering's plant factor moves -0.005 (6/12). None of these, apart from the wet equatorial trees, is a split
  better than 8/4.
- The single +6.1 C draw (r0.001 l6c_m 53669) was main's coldest draw. On main, the other roll of the same planet and
  offset had +1.59, so +2.70 is inside that planet's own range. It is regression to the mean, not a hot draw.

Read-outs for the two cold draws done first showed pCO2 nearly doubled. The full 12 do not bear that out (median
-95 ppm). That is the "global numbers are chaos" lesson again.

## 3. Full paired judge (36 L6 draws, 2 rolls x 18)
The kn arm is `paired.sh` from a frozen copy of this code (`run_full.sh`, MAXSIM 4, THREADS 1). It re-uses the screen's
12 runs, since they used the same invocation. main is lane 170b's cand arm (ca715232, the same physics as main
38073e05). Read-outs: `tools/judge.py paired`, `tools/hard_bar.py` on the symlink roots `hb_base/` and `hb_kn/`, and
`ana.py` / `tails.py` in the scratchpad. As a check, the base arm reproduces round3.md's cand column exactly (sd 1.73,
percentiles, 30/36).

### The bar: passes
| check | main | KN 0.4 |
|---|---|---|
| hard: frozen over at the end (PW-1425) | 0/36 | **0/36** |
| (old rule, 40%+ at some moment of 884-1000, reported) | 0/36 | 0/36 |
| hard: boiled / hellhouse | 0/36 | 0/36 |
| hard: ocean loss | 0/36 | 0/36 |
| hard: CO2 crash (below the plants' compensation point) | 0/36 | 0/36 |
| soft pass (bar + finish moment) | 30/36 | **31/36** |
| late dT outside -6..+5 C of today's Earth | 0/36 | **0/36** (range -1.46..+4.33) |
| peak land ice in 884-1000, mean / max | 15.0 / 33.5% | 16.4 / 37.3% |

McNemar on the soft pass: both 25, main only 5, KN only 6, exact p 1.00, so within chance of main.
Secondary measures, reported: CO2 under 100 ppm 2/36 main, 1/36 KN. An 8-fold CO2 fall in 50 Myr or less (end at most
1/4 of the level before the fall): 21/36 main, 26/36 KN; (end at most 2x the bottom of the fall): 16/36 main, 24/36 KN.
End pCO2 outside 180-600 ppm: 13/36 main, 11/36 KN. The rise in fast CO2 falls is the one count that moved by more than a
few draws. It is a secondary, reported measure, not part of the bar. Paired over the same draws it is 21 against 26 of
36, which I read as within the chaos, but it is worth watching on the next judge.

### The centre: unchanged within the chaos
Paired KN - main over the 36 draws (judge medians, 95% CI): late dT +0.40 C [-0.65, +0.87], end T -1.14 C
[-2.42, +2.50], late CO2 +0.01 e-folds [-0.05, +0.14], trees +1.0 points [-1.4, +1.9], arid +0.9 points
[-1.1, +1.8], land rain -16 mm [-45, +16], sink reference +0.008. None of these moved (sign p >= 0.24). Mean late dT is
+1.40 C on main and +1.44 C with KN (mean paired difference +0.04, sd 2.10).

### Regional read-outs (late means over 600-1000 Myr, median of the paired differences, draws where KN is higher)
| measure | main | KN | median KN - main | KN higher |
|---|---|---|---|---|
| **tree cover of the wet equatorial cells, %** | 62.4 | 66.5 | **+4.0** | **33/36** |
| land tree cover, % | 40.6 | 40.8 | +1.0 | 21/36 |
| lowest latitude with land ice, deg | 31.4 | 33.8 | +0.9 | 18/36 |
| frozen sea share | 0.135 | 0.132 | -0.001 | 18/36 |
| arid land, % | 21.7 | 23.2 | +0.8 | 22/36 |
| hot desert, % | 7.7 | 8.2 | +0.2 | 20/36 |
| land rain, mm/yr | 1154 | 1130 | -17 | 16/36 |
| global mean T, C | 14.7 | 14.6 | +0.05 | 18/36 |
| weathering plant factor (w_plant) | 2.351 | 2.355 | -0.005 | 16/36 |

The wet equatorial forests are denser on 33 of 36 planets, which is the lever doing what it is for. Nothing else in the
climate moves beyond the coin-flip.

### The spread across planets: kept (narrower)
| late dT over the 36 draws | main | KN 0.4 |
|---|---|---|
| sd between draws | 1.73 C | **1.25 C** (D47 bar: about 1.7) |
| range | -3.39..+4.80 | -1.46..+4.33 |
| 10th / 25th / 50th / 75th / 90th percentile | -0.69 / +0.44 / +1.28 / +2.77 / +3.26 | -0.27 / +0.66 / +1.30 / +2.61 / +2.78 |
| interquartile range | 2.34 C | 1.95 C |
| mean distance from the median | 1.33 C | 0.99 C |
| within-seed sd (re-runs of one planet) | 1.68 C | 1.31 C |
| draws colder than -1 C / warmer than +3 C | 4 / 7 | 1 / 3 |
| hottest / coldest single late step | +11.8 / -9.3 | +11.1 / -9.8 |

The spread did not widen. It came out narrower (1.25 against 1.73 C sd). Within-seed sd also fell (1.31 against 1.68),
so most of that is likely this draw of the chaos, not a new thermostat. I do not claim the lever narrows the spread. It
keeps the D47 spread, which was the bar.

### Verdict
KN_RESP 0.4 passes the D47 bar: 0 hard failures, soft pass 31/36 against 30/36 (p 1.00), every late dT inside -6..+5 C,
and the spread is kept (sd 1.25 C). The climate's centre does not move. The lever's own target does move: rainforest NPP
on Earth goes from 628 to 831, and wet equatorial tree cover in the runs rises 4 points on 33 of 36 planets. D47 C
insulates the carbon cycle from the +8% land NPP, as designed. Rooted cover moves only 0.2% on land, and the weathering's
plant factor moves -0.005.

Open, not fixed here (scout 173's limits stand): land NPP on Earth goes 59.6 to 64.4 Pg C/yr. The total stays near
observed only when this ships with lane 123's C1 (herb root upkeep). Wet temperate forest overshoots MOD17 by 20%. Wet
tropics are still 0.72x the field median. KN 0.4 is unsourced until Lloyd 2010 and Bonan 2011 are read.

## Tests, Earth check, scorecard
- `pytest -n 2 -m "not slow"` (golden deselected, NUMBA 1 thread each): 1000 passed, 1 skipped, 5 failed.
  - Four of the failures are thread tests (`test_kernel_threads.py` x3, `test_thread_independence.py`). They need more
    than one numba thread, and with NUMBA_NUM_THREADS 2 all 4 pass. That is the environment, not the change.
  - The fifth is `test_timezoom.py::test_edge_margins_are_the_run_margin_band`. It fails with KN and passes on main. It
    needs more than 3 thick-ice cells in the second margin ring of the `sim4` fixture's geography, and the lever's
    different plants change that fixture's coastline (2 cells left). Harness fix: the test's synthetic caps start at
    |lat| > 50 instead of 55, with the assertions unchanged. It now passes on both this code and main.
- Climate-area slow tests (`test_envelopes.py`, `test_sea_level.py`, `test_co2_stock.py`): 29 passed.
- `test_golden.py --update-golden`: `sim_L4_s1_60myr.json` rewritten (the plants feed the climate and erosion), then
  2 passed without the flag.
- `tools/earth_check.py` (L6): Koppen main group 71%, exact code 37%, log-rain correlation 0.718, global mean T 13.9 C
  against NCEP's 14.0. The same as main (round3.md), as expected.
- `tools/scorecard.py`: line appended (tagged `38073e05+dirty`, src b64c007fd09c7f79: run before the commit, so the
  line carries this lane's code). Earth: group 71.4%, exact 37.4%, rain correlation 0.718, the same as main.
  - Seed 1 at 1000 Myr: ice 2.7%, trees 39.9%, land NPP 394. On ca715232 (round3.md) it was ice 5.8%, trees 31.8%,
    NPP 390.
  - Seed 2: ice 1.8%, trees 49.5%, NPP 576. On ca715232: 1.7%, 53.5%, 546.
  - These are single seeds, inside the re-run chaos.

## Status
Done: Earth check, rooted-cover check, 12-draw screen, full 36-draw judge, tests. Commit on branch (see the report).
Scratch kept: `l181/judge/` (the kn arm's 36 runs, plus links to lane 170b's base arm), `ana.py`, `tails.py`,
`judge36.json`, `npp/`, logs. Code copies removed.
