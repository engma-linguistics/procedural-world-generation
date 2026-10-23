---
title: "Full flora arrives only in a run's last ~15-25%, so showcase moments are squeezed to its end"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: surface
effort: s
impact: med
found_by: pw634-bug-hunt
blocked_by: []
relates: [PW-634, PW-434]
refs: [planet/vegetation.py, planet/highlights.py, planet/timeline.py]
---

## Description
The plant groups (`vegetation.GROUPS`, decision 3) appear at Earth's fractions of the span from
`plants_from` to the hard deadline (`group_windows`): flowering trees and shrubs ~0.73, grasses ~0.85,
C4 grasses and succulents ~0.94 (each jittered 0.6-1.3x). In the v1 1 Gyr runs the full flora exists
only from 772-876 Myr on; in the 2 Gyr Earth-like run bf5ee9 from 1636 Myr. Before that a world has
moss/crust in the grass and shrub niches, so no pasture, little foraging or fuel (PW-634).

PW-634's fix makes `highlights.representative_time` (`--at auto`, `planet make`) pick only among frames
once the last group has appeared. That leaves 32-58 candidate frames (128-232 Myr) per 1 Gyr run, and
those frames are the run's end, where sea level runs deepest (the 2026-10-21 health batch: 7 of 8 runs
end at -370..-600 m, PW-434). On the stored runs the new picks sit 30-150 m below the run median in 6 of 9
(still inside the note's band, so not flagged).

The decision: is "the full flora only at the end of the run" what we want? Options:
1. Keep it (evolution is part of the story; showcases are late-run worlds). Nothing to do.
2. Compress the timeline so every group exists by, say, 60-70% of the span (changes `simulate` outputs:
   the serial physics lane's call, re-run goldens).
3. Pick showcases by geography alone and let a pre-grass world be a pre-grass world, labelled in the
   viewer (revert the PW-634 restriction to a nudge).
Recommendation: 1 for v1 (cheapest, already merged), revisit with 2 when PW-434's deep end-of-run sea
level is fixed or if late-run geography turns out atypical.
- [ ] owner picks an option
