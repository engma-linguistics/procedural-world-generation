---
id: PW-763
title: "Place tree roots: let a preset say where and when a progenitor line starts (e.g. mammals far from reptiles, birds close to reptiles)"
type: task
status: done
parent: PW-103
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-10-24
---

## Description
Owner 2026-10-24 (PW-734 Q2): rather than authored history, the owner wants to anchor where on the world each root clade starts and at what point in the tree, relative placements (far from / near to) are enough.

## Updates
- 2026-10-24: Status todo -> done. Merged c80c766: near/far_from/lat_band/landmass hints. Deep roots have little room at 320 Myr (mammal/reptile ~1900 km apart in 4f82a4).
- 2026-10-24: fun16 built it: `near` / `far_from` (line ids), `lat_band`, `landmass` on a root, arrival or split (history._start_hints, soft multipliers on the origin score, START_KM 1500). seven_meals: reptilian far_from mammalian, avian near reptilian. Run 4f82a4 (L7 world 1df1c3): the two 320 Myr splits still land 1900 km apart because the one-tree-of-life range is small; modest effect. Ready for the coordinator to close.
- 2026-10-24: Created.
