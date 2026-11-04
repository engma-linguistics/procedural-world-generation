---
id: PW-1313
title: "God tree: 26 beings of cultures that died out still show as living on b4d502"
type: task
status: done
parent: PW-1308
milestone: v2
subsystem: culture
effort: xs
impact: low
found_by: lane117
blocked_by: []
relates: [PW-1306]
refs: [planet/lineages/gods.py, docs/review/religion/slice1.md, "run b4d502", "run a24559"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
**In plain words.** After lane 117's last fix (flushing culture endings after the last frame), 26 beings on run b4d502 whose cultures have ended are still marked alive. a24559 wasn't re-checked. Find which endings are missed (likely cultures ending between frames or merged away) and mark their beings dormant or faded per gods_mode.

## Updates
- 2026-11-03: Status todo -> done. Lane 166: two misses in gods.py inputs(): a culture merging into one that had already died out carried its gods into the dead culture (now it dies with it), and a dead culture's lagging cells after its end could found new gods (now dropped). b4d502 and a24559: 0 living beings of ended cultures (was 26 / unchecked).
- 2026-11-03: Milestones 11-03: later -> v2: v2 must-have: dead cultures' gods shown as living, fixed with the faith editor
- 2026-11-03: Triage 11-03: v2 -> later: later cultures work (languages, polities, religion, morality); food comes first (fresh-eyes review, D44)
- 2026-11-02: Created from inbox draft draft-gods-dead-cultures-still-living.md (found by lane117).
