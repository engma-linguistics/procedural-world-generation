# Physics audit (PW-245): surface and hydrology

Scope: `planet/surface.py`, `planet/hydrology.py`, the routing / lake / priority-flood / stream-power kernels in
`planet/kernels.py`, the erosion and sediment parts of the run step (`planet/tectonics/earth.py` `erode`,
`sediments`, `reefs`, `bury`), and the finishing erosion (`hydrology.erode` via `world.finish`, `timeline.texture`).

Graded on the owner's axis: **sound approximation** (crude, but has a physical basis) or **bandaid** (forces an
answer, hides a process error, or works only on Earth). Short version: no Earth-keyed, latitude-keyed or
region-keyed branches, and no clamps that hold lakes, basins or relief inside a target range. The sediment budget
balances exactly. The real problems: one erosion term that claims to be resolution-independent but isn't, one
deposition rule that ignores how much room a basin has, and a finishing pass that removes rock and puts it
nowhere.

## Measurements (scratch scripts, not committed)

- `budget.py`: wraps `surface.erode` on an L5 run, seed 1, 200 Myr (100 steps).
- `probe.py`: the same over 300 Myr (150 steps), plus overfill, mounds, chemical additions, base level and
  world erosion.
- `levels.py`, `levels2.py`: one smooth synthetic continent (fixed-frequency noise) at L5, L6 and L7.

| Check | Result |
|---|---|
| Sediment, cell sums: Σ removed vs Σ deposited per step | equal to 4e-16 (exact) |
| The same weighted by cell area (cells are 0.67–1.21× the mean area) | +0.8% over the run, −1.2…+2.6% per step |
| Negative deposits | none |
| Open-lake cells raised above the lake surface | 0 of 1616 cell-steps |
| Closed-lake cells raised > 1 m above the lake surface | **587 of 2294 cell-steps (26%), up to 1213 m** |
| Deposition that lands above a closed lake's level | 2.0% of all deposition |
| Reefs plus chemical deposits added (not taken from the dissolved load) | 5.5% of the eroded volume |
| Weathering with base level 0 instead of 200 m on continents | ×1.45 |
| `rain_factor` at its floor / its cap | 17.8% / 7.2% of land cell-steps |
| Run hillslope term, one step, synthetic continent, L5/L6/L7 | **0.67 / 1.34 / 2.48 m** |
| Run incision term, the same | 2.38 / 1.56 / 1.04 m |
| World erosion at strength 0.3, L5 run end | land lowered 46 m on average (p99 338 m), **none of it deposited** |
| World erosion, synthetic continent, L5/L6/L7 | 33 / 33 / 39 m (without the `2**(level-5)` factor: 33 / 16 / 9 m) |

## Findings, by severity

### 1. MED: the hillslope term is not a diffusion and doubles with each grid level
`surface.py:242-246` (docstring at `surface.py:12-16`). The code multiplies `_relief`, the mean of the
*one-sided* drops to the lower neighbours, by `4·κ·dt/d²` and says this is "the Laplacian on this grid … the same at
any resolution". It isn't. A one-sided mean drop is first order: on a uniform slope it equals about slope × d, while
a real Laplacian there is zero. So the lowering scales as slope/d. Measured on the same terrain, it goes
0.67 → 1.34 → 2.48 m per step from L5 to L7. Incision goes the other way (2.38 → 1.56 → 1.04 m; the
stream-power factor `incision·√flow·dt` is consistent along channels but not on hillslope cells). At L5 erosion
is mostly incision; at L7 it is mostly hillslope wear. The level-5-tuned `hillslope = 100 km²/Myr` is 2× too strong
at L6 and 4× too strong at L7.
- **Grade: unsound** (a mislabelled law with a false resolution claim), not a bandaid. Ahnert's "denudation ∝ local
  relief" is a fine law in itself.
- **Likely link: PW-243.** The L6/L7 difference in closed basins could come partly from L6 and L7 wearing their
  terrain with a different mix of terms, not only from `MIN_DEPTH`.
