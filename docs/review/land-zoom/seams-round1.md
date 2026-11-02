# Land zoom seams, round 1: turned sections and matched neighbours (PW-1338, PW-1301; epic PW-1299)

Lane 127, 2026-11-02. Code: `planet/zoom/regional.py` (Frame.up, frame_of, up_of, zoom/build/save/zoom_id),
`planet/zoom/tiling.py::section`, `planet/zoom/match.py` (new), hooks in `stage_terrain.py`, `stage_landscape.py`,
`stage_finish.py`; viewer `zoom3d_place.js`, `zoom3d.js`, `zoom.html`, `globe/tabs.js`; `seams.py`. Tests
`tests/test_zoom_tiling.py`, `tests/test_zoom_match.py`. **State: PW-1338 done; PW-1301 mechanism built and checked on
small pairs; the judge on lane 116's practice pairs and a turned tiling pair (4 km/px), and the 1 km check, are NOT run
yet** (lane handed off at its tool budget; see "Next" at the end).

## In plain words

1. **Sections can now be turned** (PW-1338). `planet zoom WORLD --section px.1.1` builds the tiling's square for that
   cell, turned to the cube face's "up"; `--up DEG` turns any zoom. The orientation is saved in `zoom.json`
   (`center.up`, `projection.up`, `projection.up_bearing_deg`), the id differs from the north-up zoom of the same
   centre (north-up ids are unchanged), the corners turn with it, and the viewer (3D placement, the globe's outlines,
   the pixel lat/lon read-out) and `seams.py` read it. Pole cells (`pz.1.1`, `mz.1.1`) work (tested).
2. **Why neighbours disagree** (diagnosis below): almost all of the height mismatch is made by the **landscape pass**
   (stream-power grading on each zoom's own drainage), which is not local: a hillside's height depends on where its
   water leaves the square. Noise and coarse fields are already keyed by place. A smaller part comes from the
   **mean correction** near each square's edge, and coasts differ in ~0.3-1.5% of places.
3. **The fix: a section is built matched to its neighbours already built** (`--match ID,...`). Where the neighbour owns
   the ground, the new section takes the neighbour's coastline and finished heights and holds them through its
   landscape pass (its valleys run down to the neighbour's ground at the neighbour's levels); across an 80 km ramp
   inside its own ground the heights (and ice) blend from the neighbour's to its own, before its rivers are found;
   class layers (biome, vegetation, landform, soil, rock) switch at a ragged line across the ramp. The mosaic shows
   each place from the section that owns it, so the two meet where both are the neighbour's surface.
4. On small test pairs this takes the height jump at the owner line from 40 m to 0.1 m (desert edge) and from 435 m to
   14 m (ice-covered range, median); far inside, the section is unchanged.

## Diagnosis: where each seam mismatch comes from

Stage-by-stage attribution (`diag.py`, scratch harness: two zooms built with a snapshot of the height after every
stage, compared at the same sphere points of their 200 km shared band). Pairs of 1000 km squares at 4 km/px, centres
800 km apart, on lane 116's worst seams of dba204. Median |dh| on land both call land, m (p95 in brackets):

| after stage | range (66.0 N 145.0 W / 61.5 N 132.2 W) | desert edge (30.7 N / 23.5 N, 120 W) | plains (58.2 N / 51.0 N, 116.7 W) |
|---|---|---|---|
| detail (noise on the coarse surface) | 12.7 (305) | 2.0 (16) | 0.9 (9) |
| mean_correction | 32.8 (472) | 6.1 (30) | 2.4 (17) |
| landform_classes, coarse_rivers | 32.7 (475) | 6.1 (30) | 2.8 (20) |
| **landscape_loop** | **301 (1895)** | **51 (270)** | **8.1 (79)** |
| final (ice bed) | 310 (1972) | 51 (270) | 8.1 (78) |

Coast mismatch is set at the coastline stage and does not change after: 0.3% (range, desert), 1.5% (plains). These
reproduce lane 116's 4000 km numbers (range 300-480 m, desert 58 m, plains 7-20 m), so the small pairs are a fair
stand-in for iteration.

Sources, in order of size:
- **Landscape pass (non-local):** heights come from integrating stream-power slopes up the zoom's own D8 drainage from
  its outlets (sea, lakes, the region's edge held at the target) with C fitted per coarse cell. Two zooms have
  different pixel lattices (turned against each other, offset) and different outlets, so D8 routes differ and every
  hillside is graded from a different base. No amount of place-keyed noise fixes this; only a shared drainage (a
  planet pass, PW-1302's first option) or conditioning one section on the other does.
- **Mean correction (edge effect):** each coarse cell keeps its mean over the pixels the zoom has of it; a cell cut by
  the square's edge (or the halo) is corrected over a different set of pixels: 2x larger near the edge (edge<40 km:
  50 m vs 24 m in the range).
- **Detail:** small differences from pixel-space filters and the bilinear resampling of rough noise on two lattices
  (a floor any two rasters have: 1-2 m on plains, ~13 m in the range at 4 km).
- **Coast:** the coastline indicator is place-keyed, but the coarse fields under it come through zoom-local selection
  and smoothing; 0.3-1.5% of band points differ.
- **Biomes** differ 7-36% (lane 116) mostly because vegetation is per pixel on different terrain; resampling two
  speckled class rasters nearest-to-nearest alone gives ~6-7% (the floor measured in the held zone below).

## Candidates considered

1. *Key everything by place* (noise, seeds): already done for noise; does not touch the landscape pass. Rejected as the
   main fix.
2. *One planet-wide drainage at zoom resolution*: would make heights and rivers agree by construction, but a planet at
   1 km is ~500 M pixels of D8; far beyond one section's 110 GB. Left to PW-1302 to judge.
3. *Overlap and blend after the fact* (build each alone, cross-fade the shared band in the mosaic): cheap, but a
   300 m mismatch cross-faded over 100 km leaves ghost valleys and rivers that end in the fade.
4. **Condition on built neighbours (chosen):** order the sweep; each section holds its built neighbours' ground (and
   coastline) through its own landscape pass, and blends into its own across a ramp before its rivers and lakes are
   found. Deterministic for a given order; first sections are built alone.

## What was built (PW-1301 mechanism, `planet/zoom/match.py`)

- **Owner rule:** the tiling's cell (`tiling.locate`) when both are tiling sections, else the nearer centre (Voronoi).
- **Held ground:** pixels the neighbour owns and covers (with `VALID_PX` = 3 px and a `FADE_KM` = 20 km fade from the
  neighbour's own edge). Before the detail stage the coast indicator takes the neighbour's land/sea there (lakes count
  as land); before the landscape pass the height there is the neighbour's ground and those pixels join the region's
  edge as outlets.
- **Ramp:** `RAMP_KM` = 80 km into the section's own ground (the tiling's least margin is 97 km): heights blended at the
  start of the final drainage (rivers, lakes and falls are found on the blended ground), then the ground and the ice
  blended once more after the ice bed (the last stage that moves the ground); class layers switch where the
  neighbour's weight beats place-keyed noise (25 km fbm), a ragged line, not a straight seam.
- **Saved:** `zoom.json` `matched_to: [ids]`; the id includes them. `planet zoom ... --match ID,...`.
- A zoom built without `--match` runs no new code (outputs unchanged), except the glacial direction fix of PW-1338.

## Results on the small pairs (diag2.py: A alone, B alone, B matched to A, 1000 km @ 4 km/px)

Median |dh| (p95), m, land both call land; d = distance from the owner line into B's ground:

| pair | alone, at the line | matched, at the line | matched, held zone d = -50 km | matched, ramp d = +40 km | B moved, d 100-300 | B moved, d > 600 |
|---|---|---|---|---|---|---|
| desert edge | 39.6 (254) | **0.1 (19.5)** | 2.2 (27) | 15.5 (75) | 9.5 (99) | 0.0 (1.1) |
| ice range | 435 (1826) | **13.8 (948)** | 8.3 (62) | 139 (1031) | 9.7 (452) | 0.0 (0.0) |

Coast mismatch at the line: desert 0.4% -> 0.4% (to check: see Next), range 0 -> 0. Biome mismatch at the line: desert
12.5% -> 7.2%, about the resampling floor (6.6% in the held zone, where B's classes are A's). The p95 of 948 m at the
range's line is where the two north-up 1000 km squares are turned ~11 degrees against each other (64 N, 13 degrees
of longitude apart): near the line's ends A covers less than the ramp past the line, so its weight fades before the
line; tiling sections (shared orientation within a face, >= 97 km margins) don't have this wedge. Slope p95 in the
ramp is no higher than inside (desert 3.6 vs 3.7 deg, range 20.3 vs 22.5): the blend makes no steps.

