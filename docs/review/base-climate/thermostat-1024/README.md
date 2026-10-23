# Thermostat lane 2026-10-24 (serial run-physics lane, after merge-1024)

Branch `worktree-agent-aacd696776c504933`, from main 12b2b02 (merge-1024 steps 1-4 on it). Each step is its own
commit. Scripts here; raw outputs in the step folders. CPU: at most ~24 cores (health `--workers 8 --threads 3`,
pytest `-n 4` with `PW_SEED_WORKERS=3`).

## Before anything: the mantle basis cache picks the world

This lane's fresh worktree built its own `planet/tectonics/__pycache__/mantle_basis_2562_*.npy` (two processes
started at once). It differs from the main checkout's by whole columns (up to 0.15): `mantle.basis` takes an SVD's
columns per degree, which are arbitrary within a degree, and `init` puts the random mantle eddies on them. With
that cache, sim4 is another world (25.0% land and 11 plates, against 30.7% and 6), and PW-636's tree passed the bed
test (27.1 m against 84.7 m) where merge-1024 saw it fail. With the main checkout's cache copied in, the failure
reproduces exactly (47.1 m against 46.2 m). Other trees on this machine hold a third variant (L5, `7bca5b...` in the
pw460/pw462 scratch trees). Every tree of this lane uses the main checkout's bases (md5 `800f36...` L4, `10b0cf...`
L5, `13daae...` L6). Draft `draft-mantle-basis-cache-picks-the-world.md` (canonical basis: a run-physics change).

## Step 1: PW-680, option C: the bed test's lag term counted the sheet's net volume, not the cell's load

`test_bed_settles_under_the_ice`'s tolerance is 5% of the dip + a lag term + 20 m. Its docstring says a bed relaxing
on `iso_tau` lags its load by about the load change of its last `iso_tau`. The code measured that with the **global
ice volume**: (V(T) - V(T - 3 kyr)) / (V(T) - V(0)), clamped at 0, times the median dip.

**The check** (`lagcheck.py`: sim4 8 C colder, frames every 0.5 kyr, the code's own discrete relaxation replayed on
each frame's grounded load). On PW-636's world:
- `bed - want` on the grown cells is the replayed lag to within 0.7 m (median): the error *is* the relaxation lag,
  nothing else.
- The sheet's volume is flat over the last 3 kyr (37.38 -> 37.37 Mkm3), so the global lag share is 0.007 and the term
  adds 3.3 m. But the ice moves within the sheet: each grown cell's load changed by a median 32 m over the last
  `iso_tau` (7% of its grown load), some up, some down, so the beds lag both ways and the median |bed - want| is
  47.1 m.
- So the term under-counts whenever ice redistributes at a steady volume, and over-counts when the volume still
  grows but the grown cells don't (main seed 2 below: share 0.10 adds 54 m, the cells lag 18 m). It is the wrong
  quantity, not a loose constant.

**The fix (harness only, `tests/test_timezoom.py`):** the lag term is each grown cell's own load change over the last
`iso_tau` (|ice_load(ice_T) - ice_load(ice_{T - 3 kyr})|, the frames' grounded ice, linear between the 2 kyr frames),
median over the cells. The 5% of the dip, the 20 m, the `grew` rule and the "pressed down" assertion are unchanged.

**Seeds 1-24 (the L4 worlds, 8 C colder; `bedtol.py`), old vs new tolerance:**

| tree / draw | eligible | old tolerance passes | new tolerance passes | the misses |
|---|---|---|---|---|
| main, 0 | 24 | 24 | 24 | |
| main, +0.001 | 24 | 24 | 24 | |
| main, -0.001 | 24 | 22 | 24 | old: two seeds where the cell lag exceeds a clamped lag share |
| PW-636, 0 | 24 | 22 (seed 1 = sim4: 47.1 / 46.2; seed 8: 46.1 / 42.0) | 24 (seed 1: 47.1 / 97.1) | |
| PW-636, +0.001 | 24 | 24 | 24 | |
| PW-636, -0.001 | 24 | 23 | 23 | seed 16, both: the "pressed down" assertion, not the tolerance |
| main, isostasy relaxing to 0.8 of the load | 24 | 1 | 1 | the break is caught on 23 of 24 by both |
| main, the bed frozen | 24 | 0 | 0 | |

The new tolerance is tighter than the old on 15 of 24 PW-636 worlds (16 of 24 on main) and looser on the rest; it tracks the error (the
median error / the cell lag: 47.1 / 54.2, 46.1 / 47.8, 102.7 / 120.7 on the deepest misses). Both breaks are caught
as before. The test stays a single-world test on sim4 (option A wasn't needed): its tolerance now measures the
physics it names, so a chaotic world shouldn't flip it by its sheet's net volume.

Full `pytest -q -n 4`: **611 passed** in 1000 s (`step1/full.txt`). Main's physics is unchanged, so the health and
Earth numbers are merge-1024 step 4's (main 12b2b02 has no run-physics change since 641ce4f).

## Step 2: PW-636, FLORA_PACE 0.8 (fd7c174 cherry-picked)

The change lines are fd7c174's (`vegetation.FLORA_PACE`, `group_windows`, overview). Conflicts: PW-636's Updates
(both kept) and `tests/golden/sim_L4_s1_60myr.json`, **regenerated on purpose** (`--update-golden`; identical to
merge-1024's step 5 golden). The branch's draft `draft-earlier-flora-deepens-ice.md` is left out: it is PW-657.

- Full `pytest -q -n 4`: **611 passed** in 1087 s (`step2/full.txt`). The bed test passes on sim4 with step 1's
  lag (47.1 m against 97.1 m). The multi-seed tests are merge-1024 step 5's three draws (all green): the runs are
  bit-identical here (below), and the bed test reads only sim4, which the offset doesn't touch.
- **Health** (`step2/health_def_101.md`). This lane's sweep on PW-636's tree reproduces merge-1024's step 5 sweep seed
  for seed, so the step-1 baseline is merge-1024's step 4 sweep (the same physics):

| sweep | pooled % kf < -150 m (step 1 -> 2) | seeds > 10% | old bar F | new bar F | icehouse % median / mean |
|---|---|---|---|---|---|
| defaults | 4.4 -> 17.4 | 1 -> 3 | 1 -> 0 | 2 -> 5 | 35.3 / 33.3 -> 53.0 / 46.1 |
| 101-108 | 20.1 -> 6.6 | 5 -> 1 | 2 -> 1 | 3 -> 4 | 56.9 / 53.2 -> 42.2 / 43.4 |
| all 16 | 12.3 +- 4.4 -> 12.0 +- 5.8 | 6 -> 4 | 3 -> 1 | 5 -> 9 | 47.1 / 43.3 -> 47.0 / 44.7 |

  Paired by seed: deep share -0.3 +- 7.4 points, icehouse share +1.5 +- 9.3 (`step2/hpair.txt`). No signal either
  way; the third seed set is in step 3.
- **Earth:** unchanged by PW-636 (merge-1024 `step5_not_kept/earth`, the same physics). `tools/scorecard.py`
  (`step2/scorecard.txt`): Earth group agreement 71.1% (exact 33.9%), log-rain r 0.649; seeds 1 and 2 at 1 Gyr: land
  34.0 / 33.2%, ice 1.1 / 1.9%, dry 27.5 / 21.2%, crust volume x0.992 / x0.967, land NPP 361 / 391, C4 at 720 / 712 Myr.

Green to merge.
