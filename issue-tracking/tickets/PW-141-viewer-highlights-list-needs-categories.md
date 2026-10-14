---
id: PW-141
title: Viewer highlights list needs categories (55 places in one list)
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: low
found_by: travel
blocked_by: []
relates: [PW-140]
refs: [viewer/index.html, planet/highlights.py, "world 67317b"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
With the PW-140 travel finders (beach, ski, mild_winter, year_round) a world like 67317b
lists 55 highlights in one score-ordered list, with every marker the same pink ring.
Travel picks sit between landscape features (ranks 11-54) and are hard to find.
Suggest a category per kind in highlights.py (landscape, water, climate, travel), a
small filter/grouping in the viewer list, and a colour per category for the markers.
(`?hl=N` now opens highlight N directly, which helps meanwhile.)
- [ ] category field on features (or a kind -> category map shared with the viewer)
- [ ] list filter or grouping; marker colour per category

## Updates
- 2026-10-14: Created from inbox draft draft-highlight-categories.md (found by travel).
