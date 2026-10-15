---
id: PW-237
title: hydrology.lakes costs ~0.6 s more per run step at L7 since the outlet cut (PW-055)
type: task
status: todo
parent: null
subsystem: infra
effort: s
impact: low
found_by: hydro
blocked_by: []
relates: [PW-055]
refs: [planet/hydrology.py, planet/kernels.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
lakes() now settles the lakes against the routed rivers (up to 3 tries) and recuts the outlet valleys
(CARVE_TRIES = 2), so it runs fill_shallow + kernels.lakes + route 3-9 times instead of once: at L7
~0.9-1.0 s per call instead of ~0.3-0.45 s (run 732abb frames), i.e. ~+15% on a run step, ~4x that at L8.
Ideas: start each step from the previous step's carved terrain (the valleys barely move in 2 Myr) and
do one recut; skip _settle's extra tries when no closed basin gets a river from outside its catchment;
reuse the priority-flood order between the settle and the carve.

## Updates
- 2026-10-15: Created from inbox draft draft-lakes-cost-l7.md (found by hydro).
