---
title: "Forked screens have no null for a code change: seed 77's inland share jumps ~3-4 points under any hydrology change"
type: task
status: todo
parent: null
milestone: later
subsystem: infra
effort: s
impact: med
found_by: scout261
blocked_by: []
relates: [PW-054, PW-831]
refs: [docs/review/wetlands/scout261.md, docs/review/wetlands/scout261/same_state.py, docs/review/basins/scout251/fork_run.py, docs/review/wetlands/scout260.md]
---

## Description
In plain words: the forked screen (one state at 200 Myr, continued with main and a candidate, draws = a 1e-5 C
climate offset) can't tell a real effect from the run taking a different path, because main's draws barely
differ from one another. On seed 77 at L6, main's four draws (offsets 0 / 1e-5 / 2e-5 / 3e-5 C) give inland medians
of 12.3 / 11.9 / 11.9 / 11.9%, three of them the same trajectory. Two unrelated code changes both moved it
the same way: scout 260's wetland candidate 12.1 -> 15.6% (2 draws), scout 261's dry-hollow fix 12.1 -> 14.2-16.1%
(3 draws), while on the same state the fix changes inland by only -0.24 points (`same_state.py`, the 200 Myr
checkpoint). So "outside main's spread" on seed 77 is likely any perturbation, not the change.

What breaks if never done: a sound change fails a screen (or a bad one passes) on a trajectory flip; reviewers
read a 3-4 point inland jump as the change's effect.

What to try: a null that perturbs the code path, not just the climate: e.g. main continued with a tiny change in the
erosion step (a 1e-9 relative nudge to elevation at the fork) or offsets large enough to diverge within 50 Myr;
check whether main's spread on seed 77 then covers 12-16%.
- [ ] main's draws on seed 77 differ by as much as an unrelated code change moves them, or the screen states it can't judge seed 77
