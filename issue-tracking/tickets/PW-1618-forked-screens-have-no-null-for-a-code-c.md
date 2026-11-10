---
id: PW-1618
title: "Forked screens have no null for a code change: seed 77's inland share jumps ~3-4 points under any hydrology change"
type: task
status: done
parent: null
milestone: later
subsystem: infra
effort: s
impact: med
found_by: scout261
blocked_by: []
relates: [PW-054, PW-831]
refs: [tools/fork_screen.py, docs/coordination.md, docs/review/wetlands/scout261.md, docs/review/wetlands/scout261/same_state.py, docs/review/basins/scout251/fork_run.py, docs/review/wetlands/scout260.md]
created: 2026-11-09
updated: 2026-11-09
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
- [x] main's draws on seed 77 differ by as much as an unrelated code change moves them, or the screen states it can't judge seed 77

## Updates
- 2026-11-09: Created from inbox draft draft-fork-screen-code-perturbation-null.md (found by scout261).
- 2026-11-09: Done (lane 263). `tools/fork_screen.py` (spin / cont / queue / measure / spread; README in docs/coordination.md "Forked screens"): draws now perturb the noise (`--kind rng`: the per-step random streams keyed by the draw) or the state (`--kind elev`: crust thickness x 1 + 1e-12 N), plus a code-change null (`--fp-null`: (elev + 1000) - 1000 into surface.erode). On main a866c5ad, L6 seeds 1/2/77/3199, every draw diverges (rng at 204 Myr, elev 220-308, fp-null 228-296) and main's spread is wide: inland medians 4.2-11.2 / 6.4-10.7 / 6.7-12.7 / 12.4-15.2%, giant-lake frames up to 30%. Seed 77's 6.7-12.7 covers scout 261's fix at 14.2 only in part (its 15.9-16.1 lie above; scout 261's main was older code): a single seed can't judge; the README says judge all seeds at once plus the same-state check.
