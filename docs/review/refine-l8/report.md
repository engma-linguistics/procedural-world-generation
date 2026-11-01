# Refining a finished L7 world onto L8 / L9 (lane 104; PW-490 first cut, PW-1198)

Written by the coordinator from the lane's report (the lane could not write report files). Design: [design.md](design.md).
Code: `planet/refine.py`. Tests: `tests/test_refine.py`.

## In plain words

It works. `planet refine <world> --level 8` takes a finished L7 world and remakes its present moment on the L8 grid. The
tectonic history stays L7's. Terrain, coasts, rivers, lakes, climate, soils, plants, resources and the rest are recomputed for
each L8 cell. The output is a normal world in the store, and the viewer opens it. L9 also works, but its file is too big for the
viewer (PW-1209).

- **World `fb5e11`** (`?world=fb5e11.json`) refines a fresh L7 world, `783674` (run `b13ee9`: seed 11, 100 Myr, current main):
  the same seed and age as the direct L8 world a16f5a, so counts compare but continents don't.
- **Cost:** the L7 route takes about 20-25 min in total (simulate 12, slice 2.2, refine 4.5-10 depending on load); the direct
  L8 route took 146 min (simulate 132, slice 14). Refine peak memory 10.8 GB (direct slice 17.7). Same file size, 440 MB
  (66 MB gzipped). The viewer opens fb5e11 in 5.3 s and turns at 60 fps, like a16f5a.
- **L9 (measurement only):** 38 min, 38.8 GB peak; 1.76 GB of JSON (229 MB gzipped) plus a 370 MB grid file; 3.3x Chrome's
  longest string, so the viewer cannot open it.
- **Where the L8 time goes** (266 s run): wave power 129 s, tides 39 s, the L7 climate 22 s, terrain 5 s. Wave power grows
  faster than the cell count, which is most of L9's 38 minutes.

## Comparison

| | L7 source 783674 | refined L8 fb5e11 | refined L9 | direct L8 a16f5a |
|---|---|---|---|---|
| Land | 34.9% | 34.9% | 34.9% | 34.0% |
| Coast cells | 4,150 | 10,053 | 20,522 | 11,734 |
| Coast length | 250k km | 302k km | 309k km | 353k km |
| River length at >= 1000 m³/s | 360k km | 393k km | 408k km | 381k km |
| Islands under 10k km² | 54 | 223 | 110 | 249 |
| Mid-sized islands (10k-100k km²) | 9 | 11 | 8 | 8 |
| Lakes (cells) | 35 (126) | 211 (1,597) | 288 (6,534) | 124 (1,944; 1,439 one salt lake) |
| Land draining inland | 3.5% | 7.8% | 7.3% | 9.5% |
| Shelf, % of ocean | 3.8 | 4.8 | 4.8 | 4.2 |
| Slope and rise, % of ocean | 5.3 | 9.2 | 7.1 | 5.0 (Earth 17.7) |

Each L7 cell keeps its mean height to within +1.8 m (spread 7.2 m) inland; the climate matches the source. Mid-sized islands
and the one-cell shelf-to-abyss drop are inherited from L7: refining cannot create the first or fix the second (PW-950). At L9
the coast hardly lengthens, because the L7 coastline still sets it. A regional zoom of fb5e11 works (zoom 361209, 49 s), and so
do its highlights.

## How it works

- **Terrain:** the regional zoom's coastline, relief noise and mean-keeping steps, run on the sphere, reusing the zoom's
  constants, noise seeds and ruggedness (moved into a shared `stage_terrain.ruggedness`).
- **Drainage:** the noise's closed hollows are filled except where the L7 world has lakes, closed basins or ground below sea
  level. Without this the L8 world had 30x the source's lake cells.
- **Geology:** each fine cell takes one L7 cell's rock column, with ragged boundaries.
- **Finish:** `world.finish` on the fine grid, with climate computed on L7 and brought down per cell by lapse rate
  (`nest.climate_coarse`).
- **Erosion default 0.1, not 0.3:** at 0.3 the land is lowered a second time (mean land 366 → 310 m; 347 at 0.1).

**Bug fixed on the way:** `nest.climate_coarse` copied each coarse cell's deep-water sinking onto every fine cell, so the
overturning read 142 Sv instead of 35. Runs never read that field, so run outputs don't change. Tested.

## Not done

The landform classes' own shapes (folds, rift blocks, mesas) and rain shadows smaller than an L7 cell (both tickets). A shared
detail-amplitude function for zoom and refine (about 40 duplicated lines) is a refactor awaiting a yes.
