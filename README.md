# procgen_world

Toy procedural planets: a plate-tectonics terrain generator, a
climate / river / biome pipeline, a plain-text world format, and a 3D
browser viewer.

## Quick start

```sh
uv run python -m planet make --seed 7              # everything: 1 Gyr run (L6, ~6 min), ice-age time zoom, finished world, highlights, 4 zooms
uv run python -m planet make --seed 7 --preset cold --level 7 --zooms 6   # a showcase recipe; --dry-run shows the plan and time estimate
uv run python -m planet make --seed 7 --peoples dnd   # also a peoples run (dnd, seven_meals or a saved tree) on the finished world
uv run python -m planet make --seed 7 --now glacial   # the world's "now": interglacial (default), glacial, end, or a kyr
uv run python -m planet simulate --seed 1          # 1 Gyr of plate tectonics + climate -> runs/<id>/
uv run python -m planet simulate --seed 1 2 3 4 --level 6 --jobs 4   # several seeds at once, one process each
uv run python -m planet list                       # runs, worlds and zooms with their ids
uv run python -m planet delete <id>                # a run, world or zoom (a world takes its zooms along)
uv run python -m planet slice <run-id> --at 300    # full world (climate, rivers, vegetation) at 300 Myr
uv run python -m planet slice <run-id> --at auto   # ... at a representative moment (typical land/landmasses after 300 Myr, once every plant group exists)
uv run python -m planet zoom <world-id> --lat 10 --lon 40   # a 1000 km region at 2 km -> zooms/<id>/
uv run python -m planet timezoom <run-id> --at 300          # 2 Myr of ice ages from that moment -> runs/<id>/ (time in kyr; --kyr to change)
uv run python -m planet finish <timezoom-id> --kyr 120     # a finished world at that frame of the time zoom (default: its end)
uv run python -m planet finish <run-id> --at 300            # ... or straight from a run's keyframe (no ice ages)
uv run python -m planet refine <world-id> --level 8           # a finished world's moment remade on a finer grid (L8; L9 can't be opened yet, PW-1209)
                                                             #   (or from the viewer: Family > the world > "Refine the whole world to", PW-1438)
uv run python -m planet satellite <world-or-zoom-id>  # add / redo the true-colour satellite view in place
uv run python -m planet serve                      # opens http://127.0.0.1:8765/viewer/ (--jobs J: jobs at once, default 4)
uv run python -m planet highlights <run-id> --at 400 --zoom 5   # its most interesting places, + 5 zooms (built at once)
```

Several things at once run as separate processes (`planet/parallel.py`): a
run is mostly serial Python/numpy work, so threads inside one process barely
help (one L6 run: 46 s at 4 numba threads, 40 s at 16 or 48), while separate
processes scale. `--jobs J` (simulate with several seeds, `highlights
--zoom`, `serve`, `tools/scorecard.py`) sets how many worker processes run
at once (default: a quarter of the cores, at most the number of jobs; the
server 4), and `--threads T` the numba threads of each (default: the cores
shared out, at most 8). `--jobs 1` runs them one after the other in the one
process. A process on its own uses `NUMBA_NUM_THREADS=16` (or the core count
if lower) and one BLAS thread unless you set those variables: numpy's
OpenBLAS otherwise starts a thread per core and spins them, ~3.5x the CPU
for no gain. numba's threading layer is `tbb` when the TBB library loads,
else `workqueue`. Outputs don't depend on any of this (same bytes).

In the viewer, pick a run from the dropdown and press play (or space;
arrow keys step frames). Click an event in the list to jump to it. The panel
shows the exact `slice` command for the moment you're looking at. Click a
cell, then "Zoom" in the info box, to refine the region around it: the server
builds a world straight from the run's keyframe nearest that time
(`timeline.world_from_frame`, a few seconds, exactly what the viewer shows;
once per keyframe) and zooms in, then opens the result in the "Regional zoom" tab (also on its own at
`http://127.0.0.1:8765/viewer/zoom.html`). A run made by older code says so
(delete it and re-run). The globe shows the spin axis and
the tilt; tick "Equator, tropics, polar circles" for those, and press N (or
"North up") to level the view.

