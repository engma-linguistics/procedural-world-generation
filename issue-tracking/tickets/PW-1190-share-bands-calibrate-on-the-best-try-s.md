---
id: PW-1190
title: Share bands calibrate on the best try's seed only
type: task
status: todo
parent: null
milestone: v2
subsystem: highlights
effort: s
impact: low
found_by: lane78
blocked_by: []
relates: [PW-1149]
refs: [planet/lineages/history/bands.py, planet/lineages/history/tries.py]
created: 2026-10-30
updated: 2026-10-30
---

## In plain words
When a people lands outside its share band, the run nudges that people's own density and runs the best try again, up to three times. A band met on that one roll may still be missed on another roll of the same tree.

## Description
- `bands.calibrate` re-runs only the best try's seed. Each round costs one try, about 250 s at L6.
- Options:
  - (a) keep it: the owner sees the nudge factor and can type it into the tree as the people's density;
  - (b) nudge on the mean share over all tries. This costs N tries a round.
  - (c) after a met band, offer a "keep this density" button in the workbench, which writes the nudged density into the tree.
- Lean: (c). It turns the soft target into a lasting, visible ecological number.
- [ ] decide (a), (b) or (c); build (c) if chosen

## Updates
- 2026-10-30: Created from inbox draft draft-share-bands-on-more-than-one-seed.md (found by lane78).
