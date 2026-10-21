# PW-514 option B: coast_loss + PW-460/459 + PW-464 judged as one batch (2026-10-21, agent pw514)

Branch `worktree-agent-ae1d70b30254180ac` (from main 64d9dff). Not merged into main. Scratch: session
scratchpad `pw514/` (`seeds.sh`, `table.py`, `earth_tz.sh`, `smoke.py`, `prof.py`, `pan_diag.py`; the
10-seed results are in `pw514/seeds_b1`).

**Outcome: don't merge.** The cost cut works: the whole batch is +4% wall at L6. Everything else fails.
Cold eras freeze on 9 of 10 seeds. The Earth zoom overshoots, and its interglacials keep 15-20% of
land iced. The zoom also loses the run's ice at I = 0 (+41 m). The blocker sits below all three
tickets: with honest margins (PW-460), neither the run's fixed point nor the zoom's endings can
deglaciate a big sheet. The cycle mean (PW-464) doesn't change that, because the interglacial's own
fixed point is the one that freezes.

## What was done
1. Merged `worktree-agent-af748cc6ffa533997` (PW-465 coast_loss) and `worktree-agent-a9f64607e1a64d2e8`
   (PW-460/459). Conflicts were resolved against main. The zoom's `climate_melt` is `climate_step` again,
   with no `melt_f`, since PW-471 removed the boosts. The front reuses the step's `orbit_k`. Drafts that
   were already intaken (PW-461/513/514/515) were left out.
2. PW-464 (`earth.cycle_ice`, `earth.glacial_states`, `icemass.balance(warm=True)`):
   - The run's climate is the cycle's interglacial (the zoom's I = 0).
   - The interglacial's ice is its own fixed point from the old interglacial ice, under the warm half
     of the orbital states. That is per cell and per hemisphere: the states whose summer sun is above
     the mean orbit's.
   - The glacial states are the glacial index's own (timezoom.cycle.Index on the planet's orbit at its
     cycling latitude). Bins are I < 0.2 for the interglacial, then 0.2-0.7 and 0.7-1. Earth-like
     weights: 0.2 / 0.44 / 0.36 at I = 0 / 0.48 / 0.81.
   - Each glacial state is cooled by I x `cycle.cooling` (the snowline-share rule, so it is
     planet-relative), polar-amplified as the zoom does it. Each one starts from the next warmer state.
   - Only the interglacial ice is carried. The world's ice and sea level are the interglacial's. Two
     new fields hold the cycle's mean and glacial maximum: `ice_mean` / `ice_glacial` / `sea_ice_mean`.
     Isostasy uses the mean load. The ice albedo uses the interglacial's area, because the glacials'
     albedo is already inside the index's cooling.
3. Cost (PW-514 item 3):
   - `coast_cost` and the bare-ground start balance are now computed once per fixed point, not every
     pass.
   - A fixed point now counts as settled when the iced cells repeat to within 0.2% (`PASS_TOL`), not
     only exactly. Before, flickering margins drove the merged code to 21 passes per update, against
     3.5 on main. It is now about 4.

