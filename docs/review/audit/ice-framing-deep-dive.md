# PW-462 deep dive: the run's ice as a cycle average, the time zoom as a window (2026-10-20, agent pw462)

Read-only. No physics was changed. Measurements ran in memory (scratchpad `pw462/`: `tzmean.py`,
`states.py`, `earth_states.py`). Nothing was written to the real store.

## 1. Verdict

**The framing is right for the time zoom and half-right for the run. It does not fix PW-461 on its own.**

- **The zoom as a window (part 2) is sound and cheap.** All 7 stored zooms and both zooms measured here start
  at an *edge* of their own range, not in the middle. The run's state is the zoom's interglacial maximum on
  moderately cold moments and its glacial maximum on deep ones. The zoom's time-mean misses the run's ice by
  -68 to +137 m. So the right acceptance metric is the window's mean, not the start's drift. The 25 m
  unforced test checks something else: whether the mass-balance rule is shared.
- **"The run's ice should be the cycle average" (part 1) is correct, but the premise behind it is wrong for
  main.** Main's run is *not* icier than the average. Averaging the balance over the 8 orbital states before
  finding one equilibrium keeps ice only where it survives the warm states too. So on moderately cold moments
  main's run holds about the **interglacial** extent:

  | L5 seed 1 @ 300 Myr, -4 C | sea level (m) |
  |---|---|
  | run rule | -19 |
  | mean of the 8 states' own equilibria | -83 |
  | forced zoom's time mean | -87 |

  Making the run a true cycle mean would make these moments **icier**, not less icy. On deep moments the
  opposite is true: L6 seed 11 @ 400 on main gives -252 m, and its zoom averages +94 m above that. There the
  orbit's 8 states all agree with the run within 13 m. About 40 m of the gap remains with *all* forcing
  off, so it is the run/zoom ice budget, not the averaging.
- **The PW-461 freeze is not a cycle-averaging problem.** On the PW-460/459 branch code, the same moment
  gives -362 m (10.4% of the planet iced). All 8 states' equilibria lie within -340..-371 m, both from the
  run's ice and from no ice. So neither averaging nor hysteresis is the cause. The zoom then sheds +101 m of
  that ice and settles there, with no cycles. The freeze is a gap between the run's and the zoom's ice
  budgets: the run has no calving or shelf losses on its coastal accumulation zones (PW-461 B(2)). Under the
  framing it becomes "the zoom's mean is 100 m above the run's", but the fix is the marine budget, not the
  averaging.
- **With honest orbital sensitivity, the orbit alone has almost nothing to average.** That is PW-459's
  0.08 C per W/m2. On the branch, the 8 states differ by only 31 m (main: 209 m). Real glacial cycles are
  the feedbacks (CO2, ice albedo, isostasy and calving at the endings), paced by the orbit. So "the run's
  ice = the cycle mean" needs the cycle's *global* swing in its states, not only the orbit's (section 4,
  item R2). That couples the run's rule to the zoom's feedback rules, which is acceptable: they are already
  shared (`icemass`).
- **Era starts and ends (part 3) are feasible but marginal.** The run's dT relaxes over 5 Myr, so a 1 Myr
  window sees an onset only where it straddles the threshold. It is the lowest priority.

So the framing **moves** the problem rather than dissolving it. The run needs (1) the zoom's marine
budget, then (2) a state-mean rule that includes the feedback swing. The zoom needs (3) a spin-up so that
it is a window. Only after these can PW-460/459 merge and the cycle work (PW-030/447) be judged on
consistent starts. None of this is a dead end, but none of it clears the ice-age problem by the
2026-10-21 time box. The realistic morning deliverable is the measurement tool and test (R1).

## 2. Measurements

### Stored time zooms (real store, read-only: frames' `sea_level_change_m`, change since the start = the run's ice)
| zoom | source | kyr | after 20 kyr | mean | mean after 100 kyr | min | max | ice at start (% of surface) |
|---|---|---|---|---|---|---|---|---|
| 080df3 | a1d3b9 (L7 seed 3199) | 1000 | -94 | -79 | -80 | -129 | 0 | 5.4 |
| 98ee98 | 2c2810 | 1000 | -91 | -111 | -112 | -143 | 0 | 8.5 |
| 7d5027 | 82fc14 (s400: seed 11 @ 400) | 600 | -7 | -89 | -95 | -147 | 0 | 3.3 |
| be3362 | 27ea70 (seed 2 @ 620) | 600 | +81 | +137 | +142 | 0 | +185 | 8.0 |
| 86c513 | a1d3b9 (warm moment) | 1000 | 0 | 0 | 0 | -7 | +9 | 0.7 |
| 755514 / 098d5d | Earth (real ice) | 600 | -10 / -11 | -12 / -14 | -13 / -15 | -43 / -45 | +5 | 2.8 |

