# World Orogen (raguilar011095/planet_heightmap_generation): research

Read from a shallow clone (files only, nothing run). Paths below are relative to that repo.

## Who, what, licence, activity
- Solo author "raguilar011095"; site orogen.studio. Created 2026-02-15, last push 2026-10-29, about 300 commits, 133 stars, 26 forks, latest release v2.1.2 (2026-10-26), open issues are UI/feature requests (gh repo view; gh issue list).
- GPL-3.0 (LICENSE). Borrow ideas and cited papers only; do not copy code into procgen_world without a licence decision.
- Browser app: JavaScript ES modules, three.js, no build step (README.md). Its stated philosophy is "concept art for planets, not a geophysical simulator", with plausibility ranked below aesthetics and speed (README Philosophy; CLAUDE.md). The repo has a CLAUDE.md of its own, so it is also built with an AI agent.
- Two products. V1 (`js/`) is a one-shot generator in seconds. V2 (`v2/js/`, "Evolution" page) is a tectonic-history engine, about 26k lines across `v2/js/*/*.js`, released as v2.x. Plans/design docs are in `plans/` (about 20 files).

## Grid and scale
- Jittered Fibonacci-sphere points, Delaunay-triangulated into Voronoi cells, CSR adjacency (`v2/js/core/sim-mesh.js`, `js/sphere-mesh.js`).
- The tectonic sim mesh is fixed and independent of render detail: 40K cells default (about 121 km), 80K and 160K selectable (`v2/README.md` Phase 12, "Performance"). 160K is about our L7 (163,842 cells), so their top sim tier matches our standard tier.
- Terrain is synthesized on a separate render mesh up to 2.5M cells, with "Add detail" beyond that (v2/README "Terrain", "Performance"). Climate runs on a fixed 1 degree lat-lon grid (360x180) and is sampled up to the terrain cells (`v2/js/climate/core.js`, `grid.js`).
- Compared with ours: the sim is 4x coarser by default and equal at the top setting. They get fine relief by synthesis from records, not by simulating fine cells.

## Performance and outputs
- CPU only, JS workers. A 600 Myr history takes about 25-36 s at 40K and about 63 s at 80K (v2/README "Performance"). A 1200 Myr history takes 19-24 s at 20K. About 2.5 min per 600 Myr at 160K. A whole-planet terrain frame at 2.5M cells takes about 1-1.3 s on 8 workers. The GPU is used only for painting maps (`view/gpu-paint.js`).
- Outputs: 3D globe and maps, 16-bit data maps (temperature, rain, wind, currents, ice, heightmaps, hillshade, Koppen index, plate ids) in 10 projections up to 65,536 px wide (README "Map export"), and a `.orogen` save of the whole history.
- Compared with ours: their history is far cheaper per Myr, but it is a much simpler model (see below).

## Subsystem by subsystem

| Subsystem | World Orogen | procgen_world |
|---|---|---|
| Tectonics (V2) | Plate-frame rasters (each plate owns a raster over the mesh plus a quaternion; crust is never resampled; `step/gather.js`). Forces from boundary state: slab pull, slab suction, ridge push, rift push, mantle flow, solved as D·omega = T per plate (`step/forces.js`, `torque-balance.js`). Rifting, suturing, terrane docking, back-arc, arcs, hotspots, LIPs, and a supercontinent cycle with mantle upwelling/downwelling (`step/supercontinent.js`). | Comparable ambition (plates, mantle, volcanism, isostasy; `planet/tectonics/`) but run over a 164k-cell grid for 0.5-2 Gyr. Theirs is more event-rule driven and steered (cycle period is drawn and set by hand). |
| Heights and erosion | Heights are mostly **synthesized per frame from records** (uplift, belt geometry, crest size, Airy root) plus noise and stripes (`terrain/synthesize.js`, `records.js`, `stripes.js`). The records erode by clocks scaled with latitude rain (`step/heights.js`). Rivers use the stream-power law, solved **analytically** along the river tree (Tzathas et al. 2024) in `terrain/carve.js`; the history's rivers persist and cut antecedent gorges (`step/rivers.js`). V1 uses Braun-Willett implicit stream power, thermal, glacial and creep passes (`js/terrain-post.js`). | We integrate erosion and sediment over time. They are cruder for the long term (the land is not a conserved mass; erosion is a wear clock) but far better at **fine landform appearance** and at keeping features riding with their plate. |
| Climate | Steady-state seasonal energy balance (`C dT/dt = S(1-a) - (A+BT) + D lap T - gamma u.grad T`) solved by multigrid for the mean and 2 harmonics, on a 1 degree grid (`climate/temperature.js`, `solver.js`). Pressure belts sized by Held-Hou, plus thermal lows and highs (`circulation.js`). Rain from a column-water budget with Bretherton exponential rain, Turc-Pike land evaporation and orographic and rain-shadow effects (`rain.js`). Köppen vs Earth: 49.5% of land cells match (plans/CLIMATE_REBUILD_REPORT.md). | Our climate is similar in spirit (Stommel gyres in `planet/ocean.py` and `climate.py`) and runs on the sim grid with vegetation, clouds, waves and tides. Theirs is a fixed-grid separable solver. |
| Ocean | Stommel/Sverdrup gyres with western boundary currents, circumpolar current, Ekman upwelling, seasonal part for monsoon seas, overturning that gives up heat along its path (`climate/ocean.js`). | Ours has a MOC and Stommel flow law (`planet/ocean.py`) plus salinity, waves, tides. Equal or better. |
| Hydrology and lakes | Priority-flood from the sea, steepest receivers, flat resolution by distance, strait opening, basin filling (`finish/finish-hydro.js`). Sediment fans, floodplains and deltas (`finish-sediment.js`). | Same priority-flood (Barnes) in `planet/hydrology.py`. Ours has discharge in m3/s and salt flats. Equal. |
| Ice | Last ice age only: Ohmura equilibrium-line summer temperature, plastic ice-sheet thickness, U-valleys, fjords, moraines and rebound (`finish/finish-ice.js`). | Ours has a real 1 Myr ice-age time zoom (`planet/timezoom`). Ours is more physical. |
| Geology and resources | The standout. Rock column per cell (cover, burial, exhumation), about 30 mineral systems from source × trap × timing × exposure, gems, districts with stories, "Ages" (Stone to Industrial) reachability (`geology/rocks.js`, `deposits.js`, `ages.js`, `districts.js`, `lithology.js`). Lithology feeds relief (hard ridges, soft vales, soluble limestone by rain and temperature). | We have `planet/resources.py`, `soils.py`, `landform.py`; check them against this. Theirs is far deeper on ore and gem genesis. |
| Fine detail | Tiles at screen resolution: ridges, benches in layered rock, dunes, karst, coves, lakes (`finish/fine-detail.js`, `finish-wind.js`). | Our regional zoom (1-4 km/px) is comparable. |
| Biomes and life | Köppen plus satellite colouring only; no vegetation model. | We are ahead (60 vegetation types, productivity, fire, reefs). |

