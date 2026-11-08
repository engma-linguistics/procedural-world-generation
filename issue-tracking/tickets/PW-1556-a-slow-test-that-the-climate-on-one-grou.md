---
id: PW-1556
title: A slow test that the climate on one ground gives the same arid share at L7 as on the nested L6 grid
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: s
impact: med
found_by: scout221
blocked_by: []
relates: [PW-290, PW-015]
refs: [docs/review/climate/levels/scout1.md, "planet/nest.py::climate_coarse", "planet/climate.py::compute", "planet/climate.py::koppen", "run a19366", "commit 14165233", "commit 6926583"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: the 10-point "L7 is drier than L6" gap of PW-290 came from the old rain kernel and was fixed
on 10-16 (PW-015 stage 1, commit 14165233), but nothing checks for it, so a later rain change could bring it
back unnoticed. L7 runs compute their spin-up climate on L6 (PW-247), so whole-run medians and the L6 judge
would not see it; only the finish window and the worlds would, at the showcase level.

Scout 221 measured it cleanly by computing one ground's climate on the L7 grid and through
`nest.climate_coarse(g7, 6, ...)`: today +0.5 to +1.1 points of Koppen B (mean +0.84) and land rain within
2% over nine moments of five L7 runs; on the 10-15 code (6926583) +6 to +8 points and land rain -27%.

What breaks if never done: a rain change that is level-dependent passes every L6 check and the L6 judge and
ships drier L7 showcase worlds (as on 10-15), with nobody noticing until a health sweep.

- [ ] a `slow` test on a generated L7 ground (a small fixed seed, or a stored test fixture): Koppen B share of
      ice-free land within 2 points and land rain within 5% between `climate.compute` on L7 and
      `nest.climate_coarse` to L6
- [ ] confirm it fails on `6926583`'s `planet/` (the scout's `old.py` approach: `git archive` into a scratch dir)

## Updates
- 2026-11-08: Created from inbox draft draft-level-pair-climate-guard.md (found by scout221).
