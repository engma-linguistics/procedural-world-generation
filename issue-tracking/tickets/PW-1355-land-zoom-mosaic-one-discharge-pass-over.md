---
id: PW-1355
title: Land zoom mosaic, one discharge pass over all sections after the sweep
type: task
status: todo
parent: PW-1299
milestone: later
subsystem: zoom
effort: m
impact: high
found_by: lane129
blocked_by: []
relates: [PW-1302, PW-1296]
refs: [planet/zoom/match.py, "planet/zoom/match.py::inflows", "planet/zoom/match.py::walls", "planet/zoom/stage_landscape.py::final_drainage", docs/review/land-zoom/rivers.py, docs/review/land-zoom/rivers-round1.md, docs/review/land-zoom/rivers1/, docs/review/land-zoom/seams-round2.md, "zoom:683193", "zoom:83b0b1", "zoom:a3a793", "zoom:3580b7", "zoom:fe600a", "zoom:e2313a", "world:dba204"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
**In plain words.** When two land sections meet, a river flowing from the section built first into the later one
now keeps its water (lane 129). A river flowing the other way, from the later section into the earlier one, cannot:
the earlier section was finished first and its river below the line carries its own guess of how much water comes
from the later section's ground. On lane 129's practice pairs that guess is off by more than 25% for most big rivers
(tile pair: 19,200 m3/s delivered where the earlier section carries 3,900; block W: 40,200 vs 98,500). A river that
crosses three sections, or the same line twice, gets this wrong at every crossing back.

**What to do.** After the sweep (PW-1296) has built every section, one pass over the whole mosaic that recomputes
discharge only (not the ground): each place's water from its owner section's own network (`receiver` layer, the
owner's pixels only), sections joined where one owner's receiver lies in another's ground (as
`match.inflows` finds the crossings), sources per pixel = the owner's own discharge minus what its donors pass on (so
the coarse inflows and lake rules each section applied are kept), then accumulate in downstream order over the joined
graph and write each section's `discharge` (and what is derived from it: river_dist, river_nav, the falls' and deltas'
discharges) back. Exact for any number of crossings both ways, cheap (a graph walk, no landscape pass).

Lane 129 matched the later section's routing to the earlier one at the line (water enters the earlier section's ground
only where that section has a stream coming in, `match.walls`), so the pass mostly corrects discharge, not courses.
Valley widths in the earlier section stay graded to its old discharge (a nudge, not a rebuild); if that shows, a
re-match of the earlier section to the later (`--match` both ways in a second sweep pass) is the heavier fallback.

- [ ] mosaic discharge pass over the saved sections of a sweep; B->A crossings within 25% for rivers >= 500 m3/s on the
      practice pairs (docs/review/land-zoom/rivers.py)
- [ ] no change to any section's ground or coast

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: owner 11-03: no whole-planet fine map is fine; the L7->L9 refine of the chosen world is v5
- 2026-11-02: Created from inbox draft draft-land-zoom-mosaic-discharge-pass.md (found by lane129).
