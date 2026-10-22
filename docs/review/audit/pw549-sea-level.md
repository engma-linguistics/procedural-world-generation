# PW-549: total sea level ends 1 Gyr far below 0 (diagnosis and fix)

Branch `worktree-agent-ac426d181f23ccb8a`, from main 04be51c (coast_loss, PW-514 option A, included).
Scratch: session scratchpad `pw549/` (`diag.py`: per 4 Myr sample, `tools/sealevel.py`'s fields plus mean cell
speed, ridge / trench length and the area they make / consume, the floor's half-space heat flux, mean age at the
trenches, and a water-conserving sea level from the absolute hypsometry; `ana.py`, `means.py`, `events.py`).
Seeds: the cold-era set 3199 11 2 21 1 5 7 13 42 99, L6, 1 Gyr; 5 of them also to 2 Gyr.

## 1. Diagnosis (main, 10 seeds x 1 Gyr)

Per 100 Myr, seed medians:

| Myr | 0 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 |
|---|---|---|---|---|---|---|---|---|---|---|
| ocean age Myr | 48 | 46 | 58 | 50 | 54 | 57 | 57 | 64 | 72 | 74 |

Over 2 Gyr (seeds 2 99 5 3199 11), mean age per 200 Myr: 46-50 in 0-200 Myr, ~55 at 200-600, 66-92 at
800-1000, then **60-120 Myr through 1-2 Gyr with no further trend** (means 1-2 Gyr: 69 / 90 / 95 / 79 / 72).

What changes:
- **Spreading falls because rifting stops, not because plates slow.** Mean cell speed is 5-6.5 cm/yr in the
  first 150 Myr (breakup of the starting supercontinent) and ~3.5-4.2 cm/yr from ~300 Myr to the end on every
  seed, old-ocean or not. What drops is the length of the ridge system and trenches (unnormalised grid edge
  sums: ~260 000 km early, 120-180 000 km late on the deep-end seeds 2 5 7 13 99, steady on 3199 11 1 42) and
  the plate count (12-13 -> 6-9). Stress rifts per 200 Myr: 10-16 in the first 400 Myr, **1-5 after ~600
  Myr** on the deep seeds (8-10 on the seeds whose ocean stays young), staying there to 2 Gyr. New plates
  then come mostly from margin subduction (9-21 per 200 Myr late).
