---
id: PW-1376
title: landuse.derive still splits each people's density by its fixed [[use]] shares, not the ladder's ways of life
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: lane 136 / lane 137 (density ladder build)
blocked_by: []
relates: [PW-1275, PW-1357]
refs: ["planet/lineages/landuse.py::derive", "planet/lineages/landuse.py::shares", "planet/lineages/landuse.py::frame_inputs", "planet/lineages/ladder.py::Ladder.sh", "planet/lineages/ladder.py::Ladder.rung", "planet/lineages/animals.py::Stock.__init__ (sh and propensity from landuse.shares)", planet/lineages/output.py, docs/review/peoples/density-ladder/build.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
With the density ladder (PW-1275) a people's ways of life vary by cell: farmable land farms once it knows a crop, grazing land is
herded, the rest forages or fishes. `landuse.frame_inputs` (the history's frames) already reads the ladder's farm and herd shares per
cell (`Ladder.sh`). But `landuse.derive` (the saved run's land cover) still splits each people's realized density by its fixed
`landuse.shares` from the `[[use]]` table, and so do the animals' and crops' propensities (`animals.Stock.__init__`). So a tabaxi
people that ploughs most of its land in the lane 137 runs gets no cropland from `derive`, and the humans who herd get none of that as
pasture there.

What to try: save the ladder's per-line farm and herd shares per cell (or per line, people weighted) with the run and read them in
`derive`; then decide whether propensities should follow the realized shares too (they decide who tames and who first cultivates).
- [ ] derive reads the ladder's shares
- [ ] land cover before/after on a dnd run (cropland and pasture per people)

## Updates
- 2026-11-02: Created from inbox draft draft-landuse-derive-static-shares.md (found by lane 136 / lane 137 (density ladder build)).
