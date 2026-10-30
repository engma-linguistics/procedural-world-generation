---
id: PW-1031
title: Any ValueError while building a world silently becomes an hour-long \"old run\" replay; other old-run fallbacks quietly change the world
type: task
status: done
parent: null
milestone: null
subsystem: store
effort: xs
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-813]
refs: [planet/api.py, planet/timeline.py, planet/tectonics/params.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. If anything goes wrong while the viewer builds a world from a run (a plain programming error, say), the code assumes the run is "too old" and starts a replay that can take an hour, then fails or saves something different. The real error is never shown. A few other "if this is missing, pretend" defaults make an old run produce a subtly different world instead of saying "delete and re-run", which the no-backward-compatibility rule says we don't want.

Verified on main b36c9581: `api.py:180-185` `except ValueError:` → `T.slice_world` (meant for `timeline.py:403-406`'s "too old" check, but `world_from_frame` runs the whole climate/hydrology/soils/vegetation finish, where numpy raises ValueError for any shape bug). Also `Params.from_stored` (params.py:198-208) drops unknown keys and fills new ones; timeline.py:206 missing plant_groups unlocks all flora; :208 missing pco2 → CA_REF; :210 reef_builders_t → -inf; :412 volcano-table schema mismatch → [].

Fix: delete the ValueError fallback (or raise a dedicated `RunTooOld`), make the shims strict with a "made by older code; delete and re-run" message, and add a test that a `world_from_frame` exception reaches the caller.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Status todo -> done. Fix lane 49: api._slice_locked no longer catches ValueError and replays: any error building a world from a keyframe reaches the caller (test_api.test_slice_error_reaches_caller). Made strict with 'made by older code; delete it and re-run': Params.from_stored (removed or missing params), timeline.keyframe_vegetation (no plant_groups, reef_builders_t or keyframe pco2), world_from_frame (no keyframe layers or sea level; missing or mismatched volcano table). test_invariants' old-run tests and test_highlights.test_ago_time (it passed partial params) updated to match. Not-slow suite 731 passed.
- 2026-10-29: Created from inbox draft draft-old-run-fallbacks-hide-bugs.md (found by code-audit-2026-10).
