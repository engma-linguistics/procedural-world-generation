---
title: "Viewer: river labels sit at the river's mouth, not along its course"
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: s
impact: low
found_by: lane311
blocked_by: []
relates: []
refs: [viewer/globe/maplabels.js, planet/lineages/featnames.py::build, planet/language/output.py::landscape_json, "languages.json landscape.rivers (lat, lon = mouth)", "run a24559 (copy)", docs/review/names/lane311/]
---

## Description
The map labels (lane 311) place each river's name where languages.json's landscape puts the river: its mouth cell (lat, lon).
The label therefore sits on the coast, often beside a bay or cape label, and a long river shows its name only where it meets the
sea. A peoples run stores no river course of its own (the world's river layer has it).

What misleads if never done: on the globe a river name reads like the name of the coast or the bay at the mouth; a reader
zoomed in on the middle of a long river sees no name for it.

Try: in featnames.build, take the river's cells from the world's river layer (or the run's flow) and place the label at the
middle cell of its main stem, with the stem's direction so the viewer can tilt the text along it.
- [ ] a24559: the five biggest rivers' labels sit inland, on the river
