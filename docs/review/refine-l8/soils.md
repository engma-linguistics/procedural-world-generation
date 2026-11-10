# Soils on a refined world (lane 274)

Daniel's split pipeline runs the settled history on an L8 refine of the L7 world, so a refined world's ground must not
change merely because the grid is finer. Lane 272b found Earth-like A's L8 refine poorer than its L7 world: fertile
class −11%, soil depth 1.31 → 0.99 m, peat over 0.5 m 31.5 → 40.1% of land. This note traces that gap and fixes it.

## In plain words
The L8 soils were thinner only because the finer grid sees steeper slopes between its closer cells, and the soils'
erosion rule was written for the slopes between L7 cells. The soils now read the slope at the L7 cells' scale on any
finer grid, as a zoom's pixels already do. Soil depth on the L8 refine is back to the L7 world's (1.43 against 1.42 m;
it was 1.09). The peat rise had nothing to do with the grid. The stored L7 world is older than today's plant code.
Re-finished with today's code, the L7 world has as much deep peat as the L8 one (43.8% against 44.1%). L7 worlds
don't change at all (all 185 layers are bit-identical).

## Where soil depth and peat are computed
- **A world and a refine run the same code.** `world.finish` calls `soils.mineral`, then `vegetation.model`, then
  `soils.organic` (world.py ~224–237). A refine (`refine.refine`) calls `world.finish` on the fine grid with the coarse
  climate brought down to it, so it has no soil path of its own.
- **Soil depth.** `soils._mineral` computes the erosion rate `E = E_MIN + E_STEEP (slope/30)^2 rain_factor + ...`
  with `slope = soils.cell_slope`. That is the relief to the steepest neighbour divided by `grid.spacing`. Depth is
  then `h = H0 ln(p0/E)`, capped by the soil's age. `slope < STEEP` (8 m/km) also gates till, alluvium and cracking
  clay, `SAND_SLOPE` gates blown sand, and drainage loses a class above `STEEP`.
- **Peat.** In `soils.organic`, `peat_c = npp × escape × sat × (1 − alluvial) / alpha × (1 − e^(−alpha × age))` wherever
  the flooded share `fw > 0`. Here `fw` is `vegetation.flooded`: floodplains, wet flats and permafrost flats. Each
  wet term is weighted by `flat = 1 − relief/400 m`, and that relief is in metres to the steepest neighbour, *not*
  divided by the spacing. The peat layer is `peat_c / PEAT_RHO`. `humanuse.fertile` halves the score where it is
  over 0.5 m.

## What depends on the grid
| quantity | where | how it scales on a finer grid |
|---|---|---|
| soils' slope (m/km) | `soils.cell_slope` | resolves rougher ground between closer cells: on 899985's L8 refine the land median is 3.9 m/km against the L7 world's 1.9; the erosion term `<(s/30)^2>` is 0.116 against 0.024 (4.7x) |
| relief (m) for the flooded share, floodplains and thin buckets | `vegetation.relief` (in `flooded`, `floodplain`, `model` → `site`) | closer neighbours: slightly *flatter* in metres (flat³ 0.359 against 0.336) |
| floodplain share of a river cell | `vegetation.floodplain` | a share of the cell, not a width in km: the river line covers half as much land at L8 (1.37% → 0.74% of land) |
| irrigated banks (q ≥ 100 m³/s) | `humanuse` fertile | the same line effect: 43.3% → 18.3% of land |
| climate, mi, NPP | coarse climate brought down | unchanged (at the coarse cells: rain +0.2%, NPP −0.8%) |

Measured with `diag_relief.py` (lane 274 scratch) on 899985 (L7, stored) and its L8 refine 730ed5 (main 6af71023). On
the coarse cells' own positions (fine cells 0..n7−1, land on both), the L8 neighbour slope is 2.09x the L7 one (median).

