---
id: PW-913
title: "Tech tree: a visible tab (global and per civ), default stop at ~mid-1400s fantasy fare, user-chosen earlier stop ('before cannons'); uneven pace, distance-based catch-up, pockets that resist advancement"
type: story
status: todo
parent: PW-675
milestone: later
subsystem: culture
effort: l
impact: high
found_by: owner
blocked_by: []
relates: [PW-856]
refs: []
created: 2026-10-26
updated: 2026-11-03
---

## Description
Owner 2026-10-26: uneven between civs; contact moves tech; isolated folk left farthest behind; some (Piraha, Sentinelese-like) refuse it, especially in inaccessible jungle.

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: the tech tree's era stop already works; the visible tab is not a must-have
- 2026-10-29: Merged the Technology tab (fun lane 47): Tree (default), Timeline, Map (the globe's technology layer, every stored moment), Inventory, Cascade, plus the old Table. Still open: the tech stop, uneven pace, catch-up, resistant pockets.
- 2026-10-29: Fun lane 47: the Technology tab is built (viewer/techtab.js in viewer/lineages.html; screenshots and notes in docs/review/techtree-tab/). In plain words: six views, Tree first (mock-up 1 unchanged), then Timeline, Map, Inventory, Cascade (one tech only; 'who taught whom' dropped) and the old Table. The Map is the globe viewer itself, embedded, with a new 'technology' layer drawn on the run's own cells at every stored moment, with both colour modes, stars for inventions and giver-to-taker arrows; the same layer is in the main viewer. Still open on this ticket: the tech stop (mid-1400s default, user-chosen earlier stop), uneven pace, catch-up by distance and pockets that resist new techs.
- 2026-10-29: Owner view ruling (docs/review/techtree-views/). In plain words: the Technology tab gets four of the five mock-up views. Keep 1 (per-people tree, with the real-world date note at the bottom) as the default, unchanged. Keep 2 (timeline) as a secondary view. Keep 3 (map with timeline and colour modes), rebuilt at full fidelity: draw it on the globe's own cells at every stored moment, not the mock-up's 1-degree raster sampled at 13 moments. Keep 4 (inventory) as is. From 5, keep only the 'one tech: its cascade' view and drop 'all techs: who taught whom'.
- 2026-10-26: Parent PW-856 -> PW-675. (PW-900 backlog reorg).
- 2026-10-26: Created from inbox draft draft-tech-tree-tab-and-stop.md (found by owner).
