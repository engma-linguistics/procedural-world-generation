---
title: Vegetation and biome maps inherit the rain field's diagonal streaks on flat interiors
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: med
found_by: veg
blocked_by: []
relates: [PW-019, PW-187]
refs: ["world bcc894", planet/climate.py]
---

## Description
The coordinator saw east-west stripes of forest and grassland across the southern continent's interior of world bcc894 (and finished bcb4b6) in the biome map. Running the new vegetation on bcc894's climate shows the cause: the precipitation layer itself has diagonal streaks there (PW-019). The vegetation softens them (soil water, a neighbour seed spread, history) but still shows them where the streaks cross the forest/savanna or grass/shrub thresholds. Not fixed in the vegetation (smoothing its input would hide a climate artefact); to merge into PW-019 as a further symptom and check after it.
