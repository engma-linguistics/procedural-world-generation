# procgen_world

Toy procedural planets: a plate-tectonics terrain generator, a
climate / river / biome pipeline, a plain-text world format, and a 3D
browser viewer.

## Quick start

```sh
uv run python -m planet simulate --seed 1          # 500 Myr of plate tectonics + climate -> runs/<id>/
uv run python -m planet list                       # runs, worlds and zooms with their ids
uv run python -m planet delete <id>                # a run, world or zoom (a world takes its zooms along)
uv run python -m planet slice <run-id> --at 300    # full world (climate, rivers, vegetation) at 300 Myr
uv run python -m planet slice <run-id> --at auto   # ... at a representative moment (typical land/landmasses after 300 Myr)
uv run python -m planet zoom <world-id> --lat 10 --lon 40   # a 1000 km region at 2 km -> zooms/<id>/
uv run python -m planet timezoom <run-id> --at 300          # 1 Myr of ice ages from that moment -> runs/<id>/ (time in kyr; --kyr to change)
uv run python -m planet finish <timezoom-id> --kyr 120     # a finished world at that frame of the time zoom (default: its end)
uv run python -m planet finish <run-id> --at 300            # ... or straight from a run's keyframe (no ice ages)
uv run python -m planet satellite <world-or-zoom-id>  # add / redo the true-colour satellite view in place
uv run python -m planet serve                      # opens http://127.0.0.1:8765/viewer/
uv run python -m planet highlights <run-id> --at 400 --zoom 5   # its most interesting places, + 5 zooms
```

In the viewer, pick a run from the dropdown and press play (or space;
arrow keys step frames). Click an event in the list to jump to it. The panel
shows the exact `slice` command for the moment you're looking at. Click a
cell, then "Zoom" in the info box, to refine the region around it: the server
builds a world straight from the run's keyframe nearest that time
(`timeline.world_from_frame`, a few seconds, exactly what the viewer shows;
once per keyframe) and zooms in, then opens the result in the "Regional zoom" tab (also on its own at
`http://127.0.0.1:8765/viewer/zoom.html`). Only runs too old to build from
their keyframes fall back to replaying the simulation (`slice`, which can take
minutes). The globe shows the spin axis and
the tilt; tick "Equator, tropics, polar circles" for those, and press N (or
"North up") to level the view.

"Find highlights" (in the panel) lists the places worth a closer look at the
moment on screen: the highest peak (and the highest ice-free one, when the
top is under an ice cap), the longest mountain range, the largest and
longest rivers, the steepest big rivers and waterfalls, canyons, river mouths
where deltas could build, fjord coasts, Mediterranean "wine country", volcanic
arcs, hotspot islands, rifts, plateaus, rain shadows, coral coasts, the biggest
lake, salt lakes, salt flats and inland basins, deserts, rainforests, ice
sheets, the deepest trench, islands and archipelagos, the most varied 1000 km
square and a few climate records. Worlds with
July / January layers also get travel tips, each with the numbers that make it
in its own hemisphere's season: beach destinations, ski country, mild-winter
retreats and a year-round resort (a beach and skiing within 400 km)
(`planet/highlights.py`; cached in `worlds/highlights/`). On ~110 km cells a
"waterfall" is a steep reach of river; each zoom lists its own pixel-scale
falls (height, discharge, place) in `zoom.json` stats, and `planet zoom`
prints the biggest. Click one to turn the
globe to it and pick it for a zoom at a suggested size (`&hl=N` in the URL
opens number N); `planet highlights --zoom N` makes those zooms ahead of time.

Each zoom also carries its own vegetation (`planet/zoom_vegetation.py`): the
world's plant model run per pixel on the zoom's terrain, so treelines follow
the valleys and sit higher on sunny slopes, gallery forests line the rivers
through savanna, oases the rivers through deserts, and mires gather in the
wettest hollows. Its named type, tree cover, canopy height, leaf area, NPP
and fire interval are stored (`zoom.load(id, decode=True)`); each plant
type's cover can be recomputed with `zoom_vegetation.fractions(<zoom-id>)`.
Zooms also store July / January temperature and rain, the sun on each slope
(`radiation_index`), a topographic wetness index and the distance to the
nearest river and the sea.

Other things to try:

```sh
uv run python -m planet simulate -s 7 --myr 1000 --set start=scattered n_plates=16
uv run python -m planet simulate --myr 2000 --set heat_start=2 continental_start=0.1   # ocean world, land emerges
uv run python -m planet simulate --set tilt=45 climate_offset=5                        # extreme seasons, hothouse
uv run python -m planet report <run-id>                                                # re-render run.txt
```

`-l/--level` controls grid detail: 4 = 2.5k cells, 5 = 10k (~220 km cells),
6 = 41k (~110 km), 7 = 164k (~55 km), 8 = 655k (~28 km). `simulate` defaults to
level 6, `generate` to level 5. Rough `simulate` times on a laptop (they vary
with load): level 6 ~3 min per 500 Myr (~6 min per Gyr), level 7 ~20-35 min
per Gyr, level 8 hours (~4 h for 1.2 Gyr on a shared machine).

## Glacial time zoom (`planet/timezoom.py`)