- **Simplest sound fix:** make it a slope law, `Δh = κ' · K · (relief / d) · dt` (relief / d is the mean downhill
  slope), with κ' set so that L6 is unchanged. L7 hillslope wear then halves. Expect a little more relief at L7
  and a shift in its closed-basin share; rerun the scorecard and the PW-243 measurement at L6 and L7.

### 2. MED: closed lakes spread their whole inflow over their floor, whatever room they have
`surface.py:276-281`. Rivers end at a closed lake (`route` makes its cells outlets), so `_route` drops all of their
remaining load there. The spread `dep ∝ depth + 1` is never capped at the lake's room. In 26% of closed-lake
cell-steps the floor ends up more than 1 m above the lake surface, at worst 1.2 km. That is 2% of all deposition.
Mass is conserved, but a closed basin that has filled turns into a sediment mound instead of overflowing. On Earth
a basin fills to its spill point and the river then carries the rest on: an endorheic basin becomes exorheic.
Open lakes are capped correctly (`pool_room`).
- **Grade: unsound** (a missing cap), not a target-chasing bandaid.
- **Relation to PW-054:** this is not the cause of basin loss (the basin is full either way), but it makes
  filled basins into bumps that can dam their neighbours.
- **Simplest sound fix:** cap closed-lake deposition at its room (`pit_room` summed over the lake, as for open lakes).
  Hand the excess to the lake's spill cell, or leave it on the lowest rim cell, so the basin opens next step.

### 3. LOW-MED: the finishing erosion deletes rock instead of moving it
`hydrology.py:43-74`, called from `world.py:83`. Twelve passes of stream-power cutting plus a creep that only
lowers ground. The removed material is never deposited. At strength 0.3, land drops 46 m on average (p99 338 m),
and 137 m at strength 1.0 (`planet generate`). The one-sided creep was chosen in PW-057 so that finishing keeps
the keyframe's lakes (a Jaccard metric). It does that by not filling hollows, not by modelling where creep
material goes. That is close to the "mask instead of process" pattern, although the stated reason (the keyframe is
already worn, its basins are real) is fair.

Checked and fine: the `2**(level-5)` factor at `hydrology.py:54` is old and its comment is muddled, but measured
it keeps the mean lowering level-consistent (33 / 33 / 39 m). Without it the cutting would fall 33 / 16 / 9 m, so
it is a sound empirical scale.
- **Grade: bandaid-ish.** It is harmless for display, but it lowers rims and peaks with no sink for the rock.
- **Simplest sound fix:** route the removed material with the run's `surface._route` (pits and lakes keep what
  fits, the rest goes to the sea) and drop it at land and coast cells. Or keep it as is and say in the overview
  that finishing sharpens and lowers without depositing.

### 4. LOW: weathering's 200 m continental base level
`surface.py:247-250`. Continental ground weathers toward 200 m, not toward sea level. With the base at 0 m,
weathering would remove 1.45× as much. The isostasy already puts a normal 35 km continent at 250 m, so this mostly
stops the relief-independent weathering term from wearing old plains down to the sea. A relief-dependent term
would do that on its own. It holds land area up a little, which is one of the scorecard and envelope metrics.
- **Grade: weak.** It is a fixed floor standing in for "flat plains don't erode", not a process. It has been there
  since the first erosion commit (`fe56a31`) and was not added to hit a number.
- Filed as needs-decision.

### 5. LOW: there is no test of sediment conservation
The budget closes exactly today, but nothing in `tests/` asserts it. `test_invariants` checks the crust budget,
not erosion against deposition. A future edit to `_route`, `_offshore` or the lake spreads could leak or create
sediment unnoticed. xs draft.

### 6. Sound approximations (checked; no action)
- **Volume, not mass, is conserved.** 1 km of eroded basement (2.8 g/cm³) becomes 1 km of sediment (2.1–2.6), so
  mass falls by up to 25%, and compaction raises density without thinning the pile. The isostasy (`sediment_lift`)
  handles the density for elevation, so it's a consistent simplification. Mass conservation would mean 1.3–1.5×
  more deposit volume, so basins would fill faster (PW-054 worse). Related to PW-049.