Every icy run moment starts at its zoom's maximum or minimum sea level. PW-436 adds seed 2 @ 580: never
below its start, up to +141 m.

### The run's rule against per-state equilibria and the zoom (in memory)
`states.py`: the run's rule (`earth.ice_sheets`, 6 climate updates as in the consistency fixture). Then each
of `cycle_dq`'s 8 orbital states alone, as `ice_sheets` with a one-state cycle: from the run's ice
("hysteresis") and from none ("fresh"). Then a default forced zoom from the run's ice.

| moment | code | run rule (m) | 8 states, from the run's ice | from no ice | mean of states | zoom mean (total) | zoom range from the start | endings |
|---|---|---|---|---|---|---|---|---|
| L5 s1 @ 300, -4 C | main | **-19** | -21 .. -230 | -20 .. -230 | **-83** / -84 | **-87** (start -19, mean -68) | -126 .. 0 | 3 (61, 47, 47 kyr) |
| same | branch 246ef40 (PW-460+459) | **-362** | -360 .. -371 | -340 .. -360 | -364 / -352 | **-260** (mean +101) | 0 .. +115 | 0 |
| L6 s11 @ 400 (in memory, dT as the run) | main | **-252** (8.1%) | -254 .. -265 | -207 .. -258 | **-259** / -236 | **-158** (mean +94, 400 kyr) | -3 .. +146 | 4 (11, 38, 13, 17 kyr) |
| Earth L6, dT 0 (rule from the real ice) | main | **-58.8** (N -10.3, S -48.4) | -58 .. -99 (N -9 .. -50) | -13 .. -99 | **-67.8** / -52.6 | (zoom 755514 from the *real* ice: -12 m mean) | -43 .. +5 | 1-2 |

Costs:
- L5: the run rule's `ice_sheets` takes < 0.1-0.3 s (2-26 passes), against ~0.7 s for the climate. A
  300 kyr zoom takes 17-20 s.
- L6, deep moment: the first updates hit the 201-pass cap at ~6 s each, then settle to 8-16 passes
  (0.3-0.5 s), against 1.3 s for the climate.
- A per-state pass makes one `climate_step` call instead of 8. So 8 per-state fixed points cost about what
  today's averaged one does, as long as their pass counts are similar.
- The zoom's orbit distribution matches `cycle_dq`'s: obliquity rms 0.85°, eccentricity rms 0.030. PW-436's
  first suspect, a wider orbit in the zoom, is ruled out.

Reading:
- On main, the time-mean of the orbital states' own equilibria matches the zoom's time mean within 4 m on
  this moment. The run's rule is 64 m less icy than both. The NH's state extremes are -16 m (warm) and
  -230 m (cold); the zoom swings 126 m.
- On Earth the run's rule (-58.8 m) is close to today's real ice (~-65 m), as it should be for an
  interglacial. But the mean of the orbital states is only -67.8 m, against a Pleistocene mean of ~-115 m
  in the same terms. The orbit-only states give the NH just -9..-50 m. The missing ~45 m is the cycle's
  global swing (the LGM's ~-2.5 C of CO2 and the albedo), which the states don't carry: PW-033/435's depth
  problem appears here too. "From no ice" drops Antarctica in one state (-13 m), so the persistent ice's
  hysteresis is real and must be kept.
- On the deep L6 moment (seed 11 @ 400 Myr built in memory with `run_sim`, -252 m and 8.1% iced, deeper
  than the stored s400 moment), the 8 states lie within -254..-265 m and their mean is -259. That is the
  run's rule within 7 m: on deep moments the orbit alone changes nothing. Yet the forced zoom loses ice at
  once (+55 m at 20 kyr) and cycles *above* the start: 4 endings, a time mean of +94 m, the start at its
  minimum. That is PW-436 on main. Its cause is the budget or the feedbacks' reference, not averaging
  (decomposition below).
- **Decomposition of that +94 m** (same moment, 200 kyr; the full run's first 200 kyr average ~+87 m):

  | variant | time mean |
  |---|---|
  | unforced: no orbit, CO2, albedo or cycle; vegetation local | **+38 m**, a plateau at +41 from 40 kyr (fails the 25 m bar on this deep moment, which the L5 fixture passes) |
  | orbit on, feedbacks and cycle off | +59 m |
  | everything on | ~+87 m |

  So roughly 40 m is the run/zoom *rule* gap (budget: R2), 20 m is the orbit (the zoom's real cycling
  loses more than the 8-state equilibrium; the averaging question, but on the opposite side from the L5
  moment), and 30 m is the feedbacks' reference with the cycle (`average_room`, the start as the
  interglacial: Z-c, Z-d).
- On the branch, the orbit barely matters and the zoom loses 100 m at once. The cause is a budget
  mismatch: calving and shelf melt of coastal ice, per PW-461's flows (calving 12,400 km3/yr against
  +11,100 of surface balance).

