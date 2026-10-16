# Run lane: tectonics, night of 2026-10-16 (PW-046, PW-284, PW-359, PW-338)

Branch `worktree-agent-a6b53b41002a0ab5c`, from main 430d913 (= the basins lane's after-PW-299 physics; the branch-point health sweep reproduces `health-basins-pw299` exactly). Health sweeps (`tools/health.py --quick --workers 8 --threads 1 --no-determinism`, 8 L6 seeds x 500 Myr): `docs/review/health-tect-base/` (branch point), `health-tect-step1/` (start at target), `health-tect-step2/` (+ hidden crust stacked, belts across the suture: the landed code), `health-tect-pw338/` (+ PW-338's patch, not landed), L7: `health-tect-L7/`. Scripts in `docs/review/audit/tectonics-night/`.

## Summary
| Step | Result |
|---|---|
| PW-046 | **Done (landed).** Three causes, all fixed at the source: the start sat 6% above the thermostat's target (and wound up its integral term), the MAX_KM cap deleted the excess of collision-front spikes, and hidden crust under a continent was deleted. Volume end/start: 8 L6 seeds, 500 Myr 0.867-0.916 -> 0.939-0.988; scorecard 1 Gyr x0.905 / x0.873 -> **x0.977 / x0.981**. |
| PW-284 prerequisite | **Done (landed):** collision belts straddle their suture (stacked crust and crust flow cross the collision boundary). Spikes > 15 km over their neighbours 59 -> 10 (L6 seed 1, 400 Myr). |
| PW-284 sound flexure | **Stopped, not landed.** On cells as wide as the flexural parameter (alpha 66 km for Te 30 km; L6 cells 120 km, L7 60 km) every one-cell load is held up by most of its root, not only collision spikes: sediment-filled moats rise in turn (checkerboard instability, 27 km peaks). Height-driven crust flow didn't stop it. Needs a decision (ticket). The 0.15 share is now documented as calibrated. |
| PW-359 | **Confirmed an artifact, stopped:** `resolve` re-cuts ~75k km3 of lake-kept hollow per L6 step on rigid plate interiors. A one-to-one sampling map was tried: it reduces lost write-backs by 2/3 but not the hollows. Sound fix (interpolating view) is a design change: ticket. |
| PW-338 | **Fix ready, not landed:** a vent's floor follows the ground around it (vents > 1 km below their ground 17.5% -> 0%). It reshuffles the L5 seed-1 envelope world into an icehouse and turns `test_climate[1]` red (arid 7.7%): draft. Patch kept. |

## PW-046: where continental volume went
Budget per process (`budget.py`, `Simulation.book`, km x level-5 cells; it closes exactly), L6 seed 2, 1 Gyr. Start volume 151,943 against a target of 143,367 (40% x 35 km): **the start was 6.0% above target** (setup turned its relief into ~37.1 km of crust).

| | branch point | landed |
|---|---|---|
| start / target | 1.060 | 1.000 |
| volume end/start (1 Gyr) | 0.873 | 0.981 |
| volume end / target | 0.925 | 0.981 |
| mean continental crust at 1 Gyr, km | 31.6 | 34.2 |
| thermostat integral (volume) at 300 / 600 / 1000 Myr | -0.090 / -0.033 / +0.27 (windup: negative until ~750 Myr) | +0.045 / ... / +0.267 |
| arcs, km-cells per Gyr | +22,489 | +41,109 |
| subduction erosion | -33,742 | -42,565 |
| erosion (sediment carried off the continents) | -30,245 | -26,668 |
| flow + MAX_KM cap | **-7,642** | -1,425 |
| resolve + collision (sampling) | -6,108 | -8,281 |

