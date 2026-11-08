# Grass NPP, round 3 (lane 185, 2026-11-04): C1 (herbs' roots pay upkeep) on D47 + KN main

**In plain words.** Grass in the model grows 1.4-1.8 times what field plots measure, because a grass plant's roots
cost it nothing to keep alive. Lane 123's fix C1 makes a herb's live roots and rhizomes respire with its leaves
(2.5 times the leaves' rate), and lowers the fire's fuel floor from 250 to GlobFIRM's 200 g C/m2 so that scrub, now
with less grass litter under it, still burns. Lane 140 judged C1 on older main and it failed (strike 1): 2 of 36
planets went over 40% land ice in the last ~120 Myr. Lanes 140b-d then found that this was mostly chaos at a thin
margin, plus a small real cold push. Since then D47 changed two things: the rock weathering reads how much ground the
plants cover, not how fast they grow, and "frozen over" is judged on how a run ends. This lane puts C1 on current main
and judges it again (attempt 2 of 3).

- On Earth's real climate the world's grassland now grows what field plots measure (Yang et al. 2020's fit, within
  4% in every rain band under 600 mm; it was 1.15-1.2x). Savanna growth falls 15%. The whole land's growth goes from
  64.4 to 60.0 Pg C/yr (observed: about 56), undoing most of lane 181's +8%. Forests barely move.
- The weathering barely notices: it reads plant cover, and C1 thins it by 0.5%. So lane 140's planned re-anchor is
  not needed.
- On all 36 test planets: none ends frozen over, boils, loses its ocean or crashes its CO2. Soft passes are 34
  against main's 31 (within chance). Every planet's late climate stays inside -6..+5 C of today's Earth, and the
  spread between planets is unchanged (sd 1.26 C against 1.25).
- The one thing that moves in the runs is the steppe: about 2 points fewer trees (of 14) on 32 of 36 planets,
  because grass fires now burn where the fuel sat just under the old floor. Land tree cover falls 1.8 points.
- Verdict: passes the D47 bar. Lane 140's strike does not recur.

Baselines: "main" is current main 21072a23. Its physics (planet/tectonics, climate, vegetation) is identical to
a6404611 (lane 181's KN_RESP commit; `git diff a6404611 HEAD -- planet/ tools/` touches only planet/lineages and
planet/server.py), so main's paired arm is lane 181's 36 `kn` runs, re-used. "Today's Earth" is the climate model's
dT = 0.

## The change
- `planet/vegetation.py`: `HERB_ROOT_RESP = 2.5`, multiplying the herb PFTs' maintenance rate `rl`; `FUEL_MIN`
  250 -> 200 g C/m2 (GlobFIRM, Thonicke et al. 2001). Lane 140's commit 88ebe5a4, cherry-picked; the only conflict
  was the golden file. Both halves go together: lane 140b showed that herb respiration alone stops the test's
  Mediterranean scrub burning (fine fuel falls below the 250 floor), and 200 is the sourced value.
- `tests/test_vegetation.py`: the fuel-floor assert reads `V.FUEL_MIN` (from 88ebe5a4).
- `planet/tectonics/diag.py` (instrument only, no physics): each climate update also records herb cover over land
  (`grass`), and tree and herb cover on the steppe (Koppen BS: `steppe_trees`, `steppe_grass`) and on the tropical
  wet-dry land (Aw: `savanna_trees`, `savanna_grass`), so a judge can see the grassy lands, not just global dT.

### Lane 140's NPP_WEATHER re-anchor: moot
NPP_WEATHER is gone (D47 C). The weathering's plant factor reads `vegetation.rooted_cover`, the summed cover of
trees, shrubs and herbs. C1 changes how fast grass grows, not whether it is there. On Earth's observed climate
(`cover_c1.py` / `cover_cmp.py` in the scratchpad, area-weighted rooted cover, main against C1):

| cells | main | C1 | change |
|---|---|---|---|
| all land | 0.867 | 0.861 | -0.005 |
| wet tropics T 18-32 C, P 2500+ mm | 0.925 | 0.924 | -0.002 |
| savanna T 18-32, P 750-1000 | 0.913 | 0.905 | -0.008 |
| warm semi-arid T 18-32, P 250-500 | 0.906 | 0.904 | -0.002 |
| steppe T 0-18, P 250-500 | 0.937 | 0.936 | -0.001 |
| wet temperate T 10-18, P 1000-1500 | 0.959 | 0.953 | -0.006 |
| dry, P < 250 | 0.716 | 0.703 | -0.013 |
| cold, T < 0 | 0.805 | 0.803 | -0.001 |

Per cell, the 1st/50th/99th percentile change is -0.098 / -0.0005 / +0.019.

So there is nothing to re-anchor. The weathering sees a 0.5% thinner cover over land, mostly in dry land, where C1's
grass thins at the margin.

## 1. Earth NPP check (Earth L6 world 506694, observed climate, soils on)
`npp_check.py` on C1, against lane 181's `--kn 0.4` output (identical to current main's code). NPP in g C/m2/yr,
area-weighted. Yardsticks as lane 123 read them (MOD17A3, Miami; Deshmukh 1984 and Yang et al. 2020 for grass
above-ground NPP).