## Why peat rises: code drift, not the grid
Lane 272b compared the refine with the stored world 899985, which was finished on 8 Nov. The plant code has changed
since (PW-1518's two-leaf canopy, 9 Nov, and hydrology changes). Peat depth goes with NPP. On land with peat, NPP was
389 g C/m²/yr in the stored world and 602 in the refine (+55%), while mi, the saturation term, glaciation age and Sph
cover barely move. To separate the two causes, I re-finished 899985 on its own L7 grid with today's code:
`refinish_l7.py` is `refine.refine` with the identity for terrain and geology, the same 0.1 erosion pass and the same
records (world ed3e56). Its NPP on peat land is 659, and its deep-peat share is 43.8%, the same as the L8 refine's
44.1%. **So the peat rise is today's plant code, not the grid, and the right L7 baseline is ed3e56, not the stored
899985.** The relief term in `flooded` moves the other way and only a little (flooded share 6.2% against 5.8%).

## The fix: relief at the cell scale
`vegetation.cell_relief(grid, elev)` reads relief at the scale of one L7 cell, `CELL_KM` = 60.2 km, which is the L7
grid's mean neighbour spacing. A finer grid with k = round(CELL_KM / spacing) rings (2 at L8, 4 at L9):
1. averages its heights over one reference cell's footprint. One pass of (the cell + half of each neighbour) is
   exactly an L7 cell's footprint on the nested L8 grid: its centre cell and half of each of its six edge-midpoint
   cells. Finer levels take ~0.74 k²/4 passes, matching the kernel's variance.
2. takes the relief to the highest and lowest of those within k rings.

At L7 and coarser, k = 1 and the code is the old `relief()`. `soils.cell_slope` divides the result by k × spacing.
`vegetation.flooded`, `floodplain` and `model` (and through it `site`'s thin buckets) read `cell_relief`. This is the
same idea as `soils.zoom_slope` for zoom pixels: the thresholds stay in the cells' measure, and the finer ground is
converted to it.

Candidates on the L8 refine's terrain, against the L7 world:

| measure | slope p25 / p50 / p75 m/km | `<(s/30)^2>` | flat³ | median L8/L7 slope at coarse cells | log-corr |
|---|---|---|---|---|---|
| L7 world, own neighbours | 0.8 / 1.9 / 4.2 | 0.0244 | 0.336 | – | – |
| L8, own neighbours (main) | 1.5 / 3.9 / 8.6 | 0.1157 | 0.359 | 2.09 | 0.88 |
| L8, 2 rings, no averaging | 1.3 / 3.1 / 6.4 | 0.0564 | 0.237 | 1.54 | 0.95 |
| **L8, 2 rings, one footprint pass (chosen)** | 0.7 / 1.9 / 4.0 | 0.0221 | 0.328 | 0.95 | 0.98 |
| L8, 2 rings, two passes | 0.6 / 1.6 / 3.4 | 0.0160 | 0.356 | 0.81 | 0.97 |

## Result
Fresh refines of 899985 to L8 (seed 1, same machine), main (730ed5) and this branch (108b4f), against ed3e56 (899985
re-finished at L7 with today's code). For reference, the stored 899985 is also shown. Land = not sea, ice or lake.
Fertile class is the mean of `humanuse` fertile (0–4) over land, so its absolute values differ from lane 272b's mask.
"Within 60 km of the sea" is the land within 60 km, by graph distance, of a sea cell.

| | 899985 stored (8 Nov code) | **ed3e56 L7, main code** | 730ed5 L8, main | 108b4f L8, this branch |
|---|---|---|---|---|
| fertile class, mean over land | 1.051 | **1.003** | 0.952 (−5.1%) | 0.965 (−3.8%) |
| fertile class, land within 60 km of the sea | 1.765 | **1.797** | 1.478 (−17.8%) | 1.681 (−6.5%) |
| soil depth mean, m | 1.416 | **1.415** | 1.085 | 1.432 |
| soil depth p25 / p50 / p75, m | 0.81 / 1.45 / 2.07 | **0.81 / 1.45 / 2.06** | 0.20 / 1.00 / 1.77 | 0.82 / 1.46 / 2.08 |
| thin stony soil, % of land | 9.8 | **9.9** | 25.0 | 10.0 |
| peat over 0.5 m, % of land | 34.1 | **43.8** | 44.1 | 43.7 |
| flooded share, % mean | 6.37 | **6.20** | 5.79 | 5.58 |
| soil fertility mean | – | **0.354** | 0.379 | 0.337 |

ed3e56 rebuilt with this branch's code (473d9d) is bit-identical in all 185 layers, so L7 outputs don't change.

What is left of the gap is from other causes:
- **Soil fertility is −5% over land and −3% on the coarse cells' own positions.** The cell-scale slope reads 3% low
  there (median ratio 0.97, erosion term 0.97x), so soils are a little older and more weathered. Loess is 4.5% lower,
  because the outwash band beside glaciated cells is one cell wide.
- **Irrigated banks.** A river of 100 m³/s or more irrigates its own cells only. Its line covers 43% of L7 land and
  18% of L8 land. Without irrigation the class means are 0.972 (L7) and 0.951 (L8 branch), −2.2%. The banks are worth
  ~1.3 points of the 3.8%. This is humanuse, not soils: see the inbox draft.
- **Floodplain share.** A river cell's floodplain is a share of the cell, not a width, so it halves on L8. It is worth
  1.4% of L7 land as alluvium, which is too little to show in the means, but it is the same line problem.

Scripts, all in the lane's scratch and not kept: `diag_relief.py`, `measure.py`, `peat_trace.py`, `fert_decomp.py`,
`fert_what_if.py`, `alluv.py`, `refinish_l7.py`.
