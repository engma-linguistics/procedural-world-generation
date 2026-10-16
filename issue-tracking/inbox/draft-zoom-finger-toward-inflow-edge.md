---
title: "Zoom deltas: a finger running out to the region's edge beside its own river's inflow gets no channel"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoom-batch6
blocked_by: []
relates: [PW-363]
refs: [planet/zoom.py, docs/review/zoom-polish/batch6.md, "world 592f2a"]
---

## Description
After PW-363 (zoom batch 6) 23 of 24 bird's-foot fingers on zoom 4.97,-114.51 of world 592f2a (1000 km @ 2 km,
seeds 1-5) have a channel of their own to the sea. The one left, seed 5, the 9,900 m^3/s delta at the region's
top edge (region px ~(8, 204)): its finger points out to the edge right beside where its own river enters the
region. The edge there is no outlet (`edge` is cleared round each inflow point so the river can't drain straight
back out), so the finger's branch (`make_branches`, the fallback from the nearest channel) can't end there: it
stops open, and its end drains back into the delta (a loop), so the branch is taken back.
Try: let a delta's seaward direction ignore the sea beyond an inflow edge, or don't build a finger whose tip lies
on a non-outlet stretch of the built area's edge (`_delta_forms` would need the inflow points).
- [ ] every bird's-foot finger in the region has a channel, or isn't drawn (zoom 4.97,-114.51 seeds 1-5)