| box | main | C1 | MOD17 | Miami |
|---|---|---|---|---|
| T 18-32 C, P 2500+ mm (wet tropics) | 831 | 827 | 1011 | 1099 |
| T 18-32 C, P 1500-2500 | 784 | 769 | 920 | 961 |
| T 18-32 C, P 750-1000 (savanna) | 803 | **682** | 476 | 593 |
| T 18-32 C, P 250-500 (warm semi-arid) | 474 | **401** | 144 | 286 |
| T 10-18 C, P 1000-1500 (wet temperate) | 889 | 878 | 741 | 734 |
| T 10-18 C, P 250-500 (temperate steppe) | 404 | **350** | 282 | 292 |
| T 0-10 C, P 500-750 (boreal-ish) | 488 | 476 | 469 | 392 |
| forest/woodland group (potveg) | 583 | 565 | 634 | 576 |
| savanna group | 714 | **632** | 501 | 583 |
| grassland group | 509 | **465** | 292 | 338 |
| shrubland / tundra / desert | 411 / 190 / 93 | 357 / 187 / 80 | 211 / 123 / 82 | 280 / 120 / 68 |

| whole land | main | C1 |
|---|---|---|
| land NPP, Pg C/yr | 64.4 | **60.0** (observed about 56) |
| potveg agreement | 62.2% | 62.4% |
| forest / savanna / desert, Mkm2 | 45.5 / 20.5 / 26.7 | 45.0 / 20.0 / 27.2 |
| burned, Mkm2/yr | 5.66 | 5.36 |
| vegetation carbon, Pg | 580 | 573 |

Grass above-ground NPP (herb layer, g dry/m2/yr) against the field fits:

| warm African grassy land, rain band | main | C1 | Deshmukh 1984 | Yang et al. 2020 | herds main / C1, t/km2 |
|---|---|---|---|---|---|
| 250-400 mm (328) | 333 | 277 | 259 | 188 | 1.28 / 0.96 |
| 400-550 mm (468) | 543 | 447 | 377 | 286 | 2.57 / 1.89 |
| 550-700 mm (626) | 711 | 588 | 512 | 397 | 4.10 / 3.07 |
| 700-900 mm (804) | 832 | 696 | 662 | 521 | 5.44 / 4.10 |

| world grassland (potveg), rain band | main | C1 | Yang et al. 2020 |
|---|---|---|---|
| 100-250 mm | 109 | 90 | 94 |
| 250-400 mm | 222 | 187 | 186 |
| 400-600 mm | 353 | 293 | 291 |

(Above 600 mm the potveg grassland cells are mostly tree-covered in the model, so the herb layer's share is small and
the row does not test the grass.)

- **Grass comes down to the field values.** On the world's grassland C1 lands on Yang's fit in every band under
  600 mm (90/187/293 against 94/186/291), from 1.15-1.2x above it. In warm Africa it goes from 1.6-1.9x Yang to
  1.3-1.6x, and from 1.3-1.4x Deshmukh's peak biomass to 1.05-1.2x. Savanna boxes fall 15% (803 -> 682); the potveg
  grassland group 9%, savanna group 11%, shrubland 13%.
- **Land NPP 64.4 -> 60.0 Pg C/yr** (observed about 56): the +8% of KN_RESP is mostly given back, as scout 173's
  table said it would be. Forests barely move (wet tropics 831 -> 827).
