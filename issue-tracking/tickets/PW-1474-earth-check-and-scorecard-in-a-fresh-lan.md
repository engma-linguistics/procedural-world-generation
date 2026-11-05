---
id: PW-1474
title: earth_check and scorecard in a fresh lane worktree start re-downloading the Earth data
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: xs
impact: low
found_by: lane 187b (worktree-agent-a176595bbea6d0de9)
blocked_by: []
relates: [PW-1458]
refs: [tools/earth_data.py, tools/earth_check.py, tools/scorecard.py, docs/coordination.md]
created: 2026-11-04
updated: 2026-11-04
---

## In plain words
A lane works in its own copy of the repo. That copy has no `data/earth` folder, which holds the Earth maps that
`tools/earth_check.py` and `tools/scorecard.py` compare against. When a lane runs either tool, it quietly starts
downloading those datasets again from the public servers. On 2026-11-04 the Kottek server reset the connection, so
earth_check crashed. A lane can then report "earth_check failed" or skip it, and a climate change gets merged without
its Earth check.

## Description
- In a fresh worktree, `data/` does not exist (`.gitignore` line 14). `earth_data.earth_on_grid` builds into
  `<worktree>/data/earth/` and fetches raw sources (Kottek, ETOPO, GPCC, ...) with curl.
- Lane 187b worked around it by copying the main checkout's `data/earth/*.npz` and the Kottek wayback zip into the
  worktree (~150 MB, without the 1.7 GB of raw zips), after which earth_check ran from cache.
- Fix options: let `earth_data` read its cache from the main checkout (for example through an environment variable
  such as `PLANET_EARTH_DATA`, read-only, without symlinks, so nothing in a lane can delete it), or add the copy step
  to the lane setup in `docs/coordination.md`.

## Acceptance
- `uv run python tools/earth_check.py` in a new lane worktree runs from the cached data with no download, and nothing
  in the lane can write to or delete the main checkout's `data/earth`.

## Updates
- 2026-11-04: Created from inbox draft draft-worktree-earth-check-no-cache.md (found by lane 187b (worktree-agent-a176595bbea6d0de9)).
