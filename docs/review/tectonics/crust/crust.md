# Lane 23: thin continents after the rift fixes (PW-970) and shelves (PW-950), 2026-10-28

## PW-970: why the area thermostat didn't answer
An area budget per process (`areadiag.py`: continental cells gained or lost, in L5 cells, per 20 Myr, plus the
thermostats' state) on L5 seeds 1-2, 400 Myr, on main and on the pre-rift-fix code (4f27750e^1):

| L5 seed 2, 380-400 Myr | resolve | subduction erosion | stretch (margins) | coherence welds | shreds | net |
|---|---|---|---|---|---|---|
| main | -94 | -266 | +98 | **+773** | -570 | +24 |

- The biggest area source was not the rifted margins. It was `crust.coherence`'s **welds**: +200 cells net per
  20 Myr against the margins' +98. At that point 26% of the continental crust was thinner than 20 km, the area
  thermostat's shrink factor was x4.4, and its integral still climbing. The pre-rift code had the same pattern,
  smaller (seed 2: 29.6 km at 400 Myr). The rift fixes added rifting and coastline, so the welds grew.
- 56% of the welded cells had been continental on the world grid the step before. The world grid samples each
  moved plate at its nearest cell, so a sampled coastline jitters by a cell from step to step. Where it jittered
  outward, the gap was welded, and the weld wrote continental crust into the plate's own ocean cell. The plate's
  continental cell that the world grid had shown there before stayed on the plate. So every outward jitter grew
  the plate's continent by a cell. The reverse (a thick spike) is never removed, since shreds are only
  < 20 km. This is a ratchet, and it runs with coastline length in cells: it is level-dependent (PW-749).
- 80% of the welds were holes among thin (< 20 km) margin cells. The weld filled them from those neighbours
  and kept the hole's own crust (10-13 km on average, mostly old shreds), as continental. Shreds and welds
  cycled the same thin margin crust, with a net gain in area.
- The volume half is separate and older: volume / target is 0.91-0.93 at L5 400 Myr on both main and the
  pre-rift code, with the arc thermostat at x2.3-3.0. Subduction erosion, the area thermostat's lever, removes
  ~21 km of crust per cell of area it takes. Draft: `draft-crust-volume-thermostat-shortfall.md`.

## The fix (a607c614)
A weld now needs (crust.coherence, `_inlet_on_plate`):
1. the inlet on the plate itself: its cell on the plate's own grid has all but 2 of its owned neighbours on
   that grid continental, the same count as on the world grid;
2. the crust around it to be continental by the model's own measure: the neighbours' mean is at least
   BECOMES_CONT_KM (20 km). That is the bound for a cell born continental, and the shred rule's bound.

Single-seed tries (L5 seed 2, 400 Myr; thickness km / continental area %): main 27.7 / 45.9; rule 2 only
31.2 / 42.1; rule 1 only 31.4 / 41.3; both 32.4 / 41.1, thin < 20 km 26% -> 5.6%, welds 773 -> 114 per 20 Myr.

Also in a607c614: `Simulation._climate` recomputes the world view's elevation at the new sea level instead
of shifting it. The result is the same up to rounding. But `test_state`, resuming from `state()`, rebuilds it
the recomputed way and caught a last-bit difference on this branch's trajectory. A checkpoint taken after a
climate update would not have resumed bit for bit.

Tests: `pytest -m 'not slow'` 700 passed; `test_envelopes.py` 10 passed, 1 skipped (Earth data). L5 400 Myr:
seed 1 29.4 -> **34.0 km**, seed 2 27.7 -> **32.8 km**. The PW-970 xfail is removed; the 28 km floor stands.
`test_churn` passes. Golden `sim_L4_s1_60myr` updated (an intended change).

## PW-950: water-loaded isostasy (round 1, failed)
The ticket's premise has the sign backwards. A continental column whose surface lies below the sea carries
water on top, not air. Each km of crust thinned then sinks it by (rho_m - rho_c) / (rho_m - rho_w) =
0.5 / 2.27 = 220 m, not 150 m. Water loading deepens a drowned margin by rho_m / (rho_m - rho_w) = 1.45 x its
air-loaded depth (the standard air- to water-loaded conversion of tectonic subsidence, e.g. Allen & Allen,
*Basin Analysis*). The model's continental isostasy (ISO_LAND, SAG_KM "air-loaded") is air-loaded.

Tried anyway (`wl.py`: every continental cell below sea level x 1.454), on the branch code, L6 seed 1:

| t (Myr) | shelf %, air | shelf %, water | submerged median (m), air | submerged median (m), water |
|---|---|---|---|---|
| 200 | 0.75 | 0.46 | -766 | -1105 |
| 300 | 2.16 | 1.71 | -875 | -1135 |
| 400 | 0.87 | 0.98 | -997 | -1369 |

Water loading is deeper at every sample, and shelves are lower in 6 of 8. The sea falls 50-230 m as the
basins deepen, but that doesn't make up for it. It is the correct physics, so leaving the model air-loaded
flatters the shelves, but it is not a fix. Not kept.

Why shelves are still few:
- Drowned continental crust is mostly the stretched edge at the 22 km floor (`crust.stretch`, -1.4 km
  air-loaded) and margin rings at 12-18 km (-2.3 to -3.4 km).
- Earth's shelves stand on crust of beta ~1.2-2 too. They are held at sea level by sediment wedges 5-15 km
  thick, built over ~100 Myr (Steckler et al. 1999, already cited in surface._offshore).
- Filling d m of water takes ~(rho_m - rho_w) / (rho_m - rho_s) ~ 2.3 d of sediment: ~3 km for a cell at the
  stretch floor.

Suggestions (in PW-950, moved to v2):
1. A tapered stretch. Thinning should fall off away from the rift axis (a necking zone 50-200 km wide), so that
   the inner margin cells keep 27-33 km and sit within a few hundred m of sea level. Today one cell jumps from
   35 to 22 km.
2. Measure the sediment delivered to the shelf brink per km of margin against the ~2.3x-depth fill. Lane 19
   asserted supply isn't the limit but didn't measure it.
3. Planation at wave base. Shelves are flattened at ~-130 m by lowstands; there is no such process now.
4. If the model ever goes water-loaded (it should, for honesty), do 1-2 first.

## Paired judge (L6 1 Gyr, v1-finish-16's 18 draws x 2 rolls, `paired.sh`; main 0c4e17c8 vs branch a607c614)
| roll | main | branch | main icebox | branch icebox | hellhouse |
|---|---|---|---|---|---|
| +0.0005 | 15/18 | 15/18 | 5/18 | 5/18 | 0 / 0 |
| +0.001 | 16/18 | 13/18 | 3/18 | 5/18 | 0 / 0 |
| pooled | **31/36** | **28/36** | 8/36 | 10/36 | 0 / 0 |

Paired: both pass 25, main only 6, branch only 3, neither 2. That is 78% against 86%; both are above the
~70% bar. A 6-to-3 split over 36 paired draws is within chance (a sign test gives p ~0.5), but it leans one
way. All 6 of the branch's lost draws fail as **too warm** at the finish moment (+4.8 to +11.1 C). The
branch's median end temperature is +0.85 C against main's -0.05 C, and 7 draws are over +3 C at the moment
against main's 3. Land rises from 31.3% to 34.8% (below). No SIM SUSPECT. Draft:
`draft-thicker-continents-more-land-warmer.md`.

## Crust and shelves in the paired set (`crustdiag.py` / `crusttally.py`: per draw the 600-1000 Myr mean, median over draws)
| arm | shelf % of ocean | submerged continent median (m) | continental crust (km) | continental % | land % | largest plate % | crust < 20 km (% of continent) |
|---|---|---|---|---|---|---|---|
| main | 1.58 | -1519 | 32.64 | 41.8 | 31.3 | 27.7 | 14.0 |
| branch | 2.10 | -819 | **34.24** | 41.3 | 34.8 | 26.3 | 3.6 |
| Earth at L6 | 5.8 | -184 | ~35-40 | ~41 | 29 | ~20 (Pacific) | |

At 1 Gyr: thickness 32.48 -> 33.91 km (median), largest plate 27.2 -> 25.6%. PW-950's criteria at 1 Gyr:
submerged median within -100..-500 m on 0/36 (main) and 2/36 (branch) draws; shelf >= 3% on 5/36 and 10/36.
The weld fix alone halves the depth of drowned continent: the thin welded margin cells were most of it.

## Scorecard (`tools/scorecard.py`, L6 seeds 1 2 at 1 Gyr; main = the a526fe7c line, lane 22's merged physics; Earth part skipped: no data in the worktree)
| seed | land % | continental % | shelf % of ocean | submerged median (m) | largest plate % (max over run) | volume ratio |
|---|---|---|---|---|---|---|
| 1 main | 29.7 | 42.2 | 2.8 | -1634 | 43.7 | 0.954 |
| 1 branch | 33.4 | 40.6 | 3.5 | -709 | 26.5 (54.4) | 1.009 |
| 2 main | 32.2 | 44.6 | 1.7 | -1623 | 21.0 | 1.003 |
| 2 branch | 33.1 | 40.9 | 3.0 | -751 | 22.0 (56.6) | 0.984 |

## Example runs (main checkout's store, L6 1 Gyr, `examples.sh`)
crust-main-s1 e37ccc, crust-new-s1 f7b8df, crust-main-s2 c9e85b, crust-new-s2 1d13bc.

## Harness
`areadiag.py` (area budget; `EXPF` patches coherence for tries), `crustdiag.py` (ice_diag plus crust fields
every 10 Myr), `crusttally.py`, `paired.sh` (as lane 22's, scratchpad l23/judge, skips draws with a log),
`wl.py` (the water-loading try), `examples.sh`.
