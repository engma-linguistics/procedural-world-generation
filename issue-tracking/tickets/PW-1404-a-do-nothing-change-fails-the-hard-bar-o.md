---
id: PW-1404
title: "A do-nothing change fails the hard bar on 2 of main's 6 coldest test planets: the frozen-over check reads chaos there"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: lane144
blocked_by: []
relates: [PW-1261, PW-1091, PW-1142, PW-994]
refs: [docs/review/base-climate/fork-judge/round1.md, docs/review/vegetation/herb-roots/round1.md, tools/hard_bar.py, tools/ice_criteria.py]
created: 2026-11-03
updated: 2026-11-03
---

## Description
**In plain words.** The hard bar says no test planet may end frozen over (40% or more of its land under ice in the
last stretch of the run). Main's coldest test planets sit only 4-7 points under that line. Lane 144 re-ran main's six
coldest with a change that does nothing physical (the climate nudged by 0.00002 C), sharing everything up to 300 Myr.
Two of the six then froze over in the window: r0.001 l6c_p 957317 (peak 44.6% of land) and r0.001 l6c_0 819014
(41.1%). These are the same two kinds of draw that failed PW-1261's herb-roots judge. Lane 140c/d's two unforked
do-nothing re-runs of the same six failed 0 of 12, and lane 144's other forked one 0 of 6. So 2 of 24 do-nothing
re-runs of these six fail, and any change, however sound, can fail the bar by chance on main's cold tail.

Baseline: main = lane 140's frozen main 4abc1707 on the judge's own draws; the comparison is the same draw re-run.
Tables: round1.md section 2b; per-arm hard_bar output in the session scratchpad `l144/hb_*.txt`.

This ticket is about how a hard failure on the cold tail should be read. It does not propose a change to the 40% line
or the window. The 2026-10-30 ruling already gives each hard failure its own diagnosis. The question is what that
diagnosis may conclude when a do-nothing re-run fails the same way.

Options:
- **A. Diagnose against a null.** A hard failure on a draw counts against the change only when the change's arm is
  colder than a do-nothing re-roll of that draw by more than chaos (e.g. two forked nulls per failing draw, ~1.5 runs
  each). The bar stays 100%; the diagnosis gains a yardstick.
- **B. Widen main's margin first** (the ice lanes): why main's cold draws sit 4-7 points under the line and swing
  by 3-27 points of peak land ice under a do-nothing re-run (lane 140c). Then any judge reads the change, not the coin toss. Long.
- **C. Leave as is.** A cold-tail failure blocks the merge until the change is shown not to cool, as for PW-1261.
Lean: A now, B as the lasting fix.

- [ ] Daniel's choice

## Updates
- 2026-11-03: Created from inbox draft draft-hard-bar-null-fails-cold-tail.md (found by lane144).
