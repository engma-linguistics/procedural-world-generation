---
id: PW-1175
title: "Niche learning: the peoples' competition still reads their authored comfort ranges, not what they have learned"
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: timezoom
effort: m
impact: low
found_by: lane79
blocked_by: []
relates: [PW-1155]
refs: [planet/lineages/history/habitat.py, planet/lineages/history/model.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
Two peoples compete according to `alpha` = niche_overlap, which is computed once from the authored comfort ranges and ways of life.
Lane 79 added `_learned_load` (PW-1155). On a cell where either people lives on learned country, it removes the ways-of-life
discount (mountain, subterranean, ...) in proportion to L. The discount is niche_overlap's x0.6 and same_way's x0.5 per differing
way. The comfort-range overlap part (temp_c, rain_mm) is unchanged. A cold people that has learned the steppe therefore still
competes with a steppe people as if its comfort were cold.

This is crude but sound for now: the ways term was the one that let the first people into a country sit in others' homelands on a
discount. Moving the temperature and rain overlap with the learned envelope is the faithful version. It would need either alpha
per cell, or a per-line learned comfort range from the cells it holds. Measure it on the lane 77 suite before and after.

## Updates
- 2026-10-30: Created from inbox draft draft-learned-niche-overlap.md (found by lane79).
