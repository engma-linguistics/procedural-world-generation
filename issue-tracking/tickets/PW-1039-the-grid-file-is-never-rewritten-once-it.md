---
id: PW-1039
title: The grid file is never rewritten once it exists, and the viewer reuses any world at the same moment even if old code or --no-resources made it
type: task
status: todo
parent: null
milestone: v1
subsystem: store
effort: s
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-444]
refs: [planet/store.py, planet/api.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. Two places keep serving something stale without noticing. (1) The globe's cell layout is saved once per grid level and never refreshed, so if the grid code ever changes (PW-444 plans to touch it), every run, world and zoom would be drawn onto the wrong cells with no error. (2) When you ask for a world at a given moment, the viewer reuses any world already made at that moment, even one made by older finishing code, with resources switched off, or force-saved after a replay mismatch. After a climate or soils change merges you keep seeing the old world until it's deleted by hand.

Verified on main b36c9581: `store.py:540-552 write_grid` returns early if `'"nbr"' in path.read_text()[-200000:]` (it also reads the whole ~20 MB L7 file on every world save to do that check). `api.py:132-144 find_slice` matches only `source_run` and `t_myr` (and not-timezoom).

Fix: store a digest of centers+nbr in the grid file (or name it `L7-<digest>.json`) and rewrite on mismatch; store a `finish_key` (finish-scope code hash, erosion, resources flag) in world meta, match on it in `find_slice`, and skip worlds with `replay_matches_keyframe: false`. Tests for both.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Owner 10-29: reliability bugs come into v1.
- 2026-10-29: Created from inbox draft draft-stale-grid-file-and-reused-worlds.md (found by code-audit-2026-10).
