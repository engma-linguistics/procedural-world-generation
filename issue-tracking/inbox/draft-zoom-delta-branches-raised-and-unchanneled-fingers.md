---
title: "Zoom deltas: some distributaries run 30-90 m above the plain; some bird's-foot fingers get no channel"
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: low
found_by: zoom-batch5
blocked_by: []
relates: [PW-061, PW-124]
refs: [planet/zoom.py, docs/review/zoom-polish/batch5.md, "world 592f2a"]
---

## Description
After PW-061 (curved distributaries and fingers, zoom batch 5), on world 592f2a's showcase zooms (seeds 1-5):

- **Raised distributaries.** On the arc zoom -9.35,-161.39 (2000 km @ 4 km, six tidal deltas) the perched-river
  metric (river px >= 100 m^3/s with land < 30 m^3/s within 2 px > 30 m below every river px near it) rose from 33
  to 45 px per seed (> 100 m: 1.4 -> 1.2). E.g. seed 2 near px (340-349, 452-457): two parallel branches (1391 and
  1373 m^3/s) at 84-88 m with the plain beside them at 10-20 m. A branch's course is pinned; where it crosses
  higher ground further down (or the settle step lifts it, SETTLE_M), the landscape pass holds everything upstream
  at least as high, so the whole branch rides above the plain. The branch walk already refuses ground (the smooth
  coarse surface `base`) more than BRANCH_CLIMB_M = 30 m above its apex, but not the target surface's bumps
  (refusing those too cut the test delta's tidal branches off the funnels). Try: unpin a branch's pixels where it
  stands > ~20 m above the lowest land within 2 px after the landscape pass, or lay the branches out on the
  landscape pass's own surface (after a few iterations) instead of the target.
- **Fingers without a channel.** On the bird's foot of 4.97,-114.51 1-3 of up to 4 fingers get a channel (seeds 1-5:
  3, 2, 3, 2, 1 mouths), the others being cut off by the trunk's own course or high ground near the apex; a finger
  with no channel is an odd strip of land. Either drop a finger whose branch can't be laid, or let its branch
  start from the trunk nearer the mouth.
- [ ] arc zoom perched px back to ~33 per seed or below, without losing tidal mouths
- [ ] every bird's-foot finger has a channel, or isn't drawn
