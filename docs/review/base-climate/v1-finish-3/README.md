# v1-finish-3: PW-725, why L7 runs are icier than L6 (2026-10-24)

Branch `worktree-agent-a4b06513c601e3751`, from main 1f0fae4. Scripts here; raw runs in the session scratchpad
`v1f3/` (`eq/`: eqcurve.py's equilibria; `base/`: the four showcase seeds at L6 on main; `fix_d1`, `fix_d2`: the
same seeds at L7 with the fix, climate_offset 0 and +0.001). CPU: at most ~24 threads (L7 runs at 3 numba threads).

## The cause: the margin band was one ring of cells, whatever their size

`eqcurve.py` takes one planet (an L7 run's checkpoint) and the same planet averaged onto the L6 grid (L6's cells
are L7's first 40962 vertices; each L6 cell the mean of the L7 cells nearest it), and at a fixed dT updates the
climate and the ice sheets as `earth.update_climate` does (climate.compute on the ice-loaded bed, then
`earth.ice_sheets`, then the load), vegetation held at the checkpoint's. Same planet, same dT, same climate: any
difference in ice is the ice rule's resolution dependence, with the carbon cycle, the drift and the history out.

89c2ab @ 700 Myr, dT 0, from no ice (`eq/plain`, `eq/m120`):

| variant | update 1 sea_ice / iced land | update 3 | snowline land (update 1) | mean T |
|---|---|---|---|---|
| L6 (averaged planet) | -28 m / 6.2% | -40 m / 7.8% | 0.81% | 13.73 C |
| L7 (its own fields) | **-100 m / 13.3%** | | 0.79% | 13.72 C |
| L7s (L6's averaged fields on the L7 grid) | -74 m / 12.1% | -125 m / 15.2% | 0.86% | 13.71 C |
| L7, margin band 120 km (2 rings) | -35 m / 7.4% | -43 m / 8.6% | 0.79% | 13.72 C |

The climate is the same at both levels (mean temperature within 0.02 C, the snowline's land, where a cap can
start, within 0.02 points), yet L7 grows twice the iced land and 3.5x the ice in one update. Most of it stays when
L7 sees L6's smoothed relief (L7s): it is the grid's cell size, not the finer peaks. And it goes when the margin
band is as wide in km at L7 as at L6.

What the band is: `earth._ice_pass` takes a sheet's margin (old ice next to bare land) to melt as the sheet's
outermost 10 km (EDGE_H, ~400 m thick), and its interior at its own (Nye, cell-mean) thickness. The margin was
the one ring of cells next to bare land: ~120 km wide at L6 (the cell size the rule was set at, PW-366: "at ~110
km cells a margin cell's snow and melt are its edge's"), ~60 km at L7. At L7 the cells 60-120 km in from the edge
counted at their full ~1 km thickness, 4 C colder by the lapse rate than as margin, so every sheet's ablation
zone was half as wide and the sheets spread until the cold eras ran away. Not physics that should depend on
resolution: the same sheet on the same climate.

## The fix: the band in km (`earth.margin_band`, MARGIN_KM = 120)

The margin band is the old ice within MARGIN_KM = 120 km of bare land, as rings of cells (round(120 / spacing),
at least one): one ring at L6 and coarser (bit-identical: the rule and every L6 result, goldens and the 32
seed-draws of v1-finish-2, stand), two at L7. Not a level-specific factor: the rule the run was calibrated with,
in km instead of cells. The honest successor stays PW-460 (the sub-cell ramp, `icemass.margin_ramp`, already in
the time zoom as `margin="ramp"`), v2 under PW-470; it would change L6 too and need the climate balance re-checked.
Test: `test_ice_margin_band_level_consistent`.

With the fix, the same planet's equilibria at the two levels (`eq/fix`, 4 updates at fixed dT):

| case | L6 sea_ice / iced land (update 4) | L7 | L7 / L6 |
|---|---|---|---|
| 89c2ab @ 700, dT -3, from no ice | -176 m / 17.9% | -202 m / 19.4% | 1.14 |
| 89c2ab @ 700, dT -1.5 | -84 m / 12.3% | -99 m / 13.4% | 1.18 |
| 89c2ab @ 700, dT +1.5 | -25 m / 5.6% | -23 m / 6.0% | 0.93 |
| 6ca373 @ 800, dT 0, from its ice | -55 m / 12.8% | -43 m / 11.6% | 0.78 |
| 6ca373 @ 800, dT +2, from its ice | -46 m / 11.0% | -42 m / 11.2% | 0.93 |

Within ~20% either way (before: 2-3.5x one way), the rest the relief's resolution (finer peaks, L7 vs L7s) and the
margins' last cell.

## 1 Gyr pass rate at L7 with the fix (`passrate.py` with LEVEL=7, `passrate_L7.txt`)

The four showcase seeds at L7, climate_offset 0 (`fix_d1`) and +0.001 (`fix_d2`), judged on 300-1000 Myr against
the owner's bar (icehouse <= 40%, no always-icebox, no hellhole):

| seed | L7 before (showcase run, same code otherwise) | L7 fix, draw 1 | L7 fix, draw 2 | L6 (main = fix at L6), draw 1 |
|---|---|---|---|---|
| 733847 | 70% (89c2ab) | 0% ok | 14% ok | 17% ok |
| 819014 | 79% (6ca373) | 89% ICEBOX | 75% ICEBOX | 55% F |
| 53669 | 63% (8b1617) | 26% ok | 40% ok | 43% F |
| 958504 | 67% (7f4f06) | 53% F | 3% ok | 9% ok |
| **pass / median** | **0/4, 68%** | **5/8 pooled (62%), median 33%** | | 2/4, median 30% |

(No run-physics commit landed between the showcase's c398e4d and this branch, so the showcase histories are the
"before". L6 is bit-identical with the fix: full pytest with the goldens unchanged, scorecard identical to the
previous line.)

The level effect is gone: the L7 icehouse median (33%) is L6's (33% over v1-finish-2's 32 draws; 30% on these four
seeds), and 5 of 8 draws pass against 0 of 4 before. 5/8 is under the ~70% bar by one draw, but its spread on 8
draws is +-17 points, and the same four seeds pass 2/4 at L6: these are a hard four, not a bad level. Seed 819014
is the icy outlier at both levels (L6 55%, L7 75-89%, deep ice -300..-400 m in 600-1000 Myr): an outlier seed, OK
by the bar's "outliers OK"; inbox draft `draft-seed-819014-icy-at-both-levels.md` (low) in case it says more than
one seed.

**Decision (delegated, evidence clear): fixed.** Resolution shouldn't matter for a planet's mean ice, and with the
band in km it doesn't, within the draws. Earth check and scorecard: unchanged (L6; the Earth climate never sees the
run's ice rule): Earth group agreement 71.1%, scorecard line identical to the one before but for the source hash.

## The showcase must be remade

The four L7 showcase histories (runs 89c2ab, 6ca373, 8b1617, 7f4f06; worlds a95cdc, 09262b, 730669, d86d34) were
made with the one-ring rule and spend 63-79% of 300-1000 Myr in an icehouse with ice to -369..-476 m: they fail the
bar on a rule that is now fixed. Their presents are interglacials (PW-700) and look fine, but the history the viewer
replays is the icier one. Remake started 2026-10-24 ~03:45 from this branch's be6f208 (`scratchpad/v1f3/make.sh`:
4 x `planet make --level 7`, random seeds 957317, 619496, 583167, 639472, 5 threads each, into the main checkout's
store; logs `v1f3/make/make1-4.log`, PIDs in `v1f3/make/pids`, ~2.5-3 h at this load). The coordinator records
their ids on PW-202 when they finish and lists the old ones as superseded (not deleted). Keep this worktree until
they finish: they run its code.

## Left

- `draft-timezoom-edge-margin-one-ring.md`: the time zoom's 'edge' margins are still one ring (v2, under PW-470).
- `draft-seed-819014-icy-at-both-levels.md`: one seed icy at both levels (low).
- L7 ice updates sometimes hit ICE_PASSES (201 passes, ~2 min per update on 6ca373 @ 800 from its ice): a margin
  cell or two flickering; a cost, not a physics issue (seen in `eq/fix`).
- PW-460 (sub-cell ramp in the run) stays the honest successor of the band, v2.

