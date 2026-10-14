# procgen_world code review (commit 59547e7)

Read-only review of `planet/`, `tools/`, `tests/`, and `viewer/`. I profiled a level-5 run (100 Myr), a level-6 run (64 Myr), one level-6 `climate.compute`, `world_from_sim`, and a 1000 km / 2 km zoom. Line numbers refer to 59547e7.

Two terms used below:
- **"No output change"**: the refactor should be bit-identical for seeded runs. Check it with the golden test proposed in item 1.
- **"Changes outputs"**: seeded runs produce different worlds, and stored runs no longer replay to their keyframes.

Conflicts with in-flight work are tagged:
- **[A]**: viewer panel/tilt/zoom API (`viewer/*`, the `Handler` in `__main__.py`)
- **[B]**: ocean currents/winds/rain (`climate.py`)
- **[C]**: new `planet/timezoom.py`

---

## Do these first (top 5)

1. **Golden-output tests, and a model version stamped into each run** (item 1). Without these, no refactor below can be shown to preserve outputs. Old runs already don't replay (see Bug 1). S–M, no output change, no conflicts.
2. **Speed up the climate kernels, which take about two-thirds of simulation time at level 6, plus `locate`** (items 9 and 10). Parallel gather loops whose sums run in the original edge order give bit-identical results. `locate` can be done now. The climate kernels touch [B], so do them after [B] lands. Expect roughly 1.5–2× faster runs overall. M.
3. **One storage module, `planet/store.py`** (item 3): a configurable data root, one binary-layer writer and reader shared by runs, zooms and timezoom, find/delete/index for all three kinds, legends, and memmap reads. This removes about 150 duplicated lines and lets the API tests from plan item 3 run against a temp directory. M, no output change. It conflicts with [A] and [C], so either give [C] the helper now or do it right after both land.
4. **Break up `Simulation._physics` (230 lines) and `tectonics.py` (1600 lines)** (item 4). Initialise all state in `__post_init__` and remove the aliased arrays. Keep the RNG call order so it stays bit-identical. M, no output change. It touches [C] only through attribute names, so agree the accessors first.
5. **Simulation checkpoints, so slicing at time t doesn't replay from 0** (item 5). Today a level-6 slice costs 10–60 s, and both plan item 3 (`/api/zoom`) and item 6 (timezoom) need state at time t. M, no output change. Coordinate with [A] and [C].

## Outright bugs and latent hazards

