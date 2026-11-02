# Lane 134: the rain on the overturning's sea (PW-1364), and the NH subtropical seas (PW-1362), 2026-11-02

Status: **the paired judge finished, and it passes the bar.** Hard failures are 0 in both arms. Soft passes are
cand 30/36 against main 32/36 (McNemar p 0.75; lane 24's null change moves 7-8 draws). One measure moved and needs
the coordinator's call: late dT +0.57 C warmer [+0.24, +1.56]. Hot desert also moved, +1.3 points. Arm a1 is a
second rain pass on the overturning's sea, commit c680e951. Not merged.

## 1. Diagnosis (the gate)

**The call order in `climate.compute`** (before this change):

1. first-guess temperatures, winds, currents;
2. `sea_surface` without the overturning (`raw0`, `sst0`);
3. `_air_temps(sst0)`;
4. the rain (`rain`, both half-years), its clouds, the summer energy split (`d_sum`);
5. the air again with `d_sum`, then `_land_finish`, then `water_balance`;
6. `ocean.freshwater` from the rain, then `ocean.solve`. That is the salinity and the overturning; its inflow's
   warmth enters through `sst_of(share, t_in)`, i.e. `sea_surface(share=, t_in=, base=raw0)`. Then `oc["sst"]` and
   `winter_half` (the inflow's smaller winter swing) feed `_air_temps` again;
7. the shelf seas, `front_shift` winds, the final air, Köppen, humidity.

The overturning's heat enters only at step 6, after the rain, so the rain never sees it. On Earth L6 the
overturning adds +5.1 C to the N Atlantic storm-track box's annual SST (`seaparts.py`). The inflow also shrinks the
box's winter swing (`winter_half`). The rain's winter sea there was 6.7 C, against 13.0 in the finished climate.

**The overturning needs the rain** (its fresh water: P - E, the rivers, the ice), so the order can't simply be
flipped. Candidates:

- **(a) A second rain pass after `ocean.solve`** on the overturning's sea and the air over it, warm-started from the
  first pass's vapour (`rain_start` = pass 1's end state: RAIN_WARM_DAYS 8 instead of 20). The overturning keeps
  pass 1's fresh water.
  - Cost on Earth L6: compute 0.81 -> 1.01 s from cold (+25%), 0.71 -> 0.96 s warm.
  - Works the same in worlds, Earth checks, zooms and runs.
- **(b) Carry the previous update's overturning** (`moc_state`) into `sea_surface` before the rain.
  - Free per step, but runs don't pass `moc_start` today (`tectonics/earth._climate`). Worlds and Earth checks
    start cold, so they would still have the bug.
  - It needs new run state too. Rejected: it fixes only runs.
- **(c) Iterate both** (rain -> overturning -> rain -> overturning ...). That is (a) plus a second `ocean.solve`.
  - Checked as a diagnostic: re-solving the overturning on pass 2's fresh water moves Earth's N Atlantic sinking
    12.49 -> 12.54 Sv and the box SST by 0.01 C.
  - Not needed.

**Chosen: (a), the simplest sound one.** Pass 2 sees the air the way pass 1 does: `_air_temps` without the summer
split, but on the overturning's sea and with `winter_half`. Pass 2's rain, clouds and `d_sum` then replace pass 1's
for everything downstream. The jets and storm tracks come from pass 2's temperatures, as pass 1's did from its own.
The winds stay the first guess's (as before).

**Convergence of the warm start:** pass 2 at 8 days against 20 days on Earth L6. Land rain ratio: median 1.000,
p5 0.981 (Apr-Sep) / 0.999 (Oct-Mar); land mean 0.999 / 1.000. That's within the kernel's ~1% warm-start error
(PW-387).

## 2. Earth screens (main = 2b3bf6f1, a1 = c680e951)

`ec2.sh TAG "TUNE"` runs these: L7 `earth_check`, lane 126's cloud screen (L7), L6 `moisture_regions --no-cf`
(P / E / PW against GPCP / NCEP / NCEP) and `seaair.py` (the rain's sea, L6). `summ2.py` makes the table. Main was
screened with a temporary `rain_moc=0` switch, since removed.

| | obs | main | a1 |
|---|---|---|---|
| B % (Kottek 30.1) | | 24.5 | 25.4 |
| exact / group % | | 37 / 71 | 36 / 71 |
| log-rain r | | 0.714 | 0.713 |
| land P (GPCC 791) | | 1056 | 1030 |
| interiors 40-60 N x obs | | 1.85 | 1.70 |
| humid coasts x obs | | 0.56 | 0.54 |
| W Europe | 903 | 1159 | 1107 |
| European Russia | 591 | 888 | 813 |
| W Siberia | 506 | 701 | 701 |
| Gobi/Mongolia | 155 | 537 | 482 |
| Central Asia | 208 | 318 | 270 |
| Great Plains | 551 | 767 | 738 |
| NE USA | 1033 | 1534 | 1456 |
| SE USA | 1329 | 720 | 648 |
| Pampas | 943 | 394 | 395 |
| India | 1126 | 626 | 591 |
| SE China | 1460 | 1062 | 1026 |
| Japan | 1683 | 672 | 622 |
| E Australia | 737 | 551 | 553 |
| Sahel | 596 | 2093 | 2034 |
| Mediterranean | 545 | 415 | 404 |
| N Atl storm track Oct-Mar P/E/PW | 1651/1339/15.2 | 1206/452/14.1 | 2765/1990/17.5 |
| N Atl storm track Apr-Sep P/E/PW | 1057/610/21.6 | 799/848/15.6 | 1760/1919/18.2 |
| N Pac storm track Oct-Mar P/E/PW | 1465/882/12.2 | 1229/427/14.7 | 1096/319/15.5 |
| Gulf of Mexico Apr-Sep P/E/PW | 1239/1423/39.0 | 523/1493/31.6 | 512/1449/31.7 |
| W Atl subtropics Oct-Mar P/E/PW | 1500/2570/24.2 | 1008/2445/22.4 | 1495/3037/24.0 |
| warm month 0-20 / 20-40 / 40-60 (NCEP 26.5 / 25.6 / 18.5) | | 24.8 / 26.0 / 18.3 | 24.9 / 26.0 / 18.4 |
| summer sun 20-40 (CRU 0.669) | | 0.758 | 0.764 |
| sky W Europe (60-75) | | 73.0 | 70.0 |
| rain's N Atl sea, Jan half: SST / air (NCEP air 8.0) | | 6.7 / 4.7 | 13.0 / 12.9 |

Sea rain by band (earth_check, model / GPCP, mm/yr):

| band | 30-40 | 40-50 | 50-60 | 60-70 | 70-80 |
|---|---|---|---|---|---|
| main | 676 | 1065 | 955 | 391 | 144 |
| a1 | 746 | 1318 | 1480 | 778 | 222 |
| GPCP | 1158 | 1300 | 1148 | 905 | 349 |

**Reading.**

- The land holds or improves:
  - B +0.9 points, log-rain r unchanged, Köppen group unchanged, exact -1 point;
  - the over-wet 40-60 N interiors 1.85 -> 1.70x (W Europe, European Russia, Mongolia and Central Asia all
    drier, toward observed);
  - the humid coasts 0.56 -> 0.54x (SE USA 720 -> 648, Japan 672 -> 622);
  - warm bands and sunshine unchanged.
- The NH seas poleward of 30 N now rain far closer to GPCP (40-50 N 1065 -> 1318 against 1300; 60-70 N 391 ->
  778 against 905).
- **The one overshoot is the N Atlantic box itself:**
  - winter rain 2765 against 1651, evaporation 1990 against 1339 (1.49x; it was 0.34x);
  - its summer evaporation 1919 against 610.
- That is explained, not new. The rain now sees the finished sea, and the finished N Atlantic is too warm:
  - its annual SST is 13.7 (air 14.3) against NCEP air 10.7;
  - its monthly half-swing is 1.92 against 4.64, so its winter is ~5 C too warm.
  - The swing is PW-593 (one 50 m layer, plus `winter_half` under the inflow). The overturning's +5.1 C annual is
    probably a little large.
  - Before this change the rain hid that error by seeing a sea 6 C colder than the climate's. Draft:
    draft-n-atlantic-finished-sea-too-warm-for-the-rain.
- The N Pacific storm track got drier (E 427 -> 319, NCEP 882). The overturning's zonal take-off (`moc_zonal`)
  cools the rest of each band slightly, and the global rescaling takes ~3% more from every cell.

## 3. L6 sanity (4 re-rolled seeds, 1 Gyr, roll 0.0005) and the paired judge

Code frozen by `git archive` into `$S/code/main` (2b3bf6f1) and `$S/code/cand` (c680e951). Draws run through
`docs/review/base-climate/v1-finish-16/paired.sh` (MAXSIM 4-5, THREADS 3; Daniel's 15-core cap for this lane), launched by
`$S/launch.sh ONLY ROLL...`, with S = /tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l134.

**Paired judge (2 rolls, 36 draws per arm; read 14:05, 2026-11-02):**

| measure | main median | cand median | median B-A | 95% CI | B>A / B<A | moved |
|---|---|---|---|---|---|---|
| end T | 1.58 | 1.90 | +0.79 | [-1.42, +1.90] | 20 / 16 | |
| late dT | 0.22 | 1.77 | +0.57 | [+0.24, +1.56] | 25 / 11 | * |
| late CO2 | 0.52 | 0.67 | +0.08 | [-0.03, +0.18] | 22 / 14 | |
| land % | 34.2 | 34.6 | +0.28 | [-0.03, +0.46] | 23 / 13 | |
| sink ref | 6.71 | 6.67 | -0.06 | [-0.09, +0.00] | 13 / 23 | |
| src ref | 7.99 | 7.94 | +0.00 | [-0.03, +0.06] | 18 / 18 | |
| arid % | 20.9 | 22.7 | +0.82 | [-0.11, +2.45] | 23 / 13 | |
| hot desert % | 7.6 | 7.9 | +1.30 | [+0.43, +1.85] | 26 / 10 | * |
| land rain | 1147 | 1166 | +5 | [-41, +33] | 18 / 18 | |
| trees % | 39.0 | 40.4 | -0.16 | [-1.90, +2.74] | 18 / 18 | |

**Pass count.**
- main 32/36 (15/18 and 17/18), cand 30/36 (14/18 and 16/18). Both pass 26 draws, main only 6, cand only 4,
  neither 0; McNemar p 0.754.
- Hard failures 0 on both arms: frozen over 0, hellhouse 0.
- Icehouse 36 / 36 on both; glacial maxima 23 -> 13.

**Reading.**
- The sanity runs' arid +5 was chaos: the judge puts arid at +0.8, not moved. CO2, sink ref and land rain didn't
  move either.
- BWh +1.3 goes the way Earth's B went (+0.9). It is also toward Kottek on Earth (11.7 -> 11.9 against 14.8), but
  away from the fix PW-290 wants (L7 worlds already too arid).
- **Late dT +0.57 C** (25 of 36 draws warmer, fewer glacial maxima) is not explained by a CO2 change.
  - Candidates: the rain's clouds over the warm storm-track seas and the land downwind (Earth's W Europe sky
    73 -> 70%), so more sun reaches high latitudes; or less snow on the drier interiors.
  - Not diagnosed: I handed off at the call budget.
  - Earth's global T is unchanged (13.9 against NCEP 14.0).
  - I read it as a moderate climate shift that the bar tolerates. Hard failures are 0 and the passes are within
    chaos, but it is a moved measure the mechanism doesn't clearly explain.
- **The coordinator's call:** merge as a soundness fix (memory: a correct mechanism even if a fitted kernel
  regresses), or first run a cheap cloud / snow-albedo split of the dT shift on 2-3 warm draws.

**Also before merging:** the full suite. test_envelopes: see section 4b. The not-slow suite passed: 926 passed. Its 7 failures were 3 thread tests under
NUMBA_NUM_THREADS=1, which pass at 4 threads; the goldens, regenerated in d2a34a48; and
the probe test, fixed in 62fa91e2.

**Don't delete `$S` until the judge is read:** the frozen code copies and the draws live there. Then
`rm -rf "${S:?}"` (no symlinks inside it). Also remove the worktree's private `data/earth/` copy (133 MB,
gitignored, a real directory, not a link).

