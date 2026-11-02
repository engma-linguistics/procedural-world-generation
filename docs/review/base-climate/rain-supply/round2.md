# Lane 134: the rain on the overturning's sea (PW-1364), and the NH subtropical seas (PW-1362), 2026-11-02

Status: **in progress.** Arm a1 (a second rain pass on the overturning's sea) holds on Earth L7; L6 sanity seeds
running. Code: commit c680e951 on this branch.

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

(pending)

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

(pending)

## Files

ec2.sh, summ2.py (lane 132's harness pointed at l134), seaparts.py, seaair.py (lane 132's).