| # | Where | What | Impact |
|---|---|---|---|
| B1 | `timeline.replay` / `slice_world` (timeline.py:249-277) | Replay rebuilds the run with *today's* code and `Params(**m["params"])`. Missing params silently take current defaults. Nothing records which code made the run. When the keyframe doesn't match, it only prints `DOES NOT match` and then saves a world labelled "`<run> @ t`" anyway. Of the 16 runs in `runs/`, 9 were created before params added since (35 params missing in 4 runs, 7 in 5), so they cannot replay identically. The "kept so older runs replay" param (`ocean_ref_age`, tectonics.py:118) gives a false sense of compatibility. | Worlds and zooms sliced from older runs don't show what the viewer showed. Fix: item 1. |
| B2 | tectonics.py:1456 | `lab[g.nbr_idx[g.nbr_off[:-1]]]` looks only at each cell's *first* neighbour, so `edge` (where a "subduction starts" event is logged) is an arbitrary subset of the coast. | Only the logged lat/lon of margin-subduction events. The fix changes `events` in run.json, which `test_deterministic` compares. |
| B3 | tectonics.py:557 | `self.removed = self.flow = self.stacked = np.zeros(n)` makes three names point at one array. It's harmless today only because each is reassigned before any in-place write (`stacked` at :685, before `_resolve` writes into it). | Latent. If anything writes in place first, it silently corrupts the others. Create three arrays. No output change. |
| B4 | tectonics.py:930, 1077, 1089, 1561, 1565 | State is created lazily (`self.veg`, `self.co2`, `self.chem`, `self.w_trench`, `self.w_boundary`, `self.newest`, `self.cell_torque`), with `getattr(self, "veg", 0.0)` defaults scattered around. | Fragile, and it hides the state list that [C] and checkpointing need. Initialise all of it in `__post_init__` with the current defaults. No output change. |
| B5 | `tests/test_envelopes.py:63`, `tools/scorecard.py:32`, `tools/earth_check.py:251` | Three different "Earth Koppen group agreement" numbers. The test and scorecard count cells, unweighted, with lat > -60. `earth_check` is area-weighted and excludes cells with no observation. plan_next compares "~68%" against "test floor 66%", which may be two different metrics. | Calibration decisions rest on a number with an unclear definition. Use one function (item 13). |
| B6 | `__main__.py:113-120` → `timeline.delete` | `DELETE /runs/<id>` and `DELETE /worlds/<id>` both delete *both* the run and the world with that id, because `m.group(1)` is ignored. Zooms can't be deleted, and deleting a world orphans its zooms. | Low, since ids are random. Fix in `store.delete(kind, id)`. Touches [A]. |
| B7 | viewer/index.html:735 | The run loader fetches the whole `frames.bin`: 390–493 MB for the stored 2000 Myr runs, and about 4× that at level 7. It holds all of it in tab memory, even though at most 2–3 layers are drawn. | Slow loads; level-7 or long runs may crash the tab. See item 6. Touches [A]. |
| B8 | zoom.py:475 vs the docstring at :6-7 | The docstring says overlapping zooms share detail, but drainage tie-break `jitter` is seeded per *pixel index* (`default_rng(seed).random(npx)`), not per position. Flats drain differently in overlapping zooms. | Minor. Hash the jitter from position (e.g. `ZK.fbm`-style hash of `Pk`). Changes zoom outputs only. |
| B9 | `tests/test_invariants.py:102` | `z["elevation"] if "elevation" in z else z["layers"]["elevation"]`: the first branch can never be taken. | Dead test code. |
| B10 | tectonics.py:1098 | The docstring says sea level is measured from "exponentially distributed ages (mean `p.ocean_ref_age`)". Not true any more: the parameter is unused (only this comment mentions it). | Stale doc. Delete the param and the comment (item 2). |

---

## Prioritised suggestions

### P1: foundations (do before refactoring anything)

