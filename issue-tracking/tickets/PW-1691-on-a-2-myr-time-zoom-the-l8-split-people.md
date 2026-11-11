---
id: PW-1691
title: On a 2 Myr time zoom the L8 split peoples run peaks at 69 GB, almost twice the 1 Myr split's 35.5 GB
type: task
status: done
parent: null
milestone: v1.0
subsystem: peoples
effort: m
impact: med
found_by: coordinator (lane 280 chain)
blocked_by: []
relates: [PW-1584, PW-1661]
refs: [docs/review/timezoom/two-myr.md, docs/review/refine-l8/split.md]
created: 2026-11-10
updated: 2026-11-11
---

## Description
**In plain words.** Making the peoples history on a refined L8 world takes almost twice the memory when the world's ice-age
zoom is 2 Myr instead of 1 Myr: 69.3 GB peak (run 1f49d0 on bcf4ba, refined from the 2 Myr world 6e2f17 of December A) against
35.5 GB (run 025b98 on 5d09cc, 1 Myr, world 899985; docs/review/refine-l8/split.md). Wall time barely moved (2:09:40 against
1:56:41), so something held in memory scales with the zoom's span (likely the recent pass's full climates for every stored
2-kyr frame, or prolonged frames). Different worlds, so not a clean pair.

**What breaks if never done.** Daniel's December world is a 2 Myr zoom refined to L8. At 69 GB it fits the machine alone but
not beside other lanes (daytime cap ~90 GB for everything), and an L8 refine of a bigger world could go past it.

**Do.** Find what scales with the span (memory profile of one split run, or `ps` sampling by stage); keep only the frames the
settled window needs, or stream them. Done when a 2 Myr split peaks within ~1.2x of the 1 Myr split on the same world.

## Updates
- 2026-11-11: Status todo -> done. lane 305 merged: L6->L7 analogue 2 Myr peak 20.4 -> 10.3 GB, byte-identical outputs; L8 measurement is PW-1752
- 2026-11-10: Created from inbox draft draft-split-2myr-peak-69gb.md (found by coordinator (lane 280 chain)).