## 3. Findings by component

Effort codes are the board's (xs < 30 min, s < 2 h, m ~half a day, l a day or more).

| # | piece | assumes now | under the framing | effort | unblocks |
|---|---|---|---|---|---|
| R-a | `icemass.balance(tilt=)`, `cycle_dq` | the cycle mean is one equilibrium under the balance averaged over 8 orbital states (obliquity ±0.85°, e 0.03, 4 perihelia) | per-state balances already exist (the loop). Add per-hemisphere warm/cold picks and a global offset per state (the cycle's CO2/albedo swing). The averaged call stays for the regional zoom's glaciers | s | R2 |
| R-b | `earth.ice_sheets` / `_ice_pass` | one fixed point, seeded from the old ice (hysteresis carried 4 Myr); margins at `EDGE_H` | one fixed point per state seeded from the persistent ice; persistent = warmest state, carried; stored = time mean, plus `ice_ig` and `ice_glacial` | l | PW-460/459 merge, phase picker, zoom footprint |
| R-c | `ablation_zone` calving | only the added ablation ring pays calving; no shelves, no deep-water loss | coastal accumulation zones pay the zoom's calving and shelf losses | m | PW-461 (the branch's +101 m), PW-436 |
| R-d | `update_climate`: `sea_ice`, `global_temperature` albedo `(ice > 0).mean()`, `ice_sink` | one ice field is the state | sea level from the mean volume (unchanged). Albedo from the time-mean area, since the union of iced cells would overstate it. Isostasy from the mean load (fine at 4 Myr) | s | (part of R-b) |
| R-e | CO2 / weathering (`sim.weathered` masked by ice; WEATHER_K; f(CO2)) | land under the step's ice doesn't weather | weight the mask by each cell's iced share of time (cycling land weathers in interglacials). Small; it gives the cold eras a little more drawdown | xs | PW-452 bookkeeping |
| R-f | the climate's ice inputs (`climate.compute` ice, `air_mass`, Köppen) | the step's ice is a snapshot | the mean field: thin mean ice over cycling land. Use `ice_ig` + mean for the climate, or the mean only (decide in R2) | s | - |
| R-g | keyframes / worlds sliced from the run (`finish`, `world`) | a world is the run's moment | a run world is the cycle-mean state at the mean orbit. Label it as such. A frame of a zoom is a real phase (`finish.orbit_dt` unchanged) | xs | - |
| R-h | `tools/health.py` (`sea_ice_m` ≥ -250, `below_150` ≤ 10%), pw449 bar (worst ≥ -450, ≤ 2% below -430), ~70% seeds | the run's ice, whatever it is | keep the numbers as cycle means and print the glacial bound as information (section 6) | xs | - |
| Z-a | `_Sim.__init__` start-up | the run's ice is the state at t = 0, settled, `sl` = 0 | spin-up S kyr before the window, discarded; the window starts at the orbit's phase | m | everything Z-* |
| Z-b | `orbit_phases(seed*1000 + round(at))`, `orbit_at` from the window start | the phase is fixed per moment | fine for "auto". For a requested phase, start the window at the time in the spun-up series that matches (the orbit is analytical) | s | phase picker |
| Z-c | `Forcing`: CO2 excess = -sl/120 from the start, `average_room` 0.5; albedo from `ice_frac0` | the start is the cycle mean (for `start=average`) | references from the run's mean (or the spin-up's), not from the window's start | s | consistent window means |
| Z-d | `cycle.Cycle`: `sl_ig` = the start; `ig_ice` = the start's ice; the boosts never act inside it | the start is the interglacial | `sl_ig` / `ig_ice` from the run's persistent ice, or learned in the spin-up. Today a mean-ice start would shield its own glacial ice from every ending (part of PW-447's stalls) | s | PW-447 re-measure |
| Z-e | `fields.ClimateFields`, `dT_run` constant | the run's dT is constant over the window | a dT trend from the neighbouring keyframes, for era starts and ends only | m | era start/end |
| Z-f | `events`, `output` meta | turning points and the cycling latitude | add the phase at the window's start and the window mean against the run's | xs | viewer summary |
| Z-g | `finish.orbit_dt` | the frame's orbit against the reference orbit, plus the anchor | unchanged: a zoom frame is a real phase | - | - |
| Z-h | `tests/test_timezoom_consistency.py` (unforced 20 kyr, 25 m) | the run's ice is an equilibrium of the zoom's balance at the mean orbit | still a valid check of the shared rule, but not of the framing. Under R2 the run's ice is no single equilibrium, so it becomes "held at the warmest / coldest state, from the run's equilibrium for that state, < 25 m in 20 kyr". The framing gets its own test (section 5) | s | R1 |
| Z-i | `tests/test_timezoom_cycle.py` | the cycle's state machine on made-up sea levels plus the L4 icehouse | unchanged (the machine is phase-agnostic). Add one case starting mid-glacial (`sl_ig` above the start) once Z-d lands | xs | - |
| Z-j | API / viewer (`parse_timezoom_request` {run, t, kyr}, `find_timezoom`, the viewer's button) | one zoom per moment and length | `phase` in the request, the available phases listed, `find_timezoom` keyed on it | m | the owner's UI idea |

## 4. Recommended order of work

Ranked by what can realistically clear the ice-age problem:

| rank | work (draft) | effort | why here |
|---|---|---|---|
| R1 | **Measure first**: `tools/tz_mean.py` plus a strict-xfail slow test, "zoom mean ≈ run" (`draft-tz-mean-matches-run-check.md`) | s | gives every later step a number. It fits in the 2026-10-21 morning |
| R2 | **Run marine budget** (`draft-run-ice-marine-budget.md`) | m | the PW-460/459 branch's 100 m gap is this. Measurable on main and branch with R1 |
| R3 | **Run ice = mean of cycle states**, persistent ice carried (`draft-run-ice-cycle-mean.md`) | l | fixes main's interglacial-edge bias, gives the zoom its footprint and the picker its phases, and lets PW-460/459 merge on top |
| R4 | **Re-apply PW-460 + PW-459** (branch 246ef40) on R2 + R3. Then the 10-seed check and tz_mean | m | the zoom side already meets the Earth targets (margin only + obs) |
| R5 | **Zoom window spin-up**, references and footprint from the run (`draft-tz-window-spinup.md`) | m | only now does the zoom's mean become meaningful; re-measure PW-447 endings on it |
| R6 | **Phase picker** API and viewer (`draft-tz-phase-picker.md`) | m | the owner's UI; needs R3's `ice_ig` / `ice_glacial` and R5 |
| R7 | **Bars as cycle means** (`draft-cold-era-bars-as-cycle-mean.md`) | xs | with R3 |
| R8 | **Era start / end** (`draft-tz-era-start-end.md`) | m | lowest; a 1 Myr window rarely straddles the threshold |

R1 + R2 + R3 + R4 is the core: about 3-4 agent-days in the serial run lane, plus the 10-seed checks.
**Stop rule for R3:** if the mean of per-state equilibria misses the zoom's mean by > 25% of the swing on 2
or more of the L6 moments, the equilibrium-per-state assumption fails (sheets don't reach their equilibrium
in a precession half-cycle). Then go to PW-461 B(3): a short reduced integration inside the run. The cost is
real: L5 300 kyr is ~20 s of zoom, and L6 is several times that per cold step.

## 5. Existing ice-age tickets

| ticket | now | verdict |
|---|---|---|
| PW-461 (deglaciate the run; options A/B/C) | needs-decision | **Decide B, reshaped**: B(2) marine budget first (R2), then B(1) with the cycle's global swing (R3). B(3) is the fallback. Not A: the extent alone doesn't change, and it makes the interglacials icier. Fold its remaining work into R2/R3 |
| PW-460 (sub-cell margin) | todo | **Keep**, blocked by R2 + R3. The ramp is right physics. Note it is strongly resolution-dependent (L5 cells ~220 km: margin mean ~1.3 km against `EDGE_H` 408 m), so the L5 fixture amplifies it |
| PW-459 (seasonal k) | todo | **Keep**, merge with PW-460 in R4. Under the framing it removes most of the orbit-only spread, which is why R3 needs the feedback swing |
| PW-436 (forced zoom from a cold moment loses ice) | todo | **Fold into R1/R5**: it is "the run sits at an edge". Its suspect list (wider orbit in the zoom, `average_room`) is part of Z-c |
| PW-366 | done | stays done. Its unforced test becomes the rule check (Z-h) |
| PW-030 (100-kyr sawtooth) | todo | **Keep**, re-measure after R5 on spun-up windows. Its "never terminates" was measured from edge starts |
| PW-447 (endings slow and stall) | needs-decision | **Keep, decide A** (the ticket's lean): fix the start first. Z-d shows the boosts can't touch the start's ice, part of what stalls |
| PW-440 | done | stays done. Its cycle survives the framing unchanged; only its footprint init changes (Z-d) |
| PW-033 / PW-435 (Earth depth, Laurentide) | todo | **Keep**. Earth's zoom starts from real ice (`start=interglacial`, a true phase), so the framing doesn't change them. R4 delivers their lever |
| PW-422 (film-shielded margins) | todo | **Keep**. Unrelated to the framing (zoom-internal) |
| PW-438 | done | stays done |
| PW-452 (cold-era ice 15-17% at dT -4) | todo | **Keep, re-measure after R3**. As cycle means the run's cold eras may get icier (main) or less icy (branch plus marine budget) |
| PW-104 (embedded ice-age episodes in the run) | todo | **Keep**. R3's states are a cheap first step toward it, and B(3) would be the same machinery |
| PW-429 (hint moderately cold moments) | todo | **Fold into the phase picker** (R6): "on/off" and the available phases are that hint |
| PW-241 / PW-295 / PW-418 (start drift) | blocked | **Close as superseded by R1/R5** once R5 lands: the start drift is no longer the metric. Leave them until then |

## 6. Acceptance tests

**"Run ice = cycle average"** (run side, R3):
1. Self-consistency of the rule: the stored mean equals the time-weighted mean of its states' extents
   (unit test, exact). The persistent ice is contained in every state's extent (≥ 99% of cells).
2. Against the zoom (R1's tool, L5 fixture + L6 s11 @ 400, seed 2 @ 580, seed 2 @ 620): the forced zoom's
   time-mean sea level after a 100 kyr spin-up, over ≥ 300 kyr, within **max(15 m, 0.25 × the zoom's
   swing)** of the run's. The time-mean iced area within 25%. The zoom's interglacial maxima within 20 m of
   the run's `ice_ig` sea level, and its glacial maxima within 30 m of `ice_glacial`. Pass on ≥ 4 of 5
   moments (the owner's ~70% bar).
3. Earth: the rule on Earth's L6 bed at dT 0 gives a mean of about today's ice plus a Pleistocene-like
   glacial share: about -100..-130 m in the run's terms, against -67.8 m from the orbit-only states today.
   `ice_ig` should be about today's ice (Antarctica + Greenland: -59 m on the run's rule today, ~-65 m real).

**"Zoom mean matches run"** (zoom side, R5): the slow test `tests/test_timezoom_mean.py` on the L5 fixture.
Spin-up 100 kyr, window 300 kyr, default forcing. |window mean - run| ≤ max(15 m, 0.25 × swing). The start
is not required to be near the run. Strict xfail until R3 (+R2 for the branch code).

**What replaces the 25 m start-drift test**: it stays, renamed and re-scoped as the *shared rule* check. Under
R3 it becomes: the zoom held at the warmest (and, separately, the coldest) orbital state, with CO2 and
albedo off, started from the run's own equilibrium for that state, drifts < 25 m in 20 kyr. It then tests
exactly what the run computes. The framing is tested by the window-mean test, not by drift.

**Cold-era health bars**: they need re-*wording*, not new numbers. As cycle means:
- Earth's Pleistocene in the run's terms (all land ice) is about -115 m mean (today's -65 plus a ~-50 m mean
  glacial excess), with glacial maxima ~-185 m. The -150 "typical" bar on the mean holds.
- -430 / -450 for the worst era's mean still allows an icehouse well beyond the LGM.
- Print the cycle's glacial bound (from `ice_glacial`) as information, not as a gate.
- The ~70% seed bar stays.

The one real change is that the bars will move: on main R3 makes moderately cold steps icier. Re-run the
10 seeds after R3 + R4 together rather than separately, or the intermediate result will look like a
regression.

## 7. What the owner needs to decide
1. PW-461: take B reshaped (R2 marine budget, then R3 cycle-state mean), accepting that main's moderately
   cold steps get icier as a result. Lean: yes.
2. Whether a cycle state's equilibrium is an acceptable stand-in for the time a sheet takes to grow (R3's
   stop rule). If not, the fallback is B(3), a reduced integration in the run (cost: tens of seconds per cold
   step at L6).
3. The zoom window: spin-up length (lean: 200 kyr) and whether Earth keeps its real-ice start (lean: yes).
4. Whether the time box moves: by the morning of 2026-10-21 only R1 is realistic. R2-R4 are 3-4 days in the
   run lane.
