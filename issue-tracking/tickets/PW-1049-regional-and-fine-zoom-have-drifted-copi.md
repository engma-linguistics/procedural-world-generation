---
id: PW-1049
title: "Regional and fine zoom have drifted copies of the finish step: a volcanic island gets a full climate class in one and Af/Cfb/ET only in the other"
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: s
impact: low
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-516]
refs: [planet/zoom/regional.py, planet/zoom/fine.py, planet/climate.py, planet/vegetation.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. Small islands the world map treats as sea get their own climate when you zoom in. The regional zoom picks from eight climate types; the fine zoom from only three, so the same island can change climate between the two zoom levels.

Verified on main b36c9581: `zoom.py:3204-3207` chooses Af/Am/Aw/Cfa/Cfb/Dfc/ET (and BWh) for "lone" land pixels; `zoom_fine.py:1218` uses `np.where(t_cold >= 18, 0, np.where(t_cold > 0, 14, 28))`. Both copies also carry the same bare-ground biome patch (`zoom.py:3215`, `zoom_fine.py:1223`, `bare = (biome == 4) & ~glacier`), which is dead: land biomes are overwritten by `vegetation.biome_of` right after, and `climate.biomes`' 11 land rules are thrown away by all three callers.

Fix: one `finish_climate(...)` used by both zooms, with named Köppen/biome ids instead of 0, 14, 28, 29; replace `climate.biomes` with a sea-only `sea_biome` and delete the two dead patches. Fine-zoom islands' classes change on purpose.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-zoom-fine-finish-climate-drift.md (found by code-audit-2026-10).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
