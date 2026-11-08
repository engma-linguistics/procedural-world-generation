# PW-290 scout 1: is L7 still drier than L6?

Scout 221, 2026-11-08, main `c2e54f2b`. Pass 1 of at most 3: diagnosis first.

## In plain words

**The 10-point gap is gone, and was fixed on 10-16, the day after the ticket was filed.** The cause was the old
rain kernel: it moved the air's water one cell per step, so on a finer grid the water travelled half as far
in kilometres before raining out and the land interiors at L7 got about a quarter less rain than at L6. PW-015
stage 1 (commit `14165233`, 10-16) rewrote the kernel to carry the water in real time and real distance; its
commit message lists PW-290 but the ticket was never updated. I re-checked it three ways:

1. **Same ground, both levels, current main.** On nine moments from five stored L7 runs, I computed the climate
   on the L7 grid and on the L6 grid for exactly the same terrain. L7 has **0.8 points more arid land on
   average** (range +0.5 to +1.1), and its land is **slightly wetter** (+0.2 to +1.8% land rain). On the code of
   the 10-15 health sweep (`6926583`), the same test gives **+6 to +8 points** with **26-28% less land rain** at
   L7: the ticket's gap, reproduced on the ground of today's runs.
2. **Which commit closed it.** The commit just before PW-015 stage 1 (`1b2f0800`) still has L7 land 17% drier
   than L6 on that ground; the merge (`f0197064`) has it 3% wetter.
3. **Whole runs, same seed at both levels** (seeds 3199 and 21, 1 Gyr, current main): RESULT_SHORT

What is left, about one point of arid land on the same ground, comes from relief the finer grid can see: an
L7 cell's rain varies about 30% more within each L6 cell's area, the extra arid cells sit on rougher, higher
ground (rain shadows of ridges L6 averages away), and Köppen's arid line is a threshold, so a wider spread of
rain around the same mean puts more cells under it. That is resolution showing real terrain, not a
level-dependent constant, and it is smaller than the spread between seeds. **I recommend closing PW-290**
(after the coordinator reads the pair table below), with one guard test so the gap cannot come back silently.
No fix, no screen and no sweep were run: there was no clear candidate worth a screen.

## 1. What changed since the ticket

PW-290 (filed 10-15, health sweep on `6926583`): Köppen B 28-30% of land at L6 against 38-42% at L7 for
seeds 3199, 21 and 11, tree cover 7-9 points lower at L7.

Since then:
- **PW-015 stage 1** (`14165233`, 10-16): the rain kernel carries vapour through cell faces in physical time
  (upwind flux plus eddy mixing, a CFL time step), replacing a per-step neighbour shuffle whose reach was a
  fixed number of cells. Its commit message: generated planet, L7/L6 land rain at shared cells 0.83 -> 1.02;
  Earth L6/L7 B 20.3/24.5 -> 18.1/17.9%.
- **PW-247** (`3da7ca1f`, 10-29): an L7 run computes its climate on the nested L6 grid
  (`Params.climate_level` = 6, `nest.climate_coarse`) except in the 10 Myr finish window, where it uses L7
  itself. So an L7 run's keyframes before the finish window show an L6-computed climate prolonged onto L7
  ground; only the finish window and the worlds sliced from it show the L7 climate. Any whole-run median of an
  L7 run over 50-1000 Myr is therefore mostly the L6 climate model on L7 terrain.
- **Lane 92** (`docs/review/v1-cut/checks.md` §4, code `e5b526ff`, 10-30): 6 L6/L7 pairs, median arid
  difference +2.1 points, sign mixed (L7 drier in 4 of 6). Those medians were taken over 50-1000 Myr, so after
  PW-247 they mostly compare the L6 climate model on two different terrains; they don't test the L7 climate.

## 2. Same ground, two levels (the clean test)

Harness: `pair.py` (in the scratchpad, copied below in short). For a stored L7 run's keyframe (read only), the
terrain and land ice go into `climate.compute` on the L7 grid, and into `nest.climate_coarse(g7, 6, ...)`, which
is exactly what an L7 run's spin-up does: the ground restricted to L6, the climate computed there and brought
back to L7 with each cell's own height through the lapse rate, the water balance and Köppen on the L7 cells.
No vegetation feedback (both cold), dT from the keyframe. Arid = Köppen B over ice-free land.

Baseline for each row: the same ground's climate computed on the L6 grid, same code (`c2e54f2b`).

