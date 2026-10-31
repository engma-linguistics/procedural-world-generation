# Inland pits: the sea by connection (PW-1229, lane 98)

## In plain words

Until now any ground below 0 m counted as sea, even a hole in the middle of a continent with no way to
the ocean. The L8 world a16f5a had hundreds of these, and its largest river ended in one; the L7 world
2a7385 showed them as deep blue pits of "ocean" inland.

Now the sea is the water that reaches the ocean. A hole below 0 m that the ocean can't reach is land:
the rivers and lakes treat it as a hollow and fill it to a lake (whose surface can sit below sea level,
like the Dead Sea's) or leave it a dry basin or salt pan (like Qattara or Lake Eyre). One rule, in one
function (`planet/geo.py: is_land`, with a JS copy in `viewer/globe/landsea.js`), is used everywhere the
run, a world slice, the climate, the hydrology, the coast, the zooms, the tools and the viewer ask
"is this land?".

What it changes: on fresh worlds a handful of pits (9 to 22 per world at L6/L7, about 20 to 35 cells)
become land, mostly as lakes, and a few big rivers that used to stop in a pit now run on to the sea. On the
same terrain the climate barely moves (dry land within 0.12 points). The run itself treats pits as land
now, so a 1 Gyr run takes a different path. The L6 scorecard's six worlds came out different in both
directions, drier on average by 4 points. One draw can't tell that from chaos, and it needs re-rolled
draws before anyone reads it as a trend. On Earth it fixes an old error in a
diagnostic: the Amazon and the Ob ended in one-cell "seas" at their mouths, so the Atlantic and the Arctic
were missing their rivers in the moisture budget (PW-386).

Stored worlds keep the old answer until they are sliced again (see the end).

## The definition

`geo.is_land(elev, ice=None, grid=None)`:

1. Wet cells: ground at or below 0 m that has no grounded ice on it. Grounded ice is land whatever its bed
   (PW-307/354), as before.
2. Wet cells are joined into bodies along the grid's links (the CSR neighbours, `grid.components`).
3. A body is **sea** if it is
   - the largest body (the world ocean), or
   - at least `SEA_MIN_KM2` = 0.3 Mkm², or
   - joined to a sea body through a **sill**: one land cell whose ground is at most `SILL_M` = 10 m and
     which neighbours both bodies. Joins chain (union-find), so a string of basins linked by sills to the
     ocean is all sea.
4. Every other wet cell is land: a closed hollow.

Why these two allowances, rather than strict cell-to-cell connection:

- **Sill (10 m, one cell).** A coarse cell is 30 to 120 km wide. A real strait narrower than that (the
  Bosporus, the Danish straits, Bab-el-Mandeb, a lagoon's inlet) shows up as one low land cell between two
  wet bodies. A one-cell barrier no higher than 10 m is within the noise of a cell's mean height for a
  coastal plain, so it does not stop the sea. Anything higher, or two cells wide, does. Tested with a
  one-cell strait at −5 m (joined), exactly `SILL_M` (joined) and 5 × `SILL_M` (not joined).
- **Size (0.3 Mkm²).** A cut-off body this big is a remnant sea or an enclosed ocean, and the climate's
  ocean should carry it. On Earth's L7 grid the bodies that need it are the Baltic (0.39 Mkm² there), the
  Black Sea (0.42) and the Red Sea (0.47), all real seas joined by straits narrower than a cell, and the
  Caspian (0.62 with its shores). The Caspian stays sea: that is the status quo, and it was part of
  Paratethys until a few Myr ago. I first set the floor at 1 Mkm²; the Earth L7 check turned all four
  into land, so I lowered it to 0.3. The PW-1229 pits are far smaller: the median generated pit is one or
  two cells, about 0.01 to 0.03 Mkm² at L6 (a cell is about 12,000 km²).

What becomes land on Earth L7 under this rule (83 cells in 29 bodies):
- Real closed hollows: Qattara (6 cells, −80 m), Lake Eyre's basin (4, −15 m), the Danakil (1, −96 m),
  the Chott basin (34.3°, 6.6°).
- Lake beds below sea level: Superior (7, −91 m), Michigan (1) and Ontario (2).
- Seas behind straits narrower than a cell: Puget Sound and the Salish Sea (5, −104 m), Lake Maracaibo
  (4), the St Lawrence estuary (2), Cook Inlet (1), the Ob gulf (11 cells near 68.7°, 73.4°), the
  Amazon's mouth cell (0.1°, −50.9°, −1 m), and a few Arctic coastal cells and two bodies (5 cells, to −989 m) at the inner Amery Ice Shelf.

On the Earth analogue those last ones are a cost of the rule, since nothing in the grid's data marks
them as connected. See the inbox draft `draft-subcell-straits-earth.md`.

### Where it is used

- The run: `Simulation.land()`, the run's erosion and lakes (`surface.py`, `hydrology.erode`/`_settle`),
  its climate, vegetation and sediment updates (`tectonics/earth.py`), and `output.water_now`, which now
  passes grounded ice so a marine-ice hole is not mistaken for a pocket lake.
- The hydrology kernels (`kernels.priority_flood`, `fill_shallow`, `lakes`, `lake_order`) take the sea
  mask explicitly instead of testing `elev <= 0`. Their radix sort of land cells now handles heights below
  0 (it flips the float bits).
- The slice and the climate: `world.py`, `climate.compute(..., land=)`, `koppen`, `biomes`. `nest.py`
  passes the fine grid's own mask down to the coarse climate grid, so connectivity is not recomputed
  coarsely.
- Coast, waves, tides and sea ice (`coast.py`), soils, landforms, vegetation, resources, highlights,
  lineages, and the export (`export.py`: raster water comes from the world cells).
- Zooms: `zoom/regional.land_world` floors pockets at `BED_FLOOR` (1 m), the way it already handles the
  bed under ice, and keeps the lake depth on top. Pixel-level zoom code gets `land=h > 0` on its own
  floored heights.
- The viewer: `load.js` builds the land view with `seaMask` (the same rule in JS; a node test checks it
  agrees with Python cell for cell). The hover card names a pit's bed "below sea level, cut off from the
  sea".
- Tools: `scorecard.py` (per-world land, shelf and dryness), `moisture_budget.py` (basins and drainage),
  `health.py`, `ice_probe.py`. `earth_data.land_of` already used `is_land`.

Not changed, by design: the time zoom (`timezoom`/`timeline`) still uses its own view of the sea; that is
filed as `draft-timezoom-sea-ignores-connection.md`. The zoom's own terrain can still cut depressions
below 0 inland; that is filed as `draft-zoom-flattens-depressions-below-sea.md`.

## Before and after: re-sliced worlds (scratch only)

Old L6/L7 runs in the store cannot be replayed (their parameters predate the current code), so I ran
fresh base-code runs in scratch (L6 seeds 1 and 2, L7 seed 1, 1000 Myr each) and sliced each at 1000 Myr
with the old code and with the new code (both slices replay the same stored keyframe). I also measured two
runs made entirely with the new code. "Bodies (old rule)" are the bodies below 0 m apart from the ocean.
"Big mouths" are rivers with flow ≥ 300.

| world (old → new) | level | bodies (old rule), cells | kept as sea | pockets → land, cells | pocket floor median | pocket cells: dry / open lake / closed lake / salt pan | lake cells old → new | top-50 mouths moved | largest river |
|---|---|---|---|---|---|---|---|---|---|
| 95ca52 → 4006fe (L6 s1) | 6 | 18, 34 | 7 | 9, 24 | −1129 m | 4 / 18 / 2 / 0 | 131 → 226 | 0 | unchanged |
| 57cdf5 → c9d64e (L6 s2) | 6 | 24, 142 | 7 | 17, 35 | −2933 m | 6 / 24 / 3 / 2 | 41 → 72 | 3, all on to the ocean | unchanged |
| 390e11 → 2f4eb4 (L7 s1) | 7 | 54, 523 | 25 | 22, 27 | −172 m | 7 / 18 / 2 / 0 | 294 → 318 | 5, all on to the ocean | unchanged (flow 3465 → 3463) |
| 03b8c1 (new-code run, L6 s1) | 6 | 15, 45 | 2 | 13, 18 | −2417 m | 8 / 4 / 2 / 4 | – | – | – |
| 21cc67 (new-code run, L6 s2) | 6 | 16, 62 | 5 | 11, 23 | −1886 m | 1 / 20 / 1 / 1 | – | – | – |

In 390e11, 4 of the 17 big mouths end in a body the old rule calls detached. All 4 bodies are kept as sea
by the new rule (sill or size), so those mouths stay where they are. The 5 top-50 mouths that moved all
now run on to the ocean.

**Where the new lake cells come from.** Every added lake cell is in a lake that holds a pocket. In 4006fe
one lake grows from 14 to 102 cells (1.27 Mkm², open, surface at 1438 m): it fills a highland basin
around a pit at −65.5°, −31.6°. Most pockets in generated worlds are PW-171 tectonic pits 1 to 4 km
deep. Sediment in the run does not heal them, and they now hold lakes up to about 7 km deep. That is
honest for the terrain we make, but the pits themselves are the odd part (see
`draft-pw171-pits-hold-deep-lakes.md`).

**The new-code runs** (03b8c1, 21cc67) keep about as many pits as the base runs. The run's erosion and
lakes now treat them as hollows, but nothing in the run fills or erodes them away faster.

### Stored worlds (read-only count, nothing re-sliced)

| world | level | bodies (old rule), cells | kept as sea | pockets → land, cells | pocket floor median | big mouths | into a detached body | into a new pocket | largest river ends in a pocket |
|---|---|---|---|---|---|---|---|---|---|
| a16f5a | 8 | 237, 672 | 95 | 142, 494 | −17 m | 66 | 21 | 17 | yes |
| 2a7385 | 7 | 41, 215 | 3 | 38, 102 | −913 m | 16 | 2 | 2 | no |

(I count 237 bodies in a16f5a where the brief says 225; I have not traced the difference in counting.
The 21 of 66 mouths matches the brief.) When a16f5a is sliced again, 17 of its
21 big mouths that end in a detached body, including the largest river, will run on to a lake or the sea.
The other 4 end in bodies the rule keeps as sea.

## Tests

- New `tests/test_landsea.py` (8 tests):
  - a cut-off pocket is land and a below-0 inlet that does connect is sea;
  - grounded ice is land;
  - one-cell strait at −5 m, at `SILL_M` and at 5 × `SILL_M`;
  - a big body is sea and a small one is land;
  - hydrology on an L6 pocket: wet enough, a closed lake with its level below 0; dry, no lake;
  - the JS `seaMask` agrees with Python.
- Updated for the rule: test_water, test_invariants, test_world_land, test_coast, test_soils,
  test_vegetation, test_landform, test_store, test_health, test_humanuse.
- Golden outputs updated on purpose (`--update-golden`): `tests/golden/climate_L4.json` and
  `sim_L4_s1_60myr.json`. The run's land, lakes and climate change wherever a pit exists.
- `uv run pytest -q -n 4 -m 'not slow'`: 857 passed, 1 skipped. Three failed only because I had set
  `NUMBA_NUM_THREADS=1` (test_kernel_threads asks for more threads); without it, 3 passed.
- Hydrology, climate, coast, ocean, golden and land/sea tests, slow included (test_coast, test_coastal,
  test_coastform, test_golden, test_landsea, test_ocean, test_polar_climate, test_water, test_zoom_coastal,
  test_zoom_water, test_invariants): 124 passed.

## Scorecard (L6, seeds 1–6, 1000 Myr) against `scorecard_L6.txt`

`uv run python tools/scorecard.py --seeds 1 2 3 4 5 6 --myr 1000 --jobs 3 --threads 2`. It took 5331 s on
a loaded machine; the baseline took 1120 s at `--jobs 7`. Baseline: `scorecard_L6.txt` (commit 1a64cd7c; since
then only the dragon food chain changed under planet/). The Earth line came back empty in the worktree because
the Köppen download failed, so I computed `earth_scores()` from the scratch copy with the stored inputs. The
scorecard's workers had loaded `tools/scorecard.py` before I switched its per-world land to `is_land`, so
these rows count land as `elevation > 0`. Pockets are about 20 cells of 40962, so that makes no visible
difference.

| seed | land % | dry % | ice % | shelf % | land > 4 km % | peak m | NPP | trees % |
|---|---|---|---|---|---|---|---|---|
| 1 | 31.6 → 34.3 | 20.0 → 24.9 | 2.7 → 2.6 | 4.7 → 1.4 | 2.37 → 0.17 | 6801 → 4421 | 462 → 388 | 42.8 → 33.5 |
| 2 | 34.5 → 33.8 | 18.5 → 18.2 | 2.3 → 6.1 | 1.6 → 1.2 | 2.59 → 5.1 | 7899 → 8294 | 411 → 233 | 41.6 → 29.6 |
| 3 | 34.3 → 34.5 | 19.7 → 27.8 | 4.4 → 1.3 | 1.8 → 2.5 | 2.52 → 2.11 | 6588 → 6524 | 276 → 425 | 34.9 → 35.0 |
| 4 | 33.9 → 35.3 | 17.9 → 24.5 | 0.0 → 5.9 | 2.7 → 2.7 | 0.01 → 1.35 | 4015 → 5785 | 495 → 278 | 49.7 → 29.9 |
| 5 | 35.0 → 34.0 | 20.8 → 21.4 | 2.3 → 1.1 | 1.9 → 3.3 | 1.67 → 0.0 | 6735 → 3746 | 422 → 425 | 40.3 → 46.9 |
| 6 | 34.9 → 34.7 | 16.0 → 20.4 | 5.6 → 3.2 | 6.1 → 2.2 | 4.05 → 2.01 | 7437 → 5470 | 405 → 433 | 38.1 → 40.0 |
| mean | 34.0 → 34.4 | 18.8 → 22.9 | 2.9 → 3.4 | 3.1 → 2.2 | 2.20 → 1.79 | 6579 → 5707 | 412 → 364 | 41.2 → 35.8 |

Earth at L6 (`earth_scores`): Köppen group agreement 71.1% → 71.1%, exact 38.4% → 38.2%, shares
A/B/C/D/E 20.3/25.0/19.4/23.8/11.4 → 20.3/24.7/19.7/24.1/11.2, log-rain correlation 0.721 → 0.718.
Atlantic E-P-R at L6 is +0.08 Sv (Atlantic minus Pacific −78 mm/yr), against +0.12 Sv at L7 below.

No hard failure: no world frozen or boiled, all land between 33.8% and 35.3%, ice 1.1% to 6.1%.

**The per-world moves are run chaos, not the climate.** The run's land mask changes wherever a pit
exists, and pits are present from early on. Each run then takes a different tectonic path: the peaks,
plate sizes and land above 4 km differ seed by seed, in both directions. To separate the direct effect,
I sliced the same keyframes with the old and the new code (identical terrain). Measured on the old land
cells:

| keyframe (old → new slice) | dry % | NPP | tree cover % | precipitation mm | temperature °C | Köppen cells changed |
|---|---|---|---|---|---|---|
| 95ca52 → 4006fe (L6 s1) | 20.28 → 20.39 | 407.5 → 405.3 | 42.57 → 42.44 | 1186 → 1188 | 11.05 → 11.08 | 292 of 12924 |
| 57cdf5 → c9d64e (L6 s2) | 18.62 → 18.62 | 364.9 → 364.6 | 41.20 → 41.21 | 1148 → 1152 | 9.32 → 9.34 | 505 of 14148 |
| 390e11 → 2f4eb4 (L7 s1) | 19.86 → 19.98 | 278.2 → 277.2 | 36.13 → 36.28 | 1140 → 1140 | 8.34 → 8.35 | 1489 of 59559 |

So on a given terrain the new rule moves the dry share by at most 0.12 points and NPP by under 1%.

The scorecard's mean dry share rose 4.1 points, but that is one draw of six diverged runs. My two
new-code runs made with `planet simulate` (same seeds) disagree with it: seed 1 is 30.5% dry (base 20.3%),
seed 2 is 14.7% (base 18.6%). One draw can't tell a shift in the distribution from chaos. Settling it
needs re-rolled draws (several seed sets, old and new), which I did not run at the 10-core cap. Filed as
`draft-scorecard-shift-after-pw1229.md`.

## Earth check (L7) against `earth_check_L7.txt`

Run from a scratch copy of the code with the stored Earth inputs copied into scratch: the Köppen server
was down, and nothing was written to `data/earth`.

| number | before | after |
|---|---|---|
| Köppen main-group agreement (excl. Antarctica) | 71% | 70% |
| exact-code agreement | 38% | 37% |
| shares A/B/C/D/E excl. Antarctica | 20.2 / 25.2 / 19.0 / 23.6 / 12.0 | 20.1 / 25.0 / 19.2 / 23.9 / 11.8 |
| dry land B (obs 30.1) | 25.2 | 25.0 |
| log-rain correlation with GPCC | 0.717 | 0.714 |
| land rain vs GPCC | ×1.33 | ×1.34 |
| city point check exact / group only / wrong group (of 78) | 41 / 17 / 20 | 37 / 21 / 20 |
| Amazon / Congo / Mississippi discharge, m³/s | 372507 / 153491 / 53675 | 371867 / 152571 / 53792 |
| lakes: open / closed / salt-pan cells (lake cells) | 29 / 85 / 201 (898) | 23 / 82 / 211 (891) |
| land draining to closed basins | 23% | 23% |
| Atlantic E-P-R | +0.54 Sv | +0.12 Sv |
| Atlantic minus Pacific E-P-R per area | +137 mm/yr | −55 mm/yr |
| Pacific / Indian E-P-R | +0.50 / +0.44 Sv | +0.50 / +0.44 Sv |

**The climate itself barely moves.** Shares move by at most 0.3 points. The four cities that drop from
exact to group (Kashgar, Athens, Atlanta, Astana) are threshold flips: BWk→BSk, BSh→BSk, Cfa→Cwa,
Dfb→Dfa. In the closed-basin table, Lake Eyre (cells within 350 km) goes from 0 closed + 4
pan cells to 12 + 12 on the model's rain, and from 4 + 1 to 0 + 1 on GPCC's rain. Its bed below 0 is now
a hollow the lake scheme fills, not a scrap of sea. River discharges at the big mouths are unchanged to
within 3%, except the Murray (984 → 1319 m³/s; observed 800). earth_check routes rivers on its own
lifted ground, so the Amazon's mouth cell never mattered there.

**The Atlantic E-P-R drop is a correction, not a climate change.** In `tools/moisture_budget.py`,
`drainage()` routed each river to the sea cell it reaches. At L7 the Amazon's mouth cell (0.1°, −50.9°,
−1 m) and the Ob gulf (11 cells near 68.7°, 73.4°) are bodies below 0 cut off from the ocean, which
`basins()` filed as "Med+inland". So the Atlantic's catchment lost 7.5 Mkm² (the Amazon and Orinoco
side) and the Arctic's lost 9.3 Mkm². With the new rule those cells are land and the rivers reach the
Atlantic and the Arctic:

| land draining to (Mkm²) | Atlantic | Pacific | Indian | Arctic | Southern | Med+inland |
|---|---|---|---|---|---|---|
| old rule | 36.17 | 21.19 | 20.97 | 10.98 | 18.38 | 39.25 |
| new rule | 43.71 | 21.43 | 20.97 | 20.28 | 21.16 | 19.38 |

This is PW-386 ("routes ~0.5 Sv of the Atlantic's rivers into 'Med+inland'"), which guessed exactly
this cause. The old L7 headline (+0.54 Sv, +137 mm/yr) passed PW-016's bar (≥ +0.25 Sv, ≥ +100 mm/yr)
only because the Amazon's water was missing. The new figure is in line with the L6 one PW-016 recorded
before (+0.20 Sv, −16 mm/yr on the PW-015 branch). PW-016's condition was never really met at L7, and it
still isn't. Nothing in the model's own ocean depended on this diagnostic.

## After merge

- Stored worlds keep their old masks until re-sliced. a16f5a (17 big mouths and the largest river move),
  2a7385 (38 pits) and the other showcase worlds should be re-sliced from their runs by the coordinator.
  Zooms built on them, such as 652c1a on a16f5a's largest river, need rebuilding after that.
- Old L6/L7 runs whose parameters predate current code cannot be replayed anyway. Delete them rather than
  keep a path for them.
- PW-386 can likely be closed by this change. Atlantic E-P-R is now +0.08 Sv at L6 and +0.12 at L7, where
  before it read +0.54 at L7. Its checkbox (Atlantic river input within ~10% between L6 and L7) still needs
  the per-basin rows (`moisture_budget.py`'s report) read on main.
- The scorecard line this lane appended to `docs/scorecard.jsonl` is committed with the code (commit
  1b94146d+dirty, earth empty for the reason above).
