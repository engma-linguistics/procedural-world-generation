---
id: PW-247
title: "Speed pass: profile and optimise the run, world finishing, zooms and the time zoom"
type: story
status: todo
parent: null
milestone: v2
subsystem: infra
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: []
created: 2026-10-15
updated: 2026-10-29
---

## Description
Owner (2026-10-15): a lot is being calculated; a faster machine helps but optimisation should too. Profile an L7 run (per step: tectonics, isostasy, erosion, lakes, climate, vegetation, ice), world finishing, zoom build, time zoom and highlights; find hot spots (numpy temporaries, Python loops, repeated work across steps, climate recomputed more than needed, numba kernels not parallel or not cached, I/O). Rules: identical outputs (or bit-for-bit within float noise, checked against goldens) unless a change is explicitly agreed; keep numba parallel kernels deterministic (PW-215). Report before/after timings per stage at L6 and L7 on the new machine. Also check thread scaling on the bigger machine.

## Updates
- 2026-10-29: Lane 27b (docs/review/speed/README.md). The defaults are now an 8/4/2 Myr ramp: the owner's fine end, every 2 Myr step in the last 10 Myr before the finish window (climate_ramp_fine; 2 more updates a run). On 6 L6 draws it sits next to the 8/4 ramp (moment T -0.2 C, same passes and iceboxes). Arm E (climate every 2 Myr, 18 L6 draws): main's warm finish is mostly its own 4 Myr lag (E -4.1 C vs main, CI excludes 0; the 8/4 ramp is within 0.3 C of E). But E has 10 iceboxes in 18 against main's 2: the ice and the climate catch up one step per update, so how much ice a run grows depends on the update rate (inbox draft). At L7 (4 seeds, 1 Gyr): the L6-grid spin-up alone passes 4/4 like main, and the full default 3/4. The only consistent shift, less arid land in the spin-up records, is absent from the native finish window the worlds get. L7 wall 11591 s main, 6512 s grid alone, 3279 s full default (not under equal load; inbox draft for a fair timing).
- 2026-10-29: Lane 27 (docs/review/speed/README.md). The run's climate is now on an 8/4 Myr ramp: every 8 Myr, then 4 in the 30 Myr before the finish window, early whenever dT moves 1 C (arm C). The L6 paired judge moved no measure (16/18 against main's 14/18), at 1.5x per L6 run. A 16 Myr early step (arm B) failed: colder, more iceboxes, the lag in the ice-albedo/CO2 loop. An L7 run's spin-up climate is solved on the nested L6 grid (planet/nest.py; ~0.37 of a native update's cost, ~2.9x per L7 Gyr expected). Its L7 judge (arm G) and the 2 Myr convergence arm (E) were still running at handoff.
- 2026-10-29: 2026-10-29: profiled L6 200 Myr and L7 100 Myr (docs/review/speed/profile-2026-10-29.md). The climate is 75% of a run's wall at both levels (4.9 s per update at L7). The hot spots are carry's fixed ~150-sweep relaxation, rain, currents and smoothing. Candidates: a coarser climate in the spin-up, warm-started relaxations, an adaptive cadence (all output-changing), and numba for the numpy-level climate (bit-identical).
- 2026-10-29: 2026-10-29: owner wants more speed. World Orogen runs 600 Myr at 160k cells in ~2.5 min on CPU workers against our L7 ~20-40 min per Gyr; the gap is mostly model choice (synthesized heights, a steady 1-degree climate solve), but a fresh per-stage profile at L7 would show what is ours to win.
- 2026-10-26: Parent PW-244 -> none. (PW-900 backlog reorg).
- 2026-10-26: Merged PW-535: planet make's time estimates for L4, L5 and L8 are still scaled, not measured. (PW-900 backlog reorg).
- 2026-10-15: Created.