#### 1. Golden-output regression tests and run provenance
- **Where:** `tests/` (new `tests/test_golden.py` and `tests/golden/*.json`); `timeline.simulate` meta (timeline.py:154); `slice_world` (timeline.py:258-277).
- **Why:** Most suggestions here claim "no output change". The only guard today is `test_deterministic`, which checks that two runs agree with each other, not with a reference. Replay correctness also silently depends on code version (B1).
- **Change:**
  - **Golden test.** Store SHA-256 hashes, or a few summary floats plus a hash, of `w_elev`, `w_thick`, `w_age`, `owner`, `precip`, `temp`, the events list, and `budget`. Take them after `run_sim(level=4, seed=1, myr=60)` and after one `climate.compute` on a fixed level-4 elevation. Add a `--update-golden` option in `conftest.py`. A commit that intends to change outputs regenerates the hashes, and the diff shows it.
  - **Provenance.** Write `"code": {"commit": ..., "dirty": bool, "planet_src_sha": <hash of planet/*.py>}` into `run.json` meta, the same thing `scorecard.py` does. `slice` compares it: on a mismatch it warns before the 10–60 s replay. When the keyframe doesn't match, record `"replay_matches_keyframe": false` in the world meta and print a loud warning, or refuse unless `--force`.
  - **Policy (owner's call).** Keep "kept for replay" params only while the source hash is unchanged. Otherwise drop them, since exact replay already requires the same code.
- **Effort:** S–M. **Risk:** no output change. **Conflicts:** none. [C] should stamp the same provenance on timezoom runs.

#### 2. Remove dead code and params
- **Where:**
  - `Params.ocean_ref_age` (tectonics.py:118)
  - `climate.precipitation()` (climate.py:600-606), which has no callers
  - unused default arguments of `climate.temperature` / `sea_temperature` (callers always pass them)
  - the dead test branch (B9)
  - `test_envelopes` builds `sim.snapshot()` only for `koppen`
- **Possibly retire (ask the owner):** the one-shot `generate` command, `generators.py` (168 lines, with its own Python BFS at :131-142 and its own `smooth` at :23), and `hydrology.erode` (hydrology.py:32), which is only used by `world.finish` after `generate`/`slice`. If `generate` is gone, `finish` only needs the light valley-sharpening pass.
- **Effort:** S. **Risk:** removing `ocean_ref_age` makes `Params(**old_params)` raise for old runs. Have `make_params`/`replay` drop unknown keys with a warning, which is also what replay of future-removed params needs. **Conflicts:** `climate.py` lines are in [B]'s file, so do it after [B].

#### 3. One storage layer: `planet/store.py`
- **Where:**
  - `timeline.simulate` frames writer (:136-148) and `timeline.load_frames` (:172-180)
  - `zoom.save` writer (:711-721) and `zoom.load` (:773-783)
  - three `update_index` functions (timeline.py:337, world.py:339, zoom.py:786)
  - `find_run` (timeline.py:312) and `find_world` (zoom.py:154)
  - `timeline.delete` (:321)
  - `W.ROOT` hard-coded (world.py:33)
  - legends built three times (timeline.py:160 and :303, zoom.py:761)
  - lat/lon list conversion done twice (timeline.write_grid :92, world.save :298)
- **Why:** [C] will add a fourth copy, since its output is in "run format". Plan item 3 asks for handler tests "without a socket", which needs a data root that isn't the repo. The per-kind code paths have drifted (B6, B7).
- **Change:**
  - `store.write_layers(path, {name: array})` and `store.read_layers(path, layout, mmap=True)`. Use `np.memmap` or `np.frombuffer` on an mmap: `slice` and `report` read 1–3 layers out of 500 MB files.
  - `store.root()`, taken from an env var such as `PLANET_DATA` with the repo as default, and passed down. Optionally a contextvar for tests.
  - `store.find(kind, ref)`, `store.delete(kind, id)` (cascading to zooms, or warning), and `store.update_index(kind)`.
  - `store.legends()`, returning rocks, koppen and biomes once.
  - Have `timeline.update_index` read only a small header rather than json-parsing every whole `run.json`, as worlds already do. It re-parses up to ~2 MB per run on every `list`, `serve` and `delete`.
- **Effort:** M. **Risk:** no numeric change. The on-disk format can stay byte-identical. **Conflicts:** [A] (the handler calls `T.delete` / `update_index`) and [C] (its run writer). Best handed to [C] as a helper now, or done right after [A] and [C] merge.

### P2: structure and readability

#### 4. Split `tectonics.py` and `Simulation._physics`
- **Where:**
  - `_physics` (tectonics.py:760-992, about 230 lines doing arcs, rift stretching, plumes, ageing, volcano caps, collision stacking, accretion, subduction erosion, arc rock, volcanoes, thinning, rifted margins, crustal flow, orogeny, global temperature, climate, glacial/vegetation erodibility, erosion, sediments, reefs, chemistry, crust birth, rock age, cratons, clipping, write-back, boundary/trench snapshot)
  - about 70 instance attributes
  - 13 numba kernels and helpers mixed in with the class
- **Change** (pure moves, keeping every RNG draw in the same order):
  - `tectonics/kernels.py`: `_fill`, `_resolve`, `_crust_flow`, `_cleanup_ghosts`, `_components`.
  - `tectonics/crust.py`: `isostasy`, `elevation`, `ocean_depth`, and the constants (`OCEAN_KM`, `ISO_*`, `EXTRA`).
  - `tectonics/events.py`: `_sutures`, `_absorb_slivers`, `_maybe_rift`, `_stress_cut`, `_rift_side`, `_split`, `_merge`. These can be free functions taking `sim`.
  - `tectonics/earth_system.py`: `_global_temperature`, `_climate`, `heat`, `target_fraction`.
  - Make `_physics` a short sequence of named substeps: `_arc_growth`, `_plumes`, `_accrete`, `_subduction_erosion`, `_stretch_and_margins`, `_crust_flow_and_orogeny`, `_surface`, `_reefs_and_chem`, `_birth_and_cratons`, `_write_back`. Each takes and returns a small `CrustState(t, cover, x, cont, rock)` dataclass rather than threading six local arrays through. Each keeps its `_book(...)` call next to the change it books.
  - Group the plate-frame arrays (`owned, age, thick, cont, rock, cover, extra, idx, Q, omega, mantle, alive, label`) into a `Plates` struct, and the `w_*` view into a `WorldView`. That makes `_merge`/`_split`'s "for arr in (...)" loops (:1292, :1536) one method each, and gives a clear state to checkpoint (item 5).
  - Fix B3 and B4 along the way.
- **Effort:** M–L, best done in 3–4 commits with the golden test green after each. **Risk:** no output change if the RNG call order (`_hotspots` → `_volcanoes` → `_global_temperature` inside `_physics`, then `_forces`, then `_maybe_rift`) and the floating-point evaluation order are kept. Don't "simplify" expressions like `t + growth*dt + plume*dt` in the same commit. **Conflicts:** [C] reads sim state (`w_elev`, `ice`, `w_cont`, `sea_level`, `dT`, …). Agree a stable accessor such as `sim.snapshot()` / `sim.world_state()` with [C] first, and keep attribute aliases for one cycle.

#### 5. Checkpoints for fast slicing
- **Where:** `timeline.replay` (:249). [A]'s `/api/zoom` and [C]'s `timezoom --at` both need the state at time t.
- **Why:** At level 6 a slice replays up to 1000 steps (10–60 s). The plan works around this with a cache keyed by (run, t).
- **Change:** During `simulate`, every K Myr (e.g. 100), write `runs/<id>/state/<t>.npz`. Store only the alive plates' arrays, compacted to owned cells (about 4–5 MB at level 6, versus about 160 MB for the full P_MAX arrays), plus the scalar and list state: hotspots, volcanoes, contact/closing matrices, budget, refs, drift, dT, sea level, climate fields. RNG needs no state, because per-step RNG is `default_rng([seed, step])`. `replay` then loads the nearest checkpoint at or before t and steps forward. Test: replay from a checkpoint must equal a full replay (golden-style).
- **Effort:** M (much easier after item 4). **Risk:** no output change, provided all state is captured. The test proves it, and B4's lazy attributes are the trap. **Conflicts:** [A] (it can drop its slice cache) and [C] (its entry point).

#### 6. Run file layout: one file per layer, and encodings in metadata
- **Where:** `timeline.LAYERS` and `keep` (timeline.py:35-55, 116-127) hard-code the quantisation (cover ×10, ice /20, flow 16·log2(1+x), wind/current ×50). The viewer decodes the same constants by hand (`index.html:227, 653, 659`, plus wind and flow elsewhere).
- **Change:**
  - Put `{"dtype", "scale", "offset", "transform": "log2p1"|null, "units"}` in `run.json["layers"]`. Python and JS then share one decoder, and new layers ([B]'s jet stream `jet_e/jet_n`, [C]'s ice thickness) are added only in Python.
  - Write `frames/<layer>.bin` (or keep `frames.bin` and have the viewer use HTTP Range requests) so the viewer fetches only the layers being drawn (fixes B7). `SimpleHTTPRequestHandler` doesn't serve Range, so per-layer files are the simpler route.
- **Effort:** M. **Risk:** a format change. Keep the reader accepting the old single-file layout (`layout` present → old path). No simulation output change. **Conflicts:** [A] (viewer loader) and [B] (new wind and jet layers). Ideally [B] adds its layers through this metadata, so agree on it before they add layers.

#### 7. Consistent layer names across runs, worlds and zooms
- **Where:**
  - run frames: `continental, age, boundary, precip, surface, cover, thickness, down`
  - worlds: `crust, crust_age, plate_boundary, precipitation, surface_rock, sediment_cover, crust_thickness, downstream`
  - zooms: `precipitation, surface_rock, climate`
- **Why:** The viewer translates by hand (`setFrame`, index.html:755-758), and `zoom.build` uses `L.get(...)` with fallbacks (zoom.py:212, 214, 218, 222, 431, 432).
- **Change:** Pick one vocabulary, for example the world names. Define it once in `store.LAYERS` (name → dtype, encoding, units, description; zoom's `LAYER_DOC` is the right idea) and add an alias map on load for old files.
- **Effort:** M. **Risk:** a format change. Old files are handled with aliases. No numeric change. **Conflicts:** [A]. Do it together with item 6.

#### 8. Split `world.py`, `timeline.py` and `__main__.py` by responsibility
- **`world.py`** currently mixes the pipeline (`generate`, `finish`), summaries (`landmasses`, a Python BFS duplicating `tectonics._components`), ASCII rendering, and JSON I/O.
  - Move to `pipeline.py` (`finish`), `report.py` (summaries, `ascii_map`, `text_report`, and timeline's `report`), and `store.py` (item 3).
  - Make `landmasses` call `grid.components(mask)`.
  - `cmd_generate` re-reads the 9 MB world it just wrote to get the summary (`__main__.py:39`). Have `save` return the summary.
- **`timeline.py`** currently mixes simulate, storage, report, replay, slice, delete and index. Move to `runs.py` (simulate, keyframe encoding, replay/slice), `report.py`, and `store.py`.
- **`__main__.py`:** move `Handler` into `planet/server.py`, with plain functions `api_zoom(store, req) -> dict` that tests can call without a socket. That matches the plan's test requirement.
  - Use `http.server.ThreadingHTTPServer`. Today's single-threaded `TCPServer` (`__main__.py:131`) blocks all static file serving while a long `/api/zoom` request runs.
- **Effort:** M. **Risk:** no output change. **Conflicts:** [A] is editing the `Handler` right now. Suggest [A] create `server.py` themselves.

#### 9. Shared geometry helpers on `Grid` (dedupe)
Duplicated idioms:
- `R_KM = 6371` is defined 5 times (tectonics.py:56, surface.py:61, climate.py:36, zoom.py:81, world.py:35).
- xyz → lat/lon appears 6 times (grid.py:58, world.py:299, timeline.py:92, tectonics.py:493, zoom.py:123, world.nearest_cell_map).
- The "boundary cells of a mask" idiom, `np.add.reduceat(~m[g.nbr_idx], g.nbr_off[:-1]) > 0`, appears at tectonics.py:1127, climate.py:80 and :360; `_sediments` (:1050) uses a variant, and `_initial_state` (:625) does it with a Python list comprehension.
- Connected components / BFS has 5 implementations: `kernels.bfs_within`, `tectonics._components`, `world.landmasses` (Python), `generators` (Python deque), and `zoom_kernels.label_components` (raster).
- Neighbour-diffusion loops have 5 variants: `surface._spread`, `tectonics._crust_flow`, `climate._smooth`, `generators.smooth`, and the creep in `hydrology.erode`.
- Local east/north frames are built in `climate._geom`, `timeline.report` (:232-236) and `zoom.Frame`.
- `cell_areas` lives in `tools/earth_check.py:188` but is grid geometry.
- The PNG writer and `_ramp` exist in both `zoom.py` and `earth_check.py`.

Change:
- Create `planet/geo.py` with `R_KM`, `xyz_to_latlon`, `latlon_to_xyz`, and `local_frame`.
- Add methods and cached properties to `Grid`: `lat`, `lon`, `spacing`, `pentagons`, `east`, `north`, directed `src`/`dst`/`d`, `deg` (move `_geom` here), `cell_areas`, `boundary(mask)`, `components(mask)`, `nbr_mean(f)`.
- Put `@functools.lru_cache` on `build_grid(level)`. It's called 7 times in `planet/` plus once per climate coarse grid. At level 6 it takes 0.11 s and at level 7 0.5 s per call, which matters for the API server. Make the cached arrays read-only (`arr.flags.writeable = False`) so nothing mutates shared state.
- Move the PNG writer to `planet/images.py`.

**Effort:** M, in many small commits. **Risk:** no output change as long as each replacement is the same arithmetic. A one-line Python BFS replaced with the numba one gives the same labels, but the labelling order must match for `landmasses` names A/B/C: both sort by size afterwards, but ties could reorder. Check it against the golden test. **Conflicts:** `climate._geom` is in [B]'s file, so do the `climate.py` part after [B].

#### 10. Magic numbers into named constants or params
- **Where:**
  - `_physics`: `23.0` (rift "fresh" thickness, :801), `22`/`22.0` (thinning floor, :894-896), `15.0` (worn-out edge, :878), `2000/3000` (volcano head, :826), `0.1`/`0.15`/`0.2` (arc, volcano and hotspot rock thresholds, :889, :1173, :899), `50`/`45` (orogen and craton thickness, :917, :969), `-350`/`-4000` (trench, :991-992)
  - `_rifted_margin`: `100.0` Myr pool decay (:1004)
  - `_sutures` and `_split`: `80`, `40` Myr lockouts, `2.5` cm/yr push, `4.0` mantle seed (:1314, :1332, :1542, :1546)
  - `_climate`: ice profile `300 + 2700·(1-e^{-d/600})` (:1130)
  - `_global_temperature`: `0.06`, `0.5`, `20.0`, `200/300/10/5` Myr time constants, `±250` m (:1076-1112)
  - `_hotspots`: 150 km radius, ×4 head for 6 Myr, 1000 m dome (:1215-1222)
  - reefs: `-5`, `-1500`, `150` (:947-948)
  - `climate.compute`: `27.8/-10.4`, `0.5/1.5·dT`, `0.3·tilt_adj`, `-0.8/+2.9`, `3.0·t_ice`, `0.03` wetness (:828-897)
  - `climate.currents`: `45/80/3`, `1.5`, `0.45/0.3` (:369-373)
  - `_season_inputs`: `25`, `9`, `70/15`, `0.3` (:555-558)
- **Why:** Some of these are physics the owner may want to tune (pole temperature, ice profile, lockouts). Others are numerics. `TUNE` exists for climate but isn't reachable from a run: `Simulation._climate` never passes `tune=`. So climate tuning can't be recorded in run.json, and changing `TUNE` silently changes replay of every run (part of B1).
- **Change:**
  - Leave numerics as module constants with a comment.
  - Put physics knobs into `Params`, or a nested `ClimateTune` that `Params` carries, so run.json records them. Defaults stay equal to today's literals.
  - Pass `tune` from `Simulation._climate`.
  - Note: every new `Params` field adds to `run.json`, and old runs replay with the default, which is the same literal. That's fine.
- **Effort:** M. **Risk:** no output change if the values are identical, but beware `float` vs `int` literals in numba-typed code. **Conflicts:** the `climate.py` parts belong to [B]. Ask [B] to name new constants in `TUNE` as they go.

#### 11. Break up `zoom.build` (395 lines)
- **Where:** zoom.py:178-571.
- **Change:** Split it into stage functions with explicit inputs: `_coarse_fields`, `_coastline`, `_detail`, `_hold_cell_means`, `_coarse_rivers`, `_categorical`, `_lakes`, `_landscape`, `_final_drainage`, `_fine_climate`, `_stats`. Also:
  - `RUGGED` (zoom.py:86) only covers rock ids 0–5; ids 6–10 fall back to 0.5 silently. Move ruggedness into `surface.ROCKS` as a column next to erodibility.
  - `SEA_CLIMATE = 30` duplicates `climate.SEA_CLASS`.
- **Effort:** M. **Risk:** no output change. **Conflicts:** [A] calls `zoom.zoom()`/`build()` only through their signatures; keep those.

#### 12. Tests: organisation and coverage
- Add the golden test (item 1) and a checkpoint-equals-full-replay test (item 5).
- Add one disk round-trip test (`simulate` → `slice` at a keyframe must match → `zoom` → `load`) under a temp `PLANET_DATA` root (needs item 3).
- Share the Earth-score function (item 13) between `test_earth_climate_score`, `scorecard.py`, and `earth_check.py`.
- `conftest.py` adds `tests` to the path via `pythonpath = [".", "tests"]` so it can `from conftest import run_sim`. Use fixtures, or move helpers to `tests/helpers.py`.
- Make the envelope sims (`level=5, seeds 1-2, 400 Myr`) a session fixture so `scorecard` or other slow tests can reuse them.
- **Effort:** S–M. **Risk:** none. **Conflicts:** none. [C]'s tests should follow the same pattern.

#### 13. One Earth-score definition
- **Where:** B5.
- **Change:** Add `tools/earth_data.score(grid, climate_out, obs) -> dict` with both `group_agree_cells` and `group_agree_area`, named explicitly. The test and scorecard import it. State in plan_next which metric the 66% and 68% floors refer to.
- **Effort:** S. **Risk:** none. **Conflicts:** [B] uses this score to judge its changes, so tell [B] which number is which before they compare.

### P3: efficiency

Measured at level 6 (64 Myr, 32 steps, 11.0 s):
- `climate.rain`: 3.5 s
- `climate.smooth`: 2.7 s
- `climate.carry`: 0.95 s
- `grid.locate`: 0.8 s
- `np.ufunc.at`: 0.34 s
- `surface.erode`: 0.47 s
- `_world_view`: 0.25 s
- everything else, including the numba `_resolve`: under 1 s

One `climate.compute` takes 0.9 s and runs every 4 steps, so climate is about 68% of sim time. At level 5, climate is 1.3 of 2.8 s. A 1000 km × 2 km zoom takes 1.2 s and `world_from_sim` 2.1 s, so neither is a priority.

#### 14. Parallel climate kernels, bit-identical *(after [B])*
- **Where:** `_smooth` (climate.py:182), `_relax_along` (:225), `_rain` (:429). `_coarse_smooth` is cheap.
- **Change:**
  - `_smooth` is already Jacobi-style (reads `f`, writes `g`). Make the cell loop `prange`. The result is identical because each cell sums its own neighbours in the same order.
  - `_relax_along` and `_rain` scatter along edges (`num[dst[e]] += …`, `moved[dst[e]] += …`). Precompute an *incoming* CSR per cell with the edges sorted by original edge index `e`, then gather in a `prange` over cells. Starting from the same initial value and adding in increasing `e` order gives bit-identical sums.
  - In `_rain`, keep the `tot` reduction (:460-464) serial: a parallel float reduction depends on thread count.
  - Expect 3–6× on these kernels with 8 cores, so about 1.5–2× on the whole simulation.
- **Effort:** M. **Risk:** no output change if the summation order is preserved; verify with the golden test. **Conflicts:** [B] is rewriting currents and rain, so do this after [B] merges, and tell [B] to write any new relaxation or streamfunction solver gather-style from the start.

#### 15. Cheaper large-scale smoothing *(after [B])*
- **Where:** `smooth(…, km)` runs `4·(km/h)²` full-grid Jacobi sweeps. At level 6 that is 270 sweeps for 900 km and 480 for 1200 km, and 4× more at level 7.
  - `_season_inputs` smooths `t_sl` over 800 km and `zs` (a function of latitude only) over 800 km, per season (:544, :570).
  - `currents` smooths `ocean` over 1200 km (:370).
  - `monsoon_wind` smooths over 900 km (:319).
- **Change:**
  - For km ≳ 4 cells, use the existing coarse-grid `smooth_big` path, or a 2-level restrict–blur–prolong. For the purely zonal `zs`, smooth the 1-D band profile with `np.convolve` instead.
  - Also compute `smooth(grid, ocean, 1200)`, `_geom`, and the `zonal_mean` bins once per `compute`, not per call.
- **Effort:** S–M. **Risk:** changes outputs slightly (a different smoothing kernel), so re-run `earth_check` and the scorecard. **Conflicts:** [B]. Offer it to them as part of their runtime budget (plan says `compute` ≤ 1.5 s).

#### 16. Parallel `locate`, now
- **Where:** `kernels.locate` (kernels.py:121), called 12× per step from `step` (tectonics.py:681) and in `_merge`/`_rift_side`.
- **Change:** `@njit(cache=True, parallel=True)` with `prange` over points. Each point's walk is independent and pure, so the result is identical. About 7% of runtime.
- Further option: locate only each plate's *owned-near-world* cells instead of all n per plate (`g.centers @ Q[k]` for all n). That is an algorithmic change in what `idx` holds for unowned cells, which `_resolve`'s gap filling reads, so it could change outputs. Not recommended now.
- **Effort:** S. **Risk:** no output change. **Conflicts:** none.

#### 17. Small numpy wins, output-neutral
- Replace `np.add.at` with `np.bincount` per component in `climate.gradient` (:208) and `_forces` (:1235-1254, including the (n,3,3) `outer` → 9 bincounts or one numba loop). It also appears in `_sutures` (:1309, :1326) and `_physics` accretion (:858). 0.34 s at level 6.
  - `bincount` accumulates in index order in float64, the same as `add.at`. It's almost always bit-identical, but verify with the golden test.
- Make `Grid.lat/lon/spacing/pentagons` cached properties. They're recomputed about 300 times per 64 Myr; `spacing` alone takes 0.15 s.
- Set `P_MAX` per run to `max_plates + 2` instead of 48. `extra` alone is 48×n×6×8 B = 94 MB at level 6 and 378 MB at level 7. Slot choice is "first dead slot", so this is output-neutral while `max_plates < P_MAX`.
- `_resolve` allocates `q = np.empty(3)` inside a loop (tectonics.py:339). Hoist it.
- `slice_world` calls `sim.snapshot()` twice (timeline.py:267 and, via `world_from_sim`, :283).
- `load_frames` reads the entire 100–500 MB `frames.bin` to compare one keyframe and draw five ASCII maps. Use memmap (item 3).
- `write_grid` reads the whole grid file on every simulate just to check for `'"nbr"'` (timeline.py:90). Check the size or a version key instead.
- **Effort:** S each. **Risk:** none except the `bincount` caveat. **Conflicts:** `climate.gradient` is in [B]'s file.

#### 18. Worlds embed the full grid: 53% of each 9 MB world file
- **Where:** `world.save` (world.py:302-321) writes lat/lon/corners/cells/neighbors (about 4.85 MB at level 6) into every world, while runs reference the shared `grids/L6.json`. Worlds also store `_plate_velocity` as an (n,3) float list (0.85 MB).
- **Change:** Write `"grid": "../grids/L6.json"`, as runs do, and have the viewer accept either. `W.load` already rebuilds the grid and ignores the stored one. Round or quantise layers stored as floats (`warm_month`, `cold_month`, `plate_speed`, `crust_age`, …) to 1 decimal.
- **Effort:** S–M. **Risk:** a format change, so keep the reader backward-compatible. No sim change. **Conflicts:** [A] (viewer `setWorld`).

#### 19. Duplicate noise implementations
- **Where:** `noise.Perlin3D` (numpy, 256-period permutation table) is used by the tectonic initial state, rifts and the slice texture. `zoom_kernels.noise3` (numba, hashed lattice, parallel) is used by zoom.
- **Change:** Long term, use one numba noise. Swapping it changes every seeded world, so bundle it with a deliberate "model v2" bump, or not at all. Short term, leave it alone; it's only 0.26 s per 64 Myr.
- **Effort:** S to write, but large in consequence. **Risk:** changes all outputs. **Conflicts:** none.

---

## Sequencing summary

| Can do now (no conflict) | After [A] (viewer/server) | After [B] (climate) | Coordinate with [C] (timezoom) |
|---|---|---|---|
| 1 golden tests + provenance, 2 dead code (non-climate), 12 tests, 13 Earth-score helper, 16 parallel `locate`, 17 (non-climate parts), B2–B4, B9 | 3 store (handler side), 6 layer files + encoding metadata, 7 layer names, 8 `server.py` + ThreadingHTTPServer, 18 world grid reference, B6, B7 | 9 (`climate._geom` part), 10 (climate constants), 14 parallel climate kernels, 15 smoothing, 2 (`precipitation()`), 17 `gradient` | 3 shared layer writer and provenance, 4 sim-state accessors, 5 checkpoints (shared entry point) |

Items 4 and 11 (splitting `tectonics.py` and `zoom.build`) don't conflict at file level with [A] or [B]. Item 4 needs the [C] accessor agreement first.
