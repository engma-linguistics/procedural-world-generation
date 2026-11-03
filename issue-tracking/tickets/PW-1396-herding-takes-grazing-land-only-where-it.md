---
id: PW-1396
title: "Herding takes grazing land only where it feeds more than the wild: is 'half at equal' the right margin?"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: peoples
effort: s
impact: low
found_by: lane 141
blocked_by: []
relates: [PW-1385]
refs: ["planet/lineages/ladder.py::herd_keep", "planet/lineages/ladder.py::HERD_POW", docs/review/peoples/density-ladder/rich-foragers.md, docs/review/peoples/density-ladder/hunters-lag.md, "tools/peoples_robust.py::wild_overlap"]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: lane 141 (PW-1385) made a herding people herd a cell's grazing land only where herding feeds more people there than
foraging or fishing, smoothly: half the grazing land is herded where the two feed the same number, 80% where herding feeds twice as
many, 20% where it feeds half. This matters only on cold and dry land, where lane 139 found herding and foraging feed similar numbers
(subarctic 68%, polar 49-63%, steppe 18-19% of herders sat where foraging comes within half). There is no labour margin in it: no
source compared herders' returns per hour of work with foragers' on the same land. Options:
- A: keep "half at equal" (as built).
- B: add a margin for herding's extra work (herd only where it feeds, say, 1.5x the wild), if a source is found.
- C: no rule for herding (back to herding all grazing land a herding people holds).
Lean A. See rich-foragers.md's results for how many herders moved.

## Updates
- 2026-11-03: Created from inbox draft draft-herding-vs-wild-margin.md (found by lane 141).
