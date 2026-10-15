---
id: PW-247
title: "Speed pass: profile and optimise the run, world finishing, zooms and the time zoom"
type: story
status: todo
parent: PW-244
subsystem: infra
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: []
created: 2026-10-15
updated: 2026-10-15
---

## Description
Owner (2026-10-15): a lot is being calculated; a faster machine helps but optimisation should too. Profile an L7 run (per step: tectonics, isostasy, erosion, lakes, climate, vegetation, ice), world finishing, zoom build, time zoom and highlights; find hot spots (numpy temporaries, Python loops, repeated work across steps, climate recomputed more than needed, numba kernels not parallel or not cached, I/O). Rules: identical outputs (or bit-for-bit within float noise, checked against goldens) unless a change is explicitly agreed; keep numba parallel kernels deterministic (PW-215). Report before/after timings per stage at L6 and L7 on the new machine. Also check thread scaling on the bigger machine.

## Updates
- 2026-10-15: Created.