## 4. PW-1362: the NH subtropical seas (diagnosis)

`seaparts.py` (Earth L6, a1) splits the annual SST into its parts and compares the swing with NCEP's air.

| box | t_sea (lat) | chill | upwelling | currents | overturning | final SST | final air | NCEP air | monthly half-swing model / NCEP |
|---|---|---|---|---|---|---|---|---|---|
| Gulf of Mexico | 22.5 | -0.38 | -1.45 | +3.13 | 0.0 | 23.8 | 22.8 | 25.0 | 2.74 / 3.61 |
| W Atlantic subtropics | 18.9 | -0.19 | -0.64 | +2.77 | +0.82 | 21.7 | 21.7 | 21.8 | 1.86 / 4.69 |
| E Atlantic subtropics | 19.8 | -0.02 | -0.13 | -0.74 | +0.78 | 19.7 | 19.8 | 21.3 | 1.46 / 3.03 |
| NW Pacific subtropics | 20.1 | -0.20 | -0.68 | +2.58 | -0.12 | 21.7 | 21.2 | 21.2 | 2.22 / 5.96 |
| N Atlantic storm track | 8.8 | -0.19 | 0.0 | 0.0 | +5.06 | 13.7 | 14.3 | 10.7 | 1.92 / 4.64 |
| N Pacific storm track | 9.0 | -0.19 | -0.03 | +0.38 | -0.50 | 8.7 | 8.0 | 7.4 | 3.08 / 5.55 |

