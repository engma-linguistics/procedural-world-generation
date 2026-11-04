# PW-1446 scout 188: where do the 12 km zoom summits come from?

Scout 188, 2026-11-04. Branch from main 78140574. Readings of stored worlds and zooms, plus 4 km test zooms (1200 and 4000 km wide) of world dba204 built in scratch. Scripts sit beside this file (`scout2_*.py`, `scout2_trial.sh`). The candidate zoom change is `scout2_land_amp.patch`. It is **not** applied on this branch (§5 says why).

## In plain words

- **Two causes stack up, and they are about the same size.** The 11,957 m summit in zoom f4db12 breaks down like this. (1) The world's own cells are too high: dba204 has 120 cells above 7 km, up to 8,233 m. Earth's highest cell of the same size is 5,878 m. (2) The zoom then adds up to 5.4 km of relief above a cell's average. Earth's most extreme case at the same pixel size is 4.3 km.
- **"On old craton" is mostly the wrong label.** In dba204, 186 of the 231 cells above 6 km are orogen (mountain-belt) rock and 45 are craton. The zoom's highest pixel happens to land on craton, but craton is not what lifts it. The high cells sit at the 80 km crust cap, 1.0 to 1.3 km above their Airy height. That is the PW-048/PW-172 spike family that scout 171 found: sediment lift plus swell.
- **The zoom's share has a clear cause and a sound fix.** The zoom makes its sub-cell detail stronger the higher the ground is (0.36 m per m of height). On Earth, sub-cell relief follows how rugged the neighbourhood is, not how high it is (that is the fit in `planet/summit.py`). The result is that the zoom turns flat 4 km plateaus into mountains: 1.1 to 1.2 km of relief inside each cell, where Earth's flat cells have 0.2 to 0.3 km. And over the 7 to 8 km plateau it builds a 40 km-wide massif that averages 9 to 10 km, higher than any cell of the world below it.
- **The candidate fix:** take the detail's strength from Earth's sub-cell relief at the cell's local relief, with no height term. On the same world and code, the tallest test-zoom summit falls from 11,456 to 9,890 m. Over the full 4000 km f4db12 view it falls from 11,957 m (the stored zoom) to 10,247 m. Flat high plateaus drop to Earth's level, and lowland and mid-height ground barely change.
- **Not committed as code:** three zoom tests on synthetic worlds fail with it (§5). One of them compares against a flat plain that the old rule made rough. That needs a ruling on the test, not a code tweak. The other two need a look at the falls and seam code.
- **The rest (about 1 km above a ~9 km goal) is in the run.** The fix for that touches the run's physics (the cells at the cap that stand above their Airy height), so I stop at the diagnosis, as the brief says.

## 1. Candidates, and what tells them apart (written before any run)