## Numbers against the criteria (fresh L6 runs)
| criterion | bar | result |
|---|---|---|
| 10-seed 1 Gyr cold-era check (interglacial ice, as `sea_ice`) | >= 7/10, no absurd drops | **1/10**: worst eras -421..-715 m, 4-26% of the time below -430 m (main 8/10) |
| the same on the cycle mean (`ice_mean`) | | 1/10 (the mean is within ~5-20 m of the interglacial: the frozen interglacial sheets dominate) |
| wall time, seed 11 L6 400 Myr, side by side, 4 threads | <= +15% | **+4%** (main 396 s, batch 412 s; CPU +12%) |
| PW-471 run moments at I = 0 within 25 m | >= 7/10 | not run (the cold-era failure decides the batch). The proxy, `test_ice_at_index_zero_is_the_runs` (L5 cold moment), gives **+40.7 m** against a 25 m bar |
| Earth zoom (L6, 600 kyr), cycles | 98-109 kyr | 98.5-108.5, unchanged (the index) |
| Earth zoom, maxima | -86..-104 m | **-141..-182 m** (at 4.5 C cooling: -90..-124 m) |
| Earth zoom, interglacial ice | 9-12% of land | **16-20%** (at 4.5 C: 15-18%; interglacial seas -30..-67 m) |
| PW-460/459 goals | margins melt, the orbit drives the ice | Margins: the zoom deepens (Laurentide to 38 N, 1.3 Mkm2 south of 50 N), but endings give back little. The L4 test `test_glacials_grow_ice_and_endings_melt_it_fast` keeps 34 of 36 m after 15 kyr. Orbit: in the run, through the warm-half interglacial and the index's weights. Not measured separately |
| `uv run pytest -q` | passes | fails: the 4 tests below, and the goldens changed (not updated, since the batch isn't accepted) |
| scorecard / earth_check | deltas vs main | not run (the batch fails before calibration matters) |

Failing tests on the batch:
- `test_timezoom_consistency::test_ice_at_index_zero_is_the_runs` (+40.7 m);
- `test_timezoom_cycle::test_glacials_grow_ice_and_endings_melt_it_fast` (endings don't melt);
- the goldens (intended changes, not regenerated);
- `test_timezoom::test_glacial_cooling_turns_forest_to_tundra...`, which failed on the merge state and
  passes with PW-464.

PW-515 (`test_frame_rivers_end_in_its_own_hollows`): on the merge state it fails only in the full suite,
not alone. It passes alone, in its own file, and in the a-h tests run in order up to the goldens. So it
depends on the trajectory (probably the numba thread count, or a cache another test leaves set). It
passes on the batch's HEAD. It was **not fixed**: no repro of the failing frame was captured.
`pan_diag.py` and the `merge_code` copy's dump hook in `tests/test_health.py` are ready for that.

## Why it fails (diagnosis)
- In the cold eras the run's *interglacial* fixed point is already -400..-700 m. The glacial states add
  little (5-20 m): the snowline land is iced, so the share, and so the cooling, is small. PW-464's
  "carry only what survives an interglacial" can't help when the interglacial itself holds the sheets.
  What holds them is the run rule's hysteresis: the old ice's height keeps the accumulation zone above
  its snowline. With PW-460's honest margin ramp (~900 m mean at L6 instead of 408 m), the margins no
  longer brake a sheet as the climate warms. The warm-half orbit (PW-459's honest k, 0.08-0.09 C per
  W/m2) is too weak a kick to break that.
- In the zoom the same margins make the endings ineffective. I falls to 0 in 8 kyr, but a big sheet's
  margins (now ramps) barely melt, so interglacials keep 15-20% of land iced. The zoom's sheets don't
  thin dynamically fast enough to drop below the snowline.
- So both halves need a deglaciation mechanism that PW-460 removed: the old 408 m margin was a crude
  stand-in for it. Candidates (needs-decision draft): (a) a sheet-wide balance in the run's fixed point
  (a sheet whose total balance under the interglacial is negative thins, lowering its Nye surface by
  the deficit, before the extent test); (b) B(3): the run's cold eras from a short zoom-like
  integration; (c) keep PW-460's ramp only where it is measured to be right (the zoom's glacial
  maxima) and the edge elsewhere: a kludge, not recommended.

## Keep from this batch (worth cherry-picking on their own)
- The cost cut (coast_cost and the start balance once per fixed point, `PASS_TOL`): +39% -> +4% wall
  for coast_loss. With coast_loss alone (PW-514 option A) this makes it mergeable cost-wise.
- `icemass.balance(warm=True)` and `earth.cycle_ice`: correct machinery. PW-464's framing is unchanged,
  but it is only useful once sheets can deglaciate.