| run (L7) @ Myr | dT | B % L7 / L6-nest | diff | BW % L7 / L6 | land rain mm L7 / L6 | PET mm L7 / L6 | land T diff |
|---|---|---|---|---|---|---|---|
| a19366 @ 200 | -0.5 | 35.7 / 34.9 | +0.8 | 28.2 / 27.1 | 895 / 893 | 1017 / 1014 | +0.06 |
| a19366 @ 600 | +0.4 | 29.5 / 28.7 | +0.8 | 16.3 / 15.2 | 1107 / 1099 | 1028 / 1027 | +0.03 |
| a19366 @ 900 | +2.8 | 23.1 / 22.3 | +0.7 | 12.3 / 11.9 | 1188 / 1173 | 1000 / 998 | +0.03 |
| 10fd90 @ 500 | -4.9 | 21.7 / 20.7 | +1.0 | 11.6 / 10.5 | 1128 / 1117 | 1010 / 1007 | +0.06 |
| 10fd90 @ 1000 | -1.8 | 23.6 / 23.1 | +0.5 | 11.0 / 10.2 | 1230 / 1209 | 1062 / 1060 | +0.01 |
| fe954c @ 400 (land-heavy) | +0.5 | 25.4 / 24.8 | +0.6 | 17.0 / 16.4 | 988 / 979 | 956 / 955 | 0.00 |
| fe954c @ 800 (land-heavy) | 0.0 | 29.0 / 28.0 | +1.0 | 20.7 / 19.9 | 1064 / 1058 | 1018 / 1016 | +0.03 |
| c9f38c @ 700 (cold preset) | -8.6 | 22.3 / 21.3 | +1.0 | 10.4 / 9.4 | 1173 / 1163 | 967 / 964 | +0.09 |
| 5aa5ff @ 600 (hothouse) | +5.2 | 19.5 / 18.4 | +1.1 | 11.0 / 10.1 | 1412 / 1409 | 1322 / 1319 | -0.04 |
| **mean** | | | **+0.84** | | **+0.9%** | **+2 mm** | **+0.03** |

PET and temperature don't depend on the level at all (within 3 mm and 0.1 C). Land rain is level-independent
in the mean (L7 0.2-1.8% wetter). The arid excess is under one point in every case.

A pure L6 grid (the ground point-sampled at the L6 cells, as an L6 run would see it, `old.py`) gives the same
answer on current code: a19366 @ 600 B 29.5 (L6) / 29.5 (L7), fe954c @ 800 28.4 / 29.0.

### Where the last point comes from (`fields.py`)

Both fields restricted to L6 (area means over land) agree closely: correlation of log land rain 0.993-0.998.
The differences are inside the L6 cells:
- the spread of rain among the L7 cells within one L6 cell's area is 60-105 mm against 46-75 mm for the
  prolonged L6 field (+30% on average): L7 resolves ridges and valleys that L6 averages away;
- the cells that are arid at L7 but not at L6 mostly sit on rougher ground: their median relief to their
  neighbours is higher than all land's in 6 of the 9 cases (e.g. 287 against 131 m, 309 against 225, 282
  against 178), about equal in 1 and lower in 2 (175 against 194, 173 against 200);
- on the roughest quarter of land, L7 rain is 1-4% below the L6 field; on the smoothest quarter 0-2% above;
- arid share by relief quartile: L7 is higher in every quartile, most in the roughest (e.g. 5aa5ff: Q4
  27.1 against 25.0; a19366 @ 600: 30.6 against 29.2).

Köppen's arid line is a threshold on each cell's rain against its temperature, so a wider spread of rain about
the same mean puts more cells below it (and a few above: L7 also loses 0.4-0.7% of land from B). The net is
newB 1.1-1.7% against lostB 0.4-0.7%.

