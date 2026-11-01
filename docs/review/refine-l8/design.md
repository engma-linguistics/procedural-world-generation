# Refine a finished L7 world to L8/L9: design note (lane 104, PW-490 first cut)

Written before the code. The report (`report.md`) says what changed against this.

## Command
`planet refine <world> --level 8 [--erosion 0.3] [--no-resources]` -> a normal `worlds/<id>.json` on the finer grid
(`grids/L8.json`, already in the store), viewer-loadable as `?world=<id>.json`. Source: any tectonic world
(keyframe or finished time-zoom frame). The source is only read.

## Data flow (new module `planet/refine.py`)
The grids nest: fine cells `0..n7-1` are the L7 cells, the rest are edge midpoints (`grid._subdivide`, `nest.step`).

1. **Load** the L7 world (`world.load`). Fine grid `G = build_grid(level)`, `own = g7.locate(G.centers)`.
2. **Smooth fields** (heights, ice, vegetation cover, soil memory): a Gaussian kernel over the L7 cell centres round
   each fine cell (its own L7 cell and that cell's ring of neighbours, sigma half an L7 cell), with weights per
   field (land only, sea only) - the sphere version of the zoom's `ZK.gauss_interp` over projected centres.
3. **Terrain**, the zoom's terrain stages (`zoom/stage_terrain.py`) on the sphere, same constants and same noise
   seeds and planet-km positions, so a refined globe and a regional zoom of the same world share their large octaves:
   - coastline (`coastline`): land indicator at sigma 0.42 cell, domain-warped fbm (0.9 cell), threshold 0; an L7
     cell keeps its own land/sea (its fine cell is the same point), only the new cells between decide;
   - detail (`detail`): base from the coast ramps, fbm + ridged noise weighted by the zoom's ruggedness (rock,
     cover, plate boundary, relief, height, ice), amplitude `rug * (0.36 h + 0.3 relief + 25) + 12`, the soft coast
     clamp. Finest octave 2 fine cells (the zoom stops at 6 px because its landscape pass carves the valleys; here
     the world finish's erosion does);
   - mean correction (`mean_correction`): 12 passes, each L7 cell's mean (the nest's full-weighting restriction,
     the same one the downscaled climate uses) pulled back to the L7 height by a smooth correction.
   The ruggedness per coarse cell moves out of `stage_terrain.coarse_fields` into a shared function (small refactor,
   bit-identical; zoom goldens check it).
   Not reused: the landform classes' synthesis (`zoom/landforms.py`): it is built on the zoom's pixel raster (D8
   receivers, bench maps on pixel rows, ~1-30 km structures), and its forms are sub-cell at 28 km and 14 km. Taking it
   onto the icosphere is a refactor, flagged in the report, not done.
4. **Geology** (plate, crust, rock, surface rock, cover, crust thickness/age, landform class and strata, glacial
   imprint): each fine cell takes one L7 cell's values, the nearest to its warped position among its candidates with
   the same land/sea (else the nearest): a fine cell sits on one rock body, the boundaries ragged, not hexagons.
5. **Finish**: `world.finish` (the same back half every world uses) on the fine grid, with
   - climate downscaled from L7: `world.finish(..., climate_level=7)` calls `nest.climate_coarse` (the run's L7-on-L6
     machinery: ground restricted to L7, the L7 climate, fields prolonged back, temperatures through the lapse rate
     on each fine cell's own height, water balance and Koppen again per fine cell). Rain shadows are the L7 climate's
     (resolved at 55 km); no sub-cell orographic rain in this cut.
   - then everything else per fine cell: the finish's erosion, rivers and lakes (sea by connection, `geo.is_land`),
     waves, tides, the sea's layers, coastal life, soils, vegetation, biomes, satellite, human use, game attributes,
     coast forms, resources.
   - vegetation warm start: the L7 world's own PFT cover, smoothed; its CO2 and unlocked PFTs; held trees for a
     time-zoom world, as `finish.frame_state`.
   - soil memory and resource history: computed on the L7 grid from the source run (`timeline.soil_memory`,
     `resources.history`) and mapped onto the fine cells; `world.finish` gets a `history=` argument for the latter.
   - orbit: a finished time-zoom world's `orbit_dt` on L7 (`finish.orbit_dt`), passed to the L7 climate.
6. **Save**: `world.save`; meta `refined_from` (world id, level), method `tectonics`, level 8.

Small changes to shared code: `world.finish` gains `climate_level` and `history`; `nest.climate_coarse` gains
`orbit_dt` (on the coarse grid); the ruggedness helper. No other code paths change.

## Expected cost (before measuring)
- The direct L8 slice (a16f5a): 13.8 min, 17.7 GB, most of it the two full L8 climates and the 12 erosion passes.
  Here the climate runs at L7 (two calls, ~1 min each at L7) and the rest is linear in cells.
- L8: ~4-8 min, ~8-15 GB peak, world file ~440 MB (as a16f5a).
- L9 (2.6 M cells): ~20-35 min, ~30-50 GB peak, world file ~1.8 GB (cannot be opened in Chrome, PW-1209;
  measurement only, written to a scratch store and deleted).
