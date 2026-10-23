---
id: PW-348
title: "World layers: land cells under 0.5 m are stored as elevation 0 (sea to readers) but carry soil and vegetation"
type: task
status: todo
parent: null
milestone: v1
subsystem: store
effort: xs
impact: low
found_by: vegbatch
blocked_by: []
relates: [PW-185]
refs: [planet/world.py, tests/test_soils.py]
created: 2026-10-16
updated: 2026-10-23
---

## Description
world.py stores `elevation` as np.round(elev) (int), so a land cell at 0 < elev < 0.5 m is saved as 0, which every reader (`elevation > 0`) takes for sea, while the model computed soil, vegetation and the rest on it as land. Seen as a failing test_world_soils (a soil type on a cell stored at 0 m) after the vegetation batch changed the L4 test run's trajectory; the test now checks soil only on `elevation < 0` / ice / lakes. Fix at the source, e.g. store land as at least 1 m (np.where(elev > 0, max(round, 1), min(round, 0))) so the stored land mask is the model's, then restore the test's `~land` checks.

## Updates
- 2026-10-23: Milestone null -> v1 (PW-597 triage, coordinator, 2026-10-23): a real bug in a v1 feature (sub-0.5 m land stored as sea but carrying soil and vegetation).
- 2026-10-16: Created from inbox draft draft-world-shore-cells-stored-at-0m.md (found by vegbatch).
