---
id: PW-1036
title: Random side streams collide with the per-step stream (setup rock ages = step 7's draws, and others); zoom seeds and noise salts collide too
type: task
status: todo
parent: null
milestone: null
subsystem: tectonics
effort: s
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-779, PW-339, PW-148]
refs: [planet/tectonics/setup.py, planet/tectonics/mantle.py, planet/tectonics/earth.py, planet/tectonics/simulation.py, planet/zoom.py, planet/zoom_volcanoes.py, planet/zoom_peoples.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. Some dice that are meant to be rolled separately are secretly the same dice. The starting rock ages reuse exactly the random numbers that step 7 of the simulation uses for its volcanoes and rifts; the mantle eddies reuse step 11's; the reef date reuses step 13's. The planet is still repeatable, but these choices are correlated by accident, and every new feature that picks a "spare" number risks another clash.

Verified on main b36c9581: `simulation.py:238` per-step stream `default_rng([seed, step_no])`; side streams `setup.py:159 [seed, 7]`, `mantle.py:185 [seed, 11]`, `earth.py:1126 [seed, 13]` are those same entropy lists. Zoom: `zoom.py:2381 default_rng(seed + 7)` (= seed+7's base stream), `zoom.py:1306 seed*7919+101+j`, `zoom_peoples.py:148`; noise salts `S + 61` and `S + 63` are each used for two unrelated features (zoom.py:2054/1950 vs zoom_volcanoes.py:290/267).

Fix: a tiny `planet/rng.py` with `stream(seed, "setup.rock_ages", *extra)` that mixes a crc32 of the tag into the entropy (the lineages' `crc32(line id)` pattern, PW-779), with the per-step stream given its own tag; a `SALT` table in zoom_kernels so every noise field has one named salt. Outputs change once on purpose: `--update-golden`.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-rng-named-streams.md (found by code-audit-2026-10).