"Find highlights" (in the panel) lists the places worth a closer look at the
moment on screen: the highest peak (and the highest ice-free one, when the
top is under an ice cap), the longest mountain range, the largest and
longest rivers, the steepest big rivers and waterfalls, canyons, river mouths
where deltas could build, fjord coasts, Mediterranean "wine country", volcanic
arcs, hotspot island chains, atoll groups, rifts, the fastest plate (at its
leading edge), plateaus, rain shadows, coral coasts, the biggest
lake, salt lakes, salt flats and inland basins, deserts, rainforests, ice
sheets, the deepest trench, islands and archipelagos, the most varied 1000 km
square and a few climate records; from the vegetation, great forests, the
great savanna, wetlands, a maquis coast and the treeline. Worlds with
July / January layers also get travel tips, each with the numbers that make it
in its own hemisphere's season: beach destinations, ski country, winter-sun
retreats and a year-round resort (a beach and skiing within 400 km)
(`planet/highlights.py`; cached in `worlds/highlights/`). On ~110 km cells a
"waterfall" is a steep reach of river; each zoom lists its own pixel-scale
falls (height, discharge, place) in `zoom.json` stats, and `planet zoom`
prints the biggest. Click one to turn the
globe to it and pick it for a zoom at a suggested size (`&hl=N` in the URL
opens number N); `planet highlights --zoom N` makes those zooms ahead of time.

Each zoom also carries its own vegetation (`planet/zoom/vegetation.py`): the
world's plant model run per pixel on the zoom's terrain, so treelines follow
the valleys and sit higher on sunny slopes, gallery forests line the rivers
through savanna, oases the rivers through deserts, and mires gather in the
wettest hollows. Its named type, tree cover, canopy height, leaf area, NPP
and fire interval are stored (`zoom.load(id, decode=True)`); each plant
type's cover can be recomputed with `zoom.vegetation.fractions(<zoom-id>)`.
Zooms also store July / January temperature and rain, the sun on each slope
(`radiation_index`), a topographic wetness index and the distance to the
nearest river and the sea.

Other things to try:

```sh
uv run python -m planet simulate -s 7 --myr 1000 --set start=scattered n_plates=16
uv run python -m planet simulate --myr 2000 --set heat_start=2 continental_start=0.1   # ocean world, land emerges
uv run python -m planet simulate --set tilt=45 climate_offset=3                        # extreme seasons, hothouse
uv run python -m planet report <run-id>                                                # re-render run.txt
```

`-l/--level` controls grid detail: 4 = 2.5k cells, 5 = 10k (~220 km cells),
6 = 41k (~110 km), 7 = 164k (~55 km), 8 = 655k (~28 km). `simulate` defaults to
level 6, `generate` to level 5. Rough `simulate` times on a laptop (they vary
with load): level 6 ~3 min per 500 Myr (~6 min per Gyr), level 7 ~35-40 min
per Gyr (~50 under load; docs/overview.md section 4), level 8 hours (~4 h for 1.2 Gyr on a shared machine).

## Game export (`planet export`, `planet/export.py`, PW-100)

```bash
uv run python -m planet export <world-or-zoom-id> [--out DIR] [--res N] [--tile 1024] [--overlap 0] [--cube N] [--raw]
uv run python -m planet export 592f2a --res 4096 --cube 1024     # a world: equirectangular + six cube faces -> exports/592f2a/
uv run python -m planet export zoom:f99af0 --tile 512 --overlap 1 --raw   # a zoom on its native grid, 2^n+1 raw tiles
```

```bash
uv run python -m planet export 592f2a --projection mollweide --center 40,-100 --res 2048   # whole world, oblique, centred on 40N 100W
uv run python -m planet export 592f2a --projection laea --center 48,2 --extent 3000km --res 1024   # regional, 3000 km square
uv run python -m planet export zoom:f99af0 --projection stereo --extent 120x80km   # a zoom reprojected (default: its own aeqd)
```