## Goldens and outputs

- No golden changed (`tests/test_golden.py` covers the sim and climate only).
- Ordinary north-up zooms: same ids, same zoom.json keys, same code paths, **except the glacial landforms** (eskers,
  drumlins, loess): the ice-flow and wind directions were read as grid east/north; they are now turned into the grid
  per pixel (`terrain.en_to_grid`). Needed for turned and polar sections (where grid north can be anywhere) and a fix
  for north-up zooms too (grid north turns away from true north away from the centre). Glaciated zooms' streaks shift
  slightly.

## Next (for the lane that picks this up)

1. Judge at 4 km/px: rebuild lane 116's practice pairs (`planet zoom dba204 --lat .. --lon .. --size-km 4000 --res-km 4`,
   centres in practice.md), B matched to A (`--match A`), and one turned tiling pair, e.g. `--section px.1.1` then
   `--section px.2.1 --match <px.1.1 id>` (check land first: `tiling.sections(world)`); measure with `seams.py A B`
   (the band is found from the data now) and compare alone vs matched. `free -g` first; ~5-10 min each at 4 km.
2. Coast at the line (desert 0.4% unchanged): find which later stage redraws land (fjords, lake fix-ups, tides) in the
   held zone and hold it.
3. One 1 km check of the best pair (~16 min and ~86 GB per section per the brief; one at a time).
4. seams.py measures A vs B over the band; for matched pairs the meaningful numbers are at the owner line and the ramp:
   add an owner-line station (`seams.py` uses the bisector; for tiling sections use the cell edge).
5. Then PW-1302 (rivers across the line; notes in `issue-tracking/inbox/draft-land-zoom-matched-rivers-notes.md`).
