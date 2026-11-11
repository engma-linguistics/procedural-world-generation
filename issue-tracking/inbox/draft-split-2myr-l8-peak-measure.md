---
title: Measure the 2 Myr L8 split peak on December A after the frame streaming (only estimated so far)
type: task
status: todo
parent: null
milestone: v1.0
subsystem: peoples
effort: s
impact: med
found_by: lane305
blocked_by: []
relates: []
refs: [tools/split_peak_l8.sh, docs/review/timezoom/two-myr.md, planet/lineages/history/handover.py, planet/lineages/output.py]
---

## Description
**In plain words.** Lane 305 made the split peoples run keep its pre-farming frames on the coarse grid and write its layers as it
goes. On an L6 -> L7 analogue the 2 Myr run's peak fell from 20.4 to 10.3 GB (outputs byte-identical); on the L8 December world
that is an *estimate* of ~35 GB against lane 280's 69.3 GB. Nobody has run it at L8: lane 280's worlds were deleted and the
2 Myr zoom of December A takes ~2 h to rebuild.

**What breaks if never done.** The December world (v0.5.0) is planned on a number nobody measured; if L8 adds something the
analogue lacks, the run still will not fit beside other lanes.

**Do.** On a quiet machine: copy runs/0b3439 and grids/ into a scratch root, `tools/split_peak_l8.sh <root>` (zoom, finish,
refine to L8, `planet lineages --tree dnd --tries 1` under MemoryMax=48G). Record wall and peak in two-myr.md section 4.
- [ ] peak at or under ~40 GB, or the stage that peaks named
