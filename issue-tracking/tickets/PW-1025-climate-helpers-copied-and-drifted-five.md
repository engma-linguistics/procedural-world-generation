---
id: PW-1025
title: "Climate helpers copied and drifted: five rules for \'is the sea frozen\', and soils use a flat Budyko w while the climate uses the vegetation's"
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: s
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-877, PW-934, PW-881, PW-245]
refs: [planet/climate.py, planet/ocean.py, planet/coast.py, planet/coastal.py, planet/soils.py, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. Different parts of the model disagree on simple questions. Waves, tides, kelp, the sea-ice colour on the map, the rain and the deep-ocean circulation each decide "is this sea frozen?" with their own rule, so a coast can be frozen for its waves and open for its rain. Likewise the soils work out evaporation with a fixed forest-agnostic number, while the rivers use the vegetation's own value, so a forest's soil leaches by a different water balance than its rivers.

From the physics-surface audit (file:lines read, not all re-probed): sea ice `climate._winter_air` (~2618), `ocean.open_share` (ocean.py:216), `coast.sea_ice_share` (coast.py:390, from air temperature), `climate.biomes` (t < -10, :2130), `compute` output swing (:2395). Budyko/Fu: `climate.budyko` (:1794), `_budyko1` (:1056), `soils.fu_runoff` with `FU_W = 2.6` (soils.py:171/200) copied from `TUNE["budyko_w"]` but ignoring the per-cell w (1.5-4.0).

Fix: one `sea_ice_months(...)` in ocean.py returned from `compute` as a layer that coast, coastal and biomes read; one numpy `budyko(p, pet, w)` with the overflow-safe branch, soils taking `w` from the finish; tests that the numba and numpy Budyko agree and that the sea-ice consumers read one layer. Same disease as PW-877/934 (snowpack and permafrost).

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Created from inbox draft draft-climate-copies-drifted.md (found by code-audit-2026-10).
