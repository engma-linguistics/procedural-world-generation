---
id: PW-671
title: Cleared land on a finished world's other colour views, runs picker and 3D relief
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: zoompeoples
blocked_by: []
relates: [PW-669, PW-662]
refs: [viewer/index.html, viewer/relief.js]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-669 tints a finished world's `satellite`, `vegetation` and `biome` colours with its newest peoples run's overlay (`&peoples=RUN` picks one, `&peoples=0` none; checkbox "show cleared land"). Not done: the plant type and tree views (a world has `tree_cover` in its layers but no tree cover colour layer; the run view has one), a picker when several peoples runs name the same world, and a look at the flat map in 3D relief (the tint is a per-cell colour, so it should work there, but nobody has checked). The tint strengths (`anthroTint`) are the run view's; on the satellite they are strong enough to read from space (cropland as orange patches), which may be more than a satellite shows.

What to try: a tree-cover view for worlds with the tint, a run picker when several peoples runs name the world, and a quieter tint factor for the satellite.
- [ ] a world with two peoples runs offers both

## Updates
- 2026-10-23: Created from inbox draft draft-world-anthro-tint-more-views.md (found by zoompeoples).
