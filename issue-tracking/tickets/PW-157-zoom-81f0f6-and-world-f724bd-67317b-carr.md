---
id: PW-157
title: Zoom 81f0f6 and world f724bd/67317b carry pre-PW-102 ice (stranded tropical cap)
type: task
status: done
parent: null
subsystem: zoom
effort: xs
impact: low
found_by: zoomice
blocked_by: []
relates: [PW-127, PW-102]
refs: ["zoom 81f0f6", "world f724bd", "world 67317b", "run 428083"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Zoom 81f0f6 (the PW-127 report) was made with the old zoom glacier rule; with the new rule the same spot (f724bd at 3.41,-38.65, seed 11) keeps its ice on the high plateau and ridges only (docs/review/ice/trop_d9324c_*.png). But the source worlds f724bd and 67317b come from run 428083, whose ice predates the PW-102 fix: the ~1.2 km tropical plateau cap there is the stranded kind PW-102 removed. Delete or remake 81f0f6 on the new code, and use a post-PW-102 run's world for tropical-ice showcases (the cleanup script won't drop 81f0f6 while PW-127 references it).

## Updates
- 2026-10-14: Status todo -> done. Deleted zoom 81f0f6. World 67317b goes once the clouds branch (which edits PW-142, its last open ref) merges; world 9b8200 replaces it as the seasonal/ocean demo. f724bd stays while PW-123/124 cite it.
- 2026-10-14: Created from inbox draft draft-stale-pre-pw102-zoom.md (found by zoomice).
