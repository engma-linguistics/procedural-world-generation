---
id: PW-606
title: "Earth world: no basement ages or tectonic history, so most resource rules can't be checked on Earth"
type: task
status: todo
parent: PW-155
milestone: v2
subsystem: surface
effort: m
impact: low
found_by: resources
blocked_by: []
relates: [PW-132, PW-155]
refs: [tools/resources_check.py, tools/earth_data.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
tools/resources_check.py --earth runs the resources' no-history rules on the Earth world with
GLiM parent rock. Porphyry lands on the Andes (14% of cells >= 0.25) and the Cordillera (6%), not the
Canadian Shield (0%); bauxite favours Guiana-Guinea (mean 0.41) over the Sahara (0.08). But BIF, diamonds,
orogenic gold and metamorphic gems need basement ages and collision history, and buried salt needs strata,
which the Earth world lacks (PW-132). A gridded basement-age map (e.g. a global geological-province age
compilation) and present plate boundaries in earth_data would make those checkable (as a plausibility
anchor only).

## Updates
- 2026-10-23: Created from inbox draft draft-resources-earth-ages.md (found by resources).
