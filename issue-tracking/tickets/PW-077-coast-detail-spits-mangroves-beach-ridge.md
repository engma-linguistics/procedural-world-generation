---
id: PW-077
title: "Coast detail: spits, mangroves, beach ridges, dendritic tidal channels"
type: task
status: wontdo
parent: null
milestone: null
subsystem: coast
effort: l
impact: med
found_by: deltas
blocked_by: []
relates: []
refs: [planet/coast.py, planet/zoom/regional.py, "zoom ce4b72"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Not done in `planet/coast.py` / the zoom: spits deflected by longshore drift, mangroves (tropical tidal
coasts), visible beach ridges in the zoom preview, and a dendritic eroded tidal-channel network (it's
noise-based now). Split when picked up.

## Updates
- 2026-10-14: Status todo -> wontdo. Merged into PW-097 (coast form); mangroves go to PW-188.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Coast ('Not done').
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
