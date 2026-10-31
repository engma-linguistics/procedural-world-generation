---
id: PW-1233
title: PW-171's continental pits now hold lakes up to ~7 km deep (they were inland "sea" before PW-1229)
type: task
status: todo
parent: null
milestone: null
subsystem: tectonics
effort: s
impact: med
found_by: lane98
blocked_by: []
relates: [PW-171, PW-1229]
refs: [planet/tectonics/crust.py, planet/hydrology.py, docs/review/v1-cut/inland-pits.md]
created: 2026-10-31
updated: 2026-10-31
---

## Description
In plain words: the narrow pits that the plate model leaves inside continents (PW-171, often one cell, 1 to 4 km
below sea level) used to be drawn as tiny patches of ocean. Since lane 98 (PW-1229) they are land, and the lake
scheme fills them, so a wet one becomes a lake kilometres deep. A pit at −65.5°, −31.6° in a scratch L6 world
(4006fe) also turns the highland basin around it into a 102-cell open lake at 1438 m. That is the honest result
for the terrain we make. The pits themselves are the oddity, and they are now more visible as lakes than they
were as sea.

Measured on scratch worlds at 1000 Myr: pockets' floor median −1129 m (L6 s1), −2933 m (L6 s2), −2417 m and
−1886 m on two new-code L6 runs, −172 m (L7 s1). Sediment in the run doesn't heal them.
This feeds PW-171 (probably `--merge-into PW-171`). That ticket fixes the source. Nothing in the hydrology
should clamp lake depth.
- [ ] pockets deeper than 1 km per world (count) reported by the scorecard or the health tool

## Updates
- 2026-10-31: Created from inbox draft draft-pw171-pits-hold-deep-lakes.md (found by lane98).