- **Cell area.** Deposits are km per cell, routed with no area weighting (cells 0.67–1.21× the mean): +0.8% net
  volume drift over 300 Myr. Tolerable; weighting the moved flux by `A_i / A_d` would fix it.
- **Reefs, evaporites and coal** are added on top of the clastic load (5.5% of the eroded volume) without taking
  the dissolved load out of it. Carbonate is partly atmospheric CO₂, so it's a fair simplification.
  `evaporite_rate` is a fixed 20 m/Myr in hot closed basins, not tied to how much salt reaches them. Plausible.
- **`rain_factor`** clip 0.1–2.5 (`surface.py:88`): a stability and desert-floor limiter, documented, not keyed to any
  region. The floor is active on 18% of land cell-steps (deserts under ~45 mm/yr still get flash floods and wind).
- **Glacial multipliers** ×3 when the warmest month is above −8 °C and ×0.3 on cold-based ice (`earth.py:371`),
  and **vegetation** 1 + 0.6·wet·(1 − cover) (`earth.py:376`): recognised effects (buzzsaw, cold-based
  protection, soil binding) with order-of-magnitude constants.
- **Lake rules** `MIN_DEPTH` 20 m, `MIN_SLOPE` 0.1 m/km, the outlet cut `CHANNEL_K·Q^0.7`: sub-grid drainage
  parameterisations with stated reasons. They act per cell, so they aren't level-consistent (already PW-243).
  None keyed to Earth; they were tuned on Earth's terrain, which is a calibration, not a special case.
- **Offshore levels** `DELTA_TOP` +2 m, `SHELF_TOP` −60 m, `SHELF_EDGE` −400 m; `fan_km`, `alluvial`; the 5 m left
  below a hollow's spill level (`surface.py:265`); spreading substeps ∝ scale² (level-consistent).
- **Priority-flood ε** 0.01 m, `carve` floor 0.5 m, `stream_power` treating the sea as 0 m: numerical details.
- **`texture`**: the coast guard (`timeline.py:420`) only stops noise drowning land.
- **`accumulate_lakes`** clamps negative flow out of a lake to 0: correct (no negative rivers).

### Known tickets: causes seen
- **PW-239:** confirmed. `surface.erode` works out `lk` on the elevation before the step's erosion (`surface.py:229`)
  and `lake_depth` is measured against that same elevation (`surface.py:298`), which `earth.erode` stores
  (`earth.py:392`).
- **PW-243:** finding 1 is a candidate contributor, besides the per-cell lake rules.
- **PW-054:** finding 2 doesn't drive basin loss. The volume-for-mass simplification (§6) slightly *understates*
  infill. Nothing in this area clamps the closed-basin share.

### Git history
I checked the tests that cover this area (`test_water.py`, `test_envelopes.py`, `test_invariants.py`,
`test_zoom_water.py`). No loosened asserts on erosion, lakes or relief. The widened ranges in history are the
crust-thickness envelope (28 ↔ 30 km, tectonics) and Köppen's 0.66 → 66 (units). Commits in this area that name a
metric: PW-055 (giant lakes, inland drainage) and PW-057 B (Jaccard). Both change processes (catchment rain,
whole-lake trapping, lake-aware routing, slope-scaled texture). Only PW-057's one-sided creep without deposition
(finding 3) leans on a mask.

## Appendix: inventory

