---
id: PW-1040
title: Peoples-run passes rewrite run.json without a lock (lost updates); two caches use fixed temp names; new ids aren't checked for collisions
type: task
status: todo
parent: null
milestone: v1
subsystem: store
effort: s
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: []
refs: [planet/lineages/landuse.py, planet/lineages/fuels.py, planet/lineages/demes.py, planet/lineages/techtree.py, planet/lineages/recent.py, planet/lineages/land.py, planet/store.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. When more than one thing adds to the same peoples run at once (say a viewer job and a command), one of them can silently undo the other's work. Two caches can also trip over each other's half-written files, and a new run or world can, rarely, land on an existing one's id.

Verified on main b36c9581: land use (`landuse.py:253-258`), fuels (`fuels.py:223-231`), demes (`demes.py:820-824`) and the tech tree (`techtree.py:343-353`) each do `json.loads(read_text)` → edit `meta` → `S.write_json`, with no `store.lock`. Slices, zooms and highlights do lock. `lineages/recent.py:217` writes `recent_rain.tmp.npz` and `land.py:246` writes `<stem>.tmp.npz`: fixed names, so two processes writing the same cache can rename each other's partial file. `store.new_id` is 3 random bytes with no existence check (`timeline.py` uses `mkdir(exist_ok=True)`).

Fix: `store.update_meta(run_dir, fn)` (take `lock(runs_dir, "meta-<id>")`, re-read, apply, write atomically) used by all four passes; a `store.atomic_path(path)` context manager with a unique temp name for the npz writers; `new_id` loops until unused and callers `mkdir(exist_ok=False)`.
- [ ] test: two threads updating different meta keys both survive

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Owner 10-29: reliability bugs come into v1.
- 2026-10-29: Created from inbox draft draft-store-concurrent-writes-lose-data.md (found by code-audit-2026-10).
