---
id: PW-669
title: Show a peoples run's cleared land on the finished world's satellite and vegetation views
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: anthro
blocked_by: []
relates: [PW-662]
refs: [viewer/index.html, planet/lineages/landuse.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-662 tints the cleared land on a peoples run's own views ('tree cover', and 'vegetation' / 'satellite' wherever a run carries them) and adds a 'land use' layer. A peoples run has no vegetation or satellite layer (only tree cover), so the satellite colours of the finished world 1df1c3 / 3e9e7d, the picture owners actually look at, are not tinted.

What to try: when a world is opened, look for a peoples run on it (`meta.world` equal to the world id; take the newest, or a `&peoples=RUN` parameter), load its `anthro_*.bin` layers like `V.anthro` in viewer/index.html, and apply `anthroTint` to the world's `satellite`, `vegetation` and `biome` colours, with a checkbox "show cleared land" in the display panel. The cells are the same L7 cells, so no resampling. Show a legend note naming the run.
- [ ] a world with a peoples run offers the toggle; one without it does not
- [ ] satellite on the globe shows fields and pasture around the farming peoples

## Updates
- 2026-10-23: Created from inbox draft draft-anthro-tint-world-satellite.md (found by anthro).