This is resolution showing real relief (lee sides of ridges L6 can't hold), not a constant tied to the grid.
Earth's own deserts behind narrow ranges are more extreme than a 120 km grid can show.

### Reproducing the original gap on today's ground (`old.py`, `bisect.sh`)

Same harness, run from frozen copies of `planet/` at older commits (`git archive`), on the ground of a19366 @
600 and fe954c @ 800; pure L6 against L7 on the same point-sampled ground. Land mask: ground above sea level
without ice (older code has no `geo.is_land`).

| code | a19366 @ 600: B % L6 / L7 | land rain L6 / L7 | fe954c @ 800: B % L6 / L7 | land rain L6 / L7 |
|---|---|---|---|---|
| `6926583` (10-15, the health sweep's) | 32.1 / 38.3 (+6.2) | 907 / 650 (-28%) | 37.8 / 45.7 (+7.9) | 805 / 599 (-26%) |
| `1b2f0800` (10-16, just before PW-015 stage 1) | 21.5 / 23.8 (+2.3) | 1043 / 861 (-17%) | | |
| `f0197064` (10-16, PW-015 stage 1 merged) | 19.3 / 18.3 (-1.0) | 1185 / 1218 (+3%) | | |
| `c2e54f2b` (today's main) | 29.5 / 29.5 (0.0) | 1091 / 1107 (+1.5%) | 28.4 / 29.0 (+0.6) | 1056 / 1064 (+0.8%) |

(The absolute B levels differ between commits because a great deal else changed; the L6/L7 difference at each
commit is the comparable number.) Between `6926583` and `1b2f0800` other rain changes on 10-15/16 (PW-266's
land recycling among them) already took the gap from about 7 to about 2 points; PW-015 stage 1 took the rest.

## 3. Whole runs, same seed at both levels

### Stored L7 runs across the switch to their own-level climate (`switch.py`)

Each stored L7 showcase run (code of 11-01, before several climate merges, so indicative only) switches from
the nested L6 climate to the L7 climate at the start of its finish window. The arid share at the last coarse
keyframe against the first fine one (baseline: the same run 2.5 Myr earlier, L6 climate):

| run | B % at last L6-climate keyframe | first L7-climate keyframe | step |
|---|---|---|---|
| a19366 (988 -> 990.5) | 24.3 | 24.5 | +0.2 |
| 10fd90 (1488 -> 1490.5) | 27.9 | 28.6 | +0.7 |
| fe954c (988 -> 990.5) | 28.9 | 30.3 | +1.4 |
| c9f38c (988 -> 990.5) | 23.2 | 23.9 | +0.7 |
| 5aa5ff (988 -> 990.5) | 17.0 | 17.4 | +0.4 |

The step is the same size as the same-ground test's +0.84 (it also includes 2.5 Myr of drift and the
vegetation's feedback); the drift within each run's last 25 Myr is as large.

SIMS_SECTION

## 4. The candidates from the brief, ranked

| candidate | verdict | evidence |
|---|---|---|
| rain kernel transport per step and grid scale (PW-304, PW-019) | **was the cause; fixed** by PW-015 stage 1 (`14165233`) | §2 bisect: L7 land rain -17% before, +3% after |
| rain-shadow / orographic scale | the remaining ~0.8 point; physical (resolved relief), not a constant | §2 relief quartiles, within-cell spread |
| river and runoff routing | not involved: Köppen and land rain don't read the routing | Köppen reads only T and rain (`climate.koppen`) |
| PET or temperature lapse | not involved | PET within 3 mm, land T within 0.1 C at every moment |
| level-dependent constants in `planet/climate.py` | none that move land rain; one hop-count term found, in the currents (below) | grep of `climate.py`; §2 |

One level-dependent term turned up in passing: `climate.currents` limits the "nothing flows into a coast" band
by hops (`bfs_within(..., 8)`, `near = hops <= 2`): 240 km at L6, 120 km at L7. It touches the coastal
currents, not the land's rain; the same-ground test above shows no effect worth chasing on land climate. Not
filed (no visible harm found).

The ice and plants are not in the same-ground test (both cold, no vegetation feedback). The whole-run pairs in
§3 include them.

## 5. Recommendation and next pass

- **Close PW-290** once the coordinator accepts §3's pairs: the gap the ticket describes is reproduced on old
  code and absent on current code, and the cause is named.
- **Guard (draft filed):** a slow test that computes one generated ground's climate at L7 and on the nested L6
  grid and asserts arid share within 2 points and land rain within 5%. On `6926583` this test would have read
  +6 to +8 points and -27%, so it catches the failure the ticket describes; today it reads +0.5 to +1.1.
- Pass 2 is not needed for PW-290. If the owner wants the last point removed, the honest lever is not the rain
  but how Köppen is read at a finer grid (it is a per-cell threshold; L7 shows real rain shadows). I would not
  do it: it would make L7 look like L6 by blurring what L7 resolves.

## Files

- This write-up. Harness scripts (scratchpad, deleted at the end; the logic is described above):
  `pair.py` (same ground, L7 vs `nest.climate_coarse` L6), `fields.py` (field diagnosis), `old.py` +
  `bisect.sh` (frozen older code), `switch.py` (arid share across a stored L7 run's finish window),
  `simpairs.py` (whole-run pairs from `tools/ice_diag.py` outputs).
- Runs read (read only): a19366, 10fd90, fe954c, c9f38c, 5aa5ff.
- Sims: `tools/ice_diag.py --seed {3199,21} --myr 1000 --level {6,7}`, in memory, outputs under
  `exports/scout221/` (deleted at the end).
