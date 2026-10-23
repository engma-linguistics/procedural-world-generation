# Multi-seed time-zoom fixtures (proposal for PW-623, PW-638, PW-640)

Branch `worktree-agent-acfa88d756b0677df`, on main 86d3806. **Not merged: the owner decides** (inbox draft
`draft-multiseed-fixtures.md`). Only `tests/` changes. No assertion or threshold inside a per-seed check changed.

## What it does

Three physics changes were held tonight because single-world fixtures flipped on a chaotic 300 Myr run. The
proposal runs each affected test's **unchanged per-seed assertions** on a fixed list of seeds and asks that
**70% of the eligible seeds pass** (`tests/seeds.py`, `PASS_RATE = 0.7`; the bar is `ceil(0.7 n)`). The failure
message lists every seed's numbers.

- **Seeds are fixed up front:**
  - L4: seeds 1-24 (`seeds.SEEDS4`, the first 24; seed 1 is sim4's world).
  - L5: seeds 25-50 (`SEEDS`, lane A16's scan window; it was 25-35).
- **Moments and cooling follow the existing rules:**
  - L4: the run's 300 Myr moment, 4 C colder (`_icehouse`, as the `icehouse` fixture).
  - L5: `_cold`, 4 C colder with the run's ice rule.
- **Caching:** the worlds are built once per pytest session. Each set is pickled in the session's shared temp dir
  behind an `fcntl` lock, so xdist workers share it (the xdist-documented pattern; sim4 has no disk cache, so
  neither has this). A spawned process pool builds them: `PW_SEED_WORKERS`, default 8, each process with
  conftest's 4 numba threads.
- **No `slow` marks changed.** The consistency module was already `slow`; the L4 tests were not and are still not.

### Eligibility, exactly

- **Forest-to-tundra:** every seed is eligible. The test has no precondition.
- **Endings:** every seed is eligible. **`extra > 10.0` is an assertion in the test, not a precondition**, so a seed
  with too little glacial ice (seed 5, extra 3.8 m) counts as a failure, not as ineligible.
- **Cold moment:**
  - Eligible for all three tests: `_plausible` (sea level within 150 m, overturning >= 2 Sv in both hemispheres,
    polar land >= 25%). This is the existing precondition, unchanged.
  - **This part needs the owner.** `test_ice_speeds_plausible` and `test_ice_at_index_zero_is_the_runs` run only on
    the plausible seeds whose cold moment has sheets (> 1% of cells under > 1 m). The file already says the drift
    tests need this: "(else the drift test below proves nothing)".
  - `test_cold_moment_has_sheets` keeps its per-seed assertion. It now asks that the window give at least
    `MIN_SHEETED = 5` such seeds, so that a 70% bar on them can tolerate one failing world. **5 is a new number.**
  - Why not the plain 70% bar? On main only **7 of 14** plausible seeds have sheets (4 of 6 in the old 25-35
    window), so the sheets test at 70% would be red on main itself. The fixture's own comment already says most
    plausible moments are warm and have no sheets.

## Before / after (every touched test)

The full diff is at the end. These are the assertions, word for word; each one is now inside a per-seed function
(`_forest_case`, `_endings_case`, `_sheets_case`, `_speeds_case`, `_index_zero_case`). The only lines added
there record numbers.

- `test_glacial_cooling_turns_forest_to_tundra_and_cools_further`:
  - Before: on sim4 (seed 1).
  - After: `seeds.check_rate` over seeds 1-24.
  - Assertions:
    `assert pl.series[-1]["F_wm2"] == 0.0`;
    `assert lost.sum() >= 5`;
    `assert (c["temp"] - t0)[lost].mean() < -0.1`;
    `assert pl.series[-1]["F_wm2"] < 0 and pl.dT_target < 0`.
- `test_glacials_grow_ice_and_endings_melt_it_fast`:
  - Before: on sim4's icehouse.
  - After: over seeds 1-24, each world made an icehouse by `_icehouse`.
  - Assertions: `assert extra > 10.0`; `assert sl_off[j] - sl_on[j] < 0.5 * extra`.
  - Its `print` line became an `out.update`.
  - `test_zoom_climate_follows_the_index` stays on sim4's icehouse; only its fixture body moved into `_icehouse`.
- `test_cold_moment_has_sheets`:
  - Before: on the first plausible seed of 25-35.
  - After: `assert (src["ice"] > 1).mean() > 0.01` on each plausible seed of 25-50, and at least `MIN_SHEETED`
    of them must pass.
- `test_ice_speeds_plausible`:
  - Before: on the first plausible seed.
  - After: on each plausible seed of 25-50 with sheets, at the 70% bar.
  - Assertions: `assert 1.0 < np.median(u) < 100.0`; `assert np.percentile(u, 99) < 5000.0`;
    `assert 500 < np.median(H[sheet]) < 3500`.
- `test_ice_at_index_zero_is_the_runs`:
  - Before and after: as the speeds test.
  - Assertions: `assert all(f["stats"]["glacial_index"] == 0.0 for f in r["frames"])`;
    `assert abs(r["frames"][-1]["stats"]["sea_level_change_m"]) < 25.0`.
  - The index-is-zero part never failed on any seed. Under a 70% bar, one world could break it unnoticed. If the
    owner wants that invariant kept at 100%, it is a one-line split.

## Cost

| | main 86d3806 | this branch |
|---|---|---|
| `uv run pytest -q` (16 xdist workers, 48 cores, no other load) | 598 passed in **3:42** | 598 passed in **4:52** |

The added minute is the L5 fixture. Its setup took 243 s here (26 L5 300 Myr runs in an 8-process pool), against
about 4 runs serially before. The L4 set (24 runs) takes about 40 s to build in the pool. The forest cases add
about 15 s and the endings cases about 40 s. With `PW_SEED_WORKERS=4`, the three modules alone took 4:15 (`-n 3`).

## Per-branch results (the three modules, `-n 3`)

| tree | forest (bar 17 of 24) | endings (bar 17 of 24) | cold: sheeted (need 5) | speeds | index 0 | verdict |
|---|---|---|---|---|---|---|
| main 86d3806 | 20 | 18 | 7 of 14 | 7 / 7 | 7 / 7 | green |
| main + `laneA17/step2_stable_summer.diff` | **16 (red)** | 21 | 6 of 13 | 6 / 6 | 6 / 6 | 1 red |
| A20 `worktree-agent-a2b66e784ed5186c3` a1462d3 + these tests | **12 (red)** | 20 | **4 of 8 (red)** | 3 / 4 | 3 / 4 | 2 red |

**The proposal does not unblock the forest test on either held branch.** The world swap below shows that each
tree's own climate is not the cause, but the 24-world population shifts as a whole: 20 of 24 pass on main's
worlds, 16 on step 2's, 12-13 on A20's. The table says which worlds. At main's base rate (75%, seeds 1-36), 12 or fewer of 24
happens by chance 0.7% of the time, so the A20 result is a real signal. Step 2's 16 of 24 (23% by chance) is not
clearly one.

What the signal is about: both changes alter the 300 Myr runs. The runs then produce worlds where the zoom's
forest loss gives a positive forcing (F > 0) more often. The failing worlds on A20 span run dT +0.01 to +9.8, so
this is not just "a colder world". That is a finding for the physics lanes, not a fixture artefact: the
multi-seed test says the old single-world diagnosis ("seed 1 is a colder world") was right for seed 1, but the
branch also shifts the population.

**Climate swap over all 24 worlds** (`xswap.sh`, `xswap.txt`): each row is one tree's zoom climate; the columns
are the 24 worlds each tree's runs give.

| climate \ worlds | main's | step 2's | A20's |
|---|---|---|---|
| main | forest 20, endings 18 | 16, 20 | 13, 21 |
| step 2 | 19, 19 | 16, 21 | 14, 21 |
| A20 | 20, 18 | 16, 21 | 12, 20 |

The worlds decide. A20's zoom climate is identical to main's on main's worlds: the same 20 / 18 and the same
failing seeds.

## The bar is close to main's own pass rate (pushback)

On main, over seeds 1-36: forest 27 of 36 pass (75%), endings 25 of 36 (69%). A 70% bar on 24 seeds then passes
by chance only this often, each time a change re-rolls the worlds:

| true pass rate | bar 17/24 (70%) | 15/24 (60%) | 12/24 (50%) |
|---|---|---|---|
| 0.69 (endings) | 0.52 | 0.82 | 0.98 |
| 0.75 (forest) | 0.77 | 0.95 | 1.00 |
| 0.83 | 0.96 | 1.00 | 1.00 |

So at 70%, the endings test would still flip on about half of all run-physics changes. Main's 18 of 24 is only
one seed above the bar. The multi-seed version is much better than one seed, but it is not yet lottery-free. The
deliberate breaks below drop the tests to 2 and 4 of 24, so a 50% bar would still catch them with a wide margin.

## Regression demonstration (on main 86d3806 + these tests, each break reverted after; `breaks.sh`, `break*.txt`)

1. **The glacial index never ends:** in `cycle.py`, `x = max(x - step / p.end_kyr, 0.0)` became `x = x`. The
   endings test fails with **2 of 24** (bar 17). Left after 15 kyr is about extra or more on almost every world.
2. **The forest loss's global term has the wrong sign** (`plants.py`, `-p.veg_toa` became `+p.veg_toa`). The
   forest test fails with **4 of 24** (bar 17). The 4 that pass are main's 4 failing worlds.
3. **The run's ice rule grows no ice** (`earth.ice_sheets` returns `0.0 * new`). `test_cold_moment_has_sheets`
   fails with **0 of 13** (need 5). The speeds and index-zero tests fail with **0 of 0 eligible** (`n > 0` is
   required).

## Per-seed tables

Main's columns come from the scans `scan.py l4 1-12` / `l4 13-36` / `l5 25-50`. The branch columns come from the
tests' own printout (`-rA`). On main's L5 table the drift numbers are shown for every plausible seed, but only the
seeds with sheets are the drift tests' worlds.

### L4 worlds (seeds 1-24)

Forest: F_wm2 (asserted < 0, together with lost >= 5 and cooling < -0.1). Endings: extra / left 15 kyr after the
first ending, in m (asserted extra > 10 and left < extra / 2). **x** marks a seed that fails.

| seed | main run dT | main forest | main endings | step 2 forest | step 2 endings | A20 forest | A20 endings |
|---|---|---|---|---|---|---|---|
| 1 | +5.10 | -0.038 | 50.2 / 1.86 | -0.045 | 30.9 / 18.4 **x** | 0.079 **x** | 47 / 22.2 |
| 2 | +3.23 | -0.163 | 87.2 / 20.4 | 0.098 **x** | 13.9 / 1.68 | -0.013 | 59.6 / 12.1 |
| 3 | +4.32 | -0.207 | 79.7 / 0.66 | -0.081 | 28 / -0.63 | -0.186 | 45.6 / -2.21 |
| 4 | +4.38 | -0.119 | 43.2 / 6.17 | -0.134 | 68.5 / 5.04 | -0.13 | 63.2 / -0.36 |
| 5 | +12.30 | 0.221 **x** | 3.79 / 0.39 **x** | -0.131 | 49 / 5.45 | 0 **x** | 11.1 / -0.92 |
| 6 | +7.94 | -0.006 | 21.5 / -0.33 | 0.055 **x** | 19.9 / 0.77 | 0.033 **x** | 16.3 / 1.02 |
| 7 | +0.74 | -0.218 | 132 / 88.5 **x** | 0.078 **x** | 24.4 / 0.4 | 0.099 **x** | 25.2 / 0.28 |
| 8 | +1.37 | -0.184 | 70.5 / 43.9 **x** | -0.032 | 80.8 / 49 **x** | -0.053 | 28.1 / 12.4 |
| 9 | +1.85 | -0.009 | 44.6 / 7.69 | -0.119 | 102 / 47.3 | 0.005 **x** | 53.3 / 3.59 |
| 10 | +3.09 | -0.045 | 55.9 / 8.5 | -0.042 | 70.8 / 21.5 | -0.067 | 63.5 / 11 |
| 11 | +6.23 | 0.025 **x** | 26.9 / 2.64 | -0.019 | 25.2 / 9.41 | -0.027 | 56.4 / 1.26 |
| 12 | +4.01 | -0.08 | 87.7 / 6.13 | -0.099 | 60.4 / 3.54 | -0.22 | 120 / 10.9 |
| 13 | -2.06 | -0.195 | 107 / 56.2 **x** | 0.062 **x** | 59.4 / 29.5 | 0.113 **x** | 27.5 / 16.6 **x** |
| 14 | +3.63 | -0.038 | 36.3 / 1.13 | 0.045 **x** | 22.6 / 0.06 | 0.063 **x** | 3.94 / 0 **x** |
| 15 | +10.60 | 0.181 **x** | 7.95 / 0.63 **x** | 0.166 **x** | 11.8 / 0.55 | 0.176 **x** | 7.97 / 0.66 **x** |
| 16 | +6.06 | 0.096 **x** | 6.52 / 0.14 **x** | -0.061 | 45.6 / 12.2 | 0.013 **x** | 45.3 / 1.68 |
| 17 | +3.27 | -0.131 | 66.8 / 0.81 | -0.291 | 134 / 74.7 **x** | -0.312 | 166 / 15.7 |
| 18 | +4.06 | -0.104 | 33.3 / 5.41 | -0.016 | 79 / 17.8 | -0.074 | 33.1 / 5.62 |
| 19 | +0.99 | -0.163 | 43.4 / 9.52 | -0.251 | 63.6 / 1.03 | -0.017 | 38.7 / 34 **x** |
| 20 | +3.32 | -0.064 | 42 / 16.4 | 0.077 **x** | 12.5 / -0.97 | -0.204 | 156 / 31.9 |
| 21 | +4.32 | -0.099 | 76.4 / 2.21 | 0.019 **x** | 25.5 / 1.01 | 0.022 **x** | 40.4 / 8.83 |
| 22 | +8.30 | -0.026 | 29.2 / 6.16 | -0.107 | 70.5 / 6.7 | 0.059 **x** | 17.5 / -0.04 |
| 23 | +6.69 | -0.079 | 23.7 / 8.14 | -0.099 | 14.5 / -1.23 | 0.031 **x** | 13.6 / 1.43 |
| 24 | +2.92 | -0.217 | 81.1 / 16.8 | -0.078 | 32.5 / 4.52 | -0.067 | 35.9 / 12.6 |

Totals:
- main: forest 20 of 24, endings 18 of 24;
- step 2: forest 16, endings 21;
- A20: forest 12, endings 20.

Main's seeds 25-36 for the base rate (`scan.py l4 13-36`):
- forest fails 27, 30, 31, 33 (8 of 12 pass);
- endings fails 29, 30, 35 (9 of 12 pass).

### L5 cold moments (the plausible seeds of 25-50)

**main**: 14 plausible, 7 with sheets (need 5)

| seed | run dT | sheets % (> 1) | median speed m/yr (1-100) | p99 (< 5000) | median H m (500-3500) | sea level change m (abs < 25) |
|---|---|---|---|---|---|---|
| 28 | -0.73 | 5.24 | 31.8 | 1.07e+03 | 1.71e+03 | -14.3 |
| 29 | +0.11 | 4.62 | 14.6 | 780 | 1.24e+03 | 9.5 |
| 30 | +1.92 | 2.66 | 30.2 | 907 | 1.2e+03 | -24 |
| 31 | +7.91 | 0 **x** | (84.9) | (127) | (886) | (-2.58) |
| 33 | +2.68 | 0 **x** | (44.5) | (670) | (1.27e+03) | (-5.29) |
| 34 | -0.81 | 3.35 | 18.3 | 1.12e+03 | 2.31e+03 | -9.43 |
| 37 | +0.81 | 2.57 | 56.7 | 886 | 1.39e+03 | -4.6 |
| 40 | +1.21 | 0.449 **x** | (70.6) | (719) | (1.3e+03) | (-6.41) |
| 41 | +4.88 | 0.186 **x** | (54.7) | (354) | (1.08e+03) | (-12.2) |
| 42 | +5.76 | 0.957 **x** | (23.5) | (255) | (940) | (-1.03) |
| 44 | +5.43 | 1.05 | 32.4 | 964 | 1.2e+03 | -4.73 |
| 45 | -0.40 | 3.91 | 21.5 | 982 | 1.4e+03 | -18.7 |
| 48 | +2.85 | 0.976 **x** | (66.3) | (771) | (1.21e+03) | (-4.04) |
| 50 | +3.72 | 0.42 **x** | (62.7) | (775) | (1.28e+03) | (-13.6) |

**step 2**: 13 plausible, 6 with sheets (need 5); not-sheeted 33, 36, 41, 42, 44, 49, 50 (sheets 0-0.83%)

| seed | run dT | sheets % | median speed | p99 | median H | sea level change |
|---|---|---|---|---|---|---|
| 27 | +0.75 | 4.13 | 25.4 | 1.23e+03 | 1.45e+03 | -17.9 |
| 30 | -2.29 | 2.29 | 41.1 | 1.04e+03 | 1.51e+03 | -23.3 |
| 35 | -0.20 | 1.78 | 46.4 | 886 | 1.15e+03 | -15 |
| 37 | -0.26 | 3.22 | 33.2 | 1.07e+03 | 1.32e+03 | -11.8 |
| 39 | -0.19 | 1.39 | 41.7 | 893 | 1.39e+03 | -19 |
| 43 | +0.78 | 2.2 | 20.9 | 458 | 1.07e+03 | -9.56 |

**A20**: 8 plausible, 4 with sheets (need 5: **red**); not-sheeted 29, 41, 47, 48 (sheets 0.03-0.77%)

| seed | run dT | sheets % | median speed | p99 | median H | sea level change |
|---|---|---|---|---|---|---|
| 30 | -2.01 | 9.08 | 14 | 1.15e+03 | 2.06e+03 | -34.6 **x** |
| 32 | +2.57 | 3.09 | 15.8 | 900 | 1.15e+03 | -6.36 |
| 34 | +0.37 | 1.14 | 128 **x** | 1.02e+03 | 1.35e+03 | -15.7 |
| 43 | +1.79 | 1.71 | 49 | 750 | 1.25e+03 | -11 |

## Files

The scripts were run from each tree's root with `PYTHONPATH=.:tests`. Their scratch paths are this session's.

| file | what it is |
|---|---|
| `scan.py` | the per-seed numbers through the tests' own case functions |
| `xswap.sh`, `xswap.py`, `xswap.txt` | the 24-world climate swap |
| `breaks.sh`, `break3.py`, `break1.txt`-`break3.txt` | the three deliberate breaks |
| `tables.py` | builds the tables above from the outputs |

## The diff of the three test modules

(Plus `tests/seeds.py`, which is new, and the `sources4` fixture in `tests/conftest.py`.)

```diff
diff --git a/tests/test_timezoom.py b/tests/test_timezoom.py
index 07de2e4..e018f52 100644
--- a/tests/test_timezoom.py
+++ b/tests/test_timezoom.py
@@ -11,6 +11,8 @@ from planet.timezoom.forcing import orbit_k, own_k
 from planet.timezoom.geometry import geometry
 from planet.timezoom.ice import shelf_step
 
+import seeds
+
 NO_ORBIT = dict(obliquity_amp=0.0, ecc_mean=0.0, ecc_100=0.0, ecc_400=0.0, orbit_ref="mean")
 
 
@@ -27,14 +29,19 @@ def cold_run(cold_src):
     return Z.simulate(cold_src, kyr=40, step=0.5, every=2.0)
 
 
-def test_glacial_cooling_turns_forest_to_tundra_and_cools_further(sim4):
+def test_glacial_cooling_turns_forest_to_tundra_and_cools_further(sources4):
     """PW-450: plants grown to balance with the start, then on a climate 4 C colder, lose forest toward the
     pole; the lying snow it no longer hides brightens the ground, which cools the land (the local
-    correction) and the planet (the global term, in dTg)."""
+    correction) and the planet (the global term, in dTg). On each of the L4 worlds (seeds.SEEDS4), at least
+    seeds.PASS_RATE of them (one world is a chaotic run's draw: PW-640)."""
+    seeds.check_rate("forest to tundra", seeds.run_case(_forest_case, sources4))
+
+
+def _forest_case(src, out):
+    """One world's assertions (as the single-seed test on sim4 had them); its numbers in out."""
     from planet import climate
     from planet.timezoom.plants import Plants
 
-    src = Z.source_from_sim(sim4)
     g, tilt = src["grid"], src["tilt"]
     elev, H = np.asarray(src["elev"], float), np.maximum(np.asarray(src["ice"], float), 0.0)
     grounded = (H > 1.0) & (elev > 0)
@@ -51,6 +58,9 @@ def test_glacial_cooling_turns_forest_to_tundra_and_cools_further(sim4):
     t0 = c["temp"].copy()
     c = pl.step(10.0, c, surf, grounded, H, -1.0, compute(-4.0))
     lost = (surf > 0) & ~grounded & (np.abs(g.lat) > 40) & (tree0 - pl.tree > 0.2)
+    out.update(run_dT=float(src["dT"]), lost=int(lost.sum()),
+               cooling=float((c["temp"] - t0)[lost].mean()) if lost.any() else float("nan"),
+               F_wm2=float(pl.series[-1]["F_wm2"]), dT_target=float(pl.dT_target))
     assert lost.sum() >= 5
     assert (c["temp"] - t0)[lost].mean() < -0.1  # the snow it hid now lies open
     assert pl.series[-1]["F_wm2"] < 0 and pl.dT_target < 0
diff --git a/tests/test_timezoom_consistency.py b/tests/test_timezoom_consistency.py
index b65beed..fbe7f5e 100644
--- a/tests/test_timezoom_consistency.py
+++ b/tests/test_timezoom_consistency.py
@@ -1,8 +1,9 @@
 """The time zoom from a run's moment starts close to its own balance (PW-418, PW-366): the run's ice
 rule (earth.ice_sheets, as earth.update_climate runs it) makes the sheets of a cold moment, then the time
 zoom runs 20 kyr with no orbital swing (so the glacial index stays 0: an interglacial). Level 5, 300 Myr, 4 C
-colder; the first of SEEDS whose moment is a plausible world with polar land (the run is chaotic,
-so the seed used to be re-picked by hand: seed 2 lost most of its polar ice after PW-300, seed 1 after PW-549)."""
+colder; every seed of SEEDS whose moment is a plausible world with polar land, and the drift tests on the
+ones with sheets (the run is chaotic, so one seed's world flips with any climate change: PW-623, PW-640; the
+seed used to be re-picked by hand: seed 2 lost most of its polar ice after PW-300, seed 1 after PW-549)."""
 
 from types import SimpleNamespace
 
@@ -16,6 +17,7 @@ from planet.tectonics import earth
 from planet.tectonics.isostasy import ice_load, land_view
 
 from helpers import run_sim
+import seeds
 
 pytestmark = pytest.mark.slow
 UNFORCED = dict(obliquity_amp=0.0, ecc_mean=0.0, ecc_100=0.0, ecc_400=0.0, orbit_ref="mean")
@@ -29,12 +31,11 @@ FLT = 1 - P.RHO_I / P.RHO_W
 # The source: a 300 Myr L5 run, whose climate feeds back on its tectonics and erosion, so any climate change
 # gives another world (PW-582 attempt 2 turned seed 4 into 6 plates at -314 m of sea level). The property under
 # test (at I = 0 the zoom keeps the run's ice) needs an ordinary world with polar land, not a particular one:
-# the first of SEEDS whose cold moment meets the precondition below, so the fixture tracks the current code
-# without riding on one chaotic world.
-SEEDS = tuple(range(25, 36))
-# (On the mature start with the CO2 stock, PW-576, 13 of seeds 4-35 meet the precondition, but most of them are warm
-# moments that 4 C of cooling leaves with < 1% under sheets: 4 0.9%, 5 0.3%, 8 0.9%, 15 0.2%, 20 1.1%, 23 0.2%,
-# 25 3.2%, 27 0.5%; 28-34 1.5-6.3%. The list starts at 25, the first with a margin; the sheets test stays a check.)
+# every seed of SEEDS whose cold moment meets the precondition below, so the fixture tracks the current code
+# without riding on one chaotic world. Of those, the ones with sheets (> 1% of cells under > 1 m: else the drift
+# tests prove nothing) are the drift tests' worlds; each drift test asks seeds.PASS_RATE of them to pass.
+SEEDS = tuple(range(25, 51))  # (lane A16's scan window; 14 of them are plausible on main 86d3806, 7 with sheets)
+MIN_SHEETED = 5  # plausible seeds with sheets the window must give (so a 70% bar on them tolerates one world)
 SL_MAX = 150.0  # m: the run's sea level within this of today's
 MOC_MIN = 2.0  # Sv: the cold climate overturns in both hemispheres
 POLAR_LAND = 0.25  # land's share of the cap poleward of 60 deg, in at least one hemisphere (where sheets can grow)
@@ -71,26 +72,68 @@ def _plausible(src, c):
             and cap >= POLAR_LAND)
 
 
+def _moment(seed):
+    """The seed's L5 300 Myr moment made 4 C colder (_cold) and its 20 kyr zoom, if it meets _plausible's
+    precondition (else None): (src, zoom). Its run's dT is kept as src["run_dT"]."""
+    src0 = Z.source_from_sim(run_sim(level=5, seed=seed, myr=300))
+    src, c = _cold(src0)
+    if not _plausible(src, c):
+        return None
+    src["run_dT"] = float(src0["dT"])
+    return src, Z.simulate(src, 20.0, 0.5, 2.0, Z.TZParams(**UNFORCED, **RUN_RULE))
+
+
 @pytest.fixture(scope="module")
-def cold_moment():
-    """A run's moment made 4 C colder (_cold), the first of SEEDS that meets _plausible's precondition."""
-    for seed in SEEDS:
-        src, c = _cold(Z.source_from_sim(run_sim(level=5, seed=seed, myr=300)))
-        if _plausible(src, c):
-            break
-    else:
+def cold_moments(tmp_path_factory):
+    """Every seed of SEEDS whose cold moment meets _plausible's precondition: [(seed, (src, zoom))]."""
+    def build():
+        return [(s, m) for s, m in zip(SEEDS, seeds.pool_map(_moment, SEEDS)) if m is not None]
+    got = seeds.shared(tmp_path_factory, "cold_moments", build)
+    if not got:
         pytest.fail(f"no seed of {SEEDS} gives a plausible source")
-    return src, Z.simulate(src, 20.0, 0.5, 2.0, Z.TZParams(**UNFORCED, **RUN_RULE))
+    return got
+
+
+def _rows(case, moments):
+    """case's unchanged assertions on each eligible seed, here (the moments are big to ship to a pool)."""
+    rows = []
+    for seed, m in moments:
+        out = dict(run_dT=m[0]["run_dT"])
+        try:
+            case(m, out)
+            rows.append((seed, True, out))
+        except AssertionError as e:
+            rows.append((seed, False, dict(out, error=(str(e).splitlines() or [""])[0])))
+    return rows
+
 
+def test_cold_moment_has_sheets(cold_moments):
+    """The window gives the drift tests at least MIN_SHEETED plausible worlds with sheets (each seed's
+    assertion as the single-seed test had it, in _sheets_case)."""
+    rows = _rows(_sheets_case, cold_moments)
+    k = sum(p for _, p, _ in rows)
+    table = "\n".join(f"  seed {s:>3}: {'sheets' if p else 'none'}  {o}" for s, p, o in rows)
+    print(f"cold moments with sheets: {k} of {len(rows)} plausible\n{table}")
+    assert k >= MIN_SHEETED, f"{k} of {len(rows)} plausible seeds have sheets (need {MIN_SHEETED})\n{table}"
 
-def test_cold_moment_has_sheets(cold_moment):
+
+def _sheeted(cold_moments):
+    return [(s, m) for s, m in cold_moments if _rows(_sheets_case, [(s, m)])[0][1]]
+
+
+def _sheets_case(cold_moment, out):
     src, _ = cold_moment
+    out.update(sheets_pct=100 * float((src["ice"] > 1).mean()))
     assert (src["ice"] > 1).mean() > 0.01  # (else the drift test below proves nothing)
 
 
-def test_ice_speeds_plausible(cold_moment):
+def test_ice_speeds_plausible(cold_moments):
     """Shallow-ice speeds (D |grad s| / H, the steepest way down) under grounded sheets: interiors
     metres to tens of m/yr, outlets up to a few km/yr."""
+    seeds.check_rate("ice speeds plausible", _rows(_speeds_case, _sheeted(cold_moments)))
+
+
+def _speeds_case(cold_moment, out):
     src, r = cold_moment
     g, G, p, st = src["grid"], geometry(src["grid"]), Z.TZParams(), r["state"]
     H, bed, sl = st["H"], st["bed"], st["sl"]
@@ -102,16 +145,25 @@ def test_ice_speeds_plausible(cold_moment):
     D = np.minimum(gamma * H**5 * grad**2, p.d_cap)
     sheet = (H > 100) & (bed + H > sl + FLT * H)
     u = (D * grad / np.maximum(H, 1.0))[sheet]
+    out.update(sheet_cells=int(sheet.sum()), u_median=float(np.median(u)) if sheet.any() else float("nan"),
+               u_p99=float(np.percentile(u, 99)) if sheet.any() else float("nan"),
+               H_median=float(np.median(H[sheet])) if sheet.any() else float("nan"))
     assert 1.0 < np.median(u) < 100.0
     assert np.percentile(u, 99) < 5000.0
     assert 500 < np.median(H[sheet]) < 3500
 
 
-def test_ice_at_index_zero_is_the_runs(cold_moment):
+def test_ice_at_index_zero_is_the_runs(cold_moments):
     """At I = 0 (an interglacial: the run's own climate) the zoom keeps the run's ice: with no orbital swing
     the default index never builds, and sea level moves little (PW-366: -43 m in 20 kyr here while the
     run's sheets were 50 kPa profiles with their margins' inner-edge rise and the time zoom melted its
     margins before its flow; PW-471: the index replaced the CO2 and ice-albedo feedbacks)."""
+    seeds.check_rate("ice at index zero", _rows(_index_zero_case, _sheeted(cold_moments)))
+
+
+def _index_zero_case(cold_moment, out):
     _, r = cold_moment
+    out.update(index_max=max(f["stats"]["glacial_index"] for f in r["frames"]),
+               sl_change_m=float(r["frames"][-1]["stats"]["sea_level_change_m"]))
     assert all(f["stats"]["glacial_index"] == 0.0 for f in r["frames"])
     assert abs(r["frames"][-1]["stats"]["sea_level_change_m"]) < 25.0
diff --git a/tests/test_timezoom_cycle.py b/tests/test_timezoom_cycle.py
index a3ca692..e7a4675 100644
--- a/tests/test_timezoom_cycle.py
+++ b/tests/test_timezoom_cycle.py
@@ -7,6 +7,8 @@ import pytest
 from planet import orbit as O, timezoom as Z
 from planet.timezoom.cycle import BETWEEN, BUILDING, ENDING, Index, cooling
 
+import seeds
+
 STEP = 0.5
 NO_ORBIT = dict(obliquity_amp=0.0, ecc_mean=0.0, ecc_100=0.0, ecc_400=0.0, orbit_ref="mean")
 
@@ -67,9 +69,14 @@ def test_cooling_is_planet_relative():
 
 @pytest.fixture(scope="module")
 def icehouse(sim4):
-    """sim4's moment 4 C colder, 200 kyr with the index (6 C at a glacial maximum, by hand: L4's planet is
+    """sim4's moment as _icehouse makes it."""
+    return _icehouse(Z.source_from_sim(sim4))
+
+
+def _icehouse(src):
+    """A moment 4 C colder, 200 kyr with the index (6 C at a glacial maximum, by hand: L4's planet is
     small) and without it; the plants local only, so dT_global is the index's alone."""
-    src = Z.source_from_sim(sim4)
+    src = dict(src)
     src["dT"] = src["dT"] - 4.0
     kw = dict(veg="local", phases="0,90,0,90")
     return [Z.simulate(src, kyr=200, step=STEP, every=2.0, params=Z.TZParams(index=i, glacial_dt=6.0, **kw))
@@ -86,16 +93,23 @@ def test_zoom_climate_follows_the_index(icehouse):
     assert all(f["stats"]["dT_global"] == 0.0 for f in off["frames"])
 
 
-def test_glacials_grow_ice_and_endings_melt_it_fast(icehouse):
+def test_glacials_grow_ice_and_endings_melt_it_fast(sources4):
     """The ice follows the index: lower seas at a glacial maximum than without it, and an ending gives
-    back most of the glacial's extra ice within 15 kyr."""
-    on, off = icehouse
+    back most of the glacial's extra ice within 15 kyr. On each of the L4 worlds (seeds.SEEDS4) made an
+    icehouse (_icehouse), at least seeds.PASS_RATE of them (one world is a chaotic run's draw: PW-638)."""
+    seeds.check_rate("glacial endings", seeds.run_case(_endings_case, sources4))
+
+
+def _endings_case(src, out):
+    """One world's assertions (as the single-seed test on sim4's icehouse had them); its numbers in out."""
+    on, off = _icehouse(src)
     t = np.array([f["t"] for f in on["frames"]])
     sl_on = np.array([f["stats"]["sea_level_change_m"] for f in on["frames"]])
     sl_off = np.array([f["stats"]["sea_level_change_m"] for f in off["frames"]])
     e = on["cycle"]["endings"][0]
     i, j = np.searchsorted(t, e["t"]), np.searchsorted(t, e["t"] + 15.0)
     extra = sl_off[i] - sl_on[i]
-    print("glacial extra ice (m):", round(extra, 1), "left after 15 kyr:", round(sl_off[j] - sl_on[j], 1))
+    out.update(run_dT=float(src["dT"]), ending_kyr=float(e["t"]), extra_m=float(extra),
+               left_m=float(sl_off[j] - sl_on[j]))
     assert extra > 10.0
     assert sl_off[j] - sl_on[j] < 0.5 * extra
```
