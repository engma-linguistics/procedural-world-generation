---
id: PW-1035
title: Slicing replays from t=0 after any edit under planet/, and four cache-key rules disagree about what \"code changed\" means
type: task
status: done
parent: null
milestone: v1
subsystem: store
effort: s
impact: high
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-089, PW-740, PW-508, PW-557]
refs: [planet/timeline.py, planet/provenance.py, planet/store.py, planet/highlights.py, planet/lineages/land.py, planet/lineages/recent.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. After almost any code change, even to the web server or the zoom, every existing run forgets its saved checkpoints and rebuilds a moment from the very start: 30-40 minutes per billion years at L7. Meanwhile some caches don't notice changes that do matter, so they can show stale results.

Verified on main b36c9581: `provenance.source_sha` hashes all of `planet/**/*.py` except `__main__.py`; `timeline.replay` (:304-321) uses a checkpoint only when that hash matches, else starts at t=0. Separately `store.code_digest` (:119) hashes only `planet/*.py` + `timezoom/*.py` and is used by the lineages caches; `highlights.VERSION` (:145) is a SHA-1 of highlights.py alone, and its cache ignores the world's content, so a re-saved world keeps stale highlights. PW-089 was closed on the warning message.

Fix: (1) always try the latest checkpoint; fall back to t=0 only if loading it raises; the keyframe comparison (timeline.py:349-361) already refuses a mismatching replay. (2) One `provenance.code_hash(scope)` that hashes the import closure of a named entry module ("sim", "finish", "lineages", "highlights"); delete `store.code_digest` and `highlights.VERSION`; key the highlights cache on the world file's mtime/size too.
- [ ] editing server.py no longer makes slice replay from t=0
- [ ] one hashing function; each cache names its scope

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Status todo -> done. Fix lane 49: (1) timeline.replay always tries the latest checkpoint at or before t and falls back to t=0 only if loading it raises (logged); slice_world's keyframe comparison still refuses a mismatching replay. So editing server.py (or anything) no longer makes a slice replay from t=0. (2) provenance.code_hash(scope): a hash of the import closure (AST, function-level imports too, except inside store/parallel/provenance, whose own source counts) of each scope's entry modules: sim (tectonics.simulation), finish (world, finish), lineages (lineages.run), highlights (highlights), plus all. store.code_digest and highlights.VERSION deleted; lineages land goods and recent climates key on code_hash('lineages'); the highlights cache keys on code_hash('highlights') and the world file's size and mtime; run.json's code stamp adds sim_sha, which slice_world's warning compares. Server, api, zoom, zoom_fine are in no scope (test_store.test_code_hash_scopes). Tests: test_simulate_checkpoints_and_replay (other-code stamp still uses the checkpoint; a broken checkpoint replays from t=0), test_highlights_cache_follows_the_world_file. README and overview known limits updated. Not-slow suite 736 passed, goldens unchanged.
- 2026-10-29: Owner 10-29: reliability bugs come into v1.
- 2026-10-29: Created from inbox draft draft-replay-from-checkpoint-and-one-code-hash.md (found by code-audit-2026-10).