| # | candidate | what would show it | result |
|---|---|---|---|
| A | the coarse model's uplift: cells too high before the zoom | world cells far above Earth's 5,878 m highest L7 cell | **yes**: dba204 has 324 cells > 5 km, 231 > 6 km, 120 > 7 km, top 8,233 m |
| B | isostasy: crust at the 80 km cap standing above its Airy height | elevation minus `250 + 150 (thick - 35)` on the top cells | **yes**: top 8 cells are at 79-80 km and stand +980 to +1,318 m above Airy; cells > 6 km have a median of +460 m |
| C | erosion never wearing old (craton) crust down | high cells mostly craton rock | **weak** in dba204: 186 of 231 cells > 6 km are orogen. In 899985 the high cells are craton (80% of land > 4 km), but its top cell is 5,546 m (Earth-like) |
| D | the zoom's relief synthesis | zoom (highest pixel - cell mean) against Earth's at the same pixel size, by local relief and by mean | **yes**: see §3 |
| E | the summit read-out stacking (summit.py on top of the zoom) | does any zoom number go through `summit_m`? | **no**: zooms report their own pixels; `summit_m` is a world-level display number (dba204's highest `summit_m` is 9,941 m) |

## 2. The coarse worlds (baseline: stored worlds on their own code; Earth L7 cell means, ETOPO1 via `tools/earth_data.py`, from scout1.md §1)

`scout2_coarse.py dba204 899985`:

| | ice-free land > 1 / 2 / 3 / 4 km | highest cell | cells > 6 / 7 km | land > 4 km by rock |
|---|---|---|---|---|
| Earth L7 | 19.7 / 5.2 / 2.7 / 1.7% | 5,878 m | 0 / 0 | |
| dba204 (run 10fd90, 1500 Myr) | 17.8 / 5.5 / 2.3 / 0.43% | 8,233 m | 231 / 120 | orogen 69%, craton 31% |
| 899985 (run a19366, 1000 Myr) | 16.6 / 5.4 / 1.1 / 0.27% | 5,546 m | 0 / 0 | craton 80%, orogen 20% |

dba204's top cells are not lone spikes. Their neighbours average 7.7 to 8.1 km, so this is a plateau held at the cap. Most of that plateau is under ice: the ice-free share above 4 km is only 0.43%. 899985 is Earth-like at the top. It has no stored zooms, so the zoom tests all use dba204.

## 3. The zoom's sub-cell relief against Earth

Earth (baseline): HydroSHEDS v1 30-arcsecond DEM (Lehner, Verdin & Jarvis 2008, as cited in `tools/earth_data.py`), in 0.5-degree blocks with at least 90% land. The blocks are the same as in `pw846_fit.py`. "Local relief" is the highest minus the lowest block mean over the 3×3 blocks, which is `summit.local_relief` on the model grid. `scout2_earth_tail.py` adds the 4 km view: the highest 4×4-pixel mean in each block, which matches a 4 km zoom pixel.

Earth, (highest pixel - block mean), at 1 km pixels | at 4 km pixels:

| local relief | blocks | 1 km p75 / p99 / max | 4 km p75 / p99 / max |
|---|---|---|---|
| 0-300 m | 34,141 | 173 / 844 / 2,460 | 128 / 631 / 2,109 |
| 300-700 | 14,342 | 745 / 1,543 / 3,317 | 554 / 1,247 / 2,998 |
| 700-1200 | 5,831 | 1,089 / 2,098 / 4,053 | 844 / 1,718 / 3,525 |
| 1200-2000 | 2,127 | 1,558 / 2,819 / 4,709 | 1,255 / 2,438 / 4,332 |
| 2000-3000 | 859 | 2,041 / 3,074 / 3,784 | 1,703 / 2,703 / 3,511 |
| 3000+ | 279 | 2,479 / 3,878 / 4,888 | 2,086 / 3,310 / 4,252 |

By block mean, at 4 km pixels, p90 / max: 3-4 km 1,653 / 2,924; 4-5 km 1,281 / 2,960; 5-7 km 1,000 / 1,631. On Earth, high plateau blocks are smoother than the mountain flanks below them. Height at a fixed local relief (the `pw846_fit.py` cross table) has no consistent effect up to 4 km mean. Only Tibet's ~100 interior blocks at 4-7 km reach a median of 0.5-0.7 km at low relief.

The stored dba204 zooms (code of 11-02), `scout2_subcell.py`. These are zoom (highest pixel - world cell mean) on full land cells, p75 by local relief, set beside Earth's 1 km p75 (the RELIEF_KNOTS):

| zoom | flat (0-300 m) | 700-1200 | 2000-3000 | 3000+ | max over a cell mean |
|---|---|---|---|---|---|
| f4db12 (51N 117W) | 257 vs 224 | 904 vs 1,062 | 2,945 vs 2,105 | 3,312 vs 2,479 | 5,442 m (cell 6,515 m → 11,957 m) |
| fe600a (70N 180) | 230 vs 262 | 829 vs 1,074 | 1,921 vs 2,077 | 2,507 vs 2,453 | 5,138 m |
| 3b412b (0N 59E) | 225 vs 154 | 1,082 vs 1,101 | 2,170 vs 1,992 | | 2,359 m |
| 0852e2 (32N 172E) | 360 vs 187 | 936 vs 1,088 | | | 2,167 m |

By cell mean, in f4db12, cells of 5-7 km have a median of 1,397, a p90 of 3,061 and a max of 5,442 m above their mean. Earth's 4 km p90 for such cells is 1,000 m. The highest peaks stand only 1-2.5 km above a 40 km box mean (`scout2_peaks.py`). The box mean itself is what is too high: 10,011 m around the 11,957 m peak, which is 1.8 km above the highest cell in the world. So the zoom builds a mid-scale massif higher than the plateau it stands on. The landscape pass caps summits at that box mean plus `min(1.8 amp, 3 km)` (`stage_landscape.fit_setup`), so the cap works and the inflated base is the problem.

Cause: `stage_terrain.detail` (and `refine.terrain`) set `amp_land = rug × (0.36 × base + 0.3 × step + 25) + 12`. On a 7-8 km plateau that is about 3 km of amplitude. The ridged detail at 0.4 cell spacing (±2.2 × amp) then makes 40 km massifs several km high, and the mean correction keeps each cell's mean by digging the rest of the cell down. Same-code scratch zooms show it plainly on flat plateaus. In e93718 (10N 70E), cells with relief under 300 m and a mean of 4.3 km get a p75 of 1,145 m, where Earth's is 308. In cd36e1 (32N 172E), cells of 3.7 km get 1,191 m against Earth's 197.

## 4. The candidate: detail amplitude from local relief

`scout2_land_amp.patch` adds `regional.land_amp(rug, local_relief) = rug × (summit.sub_cell_relief(local relief) / SUBCELL_K + 25) + 12`, with SUBCELL_K = 1.5. The zoom interpolates `summit.local_relief` onto its pixels in the slot the step relief used, and `refine.terrain` uses the same helper. Nothing in the run changes. I tried K = 1.0 and 1.5. At 1.5, the three test zooms come out about even against Earth's 4 km table (one under, one over, one close). This is a single constant, set on three zooms, so a lane should check it on 2-3 more zooms of other worlds.

Before and after, same code apart from the patch (main 78140574), 4 km pixels, world dba204. Test zooms are 1200 km wide unless marked. Each figure is the zoom's (highest pixel - world cell mean), p75 by local relief, with Earth's 4 km p75 in brackets:

| zoom | highest pixel | flat (0-300) [128] | 300-700 [554] | 700-1200 [844] | 1200-2000 [1,255] | 2000-3000 [1,703] | 3000+ [2,086] |
|---|---|---|---|---|---|---|---|
| A 61N 141W (the 8 km plateau), before | 11,456 | 714 | 919 | 1,235 | 1,600 | 2,785 | 3,429 |
| A after | **9,890** | 247 | 389 | 564 | 930 | 2,664 | 2,778 |
| B 10N 70E (4.4 km cells), before | 6,372 | 1,145 | 1,480 | 1,541 | 1,686 | 2,126 | |
| B after | **5,597** | 582 | 1,002 | 1,240 | 1,504 | 2,068 | |
| C 32N 172E (3.9 km cells), before | 5,470 | 1,191 | 1,170 | 1,120 | 1,215 | | |
| C after | **4,668** | 395 | 788 | 988 | 1,188 | | |
| f4db12 view (4000 km), stored 11-02 zoom | 11,957 | 257 | 437 | 904 | 1,579 | 2,945 | 3,312 |
| f4db12 view, after (scratch 6c40e1) | **10,247** | 228 | 412 | 648 | 1,076 | 2,592 | 2,776 |

- In zoom A, the box mean round the top peak falls from 9,178 to 8,423 m, now level with the plateau's highest cells (8.2 km) instead of above them. Cells above 7 km have a median of 362 m above their mean, down from 872.
- Each cell keeps its mean as before: the median of (zoom cell mean - world cell mean) is 0 to +1 m.
- What is left on the 2-3 km-relief flanks (2.6-2.8 km against Earth's 1.7-2.1 km) comes from the base surface's gradient between 8 km cells and their lower neighbours. The world causes that; the zoom does not.
- The coarse world itself is untouched by construction. Its highest cell stays at 8,233 m and its highest `summit_m` at 9,941 m.

## 5. Why the patch is not committed

Zoom, refine, summit, golden, crust-belt and isostasy tests with the patch: 151 passed, 3 failed. All three pass on main.

1. `test_zoom_landforms.py::test_rift_has_fault_blocks_along_its_axis`. The test wants the rift's flat floors to cover 10 points more of the zoom than the plain's. Its "plain" is a synthetic 900 m continent with zero relief. The old rule gave it 0.36 × 900 m of noise; the patch makes it nearly flat (75% of pixels under 3 m/km, against the rift's 53%). Earth's flat blocks (relief 0-100 m) have a p75 sub-cell relief of 86 m, so a flat plain is the right answer. The test's comparison needs a ruling, for example the rift floors against the rift's own flanks.
2. `test_zoom_landforms.py::test_plunge_pool_lies_below_the_whole_fall`. A fall on the synthetic escarpment world reports a plunge pool, but no pool pixel lies within 5 steps down its river. The new terrain may have exposed a latent bug in where pools are placed. Not looked into.
3. `test_zoom_match.py::test_matched_section_carries_the_neighbours_rivers_on`. A river crossing the seam carries 611 m³/s where the test allows at most 1.5 × 252. On the smoother ground a tributary probably joins right at the line. Not looked into.

Two of these are noise-sensitive checks on synthetic L5 worlds. The memory rule on fixture flips applies: compare over several re-rolled seeds before calling any of them a regression. That is a lane's work, so the patch is on file rather than merged.

## 6. Next steps

- **Zoom lane (effort s-m):** apply `scout2_land_amp.patch`. Settle the three tests (the rift test needs a ruling; check the other two over re-rolled seeds). Check K on 2-3 zooms of another world (899985 has no zooms yet), then update goldens if any. Expect every zoom's lowland detail to change a little. Flat high ground changes a lot.
- **Run physics (PW-1446 (b), coordinator's paired judge):** the top cells stand at the 80 km cap and 1.0-1.3 km above Airy (`isostasy.elevation`: `sediment_lift` + swell). Candidate: let no sediment lift or swell carry a cell at the cap above its Airy height, or scale both down as the crust nears `MAX_KM`. With the zoom fix, an Earth-like coarse top (≤ ~6-7 km) would put zoom summits at about 8-9 km.
- **Re-label PW-1446:** the zoom summits are not a craton effect in dba204 (80% of cells > 6 km are orogen). Lever (a), "stacked craton becomes orogen rock", would not lower that plateau.
