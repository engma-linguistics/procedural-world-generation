---
title: How wide should a gentle river's valley floor be inside a deep canyon?
type: task
status: needs-decision
parent: null
subsystem: zoom
effort: xs
impact: low
found_by: pw412
blocked_by: []
relates: [PW-412]
refs: [planet/zoom_fine_floodplain.py, planet/zoom_fine.py, "zoom 3453b8 (170672 -> 50 km @ 100 m)"]
---

## Description
PW-412 builds a valley floor along every alluvial reach (a gentle bed for its rock). The floor is cut regardless of the parent's ground within half a parent pixel of the valley axis: the parent pixel holding the river can't say where in it the floor lies. Beyond that, it spreads only over ground the parent holds within a bankfull depth of the floor's level.

The ticket's own example, the 310 m^3/s river at 0.04% in 170672, runs in a canyon about 1.2 km deep. At 1 km/px the parent's pixels beside it stand about 300 m above it. Its fine zoom 3453b8 now has a flat floor about 0.5-0.9 km wide. The volume of that cut goes onto the canyon's sides:
- block means are kept (rms 15.9 m before and after);
- the hillslope drainage is reshuffled, ±100 m ridge for valley, though nothing is raised systematically.

Options:
- A (as built): a floor at least one parent pixel wide on any alluvial reach, canyon or not. Real incised alluvial rivers do have floors (e.g. the Colorado's beaches and bars, Yosemite Valley's floor).
- B: in a canyon, scale the unconditional part down by the parent's relief beside the river, e.g. to the floor share that the block's hillslopes can take for a given rise. This gives narrower floors there, and meanders confined as before PW-412.

Coordinator's lean, from the agent: A. The canyon's gentle bed already says the river is alluvial there, and a floor in it is the commoner form.