## Techniques worth borrowing, ranked

1. **Mineral-system / ore-genesis model** (`v2/js/geology/deposits.js`, `ages.js`, `districts.js`, `rocks.js`). It directly serves our culinary-ethnography end goal (what people can mine, which metals, bronze and iron reachability). It maps onto our `planet/resources.py` and `zoom_resources.py`, reading our crust and rock record. It keys off history fields we already have: arcs, sutures, cratons, burial and exhumation. Highest value.
2. **Lithology controls relief** (`geology/lithology.js`, `geology-config.js`). Hard rock stays as ridges, soft rock becomes vales, and limestone is hard when dry and dissolves when wet. We would touch `planet/landform.py`, `zoom_landforms.py`, `zoom_terrain.py` and `zoom_fine_forms.py`, and could use it to make karst belong to wet limestone.
3. **Analytical stream-power solve** (Tzathas et al. 2024, `terrain/carve.js` header). One pass per river tree in place of thousands of explicit steps, with valley widths that scale with the square root of discharge. It could speed up or replace the erosion in `planet/hydrology.py` (`stream_power`) and give cheap, stable carving in the zooms (`zoom_kernels.py`). Check the paper's assumptions (n = 1) against our stream-power exponent first.
4. **Coarse-to-fine river routing**: solve rivers on a coarse mesh and route finer meshes over the finer surface plus the carving found coarser (multigrid-like, `carve.js`). It fits our L7 to zoom refinement (`planet/zoom.py`, `zoom_fine_floodplain.py`), so big rivers stay put and agree across scales.
5. **Antecedent rivers**: rivers routed over the land less their own prior cuts, so they hold their course and cut gorges through rising ranges (`step/rivers.js`). This would touch `planet/hydrology.py` and the run's stepping, and could give Indus/Brahmaputra-style gorges.
6. **Rift location from sutures, failed rifts and a smooth "crust grain" field per plate frame**, instead of straight cuts (`ops/rift-path.js`, `step/rifting.js`). Touches `planet/tectonics/events.py` and `plates.py`.
7. **Passive-margin maturity** `1 - exp(-age/60 Myr)` widens the shelf (about 40 to 180 km) and coastal plain (50 to 240 km) (`terrain` config `marginMatureMyr`). A small rule for `planet/coast.py` and `coastal.py`.
8. **Flood-basalt province shaping**: pile level and feather at the edge, escarpment retreat, mesas, kipukas, dykes (`terrain/lips.js`, `carve.js stripBasalt`). This could improve our `planet/tectonics/volcanism.py` outputs and `zoom_fine_volcano.py` (Deccan and Siberian look).
9. **Planet-relative design points**: Held-Hou Hadley width and a Rossby-radius scale are explicitly planet-dependent (`climate/circulation.js`). That matches our memory note on planet-relative thresholds, so check `planet/climate.py` against it.
10. **Engineering patterns**: exact-hash performance work (before and after hashes of event log and frames), a generator step loop that farms rifts out to helper workers (`simulate.js stepsOf`), and the GPU painting of cell values as a data texture (`view/gpu-paint.js`). These apply to our viewer and to run-time speed, not to the physics.

## Caveats
- Their README and CLAUDE.md say aesthetics come first and accuracy is secondary. The climate is tuned on Köppen match to Earth (49.5%), which our own rules treat with caution; their mechanisms are sound, but the tuning targets are Earth-shaped.
- Heights are not mass-conserving, so their erosion and sediment do not close a budget; do not borrow that part.
- GPL-3.0 applies to any code copied.