1. **The start.** The run spent ~250 Myr shedding the 6% excess, and the thermostat's integral term (THERMO_MYR 100) integrated that "too much" error the whole time, so once volume was at target the integral still held arcs back (factor ~0.7) until ~750 Myr: the volume undershot to 7.5% below target. Now `setup` shifts the continents' thickness uniformly so their mean is `continental_thickness` (relief pattern kept; the start's land 39.6 -> 37.4%).
2. **The MAX_KM cap.** Collision stacking (`stack_collisions`) and crust flow ran on edges inside one plate's continent. Crust stacked at the front could only spread back into its own plate, and a front cell with few continental neighbours of its own plate piled up to 80 km; the cap deleted the excess, 5% of the volume per Gyr in seed 2's collisions. `crust.inner_edges(sim, cont, bd)` now adds the collision edges: a belt straddles its suture (the Himalaya and Tibet do).
3. **Hidden crust.** `cleanup_ghosts` deleted plate cells hidden deep under another plate. For continental crust under a continent that is crust nobody "pulled" in `resolve`; it is now stacked like the pulled cells. Measured: 0.16% of the volume per 300 Myr (L6 seed 2), small but a leak.

What remains (~2-4% below target after 500-1000 Myr) is the PI thermostat's lag against two real sinks: subduction erosion (steered by the area thermostat) and sediment carried onto ocean floor. The resolve+collision gap is not a leak: nearest-cell sampling gives ~15% of world cells a duplicated plate cell, each gets the step's physics, and only one write survives, so every process's booked change is damped about equally (PW-359). No thermostat was strengthened.

## PW-284: spikes and flexure
Spikes (`spikes.py`: continental cells > 15 km thicker than the mean of their continental neighbours), L6 seed 1, samples every 20 Myr to 400 Myr:

| | branch point | belts across the suture | + sound flexure (not landed) |
|---|---|---|---|
| spikes > 15 km, all samples | 59 (44 on a plate boundary, 41 converging, at ~78 km) | 10 (2 on a boundary) | 792 |
| largest excess, km | 33.7 | 17.9 | 55.7 |
| highest elevation, any sample, km | 7.3 | 8.1 | 28.6 |

The sound flexure tried: `dyn += root - smooth(root, alpha)` (sum exactly zero, no cap), alpha = (D / (drho g))^1/4 from Te 30 km, E 70 GPa, nu 0.25, a sediment fill (66 km; 49-82 km for Te 20-40), replacing the 0.15 moat share. The worst cells at 140 Myr (`inspect_spike.py`): an 80 km cell with 18 km of cover at +25 km, its neighbours at -1 to -8 km with 21-46 km of crust. The load is held up because it is narrower than the plate's response, which is right for one 120 km column; but on this grid every one-cell load is such a column. A moat beside a lifted cell fills with sediment up to the burial cap, becomes a one-cell load itself and is lifted in turn. Driving crust flow by the flexed height (gravitational collapse; stable with the per-substep cap / (1 + ROOT / ISO_LAND), flexure recomputed every substep) did not stop it at the rate law's speed (26 km by 180 Myr). Patch: `flexure-attempt.patch`. Options and lean on the ticket.

## PW-359: resampling and closed hollows
`resample.py`, L6 seed 1, 0-300 Myr, per step after 50 Myr, rigid interiors = land cells at least 3 cells from any plate boundary before and after the move (~13,000 cells):

| | value |
|---|---|
| rms elevation change of interior land under `resolve` | 117 m (mostly real: the relief moves under the world cells) |
| world cells on a duplicated plate cell / plate cells hidden | 14.8% / 7.4% |
| interior pits per step, before / after resolve | 744 / 775 |
| closed hollow volume on interiors, raw (every pit) | -9k km3 per step (unchanged) |
| closed hollow volume on interiors, lake-kept (`hydrology._bed`: 20 m, slope filter) | **+75k km3 per step** |
| all land, lake-kept, the basins lane's `hollow_budget.py` on this code | resolve +66.6k, erosion -81.7k per step |
| change lost at write-back (`writeback.py`: last write wins) | 4.3% of the step's gross land change, 7.5% of land cells |

A rigid plate shouldn't change its hollows. The raw hollow volume is unchanged, but its shape isn't: each step a world cell sees a different arrangement of plate cells, so a flat floor filled to 5 m below its spill (PW-299) comes back as hollows of 20 m and more. Tried: a one-to-one nearest map (`pw359-unique-samples.patch`: a world cell that would duplicate a plate cell takes that plate cell's hidden neighbour). Duplicates 14.8 -> 10.6%, lost write-back 82 -> 28 km-cells per step (4.3 -> 2.7%), but lake-kept hollows on interiors +90k per step. The write-back loss isn't the mechanism, so it's not landed. A sound fix is an interpolating view of the elevation-carrying columns (thickness, cover) with the step's changes interpolated back. That is a design change (records and crust type stay nearest): on the ticket.

## PW-338: vents' floors
`vents.py`, L6 seed 13, 0-300 Myr, hotspot vents every 20 Myr (ground = lowest of the vent's cell and neighbours):

| | before | after (patch) |
|---|---|---|
| vents whose floor is > 1 km below their ground | 17.5% (at sea 20.1%) | 0% |
| floor - ground, median | -351 m | 0 |
| vents on land whose top is below their cell's mean | 81% | 76% (cones worn down to the lowest ground around them) |

Not landed: see the draft `draft-envelope-l5-icehouse-dry.md`.

## Health, L6 (8 seeds x 500 Myr, frames after 50 Myr; per-seed medians, then the mean)
| metric | branch point | step 1: start at target | step 2: + hidden crust, belts across the suture (landed) | + PW-338 (not landed) |
|---|---|---|---|---|
| crust volume end/start, mean (range) | 0.895 (0.867-0.916) | 0.960 (0.937-0.973) | **0.963 (0.939-0.988)** | 0.969 (0.942-0.993) |
| land % | 33.5 | 33.2 | 33.5 | 32.7 |
| continental crust % | 39.7 | 40.1 | 39.9 | 39.7 |
| mean continental crust, km | 34.9 | 33.7 | 34.0 | 34.4 |
| highest peak, mean of seeds' maxima (max), km | 8.53 (8.73) | 8.48 (8.89) | **8.03 (8.80)** | 8.13 (8.63) |
| keyframes with a peak > 9.5 km | 0 | 0 | 0 | 0 |
| inland drainage % | 4.20 | 4.06 | 4.31 | 4.88 |
| lakes % of land | 0.43 | 0.50 | 0.43 | 0.50 |
| giant-lake frames %, mean per run | 6.2 | 10.6 | 8.9 | 9.2 |
| sea level m | +5 | -50 | +2 | +32 |
| ocean age Myr | 52.8 | 57.4 | 53.5 | 50.6 |
| plates | 11.9 | 10.5 | 11.2 | 11.8 |
| icehouse spells (ice SL < -50 m), all seeds | 6 | 4 | 3 | 2 |

## Scorecard (L6 seeds 1 / 2, 1 Gyr; `--jobs 3 --threads 2`; Earth climate skipped: no `data/` in the worktree, climate untouched)
| | branch point (basins lane's after) | landed |
|---|---|---|
| crust volume end/start | x0.905 / x0.873 | **x0.977 / x0.981** |
| land at 1 Gyr | 31.1 / 31.3% | 35.6 / 32.7% (seed 1's range 32.4-35.6: it ends assembled) |
| crust | 41.2 / 40.9% | 42.7 / 40.1% |
| dry (final) | 26.9 / 19.9% | 25.6 / 27.9% |
| ice (final) | 0.3 / 2.5% | 0.3 / 0.4% |
| ocean age | 50.7 / 95.1 Myr | 77.0 / 74.9 Myr |

## L7 (seed 3199, 500 Myr)
`health.py --l6 --l7 3199 --myr 500` (`health-tect-L7/`) against the basins lane's after (`health-basins-L7-after/`, the same physics as this branch point). Frames after 50 Myr, medians:

| | branch point | landed |
|---|---|---|
| crust volume end/start | 0.900 | **0.997** |
| highest peak, any frame, km | 8.85 | 9.00 (0 frames above 9.5) |
| land / crust % | 34.6 / 38.1 | 35.0 / 38.3 |
| mean continental crust, km | 36.4 | 36.1 |
| inland drainage % | 5.87 | 7.84 |
| lakes % of land | 0.53 | 0.67 |
| giant-lake frames % | 10.6 | 10.6 |
| sea level m | +53 | -92 |
| ocean age Myr | 52.9 | 62.4 |
| plates | 13 | 10 |

One seed: the sea, ocean age and plate count differ by trajectory (an assembly at a different time), not by a process these changes touch.

## What got worse, honestly
- Giant-lake frames: 6.2 -> 8.9% per run (seed noise is about +-2.5 points; the basins lane's variants spread 6.1-10.8). Plausibly real in part: more crust stays on the continents, so more broad flat interiors.
- Mean continental crust over 500 Myr is 34.0 km against 34.9: the start is now 35 km instead of 37, and the run still settles ~1 km below target. At 1 Gyr it is thicker than before (seed 2: 34.2 vs 31.6 km).
- Seed 1's land at 1 Gyr: 35.6% (it ends assembled; its 1 Gyr track runs 32.4-35.6%).
- The start's land falls 39.6 -> 37.4% (the starting continents stand ~330 m lower).

## Tests and goldens
- `tests/test_crust_belts.py`: stacked crust at a collision front reaches the other plate and its excess over its neighbours drops below 0.8x the one-plate case (volume kept); the start's mean continental thickness is `continental_thickness` (3 seeds, incl. `continental_start` and another target).
- Goldens regenerated: `tests/golden/sim_L4_s1_60myr.json` (the start and the collisions changed every run).
