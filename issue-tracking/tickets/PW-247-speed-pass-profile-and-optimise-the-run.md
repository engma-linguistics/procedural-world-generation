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
- 2026-10-29: 2026-10-29: profiled L6 200 Myr and L7 100 Myr (docs/review/speed/profile-2026-10-29.md). The climate is 75% of a run's wall at both levels (4.9 s per update at L7). The hot spots are carry's fixed ~150-sweep relaxation, rain, currents and smoothing. Candidates: a coarser climate in the spin-up, warm-started relaxations, an adaptive cadence (all output-changing), and numba for the numpy-level climate (bit-identical).
- 2026-10-29: 2026-10-29: owner wants more speed. World Orogen runs 600 Myr at 160k cells in ~2.5 min on CPU workers against our L7 ~20-40 min per Gyr; the gap is mostly model choice (synthesized heights, a steady 1-degree climate solve), but a fresh per-stage profile at L7 would show what is ours to win.
- 2026-10-26: Parent PW-244 -> none. (PW-900 backlog reorg).
- 2026-10-26: Merged PW-535: planet make's time estimates for L4, L5 and L8 are still scaled, not measured. (PW-900 backlog reorg).
- 2026-10-15: Created.