| file:line | what | justification found | verdict |
|---|---|---|---|
| surface.py:88 | `rain_factor` (P/800)^0.8, clip 0.1–2.5 | docstring (deserts barely erode) | fine |
| surface.py:100 | `_relief`: the sea counts as 0 m | comment | fine |
| surface.py:138 | floodplain keep (1 − e^(−d/alluvial))·e^(−slope/2 m/km) | docstring; the 2 m/km is unexplained | weak (fine) |
| surface.py:162-164 | DELTA_TOP 2, SHELF_TOP −60, SHELF_EDGE −400 m | comments (wave base, shelf edge) | fine |
| surface.py:185-187 | offshore fill to the target level; fan share | docstring | fine |
| surface.py:242-246 | hillslope 4κK·dt/d² × one-sided relief | "Laplacian, same at any resolution" (false) | **suspicious** (F1) |
| surface.py:248 | continental base level 200 m | comment only | weak (F4) |
| surface.py:250 | weathering (1 + (h/h0)²), h0 2000 m | Montgomery & Brandon | fine |
| surface.py:241 | K_river = max(own rain, catchment rain) | PW-055 | fine |
| surface.py:254 | removed capped at thickness | physical | fine |
| surface.py:265 | pit room = spill − 5 m | none (a hollow is never quite filled) | fine |
| surface.py:274-275 | open-lake trap capped at pool room | PW-055 | fine |
| surface.py:276-281 | closed-lake spread ∝ depth + 1, no cap | none | **suspicious** (F2) |
| surface.py:292-294 | lateral spread k 0.15, scale² / 4·scale² substeps | comment | fine |
| earth.py:371 | glacial ×3 (t_warm > −8 °C), cold ice ×0.3 | comment (buzzsaw) | fine |
| earth.py:376 | bare wet ground erodes up to 1.6× | comment, overview §2.18 | fine |
| earth.py:417 | sand share 0.6 / 0.5 / 0.15 by setting | docstring | fine |
| earth.py:421-422 | dunes P < 200 mm, 1%/Myr | docstring | fine |
| earth.py:425-427 | evaporite T > 10 °C, sabkha T ≥ 22 °C and P < 400 mm, ×0.25; fixed 20 m/Myr | docstring; not supply-linked | weak (fine) |
| earth.py:428-429 | coal: e < 250 m, P > 1000, veg > 0.5 | docstring | fine |
| earth.py:465 | reef growth capped at −5 m, e^((e+5)/150) | docstring | fine |
| params.py:60-88 | hillslope 100, tau 400, h0 2000, incision 0.0064, alluvial 3000, fan 1000 | comments, overview | fine (hillslope per F1) |
| hydrology.py:54 | world incision 0.018·1.6·s·2^(L−5) | muddled comment; measured level-consistent | fine |
| hydrology.py:73 | one-sided creep 0.08·s, nothing deposited | PW-057 (keep the lakes) | **suspicious** (F3) |
| hydrology.py:81 | MIN_DEPTH 20 m | sub-cell channels | fine (PW-243) |
| hydrology.py:84 | MIN_SLOPE 0.1 m/km | PW-110 | fine |
| hydrology.py:87-88 | CHANNEL_K 0.1, B 0.7, CARVE_TRIES 2 | PW-055 | fine |
| hydrology.py:188, 212 | a cut valley flooded below its cell mean is no lake | comment | fine |
| hydrology.py:195 | salt pan if catch ≥ 0.1·loss | none | fine |
| hydrology.py:209 | closed lake level = mid of highest wet cell and lowest shore | comment | fine |
| hydrology.py:228-230 | BASEFLOW 0.5, frozen 0.05, −2 °C | docstring | fine |
| hydrology.py:267 | lake damping 3·size/upstream, clip 0.9 | docstring | fine |
| kernels.py:362 | a cell becomes lake if ≥ 0.5 of its loss is met | docstring (shore) | fine |
| kernels.py:526-553 | closed_excess: one cell's worth threshold | docstring | fine |
| kernels.py:567 | negative flow out of a lake clipped to 0 | docstring | fine |
| kernels.py:617 | carve floor 0.5 m | docstring | fine |
| kernels.py:632 | stream_power: sea as 0 m | numerical | fine |
| kernels.py:190 | priority-flood ε 0.01 m | Barnes 2014 | fine |
| timeline.py:401 | texture ±180 m, slope 1.25 m/km full, 15% flat | PW-057 | fine |
| timeline.py:420 | texture can't drown a coast (5 m) | comment | fine |
| isostasy.py:46 | sediment 2.1→2.6 g/cm³ over 2 km; volume, not mass, conserved | docstring | fine (§6) |

Counts: 41 items; 35 fine (all sound approximations or numerical details), 3 weak (floodplain slope scale, base
level, evaporite rate), 3 suspicious (F1, F2, F3).
