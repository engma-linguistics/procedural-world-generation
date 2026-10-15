---
id: PW-073
title: The Earth world can't be zoomed (no rock layers)
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: viewer2
blocked_by: []
relates: []
refs: [tools/earth_world.py, planet/zoom.py, "world dc3732"]
created: 2026-10-14
updated: 2026-10-15
---

## Description
World 2f38e3 (Earth, ETOPO1) has no `rock`/`surface_rock`/`sediment_cover` layers, so `planet zoom` and the
viewer's Zoom button can't run on it. Give `tools/earth_world.py` a plausible rock map (e.g. orogen on high
relief, shield elsewhere, sediment on lowlands) or let the zoom fall back to a default rock.

## Updates
- 2026-10-15: Status todo -> done. Merged (smalls2).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Viewer / Earth world (confirmed: 2f38e3 has no rock layers).
