# v1-finish-5: PW-741, the rest of L7's extra icehouse (2026-10-24)

Branch `worktree-agent-add5294651351a842`, from main 51ee51f. Scripts here; raw outputs in the session scratchpad
`v1f5/` (`eq/`, `eqice/`: eqcurve.py's equilibria; `l6rec/`: the four showcase seeds at L6 on main, recorded;
`l6fix/`, `l6c_*/`, `l7fix_d1/`, `l7fix_d2/`: runs with the fix). CPU: at most ~24 threads.

## Not the ice rule: the climate and ice at fixed forcing agree across levels

v1-finish-3's `eqcurve.py` (same planet as L7, L7 with L6's averaged relief "L7s", and L6; climate + ice sheets
at a fixed dT, carbon cycle out), 4-5 updates (sea_ice m / iced land, last update):

| moment | dT | L7 | L7s | L6 |
|---|---|---|---|---|
| 656f66 @500, from no ice | -1 | -116 / 15.6% | -105 / 13.6% | -122 / 15.0% |
| | +0.5 | -37 / 7.2% | -39 / 7.2% | -53 / 8.1% |
| | +2 | -23 / 4.2% | -24 / 4.8% | -3 / 1.1% |
| | +3.5 | -3 / 1.1% | -3 / 1.1% | -3 / 1.0% |
| 27929a @600, from no ice | -1 | -57 / 11.2% | -54 / 10.9% | -45 / 9.1% |
| | +0.5 | -38 / 8.8% | -37 / 8.5% | -37 / 7.7% |
| | +2 | -20 / 5.4% | -25 / 6.4% | -22 / 5.1% |
| | +3.5 | -12 / 3.4% | -19 / 5.1% | -19 / 4.2% |
| 656f66 @600, from its ice (-404 m) | +1 | -341 / 24.5% | -341 / 24.5% | -360 / 25.1% |
| | +2.5 | -311 / 22.5% | -309 / 22.5% | -339 / 23.6% |
| | +4 | -122 / 12.3% | -77 / 8.8% | -144 / 13.2% |
| 27929a @800, from its ice (-178 m) | +1 | -123 / 11.2% | -165 / 13.5% | -170 / 13.7% |
| | +2.5 | -60 / 7.5% | -82 / 8.8% | -156 / 12.4% |
| | +4 | -17 / 3.5% | -16 / 3.5% | -42 / 5.8% |

No sign: from no ice L7 grows as much as L6 within ~25% either way (one threshold case each way), and from ice
L7 sheds it as fast or faster (less hysteresis, if anything). L7 vs L7s (the finer relief) is as often less ice as
more. The band (PW-725) and the relief are not what keeps L7 icier: at the same dT the same planet ices the same.

## The cause: the CO2 source counted the crust thermostat's gain

`earth.global_temperature`'s volcanic source is ridge production plus 20 x the arcs' crust growth
(`crust.arc_growth`), ~95% arcs. That growth includes the volume thermostat's gain on continental arcs
(`crust.thermostats`, up to x5), the controller that holds the continents' volume on target. Its trajectory depends on
the level (`track_prefix.py` recordings; v1-finish-3's tracks for L7), mean per 100 Myr:

| | gain at 300 Myr | gain at 900-1000 | area thermostat (subduction erosion x) at 900-1000 |
|---|---|---|---|
| L6, 8 seeds | ~1.4-1.6 | **2.2-3.5** | 1.5-3.7 (area over target) |
| L7, 4 seeds x 2 draws | ~1.2-1.5 | **0.9-2.8, mostly 1.1-1.7** (peaks ~500 Myr, falls back) | 0.4-1.2 (under target) |

So after the references freeze (REF_FREEZE 300 Myr) L6's source rises ~20% above its reference and L7's doesn't:
the counted source over 300-1000 Myr averaged **1.17x the reference at L6** (8 runs: v1-finish-3 base + `l6rec`)
against **~1.01x at L7** (8 runs). At the CO2 stock's steady state (X^0.4 = s/w, with the weathering's temperature
factor) that is ~1 C: the CO2 term over 300-1000 was +2.5 C at L6 against +1.6 C at L7, and L6's dT ~0.6-1.3 C
warmer, about the 15-25 icehouse points of the ticket. The drift is identical across levels (its own random stream),
the albedo term follows the ice.

The gain is bookkeeping, not a magma flux: it stands in for an uncertain growth-versus-loss balance and climbs when
the crust budget leaks, and the leak depends on the cell size (L6 loses more to subduction erosion because its area
runs over target; L7 more to erosion; inbox `draft-crust-thermostats-level-dependent.md`). What outgasses is the
slab's melt, the arcs at their nominal rate (trench convergence x heat), which is level-consistent (the spread belt
and the trench length both scale with the cells).

## The fix (decision delegated, evidence clear)

`crust.arc_growth` returns (growth, nominal): the same arcs at the nominal rate (gain 1), from the same search
(`spread(..., also=)`); `Simulation._physics` passes the nominal one to `global_temperature`. The crust is built as
before (the gain still thickens continental arcs); only the CO2 source no longer sees it. No per-level factor.
Test: `test_arc_outgassing_is_the_slabs_melt_not_the_volume_thermostats_gain` (tests/test_crust_belts.py). The code
reproduces `track_prefix.py FIX=1` bit for bit (200 Myr at L6, 0 mismatches).

## Pass rates with the fix (owner's bar, 300-1000 Myr; passrate_L6_fix.txt, passrate_L7_fix.txt)

| | before (main) | with the fix |
|---|---|---|
| L6, showcase seeds, offset 0 | 3/4, 0 / 23 / 32 / 48% | 2/4, 11 / 10 / 82 / 45% |
| L6, all draws | 32 draws (v1-finish-2): median 33%; v1-finish-3's 4 seeds: 2/4 | **5/18 (28%), median 46%** (8 seeds, 1-3 draws each: offsets 0, +-0.001), 2 always-icebox |
| L7, showcase seeds | 12 draws: 6/12, median ~41% (showcase runs 64/42/22/60%) | **3/8 (38%), median 45%** (2 draws: 27/65/47/75%, 35/77/38/43%) |

The level effect is gone: L6 and L7 now both sit at a ~45% median. It went by L6 getting colder, not L7 warmer:
L6's ~33% was the leaking crust's CO2. Pooled over every run here, the ice response to dT is the same shape at both
levels (`icecurve.py`: icehouse ~85% of the time at dT -1..0, ~50-60% at 0..2, ~15% at 3..4).

**Remaining**: both levels are now under the ~70% bar (28-38%), the model's mean climate, not resolution: inbox
`draft-icehouse-share-both-levels-after-pw741.md` (needs-decision, v1: accept, PW-368's narrower drift, PW-564's
brightening star, or a different CO2 reference).

## Goldens, scorecard, Earth

Run physics changed at every level (the CO2 source), so the goldens were updated on purpose (`--update-golden`);
see the commit. earth_check: unaffected (the Earth climate never sees the run's CO2). Scorecard: see the line added
to docs/scorecard.jsonl.

## The showcase: not remade yet (deliberately)

The showcase's L7 statistics are unchanged within the draws (45% median against ~41%), and the next step is the
needs-decision draft's calibration, which would change every history again. Remaking the four L7 showcase runs now
(~10 CPU-hours) would make them twice; the coordinator should remake after the decision (`planet make --level 7 --seed
S` for 957317 619496 583167 639472). The current showcase (runs 656f66 fdb41e 9882e7 27929a; worlds bacb95 c6c24f
f2a9a4 61ac61) stays until then.