From Python: `planet.export.export(ref, out, res=..., tile=..., cube=..., raw=..., projection=..., center=..., extent=...)` returns the directory (nothing in it needs the server).
The output is one folder, read through `manifest.json` (units, scale, sea level, projection, every layer's tiles, provenance ids):

| File | What |
|---|---|
| `heightmap` | 16-bit greyscale PNG (or raw little-endian `.r16` with `--raw`), ground height: `m = min_m + v / 65535 * (max_m - min_m)`; the manifest gives `min_m`, `max_m`, `metres_per_step` and `sea_level_value` (the value of 0 m). Same mapping as a zoom's `heightmap.png`; `--height-range LO HI` fixes it. A world's heights are its true bed (under ice too); sea level is 0 m |
| `ice_thickness` | 16-bit, metres of land ice on the ground (surface = ground + ice) |
| `water` | 8-bit ids: 0 land, 1 sea, 2 lake |
| `biome`, `vegetation`, `rock` | 8-bit class ids; names and colours in `legend.json` |
| `river_nav`, `harbour`, `pass`, `fertile`, `fresh_water` | 8-bit human-use class ids (PW-099, `planet/humanuse.py`, overview 2.22): navigable rivers (small boats / barges / sea-going), natural harbours, mountain passes (saddle pixel), farmland quality, reach of fresh water; names and colours in `legend.json` |
| `splat_0`, `splat_1` | RGBA8 weights of 8 materials (rock sand soil grass \| forest wetland tundra snow), summing to 255 on land and 0 on water. Rules, not simulation (`export.splat_weights`: slope, cover, rain, temperature, ice), a starting point for an engine's terrain layers |
| `features.geojson` | lon/lat (WGS84): `river` lines (from the routing; `--river-min` m3/s; properties `discharge_m3s` = peak, `strahler` order, `width_m` = bankfull width at the peak (7.2 sqrt(Q)), `vertex_discharge_m3s` = discharge at each vertex), `lake` polygons (shore counter-clockwise, islands as clockwise holes; `area_km2`, `level_m`, `lake_kind`, `centroid_lat_lon`; a world's outline follows the lake cells' edges, a zoom's the lake pixels' with straight runs merged), `volcano` (status, form, summit), `waterfall` and `delta` (zooms), human-use features (PW-099): `navigable_river` lines (`nav_class`, discharge range, gradient, `open_months`, `reaches_sea`), `harbour` (class, setting estuary / bay, depth, fetch, sea-ice months), `pass` (height, open months, basin areas), `spring`, `fertile_land` (worlds: regions of good farmland), `highlight` (the world's highlights; inside the zoom's square for a zoom, if cached). Points carry `elevation_m`. Every longitude is in [-180, 180] (RFC 7946 section 3.1.9, PW-533): a river that crosses the antimeridian is a `MultiLineString` cut at the 180th meridian (both parts end on exactly +-180, the crossing latitude interpolated), and its `vertex_discharge_m3s` is then a list per part aligned with that part's coordinates (a flat list for an uncut river, aligned with its one `LineString`); a lake straddling it is a `MultiPolygon` clipped at +-180 (the pieces share an edge along the meridian; a hole across it is cut the same way) |
| `features_local.geojson` | zooms only: the same in metres `[x east, y north, z ground height]` from the zoom's centre (its azimuthal-equidistant frame; the `crs` member names it) |

Layouts (`manifest.layouts`): a **world** is an equirectangular raster (`--res` = width in px, default 2048, height half of it; `deg_per_px`, row 0 north, column 0 at -180) and optionally the six faces of a cube (`--cube N`, gnomonic; `layouts.cube` gives each face's axis and image directions, files under `cube/<face>/`); a **zoom** keeps its native grid (`--res` = km per pixel, a multiple of the native one by block averaging; rivers always follow the native routing). Layers are cut into `--tile` px tiles (`<layer>/<layer>_x<i>_y<j>.png`, none if the raster fits); `--overlap 1` shares an edge pixel between neighbours for engines that want 2^n + 1 terrain tiles. Each layer lists its files with their pixel offsets. **Projected maps** (PW-477, `planet/projection.py`, pure numpy): `--projection {equirect, equal-earth, mollweide, laea, aeqd, ortho, stereo}`, `--center lat,lon` and `--extent` (`2000km`, `3000x2000km`, `30deg`, `40x20deg`; arc degrees; wide x high) replace the plain layout by one `layouts.map` with square pixels, the projection origin at the centre point and north up. Any one of the three flags makes a map (world default `equirect` at 0,0; zoom default `aeqd` at its own centre over its own square). The whole-world projections are used obliquely, so any latitude can be centred; `stereo` shows 120 degrees from the centre by default, `ortho` the near hemisphere, `laea` and `aeqd` the globe. `--res` is the width in px (zooms: km per px; height follows the extent's aspect). Every raster layer uses it: heights are smooth blends of the cell and its neighbours (worlds) or bilinear (zooms), class maps (`water`, `biome`, `vegetation`, `rock`) take the nearest cell, and splat weights are derived from those on the map. **Nodata:** pixels the projection does not show (off the globe or outline) or outside the extent (or outside a zoom's square) are heights 0 (data are clamped to at least 1), class ids 255 and splat all 0; a `coverage` layer (255 on the map, 0 off it) marks them and `layouts.map.nodata` says so. The manifest's `layouts.map` records `projection`, `center`, `extent_km`, `m_per_px`, `x_range_m` / `y_range_m` (metres on the planet-radius sphere; pixel centre x = `x_range_m[0] + (col + 0.5) * m_per_px`, y = `y_range_m[1] - (row + 0.5) * m_per_px`), a `proj` string (PROJ, sphere of the planet's radius; an oblique equirect / Equal Earth / Mollweide is `+proj=ob_tran +o_proj=... +o_lat_p=90-lat +o_lon_p=0|180 +lon_0=...`, checked against pyproj to ~1e-9 m; `oblique_frame` gives the rotation matrix too) and the frame. `features_map.geojson` has the features as `[x, y, z]` metres on the same plane (features off the map are left out; lines are cut where they leave it or cross the seam and become MultiLineStrings); `features.geojson` stays lon/lat. `m_per_px` is the pixel size on the map plane; ground distances match it only near the centre (every projection distorts elsewhere).

New layers (PW-099's passes and harbours, PW-206's game attributes) are added as manifest entries and feature kinds, so importers need not change.

## Glacial time zoom (`planet/timezoom/`)

A side simulation at 500-year steps: geology frozen at one moment
of a run, ice sheets driven by orbital (Milankovitch) cycles, with a
degree-day mass balance (`planet/icemass.py`, the same one the run's ice and
the regional zoom's glaciers use, so a run's ice is close to the time zoom's
own balance at its start), shallow-ice flow, isostasy, calving and sea level
from the ice it holds (above flotation, plus the room under sunken beds). `timezoom earth` starts from today's Earth (ETOPO1),
with the model's summer on the real ice sheets cooled to the observed one (`anchor=obs`);
`--set baseline=obs` uses the observed climate plus the model's changes.
Knobs: `--set key=value` for any `TZParams` field (e.g. `insol_k`,
`obliquity_amp`, `phases=zero`). The viewer plays it like a run (frames in
kyr; "ice thickness" layer; the summary panel has the sea-level / ice-volume
curve with the summer sun under it (where the ice comes and goes; 65°N July
dashed), click it to jump, and the orbit at
the frame on screen); its `run.txt` has the sea-level / ice / orbit table and
glacial events.

From the viewer: on a run, "Glacial time zoom from here" (summary panel)
starts one at the frame on screen (100, 300, 1000 or 2000 kyr; ~4 min per 1000 kyr
at level 6) as a server job, and opens it when done. The viewer, `POST /api/timezoom`,
`planet make` and the CLI's `--kyr` all default to 2000 kyr (PW-1661: v1.0 worlds get 2 Myr of ice ages). The time slider of a
run is tinted blue where the run is cold (land ice on > 1% of the surface or
a global mean < 13 °C; darkest = Earth today or colder): that's where a time
zoom shows ice ages.

**Finished worlds** (`planet/finish.py`, PW-091): `planet finish <timezoom-id>
--kyr N` turns any stored frame (every 2 kyr) of a time zoom into an ordinary
world (`worlds/<id>.json`; world view, zooms and highlights work as usual):
the source run's geology with that frame's ice, sunken bed, sea level and
global temperature, run through the usual finishing (climate, rivers, lakes,
biomes, sea, coasts). Its meta records the source run and Myr, the time zoom
and the kyr. `planet finish <run-id> --at T` is the same without the ice
ages: the world straight from the keyframe (what the viewer's Zoom button
builds). In the viewer: "Finish world here" on a run frame or a time zoom
frame (server job `POST /api/finish {timezoom, kyr}` or `{run, t}`), then the
world opens;
**which moment is "now"** (PW-479): `planet make --now interglacial|glacial|end|<kyr>`
(the New planet form's select, `/api/make`'s `now`, and `planet finish --now`;
`POST /api/finish {timezoom, now}`). The default is the latest interglacial
peak of the time zoom, like Earth today: it reads the glacial index each frame
stores (`stats.glacial_index`) and takes, in the last stretch with I <= 0.05
after one full cycle (I past 0.5 and back), the frame with the highest sea level.
`glacial` is the lowest sea level in the last stretch within 0.2 of the highest
index. On a zoom too short for a full cycle, `interglacial` falls back to its end
and `glacial` to its lowest sea level (the navigator offers "Finish at the
interglacial" and "Finish at the glacial maximum" next to "Finish at its end"); the run's "Made from this run" tree lists time zooms with their
finished worlds, and a time zoom's slider has a green tick for each.

The ice ages are scripted (PW-471, the glacial index method): an index I(t)
from 0 (interglacial: the run's own climate) to 1 (glacial maximum) builds
over ~70-90 kyr and ends in 8 kyr at a summer-sunshine peak of the planet's
own orbit, and the zoom's climate is I x the glacial cooling colder
(polar-amplified). The cooling is 6.5 °C for Earth's share of land poleward
of its snowline and in proportion elsewhere (`--set glacial_dt=4` sets it by
hand, `index=off` keeps I at 0). The ice physics draws the sheets.

## Earth reference world

```sh
uv run python tools/earth_world.py      # prints the new world's id
```

Builds "Earth (today, ETOPO1) — model vs observed": real terrain and ice
through the normal pipeline (our climate, rivers, biomes; erosion off), plus
the observed temperature (NCEP), rainfall (GPCC/GPCP) and Köppen climate
(Kottek) and the model's winds, currents and jet stream. In the viewer,
temperature, precipitation and climate get a "model / observed / difference"
switch (`?obs=diff` in the URL). Re-run it after climate-model changes (and
delete the old one).

The observations live in `data/earth/` (git-ignored). `tools/earth_data.py` downloads them, but some
of the source servers are slow or flaky, so a cached copy is kept on the `earth-data` branch
(~25 MB). To restore it into a checkout without staging anything:

```sh
git fetch origin earth-data
git restore --source=origin/earth-data --worktree -- data/earth
```

## Tests and calibration

```sh
uv run pytest                    # invariants + envelope tests (~5 min; 4 numba threads, tests/conftest.py)
uv run pytest -m "not slow"      # invariants only (~6 s)
uv run python tools/earth_check.py --png earth.png   # climate, rivers and lakes on real Earth vs observations
uv run python tools/scorecard.py # slow scores (Earth + 1 Gyr worlds, at once: --jobs) appended to docs/scorecard.jsonl
PYTHONPATH=. uv run python tools/veg_check.py --png veg.png   # vegetation on real Earth vs potential vegetation and published numbers
```

- **Invariants** (`tests/test_invariants.py`) must hold whatever the tuning:
  determinism, the continental crust budget closing, sane values, storage
  that doesn't clip, the sim -> world -> zoom chain.
- **Envelopes** (`tests/test_envelopes.py`) are plausible ranges (land 22-42%,
  dry climates 12-45% of land, plate speeds, ocean age...), so a tuning change
  that quietly breaks another part of the planet fails.
- **Golden outputs** (`tests/test_golden.py`) pin hashes of a short level-4 run
  and one climate computation, so refactors can be shown not to change
  results. A commit meant to change outputs regenerates them with
  `uv run pytest tests/test_golden.py --update-golden` and commits `tests/golden/*.json`.
- The **scorecard** isn't pass/fail: it records how Earth-like things are per commit.

## Time-stepped tectonics (`planet/tectonics/`)

Each plate keeps its crust on a private copy of the grid plus a rotation saying
where that copy currently sits. Every step (default 2 Myr, `--dt`):

1. plates rotate by their angular velocity;
2. every world cell asks every plate whether it has crust there. Nobody has any:
   new ocean floor (a ridge). Several do: continental beats oceanic, young ocean
   beats old (subduction); continent vs. continent is a collision;
3. ocean floor sinks as it ages (~sqrt(age)), subduction builds arcs, collisions
   build big ranges, rifts stretch continents thin; rivers and erosion wear
   the land down and lay down sediment (every step). The climate (temperature,
   rain, ice, sea level from the ice) is recomputed on a ramp, every 8 Myr
   early to every 4 Myr (`climate_every`) in the 30 Myr before the finish
   window, sooner when the global temperature moves 1 C (PW-247), and the
   rivers use the latest one in between;
4. forces -> velocities: slab pull, ridge push, collision resistance, basal
   traction from the mantle, plus a small, slowly wandering drag term
   (meandering), give each plate a target angular velocity (the force balance,
   no momentum). The plate's velocity relaxes toward that target over
   `velocity_timescale` = 15 Myr (a stand-in for inertia) and is capped at
   `max_speed` = 18 cm/yr. The forces are computed after the plates have
   moved, so each step moves the plates with the velocities set from the
   previous step's forces. The mantle (`mantle.py`) is a smooth,
   world-frame temperature anomaly that remembers where slabs sank (cold) and
   where continents sat still (warm, insulated); it flows from warm to cold
   and drags the plates along, so continents gather over the slab graveyards
   into a supercontinent, which warms the mantle under itself and is pulled
   apart again (a supercontinent cycle; not guaranteed for every seed). New
   plumes rise from the warm mantle, mostly at its edges;
5. events: long collisions weld plates (suture); plates whose halves are pulled
   apart split along their weakest line (old sutures, thinned crust, over
   plumes) into a few big pieces, never continental slivers; old passive
   margins start subducting; slivers get absorbed.

Main knobs (`--set`): `n_plates`, `start` (`supercontinent`|`scattered`),
`continental_fraction`, `slab_pull`, `ridge_push`, `collision_drag`,
`mantle_drag`, `mantle_memory`, `mantle_scale_km`, `slab_cold`, `insulation`,
`mantle_noise`, `mantle_timescale`, `mobility`, `max_speed`, `arc_growth`,
`crust_flow`, `erosion_timescale`, `suture_after`, `rift_timescale`,
`rift_stress`, `warm_rift`, `rift_min_piece`, `ridge_time`, `max_plates`. Defaults live in `Params`.
`uv run python tools/ice_diag.py --seed 1 2 --myr 2000 --tect` tracks, beside the ice and
climate terms, sea level and its parts (ice, ocean basins, mean ocean age), fast land drops, the
largest landmass, landmass count, mantle temperature and rifts, and reports assembly spells
(`--plot` draws them; `--run <id>` gives a stored run's sea-level line).

The package's docstring (`planet/tectonics/__init__.py`) maps its modules:
`simulation` (state, step), `plates`, `motion` (forces), `crust` (the crust
budget), `volcanism`, `earth` (climate, sea level, erosion), `events` (rifts,
sutures), `isostasy`, `plate_kernels`, `setup`, `output`. `Simulation.state()`
returns the whole state (what a checkpoint must save).

Runs are deterministic: `slice` replays from the nearest saved state at or
before the moment asked for (`simulate` saves the full simulation state
every 100 Myr, `--checkpoint-every`; ~12 MB each at level 6, ~45 MB at level 7: the plates' stale crust is zeroed, store.shrink_state, and their cell map is stored as its difference from a fresh grid.locate, store.pack_idx) and checks
itself against the stored keyframe. Each run records the code that made it
(`meta.code`: git commit, dirty flag, hash of `planet/**/*.py`). If the model has
changed since, the replay is a different planet: `slice` warns, and when the
replay doesn't match the keyframe it refuses to save the world unless `--force`.

## One-shot terrain (`planet/generators.py`)

Cartoon plate tectonics: random plates, each spun around a random axis, with
mountains, trenches, ridges and rifts built where plates collide or separate.
Knobs (`--set`): `n_plates`, `continental_fraction`, `mountain_height`,
`trench_depth`, `ridge_height`, `plate_speed`.

(Earlier `noise` and `faults` generators are in git history at commit 503f101.)

Sliced and one-shot terrain then go through the shared pipeline:

1. **Climate** (`climate.py`): temperature from latitude and altitude; Earth-style
   wind bands carry moisture off the oceans; air rains out as it cools, which
   gives wet windward coasts and rain-shadow deserts. Ocean gyres come from a
   wind-driven streamfunction per basin (Stommel model: fast warm western
   boundary currents, circumpolar currents); the jet stream from the thermal
   wind steers the storm tracks; low-level winds turn along high mountains.
   The deep overturning (`ocean.py`): sea-surface salinity from evaporation,
   rain, river mouths, sea-ice brine and meltwater; density from temperature
   and salinity; deep water sinks where the winter water is densest (Nordic
   and Labrador seas, the Antarctic margin; not the fresh North Pacific), and
   the warm water flowing in to replace it, along the currents, warms its
   way north (the North Atlantic Drift and a milder Norway).
   Evaporation: potential evaporation from sunshine and temperature per
   half-year (Oudin), actual evaporation from the Budyko curve (Fu), and
   runoff = rain - evaporation (~40% of the rain on land, like Earth's).
   Lakes evaporate by Penman's open-water equation, on the clouds and the
   air's humidity (humid tropical lakes ~1400 mm, desert ones ~2000+).
   The vegetation feeds back: forests give more rain back to the air (Budyko
   w, rain recycling) and their albedo (snow hidden under conifers) nudges
   the temperatures by up to 2 C.
2. **Erosion, rivers and lakes** (`hydrology.py`): rivers carry the runoff.
   Priority-flood drainage, flow accumulation, then stream-power erosion that
   cuts valleys (`--erosion 0` skips it). Lakes evaporate: each basin fills
   only until the evaporation off its lake balances its inflow, or it spills.
   Dry basins hold closed salt lakes (the Caspian, Great Salt Lake) or salt
   pans, and their rivers end there. A river leaving a lake has cut its
   outlet down (deeper the bigger the river), so big through-flowing lakes
   drain to it.
3. **Biomes**: worlds group the vegetation model's named types (`vegetation.py`, `docs/overview.md` §2.18) into the coarse biome classes; the zoom still uses a Whittaker-style lookup on temperature and rainfall per pixel.

Knobs: `--erosion <strength>` (`generate` and `slice`); `generate` also takes
`--set erosion_iterations=12 dT=2 tilt=30` (`dT`: global temperature offset
from today's Earth, °C). There are no `equator_temp`/`pole_temp` knobs:
`climate.compute` derives the equator and pole temperatures from `dT` and
`tilt`, and the generator fails on any `--set` key it doesn't know.

## Peoples, resources and coasts in the viewer

- **Peoples** (`planet/lineages/`): open any finished world (or its time zoom), click **Peoples** in the bar at the top
  of the viewer. The panel lists the world's peoples runs (click one to open it with the peoples layer on),
  **Make peoples... (edit tree)** (opens `lineages.html?world=<id>&tree=dnd`, the editor) and **Run D&D peoples** (queues
  the stock tree as a job, as `POST /api/lineages`, and opens the result when it finishes). Peoples need the time zoom the
  world was finished from; if it was deleted the panel says so.
- **The editor**: the **Peoples editor** link in the same bar (or `viewer/lineages.html`). Without `?world=` it has a
  picker of finished worlds whose time zoom is still stored; after **Run on world** an **Open on the globe** link opens
  the run with `layer=peoples`. A bar ends where the spec ends the line (at its last living split unless it persists, at
  its extinction, or at the computed end after a run).
- **Resources and coasts**: the same panel shows whether the world on screen has its `res_*` / `coast_type` layers and, if
  not, **Add resources** / **Add coasts** (`POST /api/enrich {world, what: resources | coast}`, a queued job running
  `planet resources` / `planet coast`; the world is rewritten in place and reopened). New worlds have both already; the buttons are for older ones.

## Waves, tides and delta types (`planet/coast.py`)

Every world gets two marine layers on its sea cells (0 on land):

- `wave_power` (kW per m of wave crest, annual mean): rays are traced out
  over the sea in 16 directions from each cell, and walking back in, the
  sea grows under each stretch's wind with fetch and storm duration
  (fully developed seas after Pierson-Moskowitz, fetch- and
  duration-limited growth after JONSWAP), then travels on as slowly
  decaying swell, loses energy over shallow shelves, and stops at land or
  winter sea ice. Winds come from the climate's half-year winds plus its
  storminess, with a gust factor because power goes as ~U^5.
- `tide_range` (m): a proxy in three factors: the connection to the open
  ocean (a depth-weighted diffusion from open-ocean cells, so narrow
  shallow straits choke it; closed seas get only a small tide of their
  own), shelf resonance (a quarter-wavelength shelf amplifies the tide,
  very wide ones damp it) and funnelling into narrowing embayments.

`PYTHONPATH=. uv run python tools/coast_check.py` scores the coast form on the
Earth world against named places (21 of 32 right on 2026-10-31). No tool scores
the waves and tides against observed coasts any more.

At each big river mouth the zoom weighs the river's sediment (BQART)
against what the waves can carry along the shore (CERC) and what the tides
carry in and out (the tidal prism over the flooded plain) to get
Galloway's river, wave and tide weights (`coast.galloway`). The delta's
shape follows the weights continuously:
- **river:** long levee-bound fingers out to sea (a bird's foot);
- **wave:** a smooth arc with few mouths, a barrier and lagoon on its
  flanks, and beach ridges;
- **tide:** funnel estuaries widening seaward, creeks cutting elongate
  islands, and tidal flats.

`zoom.json` `stats.deltas` reports the weights, the type, the mouths and
the inputs. The zoom viewer shows them, and highlights name the type at
delta sites.

## Why the pentagons

See the docstring in `planet/grid.py`. A sphere can't be tiled with hexagons
alone. Euler's formula forces **exactly 12 pentagons** (not 1), like the black
patches on a football. In the viewer, tick "Highlight the 12 pentagons".

## Files

Paths, ids, indexes, deleting and the binary layer format live in
`planet/store.py`. Outputs go under the data root: the repository by
default, or `$PLANET_DATA` (e.g. `PLANET_DATA=/tmp/scratch uv run python -m
planet simulate ...`; `serve` then shows that root's runs).

- `runs/<id>/run.json`: settings, per-keyframe stats, plate velocities, the
  event log, and the layer specs. Small and readable.
- `runs/<id>/layers/<name>.bin`: one file per layer, all keyframes (raw
  little-endian, frames x cells). The viewer downloads only the layers it
  draws. Each layer's spec in run.json says its dtype, shape and encoding
  (`value = stored * scale + offset`, then an optional transform: `log2p1`
  for river flow, `nbr_slot` for the downstream cell), so Python and the
  viewer read them the same way.
- `runs/<id>/state/<t>.ckpt`: the full simulation state every 100 Myr, where
  `slice` starts replaying.
- `runs/<id>/run.txt`: the one to read or paste into a chat. It has the event log,
  stats over time, ASCII elevation maps at five moments, and a plate table.
- `worlds/<id>.json` / `.txt`: a full world (from `slice` or `generate`); it
  names its grid file (`"grid": "../grids/L6.json"`) rather than including
  it, and lists its layer files (`worlds/layers/<id>/<name>.bin`, one binary file
  per layer, PW-1209). The `.txt` has the summary and ASCII maps. Water layers: `flow` (river flow,
  upstream runoff in cells x m/yr; times a cell's area per year = m3/s),
  `runoff`, `evaporation`, `pet` (mm/yr), `lake` (0/1), `lake_kind` (0 none,
  1 open/fresh, 2 closed/salt, 3 salt pan) and `lake_level` (the lake's
  surface in m to 0.1 m, same datum as `elevation`; equal to `elevation` where there's
  no lake, so `lake_level - elevation` is the water depth), `flood_ratio` (the
  river's peak month flow / its mean month: spring floods) and `flood_month`
  (1-12). Sea layers:
  `wave_power` (kW/m) and `tide_range` (m), see `planet/coast.py`; `sst`,
  `sst_jul`, `sst_jan` (sea-surface temperature, C), `salinity` (psu) and
  `sinking` (Sv of deep water sinking per cell), see `planet/ocean.py` (0 on
  land). Air: `dewpoint_jul/_jan` (C), `humidity_jul/_jan` (% relative
  humidity), `cloud_jul/_jan` (% cloud cover) and `sunshine_jul/_jan` (hours
  of bright sunshine a day) for the two half-years (`climate.clouds`). The satellite
  view (`planet/satellite.py`): `sat` (each hemisphere's summer), `sat_jul`, `sat_jan`,
  true colour as integers 0xRRGGBB. World meta `overturning` has the
  overturning's strength (`sv`, `north_sv`, `south_sv`), its sinking sites
  and a schematic of its loop (`ocean.loop_schematic`).
- `worlds/highlights/<id>.json`: the highlights found in world `<id>` (a cache).
- `zooms/<id>/zoom.json`, `layers/<name>.bin`, `*.png`: a regional zoom
  (`preview.png` is the satellite view in summer, shaded, with rivers; `satellite.png`,
  `satellite_jul.png`, `satellite_jan.png` are its unshaded true colours).
- `grids/L<level>.json`: grid geometry shared by all runs and worlds at that level.

Runs and worlds share one vocabulary of layer names (`store.LAYERS`):
`elevation, plate, crust` (1 = continental), `crust_age, plate_boundary, rock,
surface_rock, sediment_cover, crust_thickness, precipitation, temperature,
climate, ice, flow, downstream, lake_depth, lake_kind, wind_e/_n, current_e/_n,
jet_e/_n, wave_power, tide_range, sst, sst_jul/_jan, salinity, sinking,
dewpoint_jul/_jan, humidity_jul/_jan, cloud_jul/_jan, sunshine_jul/_jan,
temperature_jul/_jan, precipitation_jul/_jan, wind_jul_e/_n, wind_jan_e/_n`
(the sea, air and seasonal wind layers are worlds only; runs keep July and
January temperature and rain too, the rain as a one-byte log scale:
`store.run_spec`), and the landform layers
(`planet/landform.py`: `landform` (class id, legend `landforms`),
`landform_age`, `strata_top`, `strata_top_km`, `strata_next`, `strata_dip`,
`fold_wavelength`, `rift_strain`, `glaciated_myr`), which run frames and
sliced worlds both carry, and the vegetation layers (`planet/vegetation.py`:
`vegetation` (named type, legend `vegetation`), `tree_cover`, `npp` in run
frames and worlds; worlds also `plant_cover`, `lai`, `lai_jul`, `lai_jan`,
`canopy_height`, `biomass`, `fire_return`, `stand_age`, `pft_dominant`,
`flooded` and `veg_<PFT>` for each of the 19 plant functional types). Not every item stores every layer: run frames have
the annual wind, current and jet layers; worlds have those plus the July /
January winds, and add `biome`, `runoff`, `evaporation`, `pet`,
`warm_month`, `cold_month` and the wave and tide layers. All of them use
`.bin` files: a world's are `worlds/layers/<id>/<name>.bin`, listed in its JSON. Run
frames keep `lake_depth` (m of water, stored in decimetres) where worlds keep `lake_level` (its
surface); `lake_kind` means the same in both. Time zooms keep a few of these
names (`elevation`, `ice`, `temperature`, `climate`, plus the frozen
geology). Zooms have
their own raster layers (`zoom.LAYER_DOC`: `water`, `discharge`,
`lake_depth`, ..., the vegetation's summary layers and the world's ten soil
layers per pixel, `soil` ... `loess`).

`delete` removes one item by id (`run:<id>`, `world:<id>` or `zoom:<id>`
when a run and a world share an id); `delete --orphans` clears zooms and
highlight caches whose world is gone, and unfinished runs. The viewer's Delete buttons do the same.

All of these are generated output (git-ignored) and reproducible from seed + settings.

In the viewer, clicking a cell copies a description to the clipboard, so you can
point at a specific place when asking for changes.

Viewer URL options: `?run=19385e&t=120&layer=plates&arrows=1` or
`?world=ae28af.json&mode=map&layer=biome&pentas=1&outlines=1&relief=40`. Ids
are the 6-hex-character ids from `planet list`; `world=` takes the file name,
so it needs the `.json`. `layer=` takes the viewer's layer names, which differ
from the stored ones: a run's rain is `layer=rainfall` (a world's is
`precipitation`), and names with spaces need URL encoding
(`layer=crust%20age`, `layer=surface%20rock`, `layer=wave%20power`).