- These are the same numbers lane 140 got on older main (grassland 489 -> 444, savanna 692 -> 608, Africa 711 -> 588
  at 626 mm), shifted by KN's forest gain.
- **Herds on Earth's climate fall** with the grass (550-700 mm: 4.10 -> 3.07 t/km2; Coe et al. 1976's parks 4.0-4.4).
  Lane 140 found the same: the herd fit's own grassland offset is now the gap (PW-1261), not the plants.

## 2. Paired screen (12 of the 36 L6 draws: main's tails)
Picked on main (lane 181's kn arm): its 5 coldest draws by late dT (-1.46 to -0.10), its 5 warmest (+2.74 to
+4.33), and 2 high-ice draws (r0.001 l6c_p 583167, the highest window peak, 37.3%; r0.001 l6c_0 819014, the most land
ice at the end, 34.6%). `sel.py` in the scratchpad. The C1 arm ran exactly as paired.sh runs a draw (`screen.sh`:
`tools/ice_diag.py`, 1 Gyr, star_brightening 1.0, the same offsets, 1 thread each, 6 at once). A second arm, **mi**
(main's code plus the diag instrument only), re-ran the same 12 to get main's grass read-outs. It reproduces lane
181's runs exactly (late dT, ice and every other field identical on 12 of 12), so single draws are deterministic and
the instrument changes nothing. Read-outs: `ana.py` in the scratchpad.

| draw | late dT main | late dT C1 | C1 - main | peak land ice in 884-1000, main / C1 | after 300 Myr | end land ice main / C1 |
|---|---|---|---|---|---|---|
| r0.0005 l6c_0 733847 | -1.46 | +0.11 | +1.57 | 24.1 / 17.4 | 39.5 / 32.8 | 14.8 / 6.6 |
| r0.0005 l6fix 619496 | -0.64 | +1.00 | +1.64 | 27.2 / 19.1 | 36.9 / 19.1 | 24.9 / 17.4 |
| r0.0005 l6c_p 53669 | -0.58 | -0.72 | -0.15 | 21.0 / 26.7 | 25.9 / 29.2 | 10.0 / 4.4 |
| r0.0005 l6fix 639472 | -0.44 | +2.12 | +2.56 | 27.1 / 6.7 | 27.1 / 22.8 | 8.0 / 5.7 |
| r0.001 l6c_0 53669 | -0.10 | +1.90 | +2.00 | 17.1 / 6.8 | 24.6 / 35.7 | 17.1 / 3.5 |
| r0.001 l6c_0 819014 | +1.15 | -0.93 | -2.07 | 35.2 / 12.9 | 35.2 / 25.6 | 34.6 / 7.8 |
| r0.001 l6c_p 583167 | +1.18 | +1.64 | +0.46 | 37.3 / 12.5 | 37.3 / 12.6 | 10.5 / 1.2 |
| r0.001 l6fix 619496 | +2.74 | +1.88 | -0.86 | 8.3 / 13.1 | 14.0 / 13.1 | 6.7 / 6.0 |
| r0.0005 l6c_0 53669 | +2.82 | +0.82 | -2.00 | 28.1 / 33.5 | 28.1 / 33.5 | 28.1 / 33.5 |
| r0.0005 l6c_m 53669 | +3.03 | +0.45 | -2.57 | 3.5 / 24.7 | 12.0 / 29.9 | 0.3 / 24.7 |
| r0.001 l6c_m 958504 | +3.07 | +1.00 | -2.07 | 9.5 / 28.1 | 13.3 / *44.5* | 4.0 / 6.3 |
| r0.001 l6c_p 733847 | +4.33 | +0.86 | -3.47 | 5.9 / 10.3 | 5.9 / 18.1 | 5.3 / 9.2 |

- **Hard failures: none.** No draw ends frozen over (the most land ice at the end is 33.5%), none boils, and every
  late dT is inside -6..+5 C (-0.93..+2.12). One draw (*44.5*, r0.001 l6c_m 958504) passes 40% land ice for a while
  before the window and ends at 6.3%: not a failure under PW-1425, reported.
- **Both tails come in,** as they must on draws picked on main's own chaos: the cold five warm by -0.15 to +2.56 C and
  the warm five cool by -0.86 to -3.47. Paired mean -0.41 C, median -0.50, sd 2.04 (twice the re-run chaos). The
  cold tail is where lane 140 failed; here every one of main's 5 coldest stays under 27% land ice in the window, and
  4 of 5 end with less ice than main.
- Window peak land ice: mean 20.4% main, 17.6% C1; max 37.3 / 33.5.

Regional read-outs (late means over 600-1000 Myr, median of the paired differences, draws where C1 is higher):

| measure | main | C1 | median C1 - main | C1 higher |
|---|---|---|---|---|
| steppe (Koppen BS) tree cover, % | 14.1 | 12.4 | **-1.5** | **1/12** |
| tropical wet-dry (Aw) tree cover, % | 56.7 | 54.3 | -1.4 | 3/12 |
| steppe herb cover, % | 23.6 | 23.8 | -0.2 | 6/12 |
| Aw herb cover, % | 11.4 | 12.2 | +1.1 | 7/12 |
| land herb cover, % | 10.9 | 10.2 | -0.2 | 6/12 |
| land tree cover, % | 39.9 | 39.5 | -1.9 | 5/12 |
| wet equatorial tree cover, % | 66.0 | 66.5 | +1.2 | 7/12 |
| arid land, % | 22.6 | 21.5 | -1.2 | 5/12 |
| hot desert, % | 7.9 | 7.0 | +0.8 | 6/12 |
| lowest latitude with land ice, deg | 31.1 | 25.3 | -5.6 | 5/12 |
| weathering plant factor (w_plant) | 2.333 | 2.329 | -0.016 | 4/12 |

- **The one consistent signal is fewer trees on the steppe** (lower on 11 of 12 planets, -1.5 points of ~14) and,
  less firmly, in the savanna country (9 of 12, -1.4 points of ~57). That is the expected direction: the lower fuel
  floor lets grass fires burn where they did not, and fire keeps trees out of grassland. It is small.
- Wet tropics, arid land, hot desert, rain and the weathering's plant factor do not move beyond the coin-flip.
- Herds: not in the run records (the herd model runs on worlds, not in the run), so only the Earth figures above.
- **Yardstick** (`tools/yardstick.py`'s learnt y, which YARDSTICK is the mean of; `ycmp.py`): main 1.335, C1 1.344
  on the 12, shift +0.009 (se 0.035). No re-fit of earth.YARDSTICK is called for.

The screen is clean, so the full judge follows.

## 3. Full paired judge (36 L6 draws, 2 rolls x 18)
The C1 arm is the screen's 12 runs plus the other 24, run the same way (`screen.sh` on `full_draws.txt`, 6 at once,
1 thread). main is lane 181's kn arm. The mi arm ran all 36 too (for the grass read-outs) and again reproduces main
exactly on 36 of 36. Read-outs: `tools/judge.py paired` and `tools/hard_bar.py` on the symlink roots `pj/`,
`hb_main/` and `hb_c1/` (`hb.sh`), and `ana.py` / `tails.py` in the scratchpad. The base arm reproduces lane 181's
KN column (sd 1.25, 31/36, peak ice 16.4 / 37.3).

### The bar: passes
| check | main | C1 |
|---|---|---|
| hard: frozen over at the end (PW-1425) | 0/36 | **0/36** |
| (old rule, 40%+ at some moment of 884-1000, reported) | 0/36 | 0/36 |
| (40%+ at some moment after 300 Myr but not at the end, reported) | 0/36 | 1/36 |
| hard: boiled / hellhouse | 0/36 | 0/36 |
| hard: ocean loss | 0/36 | 0/36 |
| hard: CO2 crash (below the plants' compensation point) | 0/36 | 0/36 |
| soft pass (bar + finish moment) | 31/36 | **34/36** |
| late dT outside -6..+5 C of today's Earth | 0/36 | **0/36** (range -0.93..+4.58) |
| peak land ice in 884-1000, mean / max | 16.4 / 37.3% | 15.0 / 33.5% |

McNemar on the soft pass: both 30, main only 1, C1 only 4, neither 1; exact p 0.375, so within chance of main.
Secondary, reported: CO2 under 100 ppm 1/36 main, 0/36 C1. An 8-fold CO2 fall in 50 Myr or less (end at most 1/4 of
the level before the fall): 26/36 main, 20/36 C1; (end at most 2x the bottom of the fall): 24/36 main, 18/36 C1. End
pCO2 outside 180-600 ppm: 11/36 main, 17/36 C1. The one draw over 40% after 300 Myr is r0.001 l6c_m 958504 (44.5%
before the window, 6.3% at the end), seen in the screen.

Lane 140's failure does not come back. Under the old worst-moment rule C1 has 0 draws over 40% in the window here,
where lane 140 had 2 on pre-D47 main (and 3 points of margin is still thin: C1's highest window peak is 33.5%,
main's 37.3%). The C1 arm's coldest draw is -0.93 C against main's -1.46.

### The centre: unchanged within the chaos
Paired C1 - main over the 36 draws (judge medians, 95% CI): late dT +0.53 C [-0.30, +1.09], end T +0.92 C
[-1.35, +2.01], late CO2 +0.04 e-folds [-0.03, +0.13], sink reference +0.008, arid +0.4 points [-1.1, +1.7],
land rain +14 mm [-38, +54]. None moved (sign p >= 0.24). Mean late dT +1.44 C main, +1.66 C C1 (mean paired
difference +0.22, sd 1.53). If anything the lean is warm, not lane 140's cold push; it is inside the chaos either way.

**Trees moved: -1.8 points of land tree cover** [-3.3, -0.5], lower on 25 of 36 (sign p 0.029), the same -1.8 lane
140 measured. The read-outs below say where.

### Regional read-outs (late means over 600-1000 Myr, median of the paired differences, draws where C1 is higher)
| measure | main | C1 | median C1 - main | C1 higher |
|---|---|---|---|---|
| **steppe (Koppen BS) tree cover, %** | 14.0 | 11.9 | **-2.0** | **4/36** |
| tropical wet-dry (Aw) tree cover, % | 56.3 | 55.1 | -1.0 | 10/36 |
| steppe herb cover, % | 22.8 | 23.9 | +0.3 | 19/36 |
| Aw herb cover, % | 11.2 | 11.7 | +0.0 | 19/36 |
| land herb cover, % | 11.5 | 11.4 | +0.2 | 20/36 |
| land tree cover, % | 40.8 | 39.9 | -1.8 | 11/36 |
| wet equatorial tree cover, % | 66.5 | 66.4 | -0.1 | 17/36 |
| arid land, % | 23.2 | 23.7 | +0.3 | 20/36 |
| hot desert, % | 8.2 | 8.3 | +0.5 | 20/36 |
| land rain, mm/yr | 1130 | 1145 | +14 | 19/36 |
| lowest latitude with land ice, deg | 33.8 | 29.6 | -0.5 | 18/36 |
| global mean T, C | 14.6 | 14.9 | +0.7 | 20/36 |
| weathering plant factor (w_plant) | 2.355 | 2.326 | **-0.035** | **7/36** |

- **The steppe loses trees** (lower on 32 of 36 planets, -2.0 points of 14), and the savanna country less so (26 of 36,
  -1.0 of 56). The herb cover there does not fall. This is what a lower fuel floor should do: grass fires now run where
  the fuel sat just under 250 g C/m2, and fire holds trees back in grassland. It is the source of the land's -1.8.
- **The weathering's plant factor falls slightly** (-0.035 of 2.36, lower on 29 of 36): rooted cover thins a little,
  as the Earth check said (-0.5% over land). It is a weaker weathering, so a warm push, and small: the late dT
  centre does not move beyond chance. The yardstick's learnt y moves +0.012 (se 0.030, `ycmp.py`): no re-fit.
- Wet tropics, arid land, hot desert, sea ice and the ice edge do not move.
- Herds: not in the run records (the herd model runs on worlds), so only the Earth figures in section 1.

### The spread across planets: kept
| late dT over the 36 draws | main | C1 |
|---|---|---|
| sd between draws | 1.25 C | **1.26 C** (D47 bar: about 1.3-1.7) |
| range | -1.46..+4.33 | -0.93..+4.58 |
| 10th / 25th / 50th / 75th / 90th percentile | -0.27 / +0.66 / +1.30 / +2.61 / +2.78 | +0.23 / +0.75 / +1.75 / +2.49 / +3.14 |
| interquartile range | 1.95 C | 1.73 C |
| mean distance from the median | 0.99 C | 1.01 C |
| within-seed sd (re-runs of one planet) | 1.31 C | 1.25 C |
| draws colder than -1 C / warmer than +3 C | 1 / 3 | 0 / 4 |
| hottest / coldest single late step | +11.1 / -9.8 | +9.5 / -7.8 |

The sd is the same as main's (1.26 against 1.25), just under the bar's 1.3-1.7 band, as main's own is since KN.

### Verdict
C1 passes the D47 bar: 0 hard failures, soft pass 34/36 against 31/36 (p 0.375), every late dT inside -6..+5 C,
and the spread kept (sd 1.26 C against main's 1.25). The climate's centre does not move beyond chance. What C1 is
for does move: on Earth's observed climate the world's grassland grows what Yang et al. 2020's fit says, savanna NPP
falls 15%, and land NPP goes from 64.4 to 60.0 Pg C/yr (observed about 56). In the runs the steppe and savanna
country hold a little fewer trees (fire), and nothing else moves. Lane 140's strike-1 failure was chaos at a thin
margin on pre-D47 main. With D47's cover-based weathering and end-of-run frozen rule, it does not recur.

Open, not fixed here:
- Earth's herds now sit about 0.75x Coe et al. 1976's parks at the same rain (550-700 mm: 3.07 against 4.0-4.4 t/km2),
  as lane 140 found. The plants are now right on the field data, so the gap is in the herd fit (PW-1261 carries it).
- Grassland and savanna NPP are still above MOD17 and Miami (465 vs 292/338, 632 vs 501/583): those are whole-stand
  NPP including the trees in those cells, and the herb layer itself matches Yang. Not chased (Earth is a plausibility
  anchor).
- The fast CO2 falls counted by the secondary measure dropped (26 -> 20 of 36) and end pCO2 outside 180-600 rose
  (11 -> 17). Both reported, not part of the bar, and paired over the same draws they read as the chaos.

## Tests, Earth check, scorecard
- `test_golden.py --update-golden`: `sim_L4_s1_60myr.json` rewritten (the plants feed the climate and erosion), then
  2 passed without the flag.
- `pytest -n 4 -m "not slow"` (golden deselected, NUMBA_NUM_THREADS 4): 1008 passed, 1 skipped, 2 failed. Both pass
  on main.
  - `test_vegetation.py::test_npp_and_types_on_ideal_climates` failed on `(cover[de] < 0.3).all()`: 2 of the 107
    "desert" cells (24 C, 40 mm) reached 0.30-0.41 cover. Those cells sit at up to 67 S, a hot desert climate at
    polar daylight. With weaker grass, the soil-crust ground type takes 70% of the worst one. The rainforest and boreal
    checks already pick their cells by a latitude band. Harness fix: the desert cells are taken from |lat| < 45, with
    the assertions unchanged. The file's 14 tests pass on this branch and on main.
  - `test_rifts.py::test_rifts_leave_no_continental_slivers` fails: one rift on the L4 seed-1 run leaves a 2.4%
    continental piece (floor 3%). C1 only changes that run's coastlines. Not loosened, not fixed here: draft
    `draft-rift-sliver-test-fails-after-c1.md`. **It is still failing on this branch.**
- Climate-area slow tests (`test_envelopes.py`, `test_sea_level.py`, `test_co2_stock.py`, `-n 4`): 29 passed.
- `tools/earth_check.py` (L6): Koppen main group 71%, exact code 37%, log-rain correlation 0.718, global mean T 13.9 C
  against NCEP's 14.0. The same as main (round2.md).
- `tools/scorecard.py`: line appended (commit b8f97459). Earth: group 71.4%, exact 37.4%, rain correlation 0.718, the
  same as main. Seed 1 at 1000 Myr: ice 4.1%, trees 42.6%, land NPP 484 (lane 181's KN line: 2.7%, 39.9%, 394).
  Seed 2: ice 1.3%, trees 34.4%, NPP 470 (KN: 1.8%, 49.5%, 576). These are single seeds, inside the re-run chaos.

## Status
Done: Earth check, rooted-cover check, 12-draw screen, full 36-draw judge, tests, Earth check, scorecard. Verdict:
passes the D47 bar. One test still fails on the branch (the rift sliver test, draft filed): the coordinator decides
whether that blocks the merge. Scratch kept: `l185/judge/` (the c1 and mi arms, 72 runs), `ana.py`, `tails.py`,
`ycmp.py`, `sel.py`, `screen.sh`, `hb.sh`, `judge36.txt`, `npp/`, logs. Code copies, symlink roots and the run data
root removed.