- **The floor's heat loss falls with it.** Half-space ocean heat flux (490/sqrt(age), mean over the floor):
  95-104 mW/m2 in the first 400 Myr (Earth's ocean ~100), 75-85 late on the deep seeds, at a constant mantle
  heat (`heat_start` 1: earth.heat = 1 throughout). Nothing in the model notices: plate mobility is
  `mobility x heat()^0.5`, a prescribed function of time, so the planet loses 15-30% less heat than it makes for
  hundreds of Myr without consequence.
- **The reference is not the main problem.** The mean floor depth over 50-1000 Myr, all seeds, is -4921 m
  against the -4853 m reference: -46 m of sea. The 48 Myr start is the model's own early state; it's the
  late regime (75-85 Myr over 1-2 Gyr) that is old. Re-centring 0 on the 2 Gyr mean (~-135 m) would move the
  whole record by +135 m and give the first 600 Myr a permanent +100..+250 m highstand instead.
- **The water budget isn't exactly conserved, but conserving it isn't the fix.** Filling the absolute
  hypsometry (all cells, continents, shelves, sediment) with the starting water minus the ice gives a level
  that swings far more (per-100-Myr means -570..+300 m) and sits mostly above the formula's, because sediment,
  arc crust and plateaus also fill the basins; those books (sediment, crust growth) are not built to close
  water to tens of metres, so a level that reads them would import their errors. The mean-depth formula is
  the cleaner of the two. Not pursued.
- Land area doesn't follow the sea: corr(sea level, land %) -0.62..+0.44 by seed, land 29-39% throughout.
  Erosion relevels the continents to the sea within ~100 Myr, so the deep sea level is mostly a datum offset
  and the slicing-time shelves (PW-548) are the visible harm.
- Ice: the ice part is under -150 m at 1 Gyr on 3 of 10 seeds; the basin term is -144..-349 m on 9 of 10
  (PW-514 option A's table). Correlated (eras of old, slow floor are also the cold ones: less ridge CO2).

So it is **(c), both, but not in the proportions the ticket guessed**:
- (a) the floor ages because stress rifting dies out after the starting supercontinent's breakup (a tectonic
  regime change, draft `draft-stress-rifts-die-out-late.md`), and by 1-2 Gyr the model's ocean is 60-120 Myr;
- (b) **the reference was measured on the wrong window.** PW-293's owner decision was "sea level 0 = the model's
  own steady ocean", and it measured that over the first 500 Myr (health --quick), which is mostly the breakup:
  stress rifts 10-16 per 200 Myr, floor ~48-55 Myr. After the 300 Myr warm-up (the owner's cut for bars) the
  model's ocean averages **-4962 m, mean age 62 Myr** (10 seeds x 300-1000 Myr; median 59.6), against the
  -4853 m reference: the whole post-warm-up record read ~-75 m low, and the late old-ocean seeds -150..-350 m.
- Not the water budget (above), not continental area (ocean share 59 -> 56-57% moves the formula's sea by
  nothing; the conserving level by tens of m and the other way), not isostasy.

## 2. Tried and not kept: the mantle's heat budget (Tozer's thermostat)

The physics gap behind (a) looked like a missing feedback: plate mobility is `mobility x heat()^0.5`, a function of
time, so a planet can lose 15-30% less heat than its mantle makes for 500 Myr. I added `mantle.heat_budget`: the
imbalance between what the mantle makes (the start's half-space ocean loss x heat(), the start being a steady
ocean) and what the floor loses (490/sqrt(age), 48 mW/m2 floor) integrates into a log vigor, plates moving
e^vigor_log more freely. `mantle_response` 340 Myr was derived (4.8e27 J/K, ~32 TW, viscosity -1.4%/K), not fitted.

Result (10 seeds, 1 Gyr): vigor moved only 0.91-1.21x by 1 Gyr, floor mean age 62 (59 on main), in-band after 300
Myr median 72% (same), cold-era check 6/10 (main 8/10). It can't work here: slab-driven plates run at the slab's
terminal speed (slab_pull x age factor / slab_drag, PW-288), which mobility doesn't set, and the deficit is in
ridge length, not speed. Reverted; noted on the draft. (A stronger response would be a fitted gain: not done.)

## 3. Fix: sea level 0 measured on the model's long-run ocean

`setup.OCEAN_MAX_AGE` 144 -> **162 Myr** (start mean age 54): the triangular start whose mean depth after the
first 2 Myr step (what `depth_ref` reads) is the long-run mean, -4968..-4977 m on the 10 seeds against -4962
measured. Same method and definition as PW-293 (measured, not derived; 0 = the model's own ocean), on the window
after the warm-up instead of the warm-up itself. Nothing else changes: same formula, same limiter, no clamp. It is
a re-centring, so it moves the warm-up up by as much as it moves the rest: the breakup's young ocean now reads a
highstand (L4 test seeds: +43..+83 m on average over 0-300 Myr; L6 50-300 Myr in the offline estimate ~+85 m).

### Band
**-250..+300 m (the health envelope), after the 300 Myr warm-up, in >= 80% of keyframes, on ~70% of seeds.**
Why: Earth's Phanerozoic is -130 (LGM ice) .. +250 m (Cretaceous basins; Haq & Schutter 2008); the band gives
the ice ~-120 m and the basins ~+50 m of headroom beyond Earth's extremes, which a planet with deeper cold eras
and wider basin swings than Earth's last 540 Myr should get. It is planet-relative in the sense that matters:
0 is the planet's own long-run ocean (and starting water), not Earth's; the width is the one scale Earth gives.
"Most of the time" as 80% leaves room for one deep icehouse era per Gyr (PW-434's territory).

### Before / after (10 L6 seeds, 1 Gyr, main = 04be51c)

Total sea level, keyframes after 300 Myr (with 50 Myr warm-up and none in brackets for the medians):

| seed | main end (ice + basin) | main min | main % in band | fixed end (ice + basin) | fixed min | fixed % in band |
|---|---|---|---|---|---|---|
| 3199 | +5 (-15 +20) | -466 | 88 | -86 (-29 -57) | -325 | 93 |
| 11 | -13 (-26 +13) | -227 | 100 | -152 (-8 -144) | -184 | 100 |
| 2 | -135 (-12 -123) | -612 | 45 | -472 (-238 -234) | -597 | 70 |
| 21 | -92 (-8 -83) | -454 | 86 | -189 (-66 -122) | -346 | 93 |
| 1 | -47 (-17 -30) | -448 | 79 | +106 (-14 +120) | -460 | 82 |
| 5 | -575 (-278 -297) | -575 | 68 | -131 (-20 -111) | -586 | 74 |
| 7 | -432 (-160 -272) | -510 | 66 | -154 (-28 -127) | -350 | 95 |
| 13 | -263 (-36 -227) | -602 | 70 | -384 (-115 -269) | -523 | 56 |
| 42 | -88 (-29 -59) | -729 | 73 | -154 (-30 -124) | -294 | 91 |
| 99 | -550 (-212 -338) | -576 | 32 | -336 (-165 -171) | -391 | 92 |
| **median** | -113 | -543 | **72% (>= 80%: 3/10)** | -154 | -371 | **92% (>= 80%: 7/10)** |
| after 50 Myr | | | 76% (4/10) | | | 93% (8/10) |
| after 0 Myr | | | 77% (4/10) | | | 94% (8/10) |

The end values are single keyframes of chaotic trajectories (the start's ages change every run's history, so
seed N "fixed" is a different planet from seed N on main); the in-band share and the minimum are the robust
numbers. The deepest frames left are cold eras (ice part -240..-280 on seeds 2, 13; PW-434, v2), with an old
late floor on the same seeds (ages 96-106 Myr at 1 Gyr, the rifting draft).

Cold-era check (ice part on 4 Myr samples, worst >= -450 m or <= 2% below -430 m): main **8/10**, fixed **7/10**
(fails: 11 -491 / 3.6%, 5 -483 / 3.2%, 13 -456 / 2.4%; main's: 2, 42). Time with ice below -150 m: median 13.5%
(main 22%). The heat-budget variant was 6/10.

### Other checks
- Earth checks: the change is in `setup.initial_state` only, which neither the Earth climate (`earth_check`, the
  scorecard's Earth line: group 70.6% / exact 30.9% / log-rain corr 0.617, identical before and after) nor the
  Earth time zoom uses. `tools/earth_check.py` ran unchanged.
- Scorecard (`--jobs 3 --threads 2`, L6 seeds 1 / 2, 1 Gyr), before -> after: land 31.5 / 30.3 -> 33.1 / 33.5 %;
  crust 41.2 / 42.5 -> 42.8 / 42.7 %; volume x0.961 / 0.94 -> 0.988 / 0.962; dry 14.2 / 24.4 -> 18.2 / 16.8 %;
  ice 1.4 / 1.1 -> 1.1 / 8.8 % (seed 2 ends in a cold era); ocean age 62.8 / 60.1 -> 56.5 / 95.8 Myr;
  NPP 356 / 341 -> 344 / 273; trees 29.8 / 21.7 -> 21.7 / 21.9 %.
- `uv run pytest -q -n 6`: 561 passed.
  - Golden `tests/golden/sim_L4_s1_60myr.json` regenerated (intended: the start ages change every run).
  - `tests/test_sea_level.py`: the warm-up test now asserts the breakup highstand (mean over 0-300 Myr in
    0..+150 m, each seed -50..+200; measured +43..+83) instead of a mean near 0.
  - `tests/test_timezoom_consistency.py`: seed 1's L5 300 Myr moment lost its polar ice with the new trajectory
    (0.2% iced, test needs > 1%); now seed 4 (4.3%), as the seed 2 -> 1 switch after PW-300.

## 4. Judgement call to flag
This re-centres sea level 0 by measurement under PW-293's own definition, with the owner's 300 Myr warm-up as the
window. It does not change what 0 means, but it does make the warm-up read high. The alternative readings
(re-centre on the 2 Gyr mean, ~-135 m deeper still; or a slowly relearning reference) do change the meaning and
were not taken. The underlying tectonic regime change (rifts dying out) is left as a draft, unscheduled.