("currents" is raw0 - t_sea + chill + upwelling: the currents' anomaly with the band mean restored.)

- **The W Atlantic and NW Pacific subtropics:** the annual mean is right (within 0.5 C); the summer deficit is all
  swing (40% of NCEP's). That is PW-593's mechanism, one 50 m summer layer under weak summer winds. It is
  strongest in the subtropical highs, where the real summer layer is ~20 m.
- **The Gulf:** the annual mean is 2.2 C cool, the swing 0.9 C short.
  - The cool mean is mostly the coastal upwelling, -1.45 C averaged over the whole box. `upwelling_cooling` puts
    up to 6.1 C in the Bay of Campeche and 4-4.5 C along N Yucatan; 82 of the box's 153 L6 cells get over 0.5 C.
  - The rule asks only whether the trades' Ekman drift points away from the nearest coast. In a small, nearly
    enclosed sea the drift piles water against the opposite shore instead of carrying it away. N Yucatan's
    upwelling is real but local (not checked against data here). The currents add +3.1.
  - It is also the cold-air outbreaks: the air is 1 C under the SST.
- **The E Atlantic:** the annual mean is 1.5 C cool. The Canary current takes -0.74, and the latitude's t_sea is
  19.8 against NCEP's 21.3. The swing is half of NCEP's.
- **Recommendation:**
  - Fold PW-1362's swing part into PW-593. It is the same rule: a summer mixed layer from the wind and the heating.
    Add the subtropical rows (W Atlantic, NW Pacific, Gulf) to PW-593's bar.
  - Draft the Gulf's upwelling as its own small item: draft-gulf-upwelling-box-wide.
  - The E Atlantic's cool mean is small and has two parts; it's noted in that draft, not ticketed.

## 4b. State and next

- **Done:**
  - the diagnosis (section 1);
  - arm a1 coded, with the probe and `moisture_regions` following the warm start;
  - Earth screens (section 2), not-slow tests and goldens;
  - the PW-1362 diagnosis (section 4);
  - drafts: draft-n-atlantic-finished-sea-too-warm-for-the-rain, draft-gulf-upwelling-box-wide.
- **Strikes:** 0 failed arms.
- **Judge read** (section 3): it passes the bar, with late dT +0.57 C moved and not explained. `tests/test_envelopes.py`
  passes (11 passed). The full suite hasn't been run (that's for the merge).
- **Scratch deleted** after the judge was read: `$S`, the frozen code and the draws. The worktree's private
  `data/earth/` copy is deleted too. To re-read the judge, re-run section 3's launches.
- **Next:** the coordinator's call on late dT. Either merge, or run a cloud / snow-albedo split of the shift on 2-3
  warm draws first.
- **PW-1362:** fold its swing part into PW-593 (the coordinator's call); the Gulf goes to the upwelling draft.
  PW-593 is the lever for both PW-1362 and the N Atlantic overshoot that this fix exposes.

## Files

ec2.sh, summ2.py (lane 132's harness pointed at l134), seaparts.py, seaair.py (lane 132's), launch.sh (a copy of $S/launch.sh), why.py.
