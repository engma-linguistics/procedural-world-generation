---
id: PW-1421
title: The planet navigator can run only the D&D peoples tree; offer the same tree choice as the New planet form
type: task
status: todo
parent: null
milestone: null
subsystem: peoples
effort: xs
impact: low
found_by: lane 153
blocked_by: []
relates: [PW-1394]
refs: [viewer/navigator.js, "planet/make.py::peoples_trees", "planet/lineages/run.py::list_trees", viewer/start.js]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: PW-1394 let the New planet form pick which peoples tree to build (dnd, seven_meals, or a saved tree). The "Run D&D peoples" button on an existing world or time zoom (viewer/navigator.js, `data-do="peoples"`, `tree: 'dnd'`) still builds only the D&D tree, so Daniel cannot start a Seven Meals peoples run on a world he already has without opening the tree editor.
Give that button a tree choice (a small select fed by `GET /api/make/options` `peoples`, or a new `/api/lineages/trees`), defaulting to dnd.
- [ ] a world or time zoom in the navigator can start a peoples run of any listed tree

## Updates
- 2026-11-03: Created from inbox draft draft-navigator-peoples-tree-choice.md (found by lane 153).