A side simulation at 500-year steps: geology frozen at one moment
of a run, ice sheets driven by orbital (Milankovitch) cycles, with a
degree-day mass balance, shallow-ice flow, isostasy, calving and sea level
from the ice it holds (above flotation, plus the room under sunken beds). `timezoom earth` starts from today's Earth (ETOPO1);
`--set baseline=obs` uses the observed climate plus the model's changes.
Knobs: `--set key=value` for any `TZParams` field (e.g. `insol_k`,
`obliquity_amp`, `phases=zero`). The viewer plays it like a run (frames in
kyr; "ice thickness" layer; the summary panel has the sea-level / ice-volume
curve with the 65°N summer sun under it, click it to jump, and the orbit at
the frame on screen); its `run.txt` has the sea-level / ice / orbit table and
glacial events.

From the viewer: on a run, "Glacial time zoom from here" (summary panel)
starts one at the frame on screen (100, 300 or 1000 kyr; ~4 min per 1000 kyr
at level 6) as a server job, and opens it when done. The viewer (and
`POST /api/timezoom`) defaults to 300 kyr; the CLI's `--kyr` defaults to 1000. The time slider of a
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
world opens; the run's "Made from this run" tree lists time zooms with their
finished worlds, and a time zoom's slider has a green tick for each.

The feedbacks: CO₂ drawdown and ice albedo grow with the extra ice. A run's
moment is taken as the cycle average (its ice is the mean extent; its dT
already holds that ice's albedo), so only `average_room` (half) of their caps
is left; Earth starts in an interglacial with the full room (`--set
start=interglacial|average`).

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

## Tests and calibration

```sh
uv run pytest                    # invariants + envelope tests (~30 s)
uv run pytest -m "not slow"      # invariants only (~6 s)
uv run python tools/earth_check.py --png earth.png   # climate, rivers and lakes on real Earth vs observations
uv run python tools/scorecard.py # slow scores (Earth + 1 Gyr worlds) appended to docs/scorecard.jsonl
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
   rain, ice, sea level from the ice) is recomputed only every
   `climate_every` = 4 Myr, matching the default keyframes, and the rivers use
   the latest one in between;
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
`uv run python tools/supercontinent.py --seed 1 2` tracks the largest landmass,
landmass count, mantle temperature and rifts over 2 Gyr (`--plot` draws them).
`PYTHONPATH=. uv run python tools/sealevel.py --seed 1 2` (or `--run <id>`) tracks
sea level and its parts (ice, ocean basins, mean ocean age) and counts fast land drops.

The package's docstring (`planet/tectonics/__init__.py`) maps its modules:
`simulation` (state, step), `plates`, `motion` (forces), `crust` (the crust
budget), `volcanism`, `earth` (climate, sea level, erosion), `events` (rifts,
sutures), `isostasy`, `plate_kernels`, `setup`, `output`. `Simulation.state()`
returns the whole state (what a checkpoint must save).

Runs are deterministic: `slice` replays from the nearest saved state at or
before the moment asked for (`simulate` saves the full simulation state
every 100 Myr, `--checkpoint-every`; ~25-30 MB each at level 6, ~110-140 MB at level 7) and checks
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
2. **Erosion, rivers and lakes** (`hydrology.py`): rivers carry the runoff.
   Priority-flood drainage, flow accumulation, then stream-power erosion that
   cuts valleys (`--erosion 0` skips it). Lakes evaporate: each basin fills
   only until the evaporation off its lake balances its inflow, or it spills.
   Dry basins hold closed salt lakes (the Caspian, Great Salt Lake) or salt
   pans, and their rivers end there.
3. **Biomes**: a Whittaker-style lookup on temperature and rainfall.

Knobs: `--erosion <strength>` (`generate` and `slice`); `generate` also takes
`--set erosion_iterations=12 dT=2 tilt=30` (`dT`: global temperature offset
from today's Earth, °C). There are no `equator_temp`/`pole_temp` knobs:
`climate.compute` derives the equator and pole temperatures from `dT` and
`tilt`, and the generator fails on any `--set` key it doesn't know.

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

`PYTHONPATH=. uv run python tools/coast_check.py` scores both on today's
Earth against known values. Waves come out within 2x at 25 of 30 coasts
(9 in range), and tides within 2x at 21 of 23 (13 in range). It also
prints the Galloway weights of real deltas.

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
  it. The `.txt` has the summary and ASCII maps. Water layers: `flow` (river flow,
  upstream runoff in cells x m/yr; times a cell's area per year = m3/s),
  `runoff`, `evaporation`, `pet` (mm/yr), `lake` (0/1), `lake_kind` (0 none,
  1 open/fresh, 2 closed/salt, 3 salt pan) and `lake_level` (the lake's
  surface in m, same datum as `elevation`; equal to `elevation` where there's
  no lake, so `lake_level - elevation` is the water depth). Sea layers:
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
(the seasonal, sea and air layers are worlds only), and the landform layers
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
`warm_month`, `cold_month` and the wave and tide layers. World layers are
stored inline in the world's JSON; runs and zooms use `.bin` files. Run
frames keep `lake_depth` (m of water) where worlds keep `lake_level` (its
surface); `lake_kind` means the same in both. Time zooms keep a few of these
names (`elevation`, `ice`, `temperature`, `climate`, plus the frozen
geology). Zooms have
their own raster layers (`zoom.LAYER_DOC`: `water`, `discharge`,
`lake_depth`, ...).

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
